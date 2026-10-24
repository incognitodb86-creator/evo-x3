"""ALI-163 R4G2 crop verification (CPU only, no GPU, no vision judge, no render).

For every face crop in ComfyUI\\input\\community\\hc that R6-R9 now reference:
  1. PIL size (must be square, 400-550 px) + sha256
  2. SCRFD-10G finds >= 1 face in the crop, and the crop's largest face is BIG (a real close-up)
  3. ArcFace (glintr100) cosine between the crop face and the same face box in the approved source still
     -> proves the crop is the SAME woman, not a neighbour/background face
  4. for pair picks, cosine between the two crops (the two women are distinct: low similarity)

Run: C:/AI/qa_gate_venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_r4g2_verify.py
Writes notes/face_r4g2/r4g2_table.txt.
"""
import hashlib
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, r"C:\AI\community\notes")
from hc_r4f_facelib import ArcFace, Scrfd, cos

HC = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
APPROVED = r"C:\Users\derek\5slock\approved_characters"
OUT = r"C:\AI\community\notes\face_r4g2"
CROPS = [
    # tag, crop file, source pick, face box used by face_crop.py, pair group
    ("HC3_w1", "HC3_w1_face.png", "GROK_IMAGINE_2026-10-19b/GI173.jpg", [382, 0, 171, 240], "HC3"),
    ("HC3_w2", "HC3_w2_face.png", "GROK_IMAGINE_2026-10-19b/GI173.jpg", [799, 228, 222, 204], "HC3"),
    ("HC4_w1", "HC4_w1_face.png", "GROK_IMAGINE_2026-10-19b/GI107.jpg", [830, 56, 107, 143], "HC4"),
    ("HC5_w1", "HC5_w1_face.png", "GROK_IMAGINE_2026-10-19b/GI150.jpg", [307, 154, 163, 212], "HC5"),
    ("HC6_w1", "HC6_w1_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD076.jpg", [471, 33, 209, 157], "HC6"),
    ("HC6_w2", "HC6_w2_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD076.jpg", [783, 68, 133, 190], "HC6"),
    # HC15 clip 1 (fix_plan 0.1, Max 2:20 PM CT Oct 24): both women of the approved BD002 pair still
    ("HC15A_w1", "BD002_w1_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD002.jpg", [252, 93, 214, 105], "HC15A"),
    ("HC15A_w2", "BD002_w2_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD002.jpg", [738, 44, 129, 175], "HC15A"),
    # HC15 clip 2 (fix_plan 0.1, HC15 pass 2): both women of the approved BD006 pair still
    ("HC15B_w1", "BD006_w1_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD006.jpg", [215, 146, 156, 91], "HC15B"),
    ("HC15B_w2", "BD006_w2_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD006.jpg", [537, 90, 109, 141], "HC15B"),
    # HC15 clip 3 (fix_plan 0.1, HC15 pass 3): both women of the approved BD013 pair still
    ("HC15C_w1", "BD013_w1_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD013.jpg", [414, 71, 155, 106], "HC15C"),
    ("HC15C_w2", "BD013_w2_face.png", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD013.jpg", [709, 58, 113, 154], "HC15C"),
    # HC15 clip 4 (fix_plan 0.1, HC15 pass 4): the solo woman of the approved GI046 start still (1 face, HC15D)
    ("HC15D_w1", "GI046_w1_face.png", "GROK_IMAGINE_2026-10-19/GI046.jpg", [341, 330, 201, 201], "HC15D"),
    # HC15 clip 5 (fix_plan 0.1, HC15 pass 6): the solo woman of the approved GI063 start still (1 face, HC15E, box h/w 1.22 frontal)
    ("HC15E_w1", "GI063_w1_face.png", "GROK_IMAGINE_2026-10-19/GI063.jpg", [209, 233, 166, 202], "HC15E"),
]

det, rec = Scrfd(thr=0.5), ArcFace()
rows, fails, emb = [], [], {}
os.makedirs(OUT, exist_ok=True)
src_cache = {}
for tag, name, src, box, group in CROPS:
    p = os.path.join(HC, name)
    with Image.open(p) as im:
        w, h = im.size
    sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
    img = cv2.imread(p, cv2.IMREAD_COLOR)
    faces = det.detect(img)
    f = faces[0] if faces else None
    crop_px = 0.0
    c_in_src = None
    if f:
        x1, y1, x2, y2 = f["box"]
        crop_px = round(100.0 * (x2 - x1) * (y2 - y1) / (w * h), 1)
        simg = src_cache.get(src)
        if simg is None:
            simg = cv2.imread(os.path.join(APPROVED, src.replace("/", os.sep)), cv2.IMREAD_COLOR)
            src_cache[src] = simg
        # the same face in the source: detect there and keep the face whose centre is nearest the box centre
        bx, by, bw, bh = box
        cx, cy = bx + bw / 2.0, by + bh / 2.0
        sf = min(det.detect(simg), key=lambda d: ((d["box"][0] + d["box"][2]) / 2 - cx) ** 2 +
                 ((d["box"][1] + d["box"][3]) / 2 - cy) ** 2)
        c_in_src = round(cos(rec.embed(img, f), rec.embed(simg, sf)), 3)
        emb[tag] = (rec.embed(img, f), group)
    row = {"tag": tag, "file": name, "px": [w, h], "sha256_12": sha[:12], "faces_in_crop": len(faces),
           "face_pct_of_crop": crop_px, "cos_crop_vs_source_face": c_in_src, "src": src, "box": box}
    rows.append(row)
    ok = w == h and 400 <= w <= 550 and len(faces) >= 1 and crop_px >= 12.0 and (c_in_src or 0) >= 0.45
    print(("PASS " if ok else "FAIL ") + json.dumps(row))
    if not ok:
        fails.append(tag)

for g in sorted({r["tag"].split("_")[0] for r in rows}):
    tags = [t for t, (_, grp) in emb.items() if grp == g and len([x for x in emb.values() if x[1] == g]) == 2]
    if len(tags) == 2:
        c = round(cos(emb[tags[0]][0], emb[tags[1]][0]), 3)
        print(f"PAIR {g} cos({tags[0]} vs {tags[1]}) = {c} (the two women must be distinct: expect low)")

lines = [json.dumps(r) for r in rows]
open(os.path.join(OUT, "r4g2_table.txt"), "w", encoding="utf-8").write(
    "ALI-163 R4G2 face-crop verification (CPU SCRFD-10G + ArcFace glintr100, qa_gate_venv)\n"
    + "\n".join(lines) + "\n")
print("FAILS " + json.dumps(fails) if fails else "ALL CROP CHECKS PASS")
sys.exit(1 if fails else 0)
