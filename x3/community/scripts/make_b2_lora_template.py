"""make_b2_lora_template.py - build the B2+LoRA request template (Derek 2026-10-30: "Make a diff of the template with
FC SYD lora, don't overwrite b2"). It reads C:\\AI\\community\\templates\\b2.api.json and writes
C:\\AI\\community\\templates\\b2_fc_sydney_lora.api.json. b2.api.json is never written: the script asserts its
sha256 before and after, so a run of this script cannot change the default recipe.

Delta over B2 = exactly two things, the wiring proven by a rendered cell on 2026-10-30
(runs/bj_pov_20261030/b5_s51083020_lora, built by C:/Users/derek/sydney/work/bj_pov_20261030/build_bj_pov_b5_lora.py):
  1. one new node "lora" (LoraLoader, FC_SYDNEY_h3_face_v1.safetensors, strength_model 0.7, strength_clip 1.0,
     model from unet, clip from the graph's own CLIPLoader)
  2. m_attn.inputs.model re-pointed unet -> lora, so the LoRA sits on the model chain.
Everything else is byte-identical to b2.api.json, including the five per-run placeholders (c0.prompt,
noise.noise_seed, img.image, save.filename_prefix, c0.length) that make_b2_request.py patches per run.
make_b2_request.py already takes --template, so a request from this file is built with:
  C:\\AI\\director\\.venv\\Scripts\\python.exe C:\\AI\\community\\scripts\\make_b2_request.py --template \
      C:\\AI\\community\\templates\\b2_fc_sydney_lora.api.json --arm-dir <run>\\<tag> --prompt-file <txt> \
      --seed <n> --image community/<file>.png --prefix community/<run>/<tag> [--frames <n>]

LoRA rules (skills/h3-prompting R31 + C:/AI/lora/person_alias_2026-10-29/h3/USAGE_FC_SYDNEY_h3.md): this LoRA's
trained trigger is a real person's name recorded in the private TRIGGER_MAP; a prompt for this template names that
trigger only while this LoRA is loaded, at the strength baked here (0.7, inside the face range 0.6-0.8 on a merged
beta7). No general NSFW LoRA on beta7. Frames stay a per-run choice, as in B2.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "templates", "b2.api.json")
DST = os.path.join(ROOT, "templates", "b2_fc_sydney_lora.api.json")
SRC_SHA = "124fb1331874f27803e95c81db67fe270b30dd5533732d7032105839dfd81ca2"  # b2.README.md, the default recipe
LORA = "FC_SYDNEY_h3_face_v1.safetensors"
STRENGTH_MODEL = 0.7
STRENGTH_CLIP = 1.0
PER_RUN = [("c0", "prompt"), ("noise", "noise_seed"), ("img", "image"),
           ("save", "filename_prefix"), ("c0", "length")]
LOCKED = [
    ("unet", "unet_name", "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors"),
    ("clip", "clip_name", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("c0", "height", 672), ("c0", "width", 384),
    ("c0", "ref_image_size", "max"),
    ("s0_sched", "steps", 8), ("s0_sched", "scheduler", "simple"),
    ("p2sched", "steps", 3), ("p2sched", "scheduler", "beta"), ("p2sched", "denoise", 0.4),
    ("ksel", "sampler_name", "euler"),
    ("m_shift", "shift_video", 12.0), ("m_shift", "shift_audio", 3.0),
    ("m_vsa", "selection.keep_percent", 10),
    ("lsu3", "mode.scale", 2.0),
    ("mkvid", "fps", 24),
]

rows = []


def t(name, cond):
    rows.append(("PASS " if cond else "DROP ") + name)
    return bool(cond)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def build():
    raw = open(SRC, "rb").read().decode("utf-8")
    base = json.loads(raw)
    g = json.loads(raw)  # independent copy, built from the file's own bytes
    g["lora"] = {
        "_meta": {"title": "FC_SYDNEY face LoRA on the model chain (B2 diff, Derek 2026-10-30)"},
        "class_type": "LoraLoader",
        "inputs": {"lora_name": LORA, "strength_model": STRENGTH_MODEL, "strength_clip": STRENGTH_CLIP,
                   "model": ["unet", 0], "clip": ["clip", 0]},
    }
    g["m_attn"]["inputs"]["model"] = ["lora", 0]
    return base, g


def check(base, g):
    ok = True
    ok &= t("b2.api.json sha is the README hash (default recipe is not being touched)", sha(SRC) == SRC_SHA)
    ok &= t("b2.api.json parses to 26 nodes", len(base) == 26)
    ok &= t("template gains exactly one node", len(g) == len(base) + 1 and set(g) - set(base) == {"lora"})
    li = g["lora"]["inputs"]
    ok &= t("lora node is a LoraLoader on the verified H3 face LoRA",
            g["lora"]["class_type"] == "LoraLoader" and li["lora_name"] == LORA)
    ok &= t("strength_model 0.7 inside the face range 0.6-0.8 on merged beta7",
            STRENGTH_MODEL == li["strength_model"] and 0.6 <= li["strength_model"] <= 0.8)
    ok &= t("strength_clip 1.0 (harmless while no trigger is used, R31)", li["strength_clip"] == STRENGTH_CLIP)
    ok &= t("model chain unet -> lora -> m_attn", li["model"] == ["unet", 0]
            and g["m_attn"]["inputs"]["model"] == ["lora", 0])
    ok &= t("clip path from the graph's own CLIPLoader", li["clip"] == ["clip", 0])
    drift = [n for n in base if n not in ("lora", "m_attn") and g[n] != base[n]]
    ok &= t("no drift outside lora / m_attn", not drift)
    if drift:
        rows.append("   drift: " + ",".join(drift))
    same = [n for n, k, v in LOCKED if g[n]["inputs"].get(k) != v]
    ok &= t("B2 locked dials unchanged (beta7 unet, TE, 384x672 -> 2x, euler/simple 8, beta/3/0.4, shift 12/3, "
            "VSA keep 10, ref max, 24 fps)", not same)
    if same:
        rows.append("   locked drift: " + ",".join("%s.%s" % (n, k) for n, k, v in same))
    ok &= t("per-run placeholders left in place for make_b2_request.py",
            all(k in g[n].get("inputs", {}) for n, k in PER_RUN)
            and g["c0"]["inputs"]["length"] == base["c0"]["inputs"]["length"] == 124)
    ok &= t("self-destruct probe: b2.api.json has no lora node and m_attn.model = unet",
            "lora" not in base and base["m_attn"]["inputs"]["model"] == ["unet", 0])
    return ok


def main():
    base, g = build()
    text = json.dumps(g, indent=1, ensure_ascii=False) + "\n"
    data = text.replace("\n", "\r\n").encode("utf-8")  # same bytes style as b2.api.json (CRLF)
    with open(DST, "wb") as fh:
        fh.write(data)
    ok = check(base, g)
    rt = json.loads(open(DST, encoding="utf-8").read())
    ok &= t("written file re-reads byte-equal to what was built", rt == g)
    ok &= t("b2.api.json bytes unchanged after this run", sha(SRC) == SRC_SHA)
    rows.append("wrote %s (%d bytes, sha256 %s)" % (DST, len(data), sha(DST)))
    rows.append("b2.api.json sha256 after: %s" % sha(SRC))
    report = "\n".join(rows) + "\nRESULT " + ("PASS\n" if ok else "DROP\n")
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
