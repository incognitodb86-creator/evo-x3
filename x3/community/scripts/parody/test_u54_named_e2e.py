"""U54 Fix 4 end-to-end tests: named talk clip and named spoof clip through the real pipeline (dry, no queue)."""
from __future__ import annotations

import io
import json
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from PIL import Image

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import render_writer_pipeline as rwp
import submit_parody_run as spr


def _patch_inproc_writer_run(monkeypatch):
    def _fake_run(cmd, **kw):
        assert Path(cmd[1]).name == "submit_parody_run.py" and cmd[2] == "writer-run", cmd
        assert "--queue" not in cmd
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = spr.main(cmd[2:])
        return subprocess.CompletedProcess(cmd, rc, out.getvalue(), err.getvalue())
    monkeypatch.setattr(rwp.subprocess, "run", _fake_run)


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
    (home / "config.yaml").write_text(
        json.dumps({
            "version": "u54-test",
            "endpoint": "http://127.0.0.1:8080/v1",
            "model_alias": "gemma4-heretic",
            "thinking": False,
            "timeout_s": 60,
            "retry_backoff_s": [1],
            "writer_prompt": "writer_prompt.md",
            "persona": "current",
            "n_candidates": 1,
            "min_ready_score": 60,
            "tie_points": 3,
            "sampler_arm": "A",
            "samplers": {"A": {"temperature": 1.0, "top_p": 0.95, "top_k": 64, "min_p": 0.10}},
            "beat_card_sampler": {"temperature": 0.7},
            "beat_card_max_tokens": 1200,
            "prose_max_tokens": 1000,
            "judge_sampler": {"temperature": 0.01, "top_k": 1},
            "judge_seed": 12345,
            "blacklist_cap": 20,
            "log_retention_days": 14,
            "log_cap_mb": 50,
            "scene_archive_days": 30,
            "shared_state_dir": str(home),
            "lint": {"speech_words_max": 25, "blacklist_ratio": 0.8, "words_min": 50, "words_max": 220,
                     "pen_phase_no_sound": 5, "opening_ratio": 0.85, "filler_lines": [],
                     "tempo_range": {"talk": [0.2, 2.5], "sex": [0.5, 2.5]}},
            "position_kinds": {"talk": ["talk"], "sex": ["missionary", "doggy"]},
        }),
        encoding="utf-8",
    )
    return home


def _still_read_file(path: Path) -> Path:
    sr = {
        "read": {
            "room": "bedroom",
            "place": "bedroom",
            "surface": "vanity table",
            "bed": True,
            "sheets": "silk sheets",
            "floor": "plush rug",
            "pose": "sitting, leaning towards mirror",
            "facing_camera": False,
            "framing": "medium close-up",
            "light": "warm lamp light",
            "people": 1,
            "garments": [{"type": "top", "name": "satin camisole", "look": "pale pink"}],
            "build": "slender",
            "skin": "soft, matte",
            "hair": "long wavy blonde",
        },
        "source": str(path),
    }
    p = path.parent / "sr.json"
    p.write_text(json.dumps(sr), encoding="utf-8")
    return p


def test_e2e_named_talk_clip_cassie(tmp_path, monkeypatch):
    _patch_inproc_writer_run(monkeypatch)
    monkeypatch.setattr(rwp, "PIPE_DIR", _make_home(tmp_path))
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "runs")
    still = _make_still(tmp_path / "still.png")
    srp = _still_read_file(still)
    run_dir = tmp_path / "runs" / "cassie_talk_e2e"

    ask_lines = ["You look good.", "So good.", "You can do this.", "Just breathe."]
    ask = (
        "Cassie Howard (Euphoria) parody: getting ready for a house party, nervous, rehearsing to her reflection. "
        "(S1) whispers, <d>[English] You look good.</d> "
        "(S1) says softly, <d>[English] So good.</d> "
        "(S1) says, <d>[English] You can do this.</d> "
        "(S1) says, <d>[English] Just breathe.</d>"
    )

    def _fake_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose="chat", **kw):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if purpose.startswith("beat_card"):
            return json.dumps({
                "summary": "(S1) rehearses in front of the vanity mirror before a house party.",
                "anchor": {"pose": "sitting, leaning towards mirror", "camera": "The camera holds a medium close-up in warm lamp light.", "sound": "Soft cloth rustles."},
                "onset": {"action": "She leans closer to the mirror.", "sound": "A shaky breath."},
                "development": {"primary_motion": "She adjusts her hair and steadies her expression.", "sound": "Her quiet voice."},
                "result": {"end_state": "She grabs her bag and stands.", "sound": "The bag strap clicks."},
                "line_topics": [
                    {"speaker": "S1", "topic": "reassuring herself"},
                    {"speaker": "S1", "topic": "repeating it"},
                    {"speaker": "S1", "topic": "forcing confidence"},
                    {"speaker": "S1", "topic": "calming breath"},
                ],
                "end_state": {"pose": "standing beside the vanity table", "garments": {"satin camisole": "on"}, "contact": None, "camera": "medium close-up", "pov": False},
            })
        return (
            "[Shot 1] The camera holds a medium close-up beside the vanity table in warm lamp light. "
            "At first, (S1) sits leaning towards the mirror, a small anxious smile flickering. "
            "(S1) whispers in a shaky voice, <d>[English] You look good.</d> "
            "(S1) says softly, <d>[English] So good.</d> "
            "As it builds, she takes a deep breath and searches her reflection. "
            "(S1) says in a quiet, forced voice, <d>[English] You can do this.</d> "
            "(S1) says, <d>[English] Just breathe.</d> "
            "By the end, she grabs her bag from the vanity and stands up quickly as soft cloth rustles."
        )

    monkeypatch.setattr(rwp.Client, "chat", _fake_chat)
    cfg = rwp.load_config(rwp.PIPE_DIR / "config.yaml")
    res = rwp.run_clip(
        {"run_dir": str(run_dir), "ask": ask, "position": "talk", "still": str(still), "still_read": str(srp)},
        cfg,
        lambda *a: None,
    )
    assert res["status"] == "READY", (res.get("error"), res.get("traceback"))
    prompt_txt = (run_dir / "prompt.txt").read_text(encoding="utf-8")
    report = json.loads((run_dir / "build_report.json").read_text(encoding="utf-8"))
    stems = (report.get("refmods") or {}).get("stems") or []

    assert "Cassie Howard" in prompt_txt and "Sydney Sweeney" in prompt_txt
    assert any("sydneysweeney" in s.lower() for s in stems), stems
    assert not any("oc_poolclub" in s.lower() for s in stems), stems
    for line in ask_lines:
        assert line in prompt_txt, f"Missing ask line: {line}"
    assert report.get("submitted") is False


def test_e2e_named_spoof_clip_daenerys(tmp_path, monkeypatch):
    _patch_inproc_writer_run(monkeypatch)
    monkeypatch.setattr(rwp, "PIPE_DIR", _make_home(tmp_path))
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "runs")
    still = _make_still(tmp_path / "still.png")
    srp = _still_read_file(still)
    run_dir = tmp_path / "runs" / "daenerys_spoof_e2e"

    ask_lines = ["Where are my dragons?", "Do not lie to me."]
    ask = (
        "Daenerys Targaryen noir detective spoof: interrogating a suspect under a desk lamp. "
        "(S1) says coldly, <d>[English] Where are my dragons?</d> "
        "(S1) leans in and says, <d>[English] Do not lie to me.</d>"
    )

    def _fake_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose="chat", **kw):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if purpose.startswith("beat_card"):
            return json.dumps({
                "summary": "(S1) interrogates a suspect in a noir detective spoof.",
                "anchor": {"pose": "sitting, leaning towards mirror", "camera": "The camera holds a medium close-up in hard side light.", "sound": "Rain taps the glass."},
                "onset": {"action": "She leans across the table.", "sound": "Chair creaks."},
                "development": {"primary_motion": "She narrows her eyes and taps the table.", "sound": "Sharp knock on wood."},
                "result": {"end_state": "She holds her cold stare.", "sound": "Steady rain."},
                "line_topics": [
                    {"speaker": "S1", "topic": "demanding where the dragons are"},
                    {"speaker": "S1", "topic": "warning not to lie"},
                ],
                "end_state": {"pose": "leaning forward over the table", "garments": {"satin camisole": "on"}, "contact": None, "camera": "medium close-up", "pov": False},
            })
        return (
            "[Shot 1] The camera holds a medium close-up in hard side light with deep shadow. "
            "At first, (S1) sits leaning forward over the table, eyes locked ahead. "
            "(S1) says in a calm, icy voice, <d>[English] Where are my dragons?</d> "
            "As it builds, she leans closer and taps the table edge. "
            "(S1) says in a low, firm voice, <d>[English] Do not lie to me.</d> "
            "By the end, she holds her steady gaze as rain taps the windowpane."
        )

    monkeypatch.setattr(rwp.Client, "chat", _fake_chat)
    cfg = rwp.load_config(rwp.PIPE_DIR / "config.yaml")
    res = rwp.run_clip(
        {"run_dir": str(run_dir), "ask": ask, "position": "talk", "still": str(still), "still_read": str(srp)},
        cfg,
        lambda *a: None,
    )
    assert res["status"] == "READY", (res.get("error"), res.get("traceback"))
    prompt_txt = (run_dir / "prompt.txt").read_text(encoding="utf-8")
    report = json.loads((run_dir / "build_report.json").read_text(encoding="utf-8"))
    stems = (report.get("refmods") or {}).get("stems") or []

    assert "Daenerys" in prompt_txt and "Emilia Clarke" in prompt_txt
    assert any("emiliaclarke" in s.lower() for s in stems), stems
    for line in ask_lines:
        assert line in prompt_txt, f"Missing ask line: {line}"
    assert report.get("submitted") is False
