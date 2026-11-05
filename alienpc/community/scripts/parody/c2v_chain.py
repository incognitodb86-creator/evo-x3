"""C2V continuation chaining for H3 parody pipeline (U6).

Chains multiple clips using Malcolm C2V continuation rules (contextLengthFrames=22,
one beat per clip, native C2V audio, no external MP3 remux) when length exceeds
single-clip ceiling.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

CONTEXT_LENGTH_FRAMES = 22  # Golden context overlap per Malcolm rules §2.9
DEFAULT_CLIP_FRAMES = 124   # Standard H3 grid frame length ((124 - 5) % 17 == 0)
SINGLE_CLIP_CEILING_S = 8.0  # Measured ceiling for single-clip generation


def plan_c2v_chain(
    total_length_s: float,
    fps: int = 24,
    clip_frames: int = DEFAULT_CLIP_FRAMES,
    context_frames: int = CONTEXT_LENGTH_FRAMES,
) -> Dict[str, Any]:
    """Plan continuation chain clips given desired total duration.

    Args:
        total_length_s: Desired total duration in seconds.
        fps: Frames per second (default: 24).
        clip_frames: Frames per clip (default: 124).
        context_frames: Overlap frames between continuation clips (default: 22).

    Returns:
        Dict containing:
            - is_chained: bool
            - clip_count: int
            - clips: list of clip spec dicts
            - total_frames: int (stitched total)
            - total_seconds: float (stitched duration)
    """
    total_target_frames = int(round(total_length_s * fps))

    # Single clip check
    if total_length_s <= SINGLE_CLIP_CEILING_S or total_target_frames <= clip_frames:
        return {
            "is_chained": False,
            "clip_count": 1,
            "clips": [
                {
                    "index": 0,
                    "tag": "clip_01",
                    "frames": clip_frames,
                    "is_continuation": False,
                    "context_length_frames": 0,
                    "effective_frames": clip_frames,
                    "effective_seconds": round(clip_frames / fps, 3),
                }
            ],
            "total_frames": clip_frames,
            "total_seconds": round(clip_frames / fps, 3),
        }

    # Multi-clip chain planning
    # Clip 0 gives `clip_frames` net frames.
    # Each subsequent clip gives `clip_frames - context_frames` net frames.
    net_continuation_frames = clip_frames - context_frames
    if net_continuation_frames <= 0:
        raise ValueError(f"clip_frames ({clip_frames}) must exceed context_frames ({context_frames})")

    needed_additional = max(0, total_target_frames - clip_frames)
    additional_clips = (needed_additional + net_continuation_frames - 1) // net_continuation_frames
    total_clips = 1 + additional_clips

    clips: List[Dict[str, Any]] = []
    current_stitched_frames = 0

    for i in range(total_clips):
        is_cont = i > 0
        ctx = context_frames if is_cont else 0
        eff = clip_frames - ctx
        current_stitched_frames += eff

        clips.append({
            "index": i,
            "tag": f"clip_{i+1:02d}",
            "frames": clip_frames,
            "is_continuation": is_cont,
            "context_length_frames": ctx,
            "effective_frames": eff,
            "effective_seconds": round(eff / fps, 3),
        })

    return {
        "is_chained": True,
        "clip_count": total_clips,
        "clips": clips,
        "total_frames": current_stitched_frames,
        "total_seconds": round(current_stitched_frames / fps, 3),
    }


def generate_c2v_requests(
    run_dir: Path,
    base_graph: Dict[str, Any],
    chain_plan: Dict[str, Any],
    base_prefix: str,
) -> List[Path]:
    """Generate per-clip request API json files for C2V continuation chain.

    Args:
        run_dir: Run directory root.
        base_graph: Base request API graph (for clip 0).
        chain_plan: Chain plan from plan_c2v_chain.
        base_prefix: Save prefix (e.g. community/parody_xxx).

    Returns:
        List of generated request.api.json paths.
    """
    c2v_dir = run_dir / "c2v"
    c2v_dir.mkdir(parents=True, exist_ok=True)
    generated_files: List[Path] = []

    for clip in chain_plan["clips"]:
        idx = clip["index"]
        tag = clip["tag"]
        clip_dir = c2v_dir / tag
        clip_dir.mkdir(parents=True, exist_ok=True)

        g = copy.deepcopy(base_graph)

        # Set per-clip length and prefix
        if "c0" in g and "inputs" in g["c0"]:
            g["c0"]["inputs"]["length"] = clip["frames"]
        if "save" in g and "inputs" in g["save"]:
            g["save"]["inputs"]["filename_prefix"] = f"{base_prefix}/{tag}"

        # If continuation, configure C2V node parameters if present
        if clip["is_continuation"]:
            # Malcolm rules §2.9: contextLengthFrames = 22
            if "c2v_context" in g:
                g["c2v_context"]["inputs"]["context_length_frames"] = clip["context_length_frames"]

        out_path = clip_dir / "request.api.json"
        out_path.write_text(json.dumps(g, indent=2, ensure_ascii=False), encoding="utf-8")
        generated_files.append(out_path)

    return generated_files
