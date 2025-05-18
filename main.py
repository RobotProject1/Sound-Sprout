import os
import psutil
import subprocess
import sys
from threading import Thread
import time

try:
    import Jetson.GPIO as GPIO
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
    print(f"Running script: {script_path}")
    subprocess.Popen([sys.executable, script_path])

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

winter_pin = 4 #physical 7
spring_pin = 8 #physical 24
rainy_pin = 19 #physical 35

GPIO.setup(rainy_pin, GPIO.IN)  # button pin set as input
GPIO.setup(spring_pin, GPIO.IN)  # button pin set as input  
GPIO.setup(winter_pin, GPIO.IN)  # button pin set as input

ss_old = ''
ss_new = 'spring'

class choose_season(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
    def stop(self):
        self.running = False
    def run(self):
        global ss_old, ss_new
        while self.running:
            while len(ss_new) == 0:
                if GPIO.input(rainy_pin) == GPIO.HIGH:
                    ss_new = 'rainy'
                    print("Rainy season selected.")
                    break
                elif GPIO.input(spring_pin) == GPIO.HIGH:
                    ss_new = 'spring'
                    print("spring season selected.")
                    break
                elif GPIO.input(winter_pin) == GPIO.HIGH:
                    ss_new = 'winter'
                    print("Winter season selected.")
                    break
            
            if ss_new == ss_old:
                pass
            else:
                ss_old = ss_new
                kill_python_scripts_by_name(['spring_sound.py', 'rainy_sound.py','winter_sound.py'])
                if ss_new == 'rainy':
                    run_script('rainy_sound.py')
                elif ss_new == 'spring':
                    run_script('spring_sound.py')
                elif ss_new == 'winter':
                    run_script('winter_sound.py')
                ss_new = ''

if __name__ == '__main__':
    onoff_pin = 7 #physical 26
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(onoff_pin, GPIO.IN)
    target_scripts = ['playsound.py','spring_sound.py','rain_sound.py','winter_sound.py']
    # run_script('playsound.py')
    while True:
        GPIO.wait_for_edge(onoff_pin, GPIO.RISING)
        print("ON button pressed. Starting system...")
        # open('sound_sprout/active.flag', 'w').close()
        time.sleep(0.3)
        choose_season_thread = choose_season()
        choose_season_thread.start()
        run_script('playsound.py')
        GPIO.wait_for_edge(onoff_pin, GPIO.RISING)
        print("OFF button pressed. Stopping system...")
        # if os.path.exists('sound_sprout/active.flag'):
        #     os.remove('sound_sprout/active.flag')
        time.sleep(0.3)
        choose_season_thread.stop()
        ss_old = ''
        ss_new = 'spring'
        kill_python_scripts_by_name(target_scripts)