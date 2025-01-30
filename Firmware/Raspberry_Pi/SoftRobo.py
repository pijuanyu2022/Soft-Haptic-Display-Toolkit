import multiprocessing
import socket
import struct
import time
from ctypes import c_bool
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_mcp4725
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode
import serial
from multiprocessing import Manager
import RPi.GPIO as GPIO

class baseSensor:
    def __init__(self, sensorInstance):
        self.instance = sensorInstance

    def readSensor(self):
        # Placeholder method to be implemented in subclasses
        raise NotImplementedError("readSensor must be implemented in the child class")

class VeabSensor(baseSensor):
    def __init__(self, i2c, addr=(0x48), RATE=490):
        ads = ADS.ADS1015(I2C(i2c), address=addr)
        ads.mode = Mode.CONTINUOUS
        ads.data_rate = RATE
        ads.gain = 2
        chan = AnalogIn(ads, ADS.P0)
        super().__init__(chan)
        self._adjusted_voltage = 0.0  # Custom attribute for adjusted voltage

    def readSensor(self):
        # Read sensor value and convert it to voltage
        return self.instance.voltage * 5

    def setAdjustedVoltage(self, value):
        # Custom setter for adjusted voltage
        self._adjusted_voltage = value

    def getAdjustedVoltage(self):
        # Custom getter for adjusted voltage
        return self._adjusted_voltage


class VEABcontrolboard:
    def __init__(self, i2c):
        # Initialize two sensors and two actuators (DACs) on the same I2C bus
        self.sensors = [VeabSensor(i2c, addr=0x48)]
        self.actuators = [
            adafruit_mcp4725.MCP4725(I2C(i2c), address=0x60)
        ]

class SoftRobot:
    def __init__(self, i2c=[1], sensorFreq=250, actuatorFreq=250, port=8888, arduino_port="/dev/ttyACM0"):
        self.stopFlag = multiprocessing.Value(c_bool, False)  # Shared flag to stop processes

        self.nSensors = 0  # Initialize the number of sensors
        self.port = port  # Port for TCP communication
        self.channels = i2c  # I2C channels for the control boards
        self.sensor_frequency = sensorFreq  # Frequency for reading sensors
        self.sensor_period = 1.0 / sensorFreq  # Time period between sensor reads
        self.actuator_frequency = actuatorFreq  # Frequency for controlling actuators
        self.actuator_period = 1.0 / actuatorFreq  # Time period for actuator control
        
        # Initialize VEAB control boards (each with sensors and actuators)
        self.boards = [VEABcontrolboard(chan) for chan in self.channels]
        
        # Aggregate all sensors and actuators from the boards
        self.actuators = [actuator for board in self.boards for actuator in board.actuators]
        self.nActuators = len(self.actuators)  # Count total number of actuators
        self.actuatorsValues = multiprocessing.Array('d', [0.5] * self.nActuators)  # Initialize actuators to a default value
        
        # Set up TCP server for communication
        self.buffersize = 8 * self.nActuators  # Buffer size based on number of actuators
        self.socket_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_TCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = ('', self.port)  # Bind to the provided port
        self.socket_TCP.bind(server_address)
        self.clients = []  # List of connected clients
        self.clients_addresses = []  # List of client addresses

        # Arduino Communication
        self.arduino_port = arduino_port
        self.arduino_baud = 115200
        self.arduino_queue = multiprocessing.Queue()  # Queue for Arduino sensor data
        self.processes = []

        # Shared dictionary for latest data
        self.manager = Manager()
        self.latest_data = self.manager.dict({
            "timestamp": 0.0,
            "veab_sensor": 0.0,
            "mpr_sensors": [0.0] * 8
        })


        # GPIO setup with digitalio
        self.solenoid_pins = [17, 27, 22, 23]  # GPIO 17, 27, 22, 23
        
        GPIO.setmode(GPIO.BCM)
        for pin in self.solenoid_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)




    def waitForClient(self):
        """Wait for a client to connect to the TCP server."""
        self.socket_TCP.listen(1)
        print("TCP server is running. Waiting for client...")
        client, client_address = self.socket_TCP.accept()  # Accept the client connection
        print("Client ", client_address, " connected. Comm's ready!")
        client.settimeout(0.5)
        self.clients.append(client)
        self.clients_addresses.append(client_address)


    def receive(self):
        """Receive actuator values from clients via TCP and handle open-loop control."""
        while not self.stopFlag.value:
            try:
                # Receive 1 byte to check the data type
                data_type = self.clients[0].recv(1)

                if data_type == b'C':  # It's a command
                    try:
                        binary_string = self.clients[0].recv(16).decode('utf-8').strip()
                        print(f"Received binary string: {binary_string}")

                        # Ensure the binary string is valid
                        if len(binary_string) != 16 or not all(c in '01' for c in binary_string):
                            print(f"Invalid binary string received: {binary_string}")
                            continue

                        # Split the binary string
                        arduino_binary = binary_string[:12]  # First 12 bits for Arduino
                        gpio_binary = binary_string[12:]     # Last 4 bits for Pi GPIO

                        # Send the first 12 bits to the Arduino
                        self.send_to_arduino(arduino_binary)

                        # Update GPIO states for the last 4 bits
                        for i, state in enumerate(gpio_binary):
                            pin_state = GPIO.HIGH if state == '1' else GPIO.LOW
                            GPIO.output(self.solenoid_pins[i], pin_state)
                            print(f"Set GPIO pin {self.solenoid_pins[i]} to {'HIGH' if state == '1' else 'LOW'}")

                    except UnicodeDecodeError as e:
                        print(f"Decoding error: {e}")
                        continue
                
                elif data_type == b'W':  # It's an actuator (wave) value
                    raw = self.clients[0].recv(self.buffersize)  # Receive the actuator data
                    unpackedData = struct.unpack('d' * int(self.buffersize / 8), raw)
                    # Store the received actuator values
                    for i in range(int(self.buffersize / 8)):
                        self.actuatorsValues[i] = unpackedData[i]

            except socket.timeout:
                continue
            except Exception as e:
                print('Error in receive:', e)
                self.stopFlag.value = True  # Stop on failure

        self.socket_TCP.close()



    def send_to_arduino(self, binary_string):
        """Send a 12-bit binary string to the Arduino."""
        try:
            if not hasattr(self, 'ser') or self.ser is None or not self.ser.is_open:
                self.ser = serial.Serial(self.arduino_port, self.arduino_baud, timeout=1)
                time.sleep(2)  # Allow time for the Arduino to reset after reconnecting

            # Send the binary string directly
            self.ser.write(f"{binary_string}\n".encode('utf-8'))
            print(f"Sent to Arduino: {binary_string}")

        except (serial.SerialException, serial.SerialTimeoutException) as e:
            print(f"[ERROR] Arduino communication error: {e}")
            self.ser = None  # Close the connection to trigger a reconnect next time




    def controlActuators(self):
        """Control actuators periodically based on the received values."""
        while not self.stopFlag.value:
            try:
                # Update the actuators with the current actuator values
                for i, p in enumerate(range(self.nActuators)):
                    self.actuators[p].normalized_value = max(0, min(1, self.actuatorsValues[i]))
                time.sleep(self.actuator_period - time.time() * self.actuator_frequency % 1 / self.actuator_frequency)
            except Exception as e:
                print('Error in control Actuators:', e)
                self.stopFlag.value = True  # Stop on failure
        self.resetActuators()  # Reset actuators to default when stopping

    def resetActuators(self):
        """Reset all actuators to a default value."""
        for i in range(self.nActuators):
            self.actuators[i].normalized_value = 0.5
            
    # ------------------------- sensors -------------------------------------------
    def read_arduino(self):
        """Read data from Arduino and update the latest_data dictionary, with reconnection logic."""
        while not self.stopFlag.value:
            try:
                if not hasattr(self, 'ser') or self.ser is None or not self.ser.is_open:
                    print(f"[INFO] Attempting to reconnect to Arduino on {self.arduino_port}")
                    self.ser = serial.Serial(self.arduino_port, self.arduino_baud, timeout=1)
                    time.sleep(2)  # Allow time for the Arduino to reset
                    print(f"[INFO] Reconnected to Arduino on {self.arduino_port}")

                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode('utf-8').strip()
                    if "Calibration complete" in data:
                        print("[INFO] Arduino calibration complete.")
                    elif data.count(',') == 9:  # Expecting 10 values: timestamp + VEAB + 8 sensor readings
                        sensor_data = data.split(",")
                        if len(sensor_data) == 10:
                            try:
                                # Parse sensor data
                                timestamp = float(sensor_data[0]) * 0.001  # Convert ms to seconds
                                veab_sensor = float(sensor_data[1])
                                mpr1 = float(sensor_data[2])
                                mpr2 = float(sensor_data[3])
                                mpr3 = float(sensor_data[4])
                                mpr4 = float(sensor_data[5])
                                mpr5 = float(sensor_data[6])
                                mpr6 = float(sensor_data[7])
                                mpr7 = float(sensor_data[8])
                                mpr8 = float(sensor_data[9])

                                # Update the shared dictionary
                                self.latest_data["timestamp"] = timestamp
                                self.latest_data["veab_sensor"] = veab_sensor
                                self.latest_data["mpr_sensors"] = [mpr1, mpr2, mpr3, mpr4, mpr5, mpr6, mpr7, mpr8]

                            except ValueError:
                                print("[ERROR] Failed to parse Arduino data:", data)

            except (serial.SerialException, serial.SerialTimeoutException) as e:
                print(f"[ERROR] Arduino communication error: {e}")
                self.ser = None  # Reset the connection to trigger a reconnect next time

            except Exception as e:
                print(f"[ERROR] Unexpected error in read_arduino: {e}")
                self.ser = None  # Reset the connection to trigger a reconnect


    def update_veab_sensor(self):
        """Update VEAB sensor values from the Arduino data."""
        while not self.stopFlag.value:
            try:
                if not self.arduino_queue.empty():
                    data = self.arduino_queue.get()
                    _, veab_sensor, *_ = data  # Now expecting 8 sensor values
                    # Update the VEAB sensor adjusted voltage
                    for board in self.boards:
                        board.sensors[0].setAdjustedVoltage(veab_sensor / 5)
            except Exception as e:
                print("[ERROR] Updating VEAB sensor failed:", e)


    def send(self):
        """Send the latest sensor data to the PC in a formatted text string with relative time starting at 0."""
        start_time = time.time()  # Record the start time

        while not self.stopFlag.value:
            try:
                if self.clients:  # Ensure there is at least one connected client
                    # Calculate relative time
                    relative_time = time.time() - start_time

                    # Get the latest data from the shared dictionary
                    veab_sensor = self.latest_data["veab_sensor"]
                    mpr_sensors = self.latest_data["mpr_sensors"]

                    # Format the data as a single string
                    formatted_data = (
                        f"Time: {relative_time:.3f}s, VEAB: {veab_sensor:.2f}, "
                        f"MPR1: {mpr_sensors[0]:.2f}, MPR2: {mpr_sensors[1]:.2f}, "
                        f"MPR3: {mpr_sensors[2]:.2f}, MPR4: {mpr_sensors[3]:.2f}, "
                        f"MPR5: {mpr_sensors[4]:.2f}, MPR6: {mpr_sensors[5]:.2f}, "
                        f"MPR7: {mpr_sensors[6]:.2f}, MPR8: {mpr_sensors[7]:.2f}\n"
                    )
                    # print(f"[send to PC] {formatted_data.strip()}")  # Print the formatted data for debugging

                    # Send the formatted string to the first client
                    self.clients[0].sendall(formatted_data.encode('utf-8'))

                    # Delay to match the desired frequency (e.g., 250 Hz)
                    time.sleep(self.sensor_period)
            except BrokenPipeError:
                print("[ERROR] Client disconnected. Stopping send function.")
                self.stopFlag.value = True
            except Exception as e:
                print(f"[ERROR] Error in send function: {e}")
                self.stopFlag.value = True



    def createProcesses(self):
        """Create multiprocessing processes for Arduino communication and actuator control."""
        # Create process for reading Arduino data
        self.processes.append(multiprocessing.Process(target=self.read_arduino))
        # Create process for updating VEAB sensor values
        self.processes.append(multiprocessing.Process(target=self.update_veab_sensor))
        # Create actuator control process
        self.processes.append(multiprocessing.Process(target=self.controlActuators))
        # Create communication processes for sending and receiving data
        self.processes.append(multiprocessing.Process(target=self.receive))
        # Create process for sending data to PC
        self.processes.append(multiprocessing.Process(target=self.send))


    def run(self):
        """Start all created processes and print sensor values for debugging."""
        for p in self.processes:
            p.start()


    def waitForProcesses(self):
        """Wait for all processes to complete."""
        for p in self.processes:

            p.join()