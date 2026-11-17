#!/usr/bin/env python3
r"""Self-setup 0.2: LOCAL fact probe for the claim inventory.

Read-only. Prints facts straight out of the installed ComfyUI, the node packs,
the venvs and the repo, so every local claim in the research notes is checked
against the box, not against memory. No GPU, no ComfyUI/llama-swap request.
"""
import glob
import json
import os
import re
import subprocess
import sys

COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
COMM = r"C:/AI/community"
RC = r"C:/Users/derek/5slock/ralph-community"

print("== ComfyUI version (the three notes disagree: 0.38.0 / 0.42.1 / 0.19.2) ==")
for cand in ("pyproject.toml", "comfyui_version.py", "ComfyUI.version"):
    p = os.path.join(COMFY, cand)
    if os.path.exists(p):
        body = open(p, encoding="utf-8", errors="replace").read()
        for line in body.splitlines():
            if re.search(r"(?i)version", line):
                print("  %s: %s" % (cand, line.strip()[:120]))
gitdir = os.path.join(COMFY, ".git")
print("  .git present:", os.path.isdir(gitdir), "file:", os.path.isfile(gitdir))
if os.path.isfile(gitdir):
    print("  .git file:", open(gitdir, encoding="utf-8", errors="replace").read().strip()[:120])
if os.path.isdir(gitdir):
    r = subprocess.run(["git", "-C", COMFY, "log", "-1", "--format=%h %ad %s", "--date=short"],
                       capture_output=True, text=True)
    print("  git HEAD:", (r.stdout or r.stderr).strip()[:200])

print("\n== nodes_minimax_h3.py facts ==")
p = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")
src = open(p, encoding="utf-8", errors="replace").read()
for pat in (r"REF_IMAGE_SHORT_EDGE\s*=\s*\S+", r'"ref_image_size":\s*\[[^\]]*\]',
            r'"frame_idx":\s*\[[^\]]*\]', r"max_size\s*=\s*\d+", r'"min":\s*\d+,\s*"max":\s*\d+',
            r"has_reference", r'"MiniMaxH3ImageToVideo"', r'"MiniMaxH3ReferenceToVideo"',
            r'"MiniMaxH3AddGuide"', r'"MiniMaxH3LatentTailGuide"'):
    hits = re.findall(pat, src)
    print("  %-46s -> %d hit(s) %s" % (pat[:46], len(hits), (hits[:4] if len(hits) < 5 else hits[:4])))
# per-class required inputs: does ImageToVideo really have NO ref slots?
for cls in ("MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo", "MiniMaxH3AddGuide"):
    i = src.find('"%s"' % cls)
    j = src.find("def ", i)
    blk = src[max(i - 400, 0):i + 3500]
    k = blk.find("INPUT_TYPES")
    blk = blk[k:k + 1600]
    print("  %s: ref_images=%s ref_image_size=%s frame_idx=%s length=%s" % (
        cls, "ref_images" in blk, "ref_image_size" in blk, "frame_idx" in blk, "length" in blk))

print("\n== MiniMax H3 sigma shift / VSA / sparse node keys (AGENTS.md: 0.19.2 dropped keys) ==")
for root, dirs, files in os.walk(os.path.join(COMFY, "comfy_extras")):
    for fn in files:
        if not fn.endswith(".py"):
            continue
        b = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
        for key in ("BlockSparseAttention", "sparse_blocks", "sparse_size", "max_dims",
                    "MiniMaxH3SigmaShift", "keep_percent", "DynamicCombo", "DynamicComboV3"):
            if key in b:
                print("  %s: %s" % (fn, key))

print("\n== continuation pack (ttulttul) README ==")
for pack in ("comfyui-minimax-h3-continuation", "ComfyUI_MiniMax_H3_Extender",
             "ComfyUI-H3-Continuum", "MiniMax-H3-Prompt-Rewriter-ComfyUI", "10S-Comfy-nodes"):
    d = os.path.join(COMFY, "custom_nodes", pack)
    print("  %s installed: %s" % (pack, os.path.isdir(d)))
    if os.path.isdir(d):
        for f in ("README.md", "readme.md"):
            rp = os.path.join(d, f)
            if os.path.isfile(rp):
                txt = open(rp, encoding="utf-8", errors="replace").read()
                print("     README %d bytes; overlap hits=%s extension hits=%s subject_definitions=%s" % (
                    len(txt), re.findall(r"overlap_frames[^\n]{0,80}", txt)[:2],
                    re.findall(r"extension_frames[^\n]{0,80}", txt)[:2], "subject_definitions" in txt))
                break

print("\n== venv / tool facts ==")
for py in (r"C:/AI/director/.venv/Scripts/python.exe", r"C:/AI/qa_gate_venv/Scripts/python.exe",
           os.path.join(COMFY, ".venv", "Scripts", "python.exe")):
    if not os.path.exists(py):
        print("  MISSING interpreter:", py)
        continue
    code = (
        "import importlib.util as u, sys\n"
        "try:\n    import torch\nexcept Exception:\n    torch = None\n"
        "cv = __import__('cv2') if u.find_spec('cv2') else None\n"
        "print('py', sys.version.split()[0], 'torch', getattr(torch, '__version__', '-'),\n"
        "      'cv2', getattr(cv, '__version__', '-'),\n"
        "      'CascadeClassifier', bool(cv and getattr(cv, 'CascadeClassifier', None)),\n"
        "      'mods', [n for n in ('mediapipe','scipy','insightface','ultralytics','onnxruntime') if u.find_spec(n)])\n"
    )
    r = subprocess.run([py, "-c", code], capture_output=True, text=True, timeout=240)
    label = py.replace(COMFY, "<COMFY>").replace("C:/AI/", "").replace("/Scripts/python.exe", "")
    print("  %s -> %s" % (label, (r.stdout or r.stderr).strip().replace("\n", " | ")[:240]))

print("\n== ffmpeg siti filter (video-review note claim) ==")
ff = None
for c in ("ffmpeg", r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"):
    r = subprocess.run([c, "-hide_banner", "-filters"], capture_output=True, text=True)
    if r.returncode == 0:
        ff = c
        names = re.findall(r"\b(siti|signalstats|blurdetect|scdet|freezedetect|tmix|psnr|ssim)\b", r.stdout)
        print("  ffmpeg %s -> filters seen: %s" % (c, sorted(set(names))))
        break
if ff is None:
    print("  ffmpeg not runnable")

print("\n== face metric assets (hc_face_research claims) ==")
for p in (r"C:/AI/models/qa_gate/face_yolov8m.pt", r"C:/AI/models/qa_gate/hand_yolov8s.pt",
          os.path.join(COMFY, "models", "insightface", "models", "antelopev2", "scrfd_10g_bnkps.onnx"),
          os.path.join(COMFY, "models", "insightface", "models", "antelopev2", "glintr100.onnx"),
          os.path.join(COMFY, "models", "insightface", "models", "buffalo_l", "det_10g.onnx"),
          os.path.join(COMFY, "models", "insightface", "models", "buffalo_l", "w600k_r50.onnx"),
          os.path.join(COMFY, "models", "latent_upscale_models"),
          r"C:/AI/community/scripts/burncheck.py", r"C:/AI/community/scripts/faceid.py",
          r"C:/AI/community/scripts/prompt_writer.py", r"C:/AI/community/p7/notes/p7_r3_close.md",
          r"C:/AI/community/p7/KNOBS.md", r"C:/AI/community/skills",
          r"C:/Users/derek/.pi/forge-policy/pi-permissions.jsonc",
          r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json",
          r"C:/AI/community/p7/p7_budget.json",
          r"C:/Users/derek/5slock/approved_characters",
          r"C:/AI/community/notes/ali147-pv26-card-probe-20261023.txt",
          r"C:/AI/community/notes/ali147_pv26-settings-20261023.txt",
          r"C:/AI/community/guides/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md",
          r"C:/AI/community/guides/VIDEO_PROMPT_WRITING_GUIDE_base_en.md"):
    if os.path.isdir(p):
        print("  DIR  %s (%d entries)" % (p, len(os.listdir(p))))
    else:
        print("  %s %s %s" % ("FILE " if os.path.isfile(p) else "MISS ",
                              os.path.getsize(p) if os.path.isfile(p) else 0, p))

print("\n== beta8/beta6 checkpoint files (model-name claims) ==")
for sub in ("checkpoints", "diffusion_models", "unet", "latent_upscale_models", "text_encoders", "vae", "loras"):
    for pat in ("10Eros*", "*H3*turbo*", "*H3*TURBO*", "*upscal*", "*Anti-Burn*", "*anti_burn*"):
        for f in glob.glob(os.path.join(COMFY, "models", sub, pat)):
            if os.path.isfile(f):
                print("  %12d %s" % (os.path.getsize(f), f.replace(COMFY, "<COMFY>")))

print("\n== comm.py / run_graph_job.py line-number claims (settings_audit) ==")
p = os.path.join(COMM, "scripts", "comm.py")
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
print("  comm.py lines:", len(lines))
for n in (165, 264):
    if n <= len(lines):
        print("  line %d: %s" % (n, lines[n - 1][:120]))
for n, pat in ((165, "ref"), (264, "guidance")):
    idx = [i + 1 for i, l in enumerate(lines) if pat in l]
    print("  lines containing '%s': %s%s" % (pat, idx[:6], " (line %d matches pattern)" % n if n in idx else " (CLAIM LINE DOES NOT MATCH)"))
p = os.path.join(COMM, "scripts", "prompt_writer.py")
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
print("  prompt_writer.py lines:", len(lines), "| line 80:", lines[79][:100] if len(lines) >= 80 else "-")

print("\n== graph facts: the current H3 graph settings_audit audited ==")
p = os.path.join(COMM, "runs", "ali147_pool_hc_r3b_s51130003", "request.api.json")
if os.path.isfile(p):
    g = json.load(open(p, encoding="utf-8"))
    print("  nodes:", len(g))
    cls = {}
    for k, v in g.items():
        cls.setdefault(v["class_type"], []).append(k)
    for k, v in sorted(g.items()):
        if v["class_type"].startswith("MiniMaxH3") or v["class_type"] in ("KSamplerSelect", "RandomNoise"):
            widgets = v.get("_meta", {}).get("widgets_values")
            print("  %-12s %-28s %s" % (k, v["class_type"], str(widgets)[:60] if widgets else ""))
    print("  classes:", json.dumps({k: len(v) for k, v in cls.items()}, sort_keys=True))
    print("  any cfg/nag/samplertypescheduler key:",
          any("cfg" in json.dumps(v).lower() for v in g.values()),
          any("nag" in json.dumps(v).lower() for v in g.values()),
          any("SamplerCustom" in v["class_type"] for v in g.values()))
else:
    print("  MISSING graph:", p)
print("\nPROBE DONE")
