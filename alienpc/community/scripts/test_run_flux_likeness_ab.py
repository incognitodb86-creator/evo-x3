"""Offline tests for run_flux_likeness_ab.py (brief items 4 & 5)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_flux_likeness_ab as ab  # noqa: E402


def test_is_valid_image_file_checks_magic_bytes(tmp_path):
    png = tmp_path / "good.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    jpg = tmp_path / "good.jpg"
    jpg.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 16)
    webp = tmp_path / "good.webp"
    webp.write_bytes(b"RIFF\x24\x00\x00\x00WEBP" + b"\x00" * 8)
    fake_html = tmp_path / "poison.png"
    fake_html.write_text("<!DOCTYPE html><html><body>403 Forbidden</body></html>", encoding="utf-8")
    empty = tmp_path / "empty.png"
    empty.write_bytes(b"")

    assert ab.is_valid_image_file(png) is True
    assert ab.is_valid_image_file(jpg) is True
    assert ab.is_valid_image_file(webp) is True
    assert ab.is_valid_image_file(fake_html) is False
    assert ab.is_valid_image_file(empty) is False


def test_collect_valid_refs_skips_html_and_refuses_poisoned_refs_ab(tmp_path):
    # Poisoned refs_ab path must be refused even if it contains files.
    poisoned = tmp_path / "refs_ab"
    (poisoned / "sydneysweeney").mkdir(parents=True)
    (poisoned / "sydneysweeney" / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    valid, skipped, warn = ab.collect_valid_refs(poisoned, "sydneysweeney")
    assert valid == [] and skipped == []
    assert warn and "refs_ab_celeb" in warn

    # Clean refs_ab_celeb accepts valid images and skips HTML disguised as .png.
    clean = tmp_path / "refs_ab_celeb"
    sub = clean / "sydneysweeney"
    sub.mkdir(parents=True)
    (sub / "real1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    (sub / "real2.jpg").write_bytes(b"\xff\xd8\xff\xe1" + b"\x00" * 16)
    (sub / "html_fake.png").write_text("<html>not a png</html>", encoding="utf-8")
    valid2, skipped2, warn2 = ab.collect_valid_refs(clean, "sydneysweeney")
    assert warn2 is None
    assert [p.name for p in valid2] == ["real1.png", "real2.jpg"]
    assert [p.name for p in skipped2] == ["html_fake.png"]


def test_parse_last_json_line_and_score_arcface_with_insightface_logs(tmp_path, monkeypatch):
    noisy_stdout = "\n".join([
        "Applied providers: ['CPUExecutionProvider'], with options: {'CPUExecutionProvider': {}}",
        "find model: C:\\Users\\derek\\.insightface\\models\\buffalo_l\\det_10g.onnx detection [1, 3, '?', '?'] 127.5 128.0",
        "set det-size: (640, 640)",
        json.dumps({
            "ref_count": 3,
            "intra_gallery": {"pairs": 3, "mean": 0.7123, "min": 0.65, "max": 0.78},
            "scores": {"L7-fixed": {"centroid": 0.68, "mean": 0.64, "max": 0.71, "min": 0.58}},
        }),
    ])
    parsed = ab.parse_last_json_line(noisy_stdout)
    assert parsed["ref_count"] == 3
    assert parsed["intra_gallery"]["mean"] == 0.7123
    assert parsed["scores"]["L7-fixed"]["max"] == 0.71

    fake_py = tmp_path / "python.exe"
    fake_py.write_text("", encoding="utf-8")
    ref = tmp_path / "r1.png"
    ref.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    cand = tmp_path / "c1.png"
    cand.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout=noisy_stdout + "\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    res = ab.score_arcface(fake_py, [ref], {"L7-fixed": cand})
    assert res["ref_count"] == 3
    assert res["intra_gallery"] == {"pairs": 3, "mean": 0.7123, "min": 0.65, "max": 0.78}
    assert res["scores"]["L7-fixed"] == {"centroid": 0.68, "mean": 0.64, "max": 0.71, "min": 0.58}


def test_render_l7_prompt_runtime_placeholders_and_distinct_celebs(tmp_path):
    cfg_path = tmp_path / "prompts.json"
    cfg_path.write_text(json.dumps({
        "Sydney Sweeney": {
            "trigger": "TEST_TRIG_A",
            "name": "Sydney Sweeney",
            "likeness_desc": "distinctive facial structure",
        },
        "Megan Fox": {
            "trigger": "TEST_TRIG_B",
            "name": "Megan Fox",
            "likeness_desc": "sharp brow line",
        },
    }), encoding="utf-8")
    cfg = ab.load_prompts_config(cfg_path)
    p_syd = ab.render_l7_prompt("Sydney Sweeney", cfg)
    p_meg = ab.render_l7_prompt("Megan Fox", cfg)
    assert p_syd != p_meg
    assert "Sydney Sweeney (TEST_TRIG_A)" in p_syd and "distinctive facial structure" in p_syd
    assert "Megan Fox (TEST_TRIG_B)" in p_meg and "sharp brow line" in p_meg
    assert "{TRIGGER}" not in p_syd and "{NAME}" not in p_syd
    assert "reference images" in p_syd.lower()


def test_l7_suite_builds_baseline_fixed_rebuilt_and_6_seeds(tmp_path):
    comfy = tmp_path / "ComfyUI"
    (comfy / "models" / "diffusion_models").mkdir(parents=True)
    (comfy / "models" / "diffusion_models" / "Miraclein_4.5_9b_FP8.safetensors").write_bytes(b"")
    (comfy / "models" / "refmods-klein9").mkdir(parents=True)
    (comfy / "models" / "refmods-klein9" / "fk9_sydneysweeney_v1_refmod.safetensors").write_bytes(b"")
    (comfy / "models" / "loras" / "klein9").mkdir(parents=True)
    (comfy / "models" / "loras" / "klein9" / "fk9_sydneysweeney_v1_prodigy.safetensors").write_bytes(b"")

    out_dir = tmp_path / "out_l7"
    rc = ab.main([
        "--dry-run",
        "--ab-suite", "l7",
        "--celebs", "Sydney Sweeney",
        "--seed", "100",
        "--num-seeds", "6",
        "--comfy-root", str(comfy),
        "--out-dir", str(out_dir),
    ])
    assert rc == 0

    # Verify 6 seeds x 3 arms built, with baseline=0.85/CLIPTextEncode vs fixed=1.0/ConditioningZeroOut
    base_g = json.loads((out_dir / "sydneysweeney_L7_baseline_s100" / "still" / "request.api.json").read_text(encoding="utf-8"))
    fixed_g = json.loads((out_dir / "sydneysweeney_L7_fixed_s100" / "still" / "request.api.json").read_text(encoding="utf-8"))
    fixed_g6 = json.loads((out_dir / "sydneysweeney_L7_fixed_s105" / "still" / "request.api.json").read_text(encoding="utf-8"))

    assert base_g["12"]["inputs"]["strength_1"] == 0.85
    assert base_g["6"]["class_type"] == "CLIPTextEncode"

    assert fixed_g["12"]["inputs"]["strength_1"] == 1.0
    assert fixed_g["6"]["class_type"] == "ConditioningZeroOut"
    assert fixed_g["6"]["inputs"]["conditioning"] == ["5", 0]
    assert fixed_g["14"]["inputs"]["conditioning"] == ["6", 0]
    assert fixed_g["1"]["inputs"]["unet_name"] == "Miraclein_4.5_9b_FP8.safetensors"
    assert "Sydney Sweeney" in fixed_g["5"]["inputs"]["text"]
    assert fixed_g["20"]["inputs"]["noise_seed"] == 100
    assert fixed_g6["20"]["inputs"]["noise_seed"] == 105


def test_l7_suite_with_v1_lora_arm(tmp_path):
    comfy = tmp_path / "ComfyUI"
    (comfy / "models" / "diffusion_models").mkdir(parents=True)
    (comfy / "models" / "diffusion_models" / "Miraclein_4.5_9b_FP8.safetensors").write_bytes(b"")
    out_dir = tmp_path / "out_v1"
    rc = ab.main([
        "--dry-run", "--ab-suite", "l7", "--with-v1-lora", "--celebs", "Megan Fox",
        "--comfy-root", str(comfy), "--out-dir", str(out_dir),
    ])
    assert rc == 0
    g = json.loads((out_dir / "meganfox_L7_v1lora" / "still" / "request.api.json").read_text(encoding="utf-8"))
    loras = [n for n in g.values() if isinstance(n, dict) and n.get("class_type") == "LoraLoaderModelOnly"
             and float(n["inputs"].get("strength_model") or 0) > 0]
    assert [n["inputs"]["lora_name"] for n in loras] == ["klein9\\fk9_meganfox_v1.safetensors"]
    assert loras[0]["inputs"]["strength_model"] == 0.60
    assert g["12"]["inputs"]["strength_1"] == 1.0
    assert g["6"]["class_type"] == "ConditioningZeroOut"
    assert not (out_dir / "meganfox_L7_v1lora_s51083601").exists()


def test_run_writes_intra_gallery_and_per_ref_stats_to_result_md(tmp_path, monkeypatch):
    comfy = tmp_path / "ComfyUI"
    (comfy / "models" / "diffusion_models").mkdir(parents=True)
    (comfy / "models" / "diffusion_models" / "Miraclein_4.5_9b_FP8.safetensors").write_bytes(b"")
    (comfy / "models" / "refmods-klein9").mkdir(parents=True)
    (comfy / "models" / "refmods-klein9" / "fk9_sydneysweeney_v1_refmod.safetensors").write_bytes(b"")
    (comfy / "models" / "loras" / "klein9").mkdir(parents=True)
    (comfy / "models" / "loras" / "klein9" / "fk9_sydneysweeney_v1_prodigy.safetensors").write_bytes(b"")

    ref_root = tmp_path / "refs_ab_celeb"
    (ref_root / "sydneysweeney").mkdir(parents=True)
    (ref_root / "sydneysweeney" / "r1.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    (ref_root / "sydneysweeney" / "r2.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
    (ref_root / "sydneysweeney" / "bad.png").write_text("<html>bad</html>", encoding="utf-8")

    rq = tmp_path / "scripts" / "run_queue.py"
    rq.parent.mkdir(parents=True)
    rq.write_text("# stub\n", encoding="utf-8")
    face_py = tmp_path / "face_py.exe"
    face_py.write_text("", encoding="utf-8")

    def fake_run(cmd, **kwargs):
        if str(rq) in cmd:
            rdir = Path(cmd[cmd.index("--run-dir") + 1])
            (rdir / "still" / "still.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
            return subprocess.CompletedProcess(cmd, 0, stdout="OK", stderr="")
        # ArcFace helper call
        cands = json.loads(cmd[-1])
        scores = {k: {"centroid": 0.69, "mean": 0.65, "max": 0.72, "min": 0.58} for k in cands}
        payload = {"ref_count": 2, "intra_gallery": {"pairs": 1, "mean": 0.74, "min": 0.74, "max": 0.74}, "scores": scores}
        return subprocess.CompletedProcess(cmd, 0, stdout="Applied providers: CPU\n" + json.dumps(payload) + "\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(ab, "make_contact_sheet", lambda *a, **k: None)

    out_dir = tmp_path / "out_run"
    rc = ab.main([
        "--run", "--ab-suite", "l7", "--celebs", "Sydney Sweeney",
        "--seed", "10", "--num-seeds", "2",
        "--comfy-root", str(comfy), "--run-queue", str(rq),
        "--face-py", str(face_py), "--ref-dir", str(ref_root), "--out-dir", str(out_dir),
    ])
    assert rc == 0
    md = (out_dir / "RESULT.md").read_text(encoding="utf-8")
    assert "## Reference gallery ceiling" in md
    assert "| Sydney Sweeney | 2 | 1 | 2 | 0.7400 | 0.7400 | 0.7400 |" in md
    assert "| 0.6500 | 0.7200 | 0.5800 | 0.6900 |" in md
    assert "## Multi-seed summary" in md
    assert "| Sydney Sweeney | L7-fixed | 2/2 | 0.6500 | 0.7200 | 0.5800 |" in md

