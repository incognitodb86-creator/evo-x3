"""Minimal offline text statistics helper for H5 harness verification."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TextCounts:
    lines: int
    words: int
    chars: int


def count_text(text: str) -> TextCounts:
    """Return line, word, and character counts for a string."""
    return TextCounts(
        lines=len(text.splitlines()),
        words=len(text.split()),
        chars=len(text),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Count lines, words, and characters.")
    parser.add_argument("text", help="Input text to count.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    sys.stdout.write(json.dumps(asdict(count_text(args.text))) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
