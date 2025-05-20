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
        for _ in range(5):  # Increased retries
            try:
                return busio.I2C(board.SCL, board.SDA)
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] I2C init attempt failed: {e}")
                time.sleep(0.5)
        raise RuntimeError("Failed to initialize I2C after retries")

def read_adc(ads, pin, samples=20, delay=0.02):
    with i2c_lock:
        try:
            from adafruit_ads1x15.analog_in import AnalogIn
            values = []
            for _ in range(samples):
                chan = AnalogIn(ads, pin)
                values.append(chan.voltage)
                time.sleep(delay)
            avg_voltage = sum(values) / len(values)
            print(f"[{time.strftime('%H:%M:%S')}] Read ADC (PID: {os.getpid()}, pin: {pin}): {avg_voltage:.3f}V")
            return avg_voltage
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ADC read error (PID: {os.getpid()}, pin: {pin}): {e}")
            return None

try:
    i2c = get_i2c()
    ads1 = None
    ads2 = None
    for _ in range(5):  # Increased retries
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