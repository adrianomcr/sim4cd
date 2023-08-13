#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Useful mathematical operations

import numpy as np
import time
from math import pi,sqrt,sin,cos,tan




def quat_mult(q1,q2):
	#Description:
	#Quaternion multiplication q1 x q2
	
	a1 = q1[0]
	b1 = q1[1]
	c1 = q1[2]
	d1 = q1[3]
	a2 = q2[0]
	b2 = q2[1]
	c2 = q2[2]
	d2 = q2[3]

	q = np.array([a1*a2 - b1*b2 - c1*c2 - d1*d2, 
                  a1*b2 + b1*a2 + c1*d2 - d1*c2,
                  a1*c2 - b1*d2 + c1*a2 + d1*b2,
                  a1*d2 + b1*c2 - c1*b2 + d1*a2])

	return q

# def d_quat_from_omega(q_in,w_in):
#     #Description:
#     #Compute the qaternion derivative given a angulr sepeed w
#     #ngular speed w is on th world/body???????? frame BODY!!!!!!!!!!!!!!!!!!!

#     q = [q_in[0],q_in[1],q_in[2],q_in[3]]


#     wx = w_in[0]
#     wy = w_in[1]
#     wz = w_in[2]
#     return np.array([0.5*( 0*q[0] - wx*q[1] - wy*q[2] - wz*q[3]),
#             0.5*(wx*q[0] +  0*q[1] + wz*q[2] - wy*q[3]),
#             0.5*(wy*q[0] - wz*q[1] +  0*q[2] + wx*q[3]),
#             0.5*(wz*q[0] + wy*q[1] - wx*q[2] +  0*q[3]) ])


def quaternion_derivative(q, w):
    """
    Calculate the derivative of a quaternion given a quaternion and an angular velocity.

    Parameters:
        q (numpy.ndarray): Input quaternion [qw, qx, qy, qz].
        w (numpy.ndarray): Angular velocity in the body frame [wx, wy, wz].

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

    #Description:
    #Return the conjugate of a quaternion

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

    #v = quaternion_multiply(q,quaternion_multiply(u,q_conj))
    v = quaternion_multiply(quaternion_multiply(q,u),q_conj)

    return v[1:4]


def normalize(u, abs_value=1.0):

    #Description:
    #The normalized version of the vector u

    return abs_value*u/np.linalg.norm(u)


def norm(u):

    #Description:
    #Return the norm of the vector u

    return np.linalg.norm(u)




def quat2rotm(q):
	#Description:
	#Converts quaternion to rotation matrix
	#Quaternion: qw, qx, qy, qz

	qw = q[0]
	qx = q[1]
	qy = q[2]
	qz = q[3]

	Rot = np.array([[1-2*(qy*qy+qz*qz), 2*(qx*qy-qz*qw), 2*(qx*qz+qy*qw)],
                    [2*(qx*qy+qz*qw), 1-2*(qx*qx+qz*qz), 2*(qy*qz-qx*qw)],
		            [2*(qx*qz-qy*qw), 2*(qy*qz+qx*qw), 1-2*(qx*qx+qy*qy)]]) #this was checked on matlab
			
	return Rot














# Example usage:
q = np.array([1.0, 0.0, 0.0, 0.0])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
w = np.array([0.1, 0.2, 0.3])      # Example angular velocity [0.1, 0.2, 0.3]
q_dot = quaternion_derivative(q, w)
print("Quaternion derivative:", q_dot)
