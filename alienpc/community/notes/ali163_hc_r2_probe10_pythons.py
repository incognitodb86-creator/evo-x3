"""R2 probe 10 (read-only): which interpreter on this box can run a CPU face metric?
Lists candidate interpreters (depth-limited walk) and probes imports per interpreter.
Nothing is downloaded, no GPU, no network.
"""
import os
import subprocess
import sys

BASES = [r"C:\AI", r"C:\Users\derek\HardcoreNSFW-TestRuntime", r"C:\Users\derek\AppData\Local\Programs\Python"]
CAND = set()
for base in BASES:
    if not os.path.isdir(base):
        continue
    for dirpath, dirnames, filenames in os.walk(base):
        if dirpath.count(os.sep) - base.count(os.sep) > 3:
            dirnames[:] = []
            continue
        if os.path.basename(dirpath).lower() in ("scripts", "bin"):
            for f in filenames:
                if f.lower() == "python.exe":
                    CAND.add(os.path.join(dirpath, f))
CAND.add(sys.executable)
CAND = sorted(CAND)
print("candidate interpreters:", len(CAND))

CODE = (
    "import importlib,json\n"
    "out=[]\n"
    "for m in ['onnxruntime','mediapipe','cv2','numpy','torch','ultralytics','scipy']:\n"
    "    try:\n"
    "        mm=importlib.import_module(m)\n"
    "        out.append([m,str(getattr(mm,'__version__',None))])\n"
    "    except Exception:\n"
    "        out.append([m,'MISSING'])\n"
    "try:\n"
    "    import cv2\n"
    "    out.append(['cv2_has_CascadeClassifier',str(hasattr(cv2,'CascadeClassifier'))])\n"
    "except Exception:\n"
    "    pass\n"
    "print(json.dumps(out))\n"
)
for c in CAND:
    try:
        r = subprocess.run([c, "-c", CODE], capture_output=True, text=True, timeout=120)
        print("== %s\n   %s" % (c, (r.stdout or r.stderr).strip().replace("\n", "  ")))
    except Exception as e:
        print("== %s  probe error %s" % (c, e))
