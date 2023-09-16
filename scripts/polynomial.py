#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# N-th order polynomials class

class polynomial:
    """
    Class that represents a polynomial
    """

    def __init__(self, coefficients):
        """
        Constructor for the polynomial class

        Parameters:
            coefficients (list of float): Coefficients of the polynomial
                [c0, c1, c2, c3, ...]
                p(u) = c0 + c1*u + c2*u**2 + c3*u**3 + ...
        """

        # Store the coefficients of the polynomial
        self.c = coefficients
        # Store the number of coefficients
        self.L = len(coefficients)
        # Store the order of the polynomial
        self.N = self.L - 1


    def eval(self, u):
        """
        Compute the value of the polynomial at u

        Returns:
            u (float): Parameter in which the value of the polynomial will be evaluated

        Returns:
            p (float): Value p(u) of the polynomial at the parameter u
        """

        power = 1
        p = 0
        for i in range(self.L):
            p = p + self.c[i]*power
            power = power*u

        return p


    def set_coefficients(self, coefficients):
        """
        Set new coefficients for the polynomial

        Parameters:
            coefficients (list of float): Coefficients of the polynomial
        """

        # Reset the coefficients of the polynomial
        self.c = coefficients
        # Recompute the number of coefficients
        self.L = len(coefficients)
        # Recompute the order of the polynomial
        self.N = self.L - 1


    def get_order(self):
        """
        Set new coefficients for the polynomial

        Returns:
            self.N (int): Order of the polynomial
        """

        return self.N