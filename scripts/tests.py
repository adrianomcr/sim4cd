#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Drone dymanics, drag force, effects lyke gyroscopic effect, etc ...




import numpy as np
import time
from math import pi,sqrt,sin,cos,tan

import math_utils as MU




q1 = np.array([0,1,0,0])
q1 = MU.normalize(q1)


wb = np.array([0,0,1])
q_dot = MU.quaternion_derivative(q1, wb)


v = MU.normalize(wb)
dt = 0.01
theta = MU.norm(wb)*dt
qdelta = [cos(theta/2),v[0]*sin(theta/2),v[1]*sin(theta/2),v[2]*sin(theta/2)]
q2 = MU.quat_mult(q1,qdelta)

print("q1:", q1)
print("q2:", q2)
print("wb:", wb)

print("\nR1:\n", MU.quat2rotm(q1))
print("R2:\n", MU.quat2rotm(q2),"\n")

print("Quaternion derivative analytic:", q_dot)
print("Quaternion derivative numeric :", (q2-q1)/dt)
print("Max error:                    ", max(abs((q2-q1)/dt-q_dot)))





q1 = np.array([1,2,3,4])
q1 = MU.normalize(q1)
q2 = MU.quat_conj(q1)
print("q1   : ", q1)
print("q2   : ", q2)
print("q1*q2: ", MU.quat_mult(q1,q2))

# # Example usage:
# q = np.array([0.707, 0.0, 0.0, 0.707])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
# # q = np.array([1.0, 0.0, 0.0, 0.0])  # Example quaternion [1, 0, 0, 0] (identity quaternion)
# w = np.array([0.0, 0.1, 0.0])      # Example angular velocity [0.1, 0.2, 0.3]
# q_dot = MU.quaternion_derivative(q, w)
# print("Quaternion derivative:", q_dot)


# q_in = q = np.array([q[0],q[1],q[2],q[3]])
# w_in = q = np.array([w[0],w[1],w[2]])
# aaa = MU.d_quat_from_omega(q_in,w_in)
#print("Quaternion derivative:", aaa)