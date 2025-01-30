import time
from multiprocessing import Process, Queue
from GUI import launchGUI as gui_run
from collections import deque
from dataclasses import dataclass
from threading import Thread
import socket
from threading import Event
import struct
import cv2
import queue


def play_video(running):
    """Play 'video_1.mp4' using OpenCV."""
    cap = cv2.VideoCapture('video_1.mp4')

    if not cap.isOpened():
        print("Error: Cannot open video file")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_period = 1.0 / fps
    start_time = time.time()

    try:
        while running.is_set():
            ret, frame = cap.read()
            if not ret:
                print("End of video reached.")
                break

            cv2.imshow('Imported Wave Video', frame)

            # Ensure correct frame rate timing
            elapsed_time = time.time() - start_time
            delay = max(0, frame_period - elapsed_time) 

            start_time = time.time()
    finally:
        cap.release()
        cv2.destroyAllWindows()


@dataclass
class MainExperiment:
    # Experimental state and control
    experiment_mode: str = "DEFAULT"
    task: str = "DEFAULT"
    dp1: str = "DEFAULT"


def receive_sensor_data_from_pi(client_socket, gui_sensor_queue, running):
    """Receive sensor data from the Raspberry Pi via a socket and send complete lines to the GUI."""
    buffer = ""
    try:
        while running.is_set():
            try:
                received_data = client_socket.recv(1024).decode('utf-8')
                if not received_data:
                    continue

                buffer += received_data

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    try:
                        parsed_data = line.split(", ")
                        time_value = float(parsed_data[0].split(":")[1].strip()[:-1])
                        veab = float(parsed_data[1].split(":")[1].strip())
                        mpr1 = float(parsed_data[2].split(":")[1].strip())
                        mpr2 = float(parsed_data[3].split(":")[1].strip())
                        mpr3 = float(parsed_data[4].split(":")[1].strip())
                        mpr4 = float(parsed_data[5].split(":")[1].strip())
                        mpr5 = float(parsed_data[6].split(":")[1].strip())
                        mpr6 = float(parsed_data[7].split(":")[1].strip())
                        mpr7 = float(parsed_data[8].split(":")[1].strip())
                        mpr8 = float(parsed_data[9].split(":")[1].strip())

                        # Add all 8 sensors to the GUI queue
                        gui_sensor_queue.put((time_value, veab, mpr1, mpr2, mpr3, mpr4, mpr5, mpr6, mpr7, mpr8))
                    except Exception as parse_error:
                        print(f"[Pi Loop] Error parsing data: {parse_error}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Pi Loop] Error in receiving data: {e}")
                running.clear()
    finally:
        client_socket.close()
        print("[Pi Loop] Socket closed.")


def main():
    # Queues for GUI communication
    gui_queue = Queue()
    gui_out_queue = Queue()
    gui_regulator_queue = Queue()
    gui_actuator_queue = Queue()
    gui_sensor_queue = Queue()

    # Start the GUI in a separate process
    gui_p = Process(target=gui_run, args=(gui_queue, gui_out_queue, gui_regulator_queue, gui_actuator_queue, gui_sensor_queue))
    gui_p.start()

    experiment = MainExperiment()
    running = Event()
    running.set()

    client_socket = None
    sensor_thread = None

    def send_regulator_data():
        """Continuously send regulator data from the regulator queue."""
        while running.is_set():
            try:
                wave_value = 0.5 + gui_regulator_queue.get(timeout=0.01) * 0.15
                if client_socket:
                    packed_wave_value = struct.pack('d', wave_value)
                    client_socket.sendall(b'W' + packed_wave_value + b'\n')
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Error sending regulator data: {e}")

    # Start a thread for sending regulator data
    regulator_thread = Thread(target=send_regulator_data, daemon=True)
    regulator_thread.start()

    try:
        while running.is_set():
            # Handle actuator commands
            try:
                gui_actuator_value = gui_actuator_queue.get(timeout=0.05)
                if client_socket:
                    if isinstance(gui_actuator_value, tuple) and gui_actuator_value[0] == "Valve":
                        binary_string = gui_actuator_value[1]
                        if binary_string:
                            gui_queue.put(("Status", f"Sending binary state: {binary_string}"))
                            print(f"Sending binary state: {binary_string}")
                            client_socket.sendall(b'C' + binary_string.encode('utf-8') + b'\n')
            except queue.Empty:
                pass

            # Handle messages from the GUI
            try:
                header, gui_data = gui_out_queue.get(timeout=0.1)
                if header == "Connect":
                    raspberry_pi_ip = gui_data
                    try:
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client_socket.settimeout(2.0)
                        client_socket.connect((raspberry_pi_ip, 12345))
                        client_socket.sendall(b'CKEEP_ALIVE')
                        gui_queue.put(("Status", f"Connected to Raspberry Pi at {raspberry_pi_ip}:12345"))
                        sensor_thread = Thread(target=receive_sensor_data_from_pi, args=(client_socket, gui_sensor_queue, running), daemon=True)
                        sensor_thread.start()
                    except Exception as e:
                        gui_queue.put(("Status", f"Failed to connect: {e}"))
                elif header == "Close":
                    running.clear()
                    break
                elif header == "Play Pattern" and gui_data == "Import Wave":
                    video_thread = Thread(target=play_video, args=(running,), daemon=True)
                    video_thread.start()
            except queue.Empty:
                pass
    finally:
        running.clear()
        if client_socket:
            client_socket.close()
        if sensor_thread and sensor_thread.is_alive():
            sensor_thread.join()
        gui_p.terminate()


if __name__ == "__main__":
    main()
