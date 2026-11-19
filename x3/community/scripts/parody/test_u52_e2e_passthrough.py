"""U52 end-to-end tests: 17n+5 frame alignment, verbatim passthrough, advisory warnings, and graph_expect."""
from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from PIL import Image
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_request as br
import render_writer_pipeline as rwp
import run_queue as rq
import wp_lint


def _patch_inproc_writer_run(monkeypatch):
    pass


def _make_still(path: Path, w: int = 90, h: int = 160) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h), (100, 90, 80)).save(path)
    return path


def _make_home(tmp_path: Path) -> Path:
    home = tmp_path / "wp_home"
    (home / "personas").mkdir(parents=True, exist_ok=True)
    (home / "writer_prompt.md").write_text(
        "WRITER PROMPT\nWrite H3 prompts.\n\nCRAFT RULES\n- Keep audio plain.\n",
        encoding="utf-8",
    )
    cfg = {
        "model_alias": "gemma4-heretic",
        "endpoint": "http://127.0.0.1:9/v1",
        "retry_backoff_s": [0, 0, 0],
        "timeout_s": 2,
        "n_candidates": 1,
        "sampler_arm": "A",
        "samplers": {"A": {"temperature": 1.0}},
        "judge_sampler": {"temperature": 0.01, "top_k": 1},
        "lint": {"block_ready": []},
        "position_kinds": {"talk": ["talk"], "sex": ["doggy", "cowgirl", "missionary"]},
    }
    (home / "config.yaml").write_text(json.dumps(cfg), encoding="utf-8")
    return home


STILL_READ = {
    "read": {
        "room": "bedroom",
        "place": "sunlit bedroom",
        "surface": "the bed",
        "bed": True,
        "sheets": "white linen sheets",
        "floor": "oak floor",
        "pose": "standing beside the bed",
        "facing_camera": True,
        "framing": "medium shot",
        "light": "warm morning window light",
        "people": 1,
        "garments": [{"type": "dress", "name": "white slip dress", "look": "white satin"}],
        "build": "athletic",
        "skin": "natural pores",
        "hair": "blonde waves",
    }
}


def _stub_writer_prompt(kind: str) -> str:
    if kind == "talk":
        dd = (
            "[Shot 1] The camera holds a medium two-shot in warm morning window light. "
            "At first, (S1) stands beside the bed in her white slip dress. "
            "(S1) says in a teasing voice, <d>[English] Line one right here.</d> "
            "(S1) says in a playful voice, <d>[English] Line two follows fast.</d> "
            "[Shot 2] At 00:02.500, the camera cuts to a medium close-up of her face. "
            "(S1) says in a warm voice, <d>[English] Line three stays intact.</d> "
            "By the end, she smiles beside the bed, soft room tone lingering."
        )
    else:
        dd = (
            "[Shot 1] The camera holds a medium shot in warm morning window light. "
            "At first, (S1) stands beside the bed in her white slip dress. "
            "(S2) steps in and guides her onto her hands and knees on the white linen sheets, "
            "sliding her white slip dress aside to one hip where it stays, and enters her vagina from behind. "
            "As it builds, PRIMARY MOTION - steady strokes, one every second, keeping hips flush. "
            "(S1) says in a breathless voice, <d>[English] Line one right now.</d> "
            "(S1) says in a tight voice, <d>[English] Line two stays here.</d> "
            "[Shot 2] At 00:02.500, the camera cuts to a close-up of her face. "
            "(S1) says in a ragged voice, <d>[English] Line three never drops.</d> "
            "By the end, he keeps the same pace, wet skin slapping on each stroke."
        )
    return (
        "subject_definitions:\n"
        "<Picture 1> is the reference image.\n"
        "<Subject 1> is the adult woman in <Picture 1>; she is (S1).\n\n"
        "summary:\n"
        "[reference generation] (S1) in a scene beside the bed.\n\n"
        "retention_analysis:\n"
        "<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - face and hair from <Picture 1>.\n\n"
        f"detailed_description:\n{dd}\n\n"
        "overall_soundscape:\n"
        "Quiet bedroom ambience continues through the clip.\n"
    )


@pytest.mark.parametrize(
    "case,position,ask,still_mode",
    [
        ("talk", "talk", "she talks to him beside the bed", "guide"),
        ("single_position", "doggy", "doggy on the bed", "guide"),
        ("guide_mode", "doggy", "doggy on the bed in guide mode", "guide"),
        ("ref_mode", "doggy", "doggy on the bed in ref mode", "ref"),
    ],
)
def test_u52_e2e_pipeline_to_request_frames_and_passthrough(tmp_path, monkeypatch, case, position, ask, still_mode):
    home = _make_home(tmp_path / case)
    monkeypatch.setattr(rwp, "PIPE_DIR", home)
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / case / "runs")

    still_path = _make_still(tmp_path / case / "still.png")
    sr_path = tmp_path / case / "still_read.json"
    sr_path.write_text(json.dumps(STILL_READ), encoding="utf-8")
    rd = tmp_path / case / "run"

    kind = "talk" if position == "talk" else "sex"
    writer_reply = _stub_writer_prompt(kind)
    seen_briefs = []

    def fake_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose=""):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if str(purpose).startswith("beat_card"):
            return json.dumps({
                "clip_seconds": 5.2,
                "summary": "clip summary",
                "camera": "medium shot",
                "partners": [],
                "anchor": {"action": "stands beside the bed", "sound": "room tone"},
                "onset": {"action": "moves onto the bed", "sound": "sheets rustle"},
                "development": {"line_topics": ["a", "b", "c"], "primary_motion": "steady strokes",
                                "tempo_word": "every second", "contact_keyword": "inside", "sound": "breath"},
                "result": {"action": "keeps going", "sound": "room tone"},
                "end_state": {"pose": "on the bed", "garments": {"dress": "aside"}, "contact": "inside", "camera": "close", "pov": False},
            })
        if str(purpose).startswith("prose_"):
            seen_briefs.append(messages[1]["content"])
            return writer_reply
        raise AssertionError(f"unexpected extra LLM call: {purpose}")

    monkeypatch.setattr(rwp.Client, "chat", fake_chat)
    _patch_inproc_writer_run(monkeypatch)

    rc = rwp.main([
        str(rd),
        "--ask", ask,
        "--position", position,
        "--still", str(still_path),
        "--still-read", str(sr_path),
        "--character", "FCSydny",
        "--config", str(home / "config.yaml"),
        "--frames", "120",
        "--still-mode", still_mode, "--debug",
    ])
    assert rc == 0, (rd / "clip_NOT_READY.txt").read_text(encoding="utf-8") if (rd / "clip_NOT_READY.txt").exists() else ""

    # Writer saw snapped 124 frames BEFORE writing, plus R7 no-header guidance
    assert seen_briefs and "124 frames" in seen_briefs[0]
    assert "overall_soundscape" in seen_briefs[0]

    req = json.loads((rd / "clip" / "request.api.json").read_text(encoding="utf-8"))
    slots = json.loads((rd / "slots.json").read_text(encoding="utf-8"))
    build_rep = json.loads((rd / "build_report.json").read_text(encoding="utf-8"))
    pick = json.loads((rd / "pick.json").read_text(encoding="utf-8"))

    # Frame alignment across graph, slots, build_report, and run_queue.graph_expect
    assert req["c0"]["inputs"]["length"] == 124
    assert slots["frames"] == 124
    assert build_rep["frames"] == 124
    assert rq.graph_expect(req)[0] == 124

    # Verbatim writer text (including 3rd spoken line, [Shot 2], and audio header) reaches c0.inputs.prompt
    c0_prompt = req["c0"]["inputs"]["prompt"]
    expected_core = writer_reply.strip()
    if still_mode == "ref":
        assert c0_prompt == f"{br.REF_MODE_PICTURE1_LEAD}\n\n{expected_core}"
        assert not any(n.get("class_type") == "MiniMaxH3AddGuide" for n in req.values())
        assert req["c0"]["inputs"]["ref_image_size"] == "max"
    else:
        assert c0_prompt == expected_core
        assert any(n.get("class_type") == "MiniMaxH3AddGuide" for n in req.values())

    assert "Line three" in c0_prompt
    assert "[Shot 2] At 00:02.500," in c0_prompt
    assert "overall_soundscape:" in c0_prompt
    assert "consenting adults" not in c0_prompt.lower()

    # Audio header emits a loud warning without stripping or blocking READY
    assert pick["status"] == "READY"
    assert any("! WARNING" in w and "overall_soundscape" in w for w in pick["warnings"])


def test_align_h3_frames_and_graph_expect_all_node_types():
    assert br.align_h3_frames(120) == 124
    assert br.align_h3_frames(192) == 192
    assert br.align_h3_frames(243) == 243
    with pytest.raises(ValueError):
        br.align_h3_frames(244)
    with pytest.raises(ValueError):
        br.align_h3_frames(0)

    for ct in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo", "EmptyMiniMaxH3LatentAV"):
        g = {"n1": {"class_type": ct, "inputs": {"length": 120, "width": 768, "height": 1344}}}
        assert rq.graph_expect(g) == (124, (768, 1344)), ct
        g_ok = {"n1": {"class_type": ct, "inputs": {"length": 192, "width": 768, "height": 1344}}}
        assert rq.graph_expect(g_ok) == (192, (768, 1344)), ct


def test_summary_line_queued_and_surface_mismatch_warning(tmp_path, monkeypatch):
    assert "queued=True" in rwp.summary_line({"status": "READY", "run_dir": str(tmp_path), "submitted": True})
    assert "queued=False" in rwp.summary_line({"status": "READY", "run_dir": str(tmp_path), "submitted": False})

    home = _make_home(tmp_path / "surf")
    monkeypatch.setattr(rwp, "PIPE_DIR", home)
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "surf" / "runs")
    still_path = _make_still(tmp_path / "surf" / "still.png")
    sr_path = tmp_path / "surf" / "sr.json"
    sr_path.write_text(json.dumps({
        "read": {**STILL_READ["read"], "surface": "wooden sideboard", "bed": False}
    }), encoding="utf-8")

    def fake_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose=""):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if str(purpose).startswith("beat_card"):
            return "not json"
        return _stub_writer_prompt("sex").replace(
            "PRIMARY MOTION - steady strokes, one every second, keeping hips flush.",
            "PRIMARY MOTION - she rises and sinks at one cycle every second as his hips lift a few inches to meet each sink.",
        )

    monkeypatch.setattr(rwp.Client, "chat", fake_chat)
    _patch_inproc_writer_run(monkeypatch)
    rc = rwp.main([
        str(tmp_path / "surf" / "run"),
        "--ask", "cowgirl on the sideboard",
        "--position", "cowgirl",
        "--still", str(still_path),
        "--still-read", str(sr_path),
        "--character", "FCSydny",
        "--config", str(home / "config.yaml"),
        "--frames", "120",
    ])
    assert rc == 0
    pick = json.loads((tmp_path / "surf" / "run" / "pick.json").read_text(encoding="utf-8"))
    assert pick["status"] == "READY"
    assert any("surface_mismatch" in w for w in pick["warnings"])


def test_wp_lint_shot_timestamps_and_beta7_audio_warning():
    good_cuts = (
        "subject_definitions:\n<Subject 1> is adult.\nsummary:\nclip.\nretention_analysis:\nkept.\n"
        "detailed_description:\n[Shot 1] Wide shot. At first, (S1) sits. "
        "[Shot 2] At 00:02.500, cuts to medium. [Shot 3] At 00:04.000, cuts to close. By the end, she smiles.\n"
    )
    res_ok = wp_lint.lint(good_cuts, {"kind": "talk", "slots": {"clip_seconds": 5.2}, "cfg": {}})
    assert "shot_timestamp" not in [i["code"] for i in res_ok["issues"]]
    assert "timestamp" not in [i["code"] for i in res_ok["issues"]]

    bad_cuts = good_cuts.replace("00:04.000", "00:02.000")
    res_bad = wp_lint.lint(bad_cuts, {"kind": "talk", "slots": {"clip_seconds": 5.2}, "cfg": {}})
    assert "shot_timestamp" in [i["code"] for i in res_bad["issues"]]
    assert "shot_timestamp" not in res_bad["hard"]

    past_len = good_cuts.replace("00:04.000", "00:07.000")
    res_past = wp_lint.lint(past_len, {"kind": "talk", "slots": {"clip_seconds": 5.2}, "cfg": {}})
    assert "shot_timestamp" in [i["code"] for i in res_past["issues"]]
    assert "shot_timestamp" not in res_past["hard"]

    with_hdr = good_cuts + "\noverall_soundscape:\nRoom tone.\n"
    res_hdr = wp_lint.lint(with_hdr, {"kind": "talk", "slots": {"clip_seconds": 5.2}, "cfg": {}})
    hdr_iss = [i for i in res_hdr["issues"] if i["code"] == "audio_header_beta7"]
    assert hdr_iss and hdr_iss[0]["note"].startswith("! WARNING") and hdr_iss[0]["hard"] is False
