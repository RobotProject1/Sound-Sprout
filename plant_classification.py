from collections import deque
from shared_ads import ads1, ads2, read_adc
import time

pin1 = [0, 1, 2]
pin2 = [0, 1, 2]

# Queues to hold last 15 voltage readings for each pin
voltage_queues_1 = {pin: deque(maxlen=15) for pin in pin1}
voltage_queues_2 = {pin: deque(maxlen=15) for pin in pin2}

id2v_dict = [
    (4.10, 1), (3.87, 2), (3.67, 3), (3.59, 4), (3.20, 5), (2.98, 6),
    (2.64, 7), (2.18, 8), (1.99, 9), (1.75, 10), (1.50, 11), (1.15, 12)
]

def read_v():
    v_list = []
    for pin in pin1:
        voltage = read_adc(ads1, pin, samples=20, delay=0.02)  # More samples, longer delay
        if voltage is None:
            print(f"[{time.strftime('%H:%M:%S')}] Skipping pin {pin} (ads1) due to ADC read failure")
            voltage = 0.0
        voltage_queues_1[pin].append(voltage)
        avg_voltage = sum(voltage_queues_1[pin]) / len(voltage_queues_1[pin])
        print(f"[{time.strftime('%H:%M:%S')}] Pin {pin} (ads1): raw={voltage:.3f}V, avg={avg_voltage:.3f}V, queue={list(voltage_queues_1[pin])}")
        v_list.append(avg_voltage)
    for pin in pin2:
        voltage = read_adc(ads2, pin, samples=20, delay=0.02)
        if voltage is None:
            print(f"[{time.strftime('%H:%M:%S')}] Skipping pin {pin} (ads2) due to ADC read failure")
            voltage = 0.0
        voltage_queues_2[pin].append(voltage)
        avg_voltage = sum(voltage_queues_2[pin]) / len(voltage_queues_2[pin])
        print(f"[{time.strftime('%H:%M:%S')}] Pin {pin} (ads2): raw={voltage:.3f}V, avg={avg_voltage:.3f}V, queue={list(voltage_queues_2[pin])}")
        v_list.append(avg_voltage)
    return v_list

def read_id():
    try:
        v_list = read_v()
        id_list = []
        valid_ids = set(range(1, 13))
        for v in v_list:
            matched_id = 0
            for volt, id in id2v_dict:
                if abs(v - volt) < 0.1:  # Wider threshold (was 0.05)
                    if id in valid_ids:
                        matched_id = id
                        print(f"[{time.strftime('%H:%M:%S')}] Voltage {v:.3f}V matched to ID {id} (target {volt:.3f}V)")
                        break
            if matched_id == 0:
                print(f"[{time.strftime('%H:%M:%S')}] Voltage {v:.3f}V matched to no ID")
            id_list.append(matched_id)
        print(f"[{time.strftime('%H:%M:%S')}] Detected IDs: {id_list}")
        return id_list
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] read_id error: {e}")
        return [0] * (len(pin1) + len(pin2))