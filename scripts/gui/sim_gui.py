#!/usr/bin/env python3
# -*- coding:utf-8 -*-



import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import json
import matplotlib.pyplot as plt
from ttkthemes import ThemedTk

import os
import home_sim as HOME
import full_set_params as FULL_SET
import cfg_actuators as CFG_ACT






class SimGUI:
    """
    Class that defines a GUI for the simulator
    """

    def __init__(self, root_):
        """
        Constructor for the dynamics class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
        """

        # Set the root variable
        self.root = root_


        self.json_path = None



        # Create the top-level notebook
        self.top_notebook = ttk.Notebook(self.root)
        self.top_notebook.pack(fill='both', expand=True)

        # Create the first tab in the top-level notebook
        tab_main = ttk.Frame(self.top_notebook)
        self.top_notebook.add(tab_main, text="Home")
        # Create buttons to load and save file
        tab_main_io = ttk.Frame(tab_main)
        tab_main_io.pack(side=tk.BOTTOM, pady=5, fill="x")
        # Create buttons to load and save file
        tab_home = ttk.Frame(tab_main)
        tab_home.pack(side=tk.BOTTOM, pady=5, expand=True, fill="both")

        self.home_gui = HOME.SimHomeApp(tab_home)

        # # Create buttons to load and save file
        # io_frame = ttk.Frame(tab_main_io)
        # io_frame.pack(side=tk.LEFT, pady=0, fill="both", expand=True)

        # Button to load file
        self.load_button = ttk.Button(tab_main_io, text="   Load", width=7, padding=(4, 4), command=self.load_json)
        self.load_button.pack(padx=5, side=tk.LEFT)

        # Button to save file
        self.save_button = ttk.Button(tab_main_io, text="   Save", width=7, padding=(4, 4), command=self.save_json)
        self.save_button.pack(padx=5, side=tk.LEFT)

        # Button to save file as
        self.saveas_button = ttk.Button(tab_main_io, text="Save As", width=7, padding=(4, 4), command=self.saveas_json)
        self.saveas_button.pack(padx=5, side=tk.LEFT)

        # Label
        self.path_label = ttk.Label(tab_main_io, text="JSON path: ")
        self.path_label.pack(side=tk.LEFT, padx=10, fill="both", expand=True)




        # Create the second tab in the top-level notebook
        tab2 = ttk.Frame(self.top_notebook)
        self.top_notebook.add(tab2, text="Configuration")

        # Create a second-level notebook inside Tab 2
        self.config_level_notebook = ttk.Notebook(tab2)
        self.config_level_notebook.pack(fill='both', expand=True)

        # Create tabs inside the second-level notebook
        cfg_tab_geo = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_geo, text="Geolocation")

        cfg_tab_sens = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_sens, text="Sensors")

        cfg_tab_act = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_act, text="Actuators")
        self.cfg_act_gui = CFG_ACT.ActuatorsEditorGUI(cfg_tab_act, False)
        # self.root.protocol("WM_DELETE_WINDOW", self.cfg_act_gui.on_closing)

        cfg_tab_full = ttk.Frame(self.config_level_notebook)
        self.config_level_notebook.add(cfg_tab_full, text="Full Parameter Set")
        self.full_set_gui = FULL_SET.JsonEditorGUI(cfg_tab_full, False)


        self.top_notebook.bind("<<NotebookTabChanged>>", self.tab_changed)
        self.config_level_notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        self.current_tab = [self.top_notebook.index(self.top_notebook.select()), self.config_level_notebook.index(self.config_level_notebook.select())]



    def tab_changed(self,event):
        current_tab_a = self.top_notebook.index(self.top_notebook.select())
        current_tab_b = self.config_level_notebook.index(self.config_level_notebook.select())
        prev_tab = self.current_tab[:]
        self.current_tab = [current_tab_a, current_tab_b]


        old_tab_gui = self.tab_map(prev_tab)
        if (old_tab_gui):
            data = old_tab_gui.get_data()
            self.data = data

        new_tab_gui = self.tab_map(self.current_tab)
        if(new_tab_gui):
            new_tab_gui.set_data(self.data,self.json_path)

        print ("Old tab: ", prev_tab)
        print ("New tab: ", self.current_tab)
        print("")



    def tab_map(self,ids):

        tab = None
        if(ids[0] == 0):
            return self.home_gui
        elif(ids[0] == 1):
            if(ids[1] == 0):
                return None
            if(ids[1] == 1):
                return None
            if(ids[1] == 2):
                return self.cfg_act_gui
            if(ids[1] == 3):
                return self.full_set_gui



    def load_json(self):
        #TODO: Use parameter server?????
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            with open(self.file_path, "r") as json_file:
                self.data = json.load(json_file)
        
            # Store the path and display it
            self.json_path = path
            self.path_label.config(text="JSON path: "+self.json_path)

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

    def on_closing(self):
        plt.close()


if __name__ == "__main__":
    """
    Main to run a detached JsonEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Custom Copter Simulator")
    # Define GUI window size
    root.geometry('1150x500')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/sim_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = SimGUI(root)

    root.protocol("WM_DELETE_WINDOW", app.on_closing)

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
# # radiance
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