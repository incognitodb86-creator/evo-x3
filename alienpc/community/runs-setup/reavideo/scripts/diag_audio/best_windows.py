import json
from pathlib import Path

bd = json.loads(Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2\breakdown.json").read_text(encoding="utf-8"))
raw = ((bd.get("audio") or {}).get("voice") or {}).get("segments") or []
segs = []
for item in raw:
    if isinstance(item, (list, tuple)) and len(item) >= 2:
        a, b = float(item[0]), float(item[1])
        if b > a:
            segs.append((a, b))
print("voice_segments_n", len(segs), "span", (min(s[0] for s in segs) if segs else None, max(s[1] for s in segs) if segs else None))

def overlap(start, duration, segments):
    end = start + duration
    total = 0.0
    n = 0
    for a, b in segments:
        o = max(0.0, min(end, b) - max(start, a))
        if o > 0:
            n += 1
            total += o
    return n, total

def best_voice_window(start, dur, cap_s, segments):
    if dur <= cap_s:
        return start, dur, overlap(start, dur, segments)
    if not segments:
        return start, cap_s, overlap(start, cap_s, segments)
    best_score = -1.0
    best_start = start
    t = start
    end = start + dur
    step = 0.25
    while t + 1e-6 < end:
        win = min(cap_s, end - t)
        _, score = overlap(t, win, segments)
        if score > best_score:
            best_score = score
            best_start = t
        t += step
    win = min(cap_s, end - best_start)
    return best_start, win, overlap(best_start, win, segments)

cap_s = 362 / 24.0
print("cap_s", cap_s)
for sid, start, end, dur in [
    ("shot_029", 318.2, 379.833, 61.633),
    ("shot_058", 708.733, 764.15, 55.417),
]:
    bstart, bwin, (n, tot) = best_voice_window(start, dur, cap_s, segs)
    first_n, first_tot = overlap(start, cap_s, segs)
    print({
        "id": sid,
        "shot_start": start,
        "shot_end": end,
        "shot_dur": dur,
        "intended_window_start": round(bstart, 3),
        "intended_window_end": round(bstart + bwin, 3),
        "intended_window_dur": round(bwin, 3),
        "voice_segs_in_intended": n,
        "voice_overlap_s_intended": round(tot, 3),
        "first_15s_start": start,
        "first_15s_voice_segs": first_n,
        "first_15s_voice_overlap_s": round(first_tot, 3),
        "offset_from_vocals_t0_if_unwindowed": 0.0,
        "delta_vs_other_needed": None,
    })
print("delta_intended_starts", round(abs(best_voice_window(708.733, 55.417, cap_s, segs)[0] - best_voice_window(318.2, 61.633, cap_s, segs)[0]), 3))
