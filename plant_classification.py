from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from shared_ads import ads1, ads2

pin1 = [0, 1, 2]
pin2 = [0, 1, 2]

# id2v_dict = [(4.78, 1), (4.35, 2), (3.98, 3), (3.64, 4), (3.33, 5), (3.03, 6), (2.67, 7), (2.38, 8), (2.13, 9), (1.79, 10), (1.56, 11), (1.09, 12)]
id2v_dict = [(4.10, 1), (3.87, 2), (3.67, 3), (3.59, 4), (3.20, 5), (2.98, 6), (2.64, 7), (2.18, 8), (1.99, 9), (1.75, 10), (1.50, 11), (1.15, 12)]

def read_v():
    v_list = []
    for pin in pin1:
         chan = AnalogIn(ads1, pin)
         v_list.append(chan.voltage)
    for pin in pin2:
        chan = AnalogIn(ads2, pin)
        v_list.append(chan.voltage)
    return v_list

def read_id(v_list):
    id_list = []
    valid_ids = set(range(1,13))
    for v in v_list:
        matched_id = 0
        for volt, id in id2v_dict:
            if abs(v - volt) < 0.05:
                if id in valid_ids:
                    matched_id = id
                    break
        if matched_id != 0:
            id_list.append(matched_id)
    return id_list