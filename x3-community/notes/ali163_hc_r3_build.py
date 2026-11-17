# ALI-163 R3 builder + precheck (CPU only, no GPU, no network). Idempotent: rewrites request.api.json from the graph spec.
# Graph = the Klein 9B image-EDIT path proved on this box (C:\Users\derek\5slock\drv.py kedit_wf, node set + names copied from it):
#   LoadImage -> VAEEncode -> ReferenceLatent(pos/neg) -> CFGGuider(cfg 1) + Flux2Scheduler(steps 4) + SamplerCustomAdvanced -> VAEDecode -> SaveImage
# One job, 6 sheets, one sheet per pick, one seed per pick (51100001-51100006), 1152x2016 portrait = the RS016 sheet shape.
# No LoRA, no PuLID, no new character (TASKS.md R3). Models already on disk (notes\ali163_hc_r3_probe.py).
import os, sys, json, hashlib, re
sys.path.insert(0, r"C:\AI\community\scripts")
import comm

ARM = r"C:\AI\community\runs\ali147_pool_hc_sheet_s51120000"
ID = "ali147_pool_hc_sheet_s51120000"   # the id TASKS.md R-IDS spec names for the sheet job
UNET = "FLUX-KLEIN-9B-FP8-NSFW.safetensors"
CLIP = "qwen_3_8b_fp8mixed.safetensors"
VAE = "flux2-vae.safetensors"
W, H, STEPS, CFG, SEED0 = 1152, 2016, 4, 1.0, 51100000
NEG = "text, captions, letters, watermark, logo, signature, extra people, deformed hands, extra limbs, missing feet, cropped body, blurry, low resolution, cartoon, painting, anime"
SINGLE = ("reference sheet of the exact same adult woman as in the input photo: identical face, identical hair, identical skin tone "
          "and body proportions. One face close-up panel and a full-body turnaround of her - front view, side profile view, back view, "
          "three-quarter view - standing in a neutral relaxed pose, plain neutral grey studio background, even soft studio lighting, "
          "photorealistic skin, sharp focus, full figure inside the frame, no text, no watermark, no logos")
PAIR = ("reference sheet of the exact same two adult women as in the input photo: identical faces, identical hair, identical skin tones "
        "and body proportions. Two face close-up panels, one per woman, and a full-body turnaround of the two of them standing side by "
        "side in the same order as in the input photo - front view, side profile view, back view, three-quarter view - in a neutral "
        "relaxed pose, plain neutral grey studio background, even soft studio lighting, photorealistic skin, sharp focus, full figures "
        "inside the frame, no text, no watermark, no logos")
PICKS = [("HC1", "community/hc/HC1_Two_women_in_studio_editorial.jpg", "pair"),
         ("HC2", "community/hc/HC2_Two_women_in_passionate_embrace.jpg", "pair"),
         ("HC3", "community/hc/HC3_lesbian_beach.jpg", "pair"),
         ("HC4", "community/hc/HC4_strip_tease_aerobics.jpg", "solo"),
         ("HC5", "community/hc/HC5_spicy_solo.jpg", "solo"),
         ("HC6", "community/hc/HC6_women_casino_lounge.jpg", "pair")]

def build():
    g = {"unet": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
         "clip": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "flux2", "device": "default"}},
         "vae": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
         "empty": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
         "samp": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
         "sched": {"class_type": "Flux2Scheduler", "inputs": {"steps": STEPS, "width": W, "height": H}}}
    for i, (tag, img, kind) in enumerate(PICKS, 1):
        p = "p%d" % i
        g[p + "img"] = {"class_type": "LoadImage", "inputs": {"image": img}}
        g[p + "pos"] = {"class_type": "CLIPTextEncode", "inputs": {"text": PAIR if kind == "pair" else SINGLE, "clip": ["clip", 0]}}
        g[p + "neg"] = {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["clip", 0]}}
        g[p + "enc"] = {"class_type": "VAEEncode", "inputs": {"pixels": [p + "img", 0], "vae": ["vae", 0]}}
        g[p + "rpos"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": [p + "pos", 0], "latent": [p + "enc", 0]}}
        g[p + "rneg"] = {"class_type": "ReferenceLatent", "inputs": {"conditioning": [p + "neg", 0], "latent": [p + "enc", 0]}}
        g[p + "noise"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": SEED0 + i}}
        g[p + "cfg"] = {"class_type": "CFGGuider", "inputs": {"model": ["unet", 0], "positive": [p + "rpos", 0], "negative": [p + "rneg", 0], "cfg": CFG}}
        g[p + "sam"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": [p + "noise", 0], "guider": [p + "cfg", 0], "sampler": ["samp", 0], "sigmas": ["sched", 0], "latent_image": ["empty", 0]}}
        g[p + "dec"] = {"class_type": "VAEDecode", "inputs": {"samples": [p + "sam", 0], "vae": ["vae", 0]}}
        g[p + "save"] = {"class_type": "SaveImage", "inputs": {"images": [p + "dec", 0], "filename_prefix": "community/hc_sheets/" + tag}}
    return g

g = build()
os.makedirs(ARM, exist_ok=True)
raw = (json.dumps(g, indent=1, ensure_ascii=True) + "\n").encode("ascii")
open(os.path.join(ARM, "request.api.json"), "wb").write(raw.replace(b"\n", b"\r\n"))
print("wrote request.api.json", len(raw), "bytes, sha256", hashlib.sha256(open(os.path.join(ARM, "request.api.json"), "rb").read()).hexdigest())

fail = []
# 1) json.tool shape
j = json.loads(open(os.path.join(ARM, "request.api.json"), encoding="utf-8").read())
print("json ok, nodes", len(j))
# 2) models on disk: resolve the way ComfyUI does (clip also lives in text_encoders)
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
def model_ok(folder_rel, name):
    if not name: return None
    subs = ["clip", "text_encoders"] if folder_rel == "clip" else [folder_rel]
    for sub in subs:
        p = os.path.join(C, "models", sub, name.replace("/", os.sep))
        if os.path.isfile(p): return sub
    return None
for k, n in j.items():
    if n["class_type"] == "UNETLoader": print("  unet", model_ok("unet", n["inputs"]["unet_name"]))
    if n["class_type"] == "CLIPLoader": print("  clip", model_ok("clip", n["inputs"]["clip_name"]), "type", n["inputs"]["type"])
    if n["class_type"] == "VAELoader": print("  vae", model_ok("vae", n["inputs"]["vae_name"]))
    if n["class_type"] == "UNETLoader" and not model_ok("unet", n["inputs"]["unet_name"]): fail.append(k + " unet missing")
    if n["class_type"] == "CLIPLoader" and not model_ok("clip", n["inputs"]["clip_name"]): fail.append(k + " clip missing")
    if n["class_type"] == "VAELoader" and not model_ok("vae", n["inputs"]["vae_name"]): fail.append(k + " vae missing")
# 3) no new LoRA / no download / no new character / no PuLID
for k, n in j.items():
    if n["class_type"] in ("LoraLoader", "LoraLoaderModelOnly", "PuLIDModelLoader", "ApplyPuLIDFlux2"): fail.append(k + " forbidden node " + n["class_type"])
    for v in n["inputs"].values():
        if isinstance(v, str) and v.lower().endswith(".safetensors") and "klein" in v.lower() and n["class_type"] != "UNETLoader": fail.append(k + " lora " + v)
# 4) LoadImage strings resolve inside ComfyUI input, byte-equal to the approved source
APPROVED = r"C:\Users\derek\5slock\approved_characters"
SRC = {"HC1": "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD004.jpg", "HC2": "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD007.jpg",
       "HC3": "GROK_IMAGINE_2026-10-19b/GI173.jpg", "HC4": "GROK_IMAGINE_2026-10-19b/GI107.jpg",
       "HC5": "GROK_IMAGINE_2026-10-19b/GI150.jpg", "HC6": "FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD076.jpg"}
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
from PIL import Image
for tag, rel, kind in PICKS:
    p = os.path.join(C, "input", rel.replace("/", os.sep))
    a = os.path.join(APPROVED, SRC[tag].replace("/", os.sep))
    okp = os.path.isfile(p)
    same = okp and os.path.isfile(a) and sha(p) == sha(a)
    sz = Image.open(p).size if okp else None
    print("  LoadImage", tag, rel, "exists", okp, "byte-equal-to-approved", same, "size", sz, kind)
    if not (okp and same and sz): fail.append(tag + " LoadImage not placed / not byte-equal")
# 5) sheet size = RS016 shape; links valid; grid rule of the video path does not apply to images
if (j["empty"]["inputs"]["width"], j["empty"]["inputs"]["height"]) != (1152, 2016): fail.append("sheet canvas not 1152x2016")
if Image.open(os.path.join(C, "input", "community", "RS016_portrait_1152x2016.png")).size != (1152, 2016): fail.append("RS016 precedent size changed")
for k, n in j.items():
    for a, v in n["inputs"].items():
        if isinstance(v, list) and isinstance(v[0], str) and v[0] not in j: fail.append(f"{k}.{a} link to missing node {v[0]}")
# 6) adults-only guard on every text input (the harness scans only "prompt" inputs, so check "text" here)
for k, n in j.items():
    for a, v in n["inputs"].items():
        if isinstance(v, str) and a in ("text", "prompt"):
            ok = comm.guard_ok(v)
            words = [w for w in ("girl", "teen", "young", "boy", "child", "student", "minor", "school", "loli") if w in v.lower()]
            print("  guard", k, a, "guard_ok", ok, "bad-words", words, "len", len(v))
            if not ok or words: fail.append(f"{k}.{a} guard/adult-word problem")
# 7) job id shape (parsed from the LIVE ralph.ps1, no hardcoded copy) + budget gate + id free
ralph = open(r"C:\Users\derek\5slock\ralph-community\ralph.ps1", encoding="utf-8-sig").read()
pats = [p.split("'", 2)[1] for p in re.findall(r"-notmatch\s*'[^']+'", ralph) if "ali147_pool" in p]
for pt in pats: print("  id pattern", pt, "match", bool(re.match(pt, ID)))
if not all(re.match(pt, ID) for pt in pats): fail.append("id refused by ralph.ps1 patterns")
b = json.load(open(r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"))
print("  budget", b)
if b["used_min"] >= 475 or b["jobs"] >= 32: fail.append("budget gate blocks the request")
for f in ("status.log", "objective.json", ID + ".mp4", ID + ".api.json", r"C:\Users\derek\5slock\ralph-community\p7\jobs\%s.result.json" % ID):
    if os.path.exists(f): fail.append("id in use: " + f)
if os.path.exists("C:/Users/derek/5slock/ralph-community/p7/JOB_REQUEST.json"): fail.append("p7 JOB_REQUEST.json already exists (job pending)")
# 8) sheets land in ComfyUI output under community/hc_sheets (nothing is copied into input by this job)
for tag, rel, kind in PICKS:
    print("  save prefix ->", os.path.join(C, "output", "community", "hc_sheets", tag + "_00001_.png"))
print("MODEL_CHAIN:", sorted({n["class_type"] for n in j.values()}))
print("RESULT:", "PASS" if not fail else "FAIL " + " | ".join(fail))
