#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Definition of constants

# TODO: Replace by proper config file

from math import pi, sqrt, sin

# Global environmental values
pressure_sea = 1013.25 # Sea level standard atmospheric pressure [hPa]
g = 9.80665 # Earth-surface gravitational acceleration [m/ss]
M = 0.02896968 # Molar mass of dry air [kg/mol]
T0 = 288.16 # Sea level standard temperature [K]
R0 = 8.314462618 # Universal gas constant [J/(mol*K)]
C_bar = (T0*R0)/(g*M)
# Reference: https://en.wikipedia.org/wiki/Atmospheric_pressure
       
# # Local environmental values defined the Equator X Greenwich
# lat0 = 0.0 # initial latitude (degrees)
# lon0 = 0.0 # initial longitude (degrees)
# h0 = 0.0 # initial altitude (meters above average sea level)
# earth_mag_field = [0.22923, 0.02772, 0.11998] # Earth magnetic field (North, West, UP) in Gauss
# # Check Earth magnetic field at: http://www.geomag.bgs.ac.uk/data_service/models_compass/wmm_calc.html

# Local environmental values defined for NEA parking
lat0 = 40.448985 # initial latitude (degrees)
lon0 = -79.898025 # initial longitude (degrees)
h0 = 372.0 # initial altitude (meters above average sea level)
earth_mag_field = [0.16928, 0.02559, -0.39550] # Local Earth magnetic field (North, West, UP) in Gauss
# Check Earth magnetic field at: http://www.geomag.bgs.ac.uk/data_service/models_compass/wmm_calc.html

# Values for the conversion between local position and geographic coordinates
earth_radius = 6378100
small_radius = earth_radius*sqrt(1 - sin(lat0*pi/180)**2)
meters2ged_lat =  180 / ( earth_radius * pi)
meters2ged_lon =  180 / ( small_radius * pi)
