#!/usr/bin/env python3
"""Pre-load safety review of a custom_node pack (Derek's rule: review source BEFORE ComfyUI loads it).

Checks: imports, network calls, subprocess/exec/eval, pickle/torch.load (weights_only?),
file writes outside the pack folder, install-time hooks (setup.py/pyproject/post_install scripts),
declared pip requirements, and which model extensions the node accepts.
Usage: review_pack.py <pack_dir>
"""
import ast
import os
import re
import sys

PACK = sys.argv[1]
RISKS = {
    "net": re.compile(r"\b(requests|urllib|httpx|socket|urlopen|http\.client|websocket)\b|\bhttps?://"),
    "proc": re.compile(r"\b(subprocess|os\.system|popen|exec\(|eval\(|Popen)\b"),
    "pickle": re.compile(r"\bpickle|torch\.load\(|weights_only|np\.load\(|load_state_dict"),
    "fs": re.compile(r"\bopen\(|shutil\.(copy|rmtree|move)|os\.remove|os\.makedirs|\.write\(|tempfile|shutil\.rmtree"),
    "gpu": re.compile(r"\b(torch\.cuda|torch\.compile|torch\.compile|autocast|torch\.no_grad|inference_mode)"),
    "deps": re.compile(r"\bimport\s+(einops|timm|transformers|safetensors|scipy|cv2|numpy|torchvision|onnx|triton|accelerate)"),
}


def scan(path, rel):
    src = open(path, encoding="utf-8", errors="replace").read()
    hits = []
    for kind, rx in RISKS.items():
        for m in rx.finditer(src):
            ln = src[:m.start()].count("\n") + 1
            line = src.splitlines()[ln - 1].strip()[:150]
            hits.append((kind, ln, line))
    imported = set()
    try:
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                imported |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                imported.add(n.module.split(".")[0])
    except SyntaxError as e:
        hits.append(("syntax", 0, str(e)))
    return hits, sorted(imported)


print("PACK", PACK)
py = []
for root, _, files in os.walk(PACK):
    for f in files:
        if f.endswith((".py", ".toml", ".cfg", ".txt", ".json", ".md")):
            py.append(os.path.join(root, f))
top = {os.path.basename(p).lower() for p in py}
print("install hooks:", sorted(top & {"setup.py", "pyproject.toml", "requirements.txt",
                                     "post_install.sh", "install.py", "package.json"}))
for p in ("requirements.txt", "pyproject.toml", "setup.py"):
    f = os.path.join(PACK, p)
    if os.path.exists(f):
        print(f"--- {p}: " + re.sub(r"\s+", " ", open(f, encoding="utf-8").read())[:400])

all_hits, all_imports = [], set()
for f in sorted(py):
    if not f.endswith(".py"):
        continue
    hits, imports = scan(f, os.path.relpath(f, PACK))
    rel = os.path.relpath(f, PACK)
    print(f"=== {rel} ({os.path.getsize(f)} B) imports={imports}")
    for h in hits:
        all_hits.append((rel,) + h)
    all_imports |= set(imports)
print("\n=== RISK LINES (kind/line/code)")
for rel, kind, ln, line in all_hits:
    print(f"  {rel}:{ln} [{kind}] {line}")
print("\nthird-party modules seen:", sorted(all_imports - {
    "os", "sys", "re", "json", "math", "time", "logging", "typing", "enum", "pathlib",
    "hashlib", "argparse", "itertools", "functools", "collections", "contextlib",
    "dataclasses", "abc", "traceback", "traceback", "io", "codecs", "warnings",
    "node", "comfy", "comfyui", "folder_paths", "nodes", "comfy_api", "PIL", "cv2",
    "numpy", "torch", "safetensors", "einops", "scipy", "timm", "transformers"}))
models = [p for p in py if p.endswith(".safetensors")]
print("model files inside pack:", models)
ck = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\latent_upscale_models"
print("checkpoint dir:", ck, os.path.isdir(ck) and [(f, os.path.getsize(os.path.join(ck, f)))
                                                    for f in os.listdir(ck)] or "MISSING")
