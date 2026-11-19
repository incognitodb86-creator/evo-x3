"""R2 probe 6 (read-only): sampler/guide wiring links, to state which conditioning
edge carries reference tokens in the HC1 graph vs RS6, and the noise links."""
import json
import os

RUNS = r"C:\AI\community\runs"
GRAPHS = {
    "HC1": "ali147_pool_hc_c1_s51100001",
    "RS6": "ali147_pool_refsheet_b_s51080000",
}
NODES = ["s0_guide", "s1_guide", "s0_samp", "s1_samp", "s0_sched", "s1_sched", "tail1", "dec_a", "dec_v", "m_vsa"]

for tag, d in GRAPHS.items():
    g = json.loads(open(os.path.join(RUNS, d, "request.api.json"), "rb").read().decode("utf-8-sig"))
    cls = {nid: n["class_type"] for nid, n in g.items()}
    print("=" * 70)
    print(tag, d)
    for nid in NODES:
        print("  %s (%s)" % (nid, cls.get(nid)))
        for k, v in sorted(g[nid]["inputs"].items()):
            if isinstance(v, list) and len(v) == 2:
                print("      %s <- %s (%s)[%s]" % (k, v[0], cls.get(v[0], "??"), v[1]))
            elif k == "prompt":
                print("      %s = <<len %d>>" % (k, len(v)))
            else:
                print("      %s = %s" % (k, v if not isinstance(v, str) or len(v) < 60 else "<<len %d>>" % len(v)))
