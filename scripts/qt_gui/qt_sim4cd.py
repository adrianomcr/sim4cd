#!/usr/bin/env python3
"""
qt_gui.py
-------
Main application that pulls together the three tabs (HomeTab, ConfigTab, InteractionTab)
into one QTabWidget inside a QMainWindow, all using a shared_data dictionary.
"""

import sys
import webbrowser
import json
import os
import signal

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QAction, QMessageBox, QFileDialog, QVBoxLayout, QLabel, QSplashScreen
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer

# The tabs import each other as top level modules ("tab_home.home_tab", "utils") and the simulator
# as "sim4cd.*", so both this directory and "scripts/" have to be importable, no matter whether the
# GUI was started as a script or through the sim4cd-gui entry point.
for _path in (os.path.dirname(os.path.abspath(__file__)),
              os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from tab_home.home_tab import HomeTab

from tab_geolocation.geolocation_tab import GeolocationTab
from tab_vehicle.vehicle_tab import VehicleTab
from tab_actuators.actuators_tab import ActuatorsTab
from tab_all_params.all_params_tab import AllParamsTab
import utils as UT

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Copter Simulator")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/icon.png")))  # Sets the window's icon



        # Shared dictionary for all tabs
        self.shared_data = {
            "simulator_status": "idle",
            "config_file_path": None,
            "config": None,
            "config_dirty": False,
            "feature_a": False,
            "feature_b": False,
            "last_interaction": "",
            # Optional hook used by utils/tabs (via shared_data only) to refresh
            # the title when the loaded file or unsaved-edit flag changes.
            "on_config_state_changed": self.update_window_title,
        }

        self.add_menubar()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.load_config(os.path.join(script_dir, "../../config/sim_params.json"))

        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        # self.tabs.setTabPosition(QTabWidget.West)

        # Create each tab's widget
        self.tab_home = HomeTab(shared_data=self.shared_data)
        self.tab_geolocation = GeolocationTab(shared_data=self.shared_data)
        self.tab_vehicle = VehicleTab(shared_data=self.shared_data)
        self.tab_actuators = ActuatorsTab(shared_data=self.shared_data)
        self.tab_all_params = AllParamsTab(shared_data=self.shared_data)
        
        
        # Add them to the QTabWidget
        self.tabs.addTab(self.tab_home, "Simulate")
        # self.tabs.addTab(self.tab_geolocation, "Geolocation")
        # self.tabs.addTab(self.tab_vehicle, "Vehicle")
        # self.tabs.addTab(self.tab_actuators, "Actuators")
        # self.tabs.addTab(self.tab_all_params, "All parameters list")


        self.sim_config_tab = QWidget()
        config_layout = QVBoxLayout()
        self.sim_config_tabs = QTabWidget()
        # self.sim_config_tabs.setTabPosition(QTabWidget.West)
        self.sim_config_tabs.addTab(self.tab_geolocation, "Geolocation")
        self.sim_config_tabs.addTab(self.tab_vehicle, "Vehicle")
        self.sim_config_tabs.addTab(self.tab_actuators, "Actuators")
        self.sim_config_tabs.addTab(self.tab_all_params, "All parameters list")
        config_layout.addWidget(self.sim_config_tabs)
        self.sim_config_tab.setLayout(config_layout)
        self.tabs.addTab(self.sim_config_tab, "Simulation config")

        # # self.showFullScreen()

        # Connect tab selection signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.sim_config_tabs.currentChanged.connect(self.on_tab_changed)

        # Trigger initial selection logic for the first tab
        if hasattr(self.tab_home, 'on_tab_selected'):
            self.tab_home.on_tab_selected()




    def on_tab_changed(self, index):

        # Get the current widget (selected tab)
        tabs_id = self.tabs.currentIndex() 
        if tabs_id == 0:
            current_widget = self.tabs.currentWidget()
        elif tabs_id == 1:
            current_widget = self.sim_config_tabs.currentWidget()

        # Check if the widget has the on_tab_selected method and call it
        if hasattr(current_widget, 'on_tab_selected'):
            current_widget.on_tab_selected()
        else:
            print("on_tab_selected method is not available")



    def keyPressEvent(self, event):
        """Toggle fullscreen when F11 is pressed"""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()


    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()  # Exit fullscreen
        else:
            self.showFullScreen()  # Enter fullscreen


    def open_source_code(self):
        if (not webbrowser.open_new_tab("https://github.com/adrianomcr/sim4cd")):
            msg = QMessageBox()
            msg.setWindowTitle("Source code")
            msg.setText('Unable to detect a web browser to launch <a href="https://github.com/adrianomcr/sim4cd">github.com/adrianomcr/sim4cd</a>.')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


    def open_about(self):
        msg = QMessageBox()
        msg.setWindowTitle("sim4cd")
        msg.setText("This is Sim4CD, a simulator for a custom drone. It is designed to allow users to easily simulate a drone with specific properties. Use this GUI to enter the properties of the drone you want to simulate.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


    def add_menubar(self):
        # Create the menu bar
        menubar = self.menuBar()

        # Add "File" menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_config)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)

        saveas_action = QAction("SaveAs", self)
        saveas_action.triggered.connect(self.saveas_config)
        file_menu.addAction(saveas_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)  # Close app when clicking Exit
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Add "View" menu
        view_menu = menubar.addMenu("View")

        fullscreen_action = QAction("Toggle fullscreen (F11)", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Add "Help" menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.open_about)
        help_menu.addAction(about_action)

        source_action = QAction("Source code", self)
        source_action.triggered.connect(self.open_source_code)
        help_menu.addAction(source_action)


    def update_window_title(self):
        """Show the loaded filename, with '*' if parameters are unsaved."""
        path = self.shared_data.get("config_file_path")
        name = os.path.basename(path) if path else "untitled"
        dirty = "*" if self.shared_data.get("config_dirty") else ""
        self.setWindowTitle(f"Custom Copter Simulator - {name}{dirty}")


    def load_config(self, path):
        try:
            # Store the path and display it
            self.shared_data['config_file_path'] = path

            # Load JSON data
            with open(path, "r") as json_file:
                self.shared_data['config'] = json.load(json_file)

            self.shared_data['config_dirty'] = False
            self.update_window_title()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file:\n{str(e)}")


    def open_config(self):
        """
        Function to show a file dialog to load a JSON file in PyQt5.
        """

        if not UT.prompt_save_if_dirty(self, self.shared_data, context="open"):
            return

        print("Open config")
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)

        if path:
            self.load_config(path)


    def save_config(self):
        UT.save_shared_config(self, self.shared_data)


    def saveas_config(self):
        UT.save_shared_config(self, self.shared_data, force_dialog=True)


    def closeEvent(self, event):
        if not UT.prompt_save_if_dirty(self, self.shared_data, context="close"):
            event.ignore()
            return

        confirm_close = self.tab_home.close_when_running_action()
        if not confirm_close:
            event.ignore()
            return

        event.accept()

def main():
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon = QIcon(os.path.join(script_dir, "resources/icon.png"))
    app.setWindowIcon(icon)


    # Create and show splash screen
    splash_pix = QPixmap(os.path.join(script_dir, "resources/splash_image.png")).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Replace with your image path
    print(os.path.join(script_dir, "resources/splash_image.png"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    splash.showMessage("Loading...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)

    window = MainWindow()
    window.setWindowIcon(icon)
    # window.show()
    QTimer.singleShot(1000, lambda: (splash.close(), window.showMaximized()))
    # QTimer.singleShot(1000, lambda: (splash.close(), window.showMaximized()))
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
