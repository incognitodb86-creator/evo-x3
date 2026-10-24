"""
ali02_citation_check.py - self-check for notes/ali02_claim_inventory_20261025.md.

Every citation in the inventory must resolve in a body that is ON DISK in
C:/AI/community/notes/web. Two hazards this exists to catch:
  1. `scripts/web_fetch.py --clean` deleted this pass's cached bodies, and notes/web is
     git-tracked, so names that already existed in git came back as the 2026-10-23
     committed copy. Line numbers recorded while fetching are therefore untrustworthy.
  2. Cards get edited: TenStrip/10Eros-Max README on main is now 3,698 B, the 15,125 B
     copy quoted in the notes is gone, so old line numbers (87-92, 141, 211, 294) fail.
This script locates each quoted phrase in the file it cites and prints the real line.
Exit 0 = all resolve; 1 = any MISSING-FILE / MISSING-TEXT (inventory must be fixed).
Probe-only: reads files, prints, mutates nothing.
"""
from __future__ import annotations
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent / "web"

# (label, file, phrase)
CITES = [
    # --- official ComfyUI MiniMax H3 docs (committed 2026-10-23 copies) ---
    ("docs-lock-identity", "02v_docs_h3.txt", "Lock identity, style, motion, camera, or voice"),
    ("docs-templates-0.4mp", "02v_docs_h3.txt", "Templates open at"),
    ("docs-native-0.98mp", "02v_docs_h3.txt", "For 16:9 native quality, set"),
    ("docs-avoid-1.0mp", "02v_docs_h3.txt", "Avoid **1.0** MP"),
    ("docs-latent-upscaler", "02v_docs_h3.txt", "Use a **latent upscaler** on the 24-channel video latent"),
    ("docs-refine-denoise", "02v_docs_h3.txt", "**0.1–0.5**"),
    ("docs-latents-separate", "02v_docs_h3.txt", "Video and audio latents are separate"),
    ("docs-trained-range", "02v_docs_h3.txt", "124–362 frames"),
    ("docs-frame-grid", "02v_docs_h3.txt", "17k+5` at 24 fps (124 frames = 5 s)"),
    ("docs-errors-compound", "02v_docs_h3.txt", "Errors compound (faces lose texture first)"),
    ("docs-steps-12-16", "02v_docs_h3.txt", "**12–16** steps"),
    ("docs-steps-50", "02v_docs_h3.txt", "little visible change past"),
    ("docs-audio-12", "02v_docs_h3.txt", "Speech and timbre need **12+** steps"),
    ("docs-sampler-template", "02v_docs_h3.txt", "**`res_multistep`** + **`simple`**"),
    ("docs-sage-2x", "02v_docs_h3.txt", "can roughly **2×** speed"),
    ("docs-int8-morph", "02v_docs_h3.txt", "INT8 attention quantization"),
    ("docs-kitchen-noint8", "02v_docs_h3.txt", "Comfy Kitchen does not support them"),
    ("docs-kitchen-bf16", "02v_docs_h3.txt", "cannot run `int8_convrot` checkpoints"),
    ("docs-sol-attn", "02v_docs_h3.txt", "`sol-attn`"),
    ("docs-vsa-keep10", "02v_docs_h3.txt", "FastH3 uses **`vsa`** at `keep_percent` **10**"),
    ("docs-version-reqs", "02v_docs_h3.txt", "0.30.0+"),
    ("docs-native-1344", "02v_docs_h3_native.txt", "**1344×768** (768px short edge); round to multiples of **32**"),
    ("docs-ref-image-size-max", "02v_docs_h3_native.txt", "keeps 2048px short edge and is much slower"),
    ("docs-prescale-2048", "02v_docs_h3_native.txt", "Pre-scale to 2048 short edge"),
    ("docs-turbo-20steps", "02v_docs_h3_native.txt", "Default **20** steps"),
    ("docs-raise-25", "02v_docs_h3_native.txt", "Raise steps (e.g. **25**)"),
    ("docs-r2v-turbo4", "02v_docs_h3_native.txt", "**4**-step Lightn"),
    ("docs-firstframe-aspect", "02v_docs_h3_native.txt", "resized to the canvas without keeping its aspect ratio"),
    ("docs-fasth3-8steps", "02v_docs_h3_fastvideo.txt", "trained for exactly 8 steps"),
    ("docs-fasth3-vsa", "02v_docs_h3_fastvideo.txt", "`keep_percent` 10 starting at 20%"),
    ("docs-fasth3-cap", "02v_docs_h3_fastvideo.txt", "capped at 768x1344"),
    ("docs-fasth3-noref2va", "02v_docs_h3_fastvideo.txt", "Ref2VA (multi-reference"),
    # --- 10Eros-Max card, current main revision (3,698 B) ---
    ("mc-beta6-10/3", "03y_mc_readme.txt", "Samples on 10/3 shift"),
    ("mc-beta6-8-12", "03y_mc_readme.txt", "slow 8-12 step reference model"),
    ("mc-beta6-sla", "03y_mc_readme.txt", "SLA sparsity seems to destroy it"),
    ("mc-turbo-on-top", "03y_mc_readme.txt", "4step turbo loras can be run on top"),
    ("mc-samplers", "03y_mc_readme.txt", "er_sde, euler, LCM, res_multistep"),
    ("mc-lora-strength", "03y_mc_readme.txt", "needing lower strength 0.2-0.6"),
    ("mc-audio-nonturbo", "03y_mc_readme.txt", "Non-turbo full step audio will always be better"),
    ("mc-resmulti", "03y_mc_readme.txt", "res_multistep/simple 6-8 steps"),
    ("mc-lcm-audio", "03y_mc_readme.txt", "LCM/simple 6-8 steps (best turbo audio)"),
    ("mc-euler", "03y_mc_readme.txt", "Euler/simple 4-8 steps"),
    ("graft-beta6", "03y_graft_md.txt", "beta_6"),
    # --- Continuum: installed-code copies (byte-exact dumps) + fetched docs ---
    ("cont-version-3102", "03y_cont_version.txt", 'PACKAGE_VERSION = "3.10.2"'),
    ("cont-readme-v39", "03y_cont_readme.txt", "MiniMax_H3_Continuum_V39.json"),
    ("cont-driving-v39", "03y_cont_driving_nodes.txt", "class H3ContinuumSamplerV39"),
    ("cont-resolution-multiple32", "03y_cont_resolution.txt", "H3_CANVAS_MULTIPLE"),
    ("cont-resolution-balanced", "03y_cont_resolution.txt", "Balanced"),
    ("cont-hardening-frames", "03y_cont_hardening.txt", "target_frames does not match"),
    ("cont-v39-sampler-doc", "02x_cont_v39_ref_inline.txt", "V39 Sampler"),
    ("cont-v39-groups", "02x_cont_v39_ref_inline.txt", "four groups"),
    ("cont-v39-20s", "02x_cont_v39_ref_inline.txt", "20 s"),
    ("cont-v39-workflow", "02x_cont_v39_workflow.json", "H3ContinuumSamplerV39"),
    ("cont-relnotes-3912", "02x_cont_relnotes_3912.txt", "3.9.12"),
    ("cont-repo-15020", "02x_cont_repo_api.json", "15020"),
    ("cont-registry-3100", "02x_registry_continuum.json", "3.10.0"),
    ("cont-registry-flagged", "02x_registry_continuum.json", "NodeVersionStatusFlagged"),
    # --- continuation node pack (correct repo: ttulttul, 17 stars) ---
    ("continuation-overlap22", "03y_continuation_readme.txt", "overlap_frames   = 22"),
    ("continuation-extension119", "03y_continuation_readme.txt", "extension_frames = 119"),
    ("continuation-mult17", "03y_continuation_readme.txt", "positive multiple of 17"),
    ("extender-subjectdefs", "02v_extender_readme.txt", "subject_definitions"),
    # --- community stats ---
    ("civ-continuum-6942", "02v_civitai_2860061.json", "6942"),
    ("civ-2906001-6489", "02v_civitai_2906001.json", "6489"),
    ("civ-multishot-11067", "02v_civitai_2833322.json", "11067"),
    ("civ-llmvision-517", "02v_civitai_2967166.json", "517"),
    ("minimax-base-4967030", "02x_minimax_base_api.json", "4967030"),
    ("fal-realism-87788", "02v_fal_realism.json", "87788"),
    ("fal-trigger-r34l1sm", "03y_fal_realism_card.txt", "r34l1sm"),
    ("antiburn-1242", "02x_antiburn_api.json", "1242"),
    ("charswap-97293", "02x_character_swap_api.json", "97293"),
    ("latentup-273841", "02x_latent_up_api.json", "273841"),
    ("latentup-repo-775", "02x_latent_up_repo.json", "775"),
    ("pe-qwen36", "02x_lightx2v_pe_api.json", "Qwen3.6"),
    ("pe-t2va", "02x_lightx2v_pe_readme.txt", "T2VA"),
    ("gemma4b-1499393", "02x_gemma4b_api.json", "1499393"),
    ("gemmaee4b-534984", "02x_gemma_e4b_api.json", "534984"),
    ("qwen4b-1232630", "02x_qwen4b_api.json", "1232630"),
    ("comfy-repo-142366", "02x_comfyui_repo.json", "142366"),
    ("kijai-repo-3406", "02x_kijai_repo.json", "3406"),
    ("issue15529-int8convrot", "03y_issue15529.html", "int8_convrot"),
    ("disc28-243f", "02x_minimax_disc28.json", "243"),
    ("cwb-stars-1", "02x_codexbench_api.json", '"stargazers_count":1'),
]


def main() -> int:
    bad = []
    for label, fname, phrase in CITES:
        path = WEB / fname
        if not path.is_file():
            print("MISSING-FILE  %-28s %s" % (label, fname)); bad.append(label); continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [i + 1 for i, ln in enumerate(lines) if phrase in ln]
        if not hits:
            print("MISSING-TEXT  %-28s %s phrase=%r" % (label, fname, phrase[:46])); bad.append(label)
        else:
            print("ok  %-28s %s:%s" % (label, fname, ",".join(map(str, hits[:4]))))
    print("\nchecked %d citations, %d problems" % (len(CITES), len(bad)))
    if bad:
        print("failed: " + ", ".join(bad)); return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
