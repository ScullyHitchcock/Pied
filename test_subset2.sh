#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

# test_i_cmd
printf "1\n2\n3\n4\n5\n" > test.txt
python3 pied.py -i '/[24]/d' test.txt
printf "1\n3\n5\n" > expected.txt
diff -u expected.txt test.txt || fail "test_i_cmd"
rm test.txt expected.txt

# test_complex_cmd1
echo 'Punctuation characters include . , ; :' | python3 pied.py 's/;/semicolon/g;/;/q' > out.txt
echo 'Punctuation characters include . , semicolon :' > expected.txt
diff -u expected.txt out.txt || fail "test_complex_cmd1"
rm out.txt expected.txt

# test_complex_cmd2
echo '1000001' | python3 pied.py ': start; s/00/0/; t start' > out.txt
echo '101' > expected.txt
diff -u expected.txt out.txt || fail "test_complex_cmd2"
rm out.txt expected.txt

# test_complex_cmd3
echo '0123456789' | python3 pied.py -n 'p; : begin;s/[^ ](.)/ \1/; t skip; q; : skip; p; b begin' > out.txt
printf "0123456789\n 123456789\n  23456789\n   3456789\n    456789\n     56789\n      6789\n       789\n        89\n         9\n" > expected.txt
diff -u expected.txt out.txt || fail "test_complex_cmd3"
rm out.txt expected.txt

# test_append
printf "5\n6\n7\n8\n9\n" | python3 pied.py '3a hello' > out.txt
printf "5\n6\n7\nhello\n8\n9\n" > expected.txt
diff -u expected.txt out.txt || fail "test_append"
rm out.txt expected.txt

# test_insert
printf "5\n6\n7\n8\n9\n" | python3 pied.py '3i hello' > out.txt
printf "5\n6\nhello\n7\n8\n9\n" > expected.txt
diff -u expected.txt out.txt || fail "test_insert"
rm out.txt expected.txt

# test_change
printf "5\n6\n7\n8\n9\n" | python3 pied.py '3c hello' > out.txt
printf "5\n6\nhello\n8\n9\n" > expected.txt
diff -u expected.txt out.txt || fail "test_change"
rm out.txt expected.txt

echo "PASS"
exit 0
