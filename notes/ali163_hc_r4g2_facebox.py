"""ALI-163 R4G2 (CPU only, no GPU, no render): face boxes for the HC3-HC6 approved start stills,
so Forge can feed --box x,y,w,h to C:/AI/community/scripts/face_crop.py.

Detector = the same CPU SCRFD-10G as R4F (notes/hc_r4f_facelib.py, insightface maths, onnxruntime CPU).
Faces are printed left-to-right (x-centre) = <Subject 1> left, <Subject 2> right, which is how the
hc_r3_c0.txt / hc_r6_c0.txt subject_definitions bind the pair. Hair luma is printed as the
blonde/darkhair sanity check (sampled above the face box).

Run: C:/AI/qa_gate_venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_r4g2_facebox.py
"""
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, r"C:\AI\community\notes")
from hc_r4f_facelib import Scrfd

APPROVED = r"C:\Users\derek\5slock\approved_characters"
PICKS = [
    ("HC3", "GROK_IMAGINE_2026-10-19b/GI173.jpg", 2),
    ("HC4", "GROK_IMAGINE_2026-10-19b/GI107.jpg", 1),
    ("HC5", "GROK_IMAGINE_2026-10-19b/GI150.jpg", 1),
    ("HC6", "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD076.jpg", 2),
]


def hair_luma(img, box):
    """Mean L of a band above/around the face box (blonde ~ high, dark ~ low)."""
    x1, y1, x2, y2 = [int(v) for v in box]
    h, w = img.shape[:2]
    fh = y2 - y1
    ys, ye = max(0, y1 - int(1.2 * fh)), max(0, y1 - int(0.15 * fh))
    xs, xe = max(0, x1 - int(0.5 * fh)), min(w, x2 + int(0.5 * fh))
    if ye <= ys or xe <= xs:
        return None
    band = img[ys:ye, xs:xe]
    return round(float(cv2.cvtColor(band, cv2.COLOR_BGR2GRAY).mean()), 1)


det = Scrfd(thr=0.5)
for tag, rel, women in PICKS:
    path = os.path.join(APPROVED, rel.replace("/", os.sep))
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    H, W = img.shape[:2]
    faces = det.detect(img)
    faces.sort(key=lambda f: (f["box"][0] + f["box"][2]) / 2.0)
    print(f"{tag} {rel} {W}x{H} women_expected {women} faces_found {len(faces)}")
    for i, f in enumerate(faces, 1):
        x1, y1, x2, y2 = f["box"]
        bw, bh = x2 - x1, y2 - y1
        print(json.dumps({
            "left_to_right_index": i, "score": round(f["score"], 3),
            "box_x,y,w,h": [round(x1), round(y1), round(bw), round(bh)],
            "pct_of_frame": round(100.0 * bw * bh / (W * H), 2),
            "hair_luma": hair_luma(img, f["box"]),
            "kps0": [round(v) for v in f["kps"][0]],
        }))
print("crop side at margin 0.6 = max(w,h)*2.2; --size 512 output (400-550 allowed)")
print("numpy", np.__version__)
