# ALI-147 FIX4_REQ pre-check (READ-ONLY: no GPU, no ComfyUI/llama-swap call, no render, no writes outside notes\).
# Simulates the live harness gates out of ralph.ps1, then self-checks the FIX4 graph.
import json, hashlib, os, re, builtins

RUNS = r"C:/AI/community/runs"
ARM = "ali147_pool_fix4_s51080000"
ARMDIR = os.path.join(RUNS, ARM)
P7 = r"C:/AI/community/p7"
JOBS = os.path.join(P7, "jobs")
REQ = os.path.join(P7, "JOB_REQUEST.json")
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
RALPH = r"C:/Users/derek/5slock/ralph-community/ralph.ps1"
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
SPEC = r"C:/Users/derek/5slock/ralph-community/specs/extender_object_info.json"
WANT = {"id": ARM, "kind": "graph", "frames": 1443, "frames_tol": 24, "minutes": 180}
CLIP_FRAMES = [243, 260, 260, 260, 260, 260]
CTX = 22
TARGET, TOL = 1443, 24
fails = []
REPORT = r"C:/AI/community/notes/ali147-fix4-req-precheck-20261022.txt"
L = []


def print(*args, **kw):
    L.append(" ".join(str(a) for a in args))


def ck(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)
    return bool(cond)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------- A: the request file itself ----------
raw = open(REQ, "rb").read()
print("JOB_REQUEST.json bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest())
req = json.loads(raw.decode("utf-8"))
ck(list(req.keys()) == ["jobs"], "top level keys == ['jobs'] got %r" % (list(req.keys()),))
jobs = req.get("jobs", [])
ck(len(jobs) == 1, "exactly one job, got %d" % len(jobs))
j = jobs[0]
ck(sorted(j.keys()) == sorted(WANT.keys()), "job keys exactly id/kind/frames/frames_tol/minutes, got %r" % sorted(j.keys()))
for k, v in WANT.items():
    ck(j.get(k) == v, "job[%s] == %r (got %r)" % (k, v, j.get(k)))

# ---------- B: the live id regexes parsed out of ralph.ps1 (AGENTS.md RS6: parse, never hardcode) ----------
rl = open(RALPH, encoding="utf-8").read().splitlines()
pat = [m.group(1) for ln in rl for m in [re.search(r"\$id -notmatch '([^']+)'", ln)] if m]
ck(len(pat) == 2, "found 2 live id gates in ralph.ps1 (line 184 + the graph/dip gate), got %d: %r" % (len(pat), pat))
for p in pat:
    ck(re.match(p, ARM) is not None, "id %s matches live pattern %s" % (ARM, p))
gates = {}
for tag, key in [("id-already-used", r'Test-Path -LiteralPath "\$Jobs\\\$id\.result\.json"'),
                 ("budget-min", r"\[double\]\$b\.used_min -ge \$GpuCapMin"),
                 ("budget-jobs", r"\[int\]\$b\.jobs -ge \$JobMax"),
                 ("graph-missing-request", r'Test-Path -LiteralPath "\$run\\request\.api\.json"'),
                 ("graph-mp4-exists", r'Test-Path -LiteralPath "\$run\\\$id\.mp4"')]:
    gates[tag] = any(re.search(key, ln) for ln in rl)
    ck(gates[tag], "ralph.ps1 gate present: %s" % tag)

# ---------- C: the id gate ----------
res = os.path.join(JOBS, ARM + ".result.json")
out = os.path.join(JOBS, ARM + ".out")
err = os.path.join(JOBS, ARM + ".err.out")
live = [p for p in (res, out, err) if os.path.exists(p)]
moved = [p for p in (res, out, err) if os.path.exists(p + ".failed-20261022")]
ck(True, "p7\\jobs live files: %r .failed-20261022 copies: %r" % ([os.path.basename(p) for p in live], [os.path.basename(p) for p in moved]))
if os.path.exists(res):
    r = json.load(open(res, encoding="utf-8-sig"))
    print("  live result.json ok=%s rc=%s note=%s started=%s finished=%s" % (r.get("ok"), r.get("rc"), r.get("note"), r.get("started"), r.get("finished")))
ck(not os.path.exists(res), "harness gate 185: '%s.result.json' absent -> request accepted (if this FAILS the run will log 'refused: id already used', no GPU spent, no new result.json)" % ARM)
print("  -> PREDICTED: RunJobs logs \"P7 job %s refused: id already used\" (the :185 continue), writes NO result.json, spends NO GPU. Only the harness moving p7\\jobs\\<id>.result.json/.out/.err.out to *.failed-<date> frees the id (p7\\jobs = protected-paths [p7-harness], Forge must not move them)." % ARM)

# ---------- D: budget gate ----------
b = json.load(open(BUDGET, encoding="utf-8-sig"))
print("  p7_budget.json", b)
ck(float(b["used_min"]) < float(b["cap_min"]), "budget gate: used_min %s < cap_min %s" % (b["used_min"], b["cap_min"]))
ck(int(b["jobs"]) < int(b["job_cap"]), "job gate: jobs %s < job_cap %s" % (b["jobs"], b["job_cap"]))
print("  NOTE the 180 min request would take used_min to %.1f (cap %s): the gate is checked BEFORE the job only" % (float(b["used_min"]) + WANT["minutes"], b["cap_min"]))

# ---------- E: run folder gates ----------
graph = os.path.join(ARMDIR, "request.api.json")
ck(os.path.exists(graph), "run folder request.api.json present (gate 268)")
ck(not os.path.exists(os.path.join(ARMDIR, ARM + ".mp4")), "gate 269: %s.mp4 absent in run root (arm not rendered)" % ARM)
for f in ("status.log", "objective.json", ARM + ".api.json", ARM + "_stills_contact.png"):
    ck(not os.path.exists(os.path.join(ARMDIR, f)), "run root clean of prior-output %s (moved to failed-20261022)" % f)
ck(os.path.exists(os.path.join(ARMDIR, "failed-20261022", "status.log")), "old outputs preserved in failed-20261022\\status.log")
ck(os.path.exists(os.path.join(ARMDIR, "graph_diff.txt")), "graph_diff.txt present")
ck(os.path.exists(os.path.join(ARMDIR, "request.api.json.bak-20261022-fix4graph")), ".bak-20261022-fix4graph present")

# ---------- F: the graph ----------
g = json.load(open(graph, encoding="utf-8"))
print("graph nodes", len(g), "sha256", sha(graph), "bytes", os.path.getsize(graph))
oi = json.load(open(SPEC, encoding="utf-8"))
known = set(oi.keys())
for nid, nd in sorted(g.items()):
    ck(nd["class_type"] in known, "node %s class %s in specs\\extender_object_info.json" % (nid, nd["class_type"]))
for nid, nd in sorted(g.items()):
    opts = oi.get(nd["class_type"], {}).get("input", {})
    allin = set()
    dyn = set()
    for sec in ("required", "optional"):
        allin |= set(opts.get(sec, {}).keys())
        for k, v in opts.get(sec, {}).items():
            if isinstance(v, list) and v and isinstance(v[0], str) and "." in str(v[0]):
                dyn.add(str(v[0]))
            # dynamic-combo (COMFY_DYNAMICCOMBO_V3): sub-inputs live under options[].inputs
            if isinstance(v, list):
                for item in v[1:]:
                    if isinstance(item, dict):
                        for o in item.get("options", []):
                            if not isinstance(o, dict):
                                continue
                            for isec in ("required", "optional"):
                                for sub in (o.get("inputs", {}) or {}).get(isec, {}):
                                    dyn.add("%s.%s" % (k, sub))
    for k in sorted(nd["inputs"].keys()):
        ck(k in allin or k in dyn, "node %s input '%s' exists in object_info (dynamic-combo sub-inputs included)" % (nid, k))
    for k, v in nd["inputs"].items():
        if isinstance(v, list) and len(v) == 2 and isinstance(v[1], int):
            ck(str(v[0]) in g, "node %s link %s -> existing node %s" % (nid, k, v[0]))

ext = [n for n in g.values() if n["class_type"] == "MiniMaxH3Extender"]
ck(len(ext) == 1, "exactly one MiniMaxH3Extender")
e = ext[0]["inputs"]
for k, v in [("run_mode", "full_batch"), ("generation_mode", "ref2va"), ("motion_context", True),
             ("refine_enabled", False), ("resolution_mode", "manual"), ("width", 768), ("height", 1344),
             ("steps", 10), ("sampler_name", "euler"), ("scheduler", "simple"), ("denoise", 1.0),
             ("context_length", "22")]:
    ck(e.get(k) == v, "extender %s == %r (got %r)" % (k, v, e.get(k)))
cj = json.loads(e["clips_json"])
print("  clips_json top-level keys %r" % sorted(cj.keys()))
print("  clips_json project-level validated=%r seed=%r seed_mode=%r" % (cj.get("validated"), cj.get("seed"), cj.get("seed_mode")))
clips = cj["clips"]
print("  clip_1 keys %r" % sorted(clips[0].keys()))
ck(len(clips) == 6, "6 clips, got %d" % len(clips))
tot = 0
for i, c in enumerate(clips, 1):
    ck(c.get("validated") is False, "clip_%d validated false" % i)
    fr = int(round(float(c["duration"]) * 24))
    ck(fr == CLIP_FRAMES[i - 1], "clip_%d duration %s -> %d frames (expected %d)" % (i, c["duration"], fr, CLIP_FRAMES[i - 1]))
    ck((fr - 5) % 17 == 0, "clip_%d %d frames on the 5+17k grid" % (i, fr))
    ck(str(c.get("seed")) == "51080000" and c.get("seed_mode") == "fixed", "clip_%d seed 51080000 / seed_mode fixed (got %r %r)" % (i, c.get("seed"), c.get("seed_mode")))
    cp = c.get("prompt")
    ck(isinstance(cp, str) and len(cp) > 0, "clip_%d prompt is a non-empty string (%d chars) sha256 %s" % (i, len(cp or ""), hashlib.sha256((cp or "").encode()).hexdigest()))
    tot += fr
kept = tot - (len(clips) - 1) * CTX
print("  raw frames %d, kept after %d seams x%d = %d frames = %.3f s" % (tot, len(clips) - 1, CTX, kept, kept / 24.0))
ck(abs(kept - TARGET) <= TOL, "kept %d within tol %d of %d" % (kept, TOL, TARGET))
for i in range(1, 7):
    p = e.get("prompt_%d" % i)
    ck(p is None, "extender has no prompt_%d input (prompts live on the PromptPackBridge) (got %r)" % (i, p))
pp = [n for n in g.values() if n["class_type"] == "MiniMaxH3PromptPackBridge"][0]["inputs"]
for i in range(1, 7):
    t = pp.get("prompt_%d" % i)
    ck(isinstance(t, str) and len(t) > 0, "ppack prompt_%d is a non-empty string (%d chars) sha256 %s" % (i, len(t or ""), hashlib.sha256((t or "").encode()).hexdigest()))

sv = [n for n in g.values() if n["class_type"] == "SaveVideo"]
ck(len(sv) == 1, "exactly one SaveVideo")
pref = sv[0]["inputs"].get("filename_prefix")
ck(pref == "community/%s/%s" % (ARM, ARM), "SaveVideo filename_prefix %r" % pref)
ck(isinstance(sv[0]["inputs"].get("video"), list) and [x["class_type"] for x in (g[x[0]] for x in [sv[0]["inputs"]["video"]])] == ["MiniMaxH3MotionContextDiskFinalDecode"], "SaveVideo fed by MiniMaxH3MotionContextDiskFinalDecode")

imgs = sorted((nid, nd["inputs"].get("image")) for nid, nd in g.items() if nd["class_type"] == "LoadImage")
for nid, s in imgs:
    print("  node %s LoadImage %r" % (nid, s))
    p = os.path.join(COMFY_IN, str(s).replace("/", os.sep))
    ok = os.path.isfile(p)
    ck(ok, "node %s LoadImage '%s' resolves inside ComfyUI\\input" % (nid, s))
    if ok:
        print("    sha256 %s size %d" % (sha(p), os.path.getsize(p)))

# ---------- G: Fairness (l) vs the base arm ----------
BASE = r"C:/Users/derek/5slock/2026-10-22-run-a"
print("  base arm dir %s exists=%s" % (BASE, os.path.exists(BASE)))
print("  -> Fairness (l) node-by-node vs the base graph is NOT computable here (no 2026-10-22-run-a on disk, same state as spec item 8 and the FIX4_GRAPH notes); the only diff in graph_diff.txt is the .bak -> new clips_json pair")
dif = open(os.path.join(ARMDIR, "graph_diff.txt"), encoding="utf-8").read().splitlines()
rm = [x for x in dif if x.startswith("-") and not x.startswith("---")]
ad = [x for x in dif if x.startswith("+") and not x.startswith("+++")]
ck(len(rm) == 1 and len(ad) == 1, "graph_diff.txt = exactly 1 removed + 1 added line (the validated/duration clip list), got -%d +%d" % (len(rm), len(ad)))
# clips_json is a JSON *string* inside the graph, so its quotes are escaped: \"validated\": true
ntrue = sum(len(re.findall(r'validated\\*":\s*true', x)) for x in rm)
nfalse = sum(len(re.findall(r'validated\\*":\s*false', x)) for x in ad)
ck(ntrue == 6 and nfalse == 6, "the only removal carries escaped validated:true x6 (%d) and the only addition escaped validated:false x6 (%d)" % (ntrue, nfalse))

# ---------- H: node-level proof the FIX4 edit touched ONLY the Extender clips_json validated/duration ----------
OLDP = os.path.join(ARMDIR, "request.api.json.bak-20261022-fix4graph")
ga = json.load(open(OLDP, encoding="utf-8"))
J = lambda x: json.dumps(x, sort_keys=True)
allnodes = sorted(set(ga) | set(g))
chg = sorted(k for k in allnodes if J(ga.get(k)) != J(g.get(k)))
ck(sorted(ga) == sorted(g), "node id set unchanged (%d ids)" % len(allnodes))
ck(chg == ["ext"], "vs the .bak the changed node set is exactly ['ext'] (got %r); %d/%d nodes byte-identical" % (chg, len(allnodes) - len(chg), len(allnodes)))
oa = json.loads(ga["ext"]["inputs"]["clips_json"])["clips"]
ck(sorted(n for n in set(ga["ext"]["inputs"]) | set(e) if J(ga["ext"]["inputs"].get(n)) != J(e.get(n))) == ["clips_json"], "the only changed ext input key is clips_json")
for i, (x, y) in enumerate(zip(oa, clips), 1):
    dk = sorted(m for m in set(x) | set(y) if J(x.get(m)) != J(y.get(m)))
    ck(set(dk) <= {"validated", "duration"}, "clip_%d only validated/duration differ from the .bak (got %r)" % (i, dk))
    ck(J({m: v for m, v in x.items() if m not in ("validated", "duration")}) == J({m: v for m, v in y.items() if m not in ("validated", "duration")}), "clip_%d identical once validated/duration excluded, prompt sha256 %s" % (i, hashlib.sha256((y.get("prompt") or "").encode()).hexdigest()))

print()
print("ALL CHECKS PASS" if not fails else "CHECK FAILS %d" % len(fails))
for f in fails:
    print(" -", f)

full = "\n".join(L) + "\n"
open(REPORT, "w", encoding="utf-8").write(full)
# console: skip the per-node boilerplate, keep everything that matters
for ln in list(L):
    if not ln.startswith("PASS node "):
        builtins.print(ln)
builtins.print("report written: %s %d bytes" % (REPORT, len(full)))
