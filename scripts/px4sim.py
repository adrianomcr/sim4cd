#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Simulation of drone dynamics integrated with PX4


import time
import threading
import signal
import numpy as np

import sensors as SENS
import silsim_comm as COM
import ros_viz as VIZ
import dynamics as DYN
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


def sim_main():
    """
    Simulation main function
    """

    global channels

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

    p0 = np.array([0,0,0])
    v0 = np.array([0,0,0])
    q0 = np.array([1,0,0,0])
    # q0 = np.array([0.707,0,0,-0.707])
    w0 = np.array([0,0,0])
    # Create an object to simulate the vehicle dynamics
    quad = DYN.quad_dynamics(max_sim_interval, p0,v0,q0,w0)

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

        # Get some state variables for sensor simulation
        p, v, q, w = quad.get_states()
        tau = quad.get_tau()
        total_force = quad.get_total_force()
        m = quad.m

        # Compute sensors TODO: Simulate sensors inside dynamics
        acc = SENS.get_acc(q, total_force, m)
        gyro = SENS.get_gyro(w)
        mag = SENS.get_mag(q,tau)
        bar = SENS.get_baro(p[2])

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
        if (t-last_time_sensors > 0):
            PX4.send_sensors(acc,gyro,mag,bar)
            last_time_sensors = t

        # Send system GPS data to PX4
        t = time.time()
        if (t-last_time_gps > 0.02): # 50Hz
            gps = SENS.get_gps(p,v)
            PX4.send_gps(gps)
            last_time_gps = t

        # Send system Ground Truth data to PX4 (for logging and comparison purposes)
        t = time.time()
        if (t-last_time_gt > 0.02): # 50Hz
            gt = SENS.get_ground_truth(p,v,q,w)
            PX4.send_ground_truth(gt)
            last_time_gt = t

        # Send RC data to PX4
        # t = time.time()
        # if (t-last_time_rc > 0.02): # 50Hz
        #     #PX4.send_rc_commands(1500,1500,1500,1500)
        #     PX4.send_rc_commands(channels)
        #     last_time_rc = t
        
        # Update ROS visualization
        t = time.time()
        if (t-last_time_ros_viz > 0.05): # 20Hz
            ros_aux.update_ros_info(p,q,v,w,p0,q0)
            last_time_ros_viz = t

        # Print info
        t = time.time()
        if (t-last_time_print > 0.1): # 10Hz
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
            print("\33[0m")
            last_time_print = t


if __name__ == "__main__":

    # Spin the simulator
    sim_main()
