"""ALI-184 BQ1b: the BODY-QUALITY REWIRE builder (Derrick 2026-10-23 4:00 PM CT "Also their bodies are ugly
as fuck what prompt was that?"; 4:04 PM CT "Do research and improve"; Max REWIRE 4:51 PM CT "rewire the HC
graph so EVERY redo loads the approved start still as the body and scene reference, with the face crop as a
face-only reference (r3r-r6 used face crops only; the start still was not in the graph)").

Cloned from notes/ali163_hc_r4g2_build.py, which stays FROZEN so r3r/r4/r5/r6 stay reproducible. This file
builds ONE clip: HC3 -> ali147_pool_hc_r3b_s51130003 (seed 51130003), the side-by-side against the rendered
r3r (runs/ali147_pool_hc_r3r_s51130003, ok rc=0, 243 f, 1344x768, audio).

Base graph = runs/ali147_pool_refsheet_b_s51080000/request.api.json (RS6, 26 nodes), the same base R4G2 uses.

The BQ1 change (research rows 1+2 of notes/body_quality_research_20261023.md, nothing else):
  3 reference pictures in BOTH chunks, in this order, in c0 and c1:
      <Picture 1> = node "img"   = community/hc/HC3_lesbian_beach.jpg  = the APPROVED start still
                    (byte-identical to approved_characters/GROK_IMAGINE_2026-10-19b/GI173.jpg, 1792x1008,
                     aspect 1.778 in the 1.70-1.85 gate, short side 1008 >= 768) = the BODY / SKIN / FIGURE /
                     WARDROBE / SCENE / LIGHT reference, the Max-mandated rewire.
      <Picture 2> = node "img2"  = community/hc/HC3_w1_face.png  (512 px SCRFD crop, left woman) = FACE+HAIR only
      <Picture 3> = node "img3"  = community/hc/HC3_w2_face.png  (512 px SCRFD crop, right woman) = FACE+HAIR only
    c0 and c1 are both MiniMaxH3ReferenceToVideo with ref_images.ref_image_1/2/3 + ref_image_size "match", and
    both keep audio_vae (ReferenceToVideo HAS audio_vae: nodes_minimax_h3.py; r3r had to DROP c1.audio_vae only
    because R4G2 made c1 a MiniMaxH3ImageToVideo, which has no such input = the rc=2 STATIC_FAIL of 14:15 CT).
  Prompts notes/hc_r3b_c0.txt + notes/hc_r3b_c1.txt (v2 format): the start still owns body/skin/figure/wardrobe/
    scene, the crops own face and hair ONLY, and the old contradiction is GONE - no "body proportions" in the
    crop sentences, no "the bodies and the camera of this video are new", no "used for the faces and the hair of
    the two women only", and c1 no longer says it "carries no reference pictures at all".
  FROZEN vs the base: BasicGuider x2, euler/simple, steps 10, shift 10/3, vsa, beta6 int8, 1344x768,
    24 fps, c0 124 f + win1.extension_frames 119 = 243 f (the R1 count), audio VAE + decoder, single pass.
  Deferred to their own arms, one variable per render (research section 2): the fal realism LoRA, steps 8 +
    shift 12/5, CFGGuider+NAGuidance (2x/step), MiniMaxH3AddGuide frame_idx 0, BlockSparseAttention off.

NO render, NO p7/JOB_REQUEST.json in this builder (that is BQ1c). 0 GPU minutes: every check here is offline
(file + graph + PIL + the on-disk H3 schema), no ComfyUI port, no comfy_ctl, no llama-swap, no vision judge.

Self-check: 13 numbered checks, PASS/FAIL lines, exit 1 on any FAIL. Check 13 is a self-destruct probe: the
same detectors run on a clone with the r3r wiring restored (face crops only in c0, no refs in c1, ref_image_size
max, the r3r prompt text) and must fire there and not fire on the real graph, so checks 4/5/8/11 are not vacuous.
Usage: python ali163_hc_bq1_build.py [HC3]
"""
import difflib
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
BASE_ID = "ali147_pool_refsheet_b_s51080000"
SRC = os.path.join(W, "runs", BASE_ID, "request.api.json")
HC_DIR = os.path.join(COMFY, "input", "community", "hc")
H3_SRC = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")
DIFF_TXT = os.path.join(W, "notes", "bq1_prompt_diff.txt")
REF_SLOT = re.compile(r"ref_images\.ref_image_\d+")     # fullmatch: a bare "ref_images" dict must NOT count


def h3_schema():
    """{class: (required, optional)} read from the ON-DISK H3 node schema = the same names
    run_graph_job.static_check reads from ComfyUI /object_info, so a graph that passes check 11 cannot die on
    STATIC_FAIL rc=2 (no network). Only TOP-LEVEL io.X.Input(...) entries count (depth 1 in the inputs=[...]
    list), so the io.Autogrow template's inner io.Image.Input("ref_image") is NOT a required node input."""
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


CLIPS = {
    "HC3": dict(id="ali147_pool_hc_r3b_s51130003", seed=51130003, women=2,
                pick_src=("GROK_IMAGINE_2026-10-19b", "GI173.jpg"),
                still="HC3_lesbian_beach.jpg",
                crops=["HC3_w1_face.png", "HC3_w2_face.png"],
                crop_boxes=[[382, 0, 171, 240], [799, 228, 222, 204]],
                old0=os.path.join(W, "notes", "hc_r3_c0.txt"), old1=os.path.join(W, "notes", "hc_r3_c1.txt"),
                p0=os.path.join(W, "notes", "hc_r3b_c0.txt"), p1=os.path.join(W, "notes", "hc_r3b_c1.txt")),
}

# ---- BQ1 wording constants (check 8) ----
DEF_P1 = ("<Picture 1> is the approved full-body start photograph of the two adult women on a sunlit seaside "
          "terrace, and it is the reference image that defines the bodies, skin, figures, height, build, skin "
          "tone, faces, hair, wardrobe, terrace, lighting and camera context of this video for both")
CROP2 = "<Picture 2> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>"
CROP3 = "<Picture 3> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 2>"
BIND1 = "<Subject 1> is the exact same woman shown in <Picture 2>"
BIND2 = "<Subject 2> is the exact same woman shown in <Picture 3>"
FORBID = ["body proportions",
          "are new and are not taken from",
          "used for the faces and the hair of the two women only",
          "These two crops are the only visual references",
          "carries no reference pictures at all"]
BODY_WORDS = ["matte skin with visible pores", "fine vellus hair", "waxy", "waist", "hips", "thigh",
              "breast", "weight", "five separate fingers"]
JOINT_WORDS = {"c0": "elbows and knees hinging naturally", "c1": "elbows bending naturally"}
GARMENT = re.compile(r"bikini|lingerie|robe|dress|top|shirt|shorts|clothing|wear", re.I)

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


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ref_slots(n):
    """Ordered ref slots of a node, read with fullmatch so a submitted graph's bare "ref_images" dict is ignored."""
    return sorted(k for k in n["inputs"] if REF_SLOT.fullmatch(k))


WANT_SLOTS = ["ref_images.ref_image_1", "ref_images.ref_image_2", "ref_images.ref_image_3"]


def slots_ok(g):
    """True only if BOTH chunks carry the 3-slot rewire: start still, crop 1, crop 2, as ReferenceToVideo, with
    audio_vae kept and no sheet node. The BQ1 requirement of the Max REWIRE (4:51 PM CT)."""
    if "sheet" in g:
        return False
    for nid in ("c0", "c1"):
        i = g[nid]["inputs"]
        if g[nid]["class_type"] != "MiniMaxH3ReferenceToVideo" or "audio_vae" not in i:
            return False
        if ref_slots(g[nid]) != WANT_SLOTS:
            return False
        if [i[k] for k in WANT_SLOTS] != [["img", 0], ["img2", 0], ["img3", 0]]:
            return False
    return True


def size_ok(g):
    return all(g[nid]["inputs"]["ref_image_size"] == "match" for nid in ("c0", "c1"))


def wording_ok(pr):
    """True only if the start still OWNS body/skin/figure/wardrobe/scene, the crops own face+hair only, both
    subjects bind to their crop AND to the first 5 seconds, and none of the 5 contradiction phrases is present."""
    return (pr.count(DEF_P1) == 1 and pr.count(CROP2) == 1 and pr.count(CROP3) == 1
            and pr.count(BIND1) == 1 and pr.count(BIND2) == 1 and all(f not in pr for f in FORBID))


def scan(g, sch):
    """Offline clone of run_graph_job.static_check for the H3 classes visible on disk."""
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


def build(tag):
    c = CLIPS[tag]
    ID, SEED, WOMEN = c["id"], c["seed"], c["women"]
    expect = {"c0": ["height", "length", "prompt", "ref_image_size", "ref_images.ref_image_2",
                     "ref_images.ref_image_3", "width"],
              "c1": ["height", "prompt", "ref_image_size", "ref_images.ref_image_1",
                     "ref_images.ref_image_2", "ref_images.ref_image_3", "width"],
              "img": ["image"], "img2": ["image"], "img3": ["image"],
              "noise": ["noise_seed"], "save": ["filename_prefix"], "win1": ["extension_frames"],
              "sheet": ["image"]}
    print("=" * 110)
    print(f"{tag}  {ID}  seed {SEED}  women {WOMEN}  start still {c['still']} + crops {' + '.join(c['crops'])}")
    src_text = open(SRC, "rb").read().decode("utf-8").replace("\r\n", "\n")
    base = json.loads(src_text)
    g = json.loads(src_text)
    p0 = open(c["p0"], encoding="utf-8").read().rstrip("\n")
    p1 = open(c["p1"], encoding="utf-8").read().rstrip("\n")

    # ---- deltas: the BQ1 rewire = 3 refs (start still + 2 face crops) on BOTH chunks ----
    del g["sheet"]
    g["img"]["inputs"]["image"] = "community/hc/" + c["still"]
    g["img2"] = {"class_type": "LoadImage", "inputs": {"image": "community/hc/" + c["crops"][0]}}
    g["img3"] = {"class_type": "LoadImage", "inputs": {"image": "community/hc/" + c["crops"][1]}}
    for nid in ("c0", "c1"):
        i = g[nid]["inputs"]
        i["width"], i["height"] = 1344, 768
        i["prompt"] = p0 if nid == "c0" else p1
        i["ref_image_size"] = "match"
        i["ref_images.ref_image_1"] = ["img", 0]
        i["ref_images.ref_image_2"] = ["img2", 0]
        i["ref_images.ref_image_3"] = ["img3", 0]
    g["c0"]["inputs"]["length"] = 124
    g["c1"]["inputs"]["length"] = ["win1", 1]
    g["win1"]["inputs"]["extension_frames"] = 119
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
    for nid, want in expect.items():
        ob = base.get(nid, {}).get("inputs", {})
        nb = new[nid]["inputs"] if nid in new else {}
        keys = sorted(k for k in set(ob) | set(nb)
                      if json.dumps(ob.get(k), sort_keys=True) != json.dumps(nb.get(k), sort_keys=True))
        if keys != want:
            per_node_ok = False
            print(f"     node {nid} changed keys {keys} != expected {want}")
    ck(added == ["img2", "img3"] and removed == ["sheet"] and len(new) == len(base) + 1
       and diff == sorted(expect) and per_node_ok,
       f"1 graph diff vs {BASE_ID}: nodes +{added} -{removed}, count {len(new)} (base {len(base)} + 2 LoadImage - 1 sheet), "
       f"changed nodes {diff}, per-node keys as expected: {per_node_ok}")
    for nid in sorted((set(base) & set(new)) - set(expect)):
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

    # ---- CHECK 4: THE REWIRE - 3 reference slots in BOTH chunks, start still + 2 face crops ----
    r0, r1 = ref_slots(new["c0"]), ref_slots(new["c1"])
    want_r = ["ref_images.ref_image_1", "ref_images.ref_image_2", "ref_images.ref_image_3"]
    links_ok = (r0 == want_r and r1 == want_r
                and all(new[nid]["inputs"][k] == ln for nid in ("c0", "c1")
                        for k, ln in (("ref_images.ref_image_1", ["img", 0]),
                                      ("ref_images.ref_image_2", ["img2", 0]),
                                      ("ref_images.ref_image_3", ["img3", 0]))))
    img_nodes = sorted(k for k, v in new.items() if v["class_type"] == "LoadImage")
    pick_src = os.path.join(APPROVED, c["pick_src"][0], c["pick_src"][1])
    still_p = os.path.join(HC_DIR, c["still"])
    crop_ps = [os.path.join(HC_DIR, n) for n in c["crops"]]
    media_ok = (img_nodes == ["img", "img2", "img3"] and "sheet" not in new
                and resolves("community/hc/" + c["still"]) and os.path.isfile(pick_src)
                and sha(still_p) == sha(pick_src)
                and all(resolves("community/hc/" + n) and n.endswith("_face.png") and os.path.isfile(p)
                        for n, p in zip(c["crops"], crop_ps))
                and new["c0"]["class_type"] == "MiniMaxH3ReferenceToVideo"
                and new["c1"]["class_type"] == "MiniMaxH3ReferenceToVideo")
    ck(links_ok and media_ok and slots_ok(new),
       f"4 REWIRE: c0 AND c1 slots {r0} -> img = the APPROVED start still community/hc/{c['still']} "
       f"(sha256 == {c['pick_src'][1]}: {sha(still_p) == sha(pick_src)}), img2/img3 = the 512 px face crops "
       f"{' + '.join(c['crops'])}; no sheet node, no Klein sheet; both chunks MiniMaxH3ReferenceToVideo")

    # ---- CHECK 5: ref_image_size = match on both chunks + the row-12 start-still quality gate (PIL, no vision) ----
    from PIL import Image
    with Image.open(still_p) as im:
        sw, sh = im.size
    ar = sw / sh
    px = []
    for p in crop_ps:
        with Image.open(p) as im:
            px.append((os.path.basename(p), im.size))
    px_ok = (1.70 <= ar <= 1.85 and min(sw, sh) >= 768
             and all(w == h and 400 <= w <= 550 for _, (w, h) in px))
    ck(new["c0"]["inputs"]["ref_image_size"] == "match" and new["c1"]["inputs"]["ref_image_size"] == "match"
       and size_ok(new) and px_ok,
       f"5 ref_image_size = match on c0 and c1 (every ref capped to the 1344x768 canvas px, the predictable budget); "
       f"start still {sw}x{sh} aspect {ar:.3f} in 1.70-1.85, short side {min(sw, sh)} >= 768; crops {px} square "
       f"400-550: {px_ok}")

    # ---- CHECK 6: sampling / audio path identical to base, single pass, no RIFE/refine ----
    fixed = (new["unet"]["inputs"]["unet_name"].endswith("beta6_int8.safetensors")
             and new["ksel"]["inputs"]["sampler_name"] == "euler"
             and new["s0_sched"]["inputs"]["scheduler"] == "simple" and int(new["s0_sched"]["inputs"]["steps"]) == 10
             and new["s1_sched"]["inputs"]["scheduler"] == "simple" and int(new["s1_sched"]["inputs"]["steps"]) == 10
             and float(new["m_shift"]["inputs"]["shift_video"]) == 10.0 and float(new["m_shift"]["inputs"]["shift_audio"]) == 3.0
             and new["m_vsa"]["inputs"]["selection"] == "vsa"
             and len([v for v in new.values() if v["class_type"] == "BasicGuider"]) == 2
             and len([v for v in new.values() if v["class_type"] == "CFGGuider"]) == 0
             and len([v for v in new.values() if v["class_type"] == "NAGuidance"]) == 0
             and not any(v["class_type"] == "MiniMaxH3AddGuide" for v in new.values())
             and json.dumps(new["tail1"]["inputs"], sort_keys=True) == json.dumps(base["tail1"]["inputs"], sort_keys=True)
             and all(json.dumps(new[n], sort_keys=True) == json.dumps(base[n], sort_keys=True)
                     for n in set(base) & set(new) - set(expect) - {"sheet"})
             and not any("RIFE" in v["class_type"] or "Refine" in v["class_type"] or "Upscale" in v["class_type"] for v in new.values())
             and new["dec_a"]["inputs"]["vae"] == ["avae", 0] and new["mkvid"]["inputs"]["audio"] == ["dec_a", 0]
             and len([v for v in new.values() if v["class_type"] == "SamplerCustomAdvanced"]) == 2
             and not any(v["class_type"] == "KSamplerAdvanced" for v in new.values()))
    ck(fixed, "6 sampling FROZEN as base (euler/simple/10 steps, shift 10/3, vsa, beta6 int8, BasicGuider x2 and no "
             "CFGGuider/NAGuidance/AddGuide = the deferred arms), single pass (2 SamplerCustomAdvanced, no "
             "RIFE/refine/upscale), audio VAE + audio decoder wired")

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
    ck(ok7, f"7 prompts byte-exact in the graph, v2 blocks present, overall_soundscape: + non_diegetic_music: in both, "
            f"guard_ok True, no youth-coded words, id not in prompt (c0 {len(p0)} chars, c1 {len(p1)} chars)")

    # ---- CHECK 8: BQ1 wording - the rewire sentence in both chunks, crops face+hair only, NO contradiction ----
    ok8 = True
    for nm, pr in (("c0", p0), ("c1", p1)):
        ok8 &= pr.count(DEF_P1) == 1 and pr.count(CROP2) == 1 and pr.count(CROP3) == 1
        ok8 &= pr.count(BIND1) == 1 and pr.count(BIND2) == 1
        ok8 &= all(f not in pr for f in FORBID)
        ok8 &= all(b in pr for b in BODY_WORDS) and JOINT_WORDS[nm] in pr
        ok8 &= sorted(set(re.findall(r"<Picture (\d)>", pr))) == ["1", "2", "3"]
        ok8 &= len(re.findall(r"^<Subject \d> is", pr, flags=re.M)) == WOMEN
    ok8 &= ("the woman on the left of <Picture 1>" in p0 and "the woman on the right of <Picture 1>" in p0
            and "the face fills each of those crops" in p0 and "the face fills each of those crops" in p1
            and "is an action in the story" in p0 and "actions in the story" in p1
            and "same three reference pictures" in p1
            and "of the reference pictures and in the first 5 seconds of this clip" in p1)
    bad_bind = [ln[:60] for ln in (p0.splitlines() + p1.splitlines())
                if (BIND1 in ln or BIND2 in ln) and GARMENT.search(ln)]
    ok8 &= not bad_bind
    ok8 &= wording_ok(p0) and wording_ok(p1)
    ck(ok8, f"8 BQ1 wording: the start-still definition line ({DEF_P1[:48]}...) in c0 AND c1, the two crop lines "
            f"say face + hairstyle ONLY (no 'body proportions'), BIND1/BIND2 point at the crops (<Picture 2>/3), "
            f"the 5 contradiction strings are ABSENT {FORBID}, body wording present ({len(BODY_WORDS)} phrases: "
            f"matte skin with visible pores / waist / hips / thigh / breast / weight / five separate fingers, "
            f"joint wording {' + '.join(JOINT_WORDS.values())}), "
            f"<Picture> set 1,2,3 in both, {WOMEN} subject lines each, the clothing-removal clause is in both, "
            f"c1 declares the same three reference pictures, no garment word in a binding line {bad_bind}")

    # ---- CHECK 9: id gates, id free, no render queued ----
    ralph = open(RALPH, encoding="utf-8-sig").read()
    pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
    free = (not os.path.exists(os.path.join(W, "p7", "jobs", f"{ID}.result.json"))
            and not os.path.exists(os.path.join(dst_dir, "objective.json"))
            and not os.path.exists(os.path.join(COMFY, "output", "community", ID)))
    ck(len(re.findall(r"^[a-z0-9_]+$", ID)) == 1 and len(pats) >= 2 and all(re.match(p, ID) for p in pats)
       and free and not os.path.exists(os.path.join(W, "p7", "JOB_REQUEST.json")),
       f"9 id charset + live ralph.ps1 id gates {pats}, id free (no result.json/objective.json/output folder), "
       f"no JOB_REQUEST.json queued (BQ1b = no render; BQ1c requests it)")

    # ---- CHECK 10: provenance - crops logged by face_crop.py, start still bytes == the approved pick ----
    logtxt = open(os.path.join(W, "notes", "face_crop.log"), encoding="utf-8").read()
    rows, ok10 = [], True
    for n, box in zip(c["crops"], c["crop_boxes"]):
        p = os.path.join(HC_DIR, n)
        line = [l for l in logtxt.splitlines() if "WROTE" in l and f"{n}\"" in l]
        rec = json.loads(line[-1].split(" WROTE ", 1)[1]) if line else {}
        good = bool(rec.get("ok") is True and rec.get("face_box") == box
                    and rec.get("src", "").endswith(c["pick_src"][1])
                    and rec.get("out_px") == 512 and os.path.isfile(p)
                    and os.path.getsize(p) == rec.get("bytes"))
        ok10 &= good
        rows.append(f"{n} src={os.path.basename(rec.get('src', '?'))} face_box={rec.get('face_box')} "
                    f"out_px={rec.get('out_px')} bytes={rec.get('bytes')} sha256={sha(p)[:12]}")
    ok10 &= (os.path.getsize(still_p) == os.path.getsize(pick_src) and sha(still_p) == sha(pick_src))
    rows.append(f"{c['still']} bytes={os.path.getsize(still_p)} sha256={sha(still_p)[:12]} == "
                f"{c['pick_src'][1]} bytes={os.path.getsize(pick_src)} sha256={sha(pick_src)[:12]}")
    ck(ok10, "10 every crop is logged by face_crop.py with ok=True, its --box, src = the approved pick, out_px 512 "
             "and the byte count on disk; the start still in ComfyUI\\input is BYTE- and sha-identical to the "
             "approved pick: " + " | ".join(rows))

    # ---- CHECK 11: static-input self-check (offline clone of run_graph_job.static_check for the H3 nodes) ----
    sch = h3_schema()
    n_h3 = len([n for n in new.values() if n["class_type"] in sch])
    bad11 = scan(new, sch)
    avae_users = sorted(k for k, v in new.items() if any(isinstance(x, list) and x == ["avae", 0] for x in v["inputs"].values()))
    dead = json.loads(open(os.path.join(W, "runs", "ali147_pool_hc_r3_s51130003", "request.api.json"),
                           encoding="utf-8").read())
    bad_dead = scan(dead, sch)
    ck(not bad11 and n_h3 >= 3 and "MiniMaxH3ReferenceToVideo" in sch
       and "audio_vae" in sch["MiniMaxH3ReferenceToVideo"][1]
       and "audio_vae" in new["c1"]["inputs"]
       and avae_users == ["c0", "c1", "dec_a"]
       and all(k in (sch["MiniMaxH3ReferenceToVideo"][0] | sch["MiniMaxH3ReferenceToVideo"][1])
               for k in ("ref_image_size", "audio_vae"))
       and "c1.audio_vae: not an input of MiniMaxH3ImageToVideo" in bad_dead,
       f"11 static-input self-check vs the on-disk schema {os.path.basename(H3_SRC)}: {n_h3} H3 nodes, every input "
       f"name legal + all required inputs present {bad11 or 'OK'}; c0 AND c1 are ReferenceToVideo so both keep "
       f"audio_vae (legal there, illegal on the ImageToVideo c1 that killed r3 at rc=2 - this check reproduces "
       f"that defect: {bad_dead}); avae feeds exactly {avae_users} (c0 + c1 ref audio + dec_a)")

    # ---- CHECK 12: the PROMPT DIFF vs the rendered r3r prompts, saved for the improve note ----
    o0 = open(c["old0"], encoding="utf-8").read().rstrip("\n").splitlines()
    o1 = open(c["old1"], encoding="utf-8").read().rstrip("\n").splitlines()
    d0 = difflib.unified_diff(o0, p0.splitlines(), "hc_r3_c0.txt (r3r)", "hc_r3b_c0.txt (BQ1b)", lineterm="", n=0)
    d1 = difflib.unified_diff(o1, p1.splitlines(), "hc_r3_c1.txt (r3r)", "hc_r3b_c1.txt (BQ1b)", lineterm="", n=0)
    dl0, dl1 = list(d0), list(d1)
    gone = [l for l in dl0 + dl1 if l.startswith("-") and any(f in l for f in FORBID)]
    same_lines = (sum(1 for l in dl0 if l.startswith("-") and not l.startswith("---")) ==
                  sum(1 for l in dl0 if l.startswith("+") and not l.startswith("+++")))
    open(DIFF_TXT, "w", encoding="utf-8").write("\n".join(dl0 + ["", ""] + dl1) + "\n")
    ck(len(gone) >= 3 and same_lines and len(dl0) > 6 and len(dl1) > 6
       and len(p0) > 1500 and len(p1) > 1500,
       f"12 prompt diff written to {os.path.basename(DIFF_TXT)}: c0 {len(o0)} lines -> {len(p0.splitlines())} "
       f"(changed-line counts balanced: {same_lines}), c1 {len(o1)} -> {len(p1.splitlines())}; the removed lines "
       f"carry {len(gone)} of the 5 contradiction phrases; lengths c0 {len(''.join(o0))} -> {len(p0)}, "
       f"c1 -> {len(p1)} chars")

    # ---- CHECK 13: self-destruct probe, proves checks 4/5/8 are NOT vacuous ----
    probe = json.loads(json.dumps(new))
    probe["sheet"] = {"class_type": "LoadImage", "inputs": {"image": "community/hc/HC3_w1_face.png"}}
    for nid in ("c0", "c1"):                       # put the r3r face-crop-only wiring back
        i = probe[nid]["inputs"]
        i["ref_images.ref_image_1"] = ["sheet", 0]
        del i["ref_images.ref_image_3"]
        i["ref_image_size"] = "max"
    probe["c1"]["class_type"] = "MiniMaxH3ImageToVideo"   # the R4G2 c1 class, no refs at all, audio_vae left on = the r3 defect
    po0, po1 = "\n".join(o0), "\n".join(o1)        # the rendered r3r prompts (the wording BQ1b replaces)
    probe["c0"]["inputs"]["prompt"], probe["c1"]["inputs"]["prompt"] = po0, po1
    caught = [not slots_ok(probe), not size_ok(probe), not wording_ok(po0), not wording_ok(po1),
              "c1.audio_vae: not an input of MiniMaxH3ImageToVideo" in " ".join(scan(probe, sch))]
    ck(all(caught) and slots_ok(new) and size_ok(new) and wording_ok(p0) and wording_ok(p1),
       f"13 SELF-DESTRUCT PROBE: the same checks run on a clone with the r3r wiring restored (c0 refs = face crops "
       f"only, c1 = ImageToVideo with no refs, ref_image_size max, the r3r prompt text) and ALL {sum(caught)}/5 "
       f"detectors fire {caught}, 0/5 fire on the real graph -> checks 4/5/8/11 are not vacuous")

    print(f"{tag} graph bytes {len(data)} sha256 {hashlib.sha256(data).hexdigest()}")
    return data


want = sys.argv[1:] or sorted(CLIPS)
for tag in want:
    build(tag)
print("=" * 110)
if fails:
    print("CHECKS FAIL " + json.dumps(fails))
    sys.exit(1)
print(f"ALL CHECKS PASS ({n_pass} PASS lines, 13 numbered checks per clip: {want})")
