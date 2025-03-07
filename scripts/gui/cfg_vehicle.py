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
import numpy as np
import subprocess
import multiprocessing
import time
import zmq

import gui.vtk_vehicle as VTK
import gui.poly_estimator as PEST
import sim4cd.polynomial as POLY
import gui.gui_utils as GU

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

        self.vtk_window_title = "Vehicle Geometry View"

        # Set the root variable
        self.root = root_

        # Set the io_enabled variable
        self.io_enabled = enable_io_

        # Define a left panel
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=False, padx=(0,1))
        # Add a title for the left panel
        self.name_l_label = ttk.Label(self.left_frame, text="Vehicle configuration")
        self.name_l_label.pack(padx=5)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(1,0))
        # Add a title for the right panel
        self.name_r_label = ttk.Label(self.right_frame, text="Vehicle geometry")
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
        self.build_right_panel(self.right_frame)


        # Create a ZeroMQ context
        self.context = zmq.Context()

        # Create a PUB socket
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5555")  # Bind to port 5555



    def build_dynamics_pannel(self,parent_frame):
        """
        Function to build the widgets into the panel used to configure dynamics properties

        Parameters:
            parent_frame (tk.Frame): Parent frame in which the panel will be built.
        """

        dyn_frame = ttk.Frame(parent_frame)
        dyn_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X, expand=False)
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


    def build_geometry_pannel(self,parent_frame):
        """
        Function to build the widgets into the panel used to configure geometry properties

        Parameters:
            parent_frame (tk.Frame): Parent frame in which the panel will be built.
        """

        geometry_frame = ttk.Frame(parent_frame)
        geometry_frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X, expand=False)
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
        dir_frame = ttk.Label(geometry_frame, text="Actuators direction [ ] (normalized vector):")
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


    def build_left_panel(self,parent_frame):
        """
        Function to build the widgets into the left panel

        Parameters:
            parent_frame (tk.Frame): Parent frame in which the panel will be built.
        """

        self.build_dynamics_pannel(parent_frame)
        self.build_geometry_pannel(parent_frame)

        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(side=tk.TOP, padx=(10,10), pady=(40,10))

        # Add button to set the estimated coefficients to the current actuator configuration parameters
        set_button = ttk.Button(button_frame, text="Set values", padding=(4, 4), command=self.set_values)
        set_button.pack(padx=5, side=tk.LEFT)


    def build_right_panel(self,parent_frame):
        """
        Function to build the widgets into the right panel

        Parameters:
            parent_frame (tk.Frame): Parent frame in which the panel will be built.
        """

        button = ttk.Button(parent_frame, text="Show vehicle", command=self.create_and_position_vtk_window)
        button.pack()


    def create_and_position_vtk_window(self):
        """
        Function to create and position a vtk window
        """

        if(not GU.get_window_id(self.vtk_window_title)):
            self.proc = multiprocessing.Process(target=self.run_external_vtk_viz, args=())
            self.proc.start()
        GU.position_external_window(self.vtk_window_title, self.right_frame)


    def set_values(self):
        """
        Function to set the values inserted in the gui to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return

        # Set mass of the vehicle
        self.data['DYN_MASS']['value'] = float(self.entry_mass.get())
        # Set moment of inertia of the vehicle
        self.data['DYN_MOI_XX']['value'] = float(self.entry_moi_x.get())
        self.data['DYN_MOI_YY']['value'] = float(self.entry_moi_y.get())
        self.data['DYN_MOI_ZZ']['value'] = float(self.entry_moi_z.get())
        # Set linear and angular drag
        self.data['DYN_DRAG_V']['value'] = float(self.entry_lin_drag.get())
        self.data['DYN_DRAG_W']['value'] = float(self.entry_ang_drag.get())

        # Set vehicle size
        self.data['VIZ_SIZE_X']['value'] = float(self.entry_size_x.get())
        self.data['VIZ_SIZE_Y']['value'] = float(self.entry_size_y.get())
        self.data['VIZ_SIZE_Z']['value'] = float(self.entry_size_z.get())


        # Return if there is no actuator selected
        if(self.act_id_var.get()):
            
            # Get the actuator id
            act_id = self.act_id_var.get().split()[-1]

            # Set position of selected actuator
            self.data[f"VEH_ACT{act_id}_POS_X"]['value'] = float(self.entry_pos_x.get())
            self.data[f"VEH_ACT{act_id}_POS_Y"]['value'] = float(self.entry_pos_y.get())
            self.data[f"VEH_ACT{act_id}_POS_Z"]['value'] = float(self.entry_pos_z.get())
            # Set direction of selected actuator
            direction = np.array([float(self.entry_dir_x.get()), float(self.entry_dir_y.get()), float(self.entry_dir_z.get())])
            direction = direction/np.linalg.norm(direction)
            direction = direction.tolist()
            self.data[f"VEH_ACT{act_id}_DIR_X"]['value'] = direction[0]
            self.data[f"VEH_ACT{act_id}_DIR_Y"]['value'] = direction[1]
            self.data[f"VEH_ACT{act_id}_DIR_Z"]['value'] = direction[2]
            # Set base of the arm that holds the selected actuator
            self.data[f"VIZ_ACT{act_id}_BASE_X"]['value'] = float(self.entry_base_x.get())
            self.data[f"VIZ_ACT{act_id}_BASE_Y"]['value'] = float(self.entry_base_y.get())
            self.data[f"VIZ_ACT{act_id}_BASE_Z"]['value'] = float(self.entry_base_z.get())

        # Update displayed data
        self.update_displayed_data()

        # Sending tate to vtk
        data_json = json.dumps(self.data)
        self.socket.send_string(data_json)  # Send the JSON-encoded dictionary


    def update_dynamic_properties(self):
        """
        Function to update the dynamics data displayed on the gui
        """
        
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
    

    def update_geometry_properties(self):
        """
        Function to update the geometry data displayed on the gui
        """

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

        GU.close_window(self.vtk_window_title)
        self.root.quit()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.destroy()

        self.socket.close()
        self.context.term()


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


    def run_external_vtk_viz(self):
        """
        Function to run an external VTK window
        """

        self.visualization = VTK.Visualization(self.data)
        
        self.visualization.start()


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
    

    def viz_return(self):
        """
        Function to update the visualization of the gui
        """
        # Just call the update_displayed_data() function
        self.update_displayed_data()

        self.create_and_position_vtk_window()


    def viz_exit(self):
        """
        Function to clean up gui when its tab is switched off
        """
        GU.close_window(self.vtk_window_title)


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
    root.geometry('1200x800')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/vehicle_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = VehicleEditorGUI(root, True)

    # Call the function to terminate the matplotlib.pyplot when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

