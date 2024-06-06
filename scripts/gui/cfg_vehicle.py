#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to configure the vehicle geometric and dynamic properties

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
from fnmatch import fnmatch
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import poly_estimator as PEST
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import polynomial as POLY

class VehicleEditorGUI:
    """
    Class that defines a GUI for configuring the vehicle geometric and dynamic properties
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the VehicleEditorGUI class

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
        self.name_l_label = ttk.Label(self.left_frame, text="Vehicle configuration")
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

        # Build the left and right panels
        self.build_left_panel(self.left_frame)
        self.build_right_panel()



    def build_dynamics_pannel(self,parent_frame):

        dyn_frame = ttk.Frame(parent_frame)
        dyn_frame.pack(side=tk.TOP, pady=5, fill=tk.X, expand=False)
        label_dyn = ttk.Label(dyn_frame, text="Dynamics configuration:")
        label_dyn.pack(side=tk.TOP, pady=5, anchor=tk.NW)

        # Subframe for mass configuration
        mass_label = ttk.Label(dyn_frame, text="Mass [kg]:")
        mass_label.pack(side=tk.TOP, pady=(5,1))
        mass_frame = ttk.Frame(dyn_frame)
        mass_frame.pack(side=tk.TOP, pady=1)
        mass_label_m = ttk.Label(mass_frame, text="m:")
        mass_label_m.grid(row=0, column=1)
        self.entry_mass = ttk.Entry(mass_frame,width=11)
        self.entry_mass.grid(row=0, column=2)

        # Subframe for moment of inertia configuration
        moi_label = ttk.Label(dyn_frame, text="Moment of inertia [kg*m*m]:")
        moi_label.pack(side=tk.TOP, pady=(10,1))
        moi_frame = ttk.Frame(dyn_frame)
        moi_frame.pack(side=tk.TOP, pady=1)
        # Moment of inertia in x
        moi_label_x = ttk.Label(moi_frame, text="xx:")
        moi_label_x.grid(row=0, column=1)
        self.entry_moi_x = ttk.Entry(moi_frame,width=11)
        self.entry_moi_x.grid(row=0, column=2)
        # Moment of inertia in y
        moi_label_y = ttk.Label(moi_frame, text=" yy:")
        moi_label_y.grid(row=0, column=3)
        self.entry_moi_y = ttk.Entry(moi_frame,width=11)
        self.entry_moi_y.grid(row=0, column=4)
        # Moment of inertia in z
        moi_label_z = ttk.Label(moi_frame, text=" zz:")
        moi_label_z.grid(row=0, column=5)
        self.entry_moi_z = ttk.Entry(moi_frame,width=11)
        self.entry_moi_z.grid(row=0, column=6)
        
        # Subframe for linear drag configuration
        lin_drag_label = ttk.Label(dyn_frame, text="Linear drag [N*s/m]:")
        lin_drag_label.pack(side=tk.TOP, pady=(10,1))
        lin_drag_frame = ttk.Frame(dyn_frame)
        lin_drag_frame.pack(side=tk.TOP, pady=1)
        lin_drag_label_m = ttk.Label(lin_drag_frame, text="drag:")
        lin_drag_label_m.grid(row=0, column=1)
        self.entry_lin_drag = ttk.Entry(lin_drag_frame,width=11)
        self.entry_lin_drag.grid(row=0, column=2)

        # Subframe for angular drag configuration
        ang_drag_label = ttk.Label(dyn_frame, text="Angular drag [N*s/rad]:")
        ang_drag_label.pack(side=tk.TOP, pady=(10,1))
        ang_drag_frame = ttk.Frame(dyn_frame)
        ang_drag_frame.pack(side=tk.TOP, pady=1)
        ang_drag_label_m = ttk.Label(ang_drag_frame, text="drag:")
        ang_drag_label_m.grid(row=0, column=1)
        self.entry_ang_drag = ttk.Entry(ang_drag_frame,width=11)
        self.entry_ang_drag.grid(row=0, column=2)


        return
    
    def build_geometry_pannel(self,parent_frame):

        geometry_frame = ttk.Frame(parent_frame)
        geometry_frame.pack(side=tk.TOP, pady=5, fill=tk.X, expand=False)
        label_geometry = ttk.Label(geometry_frame, text="Geometry configuration:")
        label_geometry.pack(side=tk.TOP, pady=5, anchor=tk.NW)

        # Define the options for the actuators ids if this information is available
        if (self.data):
            actuator_options = [f'Actuator {i}' for i in range(self.data['VEH_ACT_NUM']['value'])]
        else:
            actuator_options = []

        # Create a subframe to select the id of the actuator to be configured
        act_select_frame = ttk.Frame(geometry_frame)
        act_select_frame.pack(side=tk.TOP, pady=5)
        # Add a label for the actuator id selector
        act_select_label = ttk.Label(act_select_frame, text="Actuator number")
        act_select_label.pack(side=tk.LEFT,padx=5)
        # Add a dropdown to select among the possible actuator ids
        self.act_id_var = tk.StringVar()
        self.actuator_menu = ttk.OptionMenu(act_select_frame, self.act_id_var, None, *actuator_options)
        self.actuator_menu.pack(side=tk.LEFT, padx=10)
        # # Bind the function to update the data displayed in the gui
        self.act_id_var.trace("w", lambda *args: self.update_geometry_properties())


        # Subframe for the position of the selected actuator
        pos_frame = ttk.Label(geometry_frame, text="Actuators position [m]:")
        pos_frame.pack(side=tk.TOP, pady=(10,1))
        pos_frame = ttk.Frame(geometry_frame)
        pos_frame.pack(side=tk.TOP, pady=1)
        # Position in x
        pos_frame_x = ttk.Label(pos_frame, text="x:")
        pos_frame_x.grid(row=0, column=1)
        self.entry_pos_x = ttk.Entry(pos_frame,width=11)
        self.entry_pos_x.grid(row=0, column=2)
        # Position in y
        pos_frame_y = ttk.Label(pos_frame, text=" y:")
        pos_frame_y.grid(row=0, column=3)
        self.entry_pos_y = ttk.Entry(pos_frame,width=11)
        self.entry_pos_y.grid(row=0, column=4)
        # Position in z
        pos_frame_z = ttk.Label(pos_frame, text=" z:")
        pos_frame_z.grid(row=0, column=5)
        self.entry_pos_z = ttk.Entry(pos_frame,width=11)
        self.entry_pos_z.grid(row=0, column=6)

        # Subframe for the direction of the selected actuator
        dir_frame = ttk.Label(geometry_frame, text="Actuators direction [ ]:")
        dir_frame.pack(side=tk.TOP, pady=(10,1))
        dir_frame = ttk.Frame(geometry_frame)
        dir_frame.pack(side=tk.TOP, pady=1)
        # Direction in x
        dir_frame_x = ttk.Label(dir_frame, text="x:")
        dir_frame_x.grid(row=0, column=1)
        self.entry_dir_x = ttk.Entry(dir_frame,width=11)
        self.entry_dir_x.grid(row=0, column=2)
        # Direction in y
        dir_frame_y = ttk.Label(dir_frame, text=" y:")
        dir_frame_y.grid(row=0, column=3)
        self.entry_dir_y = ttk.Entry(dir_frame,width=11)
        self.entry_dir_y.grid(row=0, column=4)
        # Direction in z
        dir_frame_z = ttk.Label(dir_frame, text=" z:")
        dir_frame_z.grid(row=0, column=5)
        self.entry_dir_z = ttk.Entry(dir_frame,width=11)
        self.entry_dir_z.grid(row=0, column=6)

        # Subframe for the direction of the selected actuator
        base_frame = ttk.Label(geometry_frame, text="Actuators arm base [m] (visualization only):")
        base_frame.pack(side=tk.TOP, pady=(20,1))
        base_frame = ttk.Frame(geometry_frame)
        base_frame.pack(side=tk.TOP, pady=1)
        # Arm base in x
        base_frame_x = ttk.Label(base_frame, text="x:")
        base_frame_x.grid(row=0, column=1)
        self.entry_base_x = ttk.Entry(base_frame,width=11)
        self.entry_base_x.grid(row=0, column=2)
        # Arm base in y
        base_frame_y = ttk.Label(base_frame, text=" y:")
        base_frame_y.grid(row=0, column=3)
        self.entry_base_y = ttk.Entry(base_frame,width=11)
        self.entry_base_y.grid(row=0, column=4)
        # Arm base in z
        base_frame_z = ttk.Label(base_frame, text=" z:")
        base_frame_z.grid(row=0, column=5)
        self.entry_base_z = ttk.Entry(base_frame,width=11)
        self.entry_base_z.grid(row=0, column=6)


        # Subframe for the body size
        size_frame = ttk.Label(geometry_frame, text="Body size [m] (visualization only):")
        size_frame.pack(side=tk.TOP, pady=(10,1))
        size_frame = ttk.Frame(geometry_frame)
        size_frame.pack(side=tk.TOP, pady=1)
        # Size in x
        size_frame_x = ttk.Label(size_frame, text="x:")
        size_frame_x.grid(row=0, column=1)
        self.entry_size_x = ttk.Entry(size_frame,width=11)
        self.entry_size_x.grid(row=0, column=2)
        # Size in y
        size_frame_y = ttk.Label(size_frame, text=" y:")
        size_frame_y.grid(row=0, column=3)
        self.entry_size_y = ttk.Entry(size_frame,width=11)
        self.entry_size_y.grid(row=0, column=4)
        # Size in z
        size_frame_z = ttk.Label(size_frame, text=" z:")
        size_frame_z.grid(row=0, column=5)
        self.entry_size_z = ttk.Entry(size_frame,width=11)
        self.entry_size_z.grid(row=0, column=6)

        return



    def build_left_panel(self,parent_frame):
        """
        Function to build the widgets into the left panel
        """

        self.build_dynamics_pannel(parent_frame)

        self.build_geometry_pannel(parent_frame)




    def build_left_panel_old(self):
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
        moi_frame = ttk.Frame(self.left_frame)
        moi_frame.pack(side=tk.TOP, pady=5)
        poly_label = ttk.Label(moi_frame, text="p(u) = ")
        poly_label.grid(row=0, column=0)
        # Actuator polynomial coefficient for order 0
        self.entry_poly_0 = ttk.Entry(moi_frame,width=11)
        self.entry_poly_0.grid(row=0, column=1)
        poly_label_0 = ttk.Label(moi_frame, text="  ")
        poly_label_0.grid(row=0, column=2)
        # Actuator polynomial coefficient for order 0
        self.entry_poly_1 = ttk.Entry(moi_frame,width=11)
        self.entry_poly_1.grid(row=0, column=3)
        poly_label_1 = ttk.Label(moi_frame, text="u ")
        poly_label_1.grid(row=0, column=4)
        # Actuator polynomial coefficient for order 0
        self.entry_poly_2 = ttk.Entry(moi_frame,width=11)
        self.entry_poly_2.grid(row=0, column=5)
        poly_label_2 = ttk.Label(moi_frame, text="u²")
        poly_label_2.grid(row=0, column=6)


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





    def update_dynamic_properties(self):

        # If there is no data 
        if (not self.data):
            return
        
        # Update the displayed dynamic properties
        self.entry_mass.delete(0, tk.END)
        self.entry_mass.insert(0, str(self.data['DYN_MASS']['value']))
        #
        self.entry_moi_x.delete(0, tk.END)
        self.entry_moi_x.insert(0, str(self.data['DYN_MOI_XX']['value']))
        self.entry_moi_y.delete(0, tk.END)
        self.entry_moi_y.insert(0, str(self.data['DYN_MOI_YY']['value']))
        self.entry_moi_z.delete(0, tk.END)
        self.entry_moi_z.insert(0, str(self.data['DYN_MOI_ZZ']['value']))
        #
        self.entry_lin_drag.delete(0, tk.END)
        self.entry_lin_drag.insert(0, str(self.data['DYN_DRAG_V']['value']))
        self.entry_ang_drag.delete(0, tk.END)
        self.entry_ang_drag.insert(0, str(self.data['DYN_DRAG_W']['value']))


        return
    

    def update_geometry_properties(self):

        # If there is no data 
        if (not self.data):
            return


        self.entry_size_x.delete(0, tk.END)
        self.entry_size_x.insert(0, str(self.data[f"VIZ_SIZE_X"]['value']))
        self.entry_size_y.delete(0, tk.END)
        self.entry_size_y.insert(0, str(self.data[f"VIZ_SIZE_Y"]['value']))
        self.entry_size_z.delete(0, tk.END)
        self.entry_size_z.insert(0, str(self.data[f"VIZ_SIZE_Z"]['value']))

        # Return it there is no actuator selected
        if(not self.act_id_var.get()):
            return
        
        # Get selected actuator id
        act_id = self.act_id_var.get().split()[-1]

        self.entry_pos_x.delete(0, tk.END)
        self.entry_pos_x.insert(0, str(self.data[f"VEH_ACT{act_id}_POS_X"]['value']))
        self.entry_pos_y.delete(0, tk.END)
        self.entry_pos_y.insert(0, str(self.data[f"VEH_ACT{act_id}_POS_Y"]['value']))
        self.entry_pos_z.delete(0, tk.END)
        self.entry_pos_z.insert(0, str(self.data[f"VEH_ACT{act_id}_POS_Z"]['value']))

        self.entry_dir_x.delete(0, tk.END)
        self.entry_dir_x.insert(0, str(self.data[f"VEH_ACT{act_id}_DIR_X"]['value']))
        self.entry_dir_y.delete(0, tk.END)
        self.entry_dir_y.insert(0, str(self.data[f"VEH_ACT{act_id}_DIR_Y"]['value']))
        self.entry_dir_z.delete(0, tk.END)
        self.entry_dir_z.insert(0, str(self.data[f"VEH_ACT{act_id}_DIR_Z"]['value']))

        self.entry_base_x.delete(0, tk.END)
        self.entry_base_x.insert(0, str(self.data[f"VIZ_ACT{act_id}_BASE_X"]['value']))
        self.entry_base_y.delete(0, tk.END)
        self.entry_base_y.insert(0, str(self.data[f"VIZ_ACT{act_id}_BASE_Y"]['value']))
        self.entry_base_z.delete(0, tk.END)
        self.entry_base_z.insert(0, str(self.data[f"VIZ_ACT{act_id}_BASE_Z"]['value']))




        return


    def update_displayed_data(self, *args):
        """
        Function to update the data displayed on the gui

        Parameters:
            *args (list): Unused arguments passed by the function when it is binded to a widget action.
        """

        # Update the possible ids of the actuators
        self.update_actuator_options()

        self.update_dynamic_properties()

        self.update_geometry_properties()

        return



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



    def update_displayed_data_old(self, *args):
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
    Main to run a detached VehicleEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # root = ThemedTk(theme='radiance')
    # Define GUI title
    root.title("Vehicle configuration")
    # Define GUI window size
    root.geometry('1200x600')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/actuators_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = VehicleEditorGUI(root, True)

    # Call the function to terminate the matplotlib.pyplot when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

