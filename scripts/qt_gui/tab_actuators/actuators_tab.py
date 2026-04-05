#!/usr/bin/env python3
"""
vehicle_tab.py
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

# from tab_vehicle.vehicle_scene import VTKVehicleSceneWidget
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

        # Load the .ui file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uic.loadUi(os.path.join(script_dir, "actuators_tab.ui"), self)

        # ----------------------------------------------------------------------
        # Access UI widgets via findChild(...)
        # Make sure these names match those in tab_geolocation.ui
        # ----------------------------------------------------------------------
        # self.frame_globe = self.findChild(QFrame, "vtkFrame")
        # self.vtk_frame = self.findChild(type(self.vtkFrame), "vtkFrame")



        self.label_act_id = self.findChild(QLabel,"label_act_id")
        self.comboBox_act_id = self.findChild(QComboBox,"comboBox_act_id")
        self.lineEdit_timeCte = self.findChild(QLineEdit,"lineEdit_timeCte")
        self.lineEdit_MOI = self.findChild(QLineEdit,"lineEdit_MOI")
        self.comboBox_spin = self.findChild(QComboBox,"comboBox_spin")


        self.label_curveType = self.findChild(QLabel,"label_curveType")
        self.comboBox_curveType = self.findChild(QComboBox,"comboBox_curveType")
        self.lineEdit_coeffA = self.findChild(QLineEdit,"lineEdit_coeffA")
        self.lineEdit_coeffB = self.findChild(QLineEdit,"lineEdit_coeffB")
        self.lineEdit_coeffC = self.findChild(QLineEdit,"lineEdit_coeffC")
        
        self.push_button_set_values = self.findChild(QPushButton, "pushButton_set_values")

        self.pushButton_applyEstimation = self.findChild(QPushButton, "pushButton_applyEstimation")
        self.pushButton_applyEstimation.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))

        # self.poly_est_widget = PolyEstimatorGUI()

        # locate the placeholder
        container = self.findChild(QWidget, "widget_polynomialEstimator")

        # build and insert the estimator
        self.estimator = PolyEstimatorGUI()

        # give the container a layout if it doesn’t have one
        if container.layout() is None:
            container.setLayout(QVBoxLayout())
        container.layout().addWidget(self.estimator)

        # # Example plot            
        self.plot_item = self.plotWidget.addPlot()
        self.curve = self.plot_item.plot(pen=pg.mkPen('w', width=2))
        self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        # self.data  = np.sin(np.linspace(0, 2*np.pi, 1000))
        # self.ptr   = 0
        # self.ptr = (self.ptr + 1) % self.data.size
        # self.curve.setData(np.roll(self.data, self.ptr))
        # self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        # self.plot_item.setLabel("left", "y", units="m")
        # self.plot_item.setLabel("bottom", "x", units="m")

        # # ----------------------------------------------------------------------
        # # Connect signals
        # # ----------------------------------------------------------------------
        self.push_button_set_values.clicked.connect(self.set_values)

        self.comboBox_act_id.activated[int].connect(self.on_combo_act_id_changed)
        self.comboBox_curveType.activated[int].connect(self.on_combo_curve_changed)
        self.selected_actuator = None
        self.selected_curve = None


        # self.label_act_id.hide()
        self.comboBox_act_id.clear()
        number_of_actuators = self.shared_data['config']['VEH_ACT_NUM']['value']
        self.comboBox_act_id.addItems(["Actuator "+str(k) for k in range(number_of_actuators)])

        # self.label_curveType.hide()
        # self.comboBox_curveType.clear()
        # self.curve_type_list = ["Voltage to speed","Speed to thrust","Speed to torque","Torque to current"]
        # self.comboBox_curveType.addItems(self.curve_type_list)
        self.curve_type_list = ["VOLT2SPEED","SPEED2THRUST","SPEED2TORQUE","TORQUE2AMPS"]
        

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


    def plot_poly(self):

        self.poly_param_names = {
            'Voltage to speed'  : { 'name':'VOLT2SPEED'  , 'xdata':'voltage', 'xl':'Voltage [V]'  , 'yl':'Speed [rad/s]'},
            'Speed to thrust'   : { 'name':'SPEED2THRUST', 'xdata':'speed'  , 'xl':'Speed [rad/s]', 'yl':'Force [N]'    },
            'Speed to torque'   : { 'name':'SPEED2TORQUE', 'xdata':'speed'  , 'xl':'Speed [rad/s]', 'yl':'Torque [Nm]'  },
            'Torque to current' : { 'name':'TORQUE2AMPS' , 'xdata':'torque' , 'xl':'Torque [Nm]'  , 'yl':'Current [A]'  }
        }

        print("self.comboBox_act_id.currentIndex(): ", self.comboBox_act_id.currentIndex())
        print("self.comboBox_curveType.currentIndex(): ", self.comboBox_curveType.currentIndex())

        # # Return if the actuator id or the curve are not selected
        # if(not self.comboBox_act_id.currentIndex() or not self.comboBox_curveType.currentIndex()):
        #     print("AAAAAAAAAAAAAAA")
        #     return

        # Get actuator id
        act_id = self.comboBox_act_id.currentIndex()
        act_data = f"Actuator {self.comboBox_act_id.currentIndex()}"
        keys = list(self.poly_param_names.keys())
        print("keys: ", keys)
        curve_data = keys[self.comboBox_curveType.currentIndex()]

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
        poly_coefs_ = [float(self.lineEdit_coeffA.text()), float(self.lineEdit_coeffB.text()), float(self.lineEdit_coeffC.text())]

        # Create a polynomial object based on the coefficients
        poly_selected_ = POLY.polynomial(poly_coefs_)

        # Get the x data for the plot
        xdata = abscissa[self.poly_param_names[curve_data]['xdata']]
        # Initialize the y data for the plot
        ydata = []

        # Evaluate the polynomial
        for x in xdata:
            ydata.append(poly_selected_.eval(x))


        # Plot            
        # self.plot_item = self.plotWidget.addPlot(title=f"{act_data} - {curve_data}")
        # self.curve = self.plot_item.plot(pen=pg.mkPen('w', width=2))
        # self.data  = np.sin(np.linspace(0, 2*np.pi, 1000))
        # self.ptr   = 0
        # self.ptr = (self.ptr + 1) % self.data.size
        # self.curve.setData(np.roll(self.data, self.ptr))
        self.curve.setData(x=xdata, y=ydata)
        self.plot_item.setTitle(f"{act_data} - {curve_data}")
        self.plot_item.setLabel("left", self.poly_param_names[curve_data]['yl'], units="")
        self.plot_item.setLabel("bottom", self.poly_param_names[curve_data]['xl'], units="")

        # # Plot the curve on the right panel
        # self.axs.clear() # clear
        # self.axs.plot(xdata, ydata, linewidth=2, color='blue') # plot
        # self.axs.grid(True) # enable grid
        # self.axs.set_xlabel(self.poly_param_names[self.act_curve_var.get()]['xl']) # set x axis name
        # self.axs.set_ylabel(self.poly_param_names[self.act_curve_var.get()]['yl']) # set y axis name
        # self.axs.set_title(self.act_id_var.get() + ' - ' + self.act_curve_var.get()) # set title

        # # Show the plot and proceed
        # #plt.ion()
        # self.canvas.draw()


    def update_widgets_data(self):

        if not self.shared_data['config'] is None:

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

            self.lineEdit_timeCte.setText(str(self.shared_data['config'][f'ACT{self.selected_actuator}_TIME_CTE']['value']))
            self.lineEdit_MOI.setText(str(self.shared_data['config'][f'ACT{self.selected_actuator}_MOI_ROTOR']['value']))
            self.comboBox_spin.setCurrentIndex(int(self.shared_data['config'][f'ACT{self.selected_actuator}_SPIN']['value']/2+0.5))


    def update_coeff_widgets_data(self):

        act_id = self.comboBox_act_id.currentIndex()
        curve_id = self.comboBox_curveType.currentIndex()

        self.lineEdit_coeffA.setText(str(self.shared_data['config'][f'ACT{act_id}_{self.curve_type_list[curve_id]}_0']['value']))
        self.lineEdit_coeffB.setText(str(self.shared_data['config'][f'ACT{act_id}_{self.curve_type_list[curve_id]}_1']['value']))
        self.lineEdit_coeffC.setText(str(self.shared_data['config'][f'ACT{act_id}_{self.curve_type_list[curve_id]}_2']['value']))

        return
    

    def set_values(self):
        return

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
        

        return



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


