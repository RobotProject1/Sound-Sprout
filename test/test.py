import Jetson.GPIO as GPIO
import time
import ADS1x15

#test ADS1x15
def test_ads1x15():
    ADS1 = ADS1x15.ADS1115(1, 0x48)
    f = ADS1.toVoltage()
    print("ADS1 Voltage pin 1 : ", ADS1.readADC(1)*f)

if __name__ == "__main__":
    input = int(input("what do you want to test? 1:ADS1x15 2:season button 3:lighting 4:read id 5:read voltage"))
    if input == 1:
        pin = int(input("which pin do you want to test? 1:pin1 2:pin2 3:pin3"))
        if pin == 1:
            pin = 1
        elif pin == 2:
            pin = 2
        elif pin == 3:
            pin = 3
        else:
            print("Invalid pin number")
    elif input == 2:
        season = int(input("which season do you want to test? 1:winter 2:rainy 3:spring"))
        if season == 1:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while True:
                if GPIO.input(4) == GPIO.LOW:
                    print("Winter")
                    break
                time.sleep(0.1)
        elif season == 2:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while True:
                if GPIO.input(4) == GPIO.LOW:
                    print("Rainy")
                    break
                time.sleep(0.1)    

        elif season == 3:   
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            while True:
                if GPIO.input(4) == GPIO.LOW:
                    print("Spring")
                    break
                time.sleep(0.1)
        else:
            print("Invalid season number")
    elif input == 3:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        while True:
            if GPIO.input(4) == GPIO.LOW:
                print("Lighting")
                break
            time.sleep(0.1)