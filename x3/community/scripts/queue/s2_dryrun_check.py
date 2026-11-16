"""One S2 still request through run_queue --dry-run + guard, using make_render.s2_build with a fixed seed.
No counter bump, no ComfyUI, no copy (image path is a placeholder). Builds under %TEMP%."""
import os, sys, tempfile, argparse, subprocess
sys.path.insert(0, r"C:\AI\community\scripts")
import make_render as mr, run_queue as rq, json
sid, src = mr.approved_stills()[3]
base = os.path.join(tempfile.gettempdir(), "s2_dry"); runs = []
for p in ("kv", "bfs"):
    d = os.path.join(base, "s2check_" + p); os.makedirs(d, exist_ok=True); runs.append(("s2check_" + p, d))
a = argparse.Namespace(count=1, words=None)
t1, t2, size2, checks = mr.s2_build(a, 1, runs, sid, src, "community/render/%s.jpg" % sid, (752, 1360))
for tag, ch in checks: print("changed", tag, ch)
for (r, d), t in zip(runs, (t1, t2)):
    g = json.load(open(os.path.join(d, t[0], "request.api.json"), encoding="utf-8"))
    print(t[0], "guard_ok", rq.guard_graph(g))
    out = subprocess.run([mr.PY, os.path.join(mr.SCRIPTS, "run_queue.py"), "--run-dir", d, "--dry-run"], capture_output=True, text=True, cwd=mr.ROOT)
    print(out.stdout.strip(), "rc=%d" % out.returncode)
