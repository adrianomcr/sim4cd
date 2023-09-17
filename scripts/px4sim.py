#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Copter simulation integrated with PX4

import time
import threading
import signal
import numpy as np
from math import pi, sin, cos
import os
import sys

import silsim_comm as COM
import ros_viz as VIZ
import dynamics as DYN
import parameter_server as PRM
import timer as TIM
# import joystick as JOY


class px4sim(object):
    """
    PX4 simulation class
    """

    def __init__(self, params):
        """
        Constructor for the px4sim class

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object
        """

        # Load model parameters
        self.load_parameters(params)

        # Set the minimum desired frequency [Hz]
        sim_frequency_alert = 400 # an alert will show if a simulation step takes more than 1/sim_frequency_alert seconds

        # Calculate the maximum desired time interval for one simulated step [s]
        max_sim_interval = 1 / sim_frequency_alert

        # Register the custom_handler function to be called when Ctrl+C is pressed
        signal.signal(signal.SIGINT, self.custom_handler)

        # Create an object responsible by providing ROS  wih the simulated information
        self.ros_aux = VIZ.drone_show()

        # Create a object that is able to connect to px4_sitl
        self.PX4 = COM.px4_connection("tcpin", "localhost", "4560")
        # Connect to px4_sitl
        self.PX4.connect()

        # Create an object to simulate the vehicle dynamics
        self.quad = DYN.vehicle_dynamics(max_sim_interval, params)

        # Timers to control the frequency of communication with px4
        self.timer_sys_time = TIM.timer(period=4)
        self.timer_heart_beat = TIM.timer( period=1)
        self.timer_sensors = TIM.timer(frequency=self.sens_hz)
        self.timer_gps = TIM.timer(frequency=self.gps_hz)
        self.timer_gt = TIM.timer(frequency=self.gt_hz, enabled=self.gt_en)
        # self.timer_rc = TIM.timer(frequency=self.rc_hz)
        self.timer_ros_viz = TIM.timer(frequency=self.ros_hz, enabled=self.ros_en)
        self.timer_print = TIM.timer(frequency=self.print_hz, enabled=self.print_en)

        # Variable that stores the actuator PWMs
        self.actuator_commands = [0]*8


    def custom_handler(self, signal, frame):
        """
        ROS cleanup  function
        """

        print("\33[92mCtrl+C pressed. Running cleanup function\33[0m")
        # Terminate ROS node
        del self.ros_aux

        # Terminate px4sim
        print("\33[92mExiting\33[0m") 
        exit()


    def run(self):
        """
        Simulation main loop function
        """
 
        t0 = time.time()
        # Start the loop
        iteration = 0
        while True:
            loop_start_time = time.time()

            # Increment iteration count
            iteration += 1

            # Check for new actuator controls from PX4
            new, value = self.PX4.get_actuator_controls()
            if(new):
                self.actuator_commands = value

            # Perform the dynamic model integration step
            self.quad.model_step(self.actuator_commands)

            # Send system time to PX4
            if(self.timer_sys_time.tick()):
                self.PX4.send_system_time()

            # Send heart beat to PX4
            if (self.timer_heart_beat.tick()):
                self.PX4.send_heart_beat()

            # Send sensors data to PX4
            if(self.timer_sensors.tick()):
                # Get the current sensor values
                acc = self.quad.get_acc()
                gyro = self.quad.get_gyro()
                mag = self.quad.get_mag()
                bar = self.quad.get_baro()
                self.PX4.send_sensors(acc,gyro,mag,bar)

            # Send GPS data to PX4
            if (self.timer_gps.tick()):
                gps = self.quad.get_gps()
                self.PX4.send_gps(gps)

            # Send Ground Truth data to PX4 (for logging and comparison purposes)
            if (self.timer_gt.tick()):
                gt = self.quad.get_ground_truth()
                self.PX4.send_ground_truth(gt)

            # # Send RC data to PX4
            # if (self.timer_rc.tick()):
            #     self.PX4.send_rc_commands(channels)
            
            # Update ROS visualization
            if (self.timer_ros_viz.tick()):
                p, v, q, w = self.quad.get_states()
                self.ros_aux.update_ros_info(p,v,q,w,self.p0,self.q0)

            # Print info
            if (self.timer_print.tick()):
                # Get some state variables for sensor simulation
                p, v, q, w = self.quad.get_states()
                tau = self.quad.get_tau()
                total_force = self.quad.get_total_force()
                m = self.quad.m
                print("\33[1mIteration:", iteration, "\33[0m")
                print("\33[0m\33[40mAverage freq:", iteration/(time.time()-t0), "\33[0m")
                print("\33[0m\33[97m  pos: ", p, "\33[0m")
                print("\33[0m\33[40m  vel: ", v, "\33[0m")
                print("\33[0m\33[97m quat: ", q, "\33[0m")
                print("\33[0m\33[40momega: ", w, "\33[0m")
                print("\33[0m\33[97mtau:   ", tau, "\33[0m")
                # print("\33[0m\33[40macc:   ", acc, "\33[0m")
                # print("\33[0m\33[97mgyro:  ", gyro, "\33[0m")
                # print("\33[0m\33[40mmag:   ", mag, "\33[0m")
                # print("\33[0m\33[97mbar:   ", bar, "\33[0m")
                print("\33[0m\33[40mactuator_commands: %f  %f  %f  %f\33[0m" % (self.actuator_commands[0], self.actuator_commands[1], self.actuator_commands[2], self.actuator_commands[3]))
                print("\33[0m\33[97mBattery: ", self.quad.vehicle_geo.battery.output_voltage(), "   ", self.quad.vehicle_geo.battery.soc, "\33[0m")
                color = ['\33[92m','\33[91m','\33[93m']
                status = self.quad.get_status()
                print(color[status]+"status: ", status,'\33[0m')
                print("\33[0m")


    def load_parameters(self, params):
        """
        Load parameters for the PX4 simulation and store them in the instance variables

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object that contains the values of interest
        """

        # Load parameters
        self.ros_en = params.get_parameter_value('SIM_ROS_EN')
        self.ros_hz = params.get_parameter_value('SIM_ROS_HZ')
        self.sens_hz = params.get_parameter_value('SIM_SENS_HZ')
        self.gps_hz = params.get_parameter_value('SIM_GPS_HZ')
        self.gt_en = params.get_parameter_value('SIM_GT_EN')
        self.gt_hz = params.get_parameter_value('SIM_GT_HZ')
        self.print_en = params.get_parameter_value('SIM_PRINT_EN')
        self.print_hz = params.get_parameter_value('SIM_PRINT_HZ')
        self.init_pos_x = params.get_parameter_value('SIM_INIT_POS_X')
        self.init_pos_y = params.get_parameter_value('SIM_INIT_POS_Y')
        self.init_yaw = (pi/180)*params.get_parameter_value('SIM_INIT_YAW') # Converted to radians
        self.p0 = np.array([self.init_pos_x,self.init_pos_y,0])
        self.q0 = np.array([cos(self.init_yaw/2),0,0,sin(self.init_yaw/2)])


if __name__ == "__main__":
    """
    Simulator main function

    Parameters:
        param_file_name (str): Full path to the JSON config file
    """

    # Define the full path for the parameter file
    if len(sys.argv) < 2:
        # Use the default if no argument is provided
        param_file_name = os.path.expanduser('~')+"/simulation_ws/src/px4sim/config/sim_params.json"
        print(f"\33[94m[px4sim] Using default parameter file: {param_file_name}\33[0m")
    elif len(sys.argv) >= 2:
        # Use the provided argument 
        param_file_name = str(sys.argv[1])
        print(f"\33[94m[px4sim] Argument parameter file: {param_file_name}\33[0m")
    if len(sys.argv) > 2:
        # Inform that provided extra arguments were ignored
        print("\33[93m[px4sim] Extra arguments ignored\33[0m")

    # Load parameter file
    params = PRM.parameter_server(param_file_name)

    # Create the simulator object
    sim = px4sim(params)
    # Spin the simulator
    sim.run()
