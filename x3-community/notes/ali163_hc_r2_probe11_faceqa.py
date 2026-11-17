"""R2 probe 11 (read-only): the existing face-QA precedent on this box.
Lists C:\\AI\\models\\qa_gate, finds mediapipe model files (*.task/*.tflite), and looks for a
script that already runs a face metric (name match only, no model loaded, no GPU).
"""
import os
import re

D = r"C:\AI\models\qa_gate"
print("== %s" % D)
for f in sorted(os.listdir(D)):
    fp = os.path.join(D, f)
    print("  %12d  %s" % (os.path.getsize(fp) if os.path.isfile(fp) else -1, f))

NEED = re.compile(r"\.(task|tflite|onnx|pt)$", re.I)
print("== mediapipe model files in C:\\AI (name match)")
for dirpath, dirnames, filenames in os.walk(r"C:\AI"):
    if dirpath.count(os.sep) - 4 > 5:
        dirnames[:] = []
        continue
    for f in filenames:
        if NEED.search(f) and re.search(r"(face|blaze|detect|embed|scrfd|w600k|det_10g|yolo)", f, re.I):
            fp = os.path.join(dirpath, f)
            try:
                sz = os.path.getsize(fp)
            except OSError:
                sz = -1
            if sz > 100_000:
                print("  %12d  %s" % (sz, fp))

print("== scripts that mention a face model (C:\\AI\\community\\scripts, C:\\AI\\community\\notes, 5slock ralph-community)")
PAT = re.compile(r"(face_yolov8m|FaceEmbedDistance|face_metric|mediapipe|inswapper|GPEN|facebox|face_box|qa_gate)", re.I)
ROOTS = [r"C:\AI\community\scripts", r"C:\AI\community\notes", r"C:\Users\derek\5slock"]
seen = 0
for root in ROOTS:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for f in filenames:
            if not f.lower().endswith((".py", ".ps1", ".md", ".json", ".txt")):
                continue
            fp = os.path.join(dirpath, f)
            try:
                txt = open(fp, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            hits = sorted(set(m.group(0).lower() for m in PAT.finditer(txt)))
            if hits:
                print("  %s  -> %s" % (fp, ",".join(hits)))
                seen += 1
                if seen > 40:
                    raise SystemExit
