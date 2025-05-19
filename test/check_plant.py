import time
from plant_classification import read_id, read_v

def main():
    print("Checking plant IDs...")
    while True:
        voltage_list = read_v()
        id_list = read_id(voltage_list)
        print("Plant IDs:", id_list)
        time.sleep(1)  # Adjust if you want faster or slower updates

if __name__ == "__main__":
    main()