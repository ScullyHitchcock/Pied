#!/bin/sh

fail() {
  echo "FAIL: $1"
  exit 1
}

# test_substitute_with_question_delim
printf "1\n2\n3\n4\n5\n" | python3 pied.py 's?[15]?Z?' > out.txt
printf "Z\n2\n3\n4\nZ\n" > expected.txt
diff -u expected.txt out.txt || fail "test_substitute_with_question_delim"

# test_substitute_with_X_delim
printf "1\n2\n3\n4\n5\n" | python3 pied.py 'sX[15]XZX' > out.txt
printf "Z\n2\n3\n4\nZ\n" > expected.txt
diff -u expected.txt out.txt || fail "test_substitute_with_X_delim"

# test_substitute_with_pipe_delim_and_g_flag
printf "a:b:c\n" | python3 pied.py 's|:|/|g' > out.txt
printf "a/b/c\n" > expected.txt
diff -u expected.txt out.txt || fail "test_substitute_with_pipe_delim_and_g_flag"

# test_multiple_commands_with_semicolon
printf "1\n2\n3\n4\n5\n" | python3 pied.py '4q;/2/d' > out.txt
printf "1\n3\n4\n" > expected.txt
diff -u expected.txt out.txt || fail "test_multiple_commands_with_semicolon"

# test_multiple_commands_semicolon_order
printf "1\n2\n3\n4\n5\n" | python3 pied.py '/2/d;4q' > out.txt
printf "1\n3\n4\n" > expected.txt
diff -u expected.txt out.txt || fail "test_multiple_commands_semicolon_order"

# test_multiple_commands_complex_combination
seq 1 20 | python3 pied.py '/2$/,/8$/d;4,6p' > out.txt
printf "1\n9\n10\n11\n19\n20\n" > expected.txt
diff -u expected.txt out.txt || fail "test_multiple_commands_complex_combination"

# test_comments_and_white_space1
seq 24 43 | python3 pied.py ' 3, 17  d  # comment' > out.txt
printf "24\n25\n41\n42\n43\n" > expected.txt
diff -u expected.txt out.txt || fail "test_comments_and_white_space1"

# test_comments_and_white_space2
seq 24 43 | python3 pied.py '/2/d # delete  ;  4  q # quit' > out.txt
printf "30\n31\n33\n34\n35\n36\n37\n38\n39\n40\n41\n43\n" > expected.txt
diff -u expected.txt out.txt || fail "test_comments_and_white_space2"

# test_special_address1
printf "1\n2\n3\n4\n5\n" | python3 pied.py '$d' > out.txt
printf "1\n2\n3\n4\n" > expected.txt
diff -u expected.txt out.txt || fail "test_special_address1"

# test_special_address2
seq 1 10000 | python3 pied.py -n '$p' > out.txt
printf "10000\n" > expected.txt
diff -u expected.txt out.txt || fail "test_special_address2"

# test_range_addresses1
seq 10 21 | python3 pied.py '3,5d' > out.txt
printf "10\n11\n15\n16\n17\n18\n19\n20\n21\n" > expected.txt
diff -u expected.txt out.txt || fail "test_range_addresses1"

# test_range_addresses2
seq 10 21 | python3 pied.py '3,/2/d' > out.txt
printf "10\n11\n21\n" > expected.txt
diff -u expected.txt out.txt || fail "test_range_addresses2"

# test_range_addresses3
seq 10 21 | python3 pied.py '/2/,4d' > out.txt
printf "10\n11\n14\n15\n16\n17\n18\n19\n" > expected.txt
diff -u expected.txt out.txt || fail "test_range_addresses3"

# test_range_addresses4
seq 10 21 | python3 pied.py '/1$/,/^2/d' > out.txt
printf "10\n" > expected.txt
diff -u expected.txt out.txt || fail "test_range_addresses4"

# test_range_addresses5
seq 10 30 | python3 pied.py '/4/,/6/s/[12]/9/' > out.txt
printf "10\n11\n12\n13\n94\n95\n96\n17\n18\n19\n20\n21\n22\n23\n94\n95\n96\n27\n28\n29\n30\n" > expected.txt
diff -u expected.txt out.txt || fail "test_range_addresses5"

# test_read_script1
printf "1\n2\n3\n4\n5\n" | python3 pied.py -f cmd1.txt > out.txt
printf "1\n3\n4\n" > expected.txt
diff -u expected.txt out.txt || fail "test_read_script1"

# test_read_script2
printf "1\n2\n3\n4\n5\n" | python3 pied.py -f cmd2.txt > out.txt
printf "1\n3\n4\n" > expected.txt
diff -u expected.txt out.txt || fail "test_read_script2"

# test_input_files
python3 pied.py '4q;/2/d' input1.txt input2.txt > out.txt
printf "1\n1\n2\n" > expected.txt
diff -u expected.txt out.txt || fail "test_input_files"

# test_input_files2
python3 pied.py '4q;/2/d' input2.txt input1.txt > out.txt
printf "1\n3\n4\n" > expected.txt
diff -u expected.txt out.txt || fail "test_input_files2"

# test_read_script_and_input_files
python3 pied.py -f cmd2.txt input1.txt input2.txt > out.txt
printf "1\n1\n2\n" > expected.txt
diff -u expected.txt out.txt || fail "test_read_script_and_input_files"


echo "PASS"
exit 0