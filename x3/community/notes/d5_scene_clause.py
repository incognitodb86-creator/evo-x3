"""D5 (Derek 8:46 PM CT "You can delete scene guards or whatever ... auto approve"): delete the scene-line clause
'; no minor, no minor-coded figure, no one prepubertal' from the sslcaio prompts that fail the adults guard.
Backups <file>.bak-d5-2047; unified diff to _d5.diff; guard re-run over all 12 jobs."""
import json, os, re, sys, shutil, glob, difflib
sys.path.insert(0, r"C:\AI\community\scripts")
import comm, run_queue
RUN = r"C:\AI\community\runs\sslcaio_20261030"
CL = re.compile(r";\s*no minor, no minor-coded figure, no one prepubertal(?=[,.;])")
def jobs():
    out = []
    for f in ("_order_ss.json", "_order_lc.json", "_order_aio.json"):
        out += [j["tag"] for j in json.load(open(os.path.join(RUN, f), encoding="utf-8-sig"))["order"]]
    return out
def fix(o, n):
    if isinstance(o, dict): return {k: fix(v, n) for k, v in o.items()}
    if isinstance(o, list): return [fix(v, n) for v in o]
    if isinstance(o, str):
        new, c = CL.subn("", o); n[0] += c; return new
    return o
files = [os.path.join(RUN, t.replace("/", os.sep), "request.api.json") for t in jobs()]
files += [p for p in glob.glob(os.path.join(RUN, "_inputs", "prompts", "*.txt"))]
diff, total, changed = [], 0, []
for p in files:
    raw = open(p, encoding="utf-8", newline="").read(); n = [0]
    new = fix(raw, n)  # raw-text edit keeps the file's own formatting
    if p.endswith(".json"): json.loads(new.lstrip("\ufeff"))  # must still parse
    if not n[0]: continue
    if not os.path.exists(p + ".bak-d5-2047"): shutil.copy2(p, p + ".bak-d5-2047")
    open(p, "w", encoding="utf-8", newline="").write(new)
    total += n[0]; changed.append((os.path.relpath(p, RUN), n[0]))
    a = raw.replace("\\n", "\n").splitlines(); b = new.replace("\\n", "\n").splitlines()
    diff += difflib.unified_diff(a, b, os.path.relpath(p, RUN) + ".bak-d5-2047", os.path.relpath(p, RUN), n=0, lineterm="")
open(os.path.join(RUN, "_d5.diff"), "w", encoding="utf-8").write("\n".join(diff) + "\n")
print("files changed:", len(changed), "clauses removed:", total)
for r, c in changed: print("  ", r, c)
ok = 0; tj = jobs()
for t in tj:
    r = run_queue.guard_graph(json.load(open(os.path.join(RUN, t.replace("/", os.sep), "request.api.json"), encoding="utf-8-sig")))
    ok += r
    if not r: print("guard FAIL", t)
print("GUARD %d/%d" % (ok, len(tj)))
sys.exit(0 if ok == len(tj) else 4)
