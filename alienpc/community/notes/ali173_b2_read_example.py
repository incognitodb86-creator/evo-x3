r"""ALI-173 B2 CONTINUUM SCENE (2026-10-23, CPU only): read the Continuum V3.9 EXAMPLE
workflow (GUI format: nodes + links + widgets_values) and print it as a resolved API-format
input map, so the B2 builder can be written from the real wiring instead of guesses.

widget order rule used here: ComfyUI creates widgets in INPUT_TYPES order = required then
optional, and only for widget-able types (a link-only type, or forceInput, is not a widget).
The widget list per node is taken from the LIVE object_info dump saved by
notes/ali173_b2_objinfo.py, so the mapping is checkable: if widgets_values does not line up
with the widget names, this script says so loudly.
"""
import json, os, sys

NOTES = r"C:\AI\community\notes"
EX = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\ComfyUI-H3-Continuum\examples\workflows\MiniMax_H3_Continuum_V39.json"
full = json.load(open(os.path.join(NOTES, "ali173_b2_object_info_full.json"), encoding="utf-8"))
g = json.load(open(EX, encoding="utf-8"))

LINK_TYPES = ("MODEL", "CLIP", "VAE", "SAMPLER", "SIGMAS", "IMAGE", "AUDIO", "LATENT",
              "CONDITIONING", "STRING", "INT", "FLOAT", "BOOLEAN", "COMBO", "NOISE",
              "GUIDER", "H3_CONTINUUM_REFERENCE_IMAGES_V39", "H3_CONTINUUM_ASSEMBLY_PLAN",
              "H3_CONTINUUM_STILL_IMAGE_GUIDE", "H3_CONTINUUM_AUDIO_REFERENCES",
              "H3_CONTINUUM_PLAN", "H3_CONTINUUM_STATE", "MASK", "VIDEO", "H3_RESOLUTION_PLAN")


def spec(c):
    return full[c]["input"] if c in full else None


def widget_names(c):
    """widget-able inputs in spec order: not hidden, not a pure link type, not forceInput."""
    s = spec(c)
    if s is None:
        return None
    out = []
    for section in ("required", "optional"):
        for k, v in (s.get(section) or {}).items():
            if not isinstance(v, (list, tuple)) or not v:
                out.append(k); continue
            ty = v[0]
            opts = v[1] if len(v) > 1 and isinstance(v[1], dict) else {}
            if opts.get("forceInput"):
                continue
            if isinstance(ty, list):
                out.append(k); continue           # combo of literals = widget
            base = str(ty).split(",")[0].strip()
            if base in ("INT", "FLOAT", "BOOLEAN", "STRING", "COMBO"):
                out.append(k)
            elif base.isupper() and base not in ("INT", "FLOAT", "BOOLEAN", "STRING"):
                continue                          # custom/structural type = link only
            else:
                out.append(k)
    return out


nodes = {n["id"]: n for n in g["nodes"]}
links = {l[0]: l for l in g["links"]}      # [id, src_node, src_slot, dst_node, dst_slot, type]
print(f"workflow {os.path.basename(EX)}: {len(nodes)} nodes, {len(links)} links")
print("groups:", [(x.get("title"), x.get("bypass"), x.get("collapsed")) for x in g.get("groups", [])])
print()
for nid in sorted(nodes):
    n = nodes[nid]
    t = n["type"]
    wn = widget_names(t)
    ins = {}
    for inp in n.get("inputs", []):
        lid = inp.get("link")
        if lid is None:
            for sl in inp.get("links") or []:
                lid = sl; break
        if lid is None:
            ins[inp["name"]] = None
            continue
        l = links[lid]
        ins[inp["name"]] = [str(l[1]), l[2], f"{nodes[l[1]]['type']}.{l[3] if len(l) > 3 else ''}"]
    wl = [w for w in (n.get("widgets_values") or [])]
    print(f"--- node {nid} {t} mode={n.get('mode')} pos={n.get('pos')}")
    print(f"    title={n.get('title')}")
    if wn is None:
        print(f"    NOT IN object_info -> widgets_values={json.dumps(wl, ensure_ascii=False)[:400]}")
    else:
        if len(wn) != len(wl):
            print(f"    WIDGET COUNT MISMATCH spec={len(wn)} values={len(wl)}")
        for i, w in enumerate(wl):
            name = wn[i] if i < len(wn) else f"?{i}"
            s = json.dumps(w, ensure_ascii=False)
            print(f"    widget {name} = {s[:200]}{'...' if len(s) > 200 else ''}")
    for k, v in ins.items():
        if v is not None:
            print(f"    link {k} <- {v}")
    print(f"    outputs={[(o['name'], o.get('links')) for o in n.get('outputs', [])]}")
