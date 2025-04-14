#!/usr/bin/env python3
"""
home_tab.py
-----------
Defines the "Home" tab widget that includes the embedded VTK render window,
loading its UI layout from home_tab.ui.
Allows running standalone if needed.
"""
import sys
import os
import subprocess
import psutil

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
# Import the new VTK widget
from tab_home.main_scene import VTKMainSceneWidget


class HomeTab(QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data if shared_data is not None else {}

        # Load the .ui file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(script_dir,"home_tab.ui"), self)

        # Now we can access widgets by the names set in tab_home.ui
        self.btn_start = self.findChild(type(self.btnStart), "btnStart")
        self.btn_stop = self.findChild(type(self.btnStop), "btnStop")
        self.status_label = self.findChild(type(self.statusLabel), "statusLabel")

        # The frame where we'll insert the QVTKRenderWindowInteractor
        self.vtk_frame = self.findChild(type(self.vtkFrame), "vtkFrame")
        
        # Instead of directly doing VTK setup here, we just embed our custom widget
        self.init_vtk_scene()

        self.process = None

        # Connect signals
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)

    def init_vtk_scene(self):
        
        # Create our custom VTK widget and add it to the frame's layout
        self.vtk_scene_widget = VTKMainSceneWidget(parent=self.vtk_frame, config=self.shared_data['config'])
        self.vtk_frame.layout().addWidget(self.vtk_scene_widget)
        

    def on_start_clicked(self):

        # Get the path of the start_sim.sh script
        script_path = os.path.dirname(__file__)+"/../../sim4cd"
        # Check the status of the process before start
        if self.process is None or self.process.poll() is not None:
            # Create the string command to start the simulator
            cmd = os.path.join(script_path,"start_sim.sh")
            if(self.shared_data['config_file_path']):
                cmd = cmd + " " + self.shared_data['config_file_path']
                # print("self.shared_data['config_file_path']: ", self.shared_data['config_file_path'])
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText('Missing simulator configuration file. Please load a config file.')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

            # # Define a log file in the temporary folder
            # log_file_path = '/tmp/start_sim.log'
            # # Start a subprocess to run the simulator
            # with open(log_file_path, "a") as log_file:
            #     # Create a subprocess, redirect stdout and stderr to the log file
            #     self.process = subprocess.Popen(
            #         cmd.split(),                # Command string splitted
            #         stdout=log_file,            # Redirect stdout to the log file
            #         stderr=subprocess.STDOUT,   # Redirect stderr to stdout (merged)
            #         text=True,                  # Interpret output as text (Python 3.5+)
            #     )
            self.process = subprocess.Popen(
                    cmd.split(),                # Command string splitted
                    stderr=subprocess.STDOUT,   # Redirect stderr to stdout (merged)
                    text=True,                  # Interpret output as text (Python 3.5+)
                )
            
            self.shared_data["simulator_status"] = "running"
            self.status_label.setText("Simulator running")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")


    def on_stop_clicked(self):

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

        self.shared_data["simulator_status"] = "stopped"
        self.status_label.setText("Simulator stopped")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")



# Standalone runner
if __name__ == "__main__":
    app = QApplication(sys.argv)
    shared_data = {"simulator_status": "idle", "config_file_path": None, "config": None}
    main_window = QMainWindow()
    home_tab = HomeTab(shared_data=shared_data)
    main_window.setCentralWidget(home_tab)
    main_window.setWindowTitle("Home Tab Standalone")
    main_window.show()
    sys.exit(app.exec_())

