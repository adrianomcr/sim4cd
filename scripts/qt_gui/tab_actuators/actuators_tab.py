#!/usr/bin/env python3
"""
actuators_tab.py
-----------
PyQt5 tab containing a plot. Allows the user to set actuator properties.
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
    QComboBox,
    QWidget,
    QStyle
)
import json
import zmq

from tab_actuators.polynomial import PolyEstimatorGUI
import sim4cd.polynomial as POLY
import utils as UT
from math import sqrt
import numpy as np



import pyqtgraph as pg
# pg.setConfigOption('background', '#F02124')
pg.setConfigOptions(background='#0D1933', foreground='w')  # white axes / text


class ActuatorsTab(QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data if shared_data is not None else {}

        # Ensure shared_data has the needed keys
        if 'config' not in self.shared_data:
            self.shared_data['config'] = None

        # Load the .ui file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(script_dir, "actuators_tab.ui"), self)

        # ----------------------------------------------------------------------
        # Access UI widgets via findChild(...)
        # Make sure these names match those in actuators_tab.ui
        # ----------------------------------------------------------------------
        # Actuator dynamics
        self.label_act_id = self.findChild(QLabel,"label_act_id")
        self.comboBox_act_id = self.findChild(QComboBox,"comboBox_act_id")
        self.lineEdit_timeCte = self.findChild(QLineEdit,"lineEdit_timeCte")
        self.lineEdit_MOI = self.findChild(QLineEdit,"lineEdit_MOI")
        self.comboBox_spin = self.findChild(QComboBox,"comboBox_spin")

        # Actuator curve maps
        self.label_curveType = self.findChild(QLabel,"label_curveType")
        self.comboBox_curveType = self.findChild(QComboBox,"comboBox_curveType")
        self.lineEdit_coeffA = self.findChild(QLineEdit,"lineEdit_coeffA")
        self.lineEdit_coeffB = self.findChild(QLineEdit,"lineEdit_coeffB")
        self.lineEdit_coeffC = self.findChild(QLineEdit,"lineEdit_coeffC")
        self.lineEdit_coeff = [self.lineEdit_coeffA, self.lineEdit_coeffB, self.lineEdit_coeffC]

        self.push_button_set_values = self.findChild(QPushButton, "pushButton_set_values")

        self.pushButton_applyEstimation = self.findChild(QPushButton, "pushButton_applyEstimation")
        self.pushButton_applyEstimation.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))

        # locate the placeholder
        container = self.findChild(QWidget, "widget_polynomialEstimator")

        # build and insert the estimator
        self.estimator = PolyEstimatorGUI()

        # give the container a layout if it doesn’t have one
        if container.layout() is None:
            container.setLayout(QVBoxLayout())
        container.layout().addWidget(self.estimator)

        # Dictionary with generic information about the curves the user can configure
        self.poly_param_names = {
            'Voltage to speed'  : { 'name':'VOLT2SPEED'  , 'xdata':'voltage', 'xl':'Voltage [V]'  , 'yl':'Speed [rad/s]'},
            'Speed to thrust'   : { 'name':'SPEED2THRUST', 'xdata':'speed'  , 'xl':'Speed [rad/s]', 'yl':'Force [N]'    },
            'Speed to torque'   : { 'name':'SPEED2TORQUE', 'xdata':'speed'  , 'xl':'Speed [rad/s]', 'yl':'Torque [Nm]'  },
            'Torque to current' : { 'name':'TORQUE2AMPS' , 'xdata':'torque' , 'xl':'Torque [Nm]'  , 'yl':'Current [A]'  }
        }
        self.curve_type_list = list(self.poly_param_names.keys())

        # Plot to display the selected curve
        self.plot_item = self.plotWidget.addPlot()
        self.curve = self.plot_item.plot(pen=pg.mkPen('w', width=2))
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)

        # ----------------------------------------------------------------------
        # Connect signals
        # ----------------------------------------------------------------------
        self.push_button_set_values.clicked.connect(self.set_values)
        self.pushButton_applyEstimation.clicked.connect(self.apply_estimated_coefs)

        self.comboBox_act_id.activated[int].connect(self.on_combo_act_id_changed)
        self.comboBox_curveType.activated[int].connect(self.on_combo_curve_changed)
        self.selected_actuator = None
        self.selected_curve = 0

        self.comboBox_curveType.clear()
        self.comboBox_curveType.addItems(self.curve_type_list)
        self.comboBox_curveType.setCurrentIndex(self.selected_curve)


    def on_tab_selected(self):
        self.update_widgets_data()
        self.update_coeff_widgets_data()
        self.plot_poly()


    def on_combo_act_id_changed(self, index):
        self.selected_actuator = index
        self.update_widgets_data()
        self.update_coeff_widgets_data()
        self.plot_poly()


    def on_combo_curve_changed(self, index):
        self.selected_curve = index
        self.update_coeff_widgets_data()
        self.plot_poly()


    def format_as_scientific(self, value):
        """
        Define a string equivalent to a float in the scientific notation

        Parameters:
            value (float): Float value to be converted to a string

        Returns:
            formatted_value (str): String with the input float in the scientific notation
        """
        formatted_value = "{:.5e}".format(value)
        formatted_value = formatted_value.replace('+0','+')
        formatted_value = formatted_value.replace('-0','-')
        formatted_value = formatted_value.replace('e+0','')
        return formatted_value


    def update_widgets_data(self):
        """
        Update the widgets that display the dynamic properties of the selected actuator
        """

        if not self.shared_data['config'] is None:

            self.label_act_id.hide()
            self.comboBox_act_id.clear()
            number_of_actuators = self.shared_data['config']['VEH_ACT_NUM']['value']
            self.comboBox_act_id.addItems(["Actuator "+str(k) for k in range(number_of_actuators)])

            if (self.selected_actuator is None) or (self.selected_actuator >= number_of_actuators):
                self.selected_actuator = 0

            self.comboBox_act_id.setCurrentIndex(self.selected_actuator)

            self.lineEdit_timeCte.setText(str(self.shared_data['config'][f'ACT{self.selected_actuator}_TIME_CTE']['value']))
            self.lineEdit_MOI.setText(str(self.shared_data['config'][f'ACT{self.selected_actuator}_MOI_ROTOR']['value']))

            spin_data = self.shared_data['config'][f'ACT{self.selected_actuator}_SPIN']
            spin_options = spin_data['options'] if spin_data['options'] else [-1, 1]
            self.comboBox_spin.clear()
            self.comboBox_spin.addItems([str(x) for x in spin_options])
            idx = self.comboBox_spin.findText(str(int(spin_data['value'])))
            if idx >= 0:
                self.comboBox_spin.setCurrentIndex(idx)


    def update_coeff_widgets_data(self):
        """
        Update the widgets that display the polynomial coefficients of the selected curve
        """

        if (self.shared_data['config'] is None) or (self.selected_actuator is None):
            return

        curve_name = self.poly_param_names[self.curve_type_list[self.selected_curve]]['name']

        for k in range(3):
            value = self.shared_data['config'][f'ACT{self.selected_actuator}_{curve_name}_{k}']['value']
            self.lineEdit_coeff[k].setText(self.format_as_scientific(value))

        return


    def get_values_from_widget(self):
        """
        Read and validate the values inserted in the widgets

        Returns:
            valid (bool): True if all the values in the widgets are valid, False otherwise
            act_prop (list of float): Time constant, moment of inertia and spin direction of the actuator
            coefs (list of float): Coefficients of the polynomial of the selected curve
        """

        if (not UT.validate_value(self.lineEdit_timeCte.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid time constant.")
            return False, [], []
        if (not UT.validate_value(self.lineEdit_MOI.text(),'float')):
            QMessageBox.critical(self, "Error", "Invalid moment of inertia.")
            return False, [], []
        if (not UT.validate_value(self.comboBox_spin.currentText(),'int')):
            QMessageBox.critical(self, "Error", "Invalid spin direction.")
            return False, [], []

        letters = ['A', 'B', 'C']
        for k in range(3):
            if (not UT.validate_value(self.lineEdit_coeff[k].text(),'float')):
                QMessageBox.critical(self, "Error", f"Invalid polynomial coefficient {letters[k]}.")
                return False, [], []

        act_prop = [UT.parse_value(self.lineEdit_timeCte.text(),'float'),
                    UT.parse_value(self.lineEdit_MOI.text(),'float'),
                    UT.parse_value(self.comboBox_spin.currentText(),'int')]

        coefs = [UT.parse_value(self.lineEdit_coeff[k].text(),'float') for k in range(3)]

        return True, act_prop, coefs


    def set_values(self):
        """
        Set the values inserted in the widgets to the configuration data
        """

        if (self.shared_data['config'] is None) or (self.selected_actuator is None):
            QMessageBox.critical(self, "Error", "There is no parameter file loaded.")
            return

        valid, act_prop, coefs = self.get_values_from_widget()
        if (not valid):
            return

        act_id = self.selected_actuator
        curve_name = self.poly_param_names[self.curve_type_list[self.selected_curve]]['name']

        self.shared_data['config'][f'ACT{act_id}_TIME_CTE']['value'] = act_prop[0]
        self.shared_data['config'][f'ACT{act_id}_MOI_ROTOR']['value'] = act_prop[1]
        self.shared_data['config'][f'ACT{act_id}_SPIN']['value'] = act_prop[2]

        for k in range(3):
            self.shared_data['config'][f'ACT{act_id}_{curve_name}_{k}']['value'] = coefs[k]

        # Update the displayed data with the values that were set
        self.update_widgets_data()
        self.update_coeff_widgets_data()
        self.plot_poly()

        return


    def apply_estimated_coefs(self):
        """
        Apply the coefficients estimated in the polynomial estimator to the coefficient entry boxes
        """

        if (not self.estimator.has_coefs()):
            QMessageBox.critical(self, "Error", "There is no available estimation.")
            return

        C_ = self.estimator.get_coefs()

        for k in range(3):
            self.lineEdit_coeff[k].setText(self.format_as_scientific(C_[k]))

        # Update the plot with the new polynomial
        self.plot_poly()

        return


    def plot_poly(self):
        """
        Plot the selected curve on the right pane. The coefficients used are the ones in the entry boxes.
        """

        if (self.shared_data['config'] is None) or (self.selected_actuator is None):
            return

        # Get the selected actuator and curve
        act_id = self.selected_actuator
        curve_label = self.curve_type_list[self.selected_curve]

        abscissa = {}
        # Compute abscissa voltage based on the maximum voltage
        max_voltage_ = self.shared_data['config']['BAT_N_CELLS']['value']*4.2 # Assuming a LiPo Cell
        n_pts_ = 1000
        abscissa['voltage'] = [i * max_voltage_ / (n_pts_ - 1) for i in range(n_pts_)]
        # Compute abscissa speed based on the maximum speed computed from maximum value of the voltage2speed map
        volt2speed_coef_names_ = [f"ACT{act_id}_VOLT2SPEED"+f"_{i}" for i in range(3)]
        volt2speed_coef_ = [self.shared_data['config'][s]['value'] for s in volt2speed_coef_names_]
        poly_speed = POLY.polynomial(volt2speed_coef_)
        max_speed_ = poly_speed.eval(max_voltage_)
        abscissa['speed'] = [i * max_speed_ / (n_pts_ - 1) for i in range(n_pts_)]
        # Compute abscissa torque based on the maximum torque computed from maximum value of the speed2torque map
        speed2torque_coef_names_ = [f"ACT{act_id}_SPEED2TORQUE"+f"_{i}" for i in range(3)]
        speed2torque_coef_ = [self.shared_data['config'][s]['value'] for s in speed2torque_coef_names_]
        poly_torque = POLY.polynomial(speed2torque_coef_)
        max_torque_ = poly_torque.eval(max_speed_)
        abscissa['torque'] = [i * max_torque_ / (n_pts_ - 1) for i in range(n_pts_)]

        # Get the polynomial coefficients from the entry boxes
        poly_coefs_ = []
        for k in range(3):
            if (not UT.validate_value(self.lineEdit_coeff[k].text(),'float')):
                return
            poly_coefs_.append(UT.parse_value(self.lineEdit_coeff[k].text(),'float'))

        # Create a polynomial object based on the coefficients
        poly_selected_ = POLY.polynomial(poly_coefs_)

        # Get the x data for the plot
        xdata = abscissa[self.poly_param_names[curve_label]['xdata']]
        # Initialize the y data for the plot
        ydata = []

        # Evaluate the polynomial
        for x in xdata:
            ydata.append(poly_selected_.eval(x))

        # Plot the curve on the right panel
        self.curve.setData(x=xdata, y=ydata)
        self.plot_item.setTitle(f"Actuator {act_id} - {curve_label}")
        self.plot_item.setLabel("left", self.poly_param_names[curve_label]['yl'], units="")
        self.plot_item.setLabel("bottom", self.poly_param_names[curve_label]['xl'], units="")



# ------------------------------------------------------------------------------
# Standalone test
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = QMainWindow()
    tab = ActuatorsTab()
    window.setCentralWidget(tab)
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())

