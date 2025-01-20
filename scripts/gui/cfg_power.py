#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to configure the electrical power properties

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sim4cd.polynomial as POLY

class PowerEditorGUI:
    """
    Class that defines a GUI for configuring the power and battery properties
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the PowerEditorGUI class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
            enable_io_ (bool): Flag to enable the creation of input/output buttons to the gui
        """

        # Set the root variable
        self.root = root_

        # Set the io_enabled variable
        self.io_enabled = enable_io_

        # Define a left panel
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=False, padx=(4,4))
        # Add a title for the left panel
        self.name_l_label = ttk.Label(self.left_frame, text="Electrical power configuration")
        self.name_l_label.pack(padx=5)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(4,4))
        # Add a title for the right panel
        self.name_r_label = ttk.Label(self.right_frame, text="Curve models")
        self.name_r_label.pack(padx=5)

        if(self.io_enabled):
            # Create buttons to load and save file
            buttons_frame = ttk.Frame(self.left_frame)
            buttons_frame.pack(side=tk.TOP, padx=10)
            # Button to load file
            self.load_button = ttk.Button(buttons_frame, text="    Load", padding=(4, 4), command=self.load_json)
            self.load_button.pack(pady=10, side=tk.LEFT)
            # Button to save file
            self.save_button = ttk.Button(buttons_frame, text="    Save", padding=(4, 4), command=self.save_json)
            self.save_button.pack(pady=10, side=tk.LEFT)
            # Button to save file as
            self.saveas_button = ttk.Button(buttons_frame, text="  Save As", padding=(4, 4), command=self.saveas_json)
            self.saveas_button.pack(pady=10, side=tk.LEFT)

        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}

        # Parameter of the polynomial that maps the SOC (State Of Charge) to a single LiPo cell voltage
        # Based on data available at: Gandolfo, Daniel, et al. "Dynamic model of lithium polymer battery–load resistor method for electric parameters identification." Journal of the Energy Institute 88.4 (2015): 470-479.
        volt_constants = [2.5881836050934073, 19.977045504620776, -140.6535733701412, 515.4239704625197, -1057.4258331010678, 1226.7602703659068, -750.1861137479827, 187.73276915201495]
        # Define a polynomial to compute the LiPo cell voltage
        self.poly_cell_voltage = POLY.polynomial(volt_constants)

        # Build the left and right panels
        self.build_left_panel()
        self.build_right_panel()

        # Update the plot for the cell/battery voltage
        self.plot_voltage()


    def add_configurable_input(self,frame,text,units):
        """
        Function add a combo box with labels for name and unit

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
        combo = ttk.Combobox(frame, values=[])
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

        # Create a subframe for power properties
        power_label = ttk.Label(self.left_frame, text="Power configuration")
        power_label.pack(side=tk.TOP, pady=(20,2))
        power_frame = ttk.Frame(self.left_frame)
        power_frame.pack(side=tk.TOP, pady=(2,20))
        # Append combo boxes for the power configuration
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

        # Update the plot of the voltages
        self.plot_voltage()


    def plot_voltage(self):
        """
        Function to plot a polynomial representing the cell and battery voltage on the right pane.
        """

        # Compute the vector of state of charge from 0 to 1
        soc = [i/100 for i in range(101)]
        vdata = []
        # Evaluate the polynomial representing cell voltage
        for x in soc:
            vdata.append(self.poly_cell_voltage.eval(x))

        # Plot the curve of a single cell on the top of the right panel
        self.axs[0].clear() # clear
        self.axs[0].plot([i*100 for i in soc], vdata, linewidth=2, color='blue') # plot
        self.axs[0].grid(True) # enable grid
        self.axs[0].set_xlabel('State of charge [%]') # set x axis name
        self.axs[0].set_ylabel('Voltage [V]') # set y axis name
        self.axs[0].set_title('Single cell voltage') # set title
        
        # Show the plot and proceed
        self.canvas.draw()

        # Return if there if not parameter file loaded (necessary for the number of cells)
        if(not self.file_path):
            return

        n_cells = int(self.combo_n_cells.get())
        # Plot the curve of the battery on the bottom of the right panel
        self.axs[1].clear() # clear
        self.axs[1].plot([i*100 for i in soc], [v*n_cells for v in vdata], linewidth=2, color='blue') # plot
        self.axs[1].grid(True) # enable grid
        self.axs[1].set_xlabel('State of charge [%]') # set x axis name
        self.axs[1].set_ylabel('Voltage [V]') # set y axis name
        self.axs[1].set_title('Battery voltage') # set title
        
        # Show the plot and proceed
        self.canvas.draw()


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
        plt.close()

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
    Main to run a detached PowerEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Power configuration")
    # Define GUI window size
    root.geometry('1200x600')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/power_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = PowerEditorGUI(root, True)

    # Call the function to terminate the matplotlib.pyplot when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

