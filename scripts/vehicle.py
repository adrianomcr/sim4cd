#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Vehicle geometry definition
# Responsible to compute the collective action of a set of actuators arranged in a given geometric distribution

import time
import numpy as np

import actuators as ACT
import math_utils as MU


# TODO: Everything

class vehicle_geometry:
    """
    Class that represents the geometric collection of actuators of a vehicle
    """

    def __init__(self):
        """
        Constructor for the prop_actuator class
        """

        self.cmd = np.array([0, 0, 0, 0])
        self.forces = [0, 0, 0, 0]
        self.torques = [0, 0, 0, 0]
        self.total_force = np.array([0, 0, 0])
        self.total_torque = np.array([0, 0, 0])
        self.d = 0.15


        act0 = ACT.prop_actuator(1) # spins clock wise
        act1 = ACT.prop_actuator(1)
        act2 = ACT.prop_actuator(-1) # spins counter clock wise
        act3 = ACT.prop_actuator(-1)
        self.actuators = [act0,
                          act1,
                          act2,
                          act3]

        self.positions = [np.array([self.d, -self.d, 0]),
                          np.array([-self.d, self.d, 0]),
                          np.array([self.d, self.d, 0]),
                          np.array([-self.d, -self.d, 0])]
        self.directions = [np.array([0, 0, 1]),
                           np.array([0, 0, 1]),
                           np.array([0, 0, 1]),
                           np.array([0, 0, 1])]
        # Actuators configuration
        #    2       0
        #      \ ^ /
        #        |
        #    1 /   \ 3
        for i, act in enumerate(self.actuators):
            self.directions[i] = MU.normalize(self.directions[i])

        self.last_time = time.time()



    def vehicle_sim_step(self, cmd_):

        self.cmd = cmd_

        time_now = time.time()
        dt = time_now-self.last_time
        self.last_time = time_now
        if(dt > 1):
            self.reset()
        
        self.total_force = np.array([0, 0, 0])
        self.total_torque = np.array([0, 0, 0])

        
        for i, act in enumerate(self.actuators):
            self.forces[i], self.torques[i] = self.actuators[i].actuator_sim_step(self.cmd[i])

        for i, act in enumerate(self.actuators):
            self.total_force = self.total_force + self.forces[i]*self.directions[i]
            self.total_torque = self.total_torque + self.forces[i]*np.cross(self.positions[i],self.directions[i])
            self.total_torque = self.total_torque + self.torques[i]*self.directions[i]


        return self.total_force, self.total_torque



    def reset(self):

        for i, act in enumerate(self.actuators):
            self.actuators[i].reset()
        
        self.total_force = np.array([0, 0, 0])
        self.total_force = np.array([0, 0, 0])

    def get_force(self):

        return self.total_force

    def get_torque(self):

        return self.total_torque

