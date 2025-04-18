#!/usr/bin/env python3
import sys
import re


class Commands:
    """ sed [-n] '[address][command][optional-args]' """
    def __init__(self, args, lines):
        if args:
            self.address_str = self._address(args)
            self.command = self._command(args)
            self.optional_args = self._optional_args(args)
        else:
            self.address_str, self.command, self.optional_args = None, None, None

    def address_range(self, lines: list) -> range:
        # 传入地址字符串
        return self._get_addr(self.address_str, lines)

    def _address(self, cmd: str) -> str:
        # 拆解出原生地址字符串
        # 例：_parse_addr('3,/2/d') -> '3,/2/'，_parse_addr('/1$/,/^2/d') -> '/1$/,/^2/'
        # _parse_addr('q') -> ''...
        pass

    def _get_addr(self, add_str: str, lines: list) -> range:
        pass

    def _command(self, cmd: str) -> str or None:
        # 传入 cmd_str 把 command 拆出来
        # 去掉 address 部分
        if self.address_str:
            if cmd[0].isdigit():
                cmd = cmd[len(self.address_str):]
            else:
                cmd = cmd[cmd.find("/", 1) + 1:]
        if cmd.startswith("s"):
            return "s"
        if cmd and cmd[0] in "dpq":
            return cmd[0]
        return None

    def _optional_args(self, cmd: str) -> list or None:
        # 传入 cmd_str 把 optional_args 拆出来
        if self.command != "s":
            return None
        # 找到 s 命令部分
        s_index = cmd.find("s")
        if s_index == -1:
            return None
        split_str = cmd[s_index + 1]
        parts = cmd[s_index + 1:].split(split_str)
        if len(parts) < 3:
            return None
        pattern = re.compile(parts[1])
        replacement = parts[2]
        modifier = parts[3] if len(parts) > 3 else ""
        return [pattern, replacement, modifier]

    def match(self, line: str, line_num: int) -> bool:
        if isinstance(self.address_str, range):
            return line_num in self.address_str
        elif isinstance(self.address_str, re.Pattern):
            return re.search(self.address_str, line) is not None
        else:
            return True


def process(cmds: Commands, line: str, has_n: bool) -> str or None:
    if cmds.command == "p":
        print(line)
        return line
    elif not has_n:
        match cmds.command:
            case "q":
                print(line)
                sys.exit(0)
            case "d":
                return
            case "s":
                return process_s(cmds, line)

def process_s(cmds: Commands, line: str) -> str:
    pattern, repl, modifier = cmds.optional_args
    count = 0 if modifier else 1
    line = re.sub(pattern, repl, line, count=count)
    return line
    # print(line)

def parse(args: list[str]) -> tuple[bool, list]:
    has_n = False
    cmds = []
    if "-n" in args:
        has_n = True
        args = args[1:]
    if args:
        cmd_str = args[0]
        spliter = ';' if ';' in cmd_str else '\n'
        cmds = cmd_str.split(spliter)
    return has_n, cmds

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
    has_n, cmd_str = parse(stdin)
    lines = sys.stdin.readlines()
    cmds = [Commands(cmd, lines) for cmd in cmd_str]
    for line_num, line in enumerate(sys.stdin, 1):
        line = line.rstrip('\n')
        for cmd in cmds:
            if cmd.match(line, line_num):
                line = process(cmd, line, has_n)
        if not has_n and line:
            print(line)

if __name__ == '__main__':
    main()