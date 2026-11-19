"""R2 probe 5 (read-only): reference-pixel math using the exact node code path
(comfy_extras/nodes_minimax_h3.py:301-307, REF_IMAGE_SHORT_EDGE=2048 at :33).
match: scale = min(1.0, sqrt(width*height/(w*h))); max: scale = min(1.0, 2048/min(w,h)).
Both are DOWN-only (min with 1.0), aspect kept, rounded to 32.
"""
import math

CANVAS_MULTIPLE = 32


def scaled(w, h, cw, ch, mode):
    scale = min(1.0, math.sqrt((cw * ch) / (w * h))) if mode == "match" else min(1.0, 2048 / min(w, h))
    tw = max(CANVAS_MULTIPLE, round(w * scale / CANVAS_MULTIPLE) * CANVAS_MULTIPLE)
    th = max(CANVAS_MULTIPLE, round(h * scale / CANVAS_MULTIPLE) * CANVAS_MULTIPLE)
    return scale, tw, th, tw * th


CASES = [
    ("HC1/HC2 ref 1376x768 pair still @ 1344x768", 1376, 768, 1344, 768),
    ("POOL portrait 768x1344 @ 768x1344 (PV2/RS)", 768, 1344, 768, 1344),
    ("POOL portrait 768x1344 @ 1344x768 landscape", 768, 1344, 1344, 768),
    ("RS016 sheet 1152x2016 @ 768x1344 (RS arms)", 1152, 2016, 768, 1344),
    ("RS016 sheet 1152x2016 @ 1344x768 (R4-R9)", 1152, 2016, 1344, 768),
]
for label, w, h, cw, ch in CASES:
    m = scaled(w, h, cw, ch, "match")
    x = scaled(w, h, cw, ch, "max")
    print("%s" % label)
    print("   match scale %.4f -> %dx%d = %d px (%.2f Mpx)" % (m[0], m[1], m[2], m[3], m[3] / 1e6))
    print("   max   scale %.4f -> %dx%d = %d px (%.2f Mpx)  max/match = %.2fx pixels"
          % (x[0], x[1], x[2], x[3], x[3] / 1e6, x[3] / m[3]))
