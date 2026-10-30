"""make_b2_request.py - build one B2 request graph from C:\\AI\\community\\templates\\b2.api.json.

B2 is the default render recipe (Derrick 2026-10-30; see templates\\b2.README.md). This script patches ONLY the
per-run fields and nothing else:
  c0.prompt  noise.noise_seed  img.image  save.filename_prefix  c0.length (frames)
It writes <arm-dir>\\request.api.json. It does not submit anything: run_graph_job.py / run_queue.py submit the
graph and run comm.guard_ok (the adults-only prompt check) before every POST.

Usage:
  C:\\AI\\director\\.venv\\Scripts\\python.exe C:\\AI\\community\\scripts\\make_b2_request.py --arm-dir <run dir>\\<tag>
      (--prompt-file <txt> | --prompt <text>) --seed <n> --image community/<file>.png --prefix community/<run>/<tag>
      [--frames <n>] [--force]
--frames defaults to the template's c0.length (124, an example only). Pass the same number as --frames to
run_graph_job.py / run_queue.py. Unknown options are refused (argparse error, rc 2).
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


def build(tpl, **vals):
    unknown = set(vals) - set(FIELDS)
    if unknown:
        raise ValueError("refused field(s): %s" % ", ".join(sorted(unknown)))
    g = copy.deepcopy(tpl)
    for key, (node, field) in FIELDS.items():
        if node not in g or field not in g[node].get("inputs", {}):
            raise ValueError("template has no %s.%s" % (node, field))
        if vals.get(key) is not None:
            g[node]["inputs"][field] = vals[key]
    return g


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build <arm-dir>\\request.api.json from the B2 template.")
    ap.add_argument("--arm-dir", required=True)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--image", required=True, help="path inside ComfyUI/input, e.g. community/X_768x1344.png")
    ap.add_argument("--prefix", required=True, help="SaveVideo filename_prefix, e.g. community/<run>/<tag>")
    ap.add_argument("--frames", type=int, default=None, help="c0.length; default = template value (example only)")
    ap.add_argument("--template", default=TEMPLATE)
    ap.add_argument("--force", action="store_true", help="overwrite an existing request.api.json")
    a = ap.parse_args(argv)

    with open(a.template, encoding="utf-8") as f:
        tpl = json.load(f)
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

    g = build(tpl, prompt=prompt, seed=a.seed, image=a.image, prefix=a.prefix, frames=frames)
    os.makedirs(a.arm_dir, exist_ok=True)
    out = os.path.join(a.arm_dir, "request.api.json")
    if os.path.exists(out) and not a.force:
        print("REFUSED: %s exists (use --force)" % out, file=sys.stderr)
        return 3
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, indent=1, ensure_ascii=False)
    print("wrote %s frames=%d (use --frames %d with run_graph_job.py / run_queue.py)" % (out, frames, frames))
    return 0


if __name__ == "__main__":
    sys.exit(main())
