#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Useful operations related to the GUI

import json
from ttkthemes import ThemedTk
import os
from fnmatch import fnmatch
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess
import multiprocessing
import time
import zmq

from PyQt5.QtWidgets import QMessageBox



def validate_value(val_str, ptype):
    """
    Check whether val_str can be interpreted as ptype (int, float, bool).

    Parameters:
        val_str (str): String representing a value
        ptype (str): String representing the type of the value in val_str

    Returns:
        (boolean): True if val_str can be interpred as a value of type ptype, False otherwise
    
    """
    if ptype == "int":
        try:
            f = float(val_str)
            if not f.is_integer():
                return False
        except ValueError:
            return False
    elif ptype == "float":
        try:
            float(val_str)
        except ValueError:
            return False
    elif ptype == "bool":
        if val_str.lower() not in ("true", "false"):
            return False
    # fallback: no strict check
    return True


def parse_value(val_str, ptype):
    """
    Convert val_str to the correct Python type

    Parameters:
        val_str (str): String representing a value
        ptype (str): String representing the type of the value in val_str

    Returns:
        (variable type): Value of type ptype. Returns a string if the type is not int, float of bool.
    """
    if ptype == "int":
        return int(float(val_str))
    elif ptype == "float":
        return float(val_str)
    elif ptype == "bool":
        return (val_str.lower() == "true")
    return val_str

# def value_settin_handeling(val_str, ptype, error_message):

#     if (validate_value(val_str,ptype)):
#         return parse_value(val_str, ptype)
#     else:
#         QMessageBox.critical("Error", error_message)







def get_window_id(title):
    """
    Get the system id of an external window given its title.

    Parameters:
        title (str): Title of the external window.

    Returns:
         (str): String with the id associated to the window title. Returns 'None' if the window is not found.
    """

    result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').splitlines()
    for line in lines:
        if title in line:
            return line.split()[0]
    return None


def close_window(title):
    """
    Close an external window.

    Parameters:
        title (str): Title of the external window.
    """

    window_id = get_window_id(title)
    if(not window_id):
        return
    
    command = f'wmctrl -ic {window_id}'
    os.system(command)


def send_window_below(title):
    """
    Send an extenal window to be below the other windows.

    Parameters:
        title (str): Title of the external window.
    """

    window_id = get_window_id(title)
    command = f'wmctrl -i -r {window_id} -b remove,above'
    os.system(command)
    command = f'wmctrl -i -r {window_id} -b add,below'
    os.system(command)
    

def send_window_above(title):
    """
    Send an extenal window to be above the other windows.

    Parameters:
        title (str): Title of the external window.
    """

    window_id = get_window_id(title)
    command = f'wmctrl -i -r {window_id} -b remove,below'
    os.system(command)
    command = f'wmctrl -i -r {window_id} -b add,above'
    os.system(command)
