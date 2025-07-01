#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: velocity limit 

import time
from log_conf import logger

from dynamixel_sdk import *

from control_table_defs import *
from conversion import *

class Robot:
    def __init__(self, config_dict):
        config_controllers = config_dict["controllers"]
        config_motors = config_dict["motors"]

        # Interface constants
        self.device_name = config_controllers["port"]
        self.protocol = config_controllers["protocol"]
        self.baud_rate = config_controllers["baudrate"]
        self.blocking = config_controllers["blocking"]

        # Initialize motor configuration from config_motors
        self._initialize_motor_config(config_motors)

        # Validate motor types and set model_type
        self._validate_motor_types()

        # Initialize port and packet handler
        self._initialize_port()

        # Ping motors to verify connectivity and model type
        self._ping_motors()

        # Configure motor limits based on config_motors
        self._configure_motor_limits(config_motors)

        # Configure control table constants based on motor type
        self._configure_control_tables()

        # Initialize group sync read/write objects
        self._initialize_sync_objects()

        # Add parameters for group sync read operations
        self._add_sync_params()

        # Configure motor parameters (acceleration, velocity, etc.)
        self._configure_motors(config_controllers)

        # Enforce angle limits on the motors
        self._enforce_angle_limits()

    def _resolve_motor_key(self, key):
        """
        Helper method to resolve a motor key to its motor id.
        Accepts a motor key which can be either an int or a str.
        Returns the motor id if valid, otherwise returns None.
        """
        if isinstance(key, int):
            return key if key in self.dxl_ids else None
        elif isinstance(key, str):
            return self.name_to_id.get(key, None)
        return None

    def _initialize_motor_config(self, config_motors):
        """Initialize motor IDs, names, and conversion dictionaries from config."""
        self.dxl_ids = []
        self.names = []
        self.name_to_id = {}
        self.id_to_name = {}
        self.id_to_limit = {}
        self.name_to_limit = {}
        model_types = []
        for alias in config_motors:
            # Collect motor IDs and names
            self.dxl_ids.append(config_motors[alias]["id"])
            self.names.append(alias)
            # Collect model types
            model_types.append(config_motors[alias]["type"])
            # Build conversion dictionaries
            self.id_to_name[config_motors[alias]["id"]] = alias
            self.name_to_id[alias] = config_motors[alias]["id"]
        logger.info("Motors with ids %s found in config file.", self.dxl_ids)
        # Temporarily store model_types for validation
        self._model_types = model_types

    def _validate_motor_types(self):
        """Validate that all motors are of the same, supported type."""
        model_set = set(self._model_types)
        if len(model_set) > 1:
            msg = f"Cannot combine motors of different types: {model_set}"
            logger.critical(msg)
            raise RuntimeError(msg)
        elif self._model_types[0] not in (350, 1200, 1230):
            msg = "Non XL-320 and XL-330 motors specified in robot configuration."
            logger.critical(msg)
            raise RuntimeError(msg)
        else:
            self.model_type = self._model_types[0]

    def _initialize_port(self):
        """Initialize the communication port and packet handler."""
        self.port_handler = PortHandler(self.device_name)
        self.packet_handler = PacketHandler(self.protocol)
        if not self.port_handler.openPort():
            msg = f"Failed to open port: {self.device_name}"
            logger.critical(msg)
            raise RuntimeError(msg)
        else:
            logger.info(f"Successfully opened port: {self.device_name}")
            
        if not self.port_handler.setBaudRate(self.baud_rate):
            msg = f"Failed to set baud rate: {self.baud_rate}"
            logger.critical(msg)
            raise RuntimeError(msg)
        else:
            logger.info(f"Successfully set baud rate: {self.baud_rate}")

    def _ping_motors(self):
        """Ping each motor to verify connectivity and consistency."""
        model_nums = []
        for motor_id in self.dxl_ids:
            dxl_model_number, dxl_comm_result, dxl_error = self.packet_handler.ping(self.port_handler, motor_id)
            model_nums.append(dxl_model_number)
            if dxl_comm_result != COMM_SUCCESS:
                msg = f"{self.packet_handler.getTxRxResult(dxl_comm_result)}"
                logger.critical(msg)
                raise RuntimeError(msg)
            elif dxl_error != 0:
                msg = f"{self.packet_handler.getRxPacketError(dxl_error)}"
                logger.critical(msg)
                raise RuntimeError(msg)
        ping_set = set(model_nums)
        if len(ping_set) > 1:
            msg = f"Cannot combine motors of different types: {ping_set}"
            logger.critical(msg)
            raise RuntimeError(msg)
        ping_type = model_nums[0]
        if ping_type != self.model_type:
            msg = f"Motor type in config file {self.model_type} incompatible with detected type {ping_type}"
            logger.critical(msg)
            raise RuntimeError(msg)
        else:
            logger.info(f"Successfully confirmed model type {self.model_type}")

    def _configure_motor_limits(self, config_motors):
        """Convert and store angle limits for each motor."""
        for alias in config_motors:
            limits = config_motors[alias]["angle_limit"]
            dxl_limits = [degree_to_dxl(angle, self.model_type) for angle in limits]
            self.id_to_limit[config_motors[alias]["id"]] = dxl_limits
            self.name_to_limit[alias] = dxl_limits

    def _configure_control_tables(self):
        """Set control table addresses and related constants based on motor type."""
        if self.model_type == 350:
            # XL-320
            self.ADDR_TORQUE_ENABLE = XL320_CONFIG["ADDR_TORQUE_ENABLE"]
            self.ADDR_GOAL_POSITION = XL320_CONFIG["ADDR_GOAL_POSITION"]
            self.ADDR_PRESENT_POSITION = XL320_CONFIG["ADDR_PRESENT_POSITION"]
            self.ADDR_HARDWARE_ERROR_STATUS = XL320_CONFIG["ADDR_HARDWARE_ERROR_STATUS"]
            self.TORQUE_ENABLE = XL320_CONFIG["TORQUE_ENABLE"]
            self.TORQUE_DISABLE = XL320_CONFIG["TORQUE_DISABLE"]
            self.ADDR_MOVING_SPEED = XL320_CONFIG["ADDR_MOVING_SPEED"]
            self.ADDR_TORQUE_LIMIT = XL320_CONFIG["ADDR_TORQUE_LIMIT"]
            self.ADDR_P_GAIN = XL320_CONFIG["ADDR_P_GAIN"]
            self.ADDR_MOVING = XL320_CONFIG["ADDR_MOVING"]
            self.ADDR_CW_ANGLE_LIMIT = XL320_CONFIG["ADDR_CW_ANGLE_LIMIT"]
            self.ADDR_CCW_ANGLE_LIMIT = XL320_CONFIG["ADDR_CCW_ANGLE_LIMIT"]
            self.VALID_DXL = (0, 1023)

        elif self.model_type == 1200:
            # XL-330
            self.ADDR_TORQUE_ENABLE = XL330_CONFIG["ADDR_TORQUE_ENABLE"]
            self.ADDR_GOAL_POSITION = XL330_CONFIG["ADDR_GOAL_POSITION"]
            self.ADDR_PRESENT_POSITION = XL330_CONFIG["ADDR_PRESENT_POSITION"]
            self.ADDR_HARDWARE_ERROR_STATUS = XL330_CONFIG["ADDR_HARDWARE_ERROR_STATUS"]
            self.TORQUE_ENABLE = XL330_CONFIG["TORQUE_ENABLE"]
            self.TORQUE_DISABLE = XL330_CONFIG["TORQUE_DISABLE"]
            self.ADDR_PROFILE_ACCELERATION = XL330_CONFIG["ADDR_PROFILE_ACCELERATION"]
            self.ADDR_PROFILE_VELOCITY = XL330_CONFIG["ADDR_PROFILE_VELOCITY"]
            self.ADDR_DRIVE_MODE = XL330_CONFIG["ADDR_DRIVE_MODE"]
            self.ADDR_MOVING_THRESHOLD = XL330_CONFIG["ADDR_MOVING_THRESHOLD"]
            self.ADDR_MOVING = XL330_CONFIG["ADDR_MOVING"]
            self.ADDR_MAX_POSITION_LIMIT = XL330_CONFIG["ADDR_MAX_POSITION_LIMIT"]
            self.ADDR_MIN_POSITION_LIMIT = XL330_CONFIG["ADDR_MIN_POSITION_LIMIT"]
            self.VALID_DXL = (341, 3755)

        elif self.model_type == 1230:  # example model type for XC330-M181-T
            # XC-330-M181-T
            self.ADDR_TORQUE_ENABLE = XC330_CONFIG["ADDR_TORQUE_ENABLE"]
            self.ADDR_GOAL_POSITION = XC330_CONFIG["ADDR_GOAL_POSITION"]
            self.ADDR_PRESENT_POSITION = XC330_CONFIG["ADDR_PRESENT_POSITION"]
            self.ADDR_HARDWARE_ERROR_STATUS = XC330_CONFIG["ADDR_HARDWARE_ERROR_STATUS"]
            self.TORQUE_ENABLE = XC330_CONFIG["TORQUE_ENABLE"]
            self.TORQUE_DISABLE = XC330_CONFIG["TORQUE_DISABLE"]
            self.ADDR_PROFILE_ACCELERATION = XC330_CONFIG["ADDR_PROFILE_ACCELERATION"]
            self.ADDR_PROFILE_VELOCITY = XC330_CONFIG["ADDR_PROFILE_VELOCITY"]
            self.ADDR_DRIVE_MODE = XC330_CONFIG["ADDR_DRIVE_MODE"]
            self.ADDR_MOVING_THRESHOLD = XC330_CONFIG["ADDR_MOVING_THRESHOLD"]
            self.ADDR_MOVING = XC330_CONFIG["ADDR_MOVING"]
            self.ADDR_MAX_POSITION_LIMIT = XC330_CONFIG["ADDR_MAX_POSITION_LIMIT"]
            self.ADDR_MIN_POSITION_LIMIT = XC330_CONFIG["ADDR_MIN_POSITION_LIMIT"]
            self.VALID_DXL = (341, 3755)  # same valid range as XL330, adjust if needed


    def _initialize_sync_objects(self):
        """Initialize group sync read/write objects based on motor type."""
        if self.model_type == 350:
            self.group_goal_write = GroupSyncWrite(self.port_handler, self.packet_handler, 
                                                self.ADDR_GOAL_POSITION, CT_XL320_ADDR[self.ADDR_GOAL_POSITION][1])
            self.group_position_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                self.ADDR_PRESENT_POSITION, CT_XL320_ADDR[self.ADDR_PRESENT_POSITION][1])
            self.group_move_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                self.ADDR_MOVING, CT_XL320_ADDR[self.ADDR_MOVING][1])
        elif self.model_type == 1200:
            self.group_goal_write = GroupSyncWrite(self.port_handler, self.packet_handler, 
                                                self.ADDR_GOAL_POSITION, CT_XL330_ADDR[self.ADDR_GOAL_POSITION][1])
            self.group_position_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                self.ADDR_PRESENT_POSITION, CT_XL330_ADDR[self.ADDR_PRESENT_POSITION][1])
            self.group_move_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                self.ADDR_MOVING, CT_XL330_ADDR[self.ADDR_MOVING][1])
            self.group_duration_write = GroupSyncWrite(self.port_handler, self.packet_handler, 
                                                self.ADDR_PROFILE_VELOCITY, CT_XL330_ADDR[self.ADDR_PROFILE_VELOCITY][1])
            self.group_duration_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                    self.ADDR_PROFILE_VELOCITY, CT_XC330_ADDR[self.ADDR_PROFILE_VELOCITY][1])

        elif self.model_type == 1230:
            self.group_goal_write = GroupSyncWrite(self.port_handler, self.packet_handler, 
                                                   self.ADDR_GOAL_POSITION, CT_XC330_ADDR[self.ADDR_GOAL_POSITION][1])
            self.group_position_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                 self.ADDR_PRESENT_POSITION, CT_XC330_ADDR[self.ADDR_PRESENT_POSITION][1])
            self.group_move_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                 self.ADDR_MOVING, CT_XC330_ADDR[self.ADDR_MOVING][1])
            self.group_duration_write = GroupSyncWrite(self.port_handler, self.packet_handler, 
                                                  self.ADDR_PROFILE_VELOCITY, CT_XC330_ADDR[self.ADDR_PROFILE_VELOCITY][1])
            self.group_duration_read = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                     self.ADDR_PROFILE_VELOCITY, CT_XC330_ADDR[self.ADDR_PROFILE_VELOCITY][1])

    def _add_sync_params(self):
        """Add motor IDs to sync read parameter storage."""
        for dxl_id in self.dxl_ids:
            dxl_addparam_result = self.group_position_read.addParam(dxl_id)
            if dxl_addparam_result != True:
                msg = f"[ID:{dxl_id}] group_position_read addParam failed"
                logger.critical(msg)
                raise RuntimeError(msg)
            dxl_addparam_result = self.group_move_read.addParam(dxl_id)
            if dxl_addparam_result != True:
                msg = f"[ID:{dxl_id}] group_move_read addParam failed"
                logger.critical(msg)
                raise RuntimeError(msg)

    def _prepare_targets(self, args, degrees=True, check_range=True):
        """
        Prepare motor targets from input arguments.
        Converts motor keys (int or str) to motor ids and, if degrees is True, converts degree values to Dynamixel units.
        If check_range is True, validates that the target values are within each motor's limits.
        Returns a dictionary mapping motor id to target value, or None if a motor key is invalid.
        """
        try:
            temp = args if not degrees else {key: degree_to_dxl(args[key], self.model_type) for key in args}
        except Exception as e:
            logger.exception("Error converting degrees to Dynamixel values.")
            raise
        
        targets = {}
        for key, value in temp.items():
            motor_id = self._resolve_motor_key(key)
            if motor_id is None:
                logger.error("%s not a valid motor name/id.", key)
                return None
            targets[motor_id] = value
        
        if check_range:
            for motor_id in targets:
                lower_limit = self.id_to_limit[motor_id][0]
                upper_limit = self.id_to_limit[motor_id][1]
                if targets[motor_id] < lower_limit:
                    logger.warning("Invalid movement target %d for motor %d. Valid range = %s. Changed to %d",
                                targets[motor_id], motor_id, self.id_to_limit[motor_id], lower_limit)
                    targets[motor_id] = lower_limit
                elif targets[motor_id] > upper_limit:
                    logger.warning("Invalid movement target %d for motor %d. Valid range = %s. Changed to %d",
                                targets[motor_id], motor_id, self.id_to_limit[motor_id], upper_limit)
                    targets[motor_id] = upper_limit
        return targets

    def _configure_motors(self, config_controllers):
        """Configure motor parameters (acceleration, velocity, etc.) based on motor type."""
        if self.model_type in (1200, 1230):
            self.acceleration = 100
            self.velocity = 200
            self.moving_threshold = 1
            self.drive_mode = config_controllers["drivemode"]
            for motor_id in self.dxl_ids:
                self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, self.ADDR_DRIVE_MODE, self.drive_mode)
                self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_PROFILE_ACCELERATION, self.acceleration)
                self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_PROFILE_VELOCITY, self.velocity)
                self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_MOVING_THRESHOLD, self.moving_threshold)
                logger.info(f"Set profile acceleration ({self.acceleration}) and velocity ({self.velocity}) set for motor {motor_id}")
        elif self.model_type == 350:
            self.moving_speed = 100
            self.torque_limit = 512
            self.p_gain = 32
            self.drive_mode = 0
            for motor_id in self.dxl_ids:
                self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, self.ADDR_MOVING_SPEED, self.moving_speed)
                self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, self.ADDR_TORQUE_LIMIT, self.torque_limit)
                self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, self.ADDR_P_GAIN, self.p_gain)
                logger.info(f"Set moving speed ({self.moving_speed}), torque limit ({self.torque_limit}), and P gain ({self.p_gain}) set for motor {motor_id}")

    def _enforce_angle_limits(self):
        """Write angle limits to the motors based on motor type."""
        if self.model_type in (1200, 1230):
            for motor_id in self.dxl_ids:
                self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_MIN_POSITION_LIMIT, self.id_to_limit[motor_id][0])
                self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_MAX_POSITION_LIMIT, self.id_to_limit[motor_id][1])
                logger.info(f"Set min position limit ({self.id_to_limit[motor_id][0]}), max position limit ({self.id_to_limit[motor_id][1]})")
        elif self.model_type == 350:
            for motor_id in self.dxl_ids:
                self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, self.ADDR_CW_ANGLE_LIMIT, self.id_to_limit[motor_id][0])
                self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, self.ADDR_CCW_ANGLE_LIMIT, self.id_to_limit[motor_id][1])
                logger.info(f"Set CW angle limit ({self.id_to_limit[motor_id][0]}), CCW angle limit ({self.id_to_limit[motor_id][1]})")

    def reset(self):
        '''
        Move all motors to position 0, or as close to 0 as their limit allows.
        
        Returns 0 if a move fails, 1 if all successful. 
        '''
        args = {motor_id:0 for motor_id in self.dxl_ids}
        result = self.move_motors_sync(args, degrees=True)
        return result 
    
    def to_string(self):
        ''' Prints all attributes. No return. '''
        logger.info("Device Name = %s", self.device_name)
        logger.info("Protocol = %s", self.protocol)
        logger.info("Baud Rate = %s", self.baud_rate)
        logger.info("Model Type = %s", self.model_type)
        logger.info("DXL IDS = %s", self.dxl_ids)
        logger.info("Names = %s", self.names)
        logger.info("Id, name = %s", self.id_to_name)
        logger.info("Name, id = %s", self.name_to_id)
        logger.info("Id, angle limit = %s", self.id_to_limit)
        logger.info("Name, angle limit = %s", self.name_to_limit)
        logger.info("Blocking Moves = %s", self.blocking)

        if self.model_type == 350:
            logger.info("Moving speed = %s", self.moving_speed)
            logger.info("Torque limit = %s", self.torque_limit)
            logger.info("P gain = %s", self.p_gain)
        elif self.model_type in (1200, 1230):
            logger.info("Drive mode = %s", self.drive_mode)
            logger.info("Acceleration = %s", self.acceleration)
            logger.info("Velocity = %s", self.velocity)
            logger.info("Moving Threshold = %s", self.moving_threshold)

    def check_motor_status(self, args):
        '''
        Checks the current position of the specified motors. 

        Inputs: args -- a list of str motor names or int ids, or a list containing only the string "all"
        Returns 1 if successful, 0 if input was invalid. 
        '''
        # if checking all, do not specify additional motors 
        if "all" in args and len(args) != 1:
            return 0

        if args[0] != "all":
            for elem in args:
                if self._resolve_motor_key(elem) is None:
                    logger.error("%s not a valid motor name/id.", elem)
                    return 0

        # get status of all motors 
        if args[0] == "all":
            for dxl_id in self.dxl_ids:
                if self.model_type == 350:
                    pos, _, _ = self.packet_handler.read2ByteTxRx(self.port_handler, dxl_id, self.ADDR_PRESENT_POSITION)
                elif self.model_type in (1200, 1230):
                    pos, _, _ = self.packet_handler.read4ByteTxRx(self.port_handler, dxl_id, self.ADDR_PRESENT_POSITION)
                logger.info("Status Check: Motor %d Model Type: %d Position: %d", dxl_id, self.model_type, pos)
        else:
            for motor in args:
                motor_id = self._resolve_motor_key(motor)
                if motor_id is None:
                    logger.error("%s not a valid motor name/id.", motor)
                    continue
                if self.model_type == 350:
                    pos, _, _ = self.packet_handler.read2ByteTxRx(self.port_handler, motor_id, self.ADDR_PRESENT_POSITION)
                elif self.model_type in (1200, 1230):
                    pos, _, _ = self.packet_handler.read4ByteTxRx(self.port_handler, motor_id, self.ADDR_PRESENT_POSITION)
                logger.info("Status Check: Motor %d Model Type: %d Position: %d", motor_id, self.model_type, pos)
        
        return 1

    def get_diagnostic(self, args):
        '''
        Checks the error status of the specified motors 

        Inputs: args -- a list of str motor names or int ids, or a list containing only the string "all"
        Returns 1 if successful, 0 if input was invalid. 
        '''
        # if checking all, do not specify additional motors 
        if "all" in args and len(args) != 1:
            return 0
        
        # if specifying motors, motors must be valid 
        if args[0] != "all":
            for elem in args:
                if elem not in self.dxl_ids and elem not in self.names:
                    logger.error("%s not a valid motor name/id.", elem)
                    return 0
        
        # get error status of all motors 
        if args[0] == "all":
            for dxl_id in self.dxl_ids:
                error_status, _, _ = self.packet_handler.read1ByteTxRx(self.port_handler, dxl_id, self.ADDR_HARDWARE_ERROR_STATUS)                
                logger.info("Diagnostic: Motor %d Error Status: %s", dxl_id, bin(error_status))
                
        # get status of specified motors 
        else:
            for motor in args:
                if type(motor) == str:
                    dxl_id = self.name_to_id[motor]

                    error_status, _, _ = self.packet_handler.read1ByteTxRx(self.port_handler, dxl_id, self.ADDR_HARDWARE_ERROR_STATUS)
                    logger.info("Diagnostic: Motor %d Error Status: %s", dxl_id, bin(error_status))
                
                elif type(motor) == int:
                    error_status, _, _ = self.packet_handler.read1ByteTxRx(self.port_handler, motor, self.ADDR_HARDWARE_ERROR_STATUS)
                    logger.info("Diagnostic: Motor %d Error Status: %s", motor, bin(error_status))
        
        return 1

    def enable_torque(self):
        """Enables torque. Torque must be enabled before motors will move."""
        for motor_id in self.dxl_ids:
            self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
            logger.info("Torque enabled for Motor %d", motor_id)

    def disable_torque(self):
        """Disables torque. Torque must be disabled for a clean shutdown, and before setting certain values in the control table."""
        for motor_id in self.dxl_ids:
            self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
            logger.info("Torque disabled for Motor %d", motor_id)

    def move_motors(self, args, duration=None, degrees=True):
        """Move motors sequentially. If blocking is set in the config, 
        waits for all movements in args to complete before continuing."""
        targets = self._prepare_targets(args, degrees=True, check_range=True)
        if targets is None:
            return 0
        
        # set duration 
        if (duration is not None) and (self.drive_mode & DRIVE_MODE_TIME != 0):
            # check for valid times and motors 
            motor_list = [key for key in duration]
            times = {}

            for m in motor_list:
                if type(m) == int:
                    if m not in targets.keys():
                        logger.error("Invalid motor provided %s.", m)
                        return 0
                    else:
                        times[m] = duration[m]
                elif type(m) == str:
                    if m not in self.name_to_id.keys() or self.name_to_id[m] not in targets.keys():
                        logger.error("Invalid motor provided %s.", m)
                        return 0
                    else:
                        times[self.name_to_id[m]] = duration[m]
                    
            # change the times 
            for id in times:
                self.packet_handler.write4ByteTxRx(self.port_handler, id, self.ADDR_PROFILE_VELOCITY, times[id])

        # make the moves 
        if self.model_type == 350:
            for dxl_id, goal_position in targets.items():
                self.packet_handler.write2ByteTxRx(self.port_handler, dxl_id, self.ADDR_GOAL_POSITION, goal_position)
                logger.info("Motor %d Model Type: %d moved to position %d", dxl_id, self.model_type, goal_position)
        elif self.model_type in (1200, 1230):
            for dxl_id, goal_position in targets.items():
                self.packet_handler.write4ByteTxRx(self.port_handler, dxl_id, self.ADDR_GOAL_POSITION, goal_position)
                logger.info("Motor %d Model Type: %d moved to position %d", dxl_id, self.model_type, goal_position)

        # spin until completion only if blocking is set to True in the config 
        if self.blocking:
            self.check_move_complete()

        self.check_motor_status(["all"])

        return 1


    def move_motors_sync(self, args, duration=None, degrees=True, velocity=None):
        """Move motors simultaneously using group sync write and read. 
        If blocking is set in config, waits for all movements in args
        to complete before continuing."""
        
        targets = self._prepare_targets(args, degrees=degrees, check_range=False)
        if targets is None:
            return 0
        
        # If velocity is explicitly provided (manual override), convert and write profile velocities
        if velocity is not None and (self.drive_mode & DRIVE_MODE_TIME != 0):
            vel_params = {}
            for m in velocity:
                motor_id = self._resolve_motor_key(m)
                if motor_id is None or motor_id not in targets:
                    logger.error("Invalid motor provided in velocity: %s", m)
                    return 0

                profile_velocity_units = max(int(velocity[m]), 1)  # User gives raw value in Dynamixel units

                logger.debug("Motor %d: user profile velocity = %d", motor_id, profile_velocity_units)

                vel_params[motor_id] = [
                    DXL_LOBYTE(DXL_LOWORD(profile_velocity_units)),
                    DXL_HIBYTE(DXL_LOWORD(profile_velocity_units)),
                    DXL_LOBYTE(DXL_HIWORD(profile_velocity_units)),
                    DXL_HIBYTE(DXL_HIWORD(profile_velocity_units))
                ]

            # Sync write to apply user-specified velocities
            for motor_id, param_bytes in vel_params.items():
                if not self.group_duration_write.addParam(motor_id, param_bytes):
                    logger.error("[ID:%d] group_duration_write addParam failed for velocity", motor_id)
                    self.group_duration_write.clearParam()
                    return 0

            dxl_comm_result = self.group_duration_write.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                logger.error("Profile velocity sync write failed: %s",
                            self.packet_handler.getTxRxResult(dxl_comm_result))
                self.group_duration_write.clearParam()
                return 0
            else:
                logger.info("Profile velocity sync write (user velocity dict) succeeded.")
            self.group_duration_write.clearParam()
        elif (duration is not None) and (self.drive_mode & DRIVE_MODE_TIME != 0):
            times = {}
            for m in duration:
                motor_id = self._resolve_motor_key(m)
                if motor_id is None or motor_id not in targets:
                    logger.error("Invalid motor provided in duration: %s", m)
                    return 0

                goal_pos = targets[motor_id]
                dxl_present_position, _, _ = self.packet_handler.read4ByteTxRx(self.port_handler, motor_id, self.ADDR_PRESENT_POSITION)
                current_pos = dxl_present_position if dxl_present_position != 0 else 2048  # fallback if read fails

                distance = abs(goal_pos - current_pos)
                move_time_ms = duration[m]

                # Avoid divide-by-zero and too-slow movements
                if move_time_ms < 50:
                    logger.warning("Capping too-short duration (%dms) to 50ms for motor %d", move_time_ms, motor_id)
                    move_time_ms = 50

                # Velocity = distance (raw steps) / time (ms), then profile velocity = ms per step / 11.2
                velocity_raw = distance / move_time_ms if move_time_ms > 0 else 1
                profile_velocity_units = max(int((velocity_raw * 1000) / 11.2), 1) if velocity_raw > 0 else 1


                logger.debug("Motor %d: dist=%d, time=%dms, vel=%.2f, profile_vel=%d",
                            motor_id, distance, move_time_ms, velocity_raw, profile_velocity_units)

                times[motor_id] = [
                    DXL_LOBYTE(DXL_LOWORD(profile_velocity_units)),
                    DXL_HIBYTE(DXL_LOWORD(profile_velocity_units)),
                    DXL_LOBYTE(DXL_HIWORD(profile_velocity_units)),
                    DXL_HIBYTE(DXL_HIWORD(profile_velocity_units))
                ]

            # Write profile velocities to motors
            for motor_id, param_bytes in times.items():
                if not self.group_duration_write.addParam(motor_id, param_bytes):
                    logger.error("[ID:%d] group_duration_write addParam failed for duration", motor_id)
                    self.group_duration_write.clearParam()
                    return 0

            dxl_comm_result = self.group_duration_write.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                logger.error("Profile velocity sync write failed: %s",
                            self.packet_handler.getTxRxResult(dxl_comm_result))
                self.group_duration_write.clearParam()
                return 0
            else:
                logger.info("Profile velocity sync write succeeded.")
            self.group_duration_write.clearParam()

        # Prepare goal positions
        param_goal_positions = {}
        if self.model_type == 350:  # 2-byte position
            for target in targets:
                val = targets[target]
                param_goal_positions[target] = [
                    DXL_LOBYTE(DXL_LOWORD(val)),
                    DXL_HIBYTE(DXL_LOWORD(val))
                ]
        elif self.model_type in (1200, 1230):  # 4-byte position
            for target in targets:
                val = targets[target]
                param_goal_positions[target] = [
                    DXL_LOBYTE(DXL_LOWORD(val)),
                    DXL_HIBYTE(DXL_LOWORD(val)),
                    DXL_LOBYTE(DXL_HIWORD(val)),
                    DXL_HIBYTE(DXL_HIWORD(val))
                ]

        # Add goal positions to sync write buffer
        for dxl_id, param_bytes in param_goal_positions.items():
            if not self.group_goal_write.addParam(dxl_id, param_bytes):
                msg = f"[ID:{dxl_id}] group_goal_write addParam failed for position"
                logger.error(msg)
                self.group_goal_write.clearParam()
                raise RuntimeError(msg)

        for dxl_id, pos in targets.items():
            logger.debug("Moving ID %d to position %d", dxl_id, pos)

        # Send goal position command
        try:
            dxl_comm_result = self.group_goal_write.txPacket()
            if dxl_comm_result != COMM_SUCCESS:
                logger.error("Goal position sync write failed: %s",
                            self.packet_handler.getTxRxResult(dxl_comm_result))
                self.group_goal_write.clearParam()
                return 0
            else:
                logger.info("Goal position sync write succeeded.")
        except Exception:
            logger.exception("Exception during group_goal_write.txPacket")
            self.group_goal_write.clearParam()
            raise

        self.group_goal_write.clearParam()

        # Optionally block until move complete
        if self.blocking:
            self.check_move_complete()
        else:
            # If duration dict was provided, wait roughly for the longest move duration in seconds
            if duration:
                max_duration_ms = max(duration.values())
                # Avoid too short waits
                wait_time_s = max(0.05, max_duration_ms / 1000.0)
                logger.debug(f"Non-blocking mode: sleeping for {wait_time_s:.3f}s to allow move completion")
                time.sleep(wait_time_s)
            else:
                # If no duration provided, sleep a small default
                time.sleep(0.05)

        self.check_motor_status(["all"])
        return 1

    # def move_motors_sync(self, args, duration_ms=250, degrees=True, accel=800, velocity=500):
    #     """Move motors using group sync write, with fixed acceleration and velocity."""
    #     targets = self._prepare_targets(args, degrees=degrees, check_range=False)
    #     if targets is None:
    #         return 0

    #     # Write profile acceleration and velocity to each motor
    #     for motor_id in targets:
    #         self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_PROFILE_ACCELERATION, accel)
    #         self.packet_handler.write4ByteTxRx(self.port_handler, motor_id, self.ADDR_PROFILE_VELOCITY, velocity)

    #     # Prepare goal positions
    #     param_goal_positions = {}
    #     for dxl_id, val in targets.items():
    #         param_goal_positions[dxl_id] = [
    #             DXL_LOBYTE(DXL_LOWORD(val)),
    #             DXL_HIBYTE(DXL_LOWORD(val)),
    #             DXL_LOBYTE(DXL_HIWORD(val)),
    #             DXL_HIBYTE(DXL_HIWORD(val))
    #         ] if self.model_type in (1200, 1230) else [
    #             DXL_LOBYTE(DXL_LOWORD(val)),
    #             DXL_HIBYTE(DXL_LOWORD(val))
    #         ]

    #     # Add goal positions
    #     for dxl_id, param_bytes in param_goal_positions.items():
    #         if not self.group_goal_write.addParam(dxl_id, param_bytes):
    #             self.group_goal_write.clearParam()
    #             raise RuntimeError(f"[ID:{dxl_id}] group_goal_write addParam failed")

    #     dxl_comm_result = self.group_goal_write.txPacket()
    #     self.group_goal_write.clearParam()

    #     if dxl_comm_result != COMM_SUCCESS:
    #         logger.error("Goal position sync write failed: %s", self.packet_handler.getTxRxResult(dxl_comm_result))
    #         return 0

    #     if self.blocking:
    #         self.check_move_complete()
    #     else:
    #         time.sleep(duration_ms / 1000)

    #     self.check_motor_status(["all"])
    #     return 1


    
    def get_positions(self):
        ''' Get all positions with group_position_read. May replace check_motor_status.'''
        # Syncread present position
        dxl_comm_result = self.group_position_read.txRxPacket()
        if dxl_comm_result != COMM_SUCCESS:
            logger.info("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
                
        positions = {}
        for dxl_id in self.dxl_ids:
            if self.model_type == 350:
                positions[dxl_id] = self.group_position_read.getData(dxl_id, self.ADDR_PRESENT_POSITION, CT_XL320_ADDR[self.ADDR_PRESENT_POSITION][1])
            elif self.model_type == 1200:
                positions[dxl_id] = self.group_position_read.getData(dxl_id, self.ADDR_PRESENT_POSITION, CT_XL330_ADDR[self.ADDR_PRESENT_POSITION][1])
            elif self.model_type == 1230:
                positions[dxl_id] = self.group_position_read.getData(dxl_id, self.ADDR_PRESENT_POSITION, CT_XC330_ADDR[self.ADDR_PRESENT_POSITION][1])

        return positions 

    def check_move_complete(self):
        ''' Given a list of motors, gets the goal and present positions. '''
         # spin until completion
        while 1:
            goal_reached = 0
            time.sleep(0.1)

            # Syncread moving status
            dxl_comm_result = self.group_move_read.txRxPacket()
            if dxl_comm_result != COMM_SUCCESS:
                logger.error("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
                continue

            for dxl_id in self.dxl_ids:
                # Check if groupsyncread data of motor is available
                if self.model_type == 350:
                    dxl_getdata_result = self.group_move_read.isAvailable(dxl_id, self.ADDR_MOVING, CT_XL320_ADDR[self.ADDR_MOVING][1])
                    if dxl_getdata_result != True:
                        logger.error("[ID:%03d] group_move_read getdata failed" % dxl_id)

                    # Get motor moving status
                    moving = self.group_move_read.getData(dxl_id, self.ADDR_MOVING, CT_XL320_ADDR[self.ADDR_MOVING][1])
                elif self.model_type == 1200:
                    dxl_getdata_result = self.group_move_read.isAvailable(dxl_id, self.ADDR_MOVING, CT_XL330_ADDR[self.ADDR_MOVING][1])
                    if dxl_getdata_result != True:
                        logger.error("[ID:%03d] group_move_read getdata failed" % dxl_id)

                    # Get motor moving status
                    moving = self.group_move_read.getData(dxl_id, self.ADDR_MOVING, CT_XL330_ADDR[self.ADDR_MOVING][1])
                elif self.model_type == 1230:
                    dxl_getdata_result = self.group_move_read.isAvailable(dxl_id, self.ADDR_MOVING, CT_XC330_ADDR[self.ADDR_MOVING][1])
                    if dxl_getdata_result != True:
                        logger.error("[ID:%03d] group_move_read getdata failed" % dxl_id)

                    # Get motor moving status
                    moving = self.group_move_read.getData(dxl_id, self.ADDR_MOVING, CT_XC330_ADDR[self.ADDR_MOVING][1])

                if not moving:
                    goal_reached += 1
                
            if goal_reached == len(self.dxl_ids):
                break

        return 
    
    def get_motor_ids(self):
        """Returns the list of motor ids."""
        return self.dxl_ids

    def clean_shutdown(self):
        """Makes a clean shutdown of the motors."""
        logger.info("Initiating shutdown...")

        self.disable_torque()

        self.port_handler.closePort()

        logger.info("Shutdown complete.")