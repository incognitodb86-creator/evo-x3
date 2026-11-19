#!/usr/bin/env python
# bj_pov_face_curve.py - objective face-presence and face-identity curve over the POV oral clip (2026-10-30).
#
# Why this exists: the precheck tier flagged `jump` (dino prev_min 0.633, 0 cuts) and the DINO similarity
# to the start image is 0.22 at the first decoded frame, which is consistent with the woman already being in
# frame at frame 0. The named risk in the plan (plans/2026-10-30-bj-pov-plan.md) is exactly this, plus
# identity drift at the deep stroke. DINO cannot answer pose or identity, so this script uses the box's own
# CPU face instruments (hc_r4f_facelib.py: SCRFD detection + ArcFace embedding) - no vision model, no GPU.
#
# Reports, per sampled frame: is a face present, its box, and the ArcFace cosine against the reference crop
# Derek supplied. Summary: first/last frame with a face, frames with a face out of frames sampled, mean/min
# cosine, and the worst frame's index and time. Flags only - no score, no KEEP.
import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, r"C:\AI\community\notes")
from hc_r4f_facelib import ArcFace, Scrfd, cos  # noqa: E402

CLIP = r"C:/AI/community/review/bj-pov-2026-10-30/judge_runs/bjpov_b1_s51083020/bjpov_b1_s51083020.mp4"
REF = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/bj_pov_20261030/face_a.png"
STEP = 4          # every 4th frame = 25 fps-sampled -> 31 probes over 5.167 s
OUT = r"C:/AI/community/review/bj-pov-2026-10-30/judge_out/face_curve.json"
FPS = 24.0


def main():
    global CLIP, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", default=CLIP)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    CLIP, OUT = a.clip, a.out
    import cv2
    cap = cv2.VideoCapture(CLIP)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    det, rec = Scrfd(), ArcFace()
    ref_dets = det.detect(np.array(Image.open(REF).convert("RGB"))[:, :, ::-1])
    if not ref_dets:
        raise SystemExit("no face in the reference crop - instrument broken, no curve")
    ref_arr = np.array(Image.open(REF).convert("RGB"))[:, :, ::-1]
    ref_emb = rec.embed(ref_arr, max(ref_dets, key=lambda x: x["area"]))
    rows = []
    for idx in range(0, n, STEP):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, f = cap.read()
        if not ok:
            break
        dets = det.detect(f)
        if not dets:
            rows.append({"frame": idx, "t_sec": round(idx / FPS, 3), "face": False})
            continue
        d = max(dets, key=lambda x: x["area"])
        c = cos(ref_emb, rec.embed(f, d))
        rows.append({"frame": idx, "t_sec": round(idx / FPS, 3), "face": True,
                     "box": [round(v, 1) for v in d["box"]], "det_score": round(d["score"], 3),
                     "face_w_px": round(d["box"][2] - d["box"][0], 1), "arcface_cos": round(float(c), 4)})
    cap.release()

    withf = [r for r in rows if r["face"]]
    summary = {
        "clip": CLIP, "total_frames": n, "sampled": len(rows), "step": STEP,
        "ref_embedding_from": REF,
        "frames_with_face": len(withf),
        "first_face_frame": withf[0]["frame"] if withf else None,
        "last_face_frame": withf[-1]["frame"] if withf else None,
        "arcface_cos_mean": round(float(np.mean([r["arcface_cos"] for r in withf])), 4) if withf else None,
        "arcface_cos_min": round(float(np.min([r["arcface_cos"] for r in withf])), 4) if withf else None,
        "worst_face_frame": min(withf, key=lambda r: r["arcface_cos"])["frame"] if withf else None,
        "face_width_px_min": round(float(np.min([r["face_w_px"] for r in withf])), 1) if withf else None,
        "face_width_px_max": round(float(np.max([r["face_w_px"] for r in withf])), 1) if withf else None,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        import json
        json.dump({"summary": summary, "rows": rows}, fh, indent=1)
    print(json.dumps(summary, indent=1))
    print("per-probe (frame, t, face, det, arcface_cos, face_w_px):")
    for r in rows:
        if r["face"]:
            print("  f%03d %.3fs yes det=%.2f cos=%.3f w=%.0fpx" % (r["frame"], r["t_sec"],
                  r["det_score"], r["arcface_cos"], r["face_w_px"]))
        else:
            print("  f%03d %.3fs NO FACE" % (r["frame"], r["t_sec"]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
