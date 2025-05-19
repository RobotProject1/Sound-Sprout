from threading import Lock
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115

i2c = busio.I2C(board.SCL, board.SDA)

ads1 = ADS1115(i2c, address=0x48)
ads2 = ADS1115(i2c, address=0x49)

ads2_lock = Lock()