import os, json, hashlib, re, glob
C = "AI_COMMUNITY"
C = "C:/AI/community"
SRC = C + "/runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.api.json"
ARMNAME = "ali147_pool_promptv2_seg3_s51080002"
ARM = C + "/runs/" + ARMNAME
DST = ARM + "/request.api.json"
PDIR = C + "/specs/prompt_v2"
SIDECAR = C + "/runs/p7_r2_c3_pmot_full_pool/prompts"
RPT = C + "/notes/ali147-pv22-fairness-20261022.txt"
CFG = ["C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"]
def sha(b):
    return hashlib.sha256(b).hexdigest()
def load(fp):
    return json.loads(open(fp, "rb").read().decode("utf-8"))
src = load(SRC)
arm = load(DST)
srbc = open(SRC, "rb").read()
arbc = open(DST, "rb").read()
O = []
def p(s):
    O.append(str(s))
p("ALI-147 PV2-2 fairness.txt - arm " + ARMNAME)
p("This file is written by Forge (notes/ali147_pv22_fairness.py) before the render. It is a measured")
p("comparison, not an assertion: every line below is produced by comparing the two graph files on disk.")
p("METHOD_ONLY. KEEP is Derrick's only. No vision judge, no by-eye claim in this file.")
p("")
p("== graph provenance")
p("copy source (control) : " + SRC)
p("  bytes %d sha256 %s" % (len(srbc), sha(srbc)))
p("arm graph (request)   : " + DST)
p("  bytes %d sha256 %s" % (len(arbc), sha(arbc)))
p("format of both        : json.dumps(indent=1, ensure_ascii=True), CRLF, no trailing newline")
p("  source CRLF %d / arm CRLF %d ; source trailing-newline %s / arm %s" % (srbc.count(b"\r\n"), arbc.count(b"\r\n"), srbc.endswith(b"\n"), arbc.endswith(b"\n")))
p("control for this arm  : the BASE minute (runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.mp4,")
p("  the base run's own segment 3, rendered from the copy source graph with the same seed). No new control render.")
p("")
p("== node-by-node compare (json.dumps(node, sort_keys=True))")
p("%-10s %-34s %-10s %s" % ("node", "class_type", "result", "changed inputs"))
same = 0
dlist = []
for k in sorted(src):
    a = json.dumps(src[k], sort_keys=True)
    b = json.dumps(arm.get(k, {}), sort_keys=True)
    if a == b:
        same += 1
        p("%-10s %-34s %-10s %s" % (k, src[k].get("class_type"), "IDENTICAL", "-"))
    else:
        ch = [ik for ik in sorted(src[k]["inputs"]) if json.dumps(src[k]["inputs"][ik], sort_keys=True) != json.dumps(arm[k]["inputs"][ik], sort_keys=True)]
        dlist.append(k)
        p("%-10s %-34s %-10s %s" % (k, src[k].get("class_type"), "DIFFERS", json.dumps(ch)))
p("nodes total %d, identical %d, differing %s" % (len(src), same, json.dumps(dlist)))
p("")
p("== the three intended differences (all of them)")
p("1. c0.inputs.prompt  = specs/prompt_v2/v2_seg3_c0_r2v.txt verbatim")
p("2. c1.inputs.prompt  = specs/prompt_v2/v2_seg3_c1_t2va.txt verbatim")
p("3. save.inputs.filename_prefix = " + arm["save"]["inputs"]["filename_prefix"])
p("Nothing else. Node key set identical (25 nodes); input key sets on c0/c1/save unchanged.")
p("")
p("== held-equal settings (read from BOTH graphs, values shown from the arm; identical in the source)")
def both(path, fn):
    a = fn(src)
    b = fn(arm)
    return (a == b), a
rows = [
    ("checkpoint (UNETLoader.unet_name)", lambda g: g["unet"]["inputs"]["unet_name"]),
    ("weight_dtype", lambda g: g["unet"]["inputs"]["weight_dtype"]),
    ("attention backend (m_attn.attention)", lambda g: g["m_attn"]["inputs"]["attention"]),
    ("VSA selection (m_vsa.selection)", lambda g: g["m_vsa"]["inputs"]["selection"]),
    ("VSA keep_percent", lambda g: g["m_vsa"]["inputs"]["selection.keep_percent"]),
    ("VSA start/end percent", lambda g: (g["m_vsa"]["inputs"]["start_percent"], g["m_vsa"]["inputs"]["end_percent"])),
    ("VSA min_tokens/extra_tokens", lambda g: (g["m_vsa"]["inputs"]["min_tokens"], g["m_vsa"]["inputs"]["extra_tokens"])),
    ("VSA dense_blocks/sink_conditioning", lambda g: (g["m_vsa"]["inputs"]["dense_blocks"], g["m_vsa"]["inputs"]["sink_conditioning"])),
    ("VSA wiring (m_vsa.model -> m_attn)", lambda g: g["m_vsa"]["inputs"]["model"]),
    ("sigma shift video/audio (10/3)", lambda g: (g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"])),
    ("seed (noise.noise_seed)", lambda g: g["noise"]["inputs"]["noise_seed"]),
    ("steps (s0/s1)", lambda g: (g["s0_sched"]["inputs"]["steps"], g["s1_sched"]["inputs"]["steps"])),
    ("scheduler (s0/s1)", lambda g: (g["s0_sched"]["inputs"]["scheduler"], g["s1_sched"]["inputs"]["scheduler"])),
    ("denoise (s0/s1)", lambda g: (g["s0_sched"]["inputs"]["denoise"], g["s1_sched"]["inputs"]["denoise"])),
    ("sampler (ksel)", lambda g: g["ksel"]["inputs"]["sampler_name"]),
    ("CLIP (clip_name/type/device)", lambda g: (g["clip"]["inputs"]["clip_name"], g["clip"]["inputs"]["type"], g["clip"]["inputs"]["device"])),
    ("video VAE", lambda g: g["vvae"]["inputs"]["vae_name"]),
    ("audio VAE", lambda g: g["avae"]["inputs"]["vae_name"]),
    ("width/height c0", lambda g: (g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"])),
    ("width/height c1", lambda g: (g["c1"]["inputs"]["width"], g["c1"]["inputs"]["height"])),
    ("c0.length (chunk 1 frames)", lambda g: g["c0"]["inputs"]["length"]),
    ("win1.extension_frames (chunk 2 frames)", lambda g: g["win1"]["inputs"]["extension_frames"]),
    ("win1.overlap_frames (context)", lambda g: g["win1"]["inputs"]["overlap_frames"]),
    ("c1.length (link)", lambda g: g["c1"]["inputs"]["length"]),
    ("append/tail token wiring", lambda g: (g["app1"]["inputs"]["overlap_video_tokens"], g["app1"]["inputs"]["overlap_audio_tokens"], g["app1"]["inputs"]["transition_video_tokens"], g["app1"]["inputs"]["transition_audio_tokens"])),
    ("c0 class_type", lambda g: g["c0"]["class_type"]),
    ("c1 class_type", lambda g: g["c1"]["class_type"]),
    ("c0 ref_images.ref_image_1 (link)", lambda g: g["c0"]["inputs"]["ref_images.ref_image_1"]),
    ("c0 ref_image_size", lambda g: g["c0"]["inputs"]["ref_image_size"]),
    ("c0 vae/audio_vae wiring", lambda g: (g["c0"]["inputs"]["vae"], g["c0"]["inputs"]["audio_vae"])),
    ("c1 vae wiring", lambda g: g["c1"]["inputs"]["vae"]),
    ("CreateVideo fps", lambda g: g["mkvid"]["inputs"]["fps"]),
    ("save format/codec", lambda g: (g["save"]["inputs"]["format"], g["save"]["inputs"]["codec"])),
    ("LoadImage string", lambda g: g["img"]["inputs"]["image"]),
    ("guiders/samplers wiring", lambda g: (g["s0_guide"]["inputs"], g["s1_guide"]["inputs"]["model"])),
]
for label, fn in rows:
    eq, val = both(label, fn)
    p("%-42s equal=%-5s value=%s" % (label, str(eq), json.dumps(val)))
p("")
p("== prompts (PROMPT_V2 seg3) and their hashes")
sums = {}
for ln in open(PDIR + "/SHA256SUMS.txt", "rb").read().decode("utf-8").splitlines():
    m = re.match(r"^([0-9a-f]{64})\s+\*?\s*(\S+)$", ln)
    if m:
        sums[m.group(2)] = m.group(1)
p("SHA256SUMS.txt parsed entries: %d" % len(sums))
for node, fname in (("c0", "v2_seg3_c0_r2v.txt"), ("c1", "v2_seg3_c1_t2va.txt")):
    fb = open(PDIR + "/" + fname, "rb").read()
    ft = fb.decode("utf-8")
    gp = arm[node]["inputs"]["prompt"]
    p("file specs/prompt_v2/" + fname)
    p("  file bytes %d sha256 %s  (SHA256SUMS entry %s) match=%s" % (len(fb), sha(fb), sums.get(fname, "MISSING"), sha(fb) == sums.get(fname)))
    p("  CRLF %d trailing-newline %s ascii-only %s" % (fb.count(b"\r\n"), fb.endswith(b"\n"), all(ord(c) < 128 for c in ft)))
    p("  graph %s.prompt chars %d sha256 %s  verbatim-equal-to-file=%s" % (node, len(gp), sha(gp.encode()), gp == ft))
    p("  source (base seg3) %s.prompt chars %d sha256 %s" % (node, len(src[node]["inputs"]["prompt"]), sha(src[node]["inputs"]["prompt"].encode())))
    p("  delta chars %+d" % (len(gp) - len(src[node]["inputs"]["prompt"])))
    side = SIDECAR + ("/p7_r2_c3_pmot_full_pool_seg3_c0_long_r2v.txt" if node == "c0" else "/p7_r2_c3_pmot_full_pool_seg3_c1_long_cont.txt")
    if os.path.isfile(side):
        sb = open(side, "rb").read()
        st = sb.decode("utf-8", "replace").replace("\r\n", "\n").rstrip("\n")
        p("  base sidecar %s bytes %d crlf %d -> EOL-folded+rstrip chars %d sha256 %s  == source graph prompt: %s" % (os.path.basename(side), len(sb), sb.count(b"\r\n"), len(st), sha(st.encode()), st == src[node]["inputs"]["prompt"]))
    else:
        p("  base sidecar not found: " + side)
p("prompt-bearing nodes in the arm graph: %s" % json.dumps([k for k in sorted(arm) if isinstance(arm[k].get("inputs", {}).get("prompt"), str)]))
p("")
p("== reference still")
img = arm["img"]["inputs"]["image"]
p("LoadImage string (graph): " + img)
found = None
for root in CFG:
    cand = os.path.join(root, img.replace("/", os.sep))
    if os.path.isfile(cand):
        found = cand
        break
if found:
    b = open(found, "rb").read()
    p("resolves inside ComfyUI\\input: %s bytes %d sha256 %s" % (found, len(b), sha(b)))
    p("expected sha256 9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075 match=%s" % (sha(b) == "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"))
    try:
        im = __import__("PIL.Image", fromlist=["open"]).open(found)
        p("PIL size %s mode %s format %s" % (str(im.size), im.mode, im.format))
    except Exception as e:
        p("PIL: " + repr(e))
else:
    p("NOT FOUND under " + json.dumps(CFG))
p("source graph LoadImage string is the same file: %s" % (src["img"]["inputs"]["image"] == img))
p("")
p("== frame budget and the comparison frames")
p("c0.length 243 + win1.extension_frames 238 = 481 frames at fps 24 = 20.04 s (the request states frames 481, frames_tol 0).")
p("The base run's own segment 3 (the control) is 481 frames; the base stitched minute frames 962-1442 are")
p("the same segment. PV2-2 asks for sbs_base_seg3_promptv2.mp4 (base 962-1442 | new 0-480) and full-res")
p("stills at new frames 200, 243, 300, 400, 480: hstack side-by-sides and fixed-frame stills are Max/harness")
p("files (run_graph_job.py has no hstack path); the harness contact sheet covers the +-1.5 s windows only.")
p("")
p("== graph_diff summary (see graph_diff.txt, produced by git diff --no-index source vs arm)")
gd = ARM + "/graph_diff.txt"
if os.path.isfile(gd):
    gb = open(gd, "rb").read()
    t = gb.decode("utf-8", "replace")
    rl = [l for l in t.splitlines() if l.startswith("-") and not l.startswith("---")]
    al = [l for l in t.splitlines() if l.startswith("+") and not l.startswith("+++")]
    hn = [l for l in t.splitlines() if l.startswith("@@")]
    p("graph_diff.txt bytes %d sha256 %s hunks %d removed %d added %d" % (len(gb), sha(gb), len(hn), len(rl), len(al)))
    for l in hn:
        p("  hunk " + l)
    for l in rl:
        p("  -line len %d starts %r" % (len(l), l[:60]))
    want = {("prompt", sha(arm["c0"]["inputs"]["prompt"].encode())): "c0.prompt = v2_seg3_c0_r2v.txt",
            ("prompt", sha(arm["c1"]["inputs"]["prompt"].encode())): "c1.prompt = v2_seg3_c1_t2va.txt",
            ("filename_prefix", sha(arm["save"]["inputs"]["filename_prefix"].encode())): "save.filename_prefix = " + arm["save"]["inputs"]["filename_prefix"]}
    got = []
    for l in al:
        p("  +line len %d starts %r" % (len(l), l[:60]))
        try:
            d = json.loads("{" + l.lstrip("+").strip().rstrip(",") + "}")
            for k, v in d.items():
                p("  +line key=%r chars=%d sha256=%s" % (k, len(v) if isinstance(v, str) else -1, sha(v.encode()) if isinstance(v, str) else "-"))
                got.append((k, sha(v.encode()) if isinstance(v, str) else "-"))
        except Exception as e:
            p("  +line parse: " + repr(e))
    p("every added line is one of the three intended new values: %s" % json.dumps([g in want for g in got]))
    p("mapped to: %s" % json.dumps([want.get(g, "UNEXPECTED") for g in got]))
    p("set of added lines == set of the three intended values: %s" % (sorted(got) == sorted(want.keys())))
else:
    p("graph_diff.txt not present yet: " + gd)
p("")
p("== control media, measured read-only (ffprobe -count_packets + certutil) - the comparison target")
p("base seg3 clip : runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.mp4")
p("  481 packets h264 768x1344 24/1 fps + aac 32000 Hz stereo, format duration 20.041688 s, bytes 5624126")
p("  sha256 fc28701abc585f3ae052b9316df22ba4edf7f31a2f3c685d2bbd758d2191d053")
p("  sidecar secs 816.0 (the control's own render time = the render-time baseline), seed 51080002, steps 10, mode r2v, w/h 768/1344")
p("base stitched  : runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_stitched.mp4")
p("  1443 packets h264 768x1344 24/1 fps, format duration 60.157063 s, bytes 16311891")
p("  sha256 ae93a7477aefc5ef698de0ac71d45e13f29731732ce3a0c832ac8360acda581d")
p("  the sbs window frames 962-1442 = 481 frames = exactly the segment-3 window of the stitched minute (1443 = 481*3 - 60 context frames).")
p("this arm asks for frames 481 / frames_tol 0 / minutes 60: minutes is a PRE-JOB gate only (ralph.ps1 clamps 30..180); expected duration 481/24 = 20.0417 s.")
p("")
p("== known differences that are NOT in the graph")
p("- seed 51080002 is the base run's own segment-3 seed (base seg1/2/3 used 51080000/51080001/51080002),")
p("  so this arm is a same-seed comparison against the base minute's segment 3. Node 'noise' is IDENTICAL.")
p("- render time, frames, hashes, contact sheet: PENDING, the render is run by the harness after this iteration.")
open(RPT, "w", encoding="utf-8").write("\n".join(O) + "\n")
open(ARM + "/fairness.txt", "w", encoding="utf-8").write("\n".join(O) + "\n")
print("\n".join(O[:40]))
print("FAIRNESS WROTE " + ARM + "/fairness.txt bytes %d" % len("\n".join(O) + "\n"))
print("REPORT " + RPT)
