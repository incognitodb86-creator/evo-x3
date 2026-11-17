#!/usr/bin/env python
# ALI-163 R8 (clip 5, pick HC5 = spicy_solo / GI150, id ali147_pool_hc_r5_s51130005) READ-ONLY request self-check.
# Pattern = notes/ali163_hc_r6_request_check.py (R6, 63 PASS) adapted to the single-woman arm, plus
# check 53 = the structural diff against the ALREADY-RENDERED-OK r4 graph (same single-ref shape),
# which must list ONLY the intended keys (c0.prompt, c1.prompt, img.image, noise.noise_seed, save prefix).
# Verifies the rebuilt graph (the R7 pass fixed the rc=2 c1.audio_vae defect): no writes outside notes/.
import json, hashlib, os, re, sys
sys.path.insert(0, r"C:/AI/community/scripts")
from comm import guard_ok

# --- h3_schema / _args / scan copied VERBATIM from notes/ali163_hc_r4g2_build.py (that module runs its builder on
# import, so it must NOT be imported; these three are read-only) ---
H3_SRC = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_minimax_h3.py"


def h3_schema():
    txt = open(H3_SRC, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'node_id="(\w+)",', txt):
        cls, start = m.group(1), m.end()
        end = txt.find("outputs=[", start)
        blk = txt[start:end if end > 0 else start + 4000]
        req, opt = set(), set()
        for im in re.finditer(r'io\.\w+\.Input\("(\w+)"', blk):
            pre = blk[:im.start()]
            depth = pre.count("(") - pre.count(")") + pre.count("[") - pre.count("]")
            if depth != 1:
                continue
            args = _args(blk, im.end())
            (opt if "optional=True" in args else req).add(im.group(1))
        if req:
            out[cls] = (req, opt)
    return out


def _args(txt, i):
    depth, j = 0, i
    while j < len(txt):
        if txt[j] == "(":
            depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0:
                return txt[i + 1:j]
        j += 1
    return txt[i:]


def scan(g, sch):
    bad = []
    for nid, n in sorted(g.items()):
        ct = n["class_type"]
        if ct not in sch:
            continue
        names = sch[ct][0] | sch[ct][1]
        keys = {k.split(".")[0] for k in n["inputs"]}
        bad += [f"{nid}.{k}: not an input of {ct}" for k in sorted(keys - names)]
        bad += [f"{nid}: required input {r} missing" for r in sorted(sch[ct][0])
                if r not in n["inputs"] and not any(a.startswith(r + ".") for a in n["inputs"])]
    return bad

DEF_HEAD = "<Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
BIND1 = "<Subject 1> is the exact same woman shown in <Picture 1>"
CLOSE = "in close-up"
FILLS = "the face fills"

RUNS = r"C:/AI/community/runs"
NOTES = r"C:/AI/community/notes"
JOBS = r"C:/AI/community/p7/jobs"
COMFY_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
COMFY_OUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output"
ID = "ali147_pool_hc_r5_s51130005"
SEED = 51130005
RUN = os.path.join(RUNS, ID)
REFS = ["community/hc/HC5_w1_face.png"]          # single-woman pick HC5 = GI150.jpg (one face crop, R4G2)
GOOD = os.path.join(RUNS, "ali147_pool_hc_r4_s51130004", "request.api.json")  # rendered ok=True, 1 ref
SHA_R5 = "995ba1c7232f30a26afcd4c88d71d0c3427d5f61af9ca353ff1941105849cf9e"   # R7 rebuild record

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

raw = open(os.path.join(RUN, "request.api.json"), "rb").read()
g = json.loads(raw)
sha = hashlib.sha256(raw).hexdigest()

# 1 graph integrity
chk(sha == SHA_R5, "1 graph sha == R7-rebuild record", sha[:12])
chk(len(g) == 25, "2 node count 25 (RS6 26 - sheet + img2, single-woman arm)", str(len(g)))

# 2 id free
chk(not os.path.exists(os.path.join(JOBS, ID + ".result.json")), "3 no p7 result.json")
chk(not os.path.exists(os.path.join(RUN, ID + ".mp4")), "4 no runs mp4")
chk(not os.path.exists(os.path.join(RUN, "objective.json")), "5 no objective.json")
chk(not os.path.exists(os.path.join(COMFY_OUT, "community", ID)), "6 no output folder")
chk(not os.path.exists(r"C:/AI/community/p7/JOB_REQUEST.json"), "7 JOB_REQUEST.json absent")
chk(not os.path.exists(r"C:/Users/derek/5slock/ralph-community/p7"), "7b no stray ralph-community/p7")

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

# 5 reference slots = the one face crop, resolved inside ComfyUI input, NO Klein sheet anywhere
refs = {k: v for k, v in g.items() if types[k] == "LoadImage"}
chk(sorted(refs) == ["img"], "26 exactly 1 LoadImage node (single-woman pick)", str(sorted(refs)))
flat = {k: v for k, v in c0["inputs"].items() if re.fullmatch(r"ref_images\.ref_image_\d+", k)}
chk(len(flat) == 1, "27 c0 carries 1 ref slot", str(len(flat)))
slotfiles = []
for k in sorted(flat):
    v = flat[k]
    src = v[0] if isinstance(v, list) and v else None
    slotfiles.append(g[src]["inputs"]["image"] if src in g and types.get(src) == "LoadImage" else str(v))
chk(slotfiles == REFS, "28 ref slot = HC5_w1_face", str(slotfiles))
chk(sorted(c1["inputs"]) == ["clip", "height", "length", "prompt", "vae", "width"],
    "28b c1 inputs = clip/height/length/prompt/vae/width (0 refs, NO audio_vae)", str(sorted(c1["inputs"])))
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
imgvals = [str(v["inputs"].get("image", "")) for v in g.values() if str(v.get("class_type", "")).startswith("LoadImage")]
chk(not any("sheet" in s.lower() or "klein" in s.lower() for s in imgvals),
    "30 no Klein/sheet reference in any image node", str(imgvals))
chk("hc_sheets" not in json.dumps(g) and "Klein" not in json.dumps(g), "30b no sheet path anywhere in the graph")
chk(types["img"] == "LoadImage" and g["img"]["inputs"]["image"] == REFS[0], "31 img node = HC5_w1_face")

# 6 prompt text: F1-F5 (subject_definitions both chunks, face/hair-only binding, close-up beat, soundscape)
p0, p1 = c0["inputs"]["prompt"], c1["inputs"]["prompt"]
chk(p0.split("\n")[0].startswith("subject_definitions"), "33 c0 opens with subject_definitions")
chk("subject_definitions" in p1, "34 c1 carries subject_definitions")
chk("youth" not in (p0 + p1).lower() and not re.search(r"\b(teen|teenage|minor|underage|schoolgirl|loli)\b", (p0 + p1).lower()), "33b no youth-coded words in either prompt")
chk(DEF_HEAD in p0 and BIND1 in p0, "35 c0 verbatim definition + Subject 1 binding")
chk(BIND1 in p1, "36 c1 binds Subject 1 to Picture 1 of the earlier segment")
chk(("close-up crop" in p0 and FILLS in p0) or ("tight close-up crop" in p0 and FILLS in p0), "37 c0 picture = close-up crop, face fills")
chk(p0.count(CLOSE) >= 1, "38 c0 close-up camera beats >= 1", str(p0.count(CLOSE)))
chk(p1.count(CLOSE) >= 1, "39 c1 close-up camera beats >= 1", str(p1.count(CLOSE)))
chk("overall_soundscape:" in p0, "40 c0 overall_soundscape:")
chk("non_diegetic_music" in p0, "41 c0 non_diegetic_music")
chk("overall_soundscape:" in p1 and "integrated_multimodal_description" in p1, "42 c1 integrated_multimodal_description + soundscape")
chk("first 5 seconds" in p1 or "opening five seconds" in p1, "43 c1 binds to the first 5 seconds")
chk("validated" not in json.dumps(g), "44 no MiniMaxH3 clips_json validated flag in this graph")

# 7 prompt files exist with guard_ok, and they match the graph text
for nm, graph_txt in (("hc_r5_c0.txt", p0), ("hc_r5_c1.txt", p1)):
    fp = os.path.join(NOTES, nm)
    chk(os.path.isfile(fp), f"45 prompt file {nm}")
    if os.path.isfile(fp):
        txt = open(fp, encoding="utf-8").read().rstrip("\n")
        chk(guard_ok(txt), f"46 {nm} guard_ok True", f"{len(txt)} ch")
        chk(txt == graph_txt, f"47 {nm} text == graph prompt", f"{len(txt)} vs {len(graph_txt)} ch")
chk(guard_ok(p0) and guard_ok(p1), "48 graph prompts pass the adults-only guard")

# 8 seed + save prefix
chk(g["noise"]["inputs"]["noise_seed"] == SEED, "49 noise_seed 51130005", str(g["noise"]["inputs"]["noise_seed"]))
chk(save["inputs"]["filename_prefix"] == f"community/{ID}/{ID}", "50 save prefix", save["inputs"]["filename_prefix"])

# 9 id gates copied verbatim from ralph.ps1 (lines 199 and 280)
gates = [r"^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\d+)$",
         r"^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\d+$"]
for i, pat in enumerate(gates):
    chk(re.match(pat, ID) is not None, f"51.{i} ralph.ps1 id gate {i+1} accepts {ID}")

# 10 budget gate (TASKS.md R3-R9 gate: used_min >= 475 or jobs >= 35 -> no request)
_bp = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"; b = json.loads(open(_bp, encoding="utf-8").read()) if __import__("os").path.exists(_bp) else None  # Max2 audit-fix #2: budget retired (17e932f), missing file = no block
chk(b is None or (b["used_min"] < 475 and b["jobs"] < 35), "52 budget gate open", "budget gate retired (17e932f): no p7_budget.json" if b is None else f"used_min {b['used_min']}/{b['cap_min']} jobs {b['jobs']}/{b['job_cap']}")

# 11 offline clone of run_graph_job.static_check (on-disk H3 schema, no network)
sch = h3_schema()
bad = scan(g, sch)
chk(not bad, "53a static_check clone: all H3 inputs legal + required present", str(bad[:3]))
chk("audio_vae" not in sch["MiniMaxH3ImageToVideo"][0] | sch["MiniMaxH3ImageToVideo"][1]
    and "audio_vae" in sch["MiniMaxH3ReferenceToVideo"][1], "53b schema clone is not vacuous (ImageToVideo has no audio_vae, ReferenceToVideo does)")
avae = [k for k, v in g.items() if any((isinstance(x, list) and x and x[0] == "avae") or x == "avae" for x in v["inputs"].values())]
chk(sorted(avae) == ["c0", "dec_a"], "53c avae feeds exactly c0 + dec_a", str(sorted(avae)))

# 12 structural diff vs the r4 graph that rendered ok=True (same single-ref arm): intended keys ONLY
g4 = json.loads(open(GOOD, "rb").read())
diff = set()
for k in sorted(set(g) | set(g4)):
    if k not in g or k not in g4:
        diff.add(k + ":node")
    elif g[k]["class_type"] != g4[k]["class_type"]:
        diff.add(k + ":class")
    else:
        for inp in sorted(set(g[k]["inputs"]) | set(g4[k]["inputs"])):
            if g[k]["inputs"].get(inp) != g4[k]["inputs"].get(inp):
                diff.add(f"{k}.{inp}")
want = {"c0.prompt", "c1.prompt", "img.image", "noise.noise_seed", "save.filename_prefix"}
chk(diff == want, "54 diff vs rendered r4 graph = only the 5 intended keys", str(sorted(diff - want)) + " extra / " + str(sorted(want - diff)) + " missing")

# 13 graph is loadable JSON with the same key set as r4 (no orphan links)
chk(set(g) == set(g4), "55 node id set == r4's", str(sorted(set(g) ^ set(g4))))
links = [f"{k}.{i} -> {x[0]}" for k, v in g.items() for i, x in v["inputs"].items()
         if isinstance(x, list) and len(x) == 2 and isinstance(x[0], str) and x[0] not in g]
chk(not links, "56 all link inputs resolve to a node in this graph", str(links[:3]))

print("RESULT", "ALL CHECKS PASS" if not fails else f"{len(fails)} FAIL: {fails}", f"({ok} PASS lines)")
sys.exit(0 if not fails else 1)
