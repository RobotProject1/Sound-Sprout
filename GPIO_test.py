import Jetson.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Disable warnings

GPIO.setup(26, GPIO.IN)

try:
    print("Waiting for rising edge on pin 24...")
    GPIO.wait_for_edge(24, GPIO.RISING)
    print("ON")
finally:
    GPIO.cleanup()