'''
River Kelly
Alex Fischer
Kyler Gappa
CSCI-455: Embedded Systems (Robotics)
Spring 2022
'''

from src import KeyBindings, TangBotController

if __name__ == "__main__":
    bot_controller = TangBotController()
    key_bindings = KeyBindings(bot_controller)
    key_bindings.start()

# END main.py
