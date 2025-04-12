import sounddevice as sd
from playsound_v1 import mix
sound = mix(['sound\summer\RADISH.wav'])
print(sound)
while True:
    sd.play(sound[0], samplerate=sound[1])
    sd.wait()