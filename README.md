# text-word-frequency

Word frequency counter for text files

## Features

- Unicode-aware word tokenization
- Case-fold, minimum length, digit filtering
- Relative frequency in words-per-million (`--freq`)
- Multi-file input, JSON output

## Installation

Requires Python 3.9+. No external dependencies.

```bash
pip install .
# or directly from GitHub
pip install git+https://github.com/TataneSan/text-word-frequency.git
```

You can also run it without installing:

```bash
python -m text_word_frequency [args]
```

## Usage

```
text-word-frequency [files...] [-n N] [--min-len N] [--min-count N] [-i] [--freq] [--json]
```

### Examples

```bash
printf 'the cat sat on the mat\n' | text-word-frequency -
text-word-frequency book.txt -n 20 -i --freq
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | File error |

## License

MIT — see [LICENSE](LICENSE).
