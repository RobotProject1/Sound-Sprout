import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import time

try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print(f"[{time.strftime('%H:%M:%S')}] I2C initialized")
    ads1 = ADS.ADS1115(i2c, address=0x48)
    print(f"[{time.strftime('%H:%M:%S')}] ADS1115 at 0x48 initialized")
    ads2 = ADS.ADS1115(i2c, address=0x49)
    print(f"[{time.strftime('%H:%M:%S')}] ADS1115 at 0x49 initialized")
except Exception as e:
    print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")