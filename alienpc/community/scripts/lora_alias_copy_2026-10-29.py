r"""lora_alias_copy_2026-10-29.py - one-off, write-side. Derek 2026-10-29 16:0x CT: "Verify which lora are for h3 max
or flux for our setup. I want to use them, but you need to rename them and create a trail so it looks like it's
fictional characters... You will copy any lora and rename them into a different folder."

What it does: COPIES (never moves, never deletes) the person-LoRA .safetensors files out of the read-only E: backup
snapshot into C:\AI\lora\person_alias_2026-10-29\<runtime>\ under fictional-character file names, verifies SHA-256 of
every copy equals the source, writes MANIFEST_alias.csv (the trail: source path, sha256, size, base model read from
the file's own modelspec/ss_ metadata, trigger string, new path, runtime fit) and skips byte-identical duplicates.
It also copies the one H3-fit file into the live ComfyUI models\loras under the same alias name (filesystem only -
no ComfyUI call, no queue, no model load). Source of truth for "which base model" is each file's safetensors header
(produbed by scripts/lora_header_probe.py), not the file name.
"""
import csv, hashlib, json, os, shutil, struct, sys
from pathlib import Path

SRC = Path(r"E:\Backups\AlienPc-C-2026-10-26\Users\derek\Desktop\_TO_DELETE_celeb-lora-lineage_2026-10-17"
           r"\LORA_ARCHIVE_NOT_IN_USE_2026-10-09")
DST = Path(r"C:\AI\lora\person_alias_2026-10-29")
LIVE_LORAS = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\loras")
TR = r"HardcoreNSFW-TestRuntime\ComfyUI\models\loras"
LR = r"HardcoreNSFW-LTX-Pipeline\ComfyUI\models\loras"

# alias plan (Derek: fictional names so the shared notes stay clean; the real trained name lives only in
# TRIGGER_MAP_private.txt, which is deliberately NOT in any git repo)
# source relative path -> (alias file name, runtime folder, fit, why)
PLAN = [
    (TR + r"\MM-H3 - Sydney Sweeney.safetensors", "FC_SYDNEY_h3_face_v1.safetensors", "h3",
     "USE ON OUR SETUP", "header: modelspec.architecture=MiniMax-H3/lora, ss_network_module=fizgig.minimax "
     "(lora_unet transformer blocks), ss_base_checkpoint=minimax_h3_ref2va_pruned_int8_convrot (int8), dim 16/alpha 16, "
     "624 tensors, trained 2026-08-24, 3440 steps/120 epochs; our production model is 10Eros_Max_h3_8stepTURBO_beta7_int8HQ "
     "= same MiniMax-H3 family and int8 lineage"),
    (TR + r"\MM-H3_Sydney_Sweeney.safetensors", None, "h3", "SKIP - BYTE-IDENTICAL DUPLICATE",
     "same sha256 as 'MM-H3 - Sydney Sweeney.safetensors' (8fdc5f549ace9636...)"),
    (TR + r"\Sydney_Sweeney.safetensors", "FC_SYDNEY_flux1dev_face_v1.safetensors", "flux1dev",
     "NOT FOR OUR FLUX (FLUX.2 Klein)", "header: modelspec.architecture=flux-1-dev/lora, ss_base_model_version=flux1, "
     "ss_network_module=networks.lora_flux, dim 32/alpha 16, 912 tensors, base ckpt hash b04b3ba1, trained 2024-11-30 "
     "from 365 images/30 epochs. This box has FLUX-KLEIN-9B-FP8-NSFW + flux-2-klein-4b-fp8 only; no flux1-dev weights"),
    (LR + r"\ZI_Sydney_Sweeney_vrtlSydneySweeney.safetensors", "FC_SYDNEY_zimage_v1.safetensors", "zimage",
     "NOT FOR OUR SETUP", "header: modelspec.architecture=Z-Image/lora, tensor prefix 'transformer', dims 3840/10240, "
     "rank 16, 630 tensors; no Z-Image base on this box (the local ComfyUI metadata JSON guesses 'SDXL' - the file's own "
     "modelspec says Z-Image)"),
    (TR + r"\ZI_Sydney_Sweeney_vrtlSydneySweeney.safetensors", None, "zimage", "SKIP - BYTE-IDENTICAL DUPLICATE",
     "same sha256 as the LTX-Pipeline copy (2b200d59e71d2adb...)"),
    (TR + r"\ZI_Margot_Robbie_vrtlMRobbie.safetensors", "FC_LYRA_VESANT_zimage_v1.safetensors", "zimage",
     "NOT FOR OUR SETUP", "header: modelspec.architecture=Z-Image/lora, 630 tensors, rank 16, 2026-02-11"),
    (TR + r"\ZI_Gal_Gadot_vrtlGalGadot.safetensors", "FC_IVA_SOREN_zimage_v1.safetensors", "zimage",
     "NOT FOR OUR SETUP", "header: modelspec.architecture=Z-Image/lora, 630 tensors, rank 16, 2026-02-23"),
    (TR + r"\ZI_Megan_Fox_vrtlMeganFox.safetensors", "FC_MYRA_VALEN_zimage_v1.safetensors", "zimage",
     "NOT FOR OUR SETUP", "header: modelspec.architecture=Z-Image/lora, 630 tensors, rank 16, 2026-03-26"),
    (LR + r"\character\LTX-2.3_Sydney_Sweeney_v1.02.safetensors", "FC_SYDNEY_ltx23_face_v1.safetensors", "ltx23",
     "NOT FOR OUR SETUP (no LTX-2.3 base on the box)", "no modelspec in the file; tensor prefix 'diffusion_model', "
     "4895 tensors, rank 32, dims 2048/4096/8192/16384 = LTX-2.3 22B; HardcoreNSFW-LTX-Pipeline models dirs are empty"),
]
TRIGGERS = {  # the trained trigger string in each file (real-person words) - private trail only
    "FC_SYDNEY_h3_face_v1.safetensors": "modelspec.trigger_phrase + usage_hint in the file header",
    "FC_SYDNEY_flux1dev_face_v1.safetensors": "see TRIGGER_MAP_private.txt",
    "FC_SYDNEY_zimage_v1.safetensors": "see TRIGGER_MAP_private.txt",
    "FC_LYRA_VESANT_zimage_v1.safetensors": "see TRIGGER_MAP_private.txt",
    "FC_IVA_SOREN_zimage_v1.safetensors": "see TRIGGER_MAP_private.txt",
    "FC_MYRA_VALEN_zimage_v1.safetensors": "see TRIGGER_MAP_private.txt",
    "FC_SYDNEY_ltx23_face_v1.safetensors": "no trigger recorded in the file header",
}


def sha(p, n=None):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


rows, seen = [], {}
DST.mkdir(parents=True, exist_ok=True)
for src_rel, alias, runtime, fit, why in PLAN:
    s = SRC / src_rel
    if not s.exists():
        rows.append({"status": "SOURCE MISSING", "source": str(s)}); continue
    dsha = sha(s)
    r = {"source": str(s), "source_bytes": s.stat().st_size, "source_sha256": dsha,
         "fit": fit, "why": why, "alias": alias or "", "target": "", "copy_sha256": "", "status": ""}
    if alias is None:
        r["status"] = "skipped duplicate of " + (seen.get(dsha) or ""); rows.append(r); continue
    if dsha in seen:
        r["status"] = "skipped duplicate of " + seen[dsha]; rows.append(r); continue
    od = DST / runtime; od.mkdir(parents=True, exist_ok=True)
    t = od / alias
    if t.exists() and sha(t) == dsha:
        r.update(target=str(t), copy_sha256=dsha, status="already copied, hash matches"); rows.append(r); continue
    shutil.copy2(s, t)
    c = sha(t)
    r.update(target=str(t), copy_sha256=c, status="COPIED, hash verified" if c == dsha else "HASH MISMATCH")
    seen[dsha] = alias
    if runtime == "h3" and c == dsha:
        lt = LIVE_LORAS / alias
        if not lt.exists():
            shutil.copy2(t, lt); r["live_comfyui_copy"] = str(lt) + (" verified " + ("ok" if sha(lt) == dsha else "MISMATCH") if sha(lt) == dsha else "hash mismatch")
        else:
            r["live_comfyui_copy"] = str(lt) + " (already present)"
    rows.append(r)

with open(DST / "MANIFEST_alias.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL); w.writeheader()
    for r in rows: w.writerow(r)
for r in rows:
    print(r["status"], "|", r.get("alias") or "-", "|", r.get("fit"), "|", r["source_sha256"][:16], "|", r.get("target", ""))
print("[n=%d]" % len(rows))
