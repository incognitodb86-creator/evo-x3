"""make_b2_request.py - build one B2 request graph from C:\\AI\\community\\templates\\b2.api.json.

B2 is the default render recipe (Derrick 2026-10-30; see templates\\b2.README.md). This script patches ONLY the
per-run fields and nothing else:
  c0.prompt  noise.noise_seed  img.image  save.filename_prefix  c0.length (frames)  refmods.inputs.mod_1 (--refmod)
It writes <arm-dir>\\request.api.json. It does not submit anything: run_graph_job.py / run_queue.py submit the
graph and run comm.guard_ok (the adults-only prompt check) before every POST.

Usage:
  C:\\AI\\director\\.venv\\Scripts\\python.exe C:\\AI\\community\\scripts\\make_b2_request.py --arm-dir <run dir>\\<tag>
      (--prompt-file <txt> | --prompt <text>) --seed <n> --image community/<file>.png --prefix community/<run>/<tag>
      [--frames <n>] [--force]
  RefMod identity route (templates\\b2_refmod.README.md): the same command with --refmod <installed refmod
  name> and NO --image, because a RefMod graph has no img node.
--frames defaults to the template's c0.length (124, an example only). Pass the same number as --frames to
run_graph_job.py / run_queue.py. --image is required only for a template that has an img node; --refmod only
for a template that has refmods.mod_1. Unknown options are refused (argparse error, rc 2). With --refmod absent
the graph written is byte-identical to what this script wrote before the flag existed.
"""
import argparse, copy, json, os, sys

TEMPLATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "b2.api.json")
# per-run field -> (node id, input key). Nothing else may change.
FIELDS = {
    "prompt": ("c0", "prompt"),
    "seed": ("noise", "noise_seed"),
    "image": ("img", "image"),
    "prefix": ("save", "filename_prefix"),
    "frames": ("c0", "length"),
}


# RefMod identity slot: kept out of FIELDS so a template with no refmods node is untouched by its absence.
REFMOD_FIELD = ("refmods", "mod_1")


def build(tpl, refmod=None, **vals):
    unknown = set(vals) - set(FIELDS)
    if unknown:
        raise ValueError("refused field(s): %s" % ", ".join(sorted(unknown)))
    g = copy.deepcopy(tpl)
    for key, (node, field) in FIELDS.items():
        if vals.get(key) is None:
            continue
        if node not in g or field not in g[node].get("inputs", {}):
            raise ValueError("template has no %s.%s" % (node, field))
        g[node]["inputs"][field] = vals[key]
    if refmod is not None:
        node, field = REFMOD_FIELD
        if node not in g or field not in g[node].get("inputs", {}):
            raise ValueError("template has no %s.%s (not a RefMod template)" % (node, field))
        g[node]["inputs"][field] = refmod
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build <arm-dir>\\request.api.json from the B2 template.")
    ap.add_argument("--arm-dir", required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--image", help="path inside ComfyUI/input, e.g. community/X_768x1344.png; required "
                                    "only for a template with an img node")
    ap.add_argument("--refmod", help="set refmods.inputs.mod_1, e.g. minimaxh3_sydneysweeney_v1_refmod "
                                     "(a file inside ComfyUI/models/refmods); RefMod templates only")
    ap.add_argument("--prefix", required=True, help="SaveVideo filename_prefix, e.g. community/<run>/<tag>")
    ap.add_argument("--frames", type=int, default=None, help="c0.length; default = template value (example only)")
    ap.add_argument("--template", default=TEMPLATE)
    ap.add_argument("--force", action="store_true", help="overwrite an existing request.api.json")
    a = ap.parse_args(argv)

    with open(a.template, encoding="utf-8") as f:
        tpl = json.load(f)
    if "img" in tpl and not a.image:
        ap.error("--image is required: this template has an img node")
    if a.image and "img" not in tpl:
        ap.error("--image refused: this template has no img node (a RefMod arm takes no reference image)")
    if a.refmod and ("refmods" not in tpl or "mod_1" not in tpl["refmods"].get("inputs", {})):
        ap.error("--refmod refused: this template has no refmods.mod_1 (not a RefMod template)")
    if a.prompt is not None:
        prompt = a.prompt
    else:
        with open(a.prompt_file, encoding="utf-8") as f:
            prompt = f.read()
    if not prompt.strip():
        ap.error("empty prompt")
    frames = a.frames if a.frames is not None else tpl["c0"]["inputs"]["length"]
    if frames < 1:
        ap.error("--frames must be positive")
    if (frames - 5) % 17:
        print("WARNING: %d frames is off the H3 grid ((frames - 5) %% 17 == 0, e.g. 124, 243)" % frames,
              file=sys.stderr)

    g = build(tpl, prompt=prompt, seed=a.seed, image=a.image, prefix=a.prefix, frames=frames,
              refmod=a.refmod)
    os.makedirs(a.arm_dir, exist_ok=True)
    out = os.path.join(a.arm_dir, "request.api.json")
    if os.path.exists(out) and not a.force:
        print("REFUSED: %s exists (use --force)" % out, file=sys.stderr)
        return 3
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, indent=1, ensure_ascii=False)
    print("wrote %s frames=%d refmod=%s (use --frames %d with run_graph_job.py / run_queue.py)"
          % (out, frames, a.refmod or "none", frames))
    return 0


if __name__ == "__main__":
    sys.exit(main())
