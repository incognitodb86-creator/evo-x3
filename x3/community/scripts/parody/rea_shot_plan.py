#!/usr/bin/env python3
"""REA C2: shot plan helpers for the H3 parody batch.

Turns a shot's duration (plus the onset beats that REA C1 measured) into
clip-length plan parts on the ComfyUI 17n+5 frame grid, translates free-text
camera notes into the H3 vocabulary, freezes the cast/identity lock for a
batch, and writes the batch card that Derrick replies GO to.

Frame arithmetic is reused from build_request (H3_FPS, SINGLE_CLIP_MAX_FRAMES,
H3_MIN_FRAMES, align_h3_frames) and the Flux naming from flux_still, so this
module cannot drift from the builder. stdlib + numpy only, offline.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import build_request as br
import flux_still

# --- constants (all derived from the builder's own limits) -------------------
H3_MIN_CLIP_FRAMES = int(br.H3_MIN_FRAMES)  # 56
SINGLE_CLIP_MAX_FRAMES = int(br.SINGLE_CLIP_MAX_FRAMES)  # 243 on 16 GB
BEAT_WINDOW_SEC = 1.0  # a cut may move at most this far onto a beat
OC_CHARACTERS = ("fcsydny", "fcmegan")  # case-insensitive OC lane cast
CANVAS_BY_ASPECT = {"9:16": [768, 1344], "16:9": [1344, 768]}
SUFFIXES = "abcdefghijklmnopqrstuvwxyz"

GO_LINE = "Reply GO to run this batch."


# --- 1) frame plan ----------------------------------------------------------

def _beat_frames(beats: Optional[Sequence[float]], shot_start: float) -> List[int]:
    """Beat times (absolute seconds) -> frame offsets inside the shot."""
    out: List[int] = []
    for b in beats or []:
        try:
            out.append(int(round((float(b) - float(shot_start)) * br.H3_FPS)))
        except (TypeError, ValueError):
            continue
    return sorted(out)


def _nominal_take(remaining: int, cap: int, min_frames: int) -> int:
    """Real frames this part should consume before looking for a beat."""
    if remaining <= cap:
        return remaining
    if remaining - cap < min_frames:
        # a stubby tail is worse than two even parts, so split the remainder
        return min(int(math.ceil(remaining / 2.0)), cap)
    return cap


def _cut_take(start: int, remaining: int, cap: int, min_frames: int,
              beat_frames: Sequence[int], window_frames: int) -> int:
    """Frames for the part starting at `start`, nudged onto the nearest beat."""
    nominal = _nominal_take(remaining, cap, min_frames)
    if remaining <= cap or not beat_frames:
        return nominal
    target = start + nominal
    lo, hi = start + 1, start + cap
    candidates = [b for b in beat_frames
                  if lo <= b <= hi and abs(b - target) <= window_frames]
    if not candidates:
        return nominal
    best = min(candidates, key=lambda b: (abs(b - target), b))
    return best - start


def plan_frames(seconds: float, beats: Optional[Sequence[float]] = None,
                shot_start: float = 0.0) -> List[Dict[str, Any]]:
    """Plan the clip parts for one shot of `seconds` (absolute start `shot_start`).

    Every part carries the aligned (17n+5, <= SINGLE_CLIP_MAX_FRAMES) frame
    length the graph must render, plus `trim_to_frames` whenever the real shot
    footage is shorter than what gets rendered. Parts longer than one clip get
    a letter `suffix` and `continue_from` (the previous suffix) so the builder
    can chain them; cuts move onto the nearest supplied beat within
    BEAT_WINDOW_SEC when beats are given.
    """
    if seconds is None:
        raise ValueError("seconds is required")
    total = int(round(float(seconds) * br.H3_FPS))
    if total < 1:
        raise ValueError(f"seconds must be positive, got {seconds!r}")
    cap = SINGLE_CLIP_MAX_FRAMES

    if total < H3_MIN_CLIP_FRAMES:
        return [{"frames": H3_MIN_CLIP_FRAMES, "trim_to_frames": total}]
    if total <= cap:
        aligned = br.align_h3_frames(total)
        part: Dict[str, Any] = {"frames": aligned}
        if aligned > total:
            part["trim_to_frames"] = total
        return [part]

    beat_frames = _beat_frames(beats, shot_start)
    window = int(round(BEAT_WINDOW_SEC * br.H3_FPS))
    parts: List[Dict[str, Any]] = []
    start = 0
    prev: Optional[str] = None
    i = 0
    while start < total:
        take = _cut_take(start, total - start, cap, H3_MIN_CLIP_FRAMES, beat_frames, window)
        suffix = SUFFIXES[i] if i < len(SUFFIXES) else f"z{i}"
        parts.append({
            "frames": br.align_h3_frames(take),
            "trim_to_frames": take,
            "suffix": suffix,
            "continue_from": prev,
        })
        start += take
        prev = suffix
        i += 1
    return parts


# --- 2) camera vocabulary ---------------------------------------------------

_SPEED_RULES = (
    ("slow", r"\bslow(?:ly)?\b|\bgentle(?:ly)?\b|\bsubtle(?:ly)?\b"),
    ("fast", r"\bquick(?:ly)?\b|\bfast\b|\bwhip(?:py|ping)?\b|\brapid(?:ly)?\b"),
)
_AMPLITUDE_RULES = (
    ("small", r"\bslight(?:ly)?\b|\bsmall\b|\bsubtle(?:ly)?\b"),
    ("large", r"\bbig\b|\bwide(?:ly)?\b|\blarge\b|\bsweeping\b"),
)
# most specific move first; static/held/tripod is checked last and is also the
# fallback for text we cannot map.
_MOVE_RULES = (
    ("pan-left", r"\bpan(?:s|ning)?[\s-]*left\b|\bleft[\s-]*pan\b"),
    ("pan-right", r"\bpan(?:s|ning)?[\s-]*right\b|\bright[\s-]*pan\b"),
    ("tilt-up", r"\btilt(?:s|ing|ed)?[\s-]*up\b|\bup[\s-]*tilt\b"),
    ("tilt-down", r"\btilt(?:s|ing|ed)?[\s-]*down\b|\bdown[\s-]*tilt\b"),
    ("push-in", r"\bpush(?:es|ed)?[\s-]*in\b|\bdolly[\s-]*in\b|\bzoom[\s-]*in\b"),
    ("pull-back", r"\bpull(?:s|ed|back|-back)?\b|\bdolly[\s-]*out\b|\bzoom[\s-]*out\b"),
    ("orbit", r"\borbit(?:s|ed|ing)?\b|\barc(?:s|ing)?\b"),
    ("handheld", r"\bhandheld\b|\bshake(?:s|d|y|ing)?\b"),
    ("held static", r"\bstatic\b|\block(?:ed|ed-off|-off)?\b|\bheld\b|\btripod\b"),
)


def _pick(text: str, rules) -> Optional[str]:
    for word, pat in rules:
        if re.search(pat, text):
            return word
    return None


def camera_vocab(move: str) -> str:
    """Free-text camera note -> H3 words (move + speed + amplitude)."""
    text = str(move or "").strip().lower()
    if not text:
        return "held static"
    name = _pick(text, _MOVE_RULES)
    if name is None or name == "held static":
        return "held static"
    speed = _pick(text, _SPEED_RULES) or "medium"
    amp = _pick(text, _AMPLITUDE_RULES) or "medium"
    return f"{speed} {name} with {amp} amplitude"


# --- 3) cast lock -----------------------------------------------------------

def shot_view(shot: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
    """Normalized view of one shot dict from a breakdown/request."""
    sid = str(shot.get("shot_id") or shot.get("id") or f"shot{index + 1}")
    seconds = shot.get("seconds")
    if seconds is None:
        seconds = shot.get("duration")
    if seconds is None and shot.get("start") is not None and shot.get("end") is not None:
        seconds = float(shot["end"]) - float(shot["start"])
    if seconds is None and shot.get("frames") is not None:
        seconds = int(shot["frames"]) / float(br.H3_FPS)
    if seconds is None:
        raise ValueError(f"shot {sid} has no seconds/duration/start+end/frames")
    start = shot.get("shot_start")
    if start is None:
        start = shot.get("start")
    beats = shot.get("beats")
    if beats is None:
        beats = shot.get("onsets")
    camera = shot.get("camera")
    if camera is None:
        camera = shot.get("camera_move")
    if camera is None:
        camera = shot.get("camera_h3")
    return {
        "shot_id": sid,
        "seconds": float(seconds),
        "shot_start": float(start or 0.0),
        "beats": list(beats or []),
        "camera": str(camera or ""),
    }


def build_cast_lock(names: Optional[Sequence[str]], character: Optional[str],
                    lane: str, aspect: str, shots: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Freeze cast identity, canvas and per-shot overrides for one batch."""
    clean_names = [str(n).strip() for n in (names or []) if str(n or "").strip()]
    char = str(character).strip() if character is not None and str(character).strip() else None
    if not clean_names and not char:
        raise ValueError("build_cast_lock needs names or character, got neither")
    key = str(aspect).strip()
    if key not in CANVAS_BY_ASPECT:
        raise ValueError(f"aspect must be 9:16 or 16:9, got {aspect!r}")

    if clean_names:
        resolved_lane = "parody"
    elif char and char.lower() in OC_CHARACTERS:
        resolved_lane = "oc"
    else:
        resolved_lane = str(lane or "").strip() or "oc"

    refmod: Optional[str] = None
    lora: Optional[str] = None
    lora_strength: Optional[float] = None
    mode = "none"
    if clean_names:
        refmod, stack = flux_still._hybrid_stack_for_name(clean_names[0])
        lora = str(stack.get("name", "")) or None
        lora_strength = stack.get("strength")
        mode = "hybrid"

    shot_overrides: List[Dict[str, Any]] = []
    for i, raw in enumerate(shots or []):
        view = shot_view(raw, i)
        shot_overrides.append({
            "shot_id": view["shot_id"],
            "parts": plan_frames(view["seconds"], view["beats"], view["shot_start"]),
            "camera_h3_vocab": camera_vocab(view["camera"]),
        })

    return {
        "lane": resolved_lane,
        "aspect": key,
        "canvas": list(CANVAS_BY_ASPECT[key]),
        "flux_identity": {
            "mode": mode,
            "refmod": refmod,
            "lora": lora,
            "lora_strength": lora_strength,
            "names": clean_names,
        },
        "h3_identity": {
            "allow_audio_ref": resolved_lane != "parody",
            "names": clean_names,
            "character": char,
        },
        "shot_overrides": shot_overrides,
    }


# --- 4) batch card ----------------------------------------------------------

def write_batch_card(batch_dir: Path, cast_lock: Dict[str, Any],
                     shots: Optional[Sequence[Dict[str, Any]]] = None) -> Path:
    """Write `batch_card.md` (one table row per shot part) and return its path."""
    out_dir = Path(batch_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    flux = dict(cast_lock.get("flux_identity") or {})
    h3 = dict(cast_lock.get("h3_identity") or {})
    fallback_cam = {}
    for i, raw in enumerate(shots or []):
        try:
            view = shot_view(raw, i)
        except ValueError:
            continue
        fallback_cam[view["shot_id"]] = camera_vocab(view["camera"])
    w, h = (cast_lock.get("canvas") or [768, 1344])[:2]

    lines = [
        "# Batch card",
        "",
        f"- lane: {cast_lock.get('lane', '')}",
        f"- aspect: {cast_lock.get('aspect', '')}  canvas: {int(w)}x{int(h)}",
        f"- flux: {flux.get('mode', 'none')} refmod={flux.get('refmod') or '-'} "
        f"lora={flux.get('lora') or '-'}",
        f"- h3: allow_audio_ref={bool(h3.get('allow_audio_ref'))} "
        f"names={','.join(h3.get('names') or []) or '-'} character={h3.get('character') or '-'}",
        "",
        "| shot | seconds | frames | trim | camera | flux mode |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for override in cast_lock.get("shot_overrides") or []:
        sid = str(override.get("shot_id", ""))
        camera = str(override.get("camera_h3_vocab") or fallback_cam.get(sid) or "held static")
        for part in override.get("parts") or []:
            label = f"{sid}{part['suffix']}" if part.get("suffix") else sid
            real = int(part.get("trim_to_frames") or part.get("frames") or 0)
            trim = part.get("trim_to_frames")
            lines.append(
                f"| {label} | {real / float(br.H3_FPS):.3f} | {int(part.get('frames', 0))} | "
                f"{int(trim) if trim is not None else '-'} | {camera} | {flux.get('mode', 'none')} |"
            )
    lines.extend(["", GO_LINE, ""])
    path = out_dir / "batch_card.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
