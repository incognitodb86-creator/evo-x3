#!/usr/bin/env python3
"""Print the node types of a ComfyUI workflow JSON (list form), with the id each type uses.

Used to read the shipped RTX / latent-upscaler example workflows as the reference wiring
before hand-building a graph (skills: "community workflow first ... run as-published").
Usage: wf_types.py <workflow.json>
"""
import json
import sys

g = json.load(open(sys.argv[1], encoding="utf-8"))
raw = g.get("nodes", [])
nodes = {n["id"]: n for n in raw} if isinstance(raw, list) else {int(k): v for k, v in raw.items()}
by = {}
for i, n in nodes.items():
    by.setdefault(n.get("type"), []).append(i)
for t in sorted(by):
    print(f"{t:34} ids={by[t][:10]}")
    n = nodes[by[t][0]]
    if n.get("widgets_values") is not None:
        print(f"{'':34} widgets={json.dumps(n['widgets_values'])[:200]}")
lmap = {l[0]: (l[1], l[2], l[3], l[4], l[5]) for l in g.get("links", []) if len(l) > 4}
tgt = sys.argv[2] if len(sys.argv) > 2 else None
if tgt:
    for i, n in nodes.items():
        if n.get("type") == tgt:
            print(f"\n== {tgt} id {i} wiring")
            for slot in n.get("inputs", []):
                lid = slot.get("link")
                if lid in lmap:
                    sn, ss, dn, ds, ty = lmap[lid]
                    print(f"   <- {slot.get('name')} ({ty}) from {sn} {nodes[sn].get('type')} slot {ss} "
                          f"widgets={json.dumps(nodes[sn].get('widgets_values'))[:120]}")
                else:
                    print(f"   <- {slot.get('name')} UNLINKED")
            for slot in n.get("outputs", []):
                for lid in slot.get("links") or []:
                    if lid in lmap:
                        sn, ss, dn, ds, ty = lmap[lid]
                        print(f"   -> {slot.get('name')} ({ty}) to {dn} {nodes[dn].get('type')} slot {ds}")
