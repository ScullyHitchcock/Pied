"""Core Pied command behavior.

These tests use small, single-purpose scripts so a failure usually points to
one command implementation instead of a larger script interaction.
"""

import pytest


def test_n_suppresses_default_output(run_pied, capsys):
    run_pied(["-n"], "a\nb\nc\n")

    assert capsys.readouterr().out == ""


def test_quit_no_address_outputs_first_line_then_exits(run_pied, capsys):
    with pytest.raises(SystemExit):
        run_pied(["q"], "1\n2\n3\n")

    assert capsys.readouterr().out == "1\n"


def test_quit_on_numbered_line(run_pied, capsys):
    with pytest.raises(SystemExit):
        run_pied(["2q"], "1\n2\n3\n")

    assert capsys.readouterr().out == "1\n2\n"


def test_quit_address_beyond_input_never_matches(run_pied, capsys):
    run_pied(["4q"], "1\n2\n3\n")

    assert capsys.readouterr().out == "1\n2\n3\n"


def test_quit_on_regex_address(run_pied, capsys):
    with pytest.raises(SystemExit):
        run_pied(["/r/q"], "hello\nworld\nbye\n")

    assert capsys.readouterr().out == "hello\nworld\n"


def test_quit_respects_suppressed_default_output(run_pied, capsys):
    # q still exits, but -n prevents the current line from being printed first.
    with pytest.raises(SystemExit):
        run_pied(["-n", "q"], "1\n2\n3\n")
    first = capsys.readouterr()

    with pytest.raises(SystemExit):
        run_pied(["-n", "1q"], "1\n2\n3\n")
    second = capsys.readouterr()

    with pytest.raises(SystemExit):
        run_pied(["-n", "/1/q"], "1\n2\n3\n")
    third = capsys.readouterr()

    assert first.out == ""
    assert second.out == ""
    assert third.out == ""


def test_print_without_n_duplicates_matching_lines(run_pied, capsys):
    run_pied(["p"], "1\n2\n3\n")

    assert capsys.readouterr().out == "1\n1\n2\n2\n3\n3\n"


def test_print_with_numbered_address(run_pied, capsys):
    run_pied(["1p"], "1\n2\n3\n")

    assert capsys.readouterr().out == "1\n1\n2\n3\n"


def test_print_with_n_outputs_only_explicit_prints(run_pied, capsys):
    run_pied(["-n", "3p"], "x\ny\nz\n")

    assert capsys.readouterr().out == "z\n"


def test_print_with_regex_address(run_pied, capsys):
    run_pied(["/1/p"], "000\n122\nabc\n")

    assert capsys.readouterr().out == "000\n122\n122\nabc\n"


def test_delete_numbered_line(run_pied, capsys):
    run_pied(["2d"], "a\nb\nc\n")

    assert capsys.readouterr().out == "a\nc\n"


def test_delete_without_address_removes_every_line(run_pied, capsys):
    run_pied(["d"], "a\nb\nc\n")

    assert capsys.readouterr().out == ""


def test_delete_with_n_still_suppresses_all_default_output(run_pied, capsys):
    run_pied(["-n", "2d"], "a\nb\nc\n")

    assert capsys.readouterr().out == ""


def test_delete_with_regex_address(run_pied, capsys):
    run_pied(["/2/d"], "2\n1\n3\n")

    assert capsys.readouterr().out == "1\n3\n"


def test_substitute_first_regex_match_per_line(run_pied, capsys):
    run_pied(["s/f./X/"], "foo\nbar\nfar\n")

    assert capsys.readouterr().out == "Xo\nbar\nXr\n"


def test_substitute_accepts_python_regex_syntax(run_pied, capsys):
    run_pied(["s/[a-z]{2}/X/"], "ab\ncd\nef\ng1\n")

    assert capsys.readouterr().out == "X\nX\nX\ng1\n"


def test_substitute_global_flag_replaces_every_match(run_pied, capsys):
    run_pied(["s/./X/g"], "abc\ndef\n")

    assert capsys.readouterr().out == "XXX\nXXX\n"


def test_substitute_without_print_is_silent_under_n(run_pied, capsys):
    run_pied(["-n", "s/a/A/"], "abc\n")

    assert capsys.readouterr().out == ""


def test_regex_address_can_be_combined_with_n_and_print(run_pied, capsys):
    run_pied(["-n", "/^1/p"], "2\n5\n8\n11\n14\n17\n20\n")

    assert capsys.readouterr().out == "11\n14\n17\n"
