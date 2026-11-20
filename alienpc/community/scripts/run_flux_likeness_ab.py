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
DEFAULT_REF_DIR = Path(os.environ.get("FLUX_AB_REFS") or r"C:\AI\refs_ab_celeb")
MIRACLEIN_FP8_DEFAULT = "Miraclein_4.5_9b_FP8.safetensors"

# Controlled clothed portrait scene P (no trigger words or adult prose in git).
PROMPT_BODY = (
    "An adult woman in her late twenties sits relaxed at a wooden cafe table by a tall sunlit window, "
    "weight resting comfortably on her forearms, wearing a plain cream knit sweater. "
    "Natural skin texture and pores, warm afternoon daylight from the left, shallow depth of field. "
    "Medium portrait at eye height, 35mm film, 50mm lens at f/2.0."
)
PROMPT_WITH_ANCHOR = f"{fs.REFMOD_ANCHOR} {PROMPT_BODY}"
# Runtime placeholder template (triggers & custom likeness cues are loaded from a non-git --prompts-json file).
L7_PROMPT_TEMPLATE = (
    "The reference images represent one adult person, {NAME}{TRIGGER_CLAUSE}; "
    "keep the face and hair unchanged and exact as in the reference images. "
    "{LIKENESS_CLAUSE}{SCENE}"
)

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
    print(json.dumps({"error": "no faces detected in reference photos", "ref_count": 0, "intra_gallery": None, "scores": {}}))
    sys.exit(0)

intra_pairs = [float(np.dot(refs[i], refs[j])) for i in range(len(refs)) for j in range(i + 1, len(refs))]
intra_gallery = (
    {
        "pairs": len(intra_pairs),
        "mean": round(float(np.mean(intra_pairs)), 4),
        "min": round(float(np.min(intra_pairs)), 4),
        "max": round(float(np.max(intra_pairs)), 4),
    }
    if intra_pairs else None
)

mean_ref = np.mean(refs, axis=0)
mean_ref = mean_ref / (np.linalg.norm(mean_ref) + 1e-12)
for k, p in cands.items():
    e = emb(p)
    if e is None:
        out[k] = None
    else:
        sims = [float(np.dot(r, e)) for r in refs]
        out[k] = {
            "centroid": round(float(np.dot(mean_ref, e)), 4),
            "mean": round(float(np.mean(sims)), 4),
            "max": round(float(np.max(sims)), 4),
            "min": round(float(np.min(sims)), 4),
        }
print(json.dumps({"ref_count": len(refs), "intra_gallery": intra_gallery, "scores": out}))
"""


def compact_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "", name).lower()


def is_valid_image_file(path: Path) -> bool:
    """Verify real PNG/JPEG/WEBP magic bytes (skips HTML error pages saved with a .png extension)."""
    try:
        with path.open("rb") as fh:
            hdr = fh.read(12)
    except OSError:
        return False
    if len(hdr) < 4:
        return False
    if hdr.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if hdr.startswith(b"\xff\xd8\xff"):
        return True
    if len(hdr) >= 12 and hdr[:4] == b"RIFF" and hdr[8:12] == b"WEBP":
        return True
    return False


def collect_valid_refs(ref_root: Optional[Path], compact_celeb: str) -> Tuple[List[Path], List[Path], Optional[str]]:
    """Return (valid_image_paths, skipped_non_images, warning). Refuses poisoned `refs_ab` folder."""
    if not ref_root:
        return [], [], None
    # Guard against scoring from C:\AI\refs_ab (which contained HTML pages named .png).
    parts_lower = [p.lower() for p in ref_root.parts]
    if "refs_ab" in parts_lower and "refs_ab_celeb" not in parts_lower:
        return [], [], f"refusing poisoned refs_ab path ({ref_root}); use C:\\AI\\refs_ab_celeb"
    sub = ref_root / compact_celeb
    if not sub.is_dir():
        return [], [], None
    valid: List[Path] = []
    skipped: List[Path] = []
    for p in sorted(sub.glob("*.*")):
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        if is_valid_image_file(p):
            valid.append(p)
        else:
            skipped.append(p)
    return valid, skipped, None


def parse_last_json_line(stdout: str) -> Dict[str, Any]:
    """Parse the last JSON object line from stdout (InsightFace logs banner lines before our JSON)."""
    for line in reversed((stdout or "").splitlines()):
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return {}


def load_prompts_config(prompts_json: Optional[Path]) -> Dict[str, Dict[str, str]]:
    """Load optional runtime per-celeb {trigger, name, likeness_desc, scene} from a local non-git JSON file."""
    if not prompts_json or not prompts_json.is_file():
        return {}
    raw = json.loads(prompts_json.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, Dict[str, str]] = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            out[compact_name(k)] = {str(sk): str(sv) for sk, sv in v.items() if sv is not None}
    return out


def render_l7_prompt(celeb: str, prompts_cfg: Optional[Dict[str, Dict[str, str]]] = None) -> str:
    """Fill L7 prompt placeholders at runtime so triggers never live in git and celeb prompts are distinct."""
    entry = (prompts_cfg or {}).get(compact_name(celeb), {})
    name = (entry.get("name") or celeb).strip()
    trigger = (entry.get("trigger") or "").strip()
    likeness = (entry.get("likeness_desc") or "").strip()
    scene = (entry.get("scene") or PROMPT_BODY).strip()
    trigger_clause = f" ({trigger})" if trigger else ""
    likeness_clause = f"{likeness} " if likeness else ""
    return L7_PROMPT_TEMPLATE.format(
        NAME=name,
        TRIGGER_CLAUSE=trigger_clause,
        LIKENESS_CLAUSE=likeness_clause,
        SCENE=scene,
    ).strip()


def _ensure_zero_out_negative(g: Dict[str, Any]) -> None:
    """Wire ConditioningZeroOut on the negative path (pos CLIPTextEncode -> node 6 -> neg Klein9RefModApply)."""
    pos_id = fs._find_node(g, "CLIPTextEncode", "positive") or fs._find_node(g, "CLIPTextEncode") or "5"
    g["6"] = {
        "_meta": {"title": "negative_zero_out"},
        "class_type": "ConditioningZeroOut",
        "inputs": {"conditioning": [pos_id, 0]},
    }
    neg_apply = g.get("14") or g.get("klein9_refmod_apply_neg")
    if isinstance(neg_apply, dict) and neg_apply.get("class_type") == "Klein9RefModApply":
        neg_apply["inputs"]["conditioning"] = ["6", 0]


def _ensure_empty_clip_negative(g: Dict[str, Any]) -> None:
    """Keep legacy empty CLIPTextEncode on node 6 for unfixed baseline arms."""
    clip_id = fs._find_node(g, "CLIPLoader") or "3"
    g["6"] = {
        "_meta": {"title": "negative"},
        "class_type": "CLIPTextEncode",
        "inputs": {"clip": [clip_id, 0], "text": ""},
    }


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
        lora_v1_fn = f"fk9_{c}_v1.safetensors"
        info["celebs"][name] = {
            "compact": c,
            "refmod": ref_fn,
            "refmod_present": (ref_dir / ref_fn).is_file(),
            "lora": f"klein9\\{lora_fn}",
            "lora_present": (lora_dir / lora_fn).is_file(),
            "lora_v1": f"klein9\\{lora_v1_fn}",
            "lora_v1_present": (lora_dir / lora_v1_fn).is_file(),
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
    *,
    ab_suite: str = "full",
    prompts_cfg: Optional[Dict[str, Dict[str, str]]] = None,
    rebuilt_refmod_suffix: str = "_rebuilt",
    seed_tag: str = "",
    with_v1_lora: bool = False,
) -> List[Dict[str, Any]]:
    c = compact_name(celeb)
    sfx = f"_s{seed}" if seed_tag else ""
    lora_spec = {"name": f"klein9/fk9_{c}_v1_prodigy.safetensors", "strength": 1.0}
    hyb_mod, hyb_lora = fs._hybrid_stack_for_name(celeb)
    l7_prompt = render_l7_prompt(celeb, prompts_cfg)
    fp8_name = preflight.get("miraclein_fp8") or MIRACLEIN_FP8_DEFAULT
    has_m_fp8 = bool(preflight.get("miraclein_fp8"))
    arms: List[Dict[str, Any]] = []

    def add(arm_id: str, desc: str, run_dir: Path, rep: Dict[str, Any], skipped: Optional[str] = None) -> None:
        arms.append({
            "arm": arm_id, "arm_key": f"{arm_id}{sfx}", "seed": seed,
            "celeb": celeb, "desc": desc, "run_dir": str(run_dir),
            "status": "SKIPPED" if skipped else rep.get("status", "ERROR"),
            "skip_reason": skipped,
        })

    if ab_suite == "l7":
        # Focused Brief-4 3-way A/B: baseline vs fixed (str 1.0 + ZeroOut + runtime prompt) vs fixed + rebuilt RefMod.
        db = out_root / f"{c}_L7_baseline{sfx}"
        if has_m_fp8 or dry_run:
            rb = fs.build_flux_still(
                db, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
                retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
            )
            if rb.get("status") == "READY":
                def _set_base(g: Dict[str, Any]) -> None:
                    g["1"]["inputs"]["unet_name"] = fp8_name
                    _ensure_empty_clip_negative(g)
                _edit_graph(db, _set_base)
            add("L7-base", f"Unfixed L7 baseline (str 0.85, no ZeroOut, generic prompt, {fp8_name})", db, rb,
                skipped=None if (has_m_fp8 or dry_run) else "Miraclein_4.5_9b_FP8.safetensors missing")
        else:
            add("L7-base", "Unfixed L7 baseline", db, {}, skipped="Miraclein_4.5_9b_FP8.safetensors missing")

        df = out_root / f"{c}_L7_fixed{sfx}"
        if has_m_fp8 or dry_run:
            rf = fs.build_flux_still(
                df, l7_prompt, mode="refmod", refmods=[hyb_mod], refmod_strength=1.0,
                retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
            )
            if rf.get("status") == "READY":
                def _set_fixed(g: Dict[str, Any]) -> None:
                    g["1"]["inputs"]["unet_name"] = fp8_name
                    _ensure_zero_out_negative(g)
                _edit_graph(df, _set_fixed)
            add("L7-fixed", f"Fixed L7 (str 1.0, ZeroOut, per-celeb prompt, {fp8_name})", df, rf,
                skipped=None if (has_m_fp8 or dry_run) else "Miraclein_4.5_9b_FP8.safetensors missing")
        else:
            add("L7-fixed", "Fixed L7", df, {}, skipped="Miraclein_4.5_9b_FP8.safetensors missing")

        rebuilt_stem = f"{hyb_mod}{rebuilt_refmod_suffix}"
        rebuilt_file = Path(preflight.get("comfy_root") or "") / "models" / "refmods-klein9" / f"{rebuilt_stem}.safetensors"
        has_rebuilt = rebuilt_file.is_file()
        dr = out_root / f"{c}_L7_rebuilt{sfx}"
        if (has_m_fp8 and has_rebuilt) or dry_run:
            rr = fs.build_flux_still(
                dr, l7_prompt, mode="refmod", refmods=[rebuilt_stem], refmod_strength=1.0,
                retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
            )
            if rr.get("status") == "READY":
                def _set_reb(g: Dict[str, Any]) -> None:
                    g["1"]["inputs"]["unet_name"] = fp8_name
                    _ensure_zero_out_negative(g)
                _edit_graph(dr, _set_reb)
            add("L7-rebuilt", f"Fixed L7 + rebuilt RefMod ({rebuilt_stem}, {fp8_name})", dr, rr,
                skipped=None if ((has_m_fp8 and has_rebuilt) or dry_run) else f"{rebuilt_stem}.safetensors not on disk")
        else:
            add("L7-rebuilt", f"Fixed L7 + rebuilt RefMod ({rebuilt_stem})", dr, {},
                skipped=f"{rebuilt_stem}.safetensors not on disk" if not has_rebuilt else "Miraclein_4.5_9b_FP8.safetensors missing")

        if with_v1_lora:
            # Official malcolmrey workflow_klein9_refmod_lora.json uses the AdamW fk9_<name>_v1 LoRA at 0.6, not _prodigy.
            dv = out_root / f"{c}_L7_v1lora{sfx}"
            v1_spec = {"name": f"klein9/fk9_{c}_v1.safetensors", "strength": 0.60}
            if has_m_fp8 or dry_run:
                rv = fs.build_flux_still(
                    dv, l7_prompt, mode="refmod", refmods=[hyb_mod], refmod_strength=1.0,
                    retention="fully_preserved (1.0)", loras=[v1_spec], seed=seed, character=celeb, dry_run=dry_run,
                )
                if rv.get("status") == "READY":
                    def _set_v1(g: Dict[str, Any]) -> None:
                        g["1"]["inputs"]["unet_name"] = fp8_name
                        _ensure_zero_out_negative(g)
                    _edit_graph(dv, _set_v1)
                add("L7-v1lora", f"Fixed L7 with fk9_{c}_v1 LoRA @ 0.60 (official workflow LoRA, {fp8_name})", dv, rv,
                    skipped=None if (has_m_fp8 or dry_run) else "Miraclein_4.5_9b_FP8.safetensors missing")
            else:
                add("L7-v1lora", "Fixed L7 with v1 LoRA", dv, {}, skipped="Miraclein_4.5_9b_FP8.safetensors missing")
        return arms

    # L0: Apples-to-apples old A5 settings with SAME prompt P (hybrid 0.85/0.60, retention 0.7, no anchor, pos-only)
    d0 = out_root / f"{c}_L0_a5_old{sfx}"
    r0 = fs.build_flux_still(
        d0, PROMPT_BODY, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
        retention="partially_preserved (0.7)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
    )
    if r0.get("status") == "READY":
        def _undo_new(g: Dict[str, Any]) -> None:
            g["5"]["inputs"]["text"] = PROMPT_BODY
            _ensure_empty_clip_negative(g)
            g["17"]["inputs"]["negative"] = ["6", 0]
            g.pop("14", None)
            g.pop("klein9_refmod_apply_neg", None)
        _edit_graph(d0, _undo_new)
        (d0 / "prompt.txt").write_text(PROMPT_BODY + "\n", encoding="utf-8")
    add("L0", "Old A5 settings (hybrid 0.85/0.60, ret 0.7, no anchor, pos-only)", d0, r0)

    # L0-t2i: Plain T2I control with NO RefMod and NO LoRA (proves whether RefMod moves the face at all)
    dt = out_root / f"{c}_L0_t2i_control{sfx}"
    rt = fs.build_flux_still(dt, PROMPT_BODY, mode="t2i", seed=seed, character=celeb, dry_run=dry_run)
    add("L0-t2i", "Plain T2I control (no RefMod, no LoRA)", dt, rt)

    # L1: New mono default — pure RefMod, retention 1.0, strength 1.0, anchor, pos+neg
    d1 = out_root / f"{c}_L1_refmod_10{sfx}"
    r1 = fs.build_flux_still(d1, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[celeb], seed=seed, character=celeb, dry_run=dry_run)
    add("L1", "Pure RefMod new default (ret 1.0, str 1.0, anchor, pos+neg, CFG 1.1)", d1, r1)

    # L2: L1 at CFG 1.0 (author's CFG)
    d2 = out_root / f"{c}_L2_refmod_cfg10{sfx}"
    r2 = fs.build_flux_still(d2, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[celeb], cfg=1.0, seed=seed, character=celeb, dry_run=dry_run)
    add("L2", "Pure RefMod ret 1.0, CFG 1.0", d2, r2)

    # L3: Hybrid author's recipe (RefMod 0.85 + LoRA 0.60, ret 0.7)
    d3 = out_root / f"{c}_L3_hybrid_07{sfx}"
    r3 = fs.build_flux_still(
        d3, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
        retention="partially_preserved (0.7)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
    )
    add("L3", "Hybrid (RefMod 0.85 + LoRA 0.60, ret 0.7, anchor, pos+neg)", d3, r3)

    # L4: Hybrid at retention 1.0
    d4 = out_root / f"{c}_L4_hybrid_10{sfx}"
    r4 = fs.build_flux_still(
        d4, PROMPT_WITH_ANCHOR, mode="refmod", refmods=[hyb_mod], refmod_strength=0.85,
        retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
    )
    add("L4", "Hybrid (RefMod 0.85 + LoRA 0.60, ret 1.0, anchor, pos+neg)", d4, r4)

    # L5: LoRA only at author's baseline strength 1.0 (with per-celeb runtime prompt)
    d5 = out_root / f"{c}_L5_lora_only_10{sfx}"
    r5 = fs.build_flux_still(d5, l7_prompt, mode="t2i", loras=[lora_spec], seed=seed, character=celeb, dry_run=dry_run)
    add("L5", "LoRA only @ 1.0 (Miraclein NVFP4, per-celeb prompt)", d5, r5)

    # L6: Non-KV Klein FP8 base (stock flux-2-klein-9b-fp8 if present, else existing FLUX-KLEIN-9B-FP8-NSFW; never bare kv-fp8)
    unets = preflight.get("unets") or {}
    l6_unet = (
        "flux-2-klein-9b-fp8.safetensors" if unets.get("flux-2-klein-9b-fp8.safetensors")
        else ("FLUX-KLEIN-9B-FP8-NSFW.safetensors" if unets.get("FLUX-KLEIN-9B-FP8-NSFW.safetensors") else None)
    )
    d6 = out_root / f"{c}_L6_klein_fp8{sfx}"
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
                _ensure_zero_out_negative(g)
            _edit_graph(d6, _set_l6)
        add("L6", f"Pure RefMod ret 1.0 on non-KV FP8 ({chosen}, 8 steps er_sde CFG 1.0)", d6, r6,
            skipped=None if (l6_unet or dry_run) else "no non-KV Klein FP8 UNET on disk")
    else:
        add("L6", "Non-KV Klein FP8 base", d6, {}, skipped="no non-KV Klein FP8 UNET on disk")

    # L7: Miraclein 4.5 FP8 fixed hybrid — RefMod strength 1.0, ZeroOut negative, per-celeb prompt
    d7 = out_root / f"{c}_L7_miraclein_fp8_hybrid{sfx}"
    if has_m_fp8 or dry_run:
        r7 = fs.build_flux_still(
            d7, l7_prompt, mode="refmod", refmods=[hyb_mod], refmod_strength=1.0,
            retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
        )
        if r7.get("status") == "READY":
            def _set_l7(g: Dict[str, Any]) -> None:
                g["1"]["inputs"]["unet_name"] = fp8_name
                _ensure_zero_out_negative(g)
            _edit_graph(d7, _set_l7)
        add("L7", f"Fixed Hybrid (str 1.0, ret 1.0, ZeroOut, per-celeb prompt) on {fp8_name}", d7, r7,
            skipped=None if (has_m_fp8 or dry_run) else "Miraclein_4.5_9b_FP8.safetensors not downloaded yet (D6c)")
    else:
        add("L7", "Miraclein 4.5 FP8", d7, {}, skipped="Miraclein_4.5_9b_FP8.safetensors not downloaded yet (D6c)")

    # L8: Optional adult/NSFW prompt check (only if --nsfw-prompt-file supplied)
    if nsfw_prompt:
        d8 = out_root / f"{c}_L8_nsfw_check{sfx}"
        r8 = fs.build_flux_still(
            d8, nsfw_prompt, mode="refmod", refmods=[hyb_mod], refmod_strength=1.0,
            retention="fully_preserved (1.0)", loras=[hyb_lora], seed=seed, character=celeb, dry_run=dry_run,
        )
        if r8.get("status") == "READY":
            _edit_graph(d8, _ensure_zero_out_negative)
        add("L8", "NSFW prompt check (hybrid str 1.0, ret 1.0, ZeroOut)", d8, r8)

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


def score_arcface(face_py: Path, ref_photos: Sequence[Path], cand_pngs: Dict[str, Path]) -> Dict[str, Any]:
    """Run InsightFace buffalo_l via face_py; parses last JSON line so banner logs never break scoring."""
    empty = {"ref_count": 0, "intra_gallery": None, "scores": {}}
    if not face_py.is_file() or not ref_photos or not cand_pngs:
        return empty
    proc = subprocess.run(
        [str(face_py), "-c", ARCFACE_HELPER,
         json.dumps([str(p) for p in ref_photos]),
         json.dumps({k: str(v) for k, v in cand_pngs.items()})],
        capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        return empty
    parsed = parse_last_json_line(proc.stdout)
    if not parsed:
        return empty
    return {
        "ref_count": int(parsed.get("ref_count") or 0),
        "intra_gallery": parsed.get("intra_gallery"),
        "scores": parsed.get("scores") or {},
    }


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
    ap.add_argument("--num-seeds", type=int, default=1, help="Number of consecutive seeds starting at --seed (e.g. 6 for L7 A/B)")
    ap.add_argument("--seeds", default="", help="Optional comma-separated explicit seed list (overrides --seed/--num-seeds)")
    ap.add_argument("--ab-suite", default="full", choices=("full", "l7"), help="'full' (L0..L7) or 'l7' (L7-base vs L7-fixed vs L7-rebuilt)")
    ap.add_argument("--prompts-json", default="", help="Optional local non-git JSON with per-celeb {trigger, name, likeness_desc, scene}")
    ap.add_argument("--rebuilt-refmod-suffix", default="_rebuilt", help="Suffix for rebuilt RefMod stem in --ab-suite l7")
    ap.add_argument("--with-v1-lora", action="store_true", help="--ab-suite l7: add L7-v1lora arm using fk9_<name>_v1.safetensors @ 0.60 (official workflow LoRA)")
    ap.add_argument("--comfy-root", default=str(DEFAULT_COMFY_ROOT))
    ap.add_argument("--run-queue", default=str(DEFAULT_RUN_QUEUE))
    ap.add_argument("--face-py", default=str(DEFAULT_FACE_PY))
    ap.add_argument("--ref-dir", default=str(DEFAULT_REF_DIR), help="Folder with <compact_name>/*.{png,jpg,webp} real refs (default C:\\AI\\refs_ab_celeb; refuses poisoned refs_ab)")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--comfy-log", default="", help="Optional ComfyUI console log file to scan for missing LoRA keys")
    ap.add_argument("--nsfw-prompt-file", default="", help="Optional path to an adult/NSFW prompt file for arm L8")
    ap.add_argument("--lease-file", default=os.environ.get("ALIENPC_LEASE_FILE", ""), help="Optional lease file path")
    a = ap.parse_args(argv)

    dry_run = not a.run
    celebs = [s.strip() for s in a.celebs.split(",") if s.strip()]
    if a.seeds.strip():
        seeds = [int(s.strip()) for s in a.seeds.split(",") if s.strip()]
    else:
        seeds = [a.seed + i for i in range(max(1, int(a.num_seeds)))]
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    nsfw_prompt = Path(a.nsfw_prompt_file).read_text(encoding="utf-8").strip() if a.nsfw_prompt_file else None
    prompts_cfg = load_prompts_config(Path(a.prompts_json)) if a.prompts_json else {}

    pre = preflight_check(Path(a.comfy_root), celebs)
    (out_dir / "preflight.json").write_text(json.dumps(pre, indent=2) + "\n", encoding="utf-8")
    print(f"PREFLIGHT comfy_exists={pre['comfy_exists']} klein9mod={pre['klein9mod_commit']} suite={a.ab_suite} seeds={seeds}")
    for fn, ok in pre["unets"].items():
        print(f"  UNET {fn}: {'PRESENT' if ok else 'missing'}")
    for nm, ci in pre["celebs"].items():
        print(f"  CELEB {nm}: refmod={ci['refmod_present']} lora={ci['lora_present']} lora_v1={ci['lora_v1_present']}")

    all_arms: List[Dict[str, Any]] = []
    multi_seed = len(seeds) > 1
    for celeb in celebs:
        for sd in seeds:
            all_arms.extend(build_arms_for_celeb(
                celeb, out_dir, sd, pre, dry_run=dry_run, nsfw_prompt=nsfw_prompt,
                ab_suite=a.ab_suite, prompts_cfg=prompts_cfg,
                rebuilt_refmod_suffix=a.rebuilt_refmod_suffix,
                seed_tag="1" if multi_seed else "",
                with_v1_lora=a.with_v1_lora,
            ))

    if dry_run:
        print(f"\nDRY_RUN built {len(all_arms)} arms under {out_dir}:")
        for x in all_arms:
            print(f"  [{x['celeb']}] {x['arm_key']:18s} | {x['status']:7s} | {x['desc']}")
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
                 "L5": "lora", "L6": "refmod", "L7": "both", "L8": "both",
                 "L7-base": "both", "L7-fixed": "both", "L7-rebuilt": "lora", "L7-v1lora": "refmod"}
        for arm in all_arms:
            ci = pre["celebs"].get(arm["celeb"]) or {}
            need = needs.get(arm["arm"])
            missing = [k for k in ("refmod", "lora") if need in (k, "both") and not ci.get(f"{k}_present")]
            if arm["arm"] == "L7-v1lora" and not ci.get("lora_v1_present"):
                missing.append("lora_v1")
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
            print(f"[{arm['celeb']}] {arm['arm_key']:18s} rc={proc.returncode} wall={arm['wall_s']}s png={bool(arm['png'])} log_hits={len(hits)}")

        # Score with ArcFace + build contact sheets
        ref_root = Path(a.ref_dir) if a.ref_dir else None
        sheets: List[str] = []
        gallery_meta: Dict[str, Dict[str, Any]] = {}
        for celeb in celebs:
            c = compact_name(celeb)
            c_arms = [x for x in all_arms if x["celeb"] == celeb]
            cands = {x["arm_key"]: Path(x["png"]) for x in c_arms if x.get("png")}
            refs, skipped_refs, ref_warn = collect_valid_refs(ref_root, c)
            if ref_warn:
                print(f"WARN [{celeb}]: {ref_warn}", file=sys.stderr)
            if skipped_refs:
                print(f"WARN [{celeb}]: skipped {len(skipped_refs)} non-image file(s) in {ref_root / c}: "
                      f"{', '.join(p.name for p in skipped_refs[:5])}", file=sys.stderr)
            af_res = score_arcface(Path(a.face_py), refs, cands)
            gallery_meta[celeb] = {
                "valid_refs": len(refs),
                "skipped_refs": len(skipped_refs),
                "ref_faces": af_res.get("ref_count", 0),
                "intra_gallery": af_res.get("intra_gallery"),
                "warning": ref_warn,
            }
            scores = af_res.get("scores") or {}
            for x in c_arms:
                x["arcface"] = scores.get(x["arm_key"])
            sheet_items = []
            for x in c_arms:
                if not x.get("png"):
                    continue
                sc = x.get("arcface")
                af_lbl = f"{sc['mean']:.3f} (max {sc['max']:.3f})" if isinstance(sc, dict) else "n/a"
                sheet_items.append((f"{x['arm_key']} af={af_lbl} {x.get('wall_s', '')}s", Path(x["png"])))
            sp = make_contact_sheet(f"Flux likeness A/B - {celeb} (seeds {','.join(str(s) for s in seeds)})",
                                    sheet_items, out_dir / f"contact_{c}.png")
            if sp:
                sheets.append(str(sp))

        # Write RESULT.md in out_dir (images stay on AlienPc/QNAP, never in git)
        lines = [
            "# FLUX-LIKENESS-20261120 RESULT",
            "",
            f"- **Suite:** `{a.ab_suite}` | **Seeds:** `{','.join(str(s) for s in seeds)}` | **ComfyUI-Flux2Klein9Mod:** `{pre['klein9mod_commit']}`",
            f"- **Ref dir:** `{a.ref_dir}`",
            f"- **Contact sheets:** {', '.join(f'`{s}`' for s in sheets) or 'none'}",
            "",
            "## Reference gallery ceiling (intra-gallery photo-to-photo cosine)",
            "",
            "| Celeb | Valid refs | Skipped non-images | Ref faces | Intra mean | Intra min | Intra max | Note |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for celeb in celebs:
            gm = gallery_meta.get(celeb) or {}
            ig = gm.get("intra_gallery") or {}
            if isinstance(ig.get("mean"), float):
                stats = f"{ig['mean']:.4f} | {ig['min']:.4f} | {ig['max']:.4f}"
            else:
                stats = "n/a | n/a | n/a"
            lines.append(
                f"| {celeb} | {gm.get('valid_refs', 0)} | {gm.get('skipped_refs', 0)} | {gm.get('ref_faces', 0)} | "
                f"{stats} | {gm.get('warning') or ''} |"
            )

        lines.extend([
            "",
            "## Per-arm results",
            "",
            "| Celeb | Arm | Seed | Description | rc | Wall (s) | AF mean | AF max | AF min | AF centroid | Log hits | PNG |",
            "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for x in all_arms:
            sc = x.get("arcface")
            if isinstance(sc, dict):
                af_m, af_hi, af_lo, af_c = f"{sc['mean']:.4f}", f"{sc['max']:.4f}", f"{sc['min']:.4f}", f"{sc['centroid']:.4f}"
            else:
                af_m = af_hi = af_lo = af_c = "n/a"
            lines.append(
                f"| {x['celeb']} | {x['arm']} | {x['seed']} | {x['desc']} | {x.get('rc', x['status'])} | "
                f"{x.get('wall_s', '-')} | {af_m} | {af_hi} | {af_lo} | {af_c} | "
                f"{len(x.get('log_hits') or [])} | `{x.get('png') or x.get('skip_reason') or ''}` |"
            )

        if multi_seed:
            lines.extend([
                "",
                "## Multi-seed summary (mean across seeds)",
                "",
                "| Celeb | Arm | Scored seeds | Mean of AF mean | Mean of AF max | Mean of AF min |",
                "|---|---|---:|---:|---:|---:|",
            ])
            for celeb in celebs:
                arm_names = list(dict.fromkeys(x["arm"] for x in all_arms if x["celeb"] == celeb))
                for an in arm_names:
                    vals = [x["arcface"] for x in all_arms if x["celeb"] == celeb and x["arm"] == an and isinstance(x.get("arcface"), dict)]
                    if vals:
                        m_avg = sum(v["mean"] for v in vals) / len(vals)
                        hi_avg = sum(v["max"] for v in vals) / len(vals)
                        lo_avg = sum(v["min"] for v in vals) / len(vals)
                        lines.append(f"| {celeb} | {an} | {len(vals)}/{len(seeds)} | {m_avg:.4f} | {hi_avg:.4f} | {lo_avg:.4f} |")
                    else:
                        lines.append(f"| {celeb} | {an} | 0/{len(seeds)} | n/a | n/a | n/a |")

        res_md = out_dir / "RESULT.md"
        res_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nDONE: wrote {res_md}")
        return 0
    finally:
        if lease_held and lease_path:
            lease_path.write_text("", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
