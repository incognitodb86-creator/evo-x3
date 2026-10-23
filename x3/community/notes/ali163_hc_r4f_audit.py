"""ALI-163 R4F audit pass - writes C:/AI/community/notes/hc_prompt_face_audit_20261023.md (mechanical
part: prompt/reference-slot/geometry/image/face tables, verbatim prompts from the graphs).

CPU only. No GPU, no ComfyUI/llama-swap call, no render, no vision judge, no download, no install.
Reads: runs/<id>/request.api.json of c1, c2, r1, r2; ComfyUI\\input\\community\\hc picks;
ComfyUI\\output\\community\\hc_sheets; notes\\face_r4f frame PNGs.
Face metric: notes\\hc_r4f_facelib.py (SCRFD-10G + ArcFace glintr100, onnxruntime CPU) in C:\\AI\\qa_gate_venv.
Reference-canvas math mirrors the installed community node
ComfyUI\\custom_nodes\\ComfyUI_MiniMax_H3_Extender\\extender.py:2267-2310 (_prepare_shared_refs),
REF_IMAGE_SHORT_EDGE = 2048 (extender.py:113), i.e.
  ref_image_size "match": scale = min(1, sqrt(W*H/(w*h)))   (ref pixel count capped to the canvas)
  ref_image_size "max"  : scale = min(1, 2048/min(w,h))     (only downscale if a side exceeds 2048)
"""
import hashlib
import json
import math
import os
import re
import sys

import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, r"C:\AI\community\notes")
from hc_r4f_facelib import Scrfd, ArcFace, cos, mean_emb

RUNS = r"C:\AI\community\runs"
INP = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
SHEETS_DIR = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\hc_sheets"
FR = r"C:\AI\community\notes\face_r4f"
AUD = r"C:\AI\community\notes\hc_prompt_face_audit_20261023.md"
SHORT = 2048
MULT = 32
IDS = ["ali147_pool_hc_c1_s51100001", "ali147_pool_hc_c2_s51100002",
       "ali147_pool_hc_r1_s51130001", "ali147_pool_hc_r2_s51130002"]
PICKS = {"ali147_pool_hc_c1_s51100001": "HC1_Two_women_in_studio_editorial.jpg",
         "ali147_pool_hc_c2_s51100002": "HC2_Two_women_in_passionate_embrace.jpg",
         "ali147_pool_hc_r1_s51130001": "HC1_Two_women_in_studio_editorial.jpg",
         "ali147_pool_hc_r2_s51130002": "HC2_Two_women_in_passionate_embrace.jpg"}
FRAMES = {"ali147_pool_hc_r1_s51130001": [("r1s_%02d.png" % i, n) for i, n in zip(range(1, 6), range(0, 200, 40))],
          "ali147_pool_hc_r2_s51130002": [("r2s_%02d.png" % i, n) for i, n in zip(range(1, 6), range(0, 200, 40))],
          "ali147_pool_hc_c1_s51100001": [("c1w_%02d.png" % i, n) for i, n in zip(range(1, 6), range(0, 400, 80))],
          "ali147_pool_hc_c2_s51100002": [("c2w_%02d.png" % i, n) for i, n in zip(range(1, 6), range(0, 400, 80))]}
PAIR = {"c1": "HC1", "c2": "HC2", "r1": "HC1", "r2": "HC2"}
ANCHOR_SHEETS = {("HC1", "w1"): "HC1_w1_blonde_00001_.png", ("HC1", "w2"): "HC1_w2_darkhair_00001_.png",
                 ("HC2", "w1"): "HC2_w1_blonde_00001_.png", ("HC2", "w2"): "HC2_w2_darkhair_00001_.png"}
BLOCKS = ["subject_definitions", "summary", "retention_analysis", "detailed_description",
          "integrated_multimodal_description", "overall_soundscape", "non_diegetic_music"]

det = Scrfd(thr=0.4, input_size=(640, 640))
emb = ArcFace()
out = []
S = out.append


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def canvas(w, h, W, H, mode):
    scale = min(1.0, math.sqrt((W * H) / float(w * h))) if mode == "match" else min(1.0, SHORT / float(min(w, h)))
    tw = max(MULT, round(w * scale / MULT) * MULT)
    th = max(MULT, round(h * scale / MULT) * MULT)
    return tw, th, scale


def faces(path, size=(640, 640)):
    img = cv2.imread(path)
    if img is None:
        return None, []
    fs = det.detect(img, thr=0.4, input_size=size)
    for f in fs:
        f["e"] = emb.embed(img, f)
    return img, fs


def dim(path):
    with Image.open(path) as im:
        return im.size


# ---------- 1. anchors from the per-woman sheets (labels only, metric as in R4F pass 1) ----------
anchor = {}
for key, fn in ANCHOR_SHEETS.items():
    img, fs = faces(os.path.join(SHEETS_DIR, fn), size=(768, 1344))
    big = [f for f in fs if f["area"] >= 1500][:4]
    if big:
        anchor[key] = mean_emb([f["e"] for f in big])


def label(pair, e):
    a, b = anchor.get((pair, "w1")), anchor.get((pair, "w2"))
    if a is None or b is None:
        return "?", 0.0
    ca, cb = cos(e, a), cos(e, b)
    return ("w1" if ca >= cb else "w2"), max(ca, cb)


# ---------- 2. header ----------
S("# ALI-163 R4F - prompt / reference / face-box AUDIT of c1, c2, r1, r2 (2026-10-23, Forge)")
S("")
S("Task line `R4F FACE RESEARCH` (WIDENED part), ralph-community\\TASKS.md. Companion: "
  "notes\\hc_face_research_20261023.md (similarity tables T1-T3 + the ranked fix list F1-F10).")
S("No GPU, no ComfyUI/llama-swap call, no render, no vision judge, no download. Machine-measured only:")
S("prompts and reference slots come from `runs\\<id>\\request.api.json`; pixel sizes from PIL; "
  "face boxes from SCRFD-10G + ArcFace glintr100 on CPU (`C:\\AI\\qa_gate_venv`, `notes\\hc_r4f_facelib.py`); "
  "the reference-canvas math mirrors the installed community node "
  "`ComfyUI\\custom_nodes\\ComfyUI_MiniMax_H3_Extender\\extender.py:2267-2310` with "
  "`REF_IMAGE_SHORT_EDGE = 2048` (`extender.py:113`) and the `match`/`max` rule of "
  "`ref_image_size` (`extender.py:2271-2274`, default `match` at `extender.py:5007`).")
S("Builder script: `C:\\AI\\community\\notes\\ali163_hc_r4f_audit.py` (this file's tables are its output).")
S("")

# ---------- 3. per-clip sections ----------
prompt_store = {}
for jid in IDS:
    g = json.load(open(os.path.join(RUNS, jid, "request.api.json"), encoding="utf-8"))
    tag = jid.split("_")[3]
    W = g["c0"]["inputs"]["width"]
    H = g["c0"]["inputs"]["height"]
    S("## %s  (%s, %dx%d)" % (jid, tag, W, H))
    S("")
    # geometry / sampling
    s0 = g["s0_sched"]["inputs"]
    rows = [
        ("model (UNETLoader)", g["unet"]["inputs"]["unet_name"]),
        ("clip", g["clip"]["inputs"]["clip_name"]),
        ("video vae / audio vae", "%s / %s" % (g["vvae"]["inputs"]["vae_name"], g["avae"]["inputs"]["vae_name"])),
        ("c0 class_type", g["c0"]["class_type"]),
        ("c0 length (frames)", g["c0"]["inputs"].get("length")),
        ("c1 class_type", g["c1"]["class_type"]),
        ("c1 length", g["c1"]["inputs"].get("length")),
        ("continuation window", "%s" % json.dumps({k: v for k, v in g.get("win1", {}).get("inputs", {}).items()
                                                   if not isinstance(v, list)})),
        ("total frames (c0 + extension)", "%s + %s" % (g["c0"]["inputs"].get("length"),
                                                       g.get("win1", {}).get("inputs", {}).get("extension_frames"))),
        ("width x height x fps", "%sx%sx%s" % (W, H, g["mkvid"]["inputs"]["fps"])),
        ("steps / scheduler / sampler / denoise", "%s / %s / %s / %s" % (
            s0["steps"], s0["scheduler"], g["ksel"]["inputs"]["sampler_name"], s0["denoise"])),
        ("shift_video / shift_audio", "%s / %s" % (g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"])),
        ("noise_seed", g["noise"]["inputs"]["noise_seed"]),
        ("ref_image_size (c0 / c1)", "%s / %s" % (g["c0"]["inputs"].get("ref_image_size", "n/a (I2V)"),
                                                  g["c1"]["inputs"].get("ref_image_size", "n/a (I2V)"))),
        ("save prefix", g["save"]["inputs"]["filename_prefix"]),
    ]
    S("| setting | value |")
    S("|---|---|")
    for k, v in rows:
        S("| %s | %s |" % (k, v))
    S("")
    # reference slots
    S("### Reference slots (<Picture N> -> LoadImage -> file) as wired in the graph")
    S("")
    S("| chunk | slot | LoadImage node | file on disk | file px | aspect | sha256(12) | ref_image_size | "
      "ref canvas px | ref Mpx | faces in ref | biggest face px | face % of ref |")
    S("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for chunk in ("c0", "c1"):
        node = g[chunk]
        mode = node["inputs"].get("ref_image_size")
        refs = node["inputs"].get("ref_images")
        if not isinstance(refs, dict):
            refs = {}
            for k, v in node["inputs"].items():
                if k.startswith("ref_images.ref_image_"):
                    refs[k.split("_")[-1]] = v
        for slot in sorted(refs, key=lambda x: int(re.sub(r"\D", "", x) or 0)):
            nid = refs[slot][0]
            fn = g[nid]["inputs"]["image"]
            p = os.path.abspath(os.path.join(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input", fn.replace("/", os.sep)))
            if not os.path.exists(p):
                p = os.path.join(INP, os.path.basename(fn))
            w, h = dim(p)
            tw, th, sc = canvas(w, h, W, H, mode)
            _, fs = faces(p, size=(896, 896) if w > h else (768, 1344))
            big = fs[0]["box"] if fs else None
            bw, bh = (int(big[2] - big[0]), int(big[3] - big[1])) if fs else (0, 0)
            fpct = (fs[0]["area"] * (tw / float(w)) ** 2) / float(tw * th) * 100 if fs else 0
            S("| %s | <Picture %s> | `%s` (%s) | `%s` | %dx%d | %.3f | %s | %s | %dx%d | %.2f | %d | %dx%d | %.2f%% |"
              % (chunk, re.sub(r"\D", "", slot), nid, g[nid].get("_meta", {}).get("title", "") or g[nid]["class_type"],
                 fn, w, h, w / float(h), sha(p)[:12], mode, tw, th, (tw * th) / 1e6,
                 len(fs), bw, bh, fpct))
    S("")
    # prompt structure
    S("### Prompt nodes (every text node in the graph)")
    S("")
    S("| chunk | class_type | chars | blocks present (in order) | subject binding lines |")
    S("|---|---|---|---|---|")
    for chunk in ("c0", "c1"):
        pr = g[chunk]["inputs"]["prompt"]
        present = [b for b in BLOCKS if b + ":" in pr]
        lines = [l for l in pr.split("\n") if "<Subject" in l and "Picture" in l]
        prompt_store["%s_%s" % (tag, chunk)] = pr
        S("| %s | %s | %d | %s | %d |" % (chunk, g[chunk]["class_type"], len(pr),
                                          ", ".join(present) if present else "(none of the v2 block names)", len(lines)))
    S("")
    for chunk in ("c0", "c1"):
        pr = prompt_store["%s_%s" % (tag, chunk)]
        S("#### %s.%s subject/reference binding, line by line (verbatim from the graph)" % (jid, chunk))
        S("")
        S("```text")
        head = []
        for i, l in enumerate(pr.split("\n")[:24]):
            head.append("%2d| %s" % (i + 1, l))
            if l.strip() == "" and i > 3 and any(b + ":" in l for b in BLOCKS):
                break
        S("\n".join(head))
        S("```")
        S("")
    # verbatim full prompts
    for chunk in ("c0", "c1"):
        S("<details><summary>verbatim full prompt - %s.%s (%d chars)</summary>" % (jid, chunk, len(prompt_store["%s_%s" % (tag, chunk)])))
        S("")
        S("```text")
        S(prompt_store["%s_%s" % (tag, chunk)])
        S("```")
        S("")
        S("</details>")
        S("")
    # face boxes over frames
    pair = PAIR[tag]
    S("### Face box per woman over 5 evenly spaced frames (SCRFD-10G thr 0.4 at 640x640, frame 1344x768 = 1.032 Mpx)")
    S("")
    S("| frame | n_faces | woman | box px (WxH) | face area px2 | % of frame | arcface cos to her sheet anchor |")
    S("|---|---|---|---|---|---|---|")
    for fn, n in FRAMES[jid]:
        img, fs = faces(os.path.join(FR, fn))
        if not fs:
            S("| %d | 0 | - | - | - | - | - |" % n)
            continue
        for w in ("w1", "w2"):
            a = anchor.get((pair, w))
            best = max(fs, key=lambda f: cos(f["e"], a))
            bw, bh = int(best["box"][2] - best["box"][0]), int(best["box"][3] - best["box"][1])
            S("| %d | %d | %s | %dx%d | %d | %.2f%% | %.3f |"
              % (n, len(fs), w, bw, bh, int(best["area"]), best["area"] / float(img.shape[1] * img.shape[0]) * 100,
                 cos(best["e"], a)))
    S("")

# ---------- 4. start stills ----------
S("## Start stills (the approved picks, as placed in ComfyUI\\input\\community\\hc)")
S("")
S("| pick (pair) | file | px | aspect | sha256(12) | faces | per-face box px | face area | % of frame | label | cos to that sheet |")
S("|---|---|---|---|---|---|---|---|---|---|---|")
seen = set()
for jid, fn in PICKS.items():
    if fn in seen:
        continue
    seen.add(fn)
    pair = PAIR[jid.split("_")[3]]
    p = os.path.join(INP, fn)
    w, h = dim(p)
    _, fs = faces(p, size=(896, 896))
    for i, f in enumerate(fs):
        lab, c = label(pair, f["e"])
        other = max([cos(f["e"], anchor[(pair, x)]) for x in ("w1", "w2") if anchor.get((pair, x)) is not None] or [0])
        S("| %s (%s) | `%s` | %dx%d | %.3f | %s | %d | %dx%d | %d | %.2f%% | %s | %.3f |"
          % (fn, pair, fn, w, h, w / float(h), sha(p)[:12], len(fs),
             int(f["box"][2] - f["box"][0]), int(f["box"][3] - f["box"][1]), int(f["area"]),
             f["area"] / float(w * h) * 100, lab, other))
S("")

# ---------- 5. sheets ----------
S("## Reference sheets (ComfyUI\\output\\community\\hc_sheets, all 10 as built by R3)")
S("")
S("| sheet | px | aspect | Mpx | sha256(12) | faces | face boxes px (WxH, y-band) | biggest face % of sheet | panel reading |")
S("|---|---|---|---|---|---|---|---|---|")
for fn in sorted(os.listdir(SHEETS_DIR)):
    p = os.path.join(SHEETS_DIR, fn)
    w, h = dim(p)
    _, fs = faces(p, size=(768, 1344))
    boxes = ["%dx%d@y%d" % (int(f["box"][2] - f["box"][0]), int(f["box"][3] - f["box"][1]), int(f["box"][1])) for f in fs]
    bands = sorted({min(int(f["box"][1]) // (h // 3), 2) for f in fs})
    S("| `%s` | %dx%d | %.3f | %.2f | %s | %d | %s | %.2f%% | faces in y-third(s) %s of 3 |"
      % (fn, w, h, w / float(h), (w * h) / 1e6, sha(p)[:12], len(fs), ", ".join(boxes[:8]),
         (fs[0]["area"] / float(w * h) * 100) if fs else 0, bands))
S("")

# ---------- 6. cross-clip ref-slot summary ----------
S("## Slot/size summary (the machine part of the comparison)")
S("")
S("| clip | c0 refs (kind) | c1 refs (kind) | c0 ref_image_size | c1 ref_image_size | pick in c1 refs? | sheet in c1 refs? | c0 ref Mpx total | c1 ref Mpx total | target canvas Mpx |")
S("|---|---|---|---|---|---|---|---|---|---|")
for jid in IDS:
    g = json.load(open(os.path.join(RUNS, jid, "request.api.json"), encoding="utf-8"))

    def slots(chunk):
        refs = g[chunk]["inputs"].get("ref_images")
        if isinstance(refs, dict):
            return [refs[k][0] for k in refs]
        return [v[0] for k, v in g[chunk]["inputs"].items() if k.startswith("ref_images.ref_image_")]

    pickbase = os.path.basename(PICKS[jid])

    def kind(nid):
        return "pick" if os.path.basename(g[nid]["inputs"]["image"]) == pickbase else "sheet"

    def mpx(chunk):
        mode = g[chunk]["inputs"].get("ref_image_size")
        tot = 0.0
        for nid in slots(chunk):
            p = os.path.join(INP, os.path.basename(g[nid]["inputs"]["image"]))
            w, h = dim(p)
            tw, th, _ = canvas(w, h, g[chunk]["inputs"]["width"], g[chunk]["inputs"]["height"], mode)
            tot += (tw * th) / 1e6
        return tot

    a, b = [kind(n) for n in slots("c0")], [kind(n) for n in slots("c1")]
    S("| %s | %d %s | %d %s | %s | %s | %s | %s | %.2f | %.2f | %.2f |"
      % (jid.split("_hc_")[1], len(a), a, len(b), b,
         g["c0"]["inputs"].get("ref_image_size", "n/a"), g["c1"]["inputs"].get("ref_image_size", "n/a"),
         "pick" in a and "pick" in b, "sheet" in b,
         mpx("c0"), mpx("c1"), (g["c0"]["inputs"]["width"] * g["c0"]["inputs"]["height"]) / 1e6))
S("")
S("<!--ANALYSIS-->")
S("")

open(AUD, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote %s  %d lines  %d bytes" % (AUD, len(out), os.path.getsize(AUD)))
