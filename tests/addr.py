import re


def process(addr1, addr2, input):
    in_range = False
    for lineno, line in enumerate(input, start=1):
        if not in_range:
            if matches(addr1, line, lineno):
                execute(delete, line)
                # 如果 addr2 同一行也匹配，则不打开范围
                if not matches(addr2, line, lineno):
                    in_range = True
        else:
            execute(delete, line)
            if matches(addr2, line, lineno):
                in_range = False


def matches(addr, line, lineno):
    if addr.isdigit():
        return int(addr) == lineno
    elif addr.startswith('/') and addr.endswith('/'):
        addr = addr[1:-1]
        return re.search(addr, line) is not None

def execute(command, line):
    return command(line)

def delete(line):
    pass

if __name__ == '__main__':
    lines = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    process('1', '3', lines)