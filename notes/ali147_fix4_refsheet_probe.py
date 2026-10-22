"""ALI-147 FIX4_PROOF diagnostics (read-only, CPU only, no GPU, no ComfyUI call).

Why the FIX4 full_batch Ref2VA run raised "Ref2VA clip 1 is marked Validated but
its disk cache is missing": does the graph's own clips_json carry a validated
flag, or does it come from the Extender's persisted per-owner project state?

Prints: the clips_json validated flags + clip keys, and the Extender cache
namespace for the node id used in the graph.
"""
import json
import os
import re

GRAPH = r"C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json"
CACHE = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/ComfyUI_MiniMax_H3_Extender/cache"

graph = json.load(open(GRAPH, encoding="utf-8"))
ext_id = [k for k, v in graph.items() if v.get("class_type") == "MiniMaxH3Extender"]
print("extender node ids in graph:", ext_id)
inp = graph[ext_id[0]]["inputs"]
cj = inp["clips_json"]
print("clips_json python type:", type(cj).__name__)
payload = json.loads(cj) if isinstance(cj, str) else cj
print("payload top-level keys:", sorted(payload.keys()))
clips = payload.get("clips", [])
print("clip count:", len(clips))
for c in clips:
    print(" clip keys:", sorted(c.keys()))
    print("  id:", c.get("id"), "name:", c.get("name"),
          "validated key present:", "validated" in c,
          "validated value:", c.get("validated", "<absent>"),
          "duration:", c.get("duration"), "seed:", c.get("seed"),
          "seed_mode:", c.get("seed_mode"))
    d = 0.0
    for f in re.findall(r'"duration":\s*([0-9.]+)', json.dumps(c)):
        pass
    print("  prompt len:", len(c.get("prompt", "")))
print("raw 'validated' substring count in clips_json string:",
      (cj if isinstance(cj, str) else json.dumps(cj)).count("validated"))

# The Extender names its on-disk project/cache after the node id (owner id):
# cache/chain_extender_<node id>.* - so a reused node id inherits a prior state.
ns = "chain_extender_" + ext_id[0]
print("cache namespace prefix:", ns)
for f in sorted(os.listdir(CACHE)):
    if f.startswith(ns):
        p = os.path.join(CACHE, f)
        st = os.stat(p)
        print("  exists:", f, "bytes:", st.st_size)
        if f.endswith(".json"):
            txt = open(p, encoding="utf-8", errors="replace").read()
            print("   json keys:", sorted(json.loads(txt).keys()) if txt.strip().startswith("{") else "not an object")
            print("   validated substring count:", txt.count("validated"))
            print("   first 600 chars:", txt[:600])
