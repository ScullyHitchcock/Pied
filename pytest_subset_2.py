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
    args = ['3c hello']
    input_data = "\n".join(str(i) for i in range(5, 10)) + "\n"
    run_pied(args, stdin_text=input_data)
    captured = capsys.readouterr()
    assert captured.out == "5\n6\nhello\n8\n9\n"