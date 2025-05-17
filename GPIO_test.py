import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(35, GPIO.IN)

try:
    while True:
        if GPIO.input(35) == GPIO.HIGH:
            print("Pin 35 is HIGH")
        else:
            print("Pin 35 is LOW")
        time.sleep(0.5)  # check twice a second
finally:
    GPIO.cleanup()