# text-word-frequency

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Count word frequencies in a text file or stdin — top N, minimum count, case folding, and CI-friendly exit codes.

## Features

- Unicode-aware word tokenization (letters/digits, keeps inner apostrophes)
- `--top N` to keep only the N most frequent words
- `--min-count N` to filter rare words, `--min-length N` to skip short ones
- `--ignore-case` case-folding
- `--with-ratio` share of total words per entry
- Gates: `--require-word`, `--forbid-word`, `--require-min-unique` (exit 2 on failure)
- `--json` machine-readable report; `-q/--quiet` for gate-only checks

## Install

```bash
pip install .
# or directly:
pip install git+https://github.com/TataneSan/text-word-frequency.git
```

## Usage

```bash
# Top 5 words of a file
text-word-frequency book.txt --top 5
#        240  the
#        198  and
#        ...

# Count stdin, ignoring case
cat book.txt | text-word-frequency --ignore-case --top 3

# Words appearing at least 10 times
text-word-frequency book.txt --min-count 10

# JSON report
text-word-frequency book.txt --json | jq '.words[0]'
```

## CI usage

Exit code 2 when a gate fails:

```bash
text-word-frequency README.md --require-word install || exit $?
text-word-frequency draft.txt --forbid-word TODO --ignore-case -q
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0    | success |
| 1    | I/O error |
| 2    | a gate failed |

## License

MIT — see [LICENSE](LICENSE).
