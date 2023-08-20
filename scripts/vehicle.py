#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Vehicle geometry
# Compute the collective action of a set of actuators arranged in a given geometric distribution

import actuators as ACT

# TODO: Everything

class vehicle_geometry:
    """
    Class that represents the geometric collection of actuators of a vehicle
    """

    def __init__(self):
        """
        Constructor for the prop_actuator class
        """

        self.force = 0
        self.torque = 0
        self.sig = cw_ccw # 1 or -1

        self.actuators = []
        self.positions = []
        self.directions = []


    def get_omega(self):

        return self.omega



