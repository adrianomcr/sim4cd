#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Useful mathematical operations

import numpy as np
import time
from math import pi,sqrt,sin,cos,tan,asin,atan2

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
    """
    Return the conjugate of a quaternion

    Parameters:
        q_in (numpy.ndarray): Input quaternion [qw, qx, qy, qz].

    Returns:
        q_conj (numpy.ndarray): The conjugate of q, [qw, -qx, -qy, -qz]
    """
    #Description:
    #Return the conjugate of a quaternion

    q_conj = -q_in
    q_conj[0] = q_in[0]

    return q_conj


def quat_mult(q1, q2):
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
    """
    Apply the rotation represented by a quaternion to a vector.

    Parameters:
        q_in (numpy.ndarray): Quaternion [qw, qx, qy, qz].
        u_in (numpy.ndarray): Vector to which the rotation q_in will be applied to

    Returns:
        v (numpy.ndarray): Result of the application of q_in to u_in
    """

    u = np.array([0, u_in[0], u_in[1], u_in[2]])
    q = q_in
    q_conj = quat_conj(q_in)

    v = quat_mult(quat_mult(q,u),q_conj)
    v = v[1:4]

    return v


def inv_pose_pq(p1,q1):
    """
    Inverse the pose represented by a position and a quaternion. As if a homogeneous matrix H_1^0 is computed from inv(H_0^1).

    Parameters:
        p1 (numpy.ndarray): Position (z, y, z) of the input pose to be inverted.
        q1 (numpy.ndarray): Quaternion (qw, qz, qy, qz) of the input pose to be inverted.

    Returns:
        p2 (numpy.ndarray): Position (z, y, z) of the inverse of the input pose.
        q2 (numpy.ndarray): Quaternion (qw, qz, qy, qz) of the inverse of the input pose.
    """

    q2 = quat_conj(q1)
    p2 = -quat_apply_rot(q2,p1)

    return p2, q2


def mult_pose_pq(p1,q1,p2,q2):
    """
    Pose resulted by the "addition" of two poses. As in the homogeneous matrix operation H_2^0 = H_1^0 * H_2^1.

    Parameters:
        p1 (numpy.ndarray): First position (z, y, z).
        q1 (numpy.ndarray): First quaternion (qw, qz, qy, qz).
        p2 (numpy.ndarray): Second position (z, y, z).
        q2 (numpy.ndarray): Second quaternion (qw, qz, qy, qz).

    Returns:
        p3 (numpy.ndarray): Resultant position (z, y, z).
        q3 (numpy.ndarray): Resultant quaternion (qw, qz, qy, qz).
    """

    q3 = quat_mult(q1,q2)
    p3 = quat_apply_rot(q1,p2) + p1

    return p3, q3


def normalize(u, abs_value=1.0):
    """
    Normalize a vector

    Parameters:
        u (numpy.ndarray): Vector to be normalized to the norm abs_value
        abs_value (float): Norm of the normalized vector

    Returns:
        (numpy.ndarray): Normalized (to the norm abs_value) version of u
    """

    return abs_value*u/norm(u)


def norm(u):
    """
    Return the norm of the vector u whose norm will be computed

    Parameters:
        u (numpy.ndarray): Vector whose norm will be computed

    Returns:
        (float): Euclidean norm of the vector u
    """

    return np.linalg.norm(u)


def inv(M):
    """
    Return the inverse of the matrix

    Parameters:
        M (numpy.ndarray nxn): Square matrix

    Returns:
        (numpy.ndarray nxn): Inverse of the matrix M
    """

    return np.linalg.inv(M)


def mean(u):
    """
    Return the mean value of the elements in the vector u

    Parameters:
        u (numpy.ndarray / list): Vector whose mean will be computed

    Returns:
        (float): Mean value of the elements of vector u
    """

    return np.array(u).mean()


def quat2rotm(q):
    """
    Converts quaternion to rotation matrix

    Parameters:
        q (numpy.ndarray): Input quaternion in the form [qw, qx, qy, qz]

    Returns:
        R (numpy.ndarray): Rotation matrix equivalent to the quaternion q
    """

    R = np.array([[1-2*(q[2]*q[2]+q[3]*q[3]), 2*(q[1]*q[2]-q[3]*q[0]), 2*(q[1]*q[3]+q[2]*q[0])],
                  [2*(q[1]*q[2]+q[3]*q[0]), 1-2*(q[1]*q[1]+q[3]*q[3]), 2*(q[2]*q[3]-q[1]*q[0])],
                  [2*(q[1]*q[3]-q[2]*q[0]), 2*(q[2]*q[3]+q[1]*q[0]), 1-2*(q[1]*q[1]+q[2]*q[2])]]) #this was checked on matlab

    return R


def quat2rpy(q):
    """Convert a quaternion to Euler angles

    Args:
        q (numpy.array): Quaternion in the form [qw,qx,qy,qz]

    Returns:
        rpy (numpy.array): Vector with the Euler angles in the form [roll, pitch, yaw]
    """
    theta = asin(-2 * (q[1] * q[3] - q[0] * q[2]))
    psi = atan2(2 * (q[0] * q[3] + q[1] * q[2]), (q[0] ** 2 + q[1] ** 2 - q[2] ** 2 - q[3] ** 2))
    phi = atan2(2 * (q[0] * q[1] + q[2] * q[3]), (q[0] ** 2 - q[1] ** 2 - q[2] ** 2 + q[3] ** 2))

    rpy = np.array([phi, theta, psi])

    return rpy