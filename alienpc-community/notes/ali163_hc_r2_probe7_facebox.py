"""R2 probe 7 (read-only, CPU, INPUTS ONLY - never on rendered output, no vision judge):
objective face-box size metric on the reference images the graph feeds the model.
OpenCV Haar cascades ship with the cv2 wheel (cv2.data.haarcascades); mediapipe/scipy are
not installed on this box, so this is a detector box metric, not an identity/embedding score.
No face metric exists for rendered output (FaceEmbedDistance never measured, REPORT_rs7 s5).
"""
import json
import math
import os

import cv2
import numpy as np
from PIL import Image

PICKS = {
    "HC1": r"C:\Users\derek\5slock\approved_characters\FLOW_BLONDE_DARK_PAIRS_2026-10-19\BD004.jpg",
    "HC2": r"C:\Users\derek\5slock\approved_characters\FLOW_BLONDE_DARK_PAIRS_2026-10-19\BD007.jpg",
    "HC3": r"C:\Users\derek\5slock\approved_characters\GROK_IMAGINE_2026-10-19b\GI173.jpg",
    "HC4": r"C:\Users\derek\5slock\approved_characters\GROK_IMAGINE_2026-10-19b\GI107.jpg",
    "HC5": r"C:\Users\derek\5slock\approved_characters\GROK_IMAGINE_2026-10-19b\GI150.jpg",
    "HC6": r"C:\Users\derek\5slock\approved_characters\FLOW_BLONDE_DARK_PAIRS_2026-10-19\BD076.jpg",
    "RS016_sheet": r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png",
    "POOL_still": r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\POOL_768x1344.png",
}
CASCADES = {
    "frontal": "haarcascade_frontalface_default.xml",
    "frontal_alt": "haarcascade_frontalface_alt2.xml",
    "profile": "haarcascade_profileface.xml",
}
CANVAS = (1344, 768)


def scale_for(w, h, mode):
    return (min(1.0, math.sqrt((CANVAS[0] * CANVAS[1]) / (w * h))) if mode == "match"
            else min(1.0, 2048 / min(w, h)))


def boxes(path):
    img = np.array(Image.open(path).convert("RGB"))
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    found = {}
    for name, fn in CASCADES.items():
        cc = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, fn))
        hits = cc.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(24, 24))
        found[name] = sorted([int(b[2]) for b in hits], reverse=True)
    return w, h, found


print("canvas %dx%d (R4-R9); match = down-only to canvas area, max = 2048 short edge (never upscale)" % CANVAS)
for tag, path in PICKS.items():
    if not os.path.exists(path):
        print(tag, "MISSING", path)
        continue
    w, h, found = boxes(path)
    sm, sx = scale_for(w, h, "match"), scale_for(w, h, "max")
    pil = Image.open(path)
    print("-- %s %s %s size=%dx%d aspect=%.4f" % (tag, os.path.basename(path), pil.format, w, h, w / h))
    print("   node scale: match %.4f -> face x%.3f px, max %.4f -> face x%.3f px" % (sm, sm, sx, sx))
    for name, ws in found.items():
        if not ws:
            print("   %-12s 0 boxes" % name)
            continue
        print("   %-12s n=%d widths_native=%s" % (name, len(ws), ws[:8]))
        print("   %-12s at match: %s | at max: %s" % ("", [round(x * sm) for x in ws[:8]], [round(x * sx) for x in ws[:8]]))
        print("   %-12s largest face share of image area = %.4f (native)" % ("", (ws[0] ** 2) / (w * h)))
