"""U55 end-to-end tests per clip type through render_writer_pipeline + fill_request (no queueing)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from PIL import Image
import pytest

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br
import fill_request as fr
import render_writer_pipeline as rwp


def _make_still(path: Path, w: int = 90, h: int = 160) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (w, h), (100, 90, 80)).save(path)
    return path


def _make_home(tmp_path: Path) -> Path:
    home = tmp_path / "wp_home"
    (home / "personas").mkdir(parents=True, exist_ok=True)
    (home / "writer_prompt.md").write_text("WRITER PROMPT\nWrite H3 prompts.\n\nCRAFT RULES\n- Plain audio.\n", encoding="utf-8")
    (home / "config.yaml").write_text(json.dumps({
        "version": "u55-test",
        "endpoint": "http://127.0.0.1:8080/v1",
        "model_alias": "gemma4-heretic",
        "thinking": False,
        "timeout_s": 60,
        "retry_backoff_s": [1],
        "writer_prompt": "writer_prompt.md",
        "persona": "current",
        "n_candidates": 1,
        "min_ready_score": 60,
        "sampler_arm": "A",
        "samplers": {"A": {"temperature": 1.0, "top_p": 0.95, "top_k": 64, "min_p": 0.10}},
        "beat_card_sampler": {"temperature": 0.7},
        "beat_card_max_tokens": 1200,
        "prose_max_tokens": 1000,
        "blacklist_cap": 20,
        "log_retention_days": 14,
        "log_cap_mb": 50,
        "scene_archive_days": 30,
        "shared_state_dir": str(home),
        "lint": {"speech_words_max": 25, "blacklist_ratio": 0.8, "words_min": 50, "words_max": 220,
                 "pen_phase_no_sound": 5, "opening_ratio": 0.85, "filler_lines": [],
                 "tempo_range": {"talk": [0.2, 2.5], "sex": [0.5, 2.5]}},
        "position_kinds": {"talk": ["talk"], "sex": ["missionary", "doggy"]},
    }), encoding="utf-8")
    return home


def _sr_file(path: Path) -> Path:
    p = path.parent / f"{path.stem}_sr.json"
    p.write_text(json.dumps({
        "read": {
            "room": "beach", "place": "shoreline", "surface": "sand", "bed": False, "sheets": "",
            "floor": "sand", "pose": "walking along the shore", "facing_camera": True,
            "framing": "medium shot", "light": "golden hour sunset", "people": 1,
            "garments": [{"type": "dress", "name": "white sundress", "look": "light cotton"}],
            "build": "slender", "skin": "tan", "hair": "blonde",
        },
        "source": str(path),
    }), encoding="utf-8")
    return p


def _graph_diff(tpl: dict, req: dict) -> list[str]:
    assert set(tpl) == set(req), f"node mismatch: +{set(req)-set(tpl)} -{set(tpl)-set(req)}"
    diffs = []
    for nid in sorted(tpl):
        assert tpl[nid].get("class_type") == req[nid].get("class_type")
        ti, ri = tpl[nid].get("inputs", {}), req[nid].get("inputs", {})
        assert set(ti) == set(ri), f"{nid} keys mismatch: +{set(ri)-set(ti)} -{set(ti)-set(ri)}"
        for k in sorted(ti):
            if ti[k] != ri[k]:
                diffs.append(f"{nid}.inputs.{k}")
    return diffs


ALLOWED_PER_CLIP = {
    "c0.inputs.prompt", "c0.inputs.width", "c0.inputs.height", "c0.inputs.length",
    "c1.inputs.prompt", "c1.inputs.width", "c1.inputs.height",
    "img_1.inputs.image", "img.inputs.image", "img2.inputs.image",
    "noise.inputs.noise_seed", "save.inputs.filename_prefix",
    *[f"refmods.inputs.mod_{i}" for i in range(1, 9)],
}


@pytest.mark.parametrize("case", [
    "plain", "oc_guide", "oc_ref", "oc_ref_2pass", "named_parody", "talk", "two_person", "long_continuation", "ref2va_16x9"
])
def test_e2e_per_clip_type_template_diff(tmp_path, monkeypatch, case):
    monkeypatch.setattr(rwp, "PIPE_DIR", _make_home(tmp_path))
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(br, "COMFY_INPUT_COMMUNITY", tmp_path / "comfy_in" / "community")

    s_port = _make_still(tmp_path / "port.png", 90, 160)
    s_land = _make_still(tmp_path / "land.png", 160, 90)
    s_p2 = _make_still(tmp_path / "p2.png", 90, 160)

    def _fake_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose="chat", **kw):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        if str(purpose).startswith("beat_card"):
            return json.dumps({
                "summary": "clip beat", "anchor": {"pose": "walking", "camera": "medium shot", "sound": "surf"},
                "onset": {"action": "steps forward", "sound": "sand"}, "development": {"primary_motion": "walks steadily", "sound": "waves"},
                "result": {"end_state": "keeps walking", "sound": "waves"}, "line_topics": [{"speaker": "S1", "topic": "hello"}],
                "end_state": {"pose": "walking", "garments": {"white sundress": "on"}, "contact": None, "camera": "medium", "pov": False},
            })
        return (
            "[Shot 1] Medium shot on a 35mm lens in golden hour sunset light. "
            "At first, (S1) walks across the sand in a white sundress. "
            "(S1) says in a warm voice, <d>[English] What a sunset.</d> "
            "As it builds, she smiles and turns toward the water. "
            "By the end, she keeps walking down the shoreline as soft waves lap the sand."
        )

    monkeypatch.setattr(rwp.Client, "chat", _fake_chat)
    cfg = rwp.load_config(rwp.PIPE_DIR / "config.yaml")
    run_dir = tmp_path / "runs" / f"u55_{case}"

    jobs = {
        "plain": {"ask": "a woman walks along a beach at sunset", "position": "walking", "still": str(s_port), "still_read": str(_sr_file(s_port)), "frames": 124},
        "oc_guide": {"ask": "FCSydny walks along the beach", "position": "walking", "still": str(s_port), "still_read": str(_sr_file(s_port)), "character": "FCSydny", "still_mode": "guide", "frames": 124},
        "oc_ref": {"ask": "FCSydny walks along the beach", "position": "walking", "still": str(s_port), "still_read": str(_sr_file(s_port)), "character": "FCSydny", "still_mode": "ref", "template": "oc_ref", "frames": 124},
        "oc_ref_2pass": {"ask": "FCSydny walks along the beach", "position": "walking", "still": str(s_port), "still_read": str(_sr_file(s_port)), "character": "FCSydny", "still_mode": "ref", "template": "oc_ref_2pass", "frames": 124},
        "named_parody": {"ask": "Daenerys Targaryen holds court and speaks", "position": "talk", "names": ["Daenerys Targaryen"], "template": "named_parody", "frames": 192},
        "talk": {"ask": "she smiles and says <d>[English] What a sunset.</d>", "position": "talk", "still": str(s_port), "still_read": str(_sr_file(s_port)), "frames": 124},
        "two_person": {"ask": "two people together on the beach", "position": "two_person", "still": str(s_land), "still_read": str(_sr_file(s_land)), "partner2_still": str(s_p2), "size": "1344x768", "frames": 124},
        "long_continuation": {"ask": "long continuous walk on the beach", "position": "walking", "still": str(s_port), "still_read": str(_sr_file(s_port)), "template": "long_continuation", "size": "576x1024", "frames": 481},
        "ref2va_16x9": {"ask": "widescreen beach walk at sunset", "position": "walking", "still": str(s_land), "still_read": str(_sr_file(s_land)), "template": "ref2va_16x9", "aspect": "16:9", "size": "1344x768", "frames": 124},
    }

    res = rwp.run_clip({"run_dir": str(run_dir), **jobs[case]}, cfg, lambda *a: None)
    assert res["status"] == "READY", (case, res.get("not_ready_reason"), res.get("error"))
    rep = json.loads((run_dir / "build_report.json").read_text(encoding="utf-8"))
    assert rep["template"] == case
    tpl = json.loads(fr.TEMPLATES[case].read_text(encoding="utf-8"))
    req = json.loads((run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
    diffs = _graph_diff(tpl, req)
    assert diffs and set(diffs) <= ALLOWED_PER_CLIP, (case, diffs)

    c0 = req["c0"]["inputs"]
    assert "What a sunset." in c0["prompt"]
    if case == "oc_ref_2pass":
        assert (c0["width"] * 2, c0["height"] * 2) == tuple(rep["canvas"])
    else:
        assert (c0["width"], c0["height"]) == tuple(rep["canvas"])
    if case == "plain":
        assert (c0["width"], c0["height"]) == (768, 1344) and req["img_1"]["inputs"]["image"]
        assert all(req["refmods"]["inputs"][f"mod_{i}"] == "(none)" for i in range(1, 9))
    elif case in ("oc_guide", "oc_ref", "oc_ref_2pass"):
        if case == "oc_ref_2pass":
            assert (c0["width"], c0["height"]) == (384, 672)
            assert req["m_vsa"]["inputs"]["start_percent"] == 0.2
            assert req["lsu3"]["inputs"]["mode.scale"] == 2.0
        else:
            assert (c0["width"], c0["height"]) == (768, 1344)
        assert req["img_1"]["inputs"]["image"]
        mods = [req["refmods"]["inputs"][f"mod_{i}"] for i in range(1, 9)]
        assert any("poolclub" in m for m in mods)
        if case in ("oc_ref", "oc_ref_2pass"):
            assert c0["prompt"].startswith(br.REF_MODE_PICTURE1_LEAD)
    elif case == "named_parody":
        assert (c0["width"], c0["height"]) == (768, 1344)
        assert req["refmods"]["inputs"]["mod_1"] == "minimaxh3_emiliaclarke_v1_refmod"
        assert "Daenerys" in c0["prompt"] and "Emilia Clarke" in c0["prompt"]
    elif case == "talk":
        assert (c0["width"], c0["height"]) == (768, 1344) and req["img_1"]["inputs"]["image"]
    elif case == "two_person":
        assert (c0["width"], c0["height"]) == (1344, 768)
        assert req["img"]["inputs"]["image"] and req["img2"]["inputs"]["image"]
    elif case == "long_continuation":
        assert (c0["width"], c0["height"]) == (576, 1024)
        assert req["img"]["inputs"]["image"] and "What a sunset." in req["c1"]["inputs"]["prompt"]
        assert rep["frames"] == 481
    elif case == "ref2va_16x9":
        assert (c0["width"], c0["height"]) == (1344, 768) and req["img"]["inputs"]["image"]


def test_18plus_still_blocks_and_position_is_free_text(tmp_path, monkeypatch):
    monkeypatch.setattr(rwp, "PIPE_DIR", _make_home(tmp_path))
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "runs")
    still = _make_still(tmp_path / "s.png")
    res = rwp.run_clip(
        {"run_dir": str(tmp_path / "runs" / "minor_block"), "ask": "a teenager on the beach",
         "position": "walking", "still": str(still), "still_read": str(_sr_file(still))},
        rwp.load_config(rwp.PIPE_DIR / "config.yaml"), lambda *a: None,
    )
    assert res["status"] == "NOT_READY" and "youth hint" in (res.get("not_ready_reason") or "").lower()


def test_u56_16x9_uses_beta7_plain_and_hard_stops_block_ready(tmp_path, monkeypatch):
    home = _make_home(tmp_path)
    cfg = json.loads((home / "config.yaml").read_text(encoding="utf-8"))
    cfg["lint"]["filler_lines"] = ["fuck me harder"]
    cfg["position_kinds"]["sex"] = ["cowgirl", "doggy"]
    (home / "config.yaml").write_text(json.dumps(cfg), encoding="utf-8")
    monkeypatch.setattr(rwp, "PIPE_DIR", home)
    monkeypatch.setattr(rwp, "RUNS_ROOT", tmp_path / "runs")
    monkeypatch.setattr(br, "COMFY_INPUT_COMMUNITY", tmp_path / "comfy_in" / "community")

    s_land = _make_still(tmp_path / "land.png", 160, 90)
    sr_land = _sr_file(s_land)

    def _ok_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose="chat", **kw):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        return "[Shot 1] Wide 35mm shot in sunset light. At first, (S1) walks across the sand. As it builds, she turns toward the surf. By the end, she keeps strolling as waves break."

    monkeypatch.setattr(rwp.Client, "chat", _ok_chat)
    res_g = rwp.run_clip(
        {"run_dir": str(tmp_path / "runs" / "u56_16x9_guide"), "ask": "widescreen beach walk",
         "position": "walking", "still": str(s_land), "still_read": str(sr_land), "aspect": "16:9", "frames": 124},
        rwp.load_config(home / "config.yaml"), lambda *a: None,
    )
    assert res_g["status"] == "READY"
    rep_g = json.loads((tmp_path / "runs" / "u56_16x9_guide" / "build_report.json").read_text(encoding="utf-8"))
    req_g = json.loads((tmp_path / "runs" / "u56_16x9_guide" / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert rep_g["template"] == "plain" and rep_g["canvas"] == [1344, 768]
    assert "beta7_int8HQ" in req_g["unet"]["inputs"]["unet_name"]
    assert "<Picture 1>" not in req_g["c0"]["inputs"]["prompt"]

    res_r = rwp.run_clip(
        {"run_dir": str(tmp_path / "runs" / "u56_16x9_ref"), "ask": "widescreen beach walk",
         "position": "walking", "still": str(s_land), "still_read": str(sr_land), "still_mode": "ref", "aspect": "16:9", "frames": 124},
        rwp.load_config(home / "config.yaml"), lambda *a: None,
    )
    assert res_r["status"] == "READY"
    rep_r = json.loads((tmp_path / "runs" / "u56_16x9_ref" / "build_report.json").read_text(encoding="utf-8"))
    ptxt_r = (tmp_path / "runs" / "u56_16x9_ref" / "prompt.txt").read_text(encoding="utf-8")
    assert rep_r["template"] == "oc_ref" and "[reference generation]" in ptxt_r

    def _stock_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose="chat", **kw):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        return "[Shot 1] Medium shot. At first, (S1) kneels on the sand. (S1) says in a breathless voice, <d>[English] Fuck me harder.</d> By the end, she keeps moving as waves break."

    monkeypatch.setattr(rwp.Client, "chat", _stock_chat)
    res_st = rwp.run_clip(
        {"run_dir": str(tmp_path / "runs" / "u56_stock_block"), "ask": "doggy on the beach",
         "position": "doggy", "still": str(s_land), "still_read": str(sr_land), "frames": 124},
        rwp.load_config(home / "config.yaml"), lambda *a: None,
    )
    assert res_st["status"] == "NOT_READY" and "stock_talk" in (res_st.get("not_ready_reason") or "")

    def _bad_cowgirl_chat(self, messages, sampler, seed, max_tokens, response_format=None, purpose="chat", **kw):
        self.calls.append({"purpose": purpose, "seconds": 0.0})
        return "[Shot 1] Medium shot. At first, (S1) straddles him on the sand, his penis buried in her vagina. As it builds, PRIMARY MOTION - she moves at one stroke a second while he lies flat. By the end, she keeps riding as waves break."

    monkeypatch.setattr(rwp.Client, "chat", _bad_cowgirl_chat)
    res_cg = rwp.run_clip(
        {"run_dir": str(tmp_path / "runs" / "u56_cowgirl_block"), "ask": "cowgirl on the beach",
         "position": "cowgirl", "still": str(s_land), "still_read": str(sr_land), "frames": 124},
        rwp.load_config(home / "config.yaml"), lambda *a: None,
    )
    assert res_cg["status"] == "NOT_READY" and "cowgirl_check" in (res_cg.get("not_ready_reason") or "")

