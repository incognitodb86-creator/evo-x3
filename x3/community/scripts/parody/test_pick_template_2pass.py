"""Routing and 2-pass canvas tests for the tq2_vsa_0.2 / oc_ref_2pass promotion."""
from __future__ import annotations

import json
from pathlib import Path

import fill_request as fr


def test_pick_template_portrait_ref_defaults_to_one_pass_oc_ref():
    # Derrick card 2026-11-20 8:28 AM CT: picker rolled back to the original 1-pass (4d909034 undone).
    assert fr.pick_template(True, "ref", True, character="FCTest", width=768, height=1344) == "oc_ref"
    assert fr.pick_template(True, "ref", False, width=768, height=1344) == "oc_ref"


def test_pick_template_16x9_ref_stays_on_one_pass_oc_ref():
    # Landscape 16:9 stays on 1-pass oc_ref until TQ4 Beta 7 is promoted.
    assert fr.pick_template(True, "ref", False, width=1344, height=768) == "oc_ref"
    assert fr.pick_template(True, "ref", True, character="FCTest", width=1344, height=768) == "oc_ref"


def test_pick_template_explicit_paths_unchanged():
    assert fr.pick_template(False, "guide", True, character="FCTest") == "named_parody"
    assert fr.pick_template(True, "guide", False, position="talk") == "talk"
    assert fr.pick_template(True, "guide", False) == "plain"
    assert fr.pick_template(True, "guide", True, character="FCTest") == "oc_guide"
    assert fr.pick_template(True, "ref", False, partner2_still="/tmp/p2.png") == "two_person"


def test_oc_ref_2pass_template_is_registered_with_vsa_0_2():
    assert "oc_ref_2pass" in fr.TEMPLATES
    path = fr.TEMPLATES["oc_ref_2pass"]
    assert path.is_file()
    graph = json.loads(path.read_text(encoding="utf-8"))
    assert graph["m_vsa"]["inputs"]["start_percent"] == 0.2
    assert graph["ksel"]["inputs"]["sampler_name"] == "euler"
    assert graph["s0_sched"]["inputs"]["scheduler"] == "simple"
    assert graph["s0_sched"]["inputs"]["steps"] == 8
    assert graph["p2sched"]["inputs"]["scheduler"] == "beta"
    assert graph["p2sched"]["inputs"]["steps"] == 3
    assert graph["p2sched"]["inputs"]["denoise"] == 0.4
    assert graph["c0"]["inputs"]["width"] == 384
    assert graph["c0"]["inputs"]["height"] == 672
    assert graph["lsu3"]["inputs"]["mode.scale"] == 2.0


def test_fill_request_2pass_keeps_half_res_c0(tmp_path):
    run_dir = tmp_path / "fr_2pass"
    still = tmp_path / "still.png"
    still.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
        b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    # Minimal valid 1x1 PNG may fail 18+ or image stage; use a real tiny PNG via PIL if available.
    try:
        from PIL import Image
        Image.new("RGB", (90, 160), (40, 80, 120)).save(still)
    except Exception:
        pass
    prompt = (
        "subject_definitions:\n"
        "S1 is an adult woman in her late twenties.\n\n"
        "summary:\n"
        "An adult woman walks along a beach at sunset.\n\n"
        "retention_analysis:\n"
        "Keep her face, hair, and white sundress.\n\n"
        "detailed_description:\n"
        "[Shot 1] Medium shot on a 35mm lens in golden hour light. "
        "At first, an adult woman in her late twenties walks across the sand in a white sundress. "
        "As it builds, she smiles and turns toward the water. "
        "By the end, she keeps walking down the shoreline as soft waves lap the sand."
    )
    rep = fr.fill_request(
        prompt, run_dir, ask="an adult woman walks along a beach at sunset",
        position="walking", still_image=str(still), still_mode="ref",
        template_name="oc_ref_2pass",
        width=768, height=1344, frames=124, seed=51083601, dry_run=True,
        refmod_stems=[],
    )
    assert rep["status"] == "READY", rep
    assert rep["template"] == "oc_ref_2pass"
    assert rep["canvas"] == [768, 1344]
    req = json.loads((run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert req["c0"]["inputs"]["width"] == 384
    assert req["c0"]["inputs"]["height"] == 672
    assert req["c0"]["inputs"]["length"] == 124
    assert req["m_vsa"]["inputs"]["start_percent"] == 0.2
    assert req["ksel"]["inputs"]["sampler_name"] == "euler"
    assert (run_dir / "DRY_RUN").is_file()
    assert not (run_dir / "_render_order.json").is_file()


def test_explicit_template_oc_ref_stays_one_pass(tmp_path):
    run_dir = tmp_path / "fr_1pass"
    still = tmp_path / "still.png"
    try:
        from PIL import Image
        Image.new("RGB", (90, 160), (40, 80, 120)).save(still)
    except Exception:
        still.write_bytes(Path("/workspace/mono-sync/x3/community/scripts/parody/test_pick_template_2pass.py").read_bytes()[:8])
        from PIL import Image
        Image.new("RGB", (90, 160), (40, 80, 120)).save(still)
    prompt = (
        "subject_definitions:\nS1 is an adult woman in her late twenties.\n\n"
        "summary:\nAn adult woman walks along a beach at sunset.\n\n"
        "retention_analysis:\nKeep her face and sundress.\n\n"
        "detailed_description:\n"
        "[Shot 1] Medium shot on a 35mm lens in golden hour light. "
        "An adult woman in her late twenties walks across the sand in a white sundress."
    )
    rep = fr.fill_request(
        prompt, run_dir, ask="an adult woman walks along a beach",
        position="walking", still_image=str(still), still_mode="ref",
        template_name="oc_ref", width=768, height=1344, frames=124,
        seed=51083601, dry_run=True, refmod_stems=[],
    )
    assert rep["status"] == "READY", rep
    assert rep["template"] == "oc_ref"
    req = json.loads((run_dir / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert req["c0"]["inputs"]["width"] == 768
    assert req["c0"]["inputs"]["height"] == 1344
    assert "lsu3" not in req
    assert req["m_vsa"]["inputs"]["start_percent"] == 0.0
