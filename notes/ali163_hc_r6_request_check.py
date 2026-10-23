#!/usr/bin/env python
# ALI-163 R6 (clip 3, pick HC3, id ali147_pool_hc_r3_s51130003) READ-ONLY request self-check.
# Verifies the graph R4G2 built (sha 15839d966d18) before the render request: no writes outside notes/.
import json, hashlib, os, re, sys
sys.path.insert(0, r"C:/AI/community/scripts")
from comm import guard_ok

DEF_HEAD = "<Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
BIND1 = "<Subject 1> is the exact same woman shown in <Picture 1>"
BIND2 = "<Subject 2> is the exact same woman shown in <Picture 2>"
CLOSE = "in close-up"
FILLS = "the face fills"

RUNS = r"C:/AI/community/runs"
NOTES = r"C:/AI/community/notes"
JOBS = r"C:/AI/community/p7/jobs"
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
COMFY_OUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output"
ID = "ali147_pool_hc_r3_s51130003"
SEED = 51130003
RUN = os.path.join(RUNS, ID)

gpath = os.path.join(RUN, "request.api.json")
raw = open(gpath, "rb").read()
g = json.loads(raw)
sha = hashlib.sha256(raw).hexdigest()

ok = 0
fails = []
def chk(cond, label, extra=""):
    global ok
    if cond:
        ok += 1
        print("PASS", label, extra)
    else:
        fails.append(label)
        print("FAIL", label, extra)

# 1 graph integrity
chk(sha == "15839d966d181b57b42fac95dd757c214e09cb4e58b8bf526b8f49d208caa663", "1 graph sha == R4G2 record", sha[:12])
chk(len(g) == 26, "2 node count 26 (RS6 26 - sheet + img2)", str(len(g)))

# 2 id free
chk(not os.path.exists(os.path.join(JOBS, ID + ".result.json")), "3 no p7 result.json")
chk(not os.path.exists(os.path.join(RUN, ID + ".mp4")), "4 no runs mp4")
chk(not os.path.exists(os.path.join(RUN, "objective.json")), "5 no objective.json")
chk(not os.path.exists(os.path.join(COMFY_OUT, "community", ID)), "6 no output folder")
chk(not os.path.exists(r"C:/AI/community/p7/JOB_REQUEST.json"), "7 JOB_REQUEST.json absent")

# 3 geometry / length
c0, c1, win1, mkvid, save = g["c0"], g["c1"], g["win1"], g["mkvid"], g["save"]
chk(c0["inputs"]["width"] == 1344 and c0["inputs"]["height"] == 768, "8 c0 1344x768")
chk(c1["inputs"]["width"] == 1344 and c1["inputs"]["height"] == 768, "9 c1 1344x768")
chk(c0["inputs"]["length"] == 124, "10 c0 length 124", str(c0["inputs"]["length"]))
chk(win1["inputs"]["extension_frames"] == 119, "11 win1 extension_frames 119")
chk(124 + 119 == 243, "12 total frames 243 (R1 count)")
chk(mkvid["inputs"]["fps"] == 24, "13 fps 24")
chk(round(243 / 24.0, 3) == 10.125, "14 duration 10.125 s")

# 4 sampling (single pass, community settings)
types = {k: v.get("class_type") for k, v in g.items()}
samplers = sorted([k for k, t in types.items() if t == "SamplerCustomAdvanced"])
chk(samplers == ["s0_samp", "s1_samp"], "15 exactly 2 SamplerCustomAdvanced = single pass", str(samplers))
for n in ("s0_sched", "s1_sched"):
    chk(g[n]["inputs"]["denoise"] == 1.0, f"16 {n} denoise 1.0")
    chk(g[n]["inputs"]["steps"] == 10, f"17 {n} steps 10")
    chk(g[n]["inputs"]["scheduler"] == "simple", f"18 {n} scheduler simple")
chk(g["ksel"]["inputs"]["sampler_name"] == "euler", "19 sampler euler")
chk(g["m_shift"]["inputs"]["shift_video"] == 10.0 and g["m_shift"]["inputs"]["shift_audio"] == 3.0, "20 shift 10/3")
chk(g["unet"]["inputs"]["unet_name"] == "10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors", "21 unet beta6 int8")
chk("cfg" not in raw.decode("utf-8", "ignore").lower().replace("safetensors", ""), "22 no cfg key in graph")
chk(types["c1"] == "MiniMaxH3ImageToVideo", "23 c1 MiniMaxH3ImageToVideo (continuation)", types["c1"])
chk("ref_image_size" not in c1["inputs"], "24 c1 has no ref_image_size key")
chk(c0["inputs"]["ref_image_size"] == "match", "25 c0 ref_image_size match")

# 5 reference slots = the two face crops, resolved inside ComfyUI input, NO Klein sheet anywhere
refs = {k: v for k, v in g.items() if types[k] == "LoadImage"}
chk(sorted(refs) == ["img", "img2"], "26 exactly 2 LoadImage nodes", str(sorted(refs)))
flat = {k: v for k, v in c0["inputs"].items() if re.fullmatch(r"ref_images\.ref_image_\d+", k)}
chk(len(flat) == 2, "27 c0 carries 2 ref slots", str(len(flat)))
slotfiles = []
for k in sorted(flat):
    v = flat[k]
    src = v[0] if isinstance(v, list) and v else None
    if src in g and types.get(src) == "LoadImage":
        slotfiles.append(g[src]["inputs"]["image"])
    else:
        slotfiles.append(str(v))
chk(slotfiles == ["community/hc/HC3_w1_face.png", "community/hc/HC3_w2_face.png"],
    "28 ref slots = HC3_w1_face + HC3_w2_face", str(slotfiles))
for nm in slotfiles:
    p = os.path.join(COMFY_IN, nm.replace("/", os.sep))
    chk(os.path.isfile(p), f"29 LoadImage resolves in ComfyUI input: {nm}", str(os.path.getsize(p)) if os.path.isfile(p) else "MISSING")
    if os.path.isfile(p):
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        sz = "?"
        try:
            from PIL import Image
            sz = "x".join(str(x) for x in Image.open(p).size)
        except Exception as e:
            sz = f"PIL fail {e}"
        chk(sz == "512x512", f"29b {nm} is 512x512", sz)
        print("     sha256", nm, h)
chk(not any("sheet" in json.dumps(v["inputs"]).lower() for v in g.values()), "30 no Klein sheet reference anywhere")
chk(types["img"] == "LoadImage" and g["img"]["inputs"]["image"] == "community/hc/HC3_w1_face.png", "31 img node = HC3_w1_face")
chk(types["img2"] == "LoadImage" and g["img2"]["inputs"]["image"] == "community/hc/HC3_w2_face.png", "32 img2 node = HC3_w2_face")

# 6 prompt text: F1-F5 (subject_definitions both chunks, face/hair-only binding, close-up beat, soundscape)
p0, p1 = c0["inputs"]["prompt"], c1["inputs"]["prompt"]
chk(p0.strip().startswith("subject_definitions") or "subject_definitions" in p0.split("\n")[0], "33 c0 opens with subject_definitions")
chk("subject_definitions" in p1, "34 c1 carries subject_definitions")
chk("youth" not in (p0 + p1).lower() and not re.search(r"\b(teen|teenage|minor|underage|schoolgirl|loli)\b", (p0 + p1).lower()), "33b no youth-coded words in either prompt")
chk(DEF_HEAD in p0 and BIND1 in p0 and BIND2 in p0, "35 c0 verbatim definition + both pair bindings")
chk(BIND1 in p1, "36 c1 binds Subject 1 to Picture 1 of the earlier segment")
chk("tight close-up crop" in p0 and FILLS in p0 and "faces and hair only" in p0.replace("the faces and the hair", "faces and hair only") or ("close-up crop" in p0 and FILLS in p0), "37 c0 picture = close-up crop, face fills, face/hair only")
chk(p0.count(CLOSE) >= 2, "38 c0 close-up camera beats >= 2 (one per woman)", str(p0.count(CLOSE)))
chk(p1.count(CLOSE) >= 2, "39 c1 close-up camera beats >= 2", str(p1.count(CLOSE)))
chk("overall_soundscape:" in p0, "40 c0 overall_soundscape:")
chk("non_diegetic_music" in p0, "41 c0 non_diegetic_music")
chk("overall_soundscape:" in p1 and "integrated_multimodal_description" in p1, "42 c1 integrated_multimodal_description + soundscape")
chk("first 5 seconds" in p1 or "opening five seconds" in p1, "43 c1 binds to the first 5 seconds")
chk("validated" not in json.dumps(g), "44 no MiniMaxH3 clips_json validated flag in this graph")

# 7 prompt files exist with guard_ok, and they match the graph text
for nm, graph_txt in (("hc_r3_c0.txt", p0), ("hc_r3_c1.txt", p1)):
    fp = os.path.join(NOTES, nm)
    chk(os.path.isfile(fp), f"45 prompt file {nm}")
    if os.path.isfile(fp):
        txt = open(fp, encoding="utf-8").read().rstrip("\n")
        chk(guard_ok(txt), f"46 {nm} guard_ok True (scripts/comm.py)", f"{len(txt)} ch")
        chk(txt == graph_txt, f"47 {nm} text == graph prompt", f"{len(txt)} vs {len(graph_txt)} ch")
chk(guard_ok(p0) and guard_ok(p1), "48 graph prompts pass the adults-only guard")

# 8 seed + save prefix
chk(g["noise"]["inputs"]["noise_seed"] == SEED, "49 noise_seed 51130003", str(g["noise"]["inputs"]["noise_seed"]))
chk(save["inputs"]["filename_prefix"] == f"community/{ID}/{ID}", "50 save prefix", save["inputs"]["filename_prefix"])

# 9 id gates copied verbatim from ralph.ps1 (lines 199 and 280)
gates = [r"^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\d+)$",
         r"^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\d+$"]
for i, pat in enumerate(gates):
    chk(re.match(pat, ID) is not None, f"51.{i} ralph.ps1 id gate {i+1} accepts {ID}")

# 10 budget gate (TASKS.md R3-R9 gate: used_min >= 475 or jobs >= 35 -> no request)
b = json.loads(open(r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json", encoding="utf-8").read())
chk(b["used_min"] < 475 and b["jobs"] < 35, "52 budget gate open", f"used_min {b['used_min']}/{b['cap_min']} jobs {b['jobs']}/{b['job_cap']}")

print("RESULT", "ALL CHECKS PASS" if not fails else f"{len(fails)} FAIL: {fails}", f"({ok} PASS lines)")
sys.exit(0 if not fails else 1)
