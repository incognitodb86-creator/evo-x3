"""Start-still guard + relative run-dir fix (Max Architect 2026-11-15, Derrick "Yes, make the fixes and rerun the
Q8 vs Q4 test"). The r1 blind test's Q4 chats dropped --still: the pipeline silently auto-picked a pool still and used a
still read that described a different picture. Relative run dirs landed outside runs/."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import render_writer_pipeline as p


@pytest.fixture
def runs(tmp_path, monkeypatch):
    r = tmp_path / "runs"
    r.mkdir()
    monkeypatch.setattr(p, "RUNS_ROOT", r)
    return r


def _img(tmp_path, name, data=b"jpegbytes"):
    f = tmp_path / name
    f.write_bytes(data)
    return f


def _read(tmp_path, source, name="sr.json", **extra):
    d = {"read": {"room": "beach", "garments": []}}
    if source is not None:
        d["source"] = str(source)
    d.update(extra)
    f = tmp_path / name
    f.write_text(json.dumps(d), encoding="utf-8")
    return f


# ---- run dir ----
def test_relative_run_dir_resolves_under_runs(runs):
    assert p.resolve_run_dir("blind/q4_ask1") == runs / "blind" / "q4_ask1"


def test_relative_run_dir_drops_runs_prefix(runs):
    assert p.resolve_run_dir("community/runs/blind/q4_ask1") == runs / "blind" / "q4_ask1"
    assert p.resolve_run_dir("runs\\blind\\q4_ask1") == runs / "blind" / "q4_ask1"


def test_absolute_run_dir_unchanged(runs, tmp_path):
    a = tmp_path / "elsewhere" / "r1"
    assert p.resolve_run_dir(str(a)) == a


@pytest.mark.parametrize("bad", ["", "../escape", "blind/../../x", "runs/"])
def test_bad_run_dir_refused(runs, bad):
    with pytest.raises(ValueError):
        p.resolve_run_dir(bad)


def test_run_clip_refuses_escaping_run_dir(runs):
    r = p.run_clip({"run_dir": "../x", "ask": "a", "position": "doggy", "still": "s.jpg"}, {}, lambda *a: None)
    assert r["status"] == "NOT_READY" and "does not resolve under" in r["not_ready_reason"]


# ---- still read matching ----
def test_match_same_path(tmp_path):
    s = _img(tmp_path, "a.jpg")
    rd = tmp_path / "rd"; rd.mkdir()
    assert p.still_read_mismatch(str(s), rd, str(_read(tmp_path, s))) == (None, None)


def test_match_by_hash_across_paths(tmp_path):
    s = _img(tmp_path, "a.jpg"); copy = _img(tmp_path, "copy_of_a.jpg")
    rd = tmp_path / "rd"; rd.mkdir()
    assert p.still_read_mismatch(str(s), rd, str(_read(tmp_path, copy))) == (None, None)


def test_mismatch_refused(tmp_path):
    s = _img(tmp_path, "F029.jpg", b"one"); other = _img(tmp_path, "F034.jpg", b"two")
    rd = tmp_path / "rd"; rd.mkdir()
    why, _ = p.still_read_mismatch(str(s), rd, str(_read(tmp_path, other)))
    assert why and "does not belong" in why


def test_source_sha256_checked(tmp_path):
    s = _img(tmp_path, "a.jpg", b"one")
    rd = tmp_path / "rd"; rd.mkdir()
    ok = _read(tmp_path, None, "ok.json", source_sha256=p._file_sha256(s))
    bad = _read(tmp_path, s, "bad.json", source_sha256="0" * 64)
    assert p.still_read_mismatch(str(s), rd, str(ok)) == (None, None)
    assert p.still_read_mismatch(str(s), rd, str(bad))[0]


def test_existing_run_dir_read_is_checked(tmp_path):
    s = _img(tmp_path, "new.jpg", b"new"); old = _img(tmp_path, "old.jpg", b"old")
    rd = tmp_path / "rd"; rd.mkdir()
    (rd / "still_read.json").write_text(json.dumps({"read": {}, "source": str(old)}), encoding="utf-8")
    assert p.still_read_mismatch(str(s), rd, None)[0]


def test_no_source_only_warns(tmp_path):
    s = _img(tmp_path, "a.jpg")
    rd = tmp_path / "rd"; rd.mkdir()
    why, warn = p.still_read_mismatch(str(s), rd, str(_read(tmp_path, None)))
    assert why is None and warn and "unverified" in warn


def test_no_read_is_fine(tmp_path):
    rd = tmp_path / "rd"; rd.mkdir()
    assert p.still_read_mismatch(str(_img(tmp_path, "a.jpg")), rd, None) == (None, None)


# ---- run_clip end to end (stops before any writer call) ----
CFG = {"model_alias": "x", "endpoint": "http://127.0.0.1:9/v1", "timeout_s": 1, "retry_backoff_s": [0],
       "sampler_arm": "B", "samplers": {"B": {"temperature": 1.0}}, "position_kinds": {"sex": ["doggy"]}}


@pytest.fixture
def home(tmp_path, monkeypatch):
    h = tmp_path / "home"; h.mkdir()
    monkeypatch.setattr(p, "PIPE_DIR", h)
    monkeypatch.setattr(p.Client, "chat", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no writer call")))
    return h


def test_run_clip_missing_still_with_read_is_not_ready(home, runs, tmp_path):
    other = _img(tmp_path, "F034.jpg")
    r = p.run_clip({"run_dir": "blind/q4_ask1", "ask": "she has sex with him", "position": "doggy",
                    "still_read": str(_read(tmp_path, other)), "character": "FCSydny"}, dict(CFG), lambda *a: None)
    assert r["status"] == "NOT_READY" and "start still missing" in r["not_ready_reason"]
    assert Path(r["run_dir"]) == runs / "blind" / "q4_ask1"


def test_run_clip_auto_with_read_is_not_ready(home, runs, tmp_path):
    r = p.run_clip({"run_dir": str(runs / "c"), "ask": "she has sex with him", "position": "doggy", "still": "auto",
                    "still_read": str(_read(tmp_path, _img(tmp_path, "x.jpg")))}, dict(CFG), lambda *a: None)
    assert r["status"] == "NOT_READY" and "--still auto" in r["not_ready_reason"]


def test_run_clip_wrong_read_is_not_ready(home, runs, tmp_path):
    s = _img(tmp_path, "F029.jpg", b"a"); other = _img(tmp_path, "F034.jpg", b"b")
    r = p.run_clip({"run_dir": str(runs / "c"), "ask": "she has sex with him", "position": "doggy", "still": str(s),
                    "still_read": str(_read(tmp_path, other))}, dict(CFG), lambda *a: None)
    assert r["status"] == "NOT_READY" and "does not belong" in r["not_ready_reason"]


def test_cli_without_still_is_not_ready(home, runs, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(p, "load_config", lambda path: dict(CFG))
    rc = p.main([str(runs / "c"), "--ask", "she has sex with him", "--position", "doggy",
                 "--still-read", str(_read(tmp_path, _img(tmp_path, "x.jpg")))])
    assert rc == 3 and "start still missing" in capsys.readouterr().out
