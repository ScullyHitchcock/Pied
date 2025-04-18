#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

# test_n
printf "a\nb\nc\n" | python3 pied.py -n > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_n"

# test_quit_no_addr
printf "1\n2\n3\n" | python3 pied.py q > out.txt
printf "1\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_no_addr"

# test_quit_on_second_line
printf "1\n2\n3\n" | python3 pied.py 2q > out.txt
printf "1\n2\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_on_second_line"

# test_quit_on_exceeded_line
printf "1\n2\n3\n" | python3 pied.py 4q > out.txt
printf "1\n2\n3\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_on_exceeded_line"

# test_quit_by_re
printf "0\n1\n2\n" | python3 pied.py /1/q > out.txt
printf "0\n1\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_by_re"

# test_quit_on_match
printf "hello\nworld\nbye\n" | python3 pied.py /r/q > out.txt
printf "hello\nworld\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_on_match"

# test_quit_with_n
printf "1\n2\n3\n" | python3 pied.py -n q > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_with_n #1"
printf "1\n2\n3\n" | python3 pied.py -n 1q > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_with_n #2"
printf "1\n2\n3\n" | python3 pied.py -n /1/q > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_with_n #3"

# test_print_every_line_twice_without_n
printf "1\n2\n3\n" | python3 pied.py p > out.txt
printf "1\n1\n2\n2\n3\n3\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_every_line_twice_without_n"

# test_print_only_line_1_twice
printf "1\n2\n3\n" | python3 pied.py 1p > out.txt
printf "1\n1\n2\n3\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_only_line_1_twice"

# test_print_line_3_with_n
printf "x\ny\nz\n" | python3 pied.py -n 3p > out.txt
printf "z\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_line_3_with_n"

# test_print_on_match
printf "000\n122\nabc\n" | python3 pied.py /1/p > out.txt
printf "000\n122\n122\nabc\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_on_match"

# test_print_on_match_with_n
printf "000\n122\nabc\n" | python3 pied.py -n /1/p > out.txt
printf "122\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_on_match_with_n"

# test_delete_line_2
printf "a\nb\nc\n" | python3 pied.py 2d > out.txt
printf "a\nc\n" > expected.txt
diff -u expected.txt out.txt || fail "test_delete_line_2"

# test_delete_all_lines
printf "a\nb\nc\n" | python3 pied.py d > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_delete_all_lines"

# test_delete_line_2_with_n
printf "a\nb\nc\n" | python3 pied.py -n 2d > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_delete_line_2_with_n"

# test_delete_line_matching_2
printf "2\n1\n3\n" | python3 pied.py /2/d > out.txt
printf "1\n3\n" > expected.txt
diff -u expected.txt out.txt || fail "test_delete_line_matching_2"

# test_regex_substitute
printf "foo\nbar\nfar\n" | python3 pied.py 's/f./X/' > out.txt
printf "Xo\nbar\nXr\n" > expected.txt
diff -u expected.txt out.txt || fail "test_regex_substitute"

# test_complex_regex_substitute
printf "ab\ncd\nef\ng1\n" | python3 pied.py 's/[a-z]{2}/X/' > out.txt
printf "X\nX\nX\ng1\n" > expected.txt
diff -u expected.txt out.txt || fail "test_complex_regex_substitute"

# test_substitute_with_global_flag
printf "abc\ndef\n" | python3 pied.py 's/./X/g' > out.txt
printf "XXX\nXXX\n" > expected.txt
diff -u expected.txt out.txt || fail "test_substitute_with_global_flag"

# test_substitute_with_n_flag_no_p
printf "abc\n" | python3 pied.py -n 's/a/A/' > out.txt
printf "" > expected.txt
diff -u expected.txt out.txt || fail "test_substitute_with_n_flag_no_p"

# test_print_lines_matching_regex_1_with_n
printf "2\n5\n8\n11\n14\n17\n20\n" | python3 pied.py -n '/^1/p' > out.txt
printf "11\n14\n17\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_lines_matching_regex_1_with_n"

echo "PASS"
exit 0