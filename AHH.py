import time
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADC object
ads = ADS1115(i2c)

# Create single-ended input channels
chan0 = AnalogIn(ads, ADS1115.P0)  # A0 (Button 1)
chan1 = AnalogIn(ads, ADS1115.P1)  # A1 (Button 2)
chan2 = AnalogIn(ads, ADS1115.P2)  # A2 (Button 3)
chan3 = AnalogIn(ads, ADS1115.P3)  # A3 (Potentiometer)

print("Reading voltages from A0-A3... (Ctrl+C to stop)")
try:
    while True:
        print(f"A0: {chan0.voltage:.3f} V  |  A1: {chan1.voltage:.3f} V  |  A2: {chan2.voltage:.3f} V  |  A3: {chan3.voltage:.3f} V")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nStopped.")