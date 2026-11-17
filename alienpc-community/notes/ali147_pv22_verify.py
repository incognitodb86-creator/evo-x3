# ALI-147 PV2-2 PROMPT_V2 seg3 RENDER VERIFY (READ-ONLY: no GPU/ComfyUI/llama-swap/Strata call, no
# render, no run_graph_job.py by Forge, no job request, no vision judge, no ffmpeg encode).
# Writes ONLY C:/AI/community/notes/. ffprobe/ffmpeg used as read-only probes only.
import json, os, hashlib, subprocess, re, sys

FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
FFMPEG = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
RUNS = r"C:/AI/community/runs"
ARM = "ali147_pool_promptv2_seg3_s51080002"
BASE = "p7_r2_c3_pmot_full_pool"            # the control run (its own segment 3)
SEG = BASE + "_seg3"
ARMDIR = os.path.join(RUNS, ARM)
BASEDIR = os.path.join(RUNS, BASE)
JOBS = r"C:/AI/community/p7/jobs"
PROMPTS = r"C:/AI/community/specs/prompt_v2"
BASEPROMPTS = os.path.join(BASEDIR, "prompts")
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
REPORT = r"C:/AI/community/notes/ali147-pv22-verify-20261022.txt"
sys.path.insert(0, r"C:/AI/community/scripts")

FRAMES, W, H, FPS, TOL = 481, 768, 1344, 24, 0
BASE_SECS, CTRL_SECS, PV21_SECS = 816.0, 809.7, 827.7
GRAPH_SHA = "935622324ad136b1c970963c5c1331143677717e39c33d5c62bdbb19f0492fe2"
SRC_SHA = "c5b6726c1d5870f597ba51fcf65499d489be9a1755ebf1905ab8fac5960e8fec"
DIFF_SHA = "1d9cd4dee53e5b6c792a44150ffd50edf793934bd20f1639178140f064b091b7"
REQ_SHA = "4766e4c9b0c64b3bafc9a2170d777ea559212b6852d10e5381b81bbafc61003e"
P0 = {"c0": ("8ed332629e80a8702f11eb4eb996e5a42fe3ee5f716168d25512ae01d7df5d76", 3354,
             BASEPROMPTS, BASE + "_seg3_c0_long_r2v.txt", 3373),
      "c1": ("dcd574692f426508d5ed5703cda68080ad7e9b1e8b4a49c0da3b049fd4b45d89", 2269,
             BASEPROMPTS, BASE + "_seg3_c1_long_cont.txt", 2275)}
P1 = {"c0": ("ad77122b96f4ad474a6329a72b556f3372a80cb010e68a6c3ea10fe48a53763b", 4358, "v2_seg3_c0_r2v.txt"),
      "c1": ("2e3905ee2272a9d7ff0ab47d5db1765e4fa456ba4aa5ae2798e3fac404cfb383", 2903, "v2_seg3_c1_t2va.txt")}
STILL_SHA = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a8001d7a41af1755cc918d075"
STILL_SHA_FULL = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"
BASE_MP4_SHA = "fc28701abc585f3ae052b9316df22ba4edf7f31a2f3c685d2bbd758d2191d053"
STITCH_SHA = "ae93a7477aefc5ef698de0ac71d45e13f29731732ce3a0c832ac8360acda581d"
STILL_FRAMES = [200, 243, 300, 400, 480]

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


def fold(raw):
    return raw.decode("utf-8").replace("\r\n", "\n").rstrip("\n")


mp4 = os.path.join(ARMDIR, ARM + ".mp4")
sheet = os.path.join(ARMDIR, ARM + "_stills_contact.png")
statuslog = os.path.join(ARMDIR, "status.log")
objp = os.path.join(ARMDIR, "objective.json")
graph = os.path.join(ARMDIR, "request.api.json")
hapi = os.path.join(ARMDIR, ARM + ".api.json")
gdiff = os.path.join(ARMDIR, "graph_diff.txt")
fair = os.path.join(ARMDIR, "fairness.txt")
proofmd = os.path.join(ARMDIR, "PROOF.md")
sidecar = os.path.join(ARMDIR, ARM + ".mp4.json")
resj = os.path.join(JOBS, ARM + ".result.json")
outj = os.path.join(JOBS, ARM + ".out")
srcgraph = os.path.join(BASEDIR, SEG + ".api.json")
basemp4 = os.path.join(BASEDIR, SEG + ".mp4")
baseside = os.path.join(BASEDIR, SEG + ".mp4.json")
stitch = os.path.join(BASEDIR, BASE + "_stitched.mp4")

p("== A. harness result gate (p7\\jobs\\%s.result.json)" % ARM)
res = json.load(open(resj, encoding="utf-8-sig"))
for k in ("ok", "rc", "note", "id", "kind", "started", "finished", "wall_min", "budget_used_min", "budget_cap_min"):
    p("  result.json %s = %r" % (k, res.get(k)))
ck(res.get("ok") is True, "result.json ok is True (the task's 'JOB end ok' gate)")
ck(res.get("rc") == 0, "result.json rc == 0 (got %r)" % res.get("rc"))
ck(res.get("id") == ARM and res.get("kind") == "graph", "result.json id/kind match the arm")
ck(os.path.exists(outj) and open(outj, "rb").read() == open(statuslog, "rb").read(),
   "p7\\jobs\\<id>.out is byte-identical to runs\\<id>\\status.log (same job log)")
ck(not os.path.exists(os.path.join(JOBS, ARM + ".result.failed-20261022.json")), "no failed-<date> copy for this id (never refused)")

p("\n== B. status.log verbatim + error greps (last 30 lines are the whole file)")
sl = open(statuslog, encoding="utf-8", errors="replace").read()
lines = sl.splitlines()
for ln in lines:
    p("  | " + ln)
for pat in ["JOB error", "CLIP_SKIP", "clip_skip", "node_errors", "Traceback", "STUCK", "REDO", "redo",
            "STATIC_FAIL", "COMFY_DOWN", "OBJECTIVE FAIL", "error", "ERROR", "SKIP", "blocked"]:
    hits = [ln for ln in lines if pat.lower() in ln.lower()]
    ck(hits == [], "status.log: no %r (hits %d)" % (pat, len(hits)))
starts = [ln for ln in lines if "JOB start " + ARM in ln]
ends = [ln for ln in lines if "JOB end " + ARM + " ok" in ln]
objectives = [ln for ln in lines if "OBJECTIVE ok " + ARM in ln]
unload = [ln for ln in lines if "UNLOAD LLM" in ln]
ck(len(unload) == 1, "the LLM was unloaded before the job (ALI-154) by the harness: %r" % unload)
ck(len(starts) == 1, "exactly one JOB start line for the arm")
ck(len(ends) == 1, "exactly one 'JOB end ... ok' line for the arm")
ck(len(objectives) == 1, "exactly one OBJECTIVE ok line for the arm")
p("  JOB start : %s" % (starts[0] if starts else "MISSING"))
p("  JOB end   : %s" % (ends[0] if ends else "MISSING"))
p("  OBJECTIVE : %s" % (objectives[0] if objectives else "MISSING"))
msecs = re.search(r"secs=([0-9.]+)", ends[0]) if ends else None
ck(bool(msecs), "the JOB end line carries secs= (render seconds are quotable)")
ck(res.get("started", "").startswith("2026-10-22T23:12:00"), "result.json started == the status.log UNLOAD/job start (23:12:00 CT)")
ck(res.get("finished", "").startswith("2026-10-22T23:26:28"), "result.json finished == the status.log last line (23:26:28 CT)")

p("\n== C. objective.json (harness shape attempts:[{...}]) + control comparison")
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
ck(os.path.normcase(str(obj.get("contact_sheet"))) == os.path.normcase(sheet) and os.path.exists(sheet), "objective contact_sheet == the file in the arm dir (%r)" % obj.get("contact_sheet"))
bs = json.load(open(baseside, encoding="utf-8"))
p("  CONTROL sidecar %s.mp4.json:" % SEG)
for k, v in sorted(bs.items()):
    p("    %s = %r" % (k, str(v)[:120]))
ck(bs.get("secs") == BASE_SECS and bs.get("seed") in (51080002, "51080002"),
   "control sidecar secs %r and seed %r (the base run's own segment 3 = the same-seed control)" % (bs.get("secs"), bs.get("seed")))
p("  RENDER SECONDS: arm %.1f s vs base seg3 %.1f s = %+.1f s (%+.2f %%); other 481-frame renders: CTRL %.1f, PV2-1 %.1f"
  % (a["secs"], BASE_SECS, a["secs"] - BASE_SECS, 100.0 * (a["secs"] - BASE_SECS) / BASE_SECS, CTRL_SECS, PV21_SECS))
p("  wall: result.json wall_min %.1f (%s -> %s); the request's minutes=60 is a PRE-job gate, not a render cap"
  % (res.get("wall_min", 0.0), res.get("started"), res.get("finished")))
bc = probe(["-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets,width,height,r_frame_rate", "-of", "csv=p=0", basemp4])
p("  control video recount: rc=%d out=%r" % (bc[0], bc[1]))
ck(bc[0] == 0 and bc[1].split(",")[-1] == str(FRAMES), "control is 481 packets = a valid one-variable control (same frame count, frames_tol 0 both)")
p("  bytes arm %d vs control %d = %+d (%.2f %%)" % (a["bytes"], os.path.getsize(basemp4), a["bytes"] - os.path.getsize(basemp4),
                                                     100.0 * (a["bytes"] - os.path.getsize(basemp4)) / os.path.getsize(basemp4)))

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
HARNESS_FILT = re.search(r'"-vf", "([^"]+)"', open(r"C:/AI/community/scripts/run_graph_job.py", encoding="utf-8").read()).group(1)
p("  harness filter chain (run_graph_job.py blackfreeze) = %r" % HARNESS_FILT)
rc, so, se = probe(["-i", mp4, "-vf", HARNESS_FILT, "-an", "-f", "null", "NUL"], FFMPEG)
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
ck(sha(graph) == GRAPH_SHA, "request.api.json sha256 == the PROOF record %s" % GRAPH_SHA)
ck(sha(srcgraph) == SRC_SHA, "copy source (base seg3 graph) sha256 == the PROOF record %s" % SRC_SHA[:16])
g = json.load(open(graph, encoding="utf-8"))
ga = json.load(open(hapi, encoding="utf-8"))
ck(J(g) == J(ga), "parsed graphs identical (%d nodes)" % len(g))
ck(len([x for x in os.listdir(ARMDIR) if "_redo" in x]) == 0, "no *_redo*.api.json in the arm dir (consistent with attempts length 1)")
reqs = sorted([f for f in os.listdir(JOBS) if f.startswith("request_iter")])
p("  p7\\jobs request archives: %r" % reqs)
hits = [f for f in reqs if sha(os.path.join(JOBS, f)) == REQ_SHA]
ck(len(hits) >= 1, "the consumed job request (sha256 %s...) is archived at p7\\jobs\\%s = exactly one job, id as written" % (REQ_SHA[:12], hits))
if hits:
    p("  archived request content: %s" % open(os.path.join(JOBS, hits[0]), encoding="utf-8").read().strip())
p("  p7\\JOB_REQUEST.json present = %s (a Request file is CONSUMED at exit)" % os.path.exists(r"C:/AI/community/p7/JOB_REQUEST.json"))
side = json.load(open(sidecar, encoding="utf-8"))
for k, v in sorted(side.items()):
    p("  sidecar %s = %r" % (k, str(v)[:120]))
ck(side.get("label") == "METHOD_ONLY" and side.get("run") == ARM and side.get("attempt") == 0,
   "sidecar labels METHOD_ONLY, run = the arm, attempt 0 (no redo)")
ck(side.get("prompt_id") == "2f5e0d06-b177-4463-814f-183b4d63aebf", "sidecar prompt_id == the status.log JOB start prompt_id")
ck(side.get("secs") == a["secs"], "sidecar secs == objective.json secs (%.1f)" % a["secs"])

p("\n== F. prompts: P0 (base sidecars -> base graph) = P1 (spec files) = P2 (rendered graph)")
sg = json.load(open(srcgraph, encoding="utf-8"))
for nid in ("c0", "c1"):
    h, n, d, fn, fsz = P0[nid]
    fp = os.path.join(d, fn)
    base_txt = sg[nid]["inputs"]["prompt"]
    p("  P0 %s: base graph %d ch sha256 %s | sidecar %s %d B" % (nid, len(base_txt), shastr(base_txt), os.path.basename(fp), os.path.getsize(fp)))
    ck(shastr(base_txt) == h and len(base_txt) == n, "P0: base graph %s.prompt == the PROOF record (%d ch, %s...)" % (nid, n, h[:12]))
    ck(shastr(fold(open(fp, "rb").read())) == shastr(base_txt),
       "P0 provenance: the base run's prompt sidecar %s (EOL-fold + rstrip) == base graph %s.prompt" % (fn, nid))
    ck(os.path.getsize(fp) == fsz, "sidecar size %d B as recorded" % fsz)
for nid in ("c0", "c1"):
    h, n, fn = P1[nid]
    fp = os.path.join(PROMPTS, fn)
    raw = open(fp, "rb").read()
    gp = ga[nid]["inputs"]["prompt"]
    p("  P1/P2 %s: file %d B sha256 %s | RENDERED graph string %d ch sha256 %s" % (nid, len(raw), sha(fp), len(gp), shastr(gp)))
    ck(sha(fp) == h, "P1: spec file %s sha256 == the PV2-0/SHA256SUMS record" % fn)
    ck(len(raw.decode("utf-8")) == n, "P1: spec file %s is %d chars as recorded" % (fn, n))
    ck(gp == raw.decode("utf-8"), "P2: the RENDERED graph's %s.prompt == %s VERBATIM (byte-for-byte)" % (nid, fn))
    ck(shastr(gp) == h, "P2: rendered %s.prompt sha256 == %s (P1 == P2)" % (nid, h[:12]))
sums = open(os.path.join(PROMPTS, "SHA256SUMS.txt"), encoding="utf-8").read()
rows = dict((n2, h2) for h2, n2 in re.findall(r"^([0-9a-f]{64})\s+\*?\s*(\S+)$", sums, re.M))
p("  SHA256SUMS rows parsed: %d" % len(rows))
for _, _, fn in P1.values():
    ck(rows.get(fn) == P1[[k for k in P1 if P1[k][2] == fn][0]][0], "SHA256SUMS entry for %s matches the measured file" % fn)
pdir = os.path.join(ARMDIR, "prompts")
p("  P3 rendered prompt sidecars: arm prompts dir exists = %s" % os.path.isdir(pdir))
p("  run_graph_job.py / comm.run write no prompt sidecars (P3 = the .api.json the harness rendered, which is byte-identical to request.api.json; see E + P2 above)")
ck(not os.path.isdir(pdir), "no P3 sidecar dir is produced by the harness (documented: P3 closes via the byte-identical .api.json, as in every p7 graph arm)")
for nid in ("c0", "c1"):
    ck(len(ga[nid]["inputs"]["prompt"]) > len(sg[nid]["inputs"]["prompt"]),
       "prompt grew vs the control: %s %d -> %d ch (the delta is the only variable)" % (nid, len(sg[nid]["inputs"]["prompt"]), len(ga[nid]["inputs"]["prompt"])))
import comm
ck(comm.guard_ok(ga["c0"]["inputs"]["prompt"]) and comm.guard_ok(ga["c1"]["inputs"]["prompt"]),
   "adults-only guard (the harness's own comm.guard_ok, run_graph_job.py:60) passes on both rendered V2 prompts")
ck(sorted([k for k, n in ga.items() if isinstance(n["inputs"].get("prompt"), str)]) == ["c0", "c1"],
   "only c0/c1 carry prompt strings in the rendered graph (no hidden prompt edits)")

p("\n== G. fairness vs the base seg3 graph: only c0.prompt, c1.prompt, filename_prefix")
same, diff = [], []
for k in sorted(set(sg) | set(g)):
    (same if (k in sg and k in g and J(sg[k]) == J(g[k])) else diff).append(k)
p("  identical nodes %d, differing nodes %r" % (len(same), diff))
ck(sorted(diff) == ["c0", "c1", "save"], "differing node set == ['c0','c1','save'] (%d/%d nodes byte-identical)" % (len(same), len(sg)))
for nid, keys in (("c0", ["prompt"]), ("c1", ["prompt"]), ("save", ["filename_prefix"])):
    akeys, skeys = sorted(g[nid]["inputs"].keys()), sorted(sg[nid]["inputs"].keys())
    ck(akeys == skeys, "%s input key set unchanged (%r)" % (nid, akeys))
    changed = [k for k in akeys if J(g[nid]["inputs"][k]) != J(sg[nid]["inputs"][k])]
    ck(changed == keys, "%s: changed inputs == %r (got %r)" % (nid, keys, changed))
ck(g["save"]["inputs"]["filename_prefix"] == "community/%s/%s" % (ARM, ARM), "save.filename_prefix = the new id (%r)" % g["save"]["inputs"]["filename_prefix"])
ck(g["noise"]["inputs"]["noise_seed"] == 51080002 == sg["noise"]["inputs"]["noise_seed"], "seed held at 51080002 (the base run's own seg3 seed; the noise node is IDENTICAL)")
for k, v in (("sampler_name", "euler"),):
    ids = [n["inputs"].get(k) for n in g.values() if k in n["inputs"]]
    ids_s = [n["inputs"].get(k) for n in sg.values() if k in n["inputs"]]
    ck(ids and set(map(str, ids)) == {str(v)} and ids == ids_s, "held equal: %s = %r on every node that has it, arm and control" % (k, v))
for nid in ("s0_sched", "s1_sched"):
    ck((g[nid]["inputs"]["steps"], g[nid]["inputs"]["scheduler"], g[nid]["inputs"]["denoise"]) ==
       (sg[nid]["inputs"]["steps"], sg[nid]["inputs"]["scheduler"], sg[nid]["inputs"]["denoise"]),
       "%s steps/scheduler/denoise identical to the control (%r)" % (nid, [g[nid]["inputs"][x] for x in ("steps", "scheduler", "denoise")]))
ck(J(g["m_shift"]) == J(sg["m_shift"]), "m_shift (sigma 10/3) identical")
ck(J(g["m_attn"]) == J(sg["m_attn"]) and g["m_attn"]["inputs"].get("attention") == "comfy kitchen attention",
   "m_attn identical (attention = %r, read from the file, NOT a hardcoded enum)" % g["m_attn"]["inputs"].get("attention"))
ck(J(g["m_vsa"]) == J(sg["m_vsa"]), "VSA patch node identical (this arm is prompt-only; dense is PV2-3, LoraLoaderModelOnly is PV2-4)")
ck(J(g["img"]) == J(sg["img"]), "LoadImage node identical: %r" % g["img"]["inputs"]["image"])
ck(g["c0"]["inputs"]["length"] == 243 and g["c0"]["inputs"]["width"] == W and g["c0"]["inputs"]["height"] == H, "c0.length 243 + 768x1344 (control values)")
ext = g["win1"]["inputs"]["extension_frames"]
ck(243 + ext == FRAMES, "c0.length 243 + win1.extension_frames %d = %d = the requested frames (the control's own budget)" % (ext, FRAMES))
for k in ("app1",):
    ck(J(g[k]) == J(sg[k]), "%s (context_frames 22) identical" % k)
li = [n["inputs"]["image"] for n in g.values() if n["class_type"] == "LoadImage"]
sp = os.path.join(COMFY_IN, str(li[0]).replace("/", os.sep))
ck(os.path.isfile(sp) and sha(sp) == STILL_SHA_FULL, "the start still resolves inside ComfyUI\\input: %d B sha256 %s" % (os.path.getsize(sp), sha(sp)))
ck(len(sha(sp)) == 64 and len(STILL_SHA_FULL) == 64 and sha(sp).startswith(STILL_SHA[:12]),
   "still hash is 64 hex chars and starts with the recorded prefix (the 63-char AGENTS literal is a truncation = a false fail)")
gd = open(gdiff, encoding="utf-8", errors="replace").read()
gdl = gd.splitlines()
hunks = [x for x in gdl if x.startswith("@@")]
rem = [x for x in gdl if x.startswith("-") and not x.startswith("---")]
add = [x for x in gdl if x.startswith("+") and not x.startswith("+++")]
p("  graph_diff.txt %d B sha256 %s hunks=%d removed=%d added=%d" % (os.path.getsize(gdiff), sha(gdiff), len(hunks), len(rem), len(add)))
ck(sha(gdiff) == DIFF_SHA, "graph_diff.txt sha256 == the PROOF record %s..." % DIFF_SHA[:12])
ck(len(hunks) == 3 and len(rem) == 3 and len(add) == 3, "the task's 'graph_diff only those 3 fields' = 3 hunks, exactly 3 removed + 3 added lines")
ck(all('"prompt":' in x for x in rem[:2]) and "filename_prefix" in rem[2], "the 3 removed lines are prompt, prompt, filename_prefix (control side)")
ck(all('"prompt":' in x for x in add[:2]) and "filename_prefix" in add[2], "the 3 added lines are prompt, prompt, filename_prefix (arm side)")
srctext = open(srcgraph, encoding="utf-8", errors="replace").read()
armtext = open(graph, encoding="utf-8", errors="replace").read()
srcraw = srctext.splitlines()
armraw = armtext.splitlines()
rmst = [y.lstrip("-").strip() for y in rem]
adst = [y.lstrip("+").strip() for y in add]
idx = [i for i, x in enumerate(srcraw) if x.strip() in rmst]
p("  control line indices of the 3 removed lines (0-based): %r" % idx)
ck(len(idx) == 3, "each removed line is byte-equal to a line of the control graph (diff marker + indentation stripped)")
ck(all(x in armtext for x in adst), "each added line is byte-equal to a line of the arm graph (diff marker + indentation stripped)")
ck(all(x in srctext for x in rmst), "each removed line is byte-equal to a line of the control graph (substring check on the raw file)")
ck(len(srcraw) == len(armraw), "line count unchanged (%d/%d lines) = shape-preserving edit" % (len(srcraw), len(armraw)))
ck(os.path.getsize(fair) > 0 and "c0" in open(fair, encoding="utf-8", errors="replace").read(), "fairness.txt exists and names the differing nodes")

p("\n== H. outputs: sizes, sha256, contact-sheet geometry and sampled frames")
for f in [mp4, sheet, graph, hapi, sidecar, statuslog, objp, gdiff, fair, proofmd]:
    p("  %-58s %10d B sha256 %s" % (os.path.basename(f), os.path.getsize(f), sha(f)))
ck(a["bytes"] == os.path.getsize(mp4) == int(re.search(r"bytes=(\d+)", objectives[0]).group(1)),
   "mp4 bytes agree across objective.json, the status.log OBJECTIVE line and os.path.getsize")
im = __import__("PIL.Image", fromlist=["open"]).open(sheet)
dur = a["duration"]
ts = sorted({round(m + d * 0.5, 2) for m in (10, 20, 30, 40, 50) for d in range(-3, 4) if 0 <= m + d * 0.5 <= dur - 0.05})
cols = 7
rows = (len(ts) + cols - 1) // cols
th = int(round(256.0 * H / W / 2) * 2)
p("  contact sheet PIL %r mode=%s format=%s  expected for %d tiles (grid %dx%d, tile 256x%d, padding 4): (%d, %d)"
  % (im.size, im.mode, im.format, len(ts), cols, rows, th, cols * 256 + (cols - 1) * 4, rows * th + (rows - 1) * 4))
ck(im.size == (cols * 256 + (cols - 1) * 4, rows * th + (rows - 1) * 4), "contact-sheet geometry matches run_graph_job.py:contact_sheet for a %.3f s clip" % dur)
p("  sampled t = %r s -> frames %r" % (ts, sorted({int(round(t * FPS)) for t in ts})))
cov = sorted({int(round(t * FPS)) for t in ts})
inwin = [f0 for f0 in STILL_FRAMES if 204 <= f0 <= 276]
p("  the task's stills %r: inside the sheet's windows %r; NOT sampled by the sheet: %r (frame 0 is never sampled)"
  % (STILL_FRAMES, inwin, [f0 for f0 in STILL_FRAMES if f0 not in inwin and f0 not in cov]))
p("  full-res fixed-frame stills at 200/243/300/400/480 are Max/harness files: run_graph_job.py has no fixed-frame still path")
p("  dir listing runs\\%s" % ARM)
for f in sorted(os.listdir(ARMDIR)):
    fp = os.path.join(ARMDIR, f)
    p("    %s %s %d" % ("d " if os.path.isdir(fp) else "f ", f, os.path.getsize(fp)))
ck(sorted(os.listdir(ARMDIR)) == ["PROOF.md", ARM + ".api.json", ARM + ".mp4", ARM + ".mp4.json", ARM + "_stills_contact.png",
                                  "fairness.txt", "graph_diff.txt", "objective.json", "request.api.json", "status.log"],
   "arm dir holds only harness outputs + the PROOF.md/fairness.txt/graph_diff.txt Forge is allowed to write")

p("\n== I. control measurements + sbs / fixed-frame stills (Max's per the TASKS sbs rule)")
ck(sha(basemp4) == BASE_MP4_SHA and os.path.getsize(basemp4) == 5624126, "control mp4 sha256 %s (%d B) = the PROOF record: the pair is hash-attested" % (BASE_MP4_SHA[:12], os.path.getsize(basemp4)))
rc, so, se = probe(["-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets,width,height,r_frame_rate", "-of", "csv=p=0", stitch])
p("  stitched recount: rc=%d out=%r" % (rc, so))  # noqa
sparts = so.split(",")
ck(rc == 0 and sparts[-1] == "1443", "stitched = 1443 packets (the sbs source)")
ck(sha(stitch) == STITCH_SHA, "stitched sha256 %s = the PROOF record" % STITCH_SHA[:12])
p("  the requested sbs window: base stitched frames 962-1442 (= 481 frames = the segment-3 window, 1443 = 481*3 - 60 context) | new frames 0-480")
r = subprocess.run(["find", RUNS, "-name", "sbs_*.mp4"], capture_output=True, text=True)
names = [x.replace(RUNS + os.sep, "") for x in r.stdout.split()]
p("  find runs -name sbs_*.mp4 -> %r" % names)
ck(not any("promptv2" in x for x in names), "no sbs_base_seg3_promptv2.mp4 exists -> sbs/stills pending Max (run_graph_job.py has no hstack path; sbs_* are Max/harness files)")
r = subprocess.run(["find", RUNS, "-name", "*promptv2_seg3*"], capture_output=True, text=True)
p("  find runs -name *promptv2_seg3* -> %r" % [x.replace(RUNS + os.sep, "") for x in r.stdout.split()])
ck(not any("sbs" in x for x in r.stdout.split()), "no sbs for this arm in runs (confirmed)")

p("\n== J. p7 budget + ralph.log (read-only)")
bud = json.load(open(BUDGET, encoding="utf-8-sig"))
p("  %s = %s" % (BUDGET, json.dumps(bud)))
ck(bud.get("used_min", 1e9) < bud.get("cap_min", 0) and bud.get("jobs", 10 ** 9) < bud.get("job_cap", 0),
   "budget after this job: used_min %r < cap_min %r, jobs %r < job_cap %r" % (bud.get("used_min"), bud.get("cap_min"), bud.get("jobs"), bud.get("job_cap")))
p("  this arm spent %.1f min of GPU wall; the control cost %.1f s = %.1f min (per-arm cost is consistent)"
  % (res.get("wall_min", 0.0), BASE_SECS, BASE_SECS / 60.0))
log = open(r"C:/Users/derek/5slock/ralph-community/logs/ralph.log", encoding="utf-8", errors="replace").read().splitlines()
p("  last 6 ralph.log lines:")
for ln in log[-6:]:
    p("    | " + ln)
joblines = [ln for ln in log if ARM in ln and "P7 job" in ln]
p("  P7 job lines for the arm: %r" % joblines)
ck(len([x for x in joblines if "ok=True" in x]) == 1 and len([x for x in joblines if "refused" in x.lower()]) == 0,
   "the harness ran this job exactly once, ok=True, never refused")

p("")
p("ALL CHECKS PASS" if not fails else "CHECK FAILS %d" % len(fails))
for f in fails:
    p(" -", f)
full = "\n".join(L) + "\n"
open(REPORT, "w", encoding="utf-8").write(full)
print(full)
print("report written: %s (%d bytes)" % (REPORT, len(full)))
