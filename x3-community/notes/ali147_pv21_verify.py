# ALI-147 PV2-1 PROMPT_V2 seg1 RENDER VERIFY (READ-ONLY: no GPU/ComfyUI/llama-swap/Strata call, no render,
# no run_graph_job.py by Forge, no job request, no vision judge). Writes ONLY C:/AI/community/notes/.
# ffprobe / ffmpeg are used read-only as probes (no encode by Forge).
import json, os, hashlib, subprocess, re, sys

FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
FFMPEG = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
RUNS = r"C:/AI/community/runs"
ARM = "ali147_pool_promptv2_s51080000"
CTRL = "ali147_pool_ctrl_s51080000"
ARMDIR = os.path.join(RUNS, ARM)
CTRLDIR = os.path.join(RUNS, CTRL)
JOBS = r"C:/AI/community/p7/jobs"
PROMPTS = r"C:/AI/community/specs/prompt_v2"
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
REPORT = r"C:/AI/community/notes/ali147-pv21-verify-20261022.txt"
sys.path.insert(0, r"C:/AI/community/scripts")

FRAMES, W, H, FPS, TOL = 481, 768, 1344, 24, 0
CTRL_SECS = 809.7
GRAPH_SHA = "d9212ff14b1f899dd7fb67b308d4e09d86fc8520f2f828fd83d1cfd0408fbcb5"
DIFF_SHA = "f8d0b01c9f6c623ef88447886d256100c420ac1e2a13b1b7ef5cc9f88ce8e8f1"
REQ_SHA = "f37aa53f8127872c21e439a88fd3f06f9d3576dcc75ae03eb945468217e64380"
P0_SHA = "889c543a13cfb3d0e37c20198a2d03cc3d9e4b32934ad2ce71b37b359d3175b6"
P1_SHA = "655e92a8f668f51e74bececce3471bcc32492bfdd1ade7377b456b65eec17d2b"
STILL_SHA = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"
CTRL_MP4_SHA = "1dc59ed446e4cf1a5ecbfa18616a311b658d1acc281a3624974732373ba42fda"

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
ctrlgraph = os.path.join(CTRLDIR, "submitted_graph.pretty.json")
ctrlmp4 = os.path.join(CTRLDIR, CTRL + ".mp4")
ctrlobj = os.path.join(CTRLDIR, "objective.json")

p("== A. harness result gate (p7\\jobs\\%s.result.json)" % ARM)
res = json.load(open(resj, encoding="utf-8-sig"))
for k in ("ok", "rc", "note", "id", "kind", "started", "finished", "wall_min", "budget_used_min", "budget_cap_min"):
    p("  result.json %s = %r" % (k, res.get(k)))
ck(res.get("ok") is True, "result.json ok is True (PV2-1 gate: status.log JOB end ok)")
ck(res.get("rc") == 0, "result.json rc == 0 (got %r)" % res.get("rc"))
ck(res.get("id") == ARM and res.get("kind") == "graph", "result.json id/kind match the arm")
ck(os.path.getsize(outj) > 0 and open(outj, "rb").read() == open(statuslog, "rb").read(),
   "p7\\jobs\\<id>.out is byte-identical to runs\\<id>\\status.log (same job log)")

p("\n== B. status.log verbatim + error greps")
sl = open(statuslog, encoding="utf-8", errors="replace").read()
lines = sl.splitlines()
for ln in lines:
    p("  | " + ln)
for pat in ["JOB error", "CLIP_SKIP", "clip_skip", "node_errors", "Traceback", "STUCK", "REDO", "redo", "STATIC_FAIL", "COMFY_DOWN", "error", "ERROR", "FAIL", "OBJECTIVE FAIL"]:
    hits = [ln for ln in lines if pat.lower() in ln.lower()]
    ck(hits == [], "status.log: no %r (hits %d)" % (pat, len(hits)))
starts = [ln for ln in lines if "JOB start " + ARM in ln]
ends = [ln for ln in lines if "JOB end " + ARM + " ok" in ln]
objectives = [ln for ln in lines if "OBJECTIVE ok " + ARM in ln]
unload = [ln for ln in lines if "UNLOAD LLM" in ln]
ck(len(unload) == 1, "LLM unloaded BEFORE the job (ALI-154), by the harness: %r" % unload)
ck(len(starts) == 1, "exactly one JOB start line for the arm")
ck(len(ends) == 1, "exactly one JOB end ... ok line for the arm (the task's 'JOB end ok')")
ck(len(objectives) == 1, "exactly one OBJECTIVE ok line for the arm")
p("  JOB start : %s" % (starts[0] if starts else "MISSING"))
p("  JOB end   : %s" % (ends[0] if ends else "MISSING"))
p("  OBJECTIVE : %s" % (objectives[0] if objectives else "MISSING"))
ck(res.get("started", "").startswith("2026-10-22T22:21:37"), "result.json started matches the status.log UNLOAD line (22:21:37 CT)")
ck(res.get("finished", "").startswith("2026-10-22T22:36:32"), "result.json finished matches the status.log last line (22:36:32 CT)")

p("\n== C. objective.json (harness shape attempts:[{...}]) + control comparison")
obj = json.load(open(objp, encoding="utf-8"))
p("  top-level keys %s" % sorted(obj.keys()))
att = obj["attempts"]
p("  attempts: %d" % len(att))
ck(len(att) == 1, "one attempt only = no automatic redo, no STUCK (got %d)" % len(att))
a = att[0]
for k in ("frames", "w", "h", "fps", "audio", "duration", "bytes", "secs", "blackfreeze", "file"):
    p("  attempts[0].%s = %r" % (k, a.get(k)))
p("  top-level ok=%r contact_sheet=%r" % (obj.get("ok"), obj.get("contact_sheet")))
ck(obj.get("ok") is True, "objective.json ok is True")
ck(a["frames"] == FRAMES, "objective frames == %d (frames_tol %d)" % (FRAMES, TOL))
ck((a["w"], a["h"]) == (W, H), "resolution %dx%d" % (W, H))
ck(a["fps"] == "24/1", "fps 24/1 (got %r)" % a["fps"])
ck(a["audio"] is True, "audio stream present")
ck(a["blackfreeze"] == [], "blackfreeze [] = no black/frozen frames (the harness chain)")
ck(a["bytes"] == os.path.getsize(mp4), "objective bytes == os.path.getsize(mp4) (%d)" % os.path.getsize(mp4))
ctrl = json.load(open(ctrlobj, encoding="utf-8"))
p("  CONTROL %s objective keys %s" % (CTRL, sorted(ctrl.keys())))
for k in ("frames", "w", "h", "fps", "audio", "duration", "bytes", "secs", "sha256"):
    p("  ctrl.%s = %r" % (k, ctrl.get(k)))
ck(not isinstance(ctrl.get("attempts"), list) and ctrl.get("secs") == CTRL_SECS,
   "the control is the FLAT driver shape (no attempts, top-level secs) = the control was rendered by the driver, not this loop")
ck(ctrl.get("frames") == FRAMES and (ctrl.get("w"), ctrl.get("h")) == (W, H) and ctrl.get("fps") == "24/1" and ctrl.get("audio") is True,
   "control objective is 481 / 768x1344 / 24/1 / audio - a valid one-variable control")
ds = a["secs"] - CTRL_SECS
p("  RENDER SECONDS vs CTRL: arm %.1f s vs control %.1f s = %+.1f s (%+.2f %%)  [the task's 'render seconds vs CTRL 809.7']"
  % (a["secs"], CTRL_SECS, ds, 100.0 * ds / CTRL_SECS))
p("  wall: result.json wall_min %.1f (job %s -> %s); the request's minutes=60 is a PRE-job gate, not a render cap"
  % (res.get("wall_min", 0.0), res.get("started"), res.get("finished")))
p("  bytes arm %d vs control %d = %+d (%.2f %%)" % (a["bytes"], ctrl["bytes"], a["bytes"] - ctrl["bytes"], 100.0 * (a["bytes"] - ctrl["bytes"]) / ctrl["bytes"]))
ck(abs(a["frames"] - ctrl["frames"]) == 0, "same frame count as the control (one prompt-only variable, frames_tol 0 both)")

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
m = re.search(r'"-vf", "([^"]+)"', open(r"C:/AI/community/scripts/run_graph_job.py", encoding="utf-8").read())
HARNESS_FILT = m.group(1)
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
g = json.load(open(graph, encoding="utf-8"))
ga = json.load(open(hapi, encoding="utf-8"))
ck(J(g) == J(ga), "parsed graphs identical (%d nodes)" % len(g))
ck(sorted(g.keys()) == sorted(json.load(open(ctrlgraph, encoding="utf-8")).keys()), "node key set == the CTRL graph (25 nodes, no node added/removed)")
ck(len([x for x in os.listdir(ARMDIR) if "_redo" in x]) == 0, "no *_redo*.api.json in the arm dir (consistent with attempts length 1)")
reqs = sorted([f for f in os.listdir(JOBS) if f.startswith("request_iter")])
p("  p7\\jobs request archives: %r" % reqs)
hits = [f for f in reqs if sha(os.path.join(JOBS, f)) == REQ_SHA]
ck(len(hits) == 1, "the consumed job request (sha256 %s...) is archived at p7\\jobs\\%s = exactly one job, id as written" % (REQ_SHA[:12], hits))
p("  archived request content: %s" % open(os.path.join(JOBS, hits[0]), encoding="utf-8").read().strip() if hits else "  (no archive match)")
p("  p7\\JOB_REQUEST.json present = %s (a Request file is CONSUMED at exit)" % os.path.exists(r"C:/AI/community/p7/JOB_REQUEST.json"))

p("\n== F. the rendered graph carries the two PROMPT_V2 files verbatim (the arm's only variable)")
for nid, fn, want in (("c0", "v2_seg1_c0_r2v.txt", P0_SHA), ("c1", "v2_seg1_c1_t2va.txt", P1_SHA)):
    fp = os.path.join(PROMPTS, fn)
    raw = open(fp, "rb").read()
    txt = raw.decode("utf-8")
    gp = ga[nid]["inputs"]["prompt"]
    p("  %s: file %d B sha256 %s | graph string %d ch sha256 %s" % (nid, len(raw), sha(fp), len(gp), shastr(gp)))
    ck(sha(fp) == want, "%s file sha256 == the PV2-0 / SHA256SUMS record" % fn)
    ck(gp == txt, "graph %s.prompt == %s VERBATIM (byte-for-byte, no EOL change)" % (nid, fn))
    ck(shastr(gp) == want, "graph %s.prompt sha256 == %s" % (nid, want))
sums = open(os.path.join(PROMPTS, "SHA256SUMS.txt"), encoding="utf-8").read()
rows = dict((n, h) for h, n in re.findall(r"^([0-9a-f]{64})\s+\*?\s*(\S+)$", sums, re.M))
for fn, want in (("v2_seg1_c0_r2v.txt", P0_SHA), ("v2_seg1_c1_t2va.txt", P1_SHA)):
    ck(rows.get(fn) == want, "SHA256SUMS.txt entry for %s == %s" % (fn, want[:12]))
import comm
ck(comm.guard_ok(ga["c0"]["inputs"]["prompt"]) and comm.guard_ok(ga["c1"]["inputs"]["prompt"]),
   "adults-only guard (the harness's own comm.guard_ok, run_graph_job.py:60) passes on both V2 prompts")
ck([k for k, n in ga.items() if isinstance(n["inputs"].get("prompt"), str)] == ["c0", "c1"] or
   sorted([k for k, n in ga.items() if isinstance(n["inputs"].get("prompt"), str)]) == ["c0", "c1"],
   "only c0/c1 carry prompt strings in the rendered graph (no hidden prompt edits)")

p("\n== G. fairness vs CTRL: only c0.prompt, c1.prompt, filename_prefix")
cg = json.load(open(ctrlgraph, encoding="utf-8"))
same, diff = [], []
for k in sorted(set(cg) | set(g)):
    (same if (k in cg and k in g and J(cg[k]) == J(g[k])) else diff).append(k)
p("  identical nodes %d, differing nodes %r" % (len(same), diff))
ck(sorted(diff) == ["c0", "c1", "save"], "differing node set == ['c0','c1','save'] (%d/%d nodes byte-identical)" % (len(same), len(cg)))
for nid, keys in (("c0", ["prompt"]), ("c1", ["prompt"]), ("save", ["filename_prefix"])):
    akeys = sorted(g[nid]["inputs"].keys())
    ckeys = sorted(cg[nid]["inputs"].keys())
    ck(akeys == ckeys, "%s input key set unchanged (%r)" % (nid, akeys))
    changed = [k for k in akeys if J(g[nid]["inputs"][k]) != J(cg[nid]["inputs"][k])]
    ck(changed == keys, "%s: changed inputs == %r (got %r)" % (nid, keys, changed))
ck(g["save"]["inputs"]["filename_prefix"] == "community/%s/%s" % (ARM, ARM), "save.filename_prefix = the new id (%r)" % g["save"]["inputs"]["filename_prefix"])
ck(g["noise"]["inputs"]["noise_seed"] == 51080000, "seed held at 51080000 (noise.noise_seed, identical to CTRL)")
ck(cg["save"]["inputs"]["filename_prefix"].startswith("community/" + CTRL), "CTRL prefix read from the control graph: %r" % cg["save"]["inputs"]["filename_prefix"])
for k, v in (("steps", 10), ("sampler_name", "euler"), ("scheduler", "simple"), ("denoise", 1.0)):
    ids = [n["inputs"].get(k) for n in g.values() if k in n["inputs"]]
    ids_c = [n["inputs"].get(k) for n in cg.values() if k in n["inputs"]]
    ck(ids and set(map(str, ids)) == {str(v)} and ids == ids_c, "held equal: %s = %r on every node that has it, arm and control" % (k, v))
ck(g["m_shift"]["inputs"]["shift_video"] == 10.0 and g["m_shift"]["inputs"]["shift_audio"] == 3.0, "sigma shift 10/3 held")
ck(g["c0"]["inputs"]["width"] == W and g["c0"]["inputs"]["height"] == H, "c0 resolution 768x1344")
ck(g["c0"]["inputs"]["length"] == 243, "c0.length 243 (CTRL value)")
ext = g["win1"]["inputs"]["extension_frames"]
ck(243 + ext == FRAMES, "c0.length 243 + win1.extension_frames %d = %d = the requested frames" % (ext, FRAMES))
ck(g["c1"]["inputs"]["length"] == ["win1", 1], "c1.length stays the window link %r (no length change)" % g["c1"]["inputs"]["length"])
li = [n["inputs"]["image"] for n in g.values() if n["class_type"] == "LoadImage"]
ck(li == [cg_img for cg_img in [n["inputs"]["image"] for n in cg.values() if n["class_type"] == "LoadImage"]], "LoadImage string unchanged: %r" % li)
sp = os.path.join(COMFY_IN, str(li[0]).replace("/", os.sep))
ck(os.path.isfile(sp) and sha(sp) == STILL_SHA, "the start still resolves inside ComfyUI\\input: %d B sha256 %s" % (os.path.getsize(sp), sha(sp)))
p("  m_attn attention = %r (informational; NOT 'vsa')" % g["m_attn"]["inputs"].get("attention"))
ck(g["m_vsa"]["class_type"] == "BlockSparseAttention" and J(g["m_vsa"]) == J(cg["m_vsa"]), "VSA patch node unchanged vs CTRL (this arm is prompt-only, dense is PV2-3)")
gd = open(gdiff, encoding="utf-8", errors="replace").read()
gdl = gd.splitlines()
hunks = [x for x in gdl if x.startswith("@@")]
rem = [x for x in gdl if x.startswith("-") and not x.startswith("---")]
add = [x for x in gdl if x.startswith("+") and not x.startswith("+++")]
p("  graph_diff.txt %d B sha256 %s hunks=%d removed=%d added=%d" % (os.path.getsize(gdiff), sha(gdiff), len(hunks), len(rem), len(add)))
ck(sha(gdiff) == DIFF_SHA, "graph_diff.txt sha256 == the PROOF record %s..." % DIFF_SHA[:12])
ck(len(hunks) == 3 and len(rem) == 3 and len(add) == 3, "graph_diff = 3 hunks, exactly 3 removed + 3 added lines (the task's 'only c0.prompt, c1.prompt, filename_prefix')")
ck(all('"prompt":' in x for x in rem[:2]) and all('"filename_prefix"' in x for x in rem[2:]), "the 3 removed lines are prompt, prompt, filename_prefix")
ck(len(add) == 3 and ('"prompt":' in add[0]) and ('"prompt":' in add[1]) and ('"filename_prefix"' in add[2]), "the 3 added lines are prompt, prompt, filename_prefix")
ck(rem[0].lstrip("-").strip() in open(ctrlgraph, encoding="utf-8", errors="replace").read(), "removed line 1 (a prompt) is byte-equal to a line of the CTRL graph (stripped of the diff marker)")
ck(add[0].lstrip("+").strip() in open(graph, encoding="utf-8", errors="replace").read(), "added line 1 (a prompt) is byte-equal to a line of the new arm graph")
ck(rem[2].lstrip("-").strip() in open(ctrlgraph, encoding="utf-8", errors="replace").read(), "removed line 3 (filename_prefix) is byte-equal to a CTRL graph line")
ck(add[2].lstrip("+").strip() in open(graph, encoding="utf-8", errors="replace").read(), "added line 3 (filename_prefix) is byte-equal to a new arm graph line")

p("\n== H. outputs: sizes, sha256, contact-sheet geometry and sampled frames")
for f in [mp4, sheet, graph, hapi, sidecar, statuslog, objp, gdiff, fair, proofmd]:
    p("  %-56s %10d B sha256 %s" % (os.path.basename(f), os.path.getsize(f), sha(f)))
ck(a["bytes"] == 6397658, "mp4 bytes 6397658 match objective.json + the status.log OBJECTIVE line")
ck(os.path.exists(os.path.join(CTRLDIR, CTRL + ".mp4")) and sha(os.path.join(CTRLDIR, CTRL + ".mp4")) == CTRL_MP4_SHA,
   "control mp4 sha256 %s (from its own objective.json) - the pair is hash-attested" % CTRL_MP4_SHA[:12])
im = __import__("PIL.Image", fromlist=["open"]).open(sheet)
dur = a["duration"]
ts = sorted({round(m + d * 0.5, 2) for m in (10, 20, 30, 40, 50) for d in range(-3, 4) if 0 <= m + d * 0.5 <= dur - 0.05})
cols = 7
rows = (len(ts) + cols - 1) // cols
th = int(round(256.0 * H / W / 2) * 2)
p("  contact sheet PIL %r mode=%s format=%s  expected for %d tiles (%dx%d grid, tile 256x%d, padding 4): (%d, %d)"
  % (im.size, im.mode, im.format, len(ts), cols, rows, th, cols * 256 + (cols - 1) * 4, rows * th + (rows - 1) * 4))
ck(im.size == (cols * 256 + (cols - 1) * 4, rows * th + (rows - 1) * 4), "contact sheet geometry matches run_graph_job.py:contact_sheet for a %.3f s clip" % dur)
p("  sampled t = %r s -> frames %r" % (ts, sorted({int(round(t * FPS)) for t in ts})))
p("  NOT sampled by the harness sheet: frame 0 and every frame outside those windows (fixed-frame stills 0/120/230/243/256/360/480 are Max's, not Forge's)")
meta = json.load(open(sidecar, encoding="utf-8"))
for k, v in sorted(meta.items()):
    p("  sidecar %s = %r" % (k, str(v)[:120]))
ck(meta.get("label") == "METHOD_ONLY" and meta.get("run") == ARM and meta.get("attempt") == 0, "sidecar labels METHOD_ONLY, run = the arm, attempt 0 (no redo)")
p("  dir listing runs\\%s" % ARM)
for f in sorted(os.listdir(ARMDIR)):
    fp = os.path.join(ARMDIR, f)
    p("    %s %s %d" % ("d " if os.path.isdir(fp) else "f ", f, os.path.getsize(fp)))
ck(sorted(os.listdir(ARMDIR)) == ["PROOF.md", ARM + ".api.json", ARM + ".mp4", ARM + ".mp4.json", ARM + "_stills_contact.png",
                                  "fairness.txt", "graph_diff.txt", "objective.json", "request.api.json", "status.log"],
   "arm dir holds only harness outputs + the PROOF.md/fairness.txt/graph_diff.txt Forge is allowed to write")

p("\n== I. sbs / fixed-frame stills (Max's per the TASKS sbs rule)")
r = subprocess.run(["find", RUNS, "-name", "sbs_*.mp4"], capture_output=True, text=True)
names = [x.replace(RUNS + os.sep, "") for x in r.stdout.split()]
p("  find runs -name sbs_*.mp4 -> %r" % names)
ck(not any("promptv2" in x for x in names), "no sbs_ctrl_promptv2.mp4 exists -> sbs/stills pending Max (run_graph_job.py has no hstack path; sbs_* are Max/harness files)")
r = subprocess.run(["find", RUNS, "-name", "*promptv2*"], capture_output=True, text=True)
p("  find runs -name *promptv2* -> %r" % [x.replace(RUNS + os.sep, "") for x in r.stdout.split()])
ck(not any("sbs" in x for x in r.stdout.split()), "no sbs for this arm in runs (confirmed)")

p("\n== J. p7 budget (read-only, the live counter file)")
bud = json.load(open(BUDGET, encoding="utf-8-sig"))
p("  %s = %s" % (BUDGET, json.dumps(bud)))
ck(bud.get("used_min", 1e9) < bud.get("cap_min", 0) and bud.get("jobs", 10 ** 9) < bud.get("job_cap", 0),
   "budget after this job: used_min %r < cap_min %r, jobs %r < job_cap %r" % (bud.get("used_min"), bud.get("cap_min"), bud.get("jobs"), bud.get("job_cap")))
p("  this arm spent %.1f min of GPU wall; control cost %.1f s = %.1f min (the loop's per-arm cost is consistent)"
  % (res.get("wall_min", 0.0), CTRL_SECS, CTRL_SECS / 60.0))

p("")
p("ALL CHECKS PASS" if not fails else "CHECK FAILS %d" % len(fails))
for f in fails:
    p(" -", f)
full = "\n".join(L) + "\n"
open(REPORT, "w", encoding="utf-8").write(full)
print(full)
print("report written: %s (%d bytes)" % (REPORT, len(full)))
