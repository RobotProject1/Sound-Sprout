import Jetson.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import ADS1x15

# initialize ADS1115 on I2C bus 1 with default address 0x48
ADS = ADS1x15.ADS1115(1, 0x48)
#daisy sunflower clover potato radish carrot garlic pumpkin tomato corn cauliflower mushroom
id2v_dict = [(5.00,0), (4.78, 1), (4.35, 2), (3.98, 3), (3.64, 4), (3.33, 5), (3.03, 6), (2.67, 7), (2.38, 8), (2.13, 9), (1.79, 10), (1.56, 11), (1.09, 12)]
pin = [1,2,3,4,5,6]

def read_v():
    return [ADS.readADC(i) for i in pin]

def read_id(v_list):
    id_list = []
    for v in v_list:
        matched_id = 0
        for volt, id in id2v_dict:
            if v > volt - 0.2 and v < volt + 0.2: 
                matched_id = id
                break
        id_list.append(matched_id)
    return id_list