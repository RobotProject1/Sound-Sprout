# import board
# import neopixel
# import time

# NUM_PIXELS = 8
# pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS, brightness=0.3, auto_write=False)

# def wheel(pos):
#     if pos < 85:
#         return (255 - pos * 3, pos * 3, 0)
#     elif pos < 170:
#         pos -= 85
#         return (0, 255 - pos * 3, pos * 3)
#     else:
#         pos -= 170
#         return (pos * 3, 0, 255 - pos * 3)

# def rainbow_cycle(wait):
#     for j in range(255):
#         for i in range(NUM_PIXELS):
#             rc_index = (i * 256 // NUM_PIXELS) + j
#             pixels[i] = wheel(rc_index & 255)
#         pixels.show()
#         time.sleep(wait)

# while True:
#     rainbow_cycle(0.05)

import time
from neopixel import Adafruit_NeoPixel, Color

LED_COUNT = 8        # Number of LED pixels.
LED_PIN = 21         # GPIO pin (GPIO21 = physical pin 40)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN)
strip.begin()

# Red
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(255, 0, 0))
strip.show()
time.sleep(1)

# Green
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 255, 0))
strip.show()
time.sleep(1)

# Blue
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 0, 255))
strip.show()
time.sleep(1)

# Off
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(0, 0, 0))
strip.show()