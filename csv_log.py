import minimalmodbus
import serial
import time
from contextlib import closing
import os

DEVICE_ADDRESS = 0x01
BAUD_RATE = 9600
TIMEOUT = 1
PORT = '/dev/ttyUSB0'

def read_pzem_data() -> list[float]:
    # Initialize the connection to the PZEM device
    instrument = minimalmodbus.Instrument(PORT, DEVICE_ADDRESS)
    instrument.serial.baudrate = 9600
    instrument.serial.bytesize = 8
    instrument.serial.parity = serial.PARITY_NONE
    instrument.serial.stopbits = 2
    instrument.serial.timeout = 1
    
    
    try:
        # Read measurement data
        voltage = float(instrument.read_register(0x0000, number_of_decimals=2, functioncode=4))
        current = float(instrument.read_register(0x0001, number_of_decimals=2, functioncode=4))
        power_low = instrument.read_register(0x0002, functioncode=4)
        power_high = instrument.read_register(0x0003, functioncode=4)
        power = float((power_high << 16) + power_low)
        energy_low = instrument.read_register(0x0004, functioncode=4)
        energy_high = instrument.read_register(0x0005, functioncode=4)
        energy = float((energy_high << 16) + energy_low)
        
        # Read alarm status
        high_voltage_alarm = instrument.read_register(0x0006, functioncode=4)
        low_voltage_alarm = instrument.read_register(0x0007, functioncode=4)

        # print(f"Voltage: {voltage} V")
        # print(f"Current: {current} A")
        # print(f"Power: {power * 0.1} W")
        # print(f"Energy: {energy} Wh")
        
        # Print alarm statuses
        # print(f"High Voltage Alarm: {'Alarm' if high_voltage_alarm == 0xFFFF else 'Clear'}")
        # print(f"Low Voltage Alarm: {'Alarm' if low_voltage_alarm == 0xFFFF else 'Clear'}")
        # print("-------------------------------------------------------------------------")

        # Write data into list:
        row_values = [voltage, current, power*0.1, energy]
        row_time = time.strftime('%Y-%m-%d %H:%M:%S')
        row_data = [row_time] + row_values  
      
        # Print alarm statuses
        # print(f"High Voltage Alarm: {'Alarm' if high_voltage_alarm == 0xFFFF else 'Clear'}")
        # print(f"Low Voltage Alarm: {'Alarm' if low_voltage_alarm == 0xFFFF else 'Clear'}")
        # print("-------------------------------------------------------------------------")
            
    except minimalmodbus.IllegalRequestError as e:
        print(f"Error: {e}")

    finally:
        # time.sleep(1)
        instrument.serial.close()
        return row_data


def to_csv(header: list[str], data: list[list[float]]) -> str:
    
    # Create CSV formatted string
    csv_data = ",".join(header) + "\n"  # Add the header row
    
    # Iterate through rows
    length = len(data)
    for i in range(length):
        row = ",".join([str(x) for x in data[i]]) + "\n"
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
            # print(f"row_new = {row_new}")
            data.append(row_new)
            time.sleep(1)  # wait for 1 second
        except KeyboardInterrupt:
            save_results(data)
            print("Interrupted, exiting...")
            break