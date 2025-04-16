#!/usr/bin/env python3
"""
geolocation_tab.py
-----------
PyQt5 tab containing a VTK-based globe. Allows the user to set simulation location and local magnetic field.
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
    QLabel
)
import json
import zmq
from magnetic_field_calculator import MagneticFieldCalculator
from datetime import datetime

from tab_geolocation.globe_scene import VTKGlobeSceneWidget
import utils as UT


class GeolocationTab(QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data if shared_data is not None else {}

        # Load the .ui file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(script_dir, "geolocation_tab.ui"), self)

        # ----------------------------------------------------------------------
        # Access UI widgets via findChild(...)
        # Make sure these names match those in tab_geolocation.ui
        # ----------------------------------------------------------------------
        # self.frame_globe = self.findChild(QFrame, "vtkFrame")
        self.vtk_frame = self.findChild(type(self.vtkFrame), "vtkFrame")

        self.line_edit_latitude = self.findChild(QLineEdit, "lineEdit_lat")
        self.line_edit_longitude = self.findChild(QLineEdit, "lineEdit_lon")
        self.line_edit_altitude = self.findChild(QLineEdit, "lineEdit_alt")

        self.line_edit_mag_east = self.findChild(QLineEdit, "lineEdit_mag_east")
        self.line_edit_mag_north = self.findChild(QLineEdit, "lineEdit_mag_north")
        self.line_edit_mag_up = self.findChild(QLineEdit, "lineEdit_mag_up")

        self.push_button_set_values = self.findChild(QPushButton, "pushButton_set_values")
        self.push_button_compute = self.findChild(QPushButton, "pushButton_compute_field")
        self.push_button_apply = self.findChild(QPushButton, "pushButton_apply_field")

        self.label_computed_field = self.findChild(QLabel, "label_computed_field")
        # Initialize the variable to store the estimated local magnetic field
        self.estimated_mag_field = None

        # Create a ZeroMQ context
        self.context = zmq.Context()

        # Create a PUB socket
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5565")

        # VTK setup in a separate function
        self.init_vtk_scene()

        # if self.shared_data['config']:
        #     LLA = [self.shared_data['config']['SENS_LAT_ORIGIN']['value'],
        #            self.shared_data['config']['SENS_LON_ORIGIN']['value'],
        #            self.shared_data['config']['SENS_ALT_ORIGIN']['value']]
        #     # Optional defaults for line edits:
        #     self.line_edit_latitude.setText(str(LLA[0]))
        #     self.line_edit_longitude.setText(str(LLA[1]))
        #     self.line_edit_altitude.setText(str(LLA[2]))

        #     MAG = [self.shared_data['config']['SENS_MAG_FIELD_E']['value'],
        #            self.shared_data['config']['SENS_MAG_FIELD_N']['value'],
        #            self.shared_data['config']['SENS_MAG_FIELD_U']['value']]
        #     self.line_edit_mag_east.setText(str(MAG[0]))
        #     self.line_edit_mag_north.setText(str(MAG[1]))
        #     self.line_edit_mag_up.setText(str(MAG[2]))

        #     # Update visualization
        #     self.socket.send_string(json.dumps({'LLA':LLA, 'MAG':MAG}))

        # ----------------------------------------------------------------------
        # Connect signals
        # ----------------------------------------------------------------------
        self.push_button_set_values.clicked.connect(self.set_values)
        self.push_button_compute.clicked.connect(self.compute_local_field)
        self.push_button_apply.clicked.connect(self.apply_computed_field)

    def on_tab_selected(self):
        if self.shared_data['config']:
            LLA = [self.shared_data['config']['SENS_LAT_ORIGIN']['value'],
                   self.shared_data['config']['SENS_LON_ORIGIN']['value'],
                   self.shared_data['config']['SENS_ALT_ORIGIN']['value']]
            # Optional defaults for line edits:
            self.line_edit_latitude.setText(str(LLA[0]))
            self.line_edit_longitude.setText(str(LLA[1]))
            self.line_edit_altitude.setText(str(LLA[2]))

            MAG = [self.shared_data['config']['SENS_MAG_FIELD_E']['value'],
                   self.shared_data['config']['SENS_MAG_FIELD_N']['value'],
                   self.shared_data['config']['SENS_MAG_FIELD_U']['value']]
            self.line_edit_mag_east.setText(str(MAG[0]))
            self.line_edit_mag_north.setText(str(MAG[1]))
            self.line_edit_mag_up.setText(str(MAG[2]))

            # Update visualization
            self.socket.send_string(json.dumps({'LLA':LLA, 'MAG':MAG}))

    def init_vtk_scene(self):
        """
        Create and embed a VTK RenderWindowInteractor in the frameGlobe widget,
        then display a textured sphere for the Earth.
        """

        if self.shared_data['config']:
            LLA = [self.shared_data['config']['SENS_LAT_ORIGIN']['value'],
                    self.shared_data['config']['SENS_LON_ORIGIN']['value'],
                    self.shared_data['config']['SENS_ALT_ORIGIN']['value']]
        else:
            LLA = None

        # Create our custom VTK widget and add it to the frame's layout
        self.vtk_scene_widget = VTKGlobeSceneWidget(parent=self.vtk_frame, lla=LLA)
        self.vtk_frame.layout().addWidget(self.vtk_scene_widget)
        
        return


    def get_values_from_widget(self):
        # Update data
        if (not UT.validate_value(self.line_edit_latitude.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid latitude.")
            return False, [], []
        if (not UT.validate_value(self.line_edit_longitude.text(),'float')):            
            QMessageBox.critical(self, "Error", "Invalid longitude.")
            return False, [], []
        if (not UT.validate_value(self.line_edit_altitude.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid altitude.")
            return False, [], []
        if (not UT.validate_value(self.line_edit_mag_east.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid East magnetic field.")
            return False, [], []
        if (not UT.validate_value(self.line_edit_mag_north.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid North magnetic field.")
            return False, [], []
        if (not UT.validate_value(self.line_edit_mag_up.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid Up magnetic field.")
            return False, [], []

        LLA = [UT.parse_value(self.line_edit_latitude.text(),'float'),
               UT.parse_value(self.line_edit_longitude.text(),'float'),
               UT.parse_value(self.line_edit_altitude.text(),'float')]
        mag = [UT.parse_value(self.line_edit_mag_east.text(),'float'),
               UT.parse_value(self.line_edit_mag_north.text(),'float'),
               UT.parse_value(self.line_edit_mag_up.text(),'float')]
    
        return True, LLA, mag

    def set_values(self):

        valid, LLA, mag = self.get_values_from_widget()
        if (not valid):
            # QMessageBox.critical(self, "Error", "Invalid inputs.")
            return

        self.shared_data['config']['SENS_LAT_ORIGIN']['value'] = LLA[0]
        self.shared_data['config']['SENS_LON_ORIGIN']['value'] = LLA[1]
        self.shared_data['config']['SENS_ALT_ORIGIN']['value'] = LLA[2]

        self.shared_data['config']['SENS_MAG_FIELD_E']['value'] = mag[0]
        self.shared_data['config']['SENS_MAG_FIELD_N']['value'] = mag[1]
        self.shared_data['config']['SENS_MAG_FIELD_U']['value'] = mag[2]

        # Update visualization
        self.socket.send_string(json.dumps({'LLA':LLA}))


    def compute_local_field(self):
        """
        Function to compute the magnetic field at the origin geolocation set on the entry boxes

        Parameters:
            *args (list): Unused arguments passed by the function when it is binded to a widget action.
        """

        print("Compute local field clicked.")

        # # Return if there is parameter file loaded
        # if(not self.shared_data):
        #     QMessageBox.critical(self, "Error", "There is data parameter file loaded")
        #     return
        
        # Use the label to display that the magnetic field is being computed
        self.label_computed_field.setText("Computing magnetic field ...\n\n\n\n")
        QApplication.processEvents()

        try:
            # Create a MagneticFieldCalculator object
            calculator = MagneticFieldCalculator(
                model='wmm',
                revision='2020',
                sub_revision='2'
            )
            print("A")
            # Get the geolocation where the field will be computed
            valid, LLA, _ = self.get_values_from_widget()
            if (not valid):
                QMessageBox.critical(self, "Error", "Invalid inputs for LLA.")
                return
            # Compute the magnetic field
            result = calculator.calculate(
                latitude=LLA[0],                    # latitude in degrees
                longitude=LLA[1],                   # longitude in degrees
                altitude=LLA[2]/1000.0,             # altitude in km
                date=datetime.now().strftime("%Y-%m-%d")    # date
            )
            print("B")
            # Store the computed magnetic field in the ENU frame in Gauss
            self.estimated_mag_field = [
                round(result['field-value']['east-intensity']['value']*1e-5,8),
                round(result['field-value']['north-intensity']['value']*1e-5,8),
                round(-result['field-value']['vertical-intensity']['value']*1e-5,8)
            ]
            # Update the label that displays the computed field
            result_str = ("[lat,lon,alt] = [%.3f°, %.3f°, %.0fm]\n\n  Field East: %.5f [Gauss]\nField North: %.5f [Gauss]\n    Field Up: %.5f [Gauss]" % tuple(LLA+self.estimated_mag_field))
            self.label_computed_field.setText(result_str)
            print("D")
        except:
            # Use the label to display that there was an error in the magnetic field computation
            # self.estimated_mag_label.config(text="Error in the computation of magnetic field\n\n\n\n")
            # self.root.update()
            print("E")
            return

    def apply_computed_field(self):
        print("Apply computed field clicked.")

        # Return if there is no estimated magnetic field
        if(not self.estimated_mag_field):
            QMessageBox.critical(self, "Error", "There is no magnetic field computed")
            return
        
        self.line_edit_mag_east.setText(str(self.estimated_mag_field[0]))
        self.line_edit_mag_north.setText(str(self.estimated_mag_field[1]))
        self.line_edit_mag_up.setText(str(self.estimated_mag_field[2]))


# ------------------------------------------------------------------------------
# Standalone test
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = QMainWindow()
    tab = GeolocationTab()
    window.setCentralWidget(tab)
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())


