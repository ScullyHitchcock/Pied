#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

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

echo "PASS"
exit 0