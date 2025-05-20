import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.IN) #button 1
GPIO.setup(24, GPIO.IN) #button 2
GPIO.setup(35, GPIO.IN) #button 3

try:
    while True:
        if GPIO.input(7) == GPIO.HIGH:
            print("Pin 7 is HIGH")
        else:
            print("Pin 7 is LOW")
        if GPIO.input(24) == GPIO.HIGH:
            print("Pin 24 is HIGH")
        else:
            print("Pin 24 is LOW")
        if GPIO.input(35) == GPIO.HIGH:
            print("Pin 35 is HIGH")
        else:
            print("Pin 35 is LOW")
        time.sleep(0.5)  # check twice a second
finally:
    GPIO.cleanup() 