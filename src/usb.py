# usb.py

import serial

def getUSB():
    usb = None
    usb_name = '/dev/ttyACM0'
    try:
        usb = serial.Serial(usb_name)
    except:
        print('Unable to get USD: {!s}'.format(usb_name))
        usb = None
    if usb is None:
        usb_name = '/dev/ttyACM1'
        try:
            usb = serial.Serial(usb_name)
        except:
            print('Unable to get USD: {!s}'.format(usb_name))
            usb = None
    if usb is not None:
        print('USB:\n- name: "{!s}"\n- baudrate: "{!s}"'.format(usb.name, usb.baudrate))
    else:
        print('ERROR: Unable to get USB Serial')
    # return usb (serial)
    return usb

# END
