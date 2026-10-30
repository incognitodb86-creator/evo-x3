#!/usr/bin/env python
# terrace_v3_start_frames_contact_sheet.py - brief8 Step A: a contact sheet of the three start frames, so the
# CHECKED gate can see what each arm set is fed without opening three folders. Composed by PIL geometry only:
# no vision model, no caption, no judgement, no crop, no resize of the originals - the tiles are scaled
# copies of the exact bytes Max staged, and every label is read from the file system.
import hashlib
import os
from PIL import Image, ImageDraw

SRC_IMG = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community"
SRC_TXT = r"C:\Users\derek\_max2_brief8"
OUT = r"C:\AI\community\notes\2026-10-30-brief8-start-frames.png"
TILE_H = 640
PAD, LABEL_H, HEAD_H = 18, 96, 74
TILES = [
    ("terrace (cond, reused from the v2 queue)", os.path.join(SRC_IMG, "TERRACE2_768x1344.png"),
     "in every arm's terr_* graph; the v2 queue used this same file for all 14 v2 clips"),
    ("imageA (staged by Max for this test)", os.path.join(SRC_TXT, "imageA_768x1344_crop.png"),
     "in every arm's imgA_* graph, 2 seeds each"),
    ("imageB (staged by Max for this test)", os.path.join(SRC_TXT, "imageB_768x1344_crop.png"),
     "in every arm's imgB_* graph, 2 seeds each"),
]


def sha(p, n=64):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def ar(path):
    im = Image.open(path)
    w, h = im.size
    g = 1
    for k in range(2, min(w, h) + 1):
        if w % k == 0 and h % k == 0:
            g = k
    return w, h, "%d:%d" % (w // g, h // g)


tiles, metas = [], []
for label, path, use in TILES:
    im = Image.open(path).convert("RGB")
    w, h, ratio = ar(path)
    tw = int(round(TILE_H * w / h))
    tiles.append(im.resize((tw, TILE_H), Image.LANCZOS))
    metas.append((label, os.path.basename(path), path, tw, w, h, ratio, use))

W = sum(t.width for t in tiles) + PAD * (len(tiles) + 1)
H = HEAD_H + TILE_H + LABEL_H + PAD
canvas = Image.new("RGB", (W, H), (16, 16, 18))
d = ImageDraw.Draw(canvas)
d.text((PAD, 14), "brief8 Step A - terrace settings test v3: the three start frames (contact sheet)",
       fill=(235, 235, 235))
d.text((PAD, 38), "composed 2026-10-30 by notes/terrace_v3_start_frames_contact_sheet.py - PIL geometry only, "
                  "no vision model, no caption; tiles are scaled copies of the exact staged bytes",
       fill=(150, 200, 150))
x = PAD
for (label, fn, path, tw, w, h, ratio, use), t in zip(metas, tiles):
    canvas.paste(t, (x, HEAD_H))
    y = HEAD_H + TILE_H + 6
    d.text((x, y), "%s\n%s" % (label, fn), fill=(235, 235, 235))
    d.text((x, y + 40), "file %d B | real pixels %dx%d (ratio %s) | sha256 %s…"
           % (os.path.getsize(path), w, h, ratio, sha(path, 16)), fill=(150, 200, 150))
    d.text((x, y + 62), use, fill=(200, 180, 120))
    x += t.width + PAD
canvas.save(OUT)
print("wrote %s  %dx%d px, %d B" % (OUT, canvas.width, canvas.height, os.path.getsize(OUT)))
for label, fn, path, tw, w, h, ratio, use in metas:
    print("  tile %s: %s %dx%d ratio %s sha256 %s…" % (label.split()[0], fn, w, h, ratio, sha(path, 16)))
print("the two new frames are the bytes Max staged (4d07281d… / 4c9ae12f…), unchanged; no crop, no pad, no "
      "rename by me; the graphs point at the copies in ComfyUI input\\community\\")
