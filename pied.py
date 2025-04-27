#!/usr/bin/env python3
import shutil
import sys
import re
import tempfile
from collections import deque

class Line:
    def __init__(self, filename, line_txt, next_line_txt, line_num):
        self.filename = filename
        self.contents = line_txt
        self.next_line_txt = next_line_txt
        self.line_num = line_num
        self.edge_cmds = set()

    def modify_contents(self, new_contents=None):
        self.contents = new_contents

    def is_last(self):
        return self.next_line_txt == ''

    def on_edge_of(self, cmd):
        if cmd in self.edge_cmds or self.is_last():
            return True
        if cmd.addr2.is_empty():
            return cmd.addr1.match(self)
        return False

    def __str__(self):
        return f"<File: {self.filename} Line {self.line_num}: '{self.contents}'>"

    def is_beyond(self, address) -> bool:
        if address.is_digit():
            return self.line_num > int(address.addr)
        return False

class Result:
    def __init__(self, line: Line, n_flag: bool, i_flag: bool, temp_file: str):
        self.line = line
        self.n_flag = n_flag
        self.i_flag = i_flag
        self.in_c_cmd_range = False
        self.after_queue = deque()
        self.last_special_cmd = None
        self.substituted = False
        self.deleted = False
        self.temp_file = temp_file

    def save_to_temp_file(self, txt):
        with open(self.temp_file, mode='a', encoding='utf-8') as f:
            f.write(txt + '\n')

    def suppress_output_by_c(self):
        self.in_c_cmd_range = True

    def is_substituted(self):
        return self.substituted

    def is_suppressed(self):
        return (self.n_flag or
                self.deleted or
                self.in_c_cmd_range)

    def delete_line(self):
        self.deleted = True
        self.line.modify_contents()

    def substitute_line(self, new_txt):
        self.line.modify_contents(new_txt)
        self.substituted = True

    def add_after_order(self, cmd):
        self.after_queue.appendleft(cmd)

    def mark_special_cmd(self, cmd):
        self.last_special_cmd = cmd

    def reset_status(self):
        self.substituted = False
        self.last_special_cmd = None

    def regular_output(self):
        self.output(self.line.contents)

    def after_output(self):
        while self.after_queue:
            cmd = self.after_queue.pop()
            match cmd.type:
                case 'q':
                    sys.exit(0)
                case 'a':
                    appended_line = cmd.args
                    self.output(appended_line)

    def output(self, line_txt):
        if line_txt is not None:
            if self.i_flag:
                self.save_to_temp_file(line_txt)
            else:
                print(line_txt)

class Script:
    def __init__(self, script_texts):
        self.cmd_list = []
        cmd_txt_list = self.separate_script_txt(script_texts)
        for cmd_txt in cmd_txt_list:
            self.cmd_list.append(Command(cmd_txt))

    def __len__(self):
        return len(self.cmd_list)

    @staticmethod
    def separate_script_txt(script_texts):
        cmd_txt = ''
        cmds = []
        i = 0
        length = len(script_texts)
        while i < length:
            if script_texts[i] == '/':
                addr = ''
                while addr.count('/') < 2:
                    addr += script_texts[i]
                    i += 1
                cmd_txt += addr
            elif script_texts[i] == 's':
                cmd_txt += script_texts[i]
                i += 1
                delim = script_texts[i]
                while delim == ' ':
                    i += 1
                    delim = script_texts[i]
                sub_args = ''
                while sub_args.count(delim) < 3:
                    sub_args += script_texts[i]
                    i += 1
                cmd_txt += sub_args
            elif script_texts[i] in ('t', 'b', ':'):
                while i < length and script_texts[i] not in (';', '\n'):
                    if script_texts[i] != ' ':
                        cmd_txt += script_texts[i]
                    i += 1
            elif script_texts[i] == ' ':
                i += 1
            elif script_texts[i] == '#':
                while i < length and script_texts[i] not in (';', '\n'):
                    i += 1
            elif script_texts[i] in (';', '\n'):
                if cmd_txt:
                    cmds.append(cmd_txt)
                i += 1
                cmd_txt = ''
            else:
                cmd_txt += script_texts[i]
                i += 1
        if cmd_txt:
            cmds.append(cmd_txt)
        return cmds

    def process(self, result: Result):
        i, l = 0, len(self.cmd_list)
        while i < l:
            cmd = self.cmd_list[i]
            if cmd.match(result.line):
                cmd.process(result)
                i = self.jump_to_next(result, i)
            else:
                i += 1

    def jump_to_next(self, result: Result, i: int):
        special_cmd = result.last_special_cmd
        if special_cmd is not None:
            if special_cmd.type in ('d', 'q'):
                i = self.__len__()
            elif special_cmd.type in ('t', 'b'):
                label = special_cmd.label
                for next_i, cmd in enumerate(self.cmd_list):
                    if cmd.type == ':' and cmd.label == label:
                        i = next_i
                        break
            result.reset_status()
            return i
        return i + 1

class Command:
    def __init__(self, cmd_txt):
        self.cmd_txt = cmd_txt
        cmd_info = self.parse_command(cmd_txt)
        addr1, addr2 = cmd_info["addr1"], cmd_info["addr2"]
        self.addr1 = Address(addr1)
        self.addr2 = Address(addr2)
        self.type = cmd_info["cmd"]
        self.label = cmd_info["label"]
        self.args = cmd_info["args"]
        self.in_range = False

    def __str__(self):
        return f"Command: {self.cmd_txt}"

    @staticmethod
    def parse_command(cmd_txt):
        result = {
            "addr1": None,
            "addr2": None,
            "cmd": None,
            "args": None,
            "label": None,
        }
        i = 0
        length = len(cmd_txt)
        def parse_addr():
            nonlocal i
            if cmd_txt[i] == '/':
                i += 1
                start = i
                while i < length and cmd_txt[i] != '/':
                    if cmd_txt[i] == '\\' and i + 1 < length:
                        i += 2
                    else:
                        i += 1
                addr = '/' + cmd_txt[start:i] + '/'
                i += 1
                return addr.strip()
            elif cmd_txt[i] == '$':
                i += 1
                return '$'
            elif cmd_txt[i].isdigit():
                start = i
                while i < length and cmd_txt[i].isdigit():
                    i += 1
                return cmd_txt[start:i]
            return None
        if i < length and (cmd_txt[i] == '/' or cmd_txt[i].isdigit() or cmd_txt[i] == '$'):
            result["addr1"] = parse_addr()
            if i < length and cmd_txt[i] == ',':
                i += 1
                result["addr2"] = parse_addr()
        if i < length:
            result["cmd"] = cmd_txt[i]
            i += 1
        rest = cmd_txt[i:]
        def parse_substitute(rest: str):
            delim = rest[0]
            i = 1
            parts = []
            current = ''
            while i < len(rest):
                ch = rest[i]
                if ch == '\\' and i + 1 < len(rest):
                    current += rest[i:i + 2]
                    i += 2
                elif ch == delim:
                    if '\\' + delim in current:
                        current = re.sub(r'\\(.)', r'\1', current)
                    parts.append(current)
                    current = ''
                    i += 1
                    if len(parts) == 2:
                        parts.append(rest[i:])
                        break
                else:
                    current += ch
                    i += 1
            return tuple(parts)
        if result["cmd"] in ('b', 't', ':'):
            result["label"] = rest or None
        elif result["cmd"] == 's':
            if rest:
                result["args"] = parse_substitute(rest)
        elif result["cmd"] in ('a', 'i', 'c'):
            result["args"] = rest
        return result

    def substitute(self, line: str) -> str:
        if self.type == 's':
            pattern, repl, modifier = self.args
            count = 0 if modifier else 1
            new_line = re.sub(pattern, repl, line, count=count)
            return new_line
        return line

    def match(self, line: Line) -> bool:
        if self.addr1.is_empty():
            return True
        if self.addr2.is_empty():
            return self.addr1.match(line)
        if self.in_range:
            if self.addr2.match(line):
                line.edge_cmds.add(self)
                self.in_range = False
                return True
            if self.addr2.is_regex():
                return True
            if line.is_beyond(self.addr2):
                if self.addr1.match(line):
                    return True
                self.in_range = False
                return False
            return True
        else:
            if self.addr1.match(line):
                self.in_range = True
                return True
            return False

    def process(self, result: Result):
        cur_line = result.line.contents
        match self.type:
            case 'p':
                result.output(cur_line)
            case 'q':
                result.add_after_order(self)
                result.mark_special_cmd(self)
            case 'd':
                result.delete_line()
                result.mark_special_cmd(self)
            case 's':
                sub_line = self.substitute(cur_line)
                if sub_line != cur_line:
                    result.substitute_line(sub_line)
            case 'a':
                result.add_after_order(self)
            case 'i':
                insert_txt = self.args
                result.output(insert_txt)
            case 'c':
                change_txt = self.args
                result.suppress_output_by_c()
                if result.line.on_edge_of(self):
                    result.output(change_txt)
            case 't':
                if result.is_substituted():
                    result.mark_special_cmd(self)
            case 'b':
                result.mark_special_cmd(self)

class Address:

    def __init__(self, addr):
        if addr is None:
            self.addr = ''
        else:
            self.addr = addr

    def __str__(self):
        if self.is_digit():
            type = 'Digit'
        elif self.is_regex():
            type = 'Regex'
        elif self.is_special_char():
            type = 'Last Line'
        else:
            type = 'Empty'
        return f"{type}: {self.addr}"

    def is_digit(self) -> bool:
        return self.addr.isdigit()

    def is_regex(self) -> bool:
        return self.addr.startswith('/') and self.addr.endswith('/')

    def is_special_char(self) -> bool:
        return self.addr == '$'

    def is_empty(self) -> bool:
        return self.addr == ''

    def match(self, line: Line) -> bool:
        txt = line.contents
        if self.is_digit():
            return int(self.addr) == line.line_num
        if self.is_regex():
            pattern = self.addr[1:-1]
            return re.search(pattern, txt) is not None
        if self.is_special_char():
            return line.is_last()
        return False

def line_generator(input: list | str | None) -> iter:
    def file_reader(filename) -> iter:
        with open(filename, 'r') as f:
            for line in f:
                yield line.rstrip('\n')
    def line_iterator() -> iter:
        if not input:
            for line in sys.stdin:
                yield 'stdin', line.rstrip('\n')
        elif isinstance(input, str):
            for line in file_reader(input):
                yield input, line
        elif isinstance(input, list):
            for file in input:
                for line in file_reader(file):
                    yield file, line

    it = line_iterator()
    try:
       filename, cur_line = next(it)
    except StopIteration:
        return

    line_num = 1
    for next_filename, next_line in it:
        yield Line(filename, cur_line, next_line, line_num)
        cur_line = next_line
        line_num += 1
        filename = next_filename

    yield Line(filename, cur_line, '', line_num)  # 最后一行

class PiedExecutor:
    def __init__(self, line_gen: iter, script: Script, i_flag: bool, n_flag: bool):
        self.line_gen = line_gen
        self.script = script
        self.i_flag = i_flag
        self.n_flag = n_flag

    @staticmethod
    def temp_file():
        temp = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        temp_name = temp.name
        temp.close()
        return temp_name

    def execute(self):
        temp_file = self.temp_file() if self.i_flag else None
        input_file = None
        for line in self.line_gen:
            input_file = line.filename
            result = Result(line, self.n_flag, self.i_flag, temp_file)
            self.script.process(result)

            if not result.is_suppressed():
                result.regular_output()

            result.after_output()

        if temp_file and input_file:
            shutil.move(temp_file, input_file)

def parse_cmd_line_args(args: list) -> tuple[bool, bool, str, list[str]]:
    i_flag = False
    n_flag = False
    script_txt = None
    input_files_lst = []

    # 1. -i
    if args and args[0] == '-i':
        i_flag = True
        args.pop(0)

    # 2. -n
    if args and args[0] == '-n':
        n_flag = True
        args.pop(0)

    if args:
        # 3. -f foo.pied OR inline_cmd
        if args and args[0] == '-f':
            script_filename = args[1]
            with open(script_filename, 'r') as f:
                script_txt = f.read()
            input_files_lst = args[2:]
        else:
            script_txt = args[0]
            input_files_lst = args[1:]

    return i_flag, n_flag, script_txt, input_files_lst

def main():
    args = sys.argv[1:]
    i_flag, n_flag, script_txt, input_files_lst = parse_cmd_line_args(args)
    if not script_txt:
        return
    script = Script(script_txt)

    def execute(input):
        line_gen = line_generator(input)
        pied = PiedExecutor(line_gen, script, i_flag, n_flag)
        pied.execute()

    if i_flag and input_files_lst:
        for input_filename in input_files_lst:
            execute(input_filename)
    else:
        execute(input_files_lst)

if __name__ == '__main__':
    main()