"""item 4 close-out (2026-10-29): verify PROMPT.md 1e/1f against the graph it now names.
Reads the live PROMPT.md, extracts the default graph path and the --frames number from it, and checks
them against the file on disk. CPU only, writes nothing."""
import hashlib, json, re
from pathlib import Path

PROMPT = Path(r"C:/Users/derek/5slock/ralph-community/PROMPT.md")
BAK = Path(r"C:/Users/derek/5slock/ralph-community/PROMPT.md.bak-20261029-item4-apply")
B2 = Path(r"C:/AI/community/runs/terrace_dom_q5guide_20261028_s51083007/request.api.json")

txt = PROMPT.read_text(encoding="utf-8")
lines = txt.splitlines()
i_e = next(i for i, l in enumerate(lines) if l.strip().startswith("e. Build graph:"))
i_f = next(i for i, l in enumerate(lines) if l.strip().startswith("f. Render:"))
print("1e line %d, %d chars\n%s\n" % (i_e + 1, len(lines[i_e]), lines[i_e]))
print("1f line %d, %d chars\n%s\n" % (i_f + 1, len(lines[i_f]), lines[i_f]))

# what the two lines claim
path = re.search(r"copy (C:\\AI\\community\\p7\\graphs\\[A-Za-z0-9_.]+)", lines[i_e]).group(1)
frames = int(re.search(r"--frames (\d+)", lines[i_f]).group(1))
sha_claim = re.search(r"sha256 ([0-9a-f]{64})", lines[i_e]).group(1)
bytes_claim = int(re.search(r"(\d+) B, (\d+) nodes", lines[i_e]).group(1))
nodes_claim = int(re.search(r"(\d+) B, (\d+) nodes", lines[i_e]).group(2))
target = Path(path)
print("claims: target=%s frames=%d sha=%s bytes=%d nodes=%d" % (target, frames, sha_claim[:16], bytes_claim, nodes_claim))

raw = target.read_bytes()
g = json.loads(raw.decode("utf-8"))
print("target exists: %s  bytes=%d  sha256=%s" % (target.exists(), len(raw), hashlib.sha256(raw).hexdigest()))
print("bytes match claim:", len(raw) == bytes_claim)
print("sha match claim:", hashlib.sha256(raw).hexdigest() == sha_claim)
print("node count match claim:", len(g) == nodes_claim)
print("c0.length =", g["c0"]["inputs"]["length"], "-> frames arg equals c0.length:", g["c0"]["inputs"]["length"] == frames)
b2raw = B2.read_bytes()
print("byte-identical to B2 request.api.json:", raw == b2raw, "(B2 %d B, sha %s)" % (len(b2raw), hashlib.sha256(b2raw).hexdigest()[:16]))

# the four per-run keys 1e says may change, and the settings it says must not
per_run = {"LoadImage path": g["img"]["inputs"]["image"], "c0.prompt": len(g["c0"]["inputs"]["prompt"]),
           "noise_seed": [n["inputs"]["noise_seed"] for n in g.values() if n["class_type"] == "RandomNoise"],
           "filename_prefix": g["save"]["inputs"]["filename_prefix"]}
print("per-run keys present:", per_run)
frozen = {"unet": g["unet"]["inputs"]["unet_name"], "steps": g["s0_sched"]["inputs"]["steps"],
          "sched": g["s0_sched"]["inputs"]["scheduler"], "pass2": [g["p2sched"]["inputs"][k] for k in ("scheduler", "steps", "denoise")],
          "shift": [g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"]],
          "vsa_keep": g["m_vsa"]["inputs"]["selection.keep_percent"], "ref_image_size": g["c0"]["inputs"]["ref_image_size"],
          "addguides": sorted(k for k, n in g.items() if n["class_type"] == "MiniMaxH3AddGuide"),
          "upscaler": [g["lsu3"]["inputs"]["mode"], g["lsu3"]["inputs"]["mode.scale"]],
          "sampler": g["ksel"]["inputs"]["sampler_name"], "fps": g["mkvid"]["inputs"]["fps"]}
print("frozen settings in the default:", frozen)

# the old wording must be gone from the live file
for pat in ("stock_base_tenstrip10", "--frames 124"):
    print("old string %r present in PROMPT.md: %s" % (pat, pat in txt))

# the diff against the backup, counted
import difflib
d = [l for l in difflib.unified_diff(BAK.read_text(encoding="utf-8").splitlines(), lines, lineterm="")]
changed = [l for l in d if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
print("diff-vs-backup lines changed: %d" % len(changed))
for l in changed:
    print("   %s%s" % (l[0], l[1:][:110]))
