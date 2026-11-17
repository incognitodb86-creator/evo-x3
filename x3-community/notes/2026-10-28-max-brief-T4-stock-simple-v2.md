# Max brief: T4 stock LokkenJP simple_v2 (2026-10-28 9:25 PM CT)

Derrick's go: "Test it" (9:19 PM CT). Plan: brain 40_projects/max-fix-tests/plans/2026-10-28-2015-terrace-community-settings-test-plan.md, arm T4 = true community baseline. Audit: 60_reviews/max/2026-10-28-terrace-runs-parity-audit.md section 7.

1. Download H3_Turbo_2Pass_ErosMax_b7_simple_v2.json from Hugging Face repo LokkenJP/TenEros_Max_optimized_learned into new run dir C:\AI\community\runs\terrace_dom_q5stockv2_20261028_s51083011 (keep an untouched copy as stock_simple_v2.json). Download every model file it names that is missing (UNet ..._beta7_activation_learned_HQ, text encoder qwen3vl_32b_minimax_h3_int4_convrot, upscaler 3d_fp16, anything else) and install any missing custom nodes (LokkenVideoPostProcessing, ResolutionSelector, ModelPreviewOverrideKJ, H3PowerLoraStack etc). Downloads/installs need no card. If any model file cannot be fetched: STOP and report, no substitutes.
2. Run at its OWN stock defaults (er_sde, sgm_uniform pass 1, ResolutionSelector 0.3 MP, 3d_fp16 megapixels 1.0, ref_image_size match, Add Guide BYPASSED as shipped, Lokken post-process RTX VSR 1.2 ULTRA grain 0.005 as shipped). Only deviations allowed:
   a. start image = the same file B2's LoadImage used (see runs\terrace_dom_q5guide_20261028_s51083007\request.api.json)
   b. prompt = B2's prompt file runs\terrace_dom_q5guide_20261028_s51083007\prompt_seg0.txt, by path, bytes unchanged
   c. seed fixed 51083002 (control_after_generate fixed)
   d. length 243 frames (stock 361)
   e. save filename_prefix community/terrace_dom_q5stockv2_20261028_s51083011/terrace_dom_q5stockv2_20261028_s51083011
   Also add a plain save of the native pre-post-process clip as <tag>_raw.mp4 (extra output only, post-process kept). Note that extra save node in graph_diff.txt.
3. Write graph_diff.txt in the run dir: submitted API graph vs stock_simple_v2.json converted. Must show only a-e plus the extra raw save. Anything else = fix before render.
4. comm.guard_ok must pass before render (youth guard on). ONE GPU window via C:\AI\locks\gpu-render.lock (gpu_window.ps1, gpu_guard IDLE first), -Frames 243 -Timeout 3600. status.log must log JOB start/end.
5. Upload final + _raw.mp4 to QNAP /pi-drop/, verify sizes.
6. Write C:\AI\community\notes\2026-10-28-T4-stock-v2-DONE.md: every widget changed from stock, every download (file, size, source), installed nodes, render seconds, file sizes. Then stop.
PowerShell tool only.
