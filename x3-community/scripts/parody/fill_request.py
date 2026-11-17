"""Fill a saved ComfyUI API template with per-clip values."""
from __future__ import annotations

import argparse, copy, json, sys
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
    if (width, height) == (1344, 768) and not has_identity: return "ref2va_16x9"
    pos = (position or "").strip().lower()
    if has_identity:
        if not has_still: return "named_parody"
        if br.normalize_still_mode(still_mode) == "ref": return "oc_ref"
        return "talk" if pos == "talk" and not (character and str(character).upper().startswith("FC")) else "oc_guide"
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


def fill_request(
    prompt_text: str, run_dir: Path, ask: str = "", position: str = "", still_image: Optional[str] = None,
    partner2_still: Optional[str] = None, character: Optional[str] = None, names: Optional[Sequence[str]] = None,
    refmod_stems: Optional[Sequence[str]] = None, template_name: Optional[str] = None, still_mode: str = "guide",
    width: int = 768, height: int = 1344, frames: Optional[int] = None, seed: int = 51083601,
    continuation_prompt: Optional[str] = None, dry_run: bool = True,
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
    if refmod_stems is None and (character or names or (still_image and res.oc_keys_for_still_and_names(still_image))):
        picked = res.resolve_writer_refmods(still_image=still_image, character=character, names=names)
        if (character or names) and picked.get("reason") and not picked.get("stems"):
            return _fail(picked["reason"])
        stems = list(picked.get("stems") or [])
        id_info = {k: picked.get(k) for k in ("source", "index", "trigger")}

    mode = br.normalize_still_mode(still_mode)
    tname = template_name or pick_template(bool(still_image), mode, bool(character or names or stems), character, partner2_still, position, width, height)
    tpath = TEMPLATES.get(tname)
    if not tpath or not tpath.is_file(): return _fail(f"unknown or missing template: {tname!r}")

    g = copy.deepcopy(json.loads(tpath.read_text(encoding="utf-8")))
    final_prompt = f"{br.REF_MODE_PICTURE1_LEAD}\n\n{raw}" if (mode == "ref" and "ref_images.ref_image_1" in (g.get("c0") or {}).get("inputs", {}) and not raw.startswith(br.REF_MODE_PICTURE1_LEAD)) else raw
    (run_dir / "prompt.txt").write_text(final_prompt + "\n", encoding="utf-8")

    c0_in = g["c0"]["inputs"]
    c0_in.update(prompt=final_prompt, width=int(width), height=int(height))
    if isinstance(c0_in.get("length"), int) and frames is not None and "win1" not in g:
        c0_in["length"] = int(br.align_h3_frames(int(frames)))
    if "c1" in g: g["c1"]["inputs"].update(prompt=(continuation_prompt or final_prompt).strip(), width=int(width), height=int(height))
    if (s_rel := _stage_still(still_image)):
        for nid in ("img_1", "img"):
            if nid in g: g[nid]["inputs"]["image"] = s_rel; break
    if (p2_rel := _stage_still(partner2_still)) and "img2" in g: g["img2"]["inputs"]["image"] = p2_rel
    if "refmods" in g:
        for i in range(1, 9): g["refmods"]["inputs"][f"mod_{i}"] = res._mod_stem(stems[i - 1]) if i <= len(stems) else "(none)"
    if "noise" in g: g["noise"]["inputs"]["noise_seed"] = int(seed)
    if "save" in g: g["save"]["inputs"]["filename_prefix"] = f"community/{run_dir.name}/clip"

    (run_dir / "clip").mkdir(parents=True, exist_ok=True)
    (run_dir / "clip" / "request.api.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if (nr := run_dir / "clip_NOT_READY.txt").exists(): nr.unlink()
    total_frames = (int(c0_in["length"]) + int(g["win1"]["inputs"].get("extension_frames") or 0)) if "win1" in g else (int(c0_in["length"]) if isinstance(c0_in.get("length"), int) else int(frames or 243))
    rep.update(status="READY", template=tname, template_path=str(tpath), still_mode=mode, canvas=[int(width), int(height)],
               frames=total_frames, refmods={"stems": stems, **id_info}, build={"total_frames": total_frames})
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
    a = ap.parse_args(argv); d = Path(a.run_dir)
    if not d.is_absolute() or not (d / "writer_output.txt").is_file():
        print("NOT_READY run_dir must be absolute and contain writer_output.txt"); return 3
    w, h = br.resolve_canvas(a.aspect, a.size, still_size=br.read_still_size(a.still) if a.still else None)
    r = fill_request((d / "writer_output.txt").read_text(encoding="utf-8"), d, ask=a.ask, position=a.position, still_image=a.still,
                     partner2_still=a.partner2_still, character=a.character, names=a.names, template_name=a.template,
                     still_mode=a.still_mode, width=w, height=h, frames=a.frames, seed=a.seed, dry_run=not a.queue)
    print(r.get("status"), r.get("template", ""), r.get("reason", ""))
    return 0 if r.get("status") == "READY" else 3


if __name__ == "__main__":
    sys.exit(main())
