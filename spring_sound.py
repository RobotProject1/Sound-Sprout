import os
import time
import traceback
from plant_classification import read_id, read_v
from threading import Thread

# Use absolute path for path_list.txt and audio files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_LIST_FILE = os.path.join(BASE_DIR, 'sound_sprout', 'path_list.txt')

# (1,Potato)(2,Tomato)(3,Carrot)(4,Sunflower)(5,Daisy)(6,Mushroom)(7,Shallot)(8,Clover)(9,Corn)(10,Pumpkin)(11,Cauliflower)(12,Radish)
track = {
    1: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Potato.wav'),
    2: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Tomato.wav'),
    3: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Carrot.wav'),
    4: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Sunflower.wav'),
    5: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Daisy.wav'),
    6: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Mushroom.wav'),
    7: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Shallot.wav'),
    8: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Clover.wav'),
    9: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Corn.wav'),
    10: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Pumpkin.wav'),
    11: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Cauliflower.wav'),
    12: os.path.join(BASE_DIR, 'sound_sprout/sound/spring/Radish.wav')
}

class readnwrite(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started (PID: {os.getpid()})")
        print(f"[{time.strftime('%H:%M:%S')}] Current working directory: {os.getcwd()}")
        print(f"[{time.strftime('%H:%M:%S')}] Writing to: {PATH_LIST_FILE}")
        plant_id_old = []
        plant_id_new = []
        while True:
            try:
                plant_id_new = read_id(read_v())
                print(f"[{time.strftime('%H:%M:%S')}] New plant IDs: {plant_id_new}")
                if plant_id_new == plant_id_old:
                    print(f"[{time.strftime('%H:%M:%S')}] No change in plant IDs")
                else:
                    path_list = ""
                    for i in plant_id_new:
                        if i == 0:
                            print(f"[{time.strftime('%H:%M:%S')}] Skipping ID 0")
                        else:
                            if i in track and os.path.exists(track[i]):
                                path_list += ',' + track[i]
                            else:
                                print(f"[{time.strftime('%H:%M:%S')}] Invalid ID {i} or file {track.get(i, 'N/A')} not found")
                    path_list = path_list.lstrip(',')
                    print(f"[{time.strftime('%H:%M:%S')}] Writing to path_list.txt: {path_list}")
                    with open(PATH_LIST_FILE, 'w') as file:
                        file.write(path_list)
                    plant_id_old = plant_id_new.copy()
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] readnwrite error: {e}")
                traceback.print_exc()
            time.sleep(1)

if __name__ == "__main__":
    thr1 = readnwrite()
    thr1.start()
    thr1.join()  # Keep main thread alive for standalone testing