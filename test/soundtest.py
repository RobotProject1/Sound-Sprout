import os
import time
from threading import Thread
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c, address=0x49)

class VolumeTest(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.last_volume_percent = None

    def run(self):
        while True:
            vol = AnalogIn(ads, 3)
            voltage = vol.voltage
            voltage = min(max(voltage, 0), 5.0)  # Clamp between 0 and 5V
            volume_percent = int((voltage / 5.0) * 100)

            if self.last_volume_percent is None or abs(volume_percent - self.last_volume_percent) >= 5:
                print(f"Voltage: {voltage:.2f} V -> Volume: {volume_percent}%")
                os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volume_percent}%")
                self.last_volume_percent = volume_percent

            time.sleep(0.2)  # Adjust polling rate if needed

if __name__ == "__main__":
    adjust_volume_thread = VolumeTest()
    adjust_volume_thread.start()
    print("Potentiometer check started")