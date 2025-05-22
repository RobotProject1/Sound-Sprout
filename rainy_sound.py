import time
import os
from threading import Thread
from shared_ads import ads1, read_adc
from plant_classification import read_id
from multiprocessing import Queue

class readnwrite(Thread):
    def __init__(self, audio_queue):
        Thread.__init__(self)
        self.running = True
        self.audio_queue = audio_queue

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started (PID: {os.getpid()})")
        try:
            while self.running:
                try:
                    # Read audio paths for the current season, including ambient
                    audio_paths = read_id('rainy')
                    print(f"[{time.strftime('%H:%M:%S')}] Detected audio paths: {audio_paths}")
                    
                    if audio_paths:
                        # Send to queue
                        self.audio_queue.put(audio_paths)
                        print(f"[{time.strftime('%H:%M:%S')}] Sent to queue: {audio_paths}")
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

def run(audio_queue):
    print(f"[{time.strftime('%H:%M:%S')}] rainy_sound.py started (PID: {os.getpid()})")
    try:
        readnwrite_thread = readnwrite(audio_queue)
        readnwrite_thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down rainy_sound.py")
        readnwrite_thread.stop()
        readnwrite_thread.join()
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Fatal error in rainy_sound.py: {e}")
        readnwrite_thread.stop()
        readnwrite_thread.join()

if __name__ == "__main__":
    run(Queue())  # Fallback for standalone testing