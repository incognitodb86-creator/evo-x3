# ALI-147 PV2-3 SETTINGS_DENSE seg1 RENDER VERIFY (READ-ONLY: no GPU/ComfyUI/llama-swap/Strata call,
# no render, no run_graph_job.py by Forge, no job request, no vision judge, no ffmpeg encode, no
# download/install/delete). Writes ONLY C:/AI/community/notes/. ffprobe/ffmpeg used as read-only probes.
import json, os, hashlib, subprocess, re, sys

FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
FFMPEG = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
RUNS = r"C:/AI/community/runs"
ARM = "ali147_pool_dense_s51080000"
CTRL = "ali147_pool_ctrl_s51080000"
ARMDIR = os.path.join(RUNS, ARM)
CTRLDIR = os.path.join(RUNS, CTRL)
JOBS = r"C:/AI/community/p7/jobs"
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
RALPHLOG = r"C:/Users/derek/5slock/ralph-community/logs/ralph.log"
REPORT = r"C:/AI/community/notes/ali147-pv23-verify-20261023.txt"
sys.path.insert(0, r"C:/AI/community/scripts")

FRAMES, W, H, FPS, TOL = 481, 768, 1344, 24, 0
CTRL_SECS = 809.7                      # quoted from CTRL status.log JOB end (15:55:32 CT)
GRAPH_SHA = "4e59e6265c5d5addc84bfa6ed4c37240da457878d9139243389f238e32726f39"
SRC_SHA = "698854152284100e60b6ac87a795a7f083160a9556acb3fb868793b7f4373bb6"
REQ_SHA = "c24820f489e112726ed5abe10a3c00d06f29605548eabe960e36bf7b6f04cd0a"
CTRL_GRAPH_SHA = "d9212ff14b1f899dd7fb67b308d4e09d86fc8520f2f828fd83d1cfd0408fbcb5"
CTRL_MP4_SHA = ""                       # measured below, printed for the report
PROMPT_SHA = {"c0": "7b4b22bb170f", "c1": "6686d7057ead"}
PROMPT_LEN = {"c0": 3295, "c1": 2303}
STILL_SHA = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"
VSA_KEYS = ["model", "selection", "selection.keep_percent", "start_percent", "end_percent", "min_tokens",
            "extra_tokens", "sink_conditioning", "dense_blocks", "verbose"]

fails = []
L = []


def p(*a):
    L.append(" ".join(str(x) for x in a))


def ck(cond, msg):
    p(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)
    return bool(cond)


def sha(pth):
    return hashlib.sha256(open(pth, "rb").read()).hexdigest()


def shastr(s):
    return hashlib.sha256(s.encode()).hexdigest()


def J(x):
    return json.dumps(x, sort_keys=True)


def probe(args, exe=FFPROBE):
    r = subprocess.run([exe, "-v", "error"] + args, capture_output=True, text=True)
    return (r.returncode, r.stdout.strip(), r.stderr.strip())


def lines_of(pth):
    return open(pth, encoding="utf-8", errors="replace").read().splitlines()


mp4 = os.path.join(ARMDIR, ARM + ".mp4")
sheet = os.path.join(ARMDIR, ARM + "_stills_contact.png")
statuslog = os.path.join(ARMDIR, "status.log")
objp = os.path.join(ARMDIR, "objective.json")
graph = os.path.join(ARMDIR, "request.api.json")
hapi = os.path.join(ARMDIR, ARM + ".api.json")
gdiff = os.path.join(ARMDIR, "graph_diff.txt")
sidecar = os.path.join(ARMDIR, ARM + ".mp4.json")
resj = os.path.join(JOBS, ARM + ".result.json")
outj = os.path.join(JOBS, ARM + ".out")
errj = os.path.join(JOBS, ARM + ".err.out")
ctrlsrc = os.path.join(CTRLDIR, "submitted_graph.pretty.json")
ctrlhapi = os.path.join(CTRLDIR, CTRL + ".api.json")
ctrlmp4 = os.path.join(CTRLDIR, CTRL + ".mp4")
ctrlstatus = os.path.join(CTRLDIR, "status.log")
ctrlside = os.path.join(CTRLDIR, CTRL + ".mp4.json")
ctrlobj = os.path.join(CTRLDIR, "objective.json")
ctrlsheet = os.path.join(CTRLDIR, CTRL + "_stills_contact.png")

p("== A. harness result gate (p7\\jobs\\%s.result.json)" % ARM)
res = json.load(open(resj, encoding="utf-8-sig"))
for k in ("ok", "rc", "note", "id", "kind", "started", "finished", "wall_min", "budget_used_min", "budget_cap_min"):
    p("  result.json %s = %r" % (k, res.get(k)))
ck(res.get("ok") is True, "result.json ok is True (the task's 'JOB end ok' gate)")
ck(res.get("rc") == 0, "result.json rc == 0 (got %r)" % res.get("rc"))
ck(res.get("id") == ARM and res.get("kind") == "graph", "result.json id/kind match the arm")
ck(not any((ARM + ".result.json.failed") in f for f in os.listdir(JOBS)), "no failed-<date> copy for this id (never refused, never re-run)")
ck(os.path.exists(outj) and open(outj, "rb").read() == open(statuslog, "rb").read(),
   "p7\\jobs\\<id>.out is byte-identical to runs\\<id>\\status.log (same job log)")
ck(os.path.getsize(errj) == 0, "p7\\jobs\\<id>.err.out is 0 bytes (no stderr, no CUDA OOM text there)")

p("\n== B. status.log verbatim + error greps (the task's 'JOB end ok')")
sl = open(statuslog, encoding="utf-8", errors="replace").read()
sln = sl.splitlines()
for ln in sln:
    p("  | " + ln)
for pat in ["JOB error", "CLIP_SKIP", "clip_skip", "node_errors", "Traceback", "STUCK", "REDO", "redo",
            "STATIC_FAIL", "COMFY_DOWN", "OBJECTIVE FAIL", "error", "ERROR", "SKIP", "blocked",
            "out of memory", "CUDA out of memory", "OOM", "RuntimeError", "Killed", "timeout"]:
    hits = [ln for ln in sln if pat.lower() in ln.lower()]
    ck(hits == [], "status.log: no %r (hits %d)" % (pat, len(hits)))
starts = [ln for ln in sln if "JOB start " + ARM in ln]
ends = [ln for ln in sln if "JOB end " + ARM + " ok" in ln]
objectives = [ln for ln in sln if "OBJECTIVE ok " + ARM in ln]
unload = [ln for ln in sln if "UNLOAD LLM" in ln]
ck(len(unload) == 1, "the LLM was unloaded before the job (ALI-154) by the harness: %r" % unload)
ck(len(starts) == 1, "exactly one JOB start line for the arm")
ck(len(ends) == 1, "exactly one 'JOB end ... ok' line for the arm")
ck(len(objectives) == 1, "exactly one OBJECTIVE ok line for the arm")
p("  JOB start : %s" % (starts[0] if starts else "MISSING"))
p("  JOB end   : %s" % (ends[0] if ends else "MISSING"))
p("  OBJECTIVE : %s" % (objectives[0] if objectives else "MISSING"))
msecs = re.search(r"secs=([0-9.]+)", ends[0]) if ends else None
ck(bool(msecs), "the JOB end line carries secs= (render seconds are quotable)")
ck(res.get("started", "").startswith("2026-10-22T23:47:34"), "result.json started == the status.log UNLOAD/JOB start (23:47:34 CT)")
ck(res.get("finished", "").startswith("2026-10-23T00:06:22"), "result.json finished == the status.log last line (00:06:22 CT)")
cl = lines_of(ctrlstatus)
cstart = [x for x in cl if "JOB start " + CTRL in x]
cend = [x for x in cl if "JOB end " + CTRL in x]
cobj = [x for x in cl if "OBJECTIVE ok " + CTRL in x]
p("  CONTROL status.log lines:")
for x in cl:
    p("    | " + x)
cm = re.search(r"secs=([0-9.]+)", cend[0]) if cend else None
ck(bool(cm) and float(cm.group(1)) == CTRL_SECS, "CTRL baseline re-read from the live file: secs=%s (the task's 809.7 denominator)" % (cm.group(1) if cm else "MISSING"))
ck(len(cobj) == 0, "documented: the DRIVER-RENDERED CTRL status.log has NO 'OBJECTIVE ok' line (its JOB end line is 'recorded by ali147_record_ctrl.py'), so the control's frame count comes from its objective.json + the ffprobe recount (C/D)")

p("\n== C. objective.json (harness shape attempts:[{...}]) + the render-seconds comparison")
obj = json.load(open(objp, encoding="utf-8"))
p("  top-level keys %s" % sorted(obj.keys()))
att = obj["attempts"]
p("  attempts: %d" % len(att))
ck(len(att) == 1, "one attempt only = no redo, no STUCK (got %d)" % len(att))
a = att[0]
for k in ("frames", "w", "h", "fps", "audio", "duration", "bytes", "secs", "blackfreeze", "file", "tag"):
    p("  attempts[0].%s = %r" % (k, a.get(k)))
p("  top-level ok=%r contact_sheet=%r" % (obj.get("ok"), obj.get("contact_sheet")))
ck(obj.get("ok") is True, "objective.json ok is True")
ck(a["frames"] == FRAMES, "objective frames == %d (request frames %d, frames_tol %d)" % (FRAMES, FRAMES, TOL))
ck((a["w"], a["h"]) == (W, H), "resolution %dx%d" % (W, H))
ck(a["fps"] == "24/1", "fps 24/1 (got %r)" % a["fps"])
ck(a["audio"] is True, "audio stream present")
ck(a["blackfreeze"] == [], "blackfreeze [] = no black/frozen frames (the harness chain)")
ck(a["bytes"] == os.path.getsize(mp4), "objective bytes == os.path.getsize(mp4) (%d)" % os.path.getsize(mp4))
ck(abs(a["secs"] - float(msecs.group(1))) < 1e-9, "objective secs == the status.log secs= (%.1f)" % a["secs"])
ck(os.path.normcase(str(obj.get("contact_sheet"))) == os.path.normcase(sheet) and os.path.exists(sheet),
   "objective contact_sheet == the file in the arm dir (%r)" % obj.get("contact_sheet"))
co = json.load(open(ctrlobj, encoding="utf-8"))
p("  CONTROL objective.json keys %s (flat shape, no attempts)" % sorted(co.keys()))
p("  control objective: frames=%r w=%r h=%r fps=%r audio=%r bytes=%r secs=%r blackfreeze=%r"
  % (co.get("frames"), co.get("w"), co.get("h"), co.get("fps"), co.get("audio"), co.get("bytes"), co.get("secs"), co.get("blackfreeze")))
ck(co.get("frames") == FRAMES and (co.get("w"), co.get("h")) == (W, H) and co.get("fps") == "24/1" and co.get("audio") is True,
   "the control objective shape matches the arm's (481 / 768x1344 / 24/1 / audio) = a valid one-variable control")
ck(co.get("secs") == CTRL_SECS, "control objective.json secs == %.1f = the denominator the task names" % CTRL_SECS)
p("  RENDER SECONDS (the task's 'report the slowdown'): dense %.1f s vs CTRL %.1f s = %+.1f s (%+.2f %%, ratio %.3fx)"
  % (a["secs"], CTRL_SECS, a["secs"] - CTRL_SECS, 100.0 * (a["secs"] - CTRL_SECS) / CTRL_SECS, a["secs"] / CTRL_SECS))
p("  wall: result.json wall_min %.1f (%s -> %s); the request's minutes=120 is a PRE-job gate/timeout, not a render cap"
  % (res.get("wall_min", 0.0), res.get("started"), res.get("finished")))
rows = []
for d in sorted(os.listdir(RUNS)):
    if not d.startswith("ali147_pool_"):
        continue
    ojp = os.path.join(RUNS, d, "objective.json")
    mp = os.path.join(RUNS, d, d + ".mp4")
    if not (os.path.exists(ojp) and os.path.exists(mp)):
        continue
    o2 = json.load(open(ojp, encoding="utf-8"))
    rec = o2["attempts"][0] if "attempts" in o2 else o2      # two shapes: a loop arm nests attempts, the driver CTRL is flat
    if rec.get("frames") == FRAMES and rec.get("secs"):
        rows.append((float(rec["secs"]), d, "objective.json (%s)" % ("attempts[0]" if "attempts" in o2 else "flat")))
rows.sort()
p("  every 481-frame render in runs\\ (secs, id, source), ascending:")
for s2, d2, src2 in rows:
    p("    %8.1f s  %-42s %s  vs CTRL %+.1f s" % (s2, d2, src2, s2 - CTRL_SECS))
ck(any(x[1] == ARM and x[0] == a["secs"] for x in rows) and rows[-1][1] == ARM,
   "dense is the SLOWEST 481-frame render in runs\\ (the VSA-off slowdown is the set maximum)")
ck(rows[0][0] < CTRL_SECS < a["secs"], "the CTRL baseline sits inside the spread: fastest %.1f s < CTRL %.1f s < dense %.1f s" % (rows[0][0], CTRL_SECS, a["secs"]))
ck(len([x for x in rows if x[1] == CTRL]) == 1, "the driver-rendered CTRL (flat objective.json, no status.log OBJECTIVE line) IS in the table via its objective.json secs")
p("  bytes dense %d vs CTRL %d = %+d (%.2f %%)" % (a["bytes"], co.get("bytes", 0), a["bytes"] - co.get("bytes", 0),
                                                    100.0 * (a["bytes"] - co.get("bytes", 0)) / co.get("bytes", 1)))

p("\n== D. independent ffprobe recount + black/frozen re-probes (read-only, this iteration)")
rc, so, se = probe(["-select_streams", "v:0", "-count_packets",
                    "-show_entries", "stream=nb_read_packets,r_frame_rate,avg_frame_rate,width,height", "-of", "csv=p=0", mp4])
p("  video: rc=%d out=%r err=%r" % (rc, so, se))
parts = so.split(",")
vframes = int(parts[-1]) if parts and parts[-1].isdigit() else -1
ck(rc == 0 and vframes == FRAMES, "ffprobe -count_packets video packets = %d (independent recount, never format=duration)" % vframes)
ck(parts[0] == str(W) and parts[1] == str(H), "ffprobe width/height %dx%d" % (W, H))
ck("24/1" in parts, "ffprobe r_frame_rate 24/1")
rc, so, se = probe(["-show_entries", "stream=index,codec_type,codec_name,channels,sample_rate,duration,nb_frames", "-of", "csv=p=0", mp4])
p("  streams: rc=%d out=%r" % (rc, so))
sa = [x for x in so.splitlines() if ",audio," in x]
ck(len(sa) == 1, "exactly one audio stream in the container (%r)" % sa)
rc, so, se = probe(["-show_entries", "format=duration,size", "-of", "csv=p=0", mp4])
p("  format (informational, NOT the frame gate): %r" % so)
rc, so, se = probe(["-select_streams", "v:0", "-count_packets",
                    "-show_entries", "stream=nb_read_packets,width,height,r_frame_rate", "-of", "csv=p=0", ctrlmp4])
p("  CTRL recount: rc=%d out=%r" % (rc, so))
ck(rc == 0 and so.split(",")[-1] == str(FRAMES), "CTRL is 481 packets = a valid one-variable control (same frame count)")
CTRL_MP4_SHA = sha(ctrlmp4)
p("  CTRL mp4 %d B sha256 %s" % (os.path.getsize(ctrlmp4), CTRL_MP4_SHA))
p("  CTRL mp4 sha256 is measured here (the report quotes it); the pair is hash-attested by this file")
HF = re.search(r'"-vf", "([^"]+)"', open(r"C:/AI/community/scripts/run_graph_job.py", encoding="utf-8").read())
if not HF:
    HF = re.search(r'-vf", "([^"]+)"', open(r"C:/AI/community/scripts/run_graph_job.py", encoding="utf-8").read())
p("  harness blackfreeze filter chain (run_graph_job.py) = %r" % (HF.group(1) if HF else "NOT FOUND"))
ck(bool(HF), "the harness blackdetect+freezedetect chain is readable out of run_graph_job.py")
rc, so, se = probe(["-i", mp4, "-vf", HF.group(1), "-an", "-f", "null", "NUL"], FFMPEG)
ev = [x.strip() for x in se.splitlines() if "black_start" in x or "freeze_start" in x]
p("  harness-chain events: %r rc=%d" % (ev, rc))
ck(ev == [], "re-running the harness's own blackdetect+freezedetect chain gives 0 events = objective.json blackfreeze [] reproduces")
rc, so, se = probe(["-i", mp4, "-vf", "blackdetect=d=0.2:pix_th=0.10", "-an", "-f", "null", "NUL"], FFMPEG)
bl = [x.strip() for x in se.splitlines() if "black_start" in x]
p("  stricter blackdetect (d=0.2): %r rc=%d" % (bl, rc))
ck(bl == [], "own stricter blackdetect: no black intervals")
rc, so, se = probe(["-i", mp4, "-vf", "freezedetect=n=0.005:d=0.5", "-an", "-f", "null", "NUL"], FFMPEG)
fz = [x.strip() for x in se.splitlines() if "freeze_start" in x]
p("  stricter freezedetect (n=0.005 d=0.5): %r rc=%d" % (fz, rc))
ck(fz == [], "own stricter freezedetect: no frozen intervals >= 0.5 s")

p("\n== E. provenance: the graph that rendered is the graph Forge wrote")
grb, hab = open(graph, "rb").read(), open(hapi, "rb").read()
p("  request.api.json %d B sha256 %s" % (len(grb), sha(graph)))
p("  %s.api.json %d B sha256 %s" % (ARM, len(hab), sha(hapi)))
ck(hab == grb, "%s.api.json is BYTE-IDENTICAL to request.api.json (plain cmp: no output) = the rendered graph is mine" % ARM)
ck(sha(graph) == GRAPH_SHA, "request.api.json sha256 == the iter-12 request note %s..." % GRAPH_SHA[:12])
ck(len(GRAPH_SHA) == 64 and len(sha(graph)) == 64, "both graph hashes are 64 hex chars (the 63-char literal trap)")
ck(sha(ctrlsrc) == SRC_SHA, "CTRL copy source (submitted_graph.pretty.json) sha256 == the recorded %s..." % SRC_SHA[:12])
p("  CTRL rendered .api.json %d B sha256 %s" % (os.path.getsize(ctrlhapi), sha(ctrlhapi)))
p("  CTRL source .pretty.json %d B sha256 %s" % (os.path.getsize(ctrlsrc), sha(ctrlsrc)))
ck(len(sha(ctrlhapi)) == 64 and len(sha(ctrlsrc)) == 64, "both CTRL graph hashes are 64 hex chars")
p("  NOTE: the AGENTS-recorded 'graph d9212ff14b1f...' matches NEITHER on-disk file measured here (the CTRL mp4 line is 'recorded by ali147_record_ctrl.py'); the fairness gate is the node-body compare, not that literal.")
g = json.load(open(graph, encoding="utf-8"))
ga = json.load(open(hapi, encoding="utf-8"))
sg = json.load(open(ctrlsrc, encoding="utf-8"))
sga = json.load(open(ctrlhapi, encoding="utf-8"))
ck(J(g) == J(ga), "parsed graphs identical (%d nodes)" % len(g))
csame = [k for k in sg if k in sga and J(sg[k]) == J(sga[k])]
ck(sorted(sg) == sorted(sga) and len(csame) == len(sg),
   "CTRL source vs CTRL rendered api: %d/%d node bodies byte-identical (only top-level KEY ORDER differs - the known PV2-1 finding); byte equality is NOT expected and is not a gate" % (len(csame), len(sg)))
ck(len([x for x in os.listdir(ARMDIR) if "_redo" in x]) == 0, "no *_redo*.api.json in the arm dir (consistent with attempts length 1)")
reqs = sorted([f for f in os.listdir(JOBS) if f.startswith("request_iter")])
p("  p7\\jobs request archives: %r" % reqs)
hits = [f for f in reqs if sha(os.path.join(JOBS, f)) == REQ_SHA]
ck(len(hits) == 1, "the consumed job request (sha256 %s...) is archived at exactly one p7\\jobs\\%s = one job per request" % (REQ_SHA[:12], hits))
if hits:
    p("  archived request: %s" % open(os.path.join(JOBS, hits[0]), encoding="utf-8").read().strip())
    rq = json.load(open(os.path.join(JOBS, hits[0]), encoding="utf-8"))
    ck(len(rq.get("jobs", [])) == 1 and rq["jobs"][0]["id"] == ARM and rq["jobs"][0]["kind"] == "graph"
       and rq["jobs"][0]["frames"] == FRAMES and rq["jobs"][0]["frames_tol"] == 0 and rq["jobs"][0]["minutes"] == 120,
       "the archived request is exactly one graph job (id %s, frames 481, tol 0, minutes 120)" % ARM)
    mod = json.load(open(os.path.join(JOBS, "request_iter10.json"), encoding="utf-8"))
    p("  model request_iter10.json: %s" % open(os.path.join(JOBS, "request_iter10.json"), encoding="utf-8").read().strip())
    ck(len(mod.get("jobs", [])) == 1 and set(rq["jobs"][0]) == set(mod["jobs"][0])
       and all(str(rq["jobs"][0][k]) == str(mod["jobs"][0][k]) for k in mod["jobs"][0] if k not in ("id", "minutes")),
       "bytes-shape = the accepted model request with ONLY id + minutes differing (keys identical: %r)" % sorted(mod["jobs"][0]))
p("  p7\\JOB_REQUEST.json present = %s (a Request file is CONSUMED at exit)" % os.path.exists(r"C:/AI/community/p7/JOB_REQUEST.json"))
side = json.load(open(sidecar, encoding="utf-8"))
for k, v in sorted(side.items()):
    p("  sidecar %s = %r" % (k, str(v)[:120]))
ck(side.get("label") == "METHOD_ONLY" and side.get("run") == ARM and side.get("attempt") == 0,
   "sidecar labels METHOD_ONLY, run = the arm, attempt 0 (no redo; KEEP is Derrick's)")
ck(side.get("prompt_id") == re.search(r"prompt_id=(\S+)", starts[0]).group(1), "sidecar prompt_id == the status.log JOB start prompt_id")
ck(side.get("secs") == a["secs"], "sidecar secs == objective.json secs (%.1f)" % a["secs"])
cside = json.load(open(ctrlside, encoding="utf-8"))
p("  CTRL sidecar label=%r run=%r seed=%r secs=%r prompt_id=%r" % (cside.get("label"), cside.get("run"), cside.get("seed"), cside.get("secs"), cside.get("prompt_id")))

p("\n== F. the ONE variable: m_shift.model -> m_attn, m_vsa deleted, nothing else touched")
ck("m_vsa" in sg and "m_vsa" not in g, "m_vsa exists in the control graph and is DELETED in the arm")
ck(sg["m_shift"]["inputs"]["model"] == ["m_vsa", 0], "control m_shift.model = ['m_vsa', 0] (the VSA-patched model)")
ck(g["m_shift"]["inputs"].get("model") == ["m_attn", 0], "arm m_shift.model = ['m_attn', 0] (the task's exact change)")
cons = sorted({(k, key) for k, n in sg.items() for key, v in n["inputs"].items() if isinstance(v, list) and len(v) == 2 and v[0] == "m_vsa"})
p("  control consumers of m_vsa: %r" % cons)
ck(cons == [("m_shift", "model")], "m_vsa had exactly one consumer (m_shift.model) = the single rewire is provable")
dangling = sorted({(k, key) for k, n in g.items() for key, v in n["inputs"].items()
                   if isinstance(v, list) and len(v) == 2 and (v[0] == "m_vsa" or v[0] not in g)})
ck(dangling == [], "no link in the arm points at m_vsa or at any missing node (no dangling links): %r" % dangling)
p("  arm m_shift class_type=%r inputs=%s" % (g["m_shift"]["class_type"], sorted(g["m_shift"]["inputs"].keys())))
p("  arm m_attn class_type=%r inputs=%s attention=%r" % (g["m_attn"]["class_type"], sorted(g["m_attn"]["inputs"].keys()), g["m_attn"]["inputs"].get("attention")))
p("  control m_vsa class_type=%r inputs=%s" % (sg["m_vsa"]["class_type"], sorted(sg["m_vsa"]["inputs"].keys())))
for k in VSA_KEYS:
    p("    removed VSA setting %s = %r" % (k, sg["m_vsa"]["inputs"].get(k)))
ck(sorted(sg["m_vsa"]["inputs"].keys()) == sorted(VSA_KEYS),
   "the deleted node carried exactly the 9 VSA settings the task names PLUS its own 'model' link input (= 10 input keys)")
ck(J(g["m_attn"]) == J(sg["m_attn"]) and g["m_attn"]["inputs"].get("attention") == "comfy kitchen attention",
   "m_attn is UNTOUCHED (attention = %r read from the file, NOT a hardcoded enum); it is now the last model patch in the chain" % g["m_attn"]["inputs"].get("attention"))
ck(J(g["m_shift"]) != J(sg["m_shift"]) and [k for k in g["m_shift"]["inputs"] if J(g["m_shift"]["inputs"][k]) != J(sg["m_shift"]["inputs"][k])] == ["model"],
   "m_shift: the ONLY changed input is 'model' (other inputs identical)")
ac, cc = sorted({n["class_type"] for n in g.values()}), sorted({n["class_type"] for n in sg.values()})
p("  arm classes (%d): %r" % (len(ac), ac))
p("  control classes (%d): %r" % (len(cc), cc))
ck(set(ac) < set(cc) and set(cc) - set(ac) == {sg["m_vsa"]["class_type"]}, "no NEW node class: arm classes = control classes minus the deleted BlockSparseAttention-type node")
ck(all(n["class_type"] in {x["class_type"] for x in sga.values()} for n in g.values()),
   "every arm class_type also appears in the ok-rendered CTRL .api.json = the strongest non-GPU listability proof (the node-list GET at 127.0.0.1:10004 is the harness's at render time)")
ck(sga["m_vsa"]["class_type"] not in {n["class_type"] for n in g.values()}, "the VSA patch class is absent from the arm = full dense attention")
ck(g["save"]["inputs"]["filename_prefix"] == "community/%s/%s" % (ARM, ARM), "save.filename_prefix = the new id (%r)" % g["save"]["inputs"]["filename_prefix"])
p("  prefix chain: %r -> %r (the only prefix change, per graph_diff)" % (sg["save"]["inputs"]["filename_prefix"], g["save"]["inputs"]["filename_prefix"]))
noise = sorted([k for k, n in g.items() if n["class_type"] == "RandomNoise"])
p("  RandomNoise nodes: %r seeds=%r (control %r)" % (noise, [g[k]["inputs"]["noise_seed"] for k in noise], [sg[k]["inputs"]["noise_seed"] for k in noise if k in sg]))
ck(noise and all(str(g[k]["inputs"]["noise_seed"]) == "51080000" for k in noise)
   and all(J(g[k]) == J(sg[k]) for k in noise), "seed held at 51080000 and every RandomNoise node is IDENTICAL to the control")
sched = sorted([k for k, n in g.items() if n["class_type"] == "BasicScheduler"])
p("  schedulers: %r" % sched)
for k in sched:
    ck(J(g[k]) == J(sg[k]), "%s (BasicScheduler steps/scheduler/denoise) identical to the control: %r" % (k, [g[k]["inputs"].get(x) for x in ("steps", "scheduler", "denoise")]))
ck(J(g["img"]) == J(sg["img"]), "LoadImage node identical: %r" % g["img"]["inputs"]["image"])
li = [n["inputs"]["image"] for n in g.values() if n["class_type"] == "LoadImage"]
sp = os.path.join(COMFY_IN, str(li[0]).replace("/", os.sep))
ck(os.path.isfile(sp) and sha(sp) == STILL_SHA, "the start still resolves inside ComfyUI\\input: %d B sha256 %s" % (os.path.getsize(sp), sha(sp)))
ck(len(STILL_SHA) == 64 and sha(sp).startswith("9cf9ff95f2d6"), "still hash is 64 hex chars and starts with the recorded prefix (the 63-char AGENTS literal is a truncation = a false fail)")
for nid in ("c0", "c1"):
    gp = ga[nid]["inputs"]["prompt"]
    ck(J(g[nid]) == J(sg[nid]), "%s node byte-identical to the control (prompt = CTRL verbatim)" % nid)
    ck(len(gp) == PROMPT_LEN[nid] and shastr(gp).startswith(PROMPT_SHA[nid]),
       "%s prompt %d chars sha256 %s... = the recorded CTRL text (no prompt edit in a settings arm)" % (nid, len(gp), shastr(gp)[:12]))
import comm
ck(comm.guard_ok(ga["c0"]["inputs"]["prompt"]) and comm.guard_ok(ga["c1"]["inputs"]["prompt"]),
   "adults-only guard (the harness's own comm.guard_ok, run_graph_job.py:60) passes on both rendered prompts")
pk = sorted([k for k, n in ga.items() if isinstance(n["inputs"].get("prompt"), str)])
ck(pk == ["c0", "c1"] and pk == sorted([k for k, n in sga.items() if isinstance(n["inputs"].get("prompt"), str)]),
   "only c0/c1 carry prompt strings in the arm and the control (no hidden prompt edits)")
ck(g["c0"]["inputs"]["length"] == sg["c0"]["inputs"]["length"] == 243
   and g["c0"]["inputs"]["width"] == W and g["c0"]["inputs"]["height"] == H, "c0.length 243 + 768x1344 (control values)")
ext = g["win1"]["inputs"]["extension_frames"]
ck(243 + ext == FRAMES, "c0.length 243 + win1.extension_frames %d = %d = the requested frames (the control's own budget)" % (ext, FRAMES))
ck(J(g["win1"]) == J(sg["win1"]), "win1 identical (only the frame-budget arithmetic matters here)")
ck(len(g) == len(sg) - 1, "node count %d = control %d minus the deleted m_vsa" % (len(g), len(sg)))
raw = open(graph, encoding="utf-8", newline="").read()
canon = json.dumps(g, indent=1, ensure_ascii=True)
ck(raw.replace("\r\n", "\n") == canon, "arm graph is canonical json.dumps(indent=1, ensure_ascii=True) (LF-normalised compare)")
ck("\r\n" in raw and not raw.endswith("\n") and not raw.endswith("\r\n"), "arm graph is CRLF with NO trailing newline (the accepted .api.json shape)")
srctext = open(ctrlsrc, encoding="utf-8", errors="replace").read()
ck(len(srctext.splitlines()) - 18 == len(raw.splitlines()), "line count = control %d - 18 (the deleted m_vsa block) = %d" % (len(srctext.splitlines()), len(raw.splitlines())))

p("\n== G. fairness vs the RENDERED control graph: only m_shift + save differ")
shared = sorted(set(sga) & set(g))
same, diff = [], []
for k in shared:
    (same if J(sga[k]) == J(g[k]) else diff).append(k)
p("  shared nodes %d, identical %d, differing nodes %r, control-only nodes %r" % (len(shared), len(same), diff, sorted(set(sga) - set(g))))
ck(sorted(diff) == ["m_shift", "save"], "differing node set over the %d SHARED nodes == ['m_shift','save'] (%d/%d byte-identical)" % (len(shared), len(same), len(shared)))
ck(sorted(set(sga) - set(g)) == ["m_vsa"], "the only node in the control and not in the arm is m_vsa")
ck(sorted(set(g) - set(sga)) == [], "no node was added")
for nid, keys in (("m_shift", ["model"]), ("save", ["filename_prefix"])):
    akeys, skeys = sorted(g[nid]["inputs"].keys()), sorted(sga[nid]["inputs"].keys())
    ck(akeys == skeys, "%s input key set unchanged (%r)" % (nid, akeys))
    changed = [k for k in akeys if J(g[nid]["inputs"][k]) != J(sga[nid]["inputs"][k])]
    ck(changed == keys, "%s: changed inputs == %r (got %r)" % (nid, keys, changed))
held = ["m_attn", "c0", "c1", "img", "win1", "app1"]
for k in held:
    if k in sga and k in g:
        ck(J(g[k]) == J(sga[k]), "held identical to the control: node %s (%s)" % (k, g[k]["class_type"]))
for k in ("sampler_name", "noise_seed", "steps", "scheduler", "denoise", "seed"):
    av = sorted({str(n["inputs"][k]) for n in g.values() if k in n["inputs"]})
    cv = sorted({str(n["inputs"][k]) for n in sga.values() if k in n["inputs"]})
    if not av and not cv:
        p("  (no node carries %r in either graph - skipped, an empty==empty gate is a false fail)" % k)
        continue
    ck(av == cv and av != [], "held equal across the whole graph: %s = %r (control %r)" % (k, av, cv))

p("\n== H. graph_diff.txt: the task's 'shows only m_shift.model, m_vsa removed, filename_prefix'")
gdl = lines_of(gdiff)
hunks = [x for x in gdl if x.startswith("@@")]
rem = [x for x in gdl if x.startswith("-") and not x.startswith("---")]
add = [x for x in gdl if x.startswith("+") and not x.startswith("+++")]
p("  graph_diff.txt %d B sha256 %s hunks=%d removed=%d added=%d" % (os.path.getsize(gdiff), sha(gdiff), len(hunks), len(rem), len(add)))
ck(len(hunks) == 2 and len(rem) == 20 and len(add) == 2,
   "the diff is exactly 2 hunks / 20 removed / 2 added lines = the three named changes and nothing else")
adst = [y.lstrip("+").strip() for y in add]
rmst = [y.lstrip("-").strip() for y in rem]
p("  removed lines (%d):" % len(rmst))
for x in rmst:
    p("    - %s" % x)
p("  added lines (%d): %r" % (len(adst), adst))
p("  hunks: %r" % hunks)
srcraw = srctext.splitlines()
armraw = raw.replace("\r\n", "\n").splitlines()
srcstripped = [s.strip() for s in srcraw]
armstripped = [s.strip() for s in armraw]
# the m_vsa node block, found by BRACE DEPTH (a "next node key" heuristic over-deletes - AGENTS)
st = srcstripped.index('"m_vsa": {')
blk, depth = [], 0
for i in range(st, len(srcraw)):
    blk.append(srcstripped[i])
    depth += srcraw[i].count("{") - srcraw[i].count("}")
    if depth == 0:
        break
ck(len(blk) == 18, "the m_vsa node block is 18 lines (control lines %d-%d), located by brace depth" % (st + 1, st + len(blk)))
link = [x for x in srcstripped if x == '"m_vsa",']
ck(len(link) == 1, "the control graph has exactly one '\"m_vsa\",' link element line (the m_shift.model input) = a single rewire")
alinks = [x for x in armstripped if x == '"m_attn",']
ck(len(alinks) == 1, "the arm graph has exactly one '\"m_attn\",' link element line (the new m_shift.model input)")
pf = [x for x in srcstripped if x.startswith('"filename_prefix"')]
apf = [x for x in armstripped if x.startswith('"filename_prefix"')]
ck(len(pf) == 1 and CTRL in pf[0], "the control prefix line is unique and names the CTRL id: %r" % (pf[0] if pf else None))
ck(len(apf) == 1 and g["save"]["inputs"]["filename_prefix"] in apf[0], "the arm prefix line is unique and names the arm id: %r" % (apf[0] if apf else None))
ck(sorted(rmst) == sorted(blk + ['"m_vsa",', pf[0]]),
   "the removed set == the 18-line m_vsa block + the m_shift 'm_vsa' link line + the CTRL prefix line, nothing else (%d lines)" % len(rmst))
ck(sorted(adst) == sorted(['"m_attn",', apf[0]]), "the added set == the m_shift 'm_attn' link line + the arm prefix line, nothing else (%d lines)" % len(adst))
ck(all(x in srcstripped for x in rmst), "every removed line is byte-equal to a control graph line (diff marker + indentation stripped)")
ck(all(x in armstripped for x in adst), "every added line is byte-equal to an arm graph line")
ck(not any('"prompt"' in x for x in rmst + adst), "no prompt line in the diff = prompts are CTRL verbatim (confirms F)")
ck(not any('"class_type"' in x for x in adst), "no new node block in the diff (nothing was added except 2 single lines)")
ck(len(srcraw) - len(armraw) == 18, "line count control %d - arm %d = 18 = the deleted block only" % (len(srcraw), len(armraw)))

p("\n== I. outputs: sizes, sha256, contact-sheet geometry and sampled frames")
for f in [mp4, sheet, graph, hapi, sidecar, statuslog, objp, gdiff]:
    p("  %-58s %10d B sha256 %s" % (os.path.basename(f), os.path.getsize(f), sha(f)))
p("  CONTROL for the sbs pair: mp4 %d B sha256 %s / contact sheet %d B sha256 %s"
  % (os.path.getsize(ctrlmp4), CTRL_MP4_SHA, os.path.getsize(ctrlsheet), sha(ctrlsheet)))
ck(a["bytes"] == os.path.getsize(mp4) == int(re.search(r"bytes=(\d+)", objectives[0]).group(1)),
   "mp4 bytes agree across objective.json, the status.log OBJECTIVE line and os.path.getsize")
ck(os.path.getsize(sheet) > 0 and os.path.getsize(hapi) > 0, "the contact sheet and the rendered .api.json are non-empty")
im = __import__("PIL.Image", fromlist=["open"]).open(sheet)
dur = a["duration"]
ts = sorted({round(m + d * 0.5, 2) for m in (10, 20, 30, 40, 50) for d in range(-3, 4) if 0 <= m + d * 0.5 <= dur - 0.05})
cols = 7
rowsn = (len(ts) + cols - 1) // cols
th = int(round(256.0 * H / W / 2) * 2)
p("  contact sheet PIL %r mode=%s format=%s  expected for %d tiles (grid %dx%d, tile 256x%d, padding 4): (%d, %d)"
  % (im.size, im.mode, im.format, len(ts), cols, rowsn, th, cols * 256 + (cols - 1) * 4, rowsn * th + (rowsn - 1) * 4))
ck(im.size == (cols * 256 + (cols - 1) * 4, rowsn * th + (rowsn - 1) * 4), "contact-sheet geometry matches run_graph_job.py:contact_sheet for a %.3f s clip" % dur)
cov = sorted({int(round(t * FPS)) for t in ts})
p("  sampled t = %r s -> frames %r" % (ts, cov))
ck(cov == [204, 216, 228, 240, 252, 264, 276, 444, 456, 468], "the 481-frame sheet samples exactly frames 204-276 + 444-468 (10 tiles)")
ck(max(cov) == 468, "the LAST sampled frame is 468: the t=20.0 tile is dropped by the code's t <= dur-0.05 test (dur 20.0417), so frames 480 and 0 are NEVER sampled by the sheet")
p("  never sampled by the sheet: frames 0-203, 277-443, 445-455, 457-467, 469-480")
p("  the review is this contact sheet + the objective checks only: no vision judge was called on any output (superseded 2026-10-22)")
p("  dir listing runs\\%s" % ARM)
for f in sorted(os.listdir(ARMDIR)):
    fp = os.path.join(ARMDIR, f)
    p("    %s %s %d" % ("d " if os.path.isdir(fp) else "f ", f, os.path.getsize(fp)))
ck(sorted(os.listdir(ARMDIR)) == [ARM + ".api.json", ARM + ".mp4", ARM + ".mp4.json", ARM + "_stills_contact.png",
                                  "graph_diff.txt", "objective.json", "request.api.json", "status.log"],
   "arm dir holds only harness outputs + the graph_diff.txt Forge is allowed to write (no PROOF.md/fairness.txt on a render line)")
p("  NOTE: this PV2-3 line names no PROOF.md/fairness.txt; the report is the PV2-6 notes file (Max posts it).")

p("\n== J. sbs / fixed-frame stills (Max's per the TASKS sbs rule) + p7 budget + ralph.log")
r = subprocess.run(["find", RUNS, "-name", "sbs_*.mp4"], capture_output=True, text=True)
names = [x.replace(RUNS + os.sep, "") for x in r.stdout.split()]
p("  find runs -name sbs_*.mp4 -> %r" % names)
ck(not any("dense" in x for x in names), "no sbs_ctrl_dense.mp4 exists -> sbs/stills pending Max (run_graph_job.py has no hstack path; sbs_* are Max/harness files)")
r2 = subprocess.run(["find", RUNS, "-name", "*dense*"], capture_output=True, text=True)
p("  find runs -name *dense* -> %r" % [x.replace(RUNS + os.sep, "") for x in r2.stdout.split()])
ck(not any("sbs" in x or "still" in x.lower() for x in r2.stdout.split() if "_stills_contact.png" not in x),
   "no fixed-frame stills for this arm in runs (run_graph_job.py writes only the contact sheet)")
bud = json.load(open(BUDGET, encoding="utf-8-sig"))
p("  %s = %s" % (BUDGET, json.dumps(bud)))
p("  result.json snapshot (older): budget_used_min %r cap %r" % (res.get("budget_used_min"), res.get("budget_cap_min")))
ck(bud.get("used_min", 1e9) < bud.get("cap_min", 0) and bud.get("jobs", 10 ** 9) < bud.get("job_cap", 0),
   "live budget after this job: used_min %r < cap_min %r, jobs %r < job_cap %r" % (bud.get("used_min"), bud.get("cap_min"), bud.get("jobs"), bud.get("job_cap")))
p("  this arm spent %.1f min of GPU wall (%.1f s render); the CTRL cost %.1f s = %.1f min; delta %+.1f min"
  % (res.get("wall_min", 0.0), a["secs"], CTRL_SECS, CTRL_SECS / 60.0, (a["secs"] - CTRL_SECS) / 60.0))
log = open(RALPHLOG, encoding="utf-8", errors="replace").read().splitlines()
p("  last 8 ralph.log lines:")
for ln in log[-8:]:
    p("    | " + ln)
joblines = [ln for ln in log if ARM in ln and "P7 job" in ln]
p("  P7 job lines for the arm: %r" % joblines)
ck(len([x for x in joblines if "ok=True" in x]) == 1 and len([x for x in joblines if "refused" in x.lower()]) == 0,
   "the harness ran this job exactly once, ok=True, never refused")
ck(len([x for x in joblines if "ok=False" in x]) == 0, "no ok=False run of this id (no second attempt, no re-request)")
p("  request-time budget check (iter 12 note): used_min 356.5 < 390, jobs 25 < 27 - both gates passed; live now: %r" % json.dumps(bud))

p("")
p("ALL CHECKS PASS" if not fails else "CHECK FAILS %d" % len(fails))
for f in fails:
    p(" -", f)
full = "\n".join(L) + "\n"
open(REPORT, "w", encoding="utf-8").write(full)
print(full)
print("report written: %s (%d bytes)" % (REPORT, len(full)))
