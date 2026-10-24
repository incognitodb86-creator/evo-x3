#!/usr/bin/env python3
r"""Self-setup 0.2: LOCAL probe 2 - Continuum V39 internals, sparse-attention schema,
the R3b graph settings, and the small arithmetic claims in AGENTS.md.

Read-only, CPU only. No GPU, no ComfyUI/llama-swap request, no render.
"""
import json
import os
import re

COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
CONT = os.path.join(COMFY, "custom_nodes", "ComfyUI-H3-Continuum")
COMM = r"C:/AI/community"

print("== Continuum pack version (claim: 3.10.2) ==")
for cand in ("pyproject.toml", "version.py", "__init__.py", "VERSION"):
    p = os.path.join(CONT, cand)
    if os.path.isfile(p):
        t = open(p, encoding="utf-8", errors="replace").read()
        for line in t.splitlines():
            if re.search(r"(?i)(version|__version__)", line):
                print("  %s: %s" % (cand, line.strip()[:120]))
git = os.path.join(CONT, ".git")
if os.path.isdir(git):
    import subprocess
    for args in (["git", "-C", CONT, "describe", "--tags"], ["git", "-C", CONT, "log", "-1", "--format=%h %ad %s", "--date=short"]):
        r = subprocess.run(args, capture_output=True, text=True)
        print("  $", " ".join(args[1:4]), "->", (r.stdout or r.stderr).strip()[:120])

print("\n== canvas multiple of 32 (claim: v3/resolution.py H3_CANVAS_MULTIPLE) ==")
hits = []
for root, dirs, files in os.walk(CONT):
    if ".git" in root:
        continue
    for fn in files:
        if not fn.endswith(".py"):
            continue
        p = os.path.join(root, fn)
        b = open(p, encoding="utf-8", errors="replace").read()
        for key in ("H3_CANVAS_MULTIPLE", "multiple of 32", "% 32", "target_frames", "chunks * chunk_seconds * fps",
                    "H3ContinuumSamplerV39", "H3ContinuumManualCanvasV39"):
            if key in b:
                hits.append((p.replace(CONT, "<CONT>"), key))
seen = {}
for p, k in hits:
    seen.setdefault(p, []).append(k)
for p, ks in sorted(seen.items()):
    print("  %-46s %s" % (p, sorted(set(ks))))

for rel, pats in (("v3/resolution.py", [r"H3_CANVAS_MULTIPLE\s*=\s*\S+", r"canvas.*multiple.*", r"raise .*multiple"]),
                  ("v3/hardening.py", [r"target_frames[^\n]{0,120}", r"chunks[^\n]{0,110}"]),
                  ):
    p = os.path.join(CONT, rel)
    if not os.path.isfile(p):
        print("  MISSING", rel)
        continue
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    print("  %s: %d lines" % (rel, len(lines)))
    for i, l in enumerate(lines, 1):
        if any(re.search(pat, l) for pat in pats):
            print("     %4d: %s" % (i, l.strip()[:130]))

print("\n== Continuum V39 sampler inputs (claim: NO negative / CFG key) ==")
for root, dirs, files in os.walk(CONT):
    if ".git" in root:
        continue
    for fn in files:
        if not fn.endswith(".py"):
            continue
        b = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
        if "SamplerV39" in b:
            for i, l in enumerate(b.splitlines(), 1):
                if re.search(r"(?i)(io\.\w+\.Input\(\"|class H3Continuum\w+|NODE_CLASS|negative|cfg|guidance)", l):
                    print("  %s:%d %s" % (fn, i, l.strip()[:130]))

print("\n== ModelAttentionBackend / BlockSparseAttention schema (AGENTS.md: keys dropped) ==")
p = os.path.join(COMFY, "comfy_extras", "nodes_sparse_attention.py")
src = open(p, encoding="utf-8", errors="replace").read()
for key in ("sparse_blocks", "sparse_size", "max_dims", "keep_percent", "percent_dense",
            "COMFY_DYNAMICCOMBO_V3", "DynamicCombo", "class ModelAttentionBackend", "class BlockSparseAttention",
            "vsa", "sla", "sol", "supported", "not supported", "gate"):
    n = src.count(key)
    print("  %-28s %d" % (key, n))
m = re.search(r"class BlockSparseAttention[\s\S]{0,2600}?\n\nclass ", src)
if m:
    for line in m.group(0).splitlines():
        if re.search(r"(?i)Input\(|tooltip=|options=|supported", line):
            print("   BSA|", line.strip()[:150])

print("\n== canvas arithmetic claims ==")
for w, h in ((832, 468), (1024, 576), (1344, 768), (768, 1344), (1280, 720)):
    print("  %4dx%-4d mp=%.3f  w%%32=%d h%%32=%d" % (w, h, w * h / 1e6, w % 32, h % 32))
for f, fps in ((243, 24), (124, 24), (141, 24), (481, 24), (121, 32), (193, 32), (289, 32)):
    print("  frames %-4d @%-2d fps = %.6f s | (f-5)%%17=%d" % (f, fps, round(f / fps, 6), (f - 5) % 17))
print("  2*22+119 =", 2 * 22 + 119, "| 124+119 =", 124 + 119, "| 2*22+397 =", 2 * 22 + 397)
print("  126 frames at 32 fps =", 126 / 32, "s | 96/32 =", 96 / 32, "s | 288/32 =", 288 / 32, "s")

print("\n== R3b graph keys (settings_audit / body-quality / face-research claims) ==")
p = os.path.join(COMM, "runs", "ali147_pool_hc_r3b_s51130003", "request.api.json")
g = json.load(open(p, encoding="utf-8"))
print("  nodes:", len(g))
want = ("c0", "c1", "ksel", "s0_sched", "s1_sched", "m_shift", "m_vsa", "m_attn", "s0_samp", "s1_samp")
for k in want:
    v = g.get(k)
    if not v:
        print("   %-10s ABSENT" % k)
        continue
    w = v.get("_meta", {}).get("widgets_values")
    print("   %-10s %-30s %s" % (k, v["class_type"], str(w)[:100]))
flat = json.dumps(g).lower()
for probe in ("facerefine", "facedetailer", "upscale", "prompt writer", "promptwriter", "llm",
              "res_multistep", "euler", "keep_percent", "audio_vae", "nag", "cfg"):
    print("   contains '%s': %s" % (probe, probe in flat))
print("  classes:", json.dumps(sorted({v["class_type"] for v in g.values()})))
print("\nPROBE2 DONE")
