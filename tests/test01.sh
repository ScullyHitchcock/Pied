#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

# test_quit_on_second_line
printf "1\n2\n3\n" | python3 pied.py 2q > out.txt
printf "1\n2\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_on_second_line"

# test_quit_on_exceeded_line
printf "1\n2\n3\n" | python3 pied.py 4q > out.txt
printf "1\n2\n3\n" > expected.txt
diff -u expected.txt out.txt || fail "test_quit_on_exceeded_line"

echo "PASS"
exit 0