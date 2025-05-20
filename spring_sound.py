import os
import time
from threading import Thread
from shared_ads import ads1, read_adc
from plant_classification import read_id

# Mapping of plant IDs to audio files
track = {
    1: 'sound_sprout/sound/spring/Potato.wav',
    2: 'sound_sprout/sound/spring/Tomato.wav'
}

class readnwrite(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started (PID: {os.getpid()})")
        path_list_path = 'sound_sprout/path_list.txt'
        try:
            # Verify path_list.txt is writable
            if not os.access(os.path.dirname(path_list_path) or '.', os.W_OK):
                print(f"[{time.strftime('%H:%M:%S')}] ERROR: Directory for {path_list_path} is not writable")
                return
            while self.running:
                try:
                    # Read voltages and classify plant IDs
                    id_list = read_id()
                    print(f"[{time.strftime('%H:%M:%S')}] Detected IDs: {id_list}")
                    
                    # Get audio file paths for valid IDs
                    audio_paths = []
                    for plant_id in id_list:
                        if plant_id in track:
                            audio_paths.append(track[plant_id])
                    
                    if audio_paths:
                        # Write to path_list.txt
                        try:
                            with open(path_list_path, 'w') as f:
                                f.write(','.join(audio_paths))
                            print(f"[{time.strftime('%H:%M:%S')}] Wrote to {path_list_path}: {','.join(audio_paths)}")
                        except Exception as e:
                            print(f"[{time.strftime('%H:%M:%S')}] Failed to write to {path_list_path}: {e}")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] No valid plant IDs detected")
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] readnwrite error: {e}")
                    time.sleep(1)
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Fatal error in readnwrite thread: {e}")

    def stop(self):
        print(f"[{time.strftime('%H:%M:%S')}] Stopping readnwrite thread")
        self.running = False

if __name__ == "__main__":
    print(f"[{time.strftime('%H:%M:%S')}] spring_sound.py started (PID: {os.getpid()})")
    try:
        readnwrite_thread = readnwrite()
        readnwrite_thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down spring_sound.py")
        readnwrite_thread.stop()
        readnwrite_thread.join()
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Fatal error in spring_sound.py: {e}")
        readnwrite_thread.stop()
        readnwrite_thread.join()