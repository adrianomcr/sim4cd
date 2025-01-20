#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to configure the sensors properties

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os

class SensorsEditorGUI:
    """
    Class that defines a GUI for configuring the sensors properties
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the SensorsEditorGUI class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
            enable_io_ (bool): Flag to enable the creation of input/output buttons to the gui
        """

        # Set the root variable
        self.root = root_

        # Set the io_enabled variable
        self.io_enabled = enable_io_

        if(self.io_enabled):
            # Create buttons to load and save file
            buttons_frame = ttk.Frame(self.root)
            buttons_frame.pack(side=tk.LEFT, fill="both")
            # Button to load file
            self.load_button = ttk.Button(buttons_frame, text="    Load", padding=(4, 4), command=self.load_json)
            self.load_button.pack(pady=10, side=tk.TOP)
            # Button to save file
            self.save_button = ttk.Button(buttons_frame, text="    Save", padding=(4, 4), command=self.save_json)
            self.save_button.pack(pady=10, side=tk.TOP)
            # Button to save file as
            self.saveas_button = ttk.Button(buttons_frame, text="  Save As", padding=(4, 4), command=self.saveas_json)
            self.saveas_button.pack(pady=10, side=tk.TOP)

        # Define a accelerometer panel
        self.acc_frame = ttk.Frame(self.root)
        self.acc_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the accelerometer panel
        self.name_acc_label = ttk.Label(self.acc_frame, text="Accelerometer", font=("Helvetica", 18))
        self.name_acc_label.pack(side=tk.TOP, pady=2)

        # Define a gyro panel
        self.gyro_frame = ttk.Frame(self.root)
        self.gyro_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the gyro panel
        self.name_gyro_label = ttk.Label(self.gyro_frame, text="Gyro", font=("Helvetica", 18))
        self.name_gyro_label.pack(side=tk.TOP, pady=2)

        # Define a magnetometer panel
        self.mag_frame = ttk.Frame(self.root)
        self.mag_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the magnetometer panel
        self.name_mag_label = ttk.Label(self.mag_frame, text="Magnetometer", font=("Helvetica", 18))
        self.name_mag_label.pack(side=tk.TOP, pady=2)

        # Define a panel for GPS and barometer
        gps_bar_frame = ttk.Frame(self.root)
        gps_bar_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Define a GPS panel
        self.gps_frame = ttk.Frame(gps_bar_frame)
        self.gps_frame.pack(side=tk.TOP, fill="both", expand=True)
        # Add a title for the GPS panel
        self.name_gps_label = ttk.Label(self.gps_frame, text="GPS", font=("Helvetica", 18))
        self.name_gps_label.pack(side=tk.TOP, pady=2)
        # Define a barometer panel
        self.bar_frame = ttk.Frame(gps_bar_frame)
        self.bar_frame.pack(side=tk.TOP, fill="both", expand=True)
        # Add a title for the barometer panel
        self.name_bar_label = ttk.Label(self.bar_frame, text="Barometer", font=("Helvetica", 18))
        self.name_bar_label.pack(side=tk.TOP, pady=(20,0))

        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}

        # Build the panels for each sensor
        self.build_acc_panel()
        self.build_gyro_panel()
        self.build_mag_panel()
        self.build_gps_panel()
        self.build_bar_panel()


    def build_acc_panel(self):
        """
        Function to build the widgets into the accelerometer panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.acc_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.acc_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the Gaussian noise
        self.entry_noise_acc_x = self.add_configurable_input(noise_frame_,'     Noise x','[m/s²]', '#B00000')
        self.entry_noise_acc_y = self.add_configurable_input(noise_frame_,'     Noise y','[m/s²]', '#00B000')
        self.entry_noise_acc_z = self.add_configurable_input(noise_frame_,'     Noise z','[m/s²]', '#0000B0')

        # Create a subframe for constant bias
        bias_label_ = ttk.Label(self.acc_frame, text="Constant bias")
        bias_label_.pack(side=tk.TOP, pady=(20,2))
        bias_frame_ = ttk.Frame(self.acc_frame)
        bias_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the constant bias
        self.entry_bias_acc_x = self.add_configurable_input(bias_frame_,'       Bias x','[m/s²]', '#B00000')
        self.entry_bias_acc_y = self.add_configurable_input(bias_frame_,'       Bias y','[m/s²]', '#00B000')
        self.entry_bias_acc_z = self.add_configurable_input(bias_frame_,'       Bias z','[m/s²]', '#0000B0')

        # Create a subframe for vibration coupling
        vib_label_ = ttk.Label(self.acc_frame, text="Vibration coupling")
        vib_label_.pack(side=tk.TOP, pady=(20,2))
        vib_frame_ = ttk.Frame(self.acc_frame)
        vib_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the vibration coupling
        self.entry_vib_acc_x = self.add_configurable_input(vib_frame_,'Vibration x','[  -  ]', '#B00000')
        self.entry_vib_acc_y = self.add_configurable_input(vib_frame_,'Vibration y','[  -  ]', '#00B000')
        self.entry_vib_acc_z = self.add_configurable_input(vib_frame_,'Vibration z','[  -  ]', '#0000B0')

        # Add button to apply the accelerometer values on the gui to the data dictionary
        set_button = ttk.Button(self.acc_frame, text="Set acc values", padding=(4, 4), command=self.set_values_acc)
        set_button.pack(pady=(20,5), side=tk.TOP)


    def build_gyro_panel(self):
        """
        Function to build the widgets into the gyro panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.gyro_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.gyro_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the Gaussian noise
        self.entry_noise_gyro_x = self.add_configurable_input(noise_frame_,'     Noise x','[rad/s]', '#B00000')
        self.entry_noise_gyro_y = self.add_configurable_input(noise_frame_,'     Noise y','[rad/s]', '#00B000')
        self.entry_noise_gyro_z = self.add_configurable_input(noise_frame_,'     Noise z','[rad/s]', '#0000B0')

        # Create a subframe for constant bias
        bias_label_ = ttk.Label(self.gyro_frame, text="Constant bias")
        bias_label_.pack(side=tk.TOP, pady=(20,2))
        bias_frame_ = ttk.Frame(self.gyro_frame)
        bias_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the constant bias
        self.entry_bias_gyro_x = self.add_configurable_input(bias_frame_,'       Bias x','[rad/s]', '#B00000')
        self.entry_bias_gyro_y = self.add_configurable_input(bias_frame_,'       Bias y','[rad/s]', '#00B000')
        self.entry_bias_gyro_z = self.add_configurable_input(bias_frame_,'       Bias z','[rad/s]', '#0000B0')

        # Create a subframe for vibration coupling
        vib_label_ = ttk.Label(self.gyro_frame, text="Vibration coupling")
        vib_label_.pack(side=tk.TOP, pady=(20,2))
        vib_frame_ = ttk.Frame(self.gyro_frame)
        vib_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the vibration coupling
        self.entry_vib_gyro_x = self.add_configurable_input(vib_frame_,'Vibration x','[   -   ]', '#B00000')
        self.entry_vib_gyro_y = self.add_configurable_input(vib_frame_,'Vibration y','[   -   ]', '#00B000')
        self.entry_vib_gyro_z = self.add_configurable_input(vib_frame_,'Vibration z','[   -   ]', '#0000B0')

        # Add button to apply the gyro values on the gui to the data dictionary
        set_button = ttk.Button(self.gyro_frame, text="Set gyro values", padding=(4, 4), command=self.set_values_gyro)
        set_button.pack(pady=(20,5), side=tk.TOP)


    def build_mag_panel(self):
        """
        Function to build the widgets into the magnetometer panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.mag_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.mag_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the Gaussian noise
        self.entry_noise_mag_x = self.add_configurable_input(noise_frame_,'     Noise x','[G]', '#B00000')
        self.entry_noise_mag_y = self.add_configurable_input(noise_frame_,'     Noise y','[G]', '#00B000')
        self.entry_noise_mag_z = self.add_configurable_input(noise_frame_,'     Noise z','[G]', '#0000B0')

        # Create a subframe for constant bias
        bias_label_ = ttk.Label(self.mag_frame, text="Constant bias")
        bias_label_.pack(side=tk.TOP, pady=(20,2))
        bias_frame_ = ttk.Frame(self.mag_frame)
        bias_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the constant bias
        self.entry_bias_mag_x = self.add_configurable_input(bias_frame_,'       Bias x','[G]  ', '#B00000')
        self.entry_bias_mag_y = self.add_configurable_input(bias_frame_,'       Bias y','[G]  ', '#00B000')
        self.entry_bias_mag_z = self.add_configurable_input(bias_frame_,'       Bias z','[G]  ', '#0000B0')

        # Create a subframe for interference coupling
        vib_label_ = ttk.Label(self.mag_frame, text="Interference coupling")
        vib_label_.pack(side=tk.TOP, pady=(20,2))
        vib_frame_ = ttk.Frame(self.mag_frame)
        vib_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the interference coupling
        self.entry_intf_mag_x = self.add_configurable_input(vib_frame_,'   Interf. x','[G/A]', '#B00000')
        self.entry_intf_mag_y = self.add_configurable_input(vib_frame_,'   Interf. y','[G/A]', '#00B000')
        self.entry_intf_mag_z = self.add_configurable_input(vib_frame_,'   Interf. z','[G/A]', '#0000B0')

        # Add button to apply the magnetometer values on the gui to the data dictionary
        set_button = ttk.Button(self.mag_frame, text="Set mag values", padding=(4, 4), command=self.set_values_mag)
        set_button.pack(pady=(20,5), side=tk.TOP)


    def build_gps_panel(self):
        """
        Function to build the widgets into the GPS panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.gps_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.gps_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the Gaussian noise
        self.entry_noise_gps_xy = self.add_configurable_input(noise_frame_,'    Noise xy','[m]', '#B0B000')
        self.entry_noise_gps_z = self.add_configurable_input(noise_frame_,'     Noise z','[m]', '#0000B0')

        # Add button to apply the GPS values on the gui to the data dictionary
        set_button = ttk.Button(self.gps_frame, text="Set GPS values", padding=(4, 4), command=self.set_values_gps)
        set_button.pack(pady=(20,5), side=tk.TOP)


    def build_bar_panel(self):
        """
        Function to build the widgets into the barometer panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.bar_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.bar_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the Gaussian noise
        self.entry_noise_bar_z = self.add_configurable_input(noise_frame_,'     Noise','[hPa]', '#0000B0')

        # Create a subframe for constant bias
        bias_label_ = ttk.Label(self.bar_frame, text="Constant bias")
        bias_label_.pack(side=tk.TOP, pady=(20,2))
        bias_frame_ = ttk.Frame(self.bar_frame)
        bias_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append entry boxes for the Gaussian noise
        self.entry_bias_bar_z = self.add_configurable_input(bias_frame_,'       Bias','[hPa]', '#0000B0')
        
        # Add button to apply the barometer values on the gui to the data dictionary
        set_button = ttk.Button(self.bar_frame, text="Set bar values", padding=(4, 4), command=self.set_values_bar)
        set_button.pack(pady=(20,5), side=tk.TOP)


    def add_configurable_input(self,frame,text,units,color):
        """
        Function add a entry box with labels for name and unit

        Parameters:
            frame (tkinter.ttk.Frame): Subframe in which the entry box will be added
            text (str): Label for the configurable parameter
            units (str): Measurement unit for the parameter

        Returns:
            entry (tkinter.ttk.Entry): Object for the created entry box
        """

        # Get the current number of rows in the grid
        num_rows = frame.grid_size()[1]

        # Create a label for the configuration
        label = ttk.Label(frame, text=text, foreground=color)
        label.grid(row=num_rows, column=0, padx=(1,1))
        # Create a entry box
        entry = ttk.Entry(frame, width=15)
        entry.grid(row=num_rows, column=1)
        # Create a label for the units
        unit_label = ttk.Label(frame, text=units)
        unit_label.grid(row=num_rows, column=2)

        # Bind the set function to the the enter key
        entry.bind("<Return>", lambda event=None: self.set_values())

        return entry


    def set_values_acc(self):
        """
        Function to set the values inserted in the accelerometer panel to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return
        
        # Read the values on the gui and update the data dictionary
        # Gaussian noise
        self.data["SENS_ACC_STD_X"]['value'] = float(self.entry_noise_acc_x.get())
        self.data["SENS_ACC_STD_Y"]['value'] = float(self.entry_noise_acc_y.get())
        self.data["SENS_ACC_STD_Z"]['value'] = float(self.entry_noise_acc_z.get())
        # Bias
        self.data["SENS_ACC_BIAS_X"]['value'] = float(self.entry_bias_acc_x.get())
        self.data["SENS_ACC_BIAS_Y"]['value'] = float(self.entry_bias_acc_y.get())
        self.data["SENS_ACC_BIAS_Z"]['value'] = float(self.entry_bias_acc_z.get())
        # Vibration coupling
        self.data["SENS_ACC_VIB_X"]['value'] = float(self.entry_vib_acc_x.get())
        self.data["SENS_ACC_VIB_Y"]['value'] = float(self.entry_vib_acc_y.get())
        self.data["SENS_ACC_VIB_Z"]['value'] = float(self.entry_vib_acc_z.get())


    def set_values_gyro(self):
        """
        Function to set the values inserted in the gyro panel to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return
        
        # Read the values on the gui and update the data dictionary
        # Gaussian noise
        self.data["SENS_GYRO_STD_X"]['value'] = float(self.entry_noise_gyro_x.get())
        self.data["SENS_GYRO_STD_Y"]['value'] = float(self.entry_noise_gyro_y.get())
        self.data["SENS_GYRO_STD_Z"]['value'] = float(self.entry_noise_gyro_z.get())
        # Bias
        self.data["SENS_GYRO_BIAS_X"]['value'] = float(self.entry_bias_gyro_x.get())
        self.data["SENS_GYRO_BIAS_Y"]['value'] = float(self.entry_bias_gyro_y.get())
        self.data["SENS_GYRO_BIAS_Z"]['value'] = float(self.entry_bias_gyro_z.get())
        # Vibration coupling
        self.data["SENS_GYRO_VIB_X"]['value'] = float(self.entry_vib_gyro_x.get())
        self.data["SENS_GYRO_VIB_Y"]['value'] = float(self.entry_vib_gyro_y.get())
        self.data["SENS_GYRO_VIB_Z"]['value'] = float(self.entry_vib_gyro_z.get())


    def set_values_mag(self):
        """
        Function to set the values inserted in the magnetometer panel to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return
        
        # Read the values on the gui and update the data dictionary
        # Gaussian noise
        self.data["SENS_MAG_STD_X"]['value'] = float(self.entry_noise_mag_x.get())
        self.data["SENS_MAG_STD_Y"]['value'] = float(self.entry_noise_mag_y.get())
        self.data["SENS_MAG_STD_Z"]['value'] = float(self.entry_noise_mag_z.get())
        # Bias
        self.data["SENS_MAG_BIAS_X"]['value'] = float(self.entry_bias_mag_x.get())
        self.data["SENS_MAG_BIAS_Y"]['value'] = float(self.entry_bias_mag_y.get())
        self.data["SENS_MAG_BIAS_Z"]['value'] = float(self.entry_bias_mag_z.get())
        # Interference coupling
        self.data["SENS_MAG_INTF_X"]['value'] = float(self.entry_intf_mag_x.get())
        self.data["SENS_MAG_INTF_Y"]['value'] = float(self.entry_intf_mag_y.get())
        self.data["SENS_MAG_INTF_Z"]['value'] = float(self.entry_intf_mag_z.get())


    def set_values_gps(self):
        """
        Function to set the values inserted in the GPS panel to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return
        
        # Read the values on the gui and update the data dictionary
        # Gaussian noise
        self.data["SENS_GPS_STD_XY"]['value'] = float(self.entry_noise_gps_xy.get())
        self.data["SENS_GPS_STD_Z"]['value'] = float(self.entry_noise_gps_z.get())


    def set_values_bar(self):
        """
        Function to set the values inserted in the barometer panel to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return
        
        # Read the values on the gui and update the data dictionary
        # Gaussian noise
        self.data["SENS_BAR_STD"]['value'] = float(self.entry_noise_bar_z.get())
        # Bias noise
        self.data["SENS_BAR_BIAS"]['value'] = float(self.entry_bias_bar_z.get())


    def set_values(self):
        """
        Function to set all the values inserted in the gui to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return

        # Set the values of all sensors
        self.set_values_acc()
        self.set_values_gyro()
        self.set_values_mag()
        self.set_values_gps()
        self.set_values_bar()


    def update_single_field(self,entry,param):
        """
        Function to update the data displayed on a single entry box

        Parameters:
            entry (tkinter.ttk.Entry): Entry box object that will have the value updated
            param (srt): Name of the parameter whose value will be inserted
        """

        # Clear the old value
        entry.delete(0, tk.END)
        # insert the new value
        entry.insert(0, str(self.data[param]['value']))


    def update_displayed_data(self, *args):
        """
        Function to update the data displayed on the gui

        Parameters:
            *args (list): Unused arguments passed by the function when it is binded to a widget action.
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            return
        
        # Update the data on the accelerometer frame
        # Gaussian noise
        self.update_single_field(self.entry_noise_acc_x, 'SENS_ACC_STD_X')
        self.update_single_field(self.entry_noise_acc_y, 'SENS_ACC_STD_Y')
        self.update_single_field(self.entry_noise_acc_z, 'SENS_ACC_STD_Z')
        # Bias
        self.update_single_field(self.entry_bias_acc_x, 'SENS_ACC_BIAS_X')
        self.update_single_field(self.entry_bias_acc_y, 'SENS_ACC_BIAS_Y')
        self.update_single_field(self.entry_bias_acc_z, 'SENS_ACC_BIAS_Z')
        # Vibration coupling
        self.update_single_field(self.entry_vib_acc_x, 'SENS_ACC_VIB_X')
        self.update_single_field(self.entry_vib_acc_y, 'SENS_ACC_VIB_Y')
        self.update_single_field(self.entry_vib_acc_z, 'SENS_ACC_VIB_Z')

        # Update the data on the gyro frame
        # Gaussian noise
        self.update_single_field(self.entry_noise_gyro_x, 'SENS_GYRO_STD_X')
        self.update_single_field(self.entry_noise_gyro_y, 'SENS_GYRO_STD_Y')
        self.update_single_field(self.entry_noise_gyro_z, 'SENS_GYRO_STD_Z')
        # Bias
        self.update_single_field(self.entry_bias_gyro_x, 'SENS_GYRO_BIAS_X')
        self.update_single_field(self.entry_bias_gyro_y, 'SENS_GYRO_BIAS_Y')
        self.update_single_field(self.entry_bias_gyro_z, 'SENS_GYRO_BIAS_Z')
        # Vibration coupling
        self.update_single_field(self.entry_vib_gyro_x, 'SENS_GYRO_VIB_X')
        self.update_single_field(self.entry_vib_gyro_y, 'SENS_GYRO_VIB_Y')
        self.update_single_field(self.entry_vib_gyro_z, 'SENS_GYRO_VIB_Z')

        # Update the data on the magnetometer frame
        # Gaussian noise
        self.update_single_field(self.entry_noise_mag_x, 'SENS_MAG_STD_X')
        self.update_single_field(self.entry_noise_mag_y, 'SENS_MAG_STD_Y')
        self.update_single_field(self.entry_noise_mag_z, 'SENS_MAG_STD_Z')
        # Bias
        self.update_single_field(self.entry_bias_mag_x, 'SENS_MAG_BIAS_X')
        self.update_single_field(self.entry_bias_mag_y, 'SENS_MAG_BIAS_Y')
        self.update_single_field(self.entry_bias_mag_z, 'SENS_MAG_BIAS_Z')
        # Vibration coupling
        self.update_single_field(self.entry_intf_mag_x, 'SENS_MAG_INTF_X')
        self.update_single_field(self.entry_intf_mag_y, 'SENS_MAG_INTF_Y')
        self.update_single_field(self.entry_intf_mag_z, 'SENS_MAG_INTF_Z')

        # Update the data on the GPS frame
        # Gaussian noise
        self.update_single_field(self.entry_noise_gps_xy, 'SENS_GPS_STD_XY')
        self.update_single_field(self.entry_noise_gps_z, 'SENS_GPS_STD_Z')

        # Update the data on the Barometer frame
        # Gaussian noise
        self.update_single_field(self.entry_noise_bar_z, 'SENS_BAR_STD')
        # Bias
        self.update_single_field(self.entry_bias_bar_z, 'SENS_BAR_BIAS')


    def saveas_json(self):
        """
        Function to save the current set os parameters as a new file
        """

        # Open a file dialog to select a path ans set a name for the new file to be saved
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        # If a path and a name were provided
        if path:
            # Set the new path
            self.file_path = path
            # Save current set of parameters as a JSON file
            self.save_json()


    def save_json(self):
        """
        Function to dump the current set os parameters to the origin JSON file
        """

        try:
            # If path is set
            if self.file_path:
                # Open the file
                with open(self.file_path, "w") as json_file:
                    # Dump the parameters data to the file
                    json.dump(self.data, json_file, indent=4)
        except:
            # Throw an error message there was a problem in saving the file
            messagebox.showerror("Error", "A problem ocurred when saving the file")


    def load_json(self):
        """
        Function to show a file dialog to load a json file
        """
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            with open(self.file_path, "r") as json_file:
                self.data = json.load(json_file)
            
            self.update_displayed_data()


    def on_closing(self):
        """
        Function to handle action when window is closed
        """
        # Close window
        self.root.quit()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.destroy()


    def set_data(self, d, path):
        """
        Set data dictionary and the file path of the gui

        Parameters:
            d (dict): Updated dictionary with the parameters data edited in other guis
            path (str): path for the json file that stores the parameters
        """
        # Set data dictionary and file path
        self.data = d
        self.file_path = path

        # Update the gui with the new data
        self.update_displayed_data()


    def get_data(self):
        """
        Return the current data dictionary that the gui is using

        Return:
            self.data (dict): Dictionary with the parameters data edited on the gui
        """
        return self.data


    def viz_return(self):
        """
        Function to update the visualization of the gui
        """
        # Just call the update_displayed_data() function
        self.update_displayed_data()


    def viz_exit(self):
        """
        Function to clean up gui when its tab is switched off
        """
        return

 
if __name__ == "__main__":
    """
    Main to run a detached SensorsEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Sensors configuration")
    # Define GUI window size
    root.geometry('1200x600')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/sensors_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = SensorsEditorGUI(root, True)

    # Call the function to terminate the matplotlib.pyplot when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

