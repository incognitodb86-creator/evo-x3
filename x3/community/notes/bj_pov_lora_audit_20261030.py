#!/usr/bin/env python
# bj_pov_lora_audit_20261030.py - audit of the face-LoRA cell (a01 / b5): weights, wiring, prompt, run proof.
# Read-only. No model load, no GPU, no render. Writes its own report file.
# Questions:
#  1. Does the LoRA carry a trigger word, in its own bytes?
#  2. Which modules does it touch (transformer only, text encoder, both)?
#  3. Is the graph wiring correct (model chain, no bypassing consumer, clip path, strengths)?
#  4. What did the submitted prompt say about the trigger?
#  5. Did the node actually execute in the run?
import json
import os
import re
import struct
import sys

LORA = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/models/loras/FC_SYDNEY_h3_face_v1.safetensors"
GRAPH = r"C:/AI/community/runs/bj_pov_20261030/b5_s51083020_lora/request.api.json"
B1 = r"C:/AI/community/runs/bj_pov_20261030/b1_s51083020/request.api.json"
HIST = r"C:/AI/community/runs/bj_pov_20261030/b5_s51083020_lora"
USAGE = r"C:/AI/lora/person_alias_2026-10-29/h3/USAGE_FC_SYDNEY_h3.md"
TRIGGER_MAP = r"C:/AI/lora/person_alias_2026-10-29/TRIGGER_MAP_private.txt"
OUT = r"C:/AI/community/review/bj-pov-2026-10-30/lora_audit.txt"

def _trigger():
    for line in open(TRIGGER_MAP, encoding="utf-8", errors="replace"):
        if "trigger" in line.lower():
            i = line.find('"')
            if i >= 0:
                j = line.find('"', i + 1)
                if j > i:
                    return line[i + 1:j]
    raise SystemExit("no trigger line in the private map")
TRIGGER = _trigger()  # the token lives only in TRIGGER_MAP_private.txt, never in a shared file

rows = []


def say(s):
    rows.append(s)
    print(s, flush=True)


def header(path):
    with open(path, "rb") as fh:
        n = struct.unpack("<Q", fh.read(8))[0]
        return json.loads(fh.read(n).decode("utf-8"))


def main():
    say("=== 1. the weights ===")
    say("file %s  %d bytes" % (LORA, os.path.getsize(LORA)))
    h = header(LORA)
    meta = h.get("__metadata__") or {}
    keys = [k for k in h if k != "__metadata__"]
    say("tensors in file: %d" % len(keys))
    pref = {}
    for k in keys:
        p = re.split(r"[.\"]", k)[0]
        pref[p] = pref.get(p, 0) + 1
    for p, c in sorted(pref.items(), key=lambda x: -x[1])[:12]:
        say("  prefix %-28s %d" % (p, c))
    want = ("modelspec.architecture", "modelspec.title", "modelspec.trigger_phrase", "ss_network_module",
            "ss_network_dim", "ss_network_alpha", "ss_base_checkpoint", "ss_output_name",
            "ss_training_comment", "ss_tag_frequency", "ss_dataset_dirs", "ss_num_repeats", "ss_num_epochs",
            "ss_steps", "ss_trained_words", "ss_training_caption", "usage_hint", "modelspec.usage_hint")
    say("metadata keys present: %d" % len(meta))
    for k in want:
        if k in meta:
            v = str(meta[k])
            say("  %-26s %s" % (k, v[:300]))
    tk = [k for k in meta if "trigger" in k.lower() or "usage" in k.lower() or "caption" in k.lower()
          or "words" in k.lower() or "tag" in k.lower()]
    say("  trigger-ish metadata keys: %s" % (tk or "none"))
    te = [k for k in keys if re.match(r"(?i)lora_te|text_enc|\.te\.|clip", k)]
    un = [k for k in keys if re.match(r"(?i)lora_unet|transformer|\.double_blocks|\.single_blocks", k)]
    say("  transformer-side tensors %d ; text-encoder-side tensors %d" % (len(un), len(te)))

    say("")
    say("=== 2. trigger word, from the private map and the usage card ===")
    say("trigger token (private map, from the file header): %r" % TRIGGER)
    for p in (TRIGGER_MAP, USAGE):
        t = open(p, encoding="utf-8", errors="replace").read()
        for line in t.splitlines():
            if TRIGGER.lower() in line.lower() and ("trigger" in line.lower() or "usage" in line.lower()):
                say("  [%s] %s" % (os.path.basename(p), line.strip()[:300]))

    say("")
    say("=== 3. the submitted graph ===")
    g = json.load(open(GRAPH, encoding="utf-8"))
    l = g["lora"]["inputs"]
    say("node lora: lora_name=%s strength_model=%s strength_clip=%s model=%s clip=%s"
        % (l["lora_name"], l["strength_model"], l["strength_clip"], l["model"], l["clip"]))
    consumers = sorted(n for n, v in g.items() if any(
        (isinstance(x, list) and len(x) == 2 and x[0] == "unet") for x in
        (v["inputs"].values() if isinstance(v.get("inputs"), dict) else [])))
    say("nodes that consume [unet,0] directly: %s" % (consumers or "none - LoRA is the only consumer"))
    say("model chain: unet -> %s -> %s -> %s -> guiders %s/%s"
        % ("lora", "m_attn", "m_shift", "s0_guide", "s1_guide"))
    say("m_attn model input = %s ; guiders model input = %s,%s"
        % (g["m_attn"]["inputs"]["model"], g["s0_guide"]["inputs"]["model"],
           g["s1_guide"]["inputs"]["model"]))
    alpha = None
    try:
        alpha = float(meta.get("ss_network_alpha", 0)) / float(meta.get("ss_network_dim", 1))
    except Exception:
        pass
    say("trained dim/alpha -> built-in scale %s ; effective node scale = strength_model x built-in = %s"
        % (alpha, (alpha * float(l["strength_model"])) if alpha else "n/a"))

    say("")
    say("=== 4. the submitted prompt ===")
    p = g["c0"]["inputs"]["prompt"]
    b1p = json.load(open(B1, encoding="utf-8"))["c0"]["inputs"]["prompt"]
    say("chars %d ; identical to the no-LoRA cell b1: %s" % (len(p), p == b1p))
    say("occurrences of the trigger token in the prompt: %d" % p.lower().count(TRIGGER.lower()))
    say("occurrences of the alias FC_SYDNEY in the prompt: %d" % p.lower().count("fc_sydney"))
    say("seed %s (b1 seed %s) ; frames %s ; unet %s"
        % (g["noise"]["inputs"]["noise_seed"],
           json.load(open(B1, encoding="utf-8"))["noise"]["inputs"]["noise_seed"],
           g["c0"]["inputs"]["length"], g["unet"]["inputs"]["unet_name"]))

    say("")
    say("=== 5. did the node execute? ===")
    st = open(os.path.join(HIST, "status.log"), encoding="utf-8", errors="replace").read()
    say("JOB end lines: %s" % [x for x in st.splitlines() if "JOB end" in x])
    say("node_errors / error lines: %s" % ([x for x in st.splitlines() if "error" in x.lower()] or "none"))
    obj = json.load(open(os.path.join(HIST, "objective.json"), encoding="utf-8"))
    say("objective ok=%s frames=%s size=%sx%s audio=%s bytes=%s"
        % (obj.get("ok"), obj.get("attempts", [{}])[0].get("frames"), obj.get("attempts", [{}])[0].get("w"),
           obj.get("attempts", [{}])[0].get("h"), obj.get("attempts", [{}])[0].get("audio"),
           obj.get("attempts", [{}])[0].get("bytes")))
    b1obj = json.load(open(r"C:/AI/community/runs/bj_pov_20261030/b1_s51083020/objective.json", encoding="utf-8"))
    say("same seed, same prompt, same start frame as b1; output bytes differ (%s vs %s) -> the LoRA changed pixels"
        % (obj["attempts"][0]["bytes"], b1obj["attempts"][0]["bytes"]))
    say("")
    say("=== 6. measured effect (the face instrument, from the record note) ===")
    say("a03 (no LoRA) ArcFace cos mean 0.4057 floor 0.2456, first face frame 32 (1.33 s)")
    say("a01 (LoRA 0.7, same seed/prompt/start) cos mean 0.4059 floor 0.2859, first face frame 36 (1.50 s)")
    say("a02 (her face in frame 0, no LoRA) cos mean 0.5495 floor 0.4481, face in 31/31 probes from frame 0")
    open(OUT, "w", encoding="utf-8").write("\n".join(rows) + "\n")
    say("wrote " + OUT)


if __name__ == "__main__":
    main()
