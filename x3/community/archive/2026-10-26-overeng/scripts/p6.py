# P6 (ALI-128): D1 x D2 side-by-side (same shots + seeds), then ~1-minute community video vs the current Switchyard path.
import sys, os, subprocess, time
sys.path.insert(0, r"C:\AI\community\scripts"); from comm import *
PY = sys.executable; S = os.path.join(W, "scripts"); SH = os.path.join(W, "shots")
LF = os.path.join(W, "p6.log")
def step(args, name):
    t0 = time.time(); log(f"P6 STEP {name} start", LF)
    r = subprocess.run([PY, "-u"] + args, cwd=S); log(f"P6 STEP {name} rc={r.returncode} secs={time.time()-t0:.0f}", LF)
step([os.path.join(S, "batch_queue.py"), os.path.join(SH, "p6_pairs.json"), "p6_pairs", "--no-stitch"], "pairs")
step([os.path.join(S, "batch_queue.py"), os.path.join(SH, "p6_1min_community.json"), "p6_1min_community"], "1min_community")
step([os.path.join(S, "sy_1min.py")], "1min_switchyard")
try: http(LS + "/unload", timeout=120); log("P6 GPU idle (llama-swap unload)", LF)
except Exception as e: log(f"unload warn {e}", LF)
log("P6 DONE", LF)
