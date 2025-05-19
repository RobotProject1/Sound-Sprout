import os
import wave
import numpy as np
import sounddevice as sd
import time
from threading import Thread
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# === Setup I2C and ADCs ===
i2c = busio.I2C(board.SCL, board.SDA)
ads1 = ADS1115(i2c, address=0x48)
ads2 = ADS1115(i2c, address=0x49)

# === Plant classification logic ===
pin1 = [0, 1, 2]
pin2 = [0, 1, 2]

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

# === Plant sound track mapping ===
track = {1:'sound_sprout/sound/spring/Daisy.wav',
         2:'sound_sprout/sound/spring/Sunflower.wav',
         3:'sound_sprout/sound/spring/Clover.wav', 
         4:'sound_sprout/sound/spring/Potato.wav',
         5:'sound_sprout/sound/spring/Radish.wav', 
         6:'sound_sprout/sound/spring/Carrot.wav',
         7:'sound_sprout/sound/spring/Shallot.wav', 
         8:'sound_sprout/sound/spring/Pumpkin.wav',
         9:'sound_sprout/sound/spring/Tomato.wav', 
         10:'sound_sprout/sound/spring/Corn.wav',
         11:'sound_sprout/sound/spring/Cauliflower.wav',
         12:'sound_sprout/sound/spring/Mushroom.wav'}

# === Audio mixing ===
def mix(audio_clip_paths):
    audio_arrays = []
    sample_rate = None
    num_channels = None
    if audio_clip_paths == []:
        return np.zeros((542118, 2)), 48000, 2
    for clip in audio_clip_paths:
        with wave.open(clip, 'rb') as w:
            if sample_rate is None:
                sample_rate = w.getframerate()
                num_channels = w.getnchannels()
            else:
                assert sample_rate == w.getframerate(), "All clips must have the same sample rate"
                assert num_channels == w.getnchannels(), "All clips must have the same number of channels"
            frames = w.readframes(w.getnframes())
            audio_data = np.frombuffer(frames, dtype=np.int16)
            if num_channels == 2:
                audio_data = audio_data.reshape(-1, 2)

            audio_arrays.append(audio_data)

    max_len = max(len(a) for a in audio_arrays)
    for i in range(len(audio_arrays)):
        pad_width = max_len - len(audio_arrays[i])
        if num_channels == 1:
            audio_arrays[i] = np.pad(audio_arrays[i], (0, pad_width), 'constant')
        else:
            audio_arrays[i] = np.pad(audio_arrays[i], ((0, pad_width), (0, 0)), 'constant')
    mixed_audio = np.sum(audio_arrays, axis=0)
    mixed_audio = mixed_audio.astype(np.float32)
    max_val = np.max(np.abs(mixed_audio))
    mixed_audio /= (max_val) # normalize to [-1.0, 1.0]
    return mixed_audio, sample_rate, num_channels

# === Playback callback ===
def callback(outdata, frames, time, status):
    global index, just_looped, mixed_audio
    total_frames = mixed_audio.shape[0]
    end_index = index + frames
    if end_index <= total_frames:
        chunk = mixed_audio[index:end_index]
    else:
        first_part = mixed_audio[index:]
        second_part = mixed_audio[:end_index - total_frames]
        chunk = np.vstack((first_part, second_part))
    outdata[:] = chunk
    index = (index + frames) % total_frames

# === Thread to monitor path list file changes ===
class checkfile(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.last_mtime = 0
    def run(self):
        global mixed_audio, sample_rate, num_channels
        while True:
            try:
                mtime = os.path.getmtime('sound_sprout/path_list.txt')
                if mtime == self.last_mtime:
                    pass
                else:
                    with open('sound_sprout/path_list.txt', 'r') as file:
                        path_list = file.read()
                        path_list = path_list.split(',')
                    print(path_list)
                    audio_clip_paths = [i.strip() for i in path_list if i.strip()]
                    mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
                    print(mixed_audio.shape, sample_rate, num_channels)
                    self.last_mtime = mtime
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(1)

# === Volume control thread ===
class volume(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            vol = AnalogIn(ads2, 3)
            voltage = vol.voltage
            voltage = min(max(voltage, 0), 5.0)  
            volume_percent = int((voltage / 5.0) * 100)
            os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {volume_percent}%")

# === Plant detection and writing path list ===
class readnwrite(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        plant_id_old = []
        plant_id_new = []
        while True:
            plant_id_new = read_id(read_v())
            if plant_id_new == plant_id_old:
                pass
            else:
                path_list = ""
                with open('sound_sprout/path_list.txt', 'w') as file:
                    for i in plant_id_new:
                        if i == 0:
                            pass
                        else:
                            path_list += ','+track[i]
                    file.write(path_list.lstrip(','))
            plant_id_old = plant_id_new.copy()

def start():
    mtime = os.path.getmtime('sound_sprout/path_list.txt')
    last_mtime = 0
    stream = None
    with open('sound_sprout/path_list.txt', 'r') as file:
        path_list = file.read().strip()
        path_list = [p.strip() for p in path_list.split(',') if p.strip()]
    print(path_list)
    audio_clip_paths = [i.strip() for i in path_list if i.strip()]
    mixed_audio, sample_rate, num_channels = mix(audio_clip_paths)
    index = 0
    stream = sd.OutputStream(samplerate=sample_rate, channels=num_channels, callback=callback, blocksize=8192)
    stream.start()

    checkfile_thread = checkfile()
    adjust_volume_thread = volume()
    plant_thread = readnwrite()

    checkfile_thread.start()
    adjust_volume_thread.start()
    plant_thread.start()

    print("Playsound + classification system running.")

# === Main logic ===
if __name__ == "__main__": 
    start()