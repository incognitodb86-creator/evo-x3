# ALI-147 FIX4_PROOF probe (READ-ONLY: no GPU, no ComfyUI/llama-swap call, no render, writes only notes\).
# Dumps the base run's per-segment API graphs so fairness.txt can quote the real widget values.
import json, os, hashlib

BASE = r"C:/AI/community/runs/p7_r2_c3_pmot_full_pool"
ARM = r"C:/AI/community/runs/ali147_pool_fix4_s51080000"
OUT = r"C:/AI/community/notes/ali147-fix4-proof-probe-20261022.txt"
L = []


def p(*a):
    L.append(" ".join(str(x) for x in a))


def sha(s):
    if isinstance(s, str):
        s = s.encode()
    return hashlib.sha256(s).hexdigest()


for seg in ("seg1", "seg2", "seg3"):
    f = os.path.join(BASE, "p7_r2_c3_pmot_full_pool_%s.api.json" % seg)
    g = json.load(open(f, encoding="utf-8"))
    p("=== %s  nodes=%d bytes=%d sha256=%s" % (seg, len(g), os.path.getsize(f), sha(open(f, "rb").read())))
    for nid, nd in sorted(g.items()):
        p("  node %s %s" % (nid, nd["class_type"]))
        for k, v in sorted(nd["inputs"].items()):
            if k == "prompt":
                t = v if isinstance(v, str) else str(v)
                p("    input %s len=%d sha256=%s" % (k, len(t), sha(t)))
            elif isinstance(v, str) and len(v) > 120:
                p("    input %s str_len=%d sha256=%s" % (k, len(v), sha(v)))
            else:
                p("    input %s = %r" % (k, v))

g = json.load(open(os.path.join(ARM, "request.api.json"), encoding="utf-8"))
p("=== FIX4 graph nodes=%d" % len(g))
for nid, nd in sorted(g.items()):
    p("  node %s %s" % (nid, nd["class_type"]))
    for k, v in sorted(nd["inputs"].items()):
        if k == "prompt" or (isinstance(v, str) and len(v) > 200):
            p("    input %s str_len=%d sha256=%s" % (k, len(v), sha(v)))
        else:
            p("    input %s = %r" % (k, v))

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
for ln in L:
    if "input " in ln and "sha256" not in ln and "prompt" not in ln:
        print(ln)
print("probe written: %s (%d lines)" % (OUT, len(L)))
