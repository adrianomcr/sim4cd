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
    "description":  "Flag to enable the publishing of sim data in ROS topics.",
    "value":        True,
    "default":      True,
    "type":         "bool",
    "unit":         "[]"}
data["SIM_ROS_HZ"] ={
    "description":  "Frequency of publication of sim data in ROS topics.",
    "value":        20,
    "default":      20,
    "type":         "int",
    "unit":         "[Hz]"}
data["SIM_SENS_HZ"] ={
    "description":  "Frequency of publication of sensor data through MAVLINK. Includes IMU, magnetometer and barometer.",
    "value":        800,
    "default":      800,
    "type":         "int",
    "unit":         "[Hz]"}
data["SIM_GPS_HZ"] ={
    "description":  "Frequency of publication of GPS data through MAVLINK.",
    "value":        50,
    "default":      50,
    "type":         "int",
    "unit":         "[Hz]"}
data["SIM_GT_EN"] ={
    "description":  "Flag to enable the publishing ground truth data trough MAVLINK.",
    "value":        True,
    "default":      True,
    "type":         "bool",
    "unit":         "[]"}
data["SIM_GT_HZ"] ={
    "description":  "Frequency of publication of ground truth data through MAVLINK.",
    "value":        50,
    "default":      50,
    "type":         "int",
    "unit":         "[Hz]"}
data["SIM_PRINT_EN"] ={
    "description":  "Flag to enable the printing of sim data on the terminal.",
    "value":        True,
    "default":      True,
    "type":         "bool",
    "unit":         "[]"}
data["SIM_PRINT_HZ"] ={
    "description":  "Frequency of printing of sim data on terminal.",
    "value":        10,
    "default":      10,
    "type":         "int",
    "unit":         "[Hz]"}
data["SIM_INIT_POS_X"] ={
    "description":  "Initial X position of the vehicle in the local frame. The X direction points East. Value in meters.",
    "value":        0.0,
    "default":      0.0,
    "type":         "float",
    "unit":         "[m]"}
data["SIM_INIT_POS_Y"] ={
    "description":  "Initial Y position of the vehicle in the local frame. The Y direction points North. Value in meters.",
    "value":        0.0,
    "default":      0.0,
    "type":         "float",
    "unit":         "[m]"}
data["SIM_INIT_YAW"] ={
    "description":  "Initial yaw angle of the vehicle in the local frame. Angle is measured in radians from the X axes that points East.",
    "value":        0.0,
    "default":      0.0,
    "type":         "float",
    "unit":         "[degrees]"}



# Environmental params
data["ENV_PRES_SEA"] ={
    "description":  "Sea level standard atmospheric pressure in hectopascal.",
    "value":        1013.25,
    "default":      1013.25,
    "type":         "float",
    "unit":         "[hPa]"}
data["ENV_GRAVITY"] = {
    "description":   "Earth-surface gravitational acceleration in meters per second square.",
    "value":         9.80665,
    "default":       9.80665,
    "type":          "float",
    "unit":          "[m/(s*s)]"}
data["ENV_MOL_MASS"] = {
    "description":   "Molar mass of dry air in kilograms per mol.",
    "value":         0.02896968,
    "default":       0.02896968,
    "type":          "float",
    "unit":          "[kg/mol]"}
data["ENV_TMP_SEA"] = {
    "description":   "Sea level standard temperature in Kelvin degrees.",
    "value":         288.16,
    "default":       288.16,
    "type":          "float",
    "unit":          "[K]"}
data["ENV_GAS_CTE"] = {
    "description":   "Universal gas constant in Joules per mol Kelvin.",
    "value":         8.314462618,
    "default":       8.314462618,
    "type":          "float",
    "unit":          "[J/(mol*K)]"}

# Dynamics params
data["DYN_MASS"] = {
    "description":   "Total mass of the vehicle in kilograms.",
    "value":         2.0,
    "default":       2.0,
    "type":          "float",
    "unit":          "[kg]"}
data["DYN_DRAG_V"] = {
    "description":   "Drag coefficient for linear motion in Newtons second per meter.",
    "value":         0.2,
    "default":       0.2,
    "type":          "float",
    "unit":          "[N*s/m]"}
data["DYN_DRAG_W"] = {
    "description":   "Drag coefficient for angular motion Newtons seconds per radian.",
    "value":         0.02,
    "default":       0.02,
    "type":          "float",
    "unit":          "[N*s/rad]"}
data["DYN_J_XX"] = {
    "description":   "Moment of inertia around the x axis in kilograms meter square.",
    "value":         0.07625,
    "default":       0.07625,
    "type":          "float",
    "unit":          "[kg*m*m]"}
data["DYN_J_YY"] = {
    "description":   "Moment of inertia around the y axis in kilograms meter square.",
    "value":         0.077812,
    "default":       0.077812,
    "type":          "float",
    "unit":          "[kg*m*m]"}
data["DYN_J_ZZ"] = {
    "description":   "Moment of inertia around the z axis in kilograms meter square.",
    "value":         0.1060739,
    "default":       0.1060739,
    "type":          "float",
    "unit":          "[kg*m*m]"}
data["DYN_WIND_E"] = {
    "description":   "Constant air speed in the East direction in meters per second.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m/s]"}
data["DYN_WIND_N"] = {
    "description":   "Constant air speed in the North direction in meters per second.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m/s]"}
data["DYN_WIND_U"] = {
    "description":   "Constant vertical air speed pointing up in meters per second.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m/s]"}


# Vehicle geometry
data["VEH_ACT_NUM"] = {
    "description":   "Number of actuator the vehicle has. Maximum value is 8.",
    "value":         4,
    "default":       4,
    "type":          "int",
    "unit":          "[]"}

# TODO: Define one value for each actuator
data["VEH_J_ROTOR"] = {
    "description":   "Moment of inertia of the spinning part of a single actuator in kilograms meter square.",
    "value":         0.001,
    "default":       0.001,
    "type":          "float",
    "unit":          "[kg*m*m]"}

data[f"VEH_ACT0_SPIN"] = {
    "description":   "Direction of rotation of actuator 0.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT0_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT0_DIR",
    "value":         1,
    "default":       1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT1_SPIN"] = {
    "description":   "Direction of rotation of actuator 1.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT1_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT1_DIR",
    "value":         1,
    "default":       1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT2_SPIN"] = {
    "description":   "Direction of rotation of actuator 2.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT2_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT2_DIR",
    "value":         -1,
    "default":       -1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT3_SPIN"] = {
    "description":   "Direction of rotation of actuator 3.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT3_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT3_DIR",
    "value":         -1,
    "default":       -1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT4_SPIN"] = {
    "description":   "Direction of rotation of actuator 4.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT4_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT4_DIR",
    "value":         1,
    "default":       1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT5_SPIN"] = {
    "description":   "Direction of rotation of actuator 5.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT5_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT5_DIR",
    "value":         1,
    "default":       1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT6_SPIN"] = {
    "description":   "Direction of rotation of actuator 6.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT6_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT6_DIR",
    "value":         1,
    "default":       1,
    "type":          "int",
    "unit":          "[m]"}
data[f"VEH_ACT7_SPIN"] = {
    "description":   "Direction of rotation of actuator 7.\n (1): Rotates positively (counter-clockwise) around the vector VEH_ACT7_DIR\n(-1): Rotates negatively (clockwise) around the vector VEH_ACT7_DIR",
    "value":         1,
    "default":       1,
    "type":          "int",
    "unit":          "[m]"}

data["VEH_ACT0_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 0 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT0_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 0 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT0_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 0 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT1_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 1 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT1_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 1 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT1_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 1 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT2_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 2 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT2_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 2 in the vehicle frame. Value in meters.",
    "value":         0.15,
    "default":       0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT2_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 2 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT3_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 3 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT3_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 3 in the vehicle frame. Value in meters.",
    "value":         -0.15,
    "default":       -0.15,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT3_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 3 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT4_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 4 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT4_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 4 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT4_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 4 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT5_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 5 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT5_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 5 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT5_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 5 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT6_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 6 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT6_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 6 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT6_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 6 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
#
data["VEH_ACT7_POS_X"] = {
    "description":   "X component (forward) of the position of actuator 7 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT7_POS_Y"] = {
    "description":   "Y component (right) of the position of actuator 7 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}
data["VEH_ACT7_POS_Z"] = {
    "description":   "Z component (up) of the position of actuator 7 in the vehicle frame. Value in meters.",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[m]"}

for n in range(8):
    data[f"VEH_ACT{n}_DIR_X"] = {
        "description":   f"X component (forward) of the direction of action of actuator {n} in the vehicle frame. Value in meters. Should form a unit vector with values VEH_ACT{n}_DIR_Y and VEH_ACT{n}_DIR_Z.",
        "value":         0.0,
        "default":       0.0,
        "type":          "float",
        "unit":          "[m]"}
    data[f"VEH_ACT{n}_DIR_Y"] = {
        "description":   f"Y component (right) of the direction of action of actuator {n} in the vehicle frame. Value in meters. Should form a unit vector with values VEH_ACT{n}_DIR_X and VEH_ACT{n}_DIR_Z.",
        "value":         0.0,
        "default":       0.0,
        "type":          "float",
        "unit":          "[m]"}
    data[f"VEH_ACT{n}_DIR_Z"] = {
        "description":   f"Z component (up) of the direction of action of actuator {n} in the vehicle frame. Value in meters. Should form a unit vector with values VEH_ACT{n}_DIR_X and VEH_ACT{n}_DIR_Y.",
        "value":         1.0,
        "default":       1.0,
        "type":          "float",
        "unit":          "[m]"}

data["VEH_BAT_VOLTAGE"] = {
    "description":   "Voltage of the vehicle battery in Volts.",
    "value":         24.3,
    "default":       24.3,
    "type":          "float",
    "unit":          "[V]"}


#Actuators
for n in range(8):
    data[f"ACT{n}_TIME_CTE"] = {
        "description":   f"Time constant, in seconds, of the first order dynamics of actuator {n}.",
        "value":         0.02,
        "default":       0.02,
        "type":          "float",
        "unit":          "[s]"}
    data[f"ACT{n}_VOLT2SPEED_1"] = {
        "description":   f"Constant of the linear part of the map from the applied voltage to the rotation speed of actuator {n} in radians per second per Volt.",
        "value":         33.0,
        "default":       33.0,
        "type":          "float",
        "unit":          "[rad/(s*V)]"}
    data[f"ACT{n}_SPEED2THRUST_1"] = {
        "description":   f"Constant of the linear part of the map from the rotation speed to the generated thrust of actuator {n} in Newton seconds per radian.",
        "value":         0.015,
        "default":       0.015,
        "type":          "float",
        "unit":          "[N*s/rad]"}
    data[f"ACT{n}_SPEED2TORQUE_1"] = {
        "description":   f"Constant of the linear part of the map from the rotation speed to the generated torque of actuator {n} in Newton meter seconds per radian. The signal of the torque is defined by VEH_ACT{n}_SPIN.",
        "value":         0.0009,
        "default":       0.0009,
        "type":          "float",
        "unit":          "[N*m*s/rad]"}
    data[f"ACT{n}_TORQUE2AMPS_1"] = {
        "description":   f"Constant of the linear part of the map from the generated torque to current being consumed by the actuator {n} in Amperes per Newton per meter.",
        "value":         30.0,
        "default":       30.0,
        "type":          "float",
        "unit":          "[A/(N*m)]"}

#Sensors
data["SENS_LAT_ORIGIN"] = {
    "description":   "Latitude coordinate of the origin of the local simulated frame in degrees.",
    "value":         40.448985,
    "default":       40.448985,
    "type":          "float",
    "unit":          "[degrees]"}
data["SENS_LON_ORIGIN"] = {
    "description":   "Longitude coordinate of the origin of the local simulated frame in degrees.",
    "value":         -79.898025,
    "default":       -79.898025,
    "type":          "float",
    "unit":          "[degrees]"}
data["SENS_ALT_ORIGIN"] = {
    "description":   "Altitude above average sea level, in meters, of the origin of the local simulated frame.",
    "value":         372.0,
    "default":       372.0,
    "type":          "float",
    "unit":          "[m]"}
data["SENS_MAG_FIELD_E"] = {
    "description":   "Local magnetic field in the East direction in Gauss.",
    "value":         -0.02559,
    "default":       -0.02559,
    "type":          "float",
    "unit":          "[G]"}
data["SENS_MAG_FIELD_N"] = {
    "description":   "Local magnetic field in the North direction in Gauss.",
    "value":         0.16928,
    "default":       0.16928,
    "type":          "float",
    "unit":          "[G]"}
data["SENS_MAG_FIELD_U"] = {
    "description":   "Local magnetic field in the up direction in Gauss.",
    "value":         -0.39550,
    "default":       -0.39550,
    "type":          "float",
    "unit":          "[G]"}

data["SENS_ACC_NOISE_STD"] = {
    "description":   "Standard deviation of the accelerometer noise in meters per second square.",
    "value":         0.4,
    "default":       0.4,
    "type":          "float",
    "unit":          "[m/(s*s)]"}
data["SENS_GYRO_NOISE_STD"] = {
    "description":   "Standard deviation of the gyro noise in radians per second.",
    "value":         0.1,
    "default":       0.1,
    "type":          "float",
    "unit":          "[rad/s]"}
data["SENS_MAG_NOISE_STD"] = {
    "description":   "Standard deviation of the magnetometer noise in Gauss.",
    "value":         0.15,
    "default":       0.15,
    "type":          "float",
    "unit":          "[G]"}
data["SENS_BAR_NOISE_STD"] = {
    "description":   "Standard deviation of the barometer noise in hectopascal.",
    "value":         0.005,
    "default":       0.005,
    "type":          "float",
    "unit":          "[hPa]"}
data["SENS_GPS_STD_XY"] = {
    "description":   "Standard deviation on the horizontal position given by the GPS in meters.",
    "value":         0.05,
    "default":       0.05,
    "type":          "float",
    "unit":          "[m]"}
data["SENS_GPS_STD_Z"] = {
    "description":   "Standard deviation on the vertical position given by the GPS in meters.",
    "value":         0.1,
    "default":       0.1,
    "type":          "float",
    "unit":          "[m]"}

# Save parameters to default file
save_parameters(data)



