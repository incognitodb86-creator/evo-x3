import json
from pathlib import Path
bd = json.loads(Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2\breakdown.json").read_text(encoding="utf-8"))
voice = (bd.get("audio") or {}).get("voice")
print("voice_type", type(voice).__name__)
if isinstance(voice, dict):
    print("voice_keys", sorted(voice.keys()))
    segs = voice.get("segments")
    print("segments_type", type(segs).__name__, "n", len(segs) if isinstance(segs, list) else None)
    if isinstance(segs, list) and segs:
        print("seg0_type", type(segs[0]).__name__)
        def overlap_count(start, end):
            n = 0
            tot = 0.0
            for item in segs:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    a, b = float(item[0]), float(item[1])
                elif isinstance(item, dict):
                    a = float(item.get("start") or item.get("t") or 0)
                    if "end" in item:
                        b = float(item["end"])
                    elif "dur" in item or "duration" in item:
                        b = a + float(item.get("dur") or item.get("duration"))
                    else:
                        continue
                else:
                    continue
                o = max(0.0, min(end, b) - max(start, a))
                if o > 0:
                    n += 1
                    tot += o
            return n, tot
        for sid, s, e in [("shot_029", 318.2, 379.833), ("shot_058", 708.733, 764.15)]:
            n, tot = overlap_count(s, e)
            n15, tot15 = overlap_count(s, s + 15.083)
            print(sid, "voice_segs_in_full_shot", n, "overlap_s", round(tot, 3), "in_first_15s", n15, "overlap_s", round(tot15, 3))
    else:
        print("no segments")
        # other voice scalars
        for k, v in voice.items():
            if k == "segments":
                continue
            if isinstance(v, str) and len(v) > 80:
                print("voice", k, "str_len", len(v))
            elif isinstance(v, (dict, list)):
                print("voice", k, type(v).__name__, len(v))
            else:
                print("voice", k, v)
elif voice is not None:
    print("voice_non_dict", type(voice).__name__)

for s in bd["shots"]:
    if s.get("id") in ("shot_058", "shot_029"):
        print(s.get("id"), "start", s.get("start"), "end", s.get("end"), "dur", s.get("duration"), "start_frame", s.get("start_frame"), "end_frame", s.get("end_frame"), "talk_share", s.get("talk_share"), "sung", s.get("sung"))

plan = (bd.get("audio_plan") or {}).get("plan") or []
print("plan_n", len(plan))
for i, item in enumerate(plan):
    rec = {"i": i, "keys": sorted(item.keys()), "track": item.get("track"), "rule": item.get("rule"), "source": item.get("source")}
    for k in ("what", "how", "real_material"):
        v = item.get(k)
        rec[k] = ("<str len=%d>" % len(v) if isinstance(v, str) and len(v) >= 60 else v)
    rec["lines_n"] = len(item["lines"]) if isinstance(item.get("lines"), list) else type(item.get("lines")).__name__
    segs = item.get("segments") or []
    rec["segments_n"] = len(segs)
    if segs and isinstance(segs[0], dict):
        rec["seg0_keys"] = sorted(segs[0].keys())
        rec["seg0_timing"] = {k: segs[0].get(k) for k in segs[0] if k in ("start", "end", "t", "dur", "duration", "offset", "type")}
    print(rec)
