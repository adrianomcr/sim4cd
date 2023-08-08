#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Drone dymanics, drag force, effects lyke gyroscopic effect, etc ...




import numpy as np
import time


def d_quat_from_omega(q_in,w_in):
    #Description:
    #Compute the qaternion derivative given a angulr sepeed w
    #ngular speed w is on th world/body???????? frame

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
        w (numpy.ndarray): Angular velocity in the world frame [wx, wy, wz].

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

# Example usage:
q = np.array([0.707, 0.0, 0.0, 0.707])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
# q = np.array([1.0, 0.0, 0.0, 0.0])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
w = np.array([0.0, 0.1, 0.0])      # Example angular velocity [0.1, 0.2, 0.3]
q_dot = quaternion_derivative(q, w)
print("Quaternion derivative:", q_dot)


q_in = [[q[0]],[q[1]],[q[2]],[q[3]]]
w_in = [[w[0]],[w[1]],[w[2]]]
aaa = d_quat_from_omega(q_in,w_in)
print("Quaternion derivative:", aaa)