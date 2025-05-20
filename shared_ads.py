import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
import threading
import time
import os

i2c_lock = threading.Lock()

def get_i2c():
    with i2c_lock:
        print(f"[{time.strftime('%H:%M:%S')}] Initializing I2C (PID: {os.getpid()})")
        for _ in range(3):  # Retry 3 times
            try:
                return busio.I2C(board.SCL, board.SDA)
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] I2C init attempt failed: {e}")
                time.sleep(0.5)
        raise RuntimeError("Failed to initialize I2C after retries")

try:
    i2c = get_i2c()
    ads1 = None
    ads2 = None
    for _ in range(3):  # Retry ADC initialization
        try:
            if not ads1:
                ads1 = ADS1115(i2c, address=0x48)
                print(f"[{time.strftime('%H:%M:%S')}] ADS1115 initialized: ads1={hex(0x48)}")
            if not ads2:
                ads2 = ADS1115(i2c, address=0x49)
                print(f"[{time.strftime('%H:%M:%S')}] ADS1115 initialized: ads2={hex(0x49)}")
            break
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ADS1115 init attempt failed: {e}")
            time.sleep(0.5)
    if not ads1 or not ads2:
        raise RuntimeError("Failed to initialize ADS1115 after retries")
except Exception as e:
    print(f"[{time.strftime('%H:%M:%S')}] ADS1115 initialization error: {e}")
    raise