#!/usr/bin/env python3
import sys
import re

def parse_args():
    """解析命令行参数，返回 (suppress_output: bool, command_str: str)"""
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
    - cmd: 'd', 'p', 'q', or 's'
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
    """判断当前行是否匹配地址"""
    if address_type is None:
        return True
    elif address_type == "line":
        return line_num == address_value
    elif address_type == "regex":
        return re.search(address_value, line) is not None
    return False

def process_line(line, line_num, cmd, cmd_arg, suppress_output):
    """执行具体命令逻辑"""
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
    suppress_output, command_str = parse_args()
    address_type, address_value, cmd, cmd_arg = parse_command(command_str)

    for line_num, line in enumerate(sys.stdin, 1):
        line = line.rstrip('\n')

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