import wave
import numpy as np
import sounddevice as sd
import time
from threading import Thread, Event
from shared_ads import ads2, read_adc
from multiprocessing import Queue
import os

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

class checkqueue(Thread):
    def __init__(self, stop_event, audio_queue):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.audio_queue = audio_queue

    def run(self):
        global mixed_audio, sample_rate, num_channels
        print(f"[{time.strftime('%H:%M:%S')}] checkqueue thread started (PID: {os.getpid()})")
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

class volume(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.last_volume = None

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] volume thread started (PID: {os.getpid()})")
        while not self.stop_event.is_set():
            try:
                voltage = read_adc(ads2, 3)
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

if __name__ == "__main__":
    import multiprocessing
    stop_event = Event()
    mixed_audio = np.zeros((542118, 2))
    sample_rate = 48000
    num_channels = 2
    index = 0
    audio_queue = multiprocessing.Manager().Queue()  # Create queue in main process

    try:
        stream = sd.OutputStream(samplerate=sample_rate, channels=num_channels, callback=callback, blocksize=8192)
        stream.start()

        checkqueue_thread = checkqueue(stop_event, audio_queue)
        adjust_volume_thread = volume(stop_event)
        checkqueue_thread.start()
        adjust_volume_thread.start()
        print(f"[{time.strftime('%H:%M:%S')}] Playsound good to go!")

        stop_event.wait()

    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] KeyboardInterrupt received, stopping...")
        stop_event.set()
        checkqueue_thread.join()
        adjust_volume_thread.join()
        stream.stop()
        stream.close()
        print(f"[{time.strftime('%H:%M:%S')}] Playsound shutdown complete.")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Unexpected error: {e}")
        stop_event.set()
        checkqueue_thread.join()
        adjust_volume_thread.join()
        stream.stop()
        stream.close()