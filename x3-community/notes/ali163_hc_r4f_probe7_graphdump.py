"""ALI-163 R4F audit probe 7 (CPU only, read-only): dump every node of the 4 finished HC clips'
request.api.json so the prompt / reference-slot audit can be written.
Writes C:/AI/community/notes/face_r4f/graph_dump.txt. No GPU, no ComfyUI call, no render."""
import json
import os

RUNS = r"C:\AI\community\runs"
IDS = ["ali147_pool_hc_c1_s51100001", "ali147_pool_hc_c2_s51100002",
       "ali147_pool_hc_r1_s51130001", "ali147_pool_hc_r2_s51130002"]
OUT = r"C:\AI\community\notes\face_r4f\graph_dump.txt"
SKIP = ("class_type", "_meta", "inputs", "outputs", "properties")

log = []


def say(s):
    log.append(s)


for jid in IDS:
    p = os.path.join(RUNS, jid, "request.api.json")
    g = json.load(open(p, encoding="utf-8"))
    say("#### %s  nodes=%d" % (jid, len(g)))
    for nid in sorted(g, key=lambda x: int(x) if x.isdigit() else 0):
        v = g[nid]
        inp = v.get("inputs", {})
        scalars = {k: x for k, x in inp.items() if not isinstance(x, (list, dict))}
        links = {k: x for k, x in inp.items() if isinstance(x, (list, dict))}
        say("  [%s] %s  title=%r" % (nid, v.get("class_type"), v.get("_meta", {}).get("title", "")))
        say("       config=%s" % {k: v[k] for k in SKIP if k in v and k not in ("class_type", "_meta")})
        say("       scalars=%s" % json.dumps(scalars, ensure_ascii=False)[:4000])
        say("       links=%s" % json.dumps(links, ensure_ascii=False)[:1500])
    say("")

open(OUT, "w", encoding="utf-8").write("\n".join(log) + "\n")
print("wrote %s (%d lines)" % (OUT, len(log)))
