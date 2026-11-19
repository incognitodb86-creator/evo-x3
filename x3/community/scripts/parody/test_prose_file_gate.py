"""Hermes plan U5 (Path B): --prose-file runs Hermes-written prose through the same lint, 18+ hard stops and build
as the writer path, with no writer call. Offline: scripted writer, stubbed dry build."""
from __future__ import annotations

from pathlib import Path

import render_writer_pipeline as p
from test_writer_pipeline import GOOD_SEX, home, job, scripted, stub_build  # noqa: F401 (home is a fixture)


def _prose(tmp_path, text):
    f = tmp_path / "hermes_prose.txt"
    f.write_text(text, encoding="utf-8")
    return str(f)


def test_good_prose_is_ready_without_writer_call(home, tmp_path, monkeypatch):
    calls = scripted(monkeypatch, lambda purpose: "WRITER MUST NOT BE CALLED")
    stub_build(monkeypatch)
    r = p.run_clip(job(tmp_path, "pf1", prose_file=_prose(tmp_path, GOOD_SEX)), p.load_config(home / "config.yaml"),
                   lambda *a: None)
    assert r["status"] == "READY" and r["pick"] == "hermes" and r["prose_source"] == "hermes"
    assert not [c for c in calls if c.startswith("prose") or c.startswith("rewrite")]
    assert "Deeper, the log is shaking." in (Path(r["run_dir"]) / "writer_output.txt").read_text(encoding="utf-8")


def test_youth_cue_in_prose_is_not_ready(home, tmp_path, monkeypatch):
    calls = scripted(monkeypatch, lambda purpose: GOOD_SEX)
    stub_build(monkeypatch)
    bad = GOOD_SEX.replace("At first, (S1)", "At first, (S1), 16 years old,")
    r = p.run_clip(job(tmp_path, "pf2", prose_file=_prose(tmp_path, bad), fix_once=True),
                   p.load_config(home / "config.yaml"), lambda *a: None)
    assert r["status"] == "NOT_READY" and "youth_hint" in r["pick_hard"]
    assert "rewrite" not in calls  # no writer rewrite on Path B, even with fix_once


def test_cli_refuses_empty_or_relative_prose_file(tmp_path, capsys):
    empty = tmp_path / "empty.txt"
    empty.write_text("  \n", encoding="utf-8")
    base = [str(tmp_path / "runs" / "x"), "--ask", "a", "--position", "doggy"]
    assert p.main(base + ["--prose-file", str(empty)]) == 3
    assert p.main(base + ["--prose-file", "rel.txt"]) == 3
    good = tmp_path / "g.txt"
    good.write_text(GOOD_SEX, encoding="utf-8")
    assert p.main(base + ["--prose-file", str(good), "--fix-once"]) == 3
    assert capsys.readouterr().out.count("NOT_READY") == 3
