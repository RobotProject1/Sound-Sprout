import sounddevice as sd
from playsound import mix
sound = mix(['sound\spring\Mushroom.wav', 'sound\spring\Pumpkin.wav', 'sound\spring\Garlic.wav', 'sound\spring\Potato.wav', 'sound\spring\Corn.wav'])
print('ctrl+c to stop')
try:
    while True:
        sd.play(sound[0], samplerate=sound[1])
        sd.wait()   
except KeyboardInterrupt:
    print("yood")