import minimalmodbus
import serial
import time
from contextlib import closing
import os

DEVICE_ADDRESS = 0x01
BAUD_RATE = 9600
TIMEOUT = 1
PORT = '/dev/ttyUSB0'

def read_pzem_data():
    # Initialize the connection to the PZEM device
    instrument = minimalmodbus.Instrument(PORT, DEVICE_ADDRESS)
    instrument.serial.baudrate = 9600
    instrument.serial.bytesize = 8
    instrument.serial.parity = serial.PARITY_NONE
    instrument.serial.stopbits = 2
    instrument.serial.timeout = 1
    
    try:
        # Read measurement data
        voltage = instrument.read_register(0x0000, number_of_decimals=2, functioncode=4)
        current = instrument.read_register(0x0001, number_of_decimals=2, functioncode=4)
        power_low = instrument.read_register(0x0002, functioncode=4)
        power_high = instrument.read_register(0x0003, functioncode=4)
        power = (power_high << 16) + power_low
        energy_low = instrument.read_register(0x0004, functioncode=4)
        energy_high = instrument.read_register(0x0005, functioncode=4)
        energy = (energy_high << 16) + energy_low
        
        # Read alarm status
        high_voltage_alarm = instrument.read_register(0x0006, functioncode=4)
        low_voltage_alarm = instrument.read_register(0x0007, functioncode=4)

        print(f"Voltage: {voltage} V")
        print(f"Current: {current} A")
        print(f"Power: {power * 0.1} W")
        print(f"Energy: {energy} Wh")
        data_list = [time.strftime('%Y-%m-%d %H:%M:%S'), voltage, current, power*0.1, energy]

        # Print alarm statuses
        print(f"High Voltage Alarm: {'Alarm' if high_voltage_alarm == 0xFFFF else 'Clear'}")
        print(f"Low Voltage Alarm: {'Alarm' if low_voltage_alarm == 0xFFFF else 'Clear'}")
        print("-------------------------------------------------------------------------")
        
    except minimalmodbus.IllegalRequestError as e:
        print(f"Error: {e}")

    finally:
        time.sleep(1)
        instrument.serial.close()
        return data_list

def to_csv(header: list[str], *args) -> str:
    
    # Check if the number of columns in the header matches the number of passed lists
    if len(header) != len(args):
        raise ValueError("The number of entries in the header does not match the number of columns.")
    
    # Check that all columns (lists) have the same length
    length = len(args[0])
    for col in args:
        if len(col) != length:
            raise ValueError("All columns must have the same number of rows.")
    
    # Create CSV formatted string
    csv_data = ",".join(header) + "\n"  # Add the header row
    
    # Iterate through rows and combine the corresponding values from each column
    for i in range(length):
        row = [str(col[i]) for col in args]
        csv_data += ",".join(row) + "\n"
    
    return csv_data

def safe_write(text_data: str, outfile='output.txt', folder='./'):
    
    os.makedirs(folder, exist_ok=True)

    # Check if the outfile has a .csv extension
    _, extension = os.path.splitext(outfile)
    if extension.lower() != '.csv':
        raise ValueError(f"outfile must be a .csv file, got '{outfile}' instead.")

    filepath = os.path.join(folder, outfile)

    try:
        # Make sure not to overwrite an existing file
        if os.path.exists(filepath):
            raise RuntimeError(f"File '{filepath}' already exists.")

        with open(filepath, 'w') as f:
            f.write(text_data)
            print(f'Successfully written to {filepath}')

    except RuntimeError as e:   
        print(f"Exception occurred: {e}")

def save_results(data: list) -> None:

    header = ["Time", "Voltage", "Current", "Power", "Energy"]
    
    csv_str = to_csv(header,data)
    safe_write(csv_str, outfile="pzem_logs.csv")

if __name__ == "__main__":
    data = []
    while True:
        try:
            data.append(read_pzem_data)
            time.sleep(1)  # wait for 1 second
        except KeyboardInterrupt:
            save_results(data)
            print("Interrupted, exiting...")
            break