#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# ROS support to visualize the simulation on RViz and publish the drones state as ROS topics

import rospy
from geometry_msgs.msg import Twist, Pose, Point, Quaternion
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker, MarkerArray
from math import pi, cos, sin

import math_utils as MU


class drone_show(object):
    """
    Drone state and markers publisher
    """

    def __init__(self):

        # Publishers
        self.pub_gt = None
        self.pub_pose = None
        self.pub_odom = None
        self.pub_rviz_robot = None

        self.init_node()


    def init_node(self):
        """
        Initialize ROS related variables
        """
        rospy.init_node("drone_sim")

        self.robot_arm_len = 0.3 # TODO: config param

        # self.history = []
        # self.history.append([self.state[0], self.state[1], self.state[2]])

        # publishers
        self.pub_pose = rospy.Publisher("/drone/pose", Pose, queue_size=1)
        self.pub_gt = rospy.Publisher("/drone/gt", Odometry, queue_size=1)
        self.pub_odom = rospy.Publisher("/drone/odom", Odometry, queue_size=1)
        self.pub_rviz_robot = rospy.Publisher("/drone/robot", MarkerArray, queue_size=1)
        # self.pub_rviz_hist = rospy.Publisher("/drone/history", MarkerArray, queue_size=1)


    def update_ros_info(self,p,q,vw,omega,p0,q0):
        """
        Publish information as ROS topics

        Parameters:
            p (numpy.ndarray): Position vector [x, y, z]
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
            vw (numpy.ndarray): World velocity vector [vx, vy, vz]
            omega (numpy.ndarray): Body angular velocity [wx, wy, wz]
            p0 (numpy.ndarray): Initial position vector [x, y, z]
            q0 (numpy.ndarray): Initial orientation quaternion [qw, qx, qy, qz]
        """

        # Compute the body velocity
        vb = MU.quat_apply_rot(MU.quat_conj(q),vw)

        # Compute odometry 
        p_odom, q_odom = self.compute_odometry(p,q,p0,q0)


        #Publish groung truth (odometry) topic
        self.send_odom(self.pub_odom, p_odom,q_odom,vb,omega)
        #Publish groung truth (odometry) topic
        self.send_odom(self.pub_gt, p,q,vb,omega)
        #Publish pose topic
        self.send_pose(p,q)
        #Publish marker array topic that represents the drone (visualization n RViz)
        self.send_marker(p,q)



    def compute_odometry(self,p,q,p0,q0):
        """
        Compute the odometry that has the starting pose as the origin

        Parameters:
            p (numpy.ndarray): Current position vector [x, y, z] in the world frame
            q (numpy.ndarray): Current orientation quaternion [qw, qx, qy, qz] in the world frame
            p0 (numpy.ndarray): Initial position vector [x, y, z] in the world frame
            q0 (numpy.ndarray): Initial orientation quaternion [qw, qx, qy, qz] in the world frame

        Returns:
            p_odom (numpy.ndarray): Current position ([x, y, z]) odometry with respect to the initial pose
            q_odom (numpy.ndarray): Current orientation ([qw, qx, qy, qz]) odometry with respect to the initial pose
        """

        q_odom = MU.quat_mult(MU.quat_conj(q0),q)

        p_w_d0 = - MU.quat_apply_rot(MU.quat_conj(q), p0)

        p_odom = MU.quat_apply_rot(MU.quat_conj(q0),p) + p_w_d0

        return p_odom, q_odom 



    def send_odom(self,pub,p,q,vb,omega):
        """
        Publish ROS odometry topic

        Parameters:
            pub (rospy.topics.Publisher): Publisher to a geometry_msgs/Odometry  topic
            p (numpy.ndarray): Position vector [x, y, z]
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
            vb (numpy.ndarray): Body velocity vector [vx, vy, vz]
            omega (numpy.ndarray): Body angular velocity [wx, wy, wz]
        """

        odom_msg = Odometry()

        #Publish robots odometry
        odom_msg.header.stamp = rospy.Time.now()
        odom_msg.header.frame_id = "drone"
        odom_msg.child_frame_id = "world"
        #
        odom_msg.pose.pose.position.x = p[0]
        odom_msg.pose.pose.position.y = p[1]
        odom_msg.pose.pose.position.z = p[2]
        odom_msg.pose.pose.orientation.x = q[1]
        odom_msg.pose.pose.orientation.y = q[2]
        odom_msg.pose.pose.orientation.z = q[3]
        odom_msg.pose.pose.orientation.w = q[0]
        #
        odom_msg.twist.twist.linear.x = vb[0]
        odom_msg.twist.twist.linear.y = vb[1]
        odom_msg.twist.twist.linear.z = vb[2]
        odom_msg.twist.twist.angular.x = omega[0]
        odom_msg.twist.twist.angular.y = omega[1]
        odom_msg.twist.twist.angular.z = omega[2]

        pub.publish(odom_msg)


    def send_pose(self,p,q):
        """
        Publish ROS pose topic

        Parameters:
            p (numpy.ndarray): Position vector [x, y, z]
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
        """

        pose_msg = Pose()

        #Publish robots pose
        pose_msg.position.x = p[0]
        pose_msg.position.y = p[1]
        pose_msg.position.z = p[2]
        pose_msg.orientation.x = q[1]
        pose_msg.orientation.y = q[2]
        pose_msg.orientation.z = q[3]
        pose_msg.orientation.w = q[0]

        self.pub_pose.publish(pose_msg)


    def send_marker(self,p,q):
        """
        Construct and publish ROS marker array topic that represents the drones body

        Parameters:
            p (numpy.ndarray): Position vector [x, y, z]
            q (numpy.ndarray): Orientation quaternion [qw, qx, qy, qz]
        """

        robot_marker_array = MarkerArray()

        # Define marker representing the drones body
        marker_robot = Marker()
        marker_robot.header.frame_id = "world"
        marker_robot.header.stamp = rospy.Time.now()
        marker_robot.id = 0
        marker_robot.type = marker_robot.CUBE
        marker_robot.action = marker_robot.ADD
        marker_robot.lifetime = rospy.Duration(3)
        # Size of robots body
        marker_robot.scale.x = self.robot_arm_len/2.0
        marker_robot.scale.y = self.robot_arm_len/2.0
        marker_robot.scale.z = self.robot_arm_len/6.0
        # Color of the marker
        marker_robot.color.a = 0.5
        marker_robot.color.r = 0.0
        marker_robot.color.g = 0.0
        marker_robot.color.b = 0.0
        # Position of the marker
        marker_robot.pose.position.x = p[0]
        marker_robot.pose.position.y = p[1]
        marker_robot.pose.position.z = p[2]
        # Orientation of the marker
        marker_robot.pose.orientation.x = q[1]
        marker_robot.pose.orientation.y = q[2]
        marker_robot.pose.orientation.z = q[3]
        marker_robot.pose.orientation.w = q[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_robot)


        # Define marker representing the drones arms in one diagonal
        q0 = [cos((pi/4)/2),0,0,sin((pi/4)/2)]
        qarm1 = MU.quat_mult(q,q0)
        marker_arm1 = Marker()
        marker_arm1.header.frame_id = "world"
        marker_arm1.header.stamp = rospy.Time.now()
        marker_arm1.id = 1
        marker_arm1.type = marker_arm1.CUBE
        marker_arm1.action = marker_arm1.ADD
        marker_arm1.lifetime = rospy.Duration(3)
        # Size of arms
        marker_arm1.scale.x = 2*self.robot_arm_len
        marker_arm1.scale.y = self.robot_arm_len/10.0
        marker_arm1.scale.z = self.robot_arm_len/10.0
        # Color of the marker
        marker_arm1.color.a = 0.9
        marker_arm1.color.r = 0.0
        marker_arm1.color.g = 0.0
        marker_arm1.color.b = 0.0
        # Position of the marker
        marker_arm1.pose.position.x = p[0]
        marker_arm1.pose.position.y = p[1]
        marker_arm1.pose.position.z = p[2]
        # Orientation of the marker
        marker_arm1.pose.orientation.x = qarm1[1]
        marker_arm1.pose.orientation.y = qarm1[2]
        marker_arm1.pose.orientation.z = qarm1[3]
        marker_arm1.pose.orientation.w = qarm1[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_arm1)


        # Define marker representing the drones arms in the other diagonal
        q0 = [cos((pi/4)/2),0,0,sin((pi/4)/2)]
        qarm2 = MU.quat_mult(q,q0)
        marker_arm2 = Marker()
        marker_arm2.header.frame_id = "world"
        marker_arm2.header.stamp = rospy.Time.now()
        marker_arm2.id = 2
        marker_arm2.type = marker_arm2.CUBE
        marker_arm2.action = marker_arm2.ADD
        marker_arm2.lifetime = rospy.Duration(3)
        # Size of arms
        marker_arm2.scale.x = self.robot_arm_len/10.0
        marker_arm2.scale.y = 2*self.robot_arm_len
        marker_arm2.scale.z = self.robot_arm_len/10.0
        # Color of the marker
        marker_arm2.color.a = 0.9
        marker_arm2.color.r = 0.0
        marker_arm2.color.g = 0.0
        marker_arm2.color.b = 0.0
        # Position of the marker
        marker_arm2.pose.position.x = p[0]
        marker_arm2.pose.position.y = p[1]
        marker_arm2.pose.position.z = p[2]
        # Orientation of the marker
        marker_arm2.pose.orientation.x = qarm2[1]
        marker_arm2.pose.orientation.y = qarm2[2]
        marker_arm2.pose.orientation.z = qarm2[3]
        marker_arm2.pose.orientation.w = qarm2[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_arm2)


        # Define marker representing one of the drones spinning blades
        d_arm = 0.7071067811865476*self.robot_arm_len
        helix_d = self.robot_arm_len*0.8
        helix_h = self.robot_arm_len/15.0
        h1_pos_b = [d_arm,d_arm,self.robot_arm_len/10.0]
        h1_pos_w = MU.quat_apply_rot(q,h1_pos_b)
        marker_h1 = Marker()
        marker_h1.header.frame_id = "world"
        marker_h1.header.stamp = rospy.Time.now()
        marker_h1.id = 3
        marker_h1.type = marker_h1.CYLINDER
        marker_h1.action = marker_h1.ADD
        marker_h1.lifetime = rospy.Duration(3)
        # Size of disk
        marker_h1.scale.x = helix_d
        marker_h1.scale.y = helix_d
        marker_h1.scale.z = helix_h
        # Color of the marker
        marker_h1.color.a = 0.3
        marker_h1.color.r = 0.5
        marker_h1.color.g = 0.5
        marker_h1.color.b = 0.5
        # Position of the marker
        marker_h1.pose.position.x = p[0] + h1_pos_w[0]
        marker_h1.pose.position.y = p[1] + h1_pos_w[1]
        marker_h1.pose.position.z = p[2] + h1_pos_w[2]
        # Orientation of the marker
        marker_h1.pose.orientation.x = q[1]
        marker_h1.pose.orientation.y = q[2]
        marker_h1.pose.orientation.z = q[3]
        marker_h1.pose.orientation.w = q[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_h1)


        # Define marker representing one of the drones spinning blades
        h2_pos_b = [-d_arm,d_arm,self.robot_arm_len/10.0]
        h2_pos_w = MU.quat_apply_rot(q,h2_pos_b)
        marker_h2 = Marker()
        marker_h2.header.frame_id = "world"
        marker_h2.header.stamp = rospy.Time.now()
        marker_h2.id = 4
        marker_h2.type = marker_h2.CYLINDER
        marker_h2.action = marker_h2.ADD
        marker_h2.lifetime = rospy.Duration(3)
        # Size of disk
        marker_h2.scale.x = helix_d
        marker_h2.scale.y = helix_d
        marker_h2.scale.z = helix_h
        # Color of the marker
        marker_h2.color.a = 0.3
        marker_h2.color.r = 0.5
        marker_h2.color.g = 0.5
        marker_h2.color.b = 0.5
        # Position of the marker
        marker_h2.pose.position.x = p[0] + h2_pos_w[0]
        marker_h2.pose.position.y = p[1] + h2_pos_w[1]
        marker_h2.pose.position.z = p[2] + h2_pos_w[2]
        # Orientation of the marker
        marker_h2.pose.orientation.x = q[1]
        marker_h2.pose.orientation.y = q[2]
        marker_h2.pose.orientation.z = q[3]
        marker_h2.pose.orientation.w = q[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_h2)


        # Define marker representing one of the drones spinning blades
        h3_pos_b = [-d_arm,-d_arm,self.robot_arm_len/10.0]
        h3_pos_w = MU.quat_apply_rot(q,h3_pos_b)
        marker_h3 = Marker()
        marker_h3.header.frame_id = "world"
        marker_h3.header.stamp = rospy.Time.now()
        marker_h3.id = 5
        marker_h3.type = marker_h3.CYLINDER
        marker_h3.action = marker_h3.ADD
        marker_h3.lifetime = rospy.Duration(3)
        # Size of disk
        marker_h3.scale.x = helix_d
        marker_h3.scale.y = helix_d
        marker_h3.scale.z = helix_h
        # Color of the marker
        marker_h3.color.a = 0.3
        marker_h3.color.r = 0.5
        marker_h3.color.g = 0.5
        marker_h3.color.b = 0.5
        # Position of the marker
        marker_h3.pose.position.x = p[0] + h3_pos_w[0]
        marker_h3.pose.position.y = p[1] + h3_pos_w[1]
        marker_h3.pose.position.z = p[2] + h3_pos_w[2]
        # Orientation of the marker
        marker_h3.pose.orientation.x = q[1]
        marker_h3.pose.orientation.y = q[2]
        marker_h3.pose.orientation.z = q[3]
        marker_h3.pose.orientation.w = q[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_h3)


        # Define marker representing one of the drones spinning blades
        h4_pos_b = [d_arm,-d_arm,self.robot_arm_len/10.0]
        h4_pos_w = MU.quat_apply_rot(q,h4_pos_b)
        marker_h4 = Marker()
        marker_h4.header.frame_id = "world"
        marker_h4.header.stamp = rospy.Time.now()
        marker_h4.id = 6
        marker_h4.type = marker_h4.CYLINDER
        marker_h4.action = marker_h4.ADD
        marker_h4.lifetime = rospy.Duration(3)
        # Size of disk
        marker_h4.scale.x = helix_d
        marker_h4.scale.y = helix_d
        marker_h4.scale.z = helix_h
        #Color of the marker
        marker_h4.color.a = 0.3
        marker_h4.color.r = 0.5
        marker_h4.color.g = 0.5
        marker_h4.color.b = 0.5
        # Position of the marker
        marker_h4.pose.position.x = p[0] + h4_pos_w[0]
        marker_h4.pose.position.y = p[1] + h4_pos_w[1]
        marker_h4.pose.position.z = p[2] + h4_pos_w[2]
        # Orientation of the marker
        marker_h4.pose.orientation.x = q[1]
        marker_h4.pose.orientation.y = q[2]
        marker_h4.pose.orientation.z = q[3]
        marker_h4.pose.orientation.w = q[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_h4)


        # Define marker representing the drone heading
        marker_arrow = Marker()
        marker_arrow.header.frame_id = "world"
        marker_arrow.header.stamp = rospy.Time.now()
        marker_arrow.id = 7
        marker_arrow.type = marker_arrow.ARROW
        marker_arrow.action = marker_arrow.ADD
        marker_arrow.lifetime = rospy.Duration(3)
        # Size of arrow
        marker_arrow.scale.x = self.robot_arm_len*1.0
        marker_arrow.scale.y = self.robot_arm_len/5.0
        marker_arrow.scale.z = self.robot_arm_len/5.0
        # Color of the marker
        marker_arrow.color.a = 0.99
        marker_arrow.color.r = 0.0
        marker_arrow.color.g = 0.0
        marker_arrow.color.b = 1.0
        # Position of the marker
        marker_arrow.pose.position.x = p[0]
        marker_arrow.pose.position.y = p[1]
        marker_arrow.pose.position.z = p[2]
        # Orientation of the marker
        marker_arrow.pose.orientation.x = q[1]
        marker_arrow.pose.orientation.y = q[2]
        marker_arrow.pose.orientation.z = q[3]
        marker_arrow.pose.orientation.w = q[0]
        # Append marker to array
        robot_marker_array.markers.append(marker_arrow)

        # Publish marker array
        self.pub_rviz_robot.publish(robot_marker_array)
