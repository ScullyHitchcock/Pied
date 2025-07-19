#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

# test_print_only_line_1_twice
printf "1\n2\n3\n" | python3 pied.py 1p > out.txt
printf "1\n1\n2\n3\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_only_line_1_twice"

# test_print_line_3_with_n
printf "x\ny\nz\n" | python3 pied.py -n 3p > out.txt
printf "z\n" > expected.txt
diff -u expected.txt out.txt || fail "test_print_line_3_with_n"

echo "PASS"
exit 0