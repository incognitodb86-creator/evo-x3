"""ALI-163 R4G: build the R6-R9 graphs (pick-only reference, no Klein sheets) - NO render, NO JOB_REQUEST.

Base graph = the graph R2 named: runs/ali147_pool_refsheet_b_s51080000/request.api.json (RS6, ref-sheet, 26 nodes).

Deltas per clip (nothing else changes):
  node "sheet"  : removed (the Klein multi-view sheet is gone from BOTH chunks; R5's "sheet2" is not in this base)
  c0 : MiniMaxH3ReferenceToVideo; width 1344, height 768, length 124, prompt hc_r<n>_c0.txt,
       ref_image_size "match", ref_images.ref_image_1 = [img,0] (the approved pick), ref_images.ref_image_2 removed
  c1 : class MiniMaxH3ImageToVideo; width 1344, height 768, length = [win1,1], prompt hc_r<n>_c1.txt,
       ref_image_size and every ref_images.* key removed  -> 0 reference images in the continuation chunk
  win1: extension_frames 119   (c0 124 + 119 = 243 frames = the R1 frame count, 24 fps, 10.125 s)
  img : image = community/hc/<pick file>
  noise: noise_seed = the clip seed ; save: filename_prefix = community/<id>/<id>

Sampling / geometry / audio path stay exactly as in the base (beta6 int8, euler/simple/10 steps, shift 10/3,
vsa, single pass, 24 fps, audio VAE + audio decoder wired).

Self-check: 9 numbered checks, printed PASS/FAIL; exits 1 on any FAIL. Writes only
runs/<id>/request.api.json. It never writes p7/JOB_REQUEST.json (R4G asks for no render).
Usage: python ali163_hc_r4g_build.py            (all four clips)
       python ali163_hc_r4g_build.py R6|R7|R8|R9
"""
import json
import os
import re
import sys
import hashlib

sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok

W = r"C:\AI\community"
COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
APPROVED = r"C:\Users\derek\5slock\approved_characters"
RALPH = r"C:\Users\derek\5slock\ralph-community\ralph.ps1"
BASE_ID = "ali147_pool_refsheet_b_s51080000"
SRC = os.path.join(W, "runs", BASE_ID, "request.api.json")

CLIPS = {
    "R6": dict(id="ali147_pool_hc_r3_s51130003", seed=51130003, women=2,
               pick="community/hc/HC3_lesbian_beach.jpg",
               pick_src=("GROK_IMAGINE_2026-10-19b", "GI173.jpg"),
               p0=os.path.join(W, "notes", "hc_r3_c0.txt"), p1=os.path.join(W, "notes", "hc_r3_c1.txt")),
    "R7": dict(id="ali147_pool_hc_r4_s51130004", seed=51130004, women=1,
               pick="community/hc/HC4_strip_tease_aerobics.jpg",
               pick_src=("GROK_IMAGINE_2026-10-19b", "GI107.jpg"),
               p0=os.path.join(W, "notes", "hc_r4_c0.txt"), p1=os.path.join(W, "notes", "hc_r4_c1.txt")),
    "R8": dict(id="ali147_pool_hc_r5_s51130005", seed=51130005, women=1,
               pick="community/hc/HC5_spicy_solo.jpg",
               pick_src=("GROK_IMAGINE_2026-10-19b", "GI150.jpg"),
               p0=os.path.join(W, "notes", "hc_r5_c0.txt"), p1=os.path.join(W, "notes", "hc_r5_c1.txt")),
    "R9": dict(id="ali147_pool_hc_r6_s51130006", seed=51130006, women=2,
               pick="community/hc/HC6_women_casino_lounge.jpg",
               pick_src=("FLOW_BLONDE_DARK_PAIRS_2026-10-19", "BD076.jpg"),
               p0=os.path.join(W, "notes", "hc_r6_c0.txt"), p1=os.path.join(W, "notes", "hc_r6_c1.txt")),
}

# expected per-node input-key diffs vs the RS6 base (the pick file, prompts, geometry, frames, seed, prefix)
EXPECT_KEYS = {
    "c0": ["height", "length", "prompt", "ref_image_size", "ref_images.ref_image_2", "width"],
    "c1": ["height", "prompt", "ref_image_size", "ref_images.ref_image_1", "width"],
    "img": ["image"], "noise": ["noise_seed"], "save": ["filename_prefix"], "win1": ["extension_frames"],
}
BIND = "<Subject 1> is the exact same woman shown in <Picture 1>"
DEF_HEAD = "<Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
CLOSE = "in close-up"

fails = []
n_pass = 0


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


def build(tag):
    c = CLIPS[tag]
    ID, SEED, WOMEN = c["id"], c["seed"], c["women"]
    print("=" * 110)
    print(f"{tag}  {ID}  seed {SEED}  women {WOMEN}  pick {c['pick']}")
    src_text = open(SRC, "rb").read().decode("utf-8").replace("\r\n", "\n")
    base = json.loads(src_text)
    g = json.loads(src_text)
    p0 = open(c["p0"], encoding="utf-8").read().rstrip("\n")
    p1 = open(c["p1"], encoding="utf-8").read().rstrip("\n")

    # ---- deltas ----
    del g["sheet"]
    i0 = g["c0"]["inputs"]
    i0["width"], i0["height"], i0["length"] = 1344, 768, 124
    i0["prompt"] = p0
    i0["ref_image_size"] = "match"
    i0["ref_images.ref_image_1"] = ["img", 0]
    i0.pop("ref_images.ref_image_2", None)
    i1 = g["c1"]["inputs"]
    g["c1"]["class_type"] = "MiniMaxH3ImageToVideo"
    i1["width"], i1["height"] = 1344, 768
    i1["prompt"] = p1
    i1["length"] = ["win1", 1]
    i1["audio_vae"] = ["avae", 0]
    for k in list(i1):
        if k.startswith("ref_"):
            del i1[k]
    g["win1"]["inputs"]["extension_frames"] = 119
    g["img"]["inputs"]["image"] = c["pick"]
    g["noise"]["inputs"]["noise_seed"] = SEED
    g["save"]["inputs"]["filename_prefix"] = f"community/{ID}/{ID}"

    dst_dir = os.path.join(W, "runs", ID)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, "request.api.json")
    data = json.dumps(g, indent=1, ensure_ascii=True).replace("\n", "\r\n").encode("utf-8")
    open(dst, "wb").write(data)
    new = json.loads(open(dst, encoding="utf-8").read().replace("\r\n", "\n"))

    # ---- CHECK 1: graph diff vs the base is only the intended nodes/keys ----
    added = sorted(set(new) - set(base))
    removed = sorted(set(base) - set(new))
    diff = sorted(k for k in set(base) | set(new)
                  if json.dumps(base.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True))
    per_node_ok = True
    for nid, want in EXPECT_KEYS.items():
        ob, nb = base.get(nid, {}).get("inputs", {}), new[nid]["inputs"]
        keys = sorted(k for k in set(ob) | set(nb)
                      if json.dumps(ob.get(k), sort_keys=True) != json.dumps(nb.get(k), sort_keys=True))
        if keys != want:
            per_node_ok = False
            print(f"     node {nid} changed keys {keys} != expected {want}")
    ck(added == [] and removed == ["sheet"] and len(new) == len(base) - 1 == 25
       and diff == sorted(list(EXPECT_KEYS) + ["sheet"]) and per_node_ok,
       f"1 graph diff vs {BASE_ID}: nodes +{added} -{removed}, count {len(new)}, changed nodes {diff}, per-node keys as expected")
    for nid in sorted((set(base) & set(new)) - set(EXPECT_KEYS)):
        ck(json.dumps(base[nid], sort_keys=True) == json.dumps(new[nid], sort_keys=True), f"1 node {nid} untouched")

    # ---- CHECK 2: frames = the R1 count, 24 fps ----
    n0, ext = int(new["c0"]["inputs"]["length"]), int(new["win1"]["inputs"]["extension_frames"])
    ck(n0 == 124 and ext == 119 and n0 + ext == 243 and int(new["win1"]["inputs"]["overlap_frames"]) == 22
       and int(new["mkvid"]["inputs"]["fps"]) == 24 and (n0 + ext) / 24.0 == 10.125,
       f"2 frames = c0 {n0} + win1.extension_frames {ext} = {n0 + ext} (the R1 count 243), 24 fps, {(n0 + ext) / 24.0} s")

    # ---- CHECK 3: geometry 1344x768 both chunks ----
    ck(new["c0"]["inputs"]["width"] == 1344 and new["c0"]["inputs"]["height"] == 768
       and new["c1"]["inputs"]["width"] == 1344 and new["c1"]["inputs"]["height"] == 768,
       "3 geometry 1344x768 (16:9) in c0 and c1")

    # ---- CHECK 4: references = the approved pick only, 0 in the continuation ----
    r0 = sorted(k for k in new["c0"]["inputs"] if k.startswith("ref_images"))
    r1 = sorted(k for k in new["c1"]["inputs"] if k.startswith("ref_images"))
    pick_src = os.path.join(APPROVED, c["pick_src"][0], c["pick_src"][1])
    placed = os.path.join(COMFY, "input", c["pick"].replace("/", "\\"))
    same = os.path.isfile(placed) and os.path.isfile(pick_src) and \
        hashlib.sha256(open(placed, "rb").read()).hexdigest() == hashlib.sha256(open(pick_src, "rb").read()).hexdigest()
    ck(r0 == ["ref_images.ref_image_1"] and new["c0"]["inputs"]["ref_images.ref_image_1"] == ["img", 0]
       and "ref_images" not in new["c0"]["inputs"] and r1 == []
       and new["c1"]["class_type"] == "MiniMaxH3ImageToVideo" and "sheet" not in new
       and resolves(new["img"]["inputs"]["image"]) and same,
       f"4 c0 refs {r0} (the pick only, node img), c1 refs {r1} (class {new['c1']['class_type']}, 0 refs), "
       f"no sheet node, pick {c['pick']} resolves in ComfyUI\\input and is byte-identical to approved {c['pick_src'][1]}: {same}")

    # ---- CHECK 5: ref_image_size = node default match on c0, no ref key on c1 ----
    ck(new["c0"]["inputs"]["ref_image_size"] == "match" and "ref_image_size" not in new["c1"]["inputs"],
       "5 c0 ref_image_size = match (node default, ref downscaled to the 1344x768 canvas px); c1 has no ref_image_size (0 refs)")

    # ---- CHECK 6: sampling / audio path identical to base, single pass, no RIFE/refine ----
    fixed = (new["unet"]["inputs"]["unet_name"].endswith("beta6_int8.safetensors")
             and new["ksel"]["inputs"]["sampler_name"] == "euler"
             and new["s0_sched"]["inputs"]["scheduler"] == "simple" and int(new["s0_sched"]["inputs"]["steps"]) == 10
             and new["s1_sched"]["inputs"]["scheduler"] == "simple" and int(new["s1_sched"]["inputs"]["steps"]) == 10
             and float(new["m_shift"]["inputs"]["shift_video"]) == 10.0 and float(new["m_shift"]["inputs"]["shift_audio"]) == 3.0
             and new["m_vsa"]["inputs"]["selection"] == "vsa"
             and json.dumps(new["tail1"]["inputs"], sort_keys=True) == json.dumps(base["tail1"]["inputs"], sort_keys=True)
             and all(json.dumps(new[n], sort_keys=True) == json.dumps(base[n], sort_keys=True)
                     for n in set(base) - set(EXPECT_KEYS) - {"sheet", "c1"})
             and not any("RIFE" in v["class_type"] or "Refine" in v["class_type"] or "Upscale" in v["class_type"] for v in new.values())
             and new["dec_a"]["inputs"]["vae"] == ["avae", 0] and new["mkvid"]["inputs"]["audio"] == ["dec_a", 0]
             and len([v for v in new.values() if v["class_type"] == "KSamplerAdvanced"]) == 2)
    ck(fixed, "6 sampling fixed as base (denoise 1.0 in the base sched/samplers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8), "
             "single pass (2 samplers, no RIFE/refine/upscale), audio VAE + audio decoder wired, 1344x768")

    # ---- CHECK 7: prompt text carried byte-exact + v2 blocks + guard ----
    ok7 = True
    for nm, pr in (("c0", p0), ("c1", p1)):
        gpr = new[nm]["inputs"]["prompt"]
        ok7 &= (gpr == pr and len(pr) > 1500 and guard_ok(pr) and "overall_soundscape:" in pr
                and "non_diegetic_music:" in pr and "dynamic video, fluid natural motions" in pr.lower()
                and "subject_definitions:" in pr and "minor" not in pr.lower()
                and "teen" not in pr.lower() and "school" not in pr.lower() and ID not in pr)
    ok7 &= all(h in p0 for h in ("summary:", "retention_analysis:", "detailed_description:"))
    ok7 &= "integrated_multimodal_description:" in p1 and "first 5 seconds" in p1
    ck(ok7, f"7 prompts byte-exact in the graph, v2 blocks present (c0 subject_definitions/summary/retention_analysis/detailed_description, "
            f"c1 subject_definitions/integrated_multimodal_description + first 5 seconds), overall_soundscape: + non_diegetic_music: in both, "
            f"guard_ok, no youth-coded words (c0 {len(p0)} chars, c1 {len(p1)} chars)")

    # ---- CHECK 8: the R4G identity wording, extender/model-card verbatim, both chunks, close-up beats ----
    ok8 = True
    ok8 &= DEF_HEAD in p0 and BIND in p0
    ok8 &= BIND in p1 and "of the first 5 seconds of this clip" in p1
    ok8 &= "carries no reference pictures at all" in p1
    ok8 &= "for the face" in p0 and "only" in p0 and "fully clothed" in p0 and "face is small in the frame" in p0
    ok8 &= p0.count(CLOSE) >= WOMEN and p1.count(CLOSE) >= WOMEN
    nsub0 = len(re.findall(r"^<Subject \d> is", p0, flags=re.M))
    nsub1 = len(re.findall(r"^<Subject \d> is", p1, flags=re.M))
    ok8 &= nsub0 == WOMEN and nsub1 == WOMEN
    ok8 &= not re.search(r"<Picture [2-9]>", p0) and not re.search(r"<Picture [2-9]>", p1)
    for nm, pr in (("c0", p0), ("c1", p1)):
        for line in pr.splitlines():
            if BIND in line:
                ok8 &= not re.search(r"bikini|lingerie|robe|dress|top|shirt|shorts|clothing|wear", line, re.I)
    ck(ok8, f"8 extender/model-card wording in BOTH chunks: verbatim <Picture 1> definition in c0, binding phrase "
            f"'{BIND}' in c0 and c1, c1 declares 0 reference pictures, picture = face and hair only + fully clothed/small-face/"
            f"only-reference sentence in c0, close-up face beats {p0.count(CLOSE)}/{p1.count(CLOSE)} (women {WOMEN}), "
            f"subjects c0 {nsub0} c1 {nsub1} = {WOMEN} women, no <Picture 2+>, no garment word inside any binding line")

    # ---- CHECK 9: id gates, id free, no render queued ----
    ralph = open(RALPH, encoding="utf-8-sig").read()
    pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
    free = (not os.path.exists(os.path.join(W, "p7", "jobs", f"{ID}.result.json"))
            and not os.path.exists(os.path.join(dst_dir, "objective.json"))
            and not os.path.exists(os.path.join(COMFY, "output", "community", ID)))
    ck(len(re.findall(r"^[a-z0-9_]+$", ID)) == 1 and len(pats) >= 2 and all(re.match(p, ID) for p in pats)
       and free and not os.path.exists(os.path.join(W, "p7", "JOB_REQUEST.json")),
       f"9 id charset + live ralph.ps1 id gates {pats}, id free (no result.json/objective.json/output folder), "
       f"no JOB_REQUEST.json queued (R4G = no render)")
    print(f"{tag} graph bytes {len(data)} sha256 {hashlib.sha256(data).hexdigest()}")
    return data


want = sys.argv[1:] or sorted(CLIPS)
for tag in want:
    build(tag)
print("=" * 110)
if fails:
    print("CHECKS FAIL " + json.dumps(fails))
    sys.exit(1)
print(f"ALL CHECKS PASS ({n_pass} PASS lines, 9 numbered checks per clip: {want})")
