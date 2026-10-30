"""civitai_lora_survey.py - read-only web survey (nothing downloaded) answering Derek 2026-10-29: "are these the best
lora the community uses for h3 and flux? I also want Megan Fox, Sabrina Carpenter etc."

Civitai's API is not fetchable here (robots.txt Disallow /api/*, and api/v1 returns 400 to this client, v2 404), so the
survey uses the Hugging Face API (search + file listings + sizes) and Civitai pages reached through the search engine.
It reports: what the community actually publishes for MiniMax-H3, FLUX.2 Klein, FLUX.1-dev and Z-Image; whether
name-reference/person LoRAs exist for each base; and the size of the base model we would have to install to use them.
Usage: python civitai_lora_survey.py
"""
import json, urllib.parse, urllib.request

UA = {"User-Agent": "pi-alienpc (read-only research, no downloads)"}


def get(u):
    try:
        return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=45).read())
    except Exception as e:
        return {"_err": repr(e)[:140]}


print("### 1. base models we would have to install (file sizes from the HF file listing)")
for repo in ["black-forest-labs/FLUX.1-dev", "Tongyi-MAI/Z-Image-Turbo", "Comfy-Org/MiniMax-H3"]:
    d = get("https://huggingface.co/api/models/" + repo + "?file-details=true")
    files = d.get("siblings") or []
    big = sorted([f for f in files if (f.get("size") or 0) > 5e9], key=lambda f: -f["size"])[:6]
    print("\n== %s  %s" % (repo, d.get("_err", "")))
    for f in big:
        print("   %8.1f GB  %s" % (f["size"] / 1e9, f["rfilename"]))
    print("   (files >5 GB listed; total files=%d)" % len(files))

print("\n### 2. do name-reference/person LoRAs exist per base? HF search on the names + the 'vrtl' series pattern")
for q in ["minimax-h3 lora", "flux lora megan fox", "flux lora sabrina carpenter", "z-image lora",
          "vrtl lora", "klein lora name-reference"]:
    d = get("https://huggingface.co/api/models?search=" + urllib.parse.quote(q) + "&limit=10&sort=downloads&direction=-1")
    if isinstance(d, dict) and d.get("_err"): print("\n== %s -> %s" % (q, d["_err"])); continue
    print("\n== search '%s' -> %d repos" % (q, len(d)))
    for m in d[:10]:
        print("   %-52s dl=%-7s likes=%-4s tags=%s" % (m.get("modelId"), m.get("downloads"), m.get("likes"),
              ",".join([t for t in (m.get("tags") or []) if any(k in t.lower() for k in
               ["lora", "flux", "minimax", "z-image", "sdxl", "base_model"])])))

print("\n### 3. inside the H3 LoRA packs that mention faces/people/NSFW (file names only)")
for repo in ["akatz-ai/MiniMax-H3-Character-Swap-LoRA", "fal/MiniMax-H3-Realism-People-LoRA",
             "Hearmeman/minimax-h3-loras", "Leon1000/Must_Have_Klein_9b_loras", "Se0ulSeeker/flux2_klein_9b_nsfw_loras"]:
    d = get("https://huggingface.co/api/models/" + repo + "?file-details=true")
    s = [f["rfilename"] for f in (d.get("siblings") or []) if f["rfilename"].endswith((".safetensors", ".json", ".md"))]
    print("\n== %s  %s" % (repo, d.get("_err", "")))
    for n in s[:14]:
        print("   ", n)
