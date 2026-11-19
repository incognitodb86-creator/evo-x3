"""Fill a saved ComfyUI API template with per-clip values."""
from __future__ import annotations

import argparse, copy, json, os, sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

PARODY_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PARODY_DIR.parent
TEMPLATES_DIR = SCRIPTS_DIR.parent / "templates"
for _p in (str(SCRIPTS_DIR), str(PARODY_DIR)):
    if _p not in sys.path: sys.path.insert(0, _p)

import build_request as br
import resolve as res

TEMPLATES = {k: TEMPLATES_DIR / f"{k}.api.json" for k in (
    "plain", "oc_guide", "oc_ref", "named_parody", "talk", "two_person", "long_continuation", "ref2va_16x9"
)}


def pick_template(has_still: bool, still_mode: str = "guide", has_identity: bool = False,
                  character: Optional[str] = None, partner2_still: Optional[str] = None,
                  position: str = "", width: int = 768, height: int = 1344) -> str:
    if partner2_still: return "two_person"
    mode = br.normalize_still_mode(still_mode)
    if (width, height) == (1344, 768) and not has_identity and mode == "ref": return "oc_ref"
    pos = (position or "").strip().lower()
    if has_identity:
        if not has_still: return "named_parody"
        if mode == "ref": return "oc_ref"
        return "talk" if pos == "talk" and not (character and str(character).upper().startswith("FC")) else "oc_guide"
    if mode == "ref" and has_still: return "oc_ref"
    return "talk" if pos == "talk" else "plain"


PIXL_LIBRARIES = Path("/home/evo/AI/5slock/libraries")


def pixl_abs(still):
    """A PixlStash API file_path is relative to 5slock/libraries; turn it into a full path when that file exists."""
    if isinstance(still, str) and still.strip() and not Path(still.strip()).is_absolute() and not Path(still.strip()).is_file():
        p = PIXL_LIBRARIES / still.strip()
        if p.is_file(): return str(p)
    return still


def _stage_still(still: Optional[str]) -> Optional[str]:
    if not (isinstance(still, str) and still.strip()): return None
    s, comfy_in = still.strip(), br.COMFY_INPUT_COMMUNITY.parent
    low = s.replace("\\", "/").lower()
    if "stills/comfy_input/" in low:
        rel = s.replace("\\", "/")[low.find("stills/comfy_input/") + len("stills/comfy_input/"):].lstrip("/")
        if rel and (comfy_in / rel).is_file(): return rel
    if (p := Path(s)).is_file():
        try:
            return p.resolve().relative_to(comfy_in.resolve()).as_posix()
        except ValueError:
            return (br.stage_reference_images([str(p)]) or [s])[0]
    return s


REALISM_LORA_DEFAULT = {
    "name": "h3-realism-people-t2v-i2v-r2v.safetensors",
    "strength": 0.7,
    "trigger": "r34l1sm",
}


# ComfyUI lists subfolder LoRAs with the separator of the OS it runs on. Renders run on AlienPc (Windows), so
# `klein9/x.safetensors` fails validation (value_not_in_list) unless written `klein9\x.safetensors`
# (OPUS-FINDINGS-20261119 #4). Set EVO_COMFY_PATH_SEP=/ only for a ComfyUI on Linux.
def comfy_lora_name(name: str) -> str:
    sep = os.environ.get("EVO_COMFY_PATH_SEP") or "\\"
    s = str(name or "").strip()
    return s.replace("/" if sep == "\\" else "\\", sep)


def parse_lora_spec(spec: str) -> Dict[str, Any]:
    """Parse `<lora_file>[:<strength>[:<trigger>]]` into a normalized LoRA dict."""
    parts = [p.strip() for p in str(spec or "").split(":")]
    name = parts[0]
    if not name:
        raise ValueError(f"empty lora spec: {spec!r}")
    strength = float(parts[1]) if len(parts) > 1 and parts[1] else 0.7
    trigger = parts[2] if len(parts) > 2 and parts[2] else ""
    if not trigger and "h3-realism-people" in name.lower():
        trigger = "r34l1sm"
    return {"name": name, "strength": strength, "trigger": trigger}


def _prepend_lora_triggers(prompt: str, loras: Sequence[Dict[str, Any]]) -> str:
    """Prepend active LoRA trigger word(s) to detailed_description (or prompt start) ONLY when loaded (R31)."""
    import re
    triggers = []
    for lr in loras:
        t = str(lr.get("trigger") or "").strip()
        if t and float(lr.get("strength", 0.0) or 0.0) > 0:
            if not re.search(rf"(?i)\b{re.escape(t)}\b", prompt) and t not in triggers:
                triggers.append(t)
    if not triggers:
        return prompt
    lead = ", ".join(triggers)
    m = re.search(r"(?im)^(detailed_description\s*:\s*)", prompt)
    if m:
        after = prompt[m.end():]
        sep = " " if after and not after.startswith(("\n", " ")) else ""
        return prompt[:m.end()] + f"{lead}, " + sep + after.lstrip(" ")
    return f"{lead}, {prompt}"


def _inject_h3_loras(graph: Dict[str, Any], loras: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Chain LoraLoaderModelOnly node(s) between `unet` and any node consuming `["unet", 0]`."""
    active = [
        {"name": comfy_lora_name(lr["name"]), "strength": float(lr.get("strength", 0.7)), "trigger": str(lr.get("trigger") or "").strip()}
        for lr in loras if str(lr.get("name") or "").strip() and float(lr.get("strength", 0.7)) > 0
    ]
    if not active or "unet" not in graph:
        return []
    prev_ref: List[Any] = ["unet", 0]
    for idx, lr in enumerate(active, start=1):
        nid = f"lora_{idx}"
        while nid in graph:
            nid += "_x"
        graph[nid] = {
            "_meta": {"title": f"H3 LoRA {idx}: {lr['name']}"},
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "lora_name": lr["name"],
                "model": prev_ref,
                "strength_model": lr["strength"],
            },
        }
        prev_ref = [nid, 0]
    # Rewire every existing consumer of ["unet", 0] (except the newly added lora_1) to the last LoRA node.
    first_lora_id = next(k for k, v in graph.items() if isinstance(v, dict) and v.get("class_type") == "LoraLoaderModelOnly" and v.get("inputs", {}).get("model") == ["unet", 0])
    for nid, node in graph.items():
        if nid == first_lora_id or not isinstance(node, dict):
            continue
        inp = node.get("inputs")
        if not isinstance(inp, dict):
            continue
        for k, v in list(inp.items()):
            if v == ["unet", 0]:
                inp[k] = list(prev_ref)
    return active


def fill_request(
    prompt_text: str, run_dir: Path, ask: str = "", position: str = "", still_image: Optional[str] = None,
    partner2_still: Optional[str] = None, character: Optional[str] = None, names: Optional[Sequence[str]] = None,
    refmod_stems: Optional[Sequence[str]] = None, template_name: Optional[str] = None, still_mode: str = "guide",
    width: int = 768, height: int = 1344, frames: Optional[int] = None, seed: int = 51083601,
    continuation_prompt: Optional[str] = None, dry_run: bool = True,
    loras: Optional[Sequence[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    run_dir = Path(run_dir); run_dir.mkdir(parents=True, exist_ok=True)
    still_image, partner2_still = pixl_abs(still_image), pixl_abs(partner2_still)
    rep: Dict[str, Any] = {"hook": "fill_request", "ask": ask, "position": position, "seed": seed, "frames": frames, "status": "NOT_READY", "submitted": False}

    def _fail(reason: str) -> Dict[str, Any]:
        rep.update(status="NOT_READY", reason=reason)
        (run_dir / "clip_NOT_READY.txt").write_text(f"NOT_READY: {reason}\n", encoding="utf-8")
        (run_dir / "build_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8"); return dict(rep, run_dir=str(run_dir))

    raw = (prompt_text or "").strip()
    if not raw: return _fail("empty writer output")
    if (m := br._REFUSAL_RE.search(br._D_RE.sub("", raw))): return _fail(f"refusal phrase: {m.group(0)!r}")
    try:
        br._check_writer_18plus(raw, {"ask": ask})
    except br.WriterNotReady as e:
        return _fail(str(e).removeprefix("NOT_READY: "))

    stems, id_info = list(refmod_stems or []), {}
    still_detected = res.detect_still_identity(still_image) if (refmod_stems is None and still_image and not (character or names)) else {}
    auto_names = list(still_detected.get("names") or [])
    if refmod_stems is None and (character or names or auto_names or (still_image and res.oc_keys_for_still_and_names(still_image))):
        picked = res.resolve_writer_refmods(
            still_image=still_image,
            character=character or still_detected.get("character"),
            names=(list(names) if names else (auto_names or None)),
        )
        if (character or names) and picked.get("reason") and not picked.get("stems"):
            return _fail(picked["reason"])
        stems = list(picked.get("stems") or [])
        id_info = {k: picked.get(k) for k in ("source", "index", "trigger")}
        if still_detected.get("source") and not (character or names):
            id_info["still_detected_source"] = still_detected["source"]
            id_info["still_detected_names"] = auto_names

    mode = br.normalize_still_mode(still_mode)
    tname = template_name or pick_template(bool(still_image), mode, bool(character or names or stems), character, partner2_still, position, width, height)
    tpath = TEMPLATES.get(tname)
    if not tpath or not tpath.is_file(): return _fail(f"unknown or missing template: {tname!r}")

    g = copy.deepcopy(json.loads(tpath.read_text(encoding="utf-8")))
    applied_loras = _inject_h3_loras(g, loras or [])
    final_prompt = f"{br.REF_MODE_PICTURE1_LEAD}\n\n{raw}" if (mode == "ref" and "ref_images.ref_image_1" in (g.get("c0") or {}).get("inputs", {}) and not raw.startswith(br.REF_MODE_PICTURE1_LEAD)) else raw
    if applied_loras:
        final_prompt = _prepend_lora_triggers(final_prompt, applied_loras)
    (run_dir / "prompt.txt").write_text(final_prompt + "\n", encoding="utf-8")

    c0_in = g["c0"]["inputs"]
    c0_in.update(prompt=final_prompt, width=int(width), height=int(height))
    if isinstance(c0_in.get("length"), int) and frames is not None and "win1" not in g:
        try:
            c0_in["length"] = int(br.align_h3_frames(int(frames)))
        except ValueError as e:
            return _fail(str(e))
    if "c1" in g: g["c1"]["inputs"].update(prompt=(continuation_prompt or final_prompt).strip(), width=int(width), height=int(height))
    if (s_rel := _stage_still(still_image)):
        for nid in ("img_1", "img"):
            if nid in g: g[nid]["inputs"]["image"] = s_rel; break
    if (p2_rel := _stage_still(partner2_still)) and "img2" in g: g["img2"]["inputs"]["image"] = p2_rel
    warnings: List[str] = []
    if "refmods" in g:
        if len(stems) > 8:
            warnings.append(f"refmod_slots_truncated:{len(stems)}->8")
        for i in range(1, 9): g["refmods"]["inputs"][f"mod_{i}"] = res._mod_stem(stems[i - 1]) if i <= len(stems) else "(none)"
    if "noise" in g: g["noise"]["inputs"]["noise_seed"] = int(seed)
    if "save" in g: g["save"]["inputs"]["filename_prefix"] = f"community/{run_dir.name}/clip"

    (run_dir / "clip").mkdir(parents=True, exist_ok=True)
    (run_dir / "clip" / "request.api.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if (nr := run_dir / "clip_NOT_READY.txt").exists(): nr.unlink()
    total_frames = (int(c0_in["length"]) + int(g["win1"]["inputs"].get("extension_frames") or 0)) if "win1" in g else (int(c0_in["length"]) if isinstance(c0_in.get("length"), int) else int(frames or 243))
    rep.update(status="READY", template=tname, template_path=str(tpath), still_mode=mode, canvas=[int(width), int(height)],
               frames=total_frames, refmods={"stems": stems[:8], **id_info}, loras=applied_loras, build={"total_frames": total_frames})
    if warnings:
        rep["warnings"] = warnings
    marker, order_file = run_dir / "DRY_RUN", run_dir / "_render_order.json"
    if dry_run:
        if order_file.exists(): order_file.unlink()
        marker.write_text("dry run of fill_request: built for review only, never queue this dir\n", encoding="utf-8")
        rep["dry_run"] = True
    else:
        if marker.exists(): marker.unlink()
        order_file.write_text(json.dumps({"order": [{"pos": 1, "tag": "clip", "arm": "oc_writer", "scene": position, "seed": seed}]}, indent=2), encoding="utf-8")
    (run_dir / "build_report.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return dict(rep, run_dir=str(run_dir), prompt_path=str(run_dir / "prompt.txt"))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Fill a saved ComfyUI template from writer_output.txt.")
    for f in ("run_dir", "--ask", "--position", "--still", "--partner2-still", "--character", "--template", "--aspect", "--size"):
        ap.add_argument(f, default="" if f in ("--ask", "--position") else None)
    ap.add_argument("--names", nargs="+", default=None); ap.add_argument("--still-mode", default="guide", choices=list(br.STILL_MODES))
    ap.add_argument("--frames", type=int, default=None); ap.add_argument("--seed", type=int, default=51083601); ap.add_argument("--queue", action="store_true")
    ap.add_argument("--lora", action="append", default=[], help="H3 LoRA spec: <filename>[:<strength>[:<trigger>]] (repeatable)")
    ap.add_argument("--realism-lora", nargs="?", const=str(REALISM_LORA_DEFAULT["strength"]), default=None,
                    help="Attach MiniMax-H3-Realism-People-LoRA (optional strength, default 0.7; injects r34l1sm trigger)")
    a = ap.parse_args(argv); d = Path(a.run_dir)
    if not d.is_absolute() or not (d / "writer_output.txt").is_file():
        print("NOT_READY run_dir must be absolute and contain writer_output.txt"); return 3
    lora_list = [parse_lora_spec(s) for s in (a.lora or [])]
    if a.realism_lora is not None:
        lora_list.append({**REALISM_LORA_DEFAULT, "strength": float(a.realism_lora)})
    w, h = br.resolve_canvas(a.aspect, a.size, still_size=br.read_still_size(a.still) if a.still else None)
    r = fill_request((d / "writer_output.txt").read_text(encoding="utf-8"), d, ask=a.ask, position=a.position, still_image=a.still,
                     partner2_still=a.partner2_still, character=a.character, names=a.names, template_name=a.template,
                     still_mode=a.still_mode, width=w, height=h, frames=a.frames, seed=a.seed, dry_run=not a.queue,
                     loras=(lora_list or None))
    print(r.get("status"), r.get("template", ""), r.get("reason", ""))
    return 0 if r.get("status") == "READY" else 3


if __name__ == "__main__":
    sys.exit(main())
