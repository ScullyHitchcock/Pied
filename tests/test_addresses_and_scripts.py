"""Address parsing, script-file input, and multi-command behavior."""

import pytest


def numbered_lines(start: int, stop: int) -> str:
    """Return newline-terminated numbers from start through stop inclusive."""
    return "\n".join(str(i) for i in range(start, stop + 1)) + "\n"


def test_quit_reads_multiple_input_files(run_pied, capsys, fixtures_dir):
    input1 = fixtures_dir / "input1.txt"
    input2 = fixtures_dir / "input2.txt"

    with pytest.raises(SystemExit):
        run_pied(["2q", str(input1), str(input2)])

    assert capsys.readouterr().out == "1\n2\n"


def test_substitute_supports_question_mark_delimiter(run_pied, capsys):
    run_pied(["s?[15]?Z?"], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "Z\n2\n3\n4\nZ\n"


def test_substitute_supports_letter_delimiter(run_pied, capsys):
    run_pied(["sX[15]XZX"], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "Z\n2\n3\n4\nZ\n"


def test_substitute_supports_pipe_delimiter_and_global_flag(run_pied, capsys):
    run_pied(["s|:|/|g"], "a:b:c\n")

    assert capsys.readouterr().out == "a/b/c\n"


def test_semicolon_separates_commands(run_pied, capsys):
    with pytest.raises(SystemExit):
        run_pied(["4q;/2/d"], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "1\n3\n4\n"


def test_command_order_is_preserved(run_pied, capsys):
    with pytest.raises(SystemExit):
        run_pied(["/2/d;4q"], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "1\n3\n4\n"


def test_multiple_commands_can_mix_ranges_and_prints(run_pied, capsys):
    run_pied(["/2$/,/8$/d;4,6p"], numbered_lines(1, 20))

    assert capsys.readouterr().out == "1\n9\n10\n11\n19\n20\n"


def test_newlines_also_separate_commands(run_pied, capsys):
    with pytest.raises(SystemExit):
        run_pied(["4q\n/2/d"], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "1\n3\n4\n"


def test_script_file_can_be_loaded_with_f(run_pied, capsys, fixtures_dir):
    script = fixtures_dir / "cmd1.pied"

    with pytest.raises(SystemExit):
        run_pied(["-f", str(script)], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "1\n3\n4\n"


def test_script_file_and_input_files_can_be_combined(run_pied, capsys, fixtures_dir):
    script = fixtures_dir / "cmd2.pied"
    input1 = fixtures_dir / "input1.txt"
    input2 = fixtures_dir / "input2.txt"

    with pytest.raises(SystemExit):
        run_pied(["-f", str(script), str(input1), str(input2)])

    assert capsys.readouterr().out == "1\n1\n2\n"


def test_input_file_order_affects_global_line_numbers(run_pied, capsys, fixtures_dir):
    input1 = fixtures_dir / "input1.txt"
    input2 = fixtures_dir / "input2.txt"

    with pytest.raises(SystemExit):
        run_pied(["4q;/2/d", str(input2), str(input1)])

    assert capsys.readouterr().out == "1\n3\n4\n"


def test_comments_and_whitespace_are_ignored_around_commands(run_pied, capsys):
    run_pied([" 3, 17  d  # comment"], numbered_lines(24, 43))

    assert capsys.readouterr().out == "24\n25\n41\n42\n43\n"


def test_comment_consumes_the_rest_of_a_command_line(run_pied, capsys):
    run_pied(["/2/d # delete  ;  4  q # quit"], numbered_lines(24, 43))

    assert capsys.readouterr().out == (
        "30\n31\n33\n34\n35\n36\n37\n38\n39\n40\n41\n43\n"
    )


def test_dollar_address_matches_only_the_last_line(run_pied, capsys):
    run_pied(["$d"], "1\n2\n3\n4\n5\n")

    assert capsys.readouterr().out == "1\n2\n3\n4\n"


def test_dollar_address_works_on_large_streams(run_pied, capsys):
    run_pied(["-n", "$p"], numbered_lines(1, 10000))

    assert capsys.readouterr().out == "10000\n"


def test_numeric_range_delete(run_pied, capsys):
    run_pied(["3,5d"], numbered_lines(10, 21))

    assert capsys.readouterr().out == "10\n11\n15\n16\n17\n18\n19\n20\n21\n"


def test_numeric_to_regex_range_delete(run_pied, capsys):
    run_pied(["3,/2/d"], numbered_lines(10, 21))

    assert capsys.readouterr().out == "10\n11\n21\n"


def test_regex_to_numeric_range_delete(run_pied, capsys):
    run_pied(["/2/,4d"], numbered_lines(10, 21))

    assert capsys.readouterr().out == "10\n11\n14\n15\n16\n17\n18\n19\n"


def test_regex_to_regex_range_delete(run_pied, capsys):
    run_pied(["/1$/,/^2/d"], numbered_lines(10, 21))

    assert capsys.readouterr().out == "10\n"


def test_range_address_limits_substitution(run_pied, capsys):
    run_pied(["/4/,/6/s/[12]/9/"], numbered_lines(10, 30))

    assert capsys.readouterr().out == (
        "10\n11\n12\n13\n94\n95\n96\n17\n18\n19\n"
        "20\n21\n22\n23\n94\n95\n96\n27\n28\n29\n30\n"
    )


def test_range_print_duplicates_only_matching_lines(run_pied, capsys):
    run_pied(["/2/,4p"], numbered_lines(10, 40))

    assert capsys.readouterr().out == "\n".join([
        "10", "11", "12", "12", "13", "13", "14",
        "15", "16", "17", "18", "19", "20", "20",
        "21", "21", "22", "22", "23", "23", "24",
        "24", "25", "25", "26", "26", "27", "27",
        "28", "28", "29", "29", "30", "31", "32",
        "32", "33", "34", "35", "36", "37", "38",
        "39", "40",
    ]) + "\n"


def test_complex_script_combines_multiple_address_ranges(run_pied, capsys):
    script = "1,/.1/p;/5/,/9/s/.//;/.2/,/.9/p;85q"

    with pytest.raises(SystemExit):
        run_pied(["-n", script], numbered_lines(1, 100))

    assert capsys.readouterr().out == "\n".join([
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11",
        "12", "13", "14", "5", "6", "7", "8", "9",
        "20", "21", "22", "23", "24", "5", "6", "7", "8", "9",
        "30", "31", "32", "33", "34", "5", "6", "7", "8", "9",
        "40", "41", "42", "43", "44", "5", "6", "7", "8", "9",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "60", "61", "62", "63", "64", "5", "6", "7", "8", "9",
        "70", "71", "72", "73", "74", "5", "6", "7", "8", "9",
        "80", "81", "82", "83", "84", "5",
    ]) + "\n"


def test_complex_script_has_same_behavior_when_loaded_from_file(
    run_pied, capsys, tmp_path
):
    script_file = tmp_path / "commands.pied"
    script_file.write_text("1,/.1/p;/5/,/9/s/.//\n/.2/,/.9/p;85q")

    with pytest.raises(SystemExit):
        run_pied(["-n", "-f", str(script_file)], numbered_lines(1, 100))

    assert capsys.readouterr().out == "\n".join([
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11",
        "12", "13", "14", "5", "6", "7", "8", "9",
        "20", "21", "22", "23", "24", "5", "6", "7", "8", "9",
        "30", "31", "32", "33", "34", "5", "6", "7", "8", "9",
        "40", "41", "42", "43", "44", "5", "6", "7", "8", "9",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "60", "61", "62", "63", "64", "5", "6", "7", "8", "9",
        "70", "71", "72", "73", "74", "5", "6", "7", "8", "9",
        "80", "81", "82", "83", "84", "5",
    ]) + "\n"
