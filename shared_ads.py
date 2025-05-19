# import board
# import busio
# from adafruit_ads1x15.ads1115 import ADS1115

# i2c = busio.I2C(board.SCL, board.SDA)

# ads1 = ADS1115(i2c, address=0x48)
# ads2 = ADS1115(i2c, address=0x49)

from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.ads1x15 import Mode
import busio
import board

i2c = busio.I2C(board.SCL, board.SDA)
ads1 = ADS1115(i2c, address=0x48)
ads2 = ADS1115(i2c, address=0x49)
ads2.gain = 4  # set gain to ±4.096V; try 2 for ±2.048V or 4 for ±1.024V
ads2.mode = Mode.SINGLE  # Use SINGLE mode (slower, more precise)