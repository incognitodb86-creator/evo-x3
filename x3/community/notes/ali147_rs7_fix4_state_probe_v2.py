"""ALI-147 RS7 report support probe v2 (read-only, CPU only). 2026-10-22.

Dumps the FIX4 Extender clip structure as it is on disk, without assuming a schema:
clips_json parses to a container whose elements can be dicts or strings.

  python C:/AI/community/notes/ali147_rs7_fix4_state_probe_v2.py
"""
import json
import hashlib

P = r"C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json"
raw = open(P, encoding="utf-8").read()
g = json.loads(raw)
n = g["ext"]["inputs"]
print("bytes", len(raw.encode("utf-8")), "nodes", len(g))
cj = n["clips_json"]
print("clips_json python type:", type(cj).__name__, "len:", len(cj))
clips = json.loads(cj) if isinstance(cj, str) else cj
print("parsed type:", type(clips).__name__, "len:", len(clips))
for i, c in enumerate(clips):
    print("element", i, "type:", type(c).__name__, "len:", len(c))
    if isinstance(c, str):
        sub = None
        try:
            sub = json.loads(c)
        except Exception as e:
            print("  inner json.loads fails:", type(e).__name__, e)
        if sub is not None:
            print("  inner parsed type:", type(sub).__name__, "len:", len(sub))
            items = sub if isinstance(sub, list) else [sub]
            for j, item in enumerate(items):
                if isinstance(item, dict):
                    print("   sub", j, "keys:", sorted(item.keys()))
                    print("     validated:", item.get("validated"), "duration:", item.get("duration"),
                          "prompt sha256:", hashlib.sha256(str(item.get("prompt", "")).encode("utf-8")).hexdigest()[:16])
                else:
                    print("   sub", j, "type:", type(item).__name__, "head:", str(item)[:120])
        else:
            print("  head:", c[:200].replace("\n", "\\n"))
    elif isinstance(c, dict):
        print("  keys:", sorted(c.keys()), "validated:", c.get("validated"), "duration:", c.get("duration"))
print("ext keys:", sorted(n.keys()))
print("name:", n.get("name"), "seed:", n.get("seed"), "target_resolution:", n.get("target_resolution"),
      "target_fps:", n.get("target_fps"), "target_encoding_mbps:", n.get("target_encoding_mbps"))
print("save filename_prefix:", g["save"]["inputs"]["filename_prefix"])
print("c1 LoadImage:", g["c1"]["inputs"]["image"])
