"""make_bfs_request.py - build one BFS head-swap still request from C:\\AI\\community\\templates\\flux_stills_s2_bfs.api.json.

Flux Phase 1 (Derrick 2026-10-30 2:52 PM CT: "...building bfs_klein9b.api.json and a small request patcher...").
That template name is retired (cleanup phase 2, 2026-11-05): it is templates\flux_stills_s2_bfs.api.json, the file
this tool reads today.
Modelled on make_b2_request.py. It patches ONLY the per-job fields and nothing else:
  body (Picture 1) 7.image   head (Picture 2) 8.image   seed 20.noise_seed   prefix 24.filename_prefix
  mp (size, ~1 MP) 25 + 9 resize_type.megapixels
Arm dials for an A/B test (Miraclein 4.3 plan 2026-10-30, rows M4/M8/M12: "copy only the UNET swap and steps,
keep our template"): --unet 1.unet_name   --steps 19.steps   --cfg 17.cfg. Klein 9B-KV + BFS plan 2026-10-30
(rows G/KP/KC) adds: --strength 2.strength_model (the BFS LoRA strength, the plan's "BFS 1.0 vs BFS 0.0") and
--kv, which inserts the CORE FluxKVCache node (ComfyUI PR #12905, in object_info as of this box) as node 26
between the LoRA (node 2) and the guider (node 17) - the plan's "LoRA loads before the KV node". Omit them and
the build is the Phase 1 baseline byte-for-byte; a per-job copy may change ONLY these keys. The template file
is never edited.
It writes <job-dir>\\request.api.json and, given --body-size, prints the expected output size (the order "size").
It does not submit anything: run_queue.py submits and runs comm.guard_ok on every prompt string first.

Usage:
  C:\\AI\\director\\.venv\\Scripts\\python.exe C:\\AI\\community\\scripts\\make_bfs_request.py --job-dir <run dir>\\<tag>
      --body community/<run>/<file>.png --head community/<run>/<file>.png --seed <n> --prefix community/<run>/<tag>
      [--mp 1.0] [--unet <file>.safetensors] [--steps n] [--cfg f] [--strength f] [--kv] [--body-size WxH] [--force]
"""
import argparse, copy, json, math, os, sys

COMMUNITY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # templates/ and runs/ stay in the community work tree (F6b)
TEMPLATE = os.path.join(COMMUNITY, "templates", "flux_stills_s2_bfs.api.json")
# per-job field -> [(node id, input key)]. Nothing else may change.
FIELDS = {
    "body": [("7", "image")],
    "head": [("8", "image")],
    "seed": [("20", "noise_seed")],
    "prefix": [("24", "filename_prefix")],
    "mp": [("25", "resize_type.megapixels"), ("9", "resize_type.megapixels")],
    # A/B arm dials (Miraclein 4.3 A/B plan, arms M4/M8/M12) - nothing else may change per arm.
    "unet": [("1", "unet_name")],
    "steps": [("19", "steps")],
    "cfg": [("17", "cfg")],
    # Klein 9B-KV + BFS plan arms G/KP/KC: --strength is a plain slot dial; --kv is handled in build()
    # (it inserts a node, so it owns no slot here). Nothing else may change per arm.
    "strength": [("2", "strength_model")],
    "kv": [],
}
# the core KV node (ComfyUI PR #12905, comfy_extras.nodes_flux, model in -> model out; verified present in
# notes/objinfo/NODE_INDEX.txt + NODE_INPUTS.md on 2026-10-30). It feeds the guider from the LoRA output.
KV_ID, KV_CLASS = "26", "FluxKVCache"


def build(tpl, **vals):
    unknown = set(vals) - set(FIELDS)
    if unknown:
        raise ValueError("refused field(s): %s" % ", ".join(sorted(unknown)))
    g = copy.deepcopy(tpl)
    for key, slots in FIELDS.items():
        for node, field in slots:
            if node not in g or field not in g[node].get("inputs", {}):
                raise ValueError("template has no %s.%s" % (node, field))
            if vals.get(key) is not None:
                g[node]["inputs"][field] = vals[key]
    if vals.get("kv"):
        if KV_ID in g:
            raise ValueError("template already uses node id %s" % KV_ID)
        if g.get("17", {}).get("inputs", {}).get("model") != ["2", 0]:
            raise ValueError("guider 17.model does not link the LoRA node 2; refusing to insert %s" % KV_CLASS)
        g[KV_ID] = {"_meta": {"title": "kv_cache"}, "class_type": KV_CLASS, "inputs": {"model": ["2", 0]}}
        g["17"]["inputs"]["model"] = [KV_ID, 0]
    return g


def expected_size(w, h, mp=1.0):
    """ComfyUI ResizeImageMaskNode 'scale total pixels', then EmptyFlux2LatentImage (//16) = the saved PNG size."""
    s = math.sqrt(int(mp * 1024 * 1024) / (w * h))
    return (round(w * s) // 16 * 16, round(h * s) // 16 * 16)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build <job-dir>\\request.api.json from the BFS Klein 9B template.")
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--body", required=True, help="Picture 1 (the approved still), path inside ComfyUI/input")
    ap.add_argument("--head", required=True, help="Picture 2 (plain hand crop), path inside ComfyUI/input")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--prefix", required=True, help="SaveImage filename_prefix, e.g. community/<run>/<tag>")
    ap.add_argument("--mp", type=float, default=None, help="megapixels for both resizes; default = template (1.0)")
    ap.add_argument("--unet", default=None, help="arm dial: 1.unet_name (UNETLoader), e.g. a checkpoint A/B file")
    ap.add_argument("--steps", type=int, default=None, help="arm dial: 19.steps (Flux2Scheduler)")
    ap.add_argument("--cfg", type=float, default=None, help="arm dial: 17.cfg (CFGGuider)")
    ap.add_argument("--strength", type=float, default=None, help="arm dial: 2.strength_model (BFS LoRA strength, e.g. 0.0 for the KV gate's no-LoRA tile)")
    ap.add_argument("--kv", action="store_true", help="arm dial: insert the core FluxKVCache node between the LoRA (2) and the guider (17)")
    ap.add_argument("--body-size", help="WxH of the body still, to print the expected output size")
    ap.add_argument("--template", default=TEMPLATE)
    ap.add_argument("--force", action="store_true", help="overwrite an existing request.api.json")
    a = ap.parse_args(argv)
    with open(a.template, encoding="utf-8") as f:
        tpl = json.load(f)
    g = build(tpl, body=a.body, head=a.head, seed=a.seed, prefix=a.prefix, mp=a.mp, unet=a.unet, steps=a.steps,
              cfg=a.cfg, strength=a.strength, kv=a.kv)
    os.makedirs(a.job_dir, exist_ok=True)
    out = os.path.join(a.job_dir, "request.api.json")
    if os.path.exists(out) and not a.force:
        print("REFUSED: %s exists (use --force)" % out, file=sys.stderr)
        return 3
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, indent=1, ensure_ascii=False)
    msg = "wrote %s" % out
    if a.body_size:
        w, h = (int(x) for x in a.body_size.lower().split("x"))
        msg += " size=%dx%d" % expected_size(w, h, g["25"]["inputs"]["resize_type.megapixels"])
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
