#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Rigid body dynamics of 

import numpy as np
import time

import vehicle as VEH
# import sensors as SENS
import math_utils as MU


class quad_dynamics(object):
    """
    Drone dynamics class
    """

    def __init__(self, dt_max_, p0_,v0_,q0_,w0_):
        """
        Constructor for the dynamics class

        Parameters:
            dt_max_ (float): Maximum
            p0_ (numpy.ndarray): Vehicle initial position [m]
            v0_ (numpy.ndarray): Vehicle initial world velocity [m/s]
            q0_ (numpy.ndarray): Vehicle initial orientation (qw, qx, qy, qz)
            w0_ (numpy.ndarray): Vehicle initial angular velocity [rad/s]
        """

        # Model constants
        self.g = 9.81
        self.m = 2.0
        self.drag_v = 0.1
        self.drag_w = 0.01
        self.J = 0.006*10

        # Initialize states
        self.p = p0_ # position in the world frame
        self.v = v0_ # velocity in the world frame
        self.q = q0_ # orientation (as a quaternion) in the world frame
        self.w = w0_ # angular velocity in the body frame

        # Important variables
        self.Force_b = np.array([0, 0, 0])
        self.Torque_b = np.array([0, 0, 0])
        self.total_force_w = np.array([0, 0, 0])

        # Maximum desired simulation time step
        self.dt_max = dt_max_

        # Define the vehicle geometry
        self.vehicle_geo = VEH.vehicle_geometry()

        # Initialize the last time variable for time step computation
        self.last_time = time.time()


    def model_step(self, cmd):
        """
        Perform the dynamic integration step

        Parameters:
            cmd (numpy.ndarray): PWM values (from 0 to 1) for each actuator
        """

        # Compute the (variable) time step
        time_now = time.time()
        dt = time_now-self.last_time
        self.last_time = time_now

        # Throw a warning if the simulation is computationally heavy
        if(dt > self.dt_max):
            print("\33[93m[Warning] simulation loop took too long to compute: %f ms\33[0m" % (dt*1000))

        # Compute the forces and torques that the actuators are applying to the vehicle body
        self.Force_b, self.Torque_b = self.vehicle_geo.vehicle_sim_step(cmd)

        # Temporary trick to stop the drone before takeoff
        if(self.p[2]<=0 and self.v[2]<0 and MU.norm(self.Force_b)<self.m*self.g):
            self.Force_b = [0,0,self.m*self.g*1.001]

        # Compute linear drag
        f_drag = -self.drag_v*self.v
        # Compute angular drag
        T_drag = -self.drag_w*self.w

        # Compute torque due to gyroscopic effect
        Tg = np.array([0,0,0]) # TODO: implement blades gyroscopic effect

        # Compute non inertial forces acting on the drone
        self.total_force_w = MU.quat_apply_rot(self.q,self.Force_b) + f_drag
        # Compute kinematic acceleraion
        acc_w = np.array([0,0,-self.g]) + self.total_force_w/self.m

        # Dynamic model
        p_dot = self.v
        v_dot = acc_w
        q_dot = MU.quaternion_derivative(self.q,self.w)
        w_dot = (1/self.J)*(-self.J*np.cross(self.w,self.w) + self.Torque_b + T_drag) #TODO: fix J

        # Model integration (variable time step)
        self.p = self.p + p_dot*dt
        self.v = self.v + v_dot*dt
        self.q = self.q + q_dot*dt
        self.w = self.w + w_dot*dt

        # Quaternion renormalization
        self.q = MU.normalize(self.q)


    def get_states(self):
        """
        Return the vehicles states

        Returns:
            self.p (numpy.ndarray): Vehicle position [m]
            self.v (numpy.ndarray): Vehicle world velocity [m/s]
            self.q (numpy.ndarray): Vehicle orientation (qw, qx, qy, qz)
            self.w (numpy.ndarray): Vehicle angular velocity [rad/s]
        """

        return self.p, self.v, self.q, self.w


    def get_pos(self):
        """
        Return the vehicle local position

        Returns:
            self.p (numpy.ndarray): Vehicle position [m]
        """

        return self.p


    def get_vel_w(self):
        """
        Return the vehicle velocity in the world frame

        Returns:
            self.v (numpy.ndarray): Vehicle world velocity [m/s]
        """

        return self.v


    def get_quat(self):
        """
        Return the vehicle orientation in an unit quaternion format

        Returns:
            self.q (numpy.ndarray): Vehicle orientation (qw, qx, qy, qz)
        """

        return self.q


    def get_omega(self):
        """
        Return the vehicle angular velocity in the body frame

        Returns:
            self.w (numpy.ndarray): Vehicle angular velocity [rad/s]
        """

        return self.w


    def get_tau(self):
        """
        Return the vehicle total thrust

        Returns:
            tau (float): Vehicle total thrust [N]
        """
        
        tau = MU.norm(self.Force_b)

        return tau #TODO: Revise this. In general, it does not make sense


    def get_total_force(self):
        """
        Return the sum of all forces getting applied to the vehicle except gravity

        Returns:
            self.total_force_w (numpy.ndarray): Applied non inertial forces [N]
        """

        return self.total_force_w
