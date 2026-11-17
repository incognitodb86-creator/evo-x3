# terrace_retest_plan_probe2.py - read-only checks for the terrace retest plan (part 2).
# CPU only: no submit, no GPU, no lock, no network. Appends to the same evidence file.
import glob
import hashlib
import json
import os
import re

RUNS = r"C:\AI\community\runs"
OBJ = os.path.join(RUNS, "ckattn_20261025_object_info_full.json")   # Oct 25 snapshot of live /object_info
GPUW = r"C:\AI\community\scripts\gpu_window.ps1"
LOCKSCRIPTS = [r"C:\AI\community\scripts\gpu_window.ps1", r"C:\AI\community\scripts\comfy_ctl.py",
               r"C:\AI\community\scripts\run_graph_job.py"]
OUT = os.path.join(r"C:\AI\community\notes", "terrace_retest_plan_probe.txt")

out = open(OUT, "a", encoding="utf-8")


def print(*a, **kw):  # noqa: F811
  __import__("builtins").print(*a, **kw, file=out)


print("\n" + "=" * 100)
print("### PROBE 2 (2026-10-29 ~20:40 CT)")

# 1. sampler / scheduler / ref_image_size option lists, from the saved live object_info
oi = json.load(open(OBJ, encoding="utf-8"))
print(f"\n  object_info snapshot: {OBJ} ({os.path.getsize(OBJ):,} B), "
      f"{len(oi)} node types - this is the Oct 25 capture of the live server")
for node, widget in [("KSamplerSelect", "sampler_name"), ("BasicScheduler", "scheduler"),
                     ("BasicScheduler", "denoise"), ("MiniMaxH3ReferenceToVideo", "ref_image_size"),
                     ("ResolutionSelector", "aspect_ratio"), ("ResolutionSelector", "megapixels"),
                     ("RTXVideoSuperResolution", "quality"), ("MinimaxH3LatentUpscaler3D", "model_name")]:
    spec = oi.get(node)
    if not spec:
        print(f"  {node}.{widget}: node NOT in snapshot")
        continue
    inp = spec.get("input", {}).get("required", {})
    opt = inp.get(widget) or spec.get("input", {}).get("optional", {}).get(widget)
    if opt is None:
        print(f"  {node}.{widget}: widget not in snapshot")
        continue
    vals = opt[0] if isinstance(opt, list) and opt and isinstance(opt[0], list) else opt
    print(f"  {node}.{widget}: {json.dumps(vals, ensure_ascii=False)[:1400]}")
for node in ("MiniMaxH3AddGuide", "LokkenVideoPostProcessing", "MiniMaxH3ReferenceToVideo",
             "ResolutionSelector", "MinimaxH3LatentUpscaler3D", "LoraLoaderModelOnly"):
    if node in oi:
        req = list(oi[node].get("input", {}).get("required", {}))
        optl = list(oi[node].get("input", {}).get("optional", {}))
        print(f"  node {node}: required={req} optional={optl}")
    else:
        print(f"  node {node}: NOT in the Oct 25 snapshot")

# 2. resolution math: the exact numbers for the arms
print("\n  --- ResolutionSelector + LatentUpscaler3D geometry, computed from the installed node source ---")


def selector(aspect, mp, multiple=32):
    import math
    r = {"1:1 (Square)": (1, 1), "2:3 (Portrait Photo)": (2, 3), "3:2 (Photo)": (3, 2),
         "3:4 (Portrait Standard)": (3, 4), "4:3 (Standard)": (4, 3),
         "9:16 (Portrait Widescreen)": (9, 16), "16:9 (Widescreen)": (16, 9),
         "21:9 (Ultrawide)": (21, 9)}[aspect]
    s = math.sqrt(mp * 1024 * 1024 / (r[0] * r[1]))
    return (round(r[0] * s / multiple) * multiple, round(r[1] * s / multiple) * multiple)


def upscaler_megapixels(w_in_px, h_in_px, mp, align=32, ds=8):
    """w_in_px/h_in_px = the pass-1 canvas; latent aspect = same aspect (latent = px/ds)."""
    import math
    w_in, h_in = w_in_px / ds, h_in_px / ds
    target = mp * 1024 * 1024
    ar = w_in / h_in
    h_t = (target / ar) ** 0.5
    w_t = h_t * ar
    eff = (w_t / (w_in * ds) + h_t / (h_in * ds)) / 2.0
    wa = round(w_t / align) * align
    ha = round(h_t / align) * align
    wf = round(wa / ds) * ds
    hf = round(ha / ds) * ds
    return (int(wf), int(hf)), round(eff, 4)


for asp in ("9:16 (Portrait Widescreen)", "3:4 (Portrait Standard)", "2:3 (Portrait Photo)", "4:3 (Standard)"):
    for mp in (0.3, 0.25, 0.2, 0.15):
        w, h = selector(asp, mp)
        print(f"    selector {asp} @ {mp} MP / multiple 32 -> pass-1 {w}x{h} "
              f"({w*h/1048576:.3f} MP-in-node-units, latent {w//8}x{h//8})")
print("    B2 pass 1 = 384x672 (latent 48x84) x2.0 -> 768x1344 exactly")
for pass1 in ((416, 736), (288, 512), (384, 704), (384, 672), (448, 768)):
    for mp in (1.0, 0.98, 0.9):
        (w, h), eff = upscaler_megapixels(pass1[0], pass1[1], mp)
        print(f"    pass1 {pass1[0]}x{pass1[1]} -> upscaler megapixels {mp}: {w}x{h} "
              f"({'= 768x1344' if (w, h) == (768, 1344) else 'NOT 768x1344'}) scale={eff}")

# 3. frame counts the stock chain can produce vs B2's explicit length
print("\n  --- frame counts ---")


def stock_frames(dur):
    a = max(5, round(dur * 24))
    return a + (5 - (a % 17)) % 17


for d in (5.0, 10.0, 15.0):
    print(f"    stock duration widget {d} s -> {stock_frames(d)} frames ({stock_frames(d)/24:.3f} s)")
print("    121 frames: not reachable from the stock duration widget (all outputs are 5 mod 17)")
print("    124 is reachable in BOTH arms: stock duration 5.0 s -> 124; B2 c0.length = 124 (direct widget)")

# 4. seeds: are 51083012 / 51083013 unused anywhere?
print("\n  --- proposed new fixed seeds ---")
for seed in (51083012, 51083013, 51083002):
    dirs = [d for d in glob.glob(os.path.join(RUNS, "*")) if os.path.basename(d).endswith(f"s{seed}")]
    hits = 0
    for d in dirs:
        hits += 1
    graph_hits = 0
    for p in glob.glob(os.path.join(RUNS, "*", "*.api.json")):
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if str(seed) in txt:
            graph_hits += 1
    print(f"    seed {seed}: run dirs {hits}, graphs mentioning it {graph_hits}")

# 5. the GPU lock instrument the draft names
print("\n  --- GPU lock path used by the harness ---")
for p in LOCKSCRIPTS:
    if not os.path.exists(p):
        print(f"    missing: {p}")
        continue
    for i, line in enumerate(open(p, encoding="utf-8", errors="replace").read().splitlines(), 1):
        if "gpu-render.lock" in line or "gpu_lock" in line or "locks" in line.lower():
            print(f"    {os.path.basename(p)}:{i}: {line.strip()[:170]}")

# 6. what the harness needs per run dir
print("\n  --- run_graph_job.py: the frames gate and the guard gate (line numbers) ---")
p = r"C:\AI\community\scripts\run_graph_job.py"
for i, line in enumerate(open(p, encoding="utf-8", errors="replace").read().splitlines(), 1):
    if re.search(r"frames|guard_ok|--frames|static_check|c0\.length|length", line):
        print(f"    run_graph_job.py:{i}: {line.strip()[:170]}")
out.close()
print = __import__("builtins").print
print("PROBE2 appended")
