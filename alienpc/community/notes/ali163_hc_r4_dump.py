import json, os

RUNS = r"C:\AI\community\runs"
BASE = os.path.join(RUNS, "ali147_pool_refsheet_b_s51080000", "request.api.json")
OUT = r"C:\AI\community\notes\ali163_hc_r4_rs6_dump.txt"

g = json.load(open(BASE, encoding="utf-8"))
lines = []
for nid, node in sorted(g.items(), key=lambda kv: kv[0]):
    lines.append("=== node %s class_type=%s" % (nid, node.get("class_type")))
    for k in sorted(node.keys()):
        if k == "inputs":
            for ik in sorted(node["inputs"].keys()):
                v = node["inputs"][ik]
                if ik == "prompt":
                    lines.append("  input %s = <PROMPT len=%d>" % (ik, len(v)))
                else:
                    lines.append("  input %s = %s" % (ik, json.dumps(v)))
        else:
            lines.append("  %s = %s" % (k, json.dumps(node[k])[:400]))
open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("wrote", OUT, len(lines), "lines")
