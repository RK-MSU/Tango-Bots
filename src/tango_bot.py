# tango_bot.py

from .log import log
from .log import log_method_call
from .usb import serial
from .usb import getUSB
from enum import Enum
from time import sleep

class BotServos(Enum):
    LeftWheel = 0x00
    RightWheel = 0x01
    Waist = 0x02
    HeadPan = 0x03
    HeadTilt = 0x04

class DirectionState(Enum):
    Forwards = 'Forwards'
    Backwards = 'Backwards'
    LeftTurn = 'Left Turn'
    RightTurn = 'Right Turn'

class TangBotController:
    """Object Oriented Implementation of the Tango Bot"""

    usb: serial.Serial
    TARGET_CENTER: int  = 5896
    SPEED: int          = 300       # This is the current update to the motor
    SPEED_CEILING: int  = 7500      # Upper limit for wheel speed
    SPEED_FLOOR: int    = 4500      # Lower limit for wheel speed
    _HEAD_TILT: int                 # This is the up/down value
    _HEAD_TURN: int                 # This is the left/right value
    _WAIST: int                     # This is the left/right value for the (body) waist
    _WHEEL_SPEED: int               # Speed of the forward/backward movement
    _DIRECTION_STATE: DirectionState

    # constructor
    def __init__(self):
        # Fetch the serial USB
        self.usb = getUSB()
        # Exit Safe Start. Note: something I found online
        if self.usb is not None: # TODO: see if we need this
            self.usb.write(chr(0x83).encode())
        # center all of the servo motors
        self.centerHead()       # Centers the HEAD_TILT and HEAD_PAN
        self.centerWaist()      # Centers the WAIST
        self.stop()             # Centers the WHEEL_SPEED

    def writeCmd(self, bot_servo: BotServos, target: int = TARGET_CENTER):
        # Build command
        lsb = target & 0x7F
        msb = (target >> 7) & 0x7F
        servo_chr = bot_servo.value
        cmd = chr(0xaa) + chr(0xC) + chr(0x04) + chr(servo_chr) + chr(lsb) + chr(msb)
        command = cmd.encode('utf-8')
        # Check if usb is not None
        if self.usb is not None:
            log.debug('Writing USB Command: "%s"', command)
            self.usb.write(command)
            sleep(0.2)
        else:
            log.debug('Unable to write to USB - USB not connected')

    """Getters and Setters

    The setter methods are used to condense the necesity to write to the USB each time a servo motor value is changed.
    By creatings setter methods for the servo motor values, when a value is update the change is written to the USD.

    Servo Motor Values:
    -------------------
    "HEAD_TILT"     - This is the up/down positioning for the head servo

    "HEAD_TURN"     - This is the left/right positioning for the head servo

    "WAIST"         - Left/Right positioning for the body/waist servo motor

    "WHEEL_SPEED"   - This value is used for the left and right wheel servos.
                      Note: This value is ony manipulated when going forwards and backwards. See trunLeft() and turnRight() for more details

    "DIRECTION_STATE" - Maintains the active wheel movement operation of the robot. This is necessary because when the robot changes states, for example from Forwards to Backwards, the wheel_speed needs to be centered.
    When changing the DIRECTION_STATE, if the new state is different from the current, the WHEEL_SPEED is centered (i.e. when this happens, the value is also written to the USD)

    """

    # HEAD_TILT
    @property
    def HEAD_TILT(self) -> int:
        return self._HEAD_TILT

    @HEAD_TILT.setter
    def HEAD_TILT(self, val: int):
        # TODO: validate the upper and lower limits for the HEAD_TILT value
        self._HEAD_TILT = val
        log.debug('Set HEAD_TILT: %s', self.HEAD_TILT)
        self.writeCmd(BotServos.HeadTilt, self.HEAD_TILT)

    # HEAD_TRUN
    @property
    def HEAD_TURN(self) -> int:
        return self._HEAD_TURN

    @HEAD_TURN.setter
    def HEAD_TURN(self, val: int):
        # TODO: validate the upper and lower limits for the HEAD_TURN value
        self._HEAD_TURN = val
        log.debug('Set HEAD_TURN: %s', self.HEAD_TURN)
        self.writeCmd(BotServos.HeadPan, self.HEAD_TURN)

    # WAIST
    @property
    def WAIST(self) -> int:
        return self._WAIST

    @WAIST.setter
    def WAIST(self, val: int):
        # TODO: validate the upper and lower limits for the WAIST value
        self._WAIST = val
        log.debug('Set WAIST: %s', self.WAIST)
        self.writeCmd(BotServos.Waist, self.WAIST)

    # WHEEL_SPEED
    @property
    def WHEEL_SPEED(self) -> int:
        return self._WHEEL_SPEED

    @WHEEL_SPEED.setter
    def WHEEL_SPEED(self, val: int):
        # make sure wheel speed does not exceed the upper/lower limit
        if val < self.SPEED_FLOOR:
            # set wheel speed to upper limit for wheels
            val = self.SPEED_FLOOR
        elif val > self.SPEED_CEILING:
            # set wheel speed to lower limit for wheels
            val = self.SPEED_CEILING
        self._WHEEL_SPEED = val
        log.debug('Set WHEEL_SPEED: %s', self.WHEEL_SPEED)
        self.writeCmd(BotServos.RightWheel, self.WHEEL_SPEED)
        self.writeCmd(BotServos.LeftWheel, self.WHEEL_SPEED)

    # DIRECTION_STATE
    @property
    def DIRECTION_STATE(self):
        return self._DIRECTION_STATE

    @DIRECTION_STATE.setter
    def DIRECTION_STATE(self, val: DirectionState):
        if isinstance(val, DirectionState) and isinstance(self._DIRECTION_STATE, DirectionState) and self._DIRECTION_STATE != val:
            self.WHEEL_SPEED = self.TARGET_CENTER
        self._DIRECTION_STATE = val

    """Speed Movement Methods"""

    def stop(self):
        self.WHEEL_SPEED = self.TARGET_CENTER

    def setSpeed(self, speed: int):
        self.SPEED = speed

    def setSpeedLevelOne(self):
        self.setSpeed(300)

    def setSpeedLevelTwo(self):
        self.setSpeed(500)

    def setSpeedLevelThree(self):
        self.setSpeed(800)

    """HEAD Movement Methods"""

    def moveHeadUp(self):
        self.HEAD_TILT += self.SPEED

    def moveHeadDown(self):
        self.HEAD_TILT -= self.SPEED

    def moveHeadLeft(self):
        self.HEAD_TURN += self.SPEED

    def moveHeadRight(self):
        self.HEAD_TURN -= self.SPEED

    def centerHead(self):
        self.HEAD_TURN = self.TARGET_CENTER
        self.HEAD_TILT = self.TARGET_CENTER

    """WAIST Movement Methods"""

    def centerWaist(self):
        self.WAIST = self.TARGET_CENTER

    def moveWaistLeft(self):
        self.WAIST += self.SPEED

    def moveWaistRight(self):
        self.WAIST -= self.SPEED

    """WHEEL Movement Methods"""

    def increaseWheelSpeed(self):
        self.DIRECTION_STATE = DirectionState.Forwards
        self.WHEEL_SPEED -= self.SPEED

    def decreaseWheelSpeed(self):
        self.DIRECTION_STATE = DirectionState.Backwards
        self.WHEEL_SPEED += self.SPEED
        self.writeCmd(BotServos.LeftWheel, self.WHEEL_SPEED)

    def turnLeft(self):
        self.DIRECTION_STATE = DirectionState.LeftTurn
        self.writeCmd(BotServos.RightWheel, 7400)
        self.stop()

    def turnRight(self):
        self.DIRECTION_STATE = DirectionState.RightTurn
        self.writeCmd(BotServos.RightWheel, 4600)
        self.stop()

# END
