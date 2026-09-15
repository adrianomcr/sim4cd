#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Useful operations related to the GUI

import json
import os
import tempfile
from fnmatch import fnmatch
import numpy as np
import subprocess
import multiprocessing
import time
import zmq

from PyQt5.QtWidgets import QMessageBox, QFileDialog

RUNTIME_CONFIG_FILENAME = "sim4cd_gui_runtime.json"


def notify_config_state_changed(shared_data):
    """Notify the main window that the config path or dirty flag changed.

    Tabs and these helpers only share the ``shared_data`` dict; they have no
    ``MainWindow`` reference. The window registers ``update_window_title`` as
    ``shared_data['on_config_state_changed']`` so the title can show the
    filename and a '*' while there are unsaved edits.

    ``callable()`` skips the hook when a tab is run standalone without a
    main window (no callback is registered).
    """
    callback = shared_data.get("on_config_state_changed")
    if callable(callback):
        callback()


def mark_config_dirty(shared_data):
    """Mark GUI parameters as changed since the last save."""
    if shared_data.get("config_dirty"):
        return
    shared_data["config_dirty"] = True
    notify_config_state_changed(shared_data)


def clear_config_dirty(shared_data):
    """Clear the unsaved-parameter flag (after load or save)."""
    if not shared_data.get("config_dirty"):
        return
    shared_data["config_dirty"] = False
    notify_config_state_changed(shared_data)


def write_config_to_path(shared_data, path):
    """Write the in-memory GUI parameter list to a JSON file."""
    config = shared_data.get("config")
    if not config:
        raise ValueError("No parameters to save.")
    with open(path, "w") as json_file:
        json.dump(config, json_file, indent=4)


def write_runtime_config(shared_data):
    """Dump current GUI parameters to a temp file used to start the simulator."""
    path = os.path.join(tempfile.gettempdir(), RUNTIME_CONFIG_FILENAME)
    write_config_to_path(shared_data, path)
    return path


def save_shared_config(parent, shared_data, path=None, show_success=True, force_dialog=False):
    """
    Save in-memory parameters to disk.

    If path is omitted, uses config_file_path, or prompts with Save As.
    Returns True on success, False if cancelled or failed.
    """
    dest = None if force_dialog else (path or shared_data.get("config_file_path"))
    if not dest:
        options = QFileDialog.Options()
        start_path = shared_data.get("config_file_path") or ""
        dest, _ = QFileDialog.getSaveFileName(
            parent, "Save JSON File", start_path, "JSON Files (*.json);;All Files (*)", options=options
        )
        if not dest:
            return False

    try:
        write_config_to_path(shared_data, dest)
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to save JSON file:\n{str(e)}")
        return False

    shared_data["config_file_path"] = dest
    shared_data["config_dirty"] = False
    notify_config_state_changed(shared_data)

    if show_success:
        QMessageBox.information(parent, "Success", f"Successfully saved to:\n{dest}")
    return True


def prompt_save_if_dirty(parent, shared_data, context="continue"):
    """
    If parameters changed since the last save, ask the user whether to persist them.

    context:
        'start'  - starting the simulator
        'open'   - opening another parameter file
        'close'  - closing the GUI
        'continue' - generic

    Returns True to proceed, False if the user cancelled.
    """
    if not shared_data.get("config_dirty"):
        return True

    current_path = shared_data.get("config_file_path") or "untitled"
    if context == "start":
        text = "Parameters have changed since the last save."
        info = (
            "Save them to the parameter file?\n\n"
            "The simulator will use the current GUI values either way.\n"
            f"File: {current_path}"
        )
    elif context == "open":
        text = "Parameters have changed since the last save."
        info = f"Save them before opening another file?\n\nFile: {current_path}"
    elif context == "close":
        text = "Parameters have changed since the last save."
        info = f"Save them before exiting?\n\nFile: {current_path}"
    else:
        text = "Parameters have changed since the last save."
        info = f"Save them to:\n{current_path}?"

    msg = QMessageBox(parent)
    msg.setWindowTitle("Unsaved parameters")
    msg.setText(text)
    msg.setInformativeText(info)
    msg.setIcon(QMessageBox.Warning)
    msg.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    msg.setDefaultButton(QMessageBox.Save)
    discard_btn = msg.button(QMessageBox.Discard)
    if discard_btn is not None:
        discard_btn.setText("Don't Save")

    reply = msg.exec_()
    if reply == QMessageBox.Save:
        return save_shared_config(parent, shared_data, show_success=False)
    if reply == QMessageBox.Discard:
        return True
    return False



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
