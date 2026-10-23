"""R4G probe 1: what do the c0/c1 reference slots look like in the real graphs?
Read-only. Dumps every input key of c0/c1 for: RS6 base, r1, r2, c1-clip, c2-clip, PV2 base.
"""
import json, os

W = r"C:\AI\community"
IDS = [
    "ali147_pool_refsheet_b_s51080000",
    "ali147_pool_hc_r1_s51130001",
    "ali147_pool_hc_r2_s51130002",
    "ali147_pool_hc_c1_s51100001",
    "ali147_pool_hc_c2_s51100002",
    "ali147_pool_promptv2_s51080000",
]
for i in IDS:
    d = os.path.join(W, "runs", i)
    print("=" * 100)
    print("ARM", i, "dir exists:", os.path.isdir(d))
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        print("   file", fn, os.path.getsize(os.path.join(d, fn)))
    fp = os.path.join(d, "request.api.json")
    if not os.path.isfile(fp):
        print("   (no request.api.json)")
        continue
    g = json.loads(open(fp, encoding="utf-8").read().replace("\r\n", "\n"))
    print("   nodes", len(g), "keys", sorted(g))
    for n in sorted(g):
        node = g[n]
        if n in ("c0", "c1", "img", "sheet", "sheet2", "win1", "tail1", "noise", "save"):
            print("   node", n, node["class_type"])
            for k in sorted(node["inputs"]):
                v = node["inputs"][k]
                if k == "prompt":
                    print("      ", k, "len", len(v), "sha", __import__("hashlib").sha256(v.encode()).hexdigest()[:12])
                else:
                    print("      ", k, "=", v)
