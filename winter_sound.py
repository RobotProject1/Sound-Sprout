from plant_classification import read_id,read_v
from threading import Thread
import os

#1=daisy 2=sunflower 3=clover 4=potato 5=radish 6=carrot 7=garlic 8=pumpkin 9=tomato 10=corn 11=cauliflower 12=mushroom
track = {1:'sound_sprout/sound/winter/Daisy.wav',
         2:'sound_sprout/sound/winter/Sunflower.wav',
         3:'sound_sprout/sound/winter/Clover.wav', 
         4:'sound_sprout/sound/winter/Potato.wav',
         5:'sound_sprout/sound/winter/Radish.wav', 
         6:'sound_sprout/sound/winter/Carrot.wav',
         7:'sound_sprout/sound/winter/Shallot.wav', 
         8:'sound_sprout/sound/winter/Pumpkin.wav',
         9:'sound_sprout/sound/winter/Tomato.wav', 
         10:'sound_sprout/sound/winter/Corn.wav',
         11:'sound_sprout/sound/winter/Cauliflower.wav',
         12:'sound_sprout/sound/winter/Mushroom.wav'}

class readnwrite(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        plant_id_old = []
        plant_id_new = []
        while True:
            plant_id_new = read_id(read_v())
            if plant_id_new == plant_id_old:
                pass
            else:
                with open('sound_sprout/path_list.txt', 'w') as file:
                    path_list = 'sound_sprout/sound/winter/AMBIENT.wav'
                    for i in plant_id_new:
                        if i == 0:
                            pass
                        else:
                            path_list += ','+track[i]
                    file.write(path_list)
            plant_id_old = plant_id_new.copy()

class lighting(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            pass
        #lighting code here
        
if __name__ == "__main__": 
    thr1 = readnwrite()
    thr2 = lighting()
    thr1.start()
    thr2.start()