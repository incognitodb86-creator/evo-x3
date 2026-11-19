"""R4G probe 5: link/output bookkeeping in the RS6 base and in the r1 graph (which added sheet2).
Prints full node JSON for img/sheet/sheet2/c0/c1/win1 + the global set of link ids.
Read-only, no GPU.
"""
import json, os

W = r"C:\AI\community"
for i in ("ali147_pool_refsheet_b_s51080000", "ali147_pool_hc_r1_s51130001"):
    fp = os.path.join(W, "runs", i, "request.api.json")
    g = json.loads(open(fp, encoding="utf-8").read().replace("\r\n", "\n"))
    print("=" * 110)
    print("GRAPH", i)
    for n in ("img", "sheet", "sheet2", "c0", "c1", "win1"):
        if n not in g:
            print("  -- node", n, "absent")
            continue
        node = dict(g[n])
        if "prompt" in node.get("inputs", {}):
            node["inputs"] = dict(node["inputs"])
            node["inputs"]["prompt"] = "<len %d>" % len(g[n]["inputs"]["prompt"])
        print("  node", n, json.dumps(node, indent=None, sort_keys=True)[:1200])
    ids = set()
    for n, node in g.items():
        for o in node.get("outputs", []):
            for l in (o.get("links") or []):
                ids.add(l)
    refs = []
    for n, node in g.items():
        for k, v in node["inputs"].items():
            if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and isinstance(v[1], int):
                refs.append((n, k, v[0], v[1]))
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if isinstance(vv, list) and len(vv) == 2:
                        refs.append((n, k + "." + kk, vv[0], vv[1]))
    print("  link ids declared in outputs:", sorted(ids))
    print("  consumed links count:", len(refs))
