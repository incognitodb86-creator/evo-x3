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
Four lists:
  CITES   positive citations - the phrase MUST be in the named file on disk.
  BANNED  negative controls - the phrase MUST NOT be in the file (this is how a
          refuted quote stays recorded: e.g. "50-100 words" is quoted in our notes
          as the lightx2v card's line, and the card on disk has no such text, so the
          check FAILS if anyone ever restores that citation without re-verifying it).
  GLOBAL_ABSENT (added by AUD1 2026-10-27) - tokens that appear in NO body at all. The
          AUD1 fault was an audit doc citing a body that carries 0 hits for the claim
          ("lowvram recommended for >20GB weights on 16GB VRAM" cited to
          02v_docs_h3.txt, which has no `lowvram` anywhere). The 0-hit list of that
          audit is now a gate: if a future pass fetches a body that DOES carry one of
          these tokens, the row is no longer UNSOURCED and this scan says so loudly.
  BLOCKED citations we could not resolve because the source refused the fetch
          (401/404 stamp on disk). Printed as unverifiable, never counted as a pass.
Exit 0 = all CITES resolve, all BANS hold and all GLOBAL tokens are absent; 1 = any
MISSING-FILE / MISSING-TEXT / BAN-HOLDS / GLOBAL-PRESENT (the doc must be fixed).
--selftest: runs the same detectors on a seeded set that MUST fail (2 cites + 1 ban +
1 global + 2 doc-scan faults).
Probe-only: reads files, prints, mutates nothing.

AUD1 scope (2026-10-27): the CITES rows marked `aud1:` are the verbatim wording that
notes/cf1_setup_audit_20261024.md v2 now cites, and the BANNED rows marked `aud1:` are
the refuted quotes that audit used to carry. Both audit docs are in SCAN_DOCS, so a
citation of a body that is not on disk is a named failure.

Two measured facts AUD1 added to this gate, because they are properties of the bodies:
1. The TenStrip card on disk is 3,698 B / **63 lines** (md5 6471e229170acb361bc88b232eb9c6be, four
   byte-identical copies). The card line map in notes/hc15_start_fidelity_audit.md was written against
   the 15,125 B card (its addendum records `wc -l` = 56), so `:30`/`:40`/`:41`/`:46`/`:51`/`:56` do not
   resolve against the file on disk. Six CITES rows I wrote today FAILED MISSING-TEXT for that reason
   (Ultra Mode, 3 images, the beta_6 chain line, 12+ steps, BF16 convrot, "er_sde/beta (default)");
   they are kept as BANNED rows (`card-no-*`) so the refutation is the recorded state.
2. `wc -l` on a body and a python splitlines() of the same body can disagree when the file is UTF-16LE
   (02v_docs_h3.txt) - the NUL-compact read in read_body() is the measured workaround, and the card
   file has 0 NUL bytes, so it needs none. Never cite a line number read through a decode that the
   file does not support.
3. The plan is CRLF, and its rows are single PHYSICAL lines, so the gate splits on \n only: a row's line
   number is the gate's address. Measured in fix_plan.md 2026-10-27: 251 CR (all at line ends) plus 12
   control bytes inside the text (8x0x07, 2x0x08, 2x0x09) - a non-raw Python string wrote `C:` + backslash
   paths and
   ate the escapes (the AGENTS.md notes/ticks rule, now proven in the plan itself). A splitlines() there
   invents rows, and reading a path through a decoder that eats escapes is how a citation stops matching the
   file it names.

PLAN mode (0.7, 2026-10-27) - the same class of fault one level up: a PLAN row that cites an artifact.
`--plan` reads ralph-community/fix_plan.md, takes the rows that belong to an OPEN item (`- [ ]` / `- [~]`,
excluding `## Optional`), extracts every forward-slash and backslash `C:` path citation, and checks it
that prompted it: three rows of the TOP-SCENE item point at `notes/hc15_20261024_stills.md`, and no such file
has ever been committed; the register the builder really writes is the generated block in
`notes/hc15_20261024.md` (six clips) plus the per-id manifests `notes/hc15_anchor_carry_<id>.json`. A path
that is not there costs the next agent its whole verification step, exactly like a dead web/ token.
Three claim classes, because a plan row does not always assert existence (measured on the real plan):
  POSITIVE  the row treats the file as the artifact to read/verify -> MUST exist, and inside a repo this
            agent owns (C:/AI/community, C:/AI/director, ralph-community) MUST be git-tracked (L8, L20:
            untracked files die at the pass boundary, so a tracked citation is the only durable one).
  ABSENT    the row states the file is gone / has 0 rows / is not on disk -> MUST stay absent; if it shows
            up the row is stale and the gate fires PLAN-PATH-RESURRECTED (the BANNED-list rule).
  RUNTIME   the row describes a file a running script creates (the gpu-render lock) -> its directory must
            exist and the file may come and go; a present lock is reported, never a failure.
`--plan-selftest` seeds seven cases on mutated COPIES of the real plan written to a temp dir (nothing is
written into the plan, and no seed file is left in the repo - 0.8): a deleted cited path, an existing tracked
path asserted absent, an existing UNTRACKED path cited as the artifact (notes/hc15_audit/ab_seed_00.json is
the real untracked file this fires on), a plan with no citations at all (PLAN-NO-CITES: a gate that reads
nothing must not look green), a runtime path whose directory is gone, a gitignored runtime path (the budget
ledger) that must NOT fail - the rule that keeps .gitignore-declared trees out of the findings needs a seed
too - and a directory reported as empty, which must NOT fail either because the row's claim is 'nothing
there'. Exit 0 = all seven behave and the real plan is clean.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
import tempfile
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
    # graft write-up: supports ONLY "the 10Eros builds are a structured cross-arch
    # graft" - it has NO "beta" string and NO frame counts, so it is not the source
    # for the 124/243/362 frame claim (that is MiniMax discussion 28 + the docs).
    ("graft-structured-transfer", "03y_graft_md.txt", "structured cross-architecture transfer"),
    ("disc28-frame-grid-124", "02x_minimax_disc28.json", "124"),
    ("disc28-frame-grid-362", "02x_minimax_disc28.json", "362"),
    # --- Continuum: installed-code copies (byte-exact dumps) + fetched docs ---
    ("cont-version-3102", "03y_cont_version.txt", 'PACKAGE_VERSION = "3.10.2"'),
    ("cont-readme-v39", "03y_cont_readme.txt", "MiniMax_H3_Continuum_V39.json"),
    ("cont-driving-v39", "03y_cont_driving_nodes.txt", "class H3ContinuumSamplerV39"),
    ("cont-resolution-multiple32", "03y_cont_resolution.txt", "H3_CANVAS_MULTIPLE"),
    ("cont-resolution-balanced", "03y_cont_resolution.txt", "Balanced"),
    ("cont-hardening-frames", "03y_cont_hardening.txt", "target_frames does not match"),
    ("cont-v39-refdoc", "03y_cont_v39_ref_inline.txt", "has a new Reference Images input"),
    ("cont-v39-draft030", "03y_cont_v39_ref_inline.txt", "Draft 0.30 MP"),
    ("cont-v39-nogate", "03y_cont_v39_ref_inline.txt", "has not passed a real browser save/reload or GPU acceptance gate"),
    ("cont-v39-seqblank", "03y_cont_v39_ref_inline.txt", "Sequence Prompt is blank"),
    ("cont-v39-workflow", "02x_cont_v39_workflow.json", "H3ContinuumSamplerV39"),
    ("cont-relnotes-3912", "02x_cont_relnotes_3912.txt", "3.9.12"),
    ("cont-repo-265", "02x_cont_repo_api.json", "265"),
    ("cont-repo-owner", "02x_cont_repo_api.json", "ukr8b3g-cmyk/ComfyUI-H3-Continuum"),
    ("cont-registry-3100", "02v_registry_continuum.json", "3.10.0"),
    ("cont-registry-flagged", "02v_registry_continuum.json", "NodeVersionStatusFlagged"),
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
    ("antiburn-1242", "04z_antiburn_api.json", "1242"),
    ("charswap-97293", "04z_charswap_api.json", "97293"),
    ("latentup-273841", "02x_latent_up_api.json", "273841"),
    ("latentup-repo-775", "02x_latent_up_repo.json", "775"),
    ("pe-qwen36", "04z_pe_api.json", "Qwen3.6"),
    ("pe-t2va", "02v_lightx2v_pe_readme.txt", "T2VA"),
    ("pe-short-prompt", "02v_lightx2v_pe_readme.txt", "Short prompt \u2500\u2500\u25ba"),
    ("gemma12b-1499393", "04z_gemma12b_api.json", "1499393"),
    ("gemmae4b-534984", "04z_gemmae4b_api.json", "534984"),
    ("qwen4b-1232630", "04z_qwen4b_api.json", "1232630"),
    ("comfy-repo-142366", "02x_comfyui_repo.json", "142366"),
    ("kijai-repo-3406", "02x_kijai_repo.json", "3406"),
    ("issue15529-int8convrot", "03y_issue15529.html", "int8_convrot"),
    ("disc28-243f", "02x_minimax_disc28.json", "243"),
    ("fal-87788", "04z_fal_api.json", "87788"),
    # --- aud1 (2026-10-27): the verbatim wording cf1_setup_audit_20261024.md v2 cites ---
    ("aud1-docs-ck-flag", "02v_docs_h3.txt", "or use `--use-ck-attention`"),
    ("aud1-docs-ck-bf16-row", "02v_docs_h3.txt", "On **bf16** checkpoints, **Comfy Kitchen attention**"),
    ("aud1-docs-start-pct", "02v_docs_h3.txt", "Defaults `start_percent` **0.2**, `end_percent` **1.0**"),
    ("aud1-docs-steps-173", "02v_docs_h3.txt", "little visible change past **50**"),
    ("aud1-docs-audio-12plus", "02v_docs_h3.txt", "Speech and timbre need **12+** steps"),
    ("aud1-docs-antiburn-05", "02v_docs_h3.txt", "on clips after the first at `strength_model`"),
    ("aud1-antiburn-card-start05", "02v_antiburn_readme.txt", "**Start at 0.5.**"),
    ("aud1-antiburn-card-numbers", "02v_antiburn_readme.txt", "without the LoRA, **+6%** with it at 0.5"),
    ("aud1-native-round32", "02v_docs_h3_native.txt", "round sides to 32"),
    ("aud1-corenodes-17k5", "02v_core_nodes_minimax_head.txt", "17k+5"),
    ("aud1-corenodes-refsize-opts", "02v_core_nodes_minimax_head.txt", 'ref_image_size", options=["match", "max"]'),
    ("aud1-corenodes-audiovae", "02v_core_nodes_minimax_head.txt", "_encode_ref_audio(audio_vae, audio)"),
    ("aud1-card-nocache", "03y_mc_readme.txt", "No cache or spectrum if doing reference"),
    ("aud1-card-sla", "03y_mc_readme.txt", "SLA sparsity seems to destroy it"),
    ("aud1-card-euler-row", "03y_mc_readme.txt", "Euler/simple 4-8 steps"),
    ("aud1-card-audio-nonturbo", "03y_mc_readme.txt", "Non-turbo full step audio will always be better"),
    ("aud1-pe-nondiegetic", "02v_lightx2v_pe_readme.txt", "non_diegetic_music"),
    ("aud1-pytraveler-six", "02v_pytraveler2_readme.txt", "`Ref2AV` returns six"),
    ("aud1-extender-subjdef", "02v_extender_readme.txt", "at the **very beginning of every clip prompt**"),
    ("aud1-ls-checkendpoint", "01r_ls_comfyui.txt", "checkEndpoint: /"),
    ("aud1-ls-configkeys", "01r_ls_comfyui.txt", "models.*.compat.ignoreWebsockets"),
    ("aud1-ls-concurrency", "01r_ls_comfyui.txt", "raised to at least `999`"),
    ("aud1-ls-cmdstop-example", "01r_ls_comfyui.txt", "cmdStop: docker stop comfyui-auto"),
    ("aud1-ls-readme-cmdstop", "01r_llamaswap_readme.txt", "`cmdStop` gracefully stop Docker/Podman containers"),
    ("aud1-ls-readme-unloadtimeout", "01r_llamaswap_readme.txt", "`unloadTimeout` to tune graceful unloads"),
    ("aud1-ls-readme-ttl", "01r_llamaswap_readme.txt", "`ttl` to automatically unload models"),
    ("aud1-ls-ttl-persistent", "01r_ls_ttl-and-unloading.txt", "plus a `persistent` group"),
    ("aud1-comfymcp-listen-loopback", "01r_comfymcp_readme.html", "is the default bind spelled explicitly"),
    # aud1: the llama-swap GROUPS page IS on disk, saved under other names (agy41/rt prefixes).
    ("aud1-groups-swap-true", "agy41_ls_groups.md", "only one member runs at a time"),
    ("aud1-groups-exclusive-true", "agy41_ls_groups.md", "running a member unloads every other group"),
    ("aud1-groups-persistent", "agy41_ls_groups.md", "other groups can never unload this one"),
    # aud1: the TenStrip card sentences hc15_start_fidelity_audit.md now records verbatim.
    # Measured 2026-10-27 against the 3,698 B / 63-line card on disk (md5 6471e229...). Six rows
    # I first wrote here FAILED MISSING-TEXT: they were 15,125 B-card sentences (Ultra Mode, 3
    # images, the beta_6 chain line, 12+ steps, BF16 convrot, er_sde/beta (default)) that are in
    # NO copy on disk. They are BANNED rows below, not CITES rows.
    ("aud1-card-shifted-base", "03y_mc_readme.txt", "Shifted base H3, a capable model"),
    ("aud1-card-beta5-grafts", "03y_mc_readme.txt", "7 different concept-grouped grafts"),
    ("aud1-card-lora-strength", "03y_mc_readme.txt", "usually needing lower strength 0.2-0.6"),
    ("aud1-card-sampler-list-head", "03y_mc_readme.txt", "Some working sampling setups:"),
    ("aud1-card-ersde-4steps", "03y_mc_readme.txt", "er_sde/beta 4 steps"),
    ("aud1-card-ersde-beta57-4-6", "03y_mc_readme.txt", "er_sde/beta57 4-6 steps"),
    ("aud1-card-lcm-best-turbo-audio", "03y_mc_readme.txt", "(best turbo audio)"),
    ("aud1-card-lcm-beta-4-6", "03y_mc_readme.txt", "LCM/beta 4-6 steps"),
    ("aud1-card-lcm-simple-6-8", "03y_mc_readme.txt", "LCM/simple 6-8 steps"),
    ("aud1-card-turbo-lora-on-top", "03y_mc_readme.txt", "4step turbo loras can be run on top of it"),
    ("aud1-card-perfect-at-8", "03y_mc_readme.txt", "looks and sounds perfect at 8 steps"),
    ("aud1-card-int8-convrot-link", "03y_mc_readme.txt", "cicalooo/10Eros-Max-h3-int8-convrot"),
    ("aud1-card-beta34-corrupt", "03y_mc_readme.txt", "beta_4 and beta_3 are corrupted test versions"),
    ("aud1-card-delta1024", "03y_mc_readme.txt", "built on the delta1024 h3 merge"),
    ("aud1-card-license-source-models", "03y_mc_readme.txt", "transferred character from LTX 2.3, Wan 2.2, and Krea 2"),
]

# Must NOT be present in the named file (refuted quotes; see docstring).
BANNED = [
    # settings_audit_20261023.md:221-233 / hc_face_research:166-172 attribute
    # "50-100 words" to MiniMax docs AND to the lightx2v rewriter card.
    # grep -rl "50-100 words" over ALL of notes/web = 0 files. Refuted.
    ("pe-50-100-words-absent", "02v_lightx2v_pe_readme.txt", "50-100 words"),
    ("docs-50-100-words-absent", "02v_docs_h3.txt", "50-100 words"),
    ("docs-100-200-words-absent", "02v_docs_h3_native.txt", "100-200 words"),
    ("mc-word-count-absent", "03y_mc_readme.txt", "word"),
    # 02v_docs_h3.txt is the resolution/steps page: FaceRefine was quoted from it.
    ("docs-facerefine-absent", "02v_docs_h3.txt", "facerefine"),
    # 03y_graft_md.txt was cited for the 124/243/362 frame grid and for "beta6".
    ("graft-no-frame-grid", "03y_graft_md.txt", "243"),
    ("graft-no-beta-string", "03y_graft_md.txt", "beta"),
    # --- aud1 (2026-10-27): quotes the 2026-10-24 cf1 audit cited and the bodies refute ---
    # the memory row: "lowvram recommended for >20GB weights on 16GB VRAM" cited to the H3 docs page.
    ("aud1-docs-no-lowvram", "02v_docs_h3.txt", "lowvram"),
    ("aud1-docs-no-20gb", "02v_docs_h3.txt", ">20GB"),
    ("aud1-docs-no-16gb-vram", "02v_docs_h3.txt", "16GB VRAM"),
    ("aud1-docs-no-rife", "02v_docs_h3.txt", "RIFE"),
    ("aud1-docs-no-cfg-value", "02v_docs_h3.txt", "cfg 1.0"),
    ("aud1-docs-no-frames-literal", "02v_docs_h3.txt", "(frames - 5)"),
    # the health-timeout / Strata / KV rows cited the llama-swap README: none of it is there.
    ("aud1-ls-no-120-1200", "01r_llamaswap_readme.txt", "120-1200"),
    ("aud1-ls-no-max-context", "01r_llamaswap_readme.txt", "--max-context"),
    ("aud1-ls-no-kv-int8", "01r_llamaswap_readme.txt", "int8"),
    ("aud1-ls-comfyui-no-exclusive", "01r_ls_comfyui.txt", "exclusive"),
    ("aud1-ls-comfyui-no-taskkill", "01r_ls_comfyui.txt", "taskkill"),
    # the TenStrip card rows quoted sentences the 3,698 B card on disk does not contain.
    ("aud1-card-no-topk", "03y_mc_readme.txt", "topk"),
    ("aud1-card-no-video-only", "03y_mc_readme.txt", "video-only"),
    ("aud1-card-no-simple-motion", "03y_mc_readme.txt", "simple motion"),
    ("aud1-card-no-word-rule", "03y_mc_readme.txt", "350-500"),
    ("aud1-card-no-cfg", "03y_mc_readme.txt", "cfg"),
    # invented quotes from notes/plans/aud1-citation-repair.md (2026-10-27): 0 hits in every body.
    ("aud1-card-no-invented-smarter", "03y_mc_readme.txt", "much smarter"),
    ("aud1-card-no-invented-guider", "03y_mc_readme.txt", "ModelSamplingModelPatch"),
    ("aud1-card-no-invented-3images", "03y_mc_readme.txt", "Use 3 images"),
    # the Qwen card row: that card was never fetched.
    ("aud1-no-qwen-card", "02v_docs_h3.txt", "Qwen2.5-Coder-32B-Instruct"),
    # scoped refutations for tokens that DO occur elsewhere in the corpus: RIFE is in reddit
    # bodies + a Civitai listing, "cfg 1.0" in Civitai listing JSONs, "16GB VRAM" in one
    # Civitai listing, `exclusive: true` in the groups page - none of it in a docs page.
    ("aud1-ls-comfyui-no-rife", "01r_ls_comfyui.txt", "RIFE"),
    ("aud1-ls-comfyui-no-cfg", "01r_ls_comfyui.txt", "cfg"),
    ("aud1-groups-no-taskkill", "agy41_ls_groups.md", "taskkill"),
    ("aud1-docs-no-exclusive", "02v_docs_h3.txt", "exclusive"),
    # The card line map in notes/hc15_start_fidelity_audit.md was written against the 15,125 B card
    # (that file's addendum says `wc -l` = 56; the copy on disk is 3,698 B / 63 lines). These are the
    # sentences that map attributes to the card and are NOT in any copy on disk.
    ("card-no-ultra-mode", "03y_mc_readme.txt", "Ultra Mode"),
    ("card-no-3-images", "03y_mc_readme.txt", "3 images of a character"),
    ("card-no-beta6-chain-line", "03y_mc_readme.txt", "Beta 6 is the 10/3 shift model"),
    ("card-no-12plus-steps", "03y_mc_readme.txt", "12+ steps"),
    ("card-no-bf16-convrot-line", "03y_mc_readme.txt", "quantize to int8 with a convrot"),
    ("card-no-ersde-default-tag", "03y_mc_readme.txt", "(default)"),
    ("card-no-personal-go-to", "03y_mc_readme.txt", "my personal go-to"),
    ("card-no-10eros-max-spaceform", "03y_mc_readme.txt", "10Eros Max"),
    ("card-no-model-spec", "03y_mc_readme.txt", "Model Spec"),
]

# Source refused the fetch this pass; the stamp body is on disk. = unverifiable.
BLOCKED = [
    ("cwb-stars-1", "amirfarzam/CodexBench stars + SKILL.md path",
     "https://api.github.com/repos/amirfarzam/CodexBench -> 401", "04z_codexbench_api.401.txt"),
    ("cwb-skill-file", "cwb2b-minimax-h3-video-prompt/SKILL.md in that repo",
     "raw file 02x_codexbench_skill_raw.txt is NOT on disk", "(no body)"),
    ("tenstrip-concept-loras", "TenStrip/10Eros-Concept-LoRAs-H3 strengths",
     "HF api 401 'Invalid username or password'", "04z_* / 02v_* 401 stamps"),
]

# Tokens that must appear in NO body in notes/web (the AUD1 0-hit list, made a gate).
# `excl` lists Forge-made files (our own extracts/notes saved inside web/), which are not
# community sources and so never count as support for a community claim.
# Five tokens were dropped on 2026-10-27 after this scan FIRED on them: `16GB VRAM` (1
# Civitai listing), `RIFE` (reddit bodies + a Civitai listing + .403 stamps), `cfg 1.0`
# (Civitai listing JSONs), `exclusive: true` (the groups page IS on disk), `simple motion`
# (a Civitai listing). Those claims are now file-scoped BANNED rows, which is the honest
# shape: "not in the page the audit cited", not "in no body anywhere".
GLOBAL_ABSENT = [
    ("g-lowvram", "lowvram", ()),
    ("g-20gb", ">20GB", ()),
    ("g-qwen-card", "Qwen2.5-Coder-32B-Instruct", ()),
    ("g-top-p-095", "top_p 0.95", ()),
    ("g-350-500-words", "350-500 words", ()),
    ("g-120-1200", "120-1200", ()),
    ("g-unload-delay", "unload_delay", ()),
    ("g-vram-reserve-mib", "vram-reserve-mib", ()),
    ("g-max-context", "--max-context", ()),
    ("g-kv-int8", "--kv int8", ()),
    ("g-spec-min-p", "--spec-min-p", ()),
    ("g-taskkill", "taskkill", ()),
    ("g-localhost-proxy", "127.0.0.1:3489", ()),
    ("g-total-timeout", "totalTimeout", ()),
    ("g-context-throttle", "contextThrottle", ()),
    ("g-card-topk", "topk 0.1", ()),
    ("g-card-video-only", "video-only ON", ()),
    ("g-invented-smarter", "much smarter", ()),
    ("g-invented-modelsampling", "ModelSamplingModelPatch", ()),
    ("g-invented-3images", "Use 3 images of the character", ()),
    # Cited by notes/plans/aud1-citation-repair.md as `notes/web/pq1_tenstrip_d27_text.txt:12` (HF discussion
    # #27). That file is not on disk, and neither sentence is in any of the 1,146 bodies: a citation of a body
    # that is not on disk is a fault, not a quotation (AGENTS.md L4).
    ("g-d27-no-euler-line", "euler + simple 6/8 steps", ()),
    ("g-d27-no-convergence-line", "res_multistep is for faster convergence", ()),
]

# Seeded failures for --selftest: every detector here MUST fire.
SELFTEST_CITES = [
    ("st-missing-file", "02x_definitely_not_saved.json", "stargazers"),
    ("st-missing-text", "03y_mc_readme.txt", "ZZZ phrase that is not in any body ZZZ"),
]
SELFTEST_BANS = [("st-ban-must-fire", "02v_lightx2v_pe_readme.txt", "T2VA")]
# a token that IS all over the corpus: the global-absence detector MUST fire on it.
SELFTEST_GLOBAL = [("st-global-must-fire", "res_multistep", ())]


def find_lines(fname: str, phrase: str):
    """Return ('file', []) if the body is absent, else ('lines', [lineno, ...])."""
    path = WEB / fname
    if not path.is_file():
        return "file", []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "lines", [i + 1 for i, ln in enumerate(lines) if phrase in ln]


def all_bodies():
    """{name: text} for every saved body in notes/web (.txt/.md/.json/.html)."""
    out = {}
    for p in WEB.iterdir():
        if p.suffix in (".txt", ".md", ".json", ".html"):
            out[p.name] = p.read_text(encoding="utf-8", errors="replace")
    return out


def scan_global(items) -> int:
    """Tokens that must be in NO body. Probe-only: reads bodies, prints, mutates nothing."""
    texts = all_bodies()
    bad = 0
    for lab, tok, excl in items:
        hits = []
        for name, tx in texts.items():
            if name in excl:
                continue
            for i, ln in enumerate(tx.splitlines()):
                if tok.lower() in ln.lower():
                    hits.append((name, i + 1))
                    break
        if hits:
            print("GLOBAL-PRESENT  %-26s token=%r in %d bodies, first %s" % (lab, tok, len(hits), hits[:3]))
            bad += 1
        else:
            print("global-ok  %-24s token=%r absent in %d bodies" % (lab, tok, len(texts)))
    print("global-absence scan: %d tokens over %d bodies, %d problems" % (len(items), len(texts), bad))
    return bad


def run(cites, bans, label="") -> int:
    bad = []
    for lab, fname, phrase in cites:
        kind, hits = find_lines(fname, phrase)
        if kind == "file":
            print("MISSING-FILE  %-28s %s" % (lab, fname)); bad.append(lab)
        elif not hits:
            print("MISSING-TEXT  %-28s %s phrase=%r" % (lab, fname, phrase[:46])); bad.append(lab)
        else:
            print("ok  %-28s %s:%s" % (lab, fname, ",".join(map(str, hits[:4]))))
    for lab, fname, phrase in bans:
        kind, hits = find_lines(fname, phrase)
        if kind == "file":
            print("MISSING-FILE  %-28s %s (ban body absent)" % (lab, fname)); bad.append(lab)
        elif hits:
            print("BAN-HOLDS     %-28s %s:%s phrase=%r" % (lab, fname, ",".join(map(str, hits[:4])), phrase[:40])); bad.append(lab)
        else:
            print("ban-ok  %-24s %s phrase=%r absent" % (lab, fname, phrase[:40]))
    print("\n%schecked %d citations + %d bans, %d problems" % (label, len(cites), len(bans), len(bad)))
    if bad:
        print("failed: " + ", ".join(bad))
    return len(bad)


# Every web/<file> token written in our audit docs must be a body that exists on disk.
# The curated CITES list only proves what I chose to quote; prose accumulates. In this
# pass 7 dead tokens (02v_docs_fastvideo.txt, 02v_lightx2v_readme.txt, 02v_pack_readme.txt,
# 02v_minimax_base_video_prompt_base_en.txt, 02x_minimax_video_prompt_ref_en.txt,
# 02x_gh_search.json, 02x_codexbench_skill_raw.txt) sat in the inventory citing files that
# were never saved - the curated list said "0 problems". This scan closes that hole.
# The two audit docs AUD1 is about: a citation of a body that is not on disk is a named
# failure there too, not only in the claim inventory.
SCAN_DOCS = [
    "ali02_claim_inventory_20261025.md",
    "self_setup_20261023.md",
    "ali02_self_setup_rows_a.py",
    "ali02_self_setup_rows_b.py",
    "ali02_self_setup_rows_c.py",
    "progress_0.2.md",
    "cf1_setup_audit_20261024.md",
    "hc15_start_fidelity_audit.md",
]
CITE_RE = re.compile(r"(?:notes/)?web/[\w.\-]+\.(?:json|html|txt|md)")
SEED_DOC = "00zz_seed_doc_must_not_exist.md"
SEED_TOKEN = "web/00zz_seed_body_must_not_exist.json"


def scan_docs(doc_paths=SCAN_DOCS, extra_tokens=()) -> int:
    """Cite-token existence scan. Probe-only: reads docs, checks web/, mutates nothing."""
    bad = []
    total = 0
    for name in doc_paths:
        p = Path(__file__).resolve().parent / name
        if not p.is_file():
            print("DOC-MISSING      %-30s (audit doc not on disk)" % name)
            bad.append("DOC " + name)
            continue
        toks = sorted(set(CITE_RE.findall(p.read_text(encoding="utf-8", errors="replace"))))
        total += len(toks)
        for tok in toks:
            if not (WEB / tok.split("/")[-1]).is_file():
                print("AUTO-CITE-MISSING %-25s cited by %s" % (tok, name))
                bad.append("AUTO " + tok)
    for tok in extra_tokens:
        if not (WEB / tok.split("/")[-1]).is_file():
            print("AUTO-CITE-MISSING %-25s (seeded fault)" % tok)
            bad.append("AUTO-SEED " + tok)
    print("auto-cite scan: %d tokens over %d docs, %d problems" % (total, len(doc_paths), len(bad)))
    return len(bad)


# ---------------------------------------------------------------- PLAN mode (0.7) --
PLAN_DEF = Path(r"C:/Users/derek/5slock/ralph-community/fix_plan.md")
# repos this agent owns (AGENTS.md: these are the git repos); a cited path inside one must be tracked.
REPOS = ("C:/AI/community", "C:/AI/director", "C:/Users/derek/5slock/ralph-community")
PATH_FWD = re.compile(r"C:/[A-Za-z0-9_./\-]+[A-Za-z0-9_./\-]*")
PATH_BS = re.compile(r"C:\\+[A-Za-z0-9_./\-][A-Za-z0-9_.\\/\-]*")   # "/" in the class: mixed-separator paths are real
TASK_MARK = re.compile(r"^\s*(?:[-*]|\d+\.)\s*\[([ x~])\]")
HEAD_MARK = re.compile(r"^#{1,4} ")
# a row that says the file is gone / empty / never committed is an ABSENT claim, not a promise.
NEG_RES = [r"\bdoes not exist\b", r"\bno such file\b", r"\b0 files\b", r"\b0 hits\b", r"\b0 rows\b",
           r"\bnever committed\b", r"\bnot on disk\b", r"\bnot tracked\b", r"\buntracked\b", r"\bis absent\b",
           r"\bare absent\b", r"\babsent\b", r"\bno mp4\b", r"\bno register\b", r"\bis gone\b", r"\bis deleted\b",
           r"\breleased\b", r"\bno such\b", r"\bnot there\b", r"\bmissing\b", r"\bno file\b"]
# a row that describes a file a running script creates: the file may legitimately not be there between runs.
RUN_RES = [r"\block file\b", r"\btaken by\b", r"\b-acquire\b", r"\bat render time\b", r"\bduring a render\b",
           r"\bwhile a render runs\b", r"\bgate file\b", r"\blive gate\b", r"\bruntime\b"]


def plan_lines(plan_path):
    """The plan as physical lines (split on \n, trailing \r dropped) - see docstring fact 3."""
    return Path(plan_path).read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").split("\n")


def _scrub(s):
    """Printable excerpt: control characters (the eaten-escape bytes) become visible markers."""
    return "".join(ch if ord(ch) >= 32 else "<%02X>" % ord(ch) for ch in s)


def plan_open_rows(lines):
    """[(lineno, text)] for every line owned by an OPEN item: the `- [ ]`/`- [~]` line and its continuation
    lines, up to the next task marker (its open/closed state wins) or any heading (ends the item). Rows under
    a `## Optional` heading are exempt (the loop's own exit rule never reads them)."""
    out, owner, opt = [], None, False
    for i, ln in enumerate(lines):
        if HEAD_MARK.match(ln):
            opt = ln.lstrip("#").strip().lower().startswith("optional")
            owner = None
            continue
        m = TASK_MARK.match(ln)
        if m:
            owner = m.group(1) in " ~"
        if owner and not opt:
            out.append((i + 1, ln))
    return out


def _clean_tok(tok):
    """Normalize one cited path: backslashes to slashes, drop a `:12` line anchor and trailing prose
    punctuation and any trailing slash, drop the bare drive root (a drive root is not an artifact)."""
    t = tok.replace("\\\\", "/").replace("\\", "/")
    t = re.sub(r":\d+(-\d+)?$", "", t)
    t = t.rstrip(".,;:()")
    while t.endswith("**"):
        t = t[:-2].rstrip(".,;:()")
    t = t.rstrip("/")
    if re.fullmatch(r"[A-Za-z]:", t):
        return None
    return t


def sentence_spans(line):
    """[(start, end)] spans covering the line: one span per SENTENCE. A sentence ends at `.`, `;` or `:`
    followed by whitespace, or at a list/heading marker. A span longer than 400 chars is cut at the nearest
    `) ``, ``, `` `, ``, `, ` or `) ` so a claim window stays local. This exists because the plan's rows are
    single physical lines that mix claims: row Q3 states a real ledger, then says a different file is absent 50
    characters later, and a character window (160 chars, then 60 - both measured) calls the ledger an absence
    claim. A claim is a sentence, so the window is the sentence that carries the mention."""
    n = len(line)
    starts = [0] + [m.end() for m in re.finditer(r"(?<=[.;:])\s+", line)]
    starts += [m.end() for m in re.finditer(r"^\s*(?:[-*]|\d+\.)\s+", line, re.M)]
    starts = sorted(set(s for s in starts if 0 <= s <= n))
    spans = list(zip(starts, starts[1:] + [n]))
    out = []
    for s, e in spans:
        if e - s > 400:
            cut = max(line[s:e].rfind(c, 0, 400) for c in (") `", "`, ", ", ", ") "))
            e = s + cut if cut > 80 else e
        out.append((s, e))
    return out


def claim_window(line, spans, pos):
    """The claim text for a mention at `pos`: from the sentence's start (or 60 chars before the mention, if
    that is later) to the sentence's end, never more than 60 chars past the mention. The cap past the mention
    is measured: row Q3's ledger mention sits 15 chars before its sentence ends, and a belt that reached the
    sentence boundary + 60 chars read the NEXT sentence's "is absent" and called the ledger an absence claim.
    Consequence, and the point of the gate: a citation's claim must be IN THE SAME SENTENCE as the citation."""
    lo = max(0, pos - 60)
    for s, e in spans:
        if s <= pos < e:
            return line[min(lo, s):e].lower()
    return line[lo:pos + 60].lower()


COUNT_NEG = re.compile(r"^(?:0|zero|no)\s+(?:rows|files|hits|matches|entries)\b")
SCOPE = re.compile(r"^\W{0,6}\b(?:in|under|for|over|from|against|matching|matches)\b")


def neg_claim(line, win, mpos):
    """True when the sentence around a path mention claims that path is GONE. Two measured false-absence
    classes are excluded, both read off real rows of this plan: a SCOPED search result - "has 0 hits in
    <path>" (row 2.4) and "0 files matching <id>" (row Q2) report what a SEARCH returned, not the cited file;
    and a count sitting before the mention with a scope word between them ("grep -l X in that repo = 0 rows.
    <path>") is about the pattern. A bare claim ("0 files.", "no such file on disk", "is absent", "does not
    exist") is the absence this gate exists to keep honest."""
    for r in NEG_RES:
        for m in re.finditer(r, win):
            if not COUNT_NEG.match(m.group(0)):
                return True
            if m.end() <= mpos:
                if not SCOPE.search(win[m.end():mpos]):
                    return True
            elif not SCOPE.search(win[m.end():]):
                return True
    return False


def plan_cites(lines):
    """[(path, lineno, cls, excerpt)] for every path cited by an OPEN row. cls = POSITIVE / ABSENT / RUNTIME,
    read from the sentence that carries that mention (see sentence_spans()): a row of this plan is one physical
    line that can name a real artifact, a denied file and a runtime lock in the same breath, so a per-line
    classifier mis-classes everything on it (measured on the real plan: 20 problems, 17 of them invented by the
    coarse rule). No claim marker in the sentence = POSITIVE: the row treats the path as an artifact to read."""
    out = []
    for n, ln in plan_open_rows(lines):
        spans = sentence_spans(ln)
        hits = [(m.start(), m.end(), _clean_tok(m.group(0))) for m in PATH_FWD.finditer(ln)]
        hits += [(m.start(), m.end(), _clean_tok(m.group(0))) for m in PATH_BS.finditer(ln)]
        seen = {}
        for s, e, t in hits:
            if not t:
                continue
            win = claim_window(ln, spans, s)
            cls = "POSITIVE"
            if any(re.search(r, win) for r in RUN_RES):
                cls = "RUNTIME"
            elif neg_claim(ln, win, s):
                cls = "ABSENT"
            if repo_of(t) and os.path.normpath(t).lower() == os.path.normpath(repo_of(t)).lower():
                cls = "POSITIVE"      # a repo root is an existence claim, never an absence claim
            seen.setdefault(t, cls)
        for t, cls in sorted(seen.items()):
            out.append((t, n, cls, _scrub(ln.strip())[:110]))
    return out


def repo_of(path):
    p = str(path).replace("\\", "/").lower()
    for r in REPOS:
        if p == r.lower() or p.startswith(r.lower() + "/"):
            return r
    return None


def is_tracked(path):
    """True when git lists the path (file or directory prefix) in the repo that owns it. Outside an owned
    repo there is no tracking rule (ComfyUI's install, C:/AI/locks, the 5slock tree), so True = 'no rule'."""
    r = repo_of(path)
    if not r:
        return True
    rel = os.path.relpath(str(path), r).replace(os.sep, "/")
    try:
        out = subprocess.run(["git", "-C", r, "ls-files", "--", rel], capture_output=True, text=True,
                             timeout=60)
    except Exception as e:
        print("PLAN-PATH-GITERROR %s: %s" % (path, e))
        return False
    return bool(out.stdout.strip())


def ignore_rule(path):
    """`git check-ignore -v` for a path in an owned repo: 'file:line:pattern <TAB> path' when the repo declares
    the path ignored, else ''. A gitignored runtime tree (logs/, runs/, .venv/, incoming/, p7/jobs/) is absent
    from git BY DESIGN (L1: .gitignore ignores logs/ at any depth), so a citation of one is reported, never a
    failure - the L8 class is a file a pass NEEDS durable and is not tracked, which is what PLAN-PATH-UNTRACKED
    means."""
    r = repo_of(path)
    if not r:
        return ""
    rel = os.path.relpath(str(path), r).replace(os.sep, "/")
    try:
        out = subprocess.run(["git", "-C", r, "check-ignore", "-v", "--", rel], capture_output=True,
                             text=True, timeout=60)
    except Exception:
        return ""
    return out.stdout.strip().split("\t")[0] if out.returncode == 0 else ""


def plan_check(plan_path=PLAN_DEF, label=""):
    """The gate: every path cited by an OPEN plan row exists (and, in an owned repo, is tracked); every
    ABSENT-claim path stays absent; every RUNTIME path's directory exists. Probe-only: reads, prints, writes
    nothing. Returns the number of problems."""
    plan_path = Path(plan_path)
    if not plan_path.is_file():
        print("PLAN-NO-PLAN %s is not on disk" % plan_path)
        return 1
    lines = plan_lines(plan_path)
    cites = plan_cites(lines)
    if not cites:
        print("PLAN-NO-CITES %s: 0 paths cited by open rows - the gate read nothing, so it proves nothing"
              % plan_path)
        return 1
    bad = []
    for path, n, cls, excerpt in cites:
        p = Path(path)
        ex = p.exists()
        if cls == "ABSENT":
            if ex and p.is_dir():
                print("plan-absent-dir   L%-3d %s is a directory the row points at while naming a file that is "
                      "not there - the absence claim is about the file, not this directory" % (n, path))
            elif ex and p.is_dir() and not os.listdir(p):
                print("plan-empty-ok   L%-3d %s is an empty tree, which is what the row states" % (n, path))
            elif ex:
                print("PLAN-PATH-RESURRECTED L%-3d %s exists on disk (%d B) while the row says it is gone"
                      % (n, path, p.stat().st_size))
                bad.append((n, path, "resurrected"))
            else:
                print("plan-absent-ok  L%-3d %s is absent as the row states" % (n, path))
        elif cls == "RUNTIME":
            d = p if p.is_dir() else p.parent
            if not d.is_dir():
                print("PLAN-PATH-MISSING L%-3d %s: a runtime path whose directory %s does not exist"
                      % (n, path, d))
                bad.append((n, path, "runtime-dir"))
            else:
                print("plan-runtime-ok   L%-3d %s (dir %s exists; %s on disk now)" % (n, path, d,
                                                                                      "file present" if ex else "file absent"))
        else:
            if not ex:
                print("PLAN-PATH-MISSING L%-3d %s cited as the artifact by an OPEN row and not on disk"
                      % (n, path))
                bad.append((n, path, "missing"))
                continue
            if not is_tracked(p):
                ign = ignore_rule(p)
                if ign:
                    print("plan-gitignored L%-3d %s is not tracked and the repo declares it ignored (%s) - a "
                          "runtime path, never a durable citation" % (n, path, ign))
                    continue
                print("PLAN-PATH-UNTRACKED L%-3d %s exists (%d B) but git lists no file under it in %s"
                      % (n, path, p.stat().st_size if p.is_file() else 0, repo_of(p)))
                bad.append((n, path, "untracked"))
                continue
            print("plan-ok         L%-3d %s exists and is tracked" % (n, path))
    n_open = len(plan_open_rows(lines))
    print("\n%splan path gate: %d open-row lines, %d path citations, %d problems (%d POSITIVE / %d ABSENT / "
          "%d RUNTIME)" % (label, n_open, len(cites), len(bad),
                           sum(1 for c in cites if c[2] == "POSITIVE"),
                           sum(1 for c in cites if c[2] == "ABSENT"),
                           sum(1 for c in cites if c[2] == "RUNTIME")))
    return len(bad)


def _plan_seed(tmp, text):
    p = Path(tmp) / "seed_plan.md"
    p.write_text(text, encoding="utf-8")
    return p


def plan_selftest():
    """Every detector of the plan gate MUST fire on a seeded copy of the real plan (written to a temp dir,
    so the seed never enters the repo), and the real plan must be clean. Returns 0 when that holds."""
    real = plan_lines(PLAN_DEF)
    cites = plan_cites(real)
    if not cites:
        print("SELFTEST ABORT: the real plan yields 0 citations, so no seed can be chosen")
        return 1
    tracked_ok = next((c for c in cites if Path(c[0]).is_file() and repo_of(c[0]) and is_tracked(c[0])), None)
    real_problems = plan_check(PLAN_DEF, label="real plan (baseline) ")
    untracked = "C:/AI/community/notes/hc15_audit/ab_seed_00.json"      # measured: on disk, git lists 0 files
    ledger = "C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"  # measured: on disk, .gitignore-declared
    absent = "C:/AI/community/notes/zz_07_seed_path_absent.md"
    if not tracked_ok:
        print("SELFTEST ABORT: no tracked cited path in the real plan to seed against")
        return 1
    fires = {}
    with tempfile.TemporaryDirectory() as tmp:
        # S1: a cited artifact is deleted (the 0.7 fault) -> PLAN-PATH-MISSING
        s = list(real) + ["", "- [ ] **9.9 seed** read the register at `%s` and report it." % absent, ""]
        fires["missing"] = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S1 ")
        # S2: a real tracked file asserted absent -> PLAN-PATH-RESURRECTED
        s = list(real) + ["", "- [ ] **9.9 seed** `%s` is absent, so the step cannot be verified." % tracked_ok[0], ""]
        fires["resurrected"] = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S2 ")
        # S3: an existing UNTRACKED file cited as the artifact -> PLAN-PATH-UNTRACKED
        s = list(real) + ["", "- [ ] **9.9 seed** open `%s` and use the row." % untracked, ""]
        fires["untracked"] = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S3 ")
        # S4: a plan with no citations -> PLAN-NO-CITES (the gate must not look green on nothing)
        s = ["# seed plan", "", "- [ ] **9.9 seed** do the thing with no paths at all.", ""]
        fires["no_cites"] = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S4 ")
        # S5: a RUNTIME row whose directory is gone -> PLAN-PATH-MISSING(runtime-dir)
        s = list(real) + ["", "- [ ] **9.9 seed** the lock file lives at `%s/gpu-render.lock`." % (str(Path(tmp)).replace("\\", "/") + "/no_such_dir"), ""]
        fires["runtime_dir"] = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S5 ")
        # S7: an EMPTY tree reported as empty (the .codex/skills case: 0 files) must NOT fail - the row's claim
        # is "nothing there", so an empty directory satisfies it. Measured: the strict rule failed real rows.
        empty = os.path.join(tmp, "empty_tree")
        os.makedirs(empty, exist_ok=True)
        s = list(real) + ["", "- [ ] **9.9 seed** `%s` is an empty tree: 0 files, so nothing is installed." % empty, ""]
        s7 = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S7 ")
        empty_ok = (s7 - real_problems == 0)
        print("seed S7 (empty tree reported as empty): +%d problems, expected +0: %s"
              % (s7 - real_problems, "ok" if empty_ok else "FIRES - the gate is too strict"))
        # S6: a gitignored runtime path (the budget ledger) must NOT fail: the gate reports it, and the
        #     untracked detector must not fire there - the selftest needs a seed that proves the rule is real.
        s = list(real) + ["", "- [ ] **9.9 seed** read the live ledger at `%s` before any request." % ledger, ""]
        ign_fires = plan_check(_plan_seed(tmp, "\n".join(s)), label="seed S6 ")
        print("seed S6 (gitignored ledger cited as an artifact): %d problems, expected 0" % ign_fires)
    need = {"missing": 1, "resurrected": 1, "untracked": 1, "no_cites": 1, "runtime_dir": 1}
    bad = {k: v for k, v in fires.items() if v < need[k]}
    # S6 is measured as a DELTA over the real plan: appending a gitignored citation must add no problem.
    if ign_fires - real_problems != 0:
        bad["gitignore_rule"] = ign_fires - real_problems
    if not empty_ok:
        bad["empty_tree_rule"] = 1
    print("\nplan selftest: seeds fired %s, required %s" % (fires, need))
    if bad:
        print("SELFTEST FAILED: seeds did not fire: " + ", ".join(sorted(bad)))
        return 1
    if real_problems:
        print("SELFTEST: seeds all fire, but the REAL plan carries %d problem(s) - fix the plan" % real_problems)
        return 1
    print("plan selftest ok: PLAN-PATH-MISSING, PLAN-PATH-UNTRACKED, PLAN-PATH-RESURRECTED, "
          "PLAN-NO-CITES and the runtime-dir seed all fire; 0 on the real plan")
    return 0


def main() -> int:
    if "--plan-selftest" in sys.argv:
        return plan_selftest()
    if "--plan" in sys.argv:
        return 1 if plan_check(PLAN_DEF) else 0
    if "--selftest" in sys.argv:
        n = run(SELFTEST_CITES, SELFTEST_BANS, label="selftest (must fail 3): ")
        s = scan_docs(doc_paths=[SEED_DOC], extra_tokens=[SEED_TOKEN])
        g = scan_global(SELFTEST_GLOBAL)
        if n != 3 or s < 2 or g != 1:
            print("SELFTEST FAILED: cite/ban fired %d of 3, scan detectors %d of 2, global fired %d of 1"
                  % (n, s, g))
            return 1
        print("selftest ok: MISSING-FILE, MISSING-TEXT, BAN-HOLDS, DOC-MISSING, AUTO-CITE-MISSING, "
              "GLOBAL-PRESENT all fire")
        return 0
    for lab, what, why, stamp in BLOCKED:
        print("BLOCKED  %-24s %s | %s | body: %s" % (lab, what, why, stamp))
    plan_problems = plan_check(PLAN_DEF)
    n = run(CITES, BANNED) + scan_global(GLOBAL_ABSENT) + scan_docs() + plan_problems
    print("unverifiable (blocked) this pass: %d" % len(BLOCKED))
    print("plan path gate (fix_plan.md): %d problem(s) - seeded selftest: python %s --plan-selftest"
          % (plan_problems, sys.argv[0]))
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
