# tango_bot.py

from .usb import serial, getUSB
from .log import log
import time, threading, sys

class TangBotController:

    # properties
    usb:serial.Serial   = None
    cmd                 = None
    TARGET_CENTER:int   = 5896
    WAIST_VAL:int       = TARGET_CENTER
    HEAD_TILT_VAL:int   = TARGET_CENTER     # This is the up/down value
    HEAD_TURN_VAL:int   = TARGET_CENTER     # This is the left/right value
    LEFT_MOTOR:int      = TARGET_CENTER     # This is the current speed of the motor
    RIGHT_MOTOR:int     = TARGET_CENTER     # This is the current speed of the motor
    WHEEL_SPEED:int     = TARGET_CENTER     # When the robot is going forward/backward, the wheel speed is the same
    SPEED:int           = 200               # This is the current update to the motor
    SPEED_CEILING:int   = 7500              # Upper limit for wheel speed
    SPEED_FLOOR:int     = 4500              # Lower limit for wheel speed

    running:bool        = None
    lock:threading.Lock = None

    # constructor
    def __init__(self):
        self.usb = getUSB()
        self.running = True
        self.lock = threading.Lock()
        # Exit Safe Start
        # Note: something I found online
        # TODO: see if we need this
        if self.usb is not None:
            self.usb.write(chr(0x83).encode())

    # Stop the robot
    def stop(self):
        self.running = False
        # TODO: write to usb to stop wheels

    # write out command to usb
    def writeCmd(self):
        # Check if usb is not None
        command = self.cmd.encode('utf-8')
        log.debug('Writing USB Command: "%s"', command)
        if self.usb is not None:
            self.usb.write(command)
        else:
            log.critical('Unable to write to USB - USB not connected')

    def moveWaistLeft(self):
        self.WAIST_VAL += self.SPEED
        # TODO: write update to USB

    def moveWaistRight(self):
        self.WAIST_VAL -= self.SPEED
        # TODO: write update to USB

    def moveHeadUp(self):
        self.HEAD_TILT_VAL += self.SPEED  # Check that this moves up not down
        # TODO: write update to USB

    def moveHeadDown(self):
        self.HEAD_TILT_VAL -= self.SPEED  # Check that this moves down not up
        # TODO: write update to USB

    def moveHeadLeft(self):
        self.HEAD_TURN_VAL += self.SPEED  # Check that this moves left not right
        # TODO: write update to USB

    def moveHeadRight(self):
        self.HEAD_TURN_VAL -= self.SPEED  # Check that this moves right not left
        # TODO: write update to USB

    def increaseWheelSpeed(self):
        self.WHEEL_SPEED += self.SPEED
        # make sure wheel speed does no exceed the upper limit
        if self.WHEEL_SPEED > self.SPEED_CEILING:
            # set wheel speed to upper limit for wheels
            self.WHEEL_SPEED = self.SPEED_CEILING
        # TODO: write update to USB - left AND right wheels

    def decreaseWheelSpeed(self):
        self.WHEEL_SPEED -= self.SPEED
        # make sure wheel speed does no exceed the lower limit
        if self.WHEEL_SPEED < self.SPEED_FLOOR:
            # set wheel speed to lower limit for wheels
            self.WHEEL_SPEED = self.SPEED_FLOOR
        # TODO: write update to USB - left AND right wheels

# END
