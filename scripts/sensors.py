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
from math import pi, sqrt, exp, sin
import math_utils as MU



lat0 = 40.448985
lon0 = -79.898025

def get_acc(q,f,m):

    acc0 = MU.quat_apply_rot(MU.quat_conj(q),f/m) + np.random.normal(loc=0.0, scale=0.05, size=3)

    # acc = np.array([acc0[0],acc0[1],acc0[2]])
    acc = np.array([acc0[0],-acc0[1],-acc0[2]])

    return acc # m/s^2


def get_gyro(w):

    gyro0 = w + np.random.normal(loc=0.0, scale=0.02, size=3)
    # gyro = np.array([gyro0[0],gyro0[1],gyro0[2]])
    gyro = np.array([gyro0[0],-gyro0[1],-gyro0[2]])

    return gyro # rad/s


def get_mag(q,tau):


    mag0 = np.array([0.16928, 0.02559, -0.39550]) + np.random.normal(loc=0.0, scale=0.01, size=3) # Pittsburgh
    # mag0 = np.array([0.22923, 0.02772, 0.11998]) + np.random.normal(loc=0.0, scale=0.01, size=3) # lat, lon = [0, 0]

    #http://www.geomag.bgs.ac.uk/data_service/models_compass/wmm_calc.html
    #apply the rotation here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    mag0 =  MU.quat_apply_rot(MU.quat_conj(q),mag0)


    # mag = np.array([mag0[0],mag0[1],mag0[2]])
    mag = np.array([mag0[0],-mag0[1],-mag0[2]])

    return mag # Gauss


def get_baro(z):

    # bar = 1013.25 - 100*(z/1000) + np.random.normal(loc=0.0, scale=0.001, size=1)
    bar = 1013.25 * exp(-(z+372) / 8400) + np.random.normal(loc=0.0, scale=0.001, size=1)
    # ~ sea level plus altitude

    # Inverse
    # z =  -8400*ln(bar/1013.25)-372


    return bar #hPa


from random import random
def crandom():
    return random()-0.5

def get_gps(p,vw):


    gps = {}

    R = 6378100
    meters2ged_lat =  180 / ( R *  3.14159265359)
    r = R*sqrt(1 - sin(lat0*pi/180)**2)
    meters2ged_lon =  180 / ( r *  3.14159265359)


    gps['i_lat__degE7']               = round((   lat0+p[0]*meters2ged_lat   +crandom()*5e-8     )*1e7)
    gps['i_lon__degE7']               = round((   lon0-p[1]*meters2ged_lon     +crandom()*5e-8     )*1e7)
    gps['i_alt__mm']                  = round((   372+ p[2]         +crandom()*0.05     )*1000)
    gps['i_eph__cm']                  = round((   0           + random()*0.001    )*100)
    gps['i_epv__cm']                  = round((   0           + random()*0.001    )*100)
    gps['i_vel__cm/s']                = round((   0*sqrt(vw[0]**2+vw[1]**2)           + random()*0.001    )*100)
    # gps['i_vn__cm/s']                 = round((   vw[0]           + random()*0.001    )*100)
    # gps['i_ve__cm/s']                 = round((   -vw[1]           + random()*0.001    )*100)
    # gps['i_vd__cm/s']                 = round((   vw[2]           + random()*0.001    )*100)
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





def get_ground_truth(p,vw,q,omega):


    gt = {}

    R = 6378100
    meters2ged_lat =  180 / ( R *  3.14159265359)
    r = R*sqrt(1 - sin(lat0*pi/180)**2)
    meters2ged_lon =  180 / ( r *  3.14159265359)


    # attitude_quaternion = q # Vehicle attitude expressed as normalized quaternion in w, x, y, z order (with 1 0 0 0 being the null-rotation) (type:float)
    # rollspeed           = w[0]       # Body frame roll / phi angular speed [rad/s] (type:float)
    # pitchspeed          = w[1]      # Body frame pitch / theta angular speed [rad/s] (type:float)
    # yawspeed            = w[2]        # Body frame yaw / psi angular speed [rad/s] (type:float)
    # lat                 = drone['i_lat__degE7']             # Latitude [degE7] (type:int32_t)
    # lon                 = drone['i_lon__degE7']             # Longitude [degE7] (type:int32_t)
    # alt                 = drone['i_alt__mm']                # Altitude [mm] (type:int32_t)
    # vx                  = vw[0]*100               # Ground X Speed (Latitude) [cm/s] (type:int16_t)
    # vy                  = -vw[1]*100               # Ground Y Speed (Longitude) [cm/s] (type:int16_t)
    # vz                  = vw[2]*100               # Ground Z Speed (Altitude) [cm/s] (type:int16_t)
    # ind_airspeed        = MU.norm(vw)*100     # Indicated airspeed [cm/s] (type:uint16_t)
    # true_airspeed       = drone['i_true_airspeed__cm/s']    # True airspeed [cm/s] (type:uint16_t)
    # xacc                = 0               # X acceleration [mG] (type:int16_t)
    # yacc                = 0               # Y acceleration [mG] (type:int16_t)
    # zacc                = 0               # Z acceleration [mG] (type:int16_t)

    q_rot = MU.quat_mult(MU.quat_mult(np.array([0,1,0,0]),q),np.array([0,1,0,0]))
    gt['attitude_quaternion'] = q_rot.tolist()
    gt['rollspeed'] = omega[0]
    gt['pitchspeed'] = -omega[1]
    gt['yawspeed'] = -omega[2]
    gt['i_lat__degE7'] = (lat0+p[0]*meters2ged_lat)*1e7
    gt['i_lon__degE7'] = (lon0-p[1]*meters2ged_lon)*1e7
    gt['i_alt__mm'] = 372+ p[2]
    gt['vx'] = vw[0]*100
    gt['vy'] = -vw[1]*100
    gt['vz'] = vw[2]*100
    gt['ind_airspeed'] = MU.norm(vw)*100
    gt['true_airspeed'] = MU.norm(vw)*100
    gt['xacc'] = 0
    gt['yacc'] = 0
    gt['zacc'] = 0




    return gt # ?
