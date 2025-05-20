import os
import psutil
import subprocess
import sys
from threading import Thread, Lock
import time
import Jetson.GPIO as GPIO

ONOFF_PIN = 9
SEASONS = {
    'rainy': {'pin': 19, 'script': 'rainy_sound.py'},
    'spring': {'pin': 8, 'script': 'spring_sound.py'},
    'winter': {'pin': 4, 'script': 'winter_sound.py'}
}

running_processes = []
process_lock = Lock()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def kill_python_scripts_by_name(target_names):
    with process_lock:
        for proc in running_processes[:]:
            try:
                if proc.poll() is None:
                    cmdline = proc.cmdline()
                    for name in target_names:
                        if any(name in part for part in cmdline[1:]):
                            print(f"[{time.strftime('%H:%M:%S')}] Terminating PID {proc.pid}: {' '.join(cmdline)}")
                            proc.terminate()
                            try:
                                proc.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                print(f"[{time.strftime('%H:%M:%S')}] Force killing PID {proc.pid}")
                                proc.kill()
                            running_processes.remove(proc)
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"[{time.strftime('%H:%M:%S')}] Process {proc.pid} no longer exists or access denied")
                running_processes.remove(proc)

def run_script(script_name):
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"[{time.strftime('%H:%M:%S')}] Script {script_path} not found.")
        return None
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Running script: {script_path} (Main PID: {os.getpid()})")
        proc = subprocess.Popen([sys.executable, script_path], cwd=BASE_DIR,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        with process_lock:
            running_processes.append(proc)
        print(f"[{time.strftime('%H:%M:%S')}] Started process PID: {proc.pid}")
        def stream_output(proc):
            while proc.poll() is None:
                line = proc.stdout.readline()
                if line:
                    print(f"[{time.strftime('%H:%M:%S')}] [{proc.pid}] {line.strip()}")
                err = proc.stderr.readline()
                if err:
                    print(f"[{time.strftime('%H:%M:%S')}] [{proc.pid}] ERROR: {err.strip()}")
        Thread(target=stream_output, args=(proc,), daemon=True).start()
        return proc
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to run {script_path}: {e}")
        return None

class choose_season(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.ss_old = ''
        self.ss_new = 'spring'
        for season, config in SEASONS.items():
            GPIO.add_event_detect(
                config['pin'], GPIO.RISING, callback=self.handle_button, bouncetime=200
            )

    def handle_button(self, pin):
        for season, config in SEASONS.items():
            if pin == config['pin']:
                self.ss_new = season
                print(f"[{time.strftime('%H:%M:%S')}] {season.capitalize()} season selected.")
                if self.ss_new != self.ss_old:
                    self.ss_old = self.ss_new
                    kill_python_scripts_by_name([config['script'] for config in SEASONS.values()])
                    run_script(SEASONS[self.ss_new]['script'])
                    self.ss_new = ''
                break

    def stop(self):
        self.running = False
        for season, config in SEASONS.items():
            GPIO.remove_event_detect(config['pin'])

if __name__ == '__main__':
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ONOFF_PIN, GPIO.IN)
    for season, config in SEASONS.items():
        GPIO.setup(config['pin'], GPIO.IN)

    target_scripts = ['playsound.py', 'plant_classification.py', 'spring_sound.py', 'rainy_sound.py', 'winter_sound.py']

    try:
        while True:
            GPIO.wait_for_edge(ONOFF_PIN, GPIO.RISING)
            print(f"[{time.strftime('%H:%M:%S')}] ON button pressed. Starting system...")
            time.sleep(0.3)
            choose_season_thread = choose_season()
            choose_season_thread.start()
            run_script('playsound.py')
            GPIO.wait_for_edge(ONOFF_PIN, GPIO.RISING)
            print(f"[{time.strftime('%H:%M:%S')}] OFF button pressed. Stopping system...")
            time.sleep(0.3)
            choose_season_thread.stop()
            choose_season_thread.join()
            kill_python_scripts_by_name(target_scripts)
    finally:
        GPIO.cleanup()
        print(f"[{time.strftime('%H:%M:%S')}] GPIO resources cleaned up.")