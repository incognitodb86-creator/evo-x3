r"""make_b2_refmod_template.py - build the B2 + RefMod request template from a verified working graph.

Lane Ralph (Sydney), 2026-11-04, plan item 7; written first as the enabler of item 4a. Shape follows
make_b2_lora_template.py: read one source graph, write a template file, assert everything, and never
touch the source (its sha256 is checked before and after, so this run cannot edit a rendered graph).

Source = the arm the human rated good in the voice-face 2x2 cell:
  C:/AI/community/runs/vf_20261104/vf_b/request.api.json  (rendered 2026-11-04 17:21:30 CT,
  status.log "OBJECTIVE ok vf_b frames=192 size=768x1344 audio=True").
Delta source -> template = the per-run placeholders only:
  refmods.inputs.mod_1 -> "(none)"   the identity slot (make_b2_request.py --refmod)
  c0.prompt            -> ""         prompt text is a per-run field; the working prompt names a real
                                     person, and a shared file must not carry a real-person name, so
                                     the template keeps no prompt text
  save.filename_prefix -> "community/<run>/<tag>"   the per-run output prefix placeholder
Everything else is byte-equal to the source: the frozen dial, the 768x1344 canvas, and all 24 loader
slot keys, which are REQUIRED inputs of MiniMaxH3RefModsLoader (nodes.py:754,763-781, MAX_SLOTS=8).
"(none)" is inert: load() skips a slot whose mod is "(none)" or whose strength <= 0 (nodes.py:801-807).

Per-run fields patched by make_b2_request.py: c0.prompt, noise.noise_seed, save.filename_prefix,
c0.length (frames), refmods.inputs.mod_1 (--refmod). The graph has no img node, so --image is not
required for this template.

Usage:
  C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\make_b2_refmod_template.py \
      [--src <verified graph>] [--dst <template>]
Exits 0 only when every assertion passes; prints PASS/DROP lines. No GPU, no HTTP, no model load.
"""
import argparse
import hashlib
import json
import os
import sys

ROOT = r"C:\AI\community"  # templates/ and runs/ stay in the community work tree (F6b)
DEFAULT_SRC = r"C:\AI\community\runs\vf_20261104\vf_b\request.api.json"
DEFAULT_DST = os.path.join(ROOT, "templates", "b2_refmod.api.json")
SRC_SHA = "39cba43784e89606"  # the vf_b graph after the item-3c slot fix; the file that rendered ok
NAMES_JSON = r"C:\Users\derek\sydney\work\voice-face-2x2-2026-11-04\names.json"  # lane-private, values never printed
NONE = "(none)"
PREFIX_PLACEHOLDER = "community/<run>/<tag>"
MAX_SLOTS = 8  # MiniMaxH3RefModsLoader.MAX_SLOTS (nodes.py:754)
SLOT_KEYS = ["%s_%d" % (p, i) for i in range(1, MAX_SLOTS + 1) for p in ("mod", "strength", "copies")]
PER_RUN = [("c0", "prompt"), ("noise", "noise_seed"), ("save", "filename_prefix"), ("c0", "length"),
           ("refmods", "mod_1")]
LOCKED = [  # the frozen dial of the rendered cell, baked into the template
    ("unet", "unet_name", "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors"),
    ("clip", "clip_name", "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("c0", "width", 768), ("c0", "height", 1344), ("c0", "ref_image_size", "match"),
    ("s0_sched", "steps", 8), ("s0_sched", "scheduler", "simple"), ("s0_sched", "denoise", 1.0),
    ("ksel", "sampler_name", "euler"),
    ("m_shift", "shift_video", 12.0), ("m_shift", "shift_audio", 3.0),
    ("m_vsa", "selection.keep_percent", 10), ("m_vsa", "selection", "vsa"),
    ("mkvid", "fps", 24),
]

rows = []


def t(name, cond, detail=""):
    rows.append(("PASS " if cond else "DROP ") + name + ((" | " + str(detail)) if detail else ""))
    return bool(cond)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build templates/b2_refmod.api.json from a verified RefMod graph.")
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--dst", default=DEFAULT_DST)
    a = ap.parse_args(argv)

    src_before = sha(a.src)
    rows.append("source %s %d B sha256 %s" % (a.src, os.path.getsize(a.src), src_before))
    ok = t("source graph sha starts with the rendered-arm prefix %s" % SRC_SHA, src_before.startswith(SRC_SHA))
    src = json.loads(open(a.src, encoding="utf-8").read())

    g = json.loads(open(a.src, encoding="utf-8").read())  # independent copy from the file's own bytes
    g["refmods"]["inputs"]["mod_1"] = NONE
    g["c0"]["inputs"]["prompt"] = ""
    g["save"]["inputs"]["filename_prefix"] = PREFIX_PLACEHOLDER

    changed = sorted(n for n in src if g[n] != src[n])
    t("same node set, no node added or removed", set(g) == set(src) and len(g) == len(src))
    t("delta over the source touches only the three per-run-owning nodes",
      changed == ["c0", "refmods", "save"], "changed nodes: %s" % changed)
    ref_changed = [k for k, v in g["refmods"]["inputs"].items() if src["refmods"]["inputs"].get(k) != v]
    c_changed = [k for k, v in g["c0"]["inputs"].items() if src["c0"]["inputs"].get(k) != v]
    s_changed = [k for k, v in g["save"]["inputs"].items() if src["save"]["inputs"].get(k) != v]
    t("inside those nodes only the per-run keys differ (refmods.mod_1, c0.prompt, save.filename_prefix)",
      ref_changed == ["mod_1"] and c_changed == ["prompt"] and s_changed == ["filename_prefix"],
      "refmods=%s c0=%s save=%s" % (ref_changed, c_changed, s_changed))
    t("identity slot is the template placeholder (none)", g["refmods"]["inputs"]["mod_1"] == NONE)
    t("prompt placeholder is empty (no prompt text in a shared template)", g["c0"]["inputs"]["prompt"] == "")
    t("prefix is the per-run placeholder", g["save"]["inputs"]["filename_prefix"] == PREFIX_PLACEHOLDER)
    missing = [k for k in SLOT_KEYS if k not in g["refmods"]["inputs"]]
    t("all 24 loader slot keys present (mod/strength/copies 1-8)", not missing, "missing: %s" % missing)
    t("no active identity in the template (a template is not a run)",
      not [i for i in range(1, MAX_SLOTS + 1)
           if g["refmods"]["inputs"]["mod_%d" % i] != NONE
           and float(g["refmods"]["inputs"]["strength_%d" % i]) > 0])
    drift = [n + "." + k for n, k, v in LOCKED if g[n]["inputs"].get(k) != v]
    t("frozen dial baked in (beta7 unet, text encoder, 768x1344, ref_image_size match, euler/simple 8 "
      "steps denoise 1.0, shift 12/3, VSA vsa keep 10, 24 fps)", not drift, "drift: %s" % drift)
    t("frames stay a per-run field (source value 192 is left in the file, builder overrides)",
      g["c0"]["inputs"]["length"] == src["c0"]["inputs"]["length"] == 192)
    t("no img node (a RefMod arm takes no reference image, so --image is not required)", "img" not in g)
    t("per-run placeholders present for make_b2_request.py",
      all(k in g[n].get("inputs", {}) for n, k in PER_RUN))

    text = json.dumps(g, indent=1, ensure_ascii=False) + "\n"
    tokens = []
    try:  # lane-private file, read-only; the values are never printed, only the count and any hits
        names = json.load(open(NAMES_JSON, encoding="utf-8"))
        for arm in (names.get("arms") or {}).values():
            for word in str(arm.get("name", "")).replace("-", " ").split():
                tokens.append(word.lower())
            slug = str(arm.get("refmod", "")).strip()
            if slug:
                for part in slug.replace("minimaxh3_", "").replace("_refmod", "").split("_"):
                    tokens.append(part.lower())
        tokens = sorted({tk for tk in tokens if len(tk) >= 4 and tk.isalpha() and tk not in ("v1", "none", "refmod")})
    except Exception as ex:  # absence is reported, never fatal
        rows.append("NOTE identity-token check skipped: %s" % ex)
    hits = [tk for tk in tokens if tk.lower() in text.lower()]
    t("no real-person string in the shared template (tokens from the lane-private names.json, "
      "values never printed: %d checked)" % len(tokens), not hits, "hits: %s" % hits)

    with open(a.dst, "wb") as fh:
        fh.write(text.encode("utf-8"))
    ok = t("written file re-reads equal to what was built", json.load(open(a.dst, encoding="utf-8")) == g) and ok
    ok = t("source graph bytes unchanged after this run", sha(a.src) == src_before) and ok
    rows.append("wrote %s (%d B, sha256 %s)" % (a.dst, os.path.getsize(a.dst), sha(a.dst)))
    ok = all(r.startswith(("PASS ", "NOTE ", "source ", "wrote ")) for r in rows) and ok
    print("\n".join(rows) + "\nRESULT " + ("PASS\n" if ok else "DROP\n"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
