#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Communication with the PX4 simulated software by using mavlink



import time
import atexit
from random import random
from pymavlink import mavutil
from math import log
from constants import *


class px4_connection:
    """
    Class for the connection of the simulator with PX4
    """

    def __init__(self, protocol='tcpin', host='localhost', port='4560'):
        """
        Constructor for the px4_connection class
        """

        # Input parameters for PX4 connection
        self.protocol = protocol
        self.host = host
        self.port = port

        # Connection object
        self.vehicle = False

        # Bot time
        self.t_boot__us = False


    def connect(self):
        """
        Stablish a connection with PX4 on the port dedicated for the simulator
        """

        # Try to connect to PX4 on tcp, in localhost, at port 4560
        print("Waiting to connect...")
        self.vehicle = mavutil.mavlink_connection('tcpin:localhost:4560')

        # Wait for a command long from PX4
        msg = self.vehicle.recv_match(blocking = True)
        if msg.get_type() != "COMMAND_LONG":
            raise Exception("error")

        # Wait for a heart beat from PX4
        msg = self.vehicle.recv_match(blocking = True)
        if msg.get_type() != "HEARTBEAT":
            raise Exception("error")

        # Save the boot time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)
        self.t_boot__us  = int(t_abs__us - 30e6)
        
        # Return the connection object
        return self.vehicle


    def send_system_time(self):
        """
        Send system time information to PX4
        """
        
        # Get current time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)

        # Compute time since boot
        since_boot__us = t_abs__us - self.t_boot__us
        since_boot__ms = int(since_boot__us / 1000)
        
        # Send SYSTEM_TIME message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.system_time_send(
                time_unix_usec = t_abs__us,       # Timestamp (UNIX epoch time). [us] (type:uint64_t)
                time_boot_ms = since_boot__ms,    # Timestamp (time since system boot). [ms] (type:uint32_t)
            )


    def send_heart_beat(self):
        """
        Send heart beat information to PX4
        """

        # Send HEARTBEAT message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.heartbeat_send(
                type = 2,               # Vehicle or component type. For a flight controller component the vehicle type (quadrotor, helicopter, etc.). For other components the component type (e.g. camera, gimbal, etc.). This should be used in preference to component id for identifying the component type. (type:uint8_t, values:MAV_TYPE)
                autopilot = 0,          # Autopilot type / class. Use MAV_AUTOPILOT_INVALID for components that are not flight controllers. (type:uint8_t, values:MAV_AUTOPILOT)
                base_mode = 0,          # System mode bitmap. (type:uint8_t, values:MAV_MODE_FLAG)
                custom_mode = 0,        # A bitfield for use for autopilot-specific flags (type:uint32_t)
                system_status = 0,      # System status flag. (type:uint8_t, values:MAV_STATE)
                mavlink_version = 3,    # MAVLink version, not writable by user, gets added by protocol because of magic data type          , # uint8_t_mavlink_version (type:uint8_t)
            )
    


    def send_gps(self,gps):
        """
        Send GPS information to PX4

        Parameters:
            gps (dict): Dictionary with the GPS information
        """

        # Get current time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)

        # Extract GPS information from dictionary and round when necessary
        time_usec          = t_abs__us                     # Timestamp (UNIX Epoch time or time since system boot). The receiving end can infer timestamp format (since 1.1.1970 or since system boot) by checking for the magnitude of the number. [us] (type:uint64_t)
        fix_type           = 3                             # 0-1: no fix, 2: 2D fix, 3: 3D fix. Some applications will not use the value of this field unless it is at least two, so always correctly fill in the fix. (type:uint8_t)
        lat                = int(gps['i_lat__degE7'])    # Latitude (WGS84) [degE7] (type:int32_t)
        lon                = int(gps['i_lon__degE7'])    # Longitude (WGS84) [degE7] (type:int32_t)
        alt                = int(gps['i_alt__mm'])       # Altitude (MSL). Positive for up. [mm] (type:int32_t)
        eph                = int(gps['i_eph__cm'])       # GPS HDOP horizontal dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        epv                = int(gps['i_epv__cm'])       # GPS VDOP vertical dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        vel                = int(gps['i_vel__cm/s'])     # GPS ground speed. If unknown, set to: 65535 [cm/s] (type:uint16_t)
        vn                 = int(gps['i_vn__cm/s'])      # GPS velocity in north direction in earth-fixed NED frame [cm/s] (type:int16_t)
        ve                 = int(gps['i_ve__cm/s'])      # GPS velocity in east direction in earth-fixed NED frame [cm/s] (type:int16_t)
        vd                 = int(gps['i_vd__cm/s'])      # GPS velocity in down direction in earth-fixed NED frame [cm/s] (type:int16_t)
        cog                = 65535                         # Course over ground (NOT heading, but direction of movement), 0.0..359.99 degrees. If unknown, set to: 65535 [cdeg] (type:uint16_t)
        satellites_visible = 10                            # Number of satellites visible. If unknown, set to 255 (type:uint8_t)
        the_id             = 0                             # GPS ID (zero indexed). Used for multiple GPS inputs (type:uint8_t)
        yaw                = 0                             # Yaw of vehicle relative to Earth's North, zero means not available, use 36000 for north [cdeg] (type:uint16_t)
        
        # Send HIL_GPS message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.hil_gps_send(
            # self.vehicle.mav.hil_gps_encode(
                time_usec           = time_usec             ,
                fix_type            = fix_type              ,
                lat                 = lat                   ,
                lon                 = lon                   ,
                alt                 = alt                   ,
                eph                 = eph                   ,
                epv                 = epv                   ,
                vel                 = vel                   ,
                vn                  = vn                    ,
                ve                  = ve                    ,
                vd                  = vd                    ,
                cog                 = cog                   ,
                satellites_visible  = satellites_visible    ,
                id                  = the_id                ,
                yaw                 = 0                     ,
            )

        return


    def send_ground_truth(self,gt):
        """
        Send Ground Truth information to PX4

        Parameters:
            gt (dict): Dictionary with the Ground Truth information
        """

        # Get current time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)
        
        # Extract Ground Truth information from dictionary and round when necessary
        time_usec           = t_abs__us                    # Timestamp (UNIX Epoch time or time since system boot). The receiving end can infer timestamp format (since 1.1.1970 or since system boot) by checking for the magnitude of the number. [us] (type:uint64_t)
        attitude_quaternion = gt['attitude_quaternion']    # Vehicle attitude expressed as normalized quaternion in w, x, y, z order (with 1 0 0 0 being the null-rotation) (type:float)
        rollspeed           = gt['rollspeed']              # Body frame roll / phi angular speed [rad/s] (type:float)
        pitchspeed          = gt['pitchspeed']             # Body frame pitch / theta angular speed [rad/s] (type:float)
        yawspeed            = gt['yawspeed']               # Body frame yaw / psi angular speed [rad/s] (type:float)
        lat                 = int(gt['i_lat__degE7'])    # Latitude [degE7] (type:int32_t)
        lon                 = int(gt['i_lon__degE7'])    # Longitude [degE7] (type:int32_t)
        alt                 = int(gt['i_alt__mm'])       # Altitude [mm] (type:int32_t)
        vx                  = int(gt['vx'])              # Ground X Speed (Latitude) [cm/s] (type:int16_t)
        vy                  = int(gt['vy'])              # Ground Y Speed (Longitude) [cm/s] (type:int16_t)
        vz                  = int(gt['vz'])              # Ground Z Speed (Altitude) [cm/s] (type:int16_t)
        ind_airspeed        = int(gt['ind_airspeed'])    # Indicated airspeed [cm/s] (type:uint16_t)
        true_airspeed       = int(gt['true_airspeed'])   # True airspeed [cm/s] (type:uint16_t)
        xacc                = int(gt['xacc'])            # X acceleration [mG] (type:int16_t)
        yacc                = int(gt['yacc'])            # Y acceleration [mG] (type:int16_t)
        zacc                = int(gt['zacc'])            # Z acceleration [mG] (type:int16_t)

        # Send HIL_STATE_QUATERNION message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.hil_state_quaternion_send(
            # self.vehicle.mav.hil_state_quaternion_encode(
                time_usec           = time_usec             ,
                attitude_quaternion = attitude_quaternion   ,
                rollspeed           = rollspeed             ,
                pitchspeed          = pitchspeed            ,
                yawspeed            = yawspeed              ,
                lat                 = lat                   ,
                lon                 = lon                   ,
                alt                 = alt                   ,
                vx                  = vx                    ,
                vy                  = vy                    ,
                vz                  = vz                    ,
                ind_airspeed        = ind_airspeed          ,
                true_airspeed       = true_airspeed         ,
                xacc                = xacc                  ,
                yacc                = yacc                  ,
                zacc                = zacc                  ,
            )


    def send_sensors(self,acc,gyro,mag,bar):
        """
        Send sensor measurement information to PX4

        Parameters:
            acc (numpy.ndarray): Acceleration measured by the accelerometer
            gyro (numpy.ndarray): Angular velocity measured by the gyro
            mag (numpy.ndarray): Magnetic field measured by the magnetometer
            bar (numpy.ndarray): Barometric pressure measured by the barometer
        """

        # Get current time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)
        
        # Get all the information to populate the sensor message
        time_usec           = t_abs__us                       # Timestamp (UNIX Epoch time or time since system boot). The receiving end can infer timestamp format (since 1.1.1970 or since system boot) by checking for the magnitude of the number. [us] (type:uint64_t)
        xacc                = acc[0]                          # X acceleration [m/s/s] (type:float)
        yacc                = acc[1]                          # Y acceleration [m/s/s] (type:float)
        zacc                = acc[2]                          # Z acceleration [m/s/s] (type:float)
        xgyro               = gyro[0]                         # Angular speed around X axis in body frame [rad/s] (type:float)
        ygyro               = gyro[1]                         # Angular speed around Y axis in body frame [rad/s] (type:float)
        zgyro               = gyro[2]                         # Angular speed around Z axis in body frame [rad/s] (type:float)
        xmag                = mag[0]                          # X Magnetic field [gauss] (type:float)
        ymag                = mag[1]                          # Y Magnetic field [gauss] (type:float)
        zmag                = mag[2]                          # Z Magnetic field [gauss] (type:float)
        abs_pressure        = bar                             # Absolute pressure [hPa] (type:float)
        diff_pressure       = 0                               # Differential pressure (airspeed) [hPa] (type:float)
        pressure_alt        = -C_bar*log(bar/pressure_sea)    # Altitude calculated from pressure (type:float)
        temperature         = 40                              # Temperature [degC] (type:float)
        fields_updated      = 7167                            # Bitmap for fields that have updated since last message, bit 0 = xacc, bit 12: temperature, bit 31: full reset of attitude/position/velocities/etc was performed in sim. (type:uint32_t)
        the_id              = 0                               # Sensor ID (zero indexed). Used for multiple sensor inputs (type:uint8_t)

        # Send HIL_SENSOR message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.hil_sensor_send(
                time_usec      = time_usec      ,
                xacc           = xacc           ,
                yacc           = yacc           ,
                zacc           = zacc           ,
                xgyro          = xgyro          ,
                ygyro          = ygyro          ,
                zgyro          = zgyro          ,
                xmag           = xmag           ,
                ymag           = ymag           ,
                zmag           = zmag           ,
                abs_pressure   = abs_pressure   ,
                diff_pressure  = diff_pressure  ,
                pressure_alt   = pressure_alt   ,
                temperature    = temperature    ,
                fields_updated = fields_updated ,
                id             = the_id         ,
            )

    def send_rc_commands(self, channels):
        """
        Send RC command information to PX4

        Parameters:
            channels (numpy.ndarray): Array with dimension 18 with the values of the channels (between 1000 and 2000)
        """

        # Get current time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)

        # Compute time since boot
        since_boot__us = t_abs__us - self.t_boot__us
        since_boot__ms = int(since_boot__us / 1000)

        # Send RC_CHANNELS message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.rc_channels_send(
                time_boot_ms = since_boot__ms ,
                chancount    = 18             ,
                chan1_raw    = channels[0]    ,
                chan2_raw    = channels[1]    ,
                chan3_raw    = channels[2]    ,
                chan4_raw    = channels[3]    ,
                chan5_raw    = channels[4]    ,
                chan6_raw    = channels[5]    ,
                chan7_raw    = channels[6]    ,
                chan8_raw    = channels[7]    ,
                chan9_raw    = channels[8]    ,
                chan10_raw   = channels[9]    ,
                chan11_raw   = channels[10]   ,
                chan12_raw   = channels[11]   ,
                chan13_raw   = channels[12]   ,
                chan14_raw   = channels[13]   ,
                chan15_raw   = channels[14]   ,
                chan16_raw   = channels[15]   ,
                chan17_raw   = channels[16]   ,
                chan18_raw   = channels[17]   ,
                rssi         = 80             ,
            )


    def get_actuator_controls(self):
        """
        Get actuator controls from PX4

        Returns:
            update (bool): Flag indicating that a new message was received
            actuator_controls (numpy.ndarray): Array with the values of the new actuator controls (returns None if there is no new value)
        """

        #Initialize variables
        update = False
        actuator_commands = None

        # Receive MAVLink messages (blocking non operation)
        msg = self.vehicle.recv_match(blocking=False)

        # Is a message is received
        if msg is not None:
            # Check if the message is an actuator control
            if msg.get_type() == "HIL_ACTUATOR_CONTROLS":

                    # Extract motor control commands from the message
                    actuator_commands = msg.controls #values in [0.0, 1.0]

                    # Indicate that the motors were updated
                    update = True
            
        return update, actuator_commands









    # TODO: Implementation of battery levels. PX4 will require changes to receive it.
    def send_battery(self):

        # Get current time
        t_abs__s    = time.time()
        t_abs__us   = int(t_abs__s * 1e6)

        # Compute time since boot
        since_boot__us = t_abs__us - self.t_boot__us
        since_boot__ms = int(since_boot__us / 1000)

        # Send BATTERY_STATUS message through mavlink
        if self.vehicle != None:
            self.vehicle.mav.battery_status_send(
                id = 0,
                battery_function = 0, #MAV_BATTERY_FUNCTION_UNKNOWN
                type = 1, #LIPO
                temperature = 60, #Celsius
                voltages = [int((24.3-0.02*since_boot__ms/1000)*1000),65535,65535,65535,65535,65535,65535,65535,65535,65535],
                current_battery = -1,
                current_consumed = -1,
                energy_consumed = -1,
                battery_remaining = -1,
            )
