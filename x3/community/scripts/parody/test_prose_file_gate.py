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


def test_hermes_skills_route_path_b_through_render_writer_pipeline():
    repo_root = Path(__file__).resolve().parents[4]
    h3_render = (repo_root / "hosts" / "x3" / "hermes" / "skills" / "h3-render" / "SKILL.md").read_text(encoding="utf-8")
    h3_writer = (repo_root / "hosts" / "x3" / "hermes" / "skills" / "h3-writer" / "SKILL.md").read_text(encoding="utf-8")
    assert "render_writer_pipeline.py" in h3_render
    assert "--prose-file" in h3_render
    assert "--position" in h3_render
    assert "--still" in h3_render
    assert "FR=/home/evo/AI/community/scripts/parody/fill_request.py" not in h3_render
    assert "render_writer_pipeline.py --prose-file" in h3_writer
    assert "fill_request.py" not in h3_writer

    live_root = repo_root / "hosts" / "x3" / "live" / "hermes" / "skills" / "custom" / "creative"
    live_render = live_root / "h3-render" / "SKILL.md"
    live_writer = live_root / "h3-writer" / "SKILL.md"
    if live_render.is_file():
        live_r = live_render.read_text(encoding="utf-8")
        assert "render_writer_pipeline.py" in live_r
        assert "--prose-file" in live_r
        assert "FR=/home/evo/AI/community/scripts/parody/fill_request.py" not in live_r
    if live_writer.is_file():
        live_w = live_writer.read_text(encoding="utf-8")
        assert "render_writer_pipeline.py --prose-file" in live_w
        assert "fill_request.py" not in live_w


def test_clone_gate_covers_stub_wording_example():
    import wp_lint
    import wp_state

    stub_wording = "## Worked example: synthetic stub\n```text\nThe lantern hangs beside the cedar doorframe.\n```\n"
    phrases = wp_state.build_cloned("WRITER PROMPT\n", [], extra_texts=[stub_wording])
    hits = wp_lint.cloned_hits("At first, the lantern hangs beside the cedar doorframe while she stands.", phrases)
    assert hits


def test_assemble_output_emits_ref_sections_s2_and_wardrobe_pulled_aside():
    slots_ref = {
        "place": "bedroom",
        "light": "soft window light",
        "hair": "blonde hair",
        "position": "doggy",
        "surface": "bed",
        "still_mode": "ref",
        "garment": "satin slip",
    }
    card = {"partners": [{"label": "S2", "sex": "man", "age": 30, "build": "athletic build"}], "summary": "(S1) on the bed"}
    out_aside = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S1) pulls her satin slip aside at one hip. By the end, soft breath.",
        card,
        slots_ref,
        2,
        "sex",
    )
    assert "<Picture 1>" in out_aside
    assert "[reference generation]" in out_aside
    assert "<Subject 2>" in out_aside.split("retention_analysis:", 1)[1]
    assert "pulled aside" in out_aside.split("retention_analysis:", 1)[1]

    out_kept = p.assemble_output(
        "[Shot 1] Medium shot. At first, (S1) stands beside the bed. By the end, soft breath.",
        card,
        slots_ref,
        2,
        "sex",
    )
    assert "fully_preserved" in out_kept.split("retention_analysis:", 1)[1]
    assert "pulled aside" not in out_kept.split("retention_analysis:", 1)[1]
