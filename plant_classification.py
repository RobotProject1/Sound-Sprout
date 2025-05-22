from collections import deque
import time
from threading import Lock
from adafruit_ads1x15.analog_in import AnalogIn

adc_lock = Lock()

pin1 = [0, 1, 2]
pin2 = [0, 1, 2]

# Queues to hold last 15 voltage readings for each pin
voltage_queues_1 = {pin: deque(maxlen=15) for pin in pin1}
voltage_queues_2 = {pin: deque(maxlen=15) for pin in pin2}

id2v_dict = [
    (4.10, 1), (3.87, 2), (3.67, 3), (3.59, 4), (3.20, 5), (2.98, 6),
    (2.64, 7), (2.18, 8), (1.99, 9), (1.75, 10), (1.50, 11), (1.15, 12)
]

# Mapping of plant IDs to audio files for each season, with ambient sound for rainy and winter only
season_tracks = {
    'spring': {
        1: 'sound_sprout/sound/spring/Potato.wav',
        2: 'sound_sprout/sound/spring/Tomato.wav',
        3: 'sound_sprout/sound/spring/Carrot.wav',
        4: 'sound_sprout/sound/spring/Sunflower.wav',
        5: 'sound_sprout/sound/spring/Daisy.wav',
        6: 'sound_sprout/sound/spring/Mushroom.wav',
        7: 'sound_sprout/sound/spring/Shallot.wav',
        8: 'sound_sprout/sound/spring/Clover.wav',
        9: 'sound_sprout/sound/spring/Corn.wav',
        10: 'sound_sprout/sound/spring/Pumpkin.wav',
        11: 'sound_sprout/sound/spring/Cauliflower.wav',
        12: 'sound_sprout/sound/spring/Radish.wav'
    },
    'rainy': {
        'ambient': 'sound_sprout/sound/rainy/AMBIENT.wav',
        1: 'sound_sprout/sound/rainy/Potato.wav',
        2: 'sound_sprout/sound/rainy/Tomato.wav',
        3: 'sound_sprout/sound/rainy/Carrot.wav',
        4: 'sound_sprout/sound/rainy/Sunflower.wav',
        5: 'sound_sprout/sound/rainy/Daisy.wav',
        6: 'sound_sprout/sound/rainy/Mushroom.wav',
        7: 'sound_sprout/sound/rainy/Shallot.wav',
        8: 'sound_sprout/sound/rainy/Clover.wav',
        9: 'sound_sprout/sound/rainy/Corn.wav',
        10: 'sound_sprout/sound/rainy/Pumpkin.wav',
        11: 'sound_sprout/sound/rainy/Cauliflower.wav',
        12: 'sound_sprout/sound/rainy/Radish.wav'
    },
    'winter': {
        'ambient': 'sound_sprout/sound/winter/AMBIENT.wav',
        1: 'sound_sprout/sound/winter/Potato.wav',
        2: 'sound_sprout/sound/winter/Tomato.wav',
        3: 'sound_sprout/sound/winter/Carrot.wav',
        4: 'sound_sprout/sound/winter/Sunflower.wav',
        5: 'sound_sprout/sound/winter/Daisy.wav',
        6: 'sound_sprout/sound/winter/Mushroom.wav',
        7: 'sound_sprout/sound/winter/Shallot.wav',
        8: 'sound_sprout/sound/winter/Clover.wav',
        9: 'sound_sprout/sound/winter/Corn.wav',
        10: 'sound_sprout/sound/winter/Pumpkin.wav',
        11: 'sound_sprout/sound/winter/Cauliflower.wav',
        12: 'sound_sprout/sound/winter/Radish.wav'
    }
}

def read_v(ads1, ads2):
    v_list = []
    for pin in pin1:
        voltage = read_adc(ads1, pin)
        if voltage is None:
            print(f"[{time.strftime('%H:%M:%S')}] Skipping pin {pin} (ads1) due to ADC read failure")
            voltage = 0.0
        voltage_queues_1[pin].append(voltage)
        avg_voltage = sum(voltage_queues_1[pin]) / len(voltage_queues_1[pin])
        print(f"[{time.strftime('%H:%M:%S')}] Pin {pin} (ads1): raw={voltage:.2f}V, avg={avg_voltage:.2f}V")
        v_list.append(avg_voltage)
    for pin in pin2:
        voltage = read_adc(ads2, pin)
        if voltage is None:
            print(f"[{time.strftime('%H:%M:%S')}] Skipping pin {pin} (ads2) due to ADC read failure")
            voltage = 0.0
        voltage_queues_2[pin].append(voltage)
        avg_voltage = sum(voltage_queues_2[pin]) / len(voltage_queues_2[pin])
        print(f"[{time.strftime('%H:%M:%S')}] Pin {pin} (ads2): raw={voltage:.2f}V, avg={avg_voltage:.2f}V")
        v_list.append(avg_voltage)
    return v_list

def read_adc(ads, pin, samples=10, delay=0.01):
    with adc_lock:
        try:
            values = []
            for _ in range(samples):
                chan = AnalogIn(ads, pin)
                values.append(chan.voltage)
                time.sleep(delay)
            avg_voltage = sum(values) / len(values)
            print(f"[{time.strftime('%H:%M:%S')}] Read ADC (pin: {pin}): {avg_voltage:.2f}V")
            return avg_voltage
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] ADC read error (pin: {pin}): {e}")
            return None

def read_id(season, ads1, ads2):
    try:
        v_list = read_v(ads1, ads2)
        id_list = []
        valid_ids = set(range(1, 13))
        for v in v_list:
            matched_id = 0
            for volt, id in id2v_dict:
                if abs(v - volt) < 0.05:
                    if id in valid_ids:
                        matched_id = id
                        print(f"[{time.strftime('%H:%M:%S')}] Voltage {v:.2f}V matched to ID {id}")
                        break
            if matched_id == 0:
                print(f"[{time.strftime('%H:%M:%S')}] Voltage {v:.2f}V matched to no ID")
            id_list.append(matched_id)
        print(f"[{time.strftime('%H:%M:%S')}] Detected IDs: {id_list}")
        
        # Map IDs to audio paths based on season, include ambient sound for rainy and winter
        audio_paths = []
        track = season_tracks.get(season, {})
        if season in ['rainy', 'winter']:
            ambient_path = track.get('ambient')
            if ambient_path:
                audio_paths.append(ambient_path)
        for plant_id in id_list:
            if plant_id in track:
                audio_paths.append(track[plant_id])
        print(f"[{time.strftime('%H:%M:%S')}] Audio paths for {season}: {audio_paths}")
        return audio_paths
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] read_id error: {e}")
        return []