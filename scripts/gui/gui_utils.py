#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Useful operations related to the GUI

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
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

import gui.vtk_vehicle as VTK
import gui.poly_estimator as PEST
import sim4cd.polynomial as POLY


def move_window_to_frame(window_id, top_left, width, height, shift=0):
    """
    Move an external window to a given position on the screen.

    Parameters:
        window_id (str): String with the external window id to be positioned.
        top_left (tuple): Tuple (x, y) with the top left corner of the desired position for the window
        width (int): Desired width of the window
        height (int): Desired height of the window
        shift (int): Extra shift for the y position of the top of window
    """

    x, y = top_left
    height = height-38
    command = f'wmctrl -i -r {window_id} -e 0,{x},{round(y+shift)},{width},{height}'
    os.system(command)
    command = f'wmctrl -i -r {window_id} -b add,above'
    os.system(command)


def get_frame_corners(frame):
    """
    Get the screen pixels equivalent to the corners of a given tk grame.

    Parameters:
        frame (tk.Frame): Frame whose corners will be evaluated.

    Returns:
        top_left (tuple): Pixel (x,y) of the top left corner.
        top_right (tuple): Pixel (x,y) of the top right corner.
        bottom_left (tuple): Pixel (x,y) of the bottom left corner.
        bottom_right (tuple): Pixel (x,y) of the bottom right corner.
    """

    # Get frame position relative to the root window
    frame_x = frame.winfo_rootx()
    frame_y = frame.winfo_rooty()
    
    # Get frame size
    frame_width = frame.winfo_width()
    frame_height = frame.winfo_height()
    
    # Corners of the frame
    top_left = (frame_x, frame_y)
    top_right = (frame_x + frame_width, frame_y)
    bottom_left = (frame_x, frame_y + frame_height)
    bottom_right = (frame_x + frame_width, frame_y + frame_height)
    
    return top_left, top_right, bottom_left, bottom_right


def position_external_window(window_title, base_frame, attempts=20, delay=0.2, shift=0):
    """
    Position an external window on top of a defined frame.

    Parameters:
        window_title (str): Title of the window to be repositioned.
        base_frame (tk.Frame): Framw in which the window will be placed on top of.
        attempts (int): Number of attempts to finde the desired window.
        delay (float): Time wo wait between two attempts.
        shift (int): Extra shift to be apploed to the top of the window.
    """

    corners = get_frame_corners(base_frame)
    top_left, _, _, _ = corners
    width = base_frame.winfo_width()
    height = base_frame.winfo_height()

    for attempt in range(attempts):
        window_id = get_window_id(window_title)
        if window_id:
            move_window_to_frame(window_id, top_left, width, height, shift)
            break
        else:
            #print("Window not found")
            time.sleep(delay)


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
