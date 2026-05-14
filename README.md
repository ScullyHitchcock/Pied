# Pied

Pied is a Python implementation of a small `sed`-like stream editor. It reads
text line by line, applies an editing script, and writes the transformed output
to stdout or back to input files.

This project is based on the UNSW COMP2041/9044 Pied assignment specification:
<https://cgi.cse.unsw.edu.au/~cs2041/25T1/assignments/ass2/index.html>.

## Features

- Reads from stdin or one or more input files.
- Supports default output suppression with `-n`.
- Supports script files with `-f`.
- Supports in-place editing with `-i` for file inputs.
- Supports command separators with semicolons or newlines.
- Supports comments in scripts.
- Supports numeric addresses, regex addresses, `$` for the last line, and
  address ranges.
- Implements core editing commands:
  - `p` print
  - `d` delete
  - `q` quit
  - `s` substitute
  - `a` append
  - `i` insert
  - `c` change
  - `:` label
  - `b` unconditional branch
  - `t` branch after a successful substitution

## Usage

```sh
python3 pied.py [-i] [-n] (-f SCRIPT_FILE | SCRIPT) [FILE ...]
```

When no input files are provided, Pied reads from stdin.

Use `-i` only with file inputs:

```sh
python3 pied.py -i 's/foo/bar/g' notes.txt
```

## Examples

Print lines that match a regex while suppressing default output:

```sh
seq 2 3 20 | python3 pied.py -n '/^1/p'
```

Output:

```text
11
14
17
```

The `-n` flag suppresses normal line output, so only lines explicitly printed by
`p` are shown.

Delete from a numeric address until a regex address matches:

```sh
seq 10 21 | python3 pied.py '3,/2/d'
```

Output:

```text
10
11
21
```

The range starts on the third input line and continues until a later line
matches `/2/`.

Apply substitution only inside a regex-delimited range:

```sh
seq 10 30 | python3 pied.py '/4/,/6/s/[12]/9/'
```

Output:

```text
10
11
12
13
94
95
96
17
18
19
20
21
22
23
94
95
96
27
28
29
30
```

The `s` command runs only while the current line is within a `/4/` to `/6/`
range.

Run multiple commands in one script:

```sh
seq 1 5 | python3 pied.py '4q;/2/d'
```

Output:

```text
1
3
4
```

The script deletes lines matching `/2/`, then quits after line 4 has been
processed.

Use a custom substitution delimiter:

```sh
seq 1 5 | python3 pied.py 'sX[15]Xz/z/zX'
```

Output:

```text
z/z/z
2
3
4
z/z/z
```

The delimiter after `s` does not have to be `/`, which is useful when the
replacement contains slashes.

Loop with a label and conditional branch:

```sh
echo 1000001 | python3 pied.py ': start; s/00/0/; t start'
```

Output:

```text
101
```

The `t start` command branches back to the label only after a successful
substitution, repeatedly collapsing `00` into `0`.

Use labels and branches to build a larger script:

```sh
echo 0123456789 | python3 pied.py -n 'p; : begin;s/[^ ](.)/ \1/; t skip; q; : skip; p; b begin'
```

Output:

```text
0123456789
 123456789
  23456789
   3456789
    456789
     56789
      6789
       789
        89
         9
```

This script uses `p`, `s`, `t`, `b`, `q`, and labels together to repeatedly
shift the line until no more substitutions are possible.

## Implementation Notes

The implementation is intentionally small and self-contained in `pied.py`.

- `Script` splits a script into commands and controls branch targets.
- `Command` parses and executes individual editing commands.
- `Address` matches numeric, regex, last-line, and range addresses.
- `PiedExecutor` streams input lines through the parsed script.

Pied uses a one-line lookahead so `$` can be matched without loading the whole
input into memory.

## Tests

Runtime dependencies are limited to the Python standard library. Tests use
`pytest`, listed in `requirements-dev.txt`.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

The test suite is organized by behavior:

- `tests/test_basic_commands.py` covers basic command semantics.
- `tests/test_addresses_and_scripts.py` covers addresses, ranges, script files,
  and multi-command scripts.
- `tests/test_advanced_commands.py` covers in-place editing, insertion,
  replacement, labels, and branching.

## Limitations

Pied implements a focused subset of `sed`; it is not intended to be a full
drop-in replacement. Error handling and some edge cases are intentionally
minimal, and compatibility is limited to the command forms covered by the
project tests and examples.
