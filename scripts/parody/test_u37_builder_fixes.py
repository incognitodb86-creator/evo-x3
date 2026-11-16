"""U37 Step C builder fixes: missing --still hard fail, absolute run paths, and hard lint for fps/aspect/throat/negatives."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_request as br
import render_writer_pipeline as p
import submit_parody_run as spr
import test_writer_pipeline as twp
import wp_lint


# ---- 1. Hard fail when --still is missing or nonexistent absolute path ----------------------------------------------
def test_writer_run_cli_missing_still_fails_hard(tmp_path, capsys):
    rd = tmp_path / "r1"
    rd.mkdir()
    rc = spr._writer_run_cli([str(rd), "--ask", "she has sex with him", "--position", "doggy"])
    out = capsys.readouterr().out
    assert rc == 3 and "NOT_READY" in out and "start still missing" in out


def test_writer_run_cli_nonexistent_absolute_still_fails_hard(tmp_path, capsys):
    rd = tmp_path / "r2"
    rd.mkdir()
    missing = tmp_path / "nope.jpg"
    rc = spr._writer_run_cli([str(rd), "--ask", "she has sex with him", "--position", "doggy", "--still", str(missing)])
    out = capsys.readouterr().out
    assert rc == 3 and "NOT_READY" in out and "start still not found" in out


def test_pipeline_continue_without_still_does_not_auto_pick(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "PIPE_DIR", tmp_path / "home")
    (tmp_path / "home").mkdir()
    prev = tmp_path / "runs" / "prev"
    prev.mkdir(parents=True)
    (prev / "pick.json").write_text(json.dumps({"status": "READY"}), encoding="utf-8")
    monkeypatch.setattr(p, "auto_still", lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not auto-pick still")))
    r = p.run_clip({"run_dir": str(tmp_path / "runs" / "c2"), "ask": "continue", "position": "doggy",
                    "continue": str(prev)}, {"model_alias": "x", "endpoint": "http://127.0.0.1:9/v1",
                                             "sampler_arm": "A", "samplers": {"A": {}}, "position_kinds": {"sex": ["doggy"]}},
                   lambda *a: None)
    assert r["status"] == "NOT_READY" and "start still missing" in r["not_ready_reason"]


def test_pipeline_nonexistent_absolute_still_fails_hard(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "PIPE_DIR", tmp_path / "home")
    (tmp_path / "home").mkdir()
    r = p.run_clip({"run_dir": str(tmp_path / "runs" / "c3"), "ask": "she has sex with him", "position": "doggy",
                    "still": str(tmp_path / "missing.jpg")},
                   {"model_alias": "x", "endpoint": "http://127.0.0.1:9/v1",
                    "sampler_arm": "A", "samplers": {"A": {}}, "position_kinds": {"sex": ["doggy"]}},
                   lambda *a: None)
    assert r["status"] == "NOT_READY" and "start still file not found" in r["not_ready_reason"]


# ---- 2. Enforce absolute run paths -----------------------------------------------------------------------------------
def test_writer_run_cli_rejects_relative_run_dir(capsys):
    rc = spr._writer_run_cli(["rel_run_dir", "--ask", "she has sex with him", "--position", "doggy", "--still", "community/x.jpg"])
    out = capsys.readouterr().out
    assert rc == 3 and "NOT_READY" in out and "absolute path" in out


def test_parody_job_rejects_relative_run_dir_override():
    with pytest.raises(ValueError, match="absolute path"):
        spr.submit_parody_job(name="Testa Char", description="Adult woman, dark hair.", run_dir_override=Path("rel_run"), dry_run=True)


def test_pipeline_cli_rejects_relative_run_dir(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(p, "PIPE_DIR", tmp_path / "home")
    (tmp_path / "home").mkdir()
    monkeypatch.setattr(p, "load_config", lambda *a: {"model_alias": "x", "endpoint": "http://127.0.0.1:9/v1",
                                                      "sampler_arm": "A", "samplers": {"A": {}}, "position_kinds": {"sex": ["doggy"]}})
    rc = p.main(["rel_run_dir", "--ask", "she has sex with him", "--position", "doggy", "--still", "community/x.jpg"])
    out = capsys.readouterr().out
    assert rc == 3 and "NOT_READY" in out and "absolute path" in out


# ---- 3. Quiet post-write rewrites (fps/aspect/throat/negatives) are hard lint failures -------------------------------
@pytest.mark.parametrize("snippet,code", [
    ("24 fps, ", "dial"),
    ("24fps, ", "dial"),
    ("in 16:9 aspect, ", "dial"),
    ("with 9:16 framing, ", "dial"),
    ("His hand slides to her throat, ", "throat"),
    ("He chokes her throat, ", "throat"),
    ("the tempo does not slow, ", "negatives"),
    ("with nothing settled, ", "negatives"),
    ("with no cuts, ", "negatives"),
    ("without pausing, ", "negatives"),
])
def test_wp_lint_makes_quiet_rewrites_hard_failures(snippet, code):
    bad = twp.GOOD_SEX.replace("At first, ", f"At first, {snippet}")
    res = wp_lint.lint(twp.full(bad), twp.ctx())
    assert code in res["hard"], (snippet, res["issues"])
    assert not res["pass"]


def test_allowed_throat_and_negatives_inside_dialogue_still_pass():
    ok = twp.GOOD_SEX.replace("gripping her hips.", "his hand on her throat, gripping her hips.")
    ok = ok.replace("Deeper, the log is shaking.", "Don't stop, no slowing down.")
    res = wp_lint.lint(twp.full(ok), twp.ctx())
    assert not ({"dial", "throat", "negatives"} & set(res["hard"])), res["issues"]


def test_build_request_lint_flags_dial_throat_negatives():
    cast = {"position": "doggy", "surface": "the bed", "still_bed": True}
    raw = ("detailed_description:\n"
           "She kneels on the bed at 24 fps in 16:9. His hand slides to her throat. The tempo does not slow.\n")
    issues, _ = br.lint_writer_prompt(raw, cast)
    codes = {it["code"] for it in issues}
    assert {"dial", "throat", "negatives"} <= codes, issues
