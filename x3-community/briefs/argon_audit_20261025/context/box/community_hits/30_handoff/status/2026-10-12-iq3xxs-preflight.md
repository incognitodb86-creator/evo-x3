# IQ3_XXS preflight + Step 0 — AlienPc Local AI, 2026-10-12 ~5:30-5:50 PM CT (read-only)

## Since 10-11 (timeline from AlienPc mtimes; no gbrain folder found on PC, agent-ref newest = 10-11 8:37 AM handoff)
- 10-11 8:52 AM: lease mirror D:\AI\alienpc-shell-lease-mirror.md -> Derekgrolbot (still says so).
- 10-11 PM: Heretic 27B builds/kv work (D:\AI\director-heretic-build, llama.cpp-kvstream(-q8v), director-kv128, forge-bench, live-merge + backup-2026-10-11-merge, forge-host 9 PM); mmproj 27B downloaded 5:18 PM.
- 10-12 7:45-8:45 AM: SC117 IQ2_XS installed in upstream Strata (v0.1.42), tested, Switchyard profile e2e (RESULTS-sc117-iq2xs.md).
- 10-12 ~9:15 AM-3 PM: SC117 self-opt (SELF-OPT-2026-10-12.md): --prefill auto, T 0.6 applied.
- 10-12 12:45-12:50 PM: batch-sc117-2026-10-12 (clip-03 DONE + STOP). 1:02 PM searxng + websearch tool set up.
- 10-12 2:54-3:38 PM: sergqwer fork cloned C:\AI\strata-nvfp4 @7b00d30; NVFP4-GPTQ download STALLED: pack experts .incomplete 48.53 GB (3:35 PM), ple-fp8.gguf 47.68 GB, dense 5.58, embd 1.18; C: now 3.6 GB free. No download process running.
- Running now: SC117 Switchyard launcher (sy_strata_launch.py, port 8080, since 2:36 PM; VRAM 565 MiB so model not loaded), director ui, searxng.
- Left: finish/clean NVFP4 download (needs disk), whole iq3xxs plan (A..E).

## Lease
Mirror names Derekgrolbot (out of usage, no job of its own running). Took HOLD on box: 30_handoff/status/2026-10-12-1735-alienpc-lease-to-alienpc-local-ai.md. PC mirror not rewritten (read-only). Shell flapped twice ("temporarily unreachable"), recovered after 1-min wait.

## Inventory
- Driver 616.92 (>=580 OK). GPU 565/16303 MiB, no compute model process. ComfyUI not running; llama-server not running; strata engine not loaded (launcher python up).
- Free RAM 47.4 / 63.7 GiB -> FAILS the 50 GiB gate (director ui, searxng, SC117 launcher, Edge, etc. running).
- Disk free: C 3.6 GB (NVMe SK hynix PVC10 1024GB, SSD, holds C:\AI) | D 26 GB (Avolusion PRO-5X 11 TB USB HDD) | E 169.2 GB (ASMT 2115 2 TB USB SSD).
- Antigravity CLI: C:\Users\derek\AppData\Local\agy\bin\agy.exe (logs D:\AI\director\agy-logs).

## Strata installs / models
- Upstream: C:\AI\strata (Niko1221/Strata, 61b3fb5 2026-10-10), data C:\AI\Strata-data.
- Fork: C:\AI\strata-nvfp4 (sergqwer @7b00d30), no .venv yet; data C:\AI\Strata-nvfp4-data.
- SC117: C:\AI\Strata-data\models\sc117-flashnext-abliterated-iq2xs (36.94 + 26.82 GiB + mmproj 0.85), pack C:\AI\Strata-data\packs\sc117_iq2_xs.
- NVFP4-GPTQ: partial (above, ~105 GB on C incl .incomplete).
- ISTA IQ3_XXS: NOT present. Coder IQ1_M: NOT present. alesha Huihui vector: NOT present. Bundled speed-projection vectors exist in both repos' data\. Heretic 27B: C:\AI\models (9.84 GiB).

## Forge default + SC117 baseline
- Live: C:\AI\strata\strata-sc117-switchyard.json (profile coding_sc117_strata, port 8080): strata.exe --pack sc117_iq2_xs --expert-cache auto --prefill auto --spec 4 --spec-min-p 0.5 --mtp mtp-rt --max-context 65536 --kv int8 --kv-resident 32768 --pool-workers 13, vision gpu, reasoning_budget 16384. Build: Strata v0.1.42 (61b3fb5).
- Baseline (SELF-OPT harness bench_ab.py, D:\AI\forge-bench\agy-logs\sc117-selfimprove-2026-10-12\): gen 133-140 tok/s (145 with T0.6), prefill auto ~1300-1450, tools 20/20 (one run 19/20), quality 6/6, MTP accept ~0.76-0.80. RESULTS: 132.6/136.0/126.2 tok/s, 20/20 tools 0 loops, refusals 0 on 3 probes (lockpick, adult joke, violence; not a 20-prompt set). Forge step count: not found. So 130 tok/s now has cited build/context/flags.

## Step 0 (setup.py --help via upstream venv python; START-HERE.bat not run in fork because it would create a .venv)
- Upstream: has --setup, --family coder, --model IQ1_M/IQ3_XXS, --gguf-dir, --vision gpu|cpu, --experimental-speed-projection on|off|GGUF, --port, --context, --check, --no-start. NO --dry-run.
- Fork: has --dry-run (NVFP4 models only), --check, --no-start, --port, --uncensored on|off, --context, --gguf-dir, families incl qwen-nvfp4-gptq. NO --max-context (plan wrong; use --context 65536).
- Help output summarized here only; no log files written on AlienPc (read-only run).

## Update 5:45 PM CT — NVFP4 partial deleted (Derrick approved)
- Deleted ONLY: C:\AI\Strata-nvfp4-data\models\qwen-nvfp4-gptq\.cache\huggingface\download\pack\ZSfNTwiCBHl5TrA11W8Tab735_k=.325e5e0d85c262a8d8278daf73b20696ec877d9a3ff584e57391fa69ad10bc64.incomplete (52,107,741,526 B = 48.5 GiB, mtime 3:35 PM). Exclusive open succeeded (no holder), no nvfp4/hf process; no matching .lock existed. The .metadata files and the finished files were left alone.
- C: free now 52.2 GB. Gap to 120 GB: 67.8 GB. Gap to 76 GB: 23.8 GB.
- Largest on C: (read-only, nothing deleted): Users\derek\HardcoreNSFW-TestRuntime 241 GB; HardcoreNSFW-LTX-Pipeline 184.6; C:\AI\Strata-data 74.7 (SC117, in use); C:\AI\Strata-nvfp4-data 56.7 (ple-fp8.gguf 47.7 + dense 5.6 + embd 1.2, finished pieces of the stalled NVFP4 download); AppData 42 (Roaming\Python 10.8); Downloads 21.8; C:\AI\models 11.3 (Heretic 27B rollback, keep); C:\AI\vlm 9.7; .gemini 8.1; .cache\modelscope 7.9; Desktop 7.1.
- Likely safe candidates (Derrick decides): duplicate gemma_3_12B_it_fp8_e4m3fn.safetensors 12.3 GB (same size and date in both ComfyUI trees); 10Eros_v1-fp8mixed_learned 27.2 GB (older than v1.2); Downloads 21.8; .cache\modelscope 7.9; NVFP4 finished pieces 54.5 (only if arm C is moved to E: or dropped); C:\AI\vlm 9.7 (last modified 10-9). Or put the IQ3_XXS install on E: (169 GB free, USB SSD, slower).

## Update ~6:05 PM CT — SC117 self-work today (read-only)
- Work dir D:\AI\forge-bench\agy-logs\sc117-selfimprove-2026-10-12 (own .git, PHASE1/2A/3A.md uncommitted; Pi sessions pi1/pi2a/pi3a 12:54-3:07 PM).
- Tuning (SELF-OPT-2026-10-12.md): strata-sc117-switchyard.json + strata-sc117-iq2xs.json --prefill 512 -> auto (the JSON was also re-serialized; fit_max_tokens + reasoning_budget_tokens 16384 had been added in the 9:12 AM edit); pi-agent models.json SC117 temperature 1.0 -> 0.6 (D:\AI\director-runs\heretic-f6-cards-2026-10-11\pi-agent). Bench: tools 20/20, quality 6/6, gen ~145 tok/s. .bak files exist; C:\AI\strata has untracked .bak files + sy_strata_launch.py.
- Code (PHASE3A, ~3 PM): D:\AI\forge-bench\obs\recorder.py (git identity -c user.name, auto_commit_error rate limit; was 4,743 error events on 10-11), D:\AI\forge-bench\chain\overnight_batch.py (LESSONS.md carry-over), movie_loop.py committed 5498b11 on branch heretic/obs-2026-10-11-1 in D:\AI\director-runs\obs-2026-10-11-1. Backups *.bak-20261012-selfimprove. Scratch tests: ALL RECORDER / OVERNIGHT_BATCH TESTS PASS, refcopy OK, py_compile OK. recorder.py/overnight_batch.py are untracked/excluded in git, so no commit: the .bak files are the only rollback. Not yet exercised by a real batch.
- Risks: T0.6 has a known loop risk on long tasks; persona C staged, not applied; PHASE3A header names model "sc117-qwen3.8-turbo-abliterated-q4" (does not match IQ2_XS, check); 683 loop/error/thinking-limit keyword hits in pi3a.jsonl (not triaged). D:\AI\director: one commit today 9d4d564 (8:38 AM), clean tree.

## Update — approved C: deletions
- Downloads contents (folder + desktop.ini kept) and C:\Users\derek\.cache\modelscope deleted; 0 skipped. Freed 29.7 GB. **C: free 81.4 GB** (gap to 120: 38.6; above 76 by 5.4).
- gemma_3_12B_it_fp8_e4m3fn: NOT deleted. The two copies are already ONE hardlinked file (fsutil shows both paths; same size + same partial SHA256), so deleting either frees 0 B, and LTX-Pipeline workflows reference it.
- 10Eros_v1-fp8mixed_learned: NOT deleted. Referenced by LTX-Pipeline\ComfyUI\user\default\workflows\10Eros_10SNodes_LikenessGuideHelper_I2V_v3.2.json (+27 files in total: _tmp_*, _cos_community_dl_20260925 old workflows and scripts).
- Earlier C: size numbers double-count hardlinks (real used space is lower).

## ComfyUI installs (read-only)
| Install | Size | torch/CUDA | port/role | last used | nodes | models |
|---|---|---|---|---|---|---|
| C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI | 241 GB | 2.15.0.dev20260928+cu130 / 13.0 (.venv 7.6 GB) | :8189 Max/Flux production (forge-host kit local-video-ops.md L11) | output 10-12 12:14 PM | 40 | 228.8 GB |
| C:\Users\derek\HardcoreNSFW-LTX-Pipeline\ComfyUI | 184.6 GB | 2.11.0.dev20260211+cu128 / 12.8 (.venv 3 GB) | :8188 LTX Recipe B, baseline/H2H only | 10-01 (input 10-09) | 27 | 177.7 GB |
- Neither was running at check time (no python main.py; nothing listening on 8188/8189). Both have extra_model_paths.yaml (contents not read).
- TestRuntime models: diffusion_models 59.6, unet 49.9, text_encoders 48.8, clip 18.7, loras 10.7, vae 6.6, SEEDVR2 3.6, clip_vision 2.4; output 1.9; custom_nodes 1.8; _upgrade_backup_* ~0. All KEEP (production); only candidate = output 1.9 (likely, archive first).
- Duplicates across installs (name+size, >200 MB): gemma 12.3 GB (already hardlinked, 0 to gain), ltx-2.3_text_projection_bf16 2.2 GB (real copy -> hardlink = 2.2 GB).
- Consolidation proposal (not done): keep TestRuntime as the one active install; LTX-Pipeline's unique models (checkpoints 59.1 incl. 10Eros v1/v1.2, loras 37.2, diffusion 27.2) are not duplicates, so merging saves only ~2.2 GB plus the 3 GB venv. The real gain is retiring LTX-Pipeline (:8188, H2H only) and moving its models to E: or D: via extra_model_paths.yaml (~180 GB freed on C:). Risks: :8188 H2H/baseline workflows break, torch 2.11/cu128 vs 2.15/cu130 node incompatibility, and the v1 refs in the workflows above. Needs Derrick.

## Update ~6:10 PM CT — LTX-Pipeline delete: STOPPED at safety check (a), nothing deleted
- LIVE ref: C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\extra_model_paths.yaml block `ltx_pipeline_c` (base_path C:/Users/derek/HardcoreNSFW-LTX-Pipeline/ComfyUI/models/: checkpoints, loras, unet, text_encoders, vae, controlnet, latent_upscale_models). So the :8189 production install loads LTX-Pipeline's models (checkpoints 59 GB incl. 10Eros v1.2, loras 37 GB).
- Other refs (old/logs only): TestRuntime\ComfyUI\user\comfyui_8189_*.log.err (3), C:\AI\agent-ref\sydney-clone-sync-2026-10-11\...\inventory-2026-10-10.txt. No junctions; no process from that folder; :8188 not listening.
- (b) ltx-2.3_text_projection_bf16 in LTX-Pipeline has 1 link (separate copy; TestRuntime has its own copy, same name+size).
- To proceed safely: move the needed models (at least the checkpoints/loras that workflows use) into TestRuntime models or onto E:/LTX_Models (already a shared_vault_e path), then remove the ltx_pipeline_c block. That needs Derrick's approval (config change). C: free unchanged 81.4 GB.

## Update 6:00 PM CT — deletion check + Antigravity job launched
- Deletion check: no live config/script/workflow references derek\Downloads or .cache\modelscope (only an old research note in C:\AI\agent-ref\sydney-clone-sync-2026-10-11). Remove-Item was permanent (not Recycle Bin). extra_model_paths targets: TestRuntime models OK, LTX-Pipeline models OK, E:\LTX_Models MISSING (it was already missing; E: was never touched).
- Job: C:\AI\iq3xxs-test\run.ps1 (Start-Process hidden), wrapper PID 18148, agy PID 16612. Sonnet 5.5 high: RESOURCE_EXHAUSTED (credits too low), so it fell back to gemini-3.8-flash-high (dry-run PONG OK, headless -p). Log logs\job.log; markers logs\<step>.DONE/FAIL, JOB.DONE/JOB.FAIL; RESULTS.md. NVFP4 + Coder IQ1_M deferred (disk); FAIL if C: would drop below 5 GB.
