#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to edit the parameter values

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
from fnmatch import fnmatch


import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class ActuatorsEditorGUI:
    """
    Class that defines a GUI for editing the parameters
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the dynamics class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
        """




        # Set the root variable
        self.root = root_

        # Set the io_enabled variable
        self.io_enabled = enable_io_

        # Define a left panel
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.name_l_label = ttk.Label(self.left_frame, text="Actuator configuration")
        self.name_l_label.pack(pady=2)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.name_r_label = ttk.Label(self.right_frame, text="Curve model")
        self.name_r_label.pack(pady=2)



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


        # self.selector_frame = ttk.Frame(self.left_frame)
        # self.selector_frame.pack(side=tk.TOP, padx=10)

        self.editor_frame = ttk.Frame(self.left_frame)
        self.editor_frame.pack(side=tk.TOP, padx=10)



        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}

        #path = "/home/NEA.com_adriano.rezende/simulation_ws/src/px4sim/config/sim_params.json"
        path = "/home/adrianomcr/simulation_ws/src/px4sim/config/sim_params.json"
        with open(path, "r") as json_file:
                self.data = json.load(json_file)

        # print(self.data)

        self.left_panel()
        self.right_panel()

        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)




    def plot_curve(self, *args):



        print(args)
        print("act_n: ", self.act_n_var.get())
        print("curce_type: ", self.act_feature_var.get())
        print('')
        act_n = self.act_n_var.get()
        act_n = int(act_n[-1])

        self.axs.clear()

        # Data for the line plot
        x_data = [0, 0.2, 0.4, 0.6, 0.8, 1]
        y_data = [0, 2, 4, 1, 3, 7]
        y_data = [i**act_n for i in y_data]

        self.axs.set_xlim(0, 1)

        # Plot the line
        self.axs.plot(x_data, y_data)
        self.axs.grid(True)

        # Optionally, add labels and a title
        self.axs.set_xlabel('X-axis Label')
        self.axs.set_ylabel('Y-axis Label')
        self.axs.set_title(self.act_n_var.get())

        # Show the plot
        plt.ion()
        #plt.show()


        


        return



    def on_closing(self):
        # Close the matplotlib figure
        # self.fig.clf()
        # self.right_frame.destroy()
        plt.close()

    def set_data(self, d, path):
        self.data = d
        self.file_path = path

        self.update()


    def get_data(self):
        return self.data


    def update(self):
        if (self.data):
            options = [f'Actuator {i}' for i in range(self.data['VEH_ACT_NUM']['value'])]

            # self.actuator_menu['values'] = options

            self.actuator_menu['menu'].delete(0, 'end')
            for o in options:
                self.actuator_menu['menu'].add_command(label=o, command=tk._setit(self.act_n_var, o))




    def right_panel(self):

        self.fig, self.axs = plt.subplots(1,1)

        canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        canvas.draw()
        canvas.get_tk_widget().pack()
        return


    def left_panel(self):



        if (self.data):
            actuator_options = [f'Actuator {i}' for i in range(self.data['VEH_ACT_NUM']['value'])]
        else:
            actuator_options = []

        act_select_frame = ttk.Frame(self.left_frame)
        act_select_frame.pack(side=tk.TOP, pady=5)
        #
        act_select_label = ttk.Label(act_select_frame, text="Actuator number")
        act_select_label.pack(side=tk.LEFT,padx=5)
        #
        self.act_n_var = tk.StringVar()
        # Create an OptionMenu widget
        self.actuator_menu = ttk.OptionMenu(act_select_frame, self.act_n_var, None, *actuator_options)
        self.actuator_menu.pack(side=tk.LEFT, padx=10)
        # self.act_n_var.trace('w', self.on_select)
        self.act_n_var.trace("w", self.plot_curve) 

        act_features_frame = ttk.Frame(self.left_frame)
        act_features_frame.pack(side=tk.TOP, pady=5)

        act_tcte_label = ttk.Label(act_features_frame, text="Time constant")
        act_tcte_label.grid(row=0, column=0)
        # act_tcte_label.pack(side=tk.TOP,padx=5, anchor="w")
        combo_tcte = ttk.Combobox(act_features_frame, values=[])
        # combo_tcte.bind("<<ComboboxSelected>>", self.on_option_selected)
        # combo_tcte.bind("<Return>", lambda event=None: self.set_value())
        # combo_tcte.set("")
        combo_tcte.grid(row=0, column=1)

        act_moi_label = ttk.Label(act_features_frame, text="Moment of inertia")
        # act_moi_label.pack(side=tk.TOP,padx=5, anchor="w")
        act_moi_label.grid(row=2, column=0)
        combo_moi = ttk.Combobox(act_features_frame, values=[])
        combo_moi.grid(row=2, column=1)

        act_spin_label = ttk.Label(act_features_frame, text="Spin direction")
        # act_spin_label.pack(side=tk.TOP,padx=5, anchor="w")
        act_spin_label.grid(row=1, column=0)
        combo_spin = ttk.Combobox(act_features_frame, values=[])
        combo_spin.grid(row=1, column=1)



        act_curve_frame = ttk.Frame(self.left_frame)
        act_curve_frame.pack(side=tk.TOP, pady=(30,5))
        #
        act_curve_label = ttk.Label(act_curve_frame, text="Curve")
        act_curve_label.pack(side=tk.LEFT,padx=5)
        curve_options = ['Voltage to speed','Speed to thrust','Speed to torque','Torque to current']
        self.act_feature_var = tk.StringVar()
        # Create an OptionMenu widget
        self.curve_menu = ttk.OptionMenu(act_curve_frame, self.act_feature_var, None, *curve_options)
        self.curve_menu.pack(side=tk.TOP, padx=10)
        # self.act_feature_var.trace('w', self.on_select)








    def on_select(self, name, index, mode):
        # print(name)
        # print(index)
        # print(mode)

        for widget in self.editor_frame.winfo_children():
            widget.destroy()

        self.label = ttk.Label(self.editor_frame, text="aaaaaaaaaaaaa")
        self.label.pack(pady=2)
        

        return













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
        #TODO: Use parameter server?????
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            with open(self.file_path, "r") as json_file:
                self.data = json.load(json_file)
            
            # self.populate_tree()
            self.left_panel()

 
if __name__ == "__main__":
    """
    Main to run a detached JsonEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Actuators configuration")
    # Define GUI window size
    root.geometry('1150x500')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/actuators_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = ActuatorsEditorGUI(root, True)

    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

