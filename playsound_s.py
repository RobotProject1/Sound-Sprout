import wave
import numpy as np
import sounddevice as sd

def mix_and_play(audio_clip_paths):
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
    mixed_audio = np.clip(mixed_audio, -32768, 32767).astype(np.int16)

    # Play the mixed audio
    sd.play(mixed_audio, samplerate=sample_rate)
    sd.wait()

# Example usage
audio_clip_paths = ['sound/summer/CARROT.wav', 'sound/summer/RADISH.wav']
mix_and_play(audio_clip_paths)