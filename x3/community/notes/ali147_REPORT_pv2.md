# ALI-147 PV2 report - PromptV2 segment 1 (PV2-1), segment 3 (PV2-2), dense at 481 (PV2-3)
PLAN: ALI-147 - output label: **METHOD_ONLY; KEEP is Derrick's.** Written 2026-10-23 by Forge (Ralph loop, task PV2-6). READ-ONLY iteration: no GPU, no node list, no render, no job request, no vision judge, no download, no copy of any image. Report lives only under `notes\` (Max 19:46 CT rule).

## 0. How the numbers were produced (and what is not claimed)
Probe scripts + outputs, all under `C:/AI/community/notes/`:
- `ali147_pv26_report_probe.py` -> `ali147-pv26-report-probe-20261023.txt`: **TOTAL PASS=77 FAIL=0 / ALL CHECKS PASS** (prompt files vs `SHA256SUMS.txt`, CTRL/BASE controls, provenance byte-compare, status.log, objective.json, `ffprobe -count_packets`, the harness black/freeze chain re-run, contact-sheet geometry, graph fairness, `graph_diff` hunk counts, render-secs table, live budget, sbs/stills presence, held-item asset presence).
- `ali147_pv26_card_probe.py` -> `ali147-pv26-card-probe-20261023.txt`: PASS=3 FAIL=0 (K1 card, SNOFS reference, KV31 card, PV2-5 prompt, budget arithmetic).
- `ali147_pv26_settings.py` -> `ali147-pv26-settings-20261023.txt`: node-by-node settings for all 5 graphs (prompts as length + SHA256).
- `ali147_pv26_commits.py` -> `ali147-pv26-commits-20261023.txt`: VSA module + Extender commits.
Methods: `ffprobe -count_packets` for frames (never `format=duration`), `certutil`/`hashlib` SHA256, byte-compare `request.api.json` vs the harness `<id>.api.json`, node-level `json.dumps(node, sort_keys=True)` fair comparison, `git diff --no-index` for `graph_diff.txt`, `PIL.Image` sizes for the sheets, `comm.guard_ok` imported read-only, and the harness's own chain read out of `C:/AI/community/scripts/run_graph_job.py` (`blackdetect=d=1.0:pix_th=0.10,freezedetect=n=-60dB:d=2`) re-run per mp4.
**Not measured:** motion quality, anatomy lock, camera, skin, mouth, lighting. The vision judge is off ALI-147 explicit output (ruling logged 2026-10-22: review = contact sheet + objective checks) and this model cannot view images. **No "best result" is declared here** - that is a keep/drop judgement for Derek on the sheets and any side-by-sides.

## 1. Prompt files, hashes, guards
`specs\prompt_v2\SHA256SUMS.txt` (460 B, sha256 `e4457e1e16276df0b8d468d999fc5c4b25d244542d356cd440c85bbaef219e92`) lists 8 names; 4 files exist. All 4 present files hash-match, and those 4 are exactly the inputs of these arms:

| file | bytes | sha256 (self = SHA256SUMS) |
|---|---|---|
| `v2_seg1_c0_r2v.txt` | 4412 | `93757123b2b41ee857d47a3708e7f1610c8629f557582f969982be34d8581b94` |
| `v2_seg1_c1_t2va.txt` | 2770 | `8e1b304a67c02929b04a57aa105d9ea0092f977ab4cf26c75ca02351254a31d9` |
| `v2_seg3_c0_r2v.txt` | 4358 | `7bd377a27db463da847164a0c316bb2337cd1daba8dcb0b658443b55c7149bb3` |
| `v2_seg3_c1_t2va.txt` | 2903 | `268161821f8ab51ea4645be29718297a00767a801e5d370106ff96586ed37a0c` |

SHA256SUMS names with no file on disk: `stillfix_A_anatomy_ref_klein.txt`, `stillfix_B_matte_skin_klein.txt`, `v2_rs016_c1_r2v.txt`, `v2_seg1_c1_r2v_fix1.txt`.
Uppercase `PROMPT V2` / `PROMPT V2.1` headers present in all four; no lowercase form; no `disable the LORA stack`, no `removes the LORA stack`. **`True Stream` is not in the prompt text** - it is the runtime `$c0` `MiniMaxH3ReferenceToVideo.loop_policy="platform_stream"` (present in all four graphs: CTRL, BASE seg3, PV2-1, PV2-2). `logs/ali147-admission-audit.json`: `prompt_v2_segment_1` / `prompt_v2_segment_3` = `"PASS"` with the exact single-variable pass strings; its `prompt_sha256` keys cover the base prompts, while the PV2 hashes are carried in PV2-1's `PROOF.md`/`fairness.txt`. The adult form ("21+ ... admitted as adult") is present in every prompt and in the graph strings.
No second copy of any prompt outside `specs\prompt_v2` (`find C:/AI -name "v2_seg*"` = 4 hits, all in that directory); the 2026-10-19 second-copy rule (character/reference images) has no match for these prompt files.

## 2. Prompt file -> node mapping, verbatim check
| arm | node | class | chars in graph | graph prompt sha256 | source file sha256 | verbatim |
|---|---|---|---|---|---|---|
| PV2-1 | `$c0` | `MiniMaxH3ReferenceToVideo` | 4411 | `889c543a13cfb3d0e37c20198a2d03cc3d9e4b32934ad2ce71b37b359d3175b6` | `93757123…` (4412 B, CRLF+final newline) | **exact** after CRLF->LF + rstrip |
| PV2-1 | `$c1` | `MiniMaxH3ImageToVideo` | 2769 | `655e92a8f668f51e74bececce3471bcc32492bfdd1ade7377b456b65eec17d2b` | `8e1b304a…` | **exact** |
| PV2-2 | `$c0` | `MiniMaxH3ReferenceToVideo` | 4358 | `ad77122b96f4ad474a6329a72b556f3372a80cb010e68a6c3ea10fe48a53763b` | `7bd377a2…` (LF) | **exact**, no fold needed |
| PV2-2 | `$c1` | `MiniMaxH3ImageToVideo` | 2903 | `2e3905ee2272a9d7ff0ab47d5db1765e4fa456ba4aa5ae2798e3fac404cfb383` | `26816182…` | **exact** |

The header "unparsed-peak" is verbatim: every `$c0`/`$c1` string starts with the exact `PROMPT V2 ...` header line of its file. PV2-3's prompts are the CTRL ones verbatim (`$c0` 3295 chars sha `7b4b22bb170f27d5321721a822423493229249c45677473424d8e3b969757078`, `$c1` 2303 chars sha `6686d7057ead4e8433c54656e1ab1dec7ea3e3172806168c2fc4c6e475b6888c`).
`comm.guard_ok` passes on every prompt string in the three arm graphs and in each prompt file. The `p7\jobs\ali147_pool_promptv2_s51080000_ali147_pool_promptv2_00001_$.txt` sidecars (4415 B / 2773 B) = graph node string + CRLF + trailing newline, not the prompt-file bytes.

## 3. Output facts per arm (paths + SHA256 + objective)

| item | PV2-1 `ali147_pool_promptv2_s51080000` | PV2-2 `ali147_pool_promptv2_seg3_s51080002` | PV2-3 `ali147_pool_dense_s51080000` |
|---|---|---|---|
| control / source | CTRL `ali147_pool_ctrl_s51080000\submitted_graph.pretty.json` 10,886 B sha `698854152284100e60b6ac87a795a7f083160a9556acb3fb868793b7f4373bb6` | `p7_r2_c3_pmot_full_pool_seg3` - source graph `runs\p7_r2_c3_pmot_full_pool\p7_r2_c3_pmot_full_pool_seg3.api.json` 10,910 B sha `c5b6726c1d5870f597ba51fcf65499d489be9a1755ebf1905ab8fac5960e8fec`; old mp4 5,624,126 B sha `fc28701abc585f3ae052b9316df22ba4edf7f31a2f3c685d2bbd758d2191d053` (481 packets) | CTRL (same graph as PV2-1's control) |
| my graph = rendered graph | 12,480 B sha `d9212ff14b1f899dd7fb67b308d4e09d86fc8520f2f828fd83d1cfd0408fbcb5`; harness `ali147_pool_promptv2_s51080000.api.json` **0 bytes differ** | 12,569 B sha `935622324ad136b1c970963c5c1331143677717e39c33d5c62bdbb19f0492fe2`; `.api.json` **0 bytes differ** | 10,517 B sha `4e59e6265c5d5addc84bfa6ed4c37240da457878d9139243389f238e32726f39`; `.api.json` **0 bytes differ** |
| mp4 (in `runs\<arm>\`) | 6,397,658 B sha `bab4112003d81683df225aa536d2603462d0df9cc01b35800e4a6b174348bf53` | 5,654,344 B sha `f58198551261f1beb7ac555703f2a578440110497bf532682e4d3766052ea788` | 5,842,735 B sha `07ac2f7cb36bda07f54a9185295c45f011efece143c16c2f2be0b0eca3c5003c` |
| frames / res / fps | **481** packets = objective 481; 768x1344; `24/1` | same | same |
| audio | stream 1 `aac` 32000 Hz 2ch, objective `audio=true` | same | same |
| format duration | 20.041688 s (duration never used as a frame count) | same | same |
| black / freeze | objective `blackfreeze=[]`; harness chain re-run rc=0, **0 events** | same | same |
| render seconds | **827.7 s** (13.8 min), 1 attempt, no redo/STUCK/OOM | **837.7 s** (14.0 min), 1 attempt | **1098.9 s** (18.3 min), 1 attempt |
| status.log | `JOB start` 22:21:37 CT, `JOB end ... ok`, `OBJECTIVE ... ok=True`; `JOB error|CLIP_SKIP|SKIP|redo|STUCK|OOM|Complete`: no match | `JOB start` 23:12:00 CT, `JOB end ... ok secs=837.7` | `JOB start` 23:47:34 CT, `JOB end ... ok secs=1098.9` |
| result.json | `ok=true rc=0 note="run_graph_job rc=0 (ok)"` wall_min 14.9, finished 22:36:32, budget_used_min 342.0 | `ok=true rc=0` wall_min 14.5, finished 23:26:28, budget_used_min 356.5 | `ok=true rc=0` wall_min 18.8, finished 2026-10-23T00:06:22, budget_used_min 375.3 |
| control output | CTRL mp4 5,781,091 B sha `1dc59ed446e4cf1a5ecbfa18616a311b658d1acc281a3624974732373ba42fda`, 481 packets, `secs 809.7` | BASE seg3 (above), old run 855 s wall (p7 result.json) | CTRL `secs 809.7` |

## 4. The stills (viewing evidence) and their coverage
- `runs\ali147_pool_promptv2_s51080000\ali147_pool_promptv2_s51080000_stills_contact.png` 1,746,695 B sha `d7695898f5a91a5285443d9e551f0004ebd68f86aec94aa5b1ef67d5c3cd4359` - 1816x900 RGB, 12 tiles.
- `runs\ali147_pool_promptv2_seg3_s51080002\ali147_pool_promptv2_seg3_s51080002_stills_contact.png` 1,721,133 B sha `2a3762ab13139662acb88f6ded88b2f1d028fd1c2dafdb43147e7787a5a81879` - 1816x900 RGB, 12 tiles.
- `runs\ali147_pool_dense_s51080000\ali147_pool_dense_s51080000_stills_contact.png` 1,675,216 B sha `759583d6cc5878b0fba3f5c76dc7395f4db3719705388d87f9ad831271fdd864` - 1816x900 RGB, 12 tiles.
- Control sheets: CTRL `..._stills_contact.png` 1,746,746 B sha `68412d708595d54885c27d9810585816499386492622a64fa21921647eccf137`; BASE seg3 sheet 1,689,027 B sha `18d19d27d2d95dba06d39b994a6161922b2f868ca6e4206426b341161fbdb268`.
- Coverage (measured from `run_graph_job.py`'s own windows, `t=10/20/30/40/50 s ±1.5 s`, 0.5 s steps, `t <= dur-0.05`): for a 20.0417 s / 481-frame clip the tiles are t=8.5-11.5 s (frames 204-276, so the 243-frame seam is bracketed) and t=18.5-19.5 s (frames 444-468). **Frame 0 and frame 480 are never sampled** (the t=20.0 tile is dropped); the required frame-0/243/480 comparison therefore cannot be made from existing files - it needs fixed-frame stills (Max/Derek side), which do not exist.
- Side-by-sides: `find C:/AI/community/runs -name "sbs_*.mp4"` = **0 files** (whole tree). `sbs_fix1_refsheet.mp4` existed at 00:09 CT today and is gone; nothing newer than the dense render exists. So `sbs_ali147_pool_promptv2.mp4`, `sbs_ali147_pool_promptv2_seg3.mp4`, `sbs_ali147_pool_dense.mp4` and the frame 0/243/480 stills are **not present and are not Forge files** (`run_graph_job.py` has no hstack / fixed-frame path) - reported as pending Max/Derek per the TASKS sbs rule ("a missing sbs is not a failure"), not as a failed render.
- The `review/` dirs in the two prompt arms (`review\contact_sheet.png`, `review\params.json`, `review\report.md`) are harness/second-review files, not Forge outputs; `params.json` = 1018 B / 1017 B with the seed/frames/size/lora-fields (this is the source of the "lora_1..5" name list: those fields belong to the 6-clip Extender graphs, not to these per-segment graphs).

## 5. graph_diffs (all three arms, separate files)
| arm | file | bytes | sha256 | hunks | removed/added |
|---|---|---|---|---|---|
| PV2-1 | `runs\ali147_pool_promptv2_s51080000\graph_diff.txt` | 13,725 | `f8d0b01c9f6c623ef88447886d256100c420ac1e2a13b1b7ef5cc9f88ce8e8f1` | 3 (`@@ -47,7`, `@@ -72,7`, `@@ -289,7`) | 3 / 3 (`$c0.prompt`, `$c1.prompt`, `$save.filename_prefix`) |
| PV2-2 | `runs\ali147_pool_promptv2_seg3_s51080002\graph_diff.txt` | 13,806 | `1d9cd4de52757d32b3242d6916b613d074b226783381a727a86e37c7b855c33a` | 3 (`@@ -98,7`, `@@ -181,7`, `@@ -341,7`) | 3 / 3 (same three keys) |
| PV2-3 | `runs\ali147_pool_dense_s51080000\graph_diff.txt` | 1,241 | `5ec6bd9c32c9ecb14f93c2f4474dca27508789e0c7803e15e4ca44cc755e28e8` | 2 (`@@ -140,31 +140,13`, `@@ -289,7 +271,7`) | 20 / 2 (`$m_vsa` block deletion + `$m_shift.inputs.model` rewire; prefix) |
Each prompt is one escaped graph line, so 3 prompt/prefix changes = 3 hunks (the "5 hunks" expectation in the PV2-1 review note counted prompt lines, not graph lines; the real gate is the node-level comparison below). `find runs -name "request.api.json"` = 3 arms (PV2-1, PV2-2, PV2-3), each with its own `graph_diff.txt`.

## 6. Fairness - the one variable per arm, node by node
Method: `json.dumps(node, sort_keys=True)` per node, both graphs, printing the exact sets.
- **PV2-1 vs CTRL**: 25 nodes each, 25 shared, control-only `[]`, arm-only `[]`; differing shared nodes **exactly `['$c0','$c1','$save']`**; changed keys exactly `$c0.inputs.prompt`, `$c1.inputs.prompt`, `$save.inputs.filename_prefix`; node key set identical; input key sets unchanged; **22/25 nodes byte-identical**.
- **PV2-2 vs BASE seg3**: same shape - 25/25 shared, control-only `[]`, arm-only `[]`, differing exactly `['$c0','$c1','$save']`, 22/25 byte-identical.
- **PV2-3 vs CTRL**: 24 vs 25 nodes; control-only `['$m_vsa']` (deleted `BlockSparseAttention`), arm-only `[]`; differing shared `['$m_shift','$save']`; changed keys exactly `$m_shift.inputs.model` `["$m_vsa",0]` -> `["$m_attn",0]` and the prefix; prompts CTRL-verbatim; `$noise`, `$m_attn`, `$img` byte-identical. No frame/length/scheduler/VAE/CLUI/model-chain node touched.

## 7. Shared settings (measured from the graphs - the "at 8 steps" identity)
Identical inside each arm/control pair (proved by §6):
- seed `$noise.noise_seed` = **51080000** (PV2-1/CTRL/PV2-3), **51080002** (PV2-2/BASE seg3) - one shared RandomNoise feeding both samplers.
- steps/sampler: `$s0_sched`/`$s1_sched BasicScheduler steps=10 denoise=1.0 scheduler="simple"`, `$ksel KSamplerSelect sampler_name="euler"`, guides `$s0_guide`/`$s1_guide BasicGuider`. (The 8-step TURBO identity is the checkpoint name; the scheduler steps stay 10 = unchanged.)
- length/frame budget: `$c0 length=243`; `$win1 MiniMaxH3GuidedContinuationWindow extension_frames=238 overlap_frames=22` -> 243+238 = 481 raw; `$c1 length=["$win1",1]`.
- resolution/fps: 768x1344 on `$c0`/`$c1`; `$mkvid CreateVideo fps=24`.
- model chain: `$unet UNETLoader "10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors"` -> `$m_attn ModelAttentionBackend "comfy kitchen attention"` -> `$m_vsa BlockSparseAttention` (deleted only in PV2-3) -> `$m_shift MiniMaxH3SigmaShift shift_video=10.0 shift_audio=3.0` -> guides/samplers; `$vvae minimax_h3_video_vae_int8_convrot.safetensors`, `$avae minimax_h3_audio_vae_fp32.safetensors`, `$clip CLIPLoader "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors" type="minimax"`.
- reference image: `$img LoadImage "community/POOL_768x1344.png"` -> `$c0.ref_images.ref_image_1`, `$c0.ref_image_size="match"` (Autogrow group, `<Picture 1>`). File: `C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/POOL_768x1344.png`, PNG 768x1344 RGB, sha256 `9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075`. The approved source portrait `C:\Users\derek\5slock\approved_characters\POOL\COND_POOL_BIKINI_PORTRAIT.jpg` (sha `fc4f4ea4…`) is a different image; every graph loads the input-dir PNG.
- **LORA stack: none in any of these per-segment graphs** - no `LoraLoader`/`$lora_*` node exists in CTRL, BASE seg3, PV2-1, PV2-2, PV2-3 (the LORA stack belongs to the 6-clip Extender/`batch_queue` minute graphs, e.g. FIX4's `$ext` chain). So "no LORA added, removed or weighted" is verified as identically empty, and the `loop_policy=platform_stream` + `ph_all_*` PH*2 hard negatives are untouched by all three arms.
- output: `$save SaveVideo filename_prefix="community/<arm>/<arm>"` - the only non-prompt key in the prompt arms.

## 8. VSA / dense at 481 (PV2-3)
- The VSA module is **ComfyUI core**, not the Extender: `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_sparse_attention.py`, `class BlockSparseAttention` at **line 353** (its extension at :433), file sha256 `de202f2b5eb753a5748e1c6452cdc10cdf28834ffd8f8bb6acfaf6f643de9692`, mtime 2026-10-01; ComfyUI repo HEAD `6b747c0428c343e1417219641db93a4fb7cb69ae` ("ComfyUI v0.38.0", 2026-09-29) - also the last commit touching that file.
- MiniMax H3 **Extender** repo HEAD `0861230cc38cbfbdb8d7b97dd9473f536a253c0b` ("Bump version from 3.0.12 to 3.0.13", 2026-10-20): the VSA path does not touch the Extender - the control chunks are the same nodes in both arms (PV2-3 deletes only `$m_vsa` and rewires `$m_shift`).
- VSA parameter set (identical in CTRL / BASE seg3 / PV2-1 / PV2-2, deleted in PV2-3): `selection="vsa"`, `selection.keep_percent=10`, `min_tokens=12288`, `extra_tokens=256`, `start_percent=0.2`, `end_percent=1.0`, `dense_blocks=""`, `sink_conditioning="exact_kv_and_rows"`, `verbose=false`. (`BlockSparseAttention` is a core node, so it is absent from `specs\extender_object_info.json`, the 15-entry Extender snapshot.)
- dense vs VSA at 481 frames, same seed/steps/resolution: VSA ON = **809.7 s** (CTRL), VSA OFF (dense) = **1098.9 s** = **1.357x slower**, the slowest 481-frame render in `runs\`. So at this shape sparse attention is the faster path, not the slower one.
- PV2-3's request used `minutes: 120` (`p7\jobs\request_iter12.json`); ralph.ps1 uses that only as a per-attempt timeout (`--timeout minutes*20` s, `--max-redo 2`), never as a budget cost: a `minutes: 60` request gives 1200 s/attempt against a 1098.9 s render (1.09x margin). The larger request is the correct choice and is not a failure.

## 9. Render seconds across every 481-frame run (objective.json; both JSON shapes handled)
| secs | frames | run |
|---|---|---|
| 706.8 | 481 | `ali147_pool_fix5_s51080000` |
| **809.7** | 481 | `ali147_pool_ctrl_s51080000` (CTRL baseline) |
| **827.7** | 481 | `ali147_pool_promptv2_s51080000` (PV2-1) |
| **837.7** | 481 | `ali147_pool_promptv2_seg3_s51080002` (PV2-2) |
| 857.5 | 481 | `ali147_pool_fix1_s51080000` |
| 902.7 | 481 | `ali147_pool_refsheet_s51080000` |
| 978.1 | 481 | `ali147_pool_refsheet_b_s51080000` |
| **1098.9** | 481 | `ali147_pool_dense_s51080000` (PV2-3, VSA off) |
| 3004.9 | 1433 | `ali147_pool_fix4_s51080000` (excluded from the 481 ratios) |
Prompt text is not a speed factor: PV2-1 = +2.2% and PV2-2 = +2.2% vs their controls at identical seed/steps/frames = noise; the only measured latency effect in this family is VSA off = +35.7%.

## 10. Next target (what is renderable now)
- **PV2-4 (K1 + SNOFS)**: NOT renderable. `ComfyUI\models\loras` has no `h3` subdirectory and no "vagina" match, so the required `h3\Vagina_minimax-h3_epoch20.safetensors` is absent (nearest names: `PenisV2_minimax-h3_epoch60.safetensors`, `hm_nsfw_mis_doggy_only_v16_r32_384_minimax-h3_epoch170.safetensors`). No SNOFS-named **reference image** exists in `ComfyUI\input`, `5slock\approved_characters` (POOL = `COND_POOL_BIKINI_PORTRAIT.jpg`, `POOL_face_crop_250.png`, `POOL_face_up_1024.png`; REF_SHEETS_2026-10-19 = RS001-RS016) or `5slock\plans`. The only SNOFS artefacts on disk are the **Klein LORAs** `models\loras\klein_snofs_v1_1.safetensors` / `klein_snofs_v1_4.safetensors` (1,090,563,760 B each). Gate C fails; no download, no copy, no LORA.
- **PV2-5 (KV31 + SNOFS, accepted-prompt Klein 9B bf16)**: NOT renderable. `C:\Users\derek\cufy` contains no `kv31`/`inference_master` card, so `...\cards\qwen-image-2-9b\kv31_inference_master.safetensors` is absent; `specs\prompt_v2\stillfix_A_anatomy_ref_klein.txt` does not exist; `runs\pool_stillfix_a` does not exist. No render, no download.
- **Budget** (`logs\p7_budget.json`, updated 2026-10-23T00:06:22): `cap_min=390`, `used_min=375.3`, `job_cap=27`, `jobs=26` -> **14.7 GPU minutes and 1 job slot left**; the Klein arms are estimated 30-40 min each, so neither is submittable this run even with assets present.
- So the only GPU-free target in scope was this report; the next real target is a Derek decision (supply the K1 card + a named SNOFS reference, supply the KV31 card + the accepted-prompt file, or close ALI-147 on the reported methods).
- `p7\JOB_REQUEST.json` is absent (nothing submitted this iteration). Archived requests: `request_iter12.json` (dense, 481/0/**120 min**), `request_iter01.json` (fix4 1443/tol 24/180), `request_iter02.json` (refsheet_b 481/0/60).

## 11. Stills and side-by-sides - paths, SHA256, coverage
Contact sheets (the only per-arm visual files; harness-generated by `run_graph_job.py`, in each `runs\<arm>\`):
- PV2-1 `runs\ali147_pool_promptv2_s51080000\ali147_pool_promptv2_s51080000_stills_contact.png` 1,746,695 B sha256 `d7695898f5a91a5285443d9e551f0004ebd68f86aec94aa5b1ef67d5c3cd4359` - 1816x900 RGB, 12 tiles.
- PV2-2 `runs\ali147_pool_promptv2_seg3_s51080002\ali147_pool_promptv2_seg3_s51080002_stills_contact.png` 1,721,133 B sha256 `2a3762ab13139662acb88f6ded88b2f1d028fd1c2dafdb43147e7787a5a81879` - 1816x900 RGB, 12 tiles.
- PV2-3 `runs\ali147_pool_dense_s51080000\ali147_pool_dense_s51080000_stills_contact.png` 1,675,216 B sha256 `759583d6cc5878b0fba3f5c76dc7395f4db3719705388d87f9ad831271fdd864` - 1816x900 RGB, 12 tiles.
- Control sheets for comparison: CTRL `runs\ali147_pool_ctrl_s51080000\ali147_pool_ctrl_s51080000_stills_contact.png` 1,746,746 B sha256 `68412d708595d54885c27d9810585816499386492622a64fa21921647eccf137`; BASE seg3 `runs\p7_r2_c3_pmot_full_pool\p7_r2_c3_pmot_full_pool_seg3_stills_contact.png` 1,689,027 B sha256 `18d19d27d2d95dba06d39b994a6161922b2f868ca6e4206426b341161fbdb268`.
- What the sheets do and do not show: `run_graph_job.py` samples `t = 10/20/30/40/50 s ±1.5 s` at 0.5 s steps with `t <= dur-0.05`, so for these 20.0417 s / 481-frame clips the tiles are t=8.5, 9.5, 10.5, 11.5 s (frames 204/228/252/276 - the 243-frame seam is bracketed) and t=18.5/19.5 s (frames 444/468) plus the 0.5 s offsets. **Frame 0 and frame 480 are never sampled** (the t=20.0 tile is dropped by the `t <= dur-0.05` guard), so the requested frame-0/480 comparison cannot be made from these sheets - it needs fixed-frame stills, which do not exist (see next bullet).
- Fixed-frame stills (frame 0 / 243 / 480): **none exist** - the per-arm listings (printed in `ali147-pv26-report-probe-20261023.txt`) contain only `<arm>.mp4`, `<arm>.mp4.json`, `<arm>_stills_contact.png`, `objective.json`, `status.log`, the graphs, `graph_diff.txt` and, for the prompt arms, `PROOF.md`/`fairness.txt` + a harness-owned `review\` dir.
- Side-by-sides: `find C:/AI/community/runs -name "sbs_*.mp4"` = **0 files** over the whole tree (not depth-limited). `sbs_fix1_refsheet.mp4` existed at 00:09 CT today and is gone; nothing newer than the dense render exists. So `sbs_ali147_pool_promptv2.mp4`, `sbs_ali147_pool_promptv2_seg3.mp4`, `sbs_ali147_pool_dense.mp4` and the frame-0/243/480 stills are **sbs/stills pending Max**: `run_graph_job.py` has no hstack / fixed-frame path, so they are Max/Derek files by the sbs rule, not Forge outputs, and their absence is not a failed render.
- The harness second-review files exist in the two prompt arms (`runs\<arm>\review\contact_sheet.png`, `params.json` 1018/1017 B, `report.md`); they are harness-owned, not Forge outputs. The `review\params.json` `lora_1..5` fields are the reason a LORA name list appears in some audits: those fields belong to the 6-clip Extender graphs, not to these per-segment graphs, which contain no LORA node at all (section 7).

## 12. Self-audit (PV2-6 gate: PASS/FAIL summary, file count, byte count, zero failed checks)
- `notes\ali147_pv26_report_probe.py` -> `ali147-pv26-report-probe-20261023.txt`: **PASS=77 FAIL=0**, ends `ALL CHECKS PASS`.
- `notes\ali147_pv26_card_probe.py` -> `ali147-pv26-card-probe-20261023.txt`: **PASS=3 FAIL=0**, ends `ALL CHECKS PASS`.
- `notes\ali147_pv26_settings.py` (table only, no gate lines), `notes\ali147_pv26_commits.py` (info only), `notes\ali147_pv26_inventory.py` (file count + byte count).
- Files written by this iteration: **13 files, 159,036 bytes**, itemised with sizes + SHA256 prefixes in `notes\ali147-pv26-inventory-20261023.txt` - 6 scripts (`notes\ali147_pv26_report_probe.py`, `_card_probe.py`, `_settings.py`, `_commits.py`, `_linerepr.py`, `_inventory2.py`), 4 probe outputs (`ali147-pv26-report-probe-20261023.txt`, `-card-probe-`, `-settings-`, `-commits-`), the earlier report copy `notes\ali147-report-pv2-20261023.md`, this report `notes\ali147_REPORT_pv2.md`, and one copy at `runs\ali147_pool_promptv2_s51080000\REPORT_pv2.md` (sha256 `fdb497063e1c0b6dea043a50e847b3aee12faefc94b69ff9ed8cb074aeacdab5`) written before the current line's filename was read; kept, because deletes are not allowed to Forge. Reports live under `notes\` per the 19:46 CT rule.
- **Failed checks after the final run: 0.** No GPU, no node list, no render, no job request, no vision judge, no download, no image viewing, no deletes.
- **AGENTS.md: no line added.** The `## Learnings` section is at **16 bullet lines**, already over its own "max 15 lines; Max prunes at review" cap, so adding a 17th is not allowed. The new facts for Max to prune into it: (1) for a 481-frame / 20.04 s clip the contact sheet is 12 tiles = frames 204-276 + 444/456/468, so **frame 0 and frame 480 are never sampled** (the t=20.0 tile is dropped by `t <= dur-0.05` in `run_graph_job.py:45-52`) - the frame-0/480 comparison needs fixed-frame stills, which the harness never writes; (2) **VSA OFF is slower than VSA ON at 481 frames** (1098.9 s vs 809.7 s = 1.357x), so "dense" is not a speed-up arm; (3) a graph request's `minutes` is a **per-attempt timeout, not a budget cost** (ralph.ps1:270-271 `--timeout minutes*20`), so a slow arm should ask for a bigger `minutes` (PV2-3 needed 120); (4) `p7\jobs\<id>.result.json` = the `ok`/`rc`/`wall_min`/`started_at`/`finished_at`/`budget_used_min` source (not in ralph.log), and `objective.json` comes in two shapes (loop arms with `attempts:[{secs}]`, driver-rendered CTRL flat with no `request.api.json`).

## 13. Sign-off
METHOD_ONLY: each arm is one measured variable - PV2-1/PV2-2 = the two prompt strings + the output prefix (22/25 nodes byte-identical to their controls); PV2-3 = deletion of `$m_vsa` + its rewire + the prefix, prompts CTRL-verbatim. Objectives all pass (481 packets, 768x1344, 24/1, audio present, 0 black/freeze events, 1 attempt each). **KEEP is Derrick's.**
