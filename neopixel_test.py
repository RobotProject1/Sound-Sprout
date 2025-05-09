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

import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D21, 8, brightness=0.2)

pixels.fill((255, 0, 0))  # Red
time.sleep(1)
pixels.fill((0, 255, 0))  # Green
time.sleep(1)
pixels.fill((0, 0, 255))  # Blue
time.sleep(1)
pixels.fill((0, 0, 0))    # Off