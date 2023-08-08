#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Drone dymanics, drag force, effects lyke gyroscopic effect, etc ...




import numpy as np
import time

import actuators as ACT
import sensors as SENS
import silsim_comm as COM


g = 9.81
m = 2
drag_v = 0.5
drag_w = 0.1
J = 0.08


def d_quat_from_omega(q_in,w_in):
    #Description:
    #Compute the qaternion derivative given a angulr sepeed w
    #ngular speed w is on th world/body???????? frame BODY!!!!!!!!!!!!!!!!!!!

    q = [q_in[0][0],q_in[1][0],q_in[2][0],q_in[3][0]]


    wx = w_in[0][0]
    wy = w_in[1][0]
    wz = w_in[2][0]
    return [0.5*( 0*q[0] - wx*q[1] - wy*q[2] - wz*q[3]),
            0.5*(wx*q[0] +  0*q[1] + wz*q[2] - wy*q[3]),
            0.5*(wy*q[0] - wz*q[1] +  0*q[2] + wx*q[3]),
            0.5*(wz*q[0] + wy*q[1] - wx*q[2] +  0*q[3]) ]


def quaternion_derivative(q, w):
    """
    Calculate the derivative of a quaternion given a quaternion and an angular velocity.

    Parameters:
        q (numpy.ndarray): Input quaternion [qw, qx, qy, qz].
        w (numpy.ndarray): Angular velocity in the world frame [wx, wy, wz]. BODY!!!!!!!!!!!!!!

    Returns:
        numpy.ndarray: The derivative of the quaternion [qw_dot, qx_dot, qy_dot, qz_dot].
    """
    q_matrix = np.array([
        [0, -w[0], -w[1], -w[2]],
        [w[0], 0, w[2], -w[1]],
        [w[1], -w[2], 0, w[0]],
        [w[2], w[1], -w[0], 0]
    ])

    q_dot = 0.5 * np.dot(q_matrix, q)
    return q_dot


def quat_conj(q_in):

    q_conj = -q_in
    q_conj[0] = q_in[0]

    return q_conj



def quaternion_multiply(q1, q2):
    """
    Perform quaternion multiplication (Hamilton product).

    Parameters:
        q1 (numpy.ndarray): First quaternion [qw, qx, qy, qz].
        q2 (numpy.ndarray): Second quaternion [qw, qx, qy, qz].

    Returns:
        numpy.ndarray: The result of quaternion multiplication.
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    q_result = np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])
    return q_result


def quat_apply_rot(q_in,u_in):
    #Description:
    #Apply the rotation given by q to the vector u

    u = np.array([0, u_in[0], u_in[1], u_in[2]])
    q = q_in
    q_conj = quat_conj(q_in)

    v = quaternion_multiply(q,quaternion_multiply(u,q_conj))

    


    # v = q.dot(u).dot(q_conj)

    return v[1:4]

    # v = quat_mult(quat_mult(q,u),q_conj)

    # return [v[1], v[2], v[3]]


def normalize(u):

    return u/np.linalg.norm(u)


def main_loop():
    # Set the desired loop frequency in Hertz (times per second)
    loop_frequency = 500

    # Calculate the time interval for one loop iteration in seconds
    loop_interval = 1 / loop_frequency


    # Initialize states
    p = np.array([0,0,0])
    v = np.array([0,0,0])
    q = np.array([1,0,0,0])
    w = np.array([0,0,0])


    PX4 = COM.px4_connection("tcpin", "localhost", "4560")
    PX4.connect()



    last_time_sys_time = -1
    last_time_heart_beat = -1
    last_time_gps = -1
    last_time_sensors = -1
    last_time_gps = -1
    last_time_rc = -1



    # Start the loop
    iteration = 0
    while True:
        loop_start_time = time.time()


        tau = 2.1*g
        T = [0,0,0]

        f_drag = -drag_v*v
        T_drag = -drag_w*w
        Tg = np.array([0,0,0]) # blades gyroscopic effect

        # p_dot = v;
        # v_dot = R_bw*z_hat*tau/m - g*z_hat + Fd; // add drag
        # q_dot = quat_derivative(q, R_bw*w);
        # w_dot << J.inverse()*(-v1.cross(v2) + T - Td - Tg); //temp // include model

        tau_vec_b = np.array([0,0,tau])
        total_force = quat_apply_rot(q,tau_vec_b) + f_drag
        acc_w = np.array([0,0,-g]) + total_force/m

        # Dynamic model
        p_dot = v
        v_dot = acc_w
        q_dot = quaternion_derivative(q,w)
        w_dot = (1/J)*(J*np.cross(w,w) + T + T_drag)

        # Model integration
        dt = loop_interval

        p = p + p_dot*dt
        v = v + v_dot*dt
        q = q + q_dot*dt
        w = w + w_dot*dt

        # Quaternion renormalization
        q = normalize(q)



        acc = SENS.get_acc(total_force,m)
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
            PX4.send_rc_commands(1500,1500,1500,1500)
            last_time_rc = t

        
        



        # Increment iteration count
        iteration += 1
        if iteration % 100 == 0:
            print("Iteration:", iteration)
            print("  pos: ", p)
            print("  vel: ", v)
            print(" quat: ", q)
            print("omega: ", w)
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
q_dot = quaternion_derivative(q, w)
print("Quaternion derivative:", q_dot)