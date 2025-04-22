#!/usr/bin/env python3
import shutil
import sys
import re
import tempfile

def parse_command(cmd_text: str) -> dict:
    result = {
        "addr1": None,
        "addr2": None,
        "cmd": None,
        "args": None,
        "label_name": None,
        "branch_label": None,
    }

    i = 0
    length = len(cmd_text)

    def parse_addr():
        nonlocal i
        if cmd_text[i] == '/':
            # parse /.../
            i += 1
            start = i
            while i < length and cmd_text[i] != '/':
                if cmd_text[i] == '\\' and i + 1 < length:
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
            while i < length and cmd_text[i].isdigit():
                i += 1
            return cmd_text[start:i]
        return None

    # extract addr1
    if i < length and (cmd_text[i] == '/' or cmd_text[i].isdigit() or cmd_text[i] == '$'):
        result["addr1"] = parse_addr()
        # check for comma and addr2
        if i < length and cmd_text[i] == ',':
            i += 1
            result["addr2"] = parse_addr()
    if i < length:
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

def separate_script_txt(long_txt: str) -> list:
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

def read_cmd_txt(file_name: str, inline_cmd) -> str:
    # 读取脚本命令
    if file_name:
        with open(file_name, 'r') as f:
            script_txt = f.read()
    else:
        script_txt = inline_cmd
    return script_txt

def input_generator(i_flag, input_file=None):
    """生成器，输出当前行与下一行的信息：(当前行，下一行)"""
    def line_iterator() -> str:
        if input_file:
            if i_flag:
                with open(input_file, 'r') as f:
                    for line in f:
                        yield line.rstrip('\n')
            else:
                for file in input_file:
                    with open(file, 'r') as f:
                        for line in f:
                            yield line.rstrip('\n')
        else:
            for line in sys.stdin:
                yield line.rstrip('\n')

    it = line_iterator()
    try:
        cur_line = next(it)
    except StopIteration:
        return  # 空输入

    for next_line in it:
        yield cur_line, next_line
        cur_line = next_line

    yield cur_line, ''  # 最后一行

def run_pied(i_flag: bool, n_flag: bool, cmd_lst: list, input_file=None):
    # 根据输入内容 input_file，执行命令链 cmd_lst

    # 1 如果是 -i 模式，则创建临时文件 temp_file，准备接收接下来执行命令后的 output
    temp_file = None
    if i_flag:
        temp_file = creat_temp()

    # 创建内容生成器，按顺序生成两行内容(line1, line2)，如果当前行时最后一行则生成(last_line, '')
    input_gen = input_generator(i_flag, input_file)
    range_state = {}
    for line_num, two_lines in enumerate(input_gen, start=1):
        cur_line = two_lines[0]
        next_line = two_lines[1]
        is_last = True if next_line == '' else False
        # 每次 run_pied 执行时，range_state 独立
        result, output_flags = run(cmd_lst, cur_line, line_num, is_last, n_flag, temp_file, range_state)
        # 把结果 result 传入 output 函数，函数根据 n_flag 和 temp_file 的状态决定输出方式
        output(n_flag, result, output_flags, temp_file)

    # 如果是 -i 模式，则用 temp_file 覆盖原输入文件 input_file
    if input_file and i_flag:
        override(input_file, temp_file)

def run(cmd_lst, cur_line, line_num, is_last, n_flag, temp_file, range_state) -> tuple[str, list]:
    """
    对 cur_line 进行 cmd_lst 处理
    :param cmd_lst: 命令链
    :param cur_line: 要处理的文本
    :param line_num: 文本所在的行数
    :param is_last: 文本是否为最后一行
    :return:
    """
    output_flags = []
    # 按 cmd_lst 顺序对 cur_line 执行 cmd 命令
    i = 0
    l = len(cmd_lst)
    while i < l:
        cur_line, i, output_flags = run_cmd(cur_line, cmd_lst, i, line_num, is_last, output_flags, n_flag, temp_file, range_state)
    return cur_line, output_flags


def run_cmd(cur_line, cmd_lst, i, line_num, is_last, output_flags, n_flag, temp_file, range_state):
    """
    对文本 cur_line 执行 cmd_lst[i] 特定命令，返回三个结果：
    1，处理后的文本
    2，下一个要执行的命令下标
    3，文本是否被处理成功
    :param cur_line: 输入文本
    :param cmd_lst: 命令链
    :param i: 当前执行的命令在命令链中的下标
    :param line_num: 文本信息：文本在总输入的行数
    :param is_last: 文本信息：文本是否为总输入的最后一行
    :param output_flags: 储存提供给 output() 函数的信息
    :return:
        result: 处理后的文本
        next_i: 下一个要执行的命令下标
        output_flags: 储存新加的信息后返回
    """
    if "d" in output_flags:
        return cur_line, i + 1, output_flags
    cmd = cmd_lst[i]
    addr1 = cmd["addr1"]
    addr2 = cmd["addr2"]
    if aadr_matches(cur_line, line_num, is_last, addr1, addr2, range_state):
        match cmd["cmd"]:
        # 识别 cmd 字段，执行不同指令逻辑:
        # 修改 result -> 修改 next_i -> 修改 changed
            case "p":
                output(False, cur_line, [], temp_file)
                i += 1
            case "q":
                output_flags.append(cmd["cmd"])
                i = len(cmd_lst)
            case "d":
                output_flags.append(cmd["cmd"])
                i += 1
            case "s":
                pattern, repl, modifier = cmd["args"]
                count = 0 if modifier else 1
                new_line = re.sub(pattern, repl, cur_line, count=count)
                if new_line != cur_line:
                    output_flags.append(cmd["cmd"])
                    cur_line = new_line
                i += 1
            case "a":
                contents = cmd["args"]
                output_flags.append(("a", contents))
                i += 1
            case "i":
                contents = cmd["args"]
                output(n_flag, contents, [], temp_file)
                i += 1
            case "c":
                contents = cmd["args"]
                cur_line = contents
                i += 1
            case ":":
                i += 1
            case "b":
                label_name = cmd['branch_label']
                # 找到 cmd_lst 中 cmd['label_name'] == label_name 的 cmd 的下标
                #   i = new_i
                # else i += 1
                label_found = False
                for idx, c in enumerate(cmd_lst):
                    if c["cmd"] == ":" and c["label_name"] == label_name:
                        i = idx
                        label_found = True
                        break
                if not label_found:
                    i += 1
            case "t":
                if "s" in output_flags:
                    output_flags.remove("s")
                    label_name = cmd['branch_label']
                    # 找到 cmd_lst 中 cmd['label_name'] == label_name 的 cmd 的下标
                    #   i = new_i
                    # else i += 1
                    label_found = False
                    for idx, c in enumerate(cmd_lst):
                        if c["cmd"] == ":" and c["label_name"] == label_name:
                            i = idx
                            label_found = True
                            break
                    if not label_found:
                        i += 1
                else:
                    i += 1
    else:
        i += 1
    return cur_line, i, output_flags

def aadr_matches(cur_line: str, line_num: int, is_last: bool, addr1, addr2, range_state: dict) -> bool:
    """判断当前行是否符合 addr1 或 addr1,addr2 的匹配条件"""
    # 没有地址，默认全部匹配
    if addr1 is None:
        return True

    def match(addr, line_num, is_last):
        if addr is None:
            return False
        if addr == '$':
            return is_last
        elif addr.isdigit():
            return int(addr) == line_num
        elif addr.startswith('/') and addr.endswith('/'):
            pattern = addr[1:-1]
            return re.search(pattern, cur_line) is not None
        return False

    if addr2 is None:
        return match(addr1, line_num, is_last)
    else:
        # 范围：只要当前行在 addr1 和 addr2 范围内就匹配（简化处理为闭区间）
        in_range = False
        if not range_state.get("active", False):
            if match(addr1, line_num, is_last):
                range_state["active"] = True
                in_range = True
        else:
            in_range = True
            if match(addr2, line_num, is_last):
                range_state["active"] = False

        return in_range

def creat_temp():
    # 创建临时文件并返回它的文件名
    temp = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
    temp_name = temp.name
    temp.close()
    return temp_name

def output(n_flag: bool, result: str, output_flags: list, temp_file: str):

    if not output_flags or "s" in output_flags:
        if temp_file:
            with open(temp_file, 'a') as f:
                f.write(result + '\n')
        elif not n_flag:
            print(result)
    else:
        for flag in output_flags:
            if flag == "d":
                break
            elif flag == "q":
                output(n_flag, result, [], temp_file)
                sys.exit(0)
            elif type(flag) == tuple:
                contents = flag[1]
                output(n_flag, result, [], temp_file)
                output(False, contents, [], temp_file)

def override(input_file, temp_file):
    if isinstance(input_file, str):  # in-place 模式一定是单个文件
        shutil.move(temp_file, input_file)

def main():
    # 读取命令列表，解析 -i -n -f 指令
    args = sys.argv[1:]
    i_flag = False
    n_flag = False
    script_filename = None
    inline_cmd_txt = None

    # 1. -i
    if args and args[0] == '-i':
        i_flag = True
        args.pop(0)

    # 2. -n
    if args and args[0] == '-n':
        n_flag = True
        args.pop(0)

    if not args:
        return

    # 3. -f foo.pied OR inline_cmd
    if args and args[0] == '-f':
        script_filename = args[1]
        args = args[2:]
    else:
        inline_cmd_txt = args[0]
        args = args[1:]
    # 读取脚本命令生成命令链
    script_txt = read_cmd_txt(script_filename, inline_cmd_txt)
    cmd_txt_list = separate_script_txt(script_txt)
    cmd_lst = [parse_command(cmd_txt) for cmd_txt in cmd_txt_list]

    # 4. 剩下 args 都是文件列表
    input_files = args
    if input_files:
        # 对输入文件进行 run_pied
        if i_flag:
            for input_filename in input_files:
                run_pied(i_flag, n_flag, cmd_lst, input_filename)
        else:
            run_pied(i_flag, n_flag, cmd_lst, input_files)
    else:
        # 对 stdin 流进行 run_pied
        run_pied(i_flag, n_flag, cmd_lst)

if __name__ == '__main__':
    main()