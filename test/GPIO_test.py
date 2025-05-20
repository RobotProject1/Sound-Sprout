import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.IN) #button 1
GPIO.setup(23, GPIO.IN) #button 2
GPIO.setup(35, GPIO.IN) #button 3
GPIO.setup(26, GPIO.IN) #button 4

try:
    while True:
        if GPIO.input(7) == GPIO.HIGH:
            print("Button 1 is HIGH")
        else:
            print("Button 1 is LOW")
        if GPIO.input(23) == GPIO.HIGH:
            print("Button 2 is HIGH")
        else:
            print("Button 2 is LOW")
        if GPIO.input(35) == GPIO.HIGH:
            print("Button 3 is HIGH")
        else:
            print("Button 3 is LOW")
        if GPIO.input(26) == GPIO.HIGH:
            print("On/off Button is HIGH")
        else:
            print("On/off Button is LOW")
        time.sleep(0.5)  # check twice a second
finally:
    GPIO.cleanup() 