import io
import unittest
from contextlib import redirect_stdout

from text_word_frequency.cli import main


class WordFrequencyTests(unittest.TestCase):
    def run_cli(self, argv, stdin_text=""):
        import sys
        old = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = main(argv)
        finally:
            sys.stdin = old
        return code, buf.getvalue()

    def test_basic_counts(self):
        code, out = self.run_cli(["-"], "the cat and the dog and the\n")
        self.assertEqual(code, 0)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertTrue(lines[0].endswith("the"))
        self.assertIn("total: 7 words, 4 unique", out)

    def test_min_count(self):
        code, out = self.run_cli(["-", "--min-count", "2"], "a a b a\n")
        self.assertIn("  a", out)
        self.assertNotIn("  b\n", out)

    def test_require_word_ok(self):
        code, _ = self.run_cli(["-", "--require-word", "hello", "-q"], "hello world\n")
        self.assertEqual(code, 0)

    def test_require_word_fail(self):
        code, _ = self.run_cli(["-", "--require-word", "missing", "-q"], "hello world\n")
        self.assertEqual(code, 2)

    def test_forbid_word_fail(self):
        code, _ = self.run_cli(["-", "--forbid-word", "hello", "-q"], "hello world\n")
        self.assertEqual(code, 2)

    def test_json(self):
        code, out = self.run_cli(["-", "--json"], "hi hi\n")
        import json
        data = json.loads(out)
        self.assertEqual(data["total_words"], 2)
        self.assertEqual(data["words"][0]["word"], "hi")


if __name__ == "__main__":
    unittest.main()
