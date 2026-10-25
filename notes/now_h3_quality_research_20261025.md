# NOW (Derrick 2026-10-24 8:28 PM CT "do research and improve") - community H3 quality settings vs the fixed clip-1 graph

Deliverable for the NOW item, pass 1 (research half). No render, no arm, no queue, no GPU call, no vision judge,
no KEEP, no prompt change, no graph change in this pass. The graph switch set below is specified, not applied;
the builder pass is the next item (`fix_plan.md` NOW-P1).

## 0. Artifact under audit

- Graph: `C:/AI/community/p7/graphs/ali163_hc15_bd002_s51150011.api.json`, sha256
  `8a57ebbf456b6f9d74ad1ca2424076041e8ad0c524d15f7f8a7c9a126a57e769` (measured `certutil -hashfile`, matches `notes/hc15_start_fidelity_audit.md`), 27 nodes.
- Model identity is verifiable on disk: local `ComfyUI/models/diffusion_models/10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`
  = 21,709,633,539 bytes == the published size in `notes/web/02v_mc_api.json` (`id: TenStrip/10Eros-Max`, lastModified
  2026-10-13T09:03:34Z, likes 866) - a byte-size integrity match, printed by
  `python C:/Users/derek/AppData/Local/Temp/forge/probe_files.py` (throwaway probe, not a repo script).
- `vae/minimax_h3_video_vae_int8_convrot.safetensors`, `vae/minimax_h3_audio_vae_fp32.safetensors`,
  `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` are the exact filenames published by
  `Comfy-Org/MiniMax-H3` (`notes/web/02x_comfyorg_h3_api.json`, 25,532,380 downloads).
- Live node schema used for "does the node exist / what are its published defaults" =
  `C:/AI/community/notes/ali173_b2_object_info_full.json` (2,605 classes; a real `/object_info` dump from this box).
- Published-source corpus = `C:/AI/community/notes/web` (171 valid JSON bodies; `scripts/check_web_saves.py` = CLEAN).

## 1. Divergence table (every setting audited; verdict per row)

`MATCH` = graph already equals a published value. `SWITCH` = graph diverges, published value is reachable on this box.
`BLOCKED` = published value needs a file/node not installed here (sizes/names measured). `GAP` = no published value found.

| # | setting (node.key) | clip-1 graph | published value | verbatim quote (<=25 words) | saved body | URL | verdict |
|---|---|---|---|---|---|---|---|
| 1 | s0_sched.steps / s1_sched.steps | 8 / 8 | **12** (TenStrip 8-12 band for this file; ComfyUI docs: audio needs 12+) | "It's a slow 8-12 step reference model in that configuration, use LCM to get good audio." / "Speech and timbre need **12+** steps; at **8** steps audio is often the weak link." | `hc15_tenstrip_readme.txt` / `02v_docs_h3.txt` | huggingface.co/TenStrip/10Eros-Max/raw/main/README.md ; docs.comfy.org/tutorials/video/minimax/minimax-h3.md | SWITCH |
| 2 | c0.ref_image_size / c1.ref_image_size | `max` | **`match`** (node default; `max` is for 2048px refs, ours are 1024x1024) | "**`max`** keeps 2048px short edge and is much slower; it does not upscale small files (round sides to 32)." | `02v_docs_h3_native.txt` | docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md | SWITCH |
| 3 | m_attn.attention | `comfy kitchen attention` on an int8_convrot file | **`pytorch attention`** (schema default) for an int8 build; CK is documented as int8_convrot-incompatible | "**Comfy Kitchen attention cannot run `int8_convrot` checkpoints**; use a `bf16` build with that backend." | `02v_docs_h3.txt`, `03y_issue15529.html`, schema default in `ali173_b2_object_info_full.json` | docs.comfy.org/tutorials/video/minimax/minimax-h3.md ; github.com/Comfy-Org/ComfyUI/issues/15529 (title + "fixed") | SWITCH |
| 4 | new `lora_antiburn` on the continuation model path | no LoRA at all | `h3_antiburn_universal_v1.safetensors` at `strength_model` **0.5**, "on clips after the first" | "For longer chains, H3-Anti-Burn-LoRA ... on clips after the first at `strength_model` \~0.5 (tune for your continuation style)." | `02v_docs_h3.txt`, `02v_antiburn_readme.txt` | docs.comfy.org/tutorials/video/minimax/minimax-h3.md ; huggingface.co/Imagineer13/H3-Anti-Burn-LoRA | SWITCH (add) |
| 5 | m_shift.shift_video / shift_audio | 10.0 / 3.0 | 10 / 3 for beta6 ("required"), FastH3 template 10/3 | "b6 runs with 10/3 shift, 10 video shift while the normal model and b5 run 12. That's not suggested, it's required." | `_disc_10eros.txt`, `02v_docs_h3.txt`, `02v_docs_h3_fastvideo.txt` | huggingface.co/TenStrip/10Eros-Max/discussions/61 ; minimax-h3-fastvideo.md | MATCH |
| 6 | ksel.sampler_name | `res_multistep` | `res_multistep` + `simple` (templates) ; TenStrip "go-to" | "Templates use **`res_multistep`** + **`simple`**." / "res_multistep/simple 6-8 steps (my go-to for best motion quality)" | `02v_docs_h3.txt`, `hc15_tenstrip_readme.txt` | minimax-h3.md ; TenStrip/10Eros-Max README | MATCH (see §3.5 for the LCM row) |
| 7 | scheduler / denoise | `simple` / 1.0 | `simple`; 1.0 generation (0.1-0.5 is refine-only) | "Treat refine as partial denoise: `denoise` **0.1–0.5** keeps composition" | `02v_docs_h3.txt` | minimax-h3.md | MATCH |
| 8 | m_vsa.selection | `vsa` | `vsa` requires FastH3/fastv2 weights; beta6 = fastv2 turbo baked in, "Fastv2 VSA sparse node settings" | "beta_6 is a built mostly-reference hybrid with a custom turbo ... Samples on 10/3 shift, fully dense or with Fastv2 VSA sparse node settings" | `hc15_tenstrip_readme.txt`, `02v_docs_h3.txt` | TenStrip/10Eros-Max README ; minimax-h3.md ("FastH3 uses `vsa` at `keep_percent` 10") | MATCH |
| 9 | m_vsa.selection.keep_percent | 10 | 10 | "Runs Video Sparse Attention (VSA) with `keep_percent` 10 starting at 20% of the schedule" | `02v_docs_h3_fastvideo.txt` | minimax-h3-fastvideo.md | MATCH |
| 10 | m_vsa.start_percent / end_percent | 0.2 / 1.0 | 0.2 / 1.0 (schema defaults); docs: 0.4 / 0.9 protect opening/closing frames | "Defaults `start_percent` **0.2**, `end_percent` **1.0**. Later start (0.4) and earlier end (0.9) protect opening/closing frames." | `02v_docs_h3.txt`, schema defaults | minimax-h3.md | MATCH (optional hardening 0.4/0.9, not switched: speed cost) |
| 11 | m_vsa.min_tokens / extra_tokens / dense_blocks | 12288 / 256 / "" | schema published defaults 12288 / 256 ("256 recommended", "Ignored for VSA") / "" | "Sequences shorter than this stay dense." default 12288; "256 recommended, 0 disables. Ignored for VSA." | `ali173_b2_object_info_full.json`, `02v_docs_h3.txt` | live /object_info ; minimax-h3.md | MATCH |
| 12 | m_vsa.sink_conditioning | `exact_kv_and_rows` | `exact_kv_and_rows` (schema default + docs) | "Keep **`sink_conditioning`** at **`exact_kv_and_rows`** on H3 (protects packed text/audio/reference rows)." | `02v_docs_h3.txt`, schema | minimax-h3.md | MATCH |
| 13 | (no node) cache / spectrum | none | none when doing reference | "No cache or spectrum if doing reference, they cause accuracy loss." | `hc15_tenstrip_readme.txt` | TenStrip/10Eros-Max README | MATCH (compliant by absence) |
| 14 | (no node) SLA sparsity | not used | avoid on this model | "SLA sparsity seems to destroy it, avoid using that on any workflows." | `hc15_tenstrip_readme.txt` | TenStrip/10Eros-Max README | MATCH (compliant by absence) |
| 15 | c0.length / width / height | 243 / 1344 / 768 | trained 124-362 frames; 0.98 MP = 1344x768, avoid 1.0 MP; grid 17k+5 | "For 16:9 native quality, set **0.98** (\~1344×768) ... Avoid **1.0** MP (1376×768 exceeds the 768×1344 cap)." | `02v_docs_h3.txt`, `02v_docs_h3_native.txt` | minimax-h3.md / -native.md | MATCH |
| 16 | win1.overlap_frames / extension_frames | 22 / 119 | schema published defaults 22 / 119 (17k+5 / multiple of 17) | "Hidden motion-context span; must satisfy 17k + 5." default 22; "New visible frame count; must be a multiple of 17." default 119 | `ali173_b2_object_info_full.json` | live /object_info | MATCH |
| 17 | total clip length 362 f = 15.08 s | at the top of the trained range | trained ~124-362 f (~5-15 s); chaining advice | "Trained range | \~124–362 frames (\~5–15 s)" ; "Beyond the trained range, chain I2V continuations from each clip's last frame." | `02v_docs_h3.txt` | minimax-h3.md | MATCH (at ceiling; no third window) |
| 18 | g0.frame_idx (guide anchoring) | 0 only | guides are published at any frame_idx; published mid-clip recipe | "Example: first **22** frames of a clip at frame **0** continues both streams; a still at frame **60** forces the shot through that pose." | `02v_docs_h3_native.txt` | minimax-h3-native.md (#15439) | GAP for our figures (needs a named mid-clip keyframe = the blocked TOP naming row); NOT switched |
| 19 | unet.weight_dtype | `default` | read quantization from the checkpoint | "Change only the `UNETLoader` file; ComfyUI reads quantization from the checkpoint." | `02v_docs_h3.txt` | minimax-h3.md | MATCH |
| 20 | clip CLIPLoader (file/type/device) | nvfp4_awq / `minimax` / `default` | same file + type `minimax`; device has no published value | "text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`, type `minimax`" | `02x_comfyorg_h3_api.json`, `02x_cont_turbo_sample.txt` | huggingface.co/Comfy-Org/MiniMax-H3 ; Continuum V3.9 doc | MATCH (device = GAP) |
| 21 | 16 GB quantization class | int8_convrot class, 21.7 GB file on a 16 GB card | docs: `pruned_w6a8` = 16 GB (ComfyUI 0.38.0+); "step down a size" before offload | "Pick the smallest build that fits in VRAM." ; "If VRAM is tight, step down a size: CPU offload costs more than precision tradeoffs." | `02v_docs_h3.txt`, `now_int8convrot_readme.txt` | minimax-h3.md ; huggingface.co/cicalooo/10Eros-Max-h3-int8-convrot | KEEP (the file's author targets 16 GB with this exact file; switching model file is out of scope for a render) |
| 22 | sharpness path (upscaler / interpolation / sharpen) | none (native 1344x768 SaveVideo) | latent upscaler on the 24-ch video latent, refine `denoise` 0.1-0.5; TenStrip 2160p60 = `10Eros_Max_h3_hybrid_beta5_ref2va_2160p60fps.safetensors` + ComfyUI-Video-Postprocessing (NVRLutCustom, STG, interpolator, sharpening) | "Use a **latent upscaler** on the 24-channel video latent to avoid VAE round-trip ghosting." ; "Requires the 2160p60fps model file, and the ComfyUI-Video-Postprocessing nodes, with NVRLutCustom, STG, the interpolator and a touch of sharpening." | `02v_docs_h3.txt`, `hc15_tenstrip_readme.txt` | minimax-h3.md ; TenStrip/10Eros-Max README | BLOCKED this pass: the 2160p60 file is not in `models/diffusion_models` (measured) and no `ComfyUI-Video-Postprocessing` in `custom_nodes` (measured); latent-upscaler nodes exist (`ComfyUI-MiniMaxH3_LatentUpscaler`, `ComfyUI-H3-Latent-Upscaler-Mamad8`) = a second pass + ~2x time, so it is its own item (NOW-P3) |
| 23 | concept/anatomy LoRAs | none | published stacking strengths for concept LoRAs on this model | "usually needing lower strength 0.2-0.6" ; "Style LoRAs: Compete with references; use low strength (\~**0.5**) on base schedule when adherence matters" | `hc15_tenstrip_readme.txt`, `02v_docs_h3_native.txt` | TenStrip/10Eros-Max README ; minimax-h3-native.md | DEFERRED: the LoRA files in `models/loras` are unattributed by subject (gate 4: no real people) and 0 renders per pass forbids stacking two variables at once |
| 24 | prompt structure / figure description | six-section prose with `subject_definitions` naming figures by hair/photo position | official prompt guide + 350-500 word rule + `<Picture N>` role assignment | "Tags: Reference inputs as `<Picture 1>` ... Assign roles: Say which reference drives identity, style, motion, camera, or voice" | `02v_docs_h3_native.txt`, `notes/prompt_guide_20261024.md` | minimax-h3-native.md ; minimax-h3-prompt-guide.md | NOT this item (the subject-label rewrite = the 2026-10-25 naming item; prompts stay byte-identical) |
| 25 | audio loudness / post | as generated (aac, no normalization) | leave it low and realistic | "the loudness in the videos you make will be lower and more realistic, if you want to raise it that's your call" | `hc15_tenstrip_readme.txt` | TenStrip/10Eros-Max README | MATCH (no post-processing = published) |
| 26 | ComfyUI version gate | box reports 0.19.2 (AGENTS.md) | templates 0.30.0+; Multiframe 0.34.0+; sparse attention + Model Attention Backend 0.35.0+; FastH3 0.36.0+; `pruned_w6a8` 0.38.0+ | "base T2V/I2V/R2V templates need **0.30.0+**; ... sparse attention, and Model Attention Backend **0.35.0+**; FastH3 **0.36.0+**" | `02v_docs_h3.txt` | minimax-h3.md | MEASURE ROW: the live graph contains `ModelAttentionBackend`, `BlockSparseAttention`, `MiniMaxH3AddGuide`, `MiniMaxH3GuidedContinuationWindow` in the box's own `/object_info` dump, so the features are present; the published version numbers are a naming scheme this box does not report (0.19.2 < 0.30.0). Row = a documentation/version conflict, not a graph fault. |

## 2. Two source-integrity findings (measured in this pass, they gate rows above)

1. `notes/cf1_setup_audit_20261024.md` cites `minimax-h3.md` for launch flags, `BasicGuider` cfg 1.0, RIFE and a
   16 GB resolution row; the saved body `notes/web/02v_docs_h3.txt` contains none of that wording (grep for
   `--lowvram`, `RIFE`, `cfg` = 0 hits in the saved body; `--use-ck-attention` is the only flag it publishes).
   Reproduce: `grep -n -i -E "lowvram|RIFE|cfg" C:/AI/community/notes/web/02v_docs_h3.txt` (0 hits).
2. `notes/hc15_start_fidelity_audit.md` quotes the TenStrip card for "topk 0.1-0.2", "video-only ON", "Do not use
   SLA sparsity with reference workflows", "euler is for simple motion and faster tests" - none of those strings is
   in the saved card README (the card says "SLA sparsity seems to destroy it, avoid using that on any workflows."
   and "No cache or spectrum if doing reference"). Reproduce:
   `grep -n -i -E "topk|video-only|euler is for" C:/AI/community/notes/web/hc15_tenstrip_readme.txt` (0 hits).
   Consequence: rows 11/14 above use the card's real wording; `topk` is NOT a published key of
   `BlockSparseAttention` in this build (its per-method keys are `tau` for sol-attn, `keep_percent` for sla).

## 3. Decision log for the four switches (the published value, exactly as published)

1. **steps 8 -> 12** on `s0_sched` and `s1_sched`. Two independent published sources (rows 1). The clip-1 audit's
   frame-0 problem is fixed (SSIM 0.915); what the community calls out at 8 steps is audio quality and fine detail.
2. **ref_image_size `max` -> `match`** on `c0`/`c1`. Published default is `match`; `max` buys nothing for 1024x1024
   refs (it "does not upscale small files") and is "several times slower" (node tooltip). Keeps the run inside the
   12-step budget.
3. **attention `comfy kitchen attention` -> `pytorch attention`** on `m_attn` (schema default). The checkpoint is
   `int8_convrot` (published incompatibility, row 3). If the box's 0.19.2 build crashes on this pair, the run fails
   loudly at step 0 (issue #15529) - and the clip-1 render did complete with CK+int8, so this switch is a
   documented-compatibility change whose quality effect is the open question the A/B answers.
4. **Add `lora_antiburn` = `LoraLoader(h3_antiburn_universal_v1.safetensors, strength_model 0.5)` between `m_shift`
   and `s1_guide`/`s1_sched` only** (published placement "on clips after the first", published strength ~0.5).
   File is installed: `ComfyUI/models/loras/h3_antiburn_universal_v1.safetensors` (measured) and it appears in the
   live `LoraLoader.lora_name` list (measured from `/object_info`).
5. **Not switched, recorded:** `lcm` sampler (TenStrip "use LCM to get good audio" vs official docs
   "Templates use `res_multistep` + `simple`" + the docs' 12+ step audio rule, which switch 1 satisfies; one sampler
   serves video AND audio here, so an LCM switch would move two variables at once). Also not switched:
   `start/end_percent` 0.4/0.9, `topk` (not a published key in this build), CFG (no CFG key exists in the graph at
   all), and any Continuum-only sampler (its sampler has no negative/CFG per AGENTS.md).

## 4. Self-check plan the builder pass must ship (no green check that cannot fail)

- Extend `C:/AI/community/notes/hc15_anchor_fix_build.py` (no new builder scripts): it writes
  `p7/graphs/ali163_hc15_bd002_s51150021.api.json` = clip-1 bytes + exactly the 4 switches, and the byte-identical
  `runs/ali163_hc15_bd002_s51150021/request.api.json`.
- `diff_paths(new, clip11)` MUST equal exactly `{s0_sched.steps, s1_sched.steps, c0.ref_image_size, c1.ref_image_size,
  m_attn.attention, +lora_antiburn node + its 2 edges (s1_guide.model, s1_sched.model)}`; prompts must be byte-identical.
- Schema gate: every `class_type` present in `ali173_b2_object_info_full.json`; every input key present in that
  class's required/optional set (the static-check pattern of `notes/ali163_hc_r4g2_build.py` check 11).
- Seed probes (each MUST fire on a seeded fault, 0 on the real artifact): revert steps to 8; revert ref_image_size
  to `max`; revert attention to `comfy kitchen attention`; drop the LoRA node; add a `topk` key; change one prompt
  char; renumber the graph id (rendered-file gate).
- `comm.guard_ok` truthy for every prose string (prompts unchanged = already allowed by clip-1).
- `python -m pytest -q C:/AI/community/scripts/tests/test_p6_review.py` = 21 passed;
  `python C:/AI/community/notes/ali02_citation_check.py` clean on this doc.
- Arm gate before any `p7/JOB_REQUEST.json` write: ledger headroom read from
  `C:/Users/derek/5slock/ralph-community/logs/p7_budget.json` (measured this pass: used_min 472.9 / cap_min 615,
  jobs 38 / job_cap 45 = 142.1 min and 7 jobs free; a 12-step 362-frame clip is ~1.5x clip-1, so one job fits, and
  the builder pass must re-read the ledger, not reuse these numbers).

## 5. Render handoff (the GPU window, not a Ralph pass)

`C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/run_graph_job.py C:/AI/community/runs/ali163_hc15_bd002_s51150021 ali163_hc15_bd002_s51150021 --frames 362`
after `gpu_guard.ps1` returns IDLE, same seed 51150001, one job only. Then the before/after sheet is built by the
existing labelled FINAL generators (`notes/ali163_hc_final_check.py` + `notes/ali163_hc_final_sheet.py`): frame-0
SSIM/PSNR + ArcFace on the start still for 51150011 (before) and 51150021 (after), contact sheet, no vision judge.

## 6. Research hygiene for this pass (PROMPT.md rules)

7 fetches, one per URL, no retries: 2 bodies saved
(`notes/web/now_int8convrot_readme.txt` 1,919 B HTTP 200; `notes/web/now_int8convrot_api.json` 1,620 B HTTP 200),
5 blocked stamps (`now_upscaler_readme.401`, `now_conceptlora_readme.401`, `now_turbowf_readme.401`,
`now_bodyswap_readme.401`, `now_turbowf2_readme.404`) = blocked rows, never evidence. `scripts/check_web_saves.py`
= CLEAN (171 json bodies parse). No URL in this pass duplicates the 211-URL index built from the saved corpus.
Subagent fan-out: 3 `researcher` children launched (run `5316264e-7c4f-4671-8028-c2b6a23cb431`); all 3 ended in
failure state (2 x strict tool allowlist asks for `web_search`/`fetch_content`/`get_search_content`/`source_check`
that this session does not register, 1 x 1,800,000 ms timeout). Their research bodies survive on disk
(`sessions/subagent-artifacts/216bc02a-*.md`, `ff8df43f-*.md`) and their quotes were re-verified against the saved
bodies before use in §1. The shipped artifact stayed with the parent.

## 7. NOW-P1 shipped (the builder pass, 2026-10-25) - what is on disk, and the three deltas from §3/§4

Artifact (written by `notes/hc15_anchor_fix_build.py --now-build`, no new scripts, per §4):

- `C:/AI/community/p7/graphs/ali163_hc15_bd002_s51150021.api.json` - 28 nodes (27 + `lora_antiburn`), 18,489 B,
  sha256 `c42a36e9abfc056e8951aac0bc336da6292bc07af1260f741e13b739afa5829e`, indent=2 + CRLF + no trailing newline
  (the byte format of the base, measured by check 12). Base = the RENDERED clip-11
  `ali163_hc15_bd002_s51150011.api.json`, 18,235 B, sha256
  `8a57ebbf456b6f9d74ad1ca2424076041e8ad0c524d15f7f8a7c9a126a57e769`, 27 nodes, rendered in 571.7 s wall.
- `C:/AI/community/runs/ali163_hc15_bd002_s51150021/request.api.json` - byte-identical to the graph (measured).
- `C:/AI/community/p7/JOB_REQUEST.json` - re-armed: top level `id` / `api` / `run_dir` / `frames` 362 / `minutes` 20
  and `jobs[]` = one row with exactly the 6 keys `id, kind, frames, frames_tol, minutes, note`, all naming the new id.
- Builder modes added to the existing file: `--now-build`, `--now-check` (13 named detectors), `--now-selftest`
  (37 seeded faults), `--now-sheet` (labelled frame-0 before/after sheet, ffmpeg + PIL, no vision judge).

Measured switch values on the new graph, each read against the box's own `/object_info` dump
(`notes/ali173_b2_object_info_full.json`), the only source the schema gate uses:

| node | clip-11 | new | live schema |
| --- | --- | --- | --- |
| `s0_sched.steps` / `s1_sched.steps` | 8 | 12 | INT; published band 8-12 for this file (`notes/web/hc15_tenstrip_readme.txt:16` "It's a slow 8-12 step reference model in that configuration") |
| `c0.ref_image_size` / `c1.ref_image_size` | `max` | `match` | options `['match','max']`, default `match` |
| `m_attn.attention` | `comfy kitchen attention` | `pytorch attention` | options `['pytorch attention','comfy kitchen attention']`, default `pytorch attention` |
| `lora_antiburn` | absent | `LoraLoaderModelOnly` (`model` <- `m_shift`, `lora_name` = `h3_antiburn_universal_v1.safetensors`, `strength_model` 0.5) feeding `s1_guide` + `s1_sched` | required keys exactly `['model','lora_name','strength_model']`; the file is in the live `lora_name` list and installed on disk |

Prompts are byte-identical to clip-11 (`c0.prompt` sha256 `ed90eb1c0bbc6137080e632f`, `c1.prompt`
`389a3402017dcdf3ebe11857`) and `noise_seed` stays 51150001, so the render A/B against clip-11 moves the four
switches and nothing else.

§4's allowed-diff set is 8 paths; the shipped gate is 9. The three deltas, each decided by published wording:

1. **`save.filename_prefix` joined the allowed set.** §4 lists only the four switch paths + the new node + its 2
   edges. `filename_prefix` IS the output folder (`community/<id>/<id>`), so an unchanged prefix would write the new
   clip into `community/ali163_hc15_bd002_s51150011/`, the folder of the RENDERED before clip, and the id-free gate
   (`p7/jobs/<id>.result.json` + `ComfyUI/output/community/<id>/*`) could never be satisfied. It is a naming path, not
   a sampling path, and detector 5 names it in the allowed set. Seed N24 (prefix back to the rendered clip-11 folder)
   fires detectors 5 and 11.
2. **`LoraLoaderModelOnly`, not `LoraLoader`.** The LoRA's own README is the published wiring -
   `notes/web/02v_antiburn_readme.txt:29` "Load it with `LoraLoaderModelOnly` on the model that makes your
   **continuation clips**: 2, 3, 4 and so on.", `:30` "**Don't use it on clip 1.** A first clip has nothing to burn
   from.", `:31` "**Start at 0.5.**", `:83` "LoRA: merged with `LoraLoaderModelOnly` before the turbo."; and
   `notes/web/02v_docs_h3.txt:157` names only "`strength_model` ~0.5". `LoraLoaderModelOnly` requires exactly
   `['model','lora_name','strength_model']` (measured), so it exposes only the published knob. `LoraLoader` also
   requires `clip` + `strength_clip`, and **no published source gives a `strength_clip` value for this LoRA** - taking
   one would be our own setting (the item says "no settings of your own") and would move the CLIP/conditioning path as
   a fifth variable. Seed N13 (`class_type` = `LoraLoader`) fires 4 and 6.
3. **`topk` stays unwritable, confirming §3 item 5.** `BlockSparseAttention` in this build exposes
   `['dense_blocks','end_percent','extra_tokens','min_tokens','model','selection','selection.keep_percent',
   'sink_conditioning','start_percent','verbose']` - no `topk` (measured from the dump; AGENTS.md records that ComfyUI
   0.19.2 dropped `sparse_blocks`/`sparse_size`/`max_dims` from `ModelAttentionBackend`, whose live keys are now only
   `['attention','model']`). §1 row 5's beta6 fast path is therefore only half-writable here: the antiburn LoRA goes
   in, the `topk` value cannot be set at all. Seeds N15 (`topk` on `m_vsa`) and N25 (`min_tokens` moved) fire 5 and 6.

Attention switch grounding, the two published lines that decide it: `notes/web/02v_docs_h3.txt:80`
"**Comfy Kitchen attention cannot run `int8_convrot` checkpoints**; use a `bf16` build with that backend." and
`:201` "Templates use **`int8_convrot`** checkpoints. **Comfy Kitchen does not support them**
([issue #15529](https://github.com/Comfy-Org/ComfyUI/issues/15529)). Use default attention, or switch `UNETLoader` to
**`pruned_bf16`** then change backend." Our unet is `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` (measured off the
clip-11 graph), so `pytorch attention` = the docs' first-listed remedy. Steps grounding: `:176` "Speech and timbre need
**12+** steps; at **8** steps audio is often the weak link." and `:182` "Splitting the schedule across two samplers
drops multistep history: the second sampler's first step is first-order again. Keep one sampler run, or give the second
enough steps to warm up." ref-size grounding: `notes/web/02v_docs_h3_native.txt:218` "**`ref_image_size`**: Default
**`match`** (fit to canvas). **`max`** keeps 2048px short edge and is much slower; it does not upscale small files";
our refs are a 1376x768 start frame and a 512x512 face crop (`c0.ref_images.ref_image_1` -> `img` =
`ComfyUI/input/community/hc/BD002.jpg` measured 1376x768, `ref_image_2` -> `img2` = `community/hc/BD002_w2_face.png`
measured 512x512; there is no `ref_image_3` in this graph), both under the 2048px short edge, so `max` buys no extra
identity detail from these files ("it does not upscale small files") while spending reference tokens that "ride through
every sampling step".

Self-check receipts (this pass, run from `C:/AI/community`):

- `python notes/hc15_anchor_fix_build.py --now-check` = `CHECKS real ALL 13 PASS`.
- `python notes/hc15_anchor_fix_build.py --now-selftest` = `NOW-SELFTEST seeds=37 fired=37 silent=0
  real_problems=0` + `NOW-SELFTEST-CLEAN`. Per-detector coverage (number of seeds that fire each detector) =
  1:4 2:4 3:3 4:9 5:22 6:5 7:4 8:6 9:1 10:6 11:6 12:1 13:1 - every detector fires on at least one seed, so none is
  decoration (L10). Seeds include §4's list verbatim: steps back to 8 (N1), `max` back (N4), `comfy kitchen
  attention` back (N7), LoRA node dropped (N9), a `topk` key added (N15), one prompt char changed (N18), the graph id
  renumbered (N24); plus non-published option strings (N6 `largest`, N8 `sla attention`), strength 1.0 (N10), the LoRA
  on the clip-1 path against README:30 (N11), a real-but-different installed LoRA (N12), the `LoraLoader` class (N13),
  LoRA feeding only the sampler (N14), a dropped required input (N16), an unknown class (N17), the full clip-11 clone
  as the before artifact (N36), a minor-token prompt so the fiction gate must deny (N37), `cfg` injected (N33 -
  AGENTS.md: this graph has no cfg key at all), handoff drift (N26-N31), ledger over budget (N29), byte drift (N32),
  a stale frame-0 sheet (N35), and anchor/canvas/shift/window geometry (N20-N23).
- `python -m pytest -q C:/AI/community/scripts/tests/test_p6_review.py` = `21 passed in 3.06s`.
- `python C:/AI/community/notes/ali02_citation_check.py` = `checked 87 citations + 7 bans, 0 problems`; auto-cite
  scan 120 tokens over 6 docs, 0 problems; 3 blocked (401/404) this pass, used as blocked rows only.
- `python C:/AI/community/scripts/check_web_saves.py` = `CLEAN: C:/AI/community/notes/web - every *.json parses
  (json.tool-safe), 171 checked`.
- Ledger re-read this pass (not reused from §4): `used_min` 472.9 / `cap_min` 615, `jobs` 38 / `job_cap` 45 = 142.1
  min and 7 jobs free. This job books 20 min from the measured 571.7 s wall of clip-11 x 12/8 steps = ~858 s plus the
  `pytorch attention` per-step cost, so the projection is 492.9 min / 39 jobs.
- **Coupling disclosed (measured, not assumed):** `p7/JOB_REQUEST.json` carries one armed job, so re-arming it for
  51150021 turns the FIRST item's own arm detectors red. With the committed (HEAD) request file the FIRST item is
  `CHECKS ... ALL 13 PASS`; with the re-armed file it fails exactly detectors 9 (ARM) and 10 (AUDIT-named note). The
  FIRST item's builder was not edited; its receipt was written while it was armed, and any later re-arm (the
  51150012-16 rows do the same) reproduces this. `--now-check` 11 has the same property in reverse for a later pass
  that re-arms the channel.
- No render in this pass: `--now-sheet` prints `SHEET_BLOCKED no render yet: ... runs\ali163_hc15_bd002_s51150021\
  ali163_hc15_bd002_s51150021.mp4 (a Ralph pass never queues)`; the mp4 is absent,
  `p7/jobs/ali163_hc15_bd002_s51150021.result.json` is absent, and there is no `ComfyUI/output/community/ali163_hc15_bd002_s51150021`.
  §5's command stays the render handoff, and `--now-sheet` writes the labelled before/after frame-0 sheet (51150011
  before, 51150021 after) for Derrick. KEEP is Derrick's alone; no vision judge on explicit output.
