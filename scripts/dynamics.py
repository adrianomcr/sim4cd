#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Quadcopter simulation with PX4 integration


import numpy as np
import time
import threading

import actuators as ACT
import sensors as SENS
import silsim_comm as COM
import math_utils as MU
# import joystick as JOY
import ros_viz as VIZ






class quad_dynamics(object):
    """
    Drone state and markers publisher
    """

    def __init__(self, dt_):


        # Model constants
        self.g = 9.81
        self.m = 2.0
        self.drag_v = 0.1
        self.drag_w = 0.01
        self.J = 0.006*10

        # Initialize states
        self.p = np.array([0,0,0])
        self.v = np.array([0,0,0])
        self.q = np.array([1,0,0,0])
        # self.q = np.array([0.707,0,0,0.707])
        self.w = np.array([0,0,0])


        # Important variables
        self.tau = 0
        self.total_force = 0

        self.dt = dt_



    def model_step(self, motor_commands):

        f1 = ACT.thrust(motor_commands[0])
        f2 = ACT.thrust(motor_commands[1])
        f3 = ACT.thrust(motor_commands[2])
        f4 = ACT.thrust(motor_commands[3])
        #    3       1
        #        ^
        #        |
        #    2       4

        #    2       0
        #        ^
        #        |
        #    1       3


        #self.tau = 2.1*g
        self.tau = f1+f2+f3+f4
        if(self.p[2]<=0 and self.v[2]<0 and self.tau<self.m*self.g):
            self.tau = self.m*self.g*1.001
          
        T = [0,0,0]
        T[0] = 0.15*(-f1+f2+f3-f4)
        T[1] = 0.15*(-f1+f2-f3+f4)
        T[2] = 0.06*(-f1-f2+f3+f4)
        T = np.array(T)

        f_drag = -self.drag_v*self.v
        T_drag = -self.drag_w*self.w
        Tg = np.array([0,0,0]) # blades gyroscopic effect


        tau_vec_b = np.array([0,0,self.tau]) # Actuation force in body frame [N]
        self.total_force = MU.quat_apply_rot(self.q,tau_vec_b) + f_drag
        acc_w = np.array([0,0,-self.g]) + self.total_force/self.m

        # Dynamic model
        p_dot = self.v
        v_dot = acc_w
        q_dot = MU.quaternion_derivative(self.q,self.w)
        w_dot = (1/self.J)*(-self.J*np.cross(self.w,self.w) + T + T_drag)

        # Model integration
        self.p = self.p + p_dot*self.dt
        self.v = self.v + v_dot*self.dt
        self.q = self.q + q_dot*self.dt
        self.w = self.w + w_dot*self.dt

        # Quaternion renormalization
        self.q = MU.normalize(self.q)


    def get_pos(self):

        return self.p

    def get_vel_w(self):

        return self.v

    def get_quat(self):

        return self.q

    def get_omega(self):

        return self.w

    def get_tau(self):

        return self.tau

    def get_total_force(self):

        return self.total_force
        



# def main_loop():
#     global channels
#     # Set the desired loop frequency in Hertz (times per second)
#     loop_frequency = 500

#     # Calculate the time interval for one loop iteration in seconds
#     loop_interval = 1 / loop_frequency


#     # Initialize states
#     p = np.array([0,0,0])
#     v = np.array([0,0,0])
#     q = np.array([1,0,0,0])
#     # q = np.array([0.707,0,0,0.707])
#     w = np.array([0,0,0])


#     PX4 = COM.px4_connection("tcpin", "localhost", "4560")
#     c = PX4.connect()

#     # Register the custom_handler function to be called when Ctrl+C is pressed
#     signal.signal(signal.SIGINT, custom_handler)
#     global ros_aux
#     ros_aux = VIZ.drone_show()

#     last_time_sys_time = -1
#     last_time_heart_beat = -1
#     last_time_sensors = -1
#     last_time_gps = -1
#     last_time_gt = -1
#     last_time_rc = -1

#     motor_commands = [0,0,0,0]
    




    
#     channels = [1500]*18
#     # keyboard_thread = threading.Thread(target=JOY.keyboard_input_thread)
#     # keyboard_thread.start()
    


#     counter_flag = True
#     t0 = time.time()
#     # Start the loop
#     iteration = 0
#     while True:
#         loop_start_time = time.time()



#         # Receive MAVLink messages (blocking operation)
#         msg = c.recv_match(blocking=False)
#         # print(msg)

#         if msg is not None:
#             #print("\33[91m")
#             #print("msg.get_type(): ", msg.get_type())
#             # Check if it's the expected message type (SET_ACTUATOR_CONTROL_TARGET)
#             #if msg.get_type() == "SET_ACTUATOR_CONTROL_TARGET":
#             if msg.get_type() == "HIL_ACTUATOR_CONTROLS":
            
#                 if(counter_flag):
#                     if(msg.controls[0]>0):
#                         counter_flag = False
#                         counter = 0
#                         t0 = time.time()
#                         wtest = np.array([0,0,1])

#                 if(not counter_flag):
#                     # print ("\33[91m", msg, "\33[0m")
#                     counter = counter + 1
#                     # print ("\33[92m", counter/(time.time()-t0), "\33[0m")


#                     # Extract motor control commands from the message
#                     motor_commands = msg.controls #values in [0.0, 1.0]

#                     # Process the motor commands and apply them to your simulator's motors
#                     # Example: Apply motor_commands[0] to motor 1, motor_commands[1] to motor 2, and so on.
#                     #print("Received message:", msg)
#                     # print("\33[91mReceived motor commands:", motor_commands, "\33[0m")
        
#             #print("\33[0m")


#         # f1 = ACT.thrust(motor_commands[0])
#         # f2 = ACT.thrust(motor_commands[1])
#         # f3 = ACT.thrust(motor_commands[2])
#         # f4 = ACT.thrust(motor_commands[3])
#         # # print("\33[91mReceived motor commands:", [f1,f2,f3,f4], "\33[0m")
#         # #    3       1
#         # #        ^
#         # #        |
#         # #    2       4

#         # #    2       0
#         # #        ^
#         # #        |
#         # #    1       3



#         # # f1 = 5.019
#         # # f2 = 5.01
#         # # f3 = 5.01
#         # # f4 = 5.019


#         # #tau = 2.1*g
#         # tau = f1+f2+f3+f4
#         # if(p[2]<=0 and v[2]<0 and tau<m*g):
#         #     tau = m*g*1.001
          
#         # T = [0,0,0]
#         # #T[0] = 0.1*(-f1+f2+f3-f4)
#         # #T[1] = 0.1*(-f1+f2-f3+f4)*0
#         # #T[2] = 0.01*(-f1-f2+f3+f4)*0

#         # T[0] = 0.15*(-f1+f2+f3-f4)
#         # T[1] = 0.15*(-f1+f2-f3+f4)
#         # T[2] = 0.06*(-f1-f2+f3+f4)
        
#         # T = np.array(T)

#         # f_drag = -drag_v*v
#         # T_drag = -drag_w*w
#         # Tg = np.array([0,0,0]) # blades gyroscopic effect

#         # # p_dot = v;
#         # # v_dot = R_bw*z_hat*tau/m - g*z_hat + Fd; // add drag
#         # # q_dot = quat_derivative(q, R_bw*w);
#         # # w_dot << J.inverse()*(-v1.cross(v2) + T - Td - Tg); //temp // include model

#         # tau_vec_b = np.array([0,0,tau]) # Actuation force in body frame [N]
#         # total_force = MU.quat_apply_rot(q,tau_vec_b) + f_drag
#         # acc_w = np.array([0,0,-g]) + total_force/m

#         # # if(not counter_flag):
#         # #     w = wtest

#         # # Dynamic model
#         # p_dot = v
#         # v_dot = acc_w
#         # q_dot = MU.quaternion_derivative(q,w)
#         # w_dot = (1/J)*(-J*np.cross(w,w) + T + T_drag)

#         # # Model integration
#         # dt = loop_interval

#         # p = p + p_dot*dt
#         # v = v + v_dot*dt
#         # q = q + q_dot*dt
#         # w = w + w_dot*dt

#         # # Quaternion renormalization
#         # q = MU.normalize(q)


#         acc = SENS.get_acc(q, total_force, m)
#         gyro = SENS.get_gyro(w)
#         mag = SENS.get_mag(q,tau)
#         bar = SENS.get_baro(p[2])



#         t = time.time()
#         if (t-last_time_sys_time > 4):
#             PX4.send_system_time()
#             last_time_sys_time = t

#         t = time.time()
#         if (t-last_time_heart_beat > 1):
#             PX4.send_heart_beat()
#             last_time_heart_beat = t

#         t = time.time()
#         if (t-last_time_sensors > 0):
#             PX4.send_sensors(acc,gyro,mag,bar)
#             last_time_sensors = t


#         t = time.time()
#         if (t-last_time_gps > 0.02): # 50Hz
#             gps = SENS.get_gps(p,v)
#             PX4.send_gps(gps)
#             last_time_gps = t

#         t = time.time()
#         if (t-last_time_gt > 0.02): # 50Hz
#             gt = SENS.get_ground_truth(p,v,q,w)
#             PX4.send_ground_truth(gt)
#             last_time_gt = t



#         # t = time.time()
#         # if (t-last_time_rc > 0.02): # 50Hz
#         #     #PX4.send_rc_commands(1500,1500,1500,1500)
#         #     PX4.send_rc_commands(channels)
#         #     last_time_rc = t

        
        

        
#         if iteration % (50) == 0:
#             ros_aux.update_ros_info(p,q,v,w)

#         # Increment iteration count
#         iteration += 1
#         if iteration % (100) == 0:
#             print("Iteration:", iteration)
#             print("  pos: ", p)
#             print("to_fo: ", total_force/m)
#             print("  vel: ", v)
#             print(" quat: ", q)
#             print("omega: ", w)
#             print("tau: ", tau)
#             print("motor_commands: %f  %f  %f  %f" % (motor_commands[0], motor_commands[1], motor_commands[2], motor_commands[3]))
#             print("")



#         # Sleep to control loop frequency
#         elapsed_time = time.time() - loop_start_time
#         sleep_time = max(0, loop_interval - elapsed_time)
#         # if(sleep_time==0):
#         #     print("\33[93m[Warning] simulation loop took too long to compute\33[0m")
#         # print(loop_interval - elapsed_time)
#         time.sleep(sleep_time)

# if __name__ == "__main__":
#     main_loop()


















