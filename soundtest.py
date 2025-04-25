import sounddevice as sd
import wave
import numpy as np
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
sound = mix(['sound_sprout/'+i for i in ['sound/winter/Mushroom.wav', 'sound/winter/Pumpkin.wav', 'sound/winter/Shallot.wav', 'sound/winter/Potato.wav', 'sound/winter/Corn.wav','sound\winter\AMBIENT.wav','sound\winter\Radish.wav']])
print('ctrl+c to stop')
try:
    while True:
        sd.play(sound[0], samplerate=sound[1])
        sd.wait()   
except KeyboardInterrupt:
    print("yood")