import json, hashlib, os, sys

RUNS = r"C:\AI\community\runs"
BASE = os.path.join(RUNS, "ali147_pool_refsheet_b_s51080000", "request.api.json")
HC1 = os.path.join(RUNS, "ali147_pool_hc_c1_s51100001", "request.api.json")
SHEETDIR = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\hc_sheets"
INPDIR = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def brief(g, name):
    print("=== %s : %d nodes" % (name, len(g)))
    for nid, node in sorted(g.items(), key=lambda kv: kv[0]):
        ct = node.get("class_type")
        keys = sorted(node.get("inputs", {}).keys())
        print("  [%s] %s keys=%s" % (nid, ct, ",".join(keys)))

for path, nm in ((BASE, "RS6 base"), (HC1, "HC1 clip")):
    g = load(path)
    print(path, os.path.getsize(path), "bytes sha", sha(path)[:16])
    brief(g, nm)
    print()

g = load(BASE)
for nid, node in sorted(g.items(), key=lambda kv: kv[0]):
    ct = node.get("class_type", "")
    if ct.startswith("MiniMaxH3") or ct in ("LoadImage", "RandomNoise", "CreateVideo", "SaveVideo", "VAEDecode", "VAEDecodeAudio"):
        print("--- node", nid, ct)
        for k, v in sorted(node["inputs"].items()):
            sv = json.dumps(v)
            if len(sv) > 220:
                sv = sv[:220] + " ...len=%d" % len(sv)
            print("    %s = %s" % (k, sv))
        if "properties" in node:
            print("    properties =", json.dumps(node["properties"])[:300])
        if "widgets_values" in node:
            print("    widgets_values =", json.dumps(node["widgets_values"])[:300])
