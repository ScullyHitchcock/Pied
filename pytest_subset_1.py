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

def test_input_from_file(capsys):
    args = ['2q', 'input1.txt', 'input2.txt']
    with pytest.raises(SystemExit):
        run_pied(args)
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n"

def test_substitute_with_question_delim(capsys):
    run_pied(['s?[15]?Z?'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "Z\n2\n3\n4\nZ\n"

def test_substitute_with_X_delim(capsys):
    run_pied(['sX[15]XZX'], "1\n2\n3\n4\n5\n")
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
    run_pied(['/2$/,/8$/d;4,6p'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "1\n9\n10\n11\n19\n20\n"

def test_multiple_commands_newline_split(capsys):
    with pytest.raises(SystemExit):
        run_pied(['4q\n/2/d'], "1\n2\n3\n4\n5\n",)
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_multiple_commands_newline_order(capsys):
    with pytest.raises(SystemExit):
        run_pied(['/2/d\n4q'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_read_script1(capsys):
    with pytest.raises(SystemExit):
        run_pied(['-f', 'cmd1.txt'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_read_script2(capsys):
    with pytest.raises(SystemExit):
        run_pied(['-f', 'cmd2.txt'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_input_files(capsys):
    with pytest.raises(SystemExit):
        run_pied(['4q;/2/d', 'input1.txt', 'input2.txt'])
    captured = capsys.readouterr()
    assert captured.out == "1\n1\n2\n"

def test_input_files2(capsys):
    with pytest.raises(SystemExit):
        run_pied(['4q;/2/d', 'input2.txt', 'input1.txt'])
    captured = capsys.readouterr()
    assert captured.out == "1\n3\n4\n"

def test_read_script_and_input_files(capsys):
    with pytest.raises(SystemExit):
        run_pied(['-f', 'cmd2.txt', 'input1.txt', 'input2.txt'])
    captured = capsys.readouterr()
    assert captured.out == "1\n1\n2\n"

def test_comments_and_white_space1(capsys):
    input_data = "\n".join(str(i) for i in range(24, 44)) + "\n"
    run_pied([' 3, 17  d  # comment'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "24\n25\n41\n42\n43\n"

def test_comments_and_white_space2(capsys):
    input_data = "\n".join(str(i) for i in range(24, 44)) + "\n"
    run_pied(['/2/d # delete  ;  4  q # quit'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "30\n31\n33\n34\n35\n36\n37\n38\n39\n40\n41\n43\n"

def test_special_address1(capsys):
    run_pied(['$d'], "1\n2\n3\n4\n5\n")
    captured = capsys.readouterr()
    assert captured.out == "1\n2\n3\n4\n"

def test_special_address2(capsys):
    input_data = "\n".join(str(i) for i in range(1, 10001)) + "\n"
    run_pied(['-n', '$p'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "10000\n"

def test_range_addresses1(capsys):
    input_data = "\n".join(str(i) for i in range(10, 22)) + "\n"
    run_pied(['3,5d'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "10\n11\n15\n16\n17\n18\n19\n20\n21\n"

def test_range_addresses2(capsys):
    input_data = "\n".join(str(i) for i in range(10, 22)) + "\n"
    run_pied(['3,/2/d'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "10\n11\n21\n"

def test_range_addresses3(capsys):
    input_data = "\n".join(str(i) for i in range(10, 22)) + "\n"
    run_pied(['/2/,4d'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "10\n11\n14\n15\n16\n17\n18\n19\n"

def test_range_addresses4(capsys):
    input_data = "\n".join(str(i) for i in range(10, 22)) + "\n"
    run_pied(['/1$/,/^2/d'], input_data)
    captured = capsys.readouterr()
    assert captured.out == "10\n"

def test_range_addresses5(capsys):
    input_data = "\n".join(str(i) for i in range(10, 31)) + "\n"
    run_pied(['/4/,/6/s/[12]/9/'], input_data)
    captured = capsys.readouterr()
    assert captured.out == '10\n11\n12\n13\n94\n95\n96\n17\n18\n19\n20\n21\n22\n23\n94\n95\n96\n27\n28\n29\n30\n'

def test_range_addresses6(capsys):
    input_data = "\n".join(str(i) for i in range(10, 41)) + "\n"
    run_pied(['/2/,4p'], input_data)
    captured = capsys.readouterr()
    assert captured.out == """10
11
12
12
13
13
14
15
16
17
18
19
20
20
21
21
22
22
23
23
24
24
25
25
26
26
27
27
28
28
29
29
30
31
32
32
33
34
35
36
37
38
39
40
"""