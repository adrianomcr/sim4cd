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

class VTKMainSceneWidget(QWidget):
    def __init__(self, parent=None, config=None):
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
        # style = FixedVerticalInteractorStyle(renderer=self.renderer)
        # self.interactor.SetInteractorStyle(style)
        self.interactor.SetInteractorStyle(None)

        # Tell the camera that Z is up
        self.camera = self.renderer.GetActiveCamera()
        self.camera.SetPosition(-5, 0, 2)    # Example vantage point
        self.camera.SetFocalPoint(0, 0, 0)  # Looking at origin
        self.camera.SetViewUp(0, 0, 1)      # Z is "up"
        self.camera.SetViewAngle(45)        # Camera FOV

        # A vtkAssembly to group shapes so we can transform them as one unit
        self.drone_assembly = vtk.vtkAssembly()
        self.renderer.AddActor(self.drone_assembly)

        self.shadow_assembly = vtk.vtkAssembly()
        self.renderer.AddActor(self.shadow_assembly)

        # Optional timer for periodic pose updates
        self.update_timer = None
        self.update_frequency_ms = 1000

        # If config was given, add shapes automatically
        if config is not None:
            self.add_shapes(config)
            
        self.reset_group_pose(pose=[0,0,0, 0,0,0])

        ambient_light = vtk.vtkLight()
        ambient_light.SetLightTypeToSceneLight()
        ambient_light.SetColor(1.0-0.5*0, 1.0, 1.0)  # White light
        ambient_light.SetIntensity(1.0-0.4)  # Adjust brightness
        self.renderer.AddLight(ambient_light)

        # Create a ZeroMQ context
        self.context = zmq.Context()
        # Create a SUB socket
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:5545")  # Connect to the publisher
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages
        self.socket.setsockopt(zmq.RCVTIMEO, 50)  # Timeout in milliseconds


        # Load an equirectangular texture for the skybox
        #texture_reader = vtk.vtkJPEGReader()
        texture_reader = vtk.vtkPNGReader()
        texture_reader.SetFileName(os.path.join(os.path.dirname(__file__),"../resources/skybox.png"))
        texture_reader.Update()

        skybox_texture = vtk.vtkTexture()
        skybox_texture.SetInputConnection(texture_reader.GetOutputPort())
        skybox_texture.InterpolateOn()  # Smooth the texture if desired

        # Create skybox actor
        skybox = vtk.vtkSkybox()
        skybox.SetTexture(skybox_texture)
        skybox.SetFloorPlane(0,0,1,0)
        skybox.SetProjectionToSphere()  # For equirectangular images

        # Add the skybox to the scene
        self.renderer.AddActor(skybox)

        self.focal_point = [0,0,0]

        # Initialize the interactor & do initial camera fit
        self.interactor.Initialize()
        self.set_camera_pose([-5,0,2], [0,0,0], [0,0,1])

        # Set up a timer to update the data periodically
        self.interactor.AddObserver('TimerEvent', self.timer_callback)
        self.timer_id = self.interactor.CreateRepeatingTimer(10)  # Update every 10 ms

        self.interactor.Start()


    def timer_callback(self, obj, event):
        try:
            message = self.socket.recv_string(flags=zmq.NOBLOCK)
            data_dict = json.loads(message)
        except zmq.Again as e:
            # No message received
            return

        self.reset_group_pose(pose=data_dict['pose'])
        self.focal_point = [0.9*self.focal_point[k] + 0.1*data_dict['pose'][k] for k in range(3)]
        self.set_camera_pose([-5,0,2], self.focal_point, [0,0,1])

        
    def add_shapes(self, config):
        """
        All actors are added to self.drone_assembly to allow group transforms.
        """

        if (config is None):
            return

        # Build the box
        box_size = [config['VIZ_SIZE_X']['value'], config['VIZ_SIZE_Y']['value'], config['VIZ_SIZE_Z']['value']]
        box_color = [0.2, 0.2, 0.2]
        box_pose = [0, 0, 0, 0, 0, 0]
        box_actor = self.create_box_actor(box_size, 1, box_color)
        self.set_actor_pose(box_actor, box_pose)
        self.drone_assembly.AddPart(box_actor)

        box_actor_shadow = self.create_box_actor([config['VIZ_SIZE_X']['value'], config['VIZ_SIZE_Y']['value'], 0], 1, [0,0,0], 0.3, [0,0,-0.03])
        self.shadow_assembly.AddPart(box_actor_shadow)


        for k in range(config['VEH_ACT_NUM']['value']):
            c = (
                config[f'VEH_ACT{k}_POS_X']['value'],
                config[f'VEH_ACT{k}_POS_Y']['value'],
                config[f'VEH_ACT{k}_POS_Z']['value'],
            )
            d = (
                config[f'VEH_ACT{k}_DIR_X']['value'],
                config[f'VEH_ACT{k}_DIR_Y']['value'],
                config[f'VEH_ACT{k}_DIR_Z']['value'],
            )
            b = (
                config[f'VIZ_ACT{k}_BASE_X']['value'],
                config[f'VIZ_ACT{k}_BASE_Y']['value'],
                config[f'VIZ_ACT{k}_BASE_Z']['value'],
            )

            # Create and add a disk to represent propeller
            if config[f'ACT{k}_SPIN']['value'] == 1:
                color = [0.25, 0.5, 1]
            elif config[f'ACT{k}_SPIN']['value'] == -1:
                color = [0.5, 1, 0.25]
            else:
                color = [1, 1, 1]

            disk_actor = self.create_cylinder_actor(
                center=c,
                direction=d,
                radius=(box_size[0] + box_size[1]) / 2,
                height=box_size[2] / 10,
                color=color
            )
            self.drone_assembly.AddPart(disk_actor)

            disk_actor_shadow = self.create_cylinder_actor(
                center=[c[0],c[1],-0.03],
                direction=[0,0,1],
                radius=(box_size[0] + box_size[1]) / 2,
                height=box_size[2] / 100,
                color=[0,0,0],
                alpha=0.3
            )
            self.shadow_assembly.AddPart(disk_actor_shadow)


            # Add arm
            c = np.array(c)
            d = np.array(d)
            b = np.array(b)

            c_arm = (c + b) / 2.0
            d_arm = c - b
            h_arm = np.linalg.norm(d_arm)
            d_arm = d_arm / h_arm

            arm_actor = self.create_cylinder_actor(
                center=c_arm,
                direction=d_arm,
                radius=(box_size[0] + box_size[1]) / 30,
                height=h_arm,
                color=[0.3, 0.3, 0.3]
            )
            self.drone_assembly.AddPart(arm_actor)

            arm_actor_shadow = self.create_cylinder_actor(
                center=[c_arm[0],c_arm[1],-0.03],
                direction=d_arm,
                radius=(box_size[0] + box_size[1]) / 30,
                height=h_arm,
                color=[0, 0, 0],
                alpha = 0.3
            )
            self.shadow_assembly.AddPart(arm_actor_shadow)

        # Re-render
        self.vtk_widget.GetRenderWindow().Render()


    def create_box_actor(self, size, opacity, color, alpha=1.0, center=[0,0,0]):
        cube_source = vtk.vtkCubeSource()
        cube_source.SetXLength(size[0])
        cube_source.SetYLength(size[1])
        cube_source.SetZLength(size[2])
        cube_source.SetCenter(center)
        cube_source.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube_source.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(alpha)
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

    def create_cylinder_actor(self, center, direction, radius=0.12, height=0.1, color=[1, 1, 1], alpha=1.0):
        cyl_source = vtk.vtkCylinderSource()
        cyl_source.SetCenter((0.0, 0.0, 0.0))
        cyl_source.SetRadius(radius)
        cyl_source.SetHeight(height)
        cyl_source.SetResolution(50)  # Increase resolution for a smoother appearance

        # Create a transform for rotation
        rotation_transform = vtk.vtkTransform()
        rpy = self.get_rot_from_dir(direction)
        rpy = (rpy * 180 / pi).tolist()
        rotation_transform.RotateZ(rpy[2])
        rotation_transform.RotateY(rpy[1])
        rotation_transform.RotateX(rpy[0])
        # Apply the rotation transform to the cylinder
        rotation_filter = vtk.vtkTransformPolyDataFilter()
        rotation_filter.SetInputConnection(cyl_source.GetOutputPort())
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
        actor.GetProperty().SetOpacity(alpha)

        return actor

    def set_actor_pose(self, actor, pose):
        px, py, pz, rx, ry, rz = pose
        actor.SetPosition(px, py, pz)
        actor.SetOrientation(rx, ry, rz)

    def reset_group_pose(self, pose=(0, 0, 0, 0, 0, 0)):
        """Set the entire assembly's position/orientation."""
        px, py, pz, rx, ry, rz = pose
        self.drone_assembly.SetPosition(px, py, pz)
        self.drone_assembly.SetOrientation(rx, ry, rz)
        self.shadow_assembly.SetPosition(px+0.1*pz, py+0.8*pz, -0.03)
        self.shadow_assembly.SetOrientation(rx*0, ry*0, rz)
        self.vtk_widget.GetRenderWindow().Render()


    def enable_pose_reset_timer(self, enable=True, frequency_hz=1.0):
        """
        Calls _on_pose_reset_timer at the given frequency. You can modify
        that method to do more sophisticated movement/animation.
        """
        if enable:
            if self.update_timer is None:
                self.update_timer = QTimer(self)
                self.update_timer.timeout.connect(self._on_pose_reset_timer)
            self.update_frequency_ms = int(1000 / frequency_hz)
            self.update_timer.start(self.update_frequency_ms)
        else:
            if self.update_timer is not None:
                self.update_timer.stop()

    def _on_pose_reset_timer(self):
        """Example: resets assembly to identity pose."""
        self.reset_group_pose((0,0,0, 0,0,0))


    def set_camera_pose(self, position, focal_point, view_up):
        self.camera.SetPosition(*position)
        self.camera.SetFocalPoint(*focal_point)
        self.camera.SetViewUp(*view_up)





    # -------------------------------------------------------------------------
    # Ground plane at z=0
    # -------------------------------------------------------------------------
    def _create_ground_plane(self, plane_size=100):
        """
        Creates a large plane in the x–y plane (z=0).
        plane_size controls half-width/height in each direction.
        """
        plane_source = vtk.vtkPlaneSource()
        # For a 20 x 20 plane, with center at (0,0,0):
        plane_source.SetOrigin(-plane_size, -plane_size, 0)
        plane_source.SetPoint1( plane_size, -plane_size, 0)
        plane_source.SetPoint2(-plane_size,  plane_size, 0)
        plane_source.SetNormal(0, 0, 1)  # z-up
        plane_source.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane_source.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Example: a neutral gray
        actor.GetProperty().SetColor(0.075, 0.75, 0.075)
        actor.GetProperty().SetOpacity(0.4+0.6)
        return actor


    def _create_ground_plane_texture(self, plane_size=100, texture_path="path/to/your/texture.png", tile_factor=100, plane_height=0.0):
        """
        Creates a large textured plane in the x–y plane (z=0).
        - `plane_size`: half-width/height in each direction.
        - `texture_path`: path to the PNG texture file.
        - `tile_factor`: how many times to repeat the texture in each direction.
        """
        # Create a plane source
        plane_source = vtk.vtkPlaneSource()
        plane_source.SetOrigin(-plane_size, -plane_size, plane_height)
        plane_source.SetPoint1(plane_size, -plane_size, plane_height)
        plane_source.SetPoint2(-plane_size, plane_size, plane_height)
        plane_source.SetNormal(0, 0, 1)  # Z-up
        plane_source.Update()

        # Get the polydata from the plane source
        polydata = plane_source.GetOutput()

        # Create texture coordinates for tiling
        texture_coords = vtk.vtkFloatArray()
        texture_coords.SetNumberOfComponents(2)  # 2D texture coordinates (U, V)
        texture_coords.SetName("TextureCoordinates")

        # Scale texture coordinates to repeat (tile_factor controls how many times it repeats)
        texture_coords.InsertNextTuple2(0.0, 0.0)                      # Bottom-left
        texture_coords.InsertNextTuple2(tile_factor, 0.0)              # Bottom-right
        texture_coords.InsertNextTuple2(0.0, tile_factor)              # Top-left
        texture_coords.InsertNextTuple2(tile_factor, tile_factor)      # Top-right

        # Apply texture coordinates to the plane
        polydata.GetPointData().SetTCoords(texture_coords)

        # Map the texture to the plane
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Load the PNG texture
        reader = vtk.vtkPNGReader()
        reader.SetFileName(texture_path)
        reader.Update()

        # Apply texture settings
        texture = vtk.vtkTexture()
        texture.SetInputConnection(reader.GetOutputPort())
        texture.RepeatOn()  # Enable texture tiling (repeating)
        texture.InterpolateOn()  # Smooth texture mapping

        # Apply texture to the actor
        actor.SetTexture(texture)

        return actor