import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(24, GPIO.IN)

try:
    while True:
        if GPIO.input(24) == GPIO.HIGH:
            print("Pin 24 is HIGH")
        else:
            print("Pin 24 is LOW")
        time.sleep(0.5)  # check twice a second
finally:
    GPIO.cleanup()