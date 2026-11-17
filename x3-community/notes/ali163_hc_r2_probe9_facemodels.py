"""R2 probe 9 (read-only): is there any face-detection model file on this box?
cv2 5.0.0 dropped CascadeClassifier (no Haar XMLs at runtime); FaceDetectorYN /
FaceRecognizerSF exist but need an ONNX model file, and downloads are forbidden.
Bounded walk, name filter only, no image opened.
"""
import os
import re

ROOTS = [
    r"C:\Users\derek\HardcoreNSFW-TestRuntime",
    r"C:\AI",
]
SKIP = re.compile(r"([\\/]\.git([\\/]|$))|node_modules|__pycache__|\.venv")
PAT = re.compile(r"(onnx|face|insight|scrfd|yunface|arcface|embedd|det_10g|retina|mediapipe)", re.I)
hits = []
for root in ROOTS:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not SKIP.search(os.path.join(dirpath, d) + os.sep)]
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if PAT.search(f):
                try:
                    sz = os.path.getsize(fp)
                except OSError:
                    sz = -1
                if sz > 200_000:
                    hits.append((sz, fp))
hits.sort(reverse=True)
print("candidate model files (>200 KB, name match):", len(hits))
for sz, fp in hits[:40]:
    print("  %10d  %s" % (sz, fp))
