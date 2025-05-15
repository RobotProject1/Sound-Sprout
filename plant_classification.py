# import Jetson.GPIO as GPIO
# GPIO.setmode(GPIO.BCM)
# import ADS1x15

# ADS1 = ADS1x15.ADS1115(1, 0x48)
# ADS2 = ADS1x15.ADS1115(1, 0x49)
# f1 = ADS1.toVoltage()
# f2 = ADS2.toVoltage()
# #daisy sunflower clover potato radish carrot garlic pumpkin tomato corn cauliflower mushroom
# id2v_dict = [(4.78, 1), (4.35, 2), (3.98, 3), (3.64, 4), (3.33, 5), (3.03, 6), (2.67, 7), (2.38, 8), (2.13, 9), (1.79, 10), (1.56, 11), (1.09, 12)]
# pin1 = [1,2,3]
# pin2 = [1,2,3]
# ''
# def read_v():
#     return [ADS1.readADC(i)*f1 for i in pin1] + [ADS2.readADC(i)*f2 for i in pin2]    

# def read_id(v_list):
#     id_list = []
#     for v in v_list:
#         matched_id = 0
#         for volt, id in id2v_dict:
#             if abs(v - volt) < 0.1: 
#                 matched_id = id
#                 break
#         id_list.append(matched_id)
#     return id_list

import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize both ADS1115 devices with their I2C addresses
ads1 = ADS1115(i2c, address=0x48)
ads2 = ADS1115(i2c, address=0x49)

# Channel mapping
pin1 = [0, 1, 2]  # A0, A1, A2 on ADS1
pin2 = [0, 1, 2]  # A0, A1, A2 on ADS2

# Voltage-ID mapping
id2v_dict = [(4.78, 1), (4.35, 2), (3.98, 3), (3.64, 4), (3.33, 5), (3.03, 6),
             (2.67, 7), (2.38, 8), (2.13, 9), (1.79, 10), (1.56, 11), (1.09, 12)]

# Read voltages from both chips
def read_v():
    v_list = []
    for i in pin1:
        chan = AnalogIn(ads1, getattr(ADS1115, f"P{i}"))
        v_list.append(chan.voltage)
    for i in pin2:
        chan = AnalogIn(ads2, getattr(ADS1115, f"P{i}"))
        v_list.append(chan.voltage)
    return v_list

# Match voltage to closest known ID
def read_id(v_list):
    id_list = []
    for v in v_list:
        matched_id = 0
        for volt, id in id2v_dict:
            if abs(v - volt) < 0.1:
                matched_id = id
                break
        id_list.append(matched_id)
    return id_list

# Example usage
if __name__ == "__main__":
    voltages = read_v()
    ids = read_id(voltages)
    print("Voltages:", voltages)
    print("IDs:", ids)