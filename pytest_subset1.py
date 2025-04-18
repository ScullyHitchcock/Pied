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

def test_substitute_with_question_delim(capsys):
    run_pied("1\n2\n3\n4\n5\n", ['s?[15]?Z?'])
    captured = capsys.readouterr()
    assert captured.out == "Z\n2\n3\n4\nZ\n"

def test_substitute_with_X_delim(capsys):
    run_pied("1\n2\n3\n4\n5\n", ['sX[15]XZ'])
    captured = capsys.readouterr()
    assert captured.out == "Z\n2\n3\n4\nZ\n"

def test_substitute_with_pipe_delim_and_g_flag(capsys):
    run_pied("a:b:c\n", ['s|:|/|g'])
    captured = capsys.readouterr()
    assert captured.out == "a/b/c\n"

def test_multiple_commands_with_semicolon(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n4\n5\n", ['4q;/2/d'])
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_semicolon_order(capsys):
    with pytest.raises(SystemExit):
        run_pied("1\n2\n3\n4\n5\n", ['/2/d;4q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_complex_combination(capsys):
    input_data = "\n".join(str(i) for i in range(1, 21)) + "\n"
    run_pied(input_data, ['/2$/,/,8$/d;4,6p'])
    captured = capsys.readouterr()
    assert captured.out == "1\n9\n10\n11\n19\n20\n"

def test_multiple_commands_newline_split(capsys):
    run_pied("1\n2\n3\n4\n5\n", ['4q\n/2/d'])
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_newline_order(capsys):
    run_pied("1\n2\n3\n4\n5\n", ['/2/d\n4q'])
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"
