from collections import deque
from adafruit_ads1x15.analog_in import AnalogIn
from shared_ads import ads1, ads2

pin1 = [0, 1, 2]
pin2 = [0, 1, 2]

# Queues to hold last 5 voltage readings for each pin
voltage_queues_1 = {pin: deque(maxlen=15) for pin in pin1}
voltage_queues_2 = {pin: deque(maxlen=15) for pin in pin2}

id2v_dict = [(4.10, 1), (3.87, 2), (3.67, 3), (3.59, 4), (3.20, 5), (2.98, 6), (2.64, 7), (2.18, 8), (1.99, 9), (1.75, 10), (1.50, 11), (1.15, 12)]

def read_v():
    v_list = []
    for pin in pin1:
        chan = AnalogIn(ads1, pin)
        voltage_queues_1[pin].append(chan.voltage)
        avg_voltage = sum(voltage_queues_1[pin]) / len(voltage_queues_1[pin])
        print(f"Pin {pin} (ads1): raw={chan.voltage:.2f}V, avg={avg_voltage:.2f}V")
        v_list.append(avg_voltage)
    for pin in pin2:
        chan = AnalogIn(ads2, pin)
        voltage_queues_2[pin].append(chan.voltage)
        avg_voltage = sum(voltage_queues_2[pin]) / len(voltage_queues_2[pin])
        print(f"Pin {pin} (ads2): raw={chan.voltage:.2f}V, avg={avg_voltage:.2f}V")
        v_list.append(avg_voltage)
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
                    print(f"Voltage {v:.2f}V matched to ID {id}")
                    break
        if matched_id == 0:
            print(f"Voltage {v:.2f}V matched to no ID")
        id_list.append(matched_id)
    print(f"Detected IDs: {id_list}")
    return id_list