# EVO-X3 + AlienPC: changes the Linux dual-boot plan needs (LX1-LX9)

- **Status:** HELD, updated 2026-11-20 ~8 AM CT (Derrick t2854u: Linux is out of today's scope). Planning only; nothing has run on Linux. Lives on `mono` at `records/source-plans/` (primary, current copy; Derrick t3014u). The `evo-x3-all` copy is frozen at `96b71aa`.
- **Relationship:** the Linux work, moved out of the [follow-up plan](2026-11-18-x3-alienpc-followup-plan.md) so it has its own plan. The Linux dual-boot plan ([2026-11-11-alienpc-linux-dual-boot-plan.md](2026-11-11-alienpc-linux-dual-boot-plan.md), rev 4, Scout) was reviewed **NOT READY** on Nov 16 ([review](2026-11-16-alienpc-linux-dual-boot-plan-review.md)). It stays its own plan and owner; nothing here replaces it. This file lists only what the [main plan](2026-11-18-x3-alienpc-hermes-setup-plan.md) and the follow-up plan change for it. Read it with the Linux plan and its review.
- **Owner:** Derrick. **Executor:** Max, as in the main plan.
- **Rules (same as the main plan):** every live change needs Derrick's yes at the time. Change one thing at a time, record before and after, and keep the rollback ready.
- **Tracking issue:** https://github.com/incognitodb86-creator/evo-x3/issues/1
- **Which IDs are whose:** `U*`, `X*`, `BL*`, `FX*`, the review's `D1`-`D3` and rev 4's `R5` belong to the Linux plan and its review. `W*`, `G*`, `R1`-`R7` and `S1`/`S2` belong to the follow-up plan. `P*` and `D8` belong to the main plan.


## Status as of 2026-11-20 ~8 AM CT

Sources: [unified PLAN.md index](../uplan/PLAN.md) (Nov 20 closeout + dated Derrick decisions), RESULT records under `records/`, and `mono` git log. Item rows below carry the status in place.

Whole plan: **HELD.** Derrick t2854u (2026-11-19): every plan is finished today except Linux. The Linux dual-boot plan is still rev 4, NOT READY (Nov 16 review). Nothing below has run on Linux.

Count: 2 done, 3 open, 4 held, 0 closed.

### Completed
- **LX1:** decision recorded (render-first appliance + opportunistic Swift; ESP on for the Swift coding alias per Derrick t2764u, so the "ESP off" note in LX1 is superseded). Text only; no Linux build.
- **LX6:** rule only (do not plan on the unverified 22-53% / 1.6x claims). Nothing to run.

### Open (what each waits on)
- **LX2:** same as F4 `H1a` / main-plan `P2.4` Tailscale ACL. Waits on Derrick in the Tailscale admin console.
- **LX3:** same as F4 `S1`. Windows ComfyUI-Manager is still `security_level = normal` ([A8-RESULT.md](../BENCH-ALIENPC-1/A8-RESULT.md), `0fdf10a2`). Waits on the last node install, then Derrick's yes.
- **LX8:** writer node is F4 `W3c` (card C5, undecided). The S2 allowlist code and tests are on `mono` (`4d909034`, `alienpc/community/scripts/allowlist_promoted.json`), but the hook into `run_queue.py` / `comm.py` is not installed (A8 skipped).

### Held
- **LX4:** waits on the Windows tuning rows. Status of those rows: R1 done ([A4-RESULT.md](../BENCH-ALIENPC-1/A4-RESULT.md)), R3/R4 skipped ([A6-RESULT.md](../BENCH-ALIENPC-1/A6-RESULT.md)), R6 not adopted ([R6-RESULT.md](../BENCH-ALIENPC-1/R6-RESULT.md)), R2/R7 open. Windows same-graph control on Nov 19 was 286.5 s for a 243-frame 768x1344 clip (R6-RESULT), not the old 124-frame B2 number.
- **LX5, LX7, LX9:** U8/U10 on Linux not started.

### Issues
- Windows `comfyui_auto` now reports ComfyUI **0.46.0** ([R6-RESULT.md](../BENCH-ALIENPC-1/R6-RESULT.md)), not the 0.38.0 this plan and the Linux plan assume. Re-check LX7's flag list against 0.46.0 before any Linux run.
- R6 on Windows: `--fast fp16_accumulation` tied on time but not on output (mean SSIM 0.78), so it stays off. Keep it off the Linux rows too unless a blind pick says otherwise.

## 1. Changes

| ID | Change | Why |
|---|---|---|
| LX1 — **DONE** | **Decided (Derrick, 2026-11-18/19): render-first appliance + opportunistic Swift coding lane.** Under Linux the AlienPC runs ComfyUI (`comfyui_auto`, `comfyui_longvideo`) as its primary workload plus native Strata Swift (`coding_swift15_iq3s_esp`, plus a pure-coding alias with `experimental_speed_projection: false` to avoid ESP's +15% code perplexity penalty) in one exclusive llama-swap group. EVO-X3 Gufo is primary for daily coding; AlienPC Swift is used opportunistically when AlienPC is idle or X3's 2 Gufo sessions are saturated. The waiting gate stays on `:8085` and the fail-fast gate (`:8086`, `--fail-if-busy`) is behind Tailscale Serve `:8447` (main plan P5.1). Replace rev 4's "ComfyUI-only", R5's "no local LLM runs on AlienPc Linux" and X4's "AlienPc never loads a local LLM". U8 builds native Strata, not Forge. U10 records Swift's tok/s as information only, not pass/fail. | Main plan D8/Phase 5 and follow-up F4 (X3-primary coding, AlienPC render-first + opportunistic Swift). |
| LX2 — **OPEN** | **Access rules = the main plan's P2.4:** a narrow form of the review's D1 option B. It keeps today's other flows and limits only the ports with no login (`8443-8447`). Give the Windows and Linux AlienPC nodes the same tag, so the rules cover whichever OS is up. The review's FX3 already names a separate Linux node (`alienpc-linux`). | Review BL1, FX3. |
| LX3 — **OPEN** | **Same Manager setting:** the Linux build starts with ComfyUI-Manager at `strong`, or without Manager (the follow-up plan's S1). | Review BL2(c). |
| LX4 — **HELD** | **Benchmark against tuned Windows.** U10 runs after the follow-up plan's render-speed tests (its "Faster H3 Max beta7 renders" section, R1-R7), so Linux is compared with Windows at its best. It uses the same protocol on both: warm-up, at least 3 runs, median, same seed, hash-matched models. The Windows baseline is the real render time (about 142 s for a 124-frame B2 clip on Oct 30), not the old runner's poll-rounded 180 s. If those tests adopt the `activation_learned_HQ` checkpoint, stage it on Linux too. | Comparing with untuned Windows would credit Linux with gains Windows can also get. |
| LX5 — **HELD** | **Headless boot as a U10 row:** measure the clip once with a desktop session and once from `multi-user.target`. U9 (Grok Bot local execution) needs a desktop session, so headless becomes the default only if U10 shows it matters and Grok Bot can run without one. | The extra VRAM a headless boot frees isn't measured on this box. |
| LX6 — **DONE** | **Claims not to plan on.** A Nov 18 Gemini review's Linux gains (22-53%, its per-stage table, "1.6x on your hardware", sol-attn numbers) have no sources, and its 180 s baseline was the poll-rounded runner time. The Linux plan's own estimate (about 5-15%) stands until U10 measures it. | Unverified. |
| LX7 — **HELD** | **Linux ComfyUI tuning, run as extra U10 rows** after the plain Linux row (same graph, seed and models; warm-up, at least 3 runs, median; one change per row):<br>1. **Pinned memory on:** drop `--disable-pinned-memory`. That flag exists only because of Windows WinError 1450 errors.<br>2. **Fast-disk both ways:** ComfyUI auto-detects a fast NVMe on Linux by link speed (`comfy/storage.py`), so the 9100 PRO will likely show `fast_disk=True`. Read the log line, then test `--disable-fast-disk` against the default.<br>3. **Cold vs warm:** time the first render after boot apart from repeat renders, because Linux keeps recently read model files in RAM.<br>4. **Headless:** LX5.<br>Each of these changes only where weights or memory sit, so frames should match on the same seed. Still left out on Linux: sol-attn and SageAttention (both change the output) and `torch.compile` (conflicts with Dynamic VRAM). | The follow-up plan's Windows render-speed steps (R1-R7) carry over except R4, the Windows driver setting. These rows are the Linux-only part. |
| LX8 — **OPEN** | **Two review items the follow-up plan decides for both OSes:**<br>1. **D3 (secondary LLM nodes on the AlienPC)** is the follow-up plan's W3. If the `API Universal Writer` node stays, the Linux build needs the pack's Linux key storage (`MINIMAX_H3_VAULT_KEY`, kept stable across restarts, with a separate backup), `MINIMAX_H3_API_ADMIN_TOKEN`, and FX6's leak test. If it goes, AlienPC Linux holds no LLM key.<br>2. **BL3 (server-side template check)** is the follow-up plan's S2. Build the same allowlist on both OSes — including the 3-node `remote_upscale.py` graph (`VHS_LoadVideo -> RTXVideoSuperResolution -> VHS_VideoCombine`) if Linux runs RTX VSR — with graphs that contain an LLM node left off it. | One answer for both OSes. Without a vault key the pack disables key entry on Linux. |
| LX9 — **HELD** | **2x video upscale on Linux (both `nvvfx` and `ComfyUI_Nvidia_VFX_Nodes`).** Windows uses two paths: local `run_queue.py` runs Python `nvvfx`, and X3 `pi-job upscale` (`remote_upscale.py`, `x3-community` `306511e0`) posts `VHS_LoadVideo -> RTXVideoSuperResolution -> VHS_VideoCombine` (`Comfy-Org/ComfyUI_Nvidia_VFX_Nodes`) to `:8446`, while `sync-renders` publishes only clips whose `render_ok.json` has an `"upscale"` block. The Linux plan mentions neither. In U8, explicitly test **both** `nvvfx` and `ComfyUI_Nvidia_VFX_Nodes` (`RTXVideoSuperResolution`) on Ubuntu 24.04 (`sm_120`). If NVIDIA's Video Effects SDK / `RTXVideoSuperResolution` is Windows-only or unsupported on Linux, pick an explicit first-class fallback before cutover (either a Linux-supported ComfyUI video upscaler node writing the same `render_ok.json.upscale` contract, or updating `sync-renders` on Derrick's yes) — never leave an undocumented resolution/publish split. | Prevents `pi-job upscale` and `sync-renders` from silently breaking on Linux. U10 still times the base render separately from any post-pass. |

## 2. Evidence

| Claim | Verdict | Source |
|---|---|---|
| The Linux plan is rev 4, reviewed NOT READY on Nov 16 | Verified | `plans/2026-11-16-alienpc-linux-dual-boot-plan-review.md` |
| The review's D3 (secondary LLM nodes), FX6 (keys leaking through widgets, `/history` and output metadata) and BL3 (server-side template check) | Verified | `plans/2026-11-16-alienpc-linux-dual-boot-plan-review.md` (BL3, FX6, D3) |
| API Universal Writer on Linux: AES-256-GCM key file that needs `MINIMAX_H3_VAULT_KEY`; without it, browser key entry is disabled; `MINIMAX_H3_API_ADMIN_TOKEN` also protects local editing | Verified | pytraveler `docs/api_writer.md` |
| B2 takes about 142 s per 124-frame clip; `activation_learned_HQ` 127.0 s vs 143.8 s on the same seed | Verified (Oct 30) | `alienpc-community` `notes/2026-10-30-terrace-retest-v2-DONE.md` |
| `--disable-pinned-memory` was kept after "HostBuffer 1450" errors | Verified | `skills/alienpc-local-video-ops/references/max-8189-production-keep.md:19` |
| `--fast-disk` / `--disable-fast-disk` exist (v0.38.0 to v0.46.0); fast-disk is detected automatically and logged | Verified | ComfyUI `comfy/cli_args.py`, `comfy/storage.py` |
| ComfyUI-Manager security levels: `normal` allows middle-risk actions (install from the default channel, uninstall, update, restore snapshots, restart) | Verified | docs.comfy.org/manager/configuration |
| Sol-H3: unsupported on native Windows; an approximation on Linux | Verified | `xmarre/ComfyUI-Sol-H3` README |
| `run_queue.py` upscales every clip 2x with `nvvfx` by default (`--no-upscale` skips it); the Linux plan has no upscale step | Verified | `alienpc-community` `scripts/run_queue.py:5,31-37,94`; `plans/2026-11-11-alienpc-linux-dual-boot-plan.md` |
| `nvvfx` runs on Linux | Not checked; LX9 tests it | — |
| Windows vs Linux gains of 22-53%, a per-stage table, "1.6x on your hardware", sol-attn numbers | Not verified; not planned on | Nov 18 Gemini review |
