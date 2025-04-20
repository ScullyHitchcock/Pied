import sys
import re
from collections import namedtuple

def parse_single_command(cmd_text: str) -> dict:
    result = {
        "addr1": None,
        "addr2": None,
        "cmd": None,
        "args": None,
        "label_name": None,
        "branch_label": None,
    }

    i = 0
    L = len(cmd_text)

    def parse_addr():
        nonlocal i
        if cmd_text[i] == '/':
            # parse /.../
            i += 1
            start = i
            while i < L and cmd_text[i] != '/':
                if cmd_text[i] == '\\' and i + 1 < L:
                    i += 2
                else:
                    i += 1
            addr = '/' + cmd_text[start:i] + '/'
            i += 1
            return addr.strip()
        elif cmd_text[i] == '$':
            i += 1
            return '$'
        elif cmd_text[i].isdigit():
            start = i
            while i < L and cmd_text[i].isdigit():
                i += 1
            return cmd_text[start:i]
        return None

    # extract addr1
    if i < L and (cmd_text[i] == '/' or cmd_text[i].isdigit() or cmd_text[i] == '$'):
        result["addr1"] = parse_addr()
        # check for comma and addr2
        if i < L and cmd_text[i] == ',':
            i += 1
            result["addr2"] = parse_addr()
    if i < L:
        result["cmd"] = cmd_text[i]
        i += 1

    # rest is command-specific
    rest = cmd_text[i:]

    if result["cmd"] == ':':
        result["label_name"] = rest
    elif result["cmd"] in ('b', 't'):
        result["branch_label"] = rest or None
    elif result["cmd"] == 's':
        # parse s/pat/repl/flags
        if rest:
            delim = rest[0]
            parts = rest[1:].split(delim)
            result["args"] = tuple(parts)
    elif result["cmd"] in ('a', 'i', 'c'):
        result["args"] = rest

    return result

def separate_cmd_txt(long_txt: str) -> list:
    # 将长命令文本中的每一条语句拆分出来装入列表
    cmd_txt = ''
    cmds = []
    i = 0
    length = len(long_txt)
    while i < length:
        if long_txt[i] == '/':
            addr = ''
            # 如果当前字符是 / 则不断组装字符直到组装到下一个 / 后停止
            # 最终 res 内应该是 '/[any]/' 的格式
            while addr.count('/') < 2:
                addr += long_txt[i]
                i += 1
            cmd_txt += addr
        elif long_txt[i] == 's':
            # 如果当前字符是 s
            # 取 s 下一位字符标记为 separator 分隔符，最终 res 内应该是 's[separator][any][separator][any][separator]' 的格式
            cmd_txt += long_txt[i]
            i += 1
            s_separator = long_txt[i]
            while s_separator == ' ':
                i += 1
                s_separator = long_txt[i]
            sub_args = ''
            while sub_args.count(s_separator) < 3:
                sub_args += long_txt[i]
                i += 1
            cmd_txt += sub_args
        elif long_txt[i] in ('t', 'b', ':'):
            # 当字符是标签语句开头，组装字符直到当前语句结束（遇到 ; ）或到达字符串末尾
            while i < length and long_txt[i] not in (';', '\n'):
                if long_txt[i] != ' ':
                    cmd_txt += long_txt[i]
                i += 1
        elif long_txt[i] == ' ':
            # 当字符是空格键，不组装，跳过
            i += 1
        elif long_txt[i] == '#':
            # 当字符是 #，跳过不组装直到当前语句结束（遇到 ; ）或到达字符串末尾
            while i < length and long_txt[i] not in (';', '\n'):
                i += 1
        elif long_txt[i] in (';', '\n'):
            # 当字符是 ; 或 \n 语句结束符，储存当前语句 txt，继续循环
            if cmd_txt:
                cmds.append(cmd_txt)
            i += 1
            cmd_txt = ''
        else:
            # 当字符是普通字符，直接组装
            cmd_txt += long_txt[i]
            i += 1
    if cmd_txt:
        # 循环结束后如果 cmd_txt 不为空则储存
        cmds.append(cmd_txt)
    return cmds

def input_lines(files: list[str]):
    pass

def run_pied(line, cmd_lst):
    pass

def output(res, i_flag, n_flag):
    pass

def main():
    # 读取命令列表，解析 -i -n -f 指令
    args = sys.argv[1:]
    i_flag = False
    n_flag = False
    script_file = None
    inline_cmd = None

    # 1. -i
    if args and args[0] == '-i':
        i_flag = True
        args.pop(0)

    # 2. -n
    if args and args[0] == '-n':
        n_flag = True
        args.pop(0)

    # 3. -f foo.pied OR inline_cmd
    if args and args[0] == '-f':
        script_file = args[1]
        args = args[2:]
    else:
        inline_cmd = args[0]
        args = args[1:]

    # 4. 剩下 args 都是文件列表
    files = args

    # 读取脚本命令
    if script_file:
        with open(script_file, 'r') as f:
            script_txt = f.read()
    else:
        script_txt = inline_cmd

    cmd_txt_list = separate_cmd_txt(script_txt)
    cmd_lst = [parse_single_command(cmd_txt) for cmd_txt in cmd_txt_list]

    # 构建输入生成器
    input_data = input_lines(files)
    for line in input_data:
        res = run_pied(line, cmd_lst)
        output(res, i_flag, n_flag)

if __name__ == '__main__':
    main()