import serial
import csv
import time
import os

# Change to match the desired serial ports
try:
     leonardoSerial = serial.Serial(port="/dev/cu.usbserial-FTB6SPL3", baudrate=115200, timeout=1)
except:
    leonardoSerial = None

def read_monitors(leonardoFileName, combinedFileName, hours):
    # Create log files
    leonardoFile = open(leonardoFileName, "w", newline="")

    # Set variables to run while loop for a specified amount of time
    duration = hours * 3600
    start_time = time.time()
    end_time = start_time + duration

    with open(combinedFileName, "w", newline="") as csvFile:
        # Create a CSV writer object
        csvWriter = csv.writer(csvFile)
        # Write the CSV header
        csvWriter.writerow(["Time", "Current (mA)", "Bus Voltage (V)", "Temperature (C)"])

        while time.time() < end_time:
            # Flush serial lines
            if leonardoSerial is not None:
                leonardoSerial.reset_input_buffer()

                # Let the serial buffers fill up, characters get immediately after a reset
                for _ in range(25):
                    leonardoSerial.readline()

                # Wait until start of Leonardo loop
                while "Time" not in leonardoSerial.readline().decode():
                    pass

                # Process power data from Leonardo serial line
                while (leonardoSerial.in_waiting > 0):
                    # Process lines from the Leonardo line for one loop
                    leonardoLine = leonardoSerial.readline().decode()
                    while "Time" not in leonardoLine:
                        # Write the line to the Leonardo text log
                        leonardoFile.write(leonardoLine)
                        # Parse desired values to place in CSV
                        lineSplit = leonardoLine.split(":")
                        if len(lineSplit) == 2:
                            label, value = lineSplit
                            value = value.strip()
                            if label == "Current":
                                current = value.split(" ")[0]
                            elif label == "Bus Voltage":
                                voltage = value.split(" ")[0]
                            elif label == "Temperature":
                                temperature = value.split(" ")[0]

                        # Read the next line
                        leonardoLine = leonardoSerial.readline().decode()

                    # Write all the values to the CSV file
                    timestamp = round(time.time() * 1000)
                    csvWriter.writerow([timestamp, current, voltage, temperature])

                # Sleep for a short duration to prevent excessive CPU usage
                time.sleep(1)

def main():
    if leonardoSerial is None:
        print("No Leonardo serial line detected!")
    else:
        testName = input("Enter name of this test run: ")
        hours = float(input("Enter the number of hours to run: "))

        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        leonardoFileName = os.path.join(logs_dir, f"{testName}_leonardo.txt")
        combinedFileName = os.path.join(logs_dir, f"{testName}_combined.csv")

        print("Files will be saved in 'logs' directory")
        read_monitors(leonardoFileName, combinedFileName, hours)
        print("Program stopped!")

if __name__ == "__main__":
    main()
