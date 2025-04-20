from pied_for_more import parse_single_command

def test_1():
    res = parse_single_command("3,5d")
    assert res['addr1'] == '3'
    assert res['addr2'] == '5'
    assert res['cmd'] == 'd'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_cmd_2():
    res = parse_single_command("1d")
    assert res['addr1'] == '1'
    assert res['addr2'] is None
    assert res['cmd'] == 'd'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_cmd_3():
    res = parse_single_command("2q")
    assert res['addr1'] == '2'
    assert res['addr2'] is None
    assert res['cmd'] == 'q'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_cmd_4():
    res = parse_single_command(":loop")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == ':'
    assert res['args'] is None
    assert res['label_name'] == 'loop'
    assert res['branch_label'] is None

def test_cmd_5():
    res = parse_single_command(":lbl")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == ':'
    assert res['args'] is None
    assert res['label_name'] == 'lbl'
    assert res['branch_label'] is None

def test_cmd_6():
    res = parse_single_command("s/[^ ](.)/ \1/")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('[^ ](.)', ' \1', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_cmd_7():
    res = parse_single_command("tskip")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 't'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] == 'skip'

def test_cmd_8():
    res = parse_single_command(":skip")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == ':'
    assert res['args'] is None
    assert res['label_name'] == 'skip'
    assert res['branch_label'] is None

def test_cmd_10():
    res = parse_single_command("s/00/0/")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('00', '0', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_cmd_13():
    res = parse_single_command("/2/d")
    assert res['addr1'] == "/2/"
    assert res['addr2'] is None
    assert res['cmd'] == 'd'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_cmd_14():
    res = parse_single_command("/ 123;\n/,/567;.l \n/s,kkk\/,...\,g")
    assert res['addr1'] == "/ 123;\n/"
    assert res['addr2'] == "/567;.l \n/"
    assert res['cmd'] == 's'
    assert res['args'] == ("kkk\/", "...\\", "g")
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_1():
    res = parse_single_command("3q")
    assert res['addr1'] == '3'
    assert res['addr2'] is None
    assert res['cmd'] == 'q'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_2():
    res = parse_single_command("/.1/q")
    assert res['addr1'] == "/.1/"
    assert res['addr2'] is None
    assert res['cmd'] == 'q'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_3():
    res = parse_single_command("/^.+5$/q")
    assert res['addr1'] == "/^.+5$/"
    assert res['addr2'] is None
    assert res['cmd'] == 'q'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_4():
    res = parse_single_command("/1{3}/q")
    assert res['addr1'] == "/1{3}/"
    assert res['addr2'] is None
    assert res['cmd'] == 'q'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_5():
    res = parse_single_command("2p")
    assert res['addr1'] == '2'
    assert res['addr2'] is None
    assert res['cmd'] == 'p'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_6():
    res = parse_single_command("4p")
    assert res['addr1'] == '4'
    assert res['addr2'] is None
    assert res['cmd'] == 'p'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_7():
    res = parse_single_command("/^7/p")
    assert res['addr1'] == "/^7/"
    assert res['addr2'] is None
    assert res['cmd'] == 'p'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_8():
    res = parse_single_command("p")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 'p'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_9():
    res = parse_single_command("s/[15]/zzz/")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('[15]', 'zzz', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_10():
    res = parse_single_command("s/e//")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('e', '', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_11():
    res = parse_single_command("s/e//g")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('e', '', 'g')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_12():
    res = parse_single_command("5s/1/2/")
    assert res['addr1'] == '5'
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('1', '2', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_13():
    res = parse_single_command("/1.1/s/1/-/g")
    assert res['addr1'] == "/1.1/"
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('1', '-', 'g')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_14():
    res = parse_single_command("s?[15]?zzz?")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('[15]', 'zzz', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_15():
    res = parse_single_command("s_[15]_zzz_")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('[15]', 'zzz', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_16():
    res = parse_single_command("sX[15]Xz/z/zX")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == ('[15]', 'z/z/z', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_17():
    res = parse_single_command("/4/,/6/s/[12]/9/")
    assert res['addr1'] == "/4/"
    assert res['addr2'] == "/6/"
    assert res['cmd'] == 's'
    assert res['args'] == ('[12]', '9', '')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_18():
    res = parse_single_command(":start")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == ':'
    assert res['args'] is None
    assert res['label_name'] == 'start'
    assert res['branch_label'] is None

def test_txt_19():
    res = parse_single_command("tskip")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 't'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] == "skip"

def test_txt_20():
    res = parse_single_command("bbegin")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 'b'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] == "begin"

def test_txt_21():
    res = parse_single_command("3ahello")
    assert res['addr1'] == '3'
    assert res['addr2'] is None
    assert res['cmd'] == 'a'
    assert res['args'] == 'hello'
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_22():
    res = parse_single_command("3ihello")
    assert res['addr1'] == '3'
    assert res['addr2'] is None
    assert res['cmd'] == 'i'
    assert res['args'] == 'hello'
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_23():
    res = parse_single_command("3chello")
    assert res['addr1'] == '3'
    assert res['addr2'] is None
    assert res['cmd'] == 'c'
    assert res['args'] == 'hello'
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_24():
    res = parse_single_command("s/;/semicolon/g")
    assert res['addr1'] is None
    assert res['addr2'] is None
    assert res['cmd'] == 's'
    assert res['args'] == (';', 'semicolon', 'g')
    assert res['label_name'] is None
    assert res['branch_label'] is None

def test_txt_25():
    res = parse_single_command("/;/q")
    assert res['addr1'] == "/;/"
    assert res['addr2'] is None
    assert res['cmd'] == 'q'
    assert res['args'] is None
    assert res['label_name'] is None
    assert res['branch_label'] is None