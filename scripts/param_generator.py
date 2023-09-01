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

# Environmental params
data["ENV_PRES_SEA"] ={
    "description":  "Sea level standard atmospheric pressure [hPa]",
    "value":        1013.25,
    "default":      1013.25,
    "type":         "float",
    "unit":         "[hectopascal]"}
data["ENV_GRAVITY"] = {
    "description":   "Earth-surface gravitational acceleration [m/(s*s)]",
    "value":         9.81,
    "default":       9.81,
    "type":          "float",
    "unit":          "[meters]/([second]*[second])"}
data["ENV_MOL_MAS"] = {
    "description":   "Molar mass of dry air [kg/mol]",
    "value":         0.02896968,
    "default":       0.02896968,
    "type":          "float",
    "unit":          "[kilograms]/[mol]"}
data["ENV_TMP_SES"] = {
    "description":   "Sea level standard temperature [K]",
    "value":         288.16,
    "default":       288.16,
    "type":          "float",
    "unit":          "[Kelvin]"}
data["ENV_GAS_CTE"] = {
    "description":   "Universal gas constant [J/(mol*K)]",
    "value":         8.314462618,
    "default":       8.314462618,
    "type":          "float",
    "unit":          "[Joules]/([mol][Kelvin])"}

# Dynamics params
data["DYN_MASS"] = {
    "description":   "Total mass of the vehicle [kg]",
    "value":         2.0,
    "default":       2.0,
    "type":          "float",
    "unit":          "[kilograms]"}
data["DYN_DRAG_V"] = {
    "description":   "Drag coefficiet for linear motion [N*s/m]",
    "value":         0.2,
    "default":       0.2,
    "type":          "float",
    "unit":          "[Newtons]*[seconds]/[meters]"}
data["DYN_DRAG_W"] = {
    "description":   "Drag coefficiet for angular motion [N*s/rad]",
    "value":         0.02,
    "default":       0.02,
    "type":          "float",
    "unit":          "[Newtons]*[seconds]/[radians]"}
data["DYN_J_XX"] = {
    "description":   "Moment of inertion around the x axis [kg*m*m]",
    "value":         0.07625,
    "default":       0.07625,
    "type":          "float",
    "unit":          "[kilogram]*[meter]*[meter]"}
data["DYN_J_YY"] = {
    "description":   "Moment of inertion around the y axis [kg*m*m]",
    "value":         0.077812,
    "default":       0.077812,
    "type":          "float",
    "unit":          "[kilogram]*[meter]*[meter]"}
data["DYN_J_ZZ"] = {
    "description":   "Moment of inertion around the z axis [kg*m*m]",
    "value":         0.1060739,
    "default":       0.1060739,
    "type":          "float",
    "unit":          "[kilogram]*[meter]*[meter]"}
data["DYN_WIND_E"] = {
    "description":   "Constant air speed in the East direction [m/s]",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[meter]/[secong]"}
data["DYN_WIND_N"] = {
    "description":   "Constant air speed in the North direction [m/s]",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[meter]/[secong]"}
data["DYN_WIND_U"] = {
    "description":   "Constant avertical air speed pointing up [m/s]",
    "value":         0.0,
    "default":       0.0,
    "type":          "float",
    "unit":          "[meter]/[secong]"}






save_parameters(data)
# pressure_sea = 1013.25 # Sea level standard atmospheric pressure [hPa]
# g = 9.80665 # Earth-surface gravitational acceleration [m/ss]
# M = 0.02896968 # Molar mass of dry air [kg/mol]
# T0 = 288.16 # Sea level standard temperature [K]
# R0 = 8.314462618 # Universal gas constant [J/(mol*K)]
# C_bar = (T0*R0)/(g*M)


