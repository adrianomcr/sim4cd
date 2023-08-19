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

    print("\33[92mCtrl+C pressed. Running cleanup function.\33[0m]")
    global ros_aux
    del ros_aux

    exit()


def sim_main():
    """
    Simulation main function
    """

    global channels

    # Set the desired loop frequency [Hz]
    sim_frequency = 500

    # Calculate the time interval for one simulated step [s]
    sim_interval = 1 / sim_frequency

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
    quad = DYN.quad_dynamics(sim_interval, p0,v0,q0,w0)

    # Flags to control the frequency of communication with px4
    last_time_sys_time = -1
    last_time_heart_beat = -1
    last_time_sensors = -1
    last_time_gps = -1
    last_time_gt = -1
    last_time_rc = -1

    # # Create a thread that keeps listening to a joystick
    # channels = [1500]*18
    # keyboard_thread = threading.Thread(target=JOY.keyboard_input_thread)
    # keyboard_thread.start()
    
    # variable that store the actuator PWMs
    actuator_commands = [0,0,0,0]

    counter_flag = True
    t0 = time.time()
    # Start the loop
    iteration = 0
    while True:
        loop_start_time = time.time()

        # Check for new actuator controls from PX4
        new, value = PX4.get_actuator_controls()
        if(new):
            actuator_commands = value

        # Perform the dynamic model integration step
        quad.model_step(actuator_commands)

        # Get some state variables
        p = quad.get_pos()
        q = quad.get_quat()
        v = quad.get_vel_w()
        w = quad.get_omega()
        tau = quad.get_tau()
        total_force = quad.get_total_force()
        m = quad.m

        # Compute sensors
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

        # Send system Ground Truth data to PX4 (for lgging and comparison purpuses)
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
        
        # update ROS vizualixation    
        if iteration % (50) == 0:
            ros_aux.update_ros_info(p,q,v,w,p0,q0)

        # Increment iteration count
        iteration += 1
        if iteration % (100) == 0:
            print("\33[0m\33[40mIteration:", iteration, "\33[0m")
            print("\33[0m\33[97m  pos: ", p, "\33[0m")
            print("\33[0m\33[40m  vel: ", v, "\33[0m")
            print("\33[0m\33[97m quat: ", q, "\33[0m")
            print("\33[0m\33[40momega: ", w, "\33[0m")
            print("\33[0m\33[97mtau: ", tau, "\33[0m")
            print("\33[0m\33[40mactuator_commands: %f  %f  %f  %f\33[0m" % (actuator_commands[0], actuator_commands[1], actuator_commands[2], actuator_commands[3]))
            print("\33[0m")

        # Sleep to control loop frequency
        elapsed_time = time.time() - loop_start_time
        sleep_time = max(0, sim_interval - elapsed_time)
        # Throw a warning if the simulatiion is computationally heavy
        # if(sleep_time==0):
        #     print("\33[93m[Warning] simulation loop took too long to compute\33[0m")
        # print(sim_interval - elapsed_time)
        time.sleep(sleep_time)


if __name__ == "__main__":

    # Spin the simulator
    sim_main()
