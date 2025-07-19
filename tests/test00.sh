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

echo "PASS"
exit 0