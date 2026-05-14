"""Advanced command semantics: editing files, text insertion, and branching."""

import pytest


def numbered_lines(start: int, stop: int) -> str:
    """Return newline-terminated numbers from start through stop inclusive."""
    return "\n".join(str(i) for i in range(start, stop + 1)) + "\n"


def test_in_place_editing_rewrites_the_input_file(run_pied, tmp_path):
    target = tmp_path / "input.txt"
    target.write_text("1\n2\n3\n4\n5\n")

    run_pied(["-i", "/[24]/d", str(target)])

    assert target.read_text() == "1\n3\n5\n"


def test_substitution_can_feed_a_later_quit_command(run_pied, capsys):
    run_pied(["s/;/semicolon/g;/;/q"], "Punctuation characters include . , ; :")

    assert capsys.readouterr().out == "Punctuation characters include . , semicolon :\n"


def test_t_branches_when_the_previous_substitution_changed_the_line(run_pied, capsys):
    # Repeatedly collapse "00" to "0" until no substitution succeeds.
    run_pied([": start; s/00/0/; t start"], "1000001\n")

    assert capsys.readouterr().out == "101\n"


def test_b_and_t_can_build_a_looping_script(run_pied, capsys):
    script = r"p; : begin;s/[^ ](.)/ \1/; t skip; q; : skip; p; b begin"

    with pytest.raises(SystemExit):
        run_pied(["-n", script], "0123456789\n")

    assert capsys.readouterr().out == (
        "0123456789\n"
        " 123456789\n"
        "  23456789\n"
        "   3456789\n"
        "    456789\n"
        "     56789\n"
        "      6789\n"
        "       789\n"
        "        89\n"
        "         9\n"
    )


def test_append_outputs_text_after_the_current_line(run_pied, capsys):
    run_pied(["3a hello"], numbered_lines(5, 9))

    assert capsys.readouterr().out == "5\n6\n7\nhello\n8\n9\n"


def test_insert_outputs_text_before_the_current_line(run_pied, capsys):
    run_pied(["3i hello"], numbered_lines(5, 9))

    assert capsys.readouterr().out == "5\n6\nhello\n7\n8\n9\n"


def test_change_replaces_a_single_addressed_line(run_pied, capsys):
    run_pied(["2c hello"], numbered_lines(1, 3))

    assert capsys.readouterr().out == "1\nhello\n3\n"


def test_change_outputs_once_for_each_closed_range(run_pied, capsys):
    words = "\n".join([
        "a",
        "aah",
        "aahed",
        "aahing",
        "aahs",
        "aal",
        "aalii",
        "aaliis",
        "aals",
        "aardvark",
    ]) + "\n"

    run_pied(["/.{3}/,/.{5}/c hello"], words)

    assert capsys.readouterr().out == "a\nhello\nhello\nhello\n"


def test_substitute_replacement_can_contain_escaped_slashes(run_pied, capsys):
    run_pied(["s/[15]/z\\/z\\/z/"], numbered_lines(1, 5))

    assert capsys.readouterr().out == "z/z/z\n2\n3\n4\nz/z/z\n"


def test_substitute_replacement_can_contain_escaped_custom_delimiter(run_pied, capsys):
    run_pied(["s_[15]_z\\_z\\_z_"], numbered_lines(1, 5))

    assert capsys.readouterr().out == "z_z_z\n2\n3\n4\nz_z_z\n"


def test_substitute_can_use_a_digit_as_the_delimiter(run_pied, capsys):
    run_pied(["s1[\\15]1zzz1"], numbered_lines(1, 5))

    assert capsys.readouterr().out == "zzz\n2\n3\n4\nzzz\n"


def test_script_file_can_use_labels_and_branches(run_pied, capsys, fixtures_dir):
    script = fixtures_dir / "binary2words.pied"

    run_pied(["-f", str(script)], "101011\n0110\n")

    assert capsys.readouterr().out == "\n".join([
        "101011 in words is:",
        " in words is:",
        "one",
        "zero",
        "one",
        "zero",
        "one",
        "one",
        "0110 in words is:",
        " in words is:",
        "zero",
        "one",
        "one",
        "zero",
    ]) + "\n"
