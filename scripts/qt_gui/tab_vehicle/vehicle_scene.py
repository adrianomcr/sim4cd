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

class VTKVehicleSceneWidget(QWidget):
    def __init__(self, parent=None, data=None):
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
        self.set_camera_pose(position=[-4, 2, 2], focal_point=[0,0,0], view_up=[0,0,1])
        self.camera.SetViewAngle(30)        # Camera FOV
        
        # Background color
        self.renderer.SetBackground(0.05, 0.1, 0.2)

        # Re-render
        self.vtk_widget.GetRenderWindow().Render()

        # If config was given, add pin in the selected location
        self.pin_assembly = None
        if data is not None:
            self.add_vehicle(data)
            
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
        self.socket.connect("tcp://localhost:5575")  # Connect to the publisher
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
            self.add_vehicle(data_dict)
        except zmq.Again as e:
            # No message received
            return


    def add_vehicle(self, data):

        # Remove previous stuff
        self.renderer.RemoveAllViewProps()

        # Create a cube source
        cube = vtk.vtkCubeSource()

        size = [data['VIZ_SIZE_X']['value'], data['VIZ_SIZE_Y']['value'], data['VIZ_SIZE_Z']['value']]
        cube.SetXLength(size[0])
        cube.SetYLength(size[1])
        cube.SetZLength(size[2])

        # Create a mapper for the cube
        cube_mapper = vtk.vtkPolyDataMapper()
        cube_mapper.SetInputConnection(cube.GetOutputPort())

        # Create an actor for the cube
        cube_actor = vtk.vtkActor()
        cube_actor.SetMapper(cube_mapper)
        cube_actor.GetProperty().SetOpacity(1.0)  # Make the cube semi-transparent
        cube_actor.GetProperty().SetColor([0.2, 0.2, 0.2])

        # Add the cube actor to the renderer
        self.renderer.AddActor(cube_actor)

        for k in range(data['VEH_ACT_NUM']['value']):
            c = (
                data[f'VEH_ACT{k}_POS_X']['value'],
                data[f'VEH_ACT{k}_POS_Y']['value'],
                data[f'VEH_ACT{k}_POS_Z']['value'],
            )
            d = (
                data[f'VEH_ACT{k}_DIR_X']['value'],
                data[f'VEH_ACT{k}_DIR_Y']['value'],
                data[f'VEH_ACT{k}_DIR_Z']['value'],
            )
            b = (
                data[f'VIZ_ACT{k}_BASE_X']['value'],
                data[f'VIZ_ACT{k}_BASE_Y']['value'],
                data[f'VIZ_ACT{k}_BASE_Z']['value'],
            )

            # Create and add a disk to represent propeller
            if data[f'ACT{k}_SPIN']['value'] == 1:
                color = [0.25, 0.5, 1]
            elif data[f'ACT{k}_SPIN']['value'] == -1:
                color = [0.5, 1, 0.25]
            else:
                color = [1, 1, 1]
            disk_actor = self.create_disk(center=c, direction=d, radius=(size[0] + size[1]) / 2, height=size[2] / 10, color=color)
            self.renderer.AddActor(disk_actor)

            c = np.array(c)
            d = np.array(d)
            b = np.array(b)

            c_arm = (c + b) / 2.0
            d_arm = c - b
            h_arm = np.linalg.norm(d_arm)
            d_arm = d_arm / h_arm

            disk_actor = self.create_disk(center=c_arm, direction=d_arm, radius=(size[0] + size[1]) / 30, height=h_arm, color=[0.2, 0.2, 0.2])
            self.renderer.AddActor(disk_actor)

        # Add axes to indicate the x, y, and z directions
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(1.0, 1.0, 1.0)  # Set the length of the axes
        axes.AxisLabelsOn()  # Enable axis labels
        self.renderer.AddActor(axes)

        # self.render_window.Render()
        self.vtk_widget.GetRenderWindow().Render()




    def create_disk(self, center, direction, radius=0.12, height=0.1, color=[1, 1, 1]):
        cylinder_source = vtk.vtkCylinderSource()
        cylinder_source.SetCenter((0.0, 0.0, 0.0))
        cylinder_source.SetRadius(radius)
        cylinder_source.SetHeight(height)
        cylinder_source.SetResolution(50)  # Increase resolution for a smoother appearance

        # Create a transform for rotation
        rotation_transform = vtk.vtkTransform()
        rpy = self.get_rot_from_dir(direction)
        rpy = (rpy * 180 / pi).tolist()
        rotation_transform.RotateZ(rpy[2])
        rotation_transform.RotateY(rpy[1])
        rotation_transform.RotateX(rpy[0])
        # Apply the rotation transform to the cylinder
        rotation_filter = vtk.vtkTransformPolyDataFilter()
        rotation_filter.SetInputConnection(cylinder_source.GetOutputPort())
        rotation_filter.SetTransform(rotation_transform)
        rotation_filter.Update()

        # Create a transform for translation
        translation_transform = vtk.vtkTransform()
        translation_transform.Translate(center[0], center[1], center[2])  # Translate in the original frame
        # Apply the translation transform to the rotated cylinder
        translation_filter = vtk.vtkTransformPolyDataFilter()
        translation_filter.SetInputConnection(rotation_filter.GetOutputPort())
        translation_filter.SetTransform(translation_transform)
        translation_filter.Update()

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(translation_filter.GetOutputPort())

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])

        return actor

    def get_rot_from_dir(self, dir):
        y = np.array(dir)
        n = np.cross(np.array([0.0, 1.0, 0.0]), y)
        ang = asin(np.linalg.norm(n))
        ang = atan2(np.linalg.norm(n), np.dot(np.array([0, 1, 0]), y))
        n = n / (np.linalg.norm(n) + 1e-8)
        q = [cos(ang / 2), sin(ang / 2) * n[0], sin(ang / 2) * n[1], sin(ang / 2) * n[2]]
        q = np.array(q)
        q = q / np.linalg.norm(q)
        rpy = MU.quat2rpy(q)
        return rpy






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



    def set_camera_pose(self, position, focal_point, view_up):
        self.camera.SetPosition(*position)
        self.camera.SetFocalPoint(*focal_point)
        self.camera.SetViewUp(*view_up)








