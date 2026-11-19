"""ALI-163 R6R (Derrick 2026-10-23 3:15 PM CT): rebuild the clip-3 (HC3 / pick GI173) graph under the NEW id
ali147_pool_hc_r3r_s51130003 and self-check it, so the one dead clip (r3 died rc=2 STATIC_FAIL c1.audio_vae)
can be re-requested. NO render and NO GPU call here; the p7/JOB_REQUEST.json is written by Forge right after
this prints ALL CHECKS PASS.

Base graph = runs/ali147_pool_hc_r6_s51130006/request.api.json = the R9 pair-arm graph that RENDERED ok=True
(objective.json frames 243, 1344x768, 24/1 fps, audio true, 10.125 s), so the c1.audio_vae defect that killed
r3 (2026-10-23 14:15 CT) is already gone in the base. Only the 6 per-clip keys change:
  c0.prompt, c1.prompt            -> notes/hc_r3_c0.txt / hc_r3_c1.txt (the R4G2 wording, unchanged text)
  img.image, img2.image           -> community/hc/HC3_w1_face.png / HC3_w2_face.png (the R4G2 face crops)
  noise.noise_seed                -> 51130003 (same seed as the dead r3; one seed per clip)
  save.filename_prefix            -> community/<new id>/<new id>
Everything else (26 nodes, sampling, geometry, audio path, continuation window) is byte-identical to the base;
check 3 lists the diff key by key, check 13 proves the base is a rendered ok=True arm.

Self-checks: 14 numbered checks, PASS/FAIL lines, exit 1 on any FAIL. Run: python ali163_hc_r6r_build.py
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok

W = r"C:\AI\community"
COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
APPROVED = r"C:\Users\derek\5slock\approved_characters"
RALPH = r"C:\Users\derek\5slock\ralph-community\ralph.ps1"
BUDGET = r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"
H3_SRC = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")
HC_DIR = os.path.join(COMFY, "input", "community", "hc")
DEAD_ID = "ali147_pool_hc_r3_s51130003"            # the spent id (has result.json ok=false rc=2)
BASE_ID = "ali147_pool_hc_r6_s51130006"            # rendered ok=True pair arm = the template
SRC = os.path.join(W, "runs", BASE_ID, "request.api.json")
ID, SEED = "ali147_pool_hc_r3r_s51130003", 51130003
CROPS = ["HC3_w1_face.png", "HC3_w2_face.png"]
BOXES = [[382, 0, 171, 240], [799, 228, 222, 204]]
PICK = ("GROK_IMAGINE_2026-10-19b", "GI173.jpg")
P0F, P1F = os.path.join(W, "notes", "hc_r3_c0.txt"), os.path.join(W, "notes", "hc_r3_c1.txt")
EXPECT_KEYS = {"c0": ["prompt"], "c1": ["prompt"], "img": ["image"], "img2": ["image"],
               "noise": ["noise_seed"], "save": ["filename_prefix"]}
# R4G2 budget gate for R6R only (Max 3:15 PM CT): request only if jobs < 36 and used_min < 485
JOB_GATE, MIN_GATE = 36, 485.0

DEF_HEAD = "<Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
DEF_TAIL = " is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
BIND1 = "<Subject 1> is the exact same woman shown in <Picture 1>"
BIND2 = "<Subject 2> is the exact same woman shown in <Picture 2>"
CLOSE = "in close-up"
FILLS = "the face fills"

fails, n_pass = [], 0


def ck(cond, msg):
    global n_pass
    print(("PASS " if cond else "FAIL ") + msg)
    if cond:
        n_pass += 1
    else:
        fails.append(msg)


def resolves(s):
    if s.endswith(" [output]"):
        return os.path.isfile(os.path.join(COMFY, "output", s[:-9].replace("/", "\\")))
    return os.path.isfile(os.path.join(COMFY, "input", s.replace("/", "\\")))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


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


def h3_schema():
    """{class: (required, optional)} from the ON-DISK H3 schema = the names run_graph_job.static_check reads
    from /object_info, so a graph passing check 12 cannot die on STATIC_FAIL rc=2 (no network). Only TOP-LEVEL
    io.X.Input(...) entries count (paren depth 1), so Autogrow template inputs stay out of the required set."""
    txt = open(H3_SRC, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'node_id="(\w+)",', txt):
        cls, start = m.group(1), m.end()
        end = txt.find("outputs=[", start)
        blk = txt[start:end if end > 0 else start + 4000]
        req, opt = set(), set()
        for im in re.finditer(r'io\.\w+\.Input\("(\w+)"', blk):
            pre = blk[:im.start()]
            if pre.count("(") - pre.count(")") + pre.count("[") - pre.count("]") != 1:
                continue
            a = _args(blk, im.end())
            (opt if "optional=True" in a else req).add(im.group(1))
        if req:
            out[cls] = (req, opt)
    return out


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


print("=" * 110)
print(f"R6R  {ID}  seed {SEED}  women 2  {' + '.join(CROPS)}  base {BASE_ID} (rendered ok=True)")

# ---- CHECK 1: budget gate (Max 3:15 PM CT: jobs < 36 and used_min < 485 for R6R) + harness caps 615/45 ----
b = json.load(open(BUDGET, encoding="utf-8"))
ck(float(b["jobs"]) < JOB_GATE and float(b["used_min"]) < MIN_GATE
   and float(b["cap_min"]) == 615 and int(b["job_cap"]) == 45,
   f"1 R6R budget gate OPEN: jobs {b['jobs']} < {JOB_GATE} and used_min {b['used_min']} < {MIN_GATE} "
   f"(harness caps {b['cap_min']} min / {b['job_cap']} jobs, updated {b['updated']})")

# ---- CHECK 2: the NEW id is free, no stray ralph-community\p7, no live JOB_REQUEST.json ----
jd = os.path.join(W, "p7", "jobs")
free = {
    "p7/jobs/<id>.result.json absent (the only gate that makes a request submittable)": not os.path.exists(os.path.join(jd, f"{ID}.result.json")),
    "runs/<id>/<id>.mp4 absent": not os.path.exists(os.path.join(W, "runs", ID, f"{ID}.mp4")),
    "runs/<id>/objective.json absent": not os.path.exists(os.path.join(W, "runs", ID, "objective.json")),
    "ComfyUI/output/community/<id> absent": not os.path.exists(os.path.join(COMFY, "output", "community", ID)),
    "no ralph-community/p7": not os.path.exists(r"C:\Users\derek\5slock\ralph-community\p7"),
    "p7/JOB_REQUEST.json absent (this pass writes it)": not os.path.exists(os.path.join(W, "p7", "JOB_REQUEST.json")),
}
ck(all(free.values()) and os.path.exists(os.path.join(jd, DEAD_ID + ".result.json")),
   f"2 new id free: {json.dumps(free)}; the OLD id {DEAD_ID} is spent (its result.json exists = "
   f"{os.path.exists(os.path.join(jd, DEAD_ID + '.result.json'))}), which is why R6R uses a new id")

# ---- CHECK 3: build, then structural diff vs the rendered base = ONLY the 6 per-clip keys ----
base = json.loads(open(SRC, encoding="utf-8").read().replace("\r\n", "\n"))
g = json.loads(json.dumps(base))
p0 = open(P0F, encoding="utf-8").read().rstrip("\n")
p1 = open(P1F, encoding="utf-8").read().rstrip("\n")
g["c0"]["inputs"]["prompt"] = p0
g["c1"]["inputs"]["prompt"] = p1
g["img"]["inputs"]["image"] = "community/hc/" + CROPS[0]
g["img2"]["inputs"]["image"] = "community/hc/" + CROPS[1]
g["noise"]["inputs"]["noise_seed"] = SEED
g["save"]["inputs"]["filename_prefix"] = f"community/{ID}/{ID}"
dst_dir = os.path.join(W, "runs", ID)
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, "request.api.json")
data = json.dumps(g, indent=1, ensure_ascii=True).replace("\n", "\r\n").encode("utf-8")
open(dst, "wb").write(data)
new = json.loads(open(dst, encoding="utf-8").read().replace("\r\n", "\n"))
same_ids = sorted(new) == sorted(base) and len(new) == 26
diff_nodes = sorted(k for k in set(base) | set(new)
                    if json.dumps(base.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True))
per_node_ok = all(sorted(k for k in set(base[n]["inputs"]) | set(new[n]["inputs"])
                          if json.dumps(base[n]["inputs"].get(k), sort_keys=True)
                          != json.dumps(new[n]["inputs"].get(k), sort_keys=True)) == EXPECT_KEYS[n]
                  for n in EXPECT_KEYS)
untouched = all(json.dumps(base[n], sort_keys=True) == json.dumps(new[n], sort_keys=True)
                for n in set(base) & set(new) - set(EXPECT_KEYS))
ck(same_ids and diff_nodes == sorted(EXPECT_KEYS) and per_node_ok and untouched,
   f"3 diff vs the rendered base {BASE_ID}: node id set identical (26 nodes), changed nodes {diff_nodes}, "
   f"per-node keys = exactly the 6 per-clip keys {json.dumps(EXPECT_KEYS)} ({per_node_ok}), "
   f"all other 20 nodes byte-identical ({untouched})")

# ---- CHECK 4: json parses (json.tool clone) + bytes/sha recorded ----
try:
    json.loads(data.decode("utf-8"))
    ok4 = True
except Exception as e:                                        # noqa: BLE001
    ok4 = False
    print("     " + str(e))
ck(ok4, f"4 json.tool-parses, {len(data)} bytes, sha256 {sha(dst)[:32]}... at runs\\{ID}\\request.api.json")

# ---- CHECK 5: geometry + the community length (243 f = c0 124 + win1 119 @ 24 fps = 10.125 s) ----
n0, ext = int(new["c0"]["inputs"]["length"]), int(new["win1"]["inputs"]["extension_frames"])
ck(new["c0"]["inputs"]["width"] == 1344 and new["c0"]["inputs"]["height"] == 768
   and new["c1"]["inputs"]["width"] == 1344 and new["c1"]["inputs"]["height"] == 768
   and n0 == 124 and ext == 119 and n0 + ext == 243 and int(new["win1"]["inputs"]["overlap_frames"]) == 22
   and int(new["mkvid"]["inputs"]["fps"]) == 24 and (n0 + ext) / 24.0 == 10.125
   and new["c1"]["inputs"]["length"] == ["win1", 1],
   f"5 1344x768 (16:9) in c0 and c1; c0 {n0} + win1.extension_frames {ext} = {n0 + ext} f (the R1 count) "
   f"@ 24 fps = {(n0 + ext) / 24.0} s, overlap 22, c1.length = [win1,1]")

# ---- CHECK 6: single pass + sampling fixed (no cfg key at all, denoise 1.0, euler/simple/10, shift 10/3) ----
fixed = (len([v for v in new.values() if v["class_type"] == "SamplerCustomAdvanced"]) == 2
         and not any(v["class_type"] == "KSamplerAdvanced" for v in new.values())
         and float(new["s0_sched"]["inputs"]["denoise"]) == 1.0 and float(new["s1_sched"]["inputs"]["denoise"]) == 1.0
         and new["ksel"]["inputs"]["sampler_name"] == "euler"
         and new["s0_sched"]["inputs"]["scheduler"] == "simple" and int(new["s0_sched"]["inputs"]["steps"]) == 10
         and new["s1_sched"]["inputs"]["scheduler"] == "simple" and int(new["s1_sched"]["inputs"]["steps"]) == 10
         and float(new["m_shift"]["inputs"]["shift_video"]) == 10.0
         and float(new["m_shift"]["inputs"]["shift_audio"]) == 3.0
         and new["unet"]["inputs"]["unet_name"].endswith("beta6_int8.safetensors")
         and new["m_vsa"]["inputs"]["selection"] == "vsa"
         and "cfg" not in json.dumps(new).lower()
         and not any(t in v["class_type"] for v in new.values() for t in ("RIFE", "Refine", "Upscale")))
ck(fixed, "6 single pass (exactly 2 SamplerCustomAdvanced, no KSamplerAdvanced/RIFE/refine/upscale), denoise 1.0 on "
          "s0_sched + s1_sched, euler/simple/10 steps, shift 10.0 video / 3.0 audio, beta6 int8, no cfg key anywhere")

# ---- CHECK 7: reference slots = the two HC3 face crops only; c1 has 0 refs and no audio_vae; avae feeds c0+dec_a ----
r0 = sorted(k for k in new["c0"]["inputs"] if k.startswith("ref_images"))
r1 = sorted(k for k in new["c1"]["inputs"] if k.startswith("ref_images"))
img_nodes = sorted(k for k, v in new.items() if v["class_type"] == "LoadImage")
avae_users = sorted(k for k, v in new.items() if any(isinstance(x, list) and x == ["avae", 0] for x in v["inputs"].values()))
ck(r0 == ["ref_images.ref_image_1", "ref_images.ref_image_2"]
   and new["c0"]["inputs"]["ref_images.ref_image_1"] == ["img", 0]
   and new["c0"]["inputs"]["ref_images.ref_image_2"] == ["img2", 0]
   and new["c0"]["inputs"]["ref_image_size"] == "match"
   and img_nodes == ["img", "img2"]
   and new["img"]["inputs"]["image"] == "community/hc/" + CROPS[0]
   and new["img2"]["inputs"]["image"] == "community/hc/" + CROPS[1]
   and all(resolves("community/hc/" + n) for n in CROPS)
   and new["c1"]["class_type"] == "MiniMaxH3ImageToVideo" and r1 == [] and "ref_image_size" not in new["c1"]["inputs"]
   and "audio_vae" not in new["c1"]["inputs"] and "audio_vae" in new["c0"]["inputs"]
   and avae_users == ["c0", "dec_a"] and "sheet" not in new,
   f"7 exactly 2 LoadImage refs: community/hc/{CROPS[0]} -> ref_image_1 (<Picture 1>), community/hc/{CROPS[1]} -> "
   f"ref_image_2 (<Picture 2>), ref_image_size match, both resolve inside ComfyUI\\input; c1 = "
   f"MiniMaxH3ImageToVideo with {len(r1)} reference images and NO audio_vae; avae feeds exactly {avae_users}; "
   f"no Klein/sheet node (F1)")

# ---- CHECK 8: the crops exist at 512 px, are the R4G2 cuts of the approved pick GI173.jpg, hashes ----
from PIL import Image
logtxt = open(os.path.join(W, "notes", "face_crop.log"), encoding="utf-8").read()
pick_src = os.path.join(APPROVED, PICK[0], PICK[1])
ok8, rows = os.path.isfile(pick_src), []
for n, box in zip(CROPS, BOXES):
    p = os.path.join(HC_DIR, n)
    line = [l for l in logtxt.splitlines() if "WROTE" in l and f"{n}\"" in l]
    rec = json.loads(line[-1].split(" WROTE ", 1)[1]) if line else {}
    with Image.open(p) as im:
        px = im.size
    good = (rec.get("ok") is True and rec.get("face_box") == box and rec.get("src", "").endswith(PICK[1])
            and rec.get("out_px") == 512 and px == (512, 512) and os.path.getsize(p) == rec.get("bytes"))
    ok8 &= good
    rows.append(f"{n} {px} src={os.path.basename(rec.get('src', '?'))} face_box={rec.get('face_box')} "
                f"sha256={sha(p)[:12]}")
ck(ok8, "8 both face crops are 512x512, logged by scripts/face_crop.py ok=True with the expected --box, source = "
        "the approved pick " + PICK[1] + f" (exists {os.path.isfile(pick_src)}): " + " | ".join(rows))

# ---- CHECK 9: prompt text byte-exact in the graph + v2 blocks + adults-only guard ----
ok9 = True
for nm, pr in (("c0", p0), ("c1", p1)):
    gpr = new[nm]["inputs"]["prompt"]
    ok9 &= (gpr == pr and len(pr) > 1500 and guard_ok(pr) and "overall_soundscape:" in pr
            and "non_diegetic_music:" in pr and "dynamic video, fluid natural motions" in pr.lower()
            and "subject_definitions:" in pr and not any(w in pr.lower() for w in ("minor", "teen", "school"))
            and ID not in pr)
ok9 &= all(h in p0 for h in ("summary:", "retention_analysis:", "detailed_description:"))
ok9 &= "integrated_multimodal_description:" in p1 and "first 5 seconds" in p1
ck(ok9, f"9 prompts byte-identical to notes\\hc_r3_c0.txt ({len(p0)} ch) + hc_r3_c1.txt ({len(p1)} ch), guard_ok True, "
        f"overall_soundscape: + non_diegetic_music: in c0, integrated_multimodal_description + first-5-seconds "
        f"binding in c1, subject_definitions opens both, zero youth-coded words, new id not in the prompt text")

# ---- CHECK 10: R4G2 identity wording (F2-F5 kept) + close-up beats + picture binding (the builder's check 8) ----
ok10 = DEF_HEAD in p0 and p0.count(DEF_TAIL) == 2 and BIND1 in p0 and BIND2 in p0
ok10 &= p1.count(BIND1) == 1 and "of the first 5 seconds of this clip" in p1
ok10 &= "carries no reference pictures at all" in p1
ok10 &= ("fully clothed" in p0 and FILLS in p0 and "tight close-up crop" in p0
         and ("face and her hair only" in p0 or "faces and the hair of the two women only" in p0))
ok10 &= p0.count(CLOSE) >= 2 and p1.count(CLOSE) >= 2
nsub0 = len(re.findall(r"^<Subject \d> is", p0, flags=re.M))
nsub1 = len(re.findall(r"^<Subject \d> is", p1, flags=re.M))
ok10 &= nsub0 == 2 and nsub1 == 2
pics0 = sorted(set(re.findall(r"<Picture (\d)>", p0)))
pics1 = sorted(set(re.findall(r"<Picture (\d)>", p1)))
ok10 &= pics0 == ["1", "2"] and pics1 == ["1"]
ok10 &= "photograph in <Picture 1> shows" not in p0 and "face is small in the frame" not in p0
for line in p0.splitlines() + p1.splitlines():
    if BIND1 in line or BIND2 in line:
        ok10 &= not re.search(r"bikini|lingerie|robe|dress|top|shirt|shorts|clothing|wear", line, re.I)
ck(ok10, f"10 F2-F5/R4G2 wording kept: {p0.count(DEF_TAIL)} extender-verbatim definition lines in c0, {BIND1} in c0 and "
         f"c1, {BIND2} in c0, c1 declares 0 reference pictures, picture = a tight close-up crop of face and hair only "
         f"(fully clothed source stated), close-up beats c0 {p0.count(CLOSE)} / c1 {p1.count(CLOSE)}, subjects c0 "
         f"{nsub0} c1 {nsub1}, <Picture> set c0 {pics0} c1 {pics1}, no garment word in any binding line")

# ---- CHECK 11: seed + save prefix + the id passes BOTH live ralph.ps1 gates ----
ps1 = open(RALPH, encoding="utf-8-sig").read()
gates = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ps1) if "ali147_pool" in p]
gate_ok = len(gates) >= 2 and all(re.match(gp, ID) for gp in gates)
ck(int(new["noise"]["inputs"]["noise_seed"]) == SEED
   and new["save"]["inputs"]["filename_prefix"] == f"community/{ID}/{ID}"
   and ID.endswith(f"_s{SEED}") and len(re.findall(r"^[a-z0-9_]+$", ID)) == 1 and gate_ok,
   f"11 noise_seed {SEED} (the same seed as the dead r3; one seed per clip, the harness redo would be seed+1), "
   f"prefix community/{ID}/{ID}, id charset ok, accepted by BOTH live ralph.ps1 id gates {gates}")

# ---- CHECK 12: offline static clone of run_graph_job.static_check (non-vacuous: it re-finds the r3 defect) ----
sch = h3_schema()
bad12 = scan(new, sch)
n_h3 = len([v for v in new.values() if v["class_type"] in sch])
dead = json.loads(open(os.path.join(W, "runs", DEAD_ID, "request.api.json"), encoding="utf-8").read())
bad_dead = scan(dead, sch)
ck(not bad12 and n_h3 >= 3 and "MiniMaxH3ImageToVideo" in sch
   and "audio_vae" in sch["MiniMaxH3ReferenceToVideo"][1]
   and "audio_vae" not in sch["MiniMaxH3ImageToVideo"][0] | sch["MiniMaxH3ImageToVideo"][1]
   and "c1.audio_vae: not an input of MiniMaxH3ImageToVideo" in bad_dead,
   f"12 static-input self-check vs the on-disk schema: {n_h3} H3 nodes, all input names legal + required inputs "
   f"present {bad12 or 'OK'}; not vacuous - it reproduces the exact defect that killed {DEAD_ID} at rc=2: {bad_dead}")

# ---- CHECK 13: the base arm is a rendered ok=True clip (243 f, 1344x768, audio), so its shape is proven ----
ob = json.load(open(os.path.join(W, "runs", BASE_ID, "objective.json"), encoding="utf-8"))
rb = json.load(open(os.path.join(jd, f"{BASE_ID}.result.json"), encoding="utf-8"))
a = ob["attempts"][-1]
ck(ob["ok"] is True and rb["ok"] is True and rb["rc"] == 0 and a["frames"] == 243 and a["w"] == 1344
   and a["h"] == 768 and a["fps"] == "24/1" and a["audio"] is True and a["duration"] == 10.125,
   f"13 template arm {BASE_ID} rendered ok=True rc=0, objective frames {a['frames']} {a['w']}x{a['h']} "
   f"{a['fps']} audio={a['audio']} {a['duration']} s in {a['secs']} s ({a['secs'] / 60.0:.1f} min) - a known-good shape")

# ---- CHECK 14: the dead r3 job is the only clip-3 record (STATIC_FAIL rc=2, no media) -> re-request is right ----
dr = json.load(open(os.path.join(jd, f"{DEAD_ID}.result.json"), encoding="utf-8"))
dstat = open(os.path.join(W, "runs", DEAD_ID, "status.log"), encoding="utf-8").read()
ck(dr["ok"] is False and dr["rc"] == 2 and "STATIC_FAIL" in dstat and "audio_vae" in dstat
   and not os.path.exists(os.path.join(W, "runs", DEAD_ID, f"{DEAD_ID}.mp4")),
   f"14 {DEAD_ID} = ok=false rc=2, status.log '{dstat.strip().splitlines()[-1]}' = a static-check death with NO "
   f"render and NO media, so the clip is missing from FINAL and needs the fixed graph under a new id")

print("=" * 110)
if fails:
    print("CHECKS FAIL " + json.dumps(fails))
    sys.exit(1)
print(f"ALL CHECKS PASS ({n_pass} PASS lines, 14 numbered checks)")
print(f"graph {dst} {len(data)} B sha256 {sha(dst)}")
