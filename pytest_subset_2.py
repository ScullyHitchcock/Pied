import sys
import io
import pied
import pytest

def run_pied(argv_args, stdin_text=None):
    # 模拟命令行参数
    sys.argv = ['pied.py'] + argv_args
    # 模拟标准输入
    if stdin_text:
        sys.stdin = io.StringIO(stdin_text)
    pied.main()

def test_i_cmd(tmp_path, capsys):
    # 创建测试文件 test.txt，写入初始内容
    test_file = tmp_path / "test.txt"
    test_file.write_text("1\n2\n3\n4\n5\n")
    # 运行 pied.py 脚本，传入 -i 参数
    sys.argv = ['-i', '/[24]/d', str(test_file)]
    run_pied(sys.argv)
    # 读取文件修改后的内容
    result = test_file.read_text()
    assert result == "1\n3\n5\n"

def test_complex_cmd1(capsys):
    args = ['s/;/semicolon/g;/;/q']
    stdin = 'Punctuation characters include . , ; :'
    run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()
    assert captured.out == 'Punctuation characters include . , semicolon :\n'

def test_complex_cmd2(capsys):
    args = [': start; s/00/0/; t start']
    stdin = '1000001\n'
    run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()
    assert captured.out == '101\n'

def test_complex_cmd3(capsys):
    args = ['-n', r'p; : begin;s/[^ ](.)/ \1/; t skip; q; : skip; p; b begin']
    stdin = '0123456789\n'
    with pytest.raises(SystemExit):
        run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()
    assert captured.out == '0123456789\n 123456789\n  23456789\n   3456789\n    456789\n     56789\n      6789\n       789\n        89\n         9\n'

def test_append(capsys):
    args = ['3a hello']
    input_data = "\n".join(str(i) for i in range(5, 10)) + "\n"
    run_pied(args, stdin_text=input_data)
    captured = capsys.readouterr()
    assert captured.out == "5\n6\n7\nhello\n8\n9\n"

def test_insert(capsys):
    args = ['3i hello']
    input_data = "\n".join(str(i) for i in range(5, 10)) + "\n"
    run_pied(args, stdin_text=input_data)
    captured = capsys.readouterr()
    assert captured.out == "5\n6\nhello\n7\n8\n9\n"

def test_change(capsys):
    args = ['2c hello']
    input_data = "\n".join(str(i) for i in range(1, 4)) + "\n"
    run_pied(args, stdin_text=input_data)
    captured = capsys.readouterr()
    assert captured.out == "1\nhello\n3\n"

def test_change_range_cmd_dictionary(capsys):
    args = ['/.{3}/,/.{5}/c hello']
    stdin = "\n".join([
        "a",
        "aah",
        "aahed",
        "aahing",
        "aahs",
        "aal",
        "aalii",
        "aaliis",
        "aals",
        "aardvark"
    ]) + "\n"

    run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()

    # 分析：
    # 行1：a          → 不匹配任何地址，保留
    # 行2：aah        → .{3} 匹配，作为 addr1 起点
    # 行3：aahed      → 仍在范围中
    # 行4：aahing     → .{5} 匹配，作为 addr2 终点（包含），匹配结束
    # 所以第2~4行被替换为一行或多行 "hello"，按 sed 标准，c命令只输出一次 hello

    expected = "a\nhello\nhello\nhello\n"
    assert captured.out == expected

def test_substitute_escaped_slash(capsys):
    args = ['s/[15]/z\\/z\\/z/']
    stdin = "1\n2\n3\n4\n5\n"
    run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()

    expected_output = "\n".join([
        "z/z/z",  # 1 → z/z/z
        "2",
        "3",
        "4",
        "z/z/z"   # 5 → z/z/z
    ]) + "\n"

    assert captured.out == expected_output


# subset2_substitute_87: s_[15]_z\_z\_z_
def test_substitute_escaped_underscore(capsys):
    args = ['s_[15]_z\\_z\\_z_']
    stdin = "1\n2\n3\n4\n5\n"
    run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()

    expected_output = "\n".join([
        "z_z_z",  # 1 → z_z_z
        "2",
        "3",
        "4",
        "z_z_z"   # 5 → z_z_z
    ]) + "\n"

    assert captured.out == expected_output


# subset2_substitute_88: s1[\15]1zzz1
def test_substitute_escaped_delimiter_digit(capsys):
    args = ['s1[\\15]1zzz1']
    stdin = "1\n2\n3\n4\n5\n"
    run_pied(args, stdin_text=stdin)
    captured = capsys.readouterr()

    expected_output = "\n".join([
        "zzz",  # 1 → zzz
        "2",
        "3",
        "4",
        "zzz"   # 5 → zzz
    ]) + "\n"

    assert captured.out == expected_output

