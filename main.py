import os
import sys
from threading import Thread, Lock
import time
import Jetson.GPIO as GPIO
from multiprocessing import Queue
import importlib.util

# GPIO Pin Configuration (using BOARD mode, physical pin numbers)
ONOFF_PIN = 26
SEASONS = {
    'rainy': {'pin': 35, 'script': 'rainy_sound'},
    'spring': {'pin': 7, 'script': 'spring_sound'},
    'winter': {'pin': 23, 'script': 'winter_sound'}
}

running_threads = []
thread_lock = Lock()
current_season = None
audio_queue = Queue()  # Shared queue for audio paths

# Initialize I2C and ADC
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    ads1 = ADS1115(i2c, address=0x48)
    ads2 = ADS1115(i2c, address=0x49)
    print(f"[{time.strftime('%H:%M:%S')}] ADS1115 initialized: ads1={hex(0x48)}, ads2={hex(0x49)}")
except Exception as e:
    print(f"[{time.strftime('%H:%M:%S')}] ADS1115 initialization error: {e}")
    raise

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def stop_thread(thread):
    try:
        if thread.is_alive():
            module_name = getattr(thread, 'module_name', None)
            print(f"[{time.strftime('%H:%M:%S')}] Stopping {module_name}")
            thread.stop()
            thread.join(timeout=2)
            if thread.is_alive():
                print(f"[{time.strftime('%H:%M:%S')}] Thread {module_name} did not stop cleanly")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Thread {module_name} stopped")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error stopping thread: {e}")

def kill_scripts_by_name(target_names):
    with thread_lock:
        print(f"[{time.strftime('%H:%M:%S')}] Running threads before kill: {[t.module_name for t in running_threads if hasattr(t, 'module_name')]}")
        for thread in running_threads[:]:
            try:
                module_name = getattr(thread, 'module_name', None)
                if module_name in target_names:
                    stop_thread(thread)
                    running_threads.remove(thread)
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error in kill_scripts_by_name: {e}")
                running_threads.remove(thread)
        print(f"[{time.strftime('%H:%M:%S')}] Running threads after kill: {[t.module_name for t in running_threads if hasattr(t, 'module_name')]}")

def run_script(module_name, audio_queue, ads1, ads2):
    script_path = os.path.join(os.path.dirname(__file__), f"{module_name}.py")
    print(f"[{time.strftime('%H:%M:%S')}] Checking script path: {script_path}")
    if not os.path.exists(script_path):
        print(f"[{time.strftime('%H:%M:%S')}] ERROR: Script {script_path} not found.")
        return None
    try:
        module = load_module(module_name, script_path)
        thread = Thread(target=module.run, args=(audio_queue, ads1, ads2), daemon=True)
        thread.module_name = module_name  # Store module name for identification
        thread.start()
        with thread_lock:
            running_threads.append(thread)
        print(f"[{time.strftime('%H:%M:%S')}] Successfully started {module_name} thread")
        return thread
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to run {script_path}: {e}")
        return None

class choose_season(Thread):
    def __init__(self, audio_queue, ads1, ads2):
        Thread.__init__(self)
        self.running = True
        self.audio_queue = audio_queue
        self.ads1 = ads1
        self.ads2 = ads2
        print(f"[{time.strftime('%H:%M:%S')}] Initializing choose_season thread")
        for config in SEASONS.values():
            try:
                GPIO.setup(config['pin'], GPIO.IN)
                GPIO.add_event_detect(
                    config['pin'], GPIO.RISING, callback=self.handle_button, bouncetime=300
                )
                print(f"[{time.strftime('%H:%M:%S')}] Set up GPIO pin {config['pin']} for {config['script']}")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Failed to set up GPIO pin {config['pin']}: {e}")

    def handle_button(self, pin):
        global current_season
        print(f"[{time.strftime('%H:%M:%S')}] Button pressed on pin {pin}")
        try:
            for season, config in SEASONS.items():
                if pin == config['pin']:
                    if current_season == season:
                        print(f"[{time.strftime('%H:%M:%S')}] {season.capitalize()} already running, skipping")
                        break
                    print(f"[{time.strftime('%H:%M:%S')}] {season.capitalize()} season selected")
                    print(f"[{time.strftime('%H:%M:%S')}] Killing season scripts before starting {config['script']}")
                    kill_scripts_by_name([c['script'] for c in SEASONS.values()])
                    print(f"[{time.strftime('%H:%M:%S')}] Starting {config['script']}")
                    run_script(config['script'], self.audio_queue, self.ads1, self.ads2)
                    current_season = season
                    break
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] No match for pin {pin} with season {season}")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error in handle_button: {e}")

    def stop(self):
        self.running = False
        for config in SEASONS.values():
            try:
                GPIO.remove_event_detect(config['pin'])
                print(f"[{time.strftime('%H:%M:%S')}] Removed event detection for pin {config['pin']}")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] Error removing event detection for pin {config['pin']}: {e}")
        print(f"[{time.strftime('%H:%M:%S')}] choose_season thread stopped")

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ONOFF_PIN, GPIO.IN)
    target_scripts = ['playsound', 'plant_classification', 'spring_sound', 'rainy_sound', 'winter_sound']
    print(f"[{time.strftime('%H:%M:%S')}] Main script started")
    try:
        while True:
            GPIO.wait_for_edge(ONOFF_PIN, GPIO.RISING)
            print(f"[{time.strftime('%H:%M:%S')}] ON button pressed. Starting system...")
            time.sleep(0.3)
            choose_season_thread = choose_season(audio_queue, ads1, ads2)
            choose_season_thread.start()
            run_script('playsound', audio_queue, ads1, ads2)
            GPIO.wait_for_edge(ONOFF_PIN, GPIO.RISING)
            print(f"[{time.strftime('%H:%M:%S')}] OFF button pressed. Stopping system...")
            time.sleep(0.3)
            choose_season_thread.stop()
            kill_scripts_by_name(target_scripts)
            # Clear the queue on shutdown
            while not audio_queue.empty():
                audio_queue.get()
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down...")
        kill_scripts_by_name(target_scripts)
        GPIO.cleanup()
        while not audio_queue.empty():
            audio_queue.get()
    finally:
        i2c.deinit()