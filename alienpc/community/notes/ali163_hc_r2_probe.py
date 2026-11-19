"""R2 diagnosis probe (read-only). No GPU, no writes outside notes/.

Compares the ALI-163 clip-1 graph (ali147_pool_hc_c1_s51100001) with the
reference-sheet arms RS4 (ali147_pool_refsheet_s51080000) and RS6
(ali147_pool_refsheet_b_s51080000), and prints the keys R2 rests on.
"""
import json
import os

RUNS = r"C:\AI\community\runs"
GRAPHS = {
    "HC1": "ali147_pool_hc_c1_s51100001",
    "PV2": "ali147_pool_promptv2_s51080000",
    "RS4": "ali147_pool_refsheet_s51080000",
    "RS6": "ali147_pool_refsheet_b_s51080000",
}


def load(tag):
    path = os.path.join(RUNS, GRAPHS[tag], "request.api.json")
    with open(path, "rb") as fh:
        raw = fh.read()
    return tag, path, raw, json.loads(raw.decode("utf-8-sig"))


def brief(node):
    """Print the interesting scalars of one node (no prompt bodies)."""
    out = {}
    for k, v in node.items():
        if k == "class_type":
            continue
        if isinstance(v, dict):
            for kk, vv in v.items():
                if kk.startswith("prompt_") and isinstance(vv, str):
                    out[k + "." + kk] = "len=%d" % len(vv)
                elif isinstance(vv, str) and len(vv) > 120:
                    out[k + "." + kk] = "len=%d sha=%s" % (len(vv), vv[:0])
                elif isinstance(vv, (list, str, int, float, bool)) or vv is None:
                    out[k + "." + kk] = vv
        elif isinstance(v, (int, float, str, bool)) or v is None:
            out[k] = v
    return out


rows = {}
for tag in GRAPHS:
    tag, path, raw, g = load(tag)
    rows[tag] = g
    print("=" * 78)
    print(tag, GRAPHS[tag], "bytes", len(raw), "nodes", len(g))
    for nid in sorted(g, key=lambda x: (len(x), x)):
        n = g[nid]
        print("  %-8s %-32s inputs=%d" % (nid, n.get("class_type", "?"), len(n.get("inputs", {}))))

for tag in GRAPHS:
    print("=" * 78)
    print(tag, "node detail")
    g = rows[tag]
    for nid in sorted(g, key=lambda x: (len(x), x)):
        n = g[nid]
        b = brief(n.get("inputs", {}))
        print("  %-8s %s" % (nid, n.get("class_type", "?")))
        for k in sorted(b):
            print("      %s = %r" % (k, b[k]))

# node-set diffs
print("=" * 78)
print("node-set comparison")
sets = {t: set(rows[t]) for t in GRAPHS}
base = sets["HC1"]
for t in ("PV2", "RS4", "RS6"):
    print(t, "only_in_HC1", sorted(base - sets[t]), "only_in_" + t, sorted(sets[t] - base))

print("=" * 78)
print("pairwise per-node body diff (sorted json), shared nodes only")
for a, b in (("HC1", "PV2"), ("HC1", "RS4"), ("HC1", "RS6"), ("RS4", "RS6")):
    ga, gb = rows[a], rows[b]
    shared = sorted(set(ga) & set(gb))
    diff = [n for n in shared
            if json.dumps(ga[n], sort_keys=True) != json.dumps(gb[n], sort_keys=True)]
    print("%s vs %s shared=%d differing=%s" % (a, b, len(shared), diff))
    for n in diff:
        ka, kb = set(ga[n].get("inputs", {})), set(gb[n].get("inputs", {}))
        kd = sorted(ka ^ kb) + [k for k in sorted(ka & kb)
                                if json.dumps(ga[n]["inputs"][k], sort_keys=True)
                                != json.dumps(gb[n]["inputs"][k], sort_keys=True)]
        print("   node", n, ga[n].get("class_type"), gb[n].get("class_type"), "keys", kd)
