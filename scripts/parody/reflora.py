"""RefLoRA (dual-half hybrid) selection and graph graft for the H3 parody pipeline.

RefLoRA arm U2-U4 (plan 40_projects/max-forge-tests/plans/2026-11-05-reflora-arm-plan.md).
Community way: malcolmamal/ComfyUI-MiniMaxH3RefLoRA. Header reads reuse the pack's own
stdlib-only ``container.py``; the graph graft copies only the loader/Apply port wiring from the
pack's ``examples/`` (R16) onto our REF2VA B2 RefMod template. No render settings are imported.

Policy (R8 / KTD4):
- exact local pair ``minimaxh3_<id>_v<N>_refmod`` -> ``minimaxh3_<id>_v<N>_reflora.safetensors``;
- present + valid  -> INDEX + RefMod + RefLoRA (weights + visual reference half);
- absent           -> INDEX + RefMod fallback (reason recorded);
- present + broken -> block (no fallback masking the error, no auto-download).
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

COMFY_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI")
PACK_DIR = COMFY_DIR / "custom_nodes" / "ComfyUI-MiniMaxH3RefLoRA"
DEFAULT_REFLORA_DIR = COMFY_DIR / "models" / "loras" / "MinimaxH3" / "reflora"
LORA_NAME_PREFIX = "MinimaxH3\\reflora\\"
MAX_REFERENCE_SLOTS = 8

# Offline class validation (B2-3): the freshest saved object_info capture and the pack tree.
OBJINFO_DIR = Path(r"C:\AI\community\notes\objinfo")
DEFAULT_OBJINFO_DUMP = OBJINFO_DIR / "object_info_20261105.json"
CUSTOM_NODES_DIR = COMFY_DIR / "custom_nodes"
# The pack that defines the H3 latent upscaler (B2-1 restored it; U5 failed on it as .disabled).
OFFLINE_PACK_UPSCALER = "Comfyui_Minimax_h3_latent_Upscaler"
DISABLED_SUFFIX = ".disabled"
DUMP_NAME_RE = re.compile(r"^object_info_(\d{8})\.json$")
PACK_SCAN_SKIP = {"__pycache__", ".git", ".venv", "venv", "node_modules", "build", "dist"}
PACK_SCAN_MAX_BYTES = 4 << 20
VISUAL_KINDS = ("image", "video")
LORA_STRENGTH = 1.0
REFMOD_RETENTION = 1.0
CHUNK = 1 << 20

LOADER_CLASS = "MiniMaxH3RefLoRALoader"
APPLY_CLASS = "MiniMaxH3RefLoRAApply"

# Exact asset filename: minimaxh3_<id>_v<N>_(refmod|reflora).safetensors (FG-3)
REF_ASSET_RE = re.compile(
    r"^minimaxh3_([a-z0-9]+)_v(\d+)_(refmod|reflora)\.safetensors$",
    re.IGNORECASE,
)


class RefLoRAError(ValueError):
    """A present hybrid failed validation; the run must block (no silent fallback)."""


_CONTAINER = None


def _container(pack_dir: Path = PACK_DIR):
    """Import the maintainer pack's stdlib-only container module (no torch/comfy)."""
    global _CONTAINER
    if _CONTAINER is not None:
        return _CONTAINER
    src = Path(pack_dir) / "container.py"
    if not src.is_file():
        alt = Path(str(pack_dir) + ".disabled") / "container.py"
        if alt.is_file():
            src = alt
        else:
            raise RefLoRAError(f"RefLoRA pack container.py not found at {src}; pack not installed.")
    spec = importlib.util.spec_from_file_location("h3_reflora_container", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _CONTAINER = mod
    return mod


def parse_ref_asset_name(filename: str) -> Optional[Tuple[str, int, str]]:
    """Parse ``minimaxh3_<id>_v<N>_(refmod|reflora).safetensors`` -> (id, version, kind)."""
    m = REF_ASSET_RE.match(Path(filename).name)
    if not m:
        return None
    return m.group(1).lower(), int(m.group(2)), m.group(3).lower()


def hybrid_name_for(refmod_path: str) -> Optional[str]:
    """``minimaxh3_x_v1_refmod.safetensors`` -> ``minimaxh3_x_v1_reflora.safetensors`` (exact)."""
    parsed = parse_ref_asset_name(Path(refmod_path).name)
    if parsed is None or parsed[2] != "refmod":
        # fallback stem rule for fixtures that still use the suffix convention
        stem = Path(refmod_path).stem
        if not stem.endswith("_refmod"):
            return None
        return stem[: -len("_refmod")] + "_reflora.safetensors"
    file_id, ver, _ = parsed
    return f"minimaxh3_{file_id}_v{ver}_reflora.safetensors"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def tensor_digest(path: Path, key: str) -> Dict[str, Any]:
    """dtype/shape/sha256 of one tensor's raw bytes (header offsets; no tensor library)."""
    c = _container()
    header, base = c.read_header(str(path))
    spec = c.tensors_in(header).get(key)
    if spec is None:
        raise RefLoRAError(f"{path}: tensor {key!r} not present.")
    start, end = spec["data_offsets"]
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        fh.seek(base + start)
        remaining = end - start
        while remaining:
            block = fh.read(min(CHUNK, remaining))
            if not block:
                raise RefLoRAError(f"{path}: truncated tensor {key!r}.")
            h.update(block)
            remaining -= len(block)
    return {"dtype": spec["dtype"], "shape": list(spec["shape"]), "sha256": h.hexdigest()}


def inspect_hybrid(path: Path) -> Dict[str, Any]:
    """Header-only structural check via the pack's ``verify``; visual members only (KTD5)."""
    c = _container()
    try:
        info = c.verify(str(path))
    except Exception as exc:  # ContainerError or unreadable file
        raise RefLoRAError(f"{path}: unreadable RefLoRA container ({exc}).") from exc
    if not info.get("ok"):
        raise RefLoRAError(f"{path}: invalid RefLoRA: {'; '.join(info.get('problems', []))}")
    if not info.get("is_reflora") or info.get("lora_keys", 0) <= 0:
        raise RefLoRAError(f"{path}: not a dual-half RefLoRA (lora_keys={info.get('lora_keys')}).")
    visual = [m for m in info["members"] if m.get("kind") in VISUAL_KINDS]
    audio = [m for m in info["members"] if m.get("kind") not in VISUAL_KINDS]
    if not visual:
        raise RefLoRAError(f"{path}: no visual reference members.")
    return {
        "lora_keys": info["lora_keys"],
        "network_dim": info.get("network_dim"),
        "network_alpha": info.get("network_alpha"),
        "visual_members": [
            {"index": m["index"] + 1, "name": m["name"], "kind": m["kind"],
             "shape": m["shape"], "tokens": m["tokens"]}
            for m in visual
        ],
        "audio_members_excluded": [m["name"] for m in audio],
    }


def _is_link_or_junction(path: Path) -> bool:
    """True for symlinks and Windows junctions (Python 3.12 Path.is_junction)."""
    if path.is_symlink():
        return True
    is_j = getattr(path, "is_junction", None)
    if callable(is_j):
        try:
            return bool(is_j())
        except OSError:
            return False
    return False


def _safe_child(path: Path, root: Path) -> Path:
    """Refuse symlinks/junctions on the candidate and the RefLoRA root (FG-9 / R15)."""
    root_p = Path(root)
    if _is_link_or_junction(root_p):
        raise RefLoRAError(f"{root_p}: symlink/junction RefLoRA home is refused (R15 copy-only).")
    if _is_link_or_junction(path):
        raise RefLoRAError(f"{path}: symlink/junction hybrids are refused (R15 copy-only).")
    res = path.resolve()
    try:
        res.relative_to(root_p.resolve())
    except ValueError:
        raise RefLoRAError(f"{path}: resolves outside the RefLoRA home {root}.")
    return res


def select_reflora(
    loaded_refmods: Sequence[str],
    reflora_dir: Path = DEFAULT_REFLORA_DIR,
    with_file_hash: bool = True,
) -> Dict[str, Any]:
    """Pick matching hybrids for the resolver's kept standalone RefMods (in precedence order).

    Returns a dict with ``hybrids`` (ordered), ``standalone_kept`` (after provenance dedup),
    ``standalone_deduped`` (standalone == packed member, injected once from the hybrid),
    ``absent`` (standalones with no local hybrid) and ``fallback_reason``.
    """
    reflora_dir = Path(reflora_dir)
    hybrids: List[Dict[str, Any]] = []
    kept: List[str] = []
    deduped: List[Dict[str, Any]] = []
    absent: List[str] = []

    for refmod in loaded_refmods:
        name = hybrid_name_for(refmod)
        cand = reflora_dir / name if name else None
        if cand is None or not (cand.exists() or cand.is_symlink()):
            absent.append(str(refmod))
            kept.append(str(refmod))
            continue
        hp = _safe_child(cand, reflora_dir)
        info = inspect_hybrid(hp)
        standalone_stem = Path(refmod).stem
        same = [m for m in info["visual_members"] if m["name"] == standalone_stem]
        if not same:
            raise RefLoRAError(
                f"{hp.name}: no packed member named {standalone_stem!r}; standalone/packed "
                "equivalence unknown -> blocked for inspection (KTD3).")
        member = same[0]
        packed = tensor_digest(hp, f"ref_{member['index'] - 1}")
        alone = tensor_digest(Path(refmod), "latent")
        entry = {
            "path": str(hp),
            "lora_name": LORA_NAME_PREFIX + hp.name,
            "sha256": sha256_file(hp) if with_file_hash else None,
            "bytes": hp.stat().st_size,
            "lora_keys": info["lora_keys"],
            "network_dim": info["network_dim"],
            "network_alpha": info["network_alpha"],
            "members": info["visual_members"],
            "member_selection": ",".join(str(m["index"]) for m in info["visual_members"]),
            "components": "Visual",
            "audio_members_excluded": info["audio_members_excluded"],
            "lora_strength": LORA_STRENGTH,
            "refmod_retention": REFMOD_RETENTION,
            "matched_standalone": str(refmod),
        }
        if alone == packed:
            deduped.append({"standalone": str(refmod), "hybrid": str(hp),
                            "packed_member": member["name"], "tensor_sha256": packed["sha256"]})
        else:
            kept.append(str(refmod))
            entry["standalone_differs"] = {"standalone": alone, "packed": packed}
        hybrids.append(entry)

    # Effective reference budget: kept standalones + packed visual members <= 8 (KTD3).
    packed_count = sum(len(h["members"]) for h in hybrids)
    dropped: List[str] = []
    while kept and len(kept) + packed_count > MAX_REFERENCE_SLOTS:
        dropped.append(kept.pop())
    if packed_count > MAX_REFERENCE_SLOTS:
        raise RefLoRAError(f"packed references alone exceed {MAX_REFERENCE_SLOTS} slots.")

    return {
        "enabled": bool(hybrids),
        "hybrids": hybrids,
        "standalone_kept": kept,
        "standalone_deduped": deduped,
        "standalone_dropped_for_budget": dropped,
        "absent": absent,
        "effective_reference_count": len(kept) + packed_count,
        "fallback_reason": None if hybrids else "no matching local *_reflora (INDEX+RefMod fallback)",
    }


# ---------------------------------------------------------------------------
# graph graft (R3 / R9 / KTD1 / KTD2) — single-pass (b2_refmod) + two-pass (b2)
# ---------------------------------------------------------------------------

def _loader_node(model_src, clip_src, lora_name: str, members: str,
                 lora_strength: float = LORA_STRENGTH, lora_strength_clip: float = 1.0,
                 title: str = "Load H3 RefLoRA (pack example port order; B2 dials untouched)") -> Dict[str, Any]:
    """One MiniMaxH3RefLoRALoader in the pack example's port wiring; B2 dials untouched.

    ``clip_src=None`` leaves the optional CLIP input unconnected: the pack's own contract says
    MiniMax H3 LoRAs are ``lora_unet_*`` only, so CLIP "is usually left unconnected"
    (nodes.py:143-144). ``lora_strength=0.0`` is the pack's no-patch path (nodes.py:179-191).
    """
    inputs: Dict[str, Any] = {"model": model_src}
    if clip_src is not None:
        inputs["clip"] = clip_src
    inputs.update({
            "reflora_name": lora_name,
            "lora_strength": lora_strength,
            "lora_strength_clip": lora_strength_clip,
            "refmod_retention": REFMOD_RETENTION,
            "members": members,
            "components": "Visual",
            "attach_to_model": False,
            "max_total_tokens": 0,
            "show_info": True,
    })
    return {"_meta": {"title": title}, "class_type": LOADER_CLASS, "inputs": inputs}


def _apply_node(cond_src, mods_src) -> Dict[str, Any]:
    return {
        "_meta": {"title": "Apply H3 RefLoRA references (cumulative after RefMod Apply)"},
        "class_type": APPLY_CLASS,
        "inputs": {"conditioning": cond_src, "mods": mods_src,
                   "retention": 1.0, "max_total_tokens": 0},
    }


def _refmods_loader_node() -> Dict[str, Any]:
    inputs: Dict[str, Any] = {"max_total_tokens": 0, "show_info": False}
    for i in range(1, 9):
        inputs[f"mod_{i}"] = "(none)"
        inputs[f"strength_{i}"] = 1.0
        inputs[f"copies_{i}"] = 1
    return {
        "_meta": {"title": "Load H3 RefMods (one identity RefMod)"},
        "class_type": "MiniMaxH3RefModsLoader",
        "inputs": inputs,
    }


def _refmod_apply_node(cond_src=("c0", 0)) -> Dict[str, Any]:
    return {
        "_meta": {"title": "Apply H3 RefMod (retention 1.0 = fully_preserved)"},
        "class_type": "MiniMaxH3RefModApply",
        "inputs": {
            "conditioning": list(cond_src) if isinstance(cond_src, tuple) else cond_src,
            "curve_direction": "constant",
            "curve_shape": "linear",
            "curve_value": 1.0,
            "mods": ["refmods", 0],
            "override": False,
            "retention": 1.0,
            "scramble_seed": 0,
        },
    }


def add_cond_picture(graph: Dict[str, Any], image: Optional[str] = None) -> Dict[str, Any]:
    """Approved Cond -> REF2VA Picture input (same wiring as installed b2.api.json)."""
    g = graph
    g["img"] = {"_meta": {"title": "Cond still (approved_characters, staged in ComfyUI/input)"},
                "class_type": "LoadImage",
                "inputs": {"image": image or "community/<cond>.png"}}
    g["c0"]["inputs"]["ref_images.ref_image_1"] = ["img", 0]
    return g


def graft_reflora(base: Dict[str, Any], hybrids: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a copy of the B2 RefMod (single-pass) graph with one Loader+Apply per hybrid.

    MODEL: m_shift -> reflora_1 -> reflora_2 ... -> every model consumer (guider + scheduler).
    CLIP:  clip -> reflora_1 -> ... -> c0 (REF2VA encode).
    COND:  c0 -> refapply (standalone RefMods) -> reflora_apply_1 -> ... -> s0_guide.
    """
    if not hybrids:
        raise ValueError("graft_reflora needs at least one hybrid.")
    g = copy.deepcopy(base)
    for k in ("c0", "refapply", "s0_guide", "s0_sched", "m_shift", "clip"):
        if k not in g:
            raise ValueError(f"base graph lacks {k!r}; not the REF2VA B2 RefMod template.")
    model_src: List[Any] = ["m_shift", 0]
    clip_src: List[Any] = ["clip", 0]
    cond_src: List[Any] = ["refapply", 0]
    for i, h in enumerate(hybrids, start=1):
        lid, aid = f"reflora_{i}", f"reflora_apply_{i}"
        g[lid] = _loader_node(model_src, clip_src, h["lora_name"], h.get("member_selection", "all"))
        g[aid] = _apply_node(cond_src, [lid, 2])
        model_src, clip_src, cond_src = [lid, 0], [lid, 1], [aid, 0]
    g["c0"]["inputs"]["clip"] = clip_src
    g["s0_guide"]["inputs"]["model"] = model_src
    g["s0_guide"]["inputs"]["conditioning"] = cond_src
    g["s0_sched"]["inputs"]["model"] = model_src
    return g


def derive_refmod_2pass_graph(b2_graph: Dict[str, Any]) -> Dict[str, Any]:
    """Graft MiniMaxH3RefModsLoader + MiniMaxH3RefModApply onto KEEP ``b2.api.json``.

    Cond already arrives via ``img``; RefMod Apply wraps ``c0`` and feeds ``ag0``/``ag1`` positive.
    """
    g = copy.deepcopy(b2_graph)
    for k in ("c0", "ag0", "ag1", "s0_guide", "s0_sched", "s1_guide", "p2sched", "m_shift", "img"):
        if k not in g:
            raise ValueError(f"b2 graph lacks {k!r}; not the KEEP two-pass B2 template.")
    g["refmods"] = _refmods_loader_node()
    g["refapply"] = _refmod_apply_node(["c0", 0])
    g["ag0"]["inputs"]["positive"] = ["refapply", 0]
    g["ag1"]["inputs"]["positive"] = ["refapply", 0]
    return g


def graft_reflora_2pass(base: Dict[str, Any], hybrids: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Graft RefLoRA Loader+Apply onto a two-pass (b2 + RefMod) graph.

    MODEL: m_shift -> reflora_* -> s0_guide, s0_sched, s1_guide, p2sched.
    CLIP:  clip -> reflora_* -> c0.
    COND:  c0 -> refapply -> reflora_apply_* -> ag0.positive + ag1.positive.
    """
    if not hybrids:
        raise ValueError("graft_reflora_2pass needs at least one hybrid.")
    g = copy.deepcopy(base)
    for k in ("c0", "refapply", "ag0", "ag1", "s0_guide", "s0_sched", "s1_guide", "p2sched",
              "m_shift", "clip"):
        if k not in g:
            raise ValueError(f"base graph lacks {k!r}; not a two-pass RefMod B2 graph.")
    model_src: List[Any] = ["m_shift", 0]
    clip_src: List[Any] = ["clip", 0]
    cond_src: List[Any] = ["refapply", 0]
    for i, h in enumerate(hybrids, start=1):
        lid, aid = f"reflora_{i}", f"reflora_apply_{i}"
        g[lid] = _loader_node(model_src, clip_src, h["lora_name"], h.get("member_selection", "all"))
        g[aid] = _apply_node(cond_src, [lid, 2])
        model_src, clip_src, cond_src = [lid, 0], [lid, 1], [aid, 0]
    g["c0"]["inputs"]["clip"] = clip_src
    for nid in ("s0_guide", "s0_sched", "s1_guide", "p2sched"):
        g[nid]["inputs"]["model"] = model_src
    g["ag0"]["inputs"]["positive"] = cond_src
    g["ag1"]["inputs"]["positive"] = cond_src
    # Keep AddGuide -> guider conditioning path intact
    g["s0_guide"]["inputs"]["conditioning"] = ["ag0", 0]
    g["s1_guide"]["inputs"]["conditioning"] = ["ag1", 0]
    return g


def derive_reflora_template(b2_refmod: Dict[str, Any]) -> Dict[str, Any]:
    """The committed templates/b2_reflora.api.json = b2_refmod + Cond Picture + one RefLoRA."""
    placeholder = {"lora_name": LORA_NAME_PREFIX + "<id>_reflora.safetensors", "member_selection": "all"}
    g = graft_reflora(b2_refmod, [placeholder])
    return add_cond_picture(g)


def derive_reflora_2pass_template(b2_graph: Dict[str, Any]) -> Dict[str, Any]:
    """Committed templates/b2_reflora_2pass.api.json = KEEP b2 + RefMod + Cond + one RefLoRA."""
    placeholder = {"lora_name": LORA_NAME_PREFIX + "<id>_reflora.safetensors", "member_selection": "all"}
    base = derive_refmod_2pass_graph(b2_graph)
    # Cond image placeholder (b2 already has img; normalize title/path)
    g = graft_reflora_2pass(base, [placeholder])
    g = add_cond_picture(g, g.get("img", {}).get("inputs", {}).get("image") or "community/<cond>.png")
    return g


# ---------------------------------------------------------------------------
# dedicated two-pass PARODY graph (B2-4) - pass 1 voice-protected, pass 2 carries the LoRA half
# ---------------------------------------------------------------------------

PARODY_REF_LOADER = "reflora_ref"      # reference half only -> conditioning (lora_strength 0.0)
PARODY_REF_APPLY = "reflora_apply_1"   # the ONE conditioning injection, feeds both AddGuides
PARODY_P1_LOADER = "reflora_p1"        # only inserted when the pass-1 dial > 0.0
PARODY_P2_LOADER = "reflora_p2"        # pass-2 model line: lora_strength = the pass-2 dial
PASS1_LORA_STRENGTH = 0.0
PASS2_LORA_STRENGTH = 1.0
PASS1_MODEL_CONSUMERS = ("s0_guide", "s0_sched")
PASS2_MODEL_CONSUMERS = ("s1_guide", "p2sched")
COND_INJECT_CONSUMERS = ("ag0", "ag1")
GUIDER_NODES = ("s0_guide", "s1_guide")
# B2-5: a named-celeb clip with NO start photo has no picture to load and nothing to add at
# frame_idx 0, so the Cond node and BOTH AddGuides are dropped (the pack's own no-first-frame
# example has no LoadImage and no AddGuide: examples/workflow_api_minimaxh3_reflora_turbo.json
# wires MiniMaxH3ImageToVideo(20) -> MiniMaxH3RefLoRAApply(31) -> BasicGuider(41).conditioning).
NO_PHOTO_DROP_NODES = ("img",) + COND_INJECT_CONSUMERS
REFLORA_TITLE = ("Load H3 RefLoRA references for conditioning (lora_strength 0.0 = the pack's "
                 "no-patch path: base beta7 model stays voice-protected)")
P1_TITLE = "Pass-1 RefLoRA LoRA half (the --pass1-lora-strength dial); B2 KEEP dials untouched"
P2_TITLE = ("Pass-2 RefLoRA LoRA half (the --pass2-lora-strength dial); clip passthrough, "
            "H3 LoRAs are lora_unet_* only")


def _parody_hybrid(hybrid: Dict[str, Any]) -> Dict[str, Any]:
    """One placeholder/selected hybrid: an installed RefLoRA name + a member selection."""
    if not hybrid or not str(hybrid.get("lora_name") or "").strip():
        raise ValueError("the two-pass parody graph needs one RefLoRA hybrid with a lora_name")
    return {"lora_name": str(hybrid["lora_name"]).strip(),
            "members": str(hybrid.get("member_selection") or hybrid.get("members") or "all")}


def derive_parody_2pass_graph(b2_graph: Dict[str, Any], hybrid: Dict[str, Any], *,
                             pass1_lora_strength: float = PASS1_LORA_STRENGTH,
                             pass2_lora_strength: float = PASS2_LORA_STRENGTH) -> Dict[str, Any]:
    """Graft the per-pass parody dials onto the KEEP two-pass ``b2.api.json`` graph.

    Shape (the B2-4 brief, voice protection first):
      MODEL pass 1 : raw ``m_shift`` -> ``s0_guide`` + ``s0_sched`` at ``pass1_lora_strength`` 0.0,
                     so the base beta7 model is untouched and the native voice stays intact;
      MODEL pass 2 : ``m_shift`` -> ``reflora_p2``(lora_strength = pass-2 dial, attach_to_model
                     False, components Visual, clip passthrough) -> ``s1_guide`` + ``p2sched``;
      COND (both)  : ``c0`` -> ``refapply``(RefMod retention 1.0) -> ``reflora_apply_1``
                     (the RefLoRA reference half, applied ONCE) -> ``ag0``/``ag1`` positive;
      CLIP         : ``c0.clip`` stays the raw ``clip`` node - no LoRA on the text encoder.

    ``reflora_ref`` is a second loader at ``lora_strength=0.0``: the pack patches NOTHING there
    (nodes.py:179-191) and only emits ``H3_REF_MODS``, so the reference half reaches the conditioning
    of both passes without putting LoRA weights on the model any pass samples. The pack never
    mutates a model it is given - ``load_lora_for_models`` clones (comfy/sd.py:117-118) and
    ``inject.into_model`` clones (inject.py:70-72) - so sharing the ``m_shift`` output as the
    upstream of both model lines is safe: each patched line is a distinct clone, the raw pass-1
    line stays the unpatched object, and the two lines cannot alias each other.

    ``pass1_lora_strength > 0.0`` inserts ``reflora_p1`` on the pass-1 model line only; every
    other dial of the frozen b2 graph is byte-identical (``frozen_diff_2pass`` is the guard).
    """
    p1, p2 = float(pass1_lora_strength), float(pass2_lora_strength)
    for name, val in (("pass1_lora_strength", p1), ("pass2_lora_strength", p2)):
        if not 0.0 <= val <= 10.0:
            raise ValueError(f"{name} must be within 0.0..10.0 (the pack's dial range), got {val!r}")
    hyb = _parody_hybrid(hybrid)
    g = derive_refmod_2pass_graph(b2_graph)

    g[PARODY_REF_LOADER] = _loader_node(["m_shift", 0], None, hyb["lora_name"], hyb["members"],
                                        0.0, 0.0, REFLORA_TITLE)
    g[PARODY_REF_APPLY] = _apply_node(["refapply", 0], [PARODY_REF_LOADER, 2])
    for nid in COND_INJECT_CONSUMERS:
        g[nid]["inputs"]["positive"] = [PARODY_REF_APPLY, 0]

    g[PARODY_P2_LOADER] = _loader_node(["m_shift", 0], ["clip", 0], hyb["lora_name"],
                                       hyb["members"], p2, 1.0, P2_TITLE)
    for nid in PASS2_MODEL_CONSUMERS:
        g[nid]["inputs"]["model"] = [PARODY_P2_LOADER, 0]

    if p1 > 0.0:
        g[PARODY_P1_LOADER] = _loader_node(["m_shift", 0], ["clip", 0], hyb["lora_name"],
                                           hyb["members"], p1, 1.0, P1_TITLE)
        for nid in PASS1_MODEL_CONSUMERS:
            g[nid]["inputs"]["model"] = [PARODY_P1_LOADER, 0]
    return g


def drop_cond_picture(graph: Dict[str, Any]) -> Dict[str, Any]:
    """No-photo parody graph (B2-5): drop the Cond picture and BOTH AddGuides (in place).

    The pack's own no-first-frame example is the model: ``workflow_api_minimaxh3_reflora_turbo.json``
    contains no ``LoadImage`` and no ``MiniMaxH3AddGuide`` node at all, and its guide takes the
    identity conditioning from the RefLoRA Apply directly - node ``41`` ``BasicGuider``
    ``"conditioning": ["31", 0]`` (lines 185-193) where ``31`` is ``MiniMaxH3RefLoRAApply``
    ``"conditioning": ["20", 0]`` (lines 158-161) on the ``MiniMaxH3ImageToVideo`` conditioning of
    node 20. ``nodes.py`` is the same contract: ``class MiniMaxH3RefLoRAApply`` (nodes.py:234) takes
    ``conditioning`` (``("CONDITIONING", ...)`` at nodes.py:246) + ``mods`` and returns conditioning
    (``RETURN_TYPES = ("CONDITIONING",)`` at nodes.py:258, ``apply(self, conditioning, mods, ...)``
    at nodes.py:263), so with no start frame the RefMod/RefLoRA injection is the only identity feed.

    ``MiniMaxH3AddGuide`` exists to add a guide IMAGE at ``frame_idx`` (``required`` = positive,
    latent, frame_idx; ``image`` is optional), and in b2.api.json ``ag0``/``ag1`` are fed ONLY by
    ``img`` and consume ONLY the two guiders' conditioning (measured over the frozen template:
    ``ag0`` -> ``s0_guide.conditioning``, ``ag1`` -> ``s1_guide.conditioning``; the latents reach
    the samplers from ``c0``/``s1_cat``, not from the AddGuides). So with no photo the clean shape
    is: remove ``img`` + ``ag0`` + ``ag1``, drop ``c0``'s optional ``ref_images.ref_image_1``
    (``MiniMaxH3ReferenceToVideo`` lists ``ref_images`` under ``optional``), and feed both guiders
    from the ONE conditioning injection. Fails closed if that injection is not in the graph.
    """
    apply_nid = PARODY_REF_APPLY
    apply_node = graph.get(PARODY_REF_APPLY)
    if not apply_node or apply_node.get("class_type") != APPLY_CLASS:
        rm_node = graph.get("refapply")
        if rm_node and rm_node.get("class_type") == "MiniMaxH3RefModApply":
            apply_nid = "refapply"
        else:
            raise ValueError(
                f"drop_cond_picture needs the single conditioning injection {PARODY_REF_APPLY!r} "
                f"({APPLY_CLASS}) or 'refapply' (MiniMaxH3RefModApply); the no-photo graph has no other identity feed")
    for nid in NO_PHOTO_DROP_NODES:
        graph.pop(nid, None)
    graph.setdefault("c0", {}).setdefault("inputs", {}).pop("ref_images.ref_image_1", None)
    for nid in GUIDER_NODES:
        if "conditioning" not in (graph.get(nid) or {}).get("inputs", {}):
            raise ValueError(f"drop_cond_picture: {nid} has no conditioning input to rewire")
        graph[nid]["inputs"]["conditioning"] = [apply_nid, 0]
    return graph


def derive_parody_2pass_template(b2_graph: Dict[str, Any]) -> Dict[str, Any]:
    """The committed templates/b2_parody_2pass.api.json at the default dials (0.0 / 1.0).

    Generated from the live b2.api.json, so the file is the derivation and no hand-written graph
    can drift. Per-run fields stay the b2 example placeholders (``noise.noise_seed``,
    ``save.filename_prefix``, ``c0.length``); only ``img.image`` becomes the ``<cond>`` placeholder
    used by the other parody templates, and ``c0.prompt`` keeps the b2 example text.
    """
    g = derive_parody_2pass_graph(b2_graph, {
        "lora_name": LORA_NAME_PREFIX + "<id>_reflora.safetensors", "member_selection": "all"})
    return add_cond_picture(g, "community/<cond>.png")


def verify_parody_2pass_graph(graph: Dict[str, Any], b2_template: Dict[str, Any], *,
                             pass1_lora_strength: float = PASS1_LORA_STRENGTH,
                             pass2_lora_strength: float = PASS2_LORA_STRENGTH,
                             cond_wired: bool = True) -> None:
    """Fail closed unless the graph is the B2-4 two-pass parody shape (raises ValueError).

    Keeps the KEEP guard (``frozen_diff_2pass`` against the frozen b2) and adds the shape the
    voice-protection rule depends on: raw pass-1 model line at dial 0.0, one RefMod + one
    RefLoRA conditioning injection feeding BOTH guides, the LoRA half only on the pass-2 model
    line, and audio decoded from pass 1.

    ``cond_wired=False`` is the B2-5 no-photo shape: ``img``/``ag0``/``ag1`` are intentionally
    absent (their removal is the approved delta, so the KEEP guard still checks every other node),
    ``c0`` carries no ``ref_images.ref_image_1``, and the ONE conditioning injection feeds both
    guiders directly - the wiring of the pack's no-first-frame example.
    """
    p1, p2 = float(pass1_lora_strength), float(pass2_lora_strength)
    problems: List[str] = list(frozen_diff_no_photo(graph, b2_template) if not cond_wired
                               else frozen_diff_2pass(graph, b2_template))

    def node(nid: str) -> Dict[str, Any]:
        return graph.get(nid) or {}

    def cls(nid: str) -> str:
        return node(nid).get("class_type", "")

    def inp(nid: str, key: str) -> Any:
        return (node(nid).get("inputs") or {}).get(key)

    if cls("refapply") != "MiniMaxH3RefModApply":
        problems.append("refapply is not MiniMaxH3RefModApply")
    elif inp("refapply", "retention") != 1.0 or inp("refapply", "conditioning") != ["c0", 0] \
            or inp("refapply", "mods") != ["refmods", 0]:
        problems.append("refapply must be retention 1.0 wrapping c0 with the refmods loader")

    loaders = sorted(k for k, v in graph.items() if v.get("class_type") == LOADER_CLASS)
    applies = sorted(k for k, v in graph.items() if v.get("class_type") == APPLY_CLASS)
    expected_loaders = [PARODY_REF_LOADER, PARODY_P2_LOADER] + ([PARODY_P1_LOADER] if p1 > 0.0 else [])
    if sorted(loaders) != sorted(expected_loaders):
        problems.append(f"expected RefLoRA loaders {sorted(expected_loaders)}, got {loaders}")
    if len(applies) != 1 or applies[0] != PARODY_REF_APPLY:
        problems.append(f"exactly one conditioning RefLoRA Apply expected, got {applies}")
    for k in loaders:
        if inp(k, "attach_to_model") is not False:
            problems.append(f"{k}: attach_to_model must be False (Apply route only)")
        if inp(k, "components") != "Visual":
            problems.append(f"{k}: components must be Visual (native voice stays INDEX)")
    want_strength = {PARODY_REF_LOADER: 0.0, PARODY_P2_LOADER: p2, PARODY_P1_LOADER: p1}
    for k in loaders:
        got = float(inp(k, "lora_strength") or 0.0)
        want = want_strength[k]
        if abs(got - want) > 1e-9:
            problems.append(f"{k}: lora_strength {got} != the {k} dial {want}")
    for k in graph:
        if cls(k) in ("LoraLoader", "LoraLoaderModelOnly", "Power Lora Loader (rgthree)") \
                and "reflora" in str(node(k).get("inputs", {})).lower():
            problems.append(f"hybrid loaded in generic LoRA loader {k} (double injection)")

    if cls(PARODY_REF_APPLY) != APPLY_CLASS:
        problems.append(f"{PARODY_REF_APPLY} is not {APPLY_CLASS}")
    elif inp(PARODY_REF_APPLY, "conditioning") != ["refapply", 0] \
            or inp(PARODY_REF_APPLY, "mods") != [PARODY_REF_LOADER, 2]:
        problems.append(f"{PARODY_REF_APPLY} must apply {PARODY_REF_LOADER}.mods to refapply")
    if not cond_wired:
        # B2-5: no Cond picture -> no LoadImage, no AddGuide, no picture input on c0, and the
        # single injection is the guide conditioning of BOTH passes.
        for nid, gnode in graph.items():
            if gnode.get("class_type") == "LoadImage":
                problems.append(f"{nid}: no-photo graph must not carry a LoadImage node")
            if gnode.get("class_type") == "MiniMaxH3AddGuide":
                problems.append(f"{nid}: no-photo graph must not carry a MiniMaxH3AddGuide node")
        if "ref_images.ref_image_1" in (node("c0").get("inputs") or {}):
            problems.append("c0 must not wire ref_images.ref_image_1 with no Cond picture")
        for nid in GUIDER_NODES:
            if cls(nid) != "BasicGuider":
                problems.append(f"{nid} is not BasicGuider")
            elif inp(nid, "conditioning") != [PARODY_REF_APPLY, 0]:
                problems.append(f"{nid}.conditioning is not the single RefLoRA Apply "
                                f"(got {inp(nid, 'conditioning')})")
    else:
        for nid in COND_INJECT_CONSUMERS:
            if cls(nid) != "MiniMaxH3AddGuide":
                problems.append(f"{nid} is not MiniMaxH3AddGuide")
            elif inp(nid, "positive") != [PARODY_REF_APPLY, 0]:
                problems.append(f"{nid}.positive is not the single RefLoRA Apply")
        if cls("s0_guide") != "BasicGuider" or inp("s0_guide", "conditioning") != ["ag0", 0]:
            problems.append("s0_guide conditioning must stay ag0")
        if cls("s1_guide") != "BasicGuider" or inp("s1_guide", "conditioning") != ["ag1", 0]:
            problems.append("s1_guide conditioning must stay ag1")

    pass1_src = [PARODY_P1_LOADER, 0] if p1 > 0.0 else ["m_shift", 0]
    for nid in PASS1_MODEL_CONSUMERS:
        if inp(nid, "model") != pass1_src:
            problems.append(f"{nid} model is not the pass-1 model line {pass1_src} "
                            f"(got {inp(nid, 'model')})")
    for nid in PASS2_MODEL_CONSUMERS:
        if inp(nid, "model") != [PARODY_P2_LOADER, 0]:
            problems.append(f"{nid} model is not {PARODY_P2_LOADER}")

    if inp("c0", "clip") != ["clip", 0]:
        problems.append("c0.clip must stay the raw CLIP loader (no LoRA on the text encoder)")
    if inp("dec_a", "samples") != ["s0_sep", 1]:
        problems.append("dec_a.samples must stay [s0_sep, 1] (audio decoded from pass 1)")
    if cls("c0") != "MiniMaxH3ReferenceToVideo":
        problems.append("c0 is not REF2VA")
    if problems:
        raise ValueError("parody two-pass graph check failed: " + " | ".join(problems))


# Inputs that may differ from the frozen b2_refmod template (identity/Cond + run-specific only).
ALLOWED_INPUT_DELTAS = {
    ("c0", "prompt"), ("c0", "length"), ("c0", "clip"), ("c0", "ref_images.ref_image_1"),
    ("noise", "noise_seed"), ("save", "filename_prefix"),
    ("s0_guide", "model"), ("s0_guide", "conditioning"), ("s0_sched", "model"),
}

ALLOWED_INPUT_DELTAS_2PASS = ALLOWED_INPUT_DELTAS | {
    ("img", "image"),
    ("ag0", "positive"), ("ag1", "positive"),
    ("s1_guide", "model"), ("p2sched", "model"),
    # B2-4: the pass-2 model line is a per-run dial. The pass-1 model line (("s0_guide",
    # "model"), ("s0_sched", "model")) is already an approved delta, so the KEEP guard cannot
    # see a wrong pass-1 dial; verify_parody_2pass_graph checks that line against the dial.
}

# B2-5: a named-celeb clip with NO start photo. The pack's no-first-frame example feeds the guider
# conditioning straight from the RefLoRA/RefMod conditioning, so with img/ag0/ag1 gone the pass-2
# guide's conditioning is an approved delta as well (the pass-1 one already is, from the B2-4 shape).
ALLOWED_INPUT_DELTAS_NO_PHOTO = ALLOWED_INPUT_DELTAS_2PASS | {("s1_guide", "conditioning")}

ALLOWED_NEW_CLASSES = {"LoadImage", LOADER_CLASS, APPLY_CLASS,
                       "MiniMaxH3RefModsLoader", "MiniMaxH3RefModApply"}


def _refmod_slot_key(key: str) -> bool:
    return any(key.startswith(p) for p in ("mod_", "strength_", "copies_"))


def frozen_diff(base: Dict[str, Any], graph: Dict[str, Any],
                allowed_deltas: Optional[set] = None,
                allow_removed: Optional[Sequence[str]] = None) -> List[str]:
    """R9: list every difference outside the approved identity/Cond/run-specific deltas.

    ``allow_removed`` names nodes the checked graph may legitimately NOT carry (B2-5: a named-celeb
    clip with no start photo drops ``img`` + both ``MiniMaxH3AddGuide`` nodes). Everything else in
    the base graph must still be present, so the KEEP guard keeps its teeth over every dial of the
    nodes that remain.
    """
    allowed = allowed_deltas if allowed_deltas is not None else ALLOWED_INPUT_DELTAS
    dropped = set(allow_removed or ())
    bad: List[str] = []
    for nid, node in base.items():
        if nid not in graph:
            if nid in dropped:
                continue
            bad.append(f"node removed: {nid}")
            continue
        other = graph[nid]
        if other.get("class_type") != node.get("class_type"):
            bad.append(f"class changed: {nid}")
        a, b = node.get("inputs", {}), other.get("inputs", {})
        for key in set(a) | set(b):
            if a.get(key) == b.get(key):
                continue
            if (nid, key) in allowed:
                continue
            if nid == "refmods" and _refmod_slot_key(key):
                continue
            bad.append(f"dial drift: {nid}.{key}: {a.get(key)!r} -> {b.get(key)!r}")
    for nid, node in graph.items():
        if nid not in base and node.get("class_type") not in ALLOWED_NEW_CLASSES:
            bad.append(f"unapproved new node: {nid} ({node.get('class_type')})")
    return bad


def frozen_diff_2pass(graph: Dict[str, Any], b2_template: Dict[str, Any],
                      allow_removed: Optional[Sequence[str]] = None) -> List[str]:
    """R9 for two-pass: zero drift on KEEP b2 sampler/upscaler/guide/model dials."""
    return frozen_diff(b2_template, graph, allowed_deltas=ALLOWED_INPUT_DELTAS_2PASS,
                       allow_removed=allow_removed)


def frozen_diff_no_photo(graph: Dict[str, Any], b2_template: Dict[str, Any]) -> List[str]:
    """R9 for the B2-5 no-photo two-pass shape: the KEEP guard keeps every dial of the nodes that
    remain, and the approved delta is exactly the no-first-frame one - the ``img``/``ag0``/``ag1``
    removals, the dropped ``c0`` picture input, and both guiders rewired to the ONE injection."""
    return frozen_diff(b2_template, graph, allowed_deltas=ALLOWED_INPUT_DELTAS_NO_PHOTO,
                       allow_removed=NO_PHOTO_DROP_NODES)


def verify_reflora_graph(graph: Dict[str, Any], base: Dict[str, Any], n_hybrids: int,
                         two_pass: bool = False) -> None:
    """Fail closed unless topology satisfies KTD2 and R9/R10 (raises ValueError)."""
    problems = (frozen_diff_2pass(graph, base) if two_pass else frozen_diff(base, graph))
    loaders = sorted(k for k, v in graph.items() if v.get("class_type") == LOADER_CLASS)
    applies = sorted(k for k, v in graph.items() if v.get("class_type") == APPLY_CLASS)
    if len(loaders) != n_hybrids or len(applies) != n_hybrids:
        problems.append(f"expected {n_hybrids} loader/apply pairs, got {len(loaders)}/{len(applies)}")
    for k, v in graph.items():
        if v.get("class_type") in ("LoraLoader", "LoraLoaderModelOnly", "Power Lora Loader (rgthree)"):
            if "reflora" in str(v.get("inputs", {})).lower():
                problems.append(f"hybrid loaded in generic LoRA loader {k} (double injection)")
    for k in loaders:
        inp = graph[k]["inputs"]
        if inp.get("attach_to_model") is not False:
            problems.append(f"{k}: attach_to_model must be False (Apply route only)")
        if inp.get("components") != "Visual":
            problems.append(f"{k}: components must be Visual (native voice stays INDEX)")
        if not float(inp.get("lora_strength", 0)):
            problems.append(f"{k}: zero LoRA strength (weights half off)")
    mods_users: Dict[str, int] = {}
    for k in applies:
        src = graph[k]["inputs"].get("mods")
        mods_users[src[0]] = mods_users.get(src[0], 0) + 1
    for k in loaders:
        if mods_users.get(k, 0) != 1:
            problems.append(f"{k}.mods must reach exactly one Apply (got {mods_users.get(k, 0)})")
    last = loaders[-1] if loaders else None
    if last:
        model_consumers = ("s0_guide", "s0_sched") + (("s1_guide", "p2sched") if two_pass else ())
        for nid in model_consumers:
            if graph[nid]["inputs"].get("model") != [last, 0]:
                problems.append(f"{nid} model is not the final RefLoRA-patched model")
    if two_pass:
        # Cond chain: final apply feeds ag0/ag1 positive; guiders still take AddGuide.
        last_apply = applies[-1] if applies else None
        if last_apply:
            if graph["ag0"]["inputs"].get("positive") != [last_apply, 0]:
                problems.append("ag0.positive is not the final RefLoRA Apply")
            if graph["ag1"]["inputs"].get("positive") != [last_apply, 0]:
                problems.append("ag1.positive is not the final RefLoRA Apply")
        if graph["s0_guide"]["inputs"].get("conditioning") != ["ag0", 0]:
            problems.append("s0_guide conditioning must stay ag0 in two-pass")
        if graph["s1_guide"]["inputs"].get("conditioning") != ["ag1", 0]:
            problems.append("s1_guide conditioning must stay ag1 in two-pass")
    else:
        # Conditioning chain must run c0 -> refapply -> reflora_apply_* -> guider.
        chain, cur, seen = [], graph["s0_guide"]["inputs"].get("conditioning"), set()
        while isinstance(cur, list) and cur[0] not in seen:
            seen.add(cur[0])
            chain.append(cur[0])
            cur = graph[cur[0]]["inputs"].get("conditioning")
        if chain[-2:] != ["refapply", "c0"] or set(applies) - set(chain):
            problems.append(f"conditioning chain broken: {chain}")
    if graph["c0"]["inputs"].get("ref_images.ref_image_1") != ["img", 0] or "img" not in graph:
        problems.append("approved Cond does not reach REF2VA Picture input (R10)")
    if graph["c0"].get("class_type") != "MiniMaxH3ReferenceToVideo":
        problems.append("c0 is not REF2VA")
    if problems:
        raise ValueError("RefLoRA graph check failed: " + " | ".join(problems))


def reflora_ledger(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """What the submitted graph actually loads (read from the graph, not the resolver).

    ``model_line`` names the model consumers each loader feeds, so a per-pass two-pass graph
    (B2-4: reference-only at 0.0, the pass-2 LoRA half, a pass-1 loader only above 0.0) records
    which pass carries which dial instead of a list of identical strengths.
    """
    consumers: Dict[str, List[str]] = {}
    for nid, node in graph.items():
        src = (node.get("inputs") or {}).get("model")
        if isinstance(src, list) and len(src) == 2 and isinstance(src[0], str):
            consumers.setdefault(src[0], []).append(nid)
    out = []
    for k in sorted(k for k, v in graph.items() if v.get("class_type") == LOADER_CLASS):
        inp = graph[k]["inputs"]
        out.append({"node": k, "reflora_name": inp.get("reflora_name"),
                    "lora_strength": inp.get("lora_strength"),
                    "refmod_retention": inp.get("refmod_retention"),
                    "members": inp.get("members"), "components": inp.get("components"),
                    "attach_to_model": inp.get("attach_to_model"),
                    "model_line": sorted(consumers.get(k, []))})
    return out


# ---------------------------------------------------------------------------
# offline class validation (B2-3) - saved object_info capture + .disabled pack evidence
# ---------------------------------------------------------------------------

_OBJECT_INFO_CACHE: Dict[str, Tuple[Tuple[int, int], Dict[str, Any]]] = {}


def _load_object_info(dump_path: Path) -> Dict[str, Any]:
    """Read one saved object_info capture (cached by path + mtime/size; plain file read)."""
    path = Path(dump_path)
    key = str(path)
    st = path.stat()
    stamp = (st.st_mtime_ns, st.st_size)
    hit = _OBJECT_INFO_CACHE.get(key)
    if hit is not None and hit[0] == stamp:
        return hit[1]
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    _OBJECT_INFO_CACHE[key] = (stamp, data)
    return data


def _dump_tag(dump_path: Path) -> str:
    """The capture date tag in an object_info file name (``object_info_20261031.json`` -> ``20261031``)."""
    m = DUMP_NAME_RE.match(Path(dump_path).name)
    return m.group(1) if m else Path(dump_path).stem


def _saved_captures() -> List[Tuple[str, Path]]:
    """[(tag, path)] for every saved object_info capture, newest tag first."""
    if not OBJINFO_DIR.is_dir():
        return []
    found = []
    for p in OBJINFO_DIR.iterdir():
        m = DUMP_NAME_RE.match(p.name)
        if m:
            found.append((m.group(1), p))
    return sorted(found, key=lambda tp: tp[0], reverse=True)


def _pack_defining_class(class_name: str,
                         custom_nodes_dir: Path = CUSTOM_NODES_DIR) -> Optional[Tuple[str, Path]]:
    """grep the pack sources for the literal class name -> (pack_dir_name, source_file).

    Text scan only: no import of pack code, no subprocess, no ComfyUI call. A pack registers a
    node by its literal name in a ``NODE_CLASS_MAPPINGS`` key in its own ``.py``, so a literal
    substring is the evidence that this pack is the provider (the B2-2 facts were gathered the
    same way with ``grep -rln``). First hit per pack, packs in name order = deterministic.
    """
    root = Path(custom_nodes_dir)
    if not root.is_dir():
        return None
    for pack in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name):
        for dirpath, dirnames, filenames in os.walk(pack):
            dirnames[:] = sorted(d for d in dirnames if d not in PACK_SCAN_SKIP)
            for fn in sorted(filenames):
                if not fn.endswith(".py"):
                    continue
                src = Path(dirpath) / fn
                try:
                    if src.stat().st_size > PACK_SCAN_MAX_BYTES:
                        continue
                    text = src.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if class_name in text:
                    return pack.name, src
    return None


def _present_in_newer_capture(class_name: str, dump_path: Path) -> bool:
    """True if a capture taken after ``dump_path`` lists the class (so it was absent from this one)."""
    tag = _dump_tag(dump_path)
    for other_tag, other_path in _saved_captures():
        if tag is not None and other_tag <= tag:
            continue
        try:
            known = _load_object_info(other_path)
        except (OSError, ValueError):
            continue
        if class_name in known:
            return True
    return False


def offline_class_check(
    graph: Dict[str, Any],
    dump_path: Optional[Path] = None,
    *,
    custom_nodes_dir: Path = CUSTOM_NODES_DIR,
    scan_packs: bool = True,
) -> List[str]:
    """CPU-only stand-in for the unknown-class branch of ``run_graph_job.static_check()``.

    Every ``class_type`` in the graph must be listed by the saved object_info capture (default
    the freshest one, ``notes/objinfo/object_info_20261105.json``). A missing class is the one
    failure a frozen template cannot show on CPU, and it is what killed the U5 two-pass arm at
    submit time: ``static_check`` (run_graph_job.py:111-119) raised
    ``lsu3: unknown class MinimaxH3LatentUpscaler3D`` because the pack that defines it was
    parked as ``Comfyui_Minimax_h3_latent_Upscaler.disabled``. So a missing class also names
    the pack that defines it and says whether that pack is disabled, from the live directory
    name, or - when the pack is present now - from the captures: a class that shows up in a
    newer capture was not loaded when this capture was taken.

    Only file reads: no HTTP, no subprocess, no GPU, no lock, no model load. Returns the
    problem lines (``[]`` = renderable against this capture); the caller fails closed. Lines
    never carry prompt text.
    """
    path = Path(dump_path) if dump_path else DEFAULT_OBJINFO_DUMP
    if not path.is_file():
        raise RefLoRAError(
            f"offline_class_check: no object_info capture at {path}; capture one with "
            "scripts/probe_nodes.py (B2-2) - a parody graph is not built against an unknown node set."
        )
    known = _load_object_info(path)
    problems: List[str] = []
    for nid in sorted(graph):
        node = graph[nid]
        if not isinstance(node, dict):
            continue
        ct = node.get("class_type")
        if not isinstance(ct, str) or not ct:
            problems.append(f"{nid}: missing class_type")
            continue
        if ct in known:
            continue
        line = f"{nid}: unknown class {ct}"
        if scan_packs:
            prov = _pack_defining_class(ct, custom_nodes_dir)
            if prov is not None:
                pack_name = prov[0]
                if pack_name.endswith(DISABLED_SUFFIX):
                    line += f" (defined by {pack_name} - pack disabled)"
                elif _present_in_newer_capture(ct, path):
                    line += (f" (defined by {pack_name} - pack disabled at the {_dump_tag(path)} "
                             f"capture; {pack_name.removesuffix(DISABLED_SUFFIX)} is present and "
                             "enabled now)")
                else:
                    line += (f" (defined by {pack_name} - pack present, class not in this "
                             "capture and not in any newer capture)")
        problems.append(line)
    return problems

