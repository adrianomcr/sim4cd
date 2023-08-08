#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Communication with the PX4 simulated software by using mavlink



import time
import atexit
from random import random
from pymavlink import mavutil











class px4_connection:
    def __init__(self, protocol='tcpin', host='localhost', port='4560'):
        self.protocol = protocol
        self.host = host
        self.port = port

        self.vehicle = False
        self.n = 0

        # self.t_abs__us = False
        self.t_boot__us = False


        



    def connect(self):
        print("Waiting to connect...")
        self.vehicle = mavutil.mavlink_connection('tcpin:localhost:4560')

        msg = self.vehicle.recv_match(blocking = True)
        if msg.get_type() != "COMMAND_LONG":
            raise Exception("error")
        #self.n += 1
        #print(n, "<==", msg)

        msg = self.vehicle.recv_match(blocking = True)
        if msg.get_type() != "HEARTBEAT":
            raise Exception("error")
        #self.n += 1
        #print(n, "<==", msg)

        t_abs__s    = time.time()
        t_abs__us   = round(t_abs__s * 1e6)
        self.t_boot__us  = round(t_abs__us - 30e6)




    def send_system_time(self):
        # self.n += 1
        
        t_abs__s    = time.time()
        t_abs__us   = round(t_abs__s * 1e6)

        since_boot__us = t_abs__us - self.t_boot__us
        since_boot__ms = round(since_boot__us / 1000)
        
        time_unix_usec      = t_abs__us
        time_boot_ms        = since_boot__ms
        
        if self.vehicle != None:
            self.vehicle.mav.system_time_send(
                time_unix_usec  = time_unix_usec        , # Timestamp (UNIX epoch time). [us] (type:uint64_t)
                time_boot_ms    = time_boot_ms          , # Timestamp (time since system boot). [ms] (type:uint32_t)
            )


    def send_heart_beat(self):

        # self.n += 1
        
        the_type        = 0     # Vehicle or component type. For a flight controller component the vehicle type (quadrotor, helicopter, etc.). For other components the component type (e.g. camera, gimbal, etc.). This should be used in preference to component id for identifying the component type. (type:uint8_t, values:MAV_TYPE)
        autopilot       = 0     # Autopilot type / class. Use MAV_AUTOPILOT_INVALID for components that are not flight controllers. (type:uint8_t, values:MAV_AUTOPILOT)
        base_mode       = 0     # System mode bitmap. (type:uint8_t, values:MAV_MODE_FLAG)
        custom_mode     = 0     # A bitfield for use for autopilot-specific flags (type:uint32_t)
        system_status   = 0     # System status flag. (type:uint8_t, values:MAV_STATE)
        mavlink_version = 3     # MAVLink version, not writable by user, gets added by protocol because of magic data type          , # uint8_t_mavlink_version (type:uint8_t)
        
        if self.vehicle != None:
            self.vehicle.mav.heartbeat_send(
                type                = the_type          , 
                autopilot           = autopilot         , 
                base_mode           = base_mode         , 
                custom_mode         = custom_mode       , 
                system_status       = system_status     , 
                mavlink_version     = mavlink_version   , 
            )
    


    def send_gps(self,gps):

        t_abs__s    = time.time()
        t_abs__us   = round(t_abs__s * 1e6)

        # self.n += 1
        
        # time_usec           = t_abs__us                 # Timestamp (UNIX Epoch time or time since system boot). The receiving end can infer timestamp format (since 1.1.1970 or since system boot) by checking for the magnitude of the number. [us] (type:uint64_t)
        # fix_type            = 3                         # 0-1: no fix, 2: 2D fix, 3: 3D fix. Some applications will not use the value of this field unless it is at least two, so always correctly fill in the fix. (type:uint8_t)
        # lat                 = gps['i_lat__degE7']     # Latitude (WGS84) [degE7] (type:int32_t)
        # lon                 = gps['i_lon__degE7']     # Longitude (WGS84) [degE7] (type:int32_t)
        # alt                 = gps['i_alt__mm']        # Altitude (MSL). Positive for up. [mm] (type:int32_t)
        # eph                 = gps['i_eph__cm']        # GPS HDOP horizontal dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        # epv                 = gps['i_epv__cm']        # GPS VDOP vertical dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        # vel                 = gps['i_vel__cm/s']      # GPS ground speed. If unknown, set to: 65535 [cm/s] (type:uint16_t)
        # vn                  = gps['i_vn__cm/s']       # GPS velocity in north direction in earth-fixed NED frame [cm/s] (type:int16_t)
        # ve                  = gps['i_ve__cm/s']       # GPS velocity in east direction in earth-fixed NED frame [cm/s] (type:int16_t)
        # vd                  = gps['i_vd__cm/s']       # GPS velocity in down direction in earth-fixed NED frame [cm/s] (type:int16_t)
        # cog                 = gps['i_cog__cdeg']      # Course over ground (NOT heading, but direction of movement), 0.0..359.99 degrees. If unknown, set to: 65535 [cdeg] (type:uint16_t)
        # satellites_visible  = 10                        # Number of satellites visible. If unknown, set to 255 (type:uint8_t)
        # the_id              = 0                         # GPS ID (zero indexed). Used for multiple GPS inputs (type:uint8_t)
        # yaw                 = 0                         # Yaw of vehicle relative to Earth's North, zero means not available, use 36000 for north [cdeg] (type:uint16_t)

        time_usec           = t_abs__us                 # Timestamp (UNIX Epoch time or time since system boot). The receiving end can infer timestamp format (since 1.1.1970 or since system boot) by checking for the magnitude of the number. [us] (type:uint64_t)
        fix_type            = 3                         # 0-1: no fix, 2: 2D fix, 3: 3D fix. Some applications will not use the value of this field unless it is at least two, so always correctly fill in the fix. (type:uint8_t)
        lat                 = gps['i_lat__degE7']     # Latitude (WGS84) [degE7] (type:int32_t)
        lon                 = gps['i_lon__degE7']     # Longitude (WGS84) [degE7] (type:int32_t)
        alt                 = gps['i_alt__mm']        # Altitude (MSL). Positive for up. [mm] (type:int32_t)
        eph                 = gps['i_eph__cm']        # GPS HDOP horizontal dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        epv                 = gps['i_epv__cm']        # GPS VDOP vertical dilution of position (unitless). If unknown, set to: UINT16_MAX (type:uint16_t)
        vel                 = gps['i_vel__cm/s']      # GPS ground speed. If unknown, set to: 65535 [cm/s] (type:uint16_t)
        vn                  = gps['i_vn__cm/s']       # GPS velocity in north direction in earth-fixed NED frame [cm/s] (type:int16_t)
        ve                  = gps['i_ve__cm/s']       # GPS velocity in east direction in earth-fixed NED frame [cm/s] (type:int16_t)
        vd                  = gps['i_vd__cm/s']       # GPS velocity in down direction in earth-fixed NED frame [cm/s] (type:int16_t)
        cog                 = gps['i_cog__cdeg']      # Course over ground (NOT heading, but direction of movement), 0.0..359.99 degrees. If unknown, set to: 65535 [cdeg] (type:uint16_t)
        satellites_visible  = 10                        # Number of satellites visible. If unknown, set to 255 (type:uint8_t)
        the_id              = 0                         # GPS ID (zero indexed). Used for multiple GPS inputs (type:uint8_t)
        yaw                 = 0                         # Yaw of vehicle relative to Earth's North, zero means not available, use 36000 for north [cdeg] (type:uint16_t)
        

        # print ("gps:\n", gps)

        # print (0, "\33[91m--> HIL_GPS {",
        #     "time_usec :"           , time_usec,
        #     ",",
        #     "fix_type :"            , fix_type,
        #     ",",
        #     "lat :"                 , lat,
        #     ",",
        #     "lon :"                 , lon,
        #     ",",
        #     "alt :"                 , alt,
        #     ",",
        #     "eph :"                 , eph,
        #     ",",
        #     "epv :"                 , epv,
        #     ",",
        #     "vel :"                 , vel,
        #     ",",
        #     "vn :"                  , vn,
        #     ",",
        #     "ve :"                  , ve,
        #     ",",
        #     "vd :"                  , vd,
        #     ",",
        #     "cog :"                 , cog,
        #     ",",
        #     "satellites_visible :"  , satellites_visible,
        #     ",",
        #     "id :"                  , the_id,
        #     ",",
        #     "yaw :"                 , yaw,
        # "}\33[0m")

        if self.vehicle != None:
            self.vehicle.mav.hil_gps_send(
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
                yaw                 = 0                   ,
            )

        return


    def send_quaternion(self):
        return

    def send_sensors(self,acc,gyro,mag,bar):
        # self.n += 1

        t_abs__s    = time.time()
        t_abs__us   = round(t_abs__s * 1e6)
        
        time_usec           = t_abs__us     # Timestamp (UNIX Epoch time or time since system boot). The receiving end can infer timestamp format (since 1.1.1970 or since system boot) by checking for the magnitude of the number. [us] (type:uint64_t)
        xacc                = acc[0]        # X acceleration [m/s/s] (type:float)
        yacc                = acc[1]        # Y acceleration [m/s/s] (type:float)
        zacc                = acc[2]        # Z acceleration [m/s/s] (type:float)
        xgyro               = gyro[0]       # Angular speed around X axis in body frame [rad/s] (type:float)
        ygyro               = gyro[1]       # Angular speed around Y axis in body frame [rad/s] (type:float)
        zgyro               = gyro[2]       # Angular speed around Z axis in body frame [rad/s] (type:float)
        xmag                = mag[0]        # X Magnetic field [gauss] (type:float)
        ymag                = mag[1]        # Y Magnetic field [gauss] (type:float)
        zmag                = mag[2]        # Z Magnetic field [gauss] (type:float)
        abs_pressure        = bar           # Absolute pressure [hPa] (type:float)
        diff_pressure       = 0             # Differential pressure (airspeed) [hPa] (type:float)
        pressure_alt        = (1000-bar)*10             # Altitude calculated from pressure (type:float)
        temperature         = 40            # Temperature [degC] (type:float)
        #fields_updated      = 5071 #7167          # Bitmap for fields that have updated since last message, bit 0 = xacc, bit 12: temperature, bit 31: full reset of attitude/position/velocities/etc was performed in sim. (type:uint32_t)
        fields_updated      = 7167          # Bitmap for fields that have updated since last message, bit 0 = xacc, bit 12: temperature, bit 31: full reset of attitude/position/velocities/etc was performed in sim. (type:uint32_t)
        the_id              = 0             # Sensor ID (zero indexed). Used for multiple sensor inputs (type:uint8_t)
        
        # bit 0 = xacc
        # bit 12: temperature
        # bit 31: full reset of attitude/position/velocities/etc was performed in sim. (type:uint32_t)

        if self.vehicle != None:
            self.vehicle.mav.hil_sensor_send(
                time_usec           = time_usec         ,
                xacc                = xacc              ,
                yacc                = yacc              ,
                zacc                = zacc              ,
                xgyro               = xgyro             ,
                ygyro               = ygyro             ,
                zgyro               = zgyro             ,
                xmag                = xmag              ,
                ymag                = ymag              ,
                zmag                = zmag              ,
                abs_pressure        = abs_pressure      ,
                diff_pressure       = diff_pressure     ,
                pressure_alt        = pressure_alt      ,
                temperature         = temperature       ,
                fields_updated      = fields_updated    ,
                id                  = the_id            ,
            )








####################################3




    def send_rc_commands(self, roll, pitch, throttle, yaw):
        # self.n += 1

        # print("\33[92mSending RC\33[0m")

        t_abs__s    = time.time()
        t_abs__us   = round(t_abs__s * 1e6)
        
        # Convert RC commands to PWM values or other appropriate units based on your vehicle requirements.
        # Ensure that the values are within the valid range for your specific vehicle.

        # For example, if you are using PWM signals, you might need to map the RC commands
        # (usually in the range of -100 to 100) to the corresponding PWM values.

        # roll_pwm = map_to_pwm_range(roll)          # Convert roll command to PWM value
        # pitch_pwm = map_to_pwm_range(pitch)        # Convert pitch command to PWM value
        # throttle_pwm = map_to_pwm_range(throttle)  # Convert throttle command to PWM value
        # yaw_pwm = map_to_pwm_range(yaw)            # Convert yaw command to PWM value
        #
        roll_pwm = roll # Channel 1 (Roll) PWM value
        pitch_pwm = pitch# Channel 2 (Pitch) PWM value
        throttle_pwm = throttle  # Channel 3 (Throttle) PWM value
        yaw_pwm = yaw  # Channel 4 (Yaw) PWM value

        # Send the RC commands to the vehicle using MAVLink or your communication interface.
        # The exact method or message type will depend on your specific vehicle and communication protocol.







        if self.vehicle != None:
            # print("\33[93mSending RC\33[0m")
            # Assuming there is a MAVLink message type to send RC commands (e.g., RC_CHANNELS_OVERRIDE).
            # Use the appropriate message type supported by your autopilot or vehicle.
            # The channel numbers might vary based on your setup, so adjust them accordingly.
            # self.vehicle.mav.rc_channels_override_send(
            self.vehicle.mav.hil_rc_inputs_raw_encode(
                t_abs__us,
                1550,
                1400,
                1600,
                1100,
                1444,
                1566,
                1900,
                1990,
                400,
                500,
                1900,
                1900,
                120,
            )







        # if self.vehicle != None:
        #     # print("\33[93mSending RC\33[0m")
        #     # Assuming there is a MAVLink message type to send RC commands (e.g., RC_CHANNELS_OVERRIDE).
        #     # Use the appropriate message type supported by your autopilot or vehicle.
        #     # The channel numbers might vary based on your setup, so adjust them accordingly.
        #     # self.vehicle.mav.rc_channels_override_send(
        #     self.vehicle.mav.hil_rc_inputs_raw_encode(
        #         t_abs__us,
        #         1550,
        #         1400,
        #         1600,
        #         1100,
        #         1444,
        #         1566,
        #         1900,
        #         1990,
        #         400,
        #         500,
        #         1900,
        #         1900,
        #         120,
        #         # time_usec  = t_abs__us         ,
        #         # self.vehicle.target_system,
        #         # self.vehicle.target_component,
        #         # target_system = 0,
        #         # target_component = 0,
        #         # [1500,1500,1500,1500,1500],
        #         # chan1_raw = 1500,        # Target system ID (0 for broadcast)
        #         # chan2_raw = 1500,        # Target component ID (0 for broadcast)
        #         # chan3_raw = roll_pwm, # Channel 1 (Roll) PWM value
        #         # chan4_raw = pitch_pwm,# Channel 2 (Pitch) PWM value
        #         # chan5_raw = throttle_pwm,  # Channel 3 (Throttle) PWM value
        #         # chan6_raw = yaw_pwm,  # Channel 4 (Yaw) PWM value
        #         # chan7_raw = 1500,        # Channel 5 PWM value (if needed)
        #         # chan8_raw = 1500,        # Channel 6 PWM value (if needed)
        #         # chan9_raw = 1500,        # Channel 7 PWM value (if needed)
        #         # chan10_raw = 1500,         # Channel 8 PWM value (if needed)
        #         # rssi = 128,
        #     )

    # # Utility function to map a value from one range to another.
    # def map_to_pwm_range(value, from_min=-100, from_max=100, to_min=1000, to_max=2000):
    #     return int((value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min)



#####################################3






















    def get_vehicle(self):
        return self.vehicle



    # def __str__(self):
    #     return f"Account Holder: {self.account_holder}, Account Number: {self.account_number}, Balance: {self.balance:.2f}"



# def Connect():
    
#     global vehicle
#     global n
    
#     print("Waiting to connect...")
#     vehicle = mavutil.mavlink_connection('tcpin:localhost:4560')
    
#     msg = vehicle.recv_match(blocking = True)
#     if msg.get_type() != "COMMAND_LONG":
#         raise Exception("error")
#     n += 1
#     print(n, "<==", msg)
    
#     msg = vehicle.recv_match(blocking = True)
#     if msg.get_type() != "HEARTBEAT":
#         raise Exception("error")
#     n += 1
#     print(n, "<==", msg)


















