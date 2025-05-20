import os
import psutil
import subprocess
import sys
from threading import Thread, Lock
import time
import Jetson.GPIO as GPIO

# GPIO Pin Configuration (using BOARD mode, physical pin numbers)
ONOFF_PIN = 26  # Physical 26
SEASONS = {
    'rainy': {'pin': 35, 'script': 'rainy_sound.py'},  # Physical 35
    'spring': {'pin': 7, 'script': 'spring_sound.py'},  # Physical 7
    'winter': {'pin': 23, 'script': 'winter_sound.py'}  # Physical 23
}

running_processes = []
process_lock = Lock()

def kill_python_scripts_by_name(target_names):
    """Kill running Python scripts matching target names."""
    with process_lock:
        print(f"[{time.strftime('%H:%M:%S')}] Running processes before kill: {[proc.pid for proc in running_processes]}")
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
                running_processes.remove(proc)
        print(f"[{time.strftime('%H:%M:%S')}] Running processes after kill: {[proc.pid for proc in running_processes]}")

def run_script(script_name):
    """Run a Python script in a subprocess and track its process."""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    if not os.path.exists(script_path):
        print(f"[{time.strftime('%H:%M:%S')}] ERROR: Script {script_path} not found.")
        return None
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Attempting to run script: {script_path}")
        proc = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        with process_lock:
            running_processes.append(proc)
        print(f"[{time.strftime('%H:%M:%S')}] Successfully started {script_name} with PID {proc.pid}")
        # Check initial output to catch immediate errors
        try:
            stdout, stderr = proc.communicate(timeout=5)
            if stdout:
                print(f"[{time.strftime('%H:%M:%S')}] {script_name} stdout: {stdout}")
            if stderr:
                print(f"[{time.strftime('%H:%M:%S')}] {script_name} stderr: {stderr}")
        except subprocess.TimeoutExpired:
            print(f"[{time.strftime('%H:%M:%S')}] {script_name} still running (PID {proc.pid})")
        return proc
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Failed to run {script_path}: {e}")
        return None

class choose_season(Thread):
    """Thread to handle season selection based on GPIO button presses."""
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        print(f"[{time.strftime('%H:%M:%S')}] Initializing choose_season thread")
        for config in SEASONS.values():
            GPIO.setup(config['pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(
                config['pin'], GPIO.RISING, callback=self.handle_button, bouncetime=300
            )
            print(f"[{time.strftime('%H:%M:%S')}] Set up GPIO pin {config['pin']} for {config['script']}")

    def handle_button(self, pin):
        """Handle button press to select a season."""
        print(f"[{time.strftime('%H:%M:%S')}] Button pressed on pin {pin}")
        for season, config in SEASONS.items():
            if pin == config['pin']:
                print(f"[{time.strftime('%H:%M:%S')}] {season.capitalize()} season selected")
                kill_python_scripts_by_name([c['script'] for c in SEASONS.values()])
                run_script(config['script'])
                break
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No match for pin {pin} with season {season}")

    def stop(self):
        """Clean up GPIO event detection."""
        self.running = False
        for config in SEASONS.values():
            GPIO.remove_event_detect(config['pin'])
        print(f"[{time.strftime('%H:%M:%S')}] choose_season thread stopped")

if __name__ == "__main__":
    GPIO.setwarnings(False)  # Disable GPIO warnings
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(ONOFF_PIN, GPIO.IN)
    target_scripts = ['playsound.py', 'plant_classification.py', 'spring_sound.py', 'rainy_sound.py', 'winter_sound.py']
    print(f"[{time.strftime('%H:%M:%S')}] Main script started")
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
            kill_python_scripts_by_name(target_scripts)
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down...")
        kill_python_scripts_by_name(target_scripts)
        GPIO.cleanup()

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    print(f"[{time.strftime('%H:%M:%S')}] Main script started")
    try:
        run_script('spring_sound.py')  # Run directly
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"[{time.strftime('%H:%M:%S')}] Shutting down...")
        kill_python_scripts_by_name(['spring_sound.py'])
        GPIO.cleanup()