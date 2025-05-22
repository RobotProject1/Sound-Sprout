import wave
import numpy as np
import sounddevice as sd
import time
from threading import Thread, Event, Lock
import os
from multiprocessing import Queue
from adafruit_ads1x15.analog_in import AnalogIn

adc_lock = Lock()

def mix(audio_clip_paths):
    audio_arrays = []
    sample_rate = None
    num_channels = None
    if not audio_clip_paths:
        return np.zeros((542118, 2)), 48000, 2
    for clip in audio_clip_paths:
        try:
            with wave.open(clip, 'rb') as w:
                if sample_rate is None:
                    sample_rate = w.getframerate()
                    num_channels = w.getnchannels()
                else:
                    assert sample_rate == w.getframerate(), "All clips must have the same sample rate"
                    assert num_channels == w.getnchannels(), "All clips must have the same number of channels"
                frames = w.readframes(w.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                if num_channels == 2:
                    audio_data = audio_data.reshape(-1, 2)
                audio_arrays.append(audio_data)
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error loading {clip}: {e}")
            continue
    if not audio_arrays:
        return np.zeros((542118, 2)), 48000, 2
    max_len = max(len(a) for a in audio_arrays)
    for i in range(len(audio_arrays)):
        pad_width = max_len - len(audio_arrays[i])
        if num_channels == 1:
            audio_arrays[i] = np.pad(audio_arrays[i], (0, pad_width), 'constant')
        else:
            audio_arrays[i] = np.pad(audio_arrays[i], ((0, pad_width), (0, 0)), 'constant')
    mixed_audio = np.sum(audio_arrays, axis=0)
    mixed_audio = mixed_audio.astype(np.float32)
    max_val = np.max(np.abs(mixed_audio))
    if max_val > 0:
        mixed_audio /= max_val
    return mixed_audio, sample_rate, num_channels

def callback(outdata, frames, time, status):
    global index, mixed_audio
    total_frames = mixed_audio.shape[0]
    end_index = index + frames
    if end_index <= total_frames:
        chunk = mixed_audio[index:end_index]
    else:
        first_part = mixed_audio[index:]
        second_part = mixed_audio[:end_index - total_frames]
        chunk = np.vstack((first_part, second_part))
    outdata[:] = chunk
    index = (index + frames) % total_frames

def read_adc(ads, pin, samples=10, delay=0.01):
    with adc_lock:
        try:
            values = []
            for _ in range(samples):
                chan = AnalogIn(ads, pin)
                values.append(chan.voltage)
                time.sleep(delay)
            avg_voltage = sum(values) / len(values)
            print(f"[{time.strftime('%H:%M:%S')}] Read ADC (pin: {pin}): {avg_voltage:.2f}V")
            return avg_voltage
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ADC read error (pin: {pin}): {e}")
            return None

class checkqueue(Thread):
    def __init__(self, stop_event, audio_queue):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.audio_queue = audio_queue

    def run(self):
        global mixed_audio, sample_rate, num_channels
        print(f"[{time.strftime('%H:%M:%S')}] checkqueue thread started")
        while not self.stop_event.is_set():
            try:
                if not self.audio_queue.empty():
                    audio_clip_paths = self.audio_queue.get()
                    print(f"[{time.strftime('%H:%M:%S')}] Received audio paths: {audio_clip_paths}")
                    mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
                    print(f"[{time.strftime('%H:%M:%S')}] Mixed audio shape: {mixed_audio.shape}, sample rate: {sample_rate}, channels: {num_channels}")
                time.sleep(0.1)
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] checkqueue error: {e}")
                time.sleep(0.1)

    def stop(self):
        print(f"[{time.strftime('%H:%M:%S')}] Stopping checkqueue thread")
        self.stop_event.set()

class volume(Thread):
    def __init__(self, stop_event, ads2):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.ads2 = ads2
        self.last_volume = None

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] volume thread started")
        while not self.stop_event.is_set():
            try:
                voltage = read_adc(self.ads2, 3)
                if voltage is None:
                    print(f"[{time.strftime('%H:%M:%S')}] Skipping volume adjustment due to ADC read failure")
                    time.sleep(0.2)
                    continue
                voltage = min(max(voltage, 0), 5.0)
                volume_percent = int((voltage / 5.0) * 120)
                if volume_percent != self.last_volume:
                    os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volume_percent}%")
                    self.last_volume = volume_percent
                    print(f"[{time.strftime('%H:%M:%S')}] Set volume to {volume_percent}%")
                time.sleep(0.2)
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Volume control error: {e}")
                time.sleep(0.2)

    def stop(self):
        print(f"[{time.strftime('%H:%M:%S')}] Stopping volume thread")
        self.stop_event.set()

def run(audio_queue, ads1, ads2):
    stop_event = Event()
    global mixed_audio, sample_rate, num_channels, index
    mixed_audio = np.zeros((542118, 2))
    sample_rate = 48000
    num_channels = 2
    index = 0

    try:
        stream = sd.OutputStream(samplerate=sample_rate, channels=num_channels, callback=callback, blocksize=8192)
        stream.start()

        checkqueue_thread = checkqueue(stop_event, audio_queue)
        adjust_volume_thread = volume(stop_event, ads2)
        checkqueue_thread.start()
        adjust_volume_thread.start()
        print(f"[{time.strftime('%H:%M:%S')}] Playsound good to go!")

        while not stop_event.is_set():
            time.sleep(1)

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Unexpected error: {e}")
    finally:
        stop_event.set()
        checkqueue_thread.stop()
        adjust_volume_thread.stop()
        checkqueue_thread.join()
        adjust_volume_thread.join()
        stream.stop()
        stream.close()
        print(f"[{time.strftime('%H:%M:%S')}] Playsound shutdown complete.")

def stop():
    run.stop_event = Event()
    run.stop_event.set()

if __name__ == "__main__":
    from adafruit_ads1x15.ads1115 import ADS1115
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    ads1 = ADS1115(i2c, address=0x48)
    ads2 = ADS1115(i2c, address=0x49)
    run(Queue(), ads1, ads2)  # Fallback for standalone testing