#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Drone dynamics, drag force, effects like gyroscopic effect, etc ...




import numpy as np
import time

import actuators as ACT
import sensors as SENS
import silsim_comm as COM
import math_utils as MU
import joystick as JOY
import threading

g = 9.81
m = 2
drag_v = 0.5*1*0
drag_w = 0.1*1*0
J = 0.08









def main_loop():
    global channels
    # Set the desired loop frequency in Hertz (times per second)
    loop_frequency = 500

    # Calculate the time interval for one loop iteration in seconds
    loop_interval = 1 / loop_frequency


    # Initialize states
    p = np.array([0,0,0])
    v = np.array([0,0,0])
    q = np.array([1,0,0,0])
    # q = np.array([0.707,0,0,0.707])
    w = np.array([0,0,0])


    PX4 = COM.px4_connection("tcpin", "localhost", "4560")
    c = PX4.connect()



    last_time_sys_time = -1
    last_time_heart_beat = -1
    last_time_gps = -1
    last_time_sensors = -1
    last_time_gps = -1
    last_time_rc = -1

    motor_commands = [0,0,0,0]
    
    
    channels = [1500]*18
    keyboard_thread = threading.Thread(target=JOY.keyboard_input_thread)
    keyboard_thread.start()
    

    # Start the loop
    iteration = 0
    while True:
        loop_start_time = time.time()



        # Receive MAVLink messages (blocking operation)
        msg = c.recv_match(blocking=False)

        if msg is not None:
            #print("\33[91m")
            #print("msg.get_type(): ", msg.get_type())
            # Check if it's the expected message type (SET_ACTUATOR_CONTROL_TARGET)
            #if msg.get_type() == "SET_ACTUATOR_CONTROL_TARGET":
            if msg.get_type() == "HIL_ACTUATOR_CONTROLS":
            
                # Extract motor control commands from the message
                motor_commands = msg.controls

                # Process the motor commands and apply them to your simulator's motors
                # Example: Apply motor_commands[0] to motor 1, motor_commands[1] to motor 2, and so on.
                #print("Received message:", msg)
                #print("Received motor commands:", motor_commands)
        
            #print("\33[0m")


        f1 = ACT.thrust(motor_commands[0])
        f2 = ACT.thrust(motor_commands[1])
        f3 = ACT.thrust(motor_commands[2])
        f4 = ACT.thrust(motor_commands[3])
        #    3       1
        #        ^
        #        |
        #    2       4



        # f1 = 5.019
        # f2 = 5.01
        # f3 = 5.01
        # f4 = 5.019


        #tau = 2.1*g
        tau = f1+f2+f3+f4
        if(p[2]<=0 and v[2]<0 and tau<m*g):
            tau = m*g*1.001
          
        T = [0,0,0]  
        #T[0] = 0.1*(-f1+f2+f3-f4)
        #T[1] = 0.1*(-f1+f2-f3+f4)*0
        #T[2] = 0.01*(-f1-f2+f3+f4)*0




        T[0] = 0.15*(-f1+f2+f3-f4)
        T[1] = 0.15*(-f1+f2-f3+f4)
        T[2] = 0.06*(-f1-f2+f3+f4)
        
        T = np.array(T)

        f_drag = -drag_v*v
        T_drag = -drag_w*w
        Tg = np.array([0,0,0]) # blades gyroscopic effect

        # p_dot = v;
        # v_dot = R_bw*z_hat*tau/m - g*z_hat + Fd; // add drag
        # q_dot = quat_derivative(q, R_bw*w);
        # w_dot << J.inverse()*(-v1.cross(v2) + T - Td - Tg); //temp // include model

        tau_vec_b = np.array([0,0,tau])
        total_force = MU.quat_apply_rot(q,tau_vec_b) + f_drag
        acc_w = np.array([0,0,-g]) + total_force/m

        # Dynamic model
        p_dot = v
        v_dot = acc_w
        q_dot = MU.quaternion_derivative(q,w)
        w_dot = (1/J)*(-J*np.cross(w,w) + T + T_drag)

        # Model integration
        dt = loop_interval

        p = p + p_dot*dt
        v = v + v_dot*dt
        q = q + q_dot*dt
        w = w + w_dot*dt

        # Quaternion renormalization
        q = MU.normalize(q)


        acc = SENS.get_acc(q, total_force,m)
        gyro = SENS.get_gyro(w)
        mag = SENS.get_mag(q,tau)
        bar = SENS.get_baro(p[2])



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
        if (t-last_time_gps > 0.2): # 5Hz
            gps = SENS.get_gps(p)
            PX4.send_gps(gps)
            last_time_gps = t

        t = time.time()
        if (t-last_time_rc > 0.02): # 50Hz
            #PX4.send_rc_commands(1500,1500,1500,1500)
            PX4.send_rc_commands(channels)
            last_time_rc = t

        
        



        # Increment iteration count
        iteration += 1
        if iteration % (100) == 0:
            print("Iteration:", iteration)
            print("  pos: ", p)
            print("  vel: ", v)
            print(" quat: ", q)
            print("omega: ", w)
            print("tau: ", tau)
            print("motor_commands: %f  %f  %f  %f" % (motor_commands[0], motor_commands[1], motor_commands[2], motor_commands[3]))
            print("")


        # Sleep to control loop frequency
        elapsed_time = time.time() - loop_start_time
        sleep_time = max(0, loop_interval - elapsed_time)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main_loop()




















# Example usage:
q = np.array([1.0, 0.0, 0.0, 0.0])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
w = np.array([0.1, 0.2, 0.3])      # Example angular velocity [0.1, 0.2, 0.3]
q_dot = MU.quaternion_derivative(q, w)
print("Quaternion derivative:", q_dot)
