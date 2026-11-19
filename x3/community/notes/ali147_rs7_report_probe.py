"""ALI-147 RS7 report probe (read-only, CPU only). 2026-10-22.

Prints the held-equal / held-different table for the ALI-147 pool arms straight from the graphs
on disk (the graph each arm rendered: <id>.api.json where present, else request.api.json), so
REPORT.md quotes measured values. No writes, no renders, no GPU call.

  python C:/AI/community/notes/ali147_rs7_report_probe.py
"""
import hashlib
import json
import os

RUNS = r"C:/AI/community/runs"
CTRL = os.path.join(RUNS, "ali147_pool_ctrl_s51080000", "submitted_graph.pretty.json")
ARMS = [
    ("CTRL", os.path.join(RUNS, "ali147_pool_ctrl_s51080000", "submitted_graph.pretty.json")),
    ("FIX1", os.path.join(RUNS, "ali147_pool_fix1_s51080000", "ali147_pool_fix1_s51080000.api.json")),
    ("FIX5", os.path.join(RUNS, "ali147_pool_fix5_s51080000", "ali147_pool_fix5_s51080000.api.json")),
    ("REFSHEET", os.path.join(RUNS, "ali147_pool_refsheet_s51080000", "ali147_pool_refsheet_s51080000.api.json")),
    ("REFSHEET_B", os.path.join(RUNS, "ali147_pool_refsheet_b_s51080000", "ali147_pool_refsheet_b_s51080000.api.json")),
    ("FIX4", os.path.join(RUNS, "ali147_pool_fix4_s51080000", "ali147_pool_fix4_s51080000.api.json")),
]


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load(p):
    raw = open(p, encoding="utf-8").read()
    return raw, json.loads(raw)


def facts(raw, g):
    """(bytes, sha256, nodes, seed, steps per scheduler, sampler/scheduler names, shift,
    width/height/fps, window/lengths, prompts sha, LoadImage strings, class of c1, ref wiring)."""
    f = {"bytes": len(raw.encode("utf-8")), "sha256": sha(raw), "nodes": len(g)}
    f["graph_sha256_file"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    f["req_sha256_file"] = None
    unet = [v for v in g.values() if v["class_type"] == "UNETLoader"]
    f["unet"] = unet[0]["inputs"]["unet_name"] if unet else None
    for tag, nd in g.items():
        if nd["class_type"] == "KSamplerAdvanced":
            f["seed_" + tag] = nd["inputs"].get("seed")
            f["sampler_" + tag] = nd["inputs"].get("sampler_name")
        if nd["class_type"] == "BasicScheduler":
            f["steps_" + tag] = nd["inputs"].get("steps")
            f["sched_" + tag] = nd["inputs"].get("scheduler")
        if nd["class_type"] == "MiniMaxH3SigmaShift":
            f["shift"] = (nd["inputs"].get("shift_video"), nd["inputs"].get("shift_audio"))
        if nd["class_type"] == "MiniMaxH3GuidedContinuationWindow":
            f["win_" + tag] = (nd["inputs"].get("window_frame_count"), nd["inputs"].get("context_length"))
        if nd["class_type"] in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo"):
            f[tag + "_class"] = nd["class_type"]
            f[tag + "_length"] = nd["inputs"].get("length")
            f[tag + "_refsize"] = nd["inputs"].get("ref_image_size")
            f[tag + "_refs"] = {k: v for k, v in nd["inputs"].items() if k.startswith("ref_image_")}
            p = nd["inputs"].get("prompt")
            if isinstance(p, str):
                f[tag + "_prompt"] = (len(p), sha(p))
            if isinstance(p, list):
                f[tag + "_prompt"] = "link " + str(p)
        if nd["class_type"] == "PromptPackBridge":
            keys = sorted(k for k in nd["inputs"] if k.startswith("prompt_"))
            f["ppack_prompts"] = [(k, len(str(nd["inputs"][k])), sha(str(nd["inputs"][k]))[:16]) for k in keys]
        if nd["class_type"] == "MiniMaxH3Extender":
            pack = json.loads(nd["inputs"]["clips_json"])
            cl = pack["clips"]
            f["ext_clips"] = [(c.get("id"), c.get("validated"), c.get("duration"),
                               round(float(c.get("duration")) * 24), sha(str(c.get("prompt", "")))[:16]) for c in cl]
            f["ext_mode"] = (nd["inputs"].get("run_mode"), nd["inputs"].get("generation_mode"),
                             nd["inputs"].get("motion_context"), nd["inputs"].get("refine_enabled"))
        if nd["class_type"] == "LoadImage":
            f["load_" + tag] = nd["inputs"]["image"]
        if nd["class_type"] == "SaveVideo":
            f["save"] = nd["inputs"]["filename_prefix"]
        if nd["class_type"] == "VAELoader":
            f.setdefault("vaes", []).append(nd["inputs"]["vae_name"])
        if nd["class_type"] == "BlockSparseAttention":
            f["vsa"] = nd["inputs"].get("selection")
        if nd["class_type"] == "CLIPLoader":
            f["clip"] = nd["inputs"].get("clip_name")
    return f


base_raw, base_g = load(CTRL)
bf = facts(base_raw, base_g)
print("BASE(CTRL)", json.dumps(bf, sort_keys=True, default=str))
print()
for name, p in ARMS[1:]:
    if not os.path.exists(p):
        print("==", name, "MISSING", p)
        continue
    raw, g = load(p)
    f = facts(raw, g)
    same = {k: f[k] for k in bf if k in f and bf[k] == f[k]}
    diff = {k: (bf.get(k), f.get(k)) for k in set(bf) | set(f) if bf.get(k) != f.get(k)}
    print("==", name, os.path.basename(p), "bytes", f["bytes"], "sha256", f["sha256"])
    print("   identical to CTRL:", json.dumps(sorted(same), sort_keys=True))
    print("   differs from CTRL (CTRL, ARM):", json.dumps(diff, sort_keys=True, default=str))
    print()

print("== per-arm request.api.json vs the rendered .api.json (graph provenance)")
for name, d in [("REFSHEET", "ali147_pool_refsheet_s51080000"), ("REFSHEET_B", "ali147_pool_refsheet_b_s51080000"),
                ("FIX1", "ali147_pool_fix1_s51080000"), ("FIX5", "ali147_pool_fix5_s51080000"),
                ("FIX4", "ali147_pool_fix4_s51080000")]:
    a = os.path.join(RUNS, d, "request.api.json")
    b = os.path.join(RUNS, d, d + ".api.json")
    if os.path.exists(a) and os.path.exists(b):
        ra, rb = open(a, "rb").read(), open(b, "rb").read()
        print("  ", name, "request bytes", len(ra), "sha", hashlib.sha256(ra).hexdigest(),
              "rendered bytes", len(rb), "sha", hashlib.sha256(rb).hexdigest(), "byte-identical:", ra == rb)
    else:
        print("  ", name, "missing one of the two files")
