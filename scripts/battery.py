#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Battery modeling

from math import pi, sin
import time
import numpy as np
# import math_utils as MU
import polynomial as POLY


class battery:
    """
    Class that represents a battery
    """

    def __init__(self, params):
        """
        Constructor for the battery class

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object
        """

        # Load model parameters
        self.load_parameters(params)

        # Initialize the last time variable for time step computation
        self.last_time = time.time()


    def load_parameters(self, params):
        """
        Load parameters for the actuator with id act_id and store them in the instance variables

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object that contains the values of interest
        """

        self.full_charge = params.get_parameter_value("BAT_FULL_CHARGE")          # [mAh]
        self.init_charge = params.get_parameter_value("BAT_INIT_CHARGE")          # [%]
        self.n_cells = params.get_parameter_value("BAT_N_CELLS")                  #
        self.idle_current = params.get_parameter_value("PWR_IDLE_CURRENT")        # [A]
        self.internal_R = params.get_parameter_value("BAT_INTERNAL_RES")          # [Ohms]
        self.discharge_rate = params.get_parameter_value("BAT_DISCHARGE_RATE")    #
        
        # Initialize the State Of Charge variable
        self.soc = self.init_charge/100             # value from 0 to 1
        # Initialize the quarge of the battery
        self.q = self.soc * self.full_charge*3.6    # Coulomb [A*s]

        # Parameter of the polynomial that maps the SOC (State Of Charge) to a single LiPo cell voltage
        # Based on data available at: Gandolfo, Daniel, et al. "Dynamic model of lithium polymer battery–load resistor method for electric parameters identification." Journal of the Energy Institute 88.4 (2015): 470-479.
        volt_constants = [2.5881836050934073, 19.977045504620776, -140.6535733701412, 515.4239704625197, -1057.4258331010678, 1226.7602703659068, -750.1861137479827, 187.73276915201495]
        # Define a polynomial to compute the LiPo cell voltage
        self.poly_cell_voltage = POLY.polynomial(volt_constants)


    def battery_sim_step(self, I_):
        """
        Perform the integration step for the battery

        Parameters:
            I_ (float): Extra current drown by the powered system [A]
                        Does not count for the idle current

        Returns:
            Vout (float): Voltage in the output of the battery [V]
        """

        # Set the total current based on the current drown by the motors
        self.I = I_ + self.idle_current

        # Compute the simulation time step
        time_now = time.time()
        dt = time_now-self.last_time
        self.last_time = time_now
        
        # Update the amount of charge left based on the current
        self.q = self.q - self.I*dt
        # Update the normalized state of charge 
        self.soc = (self.q/3.6)/self.full_charge

        # Compute the battery output voltage
        Vout = self.output_voltage()

        return Vout


    def internal_voltage(self):
        """
        Compute the battery internal voltage based on the state of charge

        Returns:
            self.E (float): Voltage in the output of the battery [V]
        """

        # Compute the battery internal voltage based on the polynomial fit for a LiPo cell
        E_per_cell = self.poly_cell_voltage.eval(self.soc)

        # Account for the number of cells
        self.E = E_per_cell*self.n_cells

        return self.E


    def output_voltage(self):
        """
        Compute the battery output voltage based on the state of charge and the current

        Returns:
            V (float): Voltage in the output of the battery [V]
        """
        
        # Compute the output voltage accounting for voltage drop dur to internal resistance
        self.V = self.internal_voltage() - self.internal_R*self.I

        return self.V

