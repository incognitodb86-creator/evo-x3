import json, sys, collections

def norm_links(links):
    """{target_id: [(src_id, src_slot, type)]} for both link encodings."""
    out = collections.defaultdict(list)
    for L in (links or []):
        if isinstance(L, dict):
            src = L.get("origin_id", L.get("node_id", L.get("originNode")))
            dst = L.get("target_id", L.get("slot_id", L.get("targetNode")))
            out[str(dst)].append((str(src), L.get("origin_slot", L.get("index", 0)), L.get("type", "")))
        elif isinstance(L, list) and len(L) >= 5:
            out[str(L[3])].append((str(L[1]), L[2], L[5] if len(L) > 5 else ""))
    return out

def show_nodes(nodes, links, tag=""):
    tl = norm_links(links)
    for nid, n in sorted(nodes.items(), key=lambda kv: (len(kv[0]), kv[0])):
        print("  %s[%s] %-40s %s" % (tag, nid, n.get("type", n.get("class_type", "?")), (n.get("title") or "")[:32]))
        ins = n.get("inputs")
        if isinstance(ins, dict):
            kv = {k: (v if not isinstance(v, list) else "->%s.%s" % (v[0], v[1])) for k, v in ins.items()}
            if kv:
                print("        inputs: " + json.dumps(kv, default=str)[:420])
        wire = []
        for src, slot, ty in tl.get(nid, []):
            s = nodes.get(src, {})
            sname = s.get("title") or s.get("type", s.get("class_type", "?"))
            name = "?"
            if isinstance(ins, dict):
                for k, v in ins.items():
                    if v == [int(src), slot] if str(src).isdigit() else False:
                        name = k
            elif isinstance(ins, list):
                for i in ins:
                    if str(i.get("link", "")) in (str(src), "%s:%s" % (src, slot)):
                        name = i.get("name", "?")
            wire.append("%s:%s<-%s(%s)" % (src, slot, sname, ty))
        if wire:
            print("        links: " + " | ".join(wire)[:420])
        if n.get("widgets_values") is not None:
            print("        widgets: " + json.dumps(n["widgets_values"], default=str)[:420])
        if n.get("class_type") and n.get("inputs"):
            pass

def api(g):
    print("API format, %d nodes" % len(g))
    for t, c in collections.Counter(v["class_type"] for v in g.values()).most_common():
        print("  %-46s x%d" % (t, c))
    nodes = {k: {"type": v["class_type"], "inputs": v["inputs"]} for k, v in g.items()}
    print("\nparams:")
    show_nodes(nodes, [])

def graph(g):
    nodes_l = g["nodes"]
    nodes = ({str(n["id"]): n for n in nodes_l} if isinstance(nodes_l, list)
             else {str(k): v for k, v in nodes_l.items()})
    print("GRAPH format, %d nodes" % len(nodes))
    for t, c in collections.Counter(n["type"] for n in nodes.values()).most_common():
        print("  %-46s x%d" % (t, c))
    for sg in (g.get("definitions", {}) or {}).get("subgraphs", []):
        sgn = {str(n["id"]): n for n in sg["nodes"]}
        print("\n===== SUBGRAPH %r :: %d nodes =====" % (sg.get("name", "?"), len(sgn)))
        for t, c in collections.Counter(n["type"] for n in sgn.values()).most_common():
            print("  %-46s x%d" % (t, c))
        print("  internals:")
        show_nodes(sgn, sg.get("links"), tag="  ")
    print("\n===== TOP LEVEL =====")
    show_nodes(nodes, g.get("links"))

g = json.load(open(sys.argv[1], encoding="utf-8-sig"))
if isinstance(g, list) and g and "id" in g[0]:
    graph({"nodes": g, "links": []})
elif isinstance(g, dict) and "nodes" in g:
    graph(g)
else:
    api(g)
