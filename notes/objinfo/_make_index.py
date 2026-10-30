"""Regenerate NODE_INPUTS.md and NODE_INDEX.txt from a ComfyUI object_info dump.
Usage: python _make_index.py [object_info.json] [workflow.json]  (PYTHONIOENCODING=utf-8). Documentation tooling only."""
import json, sys, os
D = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, "object_info_20261030.json")
wf = sys.argv[2] if len(sys.argv) > 2 else r"C:\AI\community\runs\sslcaio_20261030\_downloads\civitai_2906001\Minimax H3 All-In-One Ultra.json"
oi = json.load(open(src, encoding="utf-8"))

def fmt(spec):
    if not isinstance(spec, (list, tuple)) or not spec:
        return str(spec)
    t, opts = spec[0], (spec[1] if len(spec) > 1 and isinstance(spec[1], dict) else {})
    if isinstance(t, list):
        s = "COMBO[" + ", ".join(map(str, t[:10])) + (f", ... +{len(t)-10}" if len(t) > 10 else "") + "]"
    elif t == "COMBO" and isinstance(opts.get("options"), list):
        o = opts["options"]; s = "COMBO[" + ", ".join(map(str, o[:10])) + (f", ... +{len(o)-10}" if len(o) > 10 else "") + "]"
    else:
        s = str(t)
    for k in ("default", "min", "max", "step"):
        if k in opts:
            v = opts[k]; v = (v[:60] + "...") if isinstance(v, str) and len(v) > 60 else v
            s += f" {k}={v!r}"
    return s

md = ["# ComfyUI node inputs (from %s)" % os.path.basename(src), "", f"{len(oi)} node classes. Regenerate: `python notes\\objinfo\\_make_index.py`.", ""]
idx = []
for name in sorted(oi, key=str.lower):
    n = oi[name]; inp = n.get("input", {}) or {}
    mod = n.get("python_module", "") or ""
    names = []
    md.append(f"## {name}")
    md.append(f"module: {mod} | category: {n.get('category','')}")
    for sec in ("required", "optional"):
        d = inp.get(sec) or {}
        if d:
            md.append(f"- {sec}:")
            for k, v in d.items():
                md.append(f"  - {k}: {fmt(v)}"); names.append(k + ("?" if sec == "optional" else ""))
    outs = n.get("output", []) or []; on = n.get("output_name", []) or outs
    md.append("- outputs: " + ", ".join(f"{a}:{b}" for a, b in zip(on, outs)))
    md.append("")
    idx.append(f"{name}\t{mod}\t{' '.join(names)}")

missing = []
if os.path.exists(wf):
    w = json.load(open(wf, encoding="utf-8"))
    nodes = list(w.get("nodes", []))
    for sg in (w.get("definitions", {}) or {}).get("subgraphs", []) or []:
        nodes += sg.get("nodes", [])
    sgids = {sg.get("id") for sg in (w.get("definitions", {}) or {}).get("subgraphs", []) or []}
    types = sorted({x.get("type") for x in nodes if x.get("type")} - sgids)
    skip = {"Note", "MarkdownNote", "Reroute", "PrimitiveNode"}
    missing = [t for t in types if t not in oi and t not in skip]
    used = [t for t in types if t in oi]
    md += ["## AIO workflow coverage (civitai 2906001)", f"Node types used: {len(types)}; found in object_info: {len(used)}.",
           "Used and installed: " + ", ".join(used), "",
           "### NOT in object_info (not installed)" ]
    md += [f"- {t}" for t in missing] or ["- none"]
open(os.path.join(D, "NODE_INPUTS.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
open(os.path.join(D, "NODE_INDEX.txt"), "w", encoding="utf-8").write("\n".join(idx) + "\n")
print(len(oi), "nodes; AIO missing:", missing)