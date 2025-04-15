from plant_classification import read_id,read_v
from threading import Thread

#1=daisy 2=sunflower 3=clover 4=potato 5=radish 6=carrot 7=garlic 8=pumpkin 9=tomato 10=corn 11=cauliflower 12=mushroom
track = {1:'sound\Rainy\CARROT.wav',
         2:'sound\Rainy\SUNFLOWER.wav',
         3:'sound\Rainy\CLOVER.wav', 
         4:'sound\Rainy\POTATO.wav',
         5:'sound\Rainy\RADISH.wav', 
         6:'sound\Rainy\CARROT.wav',
         7:'sound\Rainy\GARLIC.wav', 
         8:'sound\Rainy\PUMPKIN.wav',
         9:'sound\Rainy\TOMATO.wav', 
         10:'sound\Rainy\CORN.wav',
         11:'sound\Rainy\CAULIFLOWER.wav',
         12:'sound\Rainy\MUSHROOM.wav'}

class readnwrite(Thread):
    def __init__(self, end):
        Thread.__init__(self)
        #self.end = end
    def run(self):
        plant_id_old = []
        plant_id_new = []
        while True:
            plant_id_new = read_id(read_v())
            if plant_id_new == plant_id_old:
                pass
            else:
                with open('path_list.txt', 'w') as file:
                    path_list = 'sound\Rainy\AMBIENT.wav'
                    for i in plant_id_new:
                        path_list += ','+track[i]
                    file.write(path_list)
            plant_id_old = plant_id_new.copy()

class lighting(Thread):
    def __init__(self, end):
        Thread.__init__(self)
        #self.end = end
    def run(self):
        while True:
            pass
        #lighting code here

thr1 = readnwrite()
thr2 = lighting()
thr1.start()
thr2.start()