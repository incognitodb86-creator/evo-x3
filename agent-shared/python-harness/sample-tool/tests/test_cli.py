"""Offline unit tests for sample_tool."""
from __future__ import annotations

import json

from sample_tool import TextCounts, count_text
from sample_tool.cli import main


def test_count_text_basic() -> None:
    assert count_text("hello world\nsecond line") == TextCounts(lines=2, words=4, chars=23)


def test_count_text_empty() -> None:
    assert count_text("") == TextCounts(lines=0, words=0, chars=0)


def test_cli_outputs_json(capsys) -> None:
    rc = main(["one two three"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"lines": 1, "words": 3, "chars": 13}
