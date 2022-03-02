# tango_bot.py

from .usb import serial, getUSB

class TangBotController:

    # properties
    usb : serial.Serial = None

    # constructor
    def __init__(self):
        self.usb = getUSB()

# END
