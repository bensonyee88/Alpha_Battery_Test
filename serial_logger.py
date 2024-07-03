import serial
import csv
import time
import os

# Change to match the desired serial port
serial_port = "/dev/cu.usbserial-FTB6SPL3"  # Update this to your actual port

# Ensure the serial connection is established
try:
    leonardoSerial = serial.Serial(port=serial_port, baudrate=115200, timeout=1)
except serial.SerialException:
    leonardoSerial = None
    print(f"Could not open serial port {serial_port}")

def read_monitors(combinedFileName, hours):

    # Set variables to run while loop for a specified amount of time
    duration = hours * 3600
    start_time = time.time()
    end_time = start_time + duration

    with open(combinedFileName, "w", newline="") as csvFile:
        # Create a CSV writer object
        csvWriter = csv.writer(csvFile)

        # Write the CSV header
        csvWriter.writerow([
            "Timestamp",
            "Temperature (C)",
            "Bus Voltage (V)",
            "Current (mA)"
        ])

        temperature = busvoltage = current = None

        while time.time() < end_time:

            if leonardoSerial is not None and leonardoSerial.inWaiting() > 0:
                # Read a line from the serial port
                leonardoLine = leonardoSerial.readline().decode().strip()

                # Get the current timestamp
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                # Parse desired values to place in CSV
                if "Temperature:" in leonardoLine:
                    temperature = leonardoLine.split(":")[1].strip().split(" ")[0]
                elif "Bus Voltage:" in leonardoLine:
                    busvoltage = leonardoLine.split(":")[1].strip().split(" ")[0]
                elif "Current:" in leonardoLine:
                    current = leonardoLine.split(":")[1].strip().split(" ")[0]

                # Write all the values to the CSV file if all have been read
                if temperature is not None and busvoltage is not None and current is not None:
                    csvWriter.writerow([
                        timestamp,
                        temperature,
                        busvoltage,
                        current,
                    ])

                    # Print the line for debugging
                    # print(f"{timestamp}, {temperature}, {busvoltage}, {current}")

                    # Reset the values
                    temperature = busvoltage = current = None

            # Sleep for a short duration to prevent excessive CPU usage
            time.sleep(1)

def main():
    if leonardoSerial is None:
        print(f"No Leonardo serial line detected on {serial_port}!")
    else:
        testName = input("Enter name of this test run: ")
        hours = float(input("Enter the number of hours to run: "))

        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        combinedFileName = os.path.join(logs_dir, f"{testName}_combined.csv")

        print(f"Files will be saved in the '{logs_dir}' directory")

        read_monitors(combinedFileName, hours)

        print("Program stopped!")

if __name__ == "__main__":
    main()
