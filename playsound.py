import wave
import numpy as np
import sounddevice as sd
import os
import time
from threading import Thread
import ADS1x15

ADS1 = ADS1x15.ADS1115(1, 0x48)
f = ADS1.toVoltage()

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
    mixed_audio /= (max_val) # normalize to [-1.0, 1.0]
    return mixed_audio, sample_rate, num_channels

def callback(outdata, frames, time, status):
    global index,just_looped,mixed_audio
    total_frames = mixed_audio.shape[0]
    end_index = index + frames
    if end_index <= total_frames:
        chunk = mixed_audio[index:end_index]
    else:
        first_part = mixed_audio[index:]
        second_part = mixed_audio[:end_index - total_frames]
        chunk = np.vstack((first_part, second_part))
    outdata[:] = chunk
    index = (index + frames) % total_frames  # wrap the index to loop

class checkfile(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.last_mtime = 0
         # Set the thread as a daemon thread
    def run(self):
        global mixed_audio, sample_rate, num_channels
        while True:
            try:
                mtime = os.path.getmtime('path_list.txt')
                if mtime == self.last_mtime:
                    pass
                else:
                    with open('path_list.txt', 'r') as file:
                        path_list = file.read()
                        path_list = path_list.split(',')
                    print(path_list)
                    audio_clip_paths = [i for i in path_list if i != '']
                    mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
                    print(mixed_audio.shape, sample_rate, num_channels)
                    self.last_mtime = mtime

            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(1) 

class volume(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            raw = ADS1.readADC(0)
            voltage = raw * f  
            voltage = min(max(voltage, 0), 5.0)  

            volume_percent = int((voltage / 5.0) * 100) 
            os.system(f"amixer sset 'Master' {volume_percent}%")


if __name__ == "__main__": 
    mtime = os.path.getmtime('path_list.txt')
    last_mtime = 0
    stream = None
    with open('path_list.txt', 'r') as file:
        path_list = file.read()
        path_list = path_list.split(',')
    print(path_list)
    audio_clip_paths = [i for i in path_list if i != '']
    mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
    index = 0
    stream = sd.OutputStream(samplerate=sample_rate, channels=num_channels, callback=callback )
    stream.start()

    checkfile_thread = checkfile()
    adjust_volume_thread = volume()
    checkfile_thread.start()
    adjust_volume_thread.start()
    
                
