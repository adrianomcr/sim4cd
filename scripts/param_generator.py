#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import json
import os

def set_parameter(key, value):
    parameters = load_parameters()
    parameters[key] = value
    save_parameters(parameters)

def get_parameter(key):
    parameters = load_parameters()
    return parameters.get(key)

def load_parameters():
    try:
        with open(PARAM_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_parameters(parameters):
    with open(PARAM_FILE, "w") as file:
        json.dump(parameters, file, indent=4)

PARAM_FILE = os.path.expanduser('~')+"/simulation_ws/src/px4sim/config/sim_params.json"


data = {}

# Simulation parameters
data["SIM_ROS_EN"] ={
    "description":   "Flag to enable the publishing of sim data in ROS topics.",
    "value":         True,
    "default":       True,
    "options":       [True, False],
    "type":          "bool",
    "unit":          "[ ]"}
data["SIM_ROS_HZ"] ={
    "description":   "Frequency of publication of sim data in ROS topics.",
    "value":         20,
    "default":       20,
    "options":       [],
    "type":          "int",
    "unit":          "[Hz]"}
data["SIM_SENS_HZ"] ={
    "description":   "Frequency of publication of sensor data through MAVLINK. Includes IMU, magnetometer and barometer.",
    "value":         800,
    "default":       800,
    "options":       [],
    "type":          "int",
    "unit":          "[Hz]"}
data["SIM_GPS_HZ"] ={
    "description":   "Frequency of publication of GPS data through MAVLINK.",
    "value":         50,
    "default":       50,
    "options":       [],
    "type":          "int",
    "unit":          "[Hz]"}
data["SIM_GT_EN"] ={
    "description":   "Flag to enable the publishing ground truth data trough MAVLINK.",
    "value":         True,
    "default":       True,
    "options":       [True, False],
    "type":          "bool",
    "unit":          "[ ]"}
data["SIM_GT_HZ"] ={
    "description":   "Frequency of publication of ground truth data through MAVLINK.",
    "value":         50,
    "default":       50,
    "options":       [],
    "type":          "int",
    "unit":          "[Hz]"}
data["SIM_PRINT_EN"] ={
    "description":   "Flag to enable the printing of sim data on the terminal.",
    "value":         False,
    "default":       False,
    "options":       [True, False],
    "type":          "bool",
    "unit":          "[ ]"}
data["SIM_PRINT_HZ"] ={
    "description":   "Frequency of printing of sim data on terminal.",
    "value":         10,
    "default":       10,
    "options":       [],
    "type":          "int",
    "unit":          "[Hz]"}
data["SIM_INIT_POS_X"] ={
    "description":   "Initial X position of the vehicle in the local frame. The X direction points East. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["SIM_INIT_POS_Y"] ={
    "description":   "Initial Y position of the vehicle in the local frame. The Y direction points North. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["SIM_INIT_YAW"] ={
    "description":   "Initial yaw angle of the vehicle in the local frame. Angle is measured in radians from the X axes that points East.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[degrees]"}



# Environmental params
data["ENV_PRES_SEA"] ={
    "description":   "Sea level standard atmospheric pressure in hectopascal.",
    "value":         1013.25,
    "default":       1013.25,
    "options":       [],
    "type":          "float",
    "unit":          "[hPa]"}
data["ENV_GRAVITY"] = {
    "description":   "Earth-surface gravitational acceleration in meters per second square.",
    "value":         9.80665,
    "default":       9.80665,
    "options":       [],
    "type":          "float",
    "unit":          "[m/(s*s)]"}
data["ENV_MOL_MASS"] = {
    "description":   "Molar mass of dry air in kilograms per mol.",
    "value":         0.02896968,
    "default":       0.02896968,
    "options":       [],
    "type":          "float",
    "unit":          "[kg/mol]"}
data["ENV_TMP_SEA"] = {
    "description":   "Sea level standard temperature in Kelvin degrees.",
    "value":         288.16,
    "default":       288.16,
    "options":       [],
    "type":          "float",
    "unit":          "[K]"}
data["ENV_GAS_CTE"] = {
    "description":   "Universal gas constant in Joules per mol Kelvin.",
    "value":         8.314462618,
    "default":       8.314462618,
    "options":       [],
    "type":          "float",
    "unit":          "[J/(mol*K)]"}

# Dynamics params
data["DYN_MASS"] = {
    "description":   "Total mass of the vehicle in kilograms.",
    "value":         2.0,
    "default":       2.0,
    "options":       [],
    "type":          "float",
    "unit":          "[kg]"}
data["DYN_DRAG_V"] = {
    "description":   "Drag coefficient for linear motion in Newtons second per meter.",
    "value":         0.2,
    "default":       0.2,
    "options":       [],
    "type":          "float",
    "unit":          "[N*s/m]"}
data["DYN_DRAG_W"] = {
    "description":   "Drag coefficient for angular motion Newtons seconds per radian.",
    "value":         0.02,
    "default":       0.02,
    "options":       [],
    "type":          "float",
    "unit":          "[N*s/rad]"}
data["DYN_MOI_XX"] = {
    "description":   "Moment of inertia around the x axis in kilograms meter square.",
    "value":         0.07625,
    "default":       0.07625,
    "options":       [],
    "type":          "float",
    "unit":          "[kg*m*m]"}
data["DYN_MOI_YY"] = {
    "description":   "Moment of inertia around the y axis in kilograms meter square.",
    "value":         0.077812,
    "default":       0.077812,
    "options":       [],
    "type":          "float",
    "unit":          "[kg*m*m]"}
data["DYN_MOI_ZZ"] = {
    "description":   "Moment of inertia around the z axis in kilograms meter square.",
    "value":         0.1060739,
    "default":       0.1060739,
    "options":       [],
    "type":          "float",
    "unit":          "[kg*m*m]"}
data["DYN_WIND_E"] = {
    "description":   "Constant air speed in the East direction in meters per second.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m/s]"}
data["DYN_WIND_N"] = {
    "description":   "Constant air speed in the North direction in meters per second.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m/s]"}
data["DYN_WIND_U"] = {
    "description":   "Constant vertical air speed pointing up in meters per second.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m/s]"}


# Vehicle geometry
data["VEH_ACT_NUM"] = {
    "description":   "Number of actuator the vehicle has. Maximum value is 8.",
    "value":         4,
    "default":       4,
    "options":       [1,2,3,4,5,6,7,8],
    "type":          "int",
     "unit":         "[ ]"}

data["VEH_ACT0_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 0 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT0_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 0 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT0_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 0 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT1_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 1 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT1_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 1 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT1_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 1 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT2_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 2 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT2_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 2 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT2_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 2 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT3_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 3 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT3_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 3 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT3_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 3 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT4_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 4 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT4_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 4 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT4_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 4 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT5_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 5 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT5_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 5 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT5_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 5 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT6_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 6 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT6_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 6 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT6_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 6 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT7_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 7 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT7_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 7 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT7_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 7 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}

for n in range(8):
    data[f"VEH_ACT{n}_DIR_X"] = {
        "description":   f"X component (forward) of the direction of action of actuator {n} in the vehicle frame. Value in meters. Should form a unit vector with values VEH_ACT{n}_DIR_Y and VEH_ACT{n}_DIR_Z.",
        "value":         0.0,
        "default":       0.0,
        "options":       [],
        "type":          "float",
        "unit":          "[m]"}
    data[f"VEH_ACT{n}_DIR_Y"] = {
        "description":   f"Y component (right) of the direction of action of actuator {n} in the vehicle frame. Value in meters. Should form a unit vector with values VEH_ACT{n}_DIR_X and VEH_ACT{n}_DIR_Z.",
        "value":         0.0,
        "default":       0.0,
        "options":       [],
        "type":          "float",
        "unit":          "[m]"}
    data[f"VEH_ACT{n}_DIR_Z"] = {
        "description":   f"Z component (up) of the direction of action of actuator {n} in the vehicle frame. Value in meters. Should form a unit vector with values VEH_ACT{n}_DIR_X and VEH_ACT{n}_DIR_Y.",
        "value":         1.0,
        "default":       1.0,
        "options":       [],
        "type":          "float",
        "unit":          "[m]"}


#Actuators
for n in range(8):
    data[f"ACT{n}_TIME_CTE"] = {
        "description":   f"Time constant, in seconds, of the first order dynamics of actuator {n}.",
        "value":         0.02,
        "default":       0.02,
        "options":       [],
        "type":          "float",
        "unit":          "[s]"}
    data[f"ACT{n}_MOI_ROTOR"] = {
        "description":   f"Moment of inertia of the spinning part of e actuator {n} in kilograms meter square.",
        "value":         0.001,
        "default":       0.001,
        "options":       [],
        "type":          "float",
        "unit":          "[kg*m*m]"}
    VOLT2SPEED = [0.0, 33.0, 0.0]
    SPEED2THRUST = [0.0, 0.015, 0.0]
    SPEED2TORQUE = [0.0, 0.0009, 0.0]
    TORQUE2AMPS = [0.0, 30.0, 0.0]
    # TODO: Correct unit for order different than 1
    for i in range(3):
        data[f"ACT{n}_VOLT2SPEED_{i}"] = {
            "description":   f"Polynomial constant for order {i} of the map from the applied voltage to the rotation speed of actuator {n} in radians per second per Volt.",
            "value":         VOLT2SPEED[i],
            "default":       VOLT2SPEED[i],
            "options":       [],
            "type":          "float",
            "unit":          f"[rad/(s*V^{i})]"}
        data[f"ACT{n}_SPEED2THRUST_{i}"] = {
            "description":   f"Polynomial constant for order {i} of the map from the rotation speed to the generated thrust of actuator {n} in Newton seconds per radian.",
            "value":         SPEED2THRUST[i],
            "default":       SPEED2THRUST[i],
            "options":       [],
            "type":          "float",
            "unit":          f"[(N*s^{i})/(rad^{i})]"}
        data[f"ACT{n}_SPEED2TORQUE_{i}"] = {
            "description":   f"Polynomial constant for order {i} of the map from the rotation speed to the generated torque of actuator {n} in Newton meter seconds per radian. The signal of the torque is defined by VEH_ACT{n}_SPIN.",
            "value":         SPEED2TORQUE[i],
            "default":       SPEED2TORQUE[i],
            "options":       [],
            "type":          "float",
            "unit":          f"[(N*m*s^{i})/(rad^{i})]"}
        data[f"ACT{n}_TORQUE2AMPS_{i}"] = {
            "description":   f"Polynomial constant for order {i} of the map from the generated torque to current being consumed by the actuator {n} in Amperes per Newton per meter.",
            "value":         TORQUE2AMPS[i],
            "default":       TORQUE2AMPS[i],
            "options":       [],
            "type":          "float",
            "unit":          f"[A/(N*m)^{i}]"}


data[f"ACT0_SPIN"] = {
    "description":   "Direction of rotation of actuator 0.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT0_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT0_DIR",
    "value":         1,
    "default":       1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT1_SPIN"] = {
    "description":   "Direction of rotation of actuator 1.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT1_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT1_DIR",
    "value":         1,
    "default":       1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT2_SPIN"] = {
    "description":   "Direction of rotation of actuator 2.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT2_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT2_DIR",
    "value":         -1,
    "default":       -1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT3_SPIN"] = {
    "description":   "Direction of rotation of actuator 3.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT3_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT3_DIR",
    "value":         -1,
    "default":       -1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT4_SPIN"] = {
    "description":   "Direction of rotation of actuator 4.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT4_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT4_DIR",
    "value":         1,
    "default":       1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT5_SPIN"] = {
    "description":   "Direction of rotation of actuator 5.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT5_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT5_DIR",
    "value":         1,
    "default":       1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT6_SPIN"] = {
    "description":   "Direction of rotation of actuator 6.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT6_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT6_DIR",
    "value":         1,
    "default":       1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}
data[f"ACT7_SPIN"] = {
    "description":   "Direction of rotation of actuator 7.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT7_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT7_DIR",
    "value":         1,
    "default":       1,
    "options":       [-1, 1],
    "type":          "int",
    "unit":          "[ ]"}



#Sensors
data["SENS_LAT_ORIGIN"] = {
    "description":   "Latitude coordinate of the origin of the local simulated frame in degrees.",
    "value":         40.448985,
    "default":       40.448985,
    "options":       [],
    "type":          "float",
    "unit":          "[degrees]"}
data["SENS_LON_ORIGIN"] = {
    "description":   "Longitude coordinate of the origin of the local simulated frame in degrees.",
    "value":         -79.898025,
    "default":       -79.898025,
    "options":       [],
    "type":          "float",
    "unit":          "[degrees]"}
data["SENS_ALT_ORIGIN"] = {
    "description":   "Altitude above average sea level, in meters, of the origin of the local simulated frame.",
    "value":         372.0,
    "default":       372.0,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["SENS_MAG_FIELD_E"] = {
    "description":   "Local magnetic field in the East direction in Gauss.",
    "value":         -0.03313,
    "default":       -0.03313,
    "options":       [],
    "type":          "float",
    "unit":          "[G]"}
data["SENS_MAG_FIELD_N"] = {
    "description":   "Local magnetic field in the North direction in Gauss.",
    "value":         0.20188,
    "default":       0.20188,
    "options":       [],
    "type":          "float",
    "unit":          "[G]"}
data["SENS_MAG_FIELD_U"] = {
    "description":   "Local magnetic field in the up direction in Gauss.",
    "value":         -0.47534,
    "default":       -0.47534,
    "options":       [],
    "type":          "float",
    "unit":          "[G]"}

####################################
for d in ['X','Y','Z']:
    # Gaussian noise
    data[f"SENS_ACC_STD_{d}"] = {
        "description":   f"Standard deviation of the {d} component of the accelerometer noise in meters per second square.",
        "value":         0.4,
        "default":       0.4,
        "options":       [],
        "type":          "float",
        "unit":          "[m/(s*s)]"}
    data[f"SENS_GYRO_STD_{d}"] = {
        "description":   f"Standard deviation of the {d} component of the gyro noise in radians per second.",
        "value":         0.1,
        "default":       0.1,
        "options":       [],
        "type":          "float",
        "unit":          "[rad/s]"}
    data[f"SENS_MAG_STD_{d}"] = {
        "description":   f"Standard deviation of the {d} component of the magnetometer noise in Gauss.",
        "value":         0.15,
        "default":       0.15,
        "options":       [],
        "type":          "float",
        "unit":          "[G]"}
    # data[f"SENS_GPS_STD_{d}"] = {
    #     "description":   f"Standard deviation on the {d} component of the GPS in meters.",
    #     "value":         0.05,
    #     "default":       0.05,
    #     "options":       [],
    #     "type":          "float",
    #     "unit":          "[m]"}
    # Bias
    data[f"SENS_ACC_BIAS_{d}"] = {
        "description":   f"Constant bias of the {d} component of the accelerometer in meters per second square.",
        "value":         0.0,
        "default":       0.0,
        "options":       [],
        "type":          "float",
        "unit":          "[m/(s*s)]"}
    data[f"SENS_GYRO_BIAS_{d}"] = {
        "description":   f"Constant bias of the {d} component of the gyro in radians per second.",
        "value":         0.0,
        "default":       0.0,
        "options":       [],
        "type":          "float",
        "unit":          "[rad/s]"}
    data[f"SENS_MAG_BIAS_{d}"] = {
        "description":   f"Constant bias of the {d} component of the magnetometer in Gauss.",
        "value":         0.0,
        "default":       0.0,
        "options":       [],
        "type":          "float",
        "unit":          "[G]"}
    # Vibration
    data[f"SENS_ACC_VIB_{d}"] = {
        "description":   f"Vibration coupling index of the {d} component of the accelerometer.\nIt maps the actuators thrust to the vibration measured by the {d} component of the accelerometer.",
        "value":         1.0,
        "default":       1.0,
        "options":       [],
        "type":          "float",
        "unit":          "[ - ]"}
    data[f"SENS_GYRO_VIB_{d}"] = {
        "description":   f"Vibration coupling index of the {d} component of the gyro.\nIt maps the actuators torque to the vibration measured by the {d} component of the gyro.",
        "value":         1.0,
        "default":       1.0,
        "options":       [],
        "type":          "float",
        "unit":          "[ - ]"}
    # Magnetic coupling
    data[f"SENS_MAG_INTF_{d}"] = {
        "description":   f"Interference coupling index of the {d} component of the magnetometer in Gauss per Ampere.\nIt maps the vehicle current to the internally generated magnetic field on the {d} component of the magnetometer.",
        "value":         1.0,
        "default":       1.0,
        "options":       [],
        "type":          "float",
        "unit":          "[G/A]"}
    
####################################

# data["SENS_ACC_NOISE_STD"] = {
#     "description":   "Standard deviation of the accelerometer noise in meters per second square.",
#     "value":         0.4,
#     "default":       0.4,
#     "options":       [],
#     "type":          "float",
#     "unit":          "[m/(s*s)]"}
# data["SENS_GYRO_NOISE_STD"] = {
#     "description":   "Standard deviation of the gyro noise in radians per second.",
#     "value":         0.1,
#     "default":       0.1,
#     "options":       [],
#     "type":          "float",
#     "unit":          "[rad/s]"}
# data["SENS_MAG_NOISE_STD"] = {
#     "description":   "Standard deviation of the magnetometer noise in Gauss.",
#     "value":         0.15,
#     "default":       0.15,
#     "options":       [],
#     "type":          "float",
#     "unit":          "[G]"}
data["SENS_BAR_STD"] = {
    "description":   "Standard deviation of the barometer noise in hectopascal.",
    "value":         0.005,
    "default":       0.005,
    "options":       [],
    "type":          "float",
    "unit":          "[hPa]"}
data["SENS_BAR_BIAS"] = {
    "description":   "Constant bias of the barometer in hectopascal.",
    "value":         0.0,
    "default":       0.0,
    "options":       [],
    "type":          "float",
    "unit":          "[hPa]"}
data["SENS_GPS_STD_XY"] = {
    "description":   "Standard deviation on the horizontal position given by the GPS in meters.",
    "value":         0.05,
    "default":       0.05,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}
data["SENS_GPS_STD_Z"] = {
    "description":   "Standard deviation on the vertical position given by the GPS in meters.",
    "value":         0.1,
    "default":       0.1,
    "options":       [],
    "type":          "float",
    "unit":          "[m]"}


# Battery
data["BAT_FULL_CHARGE"] = {
    "description":   "Battery charge in Milliampere hour at full charge.",
    "value":         16000,
    "default":       16000,
    "options":       [],
    "type":          "int",
    "unit":          "[mAh]"}

data["BAT_INIT_CHARGE"] = {
    "description":   "Battery initial charge percentage.",
    "value":         100,
    "default":       100,
    "options":       [(i+1)*10 for i in range(10)],
    "type":          "int",
    "unit":          "[%]"}

data["BAT_N_CELLS"] = {
    "description":   "Battery number of cells in series.",
    "value":         6,
    "default":       6,
    "options":       [ ],
    "type":          "int",
    "unit":          "[ ]"}

data["BAT_INTERNAL_RES"] = {
    "description":   "Internal resistance of the battery in Ohms.",
    "value":         0.05,
    "default":       0.05,
    "options":       [ ],
    "type":          "float",
    "unit":          "[Ω]"}

data["BAT_DISCHARGE_RATE"] = {
    "description":   "Battery discharge rate.",
    "value":         30,
    "default":       30,
    "options":       [(i+1)*10 for i in range(10)],
    "type":          "int",
    "unit":          "['C']"}


data["PWR_IDLE_CURRENT"] = {
    "description":   "Current that is constantly drowning from the battery even if no actuator is on.",
    "value":         1,
    "default":       1,
    "options":       [ ],
    "type":          "float",
    "unit":          "[A]"}

data["PWR_EFF"] = {
    "description":   "Efficiency of the vehicle electrical power conversion board.",
    "value":         90,
    "default":       90,
    "options":       [ ],
    "type":          "int",
    "unit":          "[%]"}



sorted_items = [(key, value) for key, value in sorted(data.items())]
sorted_data = dict(sorted_items)

# Save parameters to default file
save_parameters(sorted_data)



