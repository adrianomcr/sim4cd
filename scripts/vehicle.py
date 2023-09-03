#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Vehicle geometry definition
# Responsible to compute the collective action of a set of actuators arranged in a given geometric distribution

import time
import numpy as np

import actuators as ACT
import math_utils as MU

class vehicle_geometry:
    """
    Class that represents the geometric collection of actuators of a vehicle
    """

    def __init__(self, params):
        """
        Constructor for the vehicle_geometry class

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object
        """

        self.cmds = [0, 0, 0, 0] # List of the PWM commands for the actuators
        self.forces = [0, 0, 0, 0] # List of forces being exercised by each actuator
        self.torques = [0, 0, 0, 0] # List of torques being exercised by each actuator
        self.total_force = np.array([0, 0, 0]) # Collective force vector exercised by the actuators
        self.total_torque = np.array([0, 0, 0]) # Collective torque vector exercised by the actuators

        # Actuators configuration TODO: Remove as it is old
        #    2       0
        #      \ ^ /
        #        |
        #    1 /   \ 3

        # Load model parameters
        self.load_parameters(params)

        # Define the four actuator objects
        act0 = ACT.prop_actuator(self.spin[0]) # spins counter clock wise
        act1 = ACT.prop_actuator(self.spin[1]) # spins counter clock wise
        act2 = ACT.prop_actuator(self.spin[2]) # spins clock wise
        act3 = ACT.prop_actuator(self.spin[3]) # spins clock wise
        # Define the list of actuator objects
        self.actuators = [act0,
                          act1,
                          act2,
                          act3]

        # Initialize the last time variable for time step computation
        self.last_time = time.time()


    def vehicle_sim_step(self, cmds_):
        """
        Constructor for the vehicle_geometry class

        Parameters:
            cmds_ (list): List of PWM values (from 0 to 1) for the actuators

        Returns:
            self.total_force (numpy.ndarray): Collective force the vehicle is receiving from the actuators [N]
            self.total_torque (numpy.ndarray): Collective torque the vehicle is receiving from the actuators [Nm]
        """

        # Set the received command
        self.cmds = cmds_

        # Compute the simulation time step
        time_now = time.time()
        dt = time_now-self.last_time
        self.last_time = time_now
        # Reset actuator it it was not receiving commands for a while TODO: check necessity
        if(dt > 1):
            self.reset()
        
        # Compute the forces and torques generated by each actuator
        for i, act in enumerate(self.actuators):
            self.forces[i], self.torques[i] = self.actuators[i].actuator_sim_step(self.cmds[i])

        # Initialize the computation of the collective force and torque
        self.total_force = np.array([0, 0, 0])
        self.total_torque = np.array([0, 0, 0])
        # Include the contribution of each actuator to the collective force and torque
        for i, act in enumerate(self.actuators):
            # Include vehicles body force generated by the actuator force
            self.total_force = self.total_force + self.forces[i]*self.directions[i]
            # Include vehicles body torque generated by the actuator force
            self.total_torque = self.total_torque + self.forces[i]*np.cross(self.positions[i],self.directions[i])
            # Include vehicles body torque generated by the actuator torque
            self.total_torque = self.total_torque + self.torques[i]*self.directions[i]

        # Return the collective force and torque the vehicle is receiving from the actuators
        return self.total_force, self.total_torque



    def gyroscopic_torque(self,omega):
        """
        Compute the gyroscopic effect due to the spinning actuators as an quivalent torque for a rigid body

        Parameters:
            omega (numpy.ndarray): Vehicle angular velocity (3-axis) in the body frame [rad/s]

        Returns:
            Tg (numpy.ndarray): Torque in th body frame that represents the gyroscopic effect [Nm]
        """

        # Initialize the Tg variable
        Tg = np.array([0, 0, 0])
        # Account for the effect of each actuator
        for i, act in enumerate(self.actuators):
            Tg = Tg + (-1*self.spin[i]*self.Jr*np.cross(omega,self.directions[0]*act.get_omega()))

        return Tg


    def load_parameters(self, params):
        """
        Load parameters for the vehicle geometry and store them in the instance variables

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object that contains the values of interest
        """

        self.act_num = params.get_parameter_value('VEH_ACT_NUM')
        self.Jr = params.get_parameter_value('VEH_J_ROTOR')

        self.spin = []
        self.positions = []
        self.directions = []
        for i in range(self.act_num):
            self.spin.append( params.get_parameter_value(f'VEH_ACT{i}_SPIN') )
            self.positions.append(np.array([]))
            self.directions.append(np.array([]))
            for d in ['X','Y','Z']:
                self.positions[i] = np.append(self.positions[i], params.get_parameter_value(f'VEH_ACT{i}_POS_{d}'))
                self.directions[i] = np.append(self.directions[i], params.get_parameter_value(f'VEH_ACT{i}_DIR_{d}'))

        # Make sure all of the directions are unit norm vectors
        for i in range(self.act_num):
            self.directions[i] = MU.normalize(self.directions[i])


    def reset(self):
        """
        Reset the forces the vehicles actuators are producing
        """

        # Reset actuators
        for i, act in enumerate(self.actuators):
            self.actuators[i].reset()
        
        # Reset total force and torque
        self.total_force = np.array([0, 0, 0])
        self.total_force = np.array([0, 0, 0])


    def get_cmds(self):
        """
        Get the commands list
        
        Returns:
            self.cmds (numpy.ndarray): List with commands of each actuator [PWM]
        """

        return self.cmds


    def get_force(self):
        """
        Get the collective force (in body frame) the vehicles actuators are producing
        
        Returns:
            self.total_force (numpy.ndarray): Collective force vector the actuators are exercising [N]
        """

        return self.total_force


    def get_torque(self):
        """
        Get the collective torque (in body frame) the vehicles actuators are producing
        
        Returns:
            self.total_torque (numpy.ndarray): Collective torque vector the actuators are exercising [Nm]
        """
        
        return self.total_torque


    def get_actuators_positions(self):
        """
        Get a list with the angular positions of the actuators
        
        Returns:
            self.total_torque (numpy.ndarray): Collective torque vector the actuators are exercising [Nm]
        """

        ang_pos_list = [a.get_angular_position() for a in self.actuators]
        
        return ang_pos_list


    def get_acc_noise_combined(self):
        """
        Get the combined noise the actuators inject on the vehicle's acceleration
        
        Returns:
            acc_combined_noise (numpy.ndarray): Collective acceleration (3-axis) noise caused by the set of actuators [m/s2]
        """

        # Add the acceleration noise induced by all of the actuators
        acc_combined_noise = sum(a.acc_induced_noise() for a in self.actuators)

        return acc_combined_noise # [m/s2]


    def get_gyro_noise_combined(self):
        """
        Get the combined noise the actuators inject on the vehicle's angular speed
        
        Returns:
            gyro_combined_noise (numpy.ndarray): Collective angular speed (3-axis) noise caused by the set of actuators [rad/s]
        """

        # Add the angular speed noise induced by all of the actuators
        gyro_combined_noise = sum(a.gyro_induced_noise() for a in self.actuators)

        return gyro_combined_noise


    def get_total_current(self):
        """
        Get the combined current used by all of the actuators
        
        Returns:
            total_current (float): Total current being consumed by all of the actuators [A]
        """

        # Add the current being consumed by all of the actuators
        total_current = sum(a.current for a in self.actuators)

        return total_current


    def get_mag_noise(self):
        """
        Get the internal magnetic noise caused by the total internal current
        
        Returns:
            mag_noise (numpy.ndarray): Internal magnetic field (3-axis) cause by internal currents [G]
        """

        # Compute the internal magnetic field
        mag_noise = np.array([-0.14, -0.02, -0.08])*(self.get_total_current()/40)**2 #TODO: improve model

        return mag_noise