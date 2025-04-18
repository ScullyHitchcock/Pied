#!/usr/bin/env python3
import sys
import re


class Commands:
    """ sed [-n] '[address][command][optional-args]' """
    def __init__(self, args):
        self.has_n = True if args[0] == "-n" else False
        cmd_lst = args[1:] if self.has_n else args
        if cmd_lst:
            self.address = self._address(cmd_lst[0])
            self.command = self._command(cmd_lst[0])
            self.optional_args = self._optional_args(cmd_lst[0])
        else:
            self.address, self.command, self.optional_args = None, None, None

    def _address(self, cmd: str) -> str or re.Pattern or None:
        # 传入 cmd_str 把 address 拆出来
        if cmd[0].isdigit():
            i = 0
            while i < len(cmd) and cmd[i].isdigit():
                i += 1
            return cmd[:i]
        elif cmd.startswith("/") and "/" in cmd[1:]:
            end = cmd.find("/", 1)
            pattern_str = cmd[1:end]
            return re.compile(pattern_str)
        return None

    def _command(self, cmd: str) -> str or None:
        # 传入 cmd_str 把 command 拆出来
        # 去掉 address 部分
        if self.address:
            if cmd[0].isdigit():
                cmd = cmd[len(self.address):]
            else:
                cmd = cmd[cmd.find("/", 1) + 1:]
        if cmd.startswith("s/"):
            return "s"
        if cmd and cmd[0] in "dpq":
            return cmd[0]
        return None

    def _optional_args(self, cmd: str) -> list or None:
        # 传入 cmd_str 把 optional_args 拆出来
        if self.command != "s":
            return None
        # 找到 s 命令部分
        s_index = cmd.find("s/")
        if s_index == -1:
            return None
        parts = cmd[s_index:].split("/")
        if len(parts) < 3:
            return None
        pattern = re.compile(parts[1])
        replacement = parts[2]
        modifier = parts[3] if len(parts) > 3 else ""
        return [pattern, replacement, modifier]

    def match(self, line: str, line_num: int) -> bool:
        if not self.address:
            return True
        # 如果匹配返回 True 否则 False
        if type(self.address) == str:
            return int(self.address) == line_num
        else:
            return re.search(self.address, line) is not None

def process(cmds: Commands, line: str) -> None:
    if cmds.command == "p":
        print(line)
    elif not cmds.has_n:
        match cmds.command:
            case "q":
                print(line)
                sys.exit(0)
            case "d":
                return
            case "s":
                process_s(cmds, line)

def process_s(cmds: Commands, line: str) -> None:
    pattern, repl, modifier = cmds.optional_args
    count = 0 if modifier else 1
    line = re.sub(pattern, repl, line, count=count)
    print(line)

def validate(args: list) -> None:
    if not args:
        print("Usage: pied.py [-n] 'command'")
        sys.exit(1)
    if len(args) > 2:
        print("Invalid number of arguments.")
        sys.exit(1)

def main():
    """
    负责执行程序主逻辑，按命令行输入处理 stdin 中的每一行。

    :return: None
    """
    stdin = sys.argv[1:]
    validate(stdin)
    cmds = Commands(stdin)
    for line_num, line in enumerate(sys.stdin, 1):
        line = line.rstrip('\n')

        if cmds.match(line, line_num):
            process(cmds, line)
            if cmds.command in ["d", "s"]:
                continue

        if not cmds.has_n:
            print(line)

if __name__ == '__main__':
    main()