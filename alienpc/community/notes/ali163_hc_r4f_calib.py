"""ALI-163 R4F - calibration grid + one-to-one face assignment for the HardcoreNSFW face metric.

Adds the controls a cosine gate needs, on the files that exist 2026-10-23 ~12:45 CT:
  A same-identity, clean  : pick-jpg face  <->  that woman's sheet anchor
  B different-identity    : pick-jpg face  <->  the other woman's sheet anchor
  C sheet <-> sheet       : w1 vs w2 (same pair) and across pairs
  D source <-> video      : pick-jpg face  <->  video face of that woman  (the gate's real operating range)
  E video <-> video       : same woman, consecutive sampled frames, and first vs last
  F pixel budget          : face box w/h in source px (video face vs sheet face vs pick face)
Faces are assigned to women one-to-one (best of the 2 permutations) so a single face cannot serve both women.
Anchors: L = largest detected face of the sheet, M = mean of the top 4 faces by area.
"""
import json, os, sys, time, itertools
sys.path.insert(0, r"C:\AI\community\notes")
import numpy as np
import cv2
from hc_r4f_facelib import Scrfd, ArcFace, cos, mean_emb

OUT = r"C:\AI\community\notes\face_r4f"
INP = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
SHEETS = {("HC1", "w1"): "HC1_w1_blonde_00001_.png", ("HC1", "w2"): "HC1_w2_darkhair_00001_.png",
          ("HC2", "w1"): "HC2_w1_blonde_00001_.png", ("HC2", "w2"): "HC2_w2_darkhair_00001_.png"}
PICKS = {"HC1": "HC1_Two_women_in_studio_editorial.jpg", "HC2": "HC2_Two_women_in_passionate_embrace.jpg"}
CLIPS = [
    ("r1_243f_sheeted", "HC1", ["r1s_%02d.png" % i for i in range(1, 8)], list(range(0, 280, 40))),
    ("r2_243f_sheeted", "HC2", ["r2s_%02d.png" % i for i in range(1, 8)], list(range(0, 280, 40))),
    ("c1_481f_maskonly", "HC1", ["c1w_%02d.png" % i for i in range(1, 8)], list(range(0, 560, 80))),
    ("c2_481f_maskonly", "HC2", ["c2w_%02d.png" % i for i in range(1, 8)], list(range(0, 560, 80))),
    ("r1_old157f_nosheet", "HC1", ["r1_f%02d.png" % i for i in range(1, 6)], [12, 121, 241, 361, 481]),
    ("r2_old157f_nosheet", "HC2", ["r2_f%02d.png" % i for i in range(1, 6)], [12, 121, 241, 361, 481]),
]
det, emb, t0 = Scrfd(thr=0.4, input_size=(640, 640)), ArcFace(), time.time()
log, G = [], {"A": {}, "B": {}, "C": {}, "D": {}, "E": {}, "F": {}}


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


def stat(xs):
    xs = [float(x) for x in xs]
    if not xs:
        return None
    return {"n": len(xs), "mean": round(float(np.mean(xs)), 4), "min": round(float(np.min(xs)), 4),
            "max": round(float(np.max(xs)), 4), "p25": round(float(np.percentile(xs, 25)), 4),
            "median": round(float(np.median(xs)), 4), "p75": round(float(np.percentile(xs, 75)), 4)}


# anchors
anchL, anchM, sheetfaces = {}, {}, {}
say("== sheets: faces found (SCRFD thr 0.4, 768x1344) ==")
for key, fn in SHEETS.items():
    img, fs = faces_of(os.path.join(INP, fn), thr=0.4, size=(768, 1344))
    big = [f for f in fs if f["area"] >= 1500]
    if not big:
        say("  %s %s NO FACE" % key)
        continue
    anchL[key] = big[0]["e"]
    anchM[key] = mean_emb([f["e"] for f in big[:4]])
    sheetfaces[key] = fs
    G["F"]["sheet_%s_%s" % key] = {"max_dim": int(max(big[0]["box"][2] - big[0]["box"][0], big[0]["box"][3] - big[0]["box"][1])),
                                   "areas": [int(f["area"]) for f in fs]}
    intra = [cos(big[i]["e"], big[j]["e"]) for i in range(len(big)) for j in range(i + 1, len(big))]
    say("  %s %s faces=%d areas=%s intra_sheet_cos=%s" %
        (key[0], key[1], len(fs), [int(f["area"]) for f in fs], [round(x, 3) for x in intra]))
    G["C"]["intra_sheet_%s_%s" % key] = stat(intra)
for pair in ("HC1", "HC2"):
    for w in ("w1", "w2"):
        o = "w2" if w == "w1" else "w1"
        G["C"]["anchorL_%s_%s_vs_%s" % (pair, w, o)] = stat([cos(anchL[(pair, w)], anchL[(pair, o)])])
for (p1, w1), (p2, w2) in itertools.combinations(sorted(SHEETS), 2):
    if (p1, w1) == (p2, w2):
        continue
    v = cos(anchL[(p1, w1)], anchL[(p2, w2)])
    G["C"].setdefault("anchorL_cross_%s%s_%s%s" % (p1, w1, p2, w2), stat([v]))
    say("  anchorL %s_%s vs %s_%s = %.3f" % (p1, w1, p2, w2, v))

# picks (clean source faces)
say("\n== picks: faces + A/B controls ==")
pickface = {}
for pair, fn in PICKS.items():
    img, fs = faces_of(os.path.join(INP, fn), thr=0.4, size=(896, 896))
    say("  %s faces=%d areas=%s" % (pair, len(fs), [int(f["area"]) for f in fs]))
    if len(fs) < 2:
        continue
    best, bs = None, -9
    for perm in itertools.permutations(range(len(fs)), 2):
        s = cos(fs[perm[0]]["e"], anchM[(pair, "w1")]) + cos(fs[perm[1]]["e"], anchM[(pair, "w2")])
        if s > bs:
            best, bs = perm, s
    for w, i in zip(("w1", "w2"), best):
        f = fs[i]
        pickface[(pair, w)] = f
        G["F"]["pick_%s_%s" % (pair, w)] = {"max_dim": int(max(f["box"][2] - f["box"][0], f["box"][3] - f["box"][1])),
                                            "area": int(f["area"])}
        G["A"]["%s_%s_pick_vs_sheetL" % (pair, w)] = stat([cos(f["e"], anchL[(pair, w)])])
        G["A"]["%s_%s_pick_vs_sheetM" % (pair, w)] = stat([cos(f["e"], anchM[(pair, w)])])
        o = "w2" if w == "w1" else "w1"
        G["B"]["%s_%s_pick_vs_othersheetL" % (pair, w)] = stat([cos(f["e"], anchL[(pair, o)])])
        say("  %s %s maxdim=%d  A(sheetL)=%.3f A(sheetM)=%.3f  B(other sheetL)=%.3f" %
            (pair, w, max(f["box"][2] - f["box"][0], f["box"][3] - f["box"][1]),
             cos(f["e"], anchL[(pair, w)]), cos(f["e"], anchM[(pair, w)]), cos(f["e"], anchL[(pair, o)])))

# clips with one-to-one assignment
say("\n== clips: one-to-one assignment, D (pick<->video) and E (video<->video) ==")
summary = []
for ckey, pair, files, fidx in CLIPS:
    ser = {"w1": [], "w2": []}
    n_both = n_single = n_none = 0
    for fn, n in zip(files, fidx):
        p = os.path.join(OUT, fn)
        if not os.path.exists(p):
            say("  MISSING %s" % fn)
            continue
        img, fs = faces_of(p)
        if len(fs) == 0:
            n_none += 1
            say("  %s f%-4d faces=0" % (ckey, n))
            continue
        if len(fs) == 1:
            n_single += 1
            w = "w1" if cos(fs[0]["e"], anchL[(pair, "w1")]) >= cos(fs[0]["e"], anchL[(pair, "w2")]) else "w2"
            assign = {w: fs[0]}
        else:
            n_both += 1
            best, bs = None, -9
            for perm in itertools.permutations(range(len(fs)), 2):
                s = cos(fs[perm[0]]["e"], anchL[(pair, "w1")]) + cos(fs[perm[1]]["e"], anchL[(pair, "w2")])
                if s > bs:
                    best, bs = perm, s
            assign = dict(zip(("w1", "w2"), [fs[best[0]], fs[best[1]]]))
        for w, f in assign.items():
            o = "w2" if w == "w1" else "w1"
            rec = {"frame": n, "sec": round(n / 24.0, 2), "cos_sheetL": round(cos(f["e"], anchL[(pair, w)]), 4),
                   "cos_sheetM": round(cos(f["e"], anchM[(pair, w)]), 4),
                   "cos_other_sheetL": round(cos(f["e"], anchL[(pair, o)]), 4),
                   "cos_pick": round(cos(f["e"], pickface[(pair, w)]["e"]), 4) if (pair, w) in pickface else None,
                   "area": int(f["area"]), "max_dim": int(max(f["box"][2] - f["box"][0], f["box"][3] - f["box"][1])),
                   "w": int(f["box"][2] - f["box"][0]), "h": int(f["box"][3] - f["box"][1]),
                   "det": round(f["score"], 3), "n_faces": len(fs), "ev": f["e"].tolist()}
            ser[w].append(rec)
            G["D"]["%s_%s_video_vs_pick" % (ckey, w)] = stat([r["cos_pick"] for r in ser[w] if r["cos_pick"] is not None])
            G["D"]["%s_%s_video_vs_sheetL" % (ckey, w)] = stat([r["cos_sheetL"] for r in ser[w]])
        say("  %s f%-4d faces=%d  " % (ckey, n, len(fs)) + "  ".join(
            "%s sheetL=%.3f pick=%s box=%dx%d" %
            (w, ser[w][-1]["cos_sheetL"], ("%.3f" % ser[w][-1]["cos_pick"]) if ser[w][-1]["cos_pick"] is not None else "-",
             ser[w][-1]["w"], ser[w][-1]["h"]) for w in ("w1", "w2") if ser[w] and ser[w][-1]["frame"] == n))
    for w in ("w1", "w2"):
        s = ser[w]
        consec = [cos(np.array(s[i]["ev"]), np.array(s[i + 1]["ev"])) for i in range(len(s) - 1)]
        G["E"]["%s_%s_consec" % (ckey, w)] = stat(consec)
        fl = cos(np.array(s[0]["ev"]), np.array(s[-1]["ev"])) if len(s) > 1 else None
        summary.append({"clip": ckey, "woman": w, "frames": len(files), "n_faces_pairs": n_both,
                        "n_single_face": n_single, "n_no_face": n_none, "n_scored": len(s),
                        "cos_sheetL": stat([x["cos_sheetL"] for x in s]),
                        "cos_sheetM": stat([x["cos_sheetM"] for x in s]),
                        "cos_other_sheetL": stat([x["cos_other_sheetL"] for x in s]),
                        "cos_pick": stat([x["cos_pick"] for x in s if x["cos_pick"] is not None]),
                        "consec_cos": stat(consec), "first_last_cos": round(float(fl), 4) if fl is not None else None,
                        "span_frames": (s[-1]["frame"] - s[0]["frame"]) if len(s) > 1 else 0,
                        "max_dim": stat([x["max_dim"] for x in s]), "box_w": stat([x["w"] for x in s]),
                        "box_h": stat([x["h"] for x in s]), "det": stat([x["det"] for x in s]),
                        "series": s})
        say("  SUMMARY %-20s %-3s pairs=%d single=%d none=%d  sheetL med=%s  pick med=%s  consec med=%s  first_last=%s  maxdim med=%s" %
            (ckey, w, n_both, n_single, n_none,
             (G["D"]["%s_%s_video_vs_sheetL" % (ckey, w)] or {}).get("median"),
             (G["D"]["%s_%s_video_vs_pick" % (ckey, w)] or {}).get("median"),
             (G["E"]["%s_%s_consec" % (ckey, w)] or {}).get("median"),
             summary[-1]["first_last_cos"], (summary[-1]["max_dim"] or {}).get("median")))

json.dump({"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "seconds": round(time.time() - t0, 1),
           "grid": G, "summary": summary, "log": log},
          open(os.path.join(OUT, "r4f_calib.json"), "w", encoding="utf-8"), indent=1, default=float)
open(os.path.join(OUT, "r4f_calib.txt"), "w", encoding="utf-8").write("\n".join(log) + "\n")
say("\nelapsed %.1fs  wrote r4f_calib.json + r4f_calib.txt" % (time.time() - t0))
