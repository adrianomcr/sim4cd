#!/usr/bin/env python3

import rospy
from nav_msgs.msg import Odometry
import socket
import time
from tf.transformations import euler_from_quaternion
import sim4cd.math_utils as MU

def send_command(command, host='127.0.0.1', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))


class CameraController:
    def __init__(self):
        # Initialize ROS node
        rospy.init_node('camera_controller', anonymous=True)

        # Subscribe to Odometry topic
        rospy.Subscriber('/drone/gt', Odometry, self.odom_callback)

        # Initialize pose values
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.q_c_w = [1,0,0,0]

        time.sleep(6)

    def odom_callback(self, msg):
        # Extract position
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.position.z

        # Extract orientation and convert to Euler angles
        orientation_q = msg.pose.pose.orientation
        # quaternion = (orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w)
        # self.roll, self.pitch, self.yaw = euler_from_quaternion(quaternion)
        q_d_w = [orientation_q.w, orientation_q.x, orientation_q.y, orientation_q.z]
        # rpy = MU.quat2rpy(q_d_w)
        q_c_d = [-0.5, 0.5, -0.5, 0.5]
        q_c_w = MU.quat_mult(q_d_w, q_c_d)
        rpy = MU.quat2rpy(q_c_w)
        self.roll = rpy[0]
        self.pitch = rpy[1]
        self.yaw = rpy[2]
        self.q_c_w = q_d_w

    def run(self):
        rate = rospy.Rate(30)  # 30 Hz

        delta = 0
        while not rospy.is_shutdown():
            # Set the position of the camera
            # send_command(f"SET_POSITION {self.x},{self.y},{self.z}")
            # send_command(f"SET_POSITION {self.y},{self.z},{self.x}")
            # send_command(f"SET_POSITION {0},{6},{-16}")
            send_command(f"SET_POSITION {-self.y},{self.z},{self.x}")

            # Convert roll, pitch, yaw to degrees and set the rotation of the camera
            #send_command(f"SET_ROTATION {self.yaw * 180 / 3.14159},{-self.pitch * 180 / 3.14159},{-self.roll * 180 / 3.14159}")


            delta = delta + 1/3000
            # send_command(f"SET_QUAT {1},{0},{0},{0}")
            send_command(f"SET_QUAT {self.q_c_w[0]},{self.q_c_w[2]},{-self.q_c_w[3]},{-self.q_c_w[1]}")

            rospy.loginfo(f"Position: {self.x}, {self.y}, {self.z}")
            rospy.loginfo(f"Rotation: {self.roll}, {self.pitch}, {self.yaw}")
            
            rate.sleep()


if __name__ == "__main__":
    try:
        controller = CameraController()
        controller.run()
    except rospy.ROSInterruptException:
        pass
