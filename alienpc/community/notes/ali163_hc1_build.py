"""ALI-163 HC1: build runs/ali147_pool_hc_c1_s51100001/request.api.json from the PV2 graph.

Copy of runs/ali147_pool_promptv2_s51080000/request.api.json with ONLY:
  c0.width 1344, c0.height 768, c0.prompt, c1.width 1344, c1.height 768, c1.prompt,
  img.image, noise.noise_seed, save.filename_prefix
Self-checks: node-level diff set, guard_ok on both prompts, sound line, budget/id gates parsed live.
Idempotent: rebuilds from the PV2 source every run.
"""
import json, os, re, sys, hashlib, subprocess
sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok

W = r"C:\AI\community"
SRC = os.path.join(W, "runs", "ali147_pool_promptv2_s51080000", "request.api.json")
ID = "ali147_pool_hc_c1_s51100001"
DST_DIR = os.path.join(W, "runs", "ali147_pool_hc_c1_s51100001")
DST = os.path.join(DST_DIR, "request.api.json")
P0 = os.path.join(W, "notes", "hc_c1_c0.txt")
P1 = os.path.join(W, "notes", "hc_c1_c1.txt")
IMG = "community/hc/HC1_Two_women_in_studio_editorial.jpg"
INPUT_IMG = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc\HC1_Two_women_in_studio_editorial.jpg"
SEED = 51100001
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
old = {k: json.dumps(v, sort_keys=True) for k, v in oldg.items()}
g["c0"]["inputs"]["width"] = 1344
g["c0"]["inputs"]["height"] = 768
g["c0"]["inputs"]["prompt"] = p0
g["c1"]["inputs"]["width"] = 1344
g["c1"]["inputs"]["height"] = 768
g["c1"]["inputs"]["prompt"] = p1
g["img"]["inputs"]["image"] = IMG
g["noise"]["inputs"]["noise_seed"] = SEED
g["save"]["inputs"]["filename_prefix"] = f"community/{ID}/{ID}"
out = json.dumps(g, indent=1, ensure_ascii=True) + "\n"
data = out.replace("\n", "\r\n").encode("utf-8")
os.makedirs(DST_DIR, exist_ok=True)
open(DST, "wb").write(data)

# ---- checks ----
new = json.loads(open(DST, encoding="utf-8").read().replace("\r\n", "\n"))
diff = sorted(k for k in set(oldg) | set(new) if json.dumps(oldg.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True))
ck(diff == ["c0", "c1", "img", "noise", "save"], f"changed nodes exactly c0,c1,img,noise,save -> {diff}")
for nid in ("c0", "c1"):
    keys = sorted(k for k in set(oldg[nid]["inputs"]) | set(new[nid]["inputs"])
                  if json.dumps(oldg[nid]["inputs"].get(k), sort_keys=True) != json.dumps(new[nid]["inputs"].get(k), sort_keys=True))
    ck(keys == ["height", "prompt", "width"], f"{nid} changed input keys exactly height/prompt/width -> {keys}")
ck(new["c0"]["inputs"]["width"] == 1344 and new["c0"]["inputs"]["height"] == 768, "c0 1344x768 (16:9)")
ck(new["c1"]["inputs"]["width"] == 1344 and new["c1"]["inputs"]["height"] == 768, "c1 1344x768 (16:9)")
ck(new["c0"]["inputs"]["length"] == 243 and new["win1"]["inputs"]["extension_frames"] == 238
   and new["win1"]["inputs"]["overlap_frames"] == 22 and new["mkvid"]["inputs"]["fps"] == 24,
   "length 243 + win1 238/22 = 481 frames, fps 24 unchanged")
ck(new["unet"]["inputs"]["unet_name"].endswith("beta6_int8.safetensors")
   and new["ksel"]["inputs"]["sampler_name"] == "euler"
   and new["s0_sched"]["inputs"]["scheduler"] == "simple" and new["s0_sched"]["inputs"]["steps"] == 10
   and new["m_shift"]["inputs"]["shift_video"] == 10.0 and new["m_shift"]["inputs"]["shift_audio"] == 3.0
   and new["m_vsa"]["inputs"]["selection"] == "vsa", "unet/euler/simple/10/shift 10-3/VSA unchanged")
ck(new["img"]["inputs"]["image"] == IMG and os.path.exists(INPUT_IMG), f"img string + placed file exist: {IMG}")
ck(json.dumps(new["img"]["inputs"], sort_keys=True) == json.dumps(dict(image=IMG), sort_keys=True), "img node has only image key")
ck(new["noise"]["inputs"]["noise_seed"] == SEED, f"noise_seed {SEED}")
ck(new["save"]["inputs"]["filename_prefix"] == f"community/{ID}/{ID}", "save.filename_prefix")
ck(len(re.findall(r"^[a-z0-9_]+$", ID)) == 1, "id charset")
ck(re.match(r"^ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\d+$", ID) is not None, "id matches known ralph.ps1 shape (verify live below)")
ralph = open(r"C:\Users\derek\5slock\ralph-community\ralph.ps1", encoding="utf-8-sig").read()
pats = [p for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
pats = [p.split("'", 2)[1] for p in pats]
ck(len(pats) >= 2 and all(re.match(p, ID) for p in pats), f"live ralph.ps1 id regexes accept id -> {pats}")
for nm, pr in (("c0", p0), ("c1", p1)):
    ck("overall_soundscape:" in pr, f"{nm} has overall_soundscape: line")
    ck("summary:" in pr if nm == "c0" else "integrated_multimodal_description:" in pr, f"{nm} v2 structure head")
    ck("non_diegetic_music:" in pr, f"{nm} has non_diegetic_music: line")
    ck("dynamic video, fluid natural motions" in pr or "dynamic video, fluid natural motions" in pr.lower(),
       f"{nm} has beta6 slow-motion phrase")
    ck(guard_ok(pr), f"{nm} guard_ok")
    ck(sum(1 for L in pr.split("\n") if L.strip()) >= (5 if nm == "c0" else 3), f"{nm} section count")
budget = json.loads(open(r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json", encoding="utf-8").read())
cap_min = int(re.search(r"\$GpuCapMin=(\d+)", ralph).group(1))
job_max = int(re.search(r"\$JobMax=(\d+)", ralph).group(1))
ck(float(budget["used_min"]) <= 475 and int(budget["jobs"]) < 32,
   f"budget gate (TASKS rule): used_min {budget['used_min']} <= 475, jobs {budget['jobs']} < 32 (live caps {cap_min}/{job_max})")
ck(not os.path.exists(os.path.join(W, "p7", "jobs", f"{ID}.result.json")), "id free: no p7\\jobs result.json")
ck(not os.path.exists(os.path.join(DST_DIR, "objective.json")), "id free: no objective.json")
mp4 = os.path.join(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output", "community", ID)
ck(not os.path.exists(mp4), "id free: no output folder")
print("graph bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())
print("c0 prompt chars", len(p0), "sha256", hashlib.sha256(p0.encode()).hexdigest())
print("c1 prompt chars", len(p1), "sha256", hashlib.sha256(p1.encode()).hexdigest())
print("ALL CHECKS PASS" if not fails else "CHECKS FAIL " + json.dumps(fails))
