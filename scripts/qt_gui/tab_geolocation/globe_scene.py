#!/usr/bin/env python3
import vtk
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np
from math import asin, atan2, cos, sin, pi
import zmq
import json
import os

import sim4cd.math_utils as MU

_OPACITY_ = 0.8

class VTKGlobeSceneWidget(QWidget):
    def __init__(self, parent=None, lla=None):
        """
        If 'config' is not None, we'll call add_shapes(**config)
        to insert shapes (box + 2 sets of cylinders) into the scene.
        """
        super().__init__(parent)

        # Layout to hold the VTK render window
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create VTK interactor widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)

        # Create and configure the renderer
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # Use a more intuitive trackball camera interaction style
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)

        # Camera
        self.camera = self.renderer.GetActiveCamera()
        self.set_camera_pose(position=[5, 0, 0], focal_point=[0,0,0], view_up=[0,0,1])
        # self.camera.SetPosition(5, 0, 0)    # Example vantage point
        # self.camera.SetFocalPoint(0, 0, 0)  # Looking at origin
        # self.camera.SetViewUp(0, 0, 1)      # Z is "up"
        self.camera.SetViewAngle(30)        # Camera FOV

        # Add Earth view
        self.add_earth()

        # If config was given, add pin in the selected location
        self.pin_assembly = None
        if lla is not None:
            self.add_pin(lla)
            
        # Adjust light
        ambient_light = vtk.vtkLight()
        ambient_light.SetLightTypeToSceneLight()
        ambient_light.SetColor(1.0, 1.0, 1.0)  # White light
        ambient_light.SetIntensity(0.6)  # Adjust brightness
        self.renderer.AddLight(ambient_light)

        # Create a ZeroMQ context
        self.context = zmq.Context()
        # Create a SUB socket
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5565")  # Connect to the publisher
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages
        self.socket.setsockopt(zmq.RCVTIMEO, 50)  # Timeout in milliseconds

        # Initialize the interactor
        self.interactor.Initialize()

        # Set up a timer to update the data periodically
        self.interactor.AddObserver('TimerEvent', self.timer_callback)
        self.timer_id = self.interactor.CreateRepeatingTimer(10)  # Update every 10 ms

        self.interactor.Start()


    def timer_callback(self, obj, event):
        
        try:
            message = self.socket.recv_string(flags=zmq.NOBLOCK)
            data_dict = json.loads(message)
            self.add_pin(data_dict['LLA'])
        except zmq.Again as e:
            # No message received
            return


    def update_pin(self, lla):

        latitude = lla[0]
        longitude = lla[1] + 180

        # Convert lat/lon to radians
        lat_rad = latitude*pi/180
        lon_rad = longitude*pi/180

        # Earth's surface position (radius=1.0)
        x_surf = cos(lat_rad) * cos(lon_rad)
        y_surf = cos(lat_rad) * sin(lon_rad)
        z_surf = sin(lat_rad)

        self.pin_assembly.SetPosition(x_surf, y_surf, z_surf)
        self.pin_assembly.SetOrientation(0, -latitude, longitude)

        pos = [5*x_surf, 5*y_surf, 5*z_surf]
        focal_point = [0,0,0]
        focal_point = [x_surf, y_surf, z_surf]
        up = [0,0,1]
        self.set_camera_pose(pos, focal_point, up)

        # Re-render
        self.vtk_widget.GetRenderWindow().Render()


    def add_pin(self, lla):

        if(self.pin_assembly):
            self.update_pin(lla)
            return

        self.pin_assembly = vtk.vtkAssembly()

        # Create pin to indicate geolocation
        # First part
        marker1_sphere = vtk.vtkSphereSource()
        marker1_sphere.SetRadius(0.03)

        marker1_mapper = vtk.vtkPolyDataMapper()
        marker1_mapper.SetInputConnection(marker1_sphere.GetOutputPort())

        marker1_actor = vtk.vtkActor()
        marker1_actor.SetMapper(marker1_mapper)
        marker1_actor.GetProperty().SetColor(1.0, 0.0, 0.0)

        marker1_actor.SetScale(0.3, 1.0, 1.0)
        marker1_actor.SetPosition(0.04, 0.0, 0.0)

        self.pin_assembly.AddPart(marker1_actor)

        # Second part
        marker2_sphere = vtk.vtkSphereSource()
        marker2_sphere.SetRadius(0.02)  # base radius

        marker2_mapper = vtk.vtkPolyDataMapper()
        marker2_mapper.SetInputConnection(marker2_sphere.GetOutputPort())

        marker2_actor = vtk.vtkActor()
        marker2_actor.SetMapper(marker2_mapper)
        marker2_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # red

        marker2_actor.SetScale(1.0, 0.6, 0.6)   # stretch in Y -> ellipsoid
        marker2_actor.SetPosition(0.05, 0.0, 0.0)
        
        self.pin_assembly.AddPart(marker2_actor)

        # Third part
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(0, 0, 0)
        line_source.SetPoint2(0.04, 0.0, 0.0)

        tube = vtk.vtkTubeFilter()
        tube.SetInputConnection(line_source.GetOutputPort())
        tube.SetRadius(0.003)
        tube.SetNumberOfSides(12)
        tube.Update()

        tube_mapper = vtk.vtkPolyDataMapper()
        tube_mapper.SetInputConnection(tube.GetOutputPort())

        tube_actor = vtk.vtkActor()
        tube_actor.SetMapper(tube_mapper)
        tube_actor.GetProperty().SetColor(1.0, 1.0, 1.0)
        self.pin_assembly.AddPart(tube_actor)

        # Add pin to the renderer
        self.renderer.AddActor(self.pin_assembly)

        # Update pin position
        self.update_pin(lla)

        
    def add_earth(self):
        
        # Create a TexturedSphereSource for Earth, radius = 1.0
        earth_source = vtk.vtkTexturedSphereSource()
        earth_source.SetThetaResolution(50)
        earth_source.SetPhiResolution(50)
        earth_source.SetRadius(1.0)

        # Read equirectangular Earth texture
        reader = vtk.vtkJPEGReader()
        reader.SetFileName(os.path.join(os.path.dirname(__file__),"../resources/equirectangular.jpg"))
        reader.Update()

        # Create a texture from the image reader
        texture = vtk.vtkTexture()
        texture.SetInputConnection(reader.GetOutputPort())
        texture.InterpolateOn()

        # Map the textured sphere geometry
        earth_mapper = vtk.vtkPolyDataMapper()
        earth_mapper.SetInputConnection(earth_source.GetOutputPort())

        # Earth actor
        earth_actor = vtk.vtkActor()
        earth_actor.SetMapper(earth_mapper)
        earth_actor.SetTexture(texture)

        # Add the Earth to the scene
        self.renderer.AddActor(earth_actor)
        self.renderer.SetBackground(0.05, 0.1, 0.2)

        # Re-render
        self.vtk_widget.GetRenderWindow().Render()


    def set_camera_pose(self, position, focal_point, view_up):
        self.camera.SetPosition(*position)
        self.camera.SetFocalPoint(*focal_point)
        self.camera.SetViewUp(*view_up)








