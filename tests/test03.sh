#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

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

echo "PASS"
exit 0