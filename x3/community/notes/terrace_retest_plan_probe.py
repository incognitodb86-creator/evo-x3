# terrace_retest_plan_probe.py - read-only check of Max's terrace-retest draft against files on disk.
# CPU only: no graph building, no submit, no GPU, no lock, no render.
# Usage: python C:\AI\community\notes\terrace_retest_plan_probe.py  > C:\AI\community\notes\terrace_retest_plan_probe.txt
import hashlib
import json
import os
import re
import struct
import sys

RUNS = r"C:\AI\community\runs"
B2 = os.path.join(RUNS, "terrace_dom_q5guide_20261028_s51083007", "request.api.json")
B2_DEFAULT = r"C:\AI\community\p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json"
T4DIR = os.path.join(RUNS, "terrace_dom_q5stockv2_20261028_s51083011")
STOCK_UI = os.path.join(T4DIR, "stock_simple_v2.json")
STOCK_API = os.path.join(T4DIR, "_ui2api", "api_stock.json")
T4_API = os.path.join(T4DIR, "request.api.json")
IMG = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\TERRACE2_768x1344.png"
RT_MODELS = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def brief(v, n=110):
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else f"<{len(s)} chars> {s[:n]}..."


def walk_api(path, label, keys_of_interest=None):
    g = jload(path)
    print(f"\n{'='*100}\n### {label}: {path}\n  nodes={len(g)} sha256={sha(path)} bytes={os.path.getsize(path)}")
    for nid in sorted(g, key=lambda x: (0, int(x), "") if str(x).isdigit() else (1, 0, str(x))):
        n = g[nid]
        t = n.get("class_type")
        w = n.get("inputs", {})
        widgets = {k: v for k, v in w.items() if not (isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, str)) and isinstance(v[1], int))}
        links = {k: v for k, v in w.items() if k not in widgets}
        print(f"  [{nid}] {t}")
        for k, v in widgets.items():
            print(f"       .{k} = {brief(v)}")
        for k, v in links.items():
            print(f"       {k} <- [{v[0]}]:{v[1]}")
    return g


def find(g, *types):
    return [(nid, n) for nid, n in g.items() if n.get("class_type") in types]


def stock_frame_count(dur_seconds):
    """The stock graph's own formula, quoted from the two-pass subgraph ComfyMathExpression."""
    a = max(5, round(dur_seconds * 24))
    return a + (5 - (a % 17)) % 17


def main():
    out = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "terrace_retest_plan_probe.txt"), "w", encoding="utf-8")
    global print
    _print = print

    def print(*a, **kw):  # noqa: F811 - tee to a UTF-8 file, console codepage is not UTF-8
        _print(*a, **kw, file=out)
    print("PROBE: terrace retest plan vs disk -", __import__("datetime").datetime.now().isoformat(timespec="seconds"))

    # ---------- 1. hashes / existence ----------
    print("\n### 1. Files the draft names")
    for label, p in [("B2 graph of record", B2), ("B2 default copy", B2_DEFAULT),
                     ("stock simple_v2 (UI, on-disk copy)", STOCK_UI),
                     ("stock as shipped, flat API", STOCK_API),
                     ("T4 submitted graph", T4_API), ("start image", IMG)]:
        if os.path.exists(p):
            print(f"  {label}: EXISTS bytes={os.path.getsize(p)} sha256={sha(p)}")
        else:
            print(f"  {label}: MISSING {p}")

    # start image real size
    with open(IMG, "rb") as f:
        head = f.read(33)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    w, h = struct.unpack(">II", head[16:24])
    print(f"  start image real pixels: {w}x{h}  ratio={w/h:.6f} (9:16={9/16:.6f})")

    # ---------- 2. stock UI structure: frame formula, duration, resolution selector, subgraph ids ----------
    print("\n### 2. Stock UI graph structure (stock_simple_v2.json)")
    ui = jload(STOCK_UI)
    print(f"  top-level nodes={len(ui['nodes'])} links={len(ui['links'])} definitions={len(ui.get('definitions', {}))}")
    for n in ui["nodes"]:
        t = n.get("type", "")
        if t in ("PrimitiveFloat", "Seed (rgthree)", "LoadImage", "PrimitiveStringMultiline",
                 "ResolutionSelector", "MinimaxH3LatentUpscaler3D", "RTXVideoSuperResolution",
                 "LokkenVideoPostProcessing", "SaveVideo", "ComfyMathExpression",
                 "MiniMaxH3ReferenceToVideo", "MiniMaxH3AddGuide", "UNETLoader", "CLIPLoader",
                 "KSamplerSelect", "BasicScheduler", "MiniMaxH3SigmaShift", "BlockSparseAttention",
                 "LoraLoaderModelOnly", "VAELoader", "PrimitiveString", "PrimitiveBoolean",
                 "DynamicPrompts", "MarkdownNote"):
            print(f"  ui node {n['id']:>4} type={t:<32} widgets={brief(n.get('widgets_values'), 300)}")
    subgraphs = [n for n in ui["nodes"] if n.get("type") in (ui.get("definitions", {}) or {}).get("subgraphs", {})
                 or re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", str(n.get("type", "")))]
    print(f"  subgraph instance nodes: {[(n['id'], n['type']) for n in subgraphs]}")
    defs = (ui.get("definitions", {}) or {}).get("subgraphs", [])
    for d in defs:
        print(f"  --- subgraph definition id={d.get('id')} name={d.get('name')} nodes={len(d.get('nodes', []))} version={d.get('version')}")
        for n in d.get("nodes", []):
            t = n.get("type", "")
            print(f"      ui node {n['id']:>4} type={t:<34} widgets={brief(n.get('widgets_values'), 420)}")
    # every ComfyMathExpression anywhere (frame-count math)
    print("  --- every ComfyMathExpression / maths node in the file (frame-count chain) ---")
    def scan(nodes, where):
        for n in nodes:
            if "math" in str(n.get("type", "")).lower() or "expression" in str(n.get("type", "")).lower():
                print(f"      {where} ui node {n['id']}: {brief(n.get('widgets_values'), 400)}")
    scan(ui["nodes"], "top")
    for d in defs:
        scan(d.get("nodes", []), f"sub[{d.get('name')}]")
    for dur in (5.0, 10.0, 15.0, 12.5):
        print(f"  formula at duration {dur} s -> frames {stock_frame_count(dur)}")
    reach = [f for f in range(1, 400) if f == stock_frame_count(f / 24.0)]
    print(f"  reachable frame counts <= 400 via that formula: {reach}")
    print(f"  121 frames reachable? {121 in reach}   124? {124 in reach}   243? {243 in reach}")

    # aspect_ratio options: they live in the installed node, not the file
    print("  --- ResolutionSelector widget option lists (searched in installed node source) ---")
    hits = []
    for root, dirs, files in os.walk(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes"):
        for fn in files:
            if fn.endswith(".py"):
                p = os.path.join(root, fn)
                try:
                    txt = open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                if "ResolutionSelector" in txt or "aspect_ratio" in txt and "megapixels" in txt:
                    hits.append(p)
    for p in sorted(set(hits))[:6]:
        print(f"      node source candidate: {p} ({os.path.getsize(p)} B)")

    # ---------- 3. B2 graph ----------
    b2 = walk_api(B2, "B2 graph of record")

    # ---------- 4. stock as shipped (flat API from Max's converter) ----------
    st = walk_api(STOCK_API, "stock simple_v2 as shipped, flat API")

    # ---------- 5. the arms, checked against real widget paths ----------
    print(f"\n{'='*100}\n### 5. Draft claims checked against B2's real widgets")
    c0 = dict(find(b2, "MiniMaxH3ReferenceToVideo"))
    c0id = list(c0)[0]
    c0w = c0[c0id]["inputs"]
    prompt = c0w.get("prompt", "")
    print(f"  B2 c0[{c0id}] length={c0w.get('length')} width={c0w.get('width')} height={c0w.get('height')} "
          f"fps={c0w.get('fps')} ref_image_size={c0w.get('ref_image_size')} prompt_chars={len(prompt)}")
    print(f"  B2 prompt sha256={hashlib.sha256(prompt.encode('utf-8')).hexdigest()}")
    for probe in ("Picture 1", "picture 1", "correct scene identity", "#74", "scene identity"):
        print(f"  B2 prompt contains {probe!r}: {probe.lower() in prompt.lower()}")
    print("  B2 reference-image sockets:", {k: v for k, v in c0w.items() if "ref_image" in k})
    for t in ("UNETLoader", "CLIPLoader", "VAELoader", "KSamplerSelect", "BasicScheduler", "KSampler",
              "MiniMaxH3SigmaShift", "BlockSparseAttention", "MinimaxH3LatentUpscaler3D",
              "MiniMaxH3AddGuide", "LoadImage", "SaveVideo", "CreateVideo", "VAEDecode",
              "VAEDecodeAudio", "RTXVideoSuperResolution", "LokkenVideoPostProcessing", "CheckpointLoaderSimple"):
        for nid, n in find(b2, t):
            w = n["inputs"]
            keep = {k: v for k, v in w.items() if not (isinstance(v, list) and len(v) == 2 and isinstance(v[1], int))}
            print(f"    B2 [{nid}] {t}: {brief(keep, 400)}")
    # seeded noise
    for nid, n in b2.items():
        for k, v in n.get("inputs", {}).items():
            if "seed" in k.lower() and not isinstance(v, list):
                print(f"    B2 [{nid}] {n['class_type']}.<b>{k}</b> = {v}")

    print(f"\n### 6. Stock as shipped: the same widget set")
    for t in ("UNETLoader", "CLIPLoader", "VAELoader", "KSamplerSelect", "BasicScheduler", "KSampler",
              "MiniMaxH3SigmaShift", "BlockSparseAttention", "MinimaxH3LatentUpscaler3D", "MinimaxH3AddGuide",
              "LoadImage", "SaveVideo", "CreateVideo", "RTXVideoSuperResolution", "LokkenVideoPostProcessing",
              "ResolutionSelector", "MiniMaxH3ReferenceToVideo", "LoraLoaderModelOnly", "PrimitiveFloat",
              "Seed (rgthree)", "PrimitiveStringMultiline"):
        for nid, n in find(st, t):
            w = n["inputs"]
            keep = {k: v for k, v in w.items() if not (isinstance(v, list) and len(v) == 2 and isinstance(v[1], int))}
            print(f"    STOCK [{nid}] {t}: {brief(keep, 500)}")
    for nid, n in find(st, "MiniMaxH3ReferenceToVideo"):
        p = n["inputs"].get("prompt", "")
        print(f"    STOCK c0[{nid}] prompt = {brief(p, 200)} sha256={hashlib.sha256(str(p).encode('utf-8')).hexdigest()[:16]}")

    # ---------- 7. model files the arms need ----------
    print(f"\n{'='*100}\n### 7. Model files on disk (S3 upscaler swap, beta5 claim)")
    want = re.compile(r"(minimax_h3_latent_upscaler|minimax.*upscaler|latent_upscaler)", re.I)
    for root, dirs, files in os.walk(RT_MODELS):
        for fn in files:
            if fn.endswith((".safetensors", ".ckpt", ".pt", ".bin", ".gguf")):
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, RT_MODELS)
                if want.search(fn) or "beta" in fn.lower() or "minimax_h3" in fn.lower() and "vae" in fn.lower():
                    print(f"      {rel}  {os.path.getsize(p):,} B")

    # ---------- 8. judge + lock tooling ----------
    print(f"\n### 8. Instruments named in the draft")
    for label, p in [("judge dir", r"C:\AI\community\judge"), ("scripts dir", r"C:\AI\community\scripts"),
                     ("locks dir", r"C:\AI\locks"), ("60_reviews", r"C:\AI\community\60_reviews"),
                     ("reviews dir", r"C:\AI\community\review")]:
        if os.path.isdir(p):
            ents = sorted(os.listdir(p))
            print(f"  {label}: {len(ents)} entries -> {brief(ents, 900)}")
        else:
            print(f"  {label}: NOT A DIR ({p})")
    gpu_scripts = [os.path.join(r"C:\AI\community\scripts", f) for f in os.listdir(r"C:\AI\community\scripts")
                   if "gpu" in f.lower() or "judge" in f.lower() or "qwen" in f.lower() or "zoom" in f.lower()]
    for p in gpu_scripts:
        print(f"    script: {os.path.basename(p)} ({os.path.getsize(p)} B)")
        for line in open(p, encoding="utf-8", errors="replace").read().splitlines():
            if "gpu-render.lock" in line or "Z " in line[:6] or "zoom" in line.lower()[:200]:
                print(f"       | {line.strip()[:160]}")

    # ---------- 9. the prompt files the S8 arm needs ----------
    print(f"\n### 9. Prompt provenance files")
    for p in [os.path.join(RUNS, d, f) for d, f in [
            ("terrace_dom_q5guide_20261028_s51083007", "prompt_seg0.txt"),
            ("terrace_dom_q5biglock_20261028_s51083009", "prompt_seg0.txt"),
            ("terrace_dom_q5biglock_20261028_s51083009", "prompt_lock_block.txt"),
            ("terrace_dom_q5biglock_20261028_s51083009", "prompt_full.txt")]]:
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read()
            print(f"  {os.path.relpath(p, RUNS)}: {os.path.getsize(p)} B, {len(txt)} chars, "
                  f"sha256={hashlib.sha256(txt.encode('utf-8')).hexdigest()[:16]} "
                  f"contains 'Picture 1': {'Picture 1' in txt}")
        else:
            print(f"  {os.path.relpath(p, RUNS)}: MISSING")
    lock_note = r"C:\AI\community\notes\2026-10-28-consistency-lock-block.txt"
    if os.path.exists(lock_note):
        txt = open(lock_note, encoding="utf-8").read()
        print(f"  notes/2026-10-28-consistency-lock-block.txt: {len(txt)} chars sha={hashlib.sha256(txt.encode()).hexdigest()[:16]} "
              f"contains 'Picture 1': {'Picture 1' in txt}")
    print("\nDONE (read-only, no submit, no GPU)")
    out.close()


if __name__ == "__main__":
    main()
