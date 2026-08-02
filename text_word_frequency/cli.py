"""Count word frequencies in text files or stdin."""

import argparse
import json
import re
import sys
from collections import Counter

__all__ = ["main"]

TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9_'-]+")

def collect(paths, lower, min_len, strip_digits):
    c = Counter()
    total = 0
    for path in paths:
        fh = sys.stdin if path == "-" else open(path, encoding="utf-8", errors="replace")
        close = fh is not sys.stdin
        try:
            for line in fh:
                for w in TOKEN_RE.findall(line):
                    if lower:
                        w = w.lower()
                    if strip_digits and any(ch.isdigit() for ch in w):
                        continue
                    if len(w) < min_len:
                        continue
                    c[w] += 1
                    total += 1
        except OSError as e:
            print("error: %s: %s" % (path, e), file=sys.stderr)
            return None, -1
        finally:
            if close:
                fh.close()
    return c, total

def main(argv=None):
    p = argparse.ArgumentParser(prog="text-word-frequency", description=__doc__,
        epilog="Exit codes: 0 success, 1 file error, 2 gate failed.")
    p.add_argument("files", nargs="*", default=["-"], help="text files (default: stdin)")
    p.add_argument("-n", "--top", type=int, default=None, help="show only top N")
    p.add_argument("--min-len", type=int, default=1)
    p.add_argument("--min-count", type=int, default=1)
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("--strip-digits", action="store_true", help="drop tokens containing digits")
    p.add_argument("--freq", action="store_true", help="show relative frequency (ppm)")
    p.add_argument("--require-word", metavar="WORD",
                   help="CI gate: exit 2 unless WORD appears at least "
                        "--require-count times (default: 1)")
    p.add_argument("--require-count", type=int, default=1, metavar="N",
                   help="occurrences required for --require-word (default: 1)")
    p.add_argument("--require-min-unique", type=int, default=None, metavar="N",
                   help="CI gate: exit 2 when fewer than N unique words")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    c, total = collect(args.files, args.ignore_case, args.min_len, args.strip_digits)
    if c is None:
        return 1
    items = [(w, n) for w, n in c.most_common() if n >= args.min_count]
    if args.top is not None:
        items = items[: args.top]

    ok = True
    if args.require_word is not None:
        needle = args.require_word.lower() if args.ignore_case else args.require_word
        if c.get(needle, 0) < args.require_count:
            ok = False
            print("gate failed: %r appears %d time(s) < required %d"
                  % (args.require_word, c.get(needle, 0), args.require_count),
                  file=sys.stderr)
    if args.require_min_unique is not None and len(c) < args.require_min_unique:
        ok = False
        print("gate failed: %d unique word(s) < required %d"
              % (len(c), args.require_min_unique), file=sys.stderr)

    if args.json:
        obj = {"total_words": total,
               "unique_words": len(c),
               "ok": ok,
               "words": [{"word": w, "count": n,
                          **({} if not args.freq else {"ppm": round(n / total * 1e6, 2) if total else 0})}
                         for w, n in items]}
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0 if ok else 2

    print("total: %d  unique: %d" % (total, len(c)))
    width = max((len(w) for w, _ in items), default=0)
    for w, n in items:
        line = "%-*s %d" % (width, w, n)
        if args.freq and total:
            line += "  (%.2f ppm)" % (n / total * 1e6)
        print(line)
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
