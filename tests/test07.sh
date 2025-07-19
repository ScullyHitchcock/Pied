#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

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