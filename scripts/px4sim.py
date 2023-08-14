#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Drone dynamics, drag force, effects like gyroscopic effect, etc ...




import numpy as np
import time
import threading

import actuators as ACT
import sensors as SENS
import silsim_comm as COM
import math_utils as MU
# import joystick as JOY
import ros_viz as VIZ
import dynamics as DYN




import signal
def custom_handler(signal, frame):
    print("\33[92mCtrl+C pressed. Running cleanup function.\33[0m]")
    global ros_aux
    del ros_aux
    exit()
    # # Your custom function code here
    # sys.exit(0)


def main_loop():
    global channels
    # Set the desired loop frequency in Hertz (times per second)
    loop_frequency = 500

    # Calculate the time interval for one loop iteration in seconds
    loop_interval = 1 / loop_frequency


    # # Initialize states
    # p = np.array([0,0,0])
    # v = np.array([0,0,0])
    # q = np.array([1,0,0,0])
    # # q = np.array([0.707,0,0,0.707])
    # w = np.array([0,0,0])


    PX4 = COM.px4_connection("tcpin", "localhost", "4560")
    c = PX4.connect()

    quad = DYN.quad_dynamics(loop_interval)

    # Register the custom_handler function to be called when Ctrl+C is pressed
    signal.signal(signal.SIGINT, custom_handler)
    global ros_aux
    ros_aux = VIZ.drone_show()

    last_time_sys_time = -1
    last_time_heart_beat = -1
    last_time_sensors = -1
    last_time_gps = -1
    last_time_gt = -1
    last_time_rc = -1

    motor_commands = [0,0,0,0]
    




    
    channels = [1500]*18
    # keyboard_thread = threading.Thread(target=JOY.keyboard_input_thread)
    # keyboard_thread.start()
    
    wtest = np.array([0,0,0])

    counter_flag = True
    t0 = time.time()
    # Start the loop
    iteration = 0
    while True:
        loop_start_time = time.time()



        # Receive MAVLink messages (blocking operation)
        msg = c.recv_match(blocking=False)
        # print(msg)

        if msg is not None:
            #print("\33[91m")
            #print("msg.get_type(): ", msg.get_type())
            # Check if it's the expected message type (SET_ACTUATOR_CONTROL_TARGET)
            #if msg.get_type() == "SET_ACTUATOR_CONTROL_TARGET":
            if msg.get_type() == "HIL_ACTUATOR_CONTROLS":
            
                if(counter_flag):
                    if(msg.controls[0]>0):
                        counter_flag = False
                        counter = 0
                        t0 = time.time()
                        wtest = np.array([0,0,1])

                if(not counter_flag):
                    # print ("\33[91m", msg, "\33[0m")
                    counter = counter + 1
                    # print ("\33[92m", counter/(time.time()-t0), "\33[0m")


                    # Extract motor control commands from the message
                    motor_commands = msg.controls #values in [0.0, 1.0]

                    # Process the motor commands and apply them to your simulator's motors
                    # Example: Apply motor_commands[0] to motor 1, motor_commands[1] to motor 2, and so on.
                    #print("Received message:", msg)
                    # print("\33[91mReceived motor commands:", motor_commands, "\33[0m")
        
            #print("\33[0m")


        # Model integration step
        quad.model_step(motor_commands)


        p = quad.get_pos()
        q = quad.get_quat()
        v = quad.get_vel_w()
        w = quad.get_omega()
        tau = quad.get_tau()
        total_force = quad.get_total_force()
        m = quad.m


        acc = SENS.get_acc(q, total_force, m)
        gyro = SENS.get_gyro(w)
        mag = SENS.get_mag(q,tau)
        bar = SENS.get_baro(p[2])
        # acc = SENS.get_acc(quad.get_quat(), quad.get_total_force(), quad.m)
        # gyro = SENS.get_gyro(quad.get_omega())
        # mag = SENS.get_mag(quad.get_quat(),quad.get_tau())
        # bar = SENS.get_baro((quad.get_p)[2])



        t = time.time()
        if (t-last_time_sys_time > 4):
            PX4.send_system_time()
            last_time_sys_time = t

        t = time.time()
        if (t-last_time_heart_beat > 1):
            PX4.send_heart_beat()
            last_time_heart_beat = t

        t = time.time()
        if (t-last_time_sensors > 0):
            PX4.send_sensors(acc,gyro,mag,bar)
            last_time_sensors = t


        t = time.time()
        if (t-last_time_gps > 0.02): # 50Hz
            gps = SENS.get_gps(p,v)
            PX4.send_gps(gps)
            last_time_gps = t

        t = time.time()
        if (t-last_time_gt > 0.02): # 50Hz
            gt = SENS.get_ground_truth(p,v,q,w)
            PX4.send_ground_truth(gt)
            last_time_gt = t



        # t = time.time()
        # if (t-last_time_rc > 0.02): # 50Hz
        #     #PX4.send_rc_commands(1500,1500,1500,1500)
        #     PX4.send_rc_commands(channels)
        #     last_time_rc = t

        
        

        
        if iteration % (50) == 0:
            ros_aux.update_ros_info(p,q,v,w)

        # Increment iteration count
        iteration += 1
        if iteration % (100) == 0:
            print("Iteration:", iteration)
            print("  pos: ", p)
            print("to_fo: ", total_force/m)
            print("  vel: ", v)
            print(" quat: ", q)
            print("omega: ", w)
            print("tau: ", tau)
            print("motor_commands: %f  %f  %f  %f" % (motor_commands[0], motor_commands[1], motor_commands[2], motor_commands[3]))
            print("")



        # Sleep to control loop frequency
        elapsed_time = time.time() - loop_start_time
        sleep_time = max(0, loop_interval - elapsed_time)
        # if(sleep_time==0):
        #     print("\33[93m[Warning] simulation loop took too long to compute\33[0m")
        # print(loop_interval - elapsed_time)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main_loop()




















# # Example usage:
# q = np.array([1.0, 0.0, 0.0, 0.0])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
# w = np.array([0.1, 0.2, 0.3])      # Example angular velocity [0.1, 0.2, 0.3]
# q_dot = MU.quaternion_derivative(q, w)
# print("Quaternion derivative:", q_dot)
