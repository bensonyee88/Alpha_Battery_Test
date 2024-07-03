import serial
import csv
import keyboard
import time


# Change to match the desired serial ports
try:
    leonardoSerial = serial.Serial(port = "COM8", baudrate=9600, timeout=1)
except:
    leonardoSerial = None


def read_monitors(leonardoFileName, combinedFileName, hours):

    # Create log files
    leonardoFile = open(leonardoFileName, "w", newline="")

    # # Program stop flag
    # keyPressed = False

    # Set variables to run while loop for a specifed amount of time
    duration = hours * 3600
    start_time = time.time()
    end_time = start_time + duration

    with open(combinedFileName, "w", newline="") as csvFile:
        # Create a CSV writer object
        csvWriter = csv.writer(csvFile)

        # Write the CSV rows
        csvWriter.writerow([
            "Time",
            "Current to/from Batteries (mA)",
            "Battery Voltage (TB)",
            "Temperature (Celsius)"
        ])

        timestamp = round(time.time() * 1000)
        currentBatteries = 0
        batteryVoltageTB = 0
        temperature = 0

   

        # while not keyPressed: # While 'a' not pressed
        while time.time() < end_time:

            # Flush serial lines
            leonardoSerial.reset_input_buffer()

            # Let the serial buffers fill up, characters get immediately after a reset
            i = 0
            while i < 25:
                leonardoSerial.readline()
                i = i + 1


            # Wait until start of Leonardo loop
            if (leonardoSerial is not None):
                while ("Time" not in leonardoSerial.readline().decode()):
                    pass


            # Process power data from Leonardo serial line
            if ((leonardoSerial is not None) and (leonardoSerial.inWaiting() > 0)):

                # Process lines from the Leonardo line for one loop
                leonardoLine = leonardoSerial.readline().decode()
                while ("Time" not in leonardoLine):

                    # Write the line to the Leonardo text log
                    leonardoFile.write(leonardoLine)
                    # print(leonardoLine)

                    # Parse desired values to place in CSV
                    lineSplit = leonardoLine.split(":")

                    if len(lineSplit) == 2:
                        label, value = lineSplit
                        value = value.strip()

                        if label == "Current to/from Batteries":
                            currentBatteries = value.split(" ")[0]
                            # print("Current to/from Batteries:", value.split(" ")[0])
                        elif label == "Battery Voltage":
                            batteryVoltageTB = value.split(" ")[0]
                            # print("Battery Voltage:", value.split(" ")[0])
                        elif label == "Temperature":
                            temperature = value.split(" ")[0]

                    # Read the next line
                    leonardoLine = leonardoSerial.readline().decode()

            # Write all the values to the CSV file
            csvWriter.writerow([
                timestamp,
                currentBatteries,
                batteryVoltageTB,
                temperature,
            ])

             # Sleep for a short duration to prevent excessive CPU usage
            time.sleep(1) 

            # # Shut down program if "a" key is pressed
            # if keyboard.is_pressed("a"):
            #     keyPressed = True
            #     leonardoFile.close()


def main():
    if leonardoSerial == None:
        print("No Leonardo serial line detected!")
    else:
        testName = input("Enter name of this test run: ")
        hours = float(input("Enter the number of hours to run: "))

        leonardoFileName = "logs/" + testName + "_leonardo.txt"
        combinedFileName = "logs/" + testName + "_combined.csv"

        print("Files will be saved in 'battery_test/logs' directory")
        # print("Hold 'a' to stop logging")

        read_monitors(leonardoFileName, combinedFileName, hours)

        print("Program stopped!")

if __name__ == "__main__":
    main()