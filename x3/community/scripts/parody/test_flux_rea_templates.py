"""REA C3: flux_rea_edit / flux_rea_pose candidate templates (aspect-preserving reference resize, fixed 768x1344
canvas, Miraclein UNET, pos+neg Klein9 RefMod) and the 2-active-LoRA cap in flux_still._inject_flux_loras."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

import fill_request as fr
import flux_still as fs

REA_TEMPLATES = {
    "rea_edit": fs.TEMPLATES_DIR / "flux_rea_edit.candidate.api.json",
    "rea_pose": fs.TEMPLATES_DIR / "flux_rea_pose.candidate.api.json",
}

PROMPT_EDIT = (
    "Reframe the adult woman from image 1 into a wide 16:9 shot, extending the room background to the left and right, "
    "natural skin pores, 35mm film."
)
PROMPT_POSE = (
    "Show the adult woman from image 2 in the exact pose of image 1, keeping her face, hairstyle and hair color, "
    "natural skin pores, 35mm film."
)
CELEB_LORA = {"name": "klein9/fk9_sydneysweeney_v1_prodigy.safetensors", "strength": 0.6}


@pytest.fixture(autouse=True)
def _no_real_image_staging(monkeypatch):
    """Keep every build inside tmp_path: no Comfy input dir lookups, no copies outside the test dir."""
    monkeypatch.setattr(fr, "pixl_abs", lambda still: str(still))
    monkeypatch.setattr(fr, "_stage_still", lambda still: f"rea_tests/{Path(str(still)).name}")


def _png(tmp_path: Path, name: str, size=(768, 1344)) -> Path:
    p = tmp_path / name
    Image.new("RGB", size, (140, 110, 95)).save(p, format="PNG")
    return p


def _nodes(g: dict, class_type: str) -> dict:
    return {nid: n for nid, n in g.items() if isinstance(n, dict) and n.get("class_type") == class_type}


def _assert_links_exist(g: dict) -> None:
    for nid, node in g.items():
        for key, val in (node.get("inputs") or {}).items():
            if isinstance(val, list) and val and isinstance(val[0], str):
                assert val[0] in g, f"node {nid}.{key} links to missing node {val[0]!r}"


def _active_loras(g: dict) -> list:
    return [
        nid for nid, n in _nodes(g, "LoraLoaderModelOnly").items()
        if float(n["inputs"].get("strength_model", 0) or 0.0) > 0.0
    ]


def test_rea_modes_point_at_the_two_candidate_templates():
    assert REA_TEMPLATES.keys() <= set(fs.MODES)
    for mode, path in REA_TEMPLATES.items():
        assert fs.MODES[mode] == path and path.is_file()


@pytest.mark.parametrize("mode", sorted(REA_TEMPLATES))
def test_rea_template_graph_is_sane(mode):
    g = json.loads(REA_TEMPLATES[mode].read_text(encoding="utf-8"))
    assert g
    _assert_links_exist(g)

    # No KV cache, no GetImageSize, and nothing that stretches the reference (ImageScale crop="disabled").
    assert not _nodes(g, "FluxKVCache")
    assert not _nodes(g, "GetImageSize")
    assert not _nodes(g, "ImageScale")

    # Every reference reaches VAEEncode through an aspect-preserving 1.0 MP lanczos resize.
    resizes = _nodes(g, "ResizeImageMaskNode")
    assert resizes
    for vid, vae in _nodes(g, "VAEEncode").items():
        src = vae["inputs"]["pixels"]
        assert isinstance(src, list) and src[0] in resizes, f"VAEEncode {vid} is not fed by a ResizeImageMaskNode"
        rin = resizes[src[0]]["inputs"]
        assert rin["resize_type"] == "scale total pixels"
        assert float(rin["resize_type.megapixels"]) == 1.0
        assert rin["scale_method"] == "lanczos"
        up = g[rin["input"][0]]["class_type"]
        assert up in ("LoadImage", "DWPreprocessor")

    # Fixed integer target canvas: flux_still.py --width/--height reframes natively instead of following the reference.
    for class_type in ("EmptyFlux2LatentImage", "Flux2Scheduler"):
        for nid, node in _nodes(g, class_type).items():
            assert node["inputs"]["width"] == 768 and isinstance(node["inputs"]["width"], int), nid
            assert node["inputs"]["height"] == 1344 and isinstance(node["inputs"]["height"], int), nid

    # Miraclein UNET, euler, 12 steps, CFG 1.1.
    assert _nodes(g, "UNETLoader") and all(
        n["inputs"]["unet_name"] == "Miraclein_4.5_9b_NVFP4.safetensors" for n in _nodes(g, "UNETLoader").values()
    )
    assert all(n["inputs"]["sampler_name"] == "euler" for n in _nodes(g, "KSamplerSelect").values())
    assert all(int(n["inputs"]["steps"]) == 12 for n in _nodes(g, "Flux2Scheduler").values())
    assert all(float(n["inputs"]["cfg"]) == 1.1 for n in _nodes(g, "CFGGuider").values())

    # Klein9 RefMod loader feeds a RefMod apply on BOTH the positive and the negative stream.
    loader_ids = sorted(_nodes(g, "Klein9RefModsLoader"))
    assert len(loader_ids) == 1
    applies = _nodes(g, "Klein9RefModApply")
    assert len(applies) == 2
    guider = next(iter(_nodes(g, "CFGGuider").values()))
    pos_id, neg_id = guider["inputs"]["positive"][0], guider["inputs"]["negative"][0]
    for aid in (pos_id, neg_id):
        assert aid in applies
        ain = applies[aid]["inputs"]
        assert ain["klein9_refmods"] == [loader_ids[0], 0]
        assert ain["retention"] == "fully_preserved (1.0)"
        assert ain["custom_retention"] == 1.0
        assert g[ain["conditioning"][0]]["class_type"] == "ReferenceLatent"
    assert all(v == "none" for k, v in g[loader_ids[0]]["inputs"].items() if k.startswith("mod_"))


def test_rea_pose_keeps_pose_lora_and_dwpreprocessor():
    g = json.loads(REA_TEMPLATES["rea_pose"].read_text(encoding="utf-8"))
    poses = [n for n in _nodes(g, "LoraLoaderModelOnly").values()
             if n["inputs"]["lora_name"] == "refcontrol_v2_poses.safetensors"]
    assert len(poses) == 1 and float(poses[0]["inputs"]["strength_model"]) == 0.9
    dw_id, dw = next(iter(_nodes(g, "DWPreprocessor").items()))
    assert g[dw["inputs"]["image"][0]]["class_type"] == "LoadImage"
    # the DW pose map still reaches VAEEncode through the aspect-preserving resize, not through a stretched ImageScale
    pose_resizes = [nid for nid, n in _nodes(g, "ResizeImageMaskNode").items() if n["inputs"]["input"] == [dw_id, 0]]
    assert len(pose_resizes) == 1
    assert any(v["inputs"]["pixels"] == [pose_resizes[0], 0] for v in _nodes(g, "VAEEncode").values())


def test_rea_edit_build_reframes_to_1344x768_with_likeness_refmods(tmp_path):
    r = fs.build_flux_still(
        tmp_path / "rea_edit",
        PROMPT_EDIT,
        mode="rea_edit",
        refmods=["Sydney Sweeney"],
        image=str(_png(tmp_path, "STILL.png")),
        width=1344,
        height=768,
        dry_run=True,
    )
    assert r["status"] == "READY" and r["mode"] == "rea_edit"

    g = json.loads((tmp_path / "rea_edit" / "still" / "request.api.json").read_text(encoding="utf-8"))
    _assert_links_exist(g)
    for class_type in ("EmptyFlux2LatentImage", "Flux2Scheduler"):
        for nid, node in _nodes(g, class_type).items():
            assert node["inputs"]["width"] == 1344 and node["inputs"]["height"] == 768, nid

    applies = _nodes(g, "Klein9RefModApply")
    assert len(applies) == 2
    assert all(n["inputs"]["retention"] == "fully_preserved (1.0)" for n in applies.values())
    loader = next(iter(_nodes(g, "Klein9RefModsLoader").values()))
    assert loader["inputs"]["mod_1"] == "fk9_sydneysweeney_v1_refmod"

    assert g["5"]["inputs"]["text"].startswith(fs.REFMOD_ANCHOR)
    assert (tmp_path / "rea_edit" / "prompt.txt").read_text(encoding="utf-8").startswith(fs.REFMOD_ANCHOR)
    # The reference stays aspect-preserving even after the 9:16 -> 16:9 reframe request.
    assert not _nodes(g, "ImageScale") and not _nodes(g, "GetImageSize")
    assert g["11"]["inputs"]["pixels"][0] == "10" and g["10"]["inputs"]["resize_type"] == "scale total pixels"
    assert g["7"]["inputs"]["image"] == "rea_tests/STILL.png"
    assert (tmp_path / "rea_edit" / "DRY_RUN").is_file()
    meta = json.loads((tmp_path / "rea_edit" / "flux_meta.json").read_text(encoding="utf-8"))
    assert meta["size"] == "1344x768" and meta["mode"] == "rea_edit"
    assert meta["refmods"] == ["fk9_sydneysweeney_v1_refmod"]
    assert any("sydneysweeney" in n.lower().replace(" ", "") for n in meta["names"])


def test_rea_pose_build_with_one_celeb_lora_hits_exactly_two_active_loras(tmp_path):
    r = fs.build_flux_still(
        tmp_path / "rea_pose",
        PROMPT_POSE,
        mode="rea_pose",
        refmods=["Sydney Sweeney"],
        image=str(_png(tmp_path, "IDENTITY.png")),
        pose_image=str(_png(tmp_path, "POSE_REF.png")),
        loras=[dict(CELEB_LORA)],
        dry_run=True,
    )
    assert r["status"] == "READY"
    g = json.loads((tmp_path / "rea_pose" / "still" / "request.api.json").read_text(encoding="utf-8"))
    _assert_links_exist(g)
    active = _active_loras(g)
    assert len(active) == 2
    names = sorted(g[n]["inputs"]["lora_name"] for n in active)
    assert names == sorted(["refcontrol_v2_poses.safetensors", "klein9\\fk9_sydneysweeney_v1_prodigy.safetensors"])
    # The LoRA chain stays wired into the guider model input, and both reference images landed on LoadImage nodes.
    guider = next(iter(_nodes(g, "CFGGuider").values()))
    assert guider["inputs"]["model"] in ([n, 0] for n in active)
    imgs = sorted(n["inputs"]["image"] for n in _nodes(g, "LoadImage").values())
    assert imgs == sorted(["rea_tests/IDENTITY.png", "rea_tests/POSE_REF.png"])


def test_rea_pose_rejects_third_active_lora(tmp_path):
    with pytest.raises(ValueError, match=r"FLUX LoRA cap is 2 active LoRAs \(got 3\)"):
        fs.build_flux_still(
            tmp_path / "rea_pose_3",
            PROMPT_POSE,
            mode="rea_pose",
            loras=[dict(CELEB_LORA), {"name": "klein9/fk9_meganfox_v1_prodigy.safetensors", "strength": 0.5}],
            dry_run=True,
        )


def test_plain_t2i_with_one_lora_still_works(tmp_path):
    r = fs.build_flux_still(
        tmp_path / "t2i",
        "Adult woman in her late twenties standing by a sunlit window, natural skin pores, 35mm film.",
        mode="t2i",
        loras=[dict(CELEB_LORA)],
        dry_run=True,
    )
    assert r["status"] == "READY" and r["mode"] == "t2i"
    g = json.loads((tmp_path / "t2i" / "still" / "request.api.json").read_text(encoding="utf-8"))
    assert len(_active_loras(g)) == 1
    assert not _nodes(g, "Klein9RefModApply")
