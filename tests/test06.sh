#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

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

echo "PASS"
exit 0