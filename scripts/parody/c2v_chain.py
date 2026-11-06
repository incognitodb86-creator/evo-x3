"""C2V continuation chaining for H3 parody pipeline (U6 & long-clip setup U1-U5).

Chains multiple clips using Malcolm C2V continuation rules (contextLengthFrames=22,
one beat per clip, native C2V audio, no external MP3 remux) when length exceeds
single-clip ceiling.
"""

from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

CONTEXT_LENGTH_FRAMES = 22  # Golden context overlap per Malcolm rules §2.9
DEFAULT_CLIP_FRAMES = 124   # Standard H3 grid frame length ((124 - 5) % 17 == 0)
SINGLE_CLIP_CEILING_S = 8.0  # Measured ceiling for single-clip generation

# C2V Availability Flag
# Native A/V carry is UNPROVEN on this box -> report unavailable, never claim carry
C2V_AVAILABLE: bool = False
C2V_STATUS: str = "UNPROVEN"
C2V_UNAVAILABLE_REASON: str = "native A/V carry is UNPROVEN on this box"


def frame_grid_ok(frames: int) -> bool:
    """H3 generation length grid: (f - 5) % 17 == 0 and 22 <= f <= DEFAULT_CLIP_FRAMES (U1 local constraint)."""
    return isinstance(frames, int) and 22 <= frames <= DEFAULT_CLIP_FRAMES and (frames - 5) % 17 == 0


class LengthHold(ValueError):
    """Intended length is not reachable with valid local clip budgets -> hold for D2/D3/D4 (KTD3)."""


def is_c2v_available() -> bool:
    """Return whether native C2V continuation is proven and available on this host.

    Always returns False because native A/V carry is UNPROVEN on this box.
    """
    return C2V_AVAILABLE


def get_c2v_status() -> Dict[str, Any]:
    """Get the current C2V status and rationale dict."""
    return {
        "available": C2V_AVAILABLE,
        "status": C2V_STATUS,
        "reason": C2V_UNAVAILABLE_REASON,
    }


def check_c2v_available() -> None:
    """Raise RuntimeError if C2V continuation is unproven / unavailable."""
    if not C2V_AVAILABLE:
        raise RuntimeError(f"C2V continuation unavailable: {C2V_UNAVAILABLE_REASON}")


def calculate_intended_length(total_length_s: float, fps: int = 24) -> Dict[str, Any]:
    """Calculate intended target frame count N_target from duration and fps.

    Rules:
        - T * fps nearest frame.
        - Ties round up (e.g. 0.5 -> 1.0).
        - Records unrounded frames, N_target, represented duration in seconds,
          signed delta in frames and signed delta in seconds.
        - Invariant: signed delta <= half a frame (|signed_delta_frames| <= 0.5).

    Args:
        total_length_s: Requested duration in seconds (T).
        fps: Target frames per second (default 24).

    Returns:
        Dict with keys:
            - total_length_s: float
            - fps: int
            - unrounded_frames: float
            - n_target: int
            - represented_duration_s: float
            - signed_delta_frames: float
            - signed_delta_s: float
    """
    if total_length_s <= 0:
        raise ValueError(f"total_length_s must be positive, got {total_length_s}")
    if fps <= 0:
        raise ValueError(f"fps must be positive, got {fps}")

    unrounded = float(total_length_s * fps)
    # Ties round up: floor(x + 0.5)
    n_target = int(math.floor(unrounded + 0.5))
    represented_duration_s = round(n_target / fps, 6)
    signed_delta_frames = round(n_target - unrounded, 6)
    signed_delta_s = round(represented_duration_s - total_length_s, 6)

    # Invariant: signed delta <= half a frame
    if abs(signed_delta_frames) > 0.5 + 1e-9:
        raise ValueError(
            f"Signed delta ({signed_delta_frames} frames) exceeds half a frame (+-0.5)"
        )

    return {
        "total_length_s": total_length_s,
        "fps": fps,
        "unrounded_frames": unrounded,
        "n_target": n_target,
        "represented_duration_s": represented_duration_s,
        "signed_delta_frames": signed_delta_frames,
        "signed_delta_s": signed_delta_s,
    }


def build_frame_ledger(
    clips: List[Dict[str, Any]],
    fps: int = 24,
    n_target: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Build and validate a frame ledger from planned/allocated clips.

    Ledger columns:
        - clip_id: Identifier of the clip/cell (e.g. 'clip_01')
        - index: 0-based sequence index
        - requested: target frames requested for generation
        - generated: frames produced by generator
        - context: overlap conditioning frames (0 for initial, context_frames for continuation)
        - removed_head: continuation head frames stripped at stitch seam
        - delivered: net delivered frames (generated - removed_head)
        - fps: frame rate
        - effective_seconds: delivered / fps
        - is_continuation: bool

    Invariants:
        - For every clip: delivered == generated - removed_head
        - For initial clip (index 0): context == 0, removed_head == 0
        - For every continuation clip (index > 0): removed_head == context (continuation context head removed exactly once)
        - If n_target is provided: sum(delivered) == n_target
    """
    ledger: List[Dict[str, Any]] = []
    total_delivered = 0

    for i, clip in enumerate(clips):
        clip_id = clip.get("tag", clip.get("clip_id", f"clip_{i+1:02d}"))
        requested = int(clip.get("requested", clip.get("frames", DEFAULT_CLIP_FRAMES)))
        generated = int(clip.get("generated", clip.get("frames", requested)))
        context = int(clip.get("context", clip.get("context_length_frames", 0)))
        removed_head = int(clip.get("removed_head", context if i > 0 else 0))
        delivered = int(clip.get("delivered", clip.get("effective_frames", generated - removed_head)))

        # Invariant 1: delivered == generated - removed_head
        if delivered != generated - removed_head:
            raise ValueError(
                f"Ledger mismatch for {clip_id}: delivered ({delivered}) != "
                f"generated ({generated}) - removed_head ({removed_head})"
            )

        # Invariant 2: continuation context head removed exactly once
        if i == 0:
            if context != 0 or removed_head != 0:
                raise ValueError(
                    f"Initial clip {clip_id} must have context=0 and removed_head=0 "
                    f"(got context={context}, removed_head={removed_head})"
                )
        else:
            if removed_head != context:
                raise ValueError(
                    f"Continuation clip {clip_id} context head must be removed exactly once: "
                    f"removed_head ({removed_head}) != context ({context})"
                )

        eff_sec = round(delivered / fps, 3)
        row = {
            "clip_id": clip_id,
            "index": i,
            "requested": requested,
            "generated": generated,
            "context": context,
            "removed_head": removed_head,
            "delivered": delivered,
            "fps": fps,
            "effective_seconds": eff_sec,
            "is_continuation": (i > 0),
        }
        ledger.append(row)
        total_delivered += delivered

    if n_target is not None and total_delivered != n_target:
        raise ValueError(
            f"Frame ledger invariant violated: sum(delivered)={total_delivered} != n_target={n_target}"
        )

    return ledger


def allocate_compensated_clips(
    total_length_s: float,
    fps: int = 24,
    clip_frames: int = DEFAULT_CLIP_FRAMES,
    context_frames: int = CONTEXT_LENGTH_FRAMES,
) -> Dict[str, Any]:
    """Compensated clip allocation so sum(delivered) = N_target.

    Each continuation context head is removed exactly once.

    Args:
        total_length_s: Desired total duration in seconds.
        fps: Frames per second (default: 24).
        clip_frames: Standard frame budget per clip (default: 124).
        context_frames: Overlap frames between continuation clips (default: 22).

    Returns:
        Dict containing:
            - is_chained: bool
            - clip_count: int
            - n_target: int
            - intended_length: dict from calculate_intended_length
            - clips: list of clip spec dicts with ledger fields
            - frame_ledger: list of ledger rows
            - total_frames: int (sum of delivered frames == n_target)
            - total_seconds: float (delivered / fps)
    """
    intended = calculate_intended_length(total_length_s, fps)
    n_target = intended["n_target"]

    if clip_frames <= context_frames:
        raise ValueError(
            f"clip_frames ({clip_frames}) must exceed context_frames ({context_frames})"
        )

    # Single clip check
    if total_length_s <= SINGLE_CLIP_CEILING_S or n_target <= clip_frames:
        if not frame_grid_ok(n_target):
            raise LengthHold(
                f"HOLD: N_target={n_target} is not a valid single-clip H3 length ((f-5)%17==0, <= {DEFAULT_CLIP_FRAMES}); "
                "revise the approved length via D2 - no padding/retime")
        clip_spec = {
            "index": 0,
            "tag": "clip_01",
            "requested": n_target,
            "generated": n_target,
            "context": 0,
            "removed_head": 0,
            "delivered": n_target,
            "frames": n_target,
            "is_continuation": False,
            "context_length_frames": 0,
            "effective_frames": n_target,
            "effective_seconds": round(n_target / fps, 3),
        }
        clips = [clip_spec]
        ledger = build_frame_ledger(clips, fps=fps, n_target=n_target)
        return {
            "is_chained": False,
            "clip_count": 1,
            "n_target": n_target,
            "intended_length": intended,
            "clips": clips,
            "frame_ledger": ledger,
            "total_frames": n_target,
            "total_seconds": round(n_target / fps, 3),
        }

    # Multi-clip compensated allocation
    # Clip 0 delivers clip_frames
    clips: List[Dict[str, Any]] = []
    clip_0_delivered = clip_frames
    clips.append({
        "index": 0,
        "tag": "clip_01",
        "requested": clip_frames,
        "generated": clip_frames,
        "context": 0,
        "removed_head": 0,
        "delivered": clip_0_delivered,
        "frames": clip_frames,
        "is_continuation": False,
        "context_length_frames": 0,
        "effective_frames": clip_0_delivered,
        "effective_seconds": round(clip_0_delivered / fps, 3),
    })

    remaining = n_target - clip_0_delivered
    net_continuation_frames = clip_frames - context_frames
    idx = 1

    while remaining > 0:
        tag = f"clip_{idx+1:02d}"
        if remaining >= net_continuation_frames:
            deliv = net_continuation_frames
            gen = clip_frames
            req = clip_frames
            remaining -= net_continuation_frames
        else:
            deliv = remaining
            gen = context_frames + deliv
            req = gen
            remaining = 0

        clips.append({
            "index": idx,
            "tag": tag,
            "requested": req,
            "generated": gen,
            "context": context_frames,
            "removed_head": context_frames,
            "delivered": deliv,
            "frames": gen,
            "is_continuation": True,
            "context_length_frames": context_frames,
            "effective_frames": deliv,
            "effective_seconds": round(deliv / fps, 3),
        })
        idx += 1

    bad = [c["tag"] for c in clips if not frame_grid_ok(c["generated"])]
    if bad:
        raise LengthHold(
            f"HOLD: N_target={n_target} needs off-grid generated lengths for {bad} "
            f"(continuations deliver multiples of 17 with context {context_frames}); revise length via D2/D3/D4")
    ledger = build_frame_ledger(clips, fps=fps, n_target=n_target)
    if sum(c["delivered"] for c in clips) != n_target:
        raise LengthHold(f"HOLD: allocation does not reach N_target={n_target}")

    return {
        "is_chained": True,
        "clip_count": len(clips),
        "n_target": n_target,
        "intended_length": intended,
        "clips": clips,
        "frame_ledger": ledger,
        "total_frames": n_target,
        "total_seconds": round(n_target / fps, 3),
    }


def allocate_planned_cuts(total_length_s: float, fps: int = 24) -> Dict[str, Any]:
    """Planned-cut allocation: zero context/removed head, every clip on the H3 grid, sum == N_target.

    Uses the fewest clips that can hit N_target exactly; otherwise raises LengthHold.
    """
    intended = calculate_intended_length(total_length_s, fps)
    n = intended["n_target"]
    max_m = (DEFAULT_CLIP_FRAMES - 5) // 17  # 7 -> 124
    k = max(1, math.ceil(n / DEFAULT_CLIP_FRAMES))
    while 5 * k + 17 * k <= n:
        rem = n - 5 * k
        if rem % 17 == 0:
            m = rem // 17
            if k <= m <= max_m * k:
                base, extra = divmod(m, k)
                ms = [base + (1 if i < extra else 0) for i in range(k)]
                clips = []
                for i, mi in enumerate(ms):
                    f = 5 + 17 * mi
                    clips.append({"index": i, "tag": f"clip_{i+1:02d}", "requested": f, "generated": f,
                                  "context": 0, "removed_head": 0, "delivered": f, "frames": f,
                                  "is_continuation": False, "context_length_frames": 0,
                                  "effective_frames": f, "effective_seconds": round(f / fps, 3),
                                  "method": "planned cut"})
                # planned cuts: no continuation heads; ledger rows built per clip
                ledger = [build_frame_ledger([c], fps=fps)[0] | {"index": c["index"], "is_continuation": False}
                          for c in clips]
                return {"is_chained": k > 1, "method": "planned cut", "clip_count": k, "n_target": n,
                        "intended_length": intended, "clips": clips, "frame_ledger": ledger,
                        "total_frames": n, "total_seconds": round(n / fps, 3)}
        k += 1
    raise LengthHold(f"HOLD: N_target={n} not reachable as a sum of H3 grid clip lengths; revise via D2")


def validate_continuation_context(
    predecessor_meta: Dict[str, Any],
    current_meta: Dict[str, Any],
    predecessor_clip_path: Optional[Union[str, Path]] = None,
) -> None:
    """Fail-closed validation of continuation context before chaining.

    Refuses invalid or corrupted context with descriptive ValueError or FileNotFoundError.

    Checks:
        1. Missing file: predecessor clip file must exist and be non-empty.
        2. Audio-only / video-only context: both streams required, single-stream context refused.
        3. Wrong fps / frames: fps must match; predecessor must have >= required context frames.
        4. Changed identity hash: identity sha256 / refmod hash must remain identical across seam.
        5. Incomplete predecessor: predecessor must have completed status and render_ok=True.

    Args:
        predecessor_meta: Metadata dict from predecessor cell (e.g. render_ok.json).
        current_meta: Metadata or spec dict for current continuation clip.
        predecessor_clip_path: Path to predecessor clip file (if not in predecessor_meta).

    Raises:
        FileNotFoundError: If predecessor clip file is missing.
        ValueError: If any validation rule fails.
    """
    # 1. Missing file check (fail-closed: a continuation needs a real predecessor clip)
    clip_path = predecessor_clip_path or predecessor_meta.get("clip_path")
    if clip_path is None:
        raise ValueError("fail-closed: predecessor clip path not supplied")
    if True:
        p = Path(clip_path)
        if not p.exists():
            raise FileNotFoundError(f"fail-closed: predecessor clip file missing: {p}")
        if p.is_file() and p.stat().st_size == 0:
            raise ValueError(f"fail-closed: predecessor clip file is 0 bytes: {p}")

    # 2. Incomplete predecessor check
    if predecessor_meta.get("render_ok") is False:
        raise ValueError("fail-closed: predecessor render_ok is False (incomplete predecessor)")
    if "status" in predecessor_meta and predecessor_meta["status"] not in ("complete", "ok", "success"):
        raise ValueError(f"fail-closed: predecessor status '{predecessor_meta['status']}' is incomplete")
    if predecessor_meta.get("render_ok") is not True and "status" not in predecessor_meta:
        raise ValueError("fail-closed: predecessor completion not recorded (render_ok/status missing)")

    # 3. Audio-only / video-only context (fail-closed)
    streams = predecessor_meta.get("streams")
    if isinstance(streams, list):
        has_v = any(s.get("codec_type") == "video" for s in streams)
        has_a = any(s.get("codec_type") == "audio" for s in streams)
    else:
        if "has_video" not in predecessor_meta or "has_audio" not in predecessor_meta:
            raise ValueError("fail-closed: predecessor stream evidence (streams/has_video/has_audio) missing")
        has_v = bool(predecessor_meta["has_video"])
        has_a = bool(predecessor_meta["has_audio"])

    if has_v and not has_a:
        raise ValueError("fail-closed: video-only context refused; continuation requires both video and audio")
    if has_a and not has_v:
        raise ValueError("fail-closed: audio-only context refused; continuation requires both video and audio")
    if not has_v and not has_a:
        raise ValueError("fail-closed: context contains neither video nor audio streams")

    # 4. Wrong fps / frames
    pred_fps = predecessor_meta.get("fps")
    curr_fps = current_meta.get("fps")
    if pred_fps is not None and curr_fps is not None and pred_fps != curr_fps:
        raise ValueError(f"fail-closed: fps mismatch: predecessor {pred_fps} != current {curr_fps}")

    req_context = current_meta.get("context_length_frames", current_meta.get("context", CONTEXT_LENGTH_FRAMES))
    pred_frames = predecessor_meta.get("frames", predecessor_meta.get("delivered_frames", predecessor_meta.get("delivered")))
    if pred_frames is not None and pred_frames < req_context:
        raise ValueError(
            f"fail-closed: predecessor frame count ({pred_frames}) less than required context frames ({req_context})"
        )

    # 5. Changed identity hash (fail-closed: at least one identity key must be on both sides)
    id_keys = ("identity_hash", "identity_sha256", "refmod_hash", "prompt_sha256_base", "reflora_sha256")
    if not any(k in predecessor_meta and k in current_meta for k in id_keys):
        raise ValueError("fail-closed: no identity hash recorded on both sides of the seam")
    for id_key in id_keys:
        if id_key in predecessor_meta and id_key in current_meta:
            if predecessor_meta[id_key] != current_meta[id_key]:
                raise ValueError(
                    f"fail-closed: identity hash mismatch on '{id_key}': "
                    f"{predecessor_meta[id_key]} != {current_meta[id_key]}"
                )



FRAME_COUNT_HOOK = None  # unit tests may inject a callable(path)->int (FG-5)

def count_decoded_video_frames(path: Path, ffprobe_cmd: Optional[list] = None) -> int:
    """Count decoded video frames via ffprobe ``nb_read_frames`` (KTD3 / FG-5).

    ``ffprobe_cmd`` or module ``FRAME_COUNT_HOOK`` may be injected by unit tests;
    production always shells out to ffprobe.
    """
    if FRAME_COUNT_HOOK is not None and ffprobe_cmd is None:
        return int(FRAME_COUNT_HOOK(path))
    import subprocess
    cmd = ffprobe_cmd or [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-count_frames",
        "-show_entries", "stream=nb_read_frames",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as exc:
        raise ValueError(f"ffprobe frame-count failed for {path}: {exc}") from exc
    if r.returncode != 0:
        raise ValueError(f"ffprobe frame-count failed rc={r.returncode} for {path}: {(r.stderr or '')[:300]}")
    raw = (r.stdout or "").strip().splitlines()
    if not raw or not raw[0].strip().isdigit():
        raise ValueError(f"ffprobe returned no nb_read_frames for {path}: {r.stdout!r}")
    return int(raw[0].strip())

def bridge_parody_stitch(
    run_dir: Union[Path, str],
    expected_frames: Optional[int] = None,
    expected_duration_s: Optional[float] = None,
    fps: int = 24,
    name: str = "parody_chain",
    xfade: float = 0.06,
    is_smoke: bool = False,
    method: Optional[str] = None,
) -> Dict[str, Any]:
    """Bridge to the existing take_chain_stitch.py pipeline.

    Builds the cell list, verifies expected duration and invariants, refuses
    method-smoke inputs, and delegates stitching to scripts/queue/take_chain_stitch.py.
    No second stitcher. Entire stitch body converts SystemExit -> ValueError (FG-6).
    ``expected_duration_s`` is required; N_actual comes from decoded frame count (FG-5).
    """
    if is_smoke or method in ("smoke", "method-smoke", "test-smoke"):
        raise ValueError("method-smoke inputs refused")

    run_path = Path(run_dir).resolve()
    if not run_path.is_dir():
        raise ValueError(f"Run directory not found: {run_path}")

    queue_dir = Path(__file__).resolve().parents[1] / "queue"
    if str(queue_dir) not in sys.path:
        sys.path.insert(0, str(queue_dir))
    import take_chain_stitch

    try:
        cs = take_chain_stitch.cells(run_path)
        if len(cs) < 2:
            raise ValueError(f"Need at least 2 cells to stitch chain, found {len(cs)}")

        trimmed_contexts = 0
        total_delivered = 0

        for i, c in enumerate(cs):
            meta = c.get("meta", {})
            if meta.get("is_smoke") or meta.get("method") in ("smoke", "method-smoke", "test-smoke"):
                raise ValueError("method-smoke inputs refused")

            if not meta:
                raise ValueError(f"stitch refused: {c['cell']} has no render_ok.json ledger")
            is_cont = bool(meta.get("is_continuation")) or int(
                meta.get("context", meta.get("context_length_frames", 0)) or 0) > 0
            if is_cont and not C2V_AVAILABLE:
                raise ValueError(
                    f"stitch refused: {c['cell']} is a C2V continuation but {C2V_UNAVAILABLE_REASON}")

            if i > 0:
                trim_count = meta.get("trim_count", 1 if not is_cont else None)
                if trim_count not in (0, 1) or (is_cont and trim_count != 1) or meta.get("double_trim", False):
                    raise ValueError(
                        "double-trim detected: continuation context must be removed exactly once")
                trimmed_contexts += 1

            if "delivered" in meta:
                deliv = int(meta["delivered"])
            elif "effective_frames" in meta:
                deliv = int(meta["effective_frames"])
            elif "frames" in meta:
                deliv = int(meta["frames"])
            else:
                raise ValueError(f"stitch refused: {c['cell']} ledger has no delivered/frames count")
            if not is_cont and "frames" in meta and int(meta["frames"]) != deliv:
                raise ValueError(
                    f"stitch refused: planned-cut cell {c['cell']} delivered {deliv} != generated "
                    f"{meta['frames']} (no head trim exists for a cut)")
            total_delivered += deliv

        if expected_frames is not None and total_delivered != expected_frames:
            raise ValueError(
                f"Sum of delivered frames ({total_delivered}) does not match expected_frames "
                f"({expected_frames})")

        if expected_duration_s is None:
            raise ValueError("expected_duration_s is required for product assembly (FG-5 / KTD3)")
        intended = calculate_intended_length(expected_duration_s, fps)
        if total_delivered != intended["n_target"]:
            raise ValueError(
                f"Sum of delivered frames ({total_delivered}) does not match N_target "
                f"({intended['n_target']})")

        provs = take_chain_stitch.uniform(cs)
        out_dir = run_path / "_stitch"
        out_dir.mkdir(exist_ok=True)
        take_chain_stitch.write_key(run_path, cs, out_dir)
        film = take_chain_stitch.build_film(cs, provs, out_dir, name, xfade)
        want_dur = sum(p["duration"] for p in provs)
        got = take_chain_stitch.probe(film)
        n_actual = count_decoded_video_frames(film)
        if n_actual != total_delivered:
            raise ValueError(
                f"assembly invariant failed: N_actual={n_actual} (decoded frames) != "
                f"sum(delivered)={total_delivered} (film duration={got['duration']:.3f}s @ {fps})")
    except SystemExit as exc:
        raise ValueError(f"stitch refused: {exc}") from exc

    return {
        "film": film,
        "cells": len(cs),
        "duration": got["duration"],
        "expected_duration": want_dur,
        "delta": got["duration"] - want_dur,
        "total_delivered_frames": total_delivered,
        "n_actual": n_actual,
        "key_path": out_dir / "key.csv",
    }



def plan_c2v_chain(
    total_length_s: float,
    fps: int = 24,
    clip_frames: int = DEFAULT_CLIP_FRAMES,
    context_frames: int = CONTEXT_LENGTH_FRAMES,
    compensated: bool = False,
) -> Dict[str, Any]:
    """Plan continuation chain clips given desired total duration.

    Args:
        total_length_s: Desired total duration in seconds.
        fps: Frames per second (default: 24).
        clip_frames: Frames per clip (default: 124).
        context_frames: Overlap frames between continuation clips (default: 22).
        compensated: If True, uses allocate_compensated_clips so sum(delivered) == N_target.

    Returns:
        Dict containing:
            - is_chained: bool
            - clip_count: int
            - clips: list of clip spec dicts
            - total_frames: int (stitched total)
            - total_seconds: float (stitched duration)
    """
    if compensated:
        return allocate_compensated_clips(
            total_length_s=total_length_s,
            fps=fps,
            clip_frames=clip_frames,
            context_frames=context_frames,
        )

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
