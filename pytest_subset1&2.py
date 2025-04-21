import sys
import io
import pied_for_more
import pytest

def run_pied(argv_args, stdin_text=None):
    # 模拟命令行参数
    sys.argv = ['pied_for_more.py'] + argv_args
    # 模拟标准输入
    if stdin_text:
        sys.stdin = io.StringIO(stdin_text)
    pied_for_more.main()

def test_input_from_file(capsys):
    args = ['2q', 'input1.txt', 'input2.txt']
    run_pied(args)
    captured = capsys.readouterr()
    assert captured.out == "Z\n2\n3\n4\nZ\n"

def test_substitute_with_question_delim(capsys):
    run_pied(['s?[15]?Z?'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "Z\n2\n3\n4\nZ\n"

def test_substitute_with_X_delim(capsys):
    run_pied(['sX[15]XZ'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "Z\n2\n3\n4\nZ\n"

def test_substitute_with_pipe_delim_and_g_flag(capsys):
    run_pied(['s|:|/|g'], "a:b:c\n")
    captured = capsys.readouterr()
    assert captured.out == "a/b/c\n"

def test_multiple_commands_with_semicolon(capsys):
    with pytest.raises(SystemExit):
        run_pied(['4q;/2/d'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_semicolon_order(capsys):
    with pytest.raises(SystemExit):
        run_pied(['/2/d;4q'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_complex_combination(capsys):
    input_data = "\n".join(str(i) for i in range(1, 21)) + "\n"
    run_pied(['/2$/,/,8$/d;4,6p'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "1\n9\n10\n11\n19\n20\n"

def test_multiple_commands_newline_split(capsys):
    run_pied(['4q\n/2/d'], "1\n2\n3\n4\n5\n",)
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_newline_order(capsys):
    run_pied(['/2/d\n4q'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"
