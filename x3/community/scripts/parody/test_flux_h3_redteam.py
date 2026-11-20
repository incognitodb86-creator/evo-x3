"""Red-team audit tests: Flux still builder (RefMod + LoRA + 18+ guard + pixl-inbox),
Flux-celeb -> H3Max INDEX + RefMod auto-pickup (via flux_meta.json AND ComfyUI PNG metadata),
H3Max Beta 7 LoRA + Realism LoRA (`r34l1sm` trigger only when loaded), and Beta 7 header conversion."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, PngImagePlugin

import fill_request as fr
import flux_still as fs
import render_writer_pipeline as p
import resolve as res
from test_writer_pipeline import GOOD_SEX, READ, home, job, scripted, stub_build  # noqa: F401


def _job_for_png(tmp_path, name, png_path, **kw):
    sr = dict(READ, source=str(png_path))
    srp = tmp_path / f"{name}_sr.json"
    srp.write_text(json.dumps(sr), encoding="utf-8")
    return job(tmp_path, name, still=str(png_path), still_read=str(srp), **kw)


def _make_comfy_png(path: Path, workflow: dict) -> Path:
    img = Image.new("RGB", (768, 1344), (120, 90, 80))
    info = PngImagePlugin.PngInfo()
    info.add_text("prompt", json.dumps(workflow))
    img.save(path, format="PNG", pnginfo=info)
    return path


def test_flux_still_refmod_and_lora_and_guard(tmp_path):
    # 18+ guard blocks youth terms before writing
    bad = fs.build_flux_still(tmp_path / "bad", "teen schoolgirl standing in a bedroom")
    assert bad["status"] == "NOT_READY"

    # Miraclein T2I + Klein9 RefMod + Klein9 LoRA in one graph
    r = fs.build_flux_still(
        tmp_path / "f1",
        "Adult woman in her late twenties standing by a sunlit window, natural skin pores, 35mm film.",
        mode="t2i",
        refmods=["klein9_sydney_sweeney_v1.safetensors"],
        loras=[{"name": "klein9/fk9_sydneysweeney_v1_prodigy.safetensors", "strength": 0.8}],
        character="Sydney Sweeney",
        dry_run=True,
    )
    assert r["status"] == "READY" and r["mode"] == "refmod"
    g = json.loads((tmp_path / "f1" / "still" / "request.api.json").read_text(encoding="utf-8"))
    assert g["12"]["inputs"]["mod_1"] == "klein9_sydney_sweeney_v1"
    assert g["12"]["inputs"]["mod_2"] == "none"
    assert g["12"]["inputs"]["copies_1"] == 1
    assert g["13"]["inputs"]["klein9_refmods"] == ["12", 0]
    assert g["13"]["inputs"]["custom_retention"] == 1.0
    assert g["13"]["inputs"]["retention"] == "fully_preserved (1.0)"
    # LoRA node wired between UNET (1) and CFGGuider (17)
    lora_nodes = [nid for nid, n in g.items() if n.get("class_type") == "LoraLoaderModelOnly"]
    assert len(lora_nodes) == 1
    assert g[lora_nodes[0]]["inputs"]["model"] == ["1", 0]
    assert g[lora_nodes[0]]["inputs"]["lora_name"] == "klein9\\fk9_sydneysweeney_v1_prodigy.safetensors"
    assert g["17"]["inputs"]["model"] == [lora_nodes[0], 0]
    meta = json.loads((tmp_path / "f1" / "flux_meta.json").read_text(encoding="utf-8"))
    assert "Sydney Sweeney" in meta["names"] and (tmp_path / "f1" / "DRY_RUN").is_file()

    # Hybrid CLI shortcut: RefMod author's recipe (RefMod 0.85 + Prodigy LoRA 0.60, retention 0.7)
    rc = fs.main([
        str(tmp_path / "f_hyb"),
        "--prompt", "The reference images represent one adult woman sitting on a sofa, natural skin pores, 35mm Kodak Portra 400.",
        "--hybrid", "Sydney Sweeney",
    ])
    assert rc == 0
    gh = json.loads((tmp_path / "f_hyb" / "still" / "request.api.json").read_text(encoding="utf-8"))
    assert gh["12"]["inputs"]["mod_1"] == "fk9_sydneysweeney_v1_refmod"
    assert gh["12"]["inputs"]["strength_1"] == 0.85
    hl = [n for n in gh.values() if isinstance(n, dict) and n.get("class_type") == "LoraLoaderModelOnly"]
    assert hl and hl[0]["inputs"]["lora_name"] == "klein9\\fk9_sydneysweeney_v1_prodigy.safetensors"
    assert hl[0]["inputs"]["strength_model"] == 0.60
    assert gh["13"]["inputs"]["retention"] == "partially_preserved (0.7)"


def test_refmod_likeness_defaults_anchor_and_negative_stream(tmp_path):
    """RefMod author's guide: likeness = fully_preserved (1.0); prompt points at the reference; RefMod on pos + neg."""
    r = fs.build_flux_still(
        tmp_path / "lk",
        "Adult woman in her late twenties sitting at a cafe table, natural skin pores, 35mm film.",
        refmods=["Sydney Sweeney"],
        dry_run=True,
    )
    assert r["status"] == "READY"
    g = json.loads((tmp_path / "lk" / "still" / "request.api.json").read_text(encoding="utf-8"))
    assert g["13"]["inputs"]["retention"] == "fully_preserved (1.0)"
    assert g["12"]["inputs"]["strength_1"] == 1.0
    assert g["5"]["inputs"]["text"].startswith(fs.REFMOD_ANCHOR)
    assert (tmp_path / "lk" / "prompt.txt").read_text(encoding="utf-8").startswith(fs.REFMOD_ANCHOR)
    neg_id = g["17"]["inputs"]["negative"][0]
    assert g[neg_id]["class_type"] == "Klein9RefModApply"
    assert g[neg_id]["inputs"]["conditioning"] == ["6", 0]
    assert g[neg_id]["inputs"]["klein9_refmods"] == ["12", 0]
    assert g[neg_id]["inputs"]["retention"] == "fully_preserved (1.0)"
    assert g["17"]["inputs"]["positive"] == ["13", 0]

    # A prompt that already names the reference is left as written; plain T2I gets no RefMod nodes or anchor.
    own = "The reference images represent one adult woman standing in a garden at golden hour."
    fs.build_flux_still(tmp_path / "own", own, refmods=["Sydney Sweeney"], dry_run=True)
    g2 = json.loads((tmp_path / "own" / "still" / "request.api.json").read_text(encoding="utf-8"))
    assert g2["5"]["inputs"]["text"] == own
    fs.build_flux_still(tmp_path / "t2i", "Adult woman standing in a garden at golden hour.", dry_run=True)
    g3 = json.loads((tmp_path / "t2i" / "still" / "request.api.json").read_text(encoding="utf-8"))
    assert not any(n.get("class_type") == "Klein9RefModApply" for n in g3.values() if isinstance(n, dict))
    assert not g3["5"]["inputs"]["text"].startswith(fs.REFMOD_ANCHOR)

    # Static RefMod candidate template matches likeness defaults (pos + neg RefMod at 1.0)
    static_g = json.loads(fs.MODES["refmod"].read_text(encoding="utf-8"))
    assert static_g["13"]["inputs"]["retention"] == "fully_preserved (1.0)"
    assert static_g["14"]["class_type"] == "Klein9RefModApply"
    assert static_g["17"]["inputs"]["negative"] == ["14", 0]

    # Queue command omits --remote on Windows local queueing, keeps it on X3 remote
    win_cmd = fs._queue_cmd(tmp_path / "lk", exe="python", rq=Path("run_queue.py"), remote=False)
    x3_cmd = fs._queue_cmd(tmp_path / "lk", exe="python3", rq=Path("run_queue.py"), remote=True)
    assert "--remote" not in win_cmd and "--remote" in x3_cmd


def test_comfy_png_celeb_refmod_and_lora_auto_pickup_for_h3max(tmp_path, monkeypatch):
    # Fake local H3 RefMod dir containing Sydney Sweeney + Megan Fox visual RefMods
    fake_refmods = tmp_path / "refmods"
    fake_refmods.mkdir()
    (fake_refmods / "minimaxh3_sydneysweeney_v1_refmod.safetensors").write_bytes(b"x" * 10)
    (fake_refmods / "minimaxh3_meganfox_v1_refmod.safetensors").write_bytes(b"x" * 10)
    monkeypatch.setattr(res, "REFMODS_DIR", fake_refmods)

    # Case A: PNG generated with Klein9RefModsLoader (NO flux_meta.json sidecar!)
    png_refmod = _make_comfy_png(
        tmp_path / "sydney_flux.png",
        {
            "12": {
                "class_type": "Klein9RefModsLoader",
                "inputs": {"mod_1": "klein9_sydney_sweeney_v1.safetensors", "strength_1": 1.0, "mod_2": "(none)"},
            }
        },
    )
    det_a = res.detect_still_identity(str(png_refmod))
    assert det_a["source"] == "comfy_png"
    assert any("sydney" in n.lower() for n in det_a["names"])

    # fill_request auto-picks up Sydney Sweeney's H3 visual RefMod without --character/--names!
    rep_a = fr.fill_request(GOOD_SEX, tmp_path / "h3_a", ask="she rides him", position="doggy", still_image=str(png_refmod))
    assert rep_a["status"] == "READY"
    assert rep_a["refmods"]["stems"] == ["minimaxh3_sydneysweeney_v1_refmod"]
    assert rep_a["refmods"]["still_detected_source"] == "comfy_png"

    # Case B: PNG generated with Klein9 celeb LoRA (fk9_meganfox_v1_prodigy.safetensors)
    png_lora = _make_comfy_png(
        tmp_path / "megan_flux.png",
        {
            "2": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {"lora_name": "klein9\\fk9_meganfox_v1_prodigy.safetensors", "strength_model": 0.85},
            }
        },
    )
    rep_b = fr.fill_request(GOOD_SEX, tmp_path / "h3_b", ask="she talks to camera", position="talk", still_image=str(png_lora))
    assert rep_b["status"] == "READY"
    assert rep_b["refmods"]["stems"] == ["minimaxh3_meganfox_v1_refmod"]


def test_pipeline_auto_links_flux_celeb_to_index_character(home, tmp_path, monkeypatch):
    fake_refmods = tmp_path / "refmods"
    fake_refmods.mkdir()
    (fake_refmods / "minimaxh3_sydneysweeney_v1_refmod.safetensors").write_bytes(b"x" * 10)
    monkeypatch.setattr(res, "REFMODS_DIR", fake_refmods)

    png_refmod = _make_comfy_png(
        tmp_path / "flux_out.png",
        {"12": {"class_type": "Klein9RefModsLoader", "inputs": {"mod_1": "klein9_sydney_sweeney_v1", "strength_1": 1.0}}},
    )
    scripted(monkeypatch, lambda purpose: GOOD_SEX)
    stub_build(monkeypatch)
    # Ask does NOT mention Sydney Sweeney at all; pipeline must detect her from the Flux PNG and link Cassie Howard!
    j = _job_for_png(tmp_path, "auto_celeb", png_refmod, ask="she has sex with him", character=None)
    r = p.run_clip(j, p.load_config(home / "config.yaml"), lambda *a: None)
    assert r["status"] == "READY"
    assert r["still_identity_source"] == "comfy_png"
    assert r["identity"]["actor"] == "Sydney Sweeney"
    assert r["identity"]["character"] == "Cassie Howard"


def test_h3_realism_lora_wiring_and_r31_trigger_hygiene(tmp_path):
    png = _make_comfy_png(tmp_path / "plain.png", {})
    # Without realism LoRA: no LoraLoaderModelOnly node, NO r34l1sm trigger
    r_off = fr.fill_request(
        "detailed_description: " + GOOD_SEX, tmp_path / "no_lora",
        ask="she has sex with him", position="doggy", still_image=str(png),
    )
    assert r_off["status"] == "READY"
    assert "r34l1sm" not in (tmp_path / "no_lora" / "prompt.txt").read_text(encoding="utf-8")
    g_off = json.loads((tmp_path / "no_lora" / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert g_off["m_attn"]["inputs"]["model"] == ["unet", 0]

    # With realism LoRA: LoraLoaderModelOnly wired between unet and m_attn, r34l1sm prepended
    r_on = fr.fill_request(
        "detailed_description: " + GOOD_SEX, tmp_path / "with_lora",
        ask="she has sex with him", position="doggy", still_image=str(png),
        loras=[fr.REALISM_LORA_DEFAULT],
    )
    assert r_on["status"] == "READY"
    prompt_txt = (tmp_path / "with_lora" / "prompt.txt").read_text(encoding="utf-8")
    assert "detailed_description: r34l1sm," in prompt_txt
    g_on = json.loads((tmp_path / "with_lora" / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert g_on["lora_1"]["class_type"] == "LoraLoaderModelOnly"
    assert g_on["lora_1"]["inputs"]["lora_name"] == "h3-realism-people-t2v-i2v-r2v.safetensors"
    assert g_on["lora_1"]["inputs"]["model"] == ["unet", 0]
    assert g_on["m_attn"]["inputs"]["model"] == ["lora_1", 0]


def test_lora_subfolder_uses_alienpc_backslash(tmp_path, monkeypatch):
    # OPUS-FINDINGS-20261119 #4: Windows ComfyUI lists subfolder LoRAs as `folder\file`.
    monkeypatch.delenv("EVO_COMFY_PATH_SEP", raising=False)
    assert fr.comfy_lora_name("klein9/a.safetensors") == "klein9\\a.safetensors"
    assert fr.comfy_lora_name("klein9\\a.safetensors") == "klein9\\a.safetensors"
    assert fr.comfy_lora_name(" top.safetensors ") == "top.safetensors"
    png = _make_comfy_png(tmp_path / "plain.png", {})
    r = fr.fill_request(
        "detailed_description: " + GOOD_SEX, tmp_path / "sub",
        ask="she has sex with him", position="doggy", still_image=str(png),
        loras=[fr.parse_lora_spec("h3max/concept_a.safetensors:0.4")],
    )
    assert r["status"] == "READY"
    g = json.loads((tmp_path / "sub" / "clip" / "request.api.json").read_text(encoding="utf-8"))
    assert g["lora_1"]["inputs"]["lora_name"] == "h3max\\concept_a.safetensors"
    monkeypatch.setenv("EVO_COMFY_PATH_SEP", "/")
    assert fr.comfy_lora_name("klein9\\a.safetensors") == "klein9/a.safetensors"


def test_beta7_convert_strips_banned_headers_on_prose_file(home, tmp_path, monkeypatch):
    png = _make_comfy_png(tmp_path / "p.png", {})
    bad_headers = (
        "subject_definitions:\n<Subject 1>: adult woman\n\n"
        "summary:\n(S1) on the beach.\n\n"
        "retention_analysis:\n<Subject 1>: fully_preserved\n\n"
        "integrated_multimodal_description:\n" + GOOD_SEX + "\n\n"
        "overall_soundscape:\nSoft surf and breath.\n\n"
        "non_diegetic_music:\nNone.\n"
    )
    pf = tmp_path / "hermes_prose.txt"
    pf.write_text(bad_headers, encoding="utf-8")
    scripted(monkeypatch, lambda purpose: "MUST NOT CALL")
    stub_build(monkeypatch)
    r = p.run_clip(_job_for_png(tmp_path, "b7norm", png, prose_file=str(pf)), p.load_config(home / "config.yaml"), lambda *a: None)
    assert r["status"] == "READY"
    out = (Path(r["run_dir"]) / "writer_output.txt").read_text(encoding="utf-8")
    for banned in ("integrated_multimodal_description:", "overall_soundscape:", "non_diegetic_music:"):
        assert banned not in out
    assert "Soft surf and breath." in out
