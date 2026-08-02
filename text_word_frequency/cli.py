"""text-word-frequency: count word frequencies in a text.

Tokenizes a text into words (Unicode-aware, configurable case folding and
minimum word length) and reports each word with its occurrence count, most
frequent first.

Exit codes:
    0  success (all gates satisfied)
    1  I/O error
    2  a gate failed (--require-word, --forbid-word, --require-min-unique)
"""

import argparse
import json
import re
import sys
from collections import Counter

WORD_RE = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)


def read_text(path):
    if path is None or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def count_words(text, ignore_case, min_length):
    words = WORD_RE.findall(text)
    if ignore_case:
        words = [w.casefold() for w in words]
    words = [w for w in words if len(w) >= min_length]
    return Counter(words)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="text-word-frequency",
        description="Count word frequencies in a text file or stdin.",
    )
    parser.add_argument("file", nargs="?", default=None,
                        help="input text file (default: stdin, '-' for stdin)")
    parser.add_argument("--top", type=int, default=None, metavar="N",
                        help="show only the N most frequent words")
    parser.add_argument("--min-count", type=int, default=1, metavar="N",
                        help="only report words occurring at least N times (default 1)")
    parser.add_argument("--min-length", type=int, default=1, metavar="N",
                        help="ignore words shorter than N characters (default 1)")
    parser.add_argument("--ignore-case", action="store_true",
                        help="fold case before counting")
    parser.add_argument("--with-ratio", action="store_true",
                        help="append the share of total words per entry")
    parser.add_argument("--require-word", metavar="WORD",
                        help="exit 2 unless WORD occurs at least once")
    parser.add_argument("--forbid-word", metavar="WORD",
                        help="exit 2 if WORD occurs at least once")
    parser.add_argument("--require-min-unique", type=int, metavar="N",
                        help="exit 2 unless at least N unique words were found")
    parser.add_argument("--json", action="store_true",
                        help="report as JSON (with gates + violated list)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="suppress the word list; only gates decide the exit code")
    args = parser.parse_args(argv)

    try:
        text = read_text(args.file)
    except OSError as exc:
        print("text-word-frequency: %s" % exc, file=sys.stderr)
        return 1

    counts = count_words(text, args.ignore_case, args.min_length)
    items = [(w, c) for w, c in counts.items() if c >= args.min_count]
    items.sort(key=lambda wc: (-wc[1], wc[0]))
    if args.top is not None:
        items = items[: args.top]

    total_words = sum(counts.values())
    unique_words = len(counts)

    gates = []
    violated = []

    def gate(name, target, ok):
        ok = bool(ok)
        gates.append({"name": name, "target": target, "ok": ok})
        if not ok:
            violated.append(name)

    if args.require_word is not None:
        probe = args.require_word
        if args.ignore_case:
            probe = probe.casefold()
        gate("require-word", probe, counts.get(probe, 0) > 0)
    if args.forbid_word is not None:
        probe = args.forbid_word
        if args.ignore_case:
            probe = probe.casefold()
        gate("forbid-word", probe, counts.get(probe, 0) == 0)
    if args.require_min_unique is not None:
        gate("require-min-unique", args.require_min_unique, unique_words >= args.require_min_unique)

    if args.json:
        print(json.dumps(
            {
                "total_words": total_words,
                "unique_words": unique_words,
                "min_count": args.min_count,
                "words": [
                    dict(
                        {"word": w, "count": c},
                        **({"ratio": (c / total_words) if total_words else 0.0} if args.with_ratio else {}),
                    )
                    for w, c in items
                ],
                "gates": gates,
                "violated": violated,
                "ok": not violated,
            },
            indent=2,
        ))
    elif not args.quiet:
        for w, c in items:
            if args.with_ratio:
                ratio = (c / total_words) if total_words else 0.0
                print("%8d  %6.2f%%  %s" % (c, ratio * 100.0, w))
            else:
                print("%8d  %s" % (c, w))
        print("total: %d words, %d unique" % (total_words, unique_words))

    return 2 if violated else 0


if __name__ == "__main__":
    sys.exit(main())
