import wave
import numpy as np
import sounddevice as sd
import os
import time
from threading import Thread, Event
from adafruit_ads1x15.analog_in import AnalogIn
from shared_ads import ads2

def mix(audio_clip_paths):
    audio_arrays = []
    sample_rate = None
    num_channels = None
    if audio_clip_paths == []:
        return np.zeros((542118, 2)), 48000, 2
    for clip in audio_clip_paths:
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
    if max_val > 0:  # Avoid division by zero
        mixed_audio /= max_val  # Normalize to [-1.0, 1.0]
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
    index = (index + frames) % total_frames  # Wrap the index to loop

class checkfile(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.last_mtime = 0

    def run(self):
        global mixed_audio, sample_rate, num_channels
        while not self.stop_event.is_set():
            try:
                mtime = os.path.getmtime('sound_sprout/path_list.txt')
                if mtime == self.last_mtime:
                    time.sleep(0.1)  # Reduce CPU usage
                    continue
                with open('sound_sprout/path_list.txt', 'r') as file:
                    path_list = file.read()
                    path_list = path_list.split(',')
                audio_clip_paths = [i.strip() for i in path_list if i.strip()]
                print(f"New path list: {audio_clip_paths}")
                mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
                print(f"Mixed audio shape: {mixed_audio.shape}, sample rate: {sample_rate}, channels: {num_channels}")
                self.last_mtime = mtime
            except Exception as e:
                print(f"checkfile error: {e}")
            time.sleep(0.1)  # Avoid busy looping

class volume(Thread):
    def __init__(self, stop_event):
        Thread.__init__(self)
        self.stop_event = stop_event
        self.last_volume = None

    def read_avg_voltage(self, channel=3, samples=10, delay=0.01):
        values = []
        for i in range(samples):
            if i < 0.05:
                continue
            else:
                values.append(AnalogIn(ads2, channel).voltage)
                time.sleep(delay)
        return sum(values) / len(values)

    def run(self):
        while not self.stop_event.is_set():
            try:
                voltage = self.read_avg_voltage()
                voltage = min(max(voltage, 0), 5.0)
                volume_percent = int((voltage / 5.0) * 120)
                if volume_percent != self.last_volume:
                    os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volume_percent}%")
                    self.last_volume = volume_percent
                time.sleep(0.2)
            except Exception as e:
                print(f"Volume control error: {e}")
                time.sleep(0.2)

if __name__ == "__main__":
    stop_event = Event()  # Event to signal threads to stop
    mixed_audio = np.zeros((542118, 2))  # Initialize with default
    sample_rate = 48000
    num_channels = 2
    index = 0

    try:
        # Read initial path list
        with open('sound_sprout/path_list.txt', 'r') as file:
            path_list = file.read().strip()
            path_list = [p.strip() for p in path_list.split(',') if p.strip()]
        print(f"Initial path list: {path_list}")
        audio_clip_paths = [i.strip() for i in path_list if i.strip()]
        mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)

        # Start audio stream
        stream = sd.OutputStream(samplerate=sample_rate, channels=num_channels, callback=callback, blocksize=8192)
        stream.start()

        # Start threads
        checkfile_thread = checkfile(stop_event)
        adjust_volume_thread = volume(stop_event)
        checkfile_thread.start()
        adjust_volume_thread.start()
        print("Playsound good to go!")

        # Keep main thread alive
        stop_event.wait()  # Wait indefinitely until interrupted

    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping...")
        stop_event.set()  # Signal threads to stop
        checkfile_thread.join()  # Wait for threads to exit
        adjust_volume_thread.join()
        stream.stop()  # Stop the audio stream
        stream.close()  # Close the audio stream
        print("Playsound shutdown complete.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        stop_event.set()
        checkfile_thread.join()
        adjust_volume_thread.join()
        stream.stop()
        stream.close()