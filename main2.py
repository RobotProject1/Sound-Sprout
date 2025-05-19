import time
from seasons_select import choose_season, run_script, kill_python_scripts_by_name
import Jetson.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

onoff_pin = 7  # physical 26
GPIO.setup(onoff_pin, GPIO.IN)

# Scripts to kill
target_scripts = ['playsound.py','spring_sound.py','rainy_sound.py','winter_sound.py']

run_script('playsound.py')

while True:
    GPIO.wait_for_edge(onoff_pin, GPIO.RISING)
    print("ON button pressed. Starting system...")
    time.sleep(0.3)

    choose_season_thread = choose_season()
    choose_season_thread.start()

    GPIO.wait_for_edge(onoff_pin, GPIO.RISING)
    print("OFF button pressed. Stopping system...")
    time.sleep(0.3)

    choose_season_thread.stop()
    choose_season_thread.join()
    kill_python_scripts_by_name(target_scripts)