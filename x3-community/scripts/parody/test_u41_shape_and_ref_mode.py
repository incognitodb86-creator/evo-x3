"""U41 tests: still shape check + --aspect auto + --still-mode guide|ref + S3 + writer-run/pipeline pass-through."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from PIL import Image
import pytest

import build_request as br
import render_writer_pipeline as rwp
import fill_request as fr


def _make_png(path: Path, w: int, h: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h), (120, 80, 60)).save(path)
    return path


def _parody_resolved() -> Dict[str, Any]:
    return {
        "mode": "parody",
        "index_status": "good",
        "index_flag": None,
        "loaded_refmods": ["minimaxh3_oc_poolclub_v1_refmod_visual"],
        "names": ["FCSydny"],
        "character": "FCSydny",
        "actor": "FCSydny",
        "description": "an adult woman, twenty-eight years of age, dark hair, natural skin",
        "refmod_slots": {
            "mod_1": {"path": "minimaxh3_oc_poolclub_v1_refmod_visual.safetensors", "strength": 1.0, "copies": 1},
            "mod_2": {"path": "minimaxh3_oc_poolclub_v1_refmod_audio.safetensors", "strength": 1.0, "copies": 1},
            "mod_3": {"path": "(none)", "strength": 1.0, "copies": 1},
            "mod_4": {"path": "(none)", "strength": 1.0, "copies": 1},
            "mod_5": {"path": "(none)", "strength": 1.0, "copies": 1},
            "mod_6": {"path": "(none)", "strength": 1.0, "copies": 1},
            "mod_7": {"path": "(none)", "strength": 1.0, "copies": 1},
            "mod_8": {"path": "(none)", "strength": 1.0, "copies": 1},
        },
        "tone": "parody",
    }


WRITER_READ = {
    "read": {
        "room": None,
        "place": "beach at sunset",
        "surface": "driftwood log",
        "bed": False,
        "sheets": None,
        "floor": "sand",
        "pose": "leaning against a log",
        "facing_camera": True,
        "framing": "medium shot",
        "light": "golden hour, sunset glow",
        "people": 1,
        "garments": [
            {"type": "bodysuit", "name": "sheer beige bodysuit", "look": "wet, translucent, tight"},
        ],
        "build": "athletic, toned",
        "skin": "wet, glistening",
        "hair": "blonde, wet, wind-blown",
    }
}

GOOD_SEX_DD = (
    "[Shot 1] The camera holds a low three-quarter angle at hip height beside the driftwood log. At first, (S1) leans "
    "against the log in the golden hour glow, facing the lens, her sheer beige bodysuit clinging wet to her hips, and the "
    "surf hisses behind her. (S2) steps in from the left in dark swim trunks and turns her by the waist; she bends forward "
    "and drops to her hands and knees on the sand, her forearms braced on the bleached log as the wood creaks under her "
    "weight. He kneels behind her so his hips line up with hers, hooks the bodysuit at the back and pulls it aside to one "
    "hip, where it stays, and enters her vagina from behind with a low grunt. He sinks his penis in to the hilt and stays "
    "buried in her vagina through every drive. As it builds, PRIMARY MOTION - hard rear thrusts, two strokes a second, "
    "from behind with her forearms on the log; her wet hair swings and her body jolts forward on each slap of skin. "
    "(S2) says in a low voice, <d>[English] Sand on your knees, and you still push back.</d> (S1) says in a breathless "
    "voice, <d>[English] Deeper, the log is shaking.</d> By the end, she is still rocking back onto him and he keeps the "
    "same pace, gripping her hips. The wet slap of skin and her ragged gasps ride over the waves."
)

WRITER_RAW = (
    "subject_definitions:\n"
    "<Picture 1> is the reference image.\n"
    "<Subject 1> is an adult woman, twenty-eight years of age, with blonde hair.\n"
    "<Subject 2> is an adult man, thirty-one years of age, of broad build, in dark swim trunks.\n\n"
    "summary:\n(S1) and (S2) on the log.\n\n"
    "retention_analysis:\nkept.\n\n"
    f"detailed_description:\n{GOOD_SEX_DD}\n"
)

MMF_READ = {
    "read": {
        "room": "beach",
        "place": "on a driftwood log",
        "surface": "log",
        "bed": False,
        "floor": "sand",
        "pose": "leaning, sitting",
        "facing_camera": True,
        "framing": "medium shot",
        "light": "golden hour",
        "people": 1,
        "garments": [
            {"type": "top", "name": "sheer mesh crop top", "look": "wet"},
            {"type": "bottom", "name": "sheer mesh bikini bottom", "look": "wet"},
        ],
        "build": "curvy",
        "skin": "damp skin",
        "hair": "blonde, damp",
    }
}

MMF_HDR = (
    "subject_definitions:\n<Picture 1> is the reference image.\n\n"
    "summary:\nA clip.\n\n"
    "retention_analysis:\nkept.\n\n"
    "detailed_description:\n[Shot 1] "
)

MMF_DD = (
    "The camera holds a medium shot at hip height, keeping all three faces in frame. At first, (S1) sits on the log, "
    "leaning forward. She shifts onto her hands and knees on the log. (S3) pulls her sheer mesh bikini bottom aside "
    "to one side at her hip, where it stays. (S2) kneels at her head and slides past her lips deep inside her mouth "
    "while (S3) kneels behind her and enters her, staying buried in her. <Picture 2> sets his look. As it builds, "
    "PRIMARY MOTION - (S3) thrusts about one stroke every second. By the end, he keeps thrusting. Wet suction and "
    "breath through her nose."
)


def _tpl_graph() -> Dict[str, Any]:
    return json.loads(br.DEFAULT_REFMOD_TEMPLATE.read_text(encoding="utf-8"))


# ---- Shape check & --aspect auto ------------------------------------------------------------------------

def test_read_still_size_and_shape_warning_threshold(tmp_path):
    portrait = _make_png(tmp_path / "portrait.png", 64, 112)  # exact 768x1344 ratio (0.5714)
    assert br.read_still_size(portrait) == (64, 112)
    assert br.read_still_size(tmp_path / "missing.png") is None

    # Exact match / <= 5% difference: no warning
    assert br.check_still_canvas_shape(portrait, 768, 1344, aspect="9:16") is None
    within_5 = _make_png(tmp_path / "within5.png", 104, 100)  # 1.04 vs 1.0 (4% diff)
    assert br.check_still_canvas_shape(within_5, 1024, 1024, aspect="1:1") is None

    # > 5% difference: warns cleanly
    over_5 = _make_png(tmp_path / "over5.png", 106, 100)  # 1.06 vs 1.0 (6% diff)
    w = br.check_still_canvas_shape(over_5, 1024, 1024, aspect="square")
    assert w is not None and "106x100" in w and "1024x1024" in w


def test_shape_warning_text_guide_vs_ref(tmp_path):
    portrait = _make_png(tmp_path / "p.png", 90, 160)  # 0.5625 (~9:16)
    landscape = _make_png(tmp_path / "l.png", 160, 90)  # 1.7778 (~16:9)

    w_guide_p_on_16_9 = br.check_still_canvas_shape(portrait, 1344, 768, aspect="16:9", still_mode="guide")
    assert w_guide_p_on_16_9 is not None
    assert "90x160" in w_guide_p_on_16_9
    assert "1344x768" in w_guide_p_on_16_9
    assert "--aspect 16:9" in w_guide_p_on_16_9
    assert "MiniMaxH3AddGuide" in w_guide_p_on_16_9 and "center-crop" in w_guide_p_on_16_9
    assert "top and bottom" in w_guide_p_on_16_9
    assert "--aspect 9:16" in w_guide_p_on_16_9

    w_guide_l_on_9_16 = br.check_still_canvas_shape(landscape, 768, 1344, size="768x1344", still_mode="guide")
    assert w_guide_l_on_9_16 is not None
    assert "sides" in w_guide_l_on_9_16
    assert "--size 768x1344" in w_guide_l_on_9_16
    assert "--aspect 16:9" in w_guide_l_on_9_16
    assert "widescreen" not in w_guide_l_on_9_16 and "landscape" not in w_guide_l_on_9_16

    w_ref = br.check_still_canvas_shape(portrait, 1344, 768, aspect="16:9", still_mode="ref")
    assert w_ref is not None
    assert "90x160" in w_ref and "1344x768" in w_ref
    assert "--aspect 9:16" in w_ref
    assert "AddGuide" not in w_ref and "crop" not in w_ref.lower()
    assert "un-resized reference on c0" in w_ref and "not frame-0 pinned" in w_ref


def test_aspect_auto_closest_preset_and_size_precedence():
    assert br.resolve_canvas("auto", still_size=(90, 160)) == (768, 1344)    # 9:16
    assert br.resolve_canvas("auto", still_size=(160, 90)) == (1344, 768)    # 16:9
    assert br.resolve_canvas("auto", still_size=(100, 100)) == (1024, 1024)  # 1:1
    assert br.resolve_canvas("auto", still_size=(120, 90)) == (1152, 864)    # 4:3
    assert br.resolve_canvas("auto", still_size=(90, 120)) == (864, 1152)    # 3:4
    # --size always wins over --aspect auto
    assert br.resolve_canvas("auto", size="1280x704", still_size=(90, 160)) == (1280, 704)
    # Missing still size falls back cleanly to default canvas
    assert br.resolve_canvas("auto", still_size=None) == (768, 1344)


def test_writer_run_cli_aspect_auto_and_still_mode_ref(tmp_path, capsys):
    portrait = _make_png(tmp_path / "portrait_syd.png", 90, 160)
    landscape = _make_png(tmp_path / "land_syd.png", 160, 90)

    # 1. writer-run with --aspect 16:9 + portrait still + --still-mode ref: warns without AddGuide-crop claim, builds READY
    rd1 = tmp_path / "wr_ref_warn"
    rd1.mkdir()
    (rd1 / "writer_output.txt").write_text(WRITER_RAW, encoding="utf-8")
    (rd1 / "still_read.json").write_text(json.dumps(WRITER_READ), encoding="utf-8")
    rc1 = fr.main([
        str(rd1),
        "--ask", "doggy on the log",
        "--position", "doggy",
        "--still", str(portrait),
        "--character", "FCSydny",
        "--aspect", "16:9",
        "--still-mode", "ref",
    ])
    cap1 = capsys.readouterr()
    assert rc1 == 0, (rd1 / "clip_NOT_READY.txt").read_text(encoding="utf-8") if (rd1 / "clip_NOT_READY.txt").exists() else cap1.out
    req1 = json.loads((rd1 / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert req1["c0"]["inputs"]["width"] == 1344 and req1["c0"]["inputs"]["height"] == 768
    assert req1["c0"]["inputs"]["ref_image_size"] == "max"
    assert req1["c0"]["inputs"]["ref_images.ref_image_1"] == ["img_1", 0]
    assert not any(n.get("class_type") == "MiniMaxH3AddGuide" for n in req1.values())
    assert req1["refapply"]["inputs"]["conditioning"] == ["c0", 0]
    assert (rd1 / "prompt.txt").read_text(encoding="utf-8").startswith(br.REF_MODE_PICTURE1_LEAD)

    # 2. writer-run with --aspect auto + landscape still + default guide mode: sets 1344x768, no mismatch warning
    rd2 = tmp_path / "wr_auto"
    rd2.mkdir()
    (rd2 / "writer_output.txt").write_text(WRITER_RAW, encoding="utf-8")
    (rd2 / "still_read.json").write_text(json.dumps(WRITER_READ), encoding="utf-8")
    rc2 = fr.main([
        str(rd2),
        "--ask", "doggy on the log",
        "--position", "doggy",
        "--still", str(landscape),
        "--character", "FCSydny",
        "--aspect", "auto",
    ])
    cap2 = capsys.readouterr()
    assert rc2 == 0
    assert "shape mismatch" not in cap2.err
    req2 = json.loads((rd2 / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert req2["c0"]["inputs"]["width"] == 1344 and req2["c0"]["inputs"]["height"] == 768
    assert req2["c0"]["inputs"]["ref_image_size"] == "match"
    assert "add_guide" in req2


def test_render_writer_pipeline_passes_aspect_size_and_still_mode(tmp_path, monkeypatch, capsys):
    portrait = _make_png(tmp_path / "p_pipe.png", 90, 160)
    home = tmp_path / "wp_home"
    (home / "personas").mkdir(parents=True)
    (home / "writer_prompt.md").write_text("WRITER PROMPT\nYou write clips.\n\nCRAFT RULES\n- Rule.\n", encoding="utf-8")
    cfg_dict = {
        "model_alias": "gemma4_heretic_poly_think",
        "endpoint": "http://127.0.0.1:9/v1",
        "retry_backoff_s": [0, 0, 0],
        "timeout_s": 2,
        "n_candidates": 1,
        "sampler_arm": "B",
        "samplers": {"B": {"temperature": 1.0}},
        "judge_sampler": {"temperature": 0.01, "top_k": 1},
        "lint": {},
        "position_kinds": {"sex": ["doggy"], "talk": ["talk"]},
    }
    cfg_path = home / "config.yaml"
    cfg_path.write_text(json.dumps(cfg_dict), encoding="utf-8")
    monkeypatch.setattr(rwp, "PIPE_DIR", home)
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "runs")

    rd = tmp_path / "pipe_run"
    rd.mkdir()
    sr_path = tmp_path / "sr.json"
    sr_path.write_text(json.dumps(WRITER_READ), encoding="utf-8")

    card = {
        "summary": "(S1) taken from behind on the log",
        "camera": "low three-quarter",
        "partners": [{"label": "S2", "sex": "man", "age": 31, "build": "broad build",
                      "attire": "dark swim trunks", "enters_from": "the left"}],
        "anchor": {"action": "leans on the log", "sound": "surf"},
        "onset": {"exit": "drops to hands and knees", "load": "forearms", "height": "he kneels",
                  "clearance": "bodysuit aside at the back", "entry": "enters from behind", "sound": "wood creak"},
        "development": {"primary_motion": "hard rear thrusts", "tempo_word": "strokes a second",
                        "contact_keyword": "buried in her", "follow_through": ["hair swings"],
                        "sound": "slap", "line_topics": ["S2: urges her on"]},
        "result": {"action": "still rocking", "sound": "gasps"},
        "end_state": {"pose": "hands and knees", "garments": {"bodysuit": "aside"},
                      "contact": "buried", "camera": "low", "pov": False},
    }

    def fake_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose=""):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if str(purpose).startswith("beat_card"):
            return json.dumps(card)
        if purpose == "judge":
            return '{"best": "A"}'
        return GOOD_SEX_DD

    seen_extra = []
    def fake_run_build(run_dir, ask, position, still, character, timeout=300, extra=None):
        seen_extra.append(list(extra or []))
        rep = {"status": "READY", "reason": None, "build": {"added": [], "speech": {"dropped": []}, "state": {"garments": {}}}, "frames": 243}
        (Path(run_dir) / "build_report.json").write_text(json.dumps(rep), encoding="utf-8")
        return {"status": "READY", "rc": 0, "stdout": "READY", "stderr": "", "report": rep, "seconds": 0.0, "reason": None}

    monkeypatch.setattr(rwp.Client, "chat", fake_chat)
    monkeypatch.setattr(rwp, "run_build", fake_run_build)

    rc = rwp.main([
        str(rd),
        "--ask", "she has sex with him",
        "--position", "doggy",
        "--still", str(portrait),
        "--still-read", str(sr_path),
        "--character", "FCSydny",
        "--config", str(cfg_path),
        "--aspect", "16:9",
        "--still-mode", "ref",
    ])
    cap = capsys.readouterr()
    assert rc == 0, cap.out
    assert "un-resized reference on c0" in cap.err
    assert seen_extra
    assert "--aspect" in seen_extra[0] and "16:9" in seen_extra[0]
    assert "--still-mode" in seen_extra[0] and "ref" in seen_extra[0]
