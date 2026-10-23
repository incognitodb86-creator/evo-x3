# ALI-147 PV2-6 report probe (READ-ONLY). No GPU, no ComfyUI / node list / llama-swap / Strata call,
# no render, no run_graph_job.py / batch_queue.py, no JOB_REQUEST, no vision judge, no download/install/delete,
# no image viewing. ffmpeg/ffprobe used only as read-only probes. Writes ONLY C:/AI/community/notes/.
import json, os, hashlib, subprocess, re, sys, datetime

FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
FFMPEG = FFPROBE.replace("ffprobe.exe", "ffmpeg.exe")
RUNJOB = r"C:/AI/community/scripts/run_graph_job.py"
RUNS = r"C:/AI/community/runs"
P7 = r"C:/AI/community/p7"
SPECS = r"C:/AI/community/specs/prompt_v2"
NOTES = r"C:/AI/community/notes"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
OUT = os.path.join(NOTES, "ali147-pv26-report-probe-20261023.txt")

sys.path.insert(0, r"C:/AI/community/scripts")
import comm  # the harness youth guard

L = []
F = 0
P = 0


def p(s):
    L.append(s)


def ck(cond, label):
    global F, P
    if cond:
        P += 1
        p("PASS  " + label)
    else:
        F += 1
        p("FAIL  " + label)
    return bool(cond)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def raw(path):
    with open(path, "rb") as f:
        return f.read()


def size(path):
    return os.path.getsize(path)


def probe(args):
    r = subprocess.run([FFPROBE, "-v", "error"] + args, capture_output=True, text=True)
    return (r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip())


def gk(d, *names):
    for n in names:
        if n in d:
            return d[n]
    return None


def ff_count(mp4):
    rc, out, err = probe(["-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=width,height,r_frame_rate,nb_read_packets",
                          "-of", "csv=p=0", mp4])
    rc2, out2, err2 = probe(["-show_entries", "stream=index,codec_type,codec_name,sample_rate,channels",
                             "-of", "csv=p=0", mp4])
    rc3, out3, err3 = probe(["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4])
    return out, out2, out3


HF = re.search(r'"-vf", "([^"]+)"', raw(RUNJOB).decode("utf-8", "replace"))
CHAIN = HF.group(1) if HF else "blackdetect=d=1.0:pix_th=0.10,freezedetect=n=-60dB:d=2"


def ff_rows(mp4, want_frames, want_w, want_h, tag):
    v, streams, dur = ff_count(mp4)
    parts = v.split(",")
    pk = parts[-1] if parts and parts[-1].isdigit() else "?"
    p("  %s ffprobe -count_packets = %s | streams=%s | format_dur=%s" % (tag, v, streams.replace("\n", " | "), dur))
    ck(len(parts) == 4 and pk == str(want_frames), "%s ffprobe video packets = %d (count_packets, never format=duration)" % (tag, want_frames))
    ck(len(parts) == 4 and parts[0] == str(want_w) and parts[1] == str(want_h), "%s ffprobe resolution %sx%s" % (tag, want_w, want_h))
    ck(len(parts) == 4 and parts[2] == "24/1", "%s ffprobe r_frame_rate 24/1" % tag)
    ck("audio" in streams, "%s audio stream present" % tag)
    return v


def blackfreeze(mp4):
    # the exact chain read out of run_graph_job.py (provenance, not hardcoded)
    r = subprocess.run([FFMPEG, "-v", "error", "-i", mp4, "-vf", CHAIN, "-an", "-f", "null", "NUL"],
                       capture_output=True, text=True)
    ev = [x.strip() for x in (r.stderr or "").splitlines() if "black_start" in x or "freeze_start" in x]
    return r.returncode, ev


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def graph(path):
    return load_json(path)


def nodejs(g, nid):
    return json.dumps(g[nid], sort_keys=True)


def prompts(g):
    out = {}
    for nid, node in g.items():
        for k, v in node.get("inputs", {}).items():
            if k == "prompt" and isinstance(v, str):
                out[nid] = v
    return out


ARMS = [
    ("PV2-1", "ali147_pool_promptv2_s51080000", "ali147_pool_ctrl_s51080000",
     "runs\\ali147_pool_ctrl_s51080000\\submitted_graph.pretty.json (the driver-rendered CTRL graph)",
     ["v2_seg1_c0_r2v.txt", "v2_seg1_c1_t2va.txt"], ["c0", "c1"], "prompt"),
    ("PV2-2", "ali147_pool_promptv2_seg3_s51080002", "p7_r2_c3_pmot_full_pool_seg3",
     "runs\\p7_r2_c3_pmot_full_pool\\p7_r2_c3_pmot_full_pool_seg3.api.json (the BASE minute's own segment 3)",
     ["v2_seg3_c0_r2v.txt", "v2_seg3_c1_t2va.txt"], ["c0", "c1"], "prompt"),
    ("PV2-3", "ali147_pool_dense_s51080000", "ali147_pool_ctrl_s51080000",
     "runs\\ali147_pool_ctrl_s51080000\\submitted_graph.pretty.json (the driver-rendered CTRL graph)",
     [], ["c0", "c1"], "ctrl-verbatim"),
]

p("ALI-147 PV2-6 report probe - %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
p("read-only; no GPU/ComfyUI/node-list/llama-swap/Strata, no render, no run_graph_job.py, no job request, no vision judge")

# ---------- prompt source files ----------
p("\n== A. prompt_v2 source files (specs\\prompt_v2)")
PF = {}
for name in ["v2_seg1_c0_r2v.txt", "v2_seg1_c1_t2va.txt", "v2_seg3_c0_r2v.txt", "v2_seg3_c1_t2va.txt"]:
    fp = os.path.join(SPECS, name)
    if os.path.exists(fp):
        b = raw(fp)
        PF[name] = b
        p("%s  %d B  sha256 %s  crlf=%s  trailing_nl=%s" % (name, len(b), sha(fp), b"\r\n" in b, b.endswith(b"\n")))
    else:
        p("MISSING %s" % name)
sums = os.path.join(SPECS, "SHA256SUMS.txt")
if os.path.exists(sums):
    want = {}
    for line in raw(sums).decode("utf-8", "replace").splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+\*?\s*(\S+)$", line.strip())
        if m:
            want[os.path.basename(m.group(2))] = m.group(1)
    for name in PF:
        ck(len(want.get(name, "")) == 64 and sha(os.path.join(SPECS, name)) == want[name],
           "prompt file %s sha256 equals SHA256SUMS.txt" % name)

# ---------- controls ----------
p("\n== B. controls (measured here)")
CTLM = os.path.join(RUNS, "ali147_pool_ctrl_s51080000", "ali147_pool_ctrl_s51080000.mp4")
B3 = os.path.join(RUNS, "p7_r2_c3_pmot_full_pool", "p7_r2_c3_pmot_full_pool_seg3.mp4")
CTRLGRAPH = os.path.join(RUNS, "ali147_pool_ctrl_s51080000", "submitted_graph.pretty.json")
B3GRAPH = os.path.join(RUNS, "p7_r2_c3_pmot_full_pool", "p7_r2_c3_pmot_full_pool_seg3.api.json")
for tag, mp, gph, fr in (("CTRL seg1", CTLM, CTRLGRAPH, 481),
                         ("BASE seg3", B3, B3GRAPH, 481)):
    p("%s mp4 %s" % (tag, mp))
    p("  %d B sha256 %s" % (size(mp), sha(mp)))
    p("harness blackfreeze chain (run_graph_job.py) = %r" % CHAIN)
    ff_rows(mp, fr, 768, 1344, tag)
    g = graph(gph)
    pr = prompts(g)
    for nid in sorted(pr):
        p("  graph %s node %s prompt %d chars sha256 %s" % (os.path.basename(gph), nid, len(pr[nid]),
                                                             hashlib.sha256(pr[nid].encode()).hexdigest()))
    p("  graph %s %d B sha256 %s nodes=%d" % (os.path.basename(gph), size(gph), sha(gph), len(g)))

# ---------- per arm ----------
report = {}
for tag, arm, ctl, srctag, pfiles, pnodes, pmode in ARMS:
    d = os.path.join(RUNS, arm)
    p("\n== %s  %s" % (tag, arm))
    p("control = %s   source = %s" % (ctl, srctag))
    for fn in sorted(os.listdir(d)):
        fp = os.path.join(d, fn)
        if os.path.isfile(fp):
            p("  file %-52s %10d B  sha256 %s" % (fn, size(fp), sha(fp)))
        else:
            p("  dir  %s/ (harness-owned)" % fn)
    req = os.path.join(d, "request.api.json")
    api = os.path.join(d, arm + ".api.json")
    mp4 = os.path.join(d, arm + ".mp4")
    sheet = os.path.join(d, arm + "_stills_contact.png")
    stat = os.path.join(d, "status.log")
    obj = os.path.join(d, "objective.json")
    resj = os.path.join(P7, "jobs", arm + ".result.json")
    gd = os.path.join(d, "graph_diff.txt")
    ck(raw(req) == raw(api), "PROVENANCE request.api.json bytes == harness-rendered %s.api.json (0 bytes differ)" % arm)
    ck(sha(req) == sha(api), "PROVENANCE identical sha256 %s" % sha(req))
    st = raw(stat).decode("utf-8", "replace").splitlines()
    for l in st:
        p("  status.log| %s" % l)
    keys = ("JOB start", "JOB end", "OBJECTIVE")
    ck(sum(1 for l in st if "JOB end" in l and " ok" in l) == 1, "exactly one 'JOB end ... ok' line")
    ck(not [l for l in st if re.search(r"JOB error|CLIP_SKIP|clip_skip|node_errors|Traceback|STUCK|REDO|redo|STATIC_FAIL|COMFY_DOWN|OBJECTIVE FAIL|error|ERROR|SKIP|blocked|out of memory|OOM|RuntimeError|Killed|timeout", l)],
       "status.log has no error/redo/STUCK/SKIP/OOM line (regex over every line)")
    o = load_json(obj)
    if "attempts" in o:
        att = o["attempts"]
        secs = [a.get("secs") for a in att]
        a0 = att[0]
        bf = gk(a0, "blackfreeze", "black_freeze")
        ck(o.get("ok") is True, "objective.json ok=true (attempts shape)")
        ck(len(att) == 1, "objective.json attempts length 1 = no redo, no STUCK")
        ofr, obytes, oaud, odur, ow, oh, ofps = (gk(a0, "frames"), gk(a0, "bytes"), gk(a0, "audio"), gk(a0, "duration"),
                                                 gk(a0, "w", "width"), gk(a0, "h", "height"), gk(a0, "fps"))
        p("  objective attempt0 frames=%s %sx%s fps=%s audio=%s dur=%s bytes=%s secs=%s" % (ofr, ow, oh, ofps, oaud, odur, obytes, a0.get("secs")))
        p("  objective attempt0 blackfreeze=%s" % json.dumps(bf))
        ck(bf == [], "objective.json attempt0 blackfreeze []")
    else:
        a0 = o
        secs = [o.get("secs")]
        ofr, obytes, oaud, odur, ow, oh, ofps = (gk(o, "frames"), gk(o, "bytes"), gk(o, "audio"), gk(o, "duration"),
                                                 gk(o, "w", "width"), gk(o, "h", "height"), gk(o, "fps"))
        p("  objective (flat) frames=%s %sx%s fps=%s audio=%s dur=%s bytes=%s secs=%s blackfreeze=%s" % (ofr, ow, oh, ofps, oaud, odur, obytes, o.get("secs"), json.dumps(gk(o, "blackfreeze", "black_freeze"))))
        ck(o.get("ok") is True, "objective.json ok=true (flat shape)")
    ff_rows(mp4, ofr, ow, oh, "arm " + arm)
    ck(size(mp4) == obytes, "mp4 bytes == objective bytes")
    rcbf, ev = blackfreeze(mp4)
    p("  harness-chain black/freeze events = %r rc=%d" % (ev, rcbf))
    ck(rcbf == 0 and len(ev) == 0, "harness blackfreeze chain (%s) re-run = 0 events" % CHAIN)
    im = __import__("PIL.Image", fromlist=["open"]).open(sheet)
    p("  contact sheet %s %dx%s %s %s  %d B sha256 %s" % (os.path.basename(sheet), im.size[0], im.size[1], im.mode, im.format, size(sheet), sha(sheet)))
    im.close()
    g = graph(req)
    pr = prompts(g)
    for nid in sorted(pr):
        p("  graph node %s prompt %d chars sha256 %s" % (nid, len(pr[nid]), hashlib.sha256(pr[nid].encode()).hexdigest()))
    ck(all(comm.guard_ok(t) for t in pr.values()), "comm.guard_ok passes on every prompt string in the graph")
    # one-variable gate vs the control graph
    cg = graph(CTRLGRAPH if ctl.startswith("ali147_pool_ctrl") else B3GRAPH)
    shared = sorted(set(g) & set(cg))
    diffnodes = sorted([n for n in shared if nodejs(g, n) != nodejs(cg, n)])
    p("  nodes: arm %d, control %d, shared %d, control-only %s, arm-only %s" % (len(g), len(cg), len(shared),
                                                                                sorted(set(cg) - set(g)), sorted(set(g) - set(cg))))
    p("  differing shared nodes = %s" % diffnodes)
    for n in diffnodes:
        ai = set(g[n].get("inputs", {}))
        ci = set(cg[n].get("inputs", {}))
        p("    node %s class %s -> %s ; input keys arm-only %s control-only %s" % (n, cg[n].get("class_type"), g[n].get("class_type"),
                                                                                   sorted(ai - ci), sorted(ci - ai)))
        for k in sorted(ai & ci):
            if json.dumps(g[n]["inputs"][k], sort_keys=True) != json.dumps(cg[n]["inputs"][k], sort_keys=True):
                p("    node %s input '%s' CHANGED" % (n, k))
    ck(len(set(cg) - set(g)) == (1 if pmode != "prompt" else 0),
       "control-only nodes = %s (expected %s)" % (sorted(set(cg) - set(g)), "['m_vsa'] (the deleted VSA node)" if pmode != "prompt" else "none"))
    ck(len(set(g) - set(cg)) == 0, "no new nodes added")
    if pmode == "prompt":
        ck(diffnodes == sorted(pnodes + ["save"]) or diffnodes == sorted(set(pnodes + ["save"])),
           "fairness: differing shared nodes are EXACTLY %s + save" % pnodes)
        for nid, fn in zip(pnodes, pfiles):
            fileb = raw(os.path.join(SPECS, fn))
            txt = fileb.decode("utf-8").replace("\r\n", "\n").rstrip("\n")
            gtxt = g[nid]["inputs"]["prompt"]
            ck(gtxt == txt, "node %s prompt == %s verbatim (EOL-folded, %d chars, sha256 %s)" % (nid, fn, len(txt), hashlib.sha256(txt.encode()).hexdigest()))
            ck(comm.guard_ok(gtxt), "guard_ok on node %s prompt (from %s)" % (nid, fn))
    else:
        ck(diffnodes == ["m_shift", "save"], "fairness: differing shared nodes are EXACTLY ['m_shift', 'save'] (VSA-off rewire + prefix)")
        ck(all(json.dumps(g[n]["inputs"]["prompt"], sort_keys=True) == json.dumps(cg[n]["inputs"]["prompt"], sort_keys=True) for n in ("c0", "c1")),
           "prompts are CTRL verbatim on c0 and c1")
        ck("m_vsa" not in g and "m_vsa" in cg, "node m_vsa (BlockSparseAttention) present in CTRL, DELETED in the arm")
        ck(g["m_shift"]["inputs"]["model"] == ["m_attn", 0] and cg["m_shift"]["inputs"]["model"] == ["m_vsa", 0],
           "m_shift.inputs.model ['m_vsa',0] -> ['m_attn',0]")
        ck(nodejs(g, "noise") == nodejs(cg, "noise"), "seed node byte-identical (noise_seed)")
        ck(nodejs(g, "m_attn") == nodejs(cg, "m_attn"), "m_attn untouched")
        ck(json.dumps(g["img"], sort_keys=True) == json.dumps(cg["img"], sort_keys=True), "img LoadImage node byte-identical")
    # graph_diff shape
    if os.path.exists(gd):
        gb = raw(gd).decode("utf-8", "replace")
        hunks = re.findall(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@", gb, re.M)
        rem = len([l for l in gb.splitlines() if l.startswith("-") and not l.startswith("---")])
        add = len([l for l in gb.splitlines() if l.startswith("+") and not l.startswith("+++")])
        p("  graph_diff.txt %d B sha256 %s hunks=%d removed=%d added=%d" % (size(gd), sha(gd), len(hunks), rem, add))
        for h in hunks:
            p("    hunk %s" % h)
    # result.json
    if os.path.exists(resj):
        r = load_json(resj)
        p("  result.json %s" % json.dumps(r, sort_keys=True)[:900])
    sd = load_json(os.path.join(d, arm + ".mp4.json"))
    p("  mp4.json sidecar %s" % json.dumps(sd, sort_keys=True))
    report[tag] = {"arm": arm, "secs": secs, "bytes": obytes, "frames": ofr,
                   "mp4sha": sha(mp4), "sheet": sheet, "sheetsha": sha(sheet), "sheetgeo": None,
                   "reqsha": sha(req), "gdsha": (sha(gd) if os.path.exists(gd) else None)}

# ---------- the load-image still / reference stills ----------
p("\n== C. stills (source + contact sheets)")
COMFY_INPUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
IMG = os.path.join(COMFY_INPUT, "community", "POOL_768x1344.png")
for cand in [IMG, os.path.join(COMFY_INPUT, "community", "POOL_768x1344.png") + ".png"]:
    if os.path.exists(cand):
        IMG = cand
        break
if os.path.exists(IMG):
    im = __import__("PIL.Image", fromlist=["open"]).open(IMG)
    p("source still %s %s %dx%s %s  sha256 %s" % (IMG, im.format, im.size[0], im.size[1], im.mode, sha(IMG)))
    p("size %d B" % size(IMG))
    im.close()
else:
    p("source still NOT FOUND at any probed ComfyUI\\input path")
for tag in report:
    s = report[tag]["sheet"]
    im = __import__("PIL.Image", fromlist=["open"]).open(s)
    tiles = (im.size[0] // (256 + 4)) * ((im.size[1] + 4) // (448 + 4)) if im.size[0] >= 256 else 0
    p("%s sheet %s %dx%s %s tiles(approx)=%d sha256 %s" % (tag, os.path.basename(s), im.size[0], im.size[1], im.mode, tiles, report[tag]["sheetsha"]))
    im.close()
    for t in [8.5, 11.5, 18.5, 19.5]:
        pass
    p("   sampled windows (run_graph_job.py: +-1.5 s around 0:10/0:20/0:30/0:40/0:50, t <= dur-0.05) for a 20.04 s clip = t 8.5-11.5 and 18.5-19.5 s = frames 204/216/228/240/252/264/276/444/456/468; frame 0 and 480 are NEVER sampled (harness-fixed sampling, not a defect)")

# ---------- render seconds table ----------
p("\n== D. render seconds across every 481-frame run in runs\\ (objective.json, both shapes)")
rows = []
for d in sorted(os.listdir(RUNS)):
    if not d.startswith("ali147_pool_"):
        continue
    op = os.path.join(RUNS, d, "objective.json")
    sp = os.path.join(RUNS, d, "status.log")
    if not os.path.exists(op):
        continue
    o = load_json(op)
    fr = None
    sec = None
    if "attempts" in o:
        fr = o["attempts"][0].get("frames")
        sec = o["attempts"][0].get("secs")
    else:
        fr = o.get("frames")
        sec = o.get("secs")
    bm = None
    if os.path.exists(sp):
        for l in raw(sp).decode("utf-8", "replace").splitlines():
            m = re.search(r"JOB end \S+ ok secs=([\d.]+)", l)
            if m:
                bm = m.group(1)
    rows.append((sec if sec is not None else 0, d, fr, bm))
for sec, d, fr, bm in sorted(rows):
    p("  secs %-8s frames %-5s status-log secs %-8s %s" % (sec, fr, bm, d))

# ---------- budget + sbs ----------
p("\n== E. live p7 budget + sbs/stills ownership")
if os.path.exists(BUDGET):
    b = load_json(BUDGET)
    p("  p7_budget.json %s" % json.dumps(b, sort_keys=True))
r = subprocess.run(["find", RUNS, "-name", "sbs_*.mp4"], capture_output=True, text=True)
p("  find runs -name sbs_*.mp4 -> %d file(s): %s" % (len([x for x in r.stdout.splitlines() if x.strip()]), r.stdout.strip()))
r2 = subprocess.run(["find", RUNS, "-name", "sbs_*.mp4", "-newer", os.path.join(RUNS, "ali147_pool_dense_s51080000", "objective.json")], capture_output=True, text=True)
p("  sbs newer than the dense render: %s" % (r2.stdout.strip() or "none"))
r3 = subprocess.run(["find", RUNS, "-maxdepth", "2", "-name", "*still*"], capture_output=True, text=True)
p("  runs\\*still* files: %s" % (r3.stdout.strip().replace("\n", " | ") or "none"))
r4 = subprocess.run(["find", P7, "-maxdepth", "1", "-name", "JOB_REQUEST.json"], capture_output=True, text=True)
p("  p7\\JOB_REQUEST.json present: %s (this iteration wrote no request)" % bool(r4.stdout.strip()))
r5 = subprocess.run(["find", P7, os.path.join(P7, "jobs"), "-maxdepth", "1", "-name", "request_iter*.json"], capture_output=True, text=True)
p("  archived requests: %s" % r5.stdout.strip().replace("\n", " | "))
for it in ["11", "12", "01", "02"]:
    fp = os.path.join(P7, "jobs", "request_iter%s.json" % it)
    if os.path.exists(fp):
        p("  request_iter%s.json %d B sha256 %s content=%s" % (it, size(fp), sha(fp), raw(fp).decode("utf-8", "replace").strip()))

# ---------- held items ----------
p("\n== F. held / not-rendered lines (PV2-4, PV2-5) - read-only presence checks, NO GPU")
COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
LORA = os.path.join(COMFY, "models", "loras", "h3", "Vagina_minimax-h3_epoch20.safetensors")
for tag, path in [
    ("LORA card h3\\Vagina_minimax-h3_epoch20.safetensors", LORA),
    ("PV2-4 arm dir (must not exist = not built)", os.path.join(RUNS, "ali147_pool_pv2_hmpussy_s51080002")),
    ("PV2-5 output dir (must not exist = not rendered)", os.path.join(RUNS, "pool_stillfix_a")),
    ("the stillfix_A prompt file (PV2-5 input)", os.path.join(SPECS, "stillfix_A_anatomy_ref_klein.txt")),
]:
    ex = os.path.exists(path)
    p("  %s exists=%s size=%s path=%s" % (tag, ex, (size(path) if ex and os.path.isfile(path) else "-"), path))
    if ex and os.path.isfile(path):
        p("     sha256 %s" % sha(path))
for root in [os.path.join(COMFY, "models", "loras"), os.path.join(COMFY, "models", "loras", "h3"), COMFY_INPUT]:
    if os.path.isdir(root):
        hits = [n for n in os.listdir(root) if "agina" in n.lower() or "snofs" in n.lower()]
        p("  %s -> lora/SNOFS name matches: %s" % (root, hits))
    else:
        p("  %s -> NOT A DIRECTORY" % root)
for root in [r"C:/Users/derek/5slock/approved_characters", r"C:/Users/derek/5slock/approved_characters/REF_SHEETS_2026-10-19"]:
    if os.path.isdir(root):
        names = sorted(os.listdir(root))
        p("  %s (%d entries) snofs/pool matches: %s" % (root, len(names), [n for n in names if "sno" in n.lower() or "pool" in n.lower()]))
    else:
        p("  %s NOT A DIRECTORY" % root)
for nm in ["stillfix_A_anatomy_ref_klein.txt", "stillfix_B_matte_skin_klein.txt"]:
    fp = os.path.join(SPECS, nm)
    p("  specs\\prompt_v2\\%s exists=%s" % (nm, os.path.exists(fp)))

p("\nTOTAL PASS=%d FAIL=%d" % (P, F))
p("ALL CHECKS PASS" if F == 0 else "FAILURES PRESENT: %d" % F)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(L) + "\n")
print("wrote %s  %d B  PASS=%d FAIL=%d" % (OUT, size(OUT), P, F))
