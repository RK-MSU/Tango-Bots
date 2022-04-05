# dialog.py

import os
import re
from .log import log

class Command:
    children: list = list()
    parent = None
    level: int = 0
    command: str
    response: str
    def __init__(self, lvl, command: str, response: str):
        self.level = lvl
        self.command = command
        self.response = response

class Dialog:

    lines: list = list()
    commands: list = list()

    def __init__(self, file: str = 'dialog.txt'):
        self.readFile(file)
        self.parseInstructions()
        for cmd in self.commands:
            print(cmd.level, len(cmd.children))

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
        last_command: Command = None
        for line in self.lines:
            # TODO: parse environment variables - (i.e. take the form "~{var}:[params...]") - Example: ~greetings: [hello howdy "hi there"]
            result = re.search(r'~(\w)\s*:\s*()', line)
            # parsing user commands - (i.e. take the form 'u#:(command):response')
            result = re.search(r'(u\d*)\s*:\s*\(([\w\s~]+)\)\s*:\s*(.+)', line)
            if result is not None:
                grps = result.groups()
                # get command level integer
                lvl = 0
                lvl_result = re.search(r'[u](\d+)', grps[0])
                if lvl_result == None: lvl = 0
                else:
                    lvl_span = lvl_result.span()
                    lvl = int(grps[0][lvl_span[0]+1:lvl_span[1]])
                command_str = grps[1]
                response_str = grps[2]
                # create a new command
                command = Command(lvl, command_str, response_str)
                if last_command is not None and command.level == last_command.level:
                    command.parent = last_command.parent
                elif last_command is not None and command.level == last_command.level + 1:
                    last_command.children.append(command)
                    command.parent = last_command
                last_command = command
                if command.level == 0:
                    self.commands.append(command)

# END
