import sys
import io
import pied
import pytest

def run_pied(stdin_text, argv_args):
    # 模拟命令行参数
    sys.argv = ['pied.py'] + argv_args
    # 模拟标准输入
    sys.stdin = io.StringIO(stdin_text)
    pied.main()

def test_delete_line_2(capsys):
    run_pied("a\nb\nc\n", ['2d'])
    captured = capsys.readouterr()
    assert captured.out == "a\nc\n"

def test_print_line_3_with_n(capsys):
    run_pied("x\ny\nz\n", ['-n', '3p'])
    captured = capsys.readouterr()
    assert captured.out == "z\n"

def test_regex_substitute(capsys):
    run_pied("foo\nbar\nfar\n", ['s/f./X/'])
    captured = capsys.readouterr()
    assert captured.out == "Xo\nbar\nXr\n"

def test_quit_on_match(capsys):
    with pytest.raises(SystemExit):
        run_pied("hello\nworld\nbye\n", ['/r/q'])
    captured = capsys.readouterr()
    assert captured.out == "hello\nworld\n"

def test_quit_on_second_line(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['2q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n"

def test_quit_first_line(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n"

def test_quit_on_exceeded_line(capsys):
    run_pied("1\n2\n3\n", ['4q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n3\n"

def test_print_every_line_twice_without_n(capsys):
    run_pied("1\n2\n3\n", ['p'])
    captured = capsys.readouterr()
    assert captured.out == "1\n1\n2\n2\n3\n3\n"

def test_print_only_line_1_twice(capsys):
    run_pied("1\n2\n3\n", ['1p'])
    captured = capsys.readouterr()
    assert captured.out == "1\n1\n2\n3\n"
