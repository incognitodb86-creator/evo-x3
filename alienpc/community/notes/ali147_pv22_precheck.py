import os, sys, re, json, hashlib
C = "C:/AI/community"
RC = "C:/Users/derek/5slock/ralph-community"
SRC = C + "/runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.api.json"
NAME = "ali147_pool_promptv2_seg3_s51080002"
ARM = C + "/runs/" + NAME
DST = ARM + "/request.api.json"
REQ = C + "/p7/JOB_REQUEST.json"
PROMPTS = [C + "/specs/prompt_v2/v2_seg3_c0_r2v.txt", C + "/specs/prompt_v2/v2_seg3_c1_t2va.txt"]
CFG = ["C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"]
RPT = C + "/notes/ali147-pv22-precheck-20261022.txt"
sys.path.insert(0, C + "/scripts")
L = []
ok = [True]
def p(s):
    L.append(str(s))
def sha(b):
    return hashlib.sha256(b).hexdigest()
def chk(cond, label):
    p(("PASS " if cond else "FAIL ") + label)
    if not cond:
        ok[0] = False
g = json.loads(open(DST, "rb").read().decode("utf-8"))
src = json.loads(open(SRC, "rb").read().decode("utf-8"))
p("PRE-PREQUEST READ-ONLY CHECK for " + NAME)
p("arm graph " + DST + " bytes %d sha256 %s" % (len(open(DST, "rb").read()), sha(open(DST, "rb").read())))
p("")
p("== adults-only guard (the harness's own call: run_graph_job.py -> comm.guard_ok; a hit = exit 3 CLIP_SKIP)")
from comm import guard_ok
for n in sorted(g):
    pv = g[n].get("inputs", {}).get("prompt")
    if isinstance(pv, str):
        chk(guard_ok(pv), "guard_ok on %s.prompt (%d chars, sha256 %s)" % (n, len(pv), sha(pv.encode())))
        for w in ("vulva", "pussy", "nude"):
            if w in pv.lower():
                p("  note: contains the word %r x%d (adult anatomy; not a guard term)" % (w, pv.lower().count(w)))
for fp in PROMPTS:
    t = open(fp, "rb").read().decode("utf-8")
    chk(guard_ok(t), "guard_ok on file " + os.path.basename(fp))
p("prompt-bearing nodes: %s" % json.dumps([n for n in sorted(g) if isinstance(g[n].get("inputs", {}).get("prompt"), str)]))
p("")
p("== job id gates parsed out of the LIVE ralph.ps1 (a hardcoded copy of a regex proves nothing)")
ps1 = open(RC + "/ralph.ps1", "rb").read().decode("utf-8", "replace")
pats = []
for ln in ps1.splitlines():
    if "-notmatch" in ln:
        for m in re.finditer(r"-notmatch\s+'(\$[A-Za-z0-9_]*\s*)?([^']*)'", ln):
            pats.append(m.group(2))
p("ralph.ps1 lines with -notmatch: %d, patterns found: %d" % (len([l for l in ps1.splitlines() if '-notmatch' in l]), len(pats)))
for pat in pats:
    p("  pattern " + pat)
idpats = [pt for pt in pats if "ali147" in pt]
chk(len(idpats) >= 1, "found the p7 id pattern(s) in ralph.ps1: %d" % len(idpats))
for pat in idpats:
    try:
        rr = re.compile(pat)
    except Exception as e:
        p("  cannot compile: " + repr(e))
        continue
    chk(bool(rr.match(NAME)), "id %s matches %s" % (NAME, pat))
kindpat = [pt for pt in pats if "graph" in pt and "dip" in pt]
for pat in kindpat:
    p("  kind/shape pattern (graph/dip) " + pat)
    p("  request line test: %s" % ("MATCH" if re.search(pat, json.dumps({"jobs": [{"id": NAME, "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": 60}]})) else "no"))
p("")
p("== id-free gates (ralph.ps1: 'id already used' / 'outputs exist')")
for f in (C + "/p7/jobs/" + NAME + ".result.json", C + "/p7/jobs/" + NAME + ".out", C + "/p7/jobs/" + NAME + ".err.out"):
    chk(not os.path.exists(f), "absent (id free): " + f)
for f in (ARM + "/status.log", ARM + "/objective.json", ARM + "/" + NAME + ".mp4", ARM + "/" + NAME + ".api.json", ARM + "/" + NAME + ".mp4.json", C + "/p7/jobs/" + NAME + ".result.json.failed-20261022"):
    chk(not os.path.exists(f), "absent (no prior render): " + f)
p("arm dir contents (only request.api.json / graph_diff.txt / fairness.txt / PROOF.md may exist - Forge-writable):")
if os.path.isdir(ARM):
    for n in sorted(os.listdir(ARM)):
        p("  %10d  %s" % (os.path.getsize(os.path.join(ARM, n)), n))
    chk(all(n in ("request.api.json", "graph_diff.txt", "fairness.txt", "PROOF.md") for n in os.listdir(ARM)), "arm dir holds only Forge-writable names")
p("p7/JOB_REQUEST.json present now: %s (a Request file is CONSUMED at exit -> p7/jobs/request_iter<NN>.json)" % os.path.exists(REQ))
p("")
p("== budget (live ralph-community/logs/p7_budget.json)")
bj = json.loads(open(RC + "/logs/p7_budget.json", "rb").read().decode("utf-8"))
p("p7_budget.json " + json.dumps(bj))
used = bj.get("used_min")
cap = bj.get("cap_min")
jobs = bj.get("jobs")
jcap = bj.get("job_cap")
chk(isinstance(used, (int, float)) and isinstance(cap, (int, float)) and used < cap, "used_min %s < cap_min %s" % (used, cap))
chk(isinstance(jobs, int) and isinstance(jcap, int) and jobs < jcap, "jobs %s < job_cap %s" % (jobs, jcap))
p("this job requests minutes=60 as a PRE-JOB gate only (ralph.ps1 clamps 30..180); the base run's own seg3 render time is read from its sidecar on the next lines.")
sd = json.loads(open(C + "/runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.mp4.json", "rb").read().decode("utf-8"))
p("base seg3 sidecar keys %s" % json.dumps(sorted(sd.keys())))
for kk in ("secs", "seed", "steps", "w", "h", "chunk_secs", "antiburn", "mode", "image_note", "comfy_output", "file", "prompt_id", "run", "id", "tag", "arm", "beat"):
    p("  sidecar %s -> %s" % (kk, json.dumps(sd.get(kk))[:200]))
p("  -> the base run's own seg3 render time is the control baseline for this arm (same graph, same seed).")
p("")
p("== class_type / input-key parity with the already-rendered base seg3 graph (no new node on this arm)")
chk(sorted(g.keys()) == sorted(src.keys()), "same 25 node keys as the base seg3 graph the harness already rendered")
bad = [n for n in sorted(g) if g[n].get("class_type") != src[n].get("class_type") or sorted(g[n]["inputs"].keys()) != sorted(src[n]["inputs"].keys())]
chk(not bad, "every class_type and input key set identical to the rendered source: %s" % json.dumps(bad))
p("classes used: " + json.dumps(sorted(set(g[n]["class_type"] for n in g))))
p("(MiniMaxH3* built-ins are NOT in specs/extender_object_info.json - Extender nodes only - their proof of listability is class_type in ok-rendered graphs.)")
p("")
p("== LoadImage strings resolve inside ComfyUI\\input")
for n in sorted(g):
    if g[n]["class_type"] == "LoadImage":
        s = g[n]["inputs"]["image"]
        hit = None
        for root in CFG:
            cand = os.path.join(root, s.replace("/", os.sep))
            if os.path.isfile(cand):
                hit = cand
                break
        chk(hit is not None, "%s image %r resolves inside ComfyUI\\input" % (n, s))
        if hit:
            b = open(hit, "rb").read()
            p("  %s bytes %d sha256 %s" % (hit, len(b), sha(b)))
            p("  MEASURED sha256 <%s> len %d" % (sha(b), len(sha(b))))
            p("  AGENTS.md POOL literal is 63 chars (%s) - comparing the 63-char prefix, never exact equality" % ("9cf9ff95f2d6f2fb3882219a8d98995b673e78a8001d7a41af1755cc918d075",))
            chk(len(sha(b)) == 64, "POOL still hash is a full 64-char sha256 (PV2-0 lesson: assert len==64)")
            import glob as _gl
            prev = set()
            for _f in _gl.glob(C + "/notes/*.txt") + _gl.glob(C + "/runs/*/PROOF.md") + _gl.glob(C + "/runs/*/fairness.txt"):
                try:
                    prev.update([t for t in re.findall(r"[0-9a-f]{64}", open(_f, encoding="utf-8", errors="replace").read()) if t.startswith("9cf9")])
                except Exception:
                    pass
            p("  POOL hash values recorded in existing Forge notes/PROOF/fairness files: %s" % json.dumps(sorted(prev)))
            chk(len(prev) == 1 and sha(b) == list(prev)[0], "POOL still sha256 == the single value recorded across existing notes/PROOF/fairness files (data-to-data compare; the AGENTS.md literal is a 63-char truncation, so string equality against it is a FALSE fail)")
        p("  (an absolute path outside input is invalid: nodes.py -> folder_paths.get_annotated_filepath requires is_within_directory)")
p("")
p("== settings held equal to the base seg3 graph")
chk(g["noise"]["inputs"]["noise_seed"] == 51080002 and src["noise"]["inputs"]["noise_seed"] == 51080002, "seed 51080002 in both (base seg3 seed)")
chk(g["c0"]["inputs"]["length"] + g["win1"]["inputs"]["extension_frames"] == 481, "c0.length %s + win1.extension_frames %s = 481" % (g["c0"]["inputs"]["length"], g["win1"]["inputs"]["extension_frames"]))
chk(g["mkvid"]["inputs"]["fps"] == 24, "fps 24")
chk(json.dumps(g["m_vsa"], sort_keys=True) == json.dumps(src["m_vsa"], sort_keys=True), "VSA node identical")
chk(g["m_attn"]["inputs"]["attention"] == "comfy kitchen attention", "m_attn attention is 'comfy kitchen attention' (NOT 'vsa' - a hardcoded enum would be a FALSE fail)")
chk(g["save"]["inputs"]["filename_prefix"] == "community/" + NAME + "/" + NAME, "filename_prefix routes output into community/" + NAME)
d = [n for n in sorted(src) if json.dumps(src[n], sort_keys=True) != json.dumps(g[n], sort_keys=True)]
chk(d == ["c0", "c1", "save"], "differing nodes exactly ['c0','c1','save'] (got %s)" % json.dumps(d))
p("")
p("== sbs / fixed-frame stills (Max's, per the TASKS sbs rule)")
sbs = []
for root, dirs, fn in os.walk(C + "/runs"):
    for f in fn:
        if f.startswith("sbs_"):
            sbs.append(os.path.join(root, f))
p("find runs -name 'sbs_*' = %d file(s): %s" % (len(sbs), json.dumps(sbs)))
p("expected at verify: sbs_base_seg3_promptv2.mp4 (base stitched 962-1442 | new 0-480) and full-res stills at")
p("new frames 200, 243, 300, 400, 480 = Max/harness files (run_graph_job.py has NO hstack path and its contact")
p("sheet samples only the +-1.5 s windows, so frames 200/300/400/480 are never covered by it).")
p("")
p("NOTE: the render itself (status.log JOB end ok, ffprobe 481/768x1344/24/audio, sha256, contact sheet, render secs)")
p("is verified in the NEXT iteration, per PROMPT.md: Forge may only REQUEST; the harness runs scripts/run_graph_job.py")
p("after this iteration exits. This line keeps '- [ ]'.")
open(RPT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
print("ALL CHECKS PASS" if ok[0] else "CHECKS FAILED")
print("REPORT " + RPT)
