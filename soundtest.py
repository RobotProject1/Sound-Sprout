import sounddevice as sd
from playsound_v1 import mix
sound = mix(['sound\winter\Cauliflower.wav', 'sound\winter\Daisy.wav', 'sound\winter\Radish.wav', 'sound\winter\Potato.wav', 'sound\winter\Corn.wav'])
print('ctrl+c to stop')
try:
    while True:
        sd.play(sound[0], samplerate=sound[1])
        sd.wait()   
except KeyboardInterrupt:
    print("yood")