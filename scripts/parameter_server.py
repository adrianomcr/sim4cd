#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Parameter server for the simulator

import json

class parameter_server(object):
    """
    Parameter server class
    """

    def __init__(self, json_path_):
        """
        Constructor for the parameter_server class

        Parameters:
            json_path_ (str): String with the JSON parameter file
        """

        self.json_path = json_path_
        self.data = self.load_file()

    def get_parameter(self, key):
        return self.data.get(key)
    
    def get_parameter_value(self, key):
        try:
            value = self.data.get(key)["value"]
        except:
            print("\33[91mCould not get value of parameter "+key+", does it exists?\33[0m")
            exit()
        return value

    def load_file(self):
        try:
            with open(self.json_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    # def save_to_file(self):
    #     with open(self.json_path, "w") as file:
    #         json.dump(self.data, file)


if __name__ == "__main__":
    default_file_path = "/home/NEA.com/adriano.rezende/simulation_ws/src/px4sim/config/sim_params.json"
    params = parameter_server(default_file_path)

