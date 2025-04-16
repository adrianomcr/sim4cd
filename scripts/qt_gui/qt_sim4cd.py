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

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QAction, QMessageBox, QFileDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from tab_home.home_tab import HomeTab

from tab_all_params.all_params_tab import AllParamsTab
from tab_geolocation.geolocation_tab import GeolocationTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Copter Simulator")

        # Shared dictionary for all tabs
        self.shared_data = {
            "simulator_status": "idle",
            "config_file_path": None,
            "config": None,
            "feature_a": False,
            "feature_b": False,
            "last_interaction": ""
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
        self.tab_all_params = AllParamsTab(shared_data=self.shared_data)
        
        
        # Add them to the QTabWidget
        self.tabs.addTab(self.tab_home, "Simulate")
        self.tabs.addTab(self.tab_geolocation, "Geolocation")
        self.tabs.addTab(self.tab_all_params, "All parameters list")

        # # --- Second (top-level) tab with nested tabs ---
        # config_tab = QWidget()
        # config_layout = QVBoxLayout()
        
        # # Create a nested tab widget inside the config tab
        # bkp_tabs = QTabWidget()
        
        # self.tab_config = ConfigTab(shared_data=self.shared_data)
        # self.tab_interaction = InteractionTab(shared_data=self.shared_data)
        
        # # Add the sub-tabs to the nested tab widget
        # bkp_tabs.addTab(self.tab_config, "Configuration")
        # bkp_tabs.addTab(self.tab_interaction, "Interaction")

        # # Place the nested tabs inside the config tab
        # config_layout.addWidget(bkp_tabs)
        # config_tab.setLayout(config_layout)

        # # Add the two main tabs
        # self.tabs.addTab(config_tab, "BKP tabs")

        # self.showFullScreen()



        # Connect tab selection signal
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Trigger initial selection logic for the first tab
        if hasattr(self.tab_home, 'on_tab_selected'):
            self.tab_home.on_tab_selected()


    def on_tab_changed(self, index):
        # Get the current widget (selected tab)
        current_widget = self.tabs.widget(index)

        # Check if the widget has the on_tab_selected method and call it
        if hasattr(current_widget, 'on_tab_selected'):
            current_widget.on_tab_selected()
        else:
            print("Not available")


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


    def load_config(self, path):
        try:
            # Store the path and display it
            self.shared_data['config_file_path'] = path

            # Load JSON data
            with open(path, "r") as json_file:
                self.shared_data['config'] = json.load(json_file)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON file:\n{str(e)}")


    def open_config(self):
        """
        Function to show a file dialog to load a JSON file in PyQt5.
        """

        print("Open config")
        options = QFileDialog.Options()
        path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)

        if path:
            self.load_config(path)


    def save_config(self):
        # If we already have a path, save to that file
        current_path = self.shared_data.get("config_file_path")
        if current_path:
            try:
                with open(current_path, "w") as json_file:
                    json.dump(self.shared_data.get('config', {}), json_file, indent=4)
                QMessageBox.information(self, "Success", f"Successfully saved to:\n{current_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save JSON file:\n{str(e)}")
        else:
            self.saveas_config()


    def saveas_config(self):
        # Prompt the user for a file path
        options = QFileDialog.Options()
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json);;All Files (*)", options=options)

        if path:
            try:
                with open(path, "w") as json_file:
                    json.dump(self.shared_data.get('config', {}), json_file, indent=4)
                self.shared_data['config_file_path'] = path
                QMessageBox.information(self, "Success", f"Successfully saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save JSON file:\n{str(e)}")



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
