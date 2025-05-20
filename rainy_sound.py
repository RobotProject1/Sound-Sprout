from plant_classification import read_id,read_v
from threading import Thread

#(1,Potato)(2,Tomato)(3,Carrot)(4,Sunflower)(5,Daisy)(6,Mushroom)(7,Shallot)(8,Clover)(9,Corn)(10,Pumpkin)(11,Cauliflower)(12,Radish)
track = {
    1: 'sound_sprout/sound/rainy/Potato.wav',
    2: 'sound_sprout/sound/rainy/Tomato.wav',
    3: 'sound_sprout/sound/rainy/Carrot.wav', 
    4: 'sound_sprout/sound/rainy/Sunflower.wav',
    5: 'sound_sprout/sound/rainy/Daisy.wav', 
    6: 'sound_sprout/sound/rainy/Mushroom.wav',
    7: 'sound_sprout/sound/rainy/Shallot.wav', 
    8: 'sound_sprout/sound/rainy/Clover.wav',
    9: 'sound_sprout/sound/rainy/Corn.wav', 
    10: 'sound_sprout/sound/rainy/Pumpkin.wav',
    11: 'sound_sprout/sound/rainy/Cauliflower.wav',
    12: 'sound_sprout/sound/rainy/Radish.wav'
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
                    path_list = "sound_sprout/sound/rainy/AMBIENT.wav"
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