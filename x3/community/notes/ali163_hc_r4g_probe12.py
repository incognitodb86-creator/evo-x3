"""R4G probe 12: exact inputs of dec_a / mkvid / win1 / c1 / c0 in the RS6 base (read-only)."""
import json
import os

p = os.path.join(r"C:/AI/community", "runs", "ali147_pool_refsheet_b_s51080000", "request.api.json")
g = json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))
for nid in ("c0", "c1", "dec_a", "dec_v", "mkvid", "win1", "tail1", "save", "avae", "vvae", "s0_samp", "s1_samp"):
    print("==", nid, g[nid]["class_type"])
    for k, v in sorted(g[nid]["inputs"].items()):
        if k == "prompt":
            print("   prompt: <%d chars>" % len(str(v)))
        else:
            print("   ", k, "=", json.dumps(v)[:140])
