# ALI-147 FIX4_PROOF verify (READ-ONLY: no GPU, no ComfyUI/llama-swap call, no render, no job request;
# writes ONLY C:/AI/community/notes/. Runs ffprobe (read-only probe) and `git rev-parse HEAD` on the Extender.)
import json, os, hashlib, subprocess, re

FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
FFMPEG = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
RUNS = r"C:/AI/community/runs"
ARM = "ali147_pool_fix4_s51080000"
ARMDIR = os.path.join(RUNS, ARM)
BASEDIR = os.path.join(RUNS, "p7_r2_c3_pmot_full_pool")
JOBS = r"C:/AI/community/p7/jobs"
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
EXTDIR = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes/ComfyUI_MiniMax_H3_Extender"
REPORT = r"C:/AI/community/notes/ali147-fix4-proof-verify-20261022.txt"
TARGET, TOL, CTX, FPS = 1443, 24, 22, 24
CLIP_FRAMES = [243, 260, 260, 260, 260, 260]
PROMPT_SHA = ["7b4b22bb170fbcb85dce706ef746a862d49fa14142c1a704a672d4819b77f889",
              "49c94ba7759859e26af01dff17230b80a834fa4b1ff57bcaac332cf40c655045",
              "1f37321ff13763cd836f5eaa282f93dfc20d98f49be77609a632d51e865c6815",
              "dcf5579f6cd2a04bce2d78da4aa19b35c89129b2feb07e50d202c713e1e08a11",
              "8ed332629e80a8702f11eb4eb996e5a42fe3ee5f716168d25512ae01d7df5d76",
              "d7d29ad985a7a43232f65879ea2c1c75317b6b0c803d95ede9bd26a1e78bc0e3"]
STILL_SHA = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"
EXT_COMMIT = "0861230"
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


def probe(args, exe=FFPROBE, level="error"):
    r = subprocess.run([exe, "-v", level] + args, capture_output=True, text=True)
    return (r.returncode, r.stdout.strip(), r.stderr.strip())


mp4 = os.path.join(ARMDIR, ARM + ".mp4")
sheet = os.path.join(ARMDIR, ARM + "_stills_contact.png")
statuslog = os.path.join(ARMDIR, "status.log")
objp = os.path.join(ARMDIR, "objective.json")
graph = os.path.join(ARMDIR, "request.api.json")
harness_api = os.path.join(ARMDIR, ARM + ".api.json")
resj = os.path.join(JOBS, ARM + ".result.json")
outj = os.path.join(JOBS, ARM + ".out")

p("== A. harness result gate")
res = json.load(open(resj, encoding="utf-8-sig"))
for k in ("ok", "rc", "note", "id", "kind", "started", "finished", "wall_min", "budget_used_min", "budget_cap_min"):
    p("  result.json %s = %r" % (k, res.get(k)))
ck(res.get("ok") is True, "result.json ok is True (FIX4_PROOF gate)")
ck(res.get("rc") == 0, "result.json rc == 0 (got %r)" % res.get("rc"))
ck(res.get("id") == ARM and res.get("kind") == "graph", "result.json id/kind match the arm")
ck(os.path.getsize(outj) > 0, "p7\\jobs\\%s.out is non-empty (%d bytes)" % (ARM, os.path.getsize(outj)))
same_out = open(outj, "rb").read() == open(statuslog, "rb").read()
ck(same_out, "p7\\jobs\\<id>.out is byte-identical to runs\\<id>\\status.log (same job log, copied)")

p("\n== B. status.log verbatim + error greps")
sl = open(statuslog, encoding="utf-8", errors="replace").read()
lines = sl.splitlines()
for ln in lines:
    p("  | " + ln)
for pat in ["JOB error", "CLIP_SKIP", "clip_skip", "node_errors", "Traceback", "STUCK", "redo", "error", "ERROR", "FAIL"]:
    hits = [ln for ln in lines if pat.lower() in ln.lower()]
    ck(hits == [], "status.log: no %r (hits %d)" % (pat, len(hits)))
ck(len([ln for ln in lines if "JOB start " + ARM in ln]) == 1, "exactly one JOB start line for the arm")
ck(len([ln for ln in lines if "JOB end " + ARM + " ok" in ln]) == 1, "exactly one JOB end ... ok line for the arm")
ck(len([ln for ln in lines if "OBJECTIVE ok " + ARM in ln]) == 1, "exactly one OBJECTIVE ok line for the arm")
starts = [ln for ln in lines if "JOB start " + ARM in ln]
ends = [ln for ln in lines if "JOB end " + ARM in ln]
objective = [ln for ln in lines if "OBJECTIVE ok " + ARM in ln]
p("  JOB start line: %s" % (starts[0] if starts else "MISSING"))
p("  JOB end   line: %s" % (ends[0] if ends else "MISSING"))
p("  OBJECTIVE line: %s" % (objective[0] if objective else "MISSING"))
ck(res.get("started", "").startswith("2026-10-22T20:08:29"), "result.json started matches status.log UNLOAD line (20:08:29 CT)")
ck(res.get("finished", "").startswith("2026-10-22T20:59:15"), "result.json finished matches status.log last line (20:59:15 CT)")

p("\n== C. objective.json")
obj = json.load(open(objp, encoding="utf-8"))
p("  top-level keys %s" % sorted(obj.keys()))
att = obj["attempts"]
p("  attempts: %d" % len(att))
ck(len(att) == 1, "one attempt only: no redo, no STUCK (got %d)" % len(att))
a = att[0]
for k in ("frames", "w", "h", "fps", "audio", "duration", "bytes", "secs", "blackfreeze", "file"):
    p("  attempts[0].%s = %r" % (k, a.get(k)))
p("  top-level ok=%r contact_sheet=%r" % (obj.get("ok"), obj.get("contact_sheet")))
ck(obj.get("ok") is True, "objective.json ok is True")
ck(a["frames"] == 1433, "objective frames == 1433 (got %r)" % a["frames"])
ck(abs(a["frames"] - TARGET) <= TOL, "|%d - %d| = %d <= frames_tol %d" % (a["frames"], TARGET, abs(a["frames"] - TARGET), TOL))
ck((a["w"], a["h"]) == (768, 1344), "resolution 768x1344 (got %sx%s)" % (a["w"], a["h"]))
ck(a["fps"] == "24/1", "fps 24/1 (got %r)" % a["fps"])
ck(a["audio"] is True, "audio present")
ck(a["blackfreeze"] == [], "blackfreeze [] (no black/frozen frames detected by the harness blackdetect+freezedetect)")
ck(a["bytes"] == os.path.getsize(mp4), "objective bytes == os.path.getsize(mp4) (%d)" % os.path.getsize(mp4))
ck(a["secs"] == 3004.9, "render secs recorded (%r s = %.1f min) - over the 180 min job cap: see the NOTE line" % (a["secs"], a["secs"] / 60.0))
p("  NOTE the requested job budget was minutes=180; the render took 3004.9 s = 50.1 min of JOB time, wall_min 50.8; the budget gate is checked BEFORE the job (used_min 276.3 -> 327.1 of cap 390, jobs 22 -> 23 of 27)")

p("\n== D. independent ffprobe recount (read-only, this iteration)")
rc, so, se = probe(["-select_streams", "v:0", "-count_packets",
                    "-show_entries", "stream=nb_read_packets,r_frame_rate,width,height,avg_frame_rate", "-of", "csv=p=0", mp4])
p("  video: rc=%d out=%r err=%r" % (rc, so, se))
parts = so.split(",")
vid_frames = int(parts[-1])
ck(rc == 0 and vid_frames == 1433, "ffprobe -count_packets video packets = %d (independent recount of the 1433)" % vid_frames)
ck(parts[0] == "768" and parts[1] == "1344", "ffprobe width/height 768x1344")
ck("24/1" in parts, "ffprobe r_frame_rate 24/1")
rc, so, se = probe(["-show_entries", "stream=index,codec_type,codec_name,channels,sample_rate,duration,nb_frames", "-of", "csv=p=0", mp4])
p("  streams: rc=%d out=%r" % (rc, so))
sa = [x for x in so.splitlines() if ",audio," in x]
ck(len(sa) == 1, "exactly one audio stream (%r)" % sa)
rc, so, se = probe(["-v", "error", "-show_entries", "format=duration,size", "-of", "csv=p=0", mp4])
p("  format: %s" % so)
rc, so, se = probe(["-i", mp4, "-vf", "blackdetect=d=0.2:pix_th=0.10", "-an", "-f", "null", "NUL"], FFMPEG, "info")
bl = [x.strip() for x in se.splitlines() if "blackdetect" in x]
p("  blackdetect events: %r" % bl)
p("  (read-only full decode, rc=%d, stderr lines=%d)" % (rc, len(se.splitlines())))
ck(bl == [], "own blackdetect probe (d=0.2 pix_th=0.10): no black-frame intervals; the gate is objective.json blackfreeze []")
# the harness's own filter chain, copied verbatim out of scripts/run_graph_job.py:43 (read here, not edited)
m = re.search(r'"-vf", "([^"]+)"', open(r"C:/AI/community/scripts/run_graph_job.py", encoding="utf-8").read())
HARNESS_FILT = m.group(1)
p("  harness filter chain (run_graph_job.py:43) = %r" % HARNESS_FILT)
rc, so, se = probe(["-i", mp4, "-vf", HARNESS_FILT, "-an", "-f", "null", "NUL"], FFMPEG, "info")
hv = [x.strip() for x in se.splitlines() if "blackdetect" in x or "freezedetect" in x]
p("  harness-chain events: %r (rc=%d)" % (hv, rc))
ck(hv == [], "re-running the harness's own blackdetect=d=1.0:pix_th=0.10,freezedetect=n=-60dB:d=2 chain on the mp4 gives 0 events = objective.json blackfreeze [] is reproducible")
rc, so, se = probe(["-i", mp4, "-vf", "freezedetect=n=0.005:d=0.5", "-an", "-f", "null", "NUL"], FFMPEG, "info")
fz = [x.strip() for x in se.splitlines() if "freezedetect" in x]
p("  stricter freezedetect (n=0.005 d=0.5) events: %r (rc=%d)" % (fz, rc))
ck(fz == [], "own stricter freezedetect probe: no frozen-frame intervals of 0.5 s or longer")

p("\n== E. provenance: the graph that rendered")
grb = open(graph, "rb").read()
hab = open(harness_api, "rb").read()
p("  request.api.json bytes %d sha256 %s" % (len(grb), sha(graph)))
p("  %s.api.json bytes %d sha256 %s" % (ARM, len(hab), sha(harness_api)))
ck(hab == grb[:len(hab)], "%s.api.json is a byte-exact prefix of request.api.json (tail = %r)" % (ARM, grb[len(hab):]))
ga = json.load(open(harness_api, encoding="utf-8"))
g = json.load(open(graph, encoding="utf-8"))
ck(J(ga) == J(g), "parsed graphs are identical (13 nodes), so the submitted graph is the one Forge wrote")

p("\n== F. Extender commit (read-only git rev-parse in the installed custom_nodes folder)")
r = subprocess.run(["git", "-C", EXTDIR, "rev-parse", "HEAD"], capture_output=True, text=True)
head = r.stdout.strip()
p("  git -C %s rev-parse HEAD -> rc=%d %s" % (EXTDIR, r.returncode, head))
ck(r.returncode == 0 and head.startswith(EXT_COMMIT), "Extender HEAD starts with %s (spec pins 0861230 / v3.0.13)" % EXT_COMMIT)
ver = [f for f in ("VERSION", "version.txt", "__init__.py") if os.path.exists(os.path.join(EXTDIR, f))]
for f in ver:
    txt = open(os.path.join(EXTDIR, f), encoding="utf-8", errors="replace").read()
    m = re.findall(r"3\.0\.\d+", txt)
    p("  %s version strings: %s" % (f, sorted(set(m))[:6]))

p("\n== G. graph settings (held-equal items) + clips + seams")
ext = [n for n in g.values() if n["class_type"] == "MiniMaxH3Extender"]
ck(len(ext) == 1, "exactly one MiniMaxH3Extender")
e = ext[0]["inputs"]
want = {"run_mode": "full_batch", "generation_mode": "ref2va", "motion_context": True, "refine_enabled": False,
        "resolution_mode": "manual", "width": 768, "height": 1344, "steps": 10, "sampler_name": "euler",
        "scheduler": "simple", "denoise": 1.0, "context_length": "22", "ref_image_size": "match"}
for k, v in sorted(want.items()):
    ck(e.get(k) == v, "extender %s == %r (got %r)" % (k, v, e.get(k)))
cj = json.loads(e["clips_json"])
clips = cj["clips"]
p("  clips_json top-level keys: %s" % json.dumps(sorted(cj.keys()), ensure_ascii=True))
p("  clip_1 non-prompt fields: %s" % json.dumps({k: v for k, v in sorted(clips[0].items()) if k != "prompt"}, ensure_ascii=True)[:900])
ck(len(clips) == 6, "6 clips")
seams, kept_tot, cur = [], 0, 0
for i, c in enumerate(clips, 1):
    fr = int(round(float(c["duration"]) * FPS))
    ck(fr == CLIP_FRAMES[i - 1], "clip_%d duration %s -> %d frames (expected %d)" % (i, c["duration"], fr, CLIP_FRAMES[i - 1]))
    ck((fr - 5) % 17 == 0, "clip_%d %d on the 5+17k grid" % (i, fr))
    ck(c.get("validated") is False, "clip_%d validated false" % i)
    ck(str(c.get("seed")) == "51080000" and c.get("seed_mode") == "fixed", "clip_%d seed 51080000 fixed (got %r %r)" % (i, c.get("seed"), c.get("seed_mode")))
    t = c.get("prompt")
    ck(shastr(t) == PROMPT_SHA[i - 1], "clip_%d prompt sha256 %s (expected %s)" % (i, shastr(t), PROMPT_SHA[i - 1]))
    kept = fr - (CTX if i > 1 else 0)
    cur += kept
    kept_tot += kept
    if i > 1:
        seams.append(cur - kept)
    p("  clip_%d %s raw=%d overlap_in=%d kept=%d output frames %d..%d" % (i, c.get("name"), fr, CTX if i > 1 else 0, kept, cur - kept, cur - 1))
raw = sum(CLIP_FRAMES)
p("  raw %d frames - 5 seams x%d overlap = %d kept = %.3f s at 24 fps" % (raw, CTX, raw - 5 * CTX, (raw - 5 * CTX) / 24.0))
ck(raw - 5 * CTX == kept_tot == 1433, "computed kept frames %d == 1433 == ffprobe recount" % kept_tot)
p("  clip seams (index of the first frame of each new clip's kept content): %r" % seams)
ck(kept_tot == 1433 and len(seams) == 5, "5 clip seams inside the rendered minute: %r" % seams)
ck(obj["attempts"][0]["frames"] == kept_tot, "the rendered frame count == the graph's computed count (the Extender split the minute exactly as instructed, no re-lengthening)")
ck(obj["attempts"][0]["frames"] == kept_tot, "rendered frame count == the graph's computed count (no Extender re-lengthening)")

p("\n== H. prompt provenance vs the base run's own graph text (no text edits)")
for seg, idx in [("seg1", 0), ("seg1", 1), ("seg2", 2), ("seg2", 3), ("seg3", 4), ("seg3", 5)]:
    b = json.load(open(os.path.join(BASEDIR, "p7_r2_c3_pmot_full_pool_%s.api.json" % seg), encoding="utf-8"))
    node = "c0" if idx % 2 == 0 else "c1"
    bt = b[node]["inputs"]["prompt"]
    gt = clips[idx]["prompt"]
    p("  %s %s base text len=%d sha256=%s" % (seg, node, len(bt), shastr(bt)))
    if idx % 2 == 0:
        ck(gt == bt, "clip_%d == %s %s prompt VERBATIM, byte-for-byte in the graph (no CR/LF normalisation needed: both are graph strings)" % (idx + 1, seg, node))
    else:
        contained = bt in gt
        ck(contained, "clip_%d CONTAINS the %s %s prompt verbatim as a suffix (base text len %d, clip text len %d, prefix block %d chars) = the segment's own subject_definitions block + the base text, unchanged" % (idx + 1, seg, node, len(bt), len(gt), len(gt) - len(bt)))
        if not contained:
            fold = lambda s: s.replace("\r\n", "\n")
            ck(fold(bt) in fold(gt), "clip_%d contains the %s %s text after CR/LF folding" % (idx + 1, seg, node))
            p("    first-diff index %d" % next((i for i in range(min(len(bt), len(gt))) if fold(bt)[i] != fold(gt)[len(gt) - len(bt) + i]), -1))

p("\n== I. fairness vs the base graphs (node-level, model chain + sampler settings)")
b1 = json.load(open(os.path.join(BASEDIR, "p7_r2_c3_pmot_full_pool_seg1.api.json"), encoding="utf-8"))
for nid in ["unet", "m_attn", "m_vsa", "m_shift", "clip", "vvae", "avae", "img"]:
    ck(nid in g and J(g[nid]) == J(b1[nid]), "node %s (%s) byte-identical to the base seg1 graph node" % (nid, g[nid]["class_type"]))
ck(e["model"] == ["m_shift", 0] and e["clip"] == ["clip", 0] and e["vae"] == ["vvae", 0] and e["audio_vae"] == ["avae", 0],
   "the Extender consumes the SAME model chain / clip / video VAE / audio VAE as the base run")
ck(g["m_shift"]["inputs"]["shift_video"] == 10.0 and g["m_shift"]["inputs"]["shift_audio"] == 3.0, "sigma shift 10 / 3 (base m_shift, same node)")
ck(g["m_vsa"]["inputs"]["selection"] == "vsa" and g["m_vsa"]["inputs"]["selection.keep_percent"] == 10, "VSA patch upstream of the model input (same node, keep_percent 10)")
ck(e["steps"] == b1["s0_sched"]["inputs"]["steps"] == b1["s1_sched"]["inputs"]["steps"], "steps held: Extender %r == base BasicScheduler steps" % e["steps"])
ck(e["sampler_name"] == b1["ksel"]["inputs"]["sampler_name"], "sampler held: %r == base ksel" % e["sampler_name"])
ck(e["scheduler"] == b1["s0_sched"]["inputs"]["scheduler"] == b1["s1_sched"]["inputs"]["scheduler"], "scheduler held: %r" % e["scheduler"])
ck(e["denoise"] == b1["s0_sched"]["inputs"]["denoise"] == b1["s1_sched"]["inputs"]["denoise"], "denoise held: Extender %r == base BasicScheduler denoise" % e["denoise"])
ck((e["width"], e["height"]) == (b1["c0"]["inputs"]["width"], b1["c0"]["inputs"]["height"]) == (768, 1344), "resolution held 768x1344 (base c0)")
p("  extender input names: %s" % json.dumps(sorted(e.keys()), ensure_ascii=True))
p("  extender inert/default inputs: megapixels=%r audio_context_length=%r refine_denoise=%r refine_scale=%r refine_steps=%r refs_json=%r"
  % (e.get("megapixels"), e.get("audio_context_length"), e.get("refine_denoise"), e.get("refine_scale"), e.get("refine_steps"), e.get("refs_json")))
ck(e["megapixels"] == 0.4 and e["resolution_mode"] == "manual", "megapixels 0.4 is inert under resolution_mode manual; 768x1344 = 1.03 Mpx is the requested size")
ck(e["refine_enabled"] is False, "refine_denoise/refine_scale/refine_steps are inert (refine_enabled False)")
bn = {}
for seg, gb in (("seg1", os.path.join(BASEDIR, "p7_r2_c3_pmot_full_pool_seg1.api.json")),
                ("seg2", os.path.join(BASEDIR, "p7_r2_c3_pmot_full_pool_seg2.api.json")),
                ("seg3", os.path.join(BASEDIR, "p7_r2_c3_pmot_full_pool_seg3.api.json"))):
    gd = json.load(open(gb, encoding="utf-8"))
    bn[seg] = {k: (v["class_type"], v["inputs"].get("noise_seed")) for k, v in gd.items() if v["class_type"] == "RandomNoise"}
p("  base seed sources: %s" % json.dumps(bn, ensure_ascii=True))
p("  arm graph ids: %s" % json.dumps(sorted(g.keys())))
ck(not any(v["class_type"] == "RandomNoise" for v in g.values()), "the arm graph has no RandomNoise node: the seed lives per clip in clips_json (51080000 fixed, section G) - the base restarts sampling noise per segment with a different noise_seed")
ck(float(g["dec"]["inputs"]["fps"]) == float(b1["mkvid"]["inputs"]["fps"]) == 24.0, "fps held 24 (base CreateVideo fps %r, Extender FinalDecode fps %r)" % (b1["mkvid"]["inputs"]["fps"], g["dec"]["inputs"]["fps"]))
ck(e["ref_image_size"] == b1["c0"]["inputs"]["ref_image_size"], "ref_image_size held %r (base c0)" % e["ref_image_size"])
ck(g["img"]["inputs"]["image"] == b1["img"]["inputs"]["image"], "the reference still is the SAME file string as the base graph: %r" % g["img"]["inputs"]["image"])
sp = os.path.join(COMFY_IN, str(g["img"]["inputs"]["image"]).replace("/", os.sep))
ck(os.path.isfile(sp) and sha(sp) == STILL_SHA, "still sha256 %s (expected %s), %d bytes" % (sha(sp), STILL_SHA, os.path.getsize(sp)))
seeds = {s: json.load(open(os.path.join(BASEDIR, "p7_r2_c3_pmot_full_pool_%s.api.json" % s), encoding="utf-8"))["noise"]["inputs"]["noise_seed"] for s in ("seg1", "seg2", "seg3")}
p("  base noise seeds %r" % seeds)
ck(str(seeds["seg1"]) == "51080000", "the seed held across clips is the BASE SEG1 seed 51080000")
p("  DOCUMENTED DIFFERENCE (not a fairness failure): FIX4 is ONE generation, so all 6 clips are seed_mode fixed at 51080000,")
p("  while the base pipeline re-started per segment at 51080000 / 51080001 / 51080002 (one seed per segment). Recorded in fairness.txt.")
ck(b1["win1"]["inputs"]["overlap_frames"] == 22, "the base run's own chunk overlap is 22 frames (win1 overlap_frames) = the Extender context_length '22'")
p("  base per-chunk lengths: c0 length=%d + win1 extension_frames=%d (window 260, overlap_frames 22 -> 238 new frames per chunk; 243 + 5 x 238 = 1443 over 3 separate segments)"
  % (b1["c0"]["inputs"]["length"], b1["win1"]["inputs"]["extension_frames"]))

p("\n== J. outputs: hashes, sizes, contact sheet")
for f in [mp4, sheet, graph, harness_api, os.path.join(ARMDIR, ARM + ".mp4.json"), statuslog, objp]:
    p("  %-58s %10d bytes sha256 %s" % (os.path.basename(f), os.path.getsize(f), sha(f)))
ck(os.path.getsize(mp4) == 65791775, "mp4 bytes match objective.json/status.log (65791775)")
img = __import__("PIL.Image", fromlist=["open"]).open(sheet)
p("  contact sheet PIL %r mode=%s format=%s" % (img.size, img.mode, img.format))
ck(img.size[0] > 0 and img.size[1] > 0, "contact sheet is a readable image")
meta = json.load(open(os.path.join(ARMDIR, ARM + ".mp4.json"), encoding="utf-8"))
p("  mp4 sidecar keys %s" % sorted(meta.keys()))
for k, v in sorted(meta.items()):
    p("    %s = %r" % (k, v)[:200])
p("  dir listing runs\\%s" % ARM)
for f in sorted(os.listdir(ARMDIR)):
    fp = os.path.join(ARMDIR, f)
    p("    %s %s" % ("d " if os.path.isdir(fp) else "f ", f))

p("\n== K. sbs/stills (Max's, per TASKS sbs rule)")
r = subprocess.run(["find", RUNS, "-name", "sbs_*.mp4"], capture_output=True, text=True)
p("  find runs -name sbs_*.mp4 -> %r" % r.stdout.split())
p("  -> no FIX4 side-by-side; sbs_* and fixed-frame stills are Max/harness files, never Forge files (AGENTS.md).")

p("")
p("ALL CHECKS PASS" if not fails else "CHECK FAILS %d" % len(fails))
for f in fails:
    p(" -", f)
full = "\n".join(L) + "\n"
open(REPORT, "w", encoding="utf-8").write(full)
print(full)
print("report written: %s (%d bytes)" % (REPORT, len(full)))
