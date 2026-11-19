#!/usr/bin/env python3
r"""Self-setup 0.2: LOCAL probe 3 - R3b graph inputs, node signatures, model/pack inventory.

Read-only, CPU only. No GPU, no ComfyUI/llama-swap request, no render.
"""
import json
import os
import re

COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
CONT = os.path.join(COMFY, "custom_nodes", "ComfyUI-H3-Continuum")
COMM = r"C:/AI/community"

print("== R3b graph: real inputs (request.api.json) ==")
p = os.path.join(COMM, "runs", "ali147_pool_hc_r3b_s51130003", "request.api.json")
g = json.load(open(p, encoding="utf-8"))
for k in sorted(g, key=lambda s: (g[s]["class_type"], s)):
    v = g[k]
    inp = {ik: (json.dumps(iv)[:120] if not isinstance(iv, list) else "->" + str(iv))
           for ik, iv in v.get("inputs", {}).items()}
    print("  %-10s %-34s %s" % (k, v["class_type"], json.dumps(inp, ensure_ascii=False)[:420]))

def imgsize(path):
    try:
        b = open(path, "rb").read()
    except OSError:
        return "MISSING %s" % path
    if b[:8] == b"\x89PNG\r\n\x1a\n" and len(b) > 33:
        import struct
        w, h = struct.unpack(">II", b[16:24])
    elif b[:3] == b"\xff\xd8\xff":
        import struct
        i, w, h = 2, "?", "?"
        while i < len(b) - 9:
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seglen = struct.unpack(">H", b[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                break
            i += 2 + seglen
    else:
        return "NOT-IMAGE %d bytes" % len(b)
    return "%sx%s (%d KB)" % (w, h, len(b) // 1024)

print("\n== R3b LoadImage targets on disk ==")
seen = set()
for k, v in g.items():
    if v["class_type"] == "LoadImage":
        nm = v["inputs"].get("image")
        for base in (os.path.join(COMFY, "input"), os.path.join(COMFY, "output", "community")):
            cand = os.path.join(base, nm) if isinstance(nm, str) else None
            if cand and os.path.isfile(cand):
                print("  node %-6s %s -> %s" % (k, nm, imgsize(cand)))
                seen.add(cand)
                break
        else:
            print("  node %-6s %s -> not found under ComfyUI/input" % (k, nm))

print("\n== installed source signatures ==")
src = open(os.path.join(COMFY, "comfy_extras", "nodes_sparse_attention.py"),
           encoding="utf-8", errors="replace").read()
for cls in ("ModelAttentionBackend", "BlockSparseAttention"):
    m = re.search(r"class %s\b[\s\S]*?(?=\nclass |\Z)" % cls, src)
    if not m:
        print("  class %s NOT FOUND" % cls)
        continue
    body = m.group(0)
    keys = re.findall(r"io\.\w+\.Input\(\s*\"([a-z_0-9]+)\"", body)
    opts = re.findall(r"options=\[([^\]]{0,140})\]", body)
    print("  %-24s inputs=%s options=%s" % (cls, keys, opts))

for rel in ("comfy_extras/nodes_minimax_h3.py",):
    src = open(os.path.join(COMFY, rel), encoding="utf-8", errors="replace").read()
    for cls in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3LatentTailGuide", "MiniMaxH3GuidedContinuationWindow",
                "MiniMaxH3AppendContinuation"):
        m = re.search(r"class %s\b[\s\S]*?(?=\nclass |\Z)" % cls, src)
        print("  %-36s %s" % (cls, "ABSENT in " + rel if not m else
                              re.findall(r"io\.\w+\.Input\(\s*\"([a-z_0-9]+)\"", m.group(0))))

print("  which installed pack defines MiniMaxH3GuidedContinuationWindow / MiniMaxH3LatentTailGuide")
for d in sorted(os.listdir(os.path.join(COMFY, "custom_nodes"))):
    dd = os.path.join(COMFY, "custom_nodes", d)
    if not os.path.isdir(dd) or d.startswith("."):
        continue
    for root, dirs, files in os.walk(dd):
        if ".git" in root:
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            try:
                t = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for cls in ("MiniMaxH3GuidedContinuationWindow", "MiniMaxH3LatentTailGuide", "MiniMaxH3AppendContinuation"):
                if "class " + cls in t:
                    print("     %-38s %s (%s)" % (d, cls, fn))

print("\n== Continuum V39 sampler + hardening rule ==")
src = open(os.path.join(CONT, "v3", "driving_nodes.py"), encoding="utf-8", errors="replace").read()
m = re.search(r"class H3ContinuumSamplerV39\b[\s\S]*?(?=\nclass |\Z)", src)
body = m.group(0) if m else ""
print("  V39 class found:", bool(m), "| keys:", re.findall(r"io\.\w+\.Input\(\s*\"([A-Za-z_0-9]+)\"", body)[:30])
print("  V39 mentions negative:", "negative" in body, "| cfg:", len(re.findall(r"(?i)\bcfg\b", body)),
      "| guidance:", len(re.findall(r"(?i)guidance", body)))
m38 = re.search(r"class H3ContinuumSamplerV38\b[\s\S]*?(?=\nclass H3ContinuumSamplerV39|\nclass H3ContinuumMemory)", src)
if m38:
    print("  V38 keys:", re.findall(r"io\.\w+\.Input\(\s*\"([A-Za-z_0-9]+)\"", m38.group(0))[:30])
hp = os.path.join(CONT, "hardening.py")
if os.path.isfile(hp):
    lines = open(hp, encoding="utf-8", errors="replace").read().splitlines()
    for i, l in enumerate(lines, 1):
        if re.search(r"(?i)(target_frames|chunks \* chunk_seconds \* fps|must equal)", l):
            print("  hardening.py:%d %s" % (i, l.strip()[:130]))
else:
    print("  hardening.py: ABSENT at pack root (AGENTS.md cites v3/hardening.py)")
rp = os.path.join(CONT, "v3", "resolution.py")
rl = open(rp, encoding="utf-8", errors="replace").read().splitlines()
print("  resolution.py:48 =", rl[47].strip())

print("\n== model / pack inventory ==")
for sub in ("diffusion_models", "latent_upscale_models", "text_encoders", "vae", "audio_vae", "model_patches"):
    d = os.path.join(COMFY, "models", sub)
    if os.path.isdir(d):
        names = sorted(n for n in os.listdir(d) if not n.startswith("."))
        tag = [n for n in names if re.search(r"(?i)(beta8|beta6|1x_Ultcr|upscale)", n)]
        print("  models/%-19s %2d entries | beta/upscale hits: %s" % (sub, len(names), tag[:6]))

for probe in ("ComfyUI-Klein-9B-Native-Prompting", "ComfyUI_MiniMax_H3_Extender",
              "ComfyUI-H3-Continuum", "comfyui-storyboard", "MiniMax-H3-Prompt-Rewriter-ComfyUI",
              "ComfyUI-MiniMaxH3_LatentUpscaler", "Tr1dae", "ComfyUI-Minimax-H3-Continuation"):
    d = os.path.join(COMFY, "custom_nodes", probe)
    print("  pack %-40s present=%s" % (probe, os.path.isdir(d)))

ic = os.path.join(COMM, "tools", "infinite-creation")
print("  infinite-creation present=%s version=%s" % (
    os.path.isdir(ic),
    json.load(open(os.path.join(ic, "package.json"), encoding="utf-8")).get("version")
    if os.path.isfile(os.path.join(ic, "package.json")) else "no package.json"))
db = os.path.join(ic, "data", "infinite-creation.sqlite")
print("  ic db present=%s size=%s" % (os.path.isfile(db), os.path.getsize(db) if os.path.isfile(db) else 0))

print("\n== job results on disk ==")
res = sorted(n for n in os.listdir(os.path.join(COMM, "p7", "jobs")) if n.endswith(".result.json"))
print("  p7/jobs result.json count:", len(res))
for n in res[:12]:
    d = json.load(open(os.path.join(COMM, "p7", "jobs", n), encoding="utf-8"))
    print("   ", n, d.get("status"), d.get("kind"), str(d.get("output"))[:70])
print("\nPROBE3 DONE")
