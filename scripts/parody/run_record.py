"""Run record builder and artifact manager for H3 parody pipeline (U7).

Ensures every run creates a standard self-contained run folder under runs/parody_<slug>_<ts>/
containing:
- clip.mp4
- prompt.txt
- assets.json (INDEX rows + status, RefMod slot/strength/copies, kept/dropped, stills, mode)
- request.api.json (+ optional c2v/ continuation configs)
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional


RUNS_ROOT = Path(r"C:\AI\community\runs")


def build_refmod_ledger(resolved: Dict[str, Any], graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the submitted loader slot ledger with the resolver path for each slot."""
    inputs = graph.get("refmods", {}).get("inputs", {})
    slots = resolved.get("refmod_slots", {})
    ledger: List[Dict[str, Any]] = []
    for i in range(1, 9):
        key = f"mod_{i}"
        ledger.append({
            "slot": i,
            "mod": inputs.get(key),
            "path": slots.get(key, {}).get("path", "(none)"),
            "strength": inputs.get(f"strength_{i}"),
            "copies": inputs.get(f"copies_{i}"),
        })
    return ledger


def _reflora_ledger(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    from reflora import reflora_ledger
    return reflora_ledger(graph)


def build_assets_record(
    resolved: Dict[str, Any],
    graph: Dict[str, Any],
    chain_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble structured asset ledger for assets.json."""
    # Extract dials for verification
    unet_name = graph.get("unet", {}).get("inputs", {}).get("unet_name", "")
    steps = graph.get("s0_sched", {}).get("inputs", {}).get("steps", 0)
    width = graph.get("c0", {}).get("inputs", {}).get("width", 768)
    height = graph.get("c0", {}).get("inputs", {}).get("height", 1344)
    seed = graph.get("noise", {}).get("inputs", {}).get("noise_seed", 0)

    return {
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mode": resolved.get("mode"),
        "index_status": resolved.get("index_status"),
        "index_flag": resolved.get("index_flag"),
        "names": resolved.get("names", []),
        "character": resolved.get("character"),
        "actor": resolved.get("actor"),
        "tone": resolved.get("tone", "parody"),
        "description": resolved.get("description"),
        "index_rows": resolved.get("index_rows", []),
        "refmod_slots": resolved.get("refmod_slots", {}),
        "refmod_ledger": build_refmod_ledger(resolved, graph),
        "loaded_refmods": resolved.get("loaded_refmods", []),
        "dropped_refmods": resolved.get("dropped_refmods", []),
        "stills": resolved.get("stills", []),
        "audio_refs": resolved.get("audio_refs", []),
        "dials": {
            "unet": unet_name,
            "steps": steps,
            "canvas": f"{width}x{height}",
            "seed": seed,
        },
        "identity_layers": resolved.get("identity_layers", []),
        "reflora": resolved.get("reflora", {}),
        "reflora_ledger": _reflora_ledger(graph),
        "cond_picture": graph.get("img", {}).get("inputs", {}).get("image")
        if graph.get("c0", {}).get("inputs", {}).get("ref_images.ref_image_1") == ["img", 0] else None,
        "cond_source_path": (resolved.get("cond") or {}).get("cond_source_path"),
        "cond_input_name": (resolved.get("cond") or {}).get("cond_input_name"),
        "cond_sha256": (resolved.get("cond") or {}).get("cond_sha256"),
        "chain_plan": chain_plan,
    }


def save_run_record(
    run_dir: Path,
    resolved: Dict[str, Any],
    prompt: str,
    graph: Dict[str, Any],
    chain_plan: Optional[Dict[str, Any]] = None,
    clip_source: Optional[Path] = None,
    cond_meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Path]:
    """Write all standard run artifacts into run_dir.

    Returns:
        Dict mapping artifact name to Path.
    """
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. request.api.json
    req_file = run_dir / "request.api.json"
    req_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. prompt.txt (exempt from no-prompt-files rule as run output)
    prompt_file = run_dir / "prompt.txt"
    prompt_file.write_text(prompt, encoding="utf-8")

    if cond_meta:
        resolved = dict(resolved)
        resolved["cond"] = cond_meta
    # 3. assets.json
    assets_data = build_assets_record(resolved, graph, chain_plan)
    assets_file = run_dir / "assets.json"
    assets_file.write_text(json.dumps(assets_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4. clip.mp4
    clip_file = run_dir / "clip.mp4"
    if clip_source and Path(clip_source).is_file():
        shutil.copyfile(clip_source, clip_file)

    # 5. C2V sub-folder if chained
    if chain_plan and chain_plan.get("is_chained"):
        from c2v_chain import generate_c2v_requests
        base_prefix = graph.get("save", {}).get("inputs", {}).get("filename_prefix", "community/parody")
        generate_c2v_requests(run_dir, graph, chain_plan, base_prefix)

    return {
        "request": req_file,
        "prompt": prompt_file,
        "assets": assets_file,
        "clip": clip_file,
    }


def verify_run_artifacts(run_dir: Path, require_clip: bool = True) -> Dict[str, bool]:
    """Verify presence of DoD required artifacts in run folder."""
    checks = {
        "request.api.json": (run_dir / "request.api.json").is_file(),
        "prompt.txt": (run_dir / "prompt.txt").is_file(),
        "assets.json": (run_dir / "assets.json").is_file(),
    }
    if require_clip:
        checks["clip.mp4"] = (run_dir / "clip.mp4").is_file()

    return checks
