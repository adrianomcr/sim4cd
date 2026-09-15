#!/usr/bin/env python3

# Bridge between the sim4cd state stream and the camera inside the Unity player.
#
# sim4cd_main.py publishes the vehicle state as JSON on a ZeroMQ PUB socket.
# CameraController.cs listens on a TCP socket inside the Unity player and reads
# one message per connection, so a new connection is opened for every update.

import argparse
import json
import socket
import sys
import time

import zmq


def to_unity_position(pose):
    """Convert a position from the simulator frame to the Unity frame

    Args:
        pose (list): Simulator state in the form [x, y, z, roll, pitch, yaw]

    Returns:
        position (tuple): Position in the form [x, y, z], in the Unity frame
    """
    # Unity is left handed with y up, the simulator is right handed with z up
    return (-pose[1], pose[2], pose[0])


def to_unity_quaternion(quat):
    """Convert an attitude from the simulator frame to the Unity frame

    Args:
        quat (list): Attitude of the vehicle in the form [qw, qx, qy, qz]

    Returns:
        quaternion (tuple): Attitude in the form [qw, qx, qy, qz], in the Unity frame
    """
    return (quat[0], quat[2], -quat[3], -quat[1])


class unity_camera_bridge(object):
    """
    Forwards the simulated vehicle pose to the Unity camera controller
    """

    def __init__(self, state_endpoint, unity_host, unity_port, rate):
        """
        Constructor for the unity_camera_bridge class

        Parameters:
            state_endpoint (str): ZeroMQ endpoint published by sim4cd_main.py
            unity_host (str): Host the Unity player listens on
            unity_port (int): TCP port the Unity player listens on
            rate (float): Frequency at which the camera pose is sent [Hz]
        """

        self.unity_host = unity_host
        self.unity_port = unity_port
        self.period = 1.0 / rate

        # Latest state received from the simulator
        self.pose = None
        self.quat = None

        # Create a ZeroMQ context
        self.context = zmq.Context()
        # Create a SUB socket
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(state_endpoint)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all messages

        print(f"\33[94m[unity_bridge] Reading the vehicle state from {state_endpoint}\33[0m")
        print(f"\33[94m[unity_bridge] Sending the camera pose to {unity_host}:{unity_port}\33[0m")


    def send_command(self, command):
        """
        Send a single command to the Unity camera controller

        Parameters:
            command (str): Command string understood by CameraController.cs

        Returns:
            sent (bool): True if the command reached the Unity player
        """

        try:
            with socket.create_connection((self.unity_host, self.unity_port), timeout=0.5) as s:
                s.sendall(command.encode('utf-8'))
            return True
        except OSError:
            # The Unity player is not up yet, or was closed
            return False


    def read_state(self):
        """
        Drain the state socket so that only the most recent state is kept
        """

        while True:
            try:
                message = self.socket.recv_string(flags=zmq.NOBLOCK)
            except zmq.Again:
                return
            state = json.loads(message)
            self.pose = state.get('pose', self.pose)
            self.quat = state.get('quat', self.quat)


    def run(self):
        """
        Bridge main loop function
        """

        connected = False
        next_send = time.time()
        while True:
            self.read_state()

            if self.pose is None or self.quat is None or time.time() < next_send:
                time.sleep(0.005)
                continue
            next_send = time.time() + self.period

            x, y, z = to_unity_position(self.pose)
            qw, qx, qy, qz = to_unity_quaternion(self.quat)
            # CameraController.cs splits a single message on '|', so both commands
            # are sent together to keep the position and the attitude in sync
            sent = self.send_command(f"SET_POSITION {x},{y},{z}|SET_QUAT {qw},{qx},{qy},{qz}")

            if sent != connected:
                connected = sent
                if connected:
                    print("\33[92m[unity_bridge] Connected to the Unity player\33[0m")
                else:
                    print("\33[93m[unity_bridge] Waiting for the Unity player\33[0m")


if __name__ == "__main__":
    """
    Unity camera bridge main function
    """

    parser = argparse.ArgumentParser(description="Forward the simulated vehicle pose to the Unity camera")
    parser.add_argument('--state-endpoint', default="tcp://localhost:5545",
                        help="ZeroMQ endpoint published by sim4cd_main.py")
    parser.add_argument('--unity-host', default="127.0.0.1",
                        help="Host the Unity player listens on")
    parser.add_argument('--unity-port', type=int, default=12345,
                        help="TCP port the Unity player listens on")
    parser.add_argument('--rate', type=float, default=30.0,
                        help="Frequency at which the camera pose is sent [Hz]")
    args = parser.parse_args()

    bridge = unity_camera_bridge(args.state_endpoint, args.unity_host, args.unity_port, args.rate)
    try:
        bridge.run()
    except KeyboardInterrupt:
        print("\33[92m[unity_bridge] Exiting\33[0m")
        sys.exit(0)
