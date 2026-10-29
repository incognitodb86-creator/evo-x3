"""item 4 (2026-10-29): read-only probe of B2's graph vs the current default base graph.
No GPU, no ComfyUI call, nothing written. Prints sha256 + the settings that define a render setup."""
import hashlib, json, sys

B2 = r"C:/AI/community/runs/terrace_dom_q5guide_20261028_s51083007/request.api.json"
CUR = r"C:/AI/community/p7/graphs/stock_base_tenstrip10.api.json"

KEYS = [
    ("unet", "unet_name"), ("clip", "clip_name"), ("vvae", "vae_name"), ("avae", "vae_name"),
    ("img", "image"), ("c0", "length"), ("c0", "width"), ("c0", "height"), ("c0", "ref_image_size"),
    ("m_shift", "shift_video"), ("m_shift", "shift_audio"), ("m_vsa", "selection"),
    ("m_vsa", "selection.keep_percent"), ("s0_sched", "scheduler"), ("s0_sched", "steps"),
    ("s0_sched", "denoise"), ("p2sched", "scheduler"), ("p2sched", "steps"), ("p2sched", "denoise"),
    ("ksel", "sampler_name"), ("lsu3", "mode"), ("lsu3", "mode.scale"),
    ("mkvid", "fps"), ("save", "filename_prefix"),
]


def load(p):
    return json.loads(open(p, encoding="utf-8").read())


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def summary(p):
    g = load(p)
    out = {"file": p, "sha256": sha(p), "bytes": len(open(p, "rb").read()), "nodes": len(g)}
    for k, w in KEYS:
        out[f"{k}.{w}"] = (g[k]["inputs"].get(w) if k in g else "ABSENT")
    out["classes"] = sorted({n["class_type"] for n in g.values()})
    out["prompt_bytes"] = len(g.get("c0", {}).get("inputs", {}).get("prompt", ""))
    out["ref_images"] = sorted(k for k in g if "ref_image" in json.dumps(list(g[k]["inputs"].keys())))
    return out


for p in (B2, CUR):
    s = summary(p)
    print("== %s" % p)
    for k, v in s.items():
        if k == "classes":
            print("  classes: %s" % ", ".join(v))
        elif k == "ref_images":
            print("  nodes_with_ref_image_inputs: %s" % v)
        else:
            print("  %s = %r" % (k, v))
    print()
