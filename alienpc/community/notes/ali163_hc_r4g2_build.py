"""ALI-163 R4G2: repoint the R6-R9 reference slots at the 512 px FACE CROPS of each woman's approved
start still (Derrick 2026-10-23 1:42 PM CT "Yes, let Forge crop each woman's face from her start still and
use it as the reference"), keeping the R4G F1-F5 fixes. NO render, NO p7/JOB_REQUEST.json.

Base graph = runs/ali147_pool_refsheet_b_s51080000/request.api.json (RS6, 26 nodes, the graph R2 named).

Per clip (nothing else changes):
  pairs (R6=HC3, R9=HC6): node "sheet" deleted; new node "img2" (LoadImage) = the RIGHT woman's face crop;
      c0 ref_images.ref_image_1 = [img,0]  = the LEFT woman's crop  (<Picture 1> -> <Subject 1>)
         ref_images.ref_image_2 = [img2,0] = the RIGHT woman's crop (<Picture 2> -> <Subject 2>)
  solos (R7=HC4, R8=HC5): node "sheet" deleted, no img2; c0 ref_images.ref_image_1 = [img,0] = her face crop
  c0 ref_image_size "match"; c1 = MiniMaxH3ImageToVideo with 0 reference images (all ref_* keys removed) AND no
      audio_vae: MiniMaxH3ImageToVideo has NO audio_vae input (comfy_extras/nodes_minimax_h3.py:116-135 = clip, vae,
      prompt, width, height, length, first_frame?, last_frame?), so the link the base (ReferenceToVideo) carried made
      run_graph_job.static_check fail = STATIC_FAIL ... c1.audio_vae: not an input of MiniMaxH3ImageToVideo, rc=2, the
      whole r3 job died at 0.9 min (2026-10-23 14:15 CT). The audio path stays: avae -> c0.audio_vae and avae -> dec_a
      (proof: runs/ali147_pool_hc_c2_s51100002, whose c1 = MiniMaxH3ImageToVideo with NO audio_vae, objective audio=true).
      Check 11 now re-runs that static check offline against the on-disk schema, for every H3 node in the graph.
  c0 1344x768 length 124 + win1.extension_frames 119 = 243 f @ 24 fps; prompts hc_r<n>_c0/c1.txt (R4G2 wording)
  noise.noise_seed = the clip seed; save.filename_prefix = community/<id>/<id>

The crops themselves are made by the Max-owned helper C:/AI/community/scripts/face_crop.py (Forge never edits
it); face boxes come from notes/ali163_hc_r4g2_facebox.py (CPU SCRFD-10G, notes/hc_r4f_facelib.py).
Sampling / geometry / audio path byte-identical to the base (beta6 int8, euler/simple/10, shift 10/3, vsa,
single pass, 24 fps, audio VAE + decoder wired).

Self-check: 11 numbered checks, PASS/FAIL lines, exit 1 on any FAIL.
Usage: python ali163_hc_r4g2_build.py [R6|R7|R8|R9]
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
BASE_ID = "ali147_pool_refsheet_b_s51080000"
SRC = os.path.join(W, "runs", BASE_ID, "request.api.json")
HC_DIR = os.path.join(COMFY, "input", "community", "hc")
H3_SRC = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")


def h3_schema():
    """{class: (required, optional)} read from the ON-DISK H3 node schema = the same names run_graph_job.static_check
    reads from ComfyUI /object_info, so a graph that passes check 11 cannot die on STATIC_FAIL rc=2 (no network).
    Only TOP-LEVEL io.X.Input(...) entries count (depth 0 in the inputs=[...] list), so the io.Autogrow template's
    inner io.Image.Input("ref_image") does NOT become a required input of the node."""
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
                continue                      # 1 = a direct entry of inputs=[...]; 2+ = an Autogrow template input
            args = _args(blk, im.end())
            (opt if "optional=True" in args else req).add(im.group(1))
        if req:
            out[cls] = (req, opt)
    return out


def _args(txt, i):
    """txt[i] is the '(' of an argument list; return the argument text (parens inside strings included)."""
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
    "R6": dict(id="ali147_pool_hc_r3_s51130003", seed=51130003, women=2,
               pick_src=("GROK_IMAGINE_2026-10-19b", "GI173.jpg"),
               crops=["HC3_w1_face.png", "HC3_w2_face.png"], crop_boxes=[[382, 0, 171, 240], [799, 228, 222, 204]],
               p0=os.path.join(W, "notes", "hc_r3_c0.txt"), p1=os.path.join(W, "notes", "hc_r3_c1.txt")),
    "R7": dict(id="ali147_pool_hc_r4_s51130004", seed=51130004, women=1,
               pick_src=("GROK_IMAGINE_2026-10-19b", "GI107.jpg"),
               crops=["HC4_w1_face.png"], crop_boxes=[[830, 56, 107, 143]],
               p0=os.path.join(W, "notes", "hc_r4_c0.txt"), p1=os.path.join(W, "notes", "hc_r4_c1.txt")),
    "R8": dict(id="ali147_pool_hc_r5_s51130005", seed=51130005, women=1,
               pick_src=("GROK_IMAGINE_2026-10-19b", "GI150.jpg"),
               crops=["HC5_w1_face.png"], crop_boxes=[[307, 154, 163, 212]],
               p0=os.path.join(W, "notes", "hc_r5_c0.txt"), p1=os.path.join(W, "notes", "hc_r5_c1.txt")),
    "R9": dict(id="ali147_pool_hc_r6_s51130006", seed=51130006, women=2,
               pick_src=("FLOW_BLONDE_DARK_PAIRS_2026-10-19", "BD076.jpg"),
               crops=["HC6_w1_face.png", "HC6_w2_face.png"], crop_boxes=[[471, 33, 209, 157], [783, 68, 133, 190]],
               p0=os.path.join(W, "notes", "hc_r6_c0.txt"), p1=os.path.join(W, "notes", "hc_r6_c1.txt")),
}

DEF_HEAD = "<Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
DEF_TAIL = " is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions"
BIND1 = "<Subject 1> is the exact same woman shown in <Picture 1>"
BIND2 = "<Subject 2> is the exact same woman shown in <Picture 2>"
CLOSE = "in close-up"
FILLS = "the face fills"

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


def scan(g, sch):
    """Offline clone of run_graph_job.static_check for the H3 classes it can see on disk: returns the bad-input lines."""
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
    pair = WOMEN == 2
    # per-node key diffs vs the RS6 base (the base c0 ref_image_2 slot pointed at "sheet"; it now points at
    # the img2 face crop (pair) or is deleted (solo), so ref_images.ref_image_2 is a changed key in both cases)
    expect = {"c0": ["height", "length", "prompt", "ref_image_size", "ref_images.ref_image_2", "width"],
              "c1": ["audio_vae", "height", "prompt", "ref_image_size", "ref_images.ref_image_1", "width"],
              "img": ["image"], "noise": ["noise_seed"], "save": ["filename_prefix"], "win1": ["extension_frames"],
              "sheet": ["image"]}
    if pair:
        expect["img2"] = ["image"]    # new node = the right-hand woman's face crop
    print("=" * 110)
    print(f"{tag}  {ID}  seed {SEED}  women {WOMEN}  crops {' + '.join(c['crops'])}")
    src_text = open(SRC, "rb").read().decode("utf-8").replace("\r\n", "\n")
    base = json.loads(src_text)
    g = json.loads(src_text)
    p0 = open(c["p0"], encoding="utf-8").read().rstrip("\n")
    p1 = open(c["p1"], encoding="utf-8").read().rstrip("\n")

    # ---- deltas ----
    del g["sheet"]
    if pair:
        g["img2"] = {"class_type": "LoadImage", "inputs": {"image": "community/hc/" + c["crops"][1]}}
    i0 = g["c0"]["inputs"]
    i0["width"], i0["height"], i0["length"] = 1344, 768, 124
    i0["prompt"] = p0
    i0["ref_image_size"] = "match"
    i0["ref_images.ref_image_1"] = ["img", 0]
    if pair:
        i0["ref_images.ref_image_2"] = ["img2", 0]
    else:
        i0.pop("ref_images.ref_image_2", None)
    i1 = g["c1"]["inputs"]
    g["c1"]["class_type"] = "MiniMaxH3ImageToVideo"
    i1["width"], i1["height"] = 1344, 768
    i1["prompt"] = p1
    i1["length"] = ["win1", 1]
    i1.pop("audio_vae", None)   # MiniMaxH3ImageToVideo has NO audio_vae input (static_check rc=2, see header)
    for k in list(i1):
        if k.startswith("ref_"):
            del i1[k]
    g["win1"]["inputs"]["extension_frames"] = 119
    g["img"]["inputs"]["image"] = "community/hc/" + c["crops"][0]
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
    want_added = ["img2"] if pair else []
    want_nodes = sorted(expect)
    per_node_ok = True
    for nid, want in expect.items():
        ob = base.get(nid, {}).get("inputs", {})
        nb = new[nid]["inputs"] if nid in new else {}
        keys = sorted(k for k in set(ob) | set(nb)
                      if json.dumps(ob.get(k), sort_keys=True) != json.dumps(nb.get(k), sort_keys=True))
        if keys != want:
            per_node_ok = False
            print(f"     node {nid} changed keys {keys} != expected {want}")
    ck(added == want_added and removed == ["sheet"] and len(new) == len(base) - (0 if pair else 1)
       and diff == want_nodes and per_node_ok,
       f"1 graph diff vs {BASE_ID}: nodes +{added} -{removed}, count {len(new)}, changed nodes {diff}, per-node keys as expected: {per_node_ok}")
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

    # ---- CHECK 4: reference slots point at the face crops (the R4G2 headline check) ----
    r0 = sorted(k for k in new["c0"]["inputs"] if k.startswith("ref_images"))
    r1 = sorted(k for k in new["c1"]["inputs"] if k.startswith("ref_images"))
    want_r0 = sorted(["ref_images.ref_image_1"] + (["ref_images.ref_image_2"] if pair else []))
    slots_ok = (r0 == want_r0 and new["c0"]["inputs"]["ref_images.ref_image_1"] == ["img", 0]
                and (not pair or new["c0"]["inputs"]["ref_images.ref_image_2"] == ["img2", 0]))
    img_nodes = sorted(k for k, v in new.items() if v["class_type"] == "LoadImage")
    crop_paths = [os.path.join(HC_DIR, n) for n in c["crops"]]
    crops_ok = (img_nodes == (["img", "img2"] if pair else ["img"])
                and all(resolves("community/hc/" + n) and n.endswith("_face.png") for n in c["crops"])
                and "sheet" not in new and new["c1"]["class_type"] == "MiniMaxH3ImageToVideo" and r1 == [])
    pick_src = os.path.join(APPROVED, c["pick_src"][0], c["pick_src"][1])
    names = " + ".join(c["crops"])
    ck(slots_ok and crops_ok and os.path.isfile(pick_src),
       f"4 c0 reference slots {r0} -> nodes {img_nodes} -> {names} (face crops in ComfyUI\\input\\community\\hc, "
       f"no sheet node, no Klein sheet, c1 class {new['c1']['class_type']} with {len(r1)} reference images), "
       f"every crop cut from the approved pick {c['pick_src'][1]}: {os.path.isfile(pick_src)}")

    # ---- CHECK 5: ref_image_size = node default match on c0, no ref key on c1; crop px 400-550 ----
    from PIL import Image
    px = []
    for p in crop_paths:
        with Image.open(p) as im:
            px.append((os.path.basename(p), im.size))
    px_ok = all(w == h and 400 <= w <= 550 for _, (w, h) in px)
    ck(new["c0"]["inputs"]["ref_image_size"] == "match" and "ref_image_size" not in new["c1"]["inputs"] and px_ok,
       f"5 c0 ref_image_size = match (ref kept under the 1344x768 canvas px), c1 has no ref_image_size (0 refs), "
       f"crop sizes {px} all square 400-550 px: {px_ok}")

    # ---- CHECK 6: sampling / audio path identical to base, single pass, no RIFE/refine ----
    fixed = (new["unet"]["inputs"]["unet_name"].endswith("beta6_int8.safetensors")
             and new["ksel"]["inputs"]["sampler_name"] == "euler"
             and new["s0_sched"]["inputs"]["scheduler"] == "simple" and int(new["s0_sched"]["inputs"]["steps"]) == 10
             and new["s1_sched"]["inputs"]["scheduler"] == "simple" and int(new["s1_sched"]["inputs"]["steps"]) == 10
             and float(new["m_shift"]["inputs"]["shift_video"]) == 10.0 and float(new["m_shift"]["inputs"]["shift_audio"]) == 3.0
             and new["m_vsa"]["inputs"]["selection"] == "vsa"
             and json.dumps(new["tail1"]["inputs"], sort_keys=True) == json.dumps(base["tail1"]["inputs"], sort_keys=True)
             and all(json.dumps(new[n], sort_keys=True) == json.dumps(base[n], sort_keys=True)
                     for n in set(base) & set(new) - set(expect) - {"sheet"})
             and not any("RIFE" in v["class_type"] or "Refine" in v["class_type"] or "Upscale" in v["class_type"] for v in new.values())
             and new["dec_a"]["inputs"]["vae"] == ["avae", 0] and new["mkvid"]["inputs"]["audio"] == ["dec_a", 0]
             and len([v for v in new.values() if v["class_type"] == "SamplerCustomAdvanced"]) == 2
             and not any(v["class_type"] == "KSamplerAdvanced" for v in new.values()))
    ck(fixed, "6 sampling fixed as base (denoise 1.0 in the base sched/samplers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8), "
             "single pass (2 SamplerCustomAdvanced, no RIFE/refine/upscale), audio VAE + audio decoder wired, 1344x768")

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

    # ---- CHECK 8: R4G2 identity wording (F1-F5 kept) + close-up beats + picture binding ----
    ok8 = True
    ok8 &= DEF_HEAD in p0 and p0.count(DEF_TAIL) == WOMEN and BIND1 in p0 and (BIND2 in p0) == pair
    ok8 &= p1.count(BIND1) == 1 and "of the first 5 seconds of this clip" in p1
    ok8 &= "carries no reference pictures at all" in p1
    ok8 &= ("fully clothed" in p0 and FILLS in p0 and "tight close-up crop" in p0
            and ("face and her hair only" in p0 or "faces and the hair of the two women only" in p0))
    ok8 &= p0.count(CLOSE) >= WOMEN and p1.count(CLOSE) >= WOMEN
    nsub0 = len(re.findall(r"^<Subject \d> is", p0, flags=re.M))
    nsub1 = len(re.findall(r"^<Subject \d> is", p1, flags=re.M))
    ok8 &= nsub0 == WOMEN and nsub1 == WOMEN
    pics0 = sorted(set(re.findall(r"<Picture (\d)>", p0)))
    pics1 = sorted(set(re.findall(r"<Picture (\d)>", p1)))
    ok8 &= pics0 == ([str(i + 1) for i in range(WOMEN)]) and pics1 == ["1"]
    ok8 &= "photograph in <Picture 1> shows" not in p0 and "face is small in the frame" not in p0
    for line in p0.splitlines() + p1.splitlines():
        if BIND1 in line or BIND2 in line:
            ok8 &= not re.search(r"bikini|lingerie|robe|dress|top|shirt|shorts|clothing|wear", line, re.I)
    ck(ok8, f"8 R4G2 wording kept: {p0.count(DEF_TAIL)} extender-verbatim definition line(s) in c0 (women {WOMEN}), "
            f"{BIND1} in c0 and c1, {BIND2} in c0 = {pair}, c1 declares 0 reference pictures, picture = a tight close-up "
            f"crop of face and hair only (fully clothed source stated, no 'face is small' claim), close-up beats "
            f"{p0.count(CLOSE)}/{p1.count(CLOSE)}, subjects c0 {nsub0} c1 {nsub1}, <Picture> set c0 {pics0} c1 {pics1}, "
            f"no garment word inside any binding line")

    # ---- CHECK 9: id gates, id free, no render queued ----
    ralph = open(RALPH, encoding="utf-8-sig").read()
    pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
    free = (not os.path.exists(os.path.join(W, "p7", "jobs", f"{ID}.result.json"))
            and not os.path.exists(os.path.join(dst_dir, "objective.json"))
            and not os.path.exists(os.path.join(COMFY, "output", "community", ID)))
    ck(len(re.findall(r"^[a-z0-9_]+$", ID)) == 1 and len(pats) >= 2 and all(re.match(p, ID) for p in pats)
       and free and not os.path.exists(os.path.join(W, "p7", "JOB_REQUEST.json")),
       f"9 id charset + live ralph.ps1 id gates {pats}, id free (no result.json/objective.json/output folder), "
       f"no JOB_REQUEST.json queued (R4G2 = no render)")

    # ---- CHECK 10: crop provenance (bytes/sha + the face_crop.py log line for each crop) ----
    logtxt = open(os.path.join(W, "notes", "face_crop.log"), encoding="utf-8").read()
    rows = []
    ok10 = True
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
                    f"crop_box={rec.get('crop_box')} out_px={rec.get('out_px')} bytes={rec.get('bytes')} "
                    f"sha256={sha(p)[:12]}")
    ck(ok10, "10 every crop is logged by face_crop.py with ok=True, its --box, its source = the approved pick, "
             "out_px 512 and the byte count on disk: " + " | ".join(rows))
    # ---- CHECK 11: static-input self-check (offline clone of run_graph_job.static_check for the H3 nodes) ----
    sch = h3_schema()
    n_h3 = len([n for n in new.values() if n["class_type"] in sch])
    bad11 = scan(new, sch)
    avae_users = sorted(k for k, v in new.items() if any(isinstance(x, list) and x == ["avae", 0] for x in v["inputs"].values()))
    # the check must not be vacuous: it has to catch the exact defect that killed the r3 job at rc=2 (14:15 CT)
    dead = json.loads(open(os.path.join(W, "runs", "ali147_pool_hc_r3_s51130003", "request.api.json"),
                           encoding="utf-8").read())
    bad_dead = scan(dead, sch)
    ck(not bad11 and n_h3 >= 3 and "MiniMaxH3ImageToVideo" in sch
       and "audio_vae" in sch["MiniMaxH3ReferenceToVideo"][1]
       and "audio_vae" not in sch["MiniMaxH3ImageToVideo"][0] | sch["MiniMaxH3ImageToVideo"][1]
       and "audio_vae" not in new["c1"]["inputs"] and avae_users == ["c0", "dec_a"]
       and "c1.audio_vae: not an input of MiniMaxH3ImageToVideo" in bad_dead,
       f"11 static-input self-check vs the on-disk schema {os.path.basename(H3_SRC)} (the class that killed r3 at rc=2): "
       f"{n_h3} H3 nodes, every input name legal + all required inputs present {bad11 or 'OK'}; c1 carries no audio_vae; "
       f"avae feeds exactly {avae_users} (c0 ref audio + dec_a), so the audio path survives as in the rendered c2 clip; "
       f"the check is not vacuous - it reproduces the r3 defect {bad_dead}")

    print(f"{tag} graph bytes {len(data)} sha256 {hashlib.sha256(data).hexdigest()}")
    return data


want = sys.argv[1:] or sorted(CLIPS)
for tag in want:
    build(tag)
print("=" * 110)
if fails:
    print("CHECKS FAIL " + json.dumps(fails))
    sys.exit(1)
print(f"ALL CHECKS PASS ({n_pass} PASS lines, 11 numbered checks per clip: {want})")
