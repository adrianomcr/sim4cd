#!/usr/bin/env python3
# -*- coding:utf-8 -*-



import tkinter as tk
from tkinter import ttk, PhotoImage, filedialog
import os
import subprocess
from ttkthemes import ThemedTk
import shlex
import psutil

#class SimHomeApp(tk.Frame):
class SimHomeApp():

    def __init__(self, root_):
        # super().__init__(root)
        self.root = root_
        # self.pack()

        # Define a left panel
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=False)
        self.left_frame['width'] = 200
        self.name_l_label = ttk.Label(self.left_frame, text="Home")
        self.name_l_label.pack(pady=2)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.name_r_label = ttk.Label(self.right_frame, text="Status")
        self.name_r_label.pack(pady=2)



        try:
            image_path1 = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/quad.png'
            self.image1 = PhotoImage(file=image_path1)
            self.image_label1 = tk.Label(self.right_frame, image=self.image1)
            self.image_label1.pack(anchor="center", fill="both", expand=True)

        except Exception as e:
            print("An error occurred while displaying image:", e)


        self.file_path = False
        self.data = {}




        self.start_stop_frame = ttk.Frame(self.left_frame )
        self.start_stop_frame.pack(pady=10)

        # Start Button
        self.start_button = ttk.Button(self.start_stop_frame, text="Start Simulator", padding=(4, 4), command=self.start_command)
        self.start_button.pack(side=tk.LEFT,padx=10)

        # Stop Button
        self.stop_button = ttk.Button(self.start_stop_frame, text="Stop Simulator", padding=(4, 4), command=self.stop_command)
        self.stop_button.pack(side=tk.LEFT,padx=10)

        self.process = None  # Store the subprocess object






    def set_data(self, d, path):
        self.data = d
        self.file_path = path

    def get_data(self):
        return self.data










    def start_command(self):

        script_path = os.path.dirname(__file__)+"/../"
        # print("script_path: ", script_path)
        if self.process is None or self.process.poll() is not None:
            # Start the subprocess
            cmd = script_path+"start_sim.sh"
            if(self.file_path):
                cmd = cmd + " " + self.file_path

            print("Start command: ", cmd)

            log_file_path = '/tmp/start_sim.log'
            with open(log_file_path, "a") as log_file:
                # Create a subprocess, redirect stdout and stderr to the log file
                self.process = subprocess.Popen(
                    cmd,
                    stdout=log_file,  # Redirect stdout to the log file
                    stderr=subprocess.STDOUT,  # Redirect stderr to stdout (merged)
                    text=True,  # Interpret output as text (Python 3.5+)
                    shell=True
                )
            print("Command started.")



    def stop_command(self):

        # Handle keyboard interrupt (e.g., Ctrl+C)
        # Terminate the main subprocess and its child processes
        parent = psutil.Process(self.process.pid)
        for child in parent.children(recursive=True):
            child.terminate()
        parent.terminate()
        print("Command stopped.")






if __name__ == "__main__":
    root = ThemedTk(theme='black')
    root.title("Simulator home")
    app = SimHomeApp(root)
    root.mainloop()

