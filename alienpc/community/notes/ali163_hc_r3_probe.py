# ALI-163 R3 probe (read-only, no GPU): Klein 9B edit graph assets on disk + the 6 placed HC stills.
import os, hashlib, json
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
PICKS = [
    ("HC1", "community/hc/HC1_Two_women_in_studio_editorial.jpg", "C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD004.jpg", "pair"),
    ("HC2", "community/hc/HC2_Two_women_in_passionate_embrace.jpg", "C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD007.jpg", "pair"),
    ("HC3", "community/hc/HC3_lesbian_beach.jpg", "C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19b/GI173.jpg", "pair"),
    ("HC4", "community/hc/HC4_strip_tease_aerobics.jpg", "C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19b/GI107.jpg", "solo"),
    ("HC5", "community/hc/HC5_spicy_solo.jpg", "C:/Users/derek/5slock/approved_characters/GROK_IMAGINE_2026-10-19b/GI150.jpg", "solo"),
    ("HC6", "community/hc/HC6_women_casino_lounge.jpg", "C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD076.jpg", "pair"),
]
MODELS = {
    "unet": "unet/FLUX-KLEIN-9B-FP8-NSFW.safetensors",
    "clip": "clip/qwen_3_8b_fp8mixed.safetensors",
    "vae": "vae/flux2-vae.safetensors",
    "lora_nsfw": "loras/klein_snofs_v1_4.safetensors",
}
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
print("== Klein graph assets (names taken from 5slock\\drv.py kedit_wf)")
for k, rel in MODELS.items():
    p = os.path.join(C, "models", rel.replace("/", os.sep))
    print(f"  {k}: {rel} exists={os.path.isfile(p)} size={os.path.getsize(p) if os.path.isfile(p) else -1}")
print("  loras with 'klein' in name:", [n for n in os.listdir(os.path.join(C, "models", "loras")) if "klein" in n.lower()])
print("  unet dir names with 'klein':", [n for n in os.listdir(os.path.join(C, "models", "unet")) if "klein" in n.lower()] if os.path.isdir(os.path.join(C, "models", "unet")) else "no models/unet")
for d in ("unet", "clip", "vae"):
    dd = os.path.join(C, "models", d)
    if os.path.isdir(dd):
        print(f"  models/{d} listing:", sorted(os.listdir(dd))[:24])
print("== placed HC stills in ComfyUI input")
from PIL import Image
for tag, rel, src, kind in PICKS:
    p = os.path.join(C, "input", rel.replace("/", os.sep))
    ok = os.path.isfile(p)
    sz = None
    if ok:
        im = Image.open(p); sz = im.size
    print(f"  {tag} {kind} {rel} exists={ok} size={sz} sha_in={sha(p)[:16] if ok else '-'} sha_src={sha(src)[:16]} src={os.path.isfile(src)}")
print("== RS016 sheet precedent (input) and output dirs")
rs = os.path.join(C, "input", "community", "RS016_portrait_1152x2016.png")
print("  RS016 input exists=", os.path.isfile(rs), Image.open(rs).size if os.path.isfile(rs) else None)
out = os.path.join(C, "output")
print("  output subdirs:", sorted([n for n in os.listdir(out) if os.path.isdir(os.path.join(out, n))])[:20])
print("== node class names exist in ComfyUI source (static_check runs live; source proof here)")
src = os.path.join(C, "comfy_extras")
targets = ["ReferenceLatent", "EmptyFlux2LatentImage", "Flux2Scheduler", "UNETLoader", "CLIPLoader", "VAELoader",
           "KSamplerSelect", "CFGGuider", "SamplerCustomAdvanced", "VAEEncode", "VAEDecode", "SaveImage", "CLIPTextEncode", "LoadImage"]
found = {}
files = [os.path.join(src, f) for f in os.listdir(src) if f.endswith(".py")]
files.append(os.path.join(C, "nodes.py"))
for f in files:
    t = open(f, encoding="utf-8", errors="replace").read()
    for c in targets:
        if c in t and c not in found:
            found[c] = os.path.basename(f)
for c in targets:
    print(f"  {c}: {found.get(c, 'NOT FOUND')}")
print("== venv/PIL check for the harness image branch (uses ffprobe only, no PIL import added)")
print("  director python:", os.path.isfile(r"C:\Users\derek\director\.venv\Scripts\python.exe"))
