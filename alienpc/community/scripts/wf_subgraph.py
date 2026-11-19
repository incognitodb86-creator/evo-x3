#!/usr/bin/env python3
"""Print the widgets and input sources of a list of node ids in a ComfyUI workflow JSON.

Workflow JSONs use the list form; links live at the graph top level as
[lid, src, sslot, dst, dslot, "TYPE"], so this prints the real graph structure of a
subgraph, not just widgets. Used to recover the exact pass-2 recipe from the LBH r2v template.
Usage: wf_subgraph.py <json> 6 13 18 21 22 23 31 32 33
"""
import json
import sys

path = sys.argv[1]
want = [int(a) for a in sys.argv[2:]]
g = json.load(open(path, encoding="utf-8"))
nodes = {n["id"]: n for n in g["nodes"]}
lmap = {l[0]: (l[1], l[2], l[3], l[4], l[5]) for l in g.get("links", []) if len(l) > 4}
for i in want:
    n = nodes.get(i)
    if not n:
        print(f"-- id {i}: absent")
        continue
    print(f"-- {i} {n['type']}  mode={n.get('mode')}")
    print(f"   widgets: {json.dumps(n.get('widgets_values'))[:300]}")
    for slot in n.get("inputs", []):
        lid = slot.get("link")
        if lid in lmap:
            sn, ss, dn, ds, ty = lmap[lid]
            src = nodes.get(sn, {})
            print(f"   <- {slot.get('name')} ({ty}) from {sn} {src.get('type')} slot {ss} "
                  f"widgets={json.dumps(src.get('widgets_values'))[:120]}")
        else:
            print(f"   <- {slot.get('name')} UNLINKED")
