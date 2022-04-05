# dialog.py

import os
from .log import log

class Dialog:

    lines: list = list()

    def __init__(self, file: str = 'dialog.txt'):
        self.readFile(file)
        print(self.lines)

    def readFile(self, file: str):
        if os.path.exists(file):
            with open(file, 'r') as file:
                self.lines = file.readlines()
            # clean lines by stripping whitespace
            for index, line in enumerate(self.lines):
                self.lines[index] = str(line).strip()
        else:
            log.critical('Unable to open "%s"', file)

# END
