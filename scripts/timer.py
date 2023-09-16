#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Simple timer class

from math import pi, sin
import time
import numpy as np


class timer:
    """
    Class that represents a timer
    """

    def __init__(self, frequency=None, period=None, slip_correction=False, enabled=True):
        """
        Constructor for the battery class

        Parameters:
            frequency (float): Frequency of the timer
            period (float): Period of the timer
            slip_correction (bool): Correct for time slip (True) or not (False) [Not implemented yet]
            enabled (bool): Enable (True) the timer or not (False)
        """

        if frequency is None and period is None:
            print("\33[91mTimer was not initialized with any value. Exiting.\33[0m")
            exit()
            return
        elif frequency is None:
            self.T = period
            self.f = 1.0/self.T
        elif period is None:
            self.f = frequency
            self.T = 1.0/self.f
        else:
            self.f = frequency
            self.T = 1.0/self.f
            print("\33[93mTimer ignoring value of period and using the provided frequency.\33[0m")

        # Save the current time (or, last time a method was called)
        self.time = time.time()

        # Initialize the last time that the time ticked
        self.last_tick = -1

        # Save the time slip variable
        self.slip = 0.0

        # Save the time the timer was created
        self.t_born = self.time

        # Store if the timer is enabled or not
        self.en = enabled


    def tick(self):
        """
        Check if the amount of time passed since the last tick is greater that the timer period

        Returns:
            (bool): Boolean indicating if a timer tick occurred (True) or not (False)
        """

        if (not self.en):
            return False

        self.time = time.time()
        if(self.time - self.last_tick > self.T):
            self.slip = self.time - self.last_tick - self.T
            self.last_tick = self.time
            return True
        else:
            return False


    def set_frequency(self, frequency):
        """
        Set the frequency of the timer

        Parameters:
            frequency (float): Timer frequency
        """

        self.f = frequency
        self.T = 1/self.f


    def set_period(self, period):
        """
        Set the period of the timer

        Parameters:
            period (float): Timer period
        """

        self.T = period
        self.f = 1/self.T


    def enable(self):
        """
        Enable the timer
        """
        self.en = True


    def disable(self):
        """
        Disable the timer
        """
        self.en = False
        
