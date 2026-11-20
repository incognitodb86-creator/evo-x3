#!/usr/bin/env python3
"""Controlled one-change-per-arm Flux / Miraclein celeb likeness A/B runner for AlienPc.

Decisions (Derrick 2026-11-20 ~9:07 AM CT, M6):
- Default celebs: Sydney Sweeney + Megan Fox (override with --celebs).
- Uses mono's x3/community/scripts/parody/flux_still.py directly (never stale C:\\AI\\community copies).
- Dry-run by default: runs Step 0 disk/node preflight and builds all per-run request.api.json files.
- --run queues one arm at a time locally on AlienPc ComfyUI, checks ComfyUI logs for missing LoRA keys,
  scores faces with InsightFace buffalo_l (CPU, same FACE_PY venv as make_render.py), builds labeled
  contact sheets, and writes RESULT.md in --out-dir (images never go into git).

Usage (from pulled mono clone on AlienPc):
  python alienpc\\community\\scripts\\run_flux_likeness_ab.py --dry-run
  python alienpc\\community\\scripts\\run_flux_likeness_ab.py --run --celebs "Sydney Sweeney,Megan Fox"
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
PARODY_DIR = REPO_ROOT / "x3" / "community" / "scripts" / "parody"
X3_SCRIPTS_DIR = REPO_ROOT / "x3" / "community" / "scripts"
ALIENPC_SCRIPTS_DIR = REPO_ROOT / "alienpc" / "community" / "scripts"

for _p in (str(PARODY_DIR), str(X3_SCRIPTS_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import flux_still as fs  # noqa: E402

DEFAULT_COMFY_ROOT = Path(os.environ.get("COMFY_ROOT") or r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI")
DEFAULT_FACE_PY = Path(os.environ.get("FACE_PY") or str(DEFAULT_COMFY_ROOT / ".venv" / "Scripts" / "python.exe"))
# Live AlienPc queue runner (R6-RESULT / ARM5-RESULT); the mono copy is only a fallback (it may lack local config).
_LIVE_RUN_QUEUE = Path(r"C:\AI\community\scripts\run_queue.py")
DEFAULT_RUN_QUEUE = Path(os.environ.get("RUN_QUEUE_PY") or str(
    _LIVE_RUN_QUEUE if _LIVE_RUN_QUEUE.is_file() else ALIENPC_SCRIPTS_DIR / "run_queue.py"))
DEFAULT_OUT_DIR = Path(os.environ.get("FLUX_AB_OUT") or r"C:\AI\community\runs\flux_likeness_ab_20261120")
MIRACLEIN_FP8_DEFAULT = "Miraclein_4.5_9b_FP8.safetensors"

# Controlled clothed portrait prompt P (no face shape / eye color / hair color words so text never fights RefMod).
PROMPT_BODY = (
    "An adult woman in her late twenties sits relaxed at a wooden cafe table by a tall sunlit window, "
    "weight resting comfortably on her forearms, wearing a plain cream knit sweater. "
    "Natural skin texture and pores, warm afternoon daylight from the left, shallow depth of field. "
    "Medium portrait at eye height, 35mm film, 50mm lens at f/2.0."
)
PROMPT_WITH_ANCHOR = f"{fs.REFMOD_ANCHOR} {PROMPT_BODY}"

ARCFACE_HELPER = r"""
import json, sys, numpy as np, cv2
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640, 640))

def emb(path):
    img = cv2.imread(path)
    if img is None:
        return None
    faces = app.get(img)
    if not faces:
        return None
    f = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    v = f.normed_embedding
    return v / (np.linalg.norm(v) + 1e-12)

refs = [e for e in (emb(p) for p in json.loads(sys.argv[1])) if e is not None]
cands = json.loads(sys.argv[2])
out = {}
if not refs:
    print(json.dumps({"error": "no faces detected in reference photos", "scores": {}}))
    sys.exit(0)
mean_ref = np.mean(refs, axis=0)
mean_ref = mean_ref / (np.linalg.norm(mean_ref) + 1e-12)
for k, p in cands.items():
    e = emb(p)
    out[k] = round(float(np.dot(mean_ref, e)), 4) if e is not None else None
print(json.dumps({"ref_count": len(refs), "scores": out}))
"""


def compact_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "", name).lower()


def preflight_check(comfy_root: Path, celebs: Sequence[str]) -> Dict[str, Any]:
    """Step 0 (0s GPU): inspect installed custom node, UNETs, RefMods, and Prodigy LoRAs."""
    info: Dict[str, Any] = {"comfy_root": str(comfy_root), "comfy_exists": comfy_root.is_dir(), "unets": {}, "celebs": {}}
    node_dir = comfy_root / "custom_nodes" / "ComfyUI-Flux2Klein9Mod"
    if (node_dir / ".git").exists():
        p = subprocess.run(["git", "-C", str(node_dir), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        info["klein9mod_commit"] = p.stdout.strip() or "unknown"
    else:
        info["klein9mod_commit"] = "not-found" if not node_dir.is_dir() else "no-git"

    diff_dir = comfy_root / "models" / "diffusion_models"
    unet_dir = comfy_root / "models" / "unet"
    for fn in (
        "Miraclein_4.5_9b_NVFP4.safetensors",
        "flux-2-klein-9b-fp8.safetensors",
        "FLUX-KLEIN-9B-FP8-NSFW.safetensors",
        "flux-2-klein-9b-kv-fp8.safetensors",
    ):
        found = (diff_dir / fn).is_file() or (unet_dir / fn).is_file()
        info["unets"][fn] = found
    # The FP8 download keeps whatever name Civitai gives it; match by pattern.
    fp8 = sorted(p.name for d in (diff_dir, unet_dir) if d.is_dir()
                 for p in d.glob("*.safetensors") if re.search(r"miraclein.*4\.5.*fp8", p.name, re.I))
    info["miraclein_fp8"] = fp8[0] if fp8 else None
    info["unets"][MIRACLEIN_FP8_DEFAULT] = bool(fp8)

    ref_dir = comfy_root / "models" / "refmods-klein9"
    lora_dir = comfy_root / "models" / "loras" / "klein9"
    for name in celebs:
        c = compact_name(name)
        ref_fn = f"fk9_{c}_v1_refmod.safetensors"
        lora_fn = f"fk9_{c}_v1_prodigy.safetensors"
        info["celebs"][name] = {
            "compact": c,
            "refmod": ref_fn,
            "refmod_present": (ref_dir / ref_fn).is_file(),
            "lora": f"klein9\\{lora_fn}",
            "lora_present": (lora_dir / lora_fn).is_file(),
        }
    return info


def _edit_graph(run_dir: Path, mutator) -> None:
    p = run_dir / "still" / "request.api.json"
    g = json.loads(p.read_text(encoding="utf-8"))
    mutator(g)
    p.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_arms_for_celeb(
    celeb: str,
    out_root: Path,
    seed: int,
    preflight: Dict[str, Any],
    dry_run: bool,
    nsfw_prompt: Optional[str] = None,
) -> List[Dict[str, Any]]:
    c = compact_name(celeb)
    lora_spec = {"name": f"klein9/fk9_{c}_v1_prodigy.safetensors", "strength": 1.0}
    hyb_mod, hyb_lora = fs._hybrid_stack_for_name(celeb)
    arms: List[Dict[str, Any]] = []

    def add(arm_id: str, desc: str, run_dir: Path, rep: Dict[str, Any], skipped: Optional[str] = None) -> None:
        arms.append({
            "arm": arm_id, "celeb": celeb, "desc": desc, "run_dir": str(run_dir),
            "status": "SKIPPED" if skipped else rep.get("status", "ERROR"),
            "skip_reason": skipped,
        })

    # L0: Apples-to-apples old A5 settings with SAME prompt P (hybrid 0.85/0.60, retention 0.7, no anchor, pos-only)
    d0 = out_root / f"{c}_L0_a5_old"
    r0 = fs.build_flux_still(
        d0, PROMPT_BODY, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
        retention="partially_preserved (0.7)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
    )
    if r0.get("status") == "READY":
        def _undo_new(g: Dict[str, Any]) -> None:
            g["5"]["inputs"]["text"] = PROMPT_BODY
            g["17"]["inputs"]["negative"] = ["6", 0]
            g.pop("14", None)
            g.pop("klein9_refmod_apply_neg", None)
        _edit_graph(d0, _undo_new)
        (d0 / "prompt.txt").write_text(PROMPT_BODY + "\n", encoding="utf-8")
    add("L0", "Old A5 settings (hybrid 0.85/0.60, ret 0.7, no anchor, pos-only)", d0, r0)

    # L0-t2i: Plain T2I control with NO RefMod and NO LoRA (proves whether RefMod moves the face at all)
    dt = out_root / f"{c}_L0_t2i_control"
    rt = fs.build_flux_still(dt, PROMPT_BODY, mode="t2i", seed=seed, character=celeb, dry_run=dry_run)
    add("L0-t2i", "Plain T2I control (no RefMod, no LoRA)", dt, rt)

    # L1: New mono default — pure RefMod, retention 1.0, strength 1.0, anchor, pos+neg
    d1 = out_root / f"{c}_L1_refmod_10"
    r1 = fs.build_flux_still(d1, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[celeb], seed=seed, character=celeb, dry_run=dry_run)
    add("L1", "Pure RefMod new default (ret 1.0, str 1.0, anchor, pos+neg, CFG 1.1)", d1, r1)

    # L2: L1 at CFG 1.0 (author's CFG)
    d2 = out_root / f"{c}_L2_refmod_cfg10"
    r2 = fs.build_flux_still(d2, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[celeb], cfg=1.0, seed=seed, character=celeb, dry_run=dry_run)
    add("L2", "Pure RefMod ret 1.0, CFG 1.0", d2, r2)

    # L3: Hybrid author's recipe (RefMod 0.85 + LoRA 0.60, ret 0.7)
    d3 = out_root / f"{c}_L3_hybrid_07"
    r3 = fs.build_flux_still(
        d3, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
        retention="partially_preserved (0.7)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
    )
    add("L3", "Hybrid (RefMod 0.85 + LoRA 0.60, ret 0.7, anchor, pos+neg)", d3, r3)

    # L4: Hybrid at retention 1.0
    d4 = out_root / f"{c}_L4_hybrid_10"
    r4 = fs.build_flux_still(
        d4, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
        retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
    )
    add("L4", "Hybrid (RefMod 0.85 + LoRA 0.60, ret 1.0, anchor, pos+neg)", d4, r4)

    # L5: LoRA only at author's baseline strength 1.0
    d5 = out_root / f"{c}_L5_lora_only_10"
    r5 = fs.build_flux_still(d5, PROMPT_BODY, mode="t2i", loras=[lora_spec], seed=seed, character=celeb, dry_run=dry_run)
    add("L5", "LoRA only @ 1.0 (Miraclein NVFP4)", d5, r5)

    # L6: Non-KV Klein FP8 base (stock flux-2-klein-9b-fp8 if present, else existing FLUX-KLEIN-9B-FP8-NSFW; never bare kv-fp8)
    unets = preflight.get("unets") or {}
    l6_unet = (
        "flux-2-klein-9b-fp8.safetensors" if unets.get("flux-2-klein-9b-fp8.safetensors")
        else ("FLUX-KLEIN-9B-FP8-NSFW.safetensors" if unets.get("FLUX-KLEIN-9B-FP8-NSFW.safetensors") else None)
    )
    d6 = out_root / f"{c}_L6_klein_fp8"
    if l6_unet or dry_run:
        chosen = l6_unet or "FLUX-KLEIN-9B-FP8-NSFW.safetensors"
        r6 = fs.build_flux_still(
            d6, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[celeb], cfg=1.0, steps=8,
            seed=seed, character=celeb, dry_run=dry_run,
        )
        if r6.get("status") == "READY":
            def _set_l6(g: Dict[str, Any]) -> None:
                g["1"]["inputs"]["unet_name"] = chosen
                g["18"]["inputs"]["sampler_name"] = "er_sde"
            _edit_graph(d6, _set_l6)
        add("L6", f"Pure RefMod ret 1.0 on non-KV FP8 ({chosen}, 8 steps er_sde CFG 1.0)", d6, r6,
            skipped=None if (l6_unet or dry_run) else "no non-KV Klein FP8 UNET on disk")
    else:
        add("L6", "Non-KV Klein FP8 base", d6, {}, skipped="no non-KV Klein FP8 UNET on disk")

    # L7: Miraclein 4.5 FP8 (D6c approved 8.87 GB download) — tests whether NVFP4 LoRA/RefMod approx hurts likeness
    d7 = out_root / f"{c}_L7_miraclein_fp8_hybrid"
    fp8_name = preflight.get("miraclein_fp8") or MIRACLEIN_FP8_DEFAULT
    has_m_fp8 = bool(preflight.get("miraclein_fp8"))
    if has_m_fp8 or dry_run:
        r7 = fs.build_flux_still(
            d7, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
            retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
        )
        if r7.get("status") == "READY":
            _edit_graph(d7, lambda g: g["1"]["inputs"].__setitem__("unet_name", fp8_name))
        add("L7", f"Hybrid ret 1.0 on {fp8_name}", d7, r7,
            skipped=None if (has_m_fp8 or dry_run) else "Miraclein_4.5_9b_FP8.safetensors not downloaded yet (D6c)")
    else:
        add("L7", "Miraclein 4.5 FP8", d7, {}, skipped="Miraclein_4.5_9b_FP8.safetensors not downloaded yet (D6c)")

    # L8: Optional adult/NSFW prompt check (only if --nsfw-prompt-file supplied)
    if nsfw_prompt:
        d8 = out_root / f"{c}_L8_nsfw_check"
        r8 = fs.build_flux_still(
            d8, nsfw_prompt, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
            retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
        )
        add("L8", "NSFW prompt check (hybrid ret 1.0)", d8, r8)

    return arms


def scan_comfy_log(log_path: Optional[Path], offset: int) -> Tuple[int, List[str]]:
    if not log_path or not log_path.is_file():
        return offset, []
    data = log_path.read_bytes()
    chunk = data[offset:].decode("utf-8", errors="replace")
    hits = [
        ln.strip() for ln in chunk.splitlines()
        if any(k in ln.lower() for k in ("lora key not loaded", "klein9refmod", "value_not_in_list", "error", "warning"))
    ]
    return len(data), hits[:12]


def score_arcface(face_py: Path, ref_photos: Sequence[Path], cand_pngs: Dict[str, Path]) -> Dict[str, Optional[float]]:
    if not face_py.is_file() or not ref_photos or not cand_pngs:
        return {}
    proc = subprocess.run(
        [str(face_py), "-c", ARCFACE_HELPER,
         json.dumps([str(p) for p in ref_photos]),
         json.dumps({k: str(v) for k, v in cand_pngs.items()})],
        capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        return {}
    try:
        return json.loads(proc.stdout.strip()).get("scores") or {}
    except Exception:
        return {}


def make_contact_sheet(title: str, items: Sequence[Tuple[str, Path]], out_png: Path) -> Optional[Path]:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    valid = [(lbl, p) for lbl, p in items if p.is_file()]
    if not valid:
        return None
    tw, th, pad, hdr = 384, 672, 16, 44
    cols = min(4, len(valid))
    rows = (len(valid) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + hdr + pad) + pad + 36), (22, 22, 26))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), title, fill=(240, 240, 240))
    for i, (lbl, p) in enumerate(valid):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = 36 + pad + r * (th + hdr + pad)
        im = Image.open(p).convert("RGB").resize((tw, th))
        sheet.paste(im, (x, y + hdr))
        draw.text((x, y + 6), lbl[:52], fill=(255, 220, 120))
    sheet.save(out_png)
    return out_png


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Flux / Miraclein celeb likeness A/B runner (dry-run by default).")
    ap.add_argument("--dry-run", action="store_true", help="Build graphs + run preflight only (default)")
    ap.add_argument("--run", action="store_true", help="Execute arms locally on AlienPc ComfyUI")
    ap.add_argument("--celebs", default="Sydney Sweeney,Megan Fox", help="Comma-separated celeb names")
    ap.add_argument("--seed", type=int, default=51083601)
    ap.add_argument("--comfy-root", default=str(DEFAULT_COMFY_ROOT))
    ap.add_argument("--run-queue", default=str(DEFAULT_RUN_QUEUE))
    ap.add_argument("--face-py", default=str(DEFAULT_FACE_PY))
    ap.add_argument("--ref-dir", default="", help="Optional folder with <compact_name>/*.{png,jpg,webp} reference photos")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--comfy-log", default="", help="Optional ComfyUI console log file to scan for missing LoRA keys")
    ap.add_argument("--nsfw-prompt-file", default="", help="Optional path to an adult/NSFW prompt file for arm L8")
    ap.add_argument("--lease-file", default=os.environ.get("ALIENPC_LEASE_FILE", ""), help="Optional lease file path")
    a = ap.parse_args(argv)

    dry_run = not a.run
    celebs = [s.strip() for s in a.celebs.split(",") if s.strip()]
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    nsfw_prompt = Path(a.nsfw_prompt_file).read_text(encoding="utf-8").strip() if a.nsfw_prompt_file else None

    pre = preflight_check(Path(a.comfy_root), celebs)
    (out_dir / "preflight.json").write_text(json.dumps(pre, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT comfy_exists={pre['comfy_exists']} klein9mod={pre['klein9mod_commit']}")
    for fn, ok in pre["unets"].items():
        print(f"  UNET {fn}: {'PRESENT' if ok else 'missing'}")
    for nm, ci in pre["celebs"].items():
        print(f"  CELEB {nm}: refmod={ci['refmod_present']} lora={ci['lora_present']}")

    all_arms: List[Dict[str, Any]] = []
    for celeb in celebs:
        all_arms.extend(build_arms_for_celeb(celeb, out_dir, a.seed, pre, dry_run=dry_run, nsfw_prompt=nsfw_prompt))

    if dry_run:
        print(f"\nDRY_RUN built {len(all_arms)} arms under {out_dir}:")
        for x in all_arms:
            print(f"  [{x['celeb']}] {x['arm']:6s} | {x['status']:7s} | {x['desc']}")
        print("\nRe-run with --run on AlienPc after verifying preflight.")
        return 0

    lease_path = Path(a.lease_file) if a.lease_file else None
    lease_held = False
    try:
        if lease_path:
            if lease_path.is_file() and lease_path.read_text(encoding="utf-8").strip():
                print(f"BLOCKED: lease file not empty: {lease_path}", file=sys.stderr)
                return 2
            lease_path.parent.mkdir(parents=True, exist_ok=True)
            lease_path.write_text(f"derek | FLUX-LIKENESS-20261120 | {datetime.now().isoformat(timespec='seconds')}\n", encoding="utf-8")
            lease_held = True

        comfy_log = Path(a.comfy_log) if a.comfy_log else None
        log_off = comfy_log.stat().st_size if (comfy_log and comfy_log.is_file()) else 0
        rq = Path(a.run_queue)
        if not rq.is_file():
            print(f"FAIL: run_queue.py not found at {rq}", file=sys.stderr)
            return 2

        # Never queue a graph whose RefMod or LoRA file is missing; it would only fail value_not_in_list.
        needs = {"L0": "both", "L1": "refmod", "L2": "refmod", "L3": "both", "L4": "both",
                 "L5": "lora", "L6": "refmod", "L7": "both", "L8": "both"}
        for arm in all_arms:
            ci = pre["celebs"].get(arm["celeb"]) or {}
            need = needs.get(arm["arm"])
            missing = [k for k in ("refmod", "lora") if need in (k, "both") and not ci.get(f"{k}_present")]
            if arm["status"] == "READY" and missing:
                arm["status"] = "SKIPPED"
                arm["skip_reason"] = f"missing {'/'.join(missing)} file on AlienPc"

        for arm in all_arms:
            if arm["status"] != "READY":
                continue
            rdir = Path(arm["run_dir"])
            t0 = time.monotonic()
            cmd = [sys.executable, str(rq), "--run-dir", str(rdir), "--no-upscale"]
            proc = subprocess.run(cmd, cwd=str(rq.parent.parent), capture_output=True, text=True, timeout=600)
            arm["wall_s"] = round(time.monotonic() - t0, 1)
            arm["rc"] = proc.returncode
            png = rdir / "still" / "still.png"
            if not png.is_file():
                pngs = sorted((rdir / "still").glob("*.png"))
                png = pngs[0] if pngs else png
            arm["png"] = str(png) if png.is_file() else ""
            log_off, hits = scan_comfy_log(comfy_log, log_off)
            arm["log_hits"] = hits
            print(f"[{arm['celeb']}] {arm['arm']:6s} rc={proc.returncode} wall={arm['wall_s']}s png={bool(arm['png'])} log_hits={len(hits)}")

        # Score with ArcFace + build contact sheets
        ref_root = Path(a.ref_dir) if a.ref_dir else None
        sheets: List[str] = []
        for celeb in celebs:
            c = compact_name(celeb)
            c_arms = [x for x in all_arms if x["celeb"] == celeb]
            cands = {x["arm"]: Path(x["png"]) for x in c_arms if x.get("png")}
            refs = sorted((ref_root / c).glob("*.*")) if (ref_root and (ref_root / c).is_dir()) else []
            refs = [p for p in refs if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
            scores = score_arcface(Path(a.face_py), refs, cands)
            for x in c_arms:
                x["arcface"] = scores.get(x["arm"])
            sheet_items = [
                (f"{x['arm']} af={x.get('arcface') if x.get('arcface') is not None else 'n/a'} {x.get('wall_s', '')}s",
                 Path(x["png"]))
                for x in c_arms if x.get("png")
            ]
            sp = make_contact_sheet(f"Flux likeness A/B - {celeb} (seed {a.seed})", sheet_items, out_dir / f"contact_{c}.png")
            if sp:
                sheets.append(str(sp))

        # Write RESULT.md in out_dir (images stay on AlienPc/QNAP, never in git)
        lines = [
            "# FLUX-LIKENESS-20261120 RESULT",
            "",
            f"- **Seed:** `{a.seed}` | **ComfyUI-Flux2Klein9Mod:** `{pre['klein9mod_commit']}`",
            f"- **Contact sheets:** {', '.join(f'`{s}`' for s in sheets) or 'none'}",
            "",
            "| Celeb | Arm | Description | rc | Wall (s) | ArcFace | Log hits | PNG |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
        for x in all_arms:
            af = f"{x['arcface']:.4f}" if isinstance(x.get("arcface"), float) else "n/a"
            lines.append(
                f"| {x['celeb']} | {x['arm']} | {x['desc']} | {x.get('rc', x['status'])} | "
                f"{x.get('wall_s', '-')} | {af} | {len(x.get('log_hits') or [])} | `{x.get('png') or x.get('skip_reason') or ''}` |"
            )
        res_md = out_dir / "RESULT.md"
        res_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nDONE: wrote {res_md}")
        return 0
    finally:
        if lease_held and lease_path:
            lease_path.write_text("", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
