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

Print only the second line:

```sh
printf 'alpha\nbeta\ngamma\n' | python3 pied.py -n '2p'
```

Delete a range of lines:

```sh
seq 1 5 | python3 pied.py '2,4d'
```

Substitute all colons with slashes:

```sh
printf 'a:b:c\n' | python3 pied.py 's|:|/|g'
```

Use a script file:

```sh
printf '101011\n' | python3 pied.py -f examples/binary2words.pied
```

Reverse characters on each input line:

```sh
printf 'stressed\n' | python3 pied.py -f examples/rev.pied
```

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
