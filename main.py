import os
import psutil
import subprocess
import sys

try:
    import jetson.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    class MockGPIO:
        BCM = BOARD = IN = OUT = HIGH = LOW = None
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, state): pass
        def input(self, pin): return False
        def cleanup(self): pass
        def wait_for_edge(self, pin, edge_type):
            print(f"Simulating waiting for {edge_type} edge on pin {pin}")
            return True
    GPIO = MockGPIO()

onoff_pin = 18
GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
GPIO.setup(onoff_pin, GPIO.IN)  # button pin set as input

def kill_python_scripts_by_name(target_names): # ex ['lighting_rainy.py', 'lighting_summer.py']
    """
    Kill all running Python scripts whose command lines include one of the target names.
    Does not kill the currently running script.
    """
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            cmdline = proc.info['cmdline']
            if cmdline and 'python' in cmdline[0].lower():
                for name in target_names:
                    if any(name in part for part in cmdline[1:]):  # check script path/args
                        print(f"Killing PID {proc.info['pid']}: {' '.join(cmdline)}")
                        proc.kill()
                        break

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def run_script(script_name): # ex 'lighting_rainy.py'
    """
    Run a Python script using subprocess, cross-platform.
    """
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    subprocess.Popen([sys.executable, script_path], shell=False)

target_scripts = ['lighting_rainy.py', 'lighting_summer.py','lighting_winter.py','choose_season.py','main.py','playsound.py','summer_sound.py','rain_sound.py','winter_sound.py']

if __name__ == '__main__':
    while True:
        GPIO.wait_for_edge(onoff_pin, "GPIO.FALLING")
        run_script('choose_season.py')
        run_script('playsound.py')
        GPIO.wait_for_edge(onoff_pin, 'GPIO.FALLING')
        kill_python_scripts_by_name(target_scripts)

# run_script('choose_season.py')
# run_script('playsound.py')
# kill_python_scripts_by_name(target_scripts)