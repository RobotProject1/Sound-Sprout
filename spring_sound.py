from plant_classification import read_id,read_v
from threading import Thread

#1=daisy 2=sunflower 3=clover 4=potato 5=radish 6=carrot 7=garlic 8=pumpkin 9=tomato 10=corn 11=cauliflower 12=mushroom
track = {1:'sound\spring\Daisy.wav',
         2:'sound\spring\Sunflower.wav',
         3:'sound\spring\Clover.wav', 
         4:'sound\spring\Potato.wav',
         5:'sound\spring\Radish.wav', 
         6:'sound\spring\Carrot.wav',
         7:'sound\spring\Garlic.wav', 
         8:'sound\spring\Pumpkin.wav',
         9:'sound\spring\Tomato.wav', 
         10:'sound\spring\Corn.wav',
         11:'sound\spring\Cauliflower.wav',
         12:'sound\spring\Mushroom.wav'}

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
                with open('path_list.txt', 'w') as file:
                    path_list = 'sound\spring\AMBIENT.wav'
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