from plant_classification import read_id, read_v
from threading import Thread
import os
import time

# (1,Potato)(2,Tomato)(3,Carrot)(4,Sunflower)(5,Daisy)(6,Mushroom)(7,Shallot)(8,Clover)(9,Corn)(10,Pumpkin)(11,Cauliflower)(12,Radish)
track = {
    1: 'sound_sprout/sound/spring/Potato.wav',
    2: 'sound_sprout/sound/spring/Tomato.wav',
    3: 'sound_sprout/sound/spring/Carrot.wav', 
    4: 'sound_sprout/sound/spring/Sunflower.wav',
    5: 'sound_sprout/sound/spring/Daisy.wav', 
    6: 'sound_sprout/sound/spring/Mushroom.wav',
    7: 'sound_sprout/sound/spring/Shallot.wav', 
    8: 'sound_sprout/sound/spring/Clover.wav',
    9: 'sound_sprout/sound/spring/Corn.wav', 
    10: 'sound_sprout/sound/spring/Pumpkin.wav',
    11: 'sound_sprout/sound/spring/Cauliflower.wav',
    12: 'sound_sprout/sound/spring/Radish.wav'
}

class readnwrite(Thread):
    def __init__(self):
        Thread.__init__(self)
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread initialized (PID: {os.getpid()})")
    
    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started (PID: {os.getpid()})")
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
                                print(f"[{time.strftime('%H:%M:%S')}] Added track for ID {i}: {track[i]}")
                            else:
                                print(f"[{time.strftime('%H:%M:%S')}] Invalid ID {i} or file {track.get(i, 'N/A')} not found")
                    path_list = path_list.lstrip(',')
                    print(f"[{time.strftime('%H:%M:%S')}] Writing to path_list.txt: {path_list}")
                    with open('sound_sprout/path_list.txt', 'w') as file:
                        file.write(path_list)
                    plant_id_old = plant_id_new.copy()
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] readnwrite error: {e}")
            time.sleep(1)

if __name__ == "__main__": 
    print(f"[{time.strftime('%H:%M:%S')}] spring_sound.py started (PID: {os.getpid()})")
    thr1 = readnwrite()
    thr1.start()
    thr1.join()  # Ensure the thread keeps running until interrupted