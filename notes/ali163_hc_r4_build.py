"""ALI-163 R4: build runs/ali147_pool_hc_r1_s51130001/request.api.json from the RS6 ref-sheet graph.

Copy of runs/ali147_pool_refsheet_b_s51080000/request.api.json with ONLY:
  new node "sheet2" (LoadImage, HC1_w2 sheet)
  c0: width 1344, height 768, prompt, length 124, ref_images (img, sheet, sheet2)
  c1: width 1344, height 768, prompt, ref_images (sheet, sheet2)
  win1: extension_frames 119
  img / sheet: image strings
  noise.noise_seed 51130001, save.filename_prefix
Self-checks: node/key-level diff, frame math, geometry, beta6 settings, sound lines,
guard_ok, live ralph.ps1 id gates, budget gate, id-free.
Idempotent: rebuilds from the RS6 source every run.
"""
import json, os, re, sys, hashlib
sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok

W = r"C:\AI\community"
SRC = os.path.join(W, "runs", "ali147_pool_refsheet_b_s51080000", "request.api.json")
ID = "ali147_pool_hc_r1_s51130001"
DST_DIR = os.path.join(W, "runs", ID)
DST = os.path.join(DST_DIR, "request.api.json")
P0 = os.path.join(W, "notes", "hc_r1_c0.txt")
P1 = os.path.join(W, "notes", "hc_r1_c1.txt")
IMG = "community/hc/HC1_Two_women_in_studio_editorial.jpg"
SH1 = "community/hc/HC1_w1_blonde_00001_.png"
SH2 = "community/hc/HC1_w2_darkhair_00001_.png"
SEED = 51130001
COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
fails = []

def ck(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

raw_src = open(SRC, "rb").read()
src_text = raw_src.decode("utf-8").replace("\r\n", "\n")
g = json.loads(src_text)
p0 = open(P0, encoding="utf-8").read().rstrip("\n")
p1 = open(P1, encoding="utf-8").read().rstrip("\n")
oldg = json.loads(src_text)

# ---- deltas ----
g["c0"]["inputs"]["width"] = 1344
g["c0"]["inputs"]["height"] = 768
g["c0"]["inputs"]["prompt"] = p0
g["c0"]["inputs"]["length"] = 124
g["c0"]["inputs"]["ref_images"] = {"ref_image_1": ["img", 0], "ref_image_2": ["sheet", 0],
                                   "ref_image_3": ["sheet2", 0]}
g["c1"]["inputs"]["width"] = 1344
g["c1"]["inputs"]["height"] = 768
g["c1"]["inputs"]["prompt"] = p1
g["c1"]["inputs"]["ref_images"] = {"ref_image_1": ["sheet", 0], "ref_image_2": ["sheet2", 0]}
g["win1"]["inputs"]["extension_frames"] = 119
g["img"]["inputs"]["image"] = IMG
g["sheet"]["inputs"]["image"] = SH1
g["sheet2"] = {"class_type": "LoadImage", "_meta": {"title": "Load Image (HC1_w2 darkhair sheet)"},
               "inputs": {"image": SH2}}
g["noise"]["inputs"]["noise_seed"] = SEED
g["save"]["inputs"]["filename_prefix"] = f"community/{ID}/{ID}"

os.makedirs(DST_DIR, exist_ok=True)
data = json.dumps(g, indent=1, ensure_ascii=True).replace("\n", "\r\n").encode("utf-8")
open(DST, "wb").write(data)

# ---- checks ----
new = json.loads(open(DST, encoding="utf-8").read().replace("\r\n", "\n"))
added = sorted(set(new) - set(oldg))
removed = sorted(set(oldg) - set(new))
ck(added == ["sheet2"], f"added nodes exactly [sheet2] -> {added}")
ck(removed == [], f"no nodes removed -> {removed}")
ck(len(new) == len(oldg) + 1 == 27, f"node count {len(new)} (base {len(oldg)} + 1)")
diff = sorted(k for k in set(oldg) | set(new)
              if json.dumps(oldg.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True))
ck(diff == ["c0", "c1", "img", "noise", "save", "sheet", "sheet2", "win1"], f"changed nodes -> {diff}")
EXPECT_KEYS = {"c0": ["height", "length", "prompt", "ref_images", "width"],
               "c1": ["height", "prompt", "ref_images", "width"],
               "win1": ["extension_frames"], "img": ["image"], "sheet": ["image"],
               "sheet2": ["image"], "noise": ["noise_seed"], "save": ["filename_prefix"]}
for nid, want in EXPECT_KEYS.items():
    obase = oldg.get(nid, {}).get("inputs", {})
    keys = sorted(k for k in set(obase) | set(new[nid]["inputs"])
                  if json.dumps(obase.get(k), sort_keys=True) != json.dumps(new[nid]["inputs"].get(k), sort_keys=True))
    ck(keys == want, f"{nid} changed input keys exactly {want} -> {keys}")
for nid in sorted(set(oldg) - set(EXPECT_KEYS)):
    ck(json.dumps(oldg[nid], sort_keys=True) == json.dumps(new[nid], sort_keys=True), f"{nid} untouched")

ck(new["c0"]["inputs"]["width"] == 1344 and new["c0"]["inputs"]["height"] == 768, "c0 1344x768 (16:9)")
ck(new["c1"]["inputs"]["width"] == 1344 and new["c1"]["inputs"]["height"] == 768, "c1 1344x768 (16:9)")
n0 = int(new["c0"]["inputs"]["length"]); ext = int(new["win1"]["inputs"]["extension_frames"])
ov = int(new["win1"]["inputs"]["overlap_frames"])
ck(n0 == 124 and ext == 119 and ov == 22, f"win1 plan: c0 {n0} + extension {ext} (overlap {ov})")
ck(n0 + ext == 243, f"job frames = c0.length + win1.extension_frames = {n0 + ext}")
ck(int(new["mkvid"]["inputs"]["fps"]) == 24, "fps 24 (no RIFE)")
ck((n0 + ext) / 24.0 == 10.125, f"duration (243/24) = {(n0+ext)/24.0} s")
ck(new["unet"]["inputs"]["unet_name"].endswith("beta6_int8.safetensors"), "beta6 int8 checkpoint")
ck(new["ksel"]["inputs"]["sampler_name"] == "euler" and new["s0_sched"]["inputs"]["scheduler"] == "simple"
   and int(new["s0_sched"]["inputs"]["steps"]) == 10, "euler / simple / 10 steps")
ck(float(new["m_shift"]["inputs"]["shift_video"]) == 10.0 and float(new["m_shift"]["inputs"]["shift_audio"]) == 3.0,
   "sigma shift 10 video / 3 audio")
ck(new["m_vsa"]["inputs"]["selection"] == "vsa", "video stride layer (vsa) kept")
ck(json.dumps(new["tail1"]["inputs"], sort_keys=True) == json.dumps(oldg["tail1"]["inputs"], sort_keys=True),
   "tail1 (video frame count) unchanged = base tail")
ctypes = sorted(v["class_type"] for v in new.values())
ck(not any("RIFE" in c or "Refine" in c or "Upscale" in c for c in ctypes), "no RIFE / refine / upscale nodes")
ck(new["c0"]["inputs"]["ref_image_size"] == "max" and new["c1"]["inputs"]["ref_image_size"] == "max",
   "c0 and c1 both MiniMaxH3ReferenceToVideo with ref_image_size max (face-locked, both chunks)")
ck(new["c0"]["class_type"] == "MiniMaxH3ReferenceToVideo" and new["c1"]["class_type"] == "MiniMaxH3ReferenceToVideo",
   "c0/c1 = MiniMaxH3ReferenceToVideo (the fix R2 named, RS6-proven)")
ck(new["c0"]["inputs"]["ref_images"] == {"ref_image_1": ["img", 0], "ref_image_2": ["sheet", 0],
                                         "ref_image_3": ["sheet2", 0]},
   "c0 slots: 1=pick, 2=w1 sheet, 3=w2 sheet")
ck(new["c1"]["inputs"]["ref_images"] == {"ref_image_1": ["sheet", 0], "ref_image_2": ["sheet2", 0]},
   "c1 slots: 1=w1 sheet, 2=w2 sheet (no start still in c1, as in RS6)")

def resolves(s):
    if s.endswith(" [output]"):
        return os.path.isfile(os.path.join(COMFY, "output", s[:-9].replace("/", "\\")))
    return os.path.isfile(os.path.join(COMFY, "input", s.replace("/", "\\")))
ck(resolves(new["img"]["inputs"]["image"]), f"img string resolves: {new['img']['inputs']['image']}")
ck(resolves(new["sheet"]["inputs"]["image"]), f"sheet string resolves: {new['sheet']['inputs']['image']}")
ck(resolves(new["sheet2"]["inputs"]["image"]), f"sheet2 string resolves: {new['sheet2']['inputs']['image']}")
for nm, s in (("sheet", SH1), ("sheet2", SH2)):
    ip = os.path.join(COMFY, "input", s.replace("/", "\\"))
    op = os.path.join(COMFY, "output", "community", "hc_sheets", os.path.basename(s))
    ck(hashlib.sha256(open(ip, "rb").read()).hexdigest() == hashlib.sha256(open(op, "rb").read()).hexdigest(),
       f"{nm} input copy is byte-identical to the rendered sheet png: {os.path.basename(s)}")
ck(os.path.isfile(os.path.join(COMFY, "input", IMG.replace("/", "\\"))), "placed pick is in ComfyUI\\input")
ck(json.dumps(new["noise"]["inputs"], sort_keys=True) == json.dumps(dict(noise_seed=SEED), sort_keys=True),
   f"noise node = noise_seed {SEED} only (one seed for the clip)")
ck(new["save"]["inputs"]["filename_prefix"] == f"community/{ID}/{ID}", "save.filename_prefix")
ck(len(re.findall(r"^[a-z0-9_]+$", ID)) == 1, "id charset")

ralph = open(r"C:\Users\derek\5slock\ralph-community\ralph.ps1", encoding="utf-8-sig").read()
pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
ck(len(pats) >= 2 and all(re.match(p, ID) for p in pats), f"live ralph.ps1 id regexes accept id -> {pats}")

for nm, pr in (("c0", p0), ("c1", p1)):
    ck("overall_soundscape:" in pr, f"{nm} has overall_soundscape: line")
    ck("non_diegetic_music:" in pr, f"{nm} has non_diegetic_music: line")
    ck("dynamic video, fluid natural motions" in pr.lower(), f"{nm} has the beta6 slow-motion phrase")
    ck(guard_ok(pr), f"{nm} guard_ok")
    ck("Minor" not in pr and "teen" not in pr.lower() and "school" not in pr.lower(), f"{nm} no youth-coded words")
    ck("minor" not in pr.lower(), f"{nm} word minor absent")
    if nm == "c0":
        ck(all(h in pr for h in ("subject_definitions:", "summary:", "retention_analysis:", "detailed_description:")),
           "c0 v2 sections present")
        for k, node in (("1", "img"), ("2", "sheet"), ("3", "sheet2")):
            ck(f"<Picture {k}>" in pr, f"c0 binds <Picture {k}> (slot k = {node})")
            ck(f"<Picture {k}>" in pr, f"c0 ordinal {k} used")
        ck("<Picture 4>" not in pr, "c0 no ordinal beyond its 3 slots")
    else:
        ck("integrated_multimodal_description:" in pr, "c1 integrated_multimodal_description: head")
        ck("subject_definitions:" in pr, "c1 restates subject_definitions")
        ck("<Picture 1>" in pr and "<Picture 2>" in pr, "c1 binds <Picture 1>/<Picture 2> to its 2 sheet slots")
        ck("<Picture 3>" not in pr, "c1 no ordinal beyond its 2 slots")
        ck("first 5 seconds" in pr, "c1 continues from the c0 chunk")
nsub0 = len(re.findall(r"^<Subject \d> is", p0, flags=re.M))
ck(nsub0 == 2, f"c0 defines 2 <Subject N> for the 2-woman pick -> {nsub0}")
ck(len(re.findall(r"^<Subject \d>", p1, flags=re.M)) == 2, "c1 restates 2 subjects")

budget = json.loads(open(r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json", encoding="utf-8").read())
cap_min = int(re.search(r"\$GpuCapMin=(\d+)", ralph).group(1))
job_max = int(re.search(r"\$JobMax=(\d+)", ralph).group(1))
ck(float(budget["used_min"]) <= 475 and int(budget["jobs"]) < 32,
   f"budget gate: used_min {budget['used_min']} <= 475, jobs {budget['jobs']} < 32 (live caps {cap_min}/{job_max})")
ck(not os.path.exists(os.path.join(W, "p7", "jobs", f"{ID}.result.json")), "id free: no p7\\jobs result.json")
ck(not os.path.exists(os.path.join(DST_DIR, "objective.json")), "id free: no objective.json")
ck(not os.path.exists(os.path.join(COMFY, "output", "community", ID)), "id free: no output folder")
ck(not os.path.exists(os.path.join(W, "p7", "JOB_REQUEST.json")), "no JOB_REQUEST.json already queued")

# ---- the request itself (only if every check passed) ----
if fails:
    print("CHECKS FAIL " + json.dumps(fails))
    sys.exit(1)

req = {"jobs": [{"id": ID, "kind": "graph", "frames": n0 + ext, "frames_tol": 0, "minutes": 60}]}
req_bytes = json.dumps(req, indent=1, ensure_ascii=True).replace("\n", "\r\n").encode("utf-8") + b"\r\n"
open(os.path.join(W, "p7", "JOB_REQUEST.json"), "wb").write(req_bytes)
print("graph bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())
print("request bytes", len(req_bytes), "sha256", hashlib.sha256(req_bytes).hexdigest())
print("c0 prompt chars", len(p0), "sha256", hashlib.sha256(p0.encode()).hexdigest())
print("c1 prompt chars", len(p1), "sha256", hashlib.sha256(p1.encode()).hexdigest())
print("JOB_REQUEST written:", open(os.path.join(W, "p7", "JOB_REQUEST.json"), "rb").read()[:400])
print("ALL CHECKS PASS")
