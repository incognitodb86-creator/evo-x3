"""ALI-147 RS7 report support probe v3 (read-only, CPU only). 2026-10-22.

Reads the FIX4 graph on disk and prints, per clip: validated, duration, frames at 24 fps,
prompt sha256. clips_json is a JSON string of {"version": ..., "clips": [...]}.
No writes, no renders, no GPU call.

  python C:/AI/community/notes/ali147_rs7_fix4_state_probe_v3.py
"""
import json
import hashlib

P = r"C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json"
raw = open(P, encoding="utf-8").read()
g = json.loads(raw)
pack = json.loads(g["ext"]["inputs"]["clips_json"])
print("bytes", len(raw.encode("utf-8")), "nodes", len(g), "graph node ids:", sorted(g.keys()))
print("clips_json version:", pack.get("version"), "top-level keys:", sorted(pack.keys()))
clips = pack["clips"]
print("clips:", len(clips))
tot = 0
for i, c in enumerate(clips):
    dur = c.get("duration")
    fr = round(dur * 24) if dur is not None else None
    tot += fr or 0
    print(" clip", i + 1, "validated:", c.get("validated"), "duration:", dur,
          "frames@24:", fr, "prompt_chars:", len(str(c.get("prompt", ""))),
          "prompt sha256:", hashlib.sha256(str(c.get("prompt", "")).encode("utf-8")).hexdigest(),
          "keys:", sorted(c.keys()))
print("sum of clip frames @24 fps (raw, before seams):", tot)
for tid in sorted(g):
    nd = g[tid]
    print(" node", tid, nd["class_type"], {k: v for k, v in nd["inputs"].items() if not isinstance(v, list)})
print("dip: node 'a' LoadImage:", g["a"]["inputs"]["image"] if "a" in g else None)
