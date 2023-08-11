#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Sensor models
# Compute the measurements based on the GT state
# Add noise and bias

# Gyro
# Accelerometer
# Magnetometer
# Barometer
# GPS


import numpy as np
import random
from math import exp
import math_utils as MU


def get_acc(q,f,m):

    acc0 = MU.quat_apply_rot(MU.quat_conj(q),f/m) + np.random.normal(loc=0.0, scale=0.05, size=3)

    acc = np.array([acc0[0],-acc0[1],-acc0[2]])

    return acc # m/s^2


def get_gyro(w):

    gyro0 = w + np.random.normal(loc=0.0, scale=0.02, size=3)
    gyro = np.array([gyro0[0],-gyro0[1],-gyro0[2]])

    return gyro # rad/s


def get_mag(q,tau):

    # mag0 = np.array([0.5,0,-0.1]) + np.random.normal(loc=0.0, scale=0.01, size=3)
    mag0 = np.array([0.16928, 0.02559, -0.39550]) + np.random.normal(loc=0.0, scale=0.01, size=3)
    # 0.16928
    # -0.02559
    # 0.39550
    #http://www.geomag.bgs.ac.uk/data_service/models_compass/wmm_calc.html
    #apply the rotation here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    mag0 =  MU.quat_apply_rot(MU.quat_conj(q),mag0)
    mag = np.array([mag0[0],-mag0[1],-mag0[2]])

    return mag # Gauss


def get_baro(z):

    #bar = 1013.25 - 100*(z/1000) + np.random.normal(loc=0.0, scale=0.001, size=1)
    bar = 1013.25 * exp(-(z+372) / 8400) + np.random.normal(loc=0.0, scale=0.001, size=1)
    # ~ sea level plus altitude


    return bar #hPa


from random import random
def crandom():
    return random()-0.5

def get_gps(p):


    gps = {}

    meters2ged =  180 / ( 6378100 *  3.14159265359)

    # gps['i_lat__degE7'] = round((40.448985 + p[0]*meters2ged +  np.random.normal(loc=0.0, scale=0.0000001, size=1)[0])*1e7)
    # gps['i_lon__degE7'] = round((-79.898025 + p[1]*meters2ged + np.random.normal(loc=0.0, scale=0.0000001, size=1)[0])*1e7)
    # gps['i_alt__mm'] = round((0 + p[2] + np.random.normal(loc=0.0, scale=0.5, size=1)[0])*1000)
    # gps['i_eph__cm'] = 0.3 + random.randrange(3)-1
    # gps['i_epv__cm'] = 0.4 + random.randrange(3)-1
    # gps['i_vel__cm/s'] = 0 + random.randrange(3)-1
    # gps['i_vn__cm/s'] = 0 + random.randrange(3)-1
    # gps['i_ve__cm/s'] = 0 + random.randrange(3)-1
    # gps['i_vd__cm/s'] = 0 + random.randrange(3)-1
    # gps['i_cog__cdeg'] = 0 + random.randrange(3)-1


    gps['i_lat__degE7']               = round((   40.448985+p[0]*meters2ged   +crandom()*5e-8     )*1e7)
    gps['i_lon__degE7']               = round((   -79.898025-p[1]*meters2ged     +crandom()*5e-8     )*1e7)
    gps['i_alt__mm']                  = round((   372+ p[2]         +crandom()*0.05     )*1000)
    gps['i_eph__cm']                  = round((   0.3         + random()*0.001    )*100)
    gps['i_epv__cm']                  = round((   0.4         + random()*0.001    )*100)
    gps['i_vel__cm/s']                = round((   0           + random()*0.001    )*100)
    gps['i_vn__cm/s']                 = round((   0           + random()*0.001    )*100)
    gps['i_ve__cm/s']                 = round((   0           + random()*0.001    )*100)
    gps['i_vd__cm/s']                 = round((   0           + random()*0.001    )*100)
    gps['i_cog__cdeg']                = round((   0           +crandom()*0.001    )*100)

    # lat                 = gps['i_lat__degE7']     # Latitude (WGS84) [degE7] (type:int32_t)
    # lon                 = gps['i_lon__degE7']     # Longitude (WGS84) [degE7] (type:int32_t)
    # alt                 = gps['i_alt__mm']        # Altitude (MSL). Positive for up. [mm] (type:int32_t)
    # eph                 = gps['i_eph__cm']        # GPS HDOP horizontal dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
    # epv                 = gps['i_epv__cm']        # GPS VDOP vertical dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
    # vel                 = gps['i_vel__cm/s']      # GPS ground speed. If unknown, set to: 65535 [cm/s] (type:uint16_t)
    # vn                  = gps['i_vn__cm/s']       # GPS velocity in north direction in earth-fixed NED frame [cm/s] (type:int16_t)
    # ve                  = gps['i_ve__cm/s']       # GPS velocity in east direction in earth-fixed NED frame [cm/s] (type:int16_t)
    # vd                  = gps['i_vd__cm/s']       # GPS velocity in down direction in earth-fixed NED frame [cm/s] (type:int16_t)
    # cog                 = gps['i_cog__cdeg']

    return gps # ?
