"""Offline tests for S2 template allowlist (scripts/template_allowlist.py)."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
TEMPLATES_DIR = SCRIPTS_DIR.parent / "templates"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import template_allowlist as ta


def _load_tpl(name: str) -> dict:
    return json.loads((TEMPLATES_DIR / f"{name}.api.json").read_text(encoding="utf-8"))


def _rtx_vsr_graph(video: str = "x3_rtx2x_input.mp4", fps: float = 24, prefix: str = "community/rtx2x/run1_clip_2x") -> dict:
    return {
        "1": {
            "class_type": "VHS_LoadVideo",
            "inputs": {
                "video": video,
                "force_rate": 0,
                "custom_width": 0,
                "custom_height": 0,
                "frame_load_cap": 0,
                "skip_first_frames": 0,
                "select_every_nth": 1,
            },
        },
        "2": {
            "class_type": "RTXVideoSuperResolution",
            "inputs": {
                "images": ["1", 0],
                "resize_type": "scale by multiplier",
                "resize_type.scale": 2.0,
                "quality": "ULTRA",
                "strength": 1.0,
                "image_encoding": "8-bit RGB",
            },
        },
        "3": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["2", 0],
                "audio": ["1", 2],
                "frame_rate": fps,
                "loop_count": 0,
                "filename_prefix": prefix,
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 16,
                "save_metadata": False,
                "trim_to_audio": False,
                "pingpong": False,
                "save_output": True,
            },
        },
    }


def test_b2_graph_passes_with_allowed_variations():
    g = _load_tpl("b2")
    g["c0"]["inputs"]["prompt"] = "An adult woman in a bright studio smiles at the camera."
    g["c0"]["inputs"]["length"] = 148
    g["noise"]["inputs"]["noise_seed"] = 99887766
    g["img"]["inputs"]["image"] = "community/test_still.png"
    g["save"]["inputs"]["filename_prefix"] = "community/run_s2/clip01"
    ok, matched, reason = ta.check_graph(g)
    assert ok, reason
    assert matched == "b2"


def test_b2_refmod_passes_with_refmod_variations():
    g = _load_tpl("b2_refmod")
    g["c0"]["inputs"]["prompt"] = "An adult woman walks through a sunlit cafe."
    g["refmods"]["inputs"]["mod_1"] = "minimaxh3_test_v1_refmod"
    g["refmods"]["inputs"]["mod_2"] = "(none)"
    g["noise"]["inputs"]["noise_seed"] = 42
    g["save"]["inputs"]["filename_prefix"] = "community/run_s2/ref01"
    ok, matched, reason = ta.check_graph(g)
    assert ok, reason
    assert matched == "b2_refmod"


def test_rtx_vsr_graph_passes():
    ok, matched, reason = ta.check_graph(_rtx_vsr_graph())
    assert ok, reason
    assert matched == "rtx_vsr_2x"


def test_rtx_vsr_refuses_bad_scale_or_path():
    g_scale = _rtx_vsr_graph()
    g_scale["2"]["inputs"]["resize_type.scale"] = 4.0
    ok, _, _ = ta.check_graph(g_scale)
    assert not ok

    g_path = _rtx_vsr_graph(video="../secret.mp4")
    ok, _, _ = ta.check_graph(g_path)
    assert not ok

    g_pfx = _rtx_vsr_graph(prefix="community/other/foo")
    ok, _, _ = ta.check_graph(g_pfx)
    assert not ok


def test_planted_extra_node_refused_on_b2_and_rtx():
    g_b2 = _load_tpl("b2")
    g_b2["planted"] = {"class_type": "PreviewImage", "inputs": {"images": ["dec_v", 0]}}
    ok, _, reason = ta.check_graph(g_b2)
    assert not ok
    assert "extra nodes" in reason

    g_rtx = _rtx_vsr_graph()
    g_rtx["4"] = {"class_type": "SaveImage", "inputs": {"images": ["2", 0], "filename_prefix": "community/rtx2x/x"}}
    ok, _, _ = ta.check_graph(g_rtx)
    assert not ok


def test_llm_node_graph_refused():
    g = _load_tpl("b2_omni_rewriter")
    ok, matched, reason = ta.check_graph(g)
    assert not ok
    assert matched is None
    assert "LLM/rewriter" in reason


def test_fixed_parameter_mutation_refused():
    g = _load_tpl("b2")
    g["unet"]["inputs"]["unet_name"] = "some_other_model.safetensors"
    ok, _, reason = ta.check_graph(g)
    assert not ok
    assert "unet_name" in reason


def test_path_traversal_refused():
    g = _load_tpl("b2")
    g["img"]["inputs"]["image"] = "../../Windows/win.ini"
    ok, _, _ = ta.check_graph(g)
    assert not ok

    g2 = _load_tpl("b2")
    g2["save"]["inputs"]["filename_prefix"] = "../outside/clip"
    ok, _, _ = ta.check_graph(g2)
    assert not ok


def test_u55_embedded_specs_all_load_and_match():
    specs = json.loads((SCRIPTS_DIR / "u55_allowlist_specs.json").read_text(encoding="utf-8"))
    assert set(specs.keys()) == set(ta.U55_TEMPLATE_NAMES)
    for name, spec in specs.items():
        g = copy.deepcopy(spec)
        for nid, node in g.items():
            for k, v in list(node["inputs"].items()):
                if v != ta.VAR_SENTINEL:
                    continue
                if k in ta.PROMPT_KEYS:
                    node["inputs"][k] = "An adult woman smiles in warm indoor light."
                elif k in ta.SEED_KEYS:
                    node["inputs"][k] = 123456
                elif k in ta.INPUT_PATH_KEYS:
                    node["inputs"][k] = "community/test.png"
                elif k in ta.REFMOD_NAME_KEYS:
                    node["inputs"][k] = "(none)"
                elif k in ta.REFMOD_STRENGTH_KEYS:
                    node["inputs"][k] = 1.0
                elif k in ta.FRAME_KEYS:
                    node["inputs"][k] = 124
                elif k in ta.DIM_KEYS:
                    node["inputs"][k] = 768
                elif k in ta.PREFIX_KEYS:
                    node["inputs"][k] = f"community/test/{name}"
        ok, matched, reason = ta.check_graph(g)
        assert ok, f"{name} failed: {reason}"
        assert matched in ta.CORE_TEMPLATE_NAMES


def test_promoted_template_allowed_and_candidate_ignored(tmp_path: Path):
    custom = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "custom.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "RandomNoise", "inputs": {"noise_seed": 1}},
        "3": {"class_type": "SaveImage", "inputs": {"images": ["1", 0], "filename_prefix": "community/custom/out"}},
    }
    promoted_file = tmp_path / "custom_promoted.api.json"
    promoted_file.write_text(json.dumps(custom), encoding="utf-8")

    # Without promotion: refused
    ok, _, _ = ta.check_graph(custom)
    assert not ok

    # With explicit promotion + declared variable_fields: allowed
    g = copy.deepcopy(custom)
    g["2"]["inputs"]["noise_seed"] = 99
    ok, matched, reason = ta.check_graph(g, promoted=[("custom_promoted", custom, {"2": ["noise_seed"]})])
    assert ok, reason
    assert matched == "custom_promoted"

    # Without variable_fields, mutating noise_seed is refused (exact match only)
    ok, _, _ = ta.check_graph(g, promoted=[promoted_file])
    assert not ok

    # Candidate filenames are never accepted via promotion
    cand_file = tmp_path / "draft.candidate.api.json"
    cand_file.write_text(json.dumps(custom), encoding="utf-8")
    ok, _, _ = ta.check_graph(custom, promoted=[cand_file])
    assert not ok


def test_per_template_variable_fields_refuses_fixed_negative_text(tmp_path: Path):
    tdir = tmp_path / "templates"
    tdir.mkdir()
    still_tpl = {
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_8b_fp8mixed.safetensors", "device": "default", "type": "flux2"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": "An adult woman in warm light."}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": "bad quality, blurry"}},
        "20": {"class_type": "RandomNoise", "inputs": {"noise_seed": 0}},
        "24": {"class_type": "SaveImage", "inputs": {"images": ["5", 0], "filename_prefix": "community/still/TAG"}},
    }
    tpl_file = tdir / "flux_still_promoted.api.json"
    tpl_bytes = json.dumps(still_tpl).encode("utf-8")
    tpl_file.write_bytes(tpl_bytes)
    tpl_sha = hashlib.sha256(tpl_bytes).hexdigest()

    manifest = tmp_path / "allowlist_promoted.json"
    manifest.write_text(
        json.dumps([{
            "file": "flux_still_promoted.api.json",
            "sha256": tpl_sha,
            "variable_fields": {"5": ["text"], "20": ["noise_seed"], "24": ["filename_prefix"]},
        }]),
        encoding="utf-8",
    )

    # Varying positive prompt ("5".text), seed, and prefix passes
    g_ok = copy.deepcopy(still_tpl)
    g_ok["5"]["inputs"]["text"] = "An adult woman standing by a sunlit window."
    g_ok["20"]["inputs"]["noise_seed"] = 777
    g_ok["24"]["inputs"]["filename_prefix"] = "community/still/run01"
    ok, matched, reason = ta.check_graph(g_ok, templates_dir=tdir, promoted_manifest=manifest)
    assert ok, reason
    assert matched == "flux_still_promoted"

    # Mutating fixed negative CLIPTextEncode ("6".text) is refused
    g_bad_neg = copy.deepcopy(g_ok)
    g_bad_neg["6"]["inputs"]["text"] = "tampered negative prompt"
    ok, _, reason = ta.check_graph(g_bad_neg, templates_dir=tdir, promoted_manifest=manifest)
    assert not ok
    assert "node 6.text" in reason


def test_promoted_manifest_checks_sha256_and_rejects_traversal(tmp_path: Path):
    tdir = tmp_path / "templates"
    tdir.mkdir()
    custom = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "custom.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "RandomNoise", "inputs": {"noise_seed": 1}},
        "3": {"class_type": "SaveImage", "inputs": {"images": ["1", 0], "filename_prefix": "community/custom/out"}},
    }
    good_file = tdir / "custom_promoted.api.json"
    good_bytes = json.dumps(custom).encode("utf-8")
    good_file.write_bytes(good_bytes)
    good_sha = hashlib.sha256(good_bytes).hexdigest()

    # Valid manifest next to scripts (outside templates/) with matching sha256 passes
    manifest = tmp_path / "allowlist_promoted.json"
    manifest.write_text(json.dumps([{"file": "custom_promoted.api.json", "sha256": good_sha}]), encoding="utf-8")
    ok, matched, reason = ta.check_graph(custom, templates_dir=tdir, promoted_manifest=manifest)
    assert ok, reason
    assert matched == "custom_promoted"

    # Hash mismatch is refused
    bad_manifest = tmp_path / "bad_sha.json"
    bad_manifest.write_text(json.dumps([{"file": "custom_promoted.api.json", "sha256": "0" * 64}]), encoding="utf-8")
    ok, _, _ = ta.check_graph(custom, templates_dir=tdir, promoted_manifest=bad_manifest)
    assert not ok

    # Planted manifest entries with "..", "/", or "\\" are refused even with valid sha256
    outside_file = tmp_path / "evil.api.json"
    outside_file.write_bytes(good_bytes)
    for bad_name in ("../evil.api.json", "sub/evil.api.json", r"sub\evil.api.json"):
        trav_manifest = tmp_path / "trav.json"
        trav_manifest.write_text(json.dumps([{"file": bad_name, "sha256": good_sha}]), encoding="utf-8")
        ok, _, _ = ta.check_graph(custom, templates_dir=tdir, promoted_manifest=trav_manifest)
        assert not ok, f"traversal name {bad_name!r} should be refused"

    # Manifest sitting inside templates/ is ignored by default (default manifest is in scripts/)
    assert ta.DEFAULT_PROMOTED_MANIFEST.parent == ta.SCRIPTS_DIR
    (tdir / "allowlist_promoted.json").write_text(
        json.dumps([{"file": "custom_promoted.api.json", "sha256": good_sha}]), encoding="utf-8"
    )
    ok, _, _ = ta.check_graph(custom, templates_dir=tdir)
    assert not ok

