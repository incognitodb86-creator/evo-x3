# HC15 start fidelity — measured against the saved corpus (AUD1 repair, 2026-10-29)

Text pass only. No GPU, no llama-swap/ComfyUI calls, no queue, no render, no vision judge, no KEEP (KEEP is Derrick's alone). Adults only, fictional, all named characters 21+ (canon lock v2.3.0).

AUD1 did three things to this doc: (1) every community cell now cites a saved body `path:line` **plus the verbatim sentence** that is actually in that body; (2) claims that no saved body supports were deleted and are listed in §2 with the scan that killed them; (3) the TenStrip card's real sentences are recorded in §1, because the pre-AUD1 version of this doc paraphrased the card and the paraphrases were not in it.

## Method (reproducible)

Corpus = `C:/AI/community/notes/web/` — 1,142 files, every claim checked as a case-insensitive substring over all of them:

```
python - <<'PY'   # inline, no new script file (PROMPT.md: no new tools in a Ralph pass)
import io,os
names=[f for f in sorted(os.listdir(".")) if os.path.isfile(f) and not f.startswith("__")]
for p in ["topk","video-only","faster tests","(frames-5)%17","1900","unload_delay","lowvram","RIFE",
          "shared mechanism","Strata","--kv int8","vram-reserve","350-500","616","10-FlashAtt", ...]:
    hits=[f"{f}:{i+1}" for f in names for i,l in enumerate(io.open(f,encoding="utf-8",errors="replace").read().split("\n"))
          if p.lower() in l.lower()][:3]
    print(p, hits or "NO HIT")
PY
```

Caveat that mattered: `grep -r` **with** `-F` is broken in this Git Bash build — `grep -ri -F -- "health" .` = 0 hits where `grep -ri -- "health" .` = 24. Do not trust a whole-corpus negative from `grep -r -F`; use the python scan above (measured 2026-10-29).

Provenance rule kept (AGENTS.md L8): a 401/403/404 stamp is a blocked row, never evidence. `02v_repo_10eros.404.txt` (118 B) = GitHub repos-API `{"message":"Not Found",...,"status":"404"}`, `04x_tenstrip_repo.401.txt` / `02v_minimax_h3_repo.401.txt` (41 B) = `{"error":"Invalid username or password."}`. Those say nothing about whether a repo exists.

## 1. The TenStrip card, as it is actually written

`notes/web/hc15_tenstrip_readme.txt` = 3,698 B, sha16 `ba3be667bf67bba7`; byte-identical to `agy51_tenstrip_readme.md` and `pq1_tenstrip_card.txt` (verified 2026-10-29). Quoted verbatim, with line numbers:

- `:16` "beta_6 is a built mostly-reference hybrid with a custom turbo meant to mimic how Fastv2 looks and sounds. Samples on 10/3 shift, fully dense or with Fastv2 VSA sparse node settings on multiple samplers like er_sde, euler, LCM, res_multistep, all having some different behaviors with prompt. It's a slow 8-12 step reference model in that configuration. 4step turbo loras can be run on top of it to reduce that. SLA sparsity seems to destroy it, avoid using that on any workflows. It's ideal configuration is with full gates and Fastv2 turbo and VSA gates when they have a reference solution figured out. The attempt to do that is the unstable version which has multiple issues but looks and sounds perfect at 8 steps."
- `:20` "Sampling and prompt are the key to quality and success. Non-turbo full step audio will always be better than audio on turbo versions."
- `:26` "Some working sampling setups:" then `:29` "er_sde/beta 4 steps", `:31` "er_sde/beta57 4-6 steps", `:33` "res_multistep/simple 6-8 steps (my go-to for best motion quality)", `:35` "LCM/simple 6-8 steps (best turbo audio)", `:37` "LCM/beta 4-6 steps", `:39` "Euler/simple 4-8 steps".
- `:47` "Int8 versions" / `:48` "https://huggingface.co/cicalooo/10Eros-Max-h3-int8-convrot"
- `:52` "beta_4 and beta_3 are corrupted test versions. beta_5 is the only true functional one so far."
- `:53` "No cache or spectrum if doing reference, they cause accuracy loss."
- `:54` "Hybrid model is built on the delta1024 h3 merge."

What the card therefore does and does not say: it publishes shift 10/3, an 8–12 step *reference* configuration, a sparsity stance (VSA settings yes, SLA no), a sampler/step list, an int8 lineage pointer, and "no cache/spectrum for reference". It publishes **no** `topk` number, **no** "video-only ON" switch, **no** euler/simple-motion claim, **no** 1344×768 canvas, **no** "reference-image-first", and **no** review protocol. The card's own `:52` (beta_5 is the only functional build) sits against `:16` (beta_6 described as a working hybrid) and against the discussion (`pq1_tenstrip_d61_text.txt:46` "beta6 has better image quality, movements using character sheet references feel stiff"; `:52` owner: "b6 runs with 10/3 shift ... That's not suggested, it's required"). Record the tension, do not resolve it in favour of a render.

## 2. Claims removed by AUD1 (whole-corpus scan, 1,142 bodies)

| Removed claim (pre-AUD1 wording) | Scan result | What replaced it |
| --- | --- | --- |
| TenStrip sparsifier "topk 0.1-0.2" | `topk` → 1 hit in the whole corpus, `02v_qwen35_4b_readme.txt:786` (a Qwen README); `topk 0.1` → NO HIT | card `:16` verbatim + docs `02v_docs_h3.txt:215`, `:210`, `02v_docs_h3_fastvideo.txt:110` |
| "video-only ON" attributed to the TenStrip card | `video-only` → `02x_cont_user_guide.txt:321`, `02v_ltx2_guidance.txt:52`; not in the card; `video_only` → NO HIT anywhere | USER_GUIDE `:321` verbatim (video-only = audio continuity **off**) + measured audio path in our graphs |
| "Do not use SLA sparsity with reference workflows" | NO HIT | card `:16` verbatim ("SLA sparsity seems to destroy it, avoid using that on any workflows") |
| "euler is for simple motion and faster tests" attributed to the card | `simple motion` → NO HIT; `faster tests` → `02v_civitai_2860061.json` / `civ_2860061.json` (Civitai 2860061 Turbo Workflow) | card `:33`,`:39` + Civitai 2860061 verbatim (§5 row 9) |
| "10S route: 10-FlashAtt, MiniMaxH3-10-FlashAtt ... HF 404 for that repo" | `10-FlashAtt` → NO HIT; no saved body names any 10-FlashAtt repo; `10-Flash` → NO HIT; the only 404 stamp is a GitHub repos-API 404 (`02v_repo_10eros.404.txt`) = blocked row, not evidence | card `:47-48` + `02v_cicalooo_card.txt:15-17` (10Eros-Max int8 lineage) + measured unet in our graphs (§4) |
| "Anchoring a guide at a frame is the shared mechanism behind image keyframes" quoted as PR #15439 text | `shared mechanism` → NO HIT | PR body verbatim (§5 row 8); the Continuum/10S pairing is now labelled **ours (inference)** |
| "Continuum registry (3.10.2) + saved docs: 243 f @ 24 fps, video-only ON, no LTX/pipeline" | `02v_registry_continuum.json` (1,224 B) and `04y_reg_continuum.json`: 0 hits for `3.10.2`, `video-only`, `topk`, `243`, `VSA` | card `:16` + continuation README `:58`,`:91-93` + USER_GUIDE `:321`; "243 f" is a measured graph value, not a registry claim |
| "docs and Continuum both list 616x352" | `616` → only 4-char noise in 3 JSON blobs; `352` likewise; no `616x352` anywhere | docs `02v_docs_h3.txt:126`,`:128`; `02v_docs_h3_fastvideo.txt:38`; USER_GUIDE `:315`,`:338` |
| "issue 15337: a 1344x768 H3-with-audio OOM report on a 16 GB RTX 5080 laptop, therefore 1024x576 audio / 1280x720 video only" | In `02v_comfyui_issue15337.json`: `1344` 0, `768` 0, `1024` 0, `1280` 0, `OOM` 0, `out of memory` 0, `5080` 0 | the issue's real content (§5 row 11) — an access-violation crash at **video VAE** load on an **RTX 5070 Ti 16 GB** (same GPU as this box) with a published flag workaround |
| Graph artifacts "hc15_bd002_s51150011, hc15_a2_s51150012" | Not on disk. `p7/graphs/` holds `ali163_hc15_*` names; no `a2` graph exists anywhere | real paths in §4 |
| "llama-swap: hc15_s01 upstream: ttl 300, unloadTimeout 300, renderTimeout 1800" | `hc15` → **0 occurrences** in `C:/AI/director/config/llama-swap.yaml`; `renderTimeout` → NO HIT in the corpus | the measured `comfyui_auto` block in §4 |
| Continuum README `:240-241` cited for "the graph must not auto-repair the plan" | `:236-240` is about Spectrum code marshal encodings / "Unknown or modified code remains non-reusable" — a different subject | README `:217-220` verbatim (§5 row 12) |
| "ComfyUI `start_comfyui.ps1` launch flags" | No such file (`find` over C:/AI + 5slock) | the launch line is the llama-swap `cmd` (measured, §4) |

## 3. Saved bodies the corpus **does** support (verbatim, cited)

ComfyUI H3 docs `notes/web/02v_docs_h3.txt` (18,119 B, sha16 `aa6a6e643652b428`; identical bytes to `agy41_comfy_h3_doc.md`):

- `:70` "Pick the smallest build that fits in VRAM. Change only the `UNETLoader` file; ComfyUI reads quantization from the checkpoint. LoRAs must match the build family (full-build LoRAs lose adaln on pruned)."
- `:74` `pruned_w6a8` "16 GB | Smallest; INT8 path; ComfyUI 0.38.0+" · `:75` `pruned_int8_convrot` "21 GB | Default in templates"
- `:80` "**Comfy Kitchen attention cannot run `int8_convrot` checkpoints**; use a `bf16` build with that backend."
- `:84` "Templates use int8 video + fp32 audio; int8 video decodes \~2× faster on ComfyUI 0.36.0+."
- `:126` "Templates open at **Megapixels** **0.4**: **864×480** at 16:9, **640×640** at 1:1 (the I2V default)."
- `:128` "For 16:9 native quality, set **0.98** (\~1344×768) or enter **1344 × 768** on the node. Avoid **1.0** MP (1376×768 exceeds the 768×1344 cap). H3 is trained near 1 MP; oversizing does not add detail."
- `:142` "Templates expose `duration` in seconds, converted to frames on the `17k+5` grid at 24fps." · `:147` trained range "\~124–362 frames (\~5–15 s)" · `:148` "Frame grid | `17k+5` at 24 fps (124 frames = 5 s)". The modulo form `(frames-5) % 17 == 0` is **ours** (equivalent restatement; NO HIT in the corpus).
- `:155` "Beyond the trained range, chain I2V continuations from each clip's last frame. Errors compound (faces lose texture first); turbo/distilled schedules show burn sooner."
- `:157` anti-burn LoRA "on clips after the first at `strength_model` \~0.5 (tune for your continuation style)"
- `:161` defaults 20 steps; turbo 8 (T2V/I2V/continuation), 4 (R2V, Multiframe, Fun ControlNet) · `:163` "Reference shots need more steps: reference tokens ride every step, so 4-step turbo can barely apply references (pose/face drift). For tight reference match, keep turbo off or raise toward **25**." · `:171` "Simple shots: **12–16** steps often enough" · `:173` "Most motion/prompt gains by step **16**; little visible change past **50**" · `:176` "Audio converges later than video in the joint denoise. Speech and timbre need **12+** steps; at **8** steps audio is often the weak link."
- `:180` "Templates use **`res_multistep`** + **`simple`**." · `:182` "`res_multistep` is second-order multistep (first step is Euler). Splitting the schedule across two samplers drops multistep history: the second sampler's first step is first-order again."
- `:184` "Default H3 shifts are `shift` **12** and `audio_shift` **3** from the model definition (no extra node). FastH3 templates set **ModelSamplingMiniMaxH3** to `shift_video` **10**, `shift_audio` **3**. Wrong video shift on distilled builds (e.g. **3** instead of **10** on 8-step) can show grid artifacts."
- `:201` "Templates use **`int8_convrot`** checkpoints. **Comfy Kitchen does not support them** ([issue #15529](https://github.com/Comfy-Org/ComfyUI/issues/15529)). Use default attention, or switch `UNETLoader` to **`pruned_bf16`** then change backend." · `:204` "Add **Model Attention Backend** (`comfy kitchen attention`) on the model path to `BasicGuider` (after LoRA/turbo), or use `--use-ck-attention` (0.32.0+)."
- `:208` "**Model Sparse Attention** (0.35.0+, experimental) ... For base H3 use `method` **`sol-attn`** (`sla`/`vsa` need matching weights)." · `:210` "Defaults `start_percent` **0.2**, `end_percent` **1.0**." · `:211` keep `sink_conditioning` `exact_kv_and_rows` · `:213` min_tokens default **12288** · `:215` "FastH3 uses **`vsa`** at `keep_percent` **10**"

FastH3 page `notes/web/02v_docs_h3_fastvideo.txt` — `:38` "H3's native canvas is a 768px short edge, capped at 768x1344, and resolutions are rounded to a multiple of 32" · `:39` duration snaps to "17-frame-per-block (17k+5) grid at 24fps" · `:40` "**Steps are fixed at 8**: The distilled checkpoint is trained for exactly 8 steps; changing the step count in the scheduler degrades quality" · `:110` "**BlockSparseAttention**: Runs Video Sparse Attention (VSA) with `keep_percent` 10 starting at 20% of the schedule" · `:111` "**MiniMaxH3SigmaShift**: Applies the H3 sigma shift (10 for video, 3 for audio) that matches the distilled schedule".

Native page `notes/web/02v_docs_h3_native.txt` (13,471 B, sha16 `25c75029fb77c27b`) — `:138` "the same rules as T2V (**1344×768** native target, **17k+5** grid)" · `:141` "The I2V template opens at **1:1** and **0.4** MP (**640×640**)" · `:147` "Lock character, style, motion, camera, or voice from reference images, videos, and audio." · `:211` "Up to **9** images, **3** videos, **3** standalone audio clips" · `:218` "**`ref_image_size`**: Default **`match`** (fit to canvas). **`max`** keeps 2048px short edge and is much slower; it does not upscale small files (round sides to 32). Pre-scale to 2048 short edge when needed" · `:220` "Turbo: Optional **4**-step Lightning LoRA (faster, weaker reference/audio). Prefer **20–25** steps when references must hold" · `:231` "[`MiniMaxH3AddGuide`] anchors a guide at any `frame_idx` (negative = from end), not only first/last frame."

PR #15439 `notes/web/hc15_pr15439.json` (24,796 B, sha16 `2713117e51ae5dee`) — title "Add MiniMaxH3AddGuide for anchoring image and audio guides at any frame", `state: closed`, `merged: true`, `merged_at: 2026-08-13T19:55:37Z`, +141/−46. Body: "Currently MiniMax H3 implementation in Comfyui only allows keyframe guides at the first and last frame. The model itself is capable of addressing guides by position on a continuous time axis, so this removes that restriction and exposes it as a node." … "**MiniMaxH3AddGuide** anchors a guide at any frame_idx (negative counts from the end): a still image; a clip (batches snap down to the model's valid clip lengths: 5, 22, 39... frames); audio, anchored at the same position on the timeline; any combination, and nodes chain for multiple guides" … "Example: feed the first 22 frames of an existing video plus its audio into one AddGuide at frame_idx 0 and the model generates the continuation of both streams."

Continuation README `notes/web/hc15_continuation_readme.txt` (5,483 B, sha16 `3855c015f0c3c56e`; identical `03y_continuation_readme.txt`, `cont_readme.md`) — `:58` "The example first generates a 243-frame clip. It then uses:" `:61-63` "`overlap_frames = 22`, `extension_frames = 119`, `window_length = 141`" · `:85-87` "Use the ordinary H3 model and a normal full-denoise schedule. The example shares its fixed seed, sampler, and scheduler between the initial and continuation passes. No additional model patch or refinement pass is part of this workflow." · `:91-93` "`overlap_frames` must be at least 5, must not exceed the completed latent, and must satisfy `17k + 5`. The example uses 22. `extension_frames` must be a positive multiple of 17. The example uses 119."

Continuum USER_GUIDE `notes/web/02x_cont_user_guide.txt` (75,005 B, sha16 `92bee3f3c0c34035`) — `:24` "First/Last additionally constrain the video; Last Image may merge the final two logical chunks into one physical group, which requires the same effective Reference set in both." · `:315` "`Width` / `Height` | Exact output canvas in 32-pixel steps | Visible/editable only in Manual mode; 32–16384 is accepted" · `:338` "Both must be multiples of 32." · `:321` "With Audio Continuity off, Standard uses the Video-only masked route." (the only published "Video-only" in the corpus, and it means **audio continuity off**). Continuum README `02v_continuum_readme.txt` (32,957 B, sha16 `8b4356f2720434dd`) `:1` "# ComfyUI-H3-Continuum 3.10.2 — V3.9", `:217-220` "Fix stale verified Reference Plan text after the Sampler UI is reconfigured, including workflow save/reload. Changing Reference assignments now invalidates the old Inspector display; the next backend result supplies the verified plan."

MiniMax ref guide `notes/web/agy51_ref_guide.md` (23,553 B, sha16 `1e574f356716ad55`) — `:13` "A complete rewrite output consists of six sections in the following order:" `:17-22` `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` · `:242` "For generation tasks, `detailed_description` is normally 350-500 English words. Dialogue-dense content prioritizes fitting the complete spoken timeline rather than mechanically reaching a word count."

TenStrip discussion `notes/web/pq1_tenstrip_d61_text.txt` (5,568 B, sha16 `ee197c6fbfb8974a`) — `:19` "i am using the Pixxorama workflow, with the recomended settings video shift 10 audio 3" · `:27` "Straight 8-10 steps single pass workflows are still preferred, but a two staged one is usually faster, and allows for quick previews." · `:52` owner: "b6 runs with 10/3 shift, 10 video shift while the normal model and b5 run 12. That's not suggested, it's required." · `:64` "Set your shift to 10/3 use onlysparse attn". 10Eros discussion `notes/web/_disc_10eros.txt` — `:3` TenStrip 2026-10-09: "I actually use the "fasth3" I2V comfy template. Just add steps and change sampler. For reference I just changed the node and added image loaders." · `:17` Vinyl86 2026-10-22: "What workflow should be used for this model? I haven't found one that works with VSAgates. 10Eros_Max_FastH3_VSAgates_UNSTABLE_beta6-int8_HQ".

10Eros int8 card `notes/web/02v_cicalooo_card.txt` (1,919 B, sha16 `46b859f7b2f840ad`) — `:15` "# 10Eros-Max H3 — INT8 ConvRot" · `:17` "Native ComfyUI INT8 ConvRot conversions of [TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max)."

Civitai 2860061 (the HC15 start-frame workflow, `02v_civitai_2860061.json`, 62,558 B, sha16 `76c8993eb229c486`) — Turbo Workflow block: "Recommended for faster tests and iteration. / LightX2V MiniMax H3 Turbo LoRA / 8-step example configuration / Spectrum is bypassed by default / Faster than the standard workflow in tested configurations / Some loss of facial detail or additional artifacts". Civitai 2835850 turbo-stack extract `bq1_web_extract2.txt` (175,470 B) — `:731` "UNETLoader (INT8) → LoraLoader → ModelAttentionBackend (Comfy Kitchen Attention) → BlockSparseAttention (sol-attn) → MiniMaxH3SigmaShift → BasicGuider (CFG 1.0) → SamplerCustomAdvanced" · `:792` the corpus's only RIFE text: "TensorRT Batch Size RIFE and Upscaler TRT expose sep…".

Issue 15337 `notes/web/02v_comfyui_issue15337.json` (7,732 B, sha16 `ea1be378a4b2b457`) — title "MiniMax H3 video VAE decode: access violation with pinned memory / async offload on RTX 5070 Ti (Blackwell, WDDM, cu130)", `state: open`, created 2026-08-06: "Running the official MiniMax H3 I2V template workflow crashes the whole ComfyUI process during video VAE decode when pinned memory / async weight offload are enabled (the defaults on NVIDIA). … With `--disable-async-offload --disable-pinned-memory` the same workflow completes successfully." Env: "GPU: NVIDIA GeForce RTX 5070 Ti 16 GB (Blackwell, sm_120, WDDM)", reproduction "the official `video_minimax_h3_i2v` template workflow (defaults: 0.4 MP, 5 s, 20 steps) with default launch flags", Run 1 "diffusion sampling succeeds, then audio VAE loads fine, then video VAE weight loading fails".

## 4. Measured local state (the "ours" column, all read 2026-10-29)

Graphs live in `C:/AI/community/p7/graphs/` with the shipped names, e.g. `ali163_hc15_bd002_s51150011.api.json` (27 nodes) and `ali163_hc15_bd002_s51150001.api.json` (33 nodes). Key inventory, read from the JSON (not from a plan):

| Key | `…_s51150011` | `…_s51150001` |
| --- | --- | --- |
| `unet` UNETLoader | `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` | same |
| `vvae` / `avae` | `minimax_h3_video_vae_int8_convrot.safetensors` / `minimax_h3_audio_vae_fp32.safetensors` | same |
| `clip` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (type `minimax`) | same |
| canvas / length | `c0` 1344×768, `length` 243; `c1` via `win1` (overlap 22 / extension 119) | 1344×768, `c0` 124, 3 windows (`win1`,`win2`) |
| `ksel` sampler | `res_multistep` | `euler` |
| `s0/s1(_2)_sched` | `simple`, `steps` 8, `denoise` 1.0 | `simple`, `steps` 10, `denoise` 1.0 |
| `m_shift` | `MiniMaxH3SigmaShift` shift_video 10.0, shift_audio 3.0, model input from `m_vsa` | same |
| `m_vsa` | `BlockSparseAttention` `selection: vsa`, `selection.keep_percent: 10`, `start_percent` 0.2, `end_percent` 1.0, `min_tokens` 12288, `sink_conditioning: exact_kv_and_rows` | same |
| `m_attn` | `ModelAttentionBackend` `attention: "comfy kitchen attention"` | same |
| LoraLoader nodes | **none** (turbo is inside the 10Eros file name) | **none** |
| CFG | **no `cfg` key anywhere in either graph** (0 keys matching `cfg`) | same |
| guide anchors | `g0 MiniMaxH3AddGuide` `frame_idx` 0, image `img`, positive `c0` | **no AddGuide node** |
| ref slots | `ref_images.ref_image_1`, `ref_images.ref_image_2` (fullmatch, `c0`/`c1`) with `ref_image_size: max` | same |
| audio out | `dec_a VAEDecodeAudio` → `mkvid CreateVideo` `audio`, fps 24 | same |

Local files measured: `C:/AI/director/config/llama-swap.yaml` (not `C:/AI/director/llama-swap.yaml`) — `:31-32` `swap: true` / `exclusive: true` in a `groups:` block, `:6` `healthCheckTimeout: 1200`, `:8` `globalTTL: 0`, `:9` `unloadTimeout: 15`, `:12` `timeouts.responseHeader: 1200`; `comfyui_auto` `:97` cmd = `main.py --listen 127.0.0.1 --port ${PORT} --lowvram --disable-async-offload --disable-pinned-memory --use-ck-attention`, `:98` `cmdStop: … C:\AI\director\scripts\comfy_graceful_stop.ps1 -ProcId ${PID} -Port ${PORT}` (comment: waits for the queue max 1800 s, then taskkill), `:99` `checkEndpoint: /`, `:100` `ttl: 0`, `:101` `unloadTimeout: 1900  # > graceful-stop cap`, `:102` `unlisted: true`, `:104` `ignoreWebsockets: true`. **No `hc15` upstream exists in that file (0 hits)**, so no per-line `ttl 300 / unloadTimeout 300 / renderTimeout 1800` is ours. There is no `start_comfyui.ps1` on this box (find over C:/AI and C:/Users/derek/5slock).

Model inventory (`C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/models/`): `diffusion_models/10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` present; **no** `minimax_h3_fl2va_pruned_int8_convrot*` anywhere; `unet/` holds only FLUX-KLEIN + a sulphur GGUF; `vae/` has `minimax_h3_video_vae_int8_convrot.safetensors` (2,811,065,184 B) and `minimax_h3_audio_vae_fp32.safetensors` (605,254,808 B); `loras/` has `h3_antiburn_universal_v1.safetensors` and **no** `minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors`.

## 5. Ours vs the published wording (14 rows, AUD1 measured)

| # | Row | Published wording (saved body) | Ours (measured) | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Checkpoint | docs `:75` "pruned_int8_convrot … 21 GB \| Default in templates"; docs `:80` "**Comfy Kitchen attention cannot run `int8_convrot` checkpoints**"; card `:47-48` int8 pointer; `02v_cicalooo_card.txt:17` "Native ComfyUI INT8 ConvRot conversions of TenStrip/10Eros-Max" | `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`, loaded with `weight_dtype: default` | differ in a way the docs flag: an int8 build driven through `comfy kitchen attention` (`m_attn`), the pairing docs `:80`/`:201` say needs bf16. Not a "TenStrip checkpoint" graph. |
| 2 | VAE | docs `:84` "Templates use int8 video + fp32 audio; int8 video decodes \~2× faster on ComfyUI 0.36.0+" | int8 video + fp32 audio, files present at the measured sizes | match |
| 3 | LoRAs | docs `:157` anti-burn "on clips after the first at `strength_model` \~0.5"; native `:220` "Optional **4**-step Lightning LoRA (faster, weaker reference/audio). Prefer **20–25** steps when references must hold"; card `:16` "4step turbo loras can be run on top of it to reduce that" | **no LoraLoader node in either graph**; the turbo is inside the 10Eros file; `h3_antiburn_universal_v1.safetensors` is on disk but unwired | differ, and the pre-AUD1 "LoRAs: turbo + anti_burn" cell was false |
| 4 | Shift | docs `:184` default 12 / 3, "FastH3 templates set … 10, 3"; fastvideo `:111`; card `:16` "Samples on 10/3 shift"; `pq1_tenstrip_d61_text.txt:52` "10/3 shift … required", `:19` | shift_video 10.0 / shift_audio 3.0 on `m_shift` | match (and 10/3 is the FastH3/distilled value; 12/3 is base) |
| 5 | Sampler + scheduler | docs `:180` "Templates use `res_multistep` + `simple`"; card `:33` "res_multistep/simple 6-8 steps (my go-to for best motion quality)", `:39` "Euler/simple 4-8 steps"; `02v_civitai_2860061.json` Turbo = 8 steps | s51150011: `res_multistep`/`simple`/8; s51150001: `euler`/`simple`/10 | match. The pre-AUD1 "euler for simple motion, res_multistep for complex motion" reading is gone: no source says it. |
| 6 | Steps vs audio goal | docs `:176` "Speech and timbre need **12+** steps; at **8** steps audio is often the weak link"; docs `:163` reference match "raise toward **25**"; native `:220` "Prefer **20–25** steps when references must hold"; card `:20` "Non-turbo full step audio will always be better than audio on turbo versions"; fastvideo `:40` distilled "trained for exactly 8 steps" | 8 steps (s51150011), 10 steps (s51150001), both denoise 1.0 | **the binding tension, measured**: HC15's goals are reference identity + audio; four sources put audio quality and reference adherence above an 8-step turbo pass. |
| 7 | Canvas / grid | docs `:128` "set **0.98** (\~1344×768) … Avoid **1.0** MP (1376×768 exceeds the 768×1344 cap)"; fastvideo `:38` "768px short edge, capped at 768x1344 … rounded to a multiple of 32"; docs `:142`,`:148` 17k+5 @ 24 fps, trained "124–362 frames" | 1344×768 (grid-clean), length 243 = 10.125 s at 24 fps (`(243-5)/17 = 14`) | match; 243 is on the grid and inside the 124–362 trained range. `616x352` deleted: no source. |
| 8 | Keyframe control | PR #15439 body: "only allows keyframe guides at the first and last frame … anchors a guide at any frame_idx"; native `:231` | `g0 MiniMaxH3AddGuide frame_idx: 0` in s51150011; **no guide node** in s51150001 | match for s51150011 (mid-clip anchoring is available and node `g0` is the first-frame guide). "Shared mechanism with Continuum/10S" = ours (inference), no source. |
| 9 | Continuation | README `:85-87` "ordinary H3 model and a normal full-denoise schedule … shares its fixed seed, sampler, and scheduler between the initial and continuation passes. No additional model patch or refinement pass"; `:91-93` overlap ≥5 and `17k+5`, extension a positive multiple of 17; `:58` 243-frame example, overlap 22 / extension 119 / window 141 | 33-node graph: 3 windows, overlap 22, extension 119, `denoise` 1.0 on every scheduler, one shared `ksel`/`noise`, no LoRA patch | match (this is exactly the published shape). USER_GUIDE `:24` "First/Last additionally constrain the video; Last Image may merge the final two logical chunks into one physical group, which requires the same effective Reference set in both." = a Continuum-template statement, not a statement about our hand-wired graph. |
| 10 | Reference-image-first | native `:147` "Lock character, style, motion, camera, or voice from reference images, videos, and audio."; native `:211` "Up to 9 images, 3 videos, 3 standalone audio clips"; native `:218` `ref_image_size` "Default `match` (fit to canvas). `max` keeps 2048px short edge and is much slower; it does not upscale small files (round sides to 32)" | `MiniMaxH3ReferenceToVideo` with `ref_images.ref_image_1/2` and `ref_image_size: max` | match on the mechanism. The pre-AUD1 "docs: max keeps a 2048px short edge, never downscales tight face crops" is now `:218` verbatim; the face-crop strategy is ours. |
| 11 | VRAM / canvas evidence | docs `:74` 16 GB build, `:82` "If VRAM is tight, step down a size: CPU offload costs more than precision tradeoffs"; issue 15337 (measured above): a VAE-decode access violation on an RTX 5070 Ti 16 GB at the **official template defaults** (0.4 MP, 5 s, 20 steps), workaround `--disable-async-offload --disable-pinned-memory` | our launch line already carries `--disable-async-offload --disable-pinned-memory` (yaml `:97`) | the pre-AUD1 "15337 ⇒ 1024x576 audio, 1280x720 video only" is deleted: the issue says nothing about resolutions. What it does support is the flag pair we already run. |
| 12 | Sparsifier | card `:16` "fully dense or with Fastv2 VSA sparse node settings … SLA sparsity seems to destroy it, avoid using that on any workflows"; docs `:215` "FastH3 uses `vsa` at `keep_percent` **10**"; docs `:210` start 0.2; docs `:208` "For base H3 use `method` **`sol-attn`** (`sla`/`vsa` need matching weights)"; docs `:213` min_tokens 12288; `_disc_10eros.txt:17` a user cannot find a workflow that works with VSAgates | `m_vsa` = vsa, keep_percent 10, start 0.2, min_tokens 12288 — and `m_attn` = comfy kitchen attention on an int8 unet | match on the numbers (they are the published FastH3 numbers). The open published risk: docs `:80`/`:201` (Kitchen × int8_convrot) and docs `:208` (vsa needs matching weights). No `topk` anywhere in the corpus. |
| 13 | Audio on / video-only | USER_GUIDE `:321` "With Audio Continuity off, Standard uses the Video-only masked route."; docs `:176` audio needs 12+ steps; card `:20` | audio path wired end to end (`avae`, `dec_a`, `CreateVideo.audio`), fps 24 | ours is the audio-on configuration. "video-only ON" as a TenStrip setting is deleted; the phrase exists only as the Continuum audio-continuity-off route. |
| 14 | Review protocol | no community source in the corpus | measured receipts: `notes/hc15_audit_timing.py`, `logs/hc15_after_metrics.log`, ffprobe + sha256 receipts | ours (the plan's rule, not the card's). No vision judge on explicit output; no KEEP claim here — KEEP is Derrick's alone. |

## 6. Source table (verified on disk, 2026-10-29)

All rows are bodies saved by earlier research passes; each was opened and hashed for this pass. `URL of record` = the URL in the pre-AUD1 source table, kept for provenance; the citation that carries weight is the saved body + line.

| Saved body (C:/AI/community/notes/web/) | bytes | sha16 | kind | URL of record |
| --- | --- | --- | --- | --- |
| `hc15_tenstrip_readme.txt` (= `agy51_tenstrip_readme.md` = `pq1_tenstrip_card.txt`) | 3,698 | ba3be667bf67bba7 | TenStrip model card body | https://civitai.com/models/2860061 |
| `pq1_tenstrip_d61_text.txt` (+ `.html`) | 5,568 | ee197c6fbfb8974a | TenStrip discussion 61, text extract | https://civitai.com/s/1Xgxpq1/discussions/61 |
| `_disc_10eros.txt` | — | — | 10Eros discussion extract | https://civitai.com/models/2835850 (10Eros thread) |
| `02v_cicalooo_card.txt` | 1,919 | 46b859f7b2f840ad | 10Eros-Max int8-convrot card | https://huggingface.co/cicalooo/10Eros-Max-h3-int8-convrot |
| `02v_docs_h3.txt` (= `agy41_comfy_h3_doc.md`) | 18,119 | aa6a6e643652b428 | docs.comfy.org minimax-h3.md | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md |
| `02v_docs_h3_native.txt` | 13,471 | 25c75029fb77c27b | minimax-h3-native.md | https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md |
| `02v_docs_h3_fastvideo.txt` | 6,454 | 9044f2c58dd6fae0 | minimax-h3-fastvideo.md | https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo.md |
| `agy51_ref_guide.md` | 23,553 | 1e574f356716ad55 | MiniMax H3 reference prompt guide | https://huggingface.co/MiniMaxAI/MiniMax-H3/tree/main/docs |
| `02v_antiburn_readme.txt` | 6,732 | 7c5be134731f15b4 | H3-Anti-Burn-LoRA card | https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA |
| `hc15_pr15439.json` | 24,796 | 2713117e51ae5dee | PR #15439 API body (merged) | https://github.com/Comfy-Org/ComfyUI/pull/15439 |
| `02v_comfyui_issue15337.json` | 7,732 | ea1be378a4b2b457 | issue 15337 API body (open) | https://github.com/Comfy-Org/ComfyUI/issues/15337 |
| `hc15_continuation_readme.txt` | 5,483 | 3855c015f0c3c56e | H3 Continuation README | https://github.com/Comfy-Org/ComfyUI custom-node README (continuation) |
| `02x_cont_user_guide.txt` | 75,005 | 92bee3f3c0c34035 | ComfyUI-H3-Continuum USER_GUIDE | https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum |
| `02v_continuum_readme.txt` | 32,957 | 8b4356f2720434dd | Continuum README 3.10.2 | https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum |
| `03y_cont_driving_nodes.txt` | 46,434 | 6403c2bde3fc0b8c | Continuum driving-node source (`target_frames`, canvas multiple of 32) | https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum |
| `02v_registry_continuum.json` | 1,224 | a136e5d3d56fb625 | Continuum registry entry (no version/frame data inside) | ComfyUI registry |
| `02v_civitai_2860061.json` | 62,558 | 76c8993eb229c486 | Civitai 2860061 workflow description | https://civitai.com/models/2860061 |
| `bq1_web_extract2.txt` | 175,470 | e8f47c901bec9d7f | Civitai 2835850 turbo-stack extract (CFG 1.0 chain, RIFE mention) | https://civitai.com/models/2835850 |
| `agy41_comfy_cli_args.py` | 23,657 | bebe7a5802f99aca | ComfyUI CLI parser source (`--listen`, `--port`, `--lowvram`) | https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/cli_args.py |
| `01r_ls_comfyui.txt` | 8,330 | f899f3ffb8c0b10f | llama-swap ComfyUI guide | https://github.com/mostlygeek/llama-swap (docs/kb/guides/upstreams/comfyui.md) |
| `01r_ls_ttl-and-unloading.txt` | 3,498 | 198e6130263aa69b | llama-swap ttl/unload guide | https://github.com/mostlygeek/llama-swap |
| `01r_llamaswap_readme.txt` | 17,354 | a72e7644254751db | llama-swap README (`/health`, unloadTimeout) | https://github.com/mostlygeek/llama-swap |
| `agy51_gh_minimax_h3.html` | — | — | ComfyUI README page; its only "white flash" text is an example **prompt**, not a flag effect | https://github.com/Comfy-Org/ComfyUI |
| `02v_repo_10eros.404*.txt`, `04x_tenstrip_repo.401*.txt`, `02v_minimax_h3_repo.401*.txt` | 118 / 41 | — | **blocked fetches** (GitHub 404 / HF 401) — recorded as blocked rows, used as evidence for nothing | n/a |

## 7. Still unsourced (a research pass, not a render, is the fix)

`topk` values for H3 sparsity; a published "reference-image-first" doctrine; the "10S"/10-FlashAtt repo (and any HF 404 for it); a 1080p60 + RIFE route in the H3 docs; per-resident-line llama-swap upstreams for HC15; and the pi-doc claims that `notes/cf1_setup_audit_20261024.md` attributes to `notes/pi_docs/*` — those files are **not on disk** (see the cf1 doc § AUD1). Each needs a saved body fetched from a community source before the claim can appear in a Forge doc.

## 8. Gate on this doc

AUD1 is text-only, so the gate is a citation scan, not a loop/pytest run (those are unaffected by two notes files): every community cell in §5 resolves to a `path:line` in §3/§6 whose file exists (re-verified by `os.path.exists` + sha16 above), and every removed phrase in §2 is a whole-corpus NO HIT from the § Method scan. Re-run the Method scan after any edit to this doc: a phrase quoted in §3/§5 that the scan no longer finds is a regression.
