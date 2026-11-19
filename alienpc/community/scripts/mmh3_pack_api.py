#!/usr/bin/env python3
"""Extract the API surface of the newly cloned LBH-123-AI 3D latent-upscaler pack:
node class names, widgets (with defaults), inputs/outputs, and the model folder it reads.
Source of truth = the pack's own source, not the README.
Usage: mmh3_pack_api.py [pack_dir]
"""
import re
import sys

PACK = sys.argv[1] if len(sys.argv) > 1 else (
    r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\custom_nodes"
    r"\Comfyui_Minimax_h3_latent_Upscaler")
FILES = [PACK + r"\nodes\minimax_h3_latent_upscaler_3d.py",
         PACK + r"\nodes\minimax_h3_latent_upscaler_2d.py",
         PACK + r"\nodes\MMH3_Split_Upscale.py"]
PAT = re.compile(
    r'class (?P<cls>\w+)\b'
    r'|NODE_CLASS_MAPPINGS\s*=\s*\{(?P<map>.*?)\}'
    r'|"required":\s*\{(?P<req>.*?)\n\s*\}'
    r'|"optional":\s*\{(?P<opt>.*?)\n\s*\}'
    r'|RETURN_TYPES\s*=\s*(?P<rt>\(.*?)\n'
    r'|RETURN_NAMES\s*=\s*(?P<rn>\(.*?)\n'
    r'|function\s*=\s*"(?P<fn>\w+)"'
    r'|folder_paths\.[a-z_]+\((?P<fol>[^)]*)\)'
    r'|DEFAULT_(?:CKPT|MODEL)_PATH\s*=\s*(?P<dp>\S[^\n]*)'
    r'|(?P<sc>scale["\']?\s*[:=]\s*\[[^\]]*\])', re.S)

for f in FILES:
    try:
        src = open(f, encoding="utf-8").read()
    except OSError as e:
        print("missing", f, e)
        continue
    print("=" * 72)
    print(f"{f.rsplit(chr(92), 1)[-1]}  ({len(src)} B, {src.count(chr(10))} lines)")
    for m in PAT.finditer(src):
        ln = src[:m.start()].count("\n") + 1
        for kind, val in m.groupdict().items():
            if val:
                print(f"  L{ln:<5} {kind:4} {re.sub(r'[^\\x20-\\x7e]', ' ', val)[:420]}")
