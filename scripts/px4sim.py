#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Simulation of drone dynamics integrated with PX4


import time
import threading
import signal
import numpy as np
from math import pi, sin, cos
import os

import sensors as SENS
import silsim_comm as COM
import ros_viz as VIZ
import dynamics as DYN
import parameter_server as PRM
# import joystick as JOY


def custom_handler(signal, frame):
    """
    ROS cleanup  function
    """

    print("\33[92mCtrl+C pressed. Running cleanup function\33[0m")
    global ros_aux
    # Terminate ROS node
    del ros_aux

    # Terminate px4sim
    print("\33[92mExiting\33[0m") 
    exit()


def sim_main(params):
    """
    Simulation main function
    """

    # Load parameters
    ros_en = params.get_parameter_value('SIM_ROS_EN')
    ros_hz = params.get_parameter_value('SIM_ROS_HZ')
    sens_hz = params.get_parameter_value('SIM_SENS_HZ')
    gps_hz = params.get_parameter_value('SIM_GPS_HZ')
    gt_en = params.get_parameter_value('SIM_GT_EN')
    gt_hz = params.get_parameter_value('SIM_GT_HZ')
    print_en = params.get_parameter_value('SIM_PRINT_EN')
    print_hz = params.get_parameter_value('SIM_PRINT_HZ')
    init_pos_x = params.get_parameter_value('SIM_INIT_POS_X')
    init_pos_y = params.get_parameter_value('SIM_INIT_POS_Y')
    init_yaw = (pi/180)*params.get_parameter_value('SIM_INIT_YAW') # Converted to radians
    p0 = np.array([init_pos_x,init_pos_y,0])
    q0 = np.array([cos(init_yaw/2),0,0,sin(init_yaw/2)])

    # Set the minimum desired frequency [Hz]
    sim_frequency_alert = 400 # an alert will show if a simulation step takes more than 1/sim_frequency_alert seconds

    # Calculate the maximum desired time interval for one simulated step [s]
    max_sim_interval = 1 / sim_frequency_alert

    # Register the custom_handler function to be called when Ctrl+C is pressed
    signal.signal(signal.SIGINT, custom_handler)

    # Create an object responsible by providing ROS  wih the simulated information
    global ros_aux
    ros_aux = VIZ.drone_show()

    # Create a object that is able to connect to px4_sitl
    PX4 = COM.px4_connection("tcpin", "localhost", "4560")
    # Connect to px4_sitl
    PX4.connect()

    # Create an object to simulate the vehicle dynamics
    quad = DYN.vehicle_dynamics(max_sim_interval, params)

    # Flags to control the frequency of communication with px4
    last_time_sys_time = -1
    last_time_heart_beat = -1
    last_time_sensors = -1
    last_time_gps = -1
    last_time_gt = -1
    last_time_rc = -1
    last_time_ros_viz = -1
    last_time_print = -1
    #TODO: Create a timer class to control these stuff
    
    # variable that store the actuator PWMs
    actuator_commands = [0,0,0,0]

    counter_flag = True
    t0 = time.time()
    # Start the loop
    iteration = 0
    while True:
        loop_start_time = time.time()

        # Increment iteration count
        iteration += 1

        # Check for new actuator controls from PX4
        new, value = PX4.get_actuator_controls()
        if(new):
            actuator_commands = value

        # Perform the dynamic model integration step
        quad.model_step(actuator_commands)

        # Send system time to PX4
        t = time.time()
        if (t-last_time_sys_time > 4):
            PX4.send_system_time()
            last_time_sys_time = t

        # Send system heart beat to PX4
        t = time.time()
        if (t-last_time_heart_beat > 1):
            PX4.send_heart_beat()
            last_time_heart_beat = t

        # Send system sensors data to PX4
        t = time.time()
        if (t-last_time_sensors > 1/sens_hz):
            # Get the current sensor values
            acc = quad.get_acc()
            gyro = quad.get_gyro()
            mag = quad.get_mag()
            bar = quad.get_baro()
            PX4.send_sensors(acc,gyro,mag,bar)
            last_time_sensors = t

        # Send system GPS data to PX4
        t = time.time()
        if (t-last_time_gps > 1/gps_hz): # 50Hz
            gps = quad.get_gps()
            PX4.send_gps(gps)
            # PX4.send_battery()
            last_time_gps = t

        # Send system Ground Truth data to PX4 (for logging and comparison purposes)
        if(gt_en):
            t = time.time()
            if (t-last_time_gt > 1/gt_hz): # 50Hz
                gt = quad.get_ground_truth()
                PX4.send_ground_truth(gt)
                last_time_gt = t

        # Send RC data to PX4
        # t = time.time()
        # if (t-last_time_rc > 0.02): # 50Hz
        #     #PX4.send_rc_commands(1500,1500,1500,1500)
        #     PX4.send_rc_commands(channels)
        #     last_time_rc = t
        
        # Update ROS visualization
        if(ros_en):
            t = time.time()
            if (t-last_time_ros_viz > 1/ros_hz): # 20Hz
                p, v, q, w = quad.get_states()
                ros_aux.update_ros_info(p,v,q,w,p0,q0)
                last_time_ros_viz = t

        # Print info
        if(print_en):
            t = time.time()
            if (t-last_time_print > 1/print_hz): # 10Hz
                # Get some state variables for sensor simulation
                p, v, q, w = quad.get_states()
                tau = quad.get_tau()
                total_force = quad.get_total_force()
                m = quad.m
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
                print("\33[0m\33[40mactuator_commands: %f  %f  %f  %f\33[0m" % (actuator_commands[0], actuator_commands[1], actuator_commands[2], actuator_commands[3]))
                color = ['\33[92m','\33[91m','\33[93m']
                status = quad.get_status()
                print(color[status]+"status: ", status,'\33[0m')
                print("\33[0m")
                last_time_print = t


    def load_parameters(self, params):
        """
        Load parameters for the PX4 simulation and store them in the instance variables

        Parameters:
            params (<parameter_server.parameter_server>): Parameter server object that contains the values of interest
        """

        #TODO: Read parameters here

        return


if __name__ == "__main__":

    param_file_name = os.path.expanduser('~')+"/simulation_ws/src/px4sim/config/sim_params.json"
    params = PRM.parameter_server(param_file_name)

    # Spin the simulator
    sim_main(params)
