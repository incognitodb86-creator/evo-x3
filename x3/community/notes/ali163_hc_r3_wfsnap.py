import json, io
p = r'C:\Users\derek\5slock\image_flux2_klein_image_edit_9b_distilled.json'
d = json.load(open(p, encoding='utf-8-sig'))
out = []
WANT = {"LoadImage", "SaveImage", "UNETLoader", "CLIPLoader", "VAELoader", "CLIPTextEncode",
        "EmptyFlux2LatentImage", "RandomNoise", "KSamplerSelect", "Flux2Scheduler", "CFGGuider",
        "SamplerCustomAdvanced", "ReferenceLatent", "VAEEncode", "LoraLoaderModelOnly", "ModelSamplingFlux",
        "FluxGuidance", "ImageScale", "ImageResizeKJv2", "CheckpointLoaderSimple"}
links = {l[0]: l for l in d.get("links", [])}
for n in d["nodes"]:
    t = n.get("type")
    if t in WANT:
        w = [repr(x)[:600] for x in n.get("widgets_values", [])]
        ins = {}
        for i in n.get("inputs", []):
            lid = i.get("link")
            src = links.get(lid)
            ins[i.get("name")] = (src[1], src[2]) if src else None
        out.append("%s id=%s ins=%s widgets=%s" % (t, n.get("id"), json.dumps(ins), w))
io.open(r"C:\AI\community\notes\ali163_hc_r3_wfsnap.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(x[:400] for x in out))
