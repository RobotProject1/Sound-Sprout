import Jetson.GPIO as GPIO

# Set up the GPIO mode to BOARD
GPIO.setmode(GPIO.BOARD)  # You can also use GPIO.BCM

# Set up the GPIO pin (e.g., pin 11) as an output
GPIO.setup(26, GPIO.IN)

if GPIO.wait_for_edge(26, GPIO.RISING):
    print("ON")

# Clean up the GPIO configuration
GPIO.cleanup()