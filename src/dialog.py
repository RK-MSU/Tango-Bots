# dialog.py

import os
import re
from .log import log

class Command:
    # properties
    children: list = list()
    parent = None
    level: int = 0
    command: str
    response: str
    command_has_vars: bool = False

    # constructor
    def __init__(self, lvl, command: str, response: str):
        self.level = lvl
        self.command = command
        self.response = response
        if re.search("_", self.command):
            self.command_has_vars = True

    # return false if it does not match
    # returns the response string if there is a match
    def matches(self, cmd: str):
        if self.command_has_vars is False:
            if self.command == cmd:
                return self.responseString()
            else:
                return False
        # command has variables, so check them
        temp_command_re = self.command.replace('_', '([\w]+)')
        result = re.match(temp_command_re, cmd)
        if result is not None:
            vars = result.groups()
            return self.responseString(vars)
        else:
            return False

    def responseString(self, vars: tuple = None):
        response_str = self.response
        vars_count = 0
        while True:
            result = re.search('(\$[\w]+)', response_str)
            if result is None: break
            response_str = response_str.replace(result.groups()[0], vars[vars_count])
            vars_count += 1
        return response_str

class Variable:
    # properties
    name: str
    value: any
    multi_value: bool = False

    # constructor
    def __init__(self, name, value):
        self.name = name
        self.value = value
        # check if variable is a multi-value
        if re.search(r'\[.*\]', self.value) is not None:
            self.value = self.value.strip('[]')
            self.multi_value = True
            self.getMulitValues()

    def getMulitValues(self):
        values = list()
        while True:
            result = re.match(r'([a-zA-Z]+)', self.value)
            if result is None:
                result = re.match(r'"([a-zA-Z\s]+)"', self.value)
            if result is None:
                break
            span = result.span()
            values.append(result.groups()[0])
            self.value = self.value[span[1]:].strip()
            if len(self.value) < 1:
                break
        self.value = values


class Dialog:

    lines: list = list()
    commands: list = list()
    variables: dict = dict()

    def __init__(self, file: str = 'dialog.txt'):
        self.readFile(file)
        self.parseInstructions()

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
            result = re.search(r'~([\w]+)\s*:\s*(.+)', line)
            if result is not None:
                grps = result.groups()
                variable_name = grps[0]
                variable_value = grps[1]
                var = Variable(variable_name, variable_value)
                self.variables[var.name] = var
                continue
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


if __name__ == '__main__':
    cmd = Command(0, 'my name is _', 'hello $name')
    input_str = 'my name is River'
    print(cmd.matches(input_str))

# END
