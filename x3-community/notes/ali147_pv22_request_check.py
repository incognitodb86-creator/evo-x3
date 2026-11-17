# -*- coding: utf-8 -*-
# ALI-147 PV2-2 - read-only check of p7/JOB_REQUEST.json AFTER writing it.
# Gates, in order:
#  1. exact bytes = the accepted model request shape (p7/jobs/request_iter07.json, indent=2 + trailing
#     newline) with the id replaced once; printed in full so the archive file can be compared later.
#  2. exactly one job, exact keys and order, kind graph, frames == the graph's own frame total, tol 0.
#  3. the id passes the p7 id patterns PARSED OUT OF THE LIVE ralph.ps1 (a hardcoded copy proves nothing).
#  4. id-free gates (no result.json / .out / .err.out, no arm render outputs) and the live p7 budget.
#  5. the graph file the job names exists, parses, passes comm.guard_ok, and differs from the base seg3
#     graph in exactly c0.prompt / c1.prompt / save.filename_prefix.
import json, os, re, hashlib, sys

C = "C:/AI/community"
ID = "ali147_pool_promptv2_seg3_s51080002"
SRC = C + "/runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.api.json"
ARM = C + "/runs/ali147_pool_promptv2_seg3_s51080002"
RQ = C + "/p7/JOB_REQUEST.json"
MODEL = C + "/p7/jobs/request_iter07.json"
MODEL_ID = "ali147_pool_promptv2_s51080000"
RALPH = "C:/Users/derek/5slock/ralph-community/ralph.ps1"
BUDGET = "C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
RPT = C + "/notes/ali147-pv22-request-check-20261022.txt"
sys.path.insert(0, C + "/scripts")
from comm import guard_ok

O = []
def p(s):
    O.append(str(s))
def sha(b):
    return hashlib.sha256(b).hexdigest()
FAIL = []
def chk(ok, msg):
    p(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAIL.append(msg)

raw = open(RQ, "rb").read()
p("p7/JOB_REQUEST.json bytes %d sha256 %s" % (len(raw), sha(raw)))
p("exact bytes: %r" % raw.decode("utf-8"))
model = open(MODEL, "rb").read()
exp = model.decode("utf-8").replace(MODEL_ID, ID).encode("utf-8")
chk(raw == exp, "bytes are byte-for-byte the accepted model request shape (%s, indent=2 + trailing newline) with the id replaced once" % MODEL)
chk(raw.endswith(b"\n") and raw.count(b"\r") == 0, "LF only, trailing newline present (same as every archived request_iter*.json)")
chk(raw.count(ID.encode()) == 1 and MODEL_ID.encode() not in raw, "the new id appears exactly once and the model id is gone")

req = json.loads(raw.decode("utf-8"))
chk(sorted(req.keys()) == ["jobs"], "top-level keys exactly ['jobs']")
jobs = req["jobs"]
chk(isinstance(jobs, list) and len(jobs) == 1, "exactly ONE job")
j = jobs[0]
chk(list(j.keys()) == ["id", "kind", "frames", "frames_tol", "minutes"], "job keys and order exactly id, kind, frames, frames_tol, minutes (as the model)")
chk(j["id"] == ID, "id = " + ID)
chk(j["kind"] == "graph", "kind = graph")
chk(j["frames"] == 481 and j["frames_tol"] == 0 and j["minutes"] == 60, "frames 481 / frames_tol 0 / minutes 60 (60 = PRE-JOB gate, ralph.ps1 clamps 30..180)")

g = json.loads(open(ARM + "/request.api.json", "rb").read().decode("utf-8"))
tot = g["c0"]["inputs"]["length"] + g["win1"]["inputs"]["extension_frames"]
fps = g["mkvid"]["inputs"]["fps"]
chk(tot == j["frames"], "frames matches the graph itself: c0.length %d + win1.extension_frames %d = %d" % (g["c0"]["inputs"]["length"], g["win1"]["inputs"]["extension_frames"], tot))
chk(fps == 24, "CreateVideo fps 24 -> duration %d/%d = %.4f s" % (tot, fps, tot / fps))
chk(g["save"]["inputs"]["filename_prefix"] == "community/" + ID + "/" + ID, "save.filename_prefix routes output into community/%s" % ID)

patt = []
for L in open(RALPH, encoding="utf-8", errors="replace").read().splitlines():
    if "-notmatch" in L:
        patt += re.findall(r"'(\^[^']+\$|\\\$\$[^']+)'", L)
p("ralph.ps1 -notmatch patterns: %d" % len(patt))
idpat = [x for x in patt if "ali147_pool" in x]
chk(len(idpat) >= 2, "found the p7 id patterns in the live ralph.ps1: %d" % len(idpat))
for x in idpat:
    chk(bool(re.match(x, j["id"])), "id matches %s" % x)

for f in ["p7/jobs/%s.result.json" % ID, "p7/jobs/%s.out" % ID, "p7/jobs/%s.err.out" % ID,
          "runs/%s/status.log" % ID, "runs/%s/objective.json" % ID, "runs/%s/%s.mp4" % (ID, ID),
          "runs/%s/%s.api.json" % (ID, ID), "p7/jobs/%s.result.json.failed-20261022" % ID]:
    chk(not os.path.exists(C + "/" + f), "absent (id free, no prior render): " + f)
b = json.load(open(BUDGET, encoding="utf-8")) if __import__("os").path.exists(BUDGET) else None  # Max2 audit-fix #2: budget retired (17e932f)
p("p7_budget.json %s" % json.dumps(b))
if b is None:  # Max2 audit-fix2 #1: missing p7_budget.json = budget gate retired (17e932f) = gate open, not a crash
    chk(True, "budget gate retired (17e932f): no p7_budget.json -> gate open")
else:
    chk(b["used_min"] < b["cap_min"], "used_min %s < cap_min %s (this job ~14 min at the 481-frame baseline)" % (b["used_min"], b["cap_min"]))
    chk(b["jobs"] < b["job_cap"], "jobs %s < job_cap %s" % (b["jobs"], b["job_cap"]))

chk(all(guard_ok(g[k]["inputs"]["prompt"]) for k in ("c0", "c1")), "comm.guard_ok passes on both prompts (the harness's own pre-render call)")
src = json.loads(open(SRC, "rb").read().decode("utf-8"))
diff = [n for n in sorted(g) if json.dumps(g[n], sort_keys=True) != json.dumps(src[n], sort_keys=True)]
chk(sorted(diff) == ["c0", "c1", "save"], "the graph the job names differs from the base seg3 graph in exactly ['c0','c1','save']: %s" % json.dumps(sorted(diff)))
for n, keys in [("c0", ["prompt"]), ("c1", ["prompt"]), ("save", ["filename_prefix"])]:
    ck = [k for k in g[n]["inputs"] if json.dumps(g[n]["inputs"][k], sort_keys=True) != json.dumps(src[n]["inputs"][k], sort_keys=True)]
    chk(sorted(ck) == sorted(keys), "%s inputs changed exactly %s: got %s" % (n, json.dumps(sorted(keys)), json.dumps(sorted(ck))))
for f in ["fairness.txt", "graph_diff.txt", "PROOF.md", "request.api.json"]:
    chk(os.path.exists(ARM + "/" + f), "arm artifact present: " + f)
chk(sorted(x for x in os.listdir(ARM)) == ["PROOF.md", "fairness.txt", "graph_diff.txt", "request.api.json"], "arm dir holds exactly the 4 allowed files")
p("")
p("The harness consumes p7/JOB_REQUEST.json at exit (moves it to p7/jobs/request_iter<NN>.json), so a")
p("re-request needs the file rewritten. Verify the RENDER in the next iteration per PROOF.md: result.json")
p("ok, status.log JOB end ok, cmp request.api.json vs <id>.api.json, ffprobe -count_packets 481,")
p("objective.json, sha256, contact-sheet coverage (a 481-frame sheet samples frames 204-276 and")
p("444/456/468/480 only, never 0/200/300/400). sbs_base_seg3_promptv2.mp4 and the fixed-frame stills")
p("are Max/harness outputs (run_graph_job.py has no hstack path), never Forge files. KEEP is Derek's.")
open(RPT, "w", encoding="utf-8").write("\n".join(O) + "\n")
print("\n".join(O))
print("ALL CHECKS PASS" if not FAIL else "CHECKS FAILED " + json.dumps(FAIL))
print("REPORT " + RPT)
