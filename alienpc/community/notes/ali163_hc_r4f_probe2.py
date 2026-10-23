# ALI-163 R4F probe 2: SCRFD-10G + glintr100 on CPU, decode per comfyui-reactor-node/reactor_core/inswap.py.
# Validation = face boxes on the pick stills (expect 2), face boxes on the reference sheet (expect many panels),
# face boxes on a video frame (expect 2), then same-face self-similarity vs cross-face similarity.
import sys, os, time
sys.path.insert(0, r"C:\AI\community\notes")
import numpy as np, cv2
from hc_r4f_facelib import Scrfd, ArcFace, cos

HCIN = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
FDIR = r"C:\AI\community\notes\face_r4f"
det, emb = Scrfd(thr=0.5, input_size=(640, 640)), ArcFace()

def run(path, thr=0.5, size=(640, 640)):
    img = cv2.imread(path)
    t = time.time()
    fs = det.detect(img, thr=thr, input_size=size)
    for f in fs:
        f["e"] = emb.embed(img, f)
    return img, fs, time.time() - t

for p in [HCIN + r"\hardcore1_start.png", HCIN + r"\HC1_sheet2_woman1.png", FDIR + r"\r1_f01.png"]:
    img, fs, dt = run(p)
    print("\n%s  %dx%d  n=%d  %.1fs" % (os.path.basename(p), img.shape[1], img.shape[0], len(fs), dt))
    for i, f in enumerate(fs[:8]):
        b = f["box"]
        print("  f%d area=%8.0f box=(%.0f,%.0f,%.0f,%.0f) wh=(%.0f,%.0f) score=%.2f" %
              (i, f["area"], b[0], b[1], b[2], b[3], b[2] - b[0], b[3] - b[1], f["score"]))

img, fs, dt = run(FDIR + r"\r1_f01.png")
print("\nsimilarity matrix on r1_f01 (%d faces):" % len(fs))
for i in range(len(fs)):
    print("  " + " ".join("%.3f" % cos(fs[i]["e"], fs[j]["e"]) for j in range(len(fs))))

imgA, fA, _ = run(FDIR + r"\r1_f01.png")
imgB, fB, _ = run(FDIR + r"\r1_f05.png")
print("\ncross-frame best-match cos (r1_f01 vs r1_f05):")
for i in range(len(fA)):
    print("  faceA%d -> " % i + " ".join("%.3f" % cos(fA[i]["e"], fB[j]["e"]) for j in range(len(fB))))
imgS, fS, _ = run(HCIN + r"\HC1_sheet2_woman1.png", thr=0.4, size=(768, 1280))
print("\nsheet woman1 faces=%d; video faces x sheet mean cos:" % len(fS))
if fS:
    anch = np.mean([f["e"] for f in fS], axis=0); anch = anch / np.linalg.norm(anch)
    for i in range(len(fA)):
        print("  faceA%d -> %.3f" % (i, cos(fA[i]["e"], anch)))
