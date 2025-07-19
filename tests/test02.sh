#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

# test_quit_by_re
printf "0\n1\n2\n" | python3 pied.py /1/q > out.txt
printf "0\n1\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_by_re"

# test_quit_on_match
printf "hello\nworld\nbye\n" | python3 pied.py /r/q > out.txt
printf "hello\nworld\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_on_match"

echo "PASS"
exit 0