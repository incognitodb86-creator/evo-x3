#!/c/users/derek/hardcorensfw-testruntime/comfyui/.venv/scripts/python.exe
# PW1b WEIGHTS self-check (ALI-163/ALI-173 bakeoff, CPU + read-only web only, no GPU).
# Check every downloaded file against the Hugging Face API size (tree JSON fetched with
# curl.exe -sL --max-time 30 into notes/web/), then sha256 each file. Writes
# notes/pw1b_objective.json and prints a PASS/FAIL table. rc 0 = all checks pass.
import hashlib
import json
import os
import sys

LLM = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/models/LLM"
WEB = r"C:/AI/community/notes/web"
OUT = r"C:/AI/community/notes/pw1b_objective.json"

TREES = {
    "ggml": "pw1b_tree_ggml_omni7b.json",
    "pt_gguf": "pw1b_tree_pt_lora_gguf.json",
    "lx": "pw1b_tree_lightx2v.json",
}

# (local path, tree key, path inside that repo)
FILES = [
    (os.path.join(LLM, "Qwen2.5-Omni-7B-GGUF", "Qwen2.5-Omni-7B-Q4_K_M.gguf"),
     "ggml", "Qwen2.5-Omni-7B-Q4_K_M.gguf"),
    (os.path.join(LLM, "Qwen2.5-Omni-7B-GGUF", "mmproj-Qwen2.5-Omni-7B-Q8_0.gguf"),
     "ggml", "mmproj-Qwen2.5-Omni-7B-Q8_0.gguf"),
    (os.path.join(LLM, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni",
                  "MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf"),
     "pt_gguf", "MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf"),
    (os.path.join(LLM, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni", "lightx2v-safetensors",
                  "adapter_model.safetensors"),
     "lx", "adapter_model.safetensors"),
    (os.path.join(LLM, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni", "lightx2v-safetensors",
                  "adapter_config.json"),
     "lx", "adapter_config.json"),
    (os.path.join(LLM, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni", "lightx2v-safetensors",
                  "README.md"),
     "lx", "README.md"),
    (os.path.join(LLM, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni", "lightx2v-safetensors",
                  "requirements.txt"),
     "lx", "requirements.txt"),
    (os.path.join(LLM, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni", "lightx2v-safetensors",
                  "system_prompt.py"),
     "lx", "system_prompt.py"),
]


def sizes(tree_key):
    with open(os.path.join(WEB, TREES[tree_key]), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {e["path"]: e.get("size") for e in data if e.get("type") == "file"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    tables = {k: sizes(k) for k in TREES}
    rows = []
    fails = 0
    for path, key, rel in FILES:
        api = tables[key].get(rel)
        local = os.path.getsize(path) if os.path.exists(path) else -1
        ok = api is not None and local >= 0 and local >= api
        if not ok:
            fails += 1
        rows.append({
            "path": path.replace("\\", "/"),
            "repo": key,
            "repo_path": rel,
            "hf_api_size": api,
            "local_size": local,
            "size_ok": ok,
            "sha256": sha256(path) if local >= 0 else None,
        })
        print(("PASS" if ok else "FAIL"), local, ">=", api, rel)
    total = sum(r["local_size"] for r in rows if r["local_size"] > 0)
    print("TOTAL_BYTES", total, "MB", round(total / 1e6, 1))
    print("FALLS", fails)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"files": rows, "total_bytes": total, "fails": fails}, fh, indent=1)
    print("WROTE", OUT)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
