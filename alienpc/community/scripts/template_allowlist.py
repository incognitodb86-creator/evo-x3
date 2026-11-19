"""S2 template allowlist check for AlienPc ComfyUI graphs (unified plan e0c446f).

Accepts only ComfyUI API graphs whose node IDs, class_types, link wiring, and fixed
parameters match an allowlisted production template:
  - the 8 U55 templates (plain, oc_guide, oc_ref, named_parody, talk, two_person,
    long_continuation, ref2va_16x9)
  - b2.api.json and b2_refmod.api.json
  - the 3-node RTX VSR upscale graph (VHS_LoadVideo -> RTXVideoSuperResolution ->
    VHS_VideoCombine, matching x3-community scripts/remote_upscale.py)
  - later promoted templates listed in scripts/allowlist_promoted.json (next to
    scripts/u55_allowlist_specs.json, never in templates/) with a verified sha256.
    Promotion is ONLY by a Derrick-approved commit updating that manifest;
    *.candidate.api.json and names with '/', '\\', or '..' are always refused.

Refuses:
  - any LLM / prompt-rewriter node graph (e.g. b2_omni_rewriter.api.json)
  - any extra, missing, or substituted node
  - any rewired edge or non-variable parameter change
  - path traversal in image/video/RefMod/filename_prefix fields or promoted manifest

Allowed variable fields on matched templates:
  prompt, text, noise_seed, seed, image, video, mod_1..mod_8, strength_1..strength_8,
  length, width, height, filename_prefix (plus frame_rate on RTX VSR).

This module is pure offline validation (no HTTP server, no ComfyUI import).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SCRIPTS_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATES_DIR = SCRIPTS_DIR.parent / "templates"
DEFAULT_U55_SPECS = SCRIPTS_DIR / "u55_allowlist_specs.json"
DEFAULT_PROMOTED_MANIFEST = SCRIPTS_DIR / "allowlist_promoted.json"
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")

U55_TEMPLATE_NAMES = (
    "plain",
    "oc_guide",
    "oc_ref",
    "named_parody",
    "talk",
    "two_person",
    "long_continuation",
    "ref2va_16x9",
)
CORE_TEMPLATE_NAMES = ("b2", "b2_refmod") + U55_TEMPLATE_NAMES
RTX_VSR_NAME = "rtx_vsr_2x"

VAR_SENTINEL = "__VAR__"

DENIED_LLM_CLASSES = frozenset({
    "MiniMaxH3PromptWriterOmni",
    "MiniMaxH3RewriterOptions",
    "MiniMaxH3PromptWriterAPI",
    "MiniMaxH3PromptBuilder",
})
_LLM_CLASS_RE = re.compile(r"(?:PromptWriter|Rewriter|LLM)", re.I)

PROMPT_KEYS = frozenset({"prompt", "text"})
SEED_KEYS = frozenset({"noise_seed", "seed"})
INPUT_PATH_KEYS = frozenset({"image", "video"})
REFMOD_NAME_KEYS = frozenset(f"mod_{i}" for i in range(1, 9))
REFMOD_STRENGTH_KEYS = frozenset(f"strength_{i}" for i in range(1, 9))
FRAME_KEYS = frozenset({"length"})
DIM_KEYS = frozenset({"width", "height"})
PREFIX_KEYS = frozenset({"filename_prefix"})

VARIABLE_KEYS = (
    PROMPT_KEYS
    | SEED_KEYS
    | INPUT_PATH_KEYS
    | REFMOD_NAME_KEYS
    | REFMOD_STRENGTH_KEYS
    | FRAME_KEYS
    | DIM_KEYS
    | PREFIX_KEYS
)

_SAFE_RTX_INPUT_RE = re.compile(r"^(?:x3_rtx2x_input\.mp4|rtx2x_[A-Za-z0-9._-]+\.(?:mp4|mov|mkv|webm))$")


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_link(v: Any) -> bool:
    return isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and _is_int(v[1])


def _is_safe_rel_path(s: Any, *, allow_slash: bool = True) -> bool:
    if not isinstance(s, str) or not s.strip():
        return False
    if "\x00" in s or ".." in s.replace("\\", "/").split("/"):
        return False
    if s.startswith(("/", "\\")) or (len(s) >= 2 and s[1] == ":"):
        return False
    if not allow_slash and ("/" in s or "\\" in s):
        return False
    return True


def _has_llm_node(graph: Dict[str, Any]) -> Optional[str]:
    for nid, node in graph.items():
        if not isinstance(node, dict):
            continue
        ct = str(node.get("class_type") or "")
        if ct in DENIED_LLM_CLASSES or _LLM_CLASS_RE.search(ct):
            return f"{nid} ({ct})"
    return None


def _graph_nodes(graph: Dict[str, Any]) -> Optional[Dict[str, Dict[str, Any]]]:
    if not isinstance(graph, dict) or not graph:
        return None
    out: Dict[str, Dict[str, Any]] = {}
    for nid, node in graph.items():
        if not isinstance(nid, str) or not isinstance(node, dict):
            return None
        ct = node.get("class_type")
        ins = node.get("inputs")
        if not isinstance(ct, str) or not ct or not isinstance(ins, dict):
            return None
        out[nid] = {"class_type": ct, "inputs": ins}
    return out


def _validate_var_value(key: str, val: Any) -> Optional[str]:
    if key in PROMPT_KEYS:
        return None if isinstance(val, str) else f"{key} must be str"
    if key in SEED_KEYS:
        return None if _is_int(val) else f"{key} must be int"
    if key in INPUT_PATH_KEYS:
        return None if _is_safe_rel_path(val, allow_slash=True) else f"{key} has unsafe path"
    if key in REFMOD_NAME_KEYS:
        if val == "(none)":
            return None
        return None if _is_safe_rel_path(val, allow_slash=False) else f"{key} has unsafe refmod name"
    if key in REFMOD_STRENGTH_KEYS:
        return None if (_is_num(val) and -2.0 <= float(val) <= 2.0) else f"{key} out of range"
    if key in FRAME_KEYS:
        return None if (_is_int(val) and 1 <= val <= 2000) else f"{key} must be int in 1..2000"
    if key in DIM_KEYS:
        return None if (_is_int(val) and 64 <= val <= 4096 and val % 16 == 0) else f"{key} must be multiple of 16 in 64..4096"
    if key in PREFIX_KEYS:
        return None if _is_safe_rel_path(val, allow_slash=True) else f"{key} has unsafe prefix"
    return f"{key} is not a variable field"


def _match_rtx_vsr(nodes: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
    if set(nodes.keys()) != {"1", "2", "3"}:
        return False, "node ids do not match rtx_vsr_2x"
    n1, n2, n3 = nodes["1"], nodes["2"], nodes["3"]
    if (n1["class_type"], n2["class_type"], n3["class_type"]) != (
        "VHS_LoadVideo",
        "RTXVideoSuperResolution",
        "VHS_VideoCombine",
    ):
        return False, "node classes do not match rtx_vsr_2x"

    i1, i2, i3 = n1["inputs"], n2["inputs"], n3["inputs"]
    fixed1 = {
        "force_rate": 0,
        "custom_width": 0,
        "custom_height": 0,
        "frame_load_cap": 0,
        "skip_first_frames": 0,
        "select_every_nth": 1,
    }
    if set(i1.keys()) != (set(fixed1.keys()) | {"video"}):
        return False, "rtx_vsr_2x node 1 keys mismatch"
    for k, exp in fixed1.items():
        if i1.get(k) != exp:
            return False, f"rtx_vsr_2x node 1.{k} mismatch"
    vid = i1.get("video")
    if not isinstance(vid, str) or not _SAFE_RTX_INPUT_RE.match(vid):
        return False, "rtx_vsr_2x node 1.video must be x3_rtx2x_input.mp4 or rtx2x_*.<ext>"

    fixed2 = {
        "images": ["1", 0],
        "resize_type": "scale by multiplier",
        "resize_type.scale": 2.0,
        "quality": "ULTRA",
        "strength": 1.0,
        "image_encoding": "8-bit RGB",
    }
    if set(i2.keys()) != set(fixed2.keys()):
        return False, "rtx_vsr_2x node 2 keys mismatch"
    for k, exp in fixed2.items():
        v = i2.get(k)
        if k in ("resize_type.scale", "strength"):
            if not _is_num(v) or float(v) != float(exp):
                return False, f"rtx_vsr_2x node 2.{k} must be {exp}"
        elif v != exp:
            return False, f"rtx_vsr_2x node 2.{k} mismatch"

    fixed3 = {
        "images": ["2", 0],
        "audio": ["1", 2],
        "loop_count": 0,
        "format": "video/h264-mp4",
        "pix_fmt": "yuv420p",
        "crf": 16,
        "save_metadata": False,
        "trim_to_audio": False,
        "pingpong": False,
        "save_output": True,
    }
    if set(i3.keys()) != (set(fixed3.keys()) | {"frame_rate", "filename_prefix"}):
        return False, "rtx_vsr_2x node 3 keys mismatch"
    for k, exp in fixed3.items():
        if i3.get(k) != exp:
            return False, f"rtx_vsr_2x node 3.{k} mismatch"
    fr = i3.get("frame_rate")
    if not _is_num(fr) or not (0 < float(fr) <= 240):
        return False, "rtx_vsr_2x node 3.frame_rate out of range"
    pfx = i3.get("filename_prefix")
    if not _is_safe_rel_path(pfx, allow_slash=True) or not str(pfx).startswith("community/rtx2x/"):
        return False, "rtx_vsr_2x node 3.filename_prefix must start with community/rtx2x/"

    return True, ""


def _match_template(nodes: Dict[str, Dict[str, Any]], spec: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
    if set(nodes.keys()) != set(spec.keys()):
        extra = sorted(set(nodes.keys()) - set(spec.keys()))
        missing = sorted(set(spec.keys()) - set(nodes.keys()))
        parts = []
        if extra:
            parts.append(f"extra nodes {extra}")
        if missing:
            parts.append(f"missing nodes {missing}")
        return False, "; ".join(parts)

    for nid, snode in spec.items():
        gnode = nodes[nid]
        if gnode["class_type"] != snode["class_type"]:
            return False, f"node {nid} class_type {gnode['class_type']!r} != {snode['class_type']!r}"
        s_in = snode["inputs"]
        g_in = gnode["inputs"]
        if set(g_in.keys()) != set(s_in.keys()):
            return False, f"node {nid} input keys mismatch"
        for k, expected in s_in.items():
            actual = g_in[k]
            if _is_link(expected):
                if actual != expected:
                    return False, f"node {nid}.{k} link {actual!r} != {expected!r}"
                continue
            if _is_link(actual):
                return False, f"node {nid}.{k} unexpected link {actual!r}"
            if expected == VAR_SENTINEL or k in VARIABLE_KEYS:
                err = _validate_var_value(k, actual)
                if err:
                    return False, f"node {nid}.{k}: {err}"
            else:
                if actual != expected:
                    return False, f"node {nid}.{k} fixed value {actual!r} != {expected!r}"

    return True, ""


def _is_safe_promoted_filename(name: Any) -> bool:
    if not isinstance(name, str) or not name or "\x00" in name:
        return False
    if "/" in name or "\\" in name or ".." in name:
        return False
    if not name.endswith(".api.json") or name.endswith(".candidate.api.json"):
        return False
    return True


def _load_promoted_manifest(
    manifest_path: Optional[Path],
    templates_dir: Optional[Path],
) -> List[Tuple[str, Dict[str, Any]]]:
    """Load promoted templates from scripts/allowlist_promoted.json with strict name + sha256 checks."""
    if not manifest_path or not templates_dir:
        return []
    mpath = Path(manifest_path)
    tdir = Path(templates_dir).resolve()
    if not mpath.is_file():
        return []
    try:
        data = json.loads(mpath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []

    loaded: List[Tuple[str, Dict[str, Any]]] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue
        fname = entry.get("file")
        expected_sha = entry.get("sha256")
        if not _is_safe_promoted_filename(fname):
            continue
        if not isinstance(expected_sha, str) or not _SHA256_RE.match(expected_sha):
            continue
        p = (tdir / fname).resolve()
        if p.parent != tdir or not p.is_file():
            continue
        raw_bytes = p.read_bytes()
        actual_sha = hashlib.sha256(raw_bytes).hexdigest()
        if actual_sha.lower() != expected_sha.lower():
            continue
        try:
            raw = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        loaded.append((fname.removesuffix(".api.json"), raw))
    return loaded


def load_allowlist(
    templates_dir: Path = DEFAULT_TEMPLATES_DIR,
    u55_specs_path: Path = DEFAULT_U55_SPECS,
    promoted: Optional[Sequence[Any]] = None,
    promoted_manifest: Optional[Path] = DEFAULT_PROMOTED_MANIFEST,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Load allowlisted template specs from disk + U55 fallback + verified promoted templates."""
    specs: Dict[str, Dict[str, Dict[str, Any]]] = {}

    u55_fallback: Dict[str, Any] = {}
    if u55_specs_path and Path(u55_specs_path).is_file():
        u55_fallback = json.loads(Path(u55_specs_path).read_text(encoding="utf-8"))

    tdir = Path(templates_dir) if templates_dir else None
    for name in CORE_TEMPLATE_NAMES:
        tpath = (tdir / f"{name}.api.json") if tdir else None
        if tpath and tpath.is_file():
            raw = json.loads(tpath.read_text(encoding="utf-8"))
            parsed = _graph_nodes(raw)
            if parsed and not _has_llm_node(parsed):
                specs[name] = parsed
                continue
        if name in u55_fallback:
            parsed = _graph_nodes(u55_fallback[name])
            if parsed and not _has_llm_node(parsed):
                specs[name] = parsed

    # Verified manifest entries (next to u55_allowlist_specs.json; Derrick-approved commits only)
    for name, raw in _load_promoted_manifest(promoted_manifest, tdir):
        parsed = _graph_nodes(raw)
        if parsed and not _has_llm_node(parsed):
            specs[name] = parsed

    for item in list(promoted or []):
        if isinstance(item, (str, Path)):
            p = Path(item)
            if not _is_safe_promoted_filename(p.name) or not p.is_file():
                continue
            name = p.name.removesuffix(".api.json")
            raw = json.loads(p.read_text(encoding="utf-8"))
        elif isinstance(item, tuple) and len(item) == 2:
            name, raw = str(item[0]), item[1]
            if name.endswith(".candidate"):
                continue
        else:
            continue
        parsed = _graph_nodes(raw)
        if parsed and not _has_llm_node(parsed):
            specs[name] = parsed

    return specs


def check_graph(
    graph: Any,
    *,
    templates_dir: Path = DEFAULT_TEMPLATES_DIR,
    u55_specs_path: Path = DEFAULT_U55_SPECS,
    promoted: Optional[Sequence[Any]] = None,
    promoted_manifest: Optional[Path] = DEFAULT_PROMOTED_MANIFEST,
) -> Tuple[bool, Optional[str], str]:
    """Return (allowed, matched_template_name, reason). Fail closed."""
    nodes = _graph_nodes(graph)
    if nodes is None:
        return False, None, "malformed ComfyUI API graph"

    llm = _has_llm_node(nodes)
    if llm:
        return False, None, f"refused LLM/rewriter node {llm}"

    ok_rtx, _ = _match_rtx_vsr(nodes)
    if ok_rtx:
        return True, RTX_VSR_NAME, ""

    specs = load_allowlist(
        templates_dir=templates_dir,
        u55_specs_path=u55_specs_path,
        promoted=promoted,
        promoted_manifest=promoted_manifest,
    )

    closest: List[Tuple[int, str, str]] = []
    for name, spec in specs.items():
        ok, err = _match_template(nodes, spec)
        if ok:
            return True, name, ""
        # Rank closest mismatch by node-ID overlap for a clear refusal message
        overlap = len(set(nodes.keys()) & set(spec.keys()))
        closest.append((overlap, name, err))

    if closest:
        closest.sort(key=lambda x: (-x[0], x[1]))
        _, best_name, best_err = closest[0]
        return False, None, f"graph not allowlisted (closest={best_name}: {best_err})"
    return False, None, "no allowlisted templates loaded"


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a ComfyUI API graph against the S2 allowlist.")
    ap.add_argument("graph_json", help="Path to request.api.json (or '-' for stdin)")
    ap.add_argument("--templates-dir", default=str(DEFAULT_TEMPLATES_DIR))
    ap.add_argument("--u55-specs", default=str(DEFAULT_U55_SPECS))
    ap.add_argument("--promoted-manifest", default=str(DEFAULT_PROMOTED_MANIFEST))
    ap.add_argument("--promoted", action="append", default=[], help="Additional promoted .api.json file")
    args = ap.parse_args(argv)

    raw_text = sys.stdin.read() if args.graph_json == "-" else Path(args.graph_json).read_text(encoding="utf-8")
    try:
        graph = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(f"REFUSE invalid JSON: {exc}")
        return 1

    ok, matched, reason = check_graph(
        graph,
        templates_dir=Path(args.templates_dir),
        u55_specs_path=Path(args.u55_specs),
        promoted=[Path(p) for p in args.promoted],
        promoted_manifest=Path(args.promoted_manifest),
    )
    if ok:
        print(f"ALLOW {matched}")
        return 0
    print(f"REFUSE {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
