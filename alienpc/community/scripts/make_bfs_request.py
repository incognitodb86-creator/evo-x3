"""make_bfs_request.py - build one BFS head-swap still request from C:\\AI\\community\\templates\\bfs_klein9b.api.json.

Flux Phase 1 (Derrick 2026-10-30 2:52 PM CT: "...building bfs_klein9b.api.json and a small request patcher...").
Modelled on make_b2_request.py. It patches ONLY the per-job fields and nothing else:
  body (Picture 1) 7.image   head (Picture 2) 8.image   seed 20.noise_seed   prefix 24.filename_prefix
  mp (size, ~1 MP) 25 + 9 resize_type.megapixels
Arm dials for an A/B test (Miraclein 4.3 plan 2026-10-30, rows M4/M8/M12: "copy only the UNET swap and steps,
keep our template"): --unet 1.unet_name   --steps 19.steps   --cfg 17.cfg. Omit them and the build is the
Phase 1 baseline byte-for-byte; a per-job copy may change ONLY these keys. The template file is never edited.
It writes <job-dir>\\request.api.json and, given --body-size, prints the expected output size (the order "size").
It does not submit anything: run_queue.py submits and runs comm.guard_ok on every prompt string first.

Usage:
  C:\\AI\\director\\.venv\\Scripts\\python.exe C:\\AI\\community\\scripts\\make_bfs_request.py --job-dir <run dir>\\<tag>
      --body community/<run>/<file>.png --head community/<run>/<file>.png --seed <n> --prefix community/<run>/<tag>
      [--mp 1.0] [--unet <file>.safetensors] [--steps n] [--cfg f] [--body-size WxH] [--force]
"""
import argparse, copy, json, math, os, sys

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "bfs_klein9b.api.json")
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
}


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
    ap.add_argument("--body-size", help="WxH of the body still, to print the expected output size")
    ap.add_argument("--template", default=TEMPLATE)
    ap.add_argument("--force", action="store_true", help="overwrite an existing request.api.json")
    a = ap.parse_args(argv)
    with open(a.template, encoding="utf-8") as f:
        tpl = json.load(f)
    g = build(tpl, body=a.body, head=a.head, seed=a.seed, prefix=a.prefix, mp=a.mp, unet=a.unet, steps=a.steps, cfg=a.cfg)
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
