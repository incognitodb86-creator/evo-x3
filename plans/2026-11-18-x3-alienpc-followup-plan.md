# EVO-X3 + AlienPC follow-up plan (F1)

- **Status:** Active, 2026-11-18. Planning only; nothing here has run.
- **Relationship:** follow-up to [2026-11-18-x3-alienpc-hermes-setup-plan.md](2026-11-18-x3-alienpc-hermes-setup-plan.md), the main plan, which is in progress at `12085de`. Read this file on its own. The main plan matters only where a step below names one of its steps (P0.x, P4.x and so on).
- **Owner:** Derrick. **Executor:** Max, as in the main plan.
- **Rules (same as the main plan):** every live change needs Derrick's yes at the time. Change one thing at a time, record before and after, and keep the rollback ready.
- **Tracking issue:** https://github.com/incognitodb86-creator/evo-x3/issues/1

## 0. Already true (don't redo)

| Area | State | Source |
|---|---|---|
| X3 resident model | Halogen 0.20.7 with the Huihui v2 HGN in slot `flash-next-uncensored-v2`, preloaded, never unloaded. Every chat name is pinned to it. The v1 slot `flash-next-uncensored` remains only as the rollback. | `u58` `50e84a8` |
| X3 panes | Forge `x3-local-coding/flash-next-uncensored-v2` (subagents `x3-local/flash-next-uncensored-v2-sub`), Render `x3-local/flash-next-uncensored-v2`, thinking never `off`. | `u58` `50e84a8`, `32a46c0` |
| AlienPC render | ComfyUI behind llama-swap: `comfyui_auto` (idle timer 300 s) and `comfyui_longvideo` (600 s). B2 workflow on H3 Max beta7. Finished clips go to the QNAP `renders` share. | `alienpc-comfyui-config`, `alienpc-community` `98fbc30` |
| Stills and media | PixlStash (32,964 pictures) runs on the X3; Render picks stills through its API. | main plan, starting point |
| Render settings | B2 (int8HQ main model, comfy kitchen attention, `ref_image_size: max`, 8 steps), about 142 s per 124-frame clip. | `fleet-brain` B2 decision (Oct 30) |

## 1. v2 cutover update (applies to the main plan's Phase 0)

The main plan was written while v1 was resident. Max switched to v2 at 13:57 on a second try; the first try at 12:24 crash-looped on a duplicate alias (`92bb886`). The repo has no record of tests on v2.

| Main plan step | Read as |
|---|---|
| Every place that names the resident slot `flash-next-uncensored` (main plan section 3, P0.3's `--served-model-name`, P1.6, P3.1, P4.10, P5.3, section 9) | `flash-next-uncensored-v2` and its `-v2-sub` name. |
| P0.0 | Also ask Max which checks v2 passed before the cutover. |
| P0.1 | The baseline is the live v2: C2-C6, with C1 from its startup log. If v2 fails C3, C4 or C6, go back to v1 at once and record why. |
| P0.2 | Test v1 only if v2 fails or is clearly worse than v1's U26 numbers. Both slots exist, so switching means repointing the preload hook and the pins through the apply script. Never add slots or aliases. |
| G0 | The baseline is v2; "nothing beats the baseline" keeps v2. |

## 2. Faster H3 Max beta7 renders on the AlienPC (zero quality loss)

**Baseline:** a plain B2 clip (124 frames, 768x1344, two passes) took about **142 s** of real render time on Oct 30: the mean of 3 seeds, from the output files' timestamps. The runner's old 180 s figure came from checking only every 60 s; `run_queue.py` now checks every 3 s. The comfy kitchen attention node is already in every B2 template and was 23% faster than PyTorch attention in your Oct 26 test, so that gain is already in place. Your Oct 30 test also found 6 steps "not meaningfully faster", which suggests sampling isn't the main cost.

**Test rules (the same as the Linux plan's U10, so the numbers compare):**
- One change at a time, with the same graph, still, prompt and seed.
- A warm-up run, then at least 3 runs; use the median.
- Measure real render time from ComfyUI's own timing or the output timestamps, not the runner's checks.
- Record model hashes, the driver and the ComfyUI version.

"Zero quality loss" means one of two things. Either the change only moves where weights sit in memory, in which case compare frames on the same seed. Or it changes the model or the math, in which case it needs Derrick's blind pairwise pick on the same seed, as in Terrace v3; a tie counts as no loss.

| ID | Step | Evidence and risk | Keep if |
|---|---|---|---|
| R1 | **Measure where the time goes; no change.** Run one B2 render with a time for each stage (model loads, text encode, pass 1, latent upscale, pass 2, VAE decode), from the progress messages ComfyUI already sends. Also read each model's startup line "Model storage policy: fast_disk=…" in the ComfyUI log, and record the ComfyUI and comfy-aimdo versions (last recorded on Oct 20: v0.38.0 and 0.5.5). | No stage breakdown exists in the repo. Without one, R3 and R4 are guesses. | — |
| R2 **Y** | **Switch the main model to `beta7_activation_learned_HQ`.** It's already on the AlienPC, and `submit_parody_run.py --unet` already swaps it. Confirm with 3 seeds on the current production graph (the parody 2-pass graph), blind pairwise against int8HQ. | Oct 30: **127.0 s vs 143.8 s** on the same seed (12% faster). Terrace v3's 49-clip blind scoring found it "within seed noise", meaning no visible difference. It wasn't adopted only because the rule asked for a quality win, not a tie. Changing it means changing B2's locked model, which is Derrick's call. | The blind pick is a tie or better. |
| R3 **Y** | **`--disable-fast-disk`, only if R1 logs `fast_disk=True`** for the main model or the text encoder. ComfyUI v0.38.0 (the AlienPC's version) picks disk-backed loading on its own when it detects a fast disk. Keep `--disable-pinned-memory` for this test: it was kept after Windows "HostBuffer 1450" errors. Removing it is a separate test, stopped on any WinError 1450 or paging error. | Flag help: "Disable disk-backed dynamic loading and offload over unpinned RAM." It changes only where weights sit, so the output should match. | The median is faster and the frames match. |
| R4 **Y** | **NVIDIA "CUDA - Sysmem Fallback Policy" = "Prefer No Sysmem Fallback"** for ComfyUI's `python.exe`. Undo: Driver Default. | NVIDIA's article: performance becomes stable "at the risk of a crash" when more GPU memory is needed. It changes only where memory sits. | Faster, and no out-of-memory errors in 5 renders. |
| R5 | **`queue-remote.sh` checks for "BATCH closed" every 5 s instead of every 30 s**, so the X3 learns a clip is done up to 25 s sooner. | `x3/queue-remote.sh:46` sleeps 30 between checks. Renders are unchanged. | — |
| R6 **Y**, later | **`--fast fp16_accumulation`, then `cublas_ops`**, one at a time, only after R1-R4. Never `fp8_matrix_mult` (no fp8 on this box since October's float8 errors) or `autotune`. | ComfyUI's own help calls `--fast` "untested and potentially quality deteriorating", so it needs a blind same-seed pick. | The blind pick is a tie or better. |
| R7, later | **ComfyUI upgrade** from v0.38.0 (current is v0.46.0, released Nov 18) as its own job. Save a node snapshot first (`cm-cli save-snapshot`), then run the same benchmark. | The Nov 18 review's PR claims (#16677, #16698) weren't verified. Custom nodes can break. | Every template renders and the median isn't slower. |

**Checked and not adopted:**
- `ref_image_size: match`: tested Oct 30 and dropped for "more pose drift"; `max` is your fix for the #74 flicker.
- 6 steps and `er_sde`: 6 steps hard-failed once and wasn't meaningfully faster; `er_sde` hard-failed in 4 of 7 sets (Terrace v3).
- sol-attn (`ComfyUI-Sol-H3`): unsupported on native Windows, where it falls back to dense attention. On Linux it is an approximation that "can destabilize the initial trajectory" and is "not a lossless or speedup guarantee".
- SageAttention: off on this box since Oct 14, and comfy kitchen attention already won by 23%.
- Step-skipping caches (TeaCache, EasyCache, Spectrum): they change the 8-step trajectory, so they aren't zero-loss; untested here.
- `torch.compile`: not with Dynamic VRAM streaming the model; the Nov 18 review withdrew it.
- LokkenJP's `beta7_fix1_activation_learned_HQ` (18.73 GB): built from a newer source revision (expanded PDD output heads), so it changes the model, not just the quantization. Its card has "no controlled generated-video quality or inference-speed benchmark". It's a later quality test, not a speed step.
- LokkenJP's 15.35 GB W4/W6 text encoder: the same size class as the current NVFP4 file (15.69 GB), so no speed gain. Its card claims better weight reconstruction than NVFP4, which makes it a quality test.
- Releasing the GPU lock before post-processing: the RTX VSR upscale runs on the GPU and must stay inside the lock. Only file copies can move after it (main plan P4.7).
- Waking ComfyUI during a dry run: it would push Swift out of the GPU (the review withdrew this).
- Stopping the AlienPC's PixlStash: AlienPC Render uses it (`5465fde`).

## 3. AlienPC ComfyUI safety (small, do early)

| ID | Step | Pass |
|---|---|---|
| S1 **Y** | **ComfyUI-Manager to `strong`.** Both ComfyUI installs (`comfyui_auto`, `comfyui_longvideo`) run ComfyUI-Manager 3.40 at `security_level = normal`. At that level Manager allows its "middle" features: installing custom nodes from its default channel, uninstalling and updating them, restoring snapshots, and restarting ComfyUI. Requests arrive through llama-swap from 127.0.0.1, so they count as local, and anyone who can reach `:8446` can use those features. Today that is the whole tailnet; after the main plan's P2.4, the X3 (including Hermes's shell) and Derrick's devices. Set `security_level = strong` in both `user\__manager\config.ini` files and restart each ComfyUI once. Renders don't use Manager. To update nodes later, switch back to `normal` by hand for that session, or use `cm-cli` on the AlienPC. | A Manager restart or install request through `:8446` is refused; one B2 render still completes. |
| S2 (optional) | **Template check on the AlienPC.** The main plan accepts a known gap in OD10: Hermes, with a shell as `evo`, can still POST any graph to `:8446` directly. Closing it means checking on the AlienPC, not on the caller: only graphs whose node set matches a known template (B2, B2 RefMod, B2 parody 2-pass) are accepted, and only prompt, seed, image, frames and prefix may change. This is the Linux plan review's BL3 fix and serves both OSes. | A planted graph with an extra node class is refused even when the caller's own checks are skipped. |

## 4. Linux dual-boot plan: changes it needs

The Linux plan ([2026-11-11-alienpc-linux-dual-boot-plan.md](2026-11-11-alienpc-linux-dual-boot-plan.md), rev 4, Scout) was reviewed **NOT READY** on Nov 16 ([review](2026-11-16-alienpc-linux-dual-boot-plan-review.md)). It stays its own plan and owner. This section lists only what the main plan and this follow-up change for it.

| ID | Change | Why |
|---|---|---|
| LX1 | **Decided (Derrick, 2026-11-18): render + Swift lane.** Under Linux the AlienPC also runs native Strata Swift (`coding_swift15_iq3s_esp`), with `comfyui_auto`, `comfyui_longvideo` and Swift in one exclusive llama-swap group. The waiting gate stays on `:8085` and the fail-fast gate (`:8086`, `--fail-if-busy`) is behind Tailscale Serve `:8447`, as in the main plan's P5.1. Replace rev 4's "ComfyUI-only", R5's "no local LLM runs on AlienPc Linux" and X4's "AlienPc never loads a local LLM". U8 builds native Strata, not Forge. U10 records Swift's tok/s as information only, not pass/fail. | Main plan D8 and Phase 5 (Nov 18) came after rev 4 (Nov 16). |
| LX2 | **Access rules = the main plan's P2.4:** a narrow form of the review's D1 option B. It keeps today's other flows and limits only the ports with no login (`8443-8447`). Give the Windows and Linux AlienPC nodes the same tag, so the rules cover whichever OS is up. The review's FX3 already names a separate Linux node (`alienpc-linux`). | Review BL1, FX3. |
| LX3 | **Same Manager setting:** the Linux build starts with ComfyUI-Manager at `strong`, or without Manager (S1). | Review BL2(c). |
| LX4 | **Benchmark against tuned Windows.** U10 runs after this follow-up's section 2 tests, so Linux is compared with Windows at its best. It uses the same protocol on both: warm-up, at least 3 runs, median, same seed, hash-matched models. The Windows baseline is the real render time (about 142 s for a 124-frame B2 clip on Oct 30), not the old runner's poll-rounded 180 s. If section 2 adopts the `activation_learned_HQ` checkpoint, stage it on Linux too. | Comparing with untuned Windows would credit Linux with gains Windows can also get. |
| LX5 | **Headless boot as a U10 row:** measure the clip once with a desktop session and once from `multi-user.target`. U9 (Grok Bot local execution) needs a desktop session, so headless becomes the default only if U10 shows it matters and Grok Bot can run without one. | The extra VRAM a headless boot frees isn't measured on this box. |
| LX6 | **Claims not to plan on.** A Nov 18 Gemini review's Linux gains (22-53%, its per-stage table, "1.6x on your hardware", sol-attn numbers) have no sources, and its 180 s baseline was the poll-rounded runner time. The Linux plan's own estimate (about 5-15%) stands until U10 measures it. | Unverified. |
| LX7 | **Linux ComfyUI tuning, run as extra U10 rows** after the plain Linux row (same graph, seed and models; warm-up, at least 3 runs, median; one change per row):<br>1. **Pinned memory on:** drop `--disable-pinned-memory`. That flag exists only because of Windows WinError 1450 errors.<br>2. **Fast-disk both ways:** ComfyUI auto-detects a fast NVMe on Linux by link speed (`comfy/storage.py`), so the 9100 PRO will likely show `fast_disk=True`. Read the log line, then test `--disable-fast-disk` against the default.<br>3. **Cold vs warm:** time the first render after boot apart from repeat renders, because Linux keeps recently read model files in RAM.<br>4. **Headless:** LX5.<br>Each of these changes only where weights or memory sit, so frames should match on the same seed. Still left out on Linux: sol-attn and SageAttention (both change the output) and `torch.compile` (conflicts with Dynamic VRAM). | Section 2's Windows steps carry over except R4, the Windows driver setting. These rows are the Linux-only part. |

## 5. Small improvements (after the main plan's P6, or sooner if Derrick asks)

Not fixes. Each stays inside an existing script; pick any one at a time.

| ID | Improvement | Size |
|---|---|---|
| L1 | ntfy **Copy** button on the approval push. ntfy's documented `copy` action ("useful for one-time passcodes") puts `queue <run_id> <code>` on the clipboard to paste into Hermes. Check that the QNAP's v2.35.0 shows it; without it the push still works. | One header in main-plan P4.11 |
| L2 | **Poster image:** one ffmpeg frame grab per clip into `/srv/renders/<run_id>.jpg`, so Hermes's reply shows a picture above the video link instead of a blank player. | A few lines in main-plan P4.7 |
| L3 | **Abandoned worktrees:** nightly, for worktrees in `~/AI/_worktrees` older than 7 days, save `git status` and `git diff` to the job's `_runs` folder, then `git worktree remove` and `prune`. P2.3 only cleans up merged branches today. | A few lines in main-plan P2.3's timer |
| L4 | **Contact sheet in chat:** copy P4.5's 2 x 3 sheet to `/srv/renders/sheets/`, show it in the dry-run reply, and add `pi-job render --pick N` so Derrick can choose another panel before rendering. | Small |
| L5 | **`pi-job status` overview** with no job ID: the resident model and MemAvailable, whether the AlienPC is rendering, and the last 3 jobs with their result links. For one-tap use from the phone, save "status" as an Open WebUI prompt; no Open WebUI Action button, which would need a new host endpoint and could bypass Hermes. | Small |
| L6 | **STUCK bundle:** when a job ends `STUCK`, pi-job writes `~/AI/_runs/<id>/escalate.md` with the task, `git status` and diff, and the last 3 tool errors from the session, ready to paste into GrokBot (D3). | A few lines in main-plan P4.3 |
| L7 | **Syntax check after edits:** a small pi extension runs `python3 -m py_compile`, `bash -n` or `jq empty` on the edited file and adds the error to the tool result only when something is broken, so the model fixes it on the next call instead of looping. Test first that pi's extension API can add to a tool result. Look at pi's own "text not found" message before adding a whitespace hint. | About 40 lines in `agent-shared/extensions` |
| L8 | **Fast prompt edit:** `pi-job recompile <run_id>` reruns only the writer pipeline's linter and graph filler after Derrick changes a line of `prompt.txt`. It must pass the same READY / NOT_READY gate, and it sends a new code tied to the new prompt hash (P4.11). | Small |

## 6. Evidence

| Claim | Verdict | Source |
|---|---|---|
| B2 takes about 142 s per 124-frame clip; `activation_learned_HQ` 127.0 s vs 143.8 s on the same seed | Verified (Oct 30) | `alienpc-community` `notes/2026-10-30-terrace-retest-v2-DONE.md` |
| `activation_learned_HQ` scored within seed noise in the 49-clip blind test; `match` dropped for pose drift; 6 steps not faster; `er_sde` hard-failed | Verified | `fleet-brain` `50_decisions/2026-10-30-keep-b2-render-settings.md`; `plans/2026-10-30-0652-terrace-proper-settings-test-requirements.md` |
| comfy kitchen attention is in every B2 template; it was 23.1% faster than PyTorch attention | Verified | `templates/b2*.api.json`; `briefs/argon_medium_20261026/final_review…md:32` |
| The AlienPC runs ComfyUI v0.38.0 and comfy-aimdo 0.5.5; ComfyUI-Manager 3.40 at `security_level = normal` | Verified (Oct 20 and Nov 17 snapshots) | `p1/env-lock-20261020.txt`; `alienpc-comfyui-config/comfyui_auto/user____manager__config.ini` |
| `--disable-pinned-memory` was kept after "HostBuffer 1450" errors | Verified | `skills/alienpc-local-video-ops/references/max-8189-production-keep.md:19` |
| `--fast-disk` / `--disable-fast-disk` exist (v0.38.0 to v0.46.0); fast-disk is detected automatically and logged | Verified | ComfyUI `comfy/cli_args.py`, `comfy/storage.py` |
| `--fast` is "untested and potentially quality deteriorating" | Verified | ComfyUI `comfy/cli_args.py` |
| ComfyUI's latest release is v0.46.0 (Nov 18) | Verified | GitHub releases |
| ComfyUI-Manager security levels: `normal` allows middle-risk actions (install from the default channel, uninstall, update, restore snapshots, restart) | Verified | docs.comfy.org/manager/configuration |
| NVIDIA "Prefer No Sysmem Fallback": stable speed "at the risk of a crash" | Verified | NVIDIA support article 5490 |
| Sol-H3: unsupported on native Windows; an approximation on Linux | Verified | `xmarre/ComfyUI-Sol-H3` README |
| LokkenJP fix1 HQ is 18,734,317,942 bytes, from a newer source revision, with no video-quality or speed benchmark; the W4/W6 text encoder is 15.35 GB | Verified | Hugging Face `LokkenJP/TenEros_Max_optimized_learned` (card and file list) |
| Windows vs Linux gains of 22-53%, a per-stage table, "1.6x on your hardware", PR #16677/#16698, comfy-aimdo #70/#118 | Not verified; not planned on | Nov 18 Gemini review |
| The Linux plan is rev 4, reviewed NOT READY on Nov 16 | Verified | `plans/2026-11-16-alienpc-linux-dual-boot-plan-review.md` |
