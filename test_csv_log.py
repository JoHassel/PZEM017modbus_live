# import minimalmodbus
# import serial
import time
# from contextlib import closing
import os
import random

DEVICE_ADDRESS = 0x01
BAUD_RATE = 9600
TIMEOUT = 1
PORT = '/dev/ttyUSB0'

def read_pzem_data() -> list[float]:
#     # Initialize the connection to the PZEM device
#     
    try:
#         # Read measurement data
        
#         # Read alarm status

#         row_data= list[time.strftime('%Y-%m-%d %H:%M:%S'), voltage, current, power*0.1, energy]
        row_time = time.strftime('%Y-%m-%d %H:%M:%S')
        random_values = [round(random.random(),3) for _ in range(4)]
        row_data = [row_time] + random_values  
#       # Print alarm statuses
        
#     except minimalmodbus.IllegalRequestError as e:
#         print(f"Error: {e}")

    finally:
        time.sleep(1)
#         instrument.serial.close()
        return row_data

def to_csv(header: list[str], data: list[list[float]]) -> str:
    
    # Create CSV formatted string
    csv_data = ",".join(header) + "\n"  # Add the header row
    
    # Iterate through rows
    length = len(data)
    for i in range(length):
        row = ",".join([str(x) for x in data[i]]) + "\n"
        # print(f"Row({i}) = {row}")
        csv_data += row
    
    return csv_data

def safe_write(text_data: str, outfile='logs.csv', folder='./'):
    
    os.makedirs(folder, exist_ok=True)

    # Check if the outfile has a .csv extension
    file_name, extension = os.path.splitext(outfile)
    if extension.lower() != '.csv':
        raise ValueError(f"outfile must be a .csv file, got '{outfile}' instead.")

    filepath = os.path.join(folder, outfile)

    try:
        # Make sure not to overwrite an existing file
        n = 1
        while os.path.exists(filepath):
            outfile = f"{file_name}_{n}.csv"
            n+=1
            filepath = os.path.join(folder, outfile)
            # raise RuntimeError(f"File '{filepath}' already exists.")

        with open(filepath, 'w') as f:
            f.write(text_data)
            print(f'Successfully written to {filepath}')

    except RuntimeError as e:   
        print(f"Exception occurred: {e}")

def save_results(data: list[list[float]]) -> None:

    header = ["Time", "Voltage", "Current", "Power", "Energy"]
    
    csv_str = to_csv(header,data)
    safe_write(csv_str, outfile="pzem_logs.csv")

if __name__ == "__main__":
    data = []
    while True:
        try:
            row_new = read_pzem_data()
            print(f"row_new = {row_new}")
            data.append(row_new)
            time.sleep(1)  # wait for 1 second
        except KeyboardInterrupt:
            save_results(data)
            print("Interrupted, exiting...")
            break