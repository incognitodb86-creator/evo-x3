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
    for skill_txt in (h3_render, live_render.read_text(encoding="utf-8") if live_render.is_file() else ""):
        if not skill_txt:
            continue
        low = skill_txt.lower()
        assert "wp_lint" in skill_txt
        assert "wp_state" in skill_txt
        assert "lint_ctx" in skill_txt
        assert "scanner" in low
        assert "memory" in low
        assert "synonym" in low
        assert "from the still" in low


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


def _local_still(tmp_path):
    import json
    from test_writer_pipeline import READ

    still = tmp_path / "still.jpg"
    still.write_bytes(b"\xff\xd8\xff\xe0dummy")
    sr = tmp_path / "local_sr.json"
    sr.write_text(json.dumps({**READ, "source": str(still)}), encoding="utf-8")
    return str(still), str(sr)


def test_prose_file_with_incomplete_headers_rebuilds_required_sections(home, tmp_path, monkeypatch):
    scripted(monkeypatch, lambda purpose: "WRITER MUST NOT BE CALLED")
    stub_build(monkeypatch)
    incomplete = (
        "subject_definitions:\n"
        "<Subject 1> is an adult woman.\n\n"
        "summary:\n"
        "(S1) and (S2) on the driftwood log.\n\n"
        "retention_analysis:\n"
        "<Subject 1>: fully_preserved.\n\n"
        "detailed_description:\n"
        + GOOD_SEX
    )
    still, sr = _local_still(tmp_path)
    j = job(tmp_path, "pf_sec", still=still, still_read=sr, still_mode="ref", prose_file=_prose(tmp_path, incomplete))
    r = p.run_clip(j, p.load_config(home / "config.yaml"), lambda *a: None)
    assert r["status"] == "READY"
    shipped = (Path(r["run_dir"]) / "writer_output.txt").read_text(encoding="utf-8")
    assert "<Picture 1>" in shipped
    assert "[reference generation]" in shipped
    ret = shipped.split("retention_analysis:", 1)[1]
    assert "<Subject 2>" in shipped.split("summary:", 1)[0]
    assert "<Subject 2>" in ret
    assert "pulled aside" in ret and "partially_preserved" in ret


def test_wp_lint_hard_sex_oral_blocks_ready(home, tmp_path, monkeypatch):
    import wp_lint
    from test_writer_pipeline import GOOD_ORAL, GOOD_TALK, ctx, full

    good_sex_full = full(GOOD_SEX)
    good_oral_full = full(GOOD_ORAL, "oral")
    assert wp_lint.lint(good_sex_full, ctx(), minimal=True)["pass"] is True
    assert wp_lint.lint(good_oral_full, ctx("oral", "blowjob"), minimal=True)["pass"] is True

    cases = [
        ("no_primary", good_sex_full.replace("PRIMARY MOTION - hard rear thrusts,", "hard rear thrusts land"), ctx()),
        ("no_tempo", good_sex_full.replace("two strokes a second", "harder and harder"), ctx()),
        ("tempo_range", good_sex_full.replace("two strokes a second", "five strokes a second"),
         ctx(cfg={"speech_words_max": 25, "tempo_range": {"sex": [0.5, 2.5]}})),
        ("contact_anatomy", good_sex_full.replace("his penis", "himself").replace("her vagina", "her"), ctx()),
        ("unbound_partner", good_sex_full.replace("<Subject 2> is", "<Other> is"), ctx(bodies=2)),
        ("shot_timestamp_placeholder", good_sex_full + " [Shot 2] At MM:05.000, close on her.", ctx()),
        ("slot_surface", good_sex_full.replace("log", "stone"), ctx()),
        ("slot_light_or_place", good_sex_full.replace("golden hour", "dim room"), ctx()),
        ("banned_skin_shine", good_sex_full.replace("wet hair", "glistening skin and hair"), ctx()),
        ("summary_role_swap",
         good_oral_full.replace("summary:\n[reference generation] (S1) and (S2) on the log.",
                                "summary:\n[reference generation] (S2) kneels in front of (S1) on the log."),
         ctx("oral", "blowjob")),
    ]
    for code, txt, c in cases:
        for minimal in (False, True):
            res = wp_lint.lint(txt, c, minimal=minimal)
            assert res["pass"] is False, f"{code} minimal={minimal} unexpectedly passed"
            assert code in res["hard"], f"{code} missing from hard={res['hard']} (minimal={minimal})"

    # Talk mode is not accidentally blocked by sex/oral craft gates
    talk_res = wp_lint.lint(full(GOOD_TALK, "talk").replace("log", "bench"), ctx("talk", "talk"), minimal=True)
    assert talk_res["pass"] is True

    # Pipeline wrapper flips READY -> NOT_READY when a hard sex/oral rule trips
    scripted(monkeypatch, lambda purpose: "WRITER MUST NOT BE CALLED")
    stub_build(monkeypatch)
    bad_dd = GOOD_SEX.replace("PRIMARY MOTION - hard rear thrusts,", "hard rear thrusts land")
    still, sr = _local_still(tmp_path)
    r = p.run_clip(job(tmp_path, "pf_hard", still=still, still_read=sr, prose_file=_prose(tmp_path, bad_dd)),
                   p.load_config(home / "config.yaml"), lambda *a: None)
    assert r["status"] == "NOT_READY" and "no_primary" in r["pick_hard"]


def test_r11_hand_lock_excluded_from_clone_corpus():
    import build_request as br
    import wp_lint
    import wp_state

    stub_wording = "## Worked example: synthetic stub\n```text\nThe lantern hangs beside the cedar doorframe.\n```\n"
    prompt_with_r11 = f'WRITER PROMPT\n"{br.R11_HAND}"\n'
    phrases = wp_state.build_cloned(prompt_with_r11, [br.R11_HAND, br.R11_HAND], extra_texts=[stub_wording])
    assert wp_lint.cloned_hits(br.R11_HAND, phrases) == []
    assert wp_lint.cloned_hits("The lantern hangs beside the cedar doorframe.", phrases)


def test_backend_routing_proof_writes_backend_json_pick_and_journal(home, tmp_path, monkeypatch):
    import io
    import json
    import subprocess
    import urllib.request

    class _FakeResp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(urllib.request, "urlopen",
                        lambda req, timeout=1.5: _FakeResp(b'{"running":["gemma4-heretic"]}'))
    orig_run = subprocess.run

    def fake_run(cmd, *a, **kw):
        if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "journalctl":
            return subprocess.CompletedProcess(cmd, 0, stdout="Nov 19 22:33:15 x3 llama-swap[1]: loaded gemma4-heretic\n", stderr="")
        return orig_run(cmd, *a, **kw)

    monkeypatch.setattr(subprocess, "run", fake_run)
    scripted(monkeypatch, lambda purpose: "WRITER MUST NOT BE CALLED")
    stub_build(monkeypatch)
    still, sr = _local_still(tmp_path)
    r = p.run_clip(job(tmp_path, "pf_backend", still=still, still_read=sr,
                       prose_file=_prose(tmp_path, GOOD_SEX), hermes_slot="gemma4-heretic"),
                   p.load_config(home / "config.yaml"), lambda *a: None)
    rd = Path(r["run_dir"])
    backend = json.loads((rd / "backend.json").read_text(encoding="utf-8"))
    pick = json.loads((rd / "pick.json").read_text(encoding="utf-8"))
    journal = (rd / "llama_swap_journal.txt").read_text(encoding="utf-8")
    assert backend["hermes_slot"] == "gemma4-heretic"
    assert backend["llama_swap_running"] == ["gemma4-heretic"]
    assert backend["journal_ok"] is True
    assert pick["hermes_slot"] == "gemma4-heretic"
    assert pick["llama_swap_running"] == ["gemma4-heretic"]
    assert "loaded gemma4-heretic" in journal


def test_backend_routing_proof_degrades_gracefully_when_down(home, tmp_path, monkeypatch):
    import json
    import subprocess
    import urllib.error
    import urllib.request

    def boom(*a, **kw):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    orig_run = subprocess.run

    def fake_run(cmd, *a, **kw):
        if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "journalctl":
            return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="No journal files")
        return orig_run(cmd, *a, **kw)

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.delenv("HERMES_SLOT", raising=False)
    scripted(monkeypatch, lambda purpose: "WRITER MUST NOT BE CALLED")
    stub_build(monkeypatch)
    still, sr = _local_still(tmp_path)
    r = p.run_clip(job(tmp_path, "pf_backend_down", still=still, still_read=sr,
                       prose_file=_prose(tmp_path, GOOD_SEX)),
                   p.load_config(home / "config.yaml"), lambda *a: None)
    rd = Path(r["run_dir"])
    backend = json.loads((rd / "backend.json").read_text(encoding="utf-8"))
    assert r["status"] == "READY"
    assert backend["hermes_slot"] == "unknown"
    assert backend["llama_swap_error"] and "URLError" in backend["llama_swap_error"]
    assert "unavailable" in (rd / "llama_swap_journal.txt").read_text(encoding="utf-8")
