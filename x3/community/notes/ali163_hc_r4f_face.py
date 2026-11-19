"""ALI-163 R4F FACE RESEARCH - machine identity metric for the HardcoreNSFW-TestRuntime chain.

CPU only (onnxruntime CPUExecutionProvider). No GPU, no ComfyUI/llama-swap call, no render, no download,
no installs. Reads clips/stills/sheets that exist on disk 2026-10-23 ~12:40 CT and writes only under
C:/AI/community/notes/face_r4f/.

What it measures, per clip, per woman:
  anchor embedding = mean of the top face embeddings of that woman's per-woman reference sheet
                     (HC1_w1_blonde_00001_.png / HC1_w2_darkhair_00001_.png / HC2_w1_* / HC2_w2_*)
  per sampled frame: SCRFD faces -> ArcFace embeddings -> cosine to w1/w2 anchors, assigned by max cosine
  drift  : cosine(frame_i face, frame_i+1 face) for the same woman; slope per 100 frames
  size   : face box area + width/height in source pixels (the "face crop ~200 px" claim)
  swap   : frames where the OTHER woman's anchor outscores the assigned one
  link   : pick-jpg faces vs sheet anchors (identity chain pick -> sheet -> video)
"""
import json, os, sys, time
sys.path.insert(0, r"C:\AI\community\notes")
import numpy as np
import cv2
from hc_r4f_facelib import Scrfd, ArcFace, cos, mean_emb

OUT = r"C:\AI\community\notes\face_r4f"
INP = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
RUNS = r"C:\AI\community\runs"

SHEETS = {("HC1", "w1"): "HC1_w1_blonde_00001_.png", ("HC1", "w2"): "HC1_w2_darkhair_00001_.png",
          ("HC2", "w1"): "HC2_w1_blonde_00001_.png", ("HC2", "w2"): "HC2_w2_darkhair_00001_.png"}
PICKS = {"HC1": "HC1_Two_women_in_studio_editorial.jpg", "HC2": "HC2_Two_women_in_passionate_embrace.jpg"}

# (clip key, pair, frame files, frame indices, total frames of the clip as measured by ffprobe -count_packets)
CLIPS = [
    ("r1_243f_sheeted", "HC1", ["r1s_%02d.png" % i for i in range(1, 8)], list(range(0, 280, 40)), 243),
    ("r2_243f_sheeted", "HC2", ["r2s_%02d.png" % i for i in range(1, 8)], list(range(0, 280, 40)), 243),
    ("c1_481f_maskonly", "HC1", ["c1w_%02d.png" % i for i in range(1, 8)], list(range(0, 560, 80)), 481),
    ("c2_481f_maskonly", "HC2", ["c2w_%02d.png" % i for i in range(1, 8)], list(range(0, 560, 80)), 481),
    ("r1_old157f_nosheet", "HC1", ["r1_f%02d.png" % i for i in range(1, 6)], [12, 121, 241, 361, 481], 3783),
    ("r2_old157f_nosheet", "HC2", ["r2_f%02d.png" % i for i in range(1, 6)], [12, 121, 241, 361, 481], 3762),
]

det = Scrfd(thr=0.4, input_size=(640, 640))
emb = ArcFace()
t0 = time.time()
log = []


def say(s):
    print(s)
    log.append(s)


def faces_of(path, thr=0.4, size=(640, 640)):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit("cannot read " + path)
    fs = det.detect(img, thr=thr, input_size=size)
    for f in fs:
        f["e"] = emb.embed(img, f)
    return img, fs


# ---- 1. sheet anchors ----
say("== sheet anchors (SCRFD-10G thr 0.4 at 768x1344, ArcFace glintr100, mean of top 4 by area) ==")
anchor, sheetinfo = {}, {}
for key, fn in SHEETS.items():
    p = os.path.join(INP, fn)
    img, fs = faces_of(p, thr=0.4, size=(768, 1344))
    big = [f for f in fs if f["area"] >= 1500]
    top = big[:4]
    say("  %s %s  img=%dx%d  faces=%d (area>=1500: %d)  areas=%s  det=%s" %
        (key[0], key[1], img.shape[1], img.shape[0], len(fs), len(big),
         [int(f["area"]) for f in fs[:8]], [round(f["score"], 2) for f in fs[:8]]))
    if top:
        anchor[key] = mean_emb([f["e"] for f in top])
        sheetinfo["%s_%s" % key] = {"n_faces": len(fs), "n_used": len(top),
                                    "areas": [int(f["area"]) for f in fs],
                                    "mean_area_used": int(np.mean([f["area"] for f in top])),
                                    "intra_sheet_cos": [round(cos(top[i]["e"], top[j]["e"]), 3)
                                                         for i in range(len(top)) for j in range(i + 1, len(top))]}
    else:
        sheetinfo["%s_%s" % key] = {"n_faces": len(fs), "n_used": 0}

# cross-sheet separability (w1 vs w2 anchors of the same pair): expect LOW
for pair in ("HC1", "HC2"):
    a, b = anchor.get((pair, "w1")), anchor.get((pair, "w2"))
    say("  anchor cos %s w1 vs w2 = %s" % (pair, "%.3f" % cos(a, b) if a is not None and b is not None else "n/a"))

# ---- 2. identity chain: pick jpg faces vs sheet anchors ----
say("\n== pick jpg faces vs sheet anchors (identity chain pick -> sheet) ==")
pick_anchor = {}
for pair, fn in PICKS.items():
    p = os.path.join(INP, fn)
    img, fs = faces_of(p, thr=0.4, size=(896, 896))
    say("  %s img=%dx%d faces=%d areas=%s" % (pair, img.shape[1], img.shape[0], len(fs), [int(f["area"]) for f in fs[:6]]))
    for i, f in enumerate(fs[:4]):
        row = []
        for w in ("w1", "w2"):
            a = anchor.get((pair, w))
            row.append("%s=%.3f" % (w, cos(f["e"], a)) if a is not None else "%s=n/a" % w)
        best = max(("w1", "w2"), key=lambda w: cos(f["e"], anchor[(pair, w)]) if anchor.get((pair, w)) is not None else -9)
        b = max([f["box"][2] - f["box"][0], f["box"][3] - f["box"][1]])
        say("    face%d box=%s maxdim=%d area=%d det=%.2f  %s  -> %s" %
            (i, [int(v) for v in f["box"]], int(b), int(f["area"]), f["score"], " ".join(row), best))
        pick_anchor[(pair, best)] = f["e"]

# ---- 3. per-clip per-frame identity metric ----
say("\n== per-clip frames (SCRFD thr 0.4 at 640x640) ==")
per_frame, agg = [], []
for ckey, pair, files, fidx, total in CLIPS:
    series = {w: [] for w in ("w1", "w2")}
    for fn, n in zip(files, fidx):
        p = os.path.join(OUT, fn)
        if not os.path.exists(p):
            say("  MISSING FRAME %s" % fn)
            continue
        img, fs = faces_of(p)
        row = {"clip": ckey, "frame": n, "sec": round(n / 24.0, 2), "n_faces": len(fs)}
        for w in ("w1", "w2"):
            a = anchor.get((pair, w))
            if a is None:
                continue
            cands = [f for f in fs]
            if not cands:
                continue
            best = max(cands, key=lambda f: cos(f["e"], a))
            c = cos(best["e"], a)
            other = cos(best["e"], anchor[(pair, "w2" if w == "w1" else "w1")])
            wpx, hpx = best["box"][2] - best["box"][0], best["box"][3] - best["box"][1]
            series[w].append({"frame": n, "sec": round(n / 24.0, 2), "cos": round(c, 4),
                              "cos_other": round(other, 4), "area": int(best["area"]),
                              "w": int(wpx), "h": int(hpx), "det": round(best["score"], 3),
                              "n_faces": len(fs), "ev": best["e"].tolist()})
            row[w] = {"cos": round(c, 4), "cos_other": round(other, 4), "area": int(best["area"]),
                      "w": int(wpx), "h": int(hpx)}
            per_frame.append(dict(clip=ckey, frame=n, woman=w, cos=c, cos_other=other,
                                  area=best["area"], w=wpx, h=hpx, det=best["score"], n_faces=len(fs)))
        per_frame.append(dict(clip=ckey, frame=n, woman="_frame", n_faces=len(fs)))
        say("  %s f%-4d faces=%d  " % (ckey, n, len(fs)) +
            "  ".join("%s cos=%.3f other=%.3f area=%d box=%dx%d" %
                      (w, series[w][-1]["cos"], series[w][-1]["cos_other"], series[w][-1]["area"],
                       series[w][-1]["w"], series[w][-1]["h"]) for w in ("w1", "w2") if series[w] and series[w][-1]["frame"] == n))
    # aggregates
    for w in ("w1", "w2"):
        s = series[w]
        if not s:
            agg.append({"clip": ckey, "woman": w, "n_frames": len(files), "n_with_face": 0})
            continue
        cs = [x["cos"] for x in s]
        co = [x["cos_other"] for x in s]
        consec = [round(cos(np.array(s[i]["ev"]), np.array(s[i + 1]["ev"])), 4) for i in range(len(s) - 1)]
        first_last = round(cos(np.array(s[0]["ev"]), np.array(s[-1]["ev"])), 4) if len(s) > 1 else None
        span = s[-1]["frame"] - s[0]["frame"] if len(s) > 1 else 0
        agg.append({"clip": ckey, "woman": w, "n_frames": len(files), "n_with_face": len(s),
                    "cos_mean": round(float(np.mean(cs)), 4), "cos_min": round(float(np.min(cs)), 4),
                    "cos_max": round(float(np.max(cs)), 4),
                    "cos_other_mean": round(float(np.mean(co)), 4),
                    "swaps": int(sum(1 for a, b in zip(cs, co) if b > a)),
                    "consec_cos": consec, "consec_mean": round(float(np.mean(consec)), 4) if consec else None,
                    "first_last_cos": first_last, "span_frames": span,
                    "area_mean": int(np.mean([x["area"] for x in s])), "area_min": int(np.min([x["area"] for x in s])),
                    "box_w_mean": int(np.mean([x["w"] for x in s])), "box_h_mean": int(np.mean([x["h"] for x in s])),
                    "det_mean": round(float(np.mean([x["det"] for x in s])), 3),
                    "series": s})
        # consecutive-frame self-similarity (drift) using stored embeddings? recompute from files below

say("\n== summary ==")
for a in agg:
    say("  %-22s %-3s frames=%d face=%d cos_mean=%s cos_min=%s cos_other=%s swaps=%d consec=%s first_last=%s area_mean=%s box=%sx%s det=%s" %
        (a["clip"], a["woman"], a["n_frames"], a["n_with_face"], a.get("cos_mean"), a.get("cos_min"),
         a.get("cos_other_mean"), a.get("swaps"), a.get("consec_mean"), a.get("first_last_cos"),
         a.get("area_mean"), a.get("box_w_mean"), a.get("box_h_mean"), a.get("det_mean")))

json.dump({"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "seconds": round(time.time() - t0, 1),
           "sheets": sheetinfo, "per_frame": per_frame, "summary": agg, "log": log},
          open(os.path.join(OUT, "r4f_metrics.json"), "w", encoding="utf-8"), indent=1, default=float)
open(os.path.join(OUT, "r4f_table.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
say("\nelapsed %.1fs  wrote r4f_metrics.json + r4f_table.txt" % (time.time() - t0))
