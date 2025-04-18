#!/usr/bin/env python3
import sys
import re

class Commands:
    """ sed [-n] '[address][command][optional-args]' """
    def __init__(self, *args):
        cmd = args[1:]
        self.has_n = True if cmd[0] == "-n" else False
        self.rest_cmd = [arg for arg in cmd if arg != "-n"]
        self.address = self.address()
        self.command = self.command()
        self.optional_args = self.optional_args()

    def address(self) -> str or None:
        # 通过 self.rest_cmd 求出 address
        # 没有则返回 None
        pass

    def command(self) -> str or None:
        # 通过 self.rest_cmd 求出 command
        # 没有则返回 None
        pass

    def optional_args(self) -> str or None:
        # 通过 self.rest_cmd 求出 optional-args
        # 没有则返回 None
        pass

    def match(self, line: str, line_num: int) -> bool:
        if self.address.isdigit():
            ...
        else:
            ...


def parse_args():
    """
    解析命令行参数，返回 (suppress_output: bool, command_str: str)

    :return:
        suppress_output: bool - 是否抑制输出
        command_str: str - 命令字符串
    """
    args = sys.argv[1:]
    if not args:
        print("Usage: pied.py [-n] 'command'")
        sys.exit(1)

    suppress_output = False
    if args[0] == "-n":
        suppress_output = True
        args = args[1:]

    if len(args) != 1:
        print("Invalid number of arguments.")
        sys.exit(1)

    return suppress_output, args[0]

def parse_command(command_str):
    """
    拆解地址 + 命令部分
    返回：(address_type, address_value, cmd, cmd_arg)

    - address_type: 'line', 'regex', or None
    - address_value: int or str - 地址的具体值
    - cmd: str - 命令字符，'d', 'p', 'q', or 's'
    - cmd_arg: tuple or None - 命令参数（对于 's' 命令，包含 pattern, replacement, modifier）

    :param command_str: str - 命令字符串
    :return: tuple - 包含地址类型、地址值、命令和命令参数的四元组
    """
    address_type = None
    address_value = None
    cmd_part = command_str

    if command_str[0].isdigit():
        # 行号地址，如 5d
        i = 0
        while i < len(command_str) and command_str[i].isdigit():
            i += 1
        address_type = "line"
        address_value = int(command_str[:i])
        cmd_part = command_str[i:]
    elif command_str.startswith("/") and "/".encode() in command_str.encode()[1:]:
        # 正则地址，如 /abc/d
        end = command_str.find("/", 1)
        address_type = "regex"
        address_value = command_str[1:end]
        cmd_part = command_str[end + 1:]

    if cmd_part.startswith("s/"):
        parts = cmd_part.split("/")
        # ['s', pattern, replacement, optional 'g']
        if len(parts) < 4:
            raise ValueError("Invalid substitution format")
        cmd = 's'
        pattern = parts[1]
        replacement = parts[2]
        modifier = parts[3] if len(parts) > 3 else ''
        cmd_arg = (pattern, replacement, modifier)
    else:
        cmd = cmd_part
        cmd_arg = None

    return address_type, address_value, cmd, cmd_arg

def address_matches(address_type, address_value, line_num, line):
    """
    判断当前行是否匹配地址

    :param address_type: str or None - 地址类型
    :param address_value: int or str - 地址值
    :param line_num: int - 当前行号
    :param line: str - 当前行内容
    :return: bool - 当前行是否匹配地址
    """
    if address_type is None:
        return True
    elif address_type == "line":
        return line_num == address_value
    elif address_type == "regex":
        return re.search(address_value, line) is not None
    return False

def process_line(line, line_num, cmd, cmd_arg, suppress_output):
    """
    执行具体命令逻辑

    :param line: str - 当前行内容
    :param line_num: int - 当前行号
    :param cmd: str - 命令字符
    :param cmd_arg: tuple or None - 命令参数
    :param suppress_output: bool - 是否抑制输出
    :return: str or None - 处理结果，若为 None 则表示删除行
    """
    output_line = line

    if cmd == 'd':
        return None  # 删除行，不输出

    if cmd == 'p':
        return line  # 打印行（-n 控制是否默认输出）

    if cmd == 'q':
        print(line)  # q 会在匹配行输出后退出
        sys.exit(0)

    if cmd == 's':
        pattern, repl, modifier = cmd_arg
        count = 0 if modifier == 'g' else 1
        return re.sub(pattern, repl, line, count=count)

    return output_line  # 默认直接返回

def main():
    """
    负责执行程序主逻辑，按命令行输入处理 stdin 中的每一行。

    :return: None
    """

    # suppress_output：命令是否带“-n”
    # cmd：除了“-n”命令外的其余命令
    # parse_args() 作用：把输入命令中的“-n”命令与其他命令分割开
    suppress_output, cmd = parse_args()
    address_type, address_value, cmd, cmd_arg = parse_command(cmd)


    # validate(args)
    for line_num, line in enumerate(sys.stdin, 1):
        line = line.rstrip('\n')

        # if args.match(line, line_num):
        #   process(args, line)
        #   if process is delete:
        #       continue
        # if "-n" is not in args:
        #   print(line)



        # 判断是否匹配地址
        if address_matches(address_type, address_value, line_num, line):
            result = process_line(line, line_num, cmd, cmd_arg, suppress_output)
            if result is not None:
                print(result)
        else:
            if not suppress_output:
                print(line)

if __name__ == '__main__':
    main()