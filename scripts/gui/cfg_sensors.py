#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to configure the sensors properties

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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

        # Define a gyro panel
        self.gyro_frame = ttk.Frame(self.root)
        self.gyro_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the gyro panel
        self.name_gyro_label = ttk.Label(self.gyro_frame, text="Gyro")
        self.name_gyro_label.pack(side=tk.TOP, pady=2)

        # Define a accelerometer panel
        self.acc_frame = ttk.Frame(self.root)
        self.acc_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the accelerometer panel
        self.name_acc_label = ttk.Label(self.acc_frame, text="Accelerometer")
        self.name_acc_label.pack(side=tk.TOP, pady=2)

        # Define a magnetometer panel
        self.mag_frame = ttk.Frame(self.root)
        self.mag_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the accelerometer panel
        self.name_mag_label = ttk.Label(self.mag_frame, text="Magnetometer")
        self.name_mag_label.pack(side=tk.TOP, pady=2)

        # Define a panel for GPS and barometer
        gps_bar_frame = ttk.Frame(self.root)
        gps_bar_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Define a magnetometer panel
        self.gps_frame = ttk.Frame(gps_bar_frame)
        self.gps_frame.pack(side=tk.TOP, fill="both", expand=True)
        # Add a title for the accelerometer panel
        self.name_gps_label = ttk.Label(self.gps_frame, text="GPS")
        self.name_gps_label.pack(side=tk.TOP, pady=2)
        # Define a magnetometer panel
        self.bar_frame = ttk.Frame(gps_bar_frame)
        self.bar_frame.pack(side=tk.TOP, fill="both", expand=True)
        # Add a title for the accelerometer panel
        self.name_bar_label = ttk.Label(self.bar_frame, text="Barometer")
        self.name_bar_label.pack(side=tk.TOP, pady=(20,0))



        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}

        # # Build the left and right panels
        # self.build_left_panel()
        # self.build_right_panel()

        self.build_gyro_panel()
        self.build_acc_panel()
        self.build_mag_panel()
        self.build_gps_panel()
        self.build_bar_panel()



    def build_gyro_panel(self):
        """
        Function to build the widgets into the gyro panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.gyro_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.gyro_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_noise_gyro_x = self.add_configurable_input(noise_frame_,'     Noise x','[rad/s]')
        self.combo_noise_gyro_y = self.add_configurable_input(noise_frame_,'     Noise y','[rad/s]')
        self.combo_noise_gyro_z = self.add_configurable_input(noise_frame_,'     Noise z','[rad/s]')

        # Create a subframe for constant bias
        bias_label_ = ttk.Label(self.gyro_frame, text="Constant bias")
        bias_label_.pack(side=tk.TOP, pady=(20,2))
        bias_frame_ = ttk.Frame(self.gyro_frame)
        bias_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_bias_gyro_x = self.add_configurable_input(bias_frame_,'       Bias x','[rad/s]')
        self.combo_bias_gyro_y = self.add_configurable_input(bias_frame_,'       Bias y','[rad/s]')
        self.combo_bias_gyro_z = self.add_configurable_input(bias_frame_,'       Bias z','[rad/s]')

        # Create a subframe for vibration coupling
        vib_label_ = ttk.Label(self.gyro_frame, text="Vibration coupling")
        vib_label_.pack(side=tk.TOP, pady=(20,2))
        vib_frame_ = ttk.Frame(self.gyro_frame)
        vib_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_vib_gyro_x = self.add_configurable_input(vib_frame_,'Vibration x','[rad/s]')
        self.combo_vib_gyro_y = self.add_configurable_input(vib_frame_,'Vibration y','[rad/s]')
        self.combo_vib_gyro_z = self.add_configurable_input(vib_frame_,'Vibration z','[rad/s]')

        # # Add button to apply the estimated coefficients to the current actuator
        # self.set_button = ttk.Button(self.left_frame, text="Set values", padding=(4, 4), command=self.set_values)
        # self.set_button.pack(pady=2, side=tk.TOP)


    def build_acc_panel(self):
        """
        Function to build the widgets into the acc panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.acc_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.acc_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_noise_acc_x = self.add_configurable_input(noise_frame_,'     Noise x','[m/s²]')
        self.combo_noise_acc_y = self.add_configurable_input(noise_frame_,'     Noise y','[m/s²]')
        self.combo_noise_acc_z = self.add_configurable_input(noise_frame_,'     Noise z','[m/s²]')

        todo = ttk.Label(self.acc_frame, text="Add bias\n\nAdd vibration coupling")
        todo.pack(side=tk.TOP, pady=(20,2))

    def build_mag_panel(self):
        """
        Function to build the widgets into the acc panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.mag_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.mag_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_noise_mag_x = self.add_configurable_input(noise_frame_,'     Noise x','[G]')
        self.combo_noise_mag_y = self.add_configurable_input(noise_frame_,'     Noise y','[G]')
        self.combo_noise_mag_z = self.add_configurable_input(noise_frame_,'     Noise z','[G]')

        todo = ttk.Label(self.mag_frame, text="Add bias\n\nAdd interference coupling")
        todo.pack(side=tk.TOP, pady=(20,2))

    def build_gps_panel(self):
        """
        Function to build the widgets into the acc panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.gps_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.gps_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_noise_gps_x = self.add_configurable_input(noise_frame_,'     Noise x','[m]')
        self.combo_noise_gps_y = self.add_configurable_input(noise_frame_,'     Noise y','[m]')
        self.combo_noise_gpx_z = self.add_configurable_input(noise_frame_,'     Noise z','[m]')


    def build_bar_panel(self):
        """
        Function to build the widgets into the acc panel
        """

        # Create a subframe for Gaussian noise
        noise_label_ = ttk.Label(self.bar_frame, text="   Gaussian noise\nstandard deviation")
        noise_label_.pack(side=tk.TOP, pady=(20,2))
        noise_frame_ = ttk.Frame(self.bar_frame)
        noise_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_noise_bar_z = self.add_configurable_input(noise_frame_,'     Noise x','[m]')

        # Create a subframe for constant bias
        bias_label_ = ttk.Label(self.bar_frame, text="Constant bias")
        bias_label_.pack(side=tk.TOP, pady=(20,2))
        bias_frame_ = ttk.Frame(self.bar_frame)
        bias_frame_.pack(side=tk.TOP, pady=(4,4), padx=(4,4))
        # Append combo boxes for the Gaussian noise
        self.combo_bias_bar_z = self.add_configurable_input(bias_frame_,'       Bias z','[m]')

    def add_configurable_input(self,frame,text,units):
        """
        Function to build the widgets into the left panel

        Parameters:
            frame (tkinter.ttk.Frame): Subframe in which the combobox will be added
            text (str): Label for the configurable parameter
            units (str): Measurement unit for the parameter

        Returns:
            combo (tkinter.ttk.Combobox): Object for the created combobox
        """

        num_rows = frame.grid_size()[1]

        # Create a label for the configuration
        label = ttk.Label(frame, text=text)
        label.grid(row=num_rows, column=0)
        # Create a combobox entry
        combo = ttk.Combobox(frame, values=[], width=15)
        combo.grid(row=num_rows, column=1)
        # Create a label for the units
        unit_label = ttk.Label(frame, text=units)
        unit_label.grid(row=num_rows, column=2)

        # Bind the set function to the the enter key
        combo.bind("<Return>", lambda event=None: self.set_values())

        return combo


    def build_left_panel(self):
        """
        Function to build the widgets into the left panel
        """

        # Create a subframe for Gaussian noise
        power_label = ttk.Label(self.left_frame, text="Power configuration")
        power_label.pack(side=tk.TOP, pady=(20,2))
        power_frame = ttk.Frame(self.left_frame)
        power_frame.pack(side=tk.TOP, pady=(2,20))
        # Append combo boxes for the Gaussian noise
        self.combo_idle_curr = self.add_configurable_input(power_frame,'Idle current','[A]')
        self.combo_pwr_eff = self.add_configurable_input(power_frame,'Power efficiency','[%]')

        # Create a subframe for battery properties
        battery_label = ttk.Label(self.left_frame, text="Battery configuration")
        battery_label.pack(side=tk.TOP, pady=(20,2))
        battery_frame = ttk.Frame(self.left_frame)
        battery_frame.pack(side=tk.TOP, pady=(2,20))
        # Append combo boxes for the battery configuration
        self.combo_n_cells = self.add_configurable_input(battery_frame,'Number of cells','[ ]')
        self.combo_mAh = self.add_configurable_input(battery_frame,'Full capacity','[mAh]')
        self.combo_init_charge = self.add_configurable_input(battery_frame,'Initial charge','[%]')
        self.combo_internal_R = self.add_configurable_input(battery_frame,'Internal resistance','[Ohms]')

        # Add button to apply the estimated coefficients to the current actuator
        self.set_button = ttk.Button(self.left_frame, text="Set values", padding=(4, 4), command=self.set_values)
        self.set_button.pack(pady=2, side=tk.TOP)


    def build_right_panel(self):
        """
        Function to build the widgets into the right panel
        """

        # Create a pyplot figure with 2 subplots
        self.fig, self.axs = plt.subplots(2,1)
        # Increase the space between the two plots
        plt.subplots_adjust(hspace=0.5)

        # Create a canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # Update the plot
        self.canvas.draw()
        # Attach the plot to the right_frame
        self.canvas.get_tk_widget().pack()


    def set_values(self):
        """
        Function to set the values inserted in the gui to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return

        # Read the values on the gui and update the data dictionary
        self.data["PWR_IDLE_CURRENT"]['value'] = float(self.combo_idle_curr.get())
        self.data["PWR_EFF"]['value'] = int(self.combo_pwr_eff.get())
        self.data["BAT_N_CELLS"]['value'] = int(self.combo_n_cells.get())
        self.data["BAT_FULL_CHARGE"]['value'] = int(self.combo_mAh.get())
        self.data["BAT_INIT_CHARGE"]['value'] = int(self.combo_init_charge.get())
        self.data["BAT_INTERNAL_RES"]['value'] = float(self.combo_internal_R.get())

        # Update displayed data
        self.update_displayed_data()


    def update_single_field(self,combo,param):
        """
        Function to update the data displayed on a single combo box

        Parameters:
            combo (tkinter.ttk.Combobox): Combobox object that will have the value updated
            param (srt): Name of the parameter whose value will be inserted
        """

        # Clear the old value
        combo.delete(0, tk.END)
        # insert the new value
        combo.insert(0, str(self.data[param]['value']))
        # Update the available options
        combo['values'] = self.data[param]['options']


    def update_displayed_data(self, *args):
        """
        Function to update the data displayed on the gui

        Parameters:
            *args (list): Unused arguments passed by the function when it is binded to a widget action.
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            return

        # Update the data on the combo boxes
        self.update_single_field(self.combo_idle_curr, 'PWR_IDLE_CURRENT')
        self.update_single_field(self.combo_pwr_eff, 'PWR_EFF')
        self.update_single_field(self.combo_n_cells, 'BAT_N_CELLS')
        self.update_single_field(self.combo_mAh, 'BAT_FULL_CHARGE')
        self.update_single_field(self.combo_init_charge, 'BAT_INIT_CHARGE')
        self.update_single_field(self.combo_internal_R, 'BAT_INTERNAL_RES')



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
        # Close matplotlib.pyplot to avoid gui to keep alive after it is closed
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

