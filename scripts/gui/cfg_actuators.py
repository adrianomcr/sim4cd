#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to configure the actuator properties

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
from fnmatch import fnmatch
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gui.poly_estimator as PEST
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sim4cd.polynomial as POLY

class ActuatorsEditorGUI:
    """
    Class that defines a GUI for configuring the actuators properties
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the ActuatorsEditorGUI class

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
        self.name_l_label = ttk.Label(self.left_frame, text="Actuator configuration")
        self.name_l_label.pack(padx=5)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(4,4))
        # Add a title for the right panel
        self.name_r_label = ttk.Label(self.right_frame, text="Curve model")
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

        # Define a dictionarry with generic information to build the gui
        self.poly_param_names = {
            'Voltage to speed'  : { 'name':'VOLT2SPEED'  , 'xdata':'voltage', 'xl':'Voltage [V]'  , 'yl':'Speed [rad/s]'},
            'Speed to thrust'   : { 'name':'SPEED2THRUST', 'xdata':'speed'  , 'xl':'Speed [rad/s]', 'yl':'Force [N]'    },
            'Speed to torque'   : { 'name':'SPEED2TORQUE', 'xdata':'speed'  , 'xl':'Speed [rad/s]', 'yl':'Torque [Nm]'  },
            'Torque to current' : { 'name':'TORQUE2AMPS' , 'xdata':'torque' , 'xl':'Torque [Nm]'  , 'yl':'Current [A]'  }
        }

        # Build the left and right panels
        self.build_left_panel()
        self.build_right_panel()


    def build_left_panel(self):
        """
        Function to build the widgets into the left panel
        """

        # Define the options for the actuators ids if this information is available
        if (self.data):
            actuator_options = [f'Actuator {i}' for i in range(self.data['VEH_ACT_NUM']['value'])]
        else:
            actuator_options = []

        # Create a subframe to select the id of the actuator to be configured
        act_select_frame = ttk.Frame(self.left_frame)
        act_select_frame.pack(side=tk.TOP, pady=5)
        # Add a label for the actuator id selector
        act_select_label = ttk.Label(act_select_frame, text="Actuator number")
        act_select_label.pack(side=tk.LEFT,padx=5)
        # Add a dropdown to select among the possible actuator ids
        self.act_id_var = tk.StringVar()
        self.actuator_menu = ttk.OptionMenu(act_select_frame, self.act_id_var, None, *actuator_options)
        self.actuator_menu.pack(side=tk.LEFT, padx=10)
        # Bind the function to update the data displayed in the gui
        self.act_id_var.trace("w", self.update_displayed_data)

        # Create a subframe for some actuators simple properties
        act_features_frame = ttk.Frame(self.left_frame)
        act_features_frame.pack(side=tk.TOP, pady=5)
        # Add label and entry box for actuators time constant
        act_tcte_label = ttk.Label(act_features_frame, text="Time constant")
        act_tcte_label.grid(row=0, column=0)
        self.combo_tcte = ttk.Combobox(act_features_frame, values=[])
        self.combo_tcte.grid(row=0, column=1)
        # Add label and entry box for actuators moment of inertia
        act_moi_label = ttk.Label(act_features_frame, text="Moment of inertia")
        act_moi_label.grid(row=1, column=0)
        self.combo_moi = ttk.Combobox(act_features_frame, values=[])
        self.combo_moi.grid(row=1, column=1)
        # Add label and entry box for actuators spin directions
        act_spin_label = ttk.Label(act_features_frame, text="Spin direction")
        act_spin_label.grid(row=2, column=0)
        self.combo_spin = ttk.Combobox(act_features_frame, values=[])
        self.combo_spin.grid(row=2, column=1)

        # Create a subframe to select the curve displayed in the plot
        act_curve_frame = ttk.Frame(self.left_frame)
        act_curve_frame.pack(side=tk.TOP, pady=(15,3))
        # Add a label for the curve selector
        act_curve_label = ttk.Label(act_curve_frame, text="Curve")
        act_curve_label.pack(side=tk.LEFT,padx=5)
        # Add a dropdown to select among the possible actuator ids
        curve_options = self.poly_param_names.keys()
        self.act_curve_var = tk.StringVar()
        self.curve_menu = ttk.OptionMenu(act_curve_frame, self.act_curve_var, None, *curve_options)
        self.curve_menu.pack(side=tk.TOP, padx=10)
        # Bind the function to update the data displayed in the gui
        self.act_curve_var.trace("w", self.update_displayed_data)

        # Subframe for actuator simple configurations
        act_poly_frame = ttk.Frame(self.left_frame)
        act_poly_frame.pack(side=tk.TOP, pady=5)
        poly_label = ttk.Label(act_poly_frame, text="p(u) = ")
        poly_label.grid(row=0, column=0)
        # Actuator polynomial coefficient for order 0
        self.entry_poly_0 = ttk.Entry(act_poly_frame,width=11)
        self.entry_poly_0.grid(row=0, column=1)
        poly_label_0 = ttk.Label(act_poly_frame, text="  ")
        poly_label_0.grid(row=0, column=2)
        # Actuator polynomial coefficient for order 0
        self.entry_poly_1 = ttk.Entry(act_poly_frame,width=11)
        self.entry_poly_1.grid(row=0, column=3)
        poly_label_1 = ttk.Label(act_poly_frame, text="u ")
        poly_label_1.grid(row=0, column=4)
        # Actuator polynomial coefficient for order 0
        self.entry_poly_2 = ttk.Entry(act_poly_frame,width=11)
        self.entry_poly_2.grid(row=0, column=5)
        poly_label_2 = ttk.Label(act_poly_frame, text="u²")
        poly_label_2.grid(row=0, column=6)

        # Add button to set the estimated coefficients to the current actuator configuration parameters
        self.set_button = ttk.Button(self.left_frame, text="Set values", padding=(4, 4), command=self.set_values)
        self.set_button.pack(pady=2, side=tk.TOP)

        # Add button to apply the estimated coefficients and see the plot
        self.apply_est_button = ttk.Button(self.left_frame, text="Apply estimated coefficients", padding=(4, 4), command=self.apply_coefs)
        self.apply_est_button.pack(pady=5, side=tk.BOTTOM)

        # Add polynomial estimator GUI
        estimator_frame = ttk.Frame(self.left_frame)
        estimator_frame.pack(side=tk.BOTTOM)
        self.poly_est_gui = PEST.PolyEstimatorGUI(estimator_frame)


    def build_right_panel(self):
        """
        Function to build the widgets into the right panel
        """

        # Create a pyplot figure
        self.fig, self.axs = plt.subplots(1,1)

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

        # Return if there is no actuator selected
        if(not self.act_id_var.get()):
            messagebox.showerror("Error", "Select an actuator id")
            return

        # Get the actuator id
        act_id = self.act_id_var.get().split()[-1]

        # Set simple properties
        self.data[f"ACT{act_id}_TIME_CTE"]['value'] = float(self.combo_tcte.get())
        self.data[f"ACT{act_id}_MOI_ROTOR"]['value'] = float(self.combo_moi.get())
        self.data[f"ACT{act_id}_SPIN"]['value'] = int(self.combo_spin.get())

        # Return if there not curve selected
        if(not self.act_curve_var.get()):
            return

        # Get the selected curve
        poly_param_name_ = self.poly_param_names[self.act_curve_var.get()]['name']
        # Compute the full name of the coefficient parameters
        poly_coef_names_ = [f"ACT{act_id}_"+poly_param_name_+f"_{i}" for i in range(3)]

        # Set coefficient parameters
        self.data[poly_coef_names_[0]]['value'] = float(self.entry_poly_0.get())
        self.data[poly_coef_names_[1]]['value'] = float(self.entry_poly_1.get())
        self.data[poly_coef_names_[2]]['value'] = float(self.entry_poly_2.get())

        # Update displayed data
        self.update_displayed_data()


    def format_as_scientific(self,value):
        """
        Function to define a string equivalent to a float in the scientific notation

        Parameters:
            value (float): Float value to be converted to a string

        Return:
            formatted_value (string): String with the input float in the scientific notation
        """
        formatted_value = "{:.5e}".format(value)
        formatted_value = formatted_value.replace('+0','+')
        formatted_value = formatted_value.replace('-0','-')
        formatted_value = formatted_value.replace('e+0','')
        return formatted_value


    def apply_coefs(self):
        """
        Function to apply the estimated coefficients to the coefficient entry boxes
        """

        if (not self.poly_est_gui.has_coefs()):
            # Display a message and return if there is not polynomial estimation
            messagebox.showerror("Error", "There is no available estimation")
            return
        elif(not self.act_id_var.get() and not self.act_curve_var.get()):
            # Display a message and return if actuator id and curve are not selected
            messagebox.showerror("Error", "Select an actuator id and a curve")
            return
        elif(not self.act_id_var.get()):
            # Display a message and return if actuator id is not selected
            messagebox.showerror("Error", "Select an actuator id")
            return
        elif(not self.act_curve_var.get()):
            # Display a message and return if curve is not selected
            messagebox.showerror("Error", "Select a curve")
            return

        # Get coefficients from the polynomial estimation gui
        C_ = self.poly_est_gui.get_coefs()

        # Set the coefficient for order 0
        self.entry_poly_0.delete(0, tk.END)
        self.entry_poly_0.insert(0, self.format_as_scientific(C_[0]))
        # Set the coefficient for order 1
        self.entry_poly_1.delete(0, tk.END)
        self.entry_poly_1.insert(0, self.format_as_scientific(C_[1]))
        # Set the coefficient for order 2
        self.entry_poly_2.delete(0, tk.END)
        self.entry_poly_2.insert(0, self.format_as_scientific(C_[2]))

        # Update the plot with the new polynomial
        self.plot_poly()


    def replicate_config(self):
        """
        Function to replicate the configuration of the selected actuator to the other actuators
        """
        # TODO
        return


    def update_displayed_data(self, *args):
        """
        Function to update the data displayed on the gui

        Parameters:
            *args (list): Unused arguments passed by the function when it is binded to a widget action.
        """

        # Update the possible ids of the actuators
        self.update_actuator_options()

        # Return it there is no actuator selected
        if(not self.act_id_var.get()):
            return

        # Get selected actuator id
        act_id = self.act_id_var.get().split()[-1]

        # Update the value of actuator time constant
        self.combo_tcte.delete(0, tk.END)
        self.combo_tcte.insert(0, str(self.data[f"ACT{act_id}_TIME_CTE"]['value']))
        self.combo_tcte['values'] = self.data[f"ACT{act_id}_TIME_CTE"]['options']
        # Update the value of actuator moment of inertia
        self.combo_moi.delete(0, tk.END)
        self.combo_moi.insert(0, str(self.data[f"ACT{act_id}_MOI_ROTOR"]['value']))
        self.combo_moi['values'] = self.data[f"ACT{act_id}_MOI_ROTOR"]['options']
        # Update the value of actuator spin
        self.combo_spin.delete(0, tk.END)
        self.combo_spin.insert(0, str(int(self.data[f"ACT{act_id}_SPIN"]['value'])))
        self.combo_spin['values'] = self.data[f"ACT{act_id}_SPIN"]['options']

        # Return it there is no curve selected
        if(not self.act_curve_var.get()):
            return
        
        # Get the selected curve
        poly_param_name_ = self.poly_param_names[self.act_curve_var.get()]['name']
        # Compute the full name of the coefficient parameters
        poly_coef_names_ = [f"ACT{act_id}_"+poly_param_name_+f"_{i}" for i in range(3)]
        # Cet the coefficient parameters
        poly_coefs_ = [self.data[s]['value'] for s in poly_coef_names_]

        # Get the selected curve
        poly_param_name_ = self.poly_param_names[self.act_curve_var.get()]['name']
        # Compute the full name of the coefficient parameters
        poly_coef_names_ = [f"ACT{act_id}_"+poly_param_name_+f"_{i}" for i in range(3)]

        # Update the data of the the coefficient for order 0
        self.entry_poly_0.delete(0, tk.END)
        self.entry_poly_0.insert(0, self.format_as_scientific(self.data[poly_coef_names_[0]]['value']))
        # Update the data of the the coefficient for order 1
        self.entry_poly_1.delete(0, tk.END)
        self.entry_poly_1.insert(0, self.format_as_scientific(self.data[poly_coef_names_[1]]['value']))
        # Update the data of the the coefficient for order 2
        self.entry_poly_2.delete(0, tk.END)
        self.entry_poly_2.insert(0, self.format_as_scientific(self.data[poly_coef_names_[2]]['value']))

        # Update the plot graph
        self.plot_poly()


    def plot_poly(self):
        """
        Function to plot a polynomial on the right pane. The coefficients used are the ones in the entry boxes.
        """

        # Return if the actuator id or the curve are not selected
        if(not self.act_id_var.get() or not self.act_curve_var.get()):
            return

        # Get actuator id
        act_id = self.act_id_var.get().split()[-1]

        abscissa = {}
        # Compute abscissa voltage based on the maximum voltage
        max_voltage_ = self.data['BAT_N_CELLS']['value']*4.2 # Assuming a LiPo Cell
        n_pts_ = 1000
        abscissa['voltage'] = [i * max_voltage_ / (n_pts_ - 1) for i in range(n_pts_)]
        # Compute abscissa speed based on the maximum speed computed from maximum value of the voltage2speed map
        volt2speed_coef_names_ = [f"ACT{act_id}_VOLT2SPEED"+f"_{i}" for i in range(3)]
        volt2speed_coef_ = [self.data[s]['value'] for s in volt2speed_coef_names_]
        poly_speed = POLY.polynomial(volt2speed_coef_)
        max_speed_ = poly_speed.eval(max_voltage_)
        abscissa['speed'] = [i * max_speed_ / (n_pts_ - 1) for i in range(n_pts_)]
        # Compute abscissa torque based on the maximum torque computed from maximum value of the speed2torque map
        speed2torque_coef_names_ = [f"ACT{act_id}_SPEED2TORQUE"+f"_{i}" for i in range(3)]
        speed2torque_coef_ = [self.data[s]['value'] for s in speed2torque_coef_names_]
        poly_torque = POLY.polynomial(speed2torque_coef_)
        max_torque_ = poly_torque.eval(max_speed_)
        abscissa['torque'] = [i * max_torque_ / (n_pts_ - 1) for i in range(n_pts_)]

        # Get the polynomial coefficients from the entry boxes
        poly_coefs_ = [float(self.entry_poly_0.get()), float(self.entry_poly_1.get()), float(self.entry_poly_2.get())]

        # Create a polynomial object based on the coefficients
        poly_selected_ = POLY.polynomial(poly_coefs_)

        # Get the x data for the plot
        xdata = abscissa[self.poly_param_names[self.act_curve_var.get()]['xdata']]
        # Initialize the y data for the plot
        ydata = []

        # Evaluate the polynomial
        for x in xdata:
            ydata.append(poly_selected_.eval(x))

        # Plot the curve on the right panel
        self.axs.clear() # clear
        self.axs.plot(xdata, ydata, linewidth=2, color='blue') # plot
        self.axs.grid(True) # enable grid
        self.axs.set_xlabel(self.poly_param_names[self.act_curve_var.get()]['xl']) # set x axis name
        self.axs.set_ylabel(self.poly_param_names[self.act_curve_var.get()]['yl']) # set y axis name
        self.axs.set_title(self.act_id_var.get() + ' - ' + self.act_curve_var.get()) # set title

        # Show the plot and proceed
        #plt.ion()
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
            
            # self.populate_tree()
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


    def update_actuator_options(self):
        """
        Function to update available actuators on the dropdown
        """

        # If there is data 
        if (self.data):

            # Define the options based the number of actuators
            options = [f'Actuator {i}' for i in range(self.data['VEH_ACT_NUM']['value'])]

            # Delet the list currently set of the dropdown
            self.actuator_menu['menu'].delete(0, 'end')
            # Add the updated options to the dropdown
            for opt in options:
                self.actuator_menu['menu'].add_command(label=opt, command=tk._setit(self.act_id_var, opt))

 
if __name__ == "__main__":
    """
    Main to run a detached ActuatorsEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Actuators configuration")
    # Define GUI window size
    root.geometry('1200x600')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/actuators_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = ActuatorsEditorGUI(root, True)

    # Call the function to terminate the matplotlib.pyplot when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

