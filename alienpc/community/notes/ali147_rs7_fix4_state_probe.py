"""ALI-147 RS7 report support probe (read-only, CPU only). 2026-10-22.

Prints the CURRENT state of the FIX4 graph on disk (the clip list the Extender refused), so
REPORT.md quotes measured values instead of narration. No writes, no renders, no GPU call.

  python C:/AI/community/notes/ali147_rs7_fix4_state_probe.py
"""
import json

P = r"C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json"
raw = open(P, encoding="utf-8").read()
g = json.loads(raw)
n = g["ext"]["inputs"]
print("bytes", len(raw.encode("utf-8")), "nodes", len(g))
cj = n["clips_json"]
print("clips_json type:", type(cj).__name__, "is string:", isinstance(cj, str))
clips = json.loads(cj) if isinstance(cj, str) else cj
print("clips:", len(clips))
tot = 0
for i, c in enumerate(clips):
    dur = c.get("duration")
    fr = None
    if dur is not None:
        fr = dur * 24
        tot += round(fr)
    print("  clip", i + 1, "validated:", c.get("validated"), "duration:", dur,
          "seconds@24fps:", round(fr) if fr is not None else None, "prompt sha256:",
          __import__("hashlib").sha256(str(c.get("prompt", "")).encode("utf-8")).hexdigest()[:16],
          "keys:", sorted(c.keys()))
print("sum of clip frames @24 fps (raw, before seams):", tot)
print("name:", n.get("name"), "seed:", n.get("seed"), "target_resolution:", n.get("target_resolution"),
      "target_fps:", n.get("target_fps"), "target_encoding_mbps:", n.get("target_encoding_mbps"))
print("save filename_prefix:", g["save"]["inputs"]["filename_prefix"])
print("c1 LoadImage:", g["c1"]["inputs"]["image"])
