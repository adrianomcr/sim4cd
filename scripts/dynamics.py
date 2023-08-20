#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Quadcopter simulation with PX4 integration


import numpy as np
import time

import actuators as ACT
import sensors as SENS
import silsim_comm as COM
import math_utils as MU
import ros_viz as VIZ


class quad_dynamics(object):
    """
    Drone dynamics class
    """

    def __init__(self, dt_, p0_,v0_,q0_,w0_):
        """
        Constructor
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
        self.tau = 0
        self.total_force = 0

        # Simulation time step
        self.dt = dt_



    def model_step(self, cmd):
        """
        Perform the dynamic integration step

        Parameters:
            cmd (numpy.ndarray): PWM values (from 0 to 1) for each actuator
        """

        # Compute force performed by each actuator
        f0 = ACT.thrust(cmd[0])
        f1 = ACT.thrust(cmd[1])
        f2 = ACT.thrust(cmd[2])
        f3 = ACT.thrust(cmd[3])

        # Actuators configuration
        #    2       0
        #      \ ^ /
        #        |
        #    1 /   \ 3

        # Compute total thrust
        self.tau = f0+f1+f2+f3
        if(self.p[2]<=0 and self.v[2]<0 and self.tau<self.m*self.g):
            self.tau = self.m*self.g*1.001
          
        # Compute total torque
        T = [0,0,0]
        T[0] = 0.15*(-f0+f1+f2-f3)
        T[1] = 0.15*(-f0+f1-f2+f3)
        T[2] = 0.06*(-f0-f1+f2+f3)
        T = np.array(T)

        # Compute linear drag
        f_drag = -self.drag_v*self.v
        # Compute angular drag
        T_drag = -self.drag_w*self.w

        # Compute torque due to gyroscopic effect
        Tg = np.array([0,0,0]) # TODO: blades gyroscopic effect

        # Compute non inertial forces acting on the drone
        tau_vec_b = np.array([0,0,self.tau]) # Actuation force in body frame [N]
        self.total_force = MU.quat_apply_rot(self.q,tau_vec_b) + f_drag
        # Compute kinematic acceleraion
        acc_w = np.array([0,0,-self.g]) + self.total_force/self.m

        # Dynamic model
        p_dot = self.v
        v_dot = acc_w
        q_dot = MU.quaternion_derivative(self.q,self.w)
        w_dot = (1/self.J)*(-self.J*np.cross(self.w,self.w) + T + T_drag)

        # Model integration
        self.p = self.p + p_dot*self.dt
        self.v = self.v + v_dot*self.dt
        self.q = self.q + q_dot*self.dt
        self.w = self.w + w_dot*self.dt

        # Quaternion renormalization
        self.q = MU.normalize(self.q)


    def get_pos(self):
        """
        Return the vehicle local position

        Returns:
            numpy.ndarray: Vehicle position  [m]
        """

        return self.p


    def get_vel_w(self):
        """
        Return the vehicle velocity in the world frame

        Returns:
            numpy.ndarray: Vehicle world velocity [m/sx]
        """

        return self.v


    def get_quat(self):
        """
        Return the vehicle orientation in an unit quaternion format

        Returns:
            numpy.ndarray: Vehicle orientation (qw, qx, qy, qz)
        """

        return self.q


    def get_omega(self):
        """
        Return the vehicle angular velocity in the body frame

        Returns:
            numpy.ndarray: Vehicle angular velocity [rad/s]
        """

        return self.w


    def get_tau(self):
        """
        Return the vehicle total thrust

        Returns:
            float: Vehicle total thrust [N]
        """

        return self.tau


    def get_total_force(self):
        """
        Return the sum of all forces getting applied to the vehicle except gravity

        Returns:
            numpy.ndarray: Applied non inertial forces [N]
        """

        return self.total_force
