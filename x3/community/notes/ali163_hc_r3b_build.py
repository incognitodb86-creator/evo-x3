# ALI-163 R3 (REOPENED by Max 2026-10-23 11:16 AM CT) builder + precheck. CPU only, no GPU, no network.
# Max: "pair picks use ONE SHEET PER WOMAN per R1 (RS4/RS6 wording, <Picture 1..4>); the combined two-women sheet is not used.
#  keep its solo sheets (HC4, HC5) and redo the pair sheets (HC1, HC2, HC3, HC6) one per woman".
# So this graph = 10 sheets in ONE job: 8 per-woman Klein 9B image-EDIT chains (one per woman of the 4 pair picks)
# + the 2 UNCHANGED solo chains (HC4, HC5: same prompt text, same seed, same save prefix as the queued graph).
# No crop / no reframe / no outpaint of the picks: the pair source image goes in as-is and Klein isolates one woman by
# instruction (Remove the other adult woman), which is the FLUX.2 klein edit path proved on this box by 5slock\drv.py kedit_wf.
# Source: C:\AI\community\notes\hc_redo_research_20261023.md (R1 face-lock + sheet shape), RS016 sheet 1152x2016,
# approved_characters\FLOW_BLONDE_DARK_PAIRS_2026-10-19\CHARACTER.md ("both a blonde woman and a dark-haired woman together")
# = the only text descriptor for BD004/BD007/BD076; GROK_IMAGINE_2026-10-19b\GI173 has no hair descriptor -> positional (left/right).
import os, sys, json, hashlib, re
sys.path.insert(0, r"C:\AI\community\scripts")
import comm

ARM = r"C:\AI\community\runs\ali147_pool_hc_sheet_s51120000"
ID = "ali147_pool_hc_sheet_s51120000"
REQ = r"C:\AI\community\p7\JOB_REQUEST.json"
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
APPROVED = r"C:\Users\derek\5slock\approved_characters"
UNET = "FLUX-KLEIN-9B-FP8-NSFW.safetensors"
CLIP = "qwen_3_8b_fp8mixed.safetensors"
VAE = "flux2-vae.safetensors"
W, H, STEPS, CFG = 1152, 2016, 4, 1.0
NEG = ("text, captions, letters, watermark, logo, signature, extra people, second person, two people, multiple people, "
       "duplicated person, merged bodies, deformed hands, extra limbs, missing feet, cropped body, blurry, low resolution, "
       "cartoon, painting, anime")
# solo chains kept byte-for-byte as the queued graph had them (Max: "keep its solo sheets (HC4, HC5)")
SINGLE = ("reference sheet of the exact same adult woman as in the input photo: identical face, identical hair, identical skin tone "
          "and body proportions. One face close-up panel and a full-body turnaround of her - front view, side profile view, back view, "
          "three-quarter view - standing in a neutral relaxed pose, plain neutral grey studio background, even soft studio lighting, "
          "photorealistic skin, sharp focus, full figure inside the frame, no text, no watermark, no logos")
WOMAN = ("reference sheet of ONE adult woman only, taken from the input photo: {who}. The other adult woman in the input photo is "
         "removed and must not appear anywhere in the image. Identical face, identical hair, identical skin tone and body proportions "
         "as {who2}. One face close-up panel of her and a full-body turnaround of her alone - front view, side profile view, back view, "
         "three-quarter view - standing in a neutral relaxed pose, plain neutral grey studio background, even soft studio lighting, "
         "photorealistic skin, sharp focus, full figure inside the frame, exactly one person in the image, no text, no watermark, no logos")

# (node prefix, save prefix, source pick tag, seed, prompt kind, who/who2 wording)
SHEETS = [
 ("hc1w1", "HC1_w1_blonde",   "HC1", 51120001, "the blonde adult woman in the input photo", "the blonde adult woman in the input photo"),
 ("hc1w2", "HC1_w2_darkhair", "HC1", 51120002, "the dark-haired adult woman in the input photo", "the dark-haired adult woman in the input photo"),
 ("hc2w1", "HC2_w1_blonde",   "HC2", 51120003, "the blonde adult woman in the input photo", "the blonde adult woman in the input photo"),
 ("hc2w2", "HC2_w2_darkhair", "HC2", 51120004, "the dark-haired adult woman in the input photo", "the dark-haired adult woman in the input photo"),
 ("hc3w1", "HC3_w1_left",     "HC3", 51120005, "the adult woman on the left side of the input photo", "the adult woman on the left side of the input photo"),
 ("hc3w2", "HC3_w2_right",    "HC3", 51120006, "the adult woman on the right side of the input photo", "the adult woman on the right side of the input photo"),
 ("hc4",   "HC4",             "HC4", 51100004, None, None),
 ("hc5",   "HC5",             "HC5", 51100005, None, None),
 ("hc6w1", "HC6_w1_blonde",   "HC6", 51120007, "the blonde adult woman in the input photo", "the blonde adult woman in the input photo"),
 ("hc6w2", "HC6_w2_darkhair", "HC6", 51120008, "the dark-haired adult woman in the input photo", "the dark-haired adult woman in the input photo"),
]
IMG = {"HC1": "community/hc/HC1_Two_women_in_studio_editorial.jpg",
       "HC2": "community/hc/HC2_Two_women_in_passionate_embrace.jpg",
       "HC3": "community/hc/HC3_lesbian_beach.jpg",
       "HC4": "community/hc/HC4_strip_tease_aerobics.jpg",
       "HC5": "community/hc/HC5_spicy_solo.jpg",
       "HC6": "community/hc/HC6_women_casino_lounge.jpg"}
SRC = {"HC1": "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD004.jpg", "HC2": "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD007.jpg",
       "HC3": "GROK_IMAGINE_2026-10-19b/GI173.jpg", "HC4": "GROK_IMAGINE_2026-10-19b/GI107.jpg",
       "HC5": "GROK_IMAGINE_2026-10-19b/GI150.jpg", "HC6": "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD076.jpg"}

def build():
    g = {"unet": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
         "clip": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "flux2", "device": "default"}},
         "vae": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
         "empty": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
         "samp": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
         "sched": {"class_type": "Flux2Scheduler", "inputs": {"steps": STEPS, "width": W, "height": H}}}
    for pfx, tag, pick, seed, who, who2 in SHEETS:
        text = SINGLE if who is None else WOMAN.format(who=who, who2=who2)
        g[pfx + "img"] = {"class_type": "LoadImage", "inputs": {"image": IMG[pick]}}
        g[pfx + "pos"] = {"class_type": "CLIPTextEncode", "inputs": {"text": text, "clip": ["clip", 0]}}
        g[pfx + "neg"] = {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["clip", 0]}}
        g[pfx + "enc"] = {"class_type": "VAEEncode", "inputs": {"pixels": [pfx + "img", 0], "vae": ["vae", 0]}}
        g[pfx + "rpos"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": [pfx + "pos", 0], "latent": [pfx + "enc", 0]}}
        g[pfx + "rneg"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": [pfx + "neg", 0], "latent": [pfx + "enc", 0]}}
        g[pfx + "noise"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}}
        g[pfx + "cfg"] = {"class_type": "CFGGuider", "inputs": {"model": ["unet", 0], "positive": [pfx + "rpos", 0], "negative": [pfx + "rneg", 0], "cfg": CFG}}
        g[pfx + "sam"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": [pfx + "noise", 0], "guider": [pfx + "cfg", 0], "sampler": ["samp", 0], "sigmas": ["sched", 0], "latent_image": ["empty", 0]}}
        g[pfx + "dec"] = {"class_type": "VAEDecode", "inputs": {"samples": [pfx + "sam", 0], "vae": ["vae", 0]}}
        g[pfx + "save"] = {"class_type": "SaveImage", "inputs": {"images": [pfx + "dec", 0], "filename_prefix": "community/hc_sheets/" + tag}}
    return g

fail = []
os.makedirs(ARM, exist_ok=True)
raw = (json.dumps(build(), indent=1, ensure_ascii=True) + "\n").encode("ascii")
open(os.path.join(ARM, "request.api.json"), "wb").write(raw.replace(b"\n", b"\r\n"))
graph = open(os.path.join(ARM, "request.api.json"), "rb").read()
print("wrote request.api.json", len(graph), "bytes, sha256", hashlib.sha256(graph).hexdigest())
j = json.loads(graph.decode("utf-8"))
print("1) json.tool shape ok, nodes", len(j), "chains", len(SHEETS))

def model_ok(folder_rel, name):
    subs = ["clip", "text_encoders"] if folder_rel == "clip" else [folder_rel]
    for sub in subs:
        p = os.path.join(C, "models", sub, name.replace("/", os.sep))
        if os.path.isfile(p): return sub
    return None
for k, n in j.items():
    ct = n["class_type"]
    if ct == "UNETLoader":
        r = model_ok("unet", n["inputs"]["unet_name"]); print("2) unet", r); fail += [] if r else [k + " unet missing"]
    if ct == "CLIPLoader":
        r = model_ok("clip", n["inputs"]["clip_name"]); print("2) clip", r, "type", n["inputs"]["type"]); fail += [] if r else [k + " clip missing"]
    if ct == "VAELoader":
        r = model_ok("vae", n["inputs"]["vae_name"]); print("2) vae", r); fail += [] if r else [k + " vae missing"]
    if ct in ("LoraLoader", "LoraLoaderModelOnly", "PuLIDModelLoader", "ApplyPuLIDFlux2", "IPAdapterUnifiedLoader", "ControlNetLoader"):
        fail.append(k + " forbidden node " + ct)
print("3) forbidden-node scan (LoRA / PuLID / IPAdapter / ControlNet):", "clean" if not any("forbidden" in f for f in fail) else "HIT")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
from PIL import Image
for tag, rel in IMG.items():
    p = os.path.join(C, "input", rel.replace("/", os.sep)); a = os.path.join(APPROVED, SRC[tag].replace("/", os.sep))
    okp = os.path.isfile(p); same = okp and os.path.isfile(a) and sha(p) == sha(a); sz = Image.open(p).size if okp else None
    print("4) LoadImage", tag, rel, "exists", okp, "byte-equal-to-approved", same, "size", sz)
    if not (okp and same and sz): fail.append(tag + " LoadImage not placed / not byte-equal")
if (j["empty"]["inputs"]["width"], j["empty"]["inputs"]["height"]) != (1152, 2016): fail.append("sheet canvas not 1152x2016")
if (j["sched"]["inputs"]["width"], j["sched"]["inputs"]["height"], j["sched"]["inputs"]["steps"]) != (1152, 2016, 4): fail.append("scheduler shape/steps")
if Image.open(os.path.join(C, "input", "community", "RS016_portrait_1152x2016.png")).size != (1152, 2016): fail.append("RS016 precedent size changed")
for k, n in j.items():
    for a, v in n["inputs"].items():
        if isinstance(v, list) and isinstance(v[0], str) and v[0] not in j: fail.append(f"{k}.{a} link to missing node {v[0]}")
# 5) layout gate: exactly one chain per woman of a pair pick, one per solo pick, unique prefixes, solo chains untouched
pref = [s[1] for s in SHEETS]
per = {}
for pfx, tag, pick, seed, who, who2 in SHEETS: per[pick] = per.get(pick, 0) + 1
print("5) sheets per pick", per, "unique prefixes", len(set(pref)) == len(pref))
if per != {"HC1": 2, "HC2": 2, "HC3": 2, "HC4": 1, "HC5": 1, "HC6": 2}: fail.append("pair sheets are not one-per-woman")
if len(set(pref)) != len(pref): fail.append("save prefix collision")
if j["hc4pos"]["inputs"]["text"] != SINGLE or j["hc5pos"]["inputs"]["text"] != SINGLE: fail.append("solo prompt text changed")
if j["hc4save"]["inputs"]["filename_prefix"] != "community/hc_sheets/HC4" or j["hc5save"]["inputs"]["filename_prefix"] != "community/hc_sheets/HC5": fail.append("solo save prefix changed")
if j["hc4noise"]["inputs"]["noise_seed"] != 51100004 or j["hc5noise"]["inputs"]["noise_seed"] != 51100005: fail.append("solo seed changed")
if len({n["inputs"]["noise_seed"] for k, n in j.items() if n["class_type"] == "RandomNoise"}) != len(SHEETS): fail.append("seeds not one per sheet")
# 6) adults-only guard on every text input (the harness only guard-checks "prompt" keys)
BAD = ("girl", "teen", "young", "boy", "child", "student", "minor", "school", "loli", "kid")
for k, n in j.items():
    for a, v in n["inputs"].items():
        if isinstance(v, str) and a in ("text", "prompt"):
            words = [w for w in BAD if w in v.lower()]
            if not comm.guard_ok(v) or words: fail.append(f"{k}.{a} guard/adult-word problem {words}")
print("6) guard_ok on all", sum(1 for n in j.values() for a, v in n["inputs"].items() if isinstance(v, str) and a == "text"), "text inputs:", "clean" if not any("guard" in f for f in fail) else "HIT")
# 7) pair-isolation wording present on every pair chain
for pfx, tag, pick, seed, who, who2 in SHEETS:
    if who is None: continue
    t = j[pfx + "pos"]["inputs"]["text"]
    if who not in t or "removed" not in t or "exactly one person" not in t: fail.append(pfx + " isolation wording missing")
print("7) pair per-woman isolation wording on 8 pair chains:", "clean" if not any("isolation" in f for f in fail) else "HIT")
# 8) id accepted by the LIVE ralph.ps1 gates + budget gate + id free
ralph = open(r"C:\Users\derek\5slock\ralph-community\ralph.ps1", encoding="utf-8-sig").read()
pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
for pt in pats: print("8) id pattern", pt, "match", bool(re.match(pt, ID)))
if not (pats and all(re.match(pt, ID) for pt in pats)): fail.append("id refused by ralph.ps1 patterns")
b = json.load(open(r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"))
print("8) budget", b)
if b["used_min"] >= 475 or b["jobs"] >= 32: fail.append("budget gate blocks the request (BLOCKED: batch budget)")
for f in (os.path.join(ARM, "status.log"), os.path.join(ARM, "objective.json"), os.path.join(ARM, ID + ".mp4"), os.path.join(ARM, ID + ".api.json"),
          r"C:\Users\derek\5slock\ralph-community\p7\jobs\%s.result.json" % ID, r"C:\AI\community\p7\jobs\%s.result.json" % ID):
    if os.path.exists(f): fail.append("id in use: " + f)
print("8) id free (no result.json / objective.json / status.log / mp4 / .api.json):", "clean" if not any("id in use" in f for f in fail) else "HIT")
# 9) the queued request file: exactly this one job, parses, trailing newline (not rewritten: the id is unchanged)
rq = open(REQ, "rb").read()
rj = json.loads(rq.decode("utf-8"))
job = rj["jobs"]
print("9) JOB_REQUEST.json", len(rq), "bytes sha256", hashlib.sha256(rq).hexdigest(), "trailing-newline", rq.endswith(b"\n"), "jobs", job)
if len(job) != 1 or job[0]["id"] != ID or job[0].get("kind") != "graph" or job[0].get("frames") != 0 or job[0].get("frames_tol") != 0: fail.append("request shape")
if os.path.exists(r"C:\Users\derek\5slock\ralph-community\p7\JOB_REQUEST.json"): fail.append("stray ralph-community p7 request exists")
# 10) sheet map for R3V / R4-R9 (notes only, no GPU)
MAP = r"C:\AI\community\notes\hc_sheets_map_20261023.md"
lines = ["# ALI-163 R3 (reopened) reference-sheet map, 2026-10-23 - job %s, 1152x2016 png, RS016 shape, Klein 9B image-EDIT (cfg 1.0, euler, 4 steps, no LoRA)." % ID,
         "# One sheet PER WOMAN for pair picks (Max 11:16 AM CT); solo chains HC4/HC5 unchanged from the queued graph.",
         "# Source picks are byte-equal copies in ComfyUI\\input\\community\\hc (verified below). Isolation is a Klein edit instruction, never a crop/reframe of the pick.",
         "# Sheet png lands in ComfyUI\\output\\community\\hc_sheets\\<prefix>_00001_.png; R4-R9 place/reference it by that name.",
         "",
         "| sheet png | source pick | LoadImage string | seed | isolation wording |",
         "|---|---|---|---|---|"]
for pfx, tag, pick, seed, who, who2 in SHEETS:
    lines.append("| HC sheet %s | %s (%s) | %s | %d | %s |" % (tag, pick, SRC[pick], IMG[pick], seed, "solo pick, whole image" if who is None else who))
lines += ["",
          "Pair clips (HC1/HC2/HC3/HC6) bind, per RS4/RS6 wording: <Picture 1> = the placed pair pick, <Picture 2> = the sheet named *_w1_*, <Picture 3> = the sheet named *_w2_*;",
          "<Subject 1> = the woman of sheet 2, <Subject 2> = the woman of sheet 3. Solo clips (HC4/HC5): <Picture 1> = the pick, <Picture 2> = its solo sheet.",
          "w1 = blonde (BD picks) / left (GI173); w2 = dark-haired (BD picks) / right (GI173). Hair wording rests on FLOW_BLONDE_DARK_PAIRS_2026-10-19\\CHARACTER.md."]
open(MAP, "w", encoding="utf-8", newline="\r\n").write("\n".join(lines) + "\n")
print("10) wrote", MAP)
print("MODEL_CHAIN:", sorted({n["class_type"] for n in j.values()}))
print("RESULT:", "PASS" if not fail else "FAIL " + " | ".join(fail))
