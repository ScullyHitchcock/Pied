#!/usr/bin/env python3
import shutil
import sys
import re
import tempfile
from collections import deque

class Line:
    """行信息"""
    def __init__(self, filename, line_txt, next_line_txt, line_num):
        self.filename = filename
        self.line_txt = line_txt
        self.next_line_txt = next_line_txt
        self.line_num = line_num
        self.cmds_that_match_as_last_line = set()

    def is_last(self):
        return self.next_line_txt == ''

    def is_edge_of(self, cmd):
        if cmd in self.cmds_that_match_as_last_line:
            return True
        if cmd.addr2.is_empty():
            return cmd.addr1.match(self)
        return False

    def __str__(self):
        return f"<File: {self.filename} Line {self.line_num}: '{self.line_txt}'>"

    def is_beyond(self, address) -> bool:
        if address.is_digit():
            return self.line_num > int(address.addr)
        return False

class Result:
    def __init__(self, line: Line, n_flag: bool, i_flag: bool, temp_file: str):
        self.line = line
        self.line_txt = line.line_txt
        self.n_flag = n_flag
        self.i_flag = i_flag
        self.in_c_cmd_range = False
        self.pre_queue = deque()  # i 命令要插入的行
        self.after_queue = deque()   # a 命令要插入的行
        self.signal_to_activate_index_jump = None
        self.is_substituted = False
        self.is_deleted = False
        self.temp_file = temp_file
        self.input_file = line.filename if i_flag else None

    def save_to_temp_file(self, txt):
        with open(self.temp_file, mode='a', encoding='utf-8') as f:
            f.write(txt + '\n')

    def suppress_output(self):
        return (self.n_flag or
                self.is_deleted or
                self.in_c_cmd_range)

    def add_pre_order(self, cmd):
        self.pre_queue.appendleft(cmd)

    def delete_line(self):
        self.is_deleted = True
        self.line_txt = None

    def substitute(self, new_txt: str):
        self.line_txt = new_txt
        self.line.line_txt = new_txt
        self.is_substituted = True

    def add_after_order(self, cmd):
        self.after_queue.appendleft(cmd)

    def add_jump_signal(self, cmd):
        self.signal_to_activate_index_jump = cmd

    def reset_jump_signal(self):
        self.is_substituted = False
        self.signal_to_activate_index_jump = None

    def regular_output(self):
        self.output(self.line_txt)

    def output(self, line_txt):
        if line_txt is not None:
            if self.i_flag:
                # 保存到文件
                self.save_to_temp_file(line_txt)
            else:
                # 输出到 stdout
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
        # 将长命令文本中的每一条语句拆分出来装入列表
        cmd_txt = ''
        cmds = []
        i = 0
        length = len(script_texts)
        while i < length:
            if script_texts[i] == '/':
                addr = ''
                # 如果当前字符是 / 则不断组装字符直到组装到下一个 / 后停止
                # 最终 res 内应该是 '/[any]/' 的格式
                while addr.count('/') < 2:
                    addr += script_texts[i]
                    i += 1
                cmd_txt += addr
            elif script_texts[i] == 's':
                # 如果当前字符是 s
                # 取 s 下一位字符标记为 separator 分隔符，最终 res 内应该是 's[separator][any][separator][any][separator]' 的格式
                cmd_txt += script_texts[i]
                i += 1
                s_separator = script_texts[i]
                while s_separator == ' ':
                    i += 1
                    s_separator = script_texts[i]
                sub_args = ''
                while sub_args.count(s_separator) < 3:
                    sub_args += script_texts[i]
                    i += 1
                cmd_txt += sub_args
            elif script_texts[i] in ('t', 'b', ':'):
                # 当字符是标签语句开头，组装字符直到当前语句结束（遇到 ; ）或到达字符串末尾
                while i < length and script_texts[i] not in (';', '\n'):
                    if script_texts[i] != ' ':
                        cmd_txt += script_texts[i]
                    i += 1
            elif script_texts[i] == ' ':
                # 当字符是空格键，不组装，跳过
                i += 1
            elif script_texts[i] == '#':
                # 当字符是 #，跳过不组装直到当前语句结束（遇到 ; ）或到达字符串末尾
                while i < length and script_texts[i] not in (';', '\n'):
                    i += 1
            elif script_texts[i] in (';', '\n'):
                # 当字符是 ; 或 \n 语句结束符，储存当前语句 txt，继续循环
                if cmd_txt:
                    cmds.append(cmd_txt)
                i += 1
                cmd_txt = ''
            else:
                # 当字符是普通字符，直接组装
                cmd_txt += script_texts[i]
                i += 1
        if cmd_txt:
            # 循环结束后如果 cmd_txt 不为空则储存
            cmds.append(cmd_txt)
        return cmds

    def process(self, result: Result):
        """
        遍历 cmd_list，匹配脚本，执行前置命令，将后置命令放入 result.after_queue 中
        :param line:
        :return:
        """
        i, l = 0, len(self.cmd_list)
        while i < l:
            cmd = self.cmd_list[i]
            if cmd.match(result.line):
                cmd.process(result)
                i = self.jump_to_next(result, i)
            else:
                i += 1

    def jump_to_next(self, result: Result, i: int):
        special_cmd = result.signal_to_activate_index_jump
        if special_cmd is not None:
            if special_cmd.type in ('d', 'q'):
                i = self.__len__()
            elif special_cmd.type in ('t', 'b'):
                label = special_cmd.label
                for j, cmd in enumerate(self.cmd_list):
                    if cmd.type == ':' and cmd.label == label:
                        i = j
                        break
            result.reset_jump_signal()
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
                # parse /.../
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

        # extract addr1
        if i < length and (cmd_txt[i] == '/' or cmd_txt[i].isdigit() or cmd_txt[i] == '$'):
            result["addr1"] = parse_addr()
            # check for comma and addr2
            if i < length and cmd_txt[i] == ',':
                i += 1
                result["addr2"] = parse_addr()
        if i < length:
            result["cmd"] = cmd_txt[i]
            i += 1

        # rest is command-specific
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
                        # After repl, only need to grab flags, which may have delimiters
                        parts.append(rest[i:])  # everything after second delimiter
                        break
                else:
                    current += ch
                    i += 1
            return tuple(parts)

        if result["cmd"] in ('b', 't', ':'):
            result["label"] = rest or None
        elif result["cmd"] == 's':
            # parse s/pat/repl/flags
            if rest:
                result["args"] = parse_substitute(rest)
        elif result["cmd"] in ('a', 'i', 'c'):
            result["args"] = rest

        return result

    def substitute(self, line: str) -> str:
        if self.type == 's':
            pattern, repl, modifier = self.args
            # actual_repl = re.sub(r'\\(.)', r'\1', repl)
            # actual_pattern = re.sub(r'\\(.)', r'\1', pattern)
            count = 0 if modifier else 1
            new_line = re.sub(pattern, repl, line, count=count)
            return new_line
        return line

    def match(self, line: Line) -> bool:
        if self.addr1.is_empty():
            return True
        if self.addr2.is_empty():
            return self.addr1.match(line)
        # in_range 代表上一行文本在地址匹配范围内
        if self.in_range:
            if self.addr2.match(line):
                # 当在范围内且地址2匹配，说明当前行已在范围边缘，
                # 关闭 range，代表下一行内容将要重新评估 addr1
                # 同时在 line 中记录这个 cmd（为后续 c 命令的处理提供注脚）
                # 返回 True
                line.cmds_that_match_as_last_line.add(self)
                self.in_range = False
                return True
            if self.addr2.is_regex():
                # 当在范围内且地址2不匹配，但地址2属于正则类型时，继续扩张 range，返回 True
                return True
            if line.is_beyond(self.addr2):
                # 当在范围内且地址2不匹配，但地址2属于数字类型，且当前行数已经超过地址2
                # 关闭 range，返回 False
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
        # 命令执行时机以常规输出 regular_output 为分界线：
        # pre_order: p, d, s, i, t, b
        # after_order: q, a, c
        # 当匹配到 pre_order 时，立即执行命令逻辑
        # 当匹配到 after_order 时，执行部分前置逻辑后将其加入 result 的 after_queue 中
        match self.type:
            case 'p':
                # 前置命令，立即执行
                # 执行命令：output current line
                result.output(result.line.line_txt)
            case 'q':
                # 后置命令，放在 after queue，命令逻辑为当 result.regular_out() 后执行 sys.exit()
                result.add_after_order(self)
                # 结束对 current line 的操作，向 result 添加一个信号，提示 script 将下标移至最后
                result.add_jump_signal(self)
            case 'd':
                # 前置命令，设置 result.is_deleted 为 True，同时设置 result.line_txt = None
                result.delete_line()
                # 结束对 current line 的操作，向 result 添加一个信号，提示 script 将下标移至最后
                result.add_jump_signal(self)
            case 's':
                # 前置命令，替换文本，将 result.line_txt 替换为特定文本
                cur_line = result.line.line_txt
                sub_line = self.substitute(cur_line)
                if sub_line != cur_line:
                    # 如果执行成功，修改 result.line_txt 实例属性和设置 result.is_substituted = True
                    result.substitute(sub_line)
            case 'a':
                # 后置命令
                # 执行命令：after regular_order, output specific text based on self.args
                result.add_after_order(self)
            case 'i':
                # 前置命令
                # output specific text based on args before regular_order
                insert_txt = self.args
                result.output(insert_txt)
            case 'c':
                # 前置命令
                # 在 result 中添加一个 flag，当 flag 存在时抑制 regular_output。
                # 如果 1 result.line.is_edge_of(this cmd)
                # or 2 result.line.is_last()（说明已经到达 c 命令控制范围边缘）
                # output(c.args)
                # 取消 flag
                change_txt = self.args
                result.in_c_cmd_range = True
                if result.line.is_edge_of(self) or result.line.is_last():
                    result.output(change_txt)
                    # result.in_c_cmd_range = False
            case 't':
                # 前置命令
                # 读取 result 记录，如果有 s 命令执行成功的记录，则：
                #   向 result 添加信号，提示 script 进行下标跳转工作
                if result.is_substituted:
                    result.add_jump_signal(self)
            case 'b':
                # 前置命令
                # 向 result 添加信号，提示 script 进行下标跳转工作
                result.add_jump_signal(self)

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
        txt = line.line_txt
        if self.is_digit():
            return int(self.addr) == line.line_num
        if self.is_regex():
            pattern = self.addr[1:-1]
            return re.search(pattern, txt) is not None
        if self.is_special_char():
            return line.is_last()
        return False

def line_generator(input: list | str | None) -> iter:
    """
    传入文件列表或文件名或空，按行读取输入数据
    :param input: 输入数据
    :return: 生成器
    """

    def file_reader(filename) -> iter:
        with open(filename, 'r') as f:
            for line in f:
                yield line.rstrip('\n')
    def line_iterator() -> iter:
        if not input:
            # 如果没有输入数据，从 sys.stdin 中读取
            for line in sys.stdin:
                yield 'stdin', line.rstrip('\n')
        elif isinstance(input, str):
            # 如果输入数据是单个字符串（文件名），直接打开读取
            for line in file_reader(input):
                yield input, line
        elif isinstance(input, list):
            # 如果输入数据是列表，先遍历列表在打开文件读取
            for file in input:
                for line in file_reader(file):
                    yield file, line

    it = line_iterator()
    try:
       filename, cur_line = next(it)
    except StopIteration:
        return  # 空输入

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
        # 从 line_gen 中提取 line 文本
        # script 执行 line 命令，得到 res 结果
        # 输出结果
        temp_file = self.temp_file() if self.i_flag else None
        input_file = None
        for line in self.line_gen:
            input_file = line.filename
            # 创建 result 对象，通过 script.process 方法将处理结果放入其中
            res = Result(line, self.n_flag, self.i_flag, temp_file)

            # 运行脚本，执行其中的前置命令
            self.script.process(res)

            # 执行 regular_output() 及脚本其余的后置命令
            self.output(res)
        if temp_file and input_file:
            shutil.move(temp_file, input_file)

    def output(self, result: Result):
        if not result.suppress_output():
            result.regular_output()
        while result.after_queue:
            cmd = result.after_queue.pop()
            match cmd.type:
                case 'q':
                    sys.exit(0)
                case 'a':
                    append_line = cmd.args
                    result.output(append_line)



def parse_cmd_line_args(args: list) -> tuple[bool, bool, str, list[str]]:
    """
    对命令行输入的参数进行解析，拆分出以下参数
    :param args: 命令行文本参数
    :return:
        i_flag: 如果 args 带有 -i 字样返回 True 否则 False
        n_flag: 如果 args 带有 -n 字样返回 True 否则 False
        script_txt: 脚本命令文本
        input_files_lst: input 来源文件名列表，如果为空，则说明应从 stdin 中获取输入数据
    """
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
    # 读取命令列表，解析 -i -n 指令，以及脚本命令文本，和输入来源文本
    args = sys.argv[1:]
    i_flag, n_flag, script_txt, input_files_lst = parse_cmd_line_args(args)
    if not script_txt:
        return
    # 传入脚本命令文本，得到 Script 实例对象（对象内储存若干个 Command 类型对象）
    script = Script(script_txt)

    def execute(input):
        # 创建生成器 line_gen，每次可以生成两行 Line 对象
        line_gen = line_generator(input)
        # 将生成器、脚本对象、i_flag、n_flag 一并传入，构造 PiedExecutor 对象 pied
        pied = PiedExecutor(line_gen, script, i_flag, n_flag)
        # pied 调用 execute() 方法，内部逻辑为对 line_gen 生成的每一行 Line 对象执行 script 中的 Command 命令，并输出
        pied.execute()

    if i_flag and input_files_lst:
        # 如果是 -i 模式且 input_files_lst 不为空时，需要对 input_files_lst 内的每个文件单独执行脚本命令
        for input_filename in input_files_lst:
            execute(input_filename)
    else:
        # 否则无论 input_files_lst 内有多少个文件，都视为一次输入流数据（按列表顺序读取内容），执行一次脚本
        # 如果 input_files_lst 为空，则读取 sys.stdin 作为输入数据，对其执行脚本
        execute(input_files_lst)

if __name__ == '__main__':
    main()