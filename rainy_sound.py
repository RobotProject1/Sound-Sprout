import time
import os
from threading import Thread
from shared_ads import ads1, read_adc
from plant_classification import read_id
import multiprocessing
import pickle

class readnwrite(Thread):
    def __init__(self, sender_conn):
        Thread.__init__(self)
        self.running = True
        self.sender_conn = sender_conn

    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] readnwrite thread started (PID: {os.getpid()})")
        try:
            while self.running:
                try:
                    # Read audio paths for the current season, including ambient
                    audio_paths = read_id('rainy')
                    print(f"[{time.strftime('%H:%M:%S')}] Detected audio paths: {audio_paths}")
                    
                    # Send to pipe (ambient always included by plant_classification)
                    self.sender_conn.send(audio_paths)
                    print(f"[{time.strftime('%H:%M:%S')}] Sent to pipe: {audio_paths}")
                    
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
    print(f"[{time.strftime('%H:%M:%S')}] rainy_sound.py started (PID: {os.getpid()})")
    # Deserialize pipe sender end from command-line argument
    sender_fd = pickle.loads(bytes.fromhex(sys.argv[1])) if len(sys.argv) > 1 else None
    sender_conn = multiprocessing.reduction.rebuild_pipe_connection(sender_fd, readable=False, writable=True)
    try:
        readnwrite_thread = readnwrite(sender_conn)
        readnwrite_thread.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down rainy_sound.py")
        readnwrite_thread.stop()
        readnwrite_thread.join()
        sender_conn.close()
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Fatal error in rainy_sound.py: {e}")
        readnwrite_thread.stop()
        readnwrite_thread.join()
        sender_conn.close()