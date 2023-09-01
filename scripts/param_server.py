#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Parameter served for the simulator

import json


class parm_server(object):
    """
    Drone dynamics class
    """

    def __init__(self, json_path_):
        """
        Constructor for the dynamics class

        Parameters:
            dt_max_ (float): Maximum

        """

        self.json_path = json_path_
        self.data = self.load_file()

    def get_parameter(self, key):
        return self.data.get(key)
    
    def get_parameter_value(self, key):
        return self.data.get(key)["value"]

    def load_file(self):
        try:
            with open(self.json_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_to_file(self):
        with open(self.json_path, "w") as file:
            json.dump(self.data, file)