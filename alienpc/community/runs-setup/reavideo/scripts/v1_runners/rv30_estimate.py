
"""Dry-pack the full hotel_vlm2 breakdown (tile + 362f) and print pack counts only."""
from __future__ import annotations
import json, sys
from pathlib import Path
from h3max_bridge import filter_shots, normalize_breakdown, pack_shots, parse_shot_ids, slice_long_shots, snap_frames

bd_path = Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2\breakdown.json")
audio = Path(r"C:\Users\derek\forge\reavideo\out\hotel14sav80\stems\vocals.wav")
bd = json.loads(bd_path.read_text(encoding="utf-8"))
tiled = slice_long_shots(bd, max_frames=362, mode="tile")
norm = normalize_breakdown(tiled, audio_stem=audio if audio.is_file() else None, breakdown_dir=bd_path.parent)
packs = pack_shots(norm, max_frames=362)
from collections import Counter
frames = Counter(p.frames for p in packs)
dur = sum(p.duration_s for p in packs)
audio_s = sum(p.audio_duration_s for p in packs)
# estimated wall: 2-pass 124f ~ 2.75 min midpoint of 2.5-3; scale linearly with frames
min_per_124 = 2.5
max_per_124 = 3.0
def est(minutes_per_124):
    return sum((p.frames / 124.0) * minutes_per_124 for p in packs)
print(json.dumps({
    "source_shots": len(bd["shots"]),
    "source_duration_s": bd.get("summary", {}).get("duration") or bd.get("source", {}).get("duration"),
    "tiled_windows": len(tiled["shots"]),
    "packs": len(packs),
    "frames_hist": dict(sorted(frames.items())),
    "packed_duration_s": round(dur, 3),
    "packed_audio_s": round(audio_s, 3),
    "est_wall_min_low": round(est(min_per_124), 1),
    "est_wall_min_high": round(est(max_per_124), 1),
    "est_note": "linear scale from ~2.5-3.0 min per 2-pass 124f clip; 362f ~2.92x",
}, indent=2))
