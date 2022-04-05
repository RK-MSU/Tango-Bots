# dialog.py

import os
import re
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
            cleaned_lines = list()
            for line in self.lines:
                comment_search = re.search('#', line)
                if comment_search is None:
                    cleaned_lines.append(line)
                    continue
                else:
                    span = comment_search.span()
                    if span[0] == 0:
                        continue
                    line = line[ : span[0]].strip()
                    if len(line) > 0:
                        cleaned_lines.append(line)
            self.lines = cleaned_lines
        else:
            log.critical('Unable to open "%s"', file)

# END
