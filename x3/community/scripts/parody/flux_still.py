#!/usr/bin/env python3
"""Build and (on --queue --yes-derrick) remotely run a FLUX.2 Klein / Miraclein 4.5 still on AlienPc ComfyUI.

Supports all Flux modes (T2I, Klein9 RefMod, Klein9 LoRA, ReferenceLatent single-change edit, RefControl pose/layout),
enforces the 18+ adult guard before any GPU call, writes `flux_meta.json` so H3Max automatically recognizes any celeb
RefMod/LoRA used to create the still, and copies the finished PNG into `/home/evo/AI/pixl-inbox/` for PixlStash import.

Dry run by default: builds `still/request.api.json`, `prompt.txt`, and `flux_meta.json`, prints READY, and stops for
Derrick's yes before queueing.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PARODY_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PARODY_DIR.parent
TEMPLATES_DIR = SCRIPTS_DIR.parent / "templates"
for _p in (str(SCRIPTS_DIR), str(PARODY_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_AI_ROOT = Path(
    os.environ.get("EVO_AI_ROOT")
    or ("/home/evo/AI" if os.path.isdir("/home/evo/AI") else Path(__file__).resolve().parents[3])
)
PIXL_INBOX = Path(os.environ.get("EVO_PIXL_INBOX") or (_AI_ROOT / "pixl-inbox"))

import build_request as br
import fill_request as fr
import resolve as res
import wp_lint

MODES = {
    "t2i": TEMPLATES_DIR / "miraclein_t2i.candidate.api.json",
    "refmod": TEMPLATES_DIR / "miraclein_refmod.candidate.api.json",
    "edit": TEMPLATES_DIR / "miraclein_edit.candidate.api.json",
    "klein_t2i": TEMPLATES_DIR / "flux_stills_t2i_klein.candidate.api.json",
    "pose": TEMPLATES_DIR / "flux_stills_pose_klein.candidate.api.json",
    "layout": TEMPLATES_DIR / "flux_stills_layout_klein.candidate.api.json",
}

# Klein9 RefMod author's guide (malcolmrey/various klein9/docs/FLUX2_KLEIN9_REFMODS_GUIDE.md): fully_preserved (1.0) at
# strength 1.0 is the likeness preset; partially_preserved (0.7) is the flexible-styling preset of the RefMod + LoRA hybrid.
LIKENESS_RETENTION = "fully_preserved (1.0)"
HYBRID_RETENTION = "partially_preserved (0.7)"
# Klein is an edit model: the author's benchmark prompt points it at the reference images.
REFMOD_ANCHOR = ("The reference images represent one adult person; keep the face and hair unchanged "
                 "and exact as in the reference images.")

RETENTION_PRESETS = {
    "0.4": "attribute_transfer (0.4)",
    "0.7": "partially_preserved (0.7)",
    "1.0": "fully_preserved (1.0)",
    "attribute_transfer": "attribute_transfer (0.4)",
    "partially_preserved": "partially_preserved (0.7)",
    "fully_preserved": "fully_preserved (1.0)",
}


def _norm_retention(val: Optional[str]) -> str:
    s = (val or LIKENESS_RETENTION).strip()
    return RETENTION_PRESETS.get(s.lower(), s)


def _find_node(graph: Dict[str, Any], class_type: str, title_substr: Optional[str] = None) -> Optional[str]:
    for nid, node in graph.items():
        if not isinstance(node, dict) or node.get("class_type") != class_type:
            continue
        if title_substr:
            title = str((node.get("_meta") or {}).get("title") or "").lower()
            if title_substr.lower() not in title:
                continue
        return nid
    return None


def _inject_flux_loras(graph: Dict[str, Any], loras: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    active = [
        {"name": fr.comfy_lora_name(lr["name"]), "strength": float(lr.get("strength", 0.85))}
        for lr in loras if str(lr.get("name") or "").strip() and float(lr.get("strength", 0.85)) > 0
    ]
    if not active:
        return []
    unet_id = _find_node(graph, "UNETLoader")
    if not unet_id:
        raise ValueError("Flux template has no UNETLoader node")

    # If the template already has an inactive (strength 0.0) LoraLoaderModelOnly on UNET, reuse it for the first LoRA.
    existing_lora = None
    for nid, node in graph.items():
        if isinstance(node, dict) and node.get("class_type") == "LoraLoaderModelOnly":
            if node.get("inputs", {}).get("model") == [unet_id, 0] and float(node["inputs"].get("strength_model", 0)) == 0.0:
                existing_lora = nid
                break

    first_added = None
    prev_ref: List[Any] = [unet_id, 0]
    start_idx = 0
    if existing_lora:
        graph[existing_lora]["inputs"]["lora_name"] = active[0]["name"]
        graph[existing_lora]["inputs"]["strength_model"] = active[0]["strength"]
        prev_ref = [existing_lora, 0]
        start_idx = 1

    # Chain any additional LoRAs after prev_ref, then rewire downstream consumers of prev_ref's original output.
    orig_out = list(prev_ref)
    for idx, lr in enumerate(active[start_idx:], start=1 + start_idx):
        nid = f"flux_lora_{idx}"
        while nid in graph:
            nid += "_x"
        graph[nid] = {
            "_meta": {"title": f"flux_lora_{idx}"},
            "class_type": "LoraLoaderModelOnly",
            "inputs": {"lora_name": lr["name"], "model": list(prev_ref), "strength_model": lr["strength"]},
        }
        if first_added is None:
            first_added = nid
        prev_ref = [nid, 0]

    if first_added is not None:
        for nid, node in graph.items():
            if nid == first_added or not isinstance(node, dict):
                continue
            inp = node.get("inputs")
            if not isinstance(inp, dict):
                continue
            for k, v in list(inp.items()):
                if v == orig_out:
                    inp[k] = list(prev_ref)
    return active


def _klein9_refmod_name(spec: str) -> str:
    """Turn a filename, stem, or plain celeb name (e.g. 'Sydney Sweeney') into a Klein9 RefMod stem.
    ComfyUI-Flux2Klein9Mod lists stems without `.safetensors` in `Klein9RefModsLoader` (e.g. `fk9_sydneysweeney_v1_refmod`)."""
    s = str(spec or "").strip()
    if not s or s.lower() in ("none", "(none)"):
        return "none"
    if s.lower().endswith(".safetensors"):
        return s[:-12]
    if " " in s or not any(tok in s.lower() for tok in ("fk9_", "klein9", "_refmod", "_v1", "_v2")):
        import re
        compact = re.sub(r"[^a-zA-Z0-9]", "", s).lower()
        return f"fk9_{compact}_v1_refmod"
    return s


def _hybrid_stack_for_name(name: str) -> tuple[str, Dict[str, Any]]:
    """RefMod author's hybrid stack: RefMod @ 0.85 + Prodigy LoRA @ 0.60 at partially_preserved (0.7).
    The author's own visual score (98%) was measured on distilled flux-2-klein-9b-fp8, not on Miraclein."""
    import re
    compact = re.sub(r"[^a-zA-Z0-9]", "", str(name or "")).lower()
    return (
        f"fk9_{compact}_v1_refmod",
        {"name": f"klein9/fk9_{compact}_v1_prodigy.safetensors", "strength": 0.60},
    )


def _inject_flux_refmods(
    graph: Dict[str, Any],
    refmods: Sequence[str],
    strength: float = 1.0,
    retention: Optional[str] = None,
) -> List[str]:
    clean = [_klein9_refmod_name(m) for m in refmods if str(m or "").strip()]
    clean = [m for m in clean if m != "none"]
    if not clean:
        return []
    loader_id = _find_node(graph, "Klein9RefModsLoader")
    apply_id = _find_node(graph, "Klein9RefModApply")
    if not loader_id or not apply_id:
        guider_id = _find_node(graph, "CFGGuider")
        if not guider_id:
            raise ValueError("Flux template has no CFGGuider node to attach Klein9RefModApply")
        loader_id = "klein9_refmods_loader"
        apply_id = "klein9_refmod_apply"
        pos_in = graph[guider_id]["inputs"]["positive"]
        graph[loader_id] = {
            "_meta": {"title": "klein9_refmods_loader"},
            "class_type": "Klein9RefModsLoader",
            "inputs": {
                **{f"mod_{i}": "none" for i in range(1, 9)},
                **{f"strength_{i}": 1.0 for i in range(1, 9)},
                **{f"copies_{i}": 1 for i in range(1, 9)},
            },
        }
        graph[apply_id] = {
            "_meta": {"title": "klein9_refmod_apply"},
            "class_type": "Klein9RefModApply",
            "inputs": {
                "blend_mode": "manifold_blur",
                "conditioning": pos_in,
                "custom_retention": 1.0,
                "klein9_refmods": [loader_id, 0],
                "ref_method": "default",
                "retention": _norm_retention(retention),
            },
        }
        graph[guider_id]["inputs"]["positive"] = [apply_id, 0]

    for i in range(1, 9):
        graph[loader_id]["inputs"][f"mod_{i}"] = clean[i - 1] if i <= len(clean) else "none"
        graph[loader_id]["inputs"][f"strength_{i}"] = float(strength)
        graph[loader_id]["inputs"].setdefault(f"copies_{i}", 1)
    if "refmods" in graph[apply_id]["inputs"] and "klein9_refmods" not in graph[apply_id]["inputs"]:
        graph[apply_id]["inputs"]["klein9_refmods"] = graph[apply_id]["inputs"].pop("refmods")
    graph[apply_id]["inputs"].setdefault("custom_retention", 1.0)
    graph[apply_id]["inputs"]["retention"] = _norm_retention(retention)

    # The author's workflow injects the RefMod into both the positive and the negative stream, so CFG > 1 does not
    # push away from the reference. Mirror the positive apply node onto the guider's negative input.
    guider_id = _find_node(graph, "CFGGuider")
    neg_in = graph[guider_id]["inputs"].get("negative") if guider_id else None
    neg_node = graph.get(neg_in[0]) if isinstance(neg_in, list) and neg_in else None
    if isinstance(neg_in, list) and not (isinstance(neg_node, dict) and neg_node.get("class_type") == "Klein9RefModApply"):
        neg_id = "klein9_refmod_apply_neg"
        while neg_id in graph:
            neg_id += "_x"
        graph[neg_id] = {
            "_meta": {"title": "klein9_refmod_apply_neg"},
            "class_type": "Klein9RefModApply",
            "inputs": {**copy.deepcopy(graph[apply_id]["inputs"]), "conditioning": list(neg_in)},
        }
        graph[guider_id]["inputs"]["negative"] = [neg_id, 0]
    elif isinstance(neg_node, dict):
        neg_node["inputs"]["retention"] = graph[apply_id]["inputs"]["retention"]
    return clean[:8]


def _existing_graph_refmods(graph: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for node in graph.values():
        if not isinstance(node, dict) or node.get("class_type") != "Klein9RefModsLoader":
            continue
        inp = node.get("inputs") or {}
        for i in range(1, 9):
            m = str(inp.get(f"mod_{i}") or "").strip()
            if m and m.lower() not in ("none", "(none)") and m not in out:
                out.append(m)
    return out


def _existing_graph_loras(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for node in graph.values():
        if not isinstance(node, dict) or node.get("class_type") not in ("LoraLoaderModelOnly", "LoraLoader"):
            continue
        inp = node.get("inputs") or {}
        name = str(inp.get("lora_name") or "").strip()
        strength = float(inp.get("strength_model") or 0.0)
        if name and strength > 0.0:
            out.append({"name": name, "strength": strength})
    return out


def build_flux_still(
    run_dir: Path,
    prompt_text: str,
    mode: str = "t2i",
    *,
    template_path: Optional[Path] = None,
    request_json: Optional[Path] = None,
    unet: Optional[str] = None,
    refmods: Optional[Sequence[str]] = None,
    refmod_strength: float = 1.0,
    retention: Optional[str] = None,
    loras: Optional[Sequence[Dict[str, Any]]] = None,
    image: Optional[str] = None,
    pose_image: Optional[str] = None,
    width: Optional[int] = 768,
    height: Optional[int] = 1344,
    steps: Optional[int] = None,
    cfg: Optional[float] = None,
    seed: int = 51083601,
    character: Optional[str] = None,
    actor: Optional[str] = None,
    names: Optional[Sequence[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    rep: Dict[str, Any] = {"hook": "flux_still", "mode": mode, "seed": int(seed), "status": "NOT_READY"}

    def _fail(reason: str) -> Dict[str, Any]:
        rep["reason"] = reason
        (run_dir / "still_NOT_READY.txt").write_text(f"NOT_READY: {reason}\n", encoding="utf-8")
        (run_dir / "build_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
        return dict(rep, run_dir=str(run_dir))

    raw = (prompt_text or "").strip()
    if not raw:
        return _fail("empty still prompt")
    if (m := wp_lint.YOUTH_RE.search(raw)) or (m := wp_lint.UNDER18_AGE_RE.search(raw)):
        return _fail(f"18+ guard blocked still prompt: {m.group(0)!r}")
    try:
        br._check_writer_18plus(raw, {"ask": raw})
    except br.WriterNotReady as e:
        return _fail(str(e).removeprefix("NOT_READY: "))

    # Load a saved request.api.json directly when provided; else auto-switch plain t2i -> refmod if RefMods supplied.
    if request_json is not None:
        eff_mode = "request_json"
        tpath = Path(request_json)
    else:
        eff_mode = "refmod" if (mode == "t2i" and refmods and not template_path) else mode
        tpath = Path(template_path) if template_path else MODES.get(eff_mode)
    if not tpath or not tpath.is_file():
        return _fail(f"unknown or missing Flux template: {tpath or eff_mode!r}")

    if width is not None and width % 16 != 0:
        return _fail(f"Flux width must be divisible by 16 (got {width})")
    if height is not None and height % 16 != 0:
        return _fail(f"Flux height must be divisible by 16 (got {height})")

    g = copy.deepcopy(json.loads(tpath.read_text(encoding="utf-8")))
    pos_id = _find_node(g, "CLIPTextEncode", "positive") or _find_node(g, "CLIPTextEncode")
    if not pos_id:
        return _fail("Flux template has no positive CLIPTextEncode node")
    g[pos_id]["inputs"]["text"] = raw

    if unet and str(unet).strip():
        unet_id = _find_node(g, "UNETLoader")
        if not unet_id:
            return _fail("Flux template has no UNETLoader node for --unet")
        g[unet_id]["inputs"]["unet_name"] = str(unet).strip()

    if (lat_id := _find_node(g, "EmptyFlux2LatentImage")):
        if width is not None and isinstance(g[lat_id]["inputs"].get("width"), int):
            g[lat_id]["inputs"]["width"] = int(width)
        if height is not None and isinstance(g[lat_id]["inputs"].get("height"), int):
            g[lat_id]["inputs"]["height"] = int(height)
    if (sched_id := _find_node(g, "Flux2Scheduler")):
        if width is not None and isinstance(g[sched_id]["inputs"].get("width"), int):
            g[sched_id]["inputs"]["width"] = int(width)
        if height is not None and isinstance(g[sched_id]["inputs"].get("height"), int):
            g[sched_id]["inputs"]["height"] = int(height)
        if steps is not None:
            g[sched_id]["inputs"]["steps"] = int(steps)
    if cfg is not None and (gid := _find_node(g, "CFGGuider")):
        g[gid]["inputs"]["cfg"] = float(cfg)
    if (nid := _find_node(g, "RandomNoise")):
        g[nid]["inputs"]["noise_seed"] = int(seed)

    # Stage input images for edit / pose / layout modes.
    if pose_image:
        p_rel = fr._stage_still(fr.pixl_abs(pose_image))
        p_node = _find_node(g, "LoadImage", "pose") or _find_node(g, "LoadImage", "image1") or _find_node(g, "LoadImage")
        if p_node and p_rel:
            g[p_node]["inputs"]["image"] = p_rel
    if image:
        i_rel = fr._stage_still(fr.pixl_abs(image))
        i_node = _find_node(g, "LoadImage", "identity") or _find_node(g, "LoadImage", "image2") or _find_node(g, "LoadImage", "image1") or _find_node(g, "LoadImage")
        if i_node and i_rel:
            g[i_node]["inputs"]["image"] = i_rel

    applied_refmods = _inject_flux_refmods(g, refmods or [], strength=refmod_strength, retention=retention)
    applied_loras = _inject_flux_loras(g, loras or [])
    if request_json is not None:
        if not applied_refmods:
            applied_refmods = _existing_graph_refmods(g)
        if not applied_loras:
            applied_loras = _existing_graph_loras(g)
    if applied_refmods and "reference" not in raw.lower():
        raw = f"{REFMOD_ANCHOR} {raw}"
        g[pos_id]["inputs"]["text"] = raw

    if (sid := _find_node(g, "SaveImage")):
        g[sid]["inputs"]["filename_prefix"] = f"community/{run_dir.name}/still"

    eff_w = width
    eff_h = height
    if (lat_id := _find_node(g, "EmptyFlux2LatentImage")):
        if eff_w is None:
            eff_w = g[lat_id]["inputs"].get("width")
        if eff_h is None:
            eff_h = g[lat_id]["inputs"].get("height")
    size_str = f"{int(eff_w)}x{int(eff_h)}" if (eff_w and eff_h) else "saved"
    unet_id = _find_node(g, "UNETLoader")
    eff_unet = g[unet_id]["inputs"].get("unet_name") if unet_id else None

    # Collect identity metadata so H3Max auto-picks up the celeb + INDEX character + H3 RefMod when animating this still.
    inferred_names: List[str] = []
    for x in ([character, actor] + list(names or [])):
        if x and str(x).strip() and str(x).strip() not in inferred_names:
            inferred_names.append(str(x).strip())
    for fn in list(applied_refmods) + [lr["name"] for lr in applied_loras]:
        for nm in res.names_from_flux_refmod_or_lora(fn):
            if nm not in inferred_names:
                inferred_names.append(nm)

    meta = {
        "source": "flux_still",
        "mode": eff_mode,
        "template": tpath.name,
        "unet": eff_unet,
        "prompt": raw,
        "character": character,
        "actor": actor,
        "names": inferred_names,
        "refmods": applied_refmods,
        "loras": applied_loras,
        "size": size_str,
        "seed": int(seed),
    }

    still_dir = run_dir / "still"
    still_dir.mkdir(parents=True, exist_ok=True)
    (still_dir / "request.api.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (run_dir / "prompt.txt").write_text(raw + "\n", encoding="utf-8")
    (run_dir / "flux_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (still_dir / "flux_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if (nr := run_dir / "still_NOT_READY.txt").exists():
        nr.unlink()

    order = {"order": [{"pos": 1, "tag": "still", "job_type": "still", "size": size_str,
                        "arm": eff_mode, "scene": "flux_still", "seed": int(seed)}]}
    marker, order_file = run_dir / "DRY_RUN", run_dir / "_render_order.json"
    if dry_run:
        if order_file.exists():
            order_file.unlink()
        marker.write_text("dry run of flux_still: built for review only, never queue without --yes-derrick\n", encoding="utf-8")
    else:
        if marker.exists():
            marker.unlink()
        order_file.write_text(json.dumps(order, indent=2) + "\n", encoding="utf-8")

    rep.update(status="READY", mode=eff_mode, template=tpath.name, unet=eff_unet, size=size_str,
               refmods=applied_refmods, loras=applied_loras, names=inferred_names, dry_run=dry_run)
    (run_dir / "build_report.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    return dict(rep, run_dir=str(run_dir))


def _queue_cmd(run_dir: Path, *, exe: str, rq: Path, remote: Optional[bool] = None) -> List[str]:
    use_remote = (os.name != "nt") if remote is None else bool(remote)
    cmd = [exe, str(rq)]
    if use_remote:
        cmd.append("--remote")
    cmd.extend(["--run-dir", str(run_dir), "--no-upscale"])
    return cmd


def queue_flux_still(run_dir: Path, *, pixl_inbox: Path = PIXL_INBOX, remote: Optional[bool] = None) -> Dict[str, Any]:
    """Queue a READY Flux still via run_queue.py (--remote on X3, local on Windows), then drop into pixl-inbox."""
    run_dir = Path(run_dir)
    rq = SCRIPTS_DIR / "run_queue.py"
    py = Path(os.environ.get("RQ_PY") or (_AI_ROOT / "render" / "x3" / ".venv" / "bin" / "python3"))
    exe = str(py) if py.is_file() else sys.executable
    proc = subprocess.run(
        _queue_cmd(run_dir, exe=exe, rq=rq, remote=remote),
        cwd=str(SCRIPTS_DIR.parent),
        capture_output=True, text=True, timeout=600,
    )
    png = run_dir / "still" / "still.png"
    if not png.is_file():
        pngs = sorted((run_dir / "still").glob("*.png"))
        png = pngs[0] if pngs else png
    out: Dict[str, Any] = {"rc": proc.returncode, "stdout": (proc.stdout or "")[-600:], "stderr": (proc.stderr or "")[-600:]}
    if proc.returncode == 0 and png.is_file():
        out["still"] = str(png.resolve())
        if pixl_inbox.is_dir():
            dst = pixl_inbox / f"{run_dir.name}_{png.name}"
            shutil.copy2(png, dst)
            out["pixl_inbox"] = str(dst)
        # Ensure sidecar sits next to the exact downloaded PNG filename too.
        src_meta = run_dir / "flux_meta.json"
        if src_meta.is_file():
            shutil.copy2(src_meta, png.with_suffix(".flux_meta.json"))
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build & remotely run a FLUX.2 Klein / Miraclein 4.5 still on AlienPc.")
    ap.add_argument("run_dir", help="Absolute run directory under /home/evo/AI/community/runs/<name>")
    ap.add_argument("--prompt", required=True, help="Positive FLUX still prompt (per flux-klein-prompting skill)")
    ap.add_argument("--mode", default="t2i", choices=sorted(MODES), help="Flux mode (default: t2i; auto-refmod if --refmod)")
    ap.add_argument("--template", default=None, help="Optional explicit template JSON path")
    ap.add_argument("--request-json", default=None, help="Reuse a saved request.api.json graph (preserves its UNET/RefMod/LoRA/canvas unless overridden)")
    ap.add_argument("--unet", default=None, help="Override UNETLoader unet_name (e.g. Miraclein_4.5_9b_FP8.safetensors)")
    ap.add_argument("--refmod", action="append", default=[], help="Klein9 RefMod filename, stem, or celeb name (repeatable, up to 8)")
    ap.add_argument("--refmod-strength", type=float, default=None, help="RefMod strength (default 1.0; 0.85 with --hybrid)")
    ap.add_argument("--retention", default=None,
                    help="Klein9RefModApply retention (default 'fully_preserved (1.0)' for likeness; "
                         "'partially_preserved (0.7)' with --hybrid)")
    ap.add_argument("--lora", action="append", default=[], help="Klein9 LoRA spec: <filename>[:<strength>] (repeatable)")
    ap.add_argument("--hybrid", default=None, help="RefMod author's hybrid stack for a celeb name: fk9_<name>_v1_refmod @ 0.85 + fk9_<name>_v1_prodigy LoRA @ 0.60, retention 0.7")
    ap.add_argument("--image", default=None, help="Input/identity image path (for edit / pose / layout)")
    ap.add_argument("--pose-image", default=None, help="Pose/layout reference image path (for pose / layout)")
    ap.add_argument("--width", type=int, default=None, help="Output width (default 768; with --request-json keeps saved width unless set)")
    ap.add_argument("--height", type=int, default=None, help="Output height (default 1344; with --request-json keeps saved height unless set)")
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--cfg", type=float, default=None)
    ap.add_argument("--seed", type=int, default=51083601)
    ap.add_argument("--character", default=None)
    ap.add_argument("--actor", default=None)
    ap.add_argument("--names", nargs="+", default=None)
    ap.add_argument("--queue", action="store_true", help="Queue on AlienPc ComfyUI (requires --yes-derrick)")
    ap.add_argument("--yes-derrick", action="store_true", help="Required with --queue after Derrick approves the prompt")
    a = ap.parse_args(argv)
    if a.queue and not a.yes_derrick:
        print("NOT_READY --queue requires --yes-derrick after Derrick approved this still prompt")
        return 3
    d = Path(a.run_dir)
    if not d.is_absolute():
        print(f"NOT_READY run_dir must be an absolute path: {a.run_dir}")
        return 3
    refmods = list(a.refmod or [])
    loras = [fr.parse_lora_spec(s) for s in (a.lora or [])]
    refmod_strength = a.refmod_strength
    retention = a.retention
    char = a.character
    if a.hybrid:
        h_mod, h_lora = _hybrid_stack_for_name(a.hybrid)
        refmods.insert(0, h_mod)
        loras.insert(0, h_lora)
        if refmod_strength is None:
            refmod_strength = 0.85
        if retention is None:
            retention = HYBRID_RETENTION
        if not char:
            char = a.hybrid
    if refmod_strength is None:
        refmod_strength = 1.0
    eff_w = a.width if a.width is not None else (None if a.request_json else 768)
    eff_h = a.height if a.height is not None else (None if a.request_json else 1344)
    rep = build_flux_still(
        d, a.prompt, a.mode,
        template_path=Path(a.template) if a.template else None,
        request_json=Path(a.request_json) if a.request_json else None,
        unet=a.unet,
        refmods=refmods, refmod_strength=refmod_strength, retention=retention,
        loras=loras, image=a.image, pose_image=a.pose_image,
        width=eff_w, height=eff_h, steps=a.steps, cfg=a.cfg, seed=a.seed,
        character=char, actor=a.actor, names=a.names,
        dry_run=not a.queue,
    )
    if rep.get("status") != "READY":
        print(f"NOT_READY {rep.get('reason', '')}")
        return 3
    if not a.queue:
        print(f"READY mode={rep['mode']} template={rep['template']} size={rep['size']} refmods={rep['refmods']} loras={[x['name'] for x in rep['loras']]} names={rep['names']}")
        return 0
    q = queue_flux_still(d)
    if q.get("rc") != 0 or not q.get("still"):
        print(f"FAIL rc={q.get('rc')} {q.get('stderr') or q.get('stdout')}")
        return 3
    print(f"DONE still={q['still']} pixl_inbox={q.get('pixl_inbox', 'none')} names={rep['names']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
