#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import vtk
import json
import os
import numpy as np
from math import asin, atan2, cos, sin, pi
import threading
import zmq

import sim4cd.math_utils as MU

class Visualization:
    def __init__(self, data):
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.25, 0.25, 0.25)
        self.data = data
        self.render_window = vtk.vtkRenderWindow()
        self.render_window_interactor = vtk.vtkRenderWindowInteractor()
        self.style = vtk.vtkInteractorStyleTrackballCamera()
        self.initialize_renderer(self.data, False)

        # Create a ZeroMQ context
        self.context = zmq.Context()
        # Create a SUB socket
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5555")  # Connect to the publisher
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages
        self.socket.setsockopt(zmq.RCVTIMEO, 50)  # Timeout in milliseconds


    def update_renderer(self, data):
        # Remove previous stuff
        self.renderer.RemoveAllViewProps()

        self.initialize_renderer(data, True)
        self.data = data


    def initialize_renderer(self, data, update):

        # Create a cube source
        cube = vtk.vtkCubeSource()

        if not data:
            return

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

            disk_actor = self.create_disk(center=c_arm, direction=d_arm, radius=(size[0] + size[1]) / 30, height=h_arm, color=[1, 1, 1])
            self.renderer.AddActor(disk_actor)

        # Add axes to indicate the x, y, and z directions
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(1.0, 1.0, 1.0)  # Set the length of the axes
        axes.AxisLabelsOn()  # Enable axis labels
        self.renderer.AddActor(axes)

        if update:
            self.render_window.Render()


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


    def timer_callback(self, obj, event):
        try:
            message = self.socket.recv_string(flags=zmq.NOBLOCK)
            data_dict = json.loads(message)
        except zmq.Again as e:
            # No message received
            return

        self.update_renderer(data_dict)


    def start(self):
        # Create a render window
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName("Vehicle Geometry View")

        # Create a render window interactor
        self.render_window_interactor.SetRenderWindow(self.render_window)

        # Use the 'vtkInteractorStyleTrackballCamera' for better interaction
        self.render_window_interactor.SetInteractorStyle(self.style)

        # Initialize the interactor
        self.render_window.Render()
        self.render_window_interactor.Initialize()

        # Set up a timer to update the data periodically
        self.render_window_interactor.AddObserver('TimerEvent', self.timer_callback)
        self.timer_id = self.render_window_interactor.CreateRepeatingTimer(1000)  # Update every 100 ms
        
        # Start the rendering loop
        self.render_window_interactor.Start()


def load_json(path):
    if path:
        file_path = path
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            return data
    return False

if __name__ == "__main__":
    path = os.path.normpath(os.path.abspath(__file__).rsplit('/', 1)[0] + '/../../config/sim_params.json')
    data = load_json(path)
    visualization = Visualization(data)
    visualization.start()
