#!/usr/bin/env python3
"""post_graph_build.py - build the A/B/C post-processing graph: RTX Video Super Resolution 1.2x.

Spec: C:/AI/community/notes/ab_q4_q5_brief_2026-10-28.md ("apply RTX Video Super Resolution at 1.2x with
quality ULTRA", then "encode libx264 -preset slow -crf 18"). The raw render is never re-encoded in place:
this graph reads the raw from ComfyUI's input dir and writes an upscaled video, and the crf-18 encode of
that is done by finalize_encode.py with ffmpeg.

Node spec read live from the server (scripts/probe_full.py RTXVideoSuperResolution): inputs
  images (IMAGE), resize_type (V3 dynamic combo: "scale by multiplier" {resize_type.scale 1.0-4.0, default 2.0}
  | "target dimensions" {width,height}), quality (COMBO LOW|MEDIUM|HIGH|ULTRA, default ULTRA);
  output upscaled_images (IMAGE). The pack README's names (video/process_mode/max_frames_num) are the
  OLD shape; the live node is image-based, so frames come from VHS_LoadVideo, which also carries the
  audio through to CreateVideo. VHS is installed and registered (probe_full.py VHS_LoadVideo).
The input video must sit under ComfyUI's input dir; VHS lists flat names, so the caller copies it to
input/<in_name>.mp4 first.

Usage: post_graph_build.py <out_dir> <tag> <in_name_in_comfy_input> [scale] [quality] [fps]
Writes <out_dir>/request.api.json (+ .pretty) and a self-check log. No GPU work here.
"""
import os, sys, json

SCALE = float(sys.argv[4]) if len(sys.argv) > 4 else 1.2
QUALITY = sys.argv[5] if len(sys.argv) > 5 else "ULTRA"
FPS = int(sys.argv[6]) if len(sys.argv) > 6 else 24
OUT, TAG, IN_NAME = sys.argv[1], sys.argv[2], sys.argv[3]
assert QUALITY in ("LOW", "MEDIUM", "HIGH", "ULTRA"), QUALITY
assert 0.2 <= SCALE <= 4.0, SCALE
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"

g = {
    "vhs": {"class_type": "VHS_LoadVideo", "inputs": {"video": IN_NAME, "force_rate": 0, "custom_width": 0,
            "custom_height": 0, "frame_load_cap": 0, "skip_first_frames": 0, "select_every_nth": 1}},
    "rtx": {"class_type": "RTXVideoSuperResolution", "inputs": {"images": ["vhs", 0],
            "resize_type": "scale by multiplier", "resize_type.scale": SCALE, "quality": QUALITY}},
    "mk": {"class_type": "CreateVideo", "inputs": {"images": ["rtx", 0], "audio": ["vhs", 2], "fps": FPS}},
    "save": {"class_type": "SaveVideo", "inputs": {"video": ["mk", 0], "filename_prefix": f"community/{TAG}/{TAG}",
             "format": "auto", "codec": "auto"}},
}

checks = [
    ("input = the raw render staged in ComfyUI input", os.path.exists(os.path.join(C, "input", IN_NAME))),
    ("RTX node + 1.2x by multiplier + ULTRA", g["rtx"]["class_type"] == "RTXVideoSuperResolution"
     and g["rtx"]["inputs"]["resize_type"] == "scale by multiplier" and g["rtx"]["inputs"]["resize_type.scale"] == SCALE
     and g["rtx"]["inputs"]["quality"] == QUALITY),
    ("frames from VHS, audio kept", g["rtx"]["inputs"]["images"] == ["vhs", 0] and g["mk"]["inputs"]["audio"] == ["vhs", 2]),
    ("no resampling of frame rate (force_rate 0) and no frame dropping",
     g["vhs"]["inputs"]["force_rate"] == 0 and g["vhs"]["inputs"]["frame_load_cap"] == 0
     and g["vhs"]["inputs"]["select_every_nth"] == 1 and g["vhs"]["inputs"]["skip_first_frames"] == 0),
    ("fps preserved", g["mk"]["inputs"]["fps"] == FPS),
    ("nothing else in the graph (no generator, no model, no latent work)",
     set(g) == {"vhs", "rtx", "mk", "save"}),
    ("output prefix", g["save"]["inputs"]["filename_prefix"] == f"community/{TAG}/{TAG}"),
]
os.makedirs(OUT, exist_ok=True)
logf = os.path.join(OUT, "build_graph.log")
with open(logf, "w", encoding="utf-8") as f:
    for name, ok in checks:
        f.write("CHECK %-56s %s\n" % (name, "ok" if ok else "FAIL"))
    f.write(f"post graph: in={IN_NAME} scale={SCALE} quality={QUALITY} fps={FPS} nodes={len(g)}\n")
print("\n".join(f"{name}: {'ok' if ok else 'FAIL'}" for name, ok in checks))
if not all(ok for _, ok in checks):
    sys.exit("post_graph_build: self-check FAIL")
json.dump(g, open(os.path.join(OUT, "request.api.json"), "w", encoding="utf-8"), indent=1)
json.dump(g, open(os.path.join(OUT, "request.api.pretty.json"), "w", encoding="utf-8"), indent=1)
print("wrote", os.path.join(OUT, "request.api.json"))
