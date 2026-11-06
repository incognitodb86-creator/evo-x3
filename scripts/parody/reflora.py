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
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

COMFY_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI")
PACK_DIR = COMFY_DIR / "custom_nodes" / "ComfyUI-MiniMaxH3RefLoRA"
DEFAULT_REFLORA_DIR = COMFY_DIR / "models" / "loras" / "MinimaxH3" / "reflora"
LORA_NAME_PREFIX = "MinimaxH3\\reflora\\"
MAX_REFERENCE_SLOTS = 8
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

def _loader_node(model_src, clip_src, lora_name: str, members: str) -> Dict[str, Any]:
    return {
        "_meta": {"title": "Load H3 RefLoRA (pack example port order; B2 dials untouched)"},
        "class_type": LOADER_CLASS,
        "inputs": {
            "model": model_src,
            "clip": clip_src,
            "reflora_name": lora_name,
            "lora_strength": LORA_STRENGTH,
            "lora_strength_clip": 1.0,
            "refmod_retention": REFMOD_RETENTION,
            "members": members,
            "components": "Visual",
            "attach_to_model": False,
            "max_total_tokens": 0,
            "show_info": True,
        },
    }


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
}

ALLOWED_NEW_CLASSES = {"LoadImage", LOADER_CLASS, APPLY_CLASS,
                       "MiniMaxH3RefModsLoader", "MiniMaxH3RefModApply"}


def _refmod_slot_key(key: str) -> bool:
    return any(key.startswith(p) for p in ("mod_", "strength_", "copies_"))


def frozen_diff(base: Dict[str, Any], graph: Dict[str, Any],
                allowed_deltas: Optional[set] = None) -> List[str]:
    """R9: list every difference outside the approved identity/Cond/run-specific deltas."""
    allowed = allowed_deltas if allowed_deltas is not None else ALLOWED_INPUT_DELTAS
    bad: List[str] = []
    for nid, node in base.items():
        if nid not in graph:
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


def frozen_diff_2pass(graph: Dict[str, Any], b2_template: Dict[str, Any]) -> List[str]:
    """R9 for two-pass: zero drift on KEEP b2 sampler/upscaler/guide/model dials."""
    return frozen_diff(b2_template, graph, allowed_deltas=ALLOWED_INPUT_DELTAS_2PASS)


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
    """What the submitted graph actually loads (read from the graph, not the resolver)."""
    out = []
    for k in sorted(k for k, v in graph.items() if v.get("class_type") == LOADER_CLASS):
        inp = graph[k]["inputs"]
        out.append({"node": k, "reflora_name": inp.get("reflora_name"),
                    "lora_strength": inp.get("lora_strength"),
                    "refmod_retention": inp.get("refmod_retention"),
                    "members": inp.get("members"), "components": inp.get("components"),
                    "attach_to_model": inp.get("attach_to_model")})
    return out
