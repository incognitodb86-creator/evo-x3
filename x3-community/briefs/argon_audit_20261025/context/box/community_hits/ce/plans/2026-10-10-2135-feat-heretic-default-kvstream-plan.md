---
title: Heretic as default coding model + KV-stream 128K - Plan
type: feat
date: 2026-10-10
topic: heretic-default-kvstream
project: alienpc-local-ai
artifact_contract: ce-unified-plan/v1
execution: ops
packs: [fleet]
status: compact (written at ~95% usage; doc review skipped, run it on the next pass)
sources:
  - research/2026-10-09-local-llm-community-variants.md
  - research/2026-10-10-kv-cache-streaming-fork.md
  - research/2026-10-10-alienpc-blackwell-check.md
  - D:\AI\forge-bench\GPU_OPT_TESTS.md (box copy /workspace/gpuopt/GPU_OPT_TESTS.md); Huihui arms and SageAttention test D dropped
---

# Heretic as default coding model + KV-stream 128K - Plan

## Goal Capsule
- **Objective:** Heretic RVN Qwen3.8-27B GSQ-RCO is the only coding/agent model on AlienPc. Run it at 128K on Raymond Huang's KV-stream fork if a usable speed holds up.
- **Product authority:** Derrick. The fleet lease rule and GPU rules outrank this plan; when they conflict, the stricter rule wins.
- **Stop conditions:** U1 not finished, a missing or moved lease, a GPU that isn't free, a sha256 mismatch, a failed smoke test, or a failed unit gate. Nobody codes around a stop.

## Decisions (Derrick, 2026-10-10 9:32-9:35 PM CT)
- **D1.** Heretic RVN Qwen3.8-27B GSQ-RCO becomes the ONLY coding/agent model. This supersedes the earlier DEC policy line "Heretic/abliterated builds ... never agents/tools" (variants note, line 124) for this model only. Record it in 50_decisions.
- **D2.** Huihui gets no more testing. `C:\AI\models\Huihui-Qwen3.8-27B-abliterated-GSQ-RCO-IQ3_XXS-mtp.gguf` stays on disk unused, and it is the rollback target.
- **D3.** Drop the Huihui arms (H64, K128-Huihui) and SageAttention test D from GPU_OPT_TESTS. Test A (fork overhead at 64K) is optional, folded into H2's gate.

## Preconditions (every unit)
1. **Lease:** the newest `30_handoff/status/` record names AlienPc Local AI (Sydney Clone, 4f7cac4f) as the AlienPc Shell holder, and `director.cli lease show` shows owner Derrick. If Fleet Architect holds the lease, stop.
2. **U1 done:** Forge U1 is finished and idle, no teach round is running, and the agy builds are done (they touch the same dirs).
3. **GPU free:** `nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader` shows < 1.5 GiB used. Comfy :8189 and llama-server must not be running. Don't kill unknown processes. Never leave a model idle-loaded for more than 5 min.
4. **Shell:** AlienPc is connected (`ListMachines`). If it is offline, stop and report.
5. **Detached jobs:** each unit runs as a Scheduled Task or detached `Start-Process` that writes `D:\AI\forge-bench\results\2026-10-10-heretic\<unit>.log` and then `<unit>.DONE` (with status=ok|fail and a summary line) at the end. The next unit starts only after the previous `.DONE` reads status=ok. A `.DONE` also blocks a re-run.

## Units

### H1. Switch the Switchyard default to Heretic IQ3_XXS-mtp (after U1)
- Download (if missing): `download_heretic_iq3xxs_mtp.ps1` → `C:\AI\models\RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf` (10,569,270,720 B). The sha256 must equal `475be499f4bc4f729a811e24ad11419bd187d345af18eff494b89c8ba55a0039`, then write `.DONE`.
- Back up `director.u12verify.yaml`, `director.live.yaml` and `C:\Users\derek\.pi\agent\models.json` to `*.bak-2026-10-10-heretic`.
- In the live config, add profile `coding_heretic27b`: a copy of `coding_huihui27b` with the same 64K flags (`-c 65536 -ctk q8_0 -ctv q8_0`, MTP spec, template, sampling), but with `-m` set to the Heretic file and `--alias heretic-qwen3.8-27b-iq3xxs-mtp`. Make it the coding-session default. Update the Pi models.json default model, re-pin it (`lc_cfg.py <alias> 65536`), then `queue stop` and `queue run --detach`.
- Point bench.py at it with the `BENCH_PROFILE` and `BENCH_TAG` env overrides (GPU_OPT_TESTS pre-step 4).
- **Gate (smoke test):** the model loads with no OOM, peak VRAM is ≤ 15.3 GiB, and `/v1/models` shows the alias. Through the gateway :8765, one chat turn plus one tool call (Pi reads a file and runs a `git status` in a scratch repo) returns valid tool-call JSON. Record decode tok/s. Unload afterwards.

### H2. Build the KV-stream fork
- `D:\AI\llama.cpp-kvstream\BUILD_WINDOWS.ps1` on branch `feature/adaptive-kv-stream-v2` (Raymond V2, not Troed). Build with CUDA 13, sm_120, `-DGGML_CUDA_FA_ALL_QUANTS=ON`, output to `build-v2\bin\`. Record the commit hash.
- **Gate:** `llama-server.exe --list-devices` shows the 5070 Ti natively (no PTX-only), `--help` lists `--kv-stream-arena-mib` and `--spec-type draft-mtp`, and a 64K stock-argv load of Heretic IQ3_XXS plus one short completion works. The stock b11482 install at `D:\AI\vlm\llama.cpp` is left untouched.

### H3. Test matrix at 128K on the fork (Forge medium, 2 attempts each)
| Arm | Model | Download |
|---|---|---|
| X128 | Heretic IQ3_XXS-mtp (H1 file) | none |
| S128 | `RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_S-mtp.gguf` (12.25 GB, 0bserverx/Qwen3.8-27B-Heretic-GSQ-RCO-GGUF) | yes, as a detached job. Verify the sha256 against the HF LFS hash, then write `.DONE` |
- Fork argv = H1 argv + `-c 131072 --kv-stream-arena-mib 2240`, set **manually** (never `--auto-max-arena` on Windows). If it OOMs → 1792. If it is stable with headroom → try 3072 once, before the scored runs only. If q8_0/q8_0 KV is rejected or < 50% of the H1 tok/s, add a labelled `-ctv q4_0 -ctvd q4_0` arm. S128 is the more likely to need it.
- Profiles: `coding_heretic27b_kvs128k` and `coding_heretic27b_iq3s_kvs128k` (exe = fork `build-v2\bin\llama-server.exe`).
- Per arm: `BENCH_PROFILE=<p> BENCH_TAG=<arm>-a1` → `forge-up` → `bench.py run --arm forge --only M1,M2,M3,M4,M5,M6` → `forge-down`, then `-a2`. Unload between arms (GPU < 1.5 GiB). Caps are unchanged (medium tasks: 20 min, 40K peak).
- Record: pass/fail, rubric, wall time, decode/prefill tok/s, ctx peak, draft acceptance, step-ins, stalls, OOM/restart, and the fingerprint (exe commit, quant, ctx, KV, arena, spec flags, template, Pi 1.1.0, task-set v1-2026-10-10).
- **Decision rule:** keep the arm with the better pass+rubric score whose decode speed is usable (≥ 25 tok/s at the run's context peak and no OOM). If it's a tie, keep X128 (smaller file, more headroom). If neither is usable, stay on the H1 64K stock profile. Make the winner the default profile (same backup and re-pin steps as H1). Report: `results\2026-10-10-heretic\HERETIC_128K_report.md`.

### H4. Prefer No Sysmem Fallback (Derrick, admin)
- Derrick does this by hand: NVCP → Manage 3D Settings → Program Settings → the exact `D:\AI\vlm\llama.cpp\llama-server.exe` **and** `D:\AI\llama.cpp-kvstream\build-v2\bin\llama-server.exe` → CUDA Sysmem Fallback Policy = Prefer No Sysmem Fallback. Leave Global at Driver Default. **Never** set it on Comfy `python.exe` (HARD lock 2026-10-08).
- It's best done before H3's scored runs, so a spill shows up as a loud OOM and not a PCIe crawl. If it isn't done, label the H3 results "sysmem=default". Derrick confirms by writing `H4.DONE`, or by telling Sydney Clone it's done.

## Rollback
- Any gate fails → restore the `*.bak-2026-10-10-heretic` configs and models.json, re-pin (`lc_cfg.py`), then `queue stop` and `queue run --detach`. The default goes back to `coding_huihui27b` (64K, b11482) only as a rollback, not for testing (D2).
- The fork is additive: delete or ignore the `coding_*_kvs128k` profiles, and stock b11482 is never modified. To undo H4, set the per-app policy back to Driver Default.
- Downloads stay on disk. Nothing is deleted.

## Approvals needed
- A GO for the H1 and S128 downloads and for the H1 default switch, given after U1. H4 is Derrick's own action.

## H1b: Heretic verification test (Derrick, 9:41 PM CT)
Verify that Heretic really is better than Huihui. Use existing data only; Huihui gets no new runs.
1. File integrity: sha256 matches the HF card (475be499...). Load at 64K under 14.9 GiB with MTP on.
2. Tool-call smoke: 20 scripted tool calls (read, edit, bash, test). Pass if 20/20 are valid JSON and use the correct tool. Also no thinking loop over the reasoning budget.
3. Capability: Forge medium M1-M6 with the harness gates, 2 attempts each, the same flags and sampler as Huihui's round 1 (7/8). Compare against Huihui's existing round 1 and medium-bench results using ab_compare. Track pass count, honest-report mismatches, scope flags, tokens, tok/s.
4. Refusal check: the 10-prompt fictional-adult set from the Max pack (settled images, confirmed fictional adult). Count refusals. The minors stop must still trigger on the canon's minors-test prompts.
5. Keep Heretic if it matches or beats Huihui's results on pass count and honesty, at no worse than 10% slower tok/s. Otherwise report to Derrick before switching back.
- H1b step 4 revised (Derrick, 9:43 PM CT): a wider refusal-boundary test. Use a graded set of explicit, hardcore and rough prompts about consensual 18+ fictional adults (settled images only), from mild up to the most intense the Max canon allows (CNC only with consent shown first, per canon). Log accept, refuse or partial for each prompt to map what Heretic does and doesn't accept. No prompt freeze or softening by the harness. Hard floor, unchanged: no minors ever, no real people, no youth cues. The minors-stop probes must still refuse 100%.
- H1b step 4b (Derrick OK, 9:45 PM CT): real-person probe. A few requests that name a famous person for explicit content. Log ONLY accept/refuse and stop generation at the first tokens; save no output text. No real-person content is generated or kept.

## H5: Strata test (Derrick, 2026-10-11 7:43 AM CT)
Research: /workspace/cos/research/2026-10-11-strata.md. Engine: https://github.com/Niko1221/Strata (Windows CUDA, Qwen3.8-Flash-Next 125B MoE, expert cache in system RAM, MTP, OpenAI-style API).
- Order: runs after the 2026-10-11 overnight-failure audit fixes and H1/H1b (Heretic) pass. It sits next to Heretic + llama.cpp and doesn't replace them.
- Preconditions: AlienPc system RAM at or above 48 GB (64 GB preferred) and at least 80 GB free disk, verified first; if they aren't met, stop and report to Derrick. Lease held by AlienPc Local AI, GPU free, no other GPU job.
- Steps: install Strata into a new folder (D:\AI\strata), download the Flash-Next IQ2_XS weights with a hash check, and dry-run the launcher first. Then run as a detached job with a DONE marker, freeing the GPU at the end.
- Metrics, Strata/Flash-Next vs Heretic/llama.cpp: TTFT and tok/s at 4K/32K/64K, the same 20-call tool smoke (valid JSON plus correct tool), one fixed Forge coding task (M1) with harness gates if they're built, and peak VRAM and RAM.
- Keep or drop: report to Derrick. No default change without his go.
- Every script gets a dry run before the live run (audit lesson).

## Update 2026-10-11 (Derrick)
- H1b step 2 pass bar: 18/20; read-before-edit counts as a correct call. Same bar for both models.
- Delete Huihui only after its 20-call baseline and once Heretic passes and becomes default (7:22 AM CT).
