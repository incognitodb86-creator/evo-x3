"""R4G probe 3: full node-by-node dump of the RS6 base graph (the graph R2 named) and the PV2 base,
so the R4G builder diff is written against real keys. Read-only, no GPU.
"""
import json, hashlib, os

W = r"C:\AI\community"
for i in ("ali147_pool_refsheet_b_s51080000", "ali147_pool_promptv2_s51080000", "ali147_pool_hc_r1_s51130001"):
    fp = os.path.join(W, "runs", i, "request.api.json")
    g = json.loads(open(fp, encoding="utf-8").read().replace("\r\n", "\n"))
    print("=" * 110)
    print("BASE", i, "nodes", len(g))
    for n in sorted(g):
        node = g[n]
        ins = {}
        for k, v in sorted(node["inputs"].items()):
            if k == "prompt":
                ins[k] = "len=%d sha=%s" % (len(v), hashlib.sha256(v.encode()).hexdigest()[:12])
            else:
                ins[k] = v
        print("  %-9s %-34s %s" % (n, node["class_type"], json.dumps(ins, sort_keys=True)))
