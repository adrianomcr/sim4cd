#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to put together all of the GUIs related with the simulator

import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import json
from ttkthemes import ThemedTk

import os
import home_sim as HOME
import full_set_params as FULL_SET
import cfg_actuators as CFG_ACT
import cfg_vehicle as CFG_VEH
import cfg_geolocation as CFG_GEO
import cfg_power as CFG_POW
import cfg_sensors as CFG_SENS

class SimGUI:
    """
    Class that defines a GUI for the simulator
    """

    def __init__(self, root_):
        """
        Constructor for the SimGUI class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
        """

        # Set the root variable
        self.root = root_

        # Initialize the variable to store the json path
        self.json_path = None

        # Create the top-level notebook
        self.top_notebook = ttk.Notebook(self.root)
        self.top_notebook.pack(fill='both', expand=True)

        # Create the first tab in the top-level notebook
        tab_main = ttk.Frame(self.top_notebook)
        self.top_notebook.add(tab_main, text="Home")

        # Create a subframe for the io buttons
        tab_main_io = ttk.Frame(tab_main)
        tab_main_io.pack(side=tk.BOTTOM, pady=5, fill="x")
        # Button to load file
        self.load_button = ttk.Button(tab_main_io, text="   Load", width=7, padding=(4, 4), command=self.load_json)
        self.load_button.pack(padx=5, side=tk.LEFT)
        # Button to save file
        self.save_button = ttk.Button(tab_main_io, text="   Save", width=7, padding=(4, 4), command=self.save_json)
        self.save_button.pack(padx=5, side=tk.LEFT)
        # Button to save file as
        self.saveas_button = ttk.Button(tab_main_io, text="Save As", width=7, padding=(4, 4), command=self.saveas_json)
        self.saveas_button.pack(padx=5, side=tk.LEFT)
        # Label form the path of the config file
        self.path_label = ttk.Label(tab_main_io, text="JSON path: ")
        self.path_label.pack(side=tk.LEFT, padx=10, fill="both", expand=True)

        # Create subframe for the home gui
        tab_home = ttk.Frame(tab_main)
        tab_home.pack(side=tk.BOTTOM, pady=5, expand=True, fill="both")
        # Append the home gui to the subframe
        self.home_gui = HOME.SimHomeApp(tab_home)

        # Create the second tab in the top-level notebook
        tab_config = ttk.Frame(self.top_notebook)
        self.top_notebook.add(tab_config, text="Configuration")
        # Create a second-level notebook inside Tab 2
        self.config_level_notebook = ttk.Notebook(tab_config)
        self.config_level_notebook.pack(fill='both', expand=True)

        # Inside the second-level notebook, create a tab for configuring the geolocation
        cfg_tab_geo = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_geo, text="Geolocation")
        # Append the ActuatorsEditorGUI gui to the tab
        self.cfg_geo_gui = CFG_GEO.GeolocationEditorGUI(cfg_tab_geo, False)

        # Inside the second-level notebook, create a tab for configuring the sensors
        cfg_tab_sens = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_sens, text="Sensors")
        # Append the SensorsEditorGUI gui to the tab
        self.cfg_sens_gui = CFG_SENS.SensorsEditorGUI(cfg_tab_sens, False)

        # Inside the second-level notebook, create a tab for configuring the vehicle geometry
        cfg_tab_vehicle = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_vehicle, text="Vehicle")
        # Append the VehicleEditorGUI gui to the tab
        self.cfg_veh_gui = CFG_VEH.VehicleEditorGUI(cfg_tab_vehicle, False)

        # Inside the second-level notebook, create a tab for configuring the actuators
        cfg_tab_act = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_act, text="Actuators")
        # Append the ActuatorsEditorGUI gui to the tab
        self.cfg_act_gui = CFG_ACT.ActuatorsEditorGUI(cfg_tab_act, False)

        # Inside the second-level notebook, create a tab for configuring the power
        cfg_tab_power = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_power, text="Power")
        # Append the PowerEditorGUI gui to the tab
        self.cfg_pow_gui = CFG_POW.PowerEditorGUI(cfg_tab_power, False)

        # Inside the second-level notebook, create a tab for configuring all of the parameters
        cfg_tab_full = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_full, text="Full Parameter Set")
        # Append the JsonEditorGUI gui to the tab
        self.full_set_gui = FULL_SET.JsonEditorGUI(cfg_tab_full, False)

        # Create the second tab in the top-level notebook
        tab_interact = ttk.Frame(self.top_notebook)
        self.top_notebook.add(tab_interact, text="Interaction")
        # Add temporary message
        temp_label = ttk.Label(tab_interact, text="To be implemented", font=("Helvetica", 25))
        temp_label.pack(side=tk.TOP, pady=30, fill="both", expand=True)


        # Bind the function tab_changed to the actions of changing tabs
        self.top_notebook.bind("<<NotebookTabChanged>>", self.tab_changed)
        self.config_level_notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        # Initialize the current tab variable
        self.current_tab = [self.top_notebook.index(self.top_notebook.select()), self.config_level_notebook.index(self.config_level_notebook.select())]

    def tab_changed(self,event):
        """
        Tab to handle action that need to occur when the selected tab changes

        Parameters:
            event (tkinter.Event): Unused argument passed through the bind method
        """

        # Get current first level tab
        current_tab_1 = self.top_notebook.index(self.top_notebook.select())
        # Get current second level tab
        current_tab_2 = self.config_level_notebook.index(self.config_level_notebook.select())

        # Save the previous tab variable
        prev_tab = self.current_tab[:]
        # Update the current tab variable
        self.current_tab = [current_tab_1, current_tab_2]

        # Get the object of the gui in the previous tab
        old_tab_gui = self.tab_map(prev_tab)
        if (old_tab_gui):
            # Get the updated data from the previous gui
            data = old_tab_gui.get_data()
            self.data = data

        # Get the object of the gui in the current tab
        new_tab_gui = self.tab_map(self.current_tab)
        if(new_tab_gui):
            # Set the updated data into the current gui
            new_tab_gui.set_data(self.data,self.json_path)
            new_tab_gui.viz_return()


    def tab_map(self,ids):
        """
        Function to map the id list of a GUI tab to its object

        Parameters:
            ids (list of int): List with the ids (one id of each level) of the selected tab

        Returns:
            (class of a gui tab): Object that represents the gui that are attached to the selected tab
        """
        if(ids[0] == 0):
            return self.home_gui
        elif(ids[0] == 1):
            if(ids[1] == 0):
                return self.cfg_geo_gui
            if(ids[1] == 1):
                return self.cfg_sens_gui
            if(ids[1] == 2):
                return self.cfg_veh_gui
            if(ids[1] == 3):
                return self.cfg_act_gui
            if(ids[1] == 4):
                return self.cfg_pow_gui
            if(ids[1] == 5):
                return self.full_set_gui
        if(ids[0] == 2):
            return None


    def on_closing(self):
        """
        Function to handle action when window is closed
        """
        # Make sure the simulator is closed
        self.home_gui.on_closing()
        # Make sure matplotlib.pyplot is terminated
        self.cfg_geo_gui.on_closing()
        # Make sure gui is terminated
        self.cfg_sens_gui.on_closing()
        # Make sure matplotlib.pyplot is terminated
        self.cfg_act_gui.on_closing()
        # Make sure matplotlib.pyplot is terminated
        self.cfg_pow_gui.on_closing()

        self.root.quit()
        for widget in self.root.winfo_children():
            widget.destroy()
            self.root.destroy()
        


    def load_json(self):
        """
        Function to show a file dialog to load a json file
        """
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            # Store the path and display it
            self.json_path = path
            self.path_label.config(text="JSON path: "+self.json_path)
            
            with open(self.json_path, "r") as json_file:
                self.data = json.load(json_file)
        
            # # Store the path and display it
            # self.json_path = path
            # self.path_label.config(text="JSON path: "+self.json_path)

            # Update data on the child GUIs
            self.full_set_gui.set_data(self.data, self.json_path)
            self.home_gui.set_data(self.data, self.json_path)

   
    def saveas_json(self):
        """
        Function to save the current set os parameters as a new file
        """

        # Open a file dialog to select a path ans set a name for the new file to be saved
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        # If a path and a name were provided
        if path:
            # Set the new path
            self.json_path = path
            self.path_label.config(text="JSON path: "+self.json_path)
            # Save current set of parameters as a JSON file
            self.save_json()


    def save_json(self):
        """
        Function to dump the current set os parameters to the origin JSON file
        """

        try:
            # If path is set
            if self.json_path:
                # Open the file
                with open(self.json_path, "w") as json_file:
                    # Dump the parameters data to the file
                    json.dump(self.data, json_file, indent=4)
        except:
            # Throw an error message there was a problem in saving the file
            messagebox.showerror("Error", "A problem ocurred when saving the file")


if __name__ == "__main__":
    """
    Main to run a detached SimGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Custom Copter Simulator")
    # Define GUI window size
    root.geometry('1200x600')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/sim_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = SimGUI(root)

    # Call the function to terminate the matplotlib.pyplot when window is closed 
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Maximize the window
    root.attributes('-zoomed', 1)

    # Run the tkinter event loop
    root.mainloop()











# themes_list = ['scidpink', 'alt', 'itft1', 'classic', 'adapta', 'elegance', 'default', 'scidgrey', 'winxpblue', 'arc', 'scidmint', 'kroc', 'ubuntu', 'plastik', 'breeze', 'radiance', 'black', 'scidpurple', 'scidgreen', 'keramik', 'scidblue', 'equilux', 'aquativo', 'clam', 'scidsand', 'blue', 'clearlooks', 'smog', 'yaru']
# # root = ThemedTk(theme="adapta")

# # blue
# # equilux
# # scidblue
# # scidgreen
# # scidpurple - good
# # black
# # kroc - this is orange
# # radiance - Ubuntu
# # breeze


# # adapta - ok
# # aquativo - good
# # arc
# # blue
# # clearlooks
# # elegance
# # equilux
# # itft1 - ok
# # keramik
# # plastik - ok
# # radiance - good
# # scidblue - ok
# # smog
# # winxpblue - ok
# # winnative - ok