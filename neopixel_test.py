import time
from rpi_ws281x import PixelStrip, Color

# LED strip configuration
LED_COUNT = 10          # Number of LEDs in your strip
LED_PIN = 18            # GPIO18 (pin 12), must be a PWM-capable pin
LED_FREQ_HZ = 800000    # WS2812 signal frequency
LED_DMA = 10            # DMA channel to use
LED_BRIGHTNESS = 255    # Set brightness (0 to 255)
LED_INVERT = False      # Invert signal (normally False)
LED_CHANNEL = 0         # Channel 0 = GPIO18 (use 1 if you use GPIO13/pin 33)

# Create PixelStrip object and initialize
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                   LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def clear_strip(strip):
    """Turn off all LEDs"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def chase_effect(strip, color, delay_ms=50, repeats=3):
    """Light moves from start to end, repeated multiple times"""
    for _ in range(repeats):
        for i in range(strip.numPixels()):
            clear_strip(strip)
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(delay_ms / 1000.0)
    clear_strip(strip)

# Main execution
try:
    chase_effect(strip, Color(0, 0, 255), delay_ms=100, repeats=3)  # Blue dot moves 3 times

except KeyboardInterrupt:
    pass

finally:
    clear_strip(strip)