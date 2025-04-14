#!/usr/bin/env python3
"""
geolocation_tab.py
-----------
Example PyQt5 tab containing a VTK-based globe and some placeholder input fields
and push buttons, using findChild(...) to access UI objects after loading the .ui file.
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
    QVBoxLayout
)

import json
import zmq

# VTK imports
import vtk
# from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor



from tab_geolocation.globe_scene import VTKGlobeSceneWidget


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

        self.line_edit_east = self.findChild(QLineEdit, "lineEdit_mag_east")
        self.line_edit_north = self.findChild(QLineEdit, "lineEdit_mag_north")
        self.line_edit_up = self.findChild(QLineEdit, "lineEdit_mag_up")

        self.push_button_set_values = self.findChild(QPushButton, "pushButton_set_values")
        self.push_button_compute = self.findChild(QPushButton, "pushButton_compute_field")
        self.push_button_apply = self.findChild(QPushButton, "pushButton_apply_field")

        # Create a ZeroMQ context
        self.context = zmq.Context()

        # Create a PUB socket
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5565")  # Bind to port 5555


        # VTK setup in a separate function
        self.init_vtk_scene()


        if self.shared_data['config']:
            LLA = [self.shared_data['config']['SENS_LAT_ORIGIN']['value'],
                   self.shared_data['config']['SENS_LON_ORIGIN']['value'],
                   self.shared_data['config']['SENS_ALT_ORIGIN']['value']]
            # Optional defaults for line edits:
            self.line_edit_latitude.setText(str(self.shared_data['config']['SENS_LAT_ORIGIN']['value']))
            self.line_edit_longitude.setText(str(self.shared_data['config']['SENS_LON_ORIGIN']['value']))
            self.line_edit_altitude.setText(str(self.shared_data['config']['SENS_ALT_ORIGIN']['value']))

            MAG = [self.shared_data['config']['SENS_MAG_FIELD_E']['value'],
                   self.shared_data['config']['SENS_MAG_FIELD_N']['value'],
                   self.shared_data['config']['SENS_MAG_FIELD_U']['value']]
            self.line_edit_east.setText(str(self.shared_data['config']['SENS_MAG_FIELD_E']['value']))
            self.line_edit_north.setText(str(self.shared_data['config']['SENS_MAG_FIELD_N']['value']))
            self.line_edit_up.setText(str(self.shared_data['config']['SENS_MAG_FIELD_U']['value']))

            self.socket.send_string(json.dumps({'LLA':LLA, 'MAG':MAG}))

        # ----------------------------------------------------------------------
        # Connect signals
        # ----------------------------------------------------------------------
        self.push_button_set_values.clicked.connect(self.set_values)
        self.push_button_compute.clicked.connect(self.compute_local_field)
        self.push_button_apply.clicked.connect(self.apply_computed_field)

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

    # --------------------------------------------------------------------------
    # Button placeholder functions
    # --------------------------------------------------------------------------
    def set_values(self):
        print("Set values clicked.")

        # TODO: Check for valid values

        # Update data
        self.shared_data['config']['SENS_LAT_ORIGIN']['value'] = float(self.line_edit_latitude.text())
        self.shared_data['config']['SENS_LON_ORIGIN']['value'] = float(self.line_edit_longitude.text())
        self.shared_data['config']['SENS_ALT_ORIGIN']['value'] = float(self.line_edit_altitude.text())

        # Update vizualozation
        LLA = [float(self.line_edit_latitude.text()),
               float(self.line_edit_longitude.text()),
               float(self.line_edit_altitude.text())]
        self.socket.send_string(json.dumps({'LLA':LLA}))


    def compute_local_field(self):
        print("Compute local field clicked.")
        # Your logic here

    def apply_computed_field(self):
        print("Apply computed field clicked.")
        # Your logic here


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



# #!/usr/bin/env python3
# """
# tab_geolocation.py
# -----------
# Example PyQt5 tab containing a VTK-based globe and some placeholder input fields
# and push buttons.  A matching .ui file (tab_geolocation.ui) is also provided.
# """
# import os

# from PyQt5 import uic
# from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
# import vtk
# from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


# class GeolocationTab(QWidget):
#     def __init__(self, shared_data=None, parent=None):
#         super().__init__(parent)
#         self.shared_data = shared_data if shared_data is not None else {}

#         # Load the .ui file (make sure the .ui file is in the same directory, or update path)
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         uic.loadUi(os.path.join(script_dir, "tab_geolocation.ui"), self)

#         return

#         #--------------------------------------------------------------------------
#         # Set up VTK Globe in the frameGlobe widget
#         #--------------------------------------------------------------------------
#         # We assume there is a QFrame (or QWidget) in the .ui named frameGlobe.
#         # We place a QVTKRenderWindowInteractor there.
#         self.vtkWidget = QVTKRenderWindowInteractor(self.vtkFrame)
#         # In the .ui, frameGlobe has a layout (QVBoxLayout) already, so we can
#         # add the vtkWidget directly.  If you see a layout error, ensure the .ui
#         # has a layout set on frameGlobe.
#         self.frameGlobe.layout().addWidget(self.vtkWidget)

#         # Create a renderer and attach it to the render window
#         self.renderer = vtk.vtkRenderer()
#         self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

#         # Create a sphere source for the globe
#         sphere_source = vtk.vtkTexturedSphereSource()
#         sphere_source.SetRadius(1.0)

#         # Create the Earth texture from a local file (e.g., 'earth.jpg')
#         # Adjust the file path/name as needed. This example expects 'earth.jpg'
#         # in the same directory as tab_geolocation.py.
#         earth_texture = vtk.vtkTexture()
#         earth_reader = vtk.vtkJPEGReader()
#         earth_reader.SetFileName(os.path.join(script_dir, "earth.jpg"))
#         earth_texture.SetInputConnection(earth_reader.GetOutputPort())
#         earth_texture.InterpolateOn()

#         # Create mapper and actor
#         globe_mapper = vtk.vtkPolyDataMapper()
#         globe_mapper.SetInputConnection(sphere_source.GetOutputPort())

#         globe_actor = vtk.vtkActor()
#         globe_actor.SetMapper(globe_mapper)
#         globe_actor.SetTexture(earth_texture)

#         # Add the globe actor to the scene
#         self.renderer.AddActor(globe_actor)
#         self.renderer.ResetCamera()
#         self.renderer.SetBackground(0, 0, 0)  # black background

#         # Initialize and start the VTK widget
#         self.vtkWidget.Initialize()
#         self.vtkWidget.Start()

#         #--------------------------------------------------------------------------
#         # Connect Button Signals -> Slot Functions
#         #--------------------------------------------------------------------------
#         # These placeholders simply print. Replace with real code as needed.
#         self.pushButton_compute_field.clicked.connect(self.estimate_local_magnetic_field)
#         self.pushButton_apply_field.clicked.connect(self.compute_local_field)
#         self.pushButton_set_values.clicked.connect(self.apply_computed_field)

#         # Initialize line edits (optional example defaults)
#         self.lineEdit_latitude.setText("40.448985")
#         self.lineEdit_longitude.setText("-79.898025")
#         self.lineEdit_altitude.setText("372.0")

#         self.lineEdit_mag_east.setText("0.03313")
#         self.lineEdit_mag_north.setText("0.20188")
#         self.lineEdit_mag_up.setText("0.47534")

#     #--------------------------------------------------------------------------
#     # Placeholder functions for the three buttons
#     #--------------------------------------------------------------------------
#     def estimate_local_magnetic_field(self):
#         print("Estimate local magnetic field clicked.")

#     def compute_local_field(self):
#         print("Compute local field clicked.")

#     def apply_computed_field(self):
#         print("Apply computed field clicked.")


# #------------------------------------------------------------------------------
# # If you want to test this tab as a standalone window:
# #------------------------------------------------------------------------------
# if __name__ == "__main__":
#     import sys

#     app = QApplication(sys.argv)
#     window = QMainWindow()
#     tab = GeolocationTab()
#     window.setCentralWidget(tab)
#     window.resize(1200, 800)
#     window.show()
#     sys.exit(app.exec_())
