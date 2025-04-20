from pied_for_more import separate_cmd_txt

txts = ["3,5d",
        "1d;2q",
        "1p\n2d",
        ":loop\n3d;4q",
        "  ; 3,5d ; ; :lbl ;",
        'p; : begin;s/[^ ](.)/ \1/; t skip; q; : skip; p; b begin',
        ': start; s/00/0/; t start',
        's/;/semicolon/g;/;/q',
        '/2/d # delete  ;  4  q # quit',
        ' / 123;\n/, /567;.l \n/ s ,kkk\/,...\,g\n: start; s/00/0/; t start']


def test_1():
    res = separate_cmd_txt("3,5d")
    assert res == ["3,5d"]

def test_2():
    res = separate_cmd_txt("1d;2q")
    assert res == ["1d", "2q"]

def test_3():
    res = separate_cmd_txt("1p\n2d")
    assert res == ["1p", "2d"]

def test_4():
    res = separate_cmd_txt(":loop\n3d;4q")
    assert res == [":loop", "3d", "4q"]

def test_5():
    res = separate_cmd_txt("  ; 3,5d ; ; :lbl ;")
    assert res == ["3,5d", ":lbl"]

def test_6():
    res = separate_cmd_txt('p; : begin;s/[^ ](.)/ \1/; t skip; q; : skip; p; b begin')
    assert res == ["p", ":begin", "s/[^ ](.)/ \1/", "tskip", "q", ":skip", "p", "bbegin"]

def test_7():
    res = separate_cmd_txt(': start; s/00/0/; t start')
    assert res == [":start", "s/00/0/", "tstart"]

def test_8():
    res = separate_cmd_txt('s/;/semicolon/g;/;/q')
    assert res == ["s/;/semicolon/g", "/;/q"]

def test_9():
    res = separate_cmd_txt('/2/d # delete  ;  4  q # quit')
    assert res == ["/2/d", "4q"]

def test_10():
    res = separate_cmd_txt(' / 123;\n/, /567;.l \n/ s ,kkk\/,...\,g\n: start; s/00/0/; t start')
    assert res == ['/ 123;\n/,/567;.l \n/s,kkk\/,...\,g', ':start', 's/00/0/', 'tstart']

def test_11():
    txt = '/ssfs/, /1234/ a lol \n /ss/i okok'
    res = separate_cmd_txt(txt)
    assert res == ['/ssfs/,/1234/alol', '/ss/iokok']