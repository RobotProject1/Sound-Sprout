# from plant_classification import read_id,read_v
# from threading import Thread

# #1=daisy 2=sunflower 3=clover 4=potato 5=radish 6=carrot 7=garlic 8=pumpkin 9=tomato 10=corn 11=cauliflower 12=mushroom
# track = {1:'sound_sprout/sound/spring/Daisy.wav',
#          2:'sound_sprout/sound/spring/Sunflower.wav',
#          3:'sound_sprout/sound/spring/Clover.wav', 
#          4:'sound_sprout/sound/spring/Potato.wav',
#          5:'sound_sprout/sound/spring/Radish.wav', 
#          6:'sound_sprout/sound/spring/Carrot.wav',
#          7:'sound_sprout/sound/spring/Shallot.wav', 
#          8:'sound_sprout/sound/spring/Pumpkin.wav',
#          9:'sound_sprout/sound/spring/Tomato.wav', 
#          10:'sound_sprout/sound/spring/Corn.wav',
#          11:'sound_sprout/sound/spring/Cauliflower.wav',
#          12:'sound_sprout/sound/spring/Mushroom.wav'}

# class readnwrite(Thread):
#     def __init__(self):
#         Thread.__init__(self)
#     def run(self):
#         plant_id_old = []
#         plant_id_new = []
#         while True:
#             plant_id_new = read_id(read_v())
#             if plant_id_new == plant_id_old:
#                 pass
#             else:
#                 path_list = ""
#                 with open('sound_sprout/path_list.txt', 'w') as file:
#                     for i in plant_id_new:
#                         if i == 0:
#                             pass
#                         else:
#                             path_list += ','+track[i]
#                     file.write(path_list.lstrip(','))
#             plant_id_old = plant_id_new.copy()

# if __name__ == "__main__": 
#     thr1 = readnwrite()
#     thr1.start()

from plant_classification import read_id, read_v
from threading import Thread

#1=daisy 2=sunflower 3=clover 4=potato 5=radish 6=carrot 7=garlic 8=pumpkin 9=tomato 10=corn 11=cauliflower 12=mushroom
track = {
    1: 'sound_sprout/sound/spring/Daisy.wav',
    2: 'sound_sprout/sound/spring/Sunflower.wav',
    3: 'sound_sprout/sound/spring/Clover.wav', 
    4: 'sound_sprout/sound/spring/Potato.wav',
    5: 'sound_sprout/sound/spring/Radish.wav', 
    6: 'sound_sprout/sound/spring/Carrot.wav',
    7: 'sound_sprout/sound/spring/Shallot.wav', 
    8: 'sound_sprout/sound/spring/Pumpkin.wav',
    9: 'sound_sprout/sound/spring/Tomato.wav', 
    10: 'sound_sprout/sound/spring/Corn.wav',
    11: 'sound_sprout/sound/spring/Cauliflower.wav',
    12: 'sound_sprout/sound/spring/Mushroom.wav'
}

class readnwrite(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        print("readnwrite thread started")
        plant_id_old = []
        plant_id_new = []
        while True:
            try:
                plant_id_new = read_id(read_v())
                print(f"New plant IDs: {plant_id_new}")
                if plant_id_new == plant_id_old:
                    print("No change in plant IDs")
                else:
                    path_list = ""
                    for i in plant_id_new:
                        if i == 0:
                            print(f"Skipping ID 0")
                        else:
                            if i in track and os.path.exists(track[i]):
                                path_list += ',' + track[i]
                            else:
                                print(f"Invalid ID {i} or file {track.get(i, 'N/A')} not found")
                    path_list = path_list.lstrip(',')
                    print(f"Writing to path_list.txt: {path_list}")
                    with open('sound_sprout/path_list.txt', 'w') as file:
                        file.write(path_list)
                    plant_id_old = plant_id_new.copy()
            except Exception as e:
                print(f"readnwrite error: {e}")
            time.sleep(1)

if __name__ == "__main__": 
    thr1 = readnwrite()
    thr1.start()