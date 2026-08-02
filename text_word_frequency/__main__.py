"""Entry point for `python -m text_word_frequency`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
