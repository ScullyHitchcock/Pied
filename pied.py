#!/usr/bin/env python3
import shutil
import sys
import re
import tempfile
from collections import deque

class Line:
    """Line class represents a single line from the input, storing its content,
    associated file name, line number, and the content of the next line.
    It also tracks commands that may affect the line."""

    def __init__(self, filename, line_txt, next_line_txt, line_num):
        """

        :param filename: Name of the file the line belongs to
        :param line_txt: Content of the current line
        :param next_line_txt: Content of the next line
        :param line_num: Line number (starting from 1)
        """
        self.filename = filename
        self.contents = line_txt
        self.next_line_txt = next_line_txt
        self.line_num = line_num
        self.edge_cmds = set()

    def modify_contents(self, new_contents=None):
        """
        Modify the contents of the line.
        :param new_contents: New content to set; if None, clears the contents
        :return: None
        """
        self.contents = new_contents

    def is_last(self):
        """
        Check if this line is the last line of input.
        :return: True if it is the last line, otherwise False
        """
        return self.next_line_txt == ''

    def at_boundary_of(self, cmd):
        """
        Determine if this line is at the boundary of a given command's address range.
        :param cmd: Command instance to check
        :return: True if at the boundary, otherwise False
        """
        if cmd in self.edge_cmds or self.is_last():
            return True
        if cmd.addr2.is_empty():
            return cmd.addr1.match(self)
        return False

    def __str__(self):
        return f"<File: {self.filename} Line {self.line_num}: '{self.contents}'>"

    def is_beyond(self, address) -> bool:
        """
        Check if this line's number exceeds the specified address.
        :param address: Address instance to compare against
        :return: True if the line number is greater, otherwise False
        """
        if address.is_digit():
            return self.line_num > int(address.addr)
        return False

class Result:
    """Result class manages the state of a single line during script processing.
    It tracks flags like deletion, substitution, suppression, and manages output behaviors,
    including writing to a temporary file if -i is enabled."""

    def __init__(self, line: Line, n_flag: bool, i_flag: bool, temp_file: str):
        """
        :param line: Line instance being processed
        :param n_flag: Whether -n flag (suppress default output) is active
        :param i_flag: Whether -i flag (in-place editing) is active
        :param temp_file: Path to the temporary file for in-place editing
        """
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
        """
        Save a given text line into the temporary file.
        :param txt: Text line to be written
        """
        with open(self.temp_file, mode='a', encoding='utf-8') as f:
            f.write(txt + '\n')

    def suppress_output_by_c(self):
        """
        Mark the line as suppressed due to a 'c' command.
        """
        self.in_c_cmd_range = True

    def is_substituted(self):
        """
        Check if a substitution has occurred on the current line.
        """
        return self.substituted

    def is_suppressed(self):
        """
        Check if the line output should be suppressed.
        """
        return (self.n_flag or
                self.deleted or
                self.in_c_cmd_range)

    def delete_line(self):
        """
        Mark the current line as deleted and clear its content.
        """
        self.deleted = True
        self.line.modify_contents()

    def substitute_line(self, new_txt):
        """
        Replace the line contents with a new substituted text.
        :param new_txt: New substituted text
        """
        self.line.modify_contents(new_txt)
        self.substituted = True

    def add_after_order(self, cmd):
        """
        Add a command to be executed after regular processing (e.g., 'a' or 'q' commands).
        :param cmd: Command to add
        """
        self.after_queue.appendleft(cmd)

    def mark_special_cmd(self, cmd):
        """
        Mark a special command that influences the script flow (like 'd', 'q', 't', or 'b').
        :param cmd: Special command instance
        """
        self.last_special_cmd = cmd

    def reset_status(self):
        """
        Reset temporary status flags like substitution or last special command.
        """
        self.substituted = False
        self.last_special_cmd = None

    def default_output(self):
        """
        Output the current line's contents by default
        """
        self.output(self.line.contents)

    def after_output(self):
        """
        Process any commands queued for after-default output, such as 'append' or immediate 'quit'.
        """
        while self.after_queue:
            cmd = self.after_queue.pop()
            match cmd.type:
                case 'q':
                    sys.exit(0)
                case 'a':
                    appended_line = cmd.args
                    self.output(appended_line)

    def output(self, line_txt):
        """
        Handle actual outputting of a line, either printing to stdout or writing to a temp file.
        :param line_txt: Text to output
        :return:
        """
        if line_txt is not None:
            if self.i_flag:
                self.save_to_temp_file(line_txt)
            else:
                print(line_txt)

class Script:
    """Script class parses the entire script text into individual Command instances.
    It manages the sequence of commands and controls the flow during execution,
    including handling jumps (e.g., for 't' and 'b' commands) based on labels."""

    def __init__(self, script_texts):
        """
        Initialize a Script instance by parsing raw script text into Command objects.
        :param script_texts: Raw script content, either a single script string or loaded from a file
        """
        self.cmd_list = []
        cmd_txt_list = self.separate_script_txt(script_texts)
        for cmd_txt in cmd_txt_list:
            self.cmd_list.append(Command(cmd_txt))

    def __len__(self):
        return len(self.cmd_list)

    @staticmethod
    def separate_script_txt(script_texts):
        """
        Separate raw script text into a list of individual command strings.

        Handles special parsing for:
        - Address expressions delimited by '/'
        - Substitute commands 's' with arbitrary delimiters
        - Label-related commands ('t', 'b', ':')
        - Comment lines starting with '#'
        - Command separators ';' and newlines

        :param script_texts: Raw script text (str) containing one or multiple commands
        :return: List of command strings
        """
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
        """
        Process all commands in the script sequentially for a given line result.

        For each command:
        - Check if the command matches the current line based on its address.
        - If matched, execute the command's action.
        - Handle control flow changes like jump commands ('t', 'b', 'd', 'q') via jump_to_next.

        :param result: Result object representing the current line's processing state
        :return: None
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
        """
        Determine the next command index to execute based on any special command.

        If a special command ('d', 'q', 't', 'b') was triggered during processing:
        - 'd' or 'q' will immediately terminate further command processing for this line.
        - 't' or 'b' will jump to a specified label.
        Otherwise, move to the next sequential command.

        :param result: Result object holding the current line's processing state
        :param i: Current command index
        :return: Updated command index to continue processing
        """
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
    """Command class represents a single parsed script command.
    It stores information such as addresses (addr1, addr2), command type (e.g., p, d, s, etc.),
    optional arguments, and handles matching and executing the command on a given line."""
    def __init__(self, cmd_txt):
        """
        Initialize a Command instance by parsing a single command string.
        :param cmd_txt: Raw command text string to parse (e.g., '1,3d', '/foo/s/bar/baz/', '2aHello')
        """
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
        """
        Parse a single command string into its components.

        This method identifies:
        - addr1: First address (line number, regex, or special '$')
        - addr2: Optional second address for range commands
        - cmd: Command type (e.g., p, d, s, a, i, c, b, t, :)
        - args: Arguments for substitution, append, insert, or change commands
        - label: Label name for branching commands (b, t, :)

        :param cmd_txt: Raw command text string
        :return: A dictionary containing parsed command components
        """
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
        """
        Apply a substitution command ('s') on the given line.

        If the pattern matches, replace it with the specified replacement text.
        Honors the modifier to determine if all matches or only the first should be replaced.

        :param line: Input line text to apply substitution on
        :return: Modified line after substitution (or original if no change)
        """
        if self.type == 's':
            pattern, repl, modifier = self.args
            count = 0 if modifier else 1
            new_line = re.sub(pattern, repl, line, count=count)
            return new_line
        return line

    def match(self, line: Line) -> bool:
        """
        Determine whether the current command should be applied to the given line.

        If the command has no addresses, it matches all lines.
        If it has one address, it matches lines satisfying addr1.
        If it has two addresses, it manages an active range and matches all lines within that range.

        :param line: Line object representing the current line of input
        :return: True if the command applies to the line, otherwise False
        """
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
        """
        Execute the current command on the given line result.

        Performs different actions based on the command type:
        - 'p': Print the current line
        - 'q': Queue quit command and mark special flow
        - 'd': Delete the line and mark special flow
        - 's': Perform substitution if pattern matches
        - 'a': Queue text to append after the current line
        - 'i': Insert text before the current line
        - 'c': Replace content within an address range
        - 't': Conditional branch if last substitution succeeded
        - 'b': Unconditional branch to a label

        :param result: Result object representing the processing state of the current line
        :return: None
        """
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
                if result.line.at_boundary_of(self):
                    result.output(change_txt)
            case 't':
                if result.is_substituted():
                    result.mark_special_cmd(self)
            case 'b':
                result.mark_special_cmd(self)

class Address:
    """
    Address class represents a line-matching address in a sed-like script.

    It can be:
    - A specific line number (digit)
    - A regular expression (regex pattern between slashes)
    - The special symbol '$' representing the last line
    - Or empty, meaning no specific address

    Provides methods to identify the type of address and to match it against a Line object.
    """
    def __init__(self, addr: str):
        """
        Initialize an Address instance.
        :param addr: Address string, which can be a line number, a regex pattern (surrounded by '/'),
                     the special '$' symbol, or None (meaning no address)
        """
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
        """
        Check if the address is a line number (a digit).
        """
        return self.addr.isdigit()

    def is_regex(self) -> bool:
        """
        Check if the address is a regular expression.
        """
        return self.addr.startswith('/') and self.addr.endswith('/')

    def is_special_char(self) -> bool:
        """
        Check if the address is a special character: $.
        """
        return self.addr == '$'

    def is_empty(self) -> bool:
        """
        Check if the address is empty.
        """
        return self.addr == ''

    def match(self, line: Line) -> bool:
        """
        Determine whether the given line matches this address.

        Matching rules:
        - If the address is a line number, match by comparing line numbers.
        - If the address is a regex, match by searching the pattern in the line's text.
        - If the address is '$', match if the line is the last line.
        - If the address is empty, always return False.

        :param line: Line object to be checked against this address
        :return: True if the line matches the address, otherwise False
        """
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
    """
    Generate Line objects one by one from the given input source.

    Handles three types of input:
    - None: Read from standard input (stdin)
    - str: Read lines from a single file
    - list of str: Read lines from multiple files

    Each yielded Line object contains:
    - Current line text
    - Next line text (for lookahead)
    - Line number (starting from 1)
    - Associated filename

    :param input: None, a filename string, or a list of filenames
    :return: Iterator of Line instances
    """
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

    yield Line(filename, cur_line, '', line_num)  # last line

class PiedExecutor:
    """PiedExecutor class manages the execution of the script on input lines.
    It coordinates reading lines from input, processing them with the script commands,
    handling output (stdout or in-place file editing with -i), and applying post-processing operations."""

    def __init__(self, line_gen: iter, script: Script, i_flag: bool, n_flag: bool):
        """
        Initialize a PiedExecutor instance.

        :param line_gen: Iterator that yields Line objects from input
        :param script: Script instance containing parsed commands
        :param i_flag: Whether to enable in-place editing (-i flag)
        :param n_flag: Whether to suppress default output (-n flag)
        """
        self.line_gen = line_gen
        self.script = script
        self.i_flag = i_flag
        self.n_flag = n_flag

    @staticmethod
    def temp_file():
        """
        Create and return a path to a temporary file for in-place editing.
        The file is created securely and will persist after closing.

        :return: Path to the created temporary file
        """
        temp = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
        temp_name = temp.name
        temp.close()
        return temp_name

    def execute(self):
        """
        Execute the script on the provided input lines.

        For each line:
        - Apply all script commands to the line
        - Handle suppression (-n flag, deletions, etc.)
        - Perform default output or queued output operations
        - If in-place editing (-i flag) is enabled, write results to a temporary file
        After processing all lines, move the temporary file to overwrite the original input file if needed.
        """
        temp_file = self.temp_file() if self.i_flag else None
        input_file = None
        for line in self.line_gen:
            input_file = line.filename
            result = Result(line, self.n_flag, self.i_flag, temp_file)
            self.script.process(result)

            if not result.is_suppressed():
                result.default_output()

            result.after_output()

        if temp_file and input_file:
            shutil.move(temp_file, input_file)

def parse_cmd_line_args(args: list) -> tuple[bool, bool, str, list[str]]:
    """
    Parse command-line arguments for the Pied program.

    Recognizes options:
    - '-i': Enable in-place editing
    - '-n': Suppress default output
    - '-f filename': Load script text from an external file
    Otherwise, treats the first non-option argument as the script text.

    :param args: List of command-line arguments
    :return: A tuple (i_flag, n_flag, script_text, input_files_list)
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
    """
    Main entry point of the Pied program.

    - Parse command-line arguments
    - Load the script (from a file or inline)
    - Set up input line generator
    - Execute the script on input lines
    """
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