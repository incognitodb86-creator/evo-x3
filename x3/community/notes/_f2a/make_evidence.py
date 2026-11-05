"""F2a evidence, offline (no HTTP, no GPU, no ComfyUI). Run from C:\\AI\\community\\scripts:
  C:\\AI\\director\\.venv\\Scripts\\python.exe ..\\notes\\_f2a\\make_evidence.py
Writes the measured files next to this script: node lists, the --lora none before/after graphs,
the per-run-only field diff, the bfs_klein9b -> flux_stills_s2_bfs node-by-node diff,
and the FC_ARIANA node list from the phase 7 archive copy.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))            # C:\AI\community
sys.path.insert(0, os.path.join(REPO, "scripts"))
import make_b2_request as mbr

FC_COPY = r"C:\AI\_archive\2026-11-05-cleanup\7\faces\FC_ARIANA.api.json"
B2 = os.path.join(REPO, "templates", "b2.api.json")
OLD_BFS = os.path.join(HERE, "bfs_klein9b.api.json.retired")   # git blob from before the 25e403c merge
NEW_BFS = os.path.join(REPO, "templates", "flux_stills_s2_bfs.api.json")
ARGS = ["--prompt", "two adult women (18+), no pose change", "--seed", "1", "--image",
        "community/X.png", "--prefix", "community/_selftest/x", "--frames", "22"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(name, obj):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
    print("wrote", name)


def sh(cmd):
    import subprocess
    return subprocess.run(cmd, cwd=REPO, capture_output=True).stdout.decode("utf-8", "replace")


with open(OLD_BFS, "w", encoding="utf-8", newline="\n") as f:
    f.write(sh(["git", "show", "25e403c^:templates/bfs_klein9b.api.json"]))
print("wrote", os.path.basename(OLD_BFS), len(open(OLD_BFS, encoding="utf-8").read()), "chars")


def nodelist(g):
    return sorted("%s %s" % (k, v["class_type"]) for k, v in g.items())


b2 = load(B2)
dump("b2_nodes.txt", nodelist(b2))

# after the fix: --lora none must be the plain b2 graph; only the per-run fields may differ
for sub, extra in (("stage_nolora2", ["--lora", "none"]),
                   ("stage_with_lora", ["--lora", "FC_ARIANA_h3_face_v1.safetensors", "--strength", "0.7"])):
    stage = os.path.join(HERE, sub)
    os.makedirs(stage, exist_ok=True)
    mbr.main(["--arm-dir", stage] + ARGS + extra)
    g = load(os.path.join(stage, "request.api.json"))
    dump(sub + ".nodes.txt", nodelist(g))

diffs = []
for k in sorted(set(b2) | set(load(os.path.join(HERE, "stage_nolora2", "request.api.json")))):
    a = b2.get(k, {}).get("inputs", {})
    b = load(os.path.join(HERE, "stage_nolora2", "request.api.json")).get(k, {}).get("inputs", {})
    if a != b:
        keys = sorted(set(a) | set(b))
        diffs.append({"node": k, "fields": {kk: [a.get(kk), b.get(kk)] for kk in keys if a.get(kk) != b.get(kk)}})
dump("diff_nolora_vs_b2.json", {"node_count_b2": len(b2),
                                "node_count_after": len(load(os.path.join(HERE, "stage_nolora2", "request.api.json"))),
                                "has_lora_node": "lora" in load(os.path.join(HERE, "stage_nolora2", "request.api.json")),
                                "field_diffs": diffs})

# the code path before the fix, reproduced by handing the literal string to build()
old = mbr.build(b2, lora="none", prompt=ARGS[1], seed=int(ARGS[3]), image=ARGS[5], prefix=ARGS[7],
                frames=int(ARGS[9]))
dump("b2_lora_string_none_before_fix.nodes.txt", nodelist(old))

# the phase 2 merge, node by node
o, n = load(OLD_BFS), load(NEW_BFS)
out = {"old_nodes": len(o), "new_nodes": len(n), "added": sorted(set(n) - set(o)), "removed": sorted(set(o) - set(n)),
       "class_changes": [], "input_diffs": []}
for k in sorted(set(o) & set(n)):
    if o[k]["class_type"] != n[k]["class_type"]:
        out["class_changes"].append([k, o[k]["class_type"], n[k]["class_type"]])
    for f in sorted(set(o[k]["inputs"]) | set(n[k]["inputs"])):
        if o[k]["inputs"].get(f) != n[k]["inputs"].get(f):
            out["input_diffs"].append({"node": k, "class": n[k]["class_type"], "field": f,
                                       "old": o[k]["inputs"].get(f), "new": n[k]["inputs"].get(f)})
dump("node_diff_bfs_klein9b_to_flux_stills_s2_bfs.json", out)
dump("fc_ariana_nodes.txt", nodelist(load(FC_COPY)))
