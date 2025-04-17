from plant_classification import read_id,read_v
from threading import Thread

#1=daisy 2=sunflower 3=clover 4=potato 5=radish 6=carrot 7=garlic 8=pumpkin 9=tomato 10=corn 11=cauliflower 12=mushroom
track = {1:'sound\winter\Daisy.wav',
         2:'sound\winter\Sunflower.wav',
         3:'sound\winter\Clover.wav', 
         4:'sound\winter\Potato.wav',
         5:'sound\winter\Radish.wav', 
         6:'sound\winter\Carrot.wav',
         7:'sound\winter\Garlic.wav', 
         8:'sound\winter\Pumpkin.wav',
         9:'sound\winter\Tomato.wav', 
         10:'sound\winter\Corn.wav',
         11:'sound\winter\Cauliflower.wav',
         12:'sound\winter\Mushroom.wav'}

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
                    path_list = 'sound\winter\AMBIENT.wav'
                    for i in plant_id_new:
                        if i == 0:
                            pass
                        else:
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