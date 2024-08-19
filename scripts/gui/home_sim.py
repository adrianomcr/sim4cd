#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to start and stop the simulator

import tkinter as tk
from tkinter import ttk, PhotoImage, filedialog
import os
import subprocess
from ttkthemes import ThemedTk
import psutil

class SimHomeApp():
    """
    Class that defines a GUI for starting and stopping the simulator
    """

    def __init__(self, root_):
        """
        Constructor for the SimHomeApp class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
        """

        # Set the root variable
        self.root = root_

        # Define a left panel
        self.left_frame = ttk.Frame(self.root, width=200)
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=False)
        self.name_l_label = ttk.Label(self.left_frame, text="Home")
        self.name_l_label.pack(pady=2)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.name_r_label = ttk.Label(self.right_frame, text="Status")
        self.name_r_label.pack(pady=2)

        # Add an image to the right panel
        try:
            image_path = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/quad.png'
            self.image = PhotoImage(file=image_path)
            self.image_label = tk.Label(self.right_frame, image=self.image)
            self.image_label.pack(anchor="center", fill="both", expand=True)
        except Exception as e:
            print("An error occurred while displaying image:", e)

        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}

        # Create a subframe for the start stop buttons
        self.start_stop_frame = ttk.Frame(self.left_frame )
        self.start_stop_frame.pack(pady=10)
        # Start Button
        self.start_button = ttk.Button(self.start_stop_frame, text="Start Simulator", padding=(4, 4), command=self.start_command)
        self.start_button.pack(side=tk.LEFT,padx=10)
        # Stop Button
        self.stop_button = ttk.Button(self.start_stop_frame, text="Stop Simulator", padding=(4, 4), command=self.stop_command)
        self.stop_button.pack(side=tk.LEFT,padx=10)

        self.sim_status = ttk.Label(self.left_frame, text="Simulator idle", foreground="#0000FF", font=("Helvetica", 18))
        self.sim_status.pack(pady=2)

        # Variable to store the subprocess object
        self.process = None


    def start_command(self):
        """
        Function to start the simulator in a subprocess
        """

        # Get the path of the start_sim.sh script
        script_path = os.path.dirname(__file__)+"/../sim4cd/"
        # Check the status of the process before start
        if self.process is None or self.process.poll() is not None:
            # Create the string command to start the simulator
            cmd = script_path+"start_sim.sh"
            if(self.file_path):
                cmd = cmd + " " + self.file_path

            # Define a log file in the temporary folder
            log_file_path = '/tmp/start_sim.log'
            # Start a subprocess to run the simulator
            with open(log_file_path, "a") as log_file:
                # Create a subprocess, redirect stdout and stderr to the log file
                self.process = subprocess.Popen(
                    cmd.split(),                # Command string splitted
                    stdout=log_file,            # Redirect stdout to the log file
                    stderr=subprocess.STDOUT,   # Redirect stderr to stdout (merged)
                    text=True,                  # Interpret output as text (Python 3.5+)
                )
            
            # Update label to show that simulator is running
            self.sim_status.configure(text='Simulator running', foreground="#00FF00")


    def stop_command(self):
        """
        Function to stop the simulator subprocess
        """

        # Return is there is no subprocess
        if (self.process is None):
            return

        # Terminate the simulator subprocess and all its children
        parent = psutil.Process(self.process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()

        # Indicate that there is no subprocess running
        self.process = None

        # Update label to show that simulator is idle
        self.sim_status.configure(text='Simulator idle', foreground="#0000FF")




    def set_data(self, d, path):
        """
        Set data dictionary and the file path of the gui
        """
        self.data = d
        self.file_path = path


    def get_data(self):
        """
        Return the current data dictionary that the gui is using
        """
        return self.data


    def viz_return(self):
        """
        Function to update the visualization of the gui
        """
        # Do nothing for this gui
        return


    def on_closing(self):
        """
        Function to handle action when window is closed
        """
        # Stop simulator if it is running
        self.stop_command()
        # Destroy the window
        self.root.quit()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.destroy()


if __name__ == "__main__":
    """
    Main to run a detached SimHomeApp window
    """

    # Define root GUI window
    root = ThemedTk(theme='black')
    # Define GUI title
    root.title("Simulator home")
    # Define GUI window size
    app = SimHomeApp(root)

    # Call the function to terminate the subprocess when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

