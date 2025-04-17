from main import run_script, kill_python_scripts_by_name
# import Jetson.GPIO as GPIO
try: 
    import Jetson.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    class MockGPIO:
        BCM = BOARD = IN = OUT = HIGH = LOW = None
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, state): pass
        def input(self, pin): return False
        def cleanup(self): pass
        def wait_for_edge(self, pin, edge_type):
            print(f"Simulating waiting for {edge_type} edge on pin {pin}")
            return True
    GPIO = MockGPIO()


GPIO.setmode(GPIO.BCM)
rainy_pin = 18
spring_pin = 23
winter_pin = 24

GPIO.setup(rainy_pin, GPIO.IN)  # button pin set as input
GPIO.setup(spring_pin, GPIO.IN)  # button pin set as input  
GPIO.setup(winter_pin, GPIO.IN)  # button pin set as input

ss_old = ''
ss_new = 'spring'

while True:
    while len(ss_new) == 0:
        if GPIO.input(rainy_pin) == GPIO.HIGH:
            ss_new = 'rainy'
            print("Rainy season selected.")
            break
        elif GPIO.input(spring_pin) == GPIO.HIGH:
            ss_new = 'spring'
            print("spring season selected.")
            break
        elif GPIO.input(winter_pin) == GPIO.HIGH:
            ss_new = 'winter'
            print("Winter season selected.")
            break
    
    if ss_new == ss_old:
        pass
    else:
        ss_old = ss_new
        kill_python_scripts_by_name(['spring_sound.py', 'rainy_sound.py','winter_sound.py'])
        if ss_new == 'rainy':
            run_script('rainy_sound.py')
        elif ss_new == 'spring':
            run_script('spring_sound.py')
        elif ss_new == 'winter':
            run_script('winter_sound.py')
        ss_new = ''