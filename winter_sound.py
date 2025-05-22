import time
import os
from threading import Thread
from shared_ads import ads1, read_adc
from plant_classification import read_id

class readnwrite(Thread):
    def __init__(self, audio_paths_file):
        Thread.__init__(self)
        self.running = True
        self.audio_paths_file = audio_paths_file

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started (PID: {os.getpid()})")
        try:
            while self.running:
                try:
                    # Read audio paths for the current season, including ambient
                    audio_paths = read_id('winter')
                    print(f"[{time.strftime('%H:%M:%S')}] Detected audio paths: {audio_paths}")
                    
                    if audio_paths:
                        # Write to audio_paths.txt
                        with open(self.audio_paths_file, 'w') as f:
                            f.write(','.join(audio_paths))
                        print(f"[{time.strftime('%H:%M:%S')}] Wrote to {self.audio_paths_file}: {audio_paths}")
                    else:
                        # Write only ambient if no plants detected
                        with open(self.audio_paths_file, 'w') as f:
                            f.write('sound_sprout/sound/winter/AMBIENT.wav')
                        print(f"[{time.strftime('%H:%M:%S')}] No valid plant IDs detected, wrote ambient to {self.audio_paths_file}")
                    
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
    import sys
    print(f"[{time.strftime('%H:%M:%S')}] winter_sound.py started (PID: {os.getpid()})")
    audio_paths_file = sys.argv[1] if len(sys.argv) > 1 else 'sound_sprout/audio_paths.txt'
    try:
        readnwrite_thread = readnwrite(audio_paths_file)
        readnwrite_thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down winter_sound.py")
        readnwrite_thread.stop()
        readnwrite_thread.join()
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Fatal error in winter_sound.py: {e}")
        readnwrite_thread.stop()
        readnwrite_thread.join()