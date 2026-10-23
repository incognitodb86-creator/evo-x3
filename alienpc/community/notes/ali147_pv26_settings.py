# ALI-147 PV2-6 report probe 3 (READ-ONLY): the shared-settings table for the PV2 arms and their controls.
# No GPU, no node list, no render, no job request, no vision judge, no download/install/delete. Writes ONLY C:/AI/community/notes/.
import json, os, hashlib, datetime

RUNS = r"C:/AI/community/runs"
NOTES = r"C:/AI/community/notes"
OUT = os.path.join(NOTES, "ali147-pv26-settings-20261023.txt")
L = []


def p(s):
    L.append(s)


def g(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def brief(v):
    s = json.dumps(v, sort_keys=True)
    return s if len(s) <= 220 else s[:200] + "...TRUNC(" + str(len(s)) + ")"


GRAPHS = [
    ("CTRL (driver-rendered seg1)", os.path.join(RUNS, "ali147_pool_ctrl_s51080000", "submitted_graph.pretty.json")),
    ("PV2-1 arm", os.path.join(RUNS, "ali147_pool_promptv2_s51080000", "request.api.json")),
    ("BASE seg3 (the PV2-2 control)", os.path.join(RUNS, "p7_r2_c3_pmot_full_pool", "p7_r2_c3_pmot_full_pool_seg3.api.json")),
    ("PV2-2 arm", os.path.join(RUNS, "ali147_pool_promptv2_seg3_s51080002", "request.api.json")),
    ("PV2-3 arm (dense)", os.path.join(RUNS, "ali147_pool_dense_s51080000", "request.api.json")),
]

p("ALI-147 PV2-6 settings table - %s  READ-ONLY (graph fields, no GPU)" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
p("prompt fields are shown as length + sha256 only (the prompt text itself is in the graph and in specs\\prompt_v2\\*)")
KEYN = ["noise", "m_attn", "m_vsa", "m_shift", "m_cache", "sampler", "vae", "vae_d", "img", "save", "clip",
        "lora_1", "lora_2", "lora_3", "lora_4", "lora_5", "bridge", "v2_a0", "v2_a1", "ext"]

for tag, path in GRAPHS:
    gr = g(path)
    p("\n== %s" % tag)
    p("   graph %s  %d B  sha256 %s  nodes=%d" % (path, os.path.getsize(path),
                                                   hashlib.sha256(open(path, "rb").read()).hexdigest(), len(gr)))
    for nid in sorted(gr, key=lambda x: (len(x), x)):
        nd = gr[nid]
        ins = nd.get("inputs", {})
        out = {}
        for k, v in ins.items():
            if isinstance(v, str) and ("prompt" in k or k in ("text",)) and len(v) > 120:
                out[k] = "TEXT %d chars sha256 %s" % (len(v), hashlib.sha256(v.encode()).hexdigest())
            else:
                out[k] = brief(v)
        p("  [%s] %s" % (nid, nd.get("class_type")))
        for k in sorted(out):
            p("      %-22s %s" % (k, out[k]))
    missing = [k for k in KEYN if k not in gr]
    p("   absent known setting-node ids: %s" % missing)

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("wrote %s  %d B" % (OUT, os.path.getsize(OUT)))
