from main import run_script
import jetson.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)
rainy_pin = 18
summer_pin = 23
winter_pin = 24

GPIO.setup(rainy_pin, GPIO.IN)  # button pin set as input
GPIO.setup(summer_pin, GPIO.IN)  # button pin set as input  
GPIO.setup(winter_pin, GPIO.IN)  # button pin set as input

while True:


print("Choose a season:")
