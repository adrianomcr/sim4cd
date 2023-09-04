#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Parameter server for the simulator

import json
import os

class parameter_server(object):
    """
    Parameter server class.
    """

    def __init__(self, json_path_):
        """
        Constructor for the parameter_server class.

        Parameters:
            json_path_ (str): String with the JSON parameter file.
        """

        self.json_path = json_path_
        # Load JSON file with parameters
        self.data = self.load_file()

    def get_parameter(self, key):
        """
        Get all the attributes of a given parameter.

        Parameters:
            key (str): String with the name of the parameter to be read.
        
        Returns:
            p (dict): Dictionary with all of the attributes of the requested parameter.
        """
        try:
            # Try to read the parameter attributes
            p = self.data.get(key)
        except:
            # Throw an error and exit if it was not possible to read the parameter
            print("\33[91mCould not get parameter "+key+", does it exist?\33[0m")
            exit()
        return p
    

    def get_parameter_value(self, key):
        """
        Get the current value of a given parameter.

        Parameters:
            key (str): String with the name of the parameter whose value is to be read.
        
        Returns:
            value (variable type *): Current value of the requested parameter. *Type options are: float, int, bool
        """
        try:
            # Try to read the parameter value
            value = self.data.get(key)["value"]
        except:
            # Throw an error and exit if it was not possible to read the parameter
            print("\33[91mCould not get value of parameter "+key+", does it exist?\33[0m")
            exit()
        return value


    def load_file(self):
        """
        Load the parameter stored in the variable self.json_path

        Returns:
            p (dict): Dictionary with the list of parameters and its attributes
        """
        
        try:
            # Try to read the JSON parameter file
            with open(self.json_path, "r") as file:
                p = json.load(file)
                print(f"\33[92m[parameter_server] Loaded file: {self.json_path}\33[0m")
                return p
        except FileNotFoundError:
            print(f"\33[91mError: The file '{self.json_path}' does not exist.\33[0m")
        except IsADirectoryError:
            print(f"\33[91mError: '{self.json_path}' is a directory, not a file.\33[0m")
        except Exception as e:
            print(f"\33[91mAn unexpected error occurred: {str(e)}\33[0m")
        exit()



if __name__ == "__main__":

    # Load default file if script is run directly
    default_file_path = os.path.expanduser('~')+"/simulation_ws/src/px4sim/config/sim_params.json"
    params = parameter_server(default_file_path)

