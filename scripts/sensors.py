#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Class that contains the sensor models
# Compute the measurements based on the ground truth state
# Add noise and bias

# Ground truth
# Gyro
# Accelerometer
# Magnetometer
# Barometer
# GPS

import numpy as np
import random
from math import pi, sqrt, exp, sin, cos
from random import random
import time

import math_utils as MU


class sensors(object):
    """
    Sensors class
    """

    def __init__(self, params):
        """
        Constructor for the sensors class

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object
        """

        # Load model parameters
        self.load_parameters(params)


    def get_acc(self, q,f,m,induced_noises):
        """
        Return the acceleration measured by the accelerometer

        Parameters:
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
            f (numpy.ndarray): Total force applied to the vehicle except gravity [fx, fy, fz] [Newtons]
            m (float): Vehicles mass [kg]
            induced_noises (numpy.ndarray): Noise on the acceleration (3-axis) induced by the set of actuators [m/s2]
        
        Returns:
            acc (numpy.ndarray): Accelerometer measurement (3 axis) in meters per second square [m/s2]
        """

        # Compute accelerometer measurement and add random noise
        acc = MU.quat_apply_rot(MU.quat_conj(q),f/m) + np.random.normal(loc=0.0, scale=self.acc_noise_std, size=3)

        # Add noise induced by the actuators
        acc = acc + induced_noises

        # Rotate measurement to attend PX4 standard (NED)
        acc = np.array([acc[0],-acc[1],-acc[2]])

        return acc # m/s^2


    def get_gyro(self, w,induced_noises):
        """
        Return the angular velocity measured by the gyro

        Parameters:
            w (numpy.ndarray): Body angular velocity [wx, wy, wz] [rad/s]
            induced_noises (numpy.ndarray): Noise on the angular speed (3-axis) induced by the set of actuators [rad/s]

        Returns:
            gyro (numpy.ndarray): Gyro measurement (3 axis) in radians per second [rad/s]
        """

        # Compute gyroscope measurement and add random noise
        gyro = w + np.random.normal(loc=0.0, scale=self.gyro_noise_std, size=3)

        # Add noise induced by the actuators
        gyro = gyro + induced_noises

        # Rotate measurement to attend PX4 standard (NED)
        gyro = np.array([gyro[0],-gyro[1],-gyro[2]])

        return gyro # rad/s


    def get_mag(self, q,internal_field):
        """
        Return the magnetic field measured by the magnetometer

        Parameters:
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
            internal_field (numpy.ndarray): Noise on the magnetic field (3-axis) induced by the internal currents [G]

        Returns:
            mag (numpy.ndarray): Magnetometer measurement (3 axis) Gauss [G]
        """

        mag = np.array(self.earth_mag_field)

        # Compute Earth magnetic field on the body frame and add noise
        mag =  MU.quat_apply_rot(MU.quat_conj(q),mag) + np.random.normal(loc=0.0, scale=self.mag_noise_std, size=3)

        # Add the influence of the magnetic field generated internally on the local frame
        mag = mag + internal_field

        # Rotate measurement to attend PX4 standard (NED)
        mag = np.array([mag[0],-mag[1],-mag[2]])

        return mag # Gauss


    def get_baro(self, z):
        """
        Return the pressure measured by the barometer

        Parameters:
            z (float): Height 

        Returns:
            bar (float): Barometer measurement Hectopascal [hPa]
        """

        # Compute pressure given the height
        bar = self.pressure_sea * exp(-(z+self.h0) / self.C_bar)

        # Add noise to barometric pressure
        bar = bar + np.random.normal(loc=0.0, scale=self.bar_noise_std, size=1)

        # Inverse model
        # z =  -self.C_bar*ln(bar/self.pressure_sea)-self.h0

        return bar # hPa


    def get_gps(self, p,vw):
        """
        Return a dictionary with the GPS information

        Parameters:
            p (numpy.ndarray): Position vector [x, y, z]
            vw (numpy.ndarray): World velocity vector [vx, vy, vz]

        Returns:
            gps (dict): Python dictionary with the GPS data
        """

        # Dictionary with the GPS information
        gps = {}

        # Populate dictionary
        gps['i_lat__degE7'] = ( self.lat0+(p[1]+np.random.normal(scale=self.gps_noise_std_xy))*self.meters2deg_lat )*1e7    # Latitude (WGS84) [degE7] (type:int32_t)
        gps['i_lon__degE7'] = ( self.lon0+(p[0]+np.random.normal(scale=self.gps_noise_std_xy))*self.meters2deg_lon )*1e7    # Longitude (WGS84) [degE7] (type:int32_t)
        gps['i_alt__mm'] = ( self.h0 + p[2] + np.random.normal(scale=self.gps_noise_std_xy) )*1000                          # Altitude (MSL). Positive for up. [mm] (type:int32_t)
        gps['i_eph__cm'] = ( 0 + random()*0.001 )*100                                                                       # GPS HDOP horizontal dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        gps['i_epv__cm'] = ( 0 + random()*0.001 )*100                                                                       # GPS VDOP vertical dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        gps['i_vel__cm/s'] = 65535                                                                                          # GPS ground speed. If unknown, set to: 65535 [cm/s] (type:uint16_t)
        gps['i_vn__cm/s'] = ( vw[1] + random()*0.001 )*100                                                                  # GPS velocity in north direction in earth-fixed NED frame [cm/s] (type:int16_t)
        gps['i_ve__cm/s'] = ( vw[0] + random()*0.001 )*100                                                                  # GPS velocity in east direction in earth-fixed NED frame [cm/s] (type:int16_t)
        gps['i_vd__cm/s'] = ( -vw[2] + random()*0.001 )*100                                                                 # GPS velocity in down direction in earth-fixed NED frame [cm/s] (type:int16_t)
        gps['i_cog__cdeg'] = ( 0 + self.crandom()*0.001 )*100                                                               # Course over ground (NOT heading, but direction of movement), 0.0..359.99 degrees. If unknown, set to: 65535 [cdeg] (type:uint16_t)  
        
        return gps


    def get_ground_truth(self, p,vw,q,omega):
        """
        Return a dictionary with the ground truth information

        Parameters:
            p (numpy.ndarray): Position vector [x, y, z]
            vw (numpy.ndarray): World velocity vector [vx, vy, vz]
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
            omega (numpy.ndarray): Body angular velocity [wx, wy, wz]

        Returns:
            gt (dict): Python dictionary with the ground truth data
        """

        # Compute orientation of front/right/down frame with respect with the (NED) frame
        q_rot = MU.quat_mult(MU.quat_mult(np.array([0,1,0,0]),q),np.array([0,1,0,0]))
        # TODO: Check used reference for yaw in the ground truth

        # Dictionary with the ground truth information
        gt = {}

        # Populate dictionary
        gt['attitude_quaternion'] = q_rot.tolist()
        gt['rollspeed'] = omega[0]                             # Body frame roll / phi angular speed [rad/s] (type:float)
        gt['pitchspeed'] = -omega[1]                           # Body frame pitch / theta angular speed [rad/s] (type:float)
        gt['yawspeed'] = -omega[2]                             # Body frame yaw / psi angular speed [rad/s] (type:float)
        gt['i_lat__degE7'] = (self.lat0+p[1]*self.meters2deg_lat)*1e7    # Latitude [degE7] (type:int32_t)
        gt['i_lon__degE7'] = (self.lon0+p[0]*self.meters2deg_lon)*1e7    # Longitude [degE7] (type:int32_t)
        gt['i_alt__mm'] = self.h0 + p[2]                            # Altitude [mm] (type:int32_t)
        gt['vx'] = vw[1]*100                                   # Ground X Speed (Latitude) [cm/s] (type:int16_t)
        gt['vy'] = vw[0]*100                                   # Ground Y Speed (Longitude) [cm/s] (type:int16_t)
        gt['vz'] = -vw[2]*100                                  # Ground Z Speed (Altitude) [cm/s] (type:int16_t)
        gt['ind_airspeed'] = MU.norm(vw)*100                   # Indicated airspeed [cm/s] (type:uint16_t)
        gt['true_airspeed'] = MU.norm(vw)*100                  # True airspeed [cm/s] (type:uint16_t)
        gt['xacc'] = 0                                         # X acceleration [mG] (type:int16_t)
        gt['yacc'] = 0                                         # Y acceleration [mG] (type:int16_t)
        gt['zacc'] = 0                                         # Z acceleration [mG] (type:int16_t)

        return gt


    def crandom(self):
        """
        Return a random value with distribution around 0
        """
        return random()-0.5


    def load_parameters(self, params):
        """
        Load parameters necessary for the sensors and store them in the instance variables

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object that contains the values of interest
        """

        # Global environmental values
        self.pressure_sea = params.get_parameter_value('ENV_PRES_SEA') # Sea level standard atmospheric pressure [hPa]
        g =  params.get_parameter_value('ENV_GRAVITY') # Earth-surface gravitational acceleration [m/ss]
        M = params.get_parameter_value('ENV_MOL_MASS') # Molar mass of dry air [kg/mol]
        T0 = params.get_parameter_value('ENV_TMP_SEA') # Sea level standard temperature [K]
        R0 = params.get_parameter_value('ENV_GAS_CTE') # Universal gas constant [J/(mol*K)]
        self.C_bar = (T0*R0)/(g*M)
            
        # Local environmental values
        self.lat0 = params.get_parameter_value('SENS_LAT_ORIGIN') # initial latitude (degrees)
        self.lon0 = params.get_parameter_value('SENS_LON_ORIGIN') # initial longitude (degrees)
        self.h0 = params.get_parameter_value('SENS_ALT_ORIGIN') # initial altitude (meters above average sea level)
        magx = params.get_parameter_value('SENS_MAG_FIELD_E')
        magy = params.get_parameter_value('SENS_MAG_FIELD_N')
        magz = params.get_parameter_value('SENS_MAG_FIELD_U')
        self.earth_mag_field = [magx, magy, magz] # Local Earth magnetic field (East, North, UP) in Gauss

        # Values for the conversion between local position and geographic coordinates
        earth_radius = 6378100
        small_radius = earth_radius*sqrt(1 - sin(self.lat0*pi/180)**2)
        self.meters2deg_lat =  180 / ( earth_radius * pi)
        self.meters2deg_lon =  180 / ( small_radius * pi)

        # Standard deviations of sensor noise
        self.acc_noise_std = params.get_parameter_value('SENS_ACC_NOISE_STD')
        self.gyro_noise_std = params.get_parameter_value('SENS_GYRO_NOISE_STD')
        self.mag_noise_std = params.get_parameter_value('SENS_MAG_NOISE_STD')
        self.bar_noise_std = params.get_parameter_value('SENS_BAR_NOISE_STD')
        self.gps_noise_std_xy = params.get_parameter_value('SENS_GPS_STD_XY')
        self.gps_noise_std_z = params.get_parameter_value('SENS_GPS_STD_Z')

        