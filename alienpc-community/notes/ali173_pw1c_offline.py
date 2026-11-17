"""PW1c REGISTER (no GPU): prove the MiniMax-H3 prompt-rewriter node's OWN discovery code
sees the weights PW1b put on disk, without touching ComfyUI or any GPU port.

Offline copy of what the Omni node's dropdown is built from (custom_nodes pack, v0.30.0):
  writer_omni._build_model_map()  = catalog.models_omni() entries  (labels, on-disk marked)
                                  + discovery.scan_captioner_gguf(GGUF_ARCH_OMNI) -> "on disk: ..." rows
  adapters                        = catalog.adapter(fmt, catalog.ADAPTERS_OMNI) + discovery.scan_local_gguf_adapters()
So the same three calls here are the same answer the node will build at import time.

folder_paths is stubbed (the pack imports it lazily inside functions) so this runs in any
python: it never imports ComfyUI, comfy_api, torch, or the node's own engine modules.
0 GPU minutes: no HTTP, no port, no comfy_ctl, no render.
"""
import json
import os
import sys
import types

CH = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
PACK = CH + r"/custom_nodes/MiniMax-H3-Prompt-Rewriter-ComfyUI"
OUT = r"C:/AI/community/notes/pw1c_objective.json"

fp = types.ModuleType("folder_paths")
fp.models_dir = CH + "/models"
fp.get_folder_paths = lambda key: [os.path.join(fp.models_dir, key)]
fp.add_model_folder_path = lambda *a, **k: None
fp.get_user_directory = lambda: CH + "/user"
sys.modules["folder_paths"] = fp
sys.path.insert(0, PACK)

from minimax_h3_rewriter import catalog, discovery, model_sections, paths  # noqa: E402

rep = {"model_root": paths.models_root(), "user_models_json": catalog.user_file(),
       "node_version": "", "checks": [], "dump": {}}


def chk(name, ok, note=""):
    rep["checks"].append({"name": name, "ok": bool(ok), "note": note[:400]})
    print(("PASS " if ok else "FAIL ") + name + ("  " + note[:220] if note else ""), flush=True)


def short(p):
    return os.path.relpath(p, fp.models_dir).replace("\\", "/")


# --- 1. the Omni base-model scan the node runs (label, model path, mmproj path)
base = discovery.scan_captioner_gguf(discovery.GGUF_ARCH_OMNI)
rep["dump"]["scan_omni_base"] = [(lbl, short(m), short(p)) for lbl, m, p in base]
print("\n== discovery.scan_captioner_gguf(qwen2vl) = the 'on disk:' rows of the Omni base list")
for lbl, m, p in base:
    print("   %s\n        model=%s\n        mmproj=%s" % (lbl, short(m), short(p)))

q4 = [b for b in base if os.path.basename(b[1]).lower() == "qwen2.5-omni-7b-q4_k_m.gguf"]
chk("base Q4_K_M is scanned into the Omni base list", len(q4) == 1,
    q4[0][0] if q4 else "not found")
if q4:
    hdr_m = discovery.gguf_header(q4[0][1])
    hdr_p = discovery.gguf_header(q4[0][2])
    rep["dump"]["base_header"] = {"model": hdr_m, "mmproj": hdr_p,
                                  "problem": discovery.gguf_problem_omni(q4[0][1])}
    chk("base GGUF header is an Omni build (no 'wrong size' suffix)",
        not discovery.gguf_problem_omni(q4[0][1]), str(rep["dump"]["base_header"]["problem"]))
    chk("mmproj carries audio (a real Omni projector, not vision-only)",
        bool(hdr_p.get("audio")), "mmproj audio=%s vision=%s" % (hdr_p.get("audio"), hdr_p.get("vision")))
    chk("mmproj is paired by stem to the base (discovery._pair_mmproj rule)",
        "Qwen2.5-Omni-7B" in os.path.basename(q4[0][2]), short(q4[0][2]))

# --- 2. the adapter scan the node runs
adapters = discovery.scan_local_gguf_adapters()
rep["dump"]["scan_adapters"] = [(lbl, short(p)) for lbl, p in adapters]
print("\n== discovery.scan_local_gguf_adapters() = the adapter rows")
for lbl, p in adapters:
    print("   %s  (%s)" % (lbl, short(p)))
q8 = [a for a in adapters if os.path.basename(a[1]).lower() ==
      "minimax-h3-prompt-rewriter-lora-omni-q8_0.gguf"]
chk("Q8_0 Omni adapter GGUF is scanned into the adapter list", len(q8) == 1,
    q8[0][0] if q8 else "not found")

# --- 3. the user models.json (the live list) entries the node offers
print("\n== catalog models_omni entries (the live list at %s)" % catalog.user_file())
for e in catalog.models_omni():
    held = model_sections.on_disk("models_omni", e.fmt, e.repo, e.file, e.mmproj)
    rep["dump"].setdefault("catalog_models_omni", []).append(
        {"label": e.label, "format": e.fmt, "repo": e.repo, "file": e.file,
         "mmproj": e.mmproj, "on_disk": list(held)})
    print("   %-44s fmt=%-11s on_disk=%s" % (e.label, e.fmt, [short(h) for h in held] or "NO"))
q4e = [x for x in rep["dump"]["catalog_models_omni"] if x["file"] == "Qwen2.5-Omni-7B-Q4_K_M.gguf"]
chk("catalog entry 'Qwen2.5-Omni-7B GGUF Q4_K_M' resolves on disk (no models.json edit)",
    bool(q4e and q4e[0]["on_disk"]), (q4e[0]["on_disk"] and short(q4e[0]["on_disk"][0])) or "")

for fmt, sec in ((catalog.FORMAT_GGUF, catalog.ADAPTERS_OMNI),
                 (catalog.FORMAT_TRANSFORMERS, catalog.ADAPTERS_OMNI)):
    spec = catalog.adapter(fmt, sec)
    rep["dump"]["catalog_adapter_%s" % fmt] = {"repo": spec.repo, "file": spec.file,
                                               "configured": spec.configured,
                                               "alts": [a.file for a in spec.alternatives]}
    print("\n== catalog.adapter(%r, adapters_omni) = %s %s alts=%s"
          % (fmt, spec.repo, spec.file, [a.file for a in spec.alternatives]))

# --- 4. model_sections.listing() needs comfy_api (it imports writer_omni to build the map),
# so the dropdown rows themselves are checked LIVE on :10004 in notes/ali173_pw1c_live_check.py.
# What is proven here is the data that map is built from: the two scans + the catalog entries.

# --- 5. the safetensors (lightx2v) route: where the transformers loader looks
repo = catalog.adapter(catalog.FORMAT_TRANSFORMERS, catalog.ADAPTERS_OMNI).repo
tgt = paths.local_dir_for_repo(repo)
inner = os.path.join(tgt, "lightx2v-safetensors")
rep["dump"]["safetensors_route"] = {
    "repo": repo, "repo_dir": tgt, "repo_dir_files": sorted(os.listdir(tgt)),
    "adapter_is_complete_at_repo_dir": paths.adapter_is_complete(tgt),
    "subdir": inner, "subdir_files": sorted(os.listdir(inner)) if os.path.isdir(inner) else [],
    "adapter_is_complete_in_subdir": paths.adapter_is_complete(inner),
    "present_folder_adapter_complete": paths.present_folder(repo, complete=paths.adapter_is_complete)}
print("\n== safetensors route (repo %s -> %s)" % (repo, short(tgt)))
print("   adapter_is_complete at the repo dir = %s (files: %s)"
      % (rep["dump"]["safetensors_route"]["adapter_is_complete_at_repo_dir"],
         ", ".join(rep["dump"]["safetensors_route"]["repo_dir_files"])))
print("   adapter_is_complete in lightx2v-safetensors\\ = %s; present_folder = %s"
      % (rep["dump"]["safetensors_route"]["adapter_is_complete_in_subdir"],
         rep["dump"]["safetensors_route"]["present_folder_adapter_complete"] or ""))
chk("transformers (lightx2v safetensors) adapter resolves at the repo dir",
    bool(rep["dump"]["safetensors_route"]["present_folder_adapter_complete"]),
    "files sit in the repo dir = PW1b's lightx2v-safetensors subfolder was moved up")

# --- 6. the GGUF adapter the node resolves for 'gguf' (the PW1d route)
gg_repo = catalog.adapter(catalog.FORMAT_GGUF, catalog.ADAPTERS_OMNI).repo
gg = paths.present_file(gg_repo, "MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf")
rep["dump"]["gguf_adapter_route"] = {"repo": gg_repo, "resolved": gg}
chk("GGUF Q8_0 adapter resolves through paths.present_file (%s)" % gg_repo, bool(gg), short(gg) if gg else "unresolved")

rep["pass"] = all(c["ok"] for c in rep["checks"])
print("\nSUMMARY %d/%d checks passed" % (sum(1 for c in rep["checks"] if c["ok"]), len(rep["checks"])))
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rep, f, indent=1, ensure_ascii=False)
print("dump -> " + OUT)
sys.exit(0 if rep["pass"] else 1)
