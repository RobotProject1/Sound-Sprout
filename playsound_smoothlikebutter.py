import wave
import numpy as np
import sounddevice as sd
import os
import time

def mix(audio_clip_paths):
    audio_arrays = []
    sample_rate = None
    num_channels = None

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

    # Mix by summing and clipping to int16 range
    mixed_audio = np.sum(audio_arrays, axis=0)
    mixed_audio = mixed_audio.astype(np.float32)
    max_val = np.max(np.abs(mixed_audio))
    mixed_audio /= (max_val)  # normalize to [-1.0, 1.0]
    # mixed_audio += 1.0  # shift to [0.0, 2.0]
    # mixed_audio /= 2.0  # scale to [0.0, 1.0]
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
        just_looped = True  # set the flag to indicate that we looped
    outdata[:] = chunk
    index = (index + frames) % total_frames  # wrap the index to loop

if __name__ == "__main__": 
    mtime = os.path.getmtime('path_list.txt')
    last_mtime = 0
    stream = None
    just_looped = False
    with open('path_list.txt', 'r') as file:
        path_list = file.read()
        path_list = path_list.split(',')
    print(path_list)
    audio_clip_paths = [i for i in path_list if i != '']
    mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
    index = 0
    stream = sd.OutputStream(samplerate=sample_rate, channels=num_channels, callback=callback )
    stream.start()

    while True:
        try:
            mtime = os.path.getmtime('path_list.txt')
            if mtime == last_mtime:
                pass
            else:
                with open('path_list.txt', 'r') as file:
                    path_list = file.read()
                    path_list = path_list.split(',')
                print(path_list)
                audio_clip_paths = [i for i in path_list if i != '']
                mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
                last_mtime = mtime

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(1) 
                
