#!/usr/bin/env python3
"""
vehicle_tab.py
-----------
PyQt5 tab containing a VTK-based vehicle. Allows the user to set vehicle dynamic and geometric properties.
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QFrame,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QComboBox
)
import json
import zmq

from tab_vehicle.vehicle_scene import VTKVehicleSceneWidget
import utils as UT
from math import sqrt


class VehicleTab(QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data if shared_data is not None else {}

        # Load the .ui file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(script_dir, "vehicle_tab.ui"), self)

        # ----------------------------------------------------------------------
        # Access UI widgets via findChild(...)
        # Make sure these names match those in tab_geolocation.ui
        # ----------------------------------------------------------------------
        # self.frame_globe = self.findChild(QFrame, "vtkFrame")
        self.vtk_frame = self.findChild(type(self.vtkFrame), "vtkFrame")

        # return

        # Dynamics
        self.lineEdit_mass = self.findChild(QLineEdit, "lineEdit_mass")
        self.lineEdit_moi_xx = self.findChild(QLineEdit, "lineEdit_moi_xx")
        self.lineEdit_moi_yy = self.findChild(QLineEdit, "lineEdit_moi_yy")
        self.lineEdit_moi_zz = self.findChild(QLineEdit, "lineEdit_moi_zz")
        self.lineEdit_lin_drag = self.findChild(QLineEdit, "lineEdit_lin_drag")
        self.lineEdit_ang_drag = self.findChild(QLineEdit, "lineEdit_ang_drag")

        # Geometry
        self.label_act_id = self.findChild(QLabel,"label_act_id")
        self.comboBox_act_id = self.findChild(QComboBox,"comboBox_act_id")

        self.lineEdit_act_pos_x = self.findChild(QLineEdit,"lineEdit_act_pos_x")
        self.lineEdit_act_pos_y = self.findChild(QLineEdit,"lineEdit_act_pos_y")
        self.lineEdit_act_pos_z = self.findChild(QLineEdit,"lineEdit_act_pos_z")
        self.lineEdit_act_pos = [self.lineEdit_act_pos_x, self.lineEdit_act_pos_y, self.lineEdit_act_pos_z]

        self.lineEdit_act_dir_x = self.findChild(QLineEdit,"lineEdit_act_dir_x")
        self.lineEdit_act_dir_y = self.findChild(QLineEdit,"lineEdit_act_dir_y")
        self.lineEdit_act_dir_z = self.findChild(QLineEdit,"lineEdit_act_dir_z")
        self.lineEdit_act_dir = [self.lineEdit_act_dir_x, self.lineEdit_act_dir_y, self.lineEdit_act_dir_z]

        self.lineEdit_arm_base_x = self.findChild(QLineEdit,"lineEdit_arm_base_x")
        self.lineEdit_arm_base_y = self.findChild(QLineEdit,"lineEdit_arm_base_y")
        self.lineEdit_arm_base_z = self.findChild(QLineEdit,"lineEdit_arm_base_z")
        self.lineEdit_arm_base = [self.lineEdit_arm_base_x, self.lineEdit_arm_base_y, self.lineEdit_arm_base_z]

        self.lineEdit_body_size_x = self.findChild(QLineEdit,"lineEdit_body_size_x")
        self.lineEdit_body_size_y = self.findChild(QLineEdit,"lineEdit_body_size_y")
        self.lineEdit_body_size_z = self.findChild(QLineEdit,"lineEdit_body_size_z")
        self.lineEdit_body_size = [self.lineEdit_body_size_x, self.lineEdit_body_size_y, self.lineEdit_body_size_z]

        self.push_button_set_values = self.findChild(QPushButton, "pushButton_set_values")

        # Create a ZeroMQ context
        self.context = zmq.Context()

        # Create a PUB socket
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5575")

        # VTK setup in a separate function
        self.init_vtk_scene()

        # # ----------------------------------------------------------------------
        # # Connect signals
        # # ----------------------------------------------------------------------
        self.push_button_set_values.clicked.connect(self.set_values)

        self.comboBox_act_id.activated[int].connect(self.on_combo_changed)
        self.selected_actuator = None


    def on_tab_selected(self):
        self.update_widgets_data()


    def on_combo_changed(self, index):
        self.selected_actuator = index
        self.update_widgets_data()


    def update_widgets_data(self):
        if not self.shared_data['config'] is None:
            # Optional defaults for line edits:
            self.lineEdit_mass.setText(str(self.shared_data['config']['DYN_MASS']['value']))
            self.lineEdit_moi_xx.setText(str(self.shared_data['config']['DYN_MOI_XX']['value']))
            self.lineEdit_moi_yy.setText(str(self.shared_data['config']['DYN_MOI_YY']['value']))
            self.lineEdit_moi_zz.setText(str(self.shared_data['config']['DYN_MOI_ZZ']['value']))
            self.lineEdit_lin_drag.setText(str(self.shared_data['config']['DYN_DRAG_V']['value']))
            self.lineEdit_ang_drag.setText(str(self.shared_data['config']['DYN_DRAG_W']['value']))

            self.label_act_id.hide()
            self.comboBox_act_id.clear()
            number_of_actuators = self.shared_data['config']['VEH_ACT_NUM']['value']
            self.comboBox_act_id.addItems(["Actuator "+str(k) for k in range(number_of_actuators)])

            if (self.selected_actuator):
                if(self.selected_actuator >= number_of_actuators):
                    self.selected_actuator = 0
            else:
                self.selected_actuator = 0

            self.comboBox_act_id.setCurrentIndex(self.selected_actuator) 

            letters = ['X','Y','Z']

            for k in range(3):
                self.lineEdit_act_pos[k].setText(str(self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_POS_{letters[k]}']['value']))
                self.lineEdit_act_dir[k].setText(str(self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_DIR_{letters[k]}']['value']))
                self.lineEdit_arm_base[k].setText(str(self.shared_data['config'][f'VIZ_ACT{self.selected_actuator}_BASE_{letters[k]}']['value']))
                self.lineEdit_body_size[k].setText(str(self.shared_data['config'][f'VIZ_SIZE_{letters[k]}']['value']))

            # Update visualization
            self.socket.send_string(json.dumps(self.shared_data['config']))


    def init_vtk_scene(self):
        """
        Create and embed a VTK RenderWindowInteractor in the frameGlobe widget,
        then display a drone with the configured geometry
        """

        # Create our custom VTK widget and add it to the frame's layout
        self.vtk_scene_widget = VTKVehicleSceneWidget(parent=self.vtk_frame, data=self.shared_data['config'])
        self.vtk_frame.layout().addWidget(self.vtk_scene_widget)
        
        return


    def set_values(self):

        # Update data
        if (not UT.validate_value(self.lineEdit_mass.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid mass.")
            return
        if (not UT.validate_value(self.lineEdit_moi_xx.text(),'float')):            
            QMessageBox.critical(self, "Error", "Invalid moment of inertia in X.")
            return
        if (not UT.validate_value(self.lineEdit_moi_yy.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid moment of inertia in Y.")
            return
        if (not UT.validate_value(self.lineEdit_moi_zz.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid moment of inertia in Z.")
            return
        if (not UT.validate_value(self.lineEdit_lin_drag.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid linea drag.")
            return
        if (not UT.validate_value(self.lineEdit_ang_drag.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid angular drag.")
            return

        letters = ['X', 'Y', 'Z']
        for k in range(3):
            if (not UT.validate_value(self.lineEdit_act_pos[k].text(),'float')):
                QMessageBox.critical(self, "Error", f"Invalid actuator {self.selected_actuator} position {letters[k]}.")
                return
            if (not UT.validate_value(self.lineEdit_act_dir[k].text(),'float')):
                QMessageBox.critical(self, "Error", f"Invalid actuator {self.selected_actuator} direction {letters[k]}.")
                return
            if (not UT.validate_value(self.lineEdit_arm_base[k].text(),'float')):
                QMessageBox.critical(self, "Error", f"Invalid actuator {self.selected_actuator} arm base {letters[k]}.")
                return
            if (not UT.validate_value(self.lineEdit_body_size[k].text(),'float')):
                QMessageBox.critical(self, "Error", f"Invalid body size {letters[k]}.")
                return

        self.shared_data['config']['DYN_MASS']['value'] = UT.parse_value(self.lineEdit_mass.text(),'float')
        self.shared_data['config']['DYN_MOI_XX']['value'] = UT.parse_value(self.lineEdit_moi_xx.text(),'float')
        self.shared_data['config']['DYN_MOI_YY']['value'] = UT.parse_value(self.lineEdit_moi_yy.text(),'float')
        self.shared_data['config']['DYN_MOI_ZZ']['value'] = UT.parse_value(self.lineEdit_moi_zz.text(),'float')
        self.shared_data['config']['DYN_DRAG_V']['value'] = UT.parse_value(self.lineEdit_lin_drag.text(),'float')
        self.shared_data['config']['DYN_DRAG_W']['value'] = UT.parse_value(self.lineEdit_ang_drag.text(),'float')

        for k in range(3):
            self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_POS_{letters[k]}']['value'] = UT.parse_value(self.lineEdit_act_pos[k].text(),'float')
            self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_DIR_{letters[k]}']['value'] = UT.parse_value(self.lineEdit_act_dir[k].text(),'float')
            self.shared_data['config'][f'VIZ_ACT{self.selected_actuator}_BASE_{letters[k]}']['value'] = UT.parse_value(self.lineEdit_arm_base[k].text(),'float')
            self.shared_data['config'][f'VIZ_SIZE_{letters[k]}']['value'] = UT.parse_value(self.lineEdit_body_size[k].text(),'float')
        
        self.normalize_act_dir()

        # Update visualization
        self.socket.send_string(json.dumps(self.shared_data['config']))

        return


    def normalize_act_dir(self):

        letters = ['X', 'Y', 'Z']
        d = []
        dir_norm = 0
        for k in range(3):
            d.append(self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_DIR_{letters[k]}']['value'])
            dir_norm = dir_norm + d[k]**2
        dir_norm = sqrt(dir_norm)

        if dir_norm < 1e-8:
            d = [0,0,1]
            dir_norm = 1
            QMessageBox.critical(self, "Error", "Input direction is not valid. Defaulting configuration to [0,0,1]. Set a non zero vector and reset values.")

        for k in range(3):
            self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_DIR_{letters[k]}']['value'] = round(d[k]/dir_norm,6)

        for k in range(3):
            self.lineEdit_act_dir[k].setText(str(self.shared_data['config'][f'VEH_ACT{self.selected_actuator}_DIR_{letters[k]}']['value']))


# ------------------------------------------------------------------------------
# Standalone test
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = QMainWindow()
    tab = VehicleTab()
    window.setCentralWidget(tab)
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())


