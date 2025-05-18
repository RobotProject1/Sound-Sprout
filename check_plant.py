# import board
# import busio
# from adafruit_ads1x15.ads1115 import ADS1115
# from adafruit_ads1x15.analog_in import AnalogIn
# import time

# # Initialize I2C and both ADS1115 ADCs
# i2c = busio.I2C(board.SCL, board.SDA)
# ads1 = ADS1115(i2c, address=0x48)
# ads2 = ADS1115(i2c, address=0x49)

# # Define pins to read (A0, A1, A2)
# pins = [0, 1, 2]

# print("Reading voltages from ADS1115 devices (press Ctrl+C to stop)\n")

# try:
#     while True:
#         for pin in pins:
#             chan1 = AnalogIn(ads1, pin)
#             chan2 = AnalogIn(ads2, pin)
#             print(f"ADS1 A{pin}: {chan1.voltage:.2f} V | ADS2 A{pin}: {chan2.voltage:.2f} V")
#         print("-" * 40)
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Exiting...")

import time
from plant_classification import read_id, read_v

def main():
    print("Checking plant IDs...")
    while True:
        voltage_list = read_v()
        id_list = read_id(voltage_list)
        print("Plant IDs:", id_list)
        time.sleep(1)  # Adjust if you want faster or slower updates

if __name__ == "__main__":
    main()