"""lora_header_probe.py - read-only probe of .safetensors LoRA files: parses the safetensors header JSON (no model load),
prints base-model / training metadata keys, the tensor shape summary needed to tell which runtime a LoRA fits
(LTX-2.3 vs MiniMax-H3 vs FLUX.1/FLUX.2-Klein vs SDXL), full SHA-256, and any .metadata/.metadata.json sidecar.
Usage: python lora_header_probe.py <folder_with_loras> [--json out.json]
"""
import argparse, hashlib, json, os, sys, struct
from pathlib import Path

KEYS = ["ss_base_model", "ss_base_model_version", "ss_model_name", "ss_migration_target", "ss_training_algorithm",
        "ss_network_module", "ss_network_dim", "ss_network_alpha", "ss_sd_model_name", "ss_sd_model_hash",
        "ss_unet_name", "ss_clip_name", "ss_v2", "ss_first_block", "ss_last_block", "ss_trained_blocks",
        "modelspec.title", "modelspec.architecture", "modelspec.author", "modelspec.name", "modelspec.description",
        "modelspec.date", "modelspec.license", "modelspec.dataset", "modelspec.training_version", "modelspec.precedence",
        "ss_tag_frequency", "ss_dataset_tag_frequency", "preprocessor", "processor", "trainer", "created_by",
        "format", "base_model", "name", "title", "description", "author", "source", "source_image", "version",
        "date", "trigger_words", "triggers", "prompt", "negative", "ss_num_train_images", "ss_num_epochs",
        "ss_learning_rate", "minimax", "ltx", "flux"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def header(p):
    with open(p, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        return json.loads(f.read(n).decode("utf-8", "replace"))


def probe(p):
    hd = header(p)
    md = hd.get("__metadata__") or {}
    keys = {k: (json.dumps(v)[:400] if not isinstance(v, str) else v[:400]) for k, v in sorted(md.items())
            if any(t in k.lower() for t in KEYS) or k.lower() in ("ss_tag_frequency",)}
    prefixes = {}
    for k, v in hd.items():
        if k == "__metadata__":
            continue
        sh = tuple(v.get("shape", []))
        pre = k.rsplit(".", 1)[0] if "." in k else k
        prefixes.setdefault(pre.split(".")[0], []).append(sh)
    top = sorted(prefixes.items(), key=lambda kv: -len(kv[1]))[:12]
    return {"file": os.path.basename(p), "bytes": os.path.getsize(p), "sha256": sha256(p),
            "tensors": len(hd) - 1, "metadata_keys_present": keys,
            "all_metadata_keys": sorted(md.keys()),
            "tensor_prefix_counts": {k: len(v) for k, v in top},
            "tensor_prefix_shapes_sample": {k: [list(s) for s in sorted(set(v))[:4]] for k, v in top},
            "shape_set": sorted({str(s) for k, v in prefixes.items() for s in set(v)})[:25]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("folder"); ap.add_argument("--json", default=None)
    a = ap.parse_args()
    files = sorted(str(f) for f in Path(a.folder).rglob("*.safetensors"))
    out = []
    for f in files:
        try:
            r = probe(f)
        except Exception as e:
            r = {"file": os.path.basename(f), "bytes": os.path.getsize(f), "error": repr(e)[:200]}
        for side in (f + ".json", f.replace(".safetensors", ".metadata"), f.replace(".safetensors", ".metadata.json"),
                     os.path.join(os.path.dirname(f), ".cache\\huggingface\\download", os.path.basename(f) + ".metadata")):
            if os.path.exists(side):
                r["sidecar_" + os.path.basename(side)] = open(side, "r", encoding="utf-8", errors="replace").read()[:900]
        out.append(r)
        print(json.dumps(r, indent=1)[:4000], flush=True)
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[n={len(out)}]", flush=True)
