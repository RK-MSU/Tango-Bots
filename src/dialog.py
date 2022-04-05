# dialog.py

import os
import re
from .log import log

class Command:
    children: list
    parent = None
    level: int = 0
    command: str
    response: str
    def __init__(self, lvl: int, command: str, response: str):
        self.level = lvl
        self.command = command
        self.response = response

class Dialog:

    lines: list = list()
    commands: list = list()

    def __init__(self, file: str = 'dialog.txt'):
        self.readFile(file)
        self.parseInstructions()
        print(self.commands)

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

    def parseInstructions(self):
        if len(self.lines) < 1:
            return
        for line in self.lines:
            result = re.search(r'(u\d*)\s*:\s*\(([\w\s~]+)\)\s*:\s*(.+)', line)
            if result is not None:
                grps = result.groups()
                command = Command(grps[0], grps[1], grps[2])
                self.commands.append(command)

# END
