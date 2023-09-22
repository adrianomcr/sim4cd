#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to edit the parameter values

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
# import json
from ttkthemes import ThemedTk
import os
#from fnmatch import fnmatch
import numpy as np

# import matplotlib.pyplot as plt
# from mpl_toolkits import mplot3d
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class PolyEstimatorGUI:
    """
    Class that defines a GUI for editing the parameters
    """

    def __init__(self, root_):
        """
        Constructor for the dynamics class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
        """




        # Set the root variable
        self.root = root_

        # # Set the io_enabled variable
        # self.io_enabled = enable_io_

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill="both", expand=True)
        self.name_r_label = ttk.Label(self.main_frame, text="Polynomial estimator")
        self.name_r_label.pack(pady=2)



        # if(self.io_enabled):
        #     # Create buttons to load and save file
        #     buttons_frame = ttk.Frame(self.main_frame)
        #     buttons_frame.pack(side=tk.TOP, padx=10)
        #     # Button to load file
        #     self.load_button = ttk.Button(buttons_frame, text="    Load", padding=(4, 4), command=self.load_json)
        #     self.load_button.pack(pady=10, side=tk.LEFT)
        #     # Button to save file
        #     self.save_button = ttk.Button(buttons_frame, text="    Save", padding=(4, 4), command=self.save_json)
        #     self.save_button.pack(pady=10, side=tk.LEFT)
        #     # Button to save file as
        #     self.saveas_button = ttk.Button(buttons_frame, text="  Save As", padding=(4, 4), command=self.saveas_json)
        #     self.saveas_button.pack(pady=10, side=tk.LEFT)



        # Create a treeview to display the parameters attributes
        self.tree = ttk.Treeview(self.main_frame, columns=("X", "Y"), height=5)
        # Set the headers of each column
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("#1", text=" X", anchor=tk.CENTER)
        self.tree.heading("#2", text=" Y", anchor=tk.CENTER)
        # # Attach the function update_details to the act of selecting a value on the treeview
        # self.tree.bind("<<TreeviewSelect>>", self.update_details)
        # Configure the sizes of each column
        self.tree.column("#0", minwidth=1, width=1, stretch=tk.NO, anchor=tk.W)  # Column 0 (Name)
        self.tree.column("#1", minwidth=150, width=150, stretch=tk.YES, anchor=tk.CENTER)  # Column 1 (Value)
        self.tree.column("#2", minwidth=150, width=150, stretch=tk.YES, anchor=tk.CENTER)  # Column 1 (Value)
        # Pack the treeview
        self.tree.pack(side=tk.TOP, fill="both", expand=True)
        # Define possible colors for the treeview lines
        self.tree.tag_configure("orange", foreground="#FFAA50")
        self.tree.tag_configure("white", foreground="white")


        self.point_entry_frame = ttk.Frame(self.main_frame)
        self.point_entry_frame.pack(side=tk.TOP, pady=5)
        self.x_entry = tk.Entry(self.point_entry_frame , width=15)
        self.x_entry.pack(padx=5, side=tk.LEFT, fill="x")
        self.y_entry = tk.Entry(self.point_entry_frame , width=15)
        self.y_entry.pack(padx=5, side=tk.LEFT, fill="x")

        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(side=tk.TOP, pady=5)
        self.add_button = ttk.Button(self.buttons_frame, text="Add", padding=(3, 3), command=self.add_point)
        self.add_button.pack(padx=5, side=tk.LEFT)
        self.del_button = ttk.Button(self.buttons_frame, text="Delete", padding=(3, 3), command=self.del_point)
        self.del_button.pack(padx=5, side=tk.LEFT)
        self.compute_button = ttk.Button(self.buttons_frame, text="Compute", padding=(3, 3), command=self.poly_stimate)
        self.compute_button.pack(padx=5, side=tk.LEFT)


        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}


        self.coefs_label = ttk.Label(self.main_frame, text="")
        self.coefs_label.pack(pady=2, side=tk.TOP)


        # self.root.protocol("WM_DELETE_WINDOW", self.on_closing)



    def add_point(self):

        vx = self.x_entry.get()
        vy = self.y_entry.get()
        #self.tree.insert("", "end", text=vx, values=(vy), tags=("white",))
        self.tree.insert("", "end", text='', values=(vx,vy), tags=("white",))
        # self.tree.insert("", "end", values=(vx,vy), tags=("white",))

        return

    def del_point(self):
        # Get the selected item(s)
        selected_items = self.tree.selection()

        # Ensure an item is selected before attempting deletion
        if selected_items:
            # Delete the selected item(s)
            self.tree.delete(*selected_items)

    def poly_stimate(self):

        xv = []
        yv = []

        count = 0
        for item in self.tree.get_children():
            count = count+1
            item_text = self.tree.item(item, "values")
            #x = float(self.tree.item(item, "text"))
            #y = float(self.tree.item(item, "value")[0])

            print(self.tree.item(item, "value"))
            x = float(self.tree.item(item, "value")[0])
            y = float(self.tree.item(item, "value")[1])
            xv.append(x)
            yv.append(y)
        if(count<3):
            messagebox.showerror("Error", "Add at least 3 points")
            return
        else:
            A = []
            B = []
            for i in range(count):
                A.append([1.0, xv[i], xv[i]**2])
                B.append(yv[i])

            A = np.array(A)
            B = np.array(B)

            try:
                C = ( np.linalg.inv(A.transpose().dot(A)).dot(A.transpose()) ).dot(B)
                # A*c = B
                # A'*A*c = A'*B
                # c = inv(A'*A) * A'*B
            except:
                messagebox.showerror("Error", "Error computing coefficients.\nCheck the input values.")
                return


            # print("C: ", C)
            self.set_poly_text(C)



    def set_poly_text(self, c):

        #s = f'p(u) = '

        rv = []
        sig = []
        for i, v in enumerate(c):
            r = round(v*1000)/1000
            
            if r>=0:
                rv.append(str(abs(r)))
                if i>0:
                    sig.append(' + ')
                else:
                    sig.append(' ')
            else:
                rv.append(str(-r))
                sig.append(' - ')

        s = 'p(u) ='+sig[0]+rv[0]+sig[1]+rv[1]+'*u'+sig[2]+rv[2]+'*u^2'

        self.coefs_label.config(text=s)



            



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
    root.title("Polynomial estimation")
    # Define GUI window size
    root.geometry('300x350')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/poly_est_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    # app = PolyEstimatorGUI(root, True)
    app = PolyEstimatorGUI(root)

    # root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

