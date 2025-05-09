import Jetson.GPIO as GPIO
import time

# Set up the GPIO mode to BOARD
GPIO.setmode(GPIO.BOARD)  # You can also use GPIO.BCM

# Set up the GPIO pin (e.g., pin 11) as an output
GPIO.setup(11, GPIO.OUT)

# Toggle the GPIO pin 5 times
for _ in range(5):
    GPIO.output(11, GPIO.HIGH)  # Set the pin HIGH (3.3V)
    print("Pin 11 is HIGH")
    time.sleep(1)               # Wait for 1 second
    GPIO.output(11, GPIO.LOW)   # Set the pin LOW (0V)
    print("Pin 11 is LOW")
    time.sleep(1)               # Wait for 1 second

# Clean up the GPIO configuration
GPIO.cleanup()