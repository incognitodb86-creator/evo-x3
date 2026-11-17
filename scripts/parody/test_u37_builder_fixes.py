"""U37 Step C builder fixes: missing --still hard fail, absolute run paths, and hard lint for fps/aspect/throat/negatives."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_request as br
import render_writer_pipeline as p
import test_writer_pipeline as twp
import wp_lint


# ---- 1. Hard fail when --still is missing or nonexistent absolute path ----------------------------------------------
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
    assert code in [i["code"] for i in res["issues"]], (snippet, res["issues"])
    assert code not in res["hard"], (snippet, res["hard"])
    assert res["pass"]


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


# ---- 4. U40 / U37 decisions 2 & 4 + PixlStash merged-vault checks ------------------------------------------------------
def test_resolve_accepts_render_approved_characters_pool_and_tilde(tmp_path, monkeypatch):
    import resolve as res_mod
    pool = tmp_path / "render" / "stills" / "approved_characters" / "POOL"
    pool.mkdir(parents=True)
    img = pool / "POOL_F001.jpg"
    img.write_bytes(b"jpg")
    assert res_mod.RENDER_APPROVED_STILLS_DIR in res_mod.APPROVED_IMAGE_POOLS
    monkeypatch.setattr(res_mod, "APPROVED_IMAGE_POOLS", (pool.parent,))
    assert res_mod.validate_reference_images([str(img)]) == [str(img.resolve())]
    assert res_mod.validate_reference_images(["POOL/POOL_F001.jpg"]) == [str(img.resolve())]
    monkeypatch.setenv("HOME", str(tmp_path))
    tilde_pool = tmp_path / "AI" / "render" / "stills" / "approved_characters" / "POOL"
    tilde_pool.mkdir(parents=True)
    tilde_img = tilde_pool / "POOL_F002.jpg"
    tilde_img.write_bytes(b"jpg")
    monkeypatch.setattr(res_mod, "APPROVED_IMAGE_POOLS", (tilde_pool.parent,))
    assert res_mod.validate_reference_images(["~/AI/render/stills/approved_characters/POOL/POOL_F002.jpg"]) == [
        str(tilde_img.resolve())
    ]


def test_wp_lint_catches_enters_her_mouth_oral_silence_and_deep_in_her_oral_contact():
    assert wp_lint.MOUTH_CONTACT_RE.search("His penis enters her mouth as she leans forward.")
    bad = twp.GOOD_ORAL.replace(
        "and he slides inside her mouth until her lips seal around the shaft, holding there as she works.",
        "and his penis enters her mouth, sinking deep in her as she works.",
    ).replace(
        "(S2) says in a low voice, <d>[English] Look up at me, sand girl.</d>",
        "(S1) says in a low voice, <d>[English] Look up at me.</d>",
    )
    res = wp_lint.lint(twp.full(bad, "oral"), twp.ctx("oral", "blowjob"))
    codes = [i["code"] for i in res["issues"]]
    assert "oral_silence" in codes and "oral_contact" in codes, res["issues"]
    assert "oral_silence" not in res["hard"] and "oral_contact" not in res["hard"]
    assert res["pass"]


def test_pixlstash_lookup_uses_merged_vault_only_and_skips_if_token_absent(tmp_path, monkeypatch):
    import sqlite3
    import resolve as spr

    assert len(spr._PIXLSTASH_VAULTS) == 1
    assert spr._PIXLSTASH_VAULTS[0].as_posix().endswith("5slock/libraries/vault.db")
    db = tmp_path / "vault.db"
    con = sqlite3.connect(db)
    con.executescript(
        "CREATE TABLE character (id INTEGER PRIMARY KEY, name TEXT);"
        "CREATE TABLE picture (id INTEGER PRIMARY KEY, file_path TEXT);"
        "CREATE TABLE face (id INTEGER PRIMARY KEY, character_id INTEGER, picture_id INTEGER);"
        "INSERT INTO character VALUES (1, 'Zendaya');"
        "INSERT INTO picture VALUES (1, 'POOL/flow_more_2026-10-19/POOL_F001.jpg');"
        "INSERT INTO face VALUES (1, 1, 1);"
    )
    con.commit()
    con.close()
    monkeypatch.setattr(spr, "_PIXLSTASH_VAULTS", (db,))
    assert spr.pixlstash_character_names_for_still(
        "/home/evo/AI/render/stills/approved_characters/POOL/flow_more_2026-10-19/POOL_F001.jpg"
    ) == ["Zendaya"]


def test_pixlstash_live_api_token_skips_when_not_ready():
    cfg_dir = Path("/home/evo/.config/pixlstash")
    if not cfg_dir.is_dir() or not any(cfg_dir.iterdir()):
        pytest.skip("/home/evo/.config/pixlstash/ token not present yet")
