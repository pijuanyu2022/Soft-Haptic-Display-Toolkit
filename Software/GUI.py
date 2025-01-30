
import tkinter
import tkinter.messagebox
import customtkinter
from customtkinter import CTkInputDialog  
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import numpy as np
import time
import csv
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d
import threading
import os
from PIL import Image, ImageTk  # For loading and displaying images
from tactile_array import TactileArrayController

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue")


class GUI(customtkinter.CTk):
    def __init__(self, conn, in_conn=None, regulator_conn=None, actuator_conn=None, sensor_conn=None):
        super().__init__()

        # use the protocol method to catch the window's close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # queues for multiprocessing
        self.data_queue = conn
        self.in_queue = in_conn
        self.actuator_queue = actuator_conn
        self.sensor_queue = sensor_conn
        self.regulator_queue = regulator_conn
        self.tactile_controller = TactileArrayController(self.actuator_queue)

        # Define global variables
        self.desired_pressure_value = None
        self.stop_flag = False
        self.default_font = customtkinter.CTkFont(size=14)  # Adjust the size here
        self.valve_states = [0] * 16  # Initial state: all valves OFF
        self.b_string = '0' * 16


        # configure window
        self.title("Pneumatic Haptic Display.py")
        self.geometry(f"{1400}x{900}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.create_sidebar()

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Enter", font=self.default_font)
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", text="OK", command=self.command, border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=200, height=150, font=self.default_font)
        self.textbox.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.pattern_frame()
        self.manual_frame()
        self.plot_frame()  # For original plot
        self.effect_frame()
        self.channels_frame()
        self.sensors_frame()  # For sensor plot

        # set default values
        self.pattern_button_stop.configure(state="disabled")

        # Start checking for messages after 100ms
        self.after(100, self.check_for_messages)

    ################# Original Plot Frame ####################
    def plot_frame(self):
        ############### plot frame ##############################
        self.plot_frame = customtkinter.CTkFrame(self, width=250, height=250)
        self.plot_frame.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Initialize plot data (for original plot)
        self.original_time_data = []  # Changed from self.time_data to self.original_time_data
        self.value_data = []

        # Create and embed matplotlib plot with smaller figure size
        self.original_fig, self.original_ax = plt.subplots(figsize=(4, 4))  # Changed fig to original_fig
        self.original_ax.set_title("Pressure Regulator Plot")
        self.original_ax.set_xlabel("Time (s)")
        self.original_ax.set_ylabel("Amplitude")
        self.original_ax.set_xlim(0, 10)  # Set the initial x-axis limit from 0 to 10 seconds
        self.original_ax.set_ylim(-1.05, 1.05)  # Set the y-axis limit to (-1, 1)
        self.original_line, = self.original_ax.plot([], [])  # Create an empty plot line

        self.original_canvas = FigureCanvasTkAgg(self.original_fig, master=self.plot_frame)  # Changed canvas to original_canvas
        self.original_canvas.get_tk_widget().pack(fill="both", expand=True)

    ################# Sensor Plot Frame ####################
    def sensors_frame(self):
        ############### sensors frame with tabs ##############################
        self.sensors_tabview = customtkinter.CTkTabview(self, width=250, height=400)
        self.sensors_tabview.grid(row=0, column=4, rowspan=4, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.sensors_tabview.add("Sensors 1-4")
        self.sensors_tabview.add("Sensors 5-8")

        # Tab for Sensors 1-4
        self.sensors_fig_1_4, self.axs_1_4 = plt.subplots(4, 1, figsize=(4, 6))
        self.sensors_fig_1_4.subplots_adjust(hspace=1)
        sensor_titles_1_4 = [
            "Pressure Sensor 1 (Pa)",
            "Pressure Sensor 2 (Pa)",
            "Pressure Sensor 3 (Pa)",
            "Pressure Sensor 4 (Pa)"
        ]
        self.sensor_lines_1_4 = []
        for i, ax in enumerate(self.axs_1_4):
            ax.set_title(sensor_titles_1_4[i])
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Pressure (Pa)")
            ax.set_xlim(0, 10)
            ax.set_ylim(-1, 1)
            line, = ax.plot([], [])
            self.sensor_lines_1_4.append(line)
        self.sensors_canvas_1_4 = FigureCanvasTkAgg(self.sensors_fig_1_4, master=self.sensors_tabview.tab("Sensors 1-4"))
        self.sensors_canvas_1_4.get_tk_widget().pack(fill="both", expand=True)

        # Tab for Sensors 5-8
        self.sensors_fig_5_8, self.axs_5_8 = plt.subplots(4, 1, figsize=(4, 6))
        self.sensors_fig_5_8.subplots_adjust(hspace=1)
        sensor_titles_5_8 = [
            "Pressure Sensor 5 (Pa)",
            "Pressure Sensor 6 (Pa)",
            "Pressure Sensor 7 (Pa)",
            "Pressure Sensor 8 (Pa)"
        ]
        self.sensor_lines_5_8 = []
        for i, ax in enumerate(self.axs_5_8):
            ax.set_title(sensor_titles_5_8[i])
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Pressure (Pa)")
            ax.set_xlim(0, 10)
            ax.set_ylim(-1, 1)
            line, = ax.plot([], [])
            self.sensor_lines_5_8.append(line)
        self.sensors_canvas_5_8 = FigureCanvasTkAgg(self.sensors_fig_5_8, master=self.sensors_tabview.tab("Sensors 5-8"))
        self.sensors_canvas_5_8.get_tk_widget().pack(fill="both", expand=True)

        # Initialize sensor data for all 8 sensors
        self.sensors_time_data = []
        self.mprls_1_data = []
        self.mprls_2_data = []
        self.mprls_3_data = []
        self.mprls_4_data = []
        self.mprls_5_data = []
        self.mprls_6_data = []
        self.mprls_7_data = []
        self.mprls_8_data = []

        # Set a method to update the plots dynamically
        self.after(20, self.update_sensors_plot)


    def update_sensors_plot(self):
        """Update the sensor plots for sensors 1-4 and sensors 5-8 with the most recent data from the sensor queue."""
        try:
            sensor_data = None  # Initialize sensor_data to None

            # Drain the queue and get only the most recent data
            while not self.sensor_queue.empty():
                sensor_data = self.sensor_queue.get()  # Keep reading until the queue is empty

            # If we have new data (after emptying the queue)
            if sensor_data:
                # Unpack the data (time, VEAB, MPRLS 1-8)
                current_time, veab_value, mpr_1, mpr_2, mpr_3, mpr_4, mpr_5, mpr_6, mpr_7, mpr_8 = sensor_data

                # Append new data to the respective lists
                self.sensors_time_data.append(current_time)
                self.mprls_1_data.append(mpr_1)
                self.mprls_2_data.append(mpr_2)
                self.mprls_3_data.append(mpr_3)
                self.mprls_4_data.append(mpr_4)
                self.mprls_5_data.append(mpr_5)
                self.mprls_6_data.append(mpr_6)
                self.mprls_7_data.append(mpr_7)
                self.mprls_8_data.append(mpr_8)

                # Limit the data lists to the last 200 points (optional)
                if len(self.sensors_time_data) > 200:
                    self.sensors_time_data = self.sensors_time_data[-200:]
                    self.mprls_1_data = self.mprls_1_data[-200:]
                    self.mprls_2_data = self.mprls_2_data[-200:]
                    self.mprls_3_data = self.mprls_3_data[-200:]
                    self.mprls_4_data = self.mprls_4_data[-200:]
                    self.mprls_5_data = self.mprls_5_data[-200:]
                    self.mprls_6_data = self.mprls_6_data[-200:]
                    self.mprls_7_data = self.mprls_7_data[-200:]
                    self.mprls_8_data = self.mprls_8_data[-200:]

                # Update plots for sensors 1-4
                self.sensor_lines_1_4[0].set_data(self.sensors_time_data, self.mprls_1_data)
                self.sensor_lines_1_4[1].set_data(self.sensors_time_data, self.mprls_2_data)
                self.sensor_lines_1_4[2].set_data(self.sensors_time_data, self.mprls_3_data)
                self.sensor_lines_1_4[3].set_data(self.sensors_time_data, self.mprls_4_data)

                # Update plots for sensors 5-8
                self.sensor_lines_5_8[0].set_data(self.sensors_time_data, self.mprls_5_data)
                self.sensor_lines_5_8[1].set_data(self.sensors_time_data, self.mprls_6_data)
                self.sensor_lines_5_8[2].set_data(self.sensors_time_data, self.mprls_7_data)
                self.sensor_lines_5_8[3].set_data(self.sensors_time_data, self.mprls_8_data)

                # Adjust x-axis limits dynamically
                for ax in self.axs_1_4 + self.axs_5_8:
                    ax.set_xlim(max(0, current_time - 10), current_time)  # Show last 10 seconds of data

                # Adjust y-axis limits dynamically (optional)
                all_sensor_data = (
                    self.mprls_1_data + self.mprls_2_data + self.mprls_3_data + self.mprls_4_data +
                    self.mprls_5_data + self.mprls_6_data + self.mprls_7_data + self.mprls_8_data
                )
                max_y = max(all_sensor_data)
                min_y = min(all_sensor_data)
                for ax in self.axs_1_4 + self.axs_5_8:
                    ax.set_ylim(min_y - 0.1, max_y + 0.1)

                # Redraw the canvases to reflect updates
                self.sensors_canvas_1_4.draw()
                self.sensors_canvas_5_8.draw()

        except Exception as e:
            print(f"Error updating sensor plots: {e}")

        # Call this method again after 20ms
        self.after(20, self.update_sensors_plot)




    def create_sidebar(self):
        """Creates the sidebar frame with buttons and labels."""
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Haptic Display", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sidebar buttons
        button_data = [("Connect", self.connect), ("Reset", self.reset), 
                       ("Save", self.save)]
        for i, (text, cmd) in enumerate(button_data):
            button = customtkinter.CTkButton(self.sidebar_frame, text=text, command=cmd, 
                                             fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
            button.grid(row=i+1, column=0, padx=20, pady=10)

        # Appearance mode option
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w", font=self.default_font)
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event, font=self.default_font)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # UI scaling option
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w", font=self.default_font)
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event, font=self.default_font)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

    def pattern_frame(self):

        ############### pattern frame ##############################
        self.pattern_frame = customtkinter.CTkFrame(self, width=250, height=250)
        self.pattern_frame.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.pattern_var = tkinter.IntVar(value=0)

        # Create the label with dark gray background like a bar
        self.label_pattern = customtkinter.CTkLabel(
            master=self.pattern_frame, 
            text="Pattern Type", 
            fg_color="#C0C0C0",  # Set background to dark gray
            text_color="black",    # Optional: make text white to contrast with dark gray
            width=150,              # Adjust width to make it look like a bar
            corner_radius=10, 
            font=self.default_font
        )
        self.label_pattern.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="nsew")

        # Create pattern buttons with consistent text lengths
        self.pattern_button_1 = customtkinter.CTkRadioButton(master=self.pattern_frame, text="Sine Wave      ", variable=self.pattern_var, value=0, font=self.default_font)
        self.pattern_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.pattern_button_2 = customtkinter.CTkRadioButton(master=self.pattern_frame, text="Constant Wave  ", variable=self.pattern_var, value=1, font=self.default_font)
        self.pattern_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.pattern_button_3 = customtkinter.CTkRadioButton(master=self.pattern_frame, text="Square Wave    ", variable=self.pattern_var, value=2, font=self.default_font)
        self.pattern_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")
        self.pattern_button_4 = customtkinter.CTkRadioButton(master=self.pattern_frame, text="Imported Wave  ", variable=self.pattern_var, value=3, font=self.default_font)
        self.pattern_button_4.grid(row=4, column=2, pady=10, padx=20, sticky="n")

        # pattern buttons
        self.pattern_button_import = customtkinter.CTkButton(self.pattern_frame, text="Import Pattern", command=self.import_pattern, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.pattern_button_import.grid(row=5, column=2, padx=20, pady=10)
        self.pattern_button_play = customtkinter.CTkButton(self.pattern_frame, text="Play Pattern", command=self.play_pattern, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.pattern_button_play.grid(row=6, column=2, padx=20, pady=10)
        self.pattern_button_stop = customtkinter.CTkButton(self.pattern_frame, text="Pause Pattern", command=self.pause_pattern, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.pattern_button_stop.grid(row=7, column=2, padx=20, pady=10)
        

    def manual_frame(self):
        ############### manual frame ##############################
        self.manual = customtkinter.CTkTabview(self, width=250, height=250)
        self.manual.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.manual.add("Slider")
        self.manual.add("Entry")
        self.manual.tab("Slider").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.manual.tab("Entry").grid_columnconfigure(0, weight=1)

        # set volume slider
        self.vol_label = customtkinter.CTkLabel(self.manual.tab("Slider"), text="Amplitude value:", font=self.default_font)
        self.vol_label.grid(row=0, column=0, columnspan=1, padx=10, pady=0, sticky="")

        # Initialize amplitude label to 1 (default value)
        self.vol_label_2 = customtkinter.CTkLabel(self.manual.tab("Slider"), text="1.0", font=self.default_font)
        self.vol_label_2.grid(row=1, column=0, columnspan=1, padx=10, pady=0, sticky="")

        # Set the amplitude slider's default value to 1.0
        self.vol_slider = customtkinter.CTkSlider(self.manual.tab("Slider"), from_=0.0, to=1.0, orientation="vertical", command=self.update_volume_label)
        self.vol_slider.set(1.0)  # Set initial value to 1.0
        self.vol_slider.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 5), sticky="ns")

        # Add an explicit callback to update when slider moves
        self.vol_slider.bind("<ButtonRelease-1>", lambda event: self.update_volume_label(self.vol_slider.get()))

        # set volume progress bar (optional, for display)
        self.vol_progressbar = customtkinter.CTkProgressBar(self.manual.tab("Slider"), orientation="vertical", width=20)
        self.vol_progressbar.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 5), sticky="ns")

        # set frequency slider
        self.freq_label = customtkinter.CTkLabel(self.manual.tab("Slider"), text="Frequency value:", font=self.default_font)
        self.freq_label.grid(row=5, column=0, columnspan=1, padx=10, pady=0, sticky="")

        # Initialize frequency label to 10.0 Hz (default value)
        self.freq_label_2 = customtkinter.CTkLabel(self.manual.tab("Slider"), text="1.0", font=self.default_font)
        self.freq_label_2.grid(row=5, column=1, columnspan=1, padx=10, pady=0, sticky="")

        # Set the frequency slider's default value to 10 Hz
        self.freq_slider = customtkinter.CTkSlider(self.manual.tab("Slider"), from_=0.0, to=5.0, orientation="horizontal", command=self.update_frequency_label)
        self.freq_slider.set(1.0)  # Set initial value to 10.0 Hz
        self.freq_slider.grid(row=6, column=0, columnspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")

        # Add an explicit callback to update when slider moves
        self.freq_slider.bind("<ButtonRelease-1>", lambda event: self.update_frequency_label(self.freq_slider.get()))

        # set frequency progress bar (optional, for display)
        self.freq_progressbar = customtkinter.CTkProgressBar(self.manual.tab("Slider"), orientation="horizontal", height=20)
        self.freq_progressbar.grid(row=7, column=0, columnspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")
   
        # set entry frame
        self.entry_tab = customtkinter.CTkLabel(self.manual.tab("Entry"), text="CTkLabel on Tab 2", font=self.default_font)
        self.entry_tab.grid(row=0, column=0, padx=20, pady=20)

        self.vol_entry = customtkinter.CTkEntry(self.manual.tab("Entry"), placeholder_text="Enter Amplitude Value", font=self.default_font)
        self.vol_entry.grid(row=0, column=0, columnspan=1, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.vol_button = customtkinter.CTkButton(self.manual.tab("Entry"), text="Apply Amplitude", command=self.apply_amplitude, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.vol_button.grid(row=1, column=0, padx=20, pady=10)

        self.freq_entry = customtkinter.CTkEntry(self.manual.tab("Entry"), placeholder_text="Enter Frequency Value", font=self.default_font)
        self.freq_entry.grid(row=2, column=0, columnspan=1, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.freq_button = customtkinter.CTkButton(self.manual.tab("Entry"), text="Apply Frequency", command=self.apply_frequency, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.freq_button.grid(row=3, column=0, padx=20, pady=10)

        
    def effect_frame(self):
        ############### Effect frame ##############################
        self.effect_frame = customtkinter.CTkFrame(self)
        self.effect_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.effect_var = tkinter.IntVar(value=0)

        # Create the label with dark gray background like a bar
        self.label_effect = customtkinter.CTkLabel(
            master=self.effect_frame, 
            text="Experiment", 
            fg_color="#C0C0C0",  # Set background to dark gray
            text_color="black",    # Optional: make text white to contrast with dark gray
            width=150,              # Adjust width to make it look like a bar
            corner_radius=10, 
            font=self.default_font
        )
        self.label_effect.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="nsew")

        # effect buttons
        self.effect_button_training = customtkinter.CTkButton(self.effect_frame, text="Training", command=self.start_training, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.effect_button_training.grid(row=1, column=2, padx=20, pady=10)

        self.effect_button_training = customtkinter.CTkButton(self.effect_frame, text="Experiment", command=self.start_experiment, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.default_font)
        self.effect_button_training.grid(row=2, column=2, padx=20, pady=10)

    
    def channels_frame(self):
        ############# channels frames #############
        self.channel = customtkinter.CTkTabview(self, width=250, height=250)
        self.channel.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.channel.add("Manual")
        self.channel.add("Auto")
        self.channel.tab("Manual").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.channel.tab("Auto").grid_columnconfigure(0, weight=1)

        # Define relay control switches for 8 channels
        self.channels_switch_1 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch1", 
            font=self.default_font,
            command=lambda: self.toggle_relay(1)  # Call the function with channel number
        )
        self.channels_switch_1.grid(row=1, column=0, padx=10, pady=(0, 20))

        self.channels_switch_2 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch2", 
            font=self.default_font,
            command=lambda: self.toggle_relay(2)  # Call the function with channel number
        )
        self.channels_switch_2.grid(row=1, column=1, padx=10, pady=(0, 20))

        self.channels_switch_3 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch3", 
            font=self.default_font,
            command=lambda: self.toggle_relay(3)  # Call the function with channel number
        )
        self.channels_switch_3.grid(row=2, column=0, padx=10, pady=(0, 20))

        self.channels_switch_4 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch4", 
            font=self.default_font,
            command=lambda: self.toggle_relay(4)  # Call the function with channel number
        )
        self.channels_switch_4.grid(row=2, column=1, padx=10, pady=(0, 20))

        # Ch5 controls the first single relay
        self.channels_switch_5 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch5", 
            font=self.default_font,
            command=lambda: self.toggle_relay(5)  # Call the function with channel number
        )
        self.channels_switch_5.grid(row=3, column=0, padx=10, pady=(0, 20))

        # Ch6 controls the second single relay
        self.channels_switch_6 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch6", 
            font=self.default_font,
            command=lambda: self.toggle_relay(6)  # Call the function with channel number
        )
        self.channels_switch_6.grid(row=3, column=1, padx=10, pady=(0, 20))

        # Ch7 controls the second single relay
        self.channels_switch_7 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch7", 
            font=self.default_font,
            command=lambda: self.toggle_relay(7)  # Call the function with channel number
        )
        self.channels_switch_7.grid(row=4, column=0, padx=10, pady=(0, 20))

        # Ch8 controls the second single relay
        self.channels_switch_8 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch8", 
            font=self.default_font,
            command=lambda: self.toggle_relay(8)  # Call the function with channel number
        )
        self.channels_switch_8.grid(row=4, column=1, padx=10, pady=(0, 20))

        # Ch9 controls the second single relay
        self.channels_switch_9 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch9", 
            font=self.default_font,
            command=lambda: self.toggle_relay(9)  # Call the function with channel number
        )
        self.channels_switch_9.grid(row=5, column=0, padx=10, pady=(0, 20))

        # Ch10 controls the second single relay
        self.channels_switch_10 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch10", 
            font=self.default_font,
            command=lambda: self.toggle_relay(10)  # Call the function with channel number
        )
        self.channels_switch_10.grid(row=5, column=1, padx=10, pady=(0, 20))

        # Ch11 controls the second single relay
        self.channels_switch_11 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch11", 
            font=self.default_font,
            command=lambda: self.toggle_relay(11)  # Call the function with channel number
        )
        self.channels_switch_11.grid(row=6, column=0, padx=10, pady=(0, 20))

        # Ch12 controls the second single relay
        self.channels_switch_12 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch12", 
            font=self.default_font,
            command=lambda: self.toggle_relay(12)  # Call the function with channel number
        )
        self.channels_switch_12.grid(row=6, column=1, padx=10, pady=(0, 20))

        # Ch13 controls the second single relay
        self.channels_switch_13 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch13", 
            font=self.default_font,
            command=lambda: self.toggle_relay(13)  # Call the function with channel number
        )
        self.channels_switch_13.grid(row=7, column=0, padx=10, pady=(0, 20))
        
        # Ch14 controls the second single relay
        self.channels_switch_14 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch14", 
            font=self.default_font,
            command=lambda: self.toggle_relay(14)  # Call the function with channel number
        )
        self.channels_switch_14.grid(row=7, column=1, padx=10, pady=(0, 20))

        # Ch15 controls the second single relay
        self.channels_switch_15 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch15", 
            font=self.default_font,
            command=lambda: self.toggle_relay(15)  # Call the function with channel number
        )
        self.channels_switch_15.grid(row=8, column=0, padx=10, pady=(0, 20))

        # Ch16 controls the second single relay
        self.channels_switch_16 = customtkinter.CTkSwitch(
            master=self.channel.tab("Manual"), 
            text=f"Ch16", 
            font=self.default_font,
            command=lambda: self.toggle_relay(16)  # Call the function with channel number
        )
        self.channels_switch_16.grid(row=8, column=1, padx=10, pady=(0, 20))


        # set Auto frame
        self.entry_tab = customtkinter.CTkLabel(self.channel.tab("Auto"), text="Automatical running", font=self.default_font)
        self.entry_tab.grid(row=0, column=0, padx=20, pady=20)

        # In the Auto tab:
        self.auto_channels_switch_1 = customtkinter.CTkSwitch(
            master=self.channel.tab("Auto"), 
            text=f"Demo1", 
            font=self.default_font,
            command=self.run_demo1  # Call the demo function
        )
        self.auto_channels_switch_1.grid(row=1, column=0, padx=10, pady=(0, 20))

        self.auto_channels_switch_2 = customtkinter.CTkSwitch(
            master=self.channel.tab("Auto"), 
            text=f"Demo2", 
            font=self.default_font,
            command=self.run_demo2  # Call the demo function
        )
        self.auto_channels_switch_2.grid(row=2, column=0, padx=10, pady=(0, 20))

        self.auto_channels_switch_3 = customtkinter.CTkSwitch(
            master=self.channel.tab("Auto"), 
            text=f"Demo3 (-><-)", 
            font=self.default_font,
            command=self.run_demo3  # Call the demo function
        )
        self.auto_channels_switch_3.grid(row=3, column=0, padx=10, pady=(0, 20))

        self.auto_channels_switch_4 = customtkinter.CTkSwitch(
            master=self.channel.tab("Auto"), 
            text=f"Demo4 (-->)", 
            font=self.default_font, 
            command=self.run_demo4
        )
        self.auto_channels_switch_4.grid(row=4, column=0, padx=10, pady=(0, 20))


    def run_demo1(self):
        """Run the Demo 1 pattern using binary strings."""
        def demo_pattern():
            # Convert the binary string into a list for mutability
            b_list = list(self.b_string)

            spiral_sequence = [1, 5, 9, 13, 14, 15, 16, 12, 8, 4, 3, 2, 6, 10, 11, 7]

            if self.auto_channels_switch_1.get() == 1:
                print("Starting Demo 1")
                # Turn on valves 1-16 sequentially while the switch is ON
                for i in spiral_sequence:
                    b_list[i-1] = "1"  # Update the valve state
                    binary_string = ''.join(b_list)  # Convert list back to string
                    self.actuator_queue.put(("Valve", binary_string))
                    print(f"Demo 1: Sent binary string {binary_string}")
                    time.sleep(0.15)
            else:
                print("Stopping Demo 1")
                b_list = list("1"*16)
                # Keep all valves off if the switch is OFF
                for i in reversed(spiral_sequence):
                    b_list[i-1] = "0"  # Update the valve state
                    binary_string = ''.join(b_list)  # Convert list back to string
                    self.actuator_queue.put(("Valve", binary_string))
                    print(f"Demo 1: Sent binary string {binary_string}")
                    time.sleep(0.15)
                return

            print("Demo 1: Pattern completed.")

        threading.Thread(target=demo_pattern, daemon=True).start()

    def run_demo2(self):
        """Run the Demo 2 pattern using binary strings."""
        def demo_pattern():
            print("Starting Demo 2")

            # Turn on all valves while the switch is ON
            if self.auto_channels_switch_2.get() == 1:  # Check if the switch is ON
                self.actuator_queue.put(("Valve", '1' * 16))
                print("Demo 2: All valves turned ON")
            else:
                # Turn off all valves
                self.actuator_queue.put(("Valve", '0' * 16))
                print("Demo 2: All valves turned OFF")

        threading.Thread(target=demo_pattern, daemon=True).start()
    
    def run_demo3(self):
        """Run the Demo 3 pattern using binary strings."""
        def demo_pattern():
            print("Starting Demo 3")

            # Convert the binary string into a list for mutability
            b_list = list(self.b_string)

            side_row = [1, 2, 3, 4, 13, 14, 15, 16]
            middle_row = [5, 6, 7, 8, 9, 10, 11, 12]

            delay = 0.2
            
            # Turn on all valves while the switch is ON
            while self.auto_channels_switch_3.get() == 1:  # Check if the switch is ON
                # Pattern 1: Turn on side rows, then middle rows
                for _ in range(3):
                    # Turn on side rows
                    for idx in middle_row:
                        b_list[idx - 1] = "0"
                    for idx in side_row:
                        b_list[idx - 1] = "1"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    print(f"Demo 3: Sent binary string (side rows ON): {binary_string}")
                    time.sleep(delay)

                    # Turn off side rows and turn on middle rows
                    for idx in side_row:
                        b_list[idx - 1] = "0"
                    for idx in middle_row:
                        b_list[idx - 1] = "1"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    print(f"Demo 3: Sent binary string (middle rows ON): {binary_string}")
                    time.sleep(delay)

                    # Turn off all valves when the switch is OFF
                    self.actuator_queue.put(("Valve", '0' * 16))
                    time.sleep(0.4)

                    # Check if the switch was turned OFF
                    if self.auto_channels_switch_3.get() == 0:
                        break

                # Pattern 2: Turn on middle rows, then side rows
                for _ in range(3):
                    # Turn on middle rows
                    for idx in side_row:
                        b_list[idx - 1] = "0"
                    for idx in middle_row:
                        b_list[idx - 1] = "1"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    print(f"Demo 3: Sent binary string (middle rows ON): {binary_string}")
                    time.sleep(delay)

                    # Turn off middle rows and turn on side rows
                    for idx in middle_row:
                        b_list[idx - 1] = "0"
                    for idx in side_row:
                        b_list[idx - 1] = "1"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    print(f"Demo 3: Sent binary string (side rows ON): {binary_string}")
                    time.sleep(delay)

                    # Turn off all valves when the switch is OFF
                    self.actuator_queue.put(("Valve", '0' * 16))
                    time.sleep(0.4)

                    # Check if the switch was turned OFF
                    if self.auto_channels_switch_3.get() == 0:
                        break

            # Turn off all valves when the switch is OFF
            self.actuator_queue.put(("Valve", '0' * 16))
            print("Demo 3: All valves turned OFF")

        threading.Thread(target=demo_pattern, daemon=True).start()

    def run_demo4(self):
        """Run the Demo 4 pattern using binary strings."""
        def demo_pattern():
            print("Starting Demo 4")

            # Convert the binary string into a list for mutability
            b_list = list(self.b_string)

            first_row = [1, 2, 3, 4]
            second_row = [5, 6, 7, 8]
            third_row = [9, 10, 11, 12]
            fourth_row = [13, 14, 15, 16]

            delay = 0.1
            
            # Turn on all valves while the switch is ON
            while self.auto_channels_switch_4.get() == 1:  # Check if the switch is ON
                # Pattern 1: Turn on side rows, then middle rows
                for _ in range(3):

                    # Turn on 1st row
                    for idx in first_row:
                        b_list[idx - 1] = "1"
                    for idx in second_row:
                        b_list[idx - 1] = "0"
                    for idx in third_row:
                        b_list[idx - 1] = "0"
                    for idx in fourth_row:
                        b_list[idx - 1] = "0"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn on 2nd row
                    for idx in first_row:
                        b_list[idx - 1] = "0"
                    for idx in second_row:
                        b_list[idx - 1] = "1"
                    for idx in third_row:
                        b_list[idx - 1] = "0"
                    for idx in fourth_row:
                        b_list[idx - 1] = "0"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn on 3rd row
                    for idx in first_row:
                        b_list[idx - 1] = "0"
                    for idx in second_row:
                        b_list[idx - 1] = "0"
                    for idx in third_row:
                        b_list[idx - 1] = "1"
                    for idx in fourth_row:
                        b_list[idx - 1] = "0"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn on 4th row
                    for idx in first_row:
                        b_list[idx - 1] = "0"
                    for idx in second_row:
                        b_list[idx - 1] = "0"
                    for idx in third_row:
                        b_list[idx - 1] = "0"
                    for idx in fourth_row:
                        b_list[idx - 1] = "1"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn off all valves when the switch is OFF
                    self.actuator_queue.put(("Valve", '0' * 16))
                    time.sleep(0.3)

                    # Check if the switch was turned OFF
                    if self.auto_channels_switch_4.get() == 0:
                        break

                # Pattern 2: Turn on middle rows, then side rows
                for _ in range(3):

                    # Turn on 1st row
                    for idx in first_row:
                        b_list[idx - 1] = "0"
                    for idx in second_row:
                        b_list[idx - 1] = "0"
                    for idx in third_row:
                        b_list[idx - 1] = "0"
                    for idx in fourth_row:
                        b_list[idx - 1] = "1"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn on 2nd row
                    for idx in first_row:
                        b_list[idx - 1] = "0"
                    for idx in second_row:
                        b_list[idx - 1] = "0"
                    for idx in third_row:
                        b_list[idx - 1] = "1"
                    for idx in fourth_row:
                        b_list[idx - 1] = "0"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn on 3rd row
                    for idx in first_row:
                        b_list[idx - 1] = "0"
                    for idx in second_row:
                        b_list[idx - 1] = "1"
                    for idx in third_row:
                        b_list[idx - 1] = "0"
                    for idx in fourth_row:
                        b_list[idx - 1] = "0"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn on 4th row
                    for idx in first_row:
                        b_list[idx - 1] = "1"
                    for idx in second_row:
                        b_list[idx - 1] = "0"
                    for idx in third_row:
                        b_list[idx - 1] = "0"
                    for idx in fourth_row:
                        b_list[idx - 1] = "0"
                    binary_string = ''.join(b_list)
                    self.actuator_queue.put(("Valve", binary_string))
                    time.sleep(delay)

                    # Turn off all valves when the switch is OFF
                    self.actuator_queue.put(("Valve", '0' * 16))
                    time.sleep(0.3)

                    # Check if the switch was turned OFF
                    if self.auto_channels_switch_4.get() == 0:
                        break

            # Turn off all valves when the switch is OFF
            self.actuator_queue.put(("Valve", '0' * 16))
            print("Demo 4: All valves turned OFF")

        threading.Thread(target=demo_pattern, daemon=True).start()


    def toggle_relay(self, channel):
        """Toggle the valve state and send the updated binary string."""
        def send_command():
            if channel <= 16:
                switch = getattr(self, f'channels_switch_{channel}')
                # Update the state of the corresponding valve
                self.valve_states[channel - 1] = 1 if switch.get() == 1 else 0
                
                # Create the binary string
                binary_string = ''.join(map(str, self.valve_states))
                
                # Send the binary string to the actuator queue
                self.actuator_queue.put(("Valve", binary_string))
                print(f"Sent binary string: {binary_string}")

        threading.Thread(target=send_command, daemon=True).start()




    # Helper functions
    # ---------------------------------------------------------------------------------------------
    def transmit(self, header, information):
        self.data_queue.put((header, information))

    # close the window
    def close(self):
        self.transmit("Close", "close")
        self.countdown_id = None

    def on_closing(self):
        """Handle the event when the window is closed."""
        # Send a "Close" message to the main process
        if self.in_queue:
            self.in_queue.put(("Close", None))
        self.destroy()  # Close the GUI window



    # modify the app appearance
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    ############### sidebar ##############################
    def command(self):
        self.text_print(self.entry.get())

    def connect(self):
        # Open an input dialog for entering the Raspberry Pi's IP address
        ip_address = CTkInputDialog(text="Enter Raspberry Pi IP Address", title="Connect to Raspberry Pi").get_input()

        if ip_address:
            self.text_print(f"Connecting to Raspberry Pi at {ip_address}...")
            # Send the IP address to the main process via the queue
            self.transmit("Connect", ip_address)
            self.in_queue.put(("Connect", ip_address))  # This line sends the IP address to the main process
        else:
            self.text_print("Connection canceled.")


    def reset(self):
        """Reset the plot and the GUI state."""
        # Clear the textbox
        self.textbox.delete(0.0, 'end')
        self.text_print("Reset the haptic device!")

        # Clear the time and value data lists
        self.time_data.clear()
        self.value_data.clear()

        # Reset the plot line
        self.line.set_data([], [])  # Clear the plot by setting empty data

        # Reset the axes
        self.ax.set_xlim(0, 10)  # Reset x-axis to 0-10 seconds
        self.ax.set_ylim(-1.05, 1.05)  # Reset y-axis to -1 and 1 (for sine, square, triangle waves)

        # Redraw the canvas to show the reset plot
        self.canvas.draw()

        # Optionally reset the start time (for real-time plotting)
        if hasattr(self, 'start_time'):
            del self.start_time  # Remove the start_time attribute to reset real-time plotting
        
        self.pattern_button_play.configure(state="normal")


    def save(self):
        self.text_print("Save the data from haptic device!")
    
    def stop(self):
        self.text_print("Disconnecting the haptic device!")
        self.actuator_queue.put("1_RELAY_ON")
        self.actuator_queue.put("2_RELAY_ON")
        self.actuator_queue.put("3_RELAY_ON")
        self.actuator_queue.put("4_RELAY_ON")
        self.actuator_queue.put("5_RELAY_ON")
        self.actuator_queue.put("6_RELAY_ON")

        self.stop_flag = True



    ############### plot frame ################################

    ############### pattern frame ##############################
    def import_pattern(self):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(title="Select Pattern File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        
        if file_path:
            self.text_print(f"Imported Pattern File: {file_path}")
            
            # Initialize lists to store time and Singletact Force (N) values
            time_list = []
            force_list = []
            
            # Open the CSV file and read the data
            with open(file_path, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)  # Skip the header row
                for row in csv_reader:
                    # Append data to lists
                    time_list.append(float(row[0]))       # Time (s) from the first column
                    force_list.append(float(row[3]))      # Singletact Force (N) from the fourth column
            

            # modify the time
            for i in range(len(time_list)):
                if i %2 == 0:
                    time_list[i] = time_list[i] - (0.0333333*0.5)

            # # delete the offset
            for i in range(len(force_list)):
                if force_list[i] < 0:
                    force_list[i] = 0
            
            # Interpolate the data to 100 Hz
            # gaussian filter
            sigma = 10
            self.interpolated_force = gaussian_filter1d(self.interpolate_force_data(time_list, force_list), sigma)
            
            # Return the lists if needed for further processing
            return time_list, force_list
        else:
            self.text_print("No file selected for pattern.")

    def interpolate_force_data(self, time_list, force_list):
        """Interpolate force data to 100 Hz based on the original time_list and force_list."""
        # Create an interpolation function based on the original data
        interp_function = interp1d(time_list, force_list, kind='linear', fill_value="extrapolate")
        
        # Generate a new time array with 100 Hz frequency
        self.interpolated_time = np.arange(time_list[0], time_list[-1], 0.01)  # 100 Hz => 0.01 s intervals
        
        # Interpolate force values to match the 100 Hz time base
        return interp_function(self.interpolated_time)

    def play_pattern(self):
        self.stop_flag = False
        # disable play button and enable stop button
        self.pattern_button_play.configure(state="disabled")
        self.pattern_button_stop.configure(state="normal")

        # Get the selected pattern
        selected_pattern = self.pattern_var.get()

        if selected_pattern == 0:  # Sine Wave
            pattern_name = "Sine Wave"
            self.wave_function = np.sin
        elif selected_pattern == 1:  # Triangle Wave
            pattern_name = "Constant Wave"
            self.wave_function = self.generate_constant_wave
        elif selected_pattern == 2:  # Square Wave
            pattern_name = "Square Wave"
            self.wave_function = self.generate_square_wave
        else:
            pattern_name = "Import Wave"

        self.text_print(f"Playing Pattern: {pattern_name}")
        self.run_wave()  # Start generating the selected wave
        self.in_queue.put(("Play Pattern", pattern_name))

    def generate_square_wave(self, t):
        """Generates a square wave at time t."""
        return np.sign(np.sin(t))
    
    def generate_constant_wave(self, t):
        return 1

    def generate_triangle_wave(self, t):
        """Generates a triangle wave at time t."""
        return 2 * np.abs(2 * (t / np.pi - np.floor(t / np.pi + 0.5))) - 1

    def run_wave(self):
        """Continuously add data to the plot for the selected wave at 100 Hz."""
        self.add_data()  # Add the selected wave data
        # Store the after() ID so we can cancel it later
        self.wave_job = self.after(10, self.run_wave)  # Update every 10ms (100 updates per second for 100 Hz)


    ################# Adding Data to Original Plot ####################
    def add_data(self):
        """Dynamically adds wave data to the original plot, synchronizing with real time."""
        try:
            # Get the current real time in seconds
            current_real_time = time.time()

            # If this is the first data point, set the start time
            if not hasattr(self, 'start_time'):
                self.start_time = current_real_time  # Record the time when the plotting started

            # Calculate the elapsed time
            elapsed_time = current_real_time - self.start_time

            # Check if we're using the Imported Wave pattern
            if self.pattern_var.get() == 3:  # Assuming pattern_var 3 is for "Imported Wave"
                # Find the closest interpolated time index
                idx = int(elapsed_time * 100)  # 100 Hz index based on elapsed time
                
                # Ensure the index is within the range of interpolated data
                if idx < len(self.interpolated_time):

                    # 0.50 to 0.56
                    # diff = 0.61 - 0.53 = 0.08
                    wave_value = 0.53 + 0.09*(self.interpolated_force[idx])
                    if wave_value > 0.61:
                        wave_value = 0.61

                    # wave_value = self.interpolated_force[idx]  # Use interpolated force value
                else:
                    wave_value = 0  # Stop the wave once data ends

            else:
                # For other patterns, fetch the current amplitude and frequency values from the sliders
                amplitude = float(self.vol_slider.get())  # Get amplitude from volume slider
                frequency = float(self.freq_slider.get())  # Get frequency from frequency slider

                # Use the selected wave function (sine, square, or triangle) to generate the waveform
                wave_value = amplitude * self.wave_function(2 * np.pi * frequency * elapsed_time)

            if self.stop_flag:
                wave_value = 0
            # Send wave value and pressure error to Raspberry Pi
            self.regulator_queue.put(wave_value)
            # print(wave_value)

            # Append the new data to the plot lists
            self.original_time_data.append(elapsed_time)  # Using original_time_data here
            self.value_data.append(wave_value)

            # Set the x-axis range to show the last 10 seconds
            if elapsed_time > 10:
                self.original_ax.set_xlim(elapsed_time - 10, elapsed_time)
            else:
                self.original_ax.set_xlim(0, 10)  # Show from 0 to 10 seconds initially

            # Update the plot line data without clearing the plot
            self.original_line.set_data(self.original_time_data, self.value_data)

            # Redraw the canvas to update the plot
            self.original_canvas.draw()

        except ValueError:
            tkinter.messagebox.showerror("Invalid input", "An error occurred in the wave generation.")

    def pause_pattern(self):
        """Stop updating the plot when the user clicks 'Stop Pattern'."""
        # Cancel the scheduled run_wave update
        if hasattr(self, 'wave_job'):
            self.after_cancel(self.wave_job)
            del self.wave_job  # Remove the reference to avoid accidentally using it later

        # Enable play button and disable stop button
        self.pattern_button_stop.configure(state="disabled")

        # Inform the user that the pattern has stopped
        self.text_print("Paused Pattern! Please click 'Reset' Button to clear the plot! ")


    ############### manual frame ##############################
    def update_volume_label(self, value):
        """Update the amplitude label when the slider is moved."""
        self.vol_label_2.configure(text=f"{float(value):.2f}")  # Update label with slider value

        self.vol_progressbar.set(value)  # Set the progress bar value

    def update_frequency_label(self, value):
        """Update the frequency label when the slider is moved."""
        self.freq_label_2.configure(text=f"{float(value):.2f}")  # Update label with slider value

        # Normalize the slider value to update the progress bar (0.0 to 1.0 range)
        normalized_value = float(value) / 5.0  # Since the slider is from 0 to 5
        self.freq_progressbar.set(normalized_value)  # Set the progress bar value

    def apply_amplitude(self):
        try:
            amplitude_value = float(self.vol_entry.get())  # Get the amplitude from the entry field
            if 0.0 <= amplitude_value <= 1.0:  # Ensure the value is within slider range
                self.vol_slider.set(amplitude_value)  # Update the slider
                self.update_volume_label(amplitude_value)  # Update the plot value
            else:
                tkinter.messagebox.showerror("Invalid input", "Amplitude must be between 0.0 and 1.0")
        except ValueError:
            tkinter.messagebox.showerror("Invalid input", "Please enter a valid number for amplitude.")

    
    def apply_frequency(self):
        try:
            frequency_value = float(self.freq_entry.get())  # Get the frequency from the entry field
            if 0.0 <= frequency_value <= 5.0:  # Ensure the value is within slider range
                self.freq_slider.set(frequency_value)  # Update the slider
                self.update_frequency_label(frequency_value)  # Update the plot value
            else:
                tkinter.messagebox.showerror("Invalid input", "Frequency must be between 0.0 and 5.0")
        except ValueError:
            tkinter.messagebox.showerror("Invalid input", "Please enter a valid number for frequency.")


    ############### Experiment frame ##############################
    def start_training(self):
        # Create a new window for the training
        training_window = customtkinter.CTkToplevel(self)
        training_window.title("Training")
        training_window.geometry("800x680")  # Adjust the size of the new window as needed

        # Configure grid layout for the new window
        training_window.grid_columnconfigure(0, weight=1)
        training_window.grid_rowconfigure(0, weight=1)

        # Create a tab view for "Static" and "Animation"
        training_tabview = customtkinter.CTkTabview(master=training_window, width=250, height=250)
        training_tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Add tabs
        training_tabview.add("Static")
        training_tabview.add("Animation")
        training_tabview.tab("Static").grid_columnconfigure((0, 1, 2, 3), weight=1)  # Configure grid for 4 columns
        training_tabview.tab("Static").grid_rowconfigure((0, 1, 2), weight=1)  # Configure grid for 3 rows
        training_tabview.tab("Animation").grid_columnconfigure((0, 1, 2, 3), weight=1)
        training_tabview.tab("Animation").grid_rowconfigure((0, 1, 2), weight=1)

        # Top-left Control Buttons in Static Tab
        control_frame = customtkinter.CTkFrame(master=training_tabview.tab("Static"))
        control_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        control_frame.grid_columnconfigure((0, 1), weight=1)

        # "Clear" Button
        clear_button = customtkinter.CTkButton(
            control_frame,
            text="Clear",
            command=self.tactile_controller.clear_pattern,
            font=self.default_font,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        clear_button.grid(row=0, column=1, padx=5, pady=5)

        # "Test" Button
        test_button = customtkinter.CTkButton(
            control_frame,
            text="Test",
            command=self.tactile_controller.test_pattern,
            font=self.default_font,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
        )
        test_button.grid(row=0, column=0, padx=5, pady=5)

        # Static Tab
        picture_folder_static = os.path.join(os.getcwd(), "Pictures", "Static")  # Picture folder path

        for i in range(3):  # 3 rows
            for j in range(4):  # 4 columns
                image_index = i * 4 + j + 1  # Calculate the image index (1 to 12)
                image_path = os.path.join(picture_folder_static, f"{image_index}.png")

                try:
                    # Load and resize the image
                    img = Image.open(image_path)
                    img = img.resize((100, 100))  # Resize to fit within the label (adjust as needed)
                    img_tk = ImageTk.PhotoImage(img)

                    # Create a frame for the image and button
                    image_frame = customtkinter.CTkFrame(training_tabview.tab("Static"))
                    image_frame.grid(row=i + 1, column=j, padx=10, pady=10, sticky="nsew")
                    image_frame.grid_rowconfigure(0, weight=1)
                    image_frame.grid_rowconfigure(1, weight=0)
                    image_frame.grid_columnconfigure(0, weight=1)

                    # Create a label to display the image
                    image_label = customtkinter.CTkLabel(
                        image_frame,
                        image=img_tk,
                        text="",  # No text, just the image
                    )
                    image_label.image = img_tk  # Keep a reference to avoid garbage collection
                    image_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

                    # Add the "Play" button below the image
                    play_button = customtkinter.CTkButton(
                        image_frame,
                        text="Play",
                        command=lambda idx=image_index: self.run_static_pattern(idx),
                        font=self.default_font,
                        fg_color="transparent",
                        border_width=2,
                        text_color=("gray10", "#DCE4EE"),
                    )
                    play_button.grid(row=1, column=0, padx=5, pady=5)

                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")

        # Animation Tab
        picture_folder_animation = os.path.join(os.getcwd(), "Pictures", "Animation")  # Picture folder path

        for i in range(3):  # 3 rows
            for j in range(4):  # 4 columns
                image_index = i * 4 + j + 1  # Calculate the image index (1 to 12)
                image_path = os.path.join(picture_folder_animation, f"{image_index}.png")

                try:
                    # Load and resize the image
                    img = Image.open(image_path)
                    img = img.resize((100, 100))  # Resize to fit within the label (adjust as needed)
                    img_tk = ImageTk.PhotoImage(img)

                    # Create a frame for the image and button
                    image_frame = customtkinter.CTkFrame(training_tabview.tab("Animation"))
                    image_frame.grid(row=i + 1, column=j, padx=10, pady=10, sticky="nsew")
                    image_frame.grid_rowconfigure(0, weight=1)
                    image_frame.grid_rowconfigure(1, weight=0)
                    image_frame.grid_columnconfigure(0, weight=1)

                    # Create a label to display the image
                    image_label = customtkinter.CTkLabel(
                        image_frame,
                        image=img_tk,
                        text="",  # No text, just the image
                    )
                    image_label.image = img_tk  # Keep a reference to avoid garbage collection
                    image_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

                    # Add the "Play" button below the image
                    play_button = customtkinter.CTkButton(
                        image_frame,
                        text="Play",
                        command=lambda idx=image_index: self.run_animation_pattern(idx),
                        font=self.default_font,
                        fg_color="transparent",
                        border_width=2,
                        text_color=("gray10", "#DCE4EE"),
                    )
                    play_button.grid(row=1, column=0, padx=5, pady=5)

                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")

    def start_experiment(self):
        # Create a new window for the experiment
        experiment_window = customtkinter.CTkToplevel(self)
        experiment_window.title("Experiment")
        experiment_window.geometry("1000x680")  # Adjust the size of the new window as needed

        # Configure grid layout for the experiment window
        experiment_window.grid_columnconfigure(1, weight=4)  # Main content column
        experiment_window.grid_columnconfigure(0, weight=1)  # Bar frame column
        experiment_window.grid_rowconfigure(0, weight=1)

        # Variables
        self.selected_type = tkinter.StringVar(value="Static")  # Default type: Static
        self.selected_choice = tkinter.IntVar(value=0)  # No choice selected
        self.trial_number = tkinter.IntVar(value=1)  # Start at trial 1

        # Bar Frame
        bar_frame = customtkinter.CTkFrame(experiment_window, width=200)
        bar_frame.grid(row=0, column=0, padx=(10, 10), pady=10, sticky="ns")
        bar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        bar_frame.grid_rowconfigure(6, weight=10)  # Add space below

        # Subject Number Label
        subject_label = customtkinter.CTkLabel(
            master=bar_frame,
            text="Subject Number:",
            font=self.default_font,
        )
        subject_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Subject Number Entry
        subject_entry = customtkinter.CTkEntry(
            master=bar_frame,
            placeholder_text="Enter Subject Number",
            font=self.default_font,
        )
        subject_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Experiment Type Label and OptionMenu
        type_label = customtkinter.CTkLabel(
            master=bar_frame,
            text="Type:",
            font=self.default_font,
        )
        type_label.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="w")

        type_menu = customtkinter.CTkOptionMenu(
            master=bar_frame,
            variable=self.selected_type,
            values=["Static", "Animation"],
            font=self.default_font,
        )
        type_menu.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Trial Number Label
        trial_label = customtkinter.CTkLabel(
            master=bar_frame,
            textvariable=tkinter.StringVar(value=f"Trial Number: {self.trial_number.get()}/24"),
            font=self.default_font,
        )
        trial_label.grid(row=4, column=0, padx=10, pady=(10, 5), sticky="w")

        # Play Again Button
        play_again_button = customtkinter.CTkButton(
            master=bar_frame,
            text="Play Again",
            font=self.default_font,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=self.play_pattern,  # Replace with your actual function
        )
        play_again_button.grid(row=5, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Next Button
        next_button = customtkinter.CTkButton(
            master=bar_frame,
            text="Next",
            font=self.default_font,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            command=lambda: self.next_trial(trial_label),  # Update trial number
        )
        next_button.grid(row=6, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Tab View for Static and Animation
        experiment_tabview = customtkinter.CTkTabview(master=experiment_window, width=250, height=250)
        experiment_tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Add Tabs
        experiment_tabview.add("Static")
        experiment_tabview.add("Animation")
        experiment_tabview.tab("Static").grid_columnconfigure((0, 1, 2, 3), weight=1)
        experiment_tabview.tab("Static").grid_rowconfigure((0, 1, 2), weight=1)
        experiment_tabview.tab("Animation").grid_columnconfigure((0, 1, 2, 3), weight=1)
        experiment_tabview.tab("Animation").grid_rowconfigure((0, 1, 2), weight=1)

        # Add Images and Choice Buttons to Static Tab
        self.add_choices_to_tab("Static", experiment_tabview)

        # Add Images and Choice Buttons to Animation Tab
        self.add_choices_to_tab("Animation", experiment_tabview)

    def add_choices_to_tab(self, tab_name, tabview):
        """
        Add images and choice buttons to the specified tab.

        Args:
            tab_name (str): "Static" or "Animation".
            tabview: The CTkTabview object containing the tabs.
        """
        folder_path = os.path.join(os.getcwd(), "Pictures", tab_name)

        for i in range(3):  # 3 rows
            for j in range(4):  # 4 columns
                image_index = i * 4 + j + 1
                image_path = os.path.join(folder_path, f"{image_index}.png")
                try:
                    # Load and resize the image
                    img = Image.open(image_path)
                    img = img.resize((100, 100))  # Resize image
                    img_tk = ImageTk.PhotoImage(img)

                    # Create a frame for the image and choice button
                    image_frame = customtkinter.CTkFrame(tabview.tab(tab_name))
                    image_frame.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")

                    # Add the image label
                    image_label = customtkinter.CTkLabel(
                        image_frame,
                        image=img_tk,
                        text="",
                    )
                    image_label.image = img_tk
                    image_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

                    # Add the choice button
                    choice_button = customtkinter.CTkRadioButton(
                        image_frame,
                        text=f"Choice {image_index}",
                        variable=self.selected_choice,
                        value=image_index,
                        font=self.default_font,
                        command=lambda: self.deselect_choice(),
                    )
                    choice_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")

    def deselect_choice(self):
        """
        Allow the user to deselect their choice.
        """
        if self.selected_choice.get() == 0:
            self.selected_choice.set(-1)  # Reset to an unselected state
        else:
            self.selected_choice.set(0)

    def next_trial(self, trial_label):
        """
        Update the trial number when the Next button is clicked.

        Args:
            trial_label: The CTkLabel displaying the trial number.
        """
        current_trial = self.trial_number.get()
        if current_trial < 24:
            self.trial_number.set(current_trial + 1)
            trial_label.configure(text=f"Trial Number: {self.trial_number.get()}/24")


    def run_animation_pattern(self, pattern_index):
        """
        Plays the selected animation pattern.

        Args:
            pattern_index (int): The index of the animation pattern (1 to 12).
        """
        self.tactile_controller.clear_pattern()  # Clear the current pattern
        # Dynamically call the corresponding animation_X function
        getattr(self.tactile_controller, f"animation_{pattern_index}")()


    def run_static_pattern(self, pattern_index):
            """
            Clears the current pattern and plays the selected static pattern.

            Args:
                pattern_index (int): The index of the static pattern (1 to 12).
            """
            self.tactile_controller.clear_pattern()  # Clear the current pattern
            # Dynamically call the corresponding static_X function
            getattr(self.tactile_controller, f"static_{pattern_index}")()

    
    def text_print(self, text, mode=None):
        """Inserts the given text into the textbox."""
        if mode == "main":
            self.textbox.insert("end", "[Main Loop] " + text + "\n")  # Insert text at the end with a newline
        else:
            self.textbox.insert("end", "[GUI Loop] " + text + "\n")  # Insert text at the end with a newline
        self.textbox.yview("end")  # Scroll to the end to make the new text visible
    
    def check_for_messages(self):
        """Periodically checks for messages from the main process and displays them."""
        try:
            while not self.data_queue.empty():
                header, message = self.data_queue.get()

                if header == "Status":
                    # Display the message in the GUI using text_print()
                    # print(f"Received in GUI: {message}")  # Debugging in terminal
                    self.text_print(message, "main")  # Display in the textbox

        except Exception as e:
            print(f"Error in check_for_messages: {e}")

        # Check for messages again after 100ms
        self.after(100, self.check_for_messages)





def launchGUI(conn, in_conn, regulator_conn, actuator_conn, sensor_conn):
    gui = GUI(conn, in_conn, regulator_conn, actuator_conn, sensor_conn)
    gui.mainloop()
    exit()
