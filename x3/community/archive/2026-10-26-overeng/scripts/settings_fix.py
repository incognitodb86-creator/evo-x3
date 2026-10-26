# Approved TenStrip settings fixes (Derek 2026-10-20 10:30 AM CT). Backs up every file first.
import json, os, shutil, datetime
SUF = ".bak-20261020-settings"
def bak(p):
    b = p + SUF
    if not os.path.exists(b): shutil.copy2(p, b)
    print("BACKUP", p, "->", b)
WF = r"C:\Users\derek\5slock\workflows"
for name in sorted(os.listdir(WF)):
    if not name.endswith(".json"): continue
    p = os.path.join(WF, name); g = json.load(open(p, encoding="utf-8")); bak(p)
    before = (g["130"]["inputs"]["shift_video"], g["130"]["inputs"]["shift_audio"], g["9"]["inputs"]["steps"], g["17"]["inputs"]["sampler_name"], g["9"]["inputs"]["scheduler"])
    for n in g.values():
        if n.get("class_type") == "LoraLoaderModelOnly" and "beta6mix" in n["inputs"]["lora_name"].lower():
            raise SystemExit(f"beta6mix LoRA stacked in {name}")
    g["130"]["inputs"]["shift_video"] = 10.0; g["130"]["inputs"]["shift_audio"] = 3.0
    g["9"]["inputs"]["steps"] = 10; g["9"]["inputs"]["scheduler"] = "simple"; g["17"]["inputs"]["sampler_name"] = "euler"
    if "201" not in g:
        src = g["130"]["inputs"]["model"]
        g["200"] = {"class_type": "ModelAttentionBackend", "inputs": {"model": src, "attention": "comfy kitchen attention"}, "_meta": {"title": "Attention backend (TenStrip beta6)"}}
        g["201"] = {"class_type": "BlockSparseAttention", "inputs": {"model": ["200", 0], "selection": "vsa", "selection.keep_percent": 10,
                    "start_percent": 0.2, "end_percent": 1.0, "dense_blocks": "", "min_tokens": 12288, "extra_tokens": 256,
                    "sink_conditioning": "exact_kv_and_rows", "verbose": False}, "_meta": {"title": "VSA sparse attention (TenStrip beta6)"}}
        g["130"]["inputs"]["model"] = ["201", 0]
    json.dump(g, open(p, "w", encoding="utf-8", newline=""), indent=1)
    print(f"FIX {name}: shift/audio/steps/sampler/sched {before} -> (10.0, 3.0, 10, euler, simple) + VSA")
# Switchyard live config: video.steps 8 -> 10 (config only, no code)
p = r"C:\AI\director\config\director.live.yaml"; bak(p)
L = open(p, encoding="utf-8", newline="").read().split("\n"); vi = [x.rstrip("\r") for x in L].index("video:"); done = False
for i in range(vi + 1, len(L)):
    if L[i].rstrip("\r") and not L[i].startswith(" "): break
    if L[i].rstrip("\r") == "  steps: 8": L[i] = L[i].replace("steps: 8", "steps: 10"); done = True; print(f"FIX director.live.yaml line {i+1}: video.steps 8 -> 10"); break
assert done, "video.steps line not found"
open(p, "w", encoding="utf-8", newline="").write("\n".join(L))
# pipeline_defaults.json clip.steps 8 -> 10
p = r"C:\Users\derek\5slock\loop1017\pipeline_defaults.json"; bak(p)
d = json.load(open(p, encoding="utf-8")); print("pipeline_defaults clip before", d["clip"]["steps"], d["clip"]["shift"], d["clip"]["sampler"])
d["clip"]["steps"] = 10; d["clip"]["shift"] = 10; d["clip"]["audio_shift"] = 3; d["clip"]["scheduler"] = "simple"
d["clip"]["settings_fix"] = "2026-10-20 TenStrip: 10 steps default (8 drafts), shift 10/3, euler/simple, VSA keep 10 start 0.2; never stack Eros_beta6mix_Lora on beta6; ref image aspect = output (Derek approved 10:30 AM CT)"
json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("DONE")
