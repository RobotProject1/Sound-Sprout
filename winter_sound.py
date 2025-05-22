import time
from threading import Thread
from plant_classification import read_id
from multiprocessing import Queue

class readnwrite(Thread):
    def __init__(self, audio_queue, ads1, ads2):
        Thread.__init__(self)
        self.running = True
        self.audio_queue = audio_queue
        self.ads1 = ads1
        self.ads2 = ads2

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started")
        try:
            while self.running:
                try:
                    # Read audio paths for the current season, including ambient
                    audio_paths = read_id('winter', self.ads1, self.ads2)
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

def run(audio_queue, ads1, ads2):
    print(f"[{time.strftime('%H:%M:%S')}] winter_sound.py started")
    try:
        readnwrite_thread = readnwrite(audio_queue, ads1, ads2)
        readnwrite_thread.start()
        while readnwrite_thread.running:
            time.sleep(1)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Fatal error in winter_sound.py: {e}")
    finally:
        readnwrite_thread.stop()
        readnwrite_thread.join()

def stop():
    readnwrite.running = False

if __name__ == "__main__":
    from adafruit_ads1x15.ads1115 import ADS1115
    import board
    import busio
    i2c = busio.I2C(board.SCL, board.SDA)
    ads1 = ADS1115(i2c, address=0x48)
    ads2 = ADS1115(i2c, address=0x49)
    run(Queue(), ads1, ads2)  # Fallback for standalone testing