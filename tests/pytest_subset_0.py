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

def test_n(capsys):
    run_pied("a\nb\nc\n", ['-n'])
    captured = capsys.readouterr()
    assert captured.out == ""

def test_quit_no_addr(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n"
def test_quit_on_second_line(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['2q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n"
def test_quit_on_exceeded_line(capsys):
    run_pied("1\n2\n3\n", ['4q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n3\n"
def test_quit_by_re(capsys):
    with pytest.raises(SystemExit):
        run_pied("0\n1\n2\n", ['/1/q'])
    captured = capsys.readouterr()
    assert captured.out == "0\n1\n"
def test_quit_on_match(capsys):
    with pytest.raises(SystemExit):
        run_pied("hello\nworld\nbye\n", ['/r/q'])
    captured = capsys.readouterr()
    assert captured.out == "hello\nworld\n"
def test_quit_with_n(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['-n', 'q'])
    captured1 = capsys.readouterr()
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['-n', '1q'])
    captured2 = capsys.readouterr()
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n", ['-n', '/1/q'])
    captured3 = capsys.readouterr()
    assert captured1.out == ""
    assert captured2.out == ""
    assert captured3.out == ""

def test_print_every_line_twice_without_n(capsys):
    run_pied("1\n2\n3\n", ['p'])
    captured = capsys.readouterr()
    assert captured.out == "1\n1\n2\n2\n3\n3\n"
def test_print_only_line_1_twice(capsys):
    run_pied("1\n2\n3\n", ['1p'])
    captured = capsys.readouterr()
    assert captured.out == "1\n1\n2\n3\n"
def test_print_line_3_with_n(capsys):
    run_pied("x\ny\nz\n", ['-n', '3p'])
    captured = capsys.readouterr()
    assert captured.out == "z\n"
def test_print_on_match(capsys):
    run_pied("000\n122\nabc\n", ['/1/p'])
    captured = capsys.readouterr()
    assert captured.out == "000\n122\n122\nabc\n"
def test_print_on_match_with_n(capsys):
    run_pied("000\n122\nabc\n", ['-n', '/1/p'])
    captured = capsys.readouterr()
    assert captured.out == "122\n"

def test_delete_line_2(capsys):
    run_pied("a\nb\nc\n", ['2d'])
    captured = capsys.readouterr()
    assert captured.out == "a\nc\n"
def test_delete_all_lines(capsys):
    run_pied("a\nb\nc\n", ['d'])
    captured = capsys.readouterr()
    assert captured.out == ""
def test_delete_line_2_with_n(capsys):
    run_pied("a\nb\nc\n", ['-n', '2d'])
    captured = capsys.readouterr()
    assert captured.out == ""
def test_delete_line_matching_2(capsys):
    run_pied("2\n1\n3\n", ['/2/d'])
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n"

def test_regex_substitute(capsys):
    run_pied("foo\nbar\nfar\n", ['s/f./X/'])
    captured = capsys.readouterr()
    assert captured.out == "Xo\nbar\nXr\n"
def test_complex_regex_substitute(capsys):
    run_pied("ab\ncd\nef\ng1\n", ['s/[a-z]{2}/X/'])
    captured = capsys.readouterr()
    assert captured.out == "X\nX\nX\ng1\n"
def test_substitute_with_global_flag(capsys):
    run_pied("abc\ndef\n", ['s/./X/g'])
    captured = capsys.readouterr()
    assert captured.out == "XXX\nXXX\n"
def test_substitute_with_n_flag_no_p(capsys):
    run_pied("abc\n", ['-n', 's/a/A/'])
    captured = capsys.readouterr()
    assert captured.out == ""
def test_print_lines_matching_regex_1_with_n(capsys):
    run_pied("2\n5\n8\n11\n14\n17\n20\n", ['-n', '/^1/p'])
    captured = capsys.readouterr()
    assert captured.out == "11\n14\n17\n"

