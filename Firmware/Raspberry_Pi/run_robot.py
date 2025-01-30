from SoftRobo import SoftRobot
import numpy as np

def main():
    # You can directly specify the I2C channels and port here
    i2c = [1]  # Example: use I2C channel 1 (you can modify this as needed)
    port = 12345  # Example: use port 12345 (you can modify this as needed)

    print('Using I2C channels: ', i2c)
    print('Using port:', port)

    # Initialize the SoftRobot object
    robot = SoftRobot(i2c=i2c, port=port)
    print(robot.nSensors, " sensor(s) initialized")

    # Wait for client connection
    robot.waitForClient()

    # Create and run all necessary processes
    robot.createProcesses()
    robot.run()

    # Wait for processes to finish
    robot.waitForProcesses()

    # Close TCP socket
    robot.socket_TCP.close()

if __name__ == "__main__":
    main()
