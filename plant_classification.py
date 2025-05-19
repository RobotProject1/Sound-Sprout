# from adafruit_ads1x15.analog_in import AnalogIn
# from shared_ads import ads1, ads2

# pin1 = [0, 1, 2]
# pin2 = [0, 1, 2]

# # id2v_dict = [(4.78, 1), (4.35, 2), (3.98, 3), (3.64, 4), (3.33, 5), (3.03, 6), (2.67, 7), (2.38, 8), (2.13, 9), (1.79, 10), (1.56, 11), (1.09, 12)]
# id2v_dict = [(4.10, 1), (3.87, 2), (3.67, 3), (3.59, 4), (3.20, 5), (2.98, 6), (2.64, 7), (2.18, 8), (1.99, 9), (1.75, 10), (1.50, 11), (1.15, 12)]

# def read_v():
#     v_list = []
#     for pin in pin1:
#          chan = AnalogIn(ads1, pin)
#          v_list.append(chan.voltage)
#     for pin in pin2:
#         chan = AnalogIn(ads2, pin)
#         v_list.append(chan.voltage)
#     return v_list

# def read_id(v_list):
#     id_list = []
#     valid_ids = set(range(1,13))
#     for v in v_list:
#         matched_id = 0
#         for volt, id in id2v_dict:
#             if abs(v - volt) < 0.05:
#                matched_id = id
#                break
#         if matched_id != 0:
#             id_list.append(matched_id)
#     return id_list

import time
from adafruit_ads1x15.analog_in import AnalogIn
from shared_ads import ads1, ads2

# Define pins
pin1 = [0, 1, 2]
pin2 = [0, 1, 2]

# Mapping of voltage to ID
id2v_dict = [(4.10, 1), (3.87, 2), (3.67, 3), (3.59, 4), (3.20, 5), (2.98, 6),
             (2.64, 7), (2.18, 8), (1.99, 9), (1.75, 10), (1.50, 11), (1.15, 12)]

# Stability settings
tolerance = 0.05  # volts
stability_duration = 1.0  # seconds

# Initialize voltage tracking
last_stable_voltage = [0.0] * 6
last_change_time = [time.monotonic()] * 6
current_id = [0] * 6

def read_v():
    """Read voltages from all ADC channels"""
    v_list = []
    for pin in pin1:
         chan = AnalogIn(ads1, pin)
         v_list.append(chan.voltage)
    for pin in pin2:
        chan = AnalogIn(ads2, pin)
        v_list.append(chan.voltage)
    return v_list

def read_id_stable():
    """Read and return stable IDs from ADC voltages"""
    v_list = read_v()
    now = time.monotonic()
    id_list = []

    for i, v in enumerate(v_list):
        # Check stability
        if abs(v - last_stable_voltage[i]) < tolerance:
            if now - last_change_time[i] >= stability_duration:
                # Voltage stable → get ID
                matched_id = 0
                for volt, id in id2v_dict:
                    if abs(v - volt) < tolerance and id not in id_list:
                        matched_id = id
                        break
                current_id[i] = matched_id
        else:
            # Reset stability timer
            last_stable_voltage[i] = v
            last_change_time[i] = now
            current_id[i] = 0  # Not yet stable

        # Only add if valid
        if current_id[i] != 0:
            id_list.append(current_id[i])

    return id_list