"""R2 probe 4 (read-only): the ref_image_size / reference-slot source text in the
MiniMax H3 node module, plus the RS016 sheet geometry, quoted for R2.
read/grep are policy-denied outside 5slock, so source lines come from python reads.
"""
import json
import os
import re

CANDS = [
    r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_minimax_h3.py",
    r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes\ComfyUI_MiniMax_H3_Extender\nodes_minimax_h3.py",
]
path = None
for c in CANDS:
    if os.path.exists(c):
        path = c
        break
if path is None:
    root = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f == "nodes_minimax_h3.py":
                hits.append(os.path.join(dirpath, f))
    print("found:", hits)
    path = hits[0]
print("module:", path)
lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
print("lines:", len(lines))
for i, ln in enumerate(lines, 1):
    if "ref_image_size" in ln or "match" == ln.strip().strip('"').strip(",") or "2048" in ln:
        print("%5d: %s" % (i, ln.rstrip()))
print("---- docstring / schema block around ReferenceToVideo ----")
start = None
for i, ln in enumerate(lines, 1):
    if "class MiniMaxH3ReferenceToVideo" in ln:
        start = i
        break
if start:
    for i in range(start, min(start + 70, len(lines))):
        print("%5d: %s" % (i + 1, lines[i].rstrip()))
print("---- io.Schema for ref slots ----")
for i, ln in enumerate(lines, 1):
    if "ref_image" in ln and "Schema" in ln:
        print("%5d: %s" % (i, ln.rstrip()))
print("---- sheet geometry (RS016) ----")
sheet = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png"
if os.path.exists(sheet):
    img = __import__("PIL.Image", fromlist=["open"]).open(sheet)
    print("RS016 sheet:", img.size, img.mode, img.format)
hc = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
for f in sorted(os.listdir(hc)):
    fp = os.path.join(hc, f)
    img = __import__("PIL.Image", fromlist=["open"]).open(fp)
    print("placed:", f, img.size, img.mode, round(img.size[0] / img.size[1], 4))
src = r"C:\Users\derek\5slock\approved_characters"
print("approved src tree probe:", os.path.isdir(src))
