# test_pied.py
import sys
import io
import pied  # 这里假设你的文件名是 pied.py

def run_test(stdin_text, argv_args):
    # 模拟命令行参数
    sys.argv = ['pied.py'] + argv_args
    # 模拟标准输入
    sys.stdin = io.StringIO(stdin_text)

    # 运行 pied 的主程序
    pied.main()

print("=== TEST: delete line 2 ===")
run_test("a\nb\nc\n", ['2d'])

print("=== TEST: print line 3 with -n ===")
run_test("x\ny\nz\n", ['-n', '3p'])

print("=== TEST: regex substitute ===")
run_test("foo\nbar\nfar\n", ['s/f./X/'])

print("=== TEST: quit on match ===")
run_test("hello\nworld\nbye\n", ['/r/q'])