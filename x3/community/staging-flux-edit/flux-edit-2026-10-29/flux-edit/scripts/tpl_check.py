"""U11 tpl_check (offline lint of one template version). Returns a list of problems; empty = clean.

Checks: index.json sha256; every ${KEY} declared in params.schema.json and vice versa; class_type in the saved
/object_info baseline (missing baseline = problem; --core-fallback uses the 18 core classes and says so);
no subgraph-UUID class_type; no forbidden/excluded pack class (substring match until real class names are pinned);
VAE/UNET names pinned; models.json sha256 vs a local models dir if given.
"""
import json
import os
import re

import flux_edit_guard
import tpl_fill
from tpl_fill import _jl

FORBIDDEN = ("pulid", "reactor", "promptrelay", "storyboard")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
VAE_PIN = "flux2-vae.safetensors"
UNET_PIN = "FLUX-KLEIN-9B-FP8-NSFW.safetensors"


def check(templates_root, name, version, baseline_path=None, core_fallback=None, models_dir=None):
    probs = []
    try:
        tpl_fill.verify_index(templates_root, name, version)
    except Exception as e:
        probs.append(f"INDEX {e}")
    d = tpl_fill.tdir(templates_root, name, version)
    try:
        g = _jl(os.path.join(d, "workflow_api.json"))
        schema = _jl(os.path.join(d, "params.schema.json"))
    except Exception as e:
        return probs + [f"LOAD {e!r}"]
    used = set(tpl_fill.PH.findall(json.dumps(g)))
    str_keys = {k for k, s in schema.items() if s["type"] == "string"}
    if used - set(schema):
        probs.append(f"UNDECLARED {sorted(used - set(schema))}")
    if str_keys - used:
        probs.append(f"UNUSED_STRING_KEYS {sorted(str_keys - used)}")
    if baseline_path and os.path.isfile(baseline_path):
        allowed = set(_jl(baseline_path, encoding="utf-8"))
    elif core_fallback is not None:
        allowed = set(core_fallback)
        probs.append("NOTE baseline /object_info missing; core list used (not a run clearance)")
    else:
        allowed = None
        probs.append("BASELINE_MISSING pins/object_info baseline not captured")
    for nid, n in g.items():
        ct = n.get("class_type", "")
        if UUID.match(ct):
            probs.append(f"SUBGRAPH_UUID node {nid}")
        if any(f in ct.lower() for f in FORBIDDEN):
            probs.append(f"FORBIDDEN_PACK {ct} node {nid}")
        if allowed is not None and ct not in allowed:
            probs.append(f"CLASS_NOT_IN_BASELINE {ct} node {nid}")
        if ct == "VAELoader" and n["inputs"].get("vae_name") != VAE_PIN:
            probs.append(f"VAE_NOT_PINNED {n['inputs'].get('vae_name')}")
        if ct == "UNETLoader" and n["inputs"].get("unet_name") != UNET_PIN:
            probs.append(f"UNET_NOT_PINNED {n['inputs'].get('unet_name')}")
    if models_dir:
        for m in _jl(os.path.join(d, "models.json"))["models"]:
            p = os.path.join(models_dir, m["name"])
            if not os.path.isfile(p):
                probs.append(f"MODEL_MISSING {m['name']}")
            elif len(m.get("sha256", "")) == 64 and flux_edit_guard.sha256_file(p) != m["sha256"]:
                probs.append(f"MODEL_SHA_MISMATCH {m['name']}")
            elif len(m.get("sha256", "")) != 64:
                probs.append(f"MODEL_SHA_UNVERIFIED {m['name']}")
    return probs


def blocking(probs):
    return [p for p in probs if not p.startswith("NOTE")]


if __name__ == "__main__":
    import argparse
    import sys
    ap = argparse.ArgumentParser()
    ap.add_argument("templates_root"); ap.add_argument("name"); ap.add_argument("version")
    ap.add_argument("--baseline"); ap.add_argument("--models-dir")
    a = ap.parse_args()
    ps = check(a.templates_root, a.name, a.version, a.baseline, None, a.models_dir)
    print("\n".join(ps) or "clean")
    sys.exit(1 if blocking(ps) else 0)
