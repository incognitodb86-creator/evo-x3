# Automated LOCAL quality review + optimisation loop for AI video (H3 / LTX-style image-to-video) - 2026-10-20
For Derek's AlienPc (RTX 5070 Ti 16 GB, llama-swap exclusive group, ComfyUI H3 pipeline). Everything below runs locally: ffmpeg + CPU
metrics + a local VLM judge through llama-swap. No cloud rendering, no cloud vision. Fictional adults 21+ only.
Implementation: `C:\AI\community\scripts\p6_review.py` (+ `scripts\tests\test_p6_review.py`), playbook `C:\AI\community\p7\KNOBS.md`,
loop tasks `C:\Users\derek\5slock\ralph-community\TASKS.md` section P7.

## 1. What the literature and tool docs say (short)
- **Split "video quality" into disentangled dimensions.** VBench separates temporal quality (subject consistency, background consistency,
  temporal flickering, motion smoothness, dynamic degree) from per-frame quality (aesthetic, imaging) and from prompt alignment, because one
  overall number hides failure modes - e.g. a static video scores well on flicker and consistency, which is why it also measures dynamic
  degree. https://arxiv.org/abs/2311.17982 , https://github.com/vchitect/vbench/
- **Flicker can be measured cheaply.** VBench's temporal-flickering score is the mean absolute difference between consecutive frames
  (normalised (255 - MAE)/255) on static scenes; it correlates ~99% with human preference across its benchmarks.
  https://openaccess.thecvf.com/content/CVPR2024/supplemental/Huang_VBench_Comprehensive_Benchmark_CVPR_2024_supplemental.pdf
- **Adjacent-frame metrics miss long-horizon drift.** A proposed VBench dimension samples frame pairs at growing gaps (2-50 frames) because
  models with near-perfect local smoothness can still drift badly over a long rollout - exactly the risk for 20 s continuation segments.
  https://github.com/Vchitect/VBench/issues/206
- **Learned video evaluators use 5 human-aligned aspects**: visual quality, temporal consistency, dynamic degree, text-to-video alignment,
  factual (common-sense/physics) consistency; VideoScore reaches Spearman ~0.77 with humans, far above older metrics, and its prompt feeds
  16-48 sampled frames. Even human raters disagree a lot on some aspects (low kappa), so expect noise. https://arxiv.org/html/2406.15252v3 ,
  https://huggingface.co/TIGER-Lab/VideoScore
- **Pairwise vs absolute.** GenArena finds pointwise VLM scores self-inconsistent (Krippendorff alpha ~0.52), with many false ties and ~18%
  contradictions with humans, and recommends pairwise judging with swapped order to cancel position bias
  (https://www.alphaxiv.org/abs/2602.06013). But Tripathi et al. show pairwise protocols are easier to sway with distractor features
  (preference flips ~35% vs 9% for absolute scores) (https://doi.org/10.48550/arxiv.2504.14716). UVE finds MLLM video judges still trail humans
  by >30 points on pairwise, weakest on structure/motion naturalness, and that converting pointwise ratings into pairwise choices helps weaker
  models (https://arxiv.org/html/2503.09949v3). **Practical answer: use both** - fixed-rubric absolute scores AND swapped-order pairwise
  comparisons, count a pairwise win only when both orders agree, and add model-free metrics as a third, independent signal.
- **Ensembles of weak VLM judges do not automatically help**; adding less reliable judges can add noise.
  https://arxiv.org/html/2503.05977 - so one good local judge (Qwen3-VL-8B) at temperature 0, plus metrics, beats averaging mismatched models.
- **Frame sampling for the judge.** Qwen3-VL's own video path samples ~2 fps with min/max frame and pixel budgets and passes timestamps
  (https://github.com/QwenLM/Qwen3-VL/blob/main/qwen-vl-utils/src/qwen_vl_utils/vision_process.py). Through llama.cpp's OpenAI endpoint,
  plain multiple images carry no temporal positions (community report: https://github.com/Cobdog/llama-video), so label frames explicitly
  (F1..Fn + timestamp) in a time-ordered contact sheet - the same pattern Switchyard already uses (3x3 sheet in `director\review.py`).
- **Local objective metrics in ffmpeg/OpenCV**: ffmpeg `siti` (ITU-T P.910 spatial/temporal information, legacy 11/21 definition),
  `signalstats`, `blurdetect`, `scdet`, `freezedetect` are all CPU filters. https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/siti.html ,
  https://www.ffmpeg.org/ffmpeg-filters.html
- **Burn/oversaturation knobs in LTX-style pipelines**: LTX-2 docs recommend guidance rescale 0.5-0.7 to prevent oversaturation, CFG ~3-3.5
  and STG ~1 for the guided (non-distilled) pipeline, and note distilled checkpoints do not use CFG/STG; shorter clips (~121 frames) drift less.
  https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/docs/multimodal-guidance.md ,
  https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-pipelines/docs/pipeline-selection.md ,
  https://huggingface.co/docs/diffusers/main/en/api/pipelines/ltx2 . On THIS pipeline (10Eros H3 8-step turbo, BasicGuider = CFG 1) the
  equivalent burn lever is the H3 Anti-Burn LoRA on continuation chunks, not CFG.

## 2. Review design used here (p6_review.py)
**Sampling.** One window per beat (the community 20 s segment = 2 beats of ~10 s; Switchyard = 6 equal windows). Per window 6 frames evenly
spread, skipping 0.25 s at each edge (joins/cuts), 320 px wide, tiled 3x2 with "F1 12.3s" labels (~1k image tokens). Per video one global
sheet of 12 frames (240 px, 4x3) for identity across cuts, pacing and drift. The approved reference still (D15) is attached as identity anchor.
**Fixed rubric (1-10 integers, anchors 9-10 real-footage ... 1-2 broken, "use the full scale"):** motion_quality 0.15, temporal_consistency
0.15, burn_exposure 0.10, identity_consistency 0.20, prompt_adherence 0.10 (vs the shot-list beat text only - never the generated prompt
files), artifacts 0.20, pacing_cuts 0.10; short reasons per dim; hard flags identity_break, severe_burn, body_horror, frozen, broken_cut.
Judge sees blind labels only (V1..V5), temperature 0, JSON mode, one retry on unusable JSON.
**Objective metrics (CPU, ~10 s per minute of video):** luminance flicker (std of high-passed per-frame mean luma, cuts/seams excluded),
texture flicker (temporal 2nd difference / 1st difference), within-shot saturation drift and highlight clipping late vs early (burn creep),
within-shot sharpness drift (Laplacian variance), within-shot Lab colour drift, freeze fraction, seam jump ratio at stitch joins, cut count.
Drift is measured inside shots (segments split at detected cuts) so an intended cut to a close-up is not counted as drift. Mapped to 0-10
with first-pass thresholds; weight only 0.20 because these are proxies.
**Aggregation.** abs = 0.7 x weighted dims (dim = 0.6 window mean + 0.4 global call) + 0.3 x weakest window (weakest-link, like the director
rubric). pairwise = Bradley-Terry over swapped-order pairs (consistent win = 1, disagreement or tie = 0.5), expressed as field win-rate x10.
composite = 0.40 abs + 0.40 pairwise + 0.20 objective - 0.75 per hard flag (max 2). A flag counts if the global call or >= 2 windows raise it.
**Parent vs child verdict:** PROMOTE only when the child wins pairwise in both orders and composite >= parent + 0.25, or composite >=
parent + 0.75 alone; never with more hard flags.
**Cost:** 5 videos = 30 window calls + 5 global + 20 pairwise = 55 calls, ~20-30 min including model load on the 5070 Ti.
**Safety:** gpu_guard.ps1 first (fail closed, ignores only its own pid), nvidia-smi utilisation check (gpu_guard cannot see llama-swap
benches), takes `C:\AI\locks\gpu-render.lock` while judging, unloads the judge at the end, refuses beat text that fails the adults-only guard.

First objective-only preview of the five P6 videos (no model, 2026-10-20 19:5x CT, `C:\AI\community\p7\P6_METRICS_PREVIEW.md`):
cuts 8.63, cuts_ab05 7.88, community 7.02, ab05 6.67, switchyard 4.42 (switchyard: highest flicker 0.89, seam jumps 5.1x, late highlight
clipping 0.20; community/ab05: ~22-25% within-shot saturation creep). Preview only - the VLM + pairwise review decides.

## 3. Optimisation loop (P7)
- **Keep top 3** from the full review (Switchyard stays as a reference if it places, since it is not a batch_queue shot list).
- **One knob per probe** so the effect is attributable: anti-burn strength (null/0.3/0.5/0.7, chunk 2 only), steps 10->12, seed, cut timing
  (cuts variants), one fixed prompt clause (identity / exposure / motion). Knob chosen from the parent's lowest rubric dimension.
  CFG/guidance and sigma shift are not knobs on this distilled H3 graph (BasicGuider; shift locked 10/3 by C2).
- **Probe before a full minute.** Re-render only the parent's weakest 20 s segment at final size with the same seed and the SAME prompt
  files (copied from the parent, so the LLM does not reword them) - an apples-to-apples A/B against the parent's existing segment, ~15 min,
  vs ~42 min for a full minute. Low-res drafts were rejected as probes: a different latent size changes the result, so a draft win does not
  transfer reliably to the 768x1344 final.
- **Promote only on a win**, re-review the promoted full minute against its parent with the same rubric, keep the leaderboard.
- **Budget (hard, harness-enforced):** 3 rounds x 3 slots, max 1 full render per slot per round and 3 full renders total, 360 GPU min /
  16 jobs. Expected: rank 25 min + 9 probes ~135 min + 3 probe reviews ~27 min + up to 3 full renders ~130 min + full reviews ~20 min +
  final rank ~15 min = ~5.5 h GPU worst case inside the cap; plus ~19 Forge iterations x ~4-6 min of LLM time.
- **GPU ownership:** the loop LLM and ComfyUI share one exclusive llama-swap group, so the model never starts GPU work; it writes
  `p7\JOB_REQUEST.json`, and ralph.ps1 runs it after pi exits (render through batch_queue.py, review through p6_review.py), then waits for
  completion before the next iteration.

## 4. Known limits
- An 8B VLM on stills cannot see motion directly; motion/flicker judgments come partly from frame sequences and partly from the metrics.
  UVE shows MLLMs are weakest on structure and motion naturalness - Derek's eye stays the final word.
- Objective thresholds are first-pass (calibrated on the five P6 videos only); re-check after the first full review.
- No local face-embedding identity metric (would need a new install); identity relies on the judge + reference still.
- Reusing a probe's segment inside the promoted full render would save ~14 min per promotion; not done (keeps the harness simple).
