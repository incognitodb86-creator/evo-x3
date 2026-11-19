# BENCH-ALIENPC-1 Step 1 (A4 / R1) — render timing

Date: 2026-11-19 16:42 CT
Doer: max-alienlane (executor)
Status: Step 1 DONE (read-only timings + flag recommendation). Step 2 still tests (A5) not run — they need Derrick's yes per still.

Authority: `records/uplan/PLAN.md` A4; `records/BENCH-ALIENPC-1/BRIEF.md` step 1 (R1). No changes were made for R1. A6 flags were not applied.

## Machine state when measured

- `C:\AI\locks\gpu-render.lock` released 16:33:58 CT (run_queue pid 20368 exited). GPU idle at 16:34:47 CT (RTX 5070 Ti, 0% util, 385 MiB used of 16303 MiB). `comfyui_auto` unloaded 16:33:31 CT; `:10003` and `:8447` were down (expected after unload).
- Today's batch `C:\AI\community\runs\h3max_lora_test_20261119`: 2/5 clips ok, 3/5 failed twice, then RTX 2x upscale of the two ok clips, then unload + lock release.
- Live `comfyui_auto` argv (from `C:\AI\director\config\llama-swap.yaml`, read-only): `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5`. No `--disable-fast-disk`, no `--lowvram`.

## Per-stage gap (VERIFIED missing)

R1 asked for load, text encode, sampling per pass, VAE decode, RTX 2x, and the startup line `Model storage policy: fast_disk=...`.

- RTX 2x and end-to-end wall times are on disk (below).
- Load / text-encode / sampling / VAE decode were **not** recoverable: `llama-swap.out.log` records only llama-swap health/TTL lines (today's session: health check 16:22:41 CT), not ComfyUI stdout. `C:\AI\director\logs\comfy-graceful-stop.log` is stop/kill only. No `fast_disk` / `Model storage policy` / `HostBuffer` / `1450` / OOM lines were found in those logs or `C:\AI\community\community.log`. Comfy history was not queried because ComfyUI was already unloaded; it was not started again.
- `run_queue` / `comm.py` record `JOB end ... secs=<wall>` only (poll ~3 s), not per-node times.

## Timing table

Wall seconds are `JOB end secs=` (queue submit to clip on disk, includes 3 s "queued" in both successful arms). Raw size for the video rows is 768x1344; published clip after RTX 2x is 1536x2688. Times are America/Chicago.

| When (CT) | Run / tag | Kind | Frames | Job wall (s) | Queued (s) | RTX 2x elapsed (s) | RTX 2x child (s) | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|
| 16:22:34–16:22:41 | comfyui_auto wake | startup | — | ~7 | — | — | — | First health check 16:22:41 |
| 16:22:45–16:27:52 | h3max_lora_test_20261119 / arm0_baseline | video | 243 | 304.7 | 3 | 18.7 | 15.78 | Cold-ish (fresh Comfy start). prompt_id 145222cf-…. Audio yes. upscale peak_torch 108 MiB |
| 16:27:57–16:33:10 | h3max_lora_test_20261119 / arm1_realism_0.6 | video | 243 | 310.7 | 3 | 7.6 | 5.03 | Warm Comfy. prompt_id fc2fb330-…. Audio yes. upscale peak_torch 108 MiB |
| 16:33:11–16:33:30 | h3max_lora_test_20261119 / arms 2–4 | video | — | — | — | — | — | All failed twice; no clip timing (see Failures) |
| 2026-11-15–11-18 | recent approved 243f 768x1344 clips (8 samples, sanitized set) | video | 243 | 307.7–310.9 | — | 7.3–19.6 | — | Same wall band as today's two ok arms |
| 2026-11-15 | other recent clips (same pipeline) | video | 158 | 208.1–211.2 | — | 6.3–18.7 | — | ~1.32 s/frame, same as 243f |
| 2026-11-15 | other recent clip | video | 209 | 269.4 | — | 7.4 | — | |
| 2026-11-15 | other recent clip | video | 566 | 917.5 | — | 23.7 | — | |
| 2026-10-30 | terrace_settings_v3_20261030 (42 clips with job_secs) | video | 124 | min 120.1 / median 180.1 / mean 161.6 / max 180.2 | — | — | — | job_secs look poll-rounded (many ~180). Plan's official baseline remains **~142 s** from output timestamps (mean of 3 seeds), not this job_secs set |
| 15:06–15:39 | flux_smoke_20261119* stills (today, already finished) | still | 1 | T2I 24.1–24.7; other arms 6.0–96.4 | — | n/a | n/a | Context only; not A5 |

Linear scale of the plan's 124f ≈142 s baseline to 243f is ≈278 s. Today's 243f walls (304.7–310.7 s, ~1.25–1.28 s/frame) are in the same band as other mid-November 243f clips, about 10% above that simple scale (different graph/audio/date; not a per-stage proof).

RTX 2x: first upscale in a pair is slower (~18–20 s elapsed), later ones ~7–8 s. This is after Comfy unload today (upscales ran 16:33:50 and 16:33:58).

## Failures (today's batch; no LoRA/RefMod filenames)

From `_render_queue.log` / `_run_queue.out.log`, batch closed `rc=5` at 16:33:58 CT, `done=2/5`:

- arm2, arm3, arm4: each `FAIL` at first try and at the one allowed unchanged retry, then skipped.
- Verbatim error type (filename omitted per rule): POST 400 `{"error": {"type": "prompt_outputs_failed_validation", "message": "Prompt outputs failed validation", ...}, "node_errors": {"lora_1" or "lora_2": {"errors": [{"type": "value_not_in_list", "message": "Value not in list", "details": "lora_name: '<omitted>' not in (list of length 64)", "extra_info": {"input_name": "lora_name", ...}}]}}}`
- These three arms produced no wall-time sample.

## R3 / R4 recommendation (A6)

Per the brief: R3 (`--disable-fast-disk`) **only if** the log shows `fast_disk=True`. R4 is the NVIDIA driver policy `CUDA - Sysmem Fallback Policy = Prefer No Sysmem Fallback` for ComfyUI's `python.exe`.

- **R3: do not try from this A4.** The required `fast_disk=True` startup line was not found. The live command does not pass `--disable-fast-disk`, so the default may be on, but that is an assumption, not a log line. Applying R3 would mean editing `C:\AI\director\config\llama-swap.yaml` `comfyui_auto` (and possibly `comfyui_longvideo`) `cmd` and restarting `comfyui_auto`. Not done. If a later start log shows `fast_disk=True`, that is the change to propose; do not restart until Derrick says so.
- **R4: do not try from this A4.** No sysmem-fallback, HostBuffer 1450, or OOM evidence in today's logs. This is a driver-profile change, not a Comfy launch flag. Not done.
- **R2:** not in scope (download / model switch only if Derrick wants it).

## A5 prepared (not queued)

Needs Derrick's yes **per still**, prompts written on the X3 with `flux-klein-prompting`, then `run_queue` one at a time. All six candidate files are already in `C:\AI\community\templates\`. Optional Hybrid arm uses `flux_still.py --hybrid "<Name>"` (0.85 RefMod + 0.60 paired LoRA); no names listed here. Pose/layout refs go through the existing still read + text lint first (card 30). Record pass/fail, warm/cold seconds, peak VRAM (target < 16 GB), node errors. Images stay on AlienPc / Hermes; no git. Depth LoRA only if layout fails and Derrick says yes.

1. `miraclein_t2i.candidate.api.json` (M4 T2I)
2. `miraclein_refmod.candidate.api.json` (M4 RefMod) + optional Hybrid arm
3. `miraclein_edit.candidate.api.json` (M4 single-change edit)
4. `flux_stills_t2i_klein.candidate.api.json` (ST4)
5. `flux_stills_pose_klein.candidate.api.json` (ST5 pose)
6. `flux_stills_layout_klein.candidate.api.json` (ST5 layout)

## A6 prepared (not applied)

No flag change. See R3/R4 above. A Comfy restart would be required for R3 if it is later approved.

## A7 prepared (not queued)

Fixed seed, same start still, same prompt (except TQ5's header arm). Derrick picks by eye. Order from `CANDIDATES-TQ.md` (now including the TenStrip LCM/simple 6–8 step turbo-audio note on TQ3). All candidate and 1-pass production templates exist on disk. Realism LoRA stays disabled until M5.

1. **TQ1:** `oc_guide_2pass.candidate.api.json` vs live `oc_guide.api.json`; `oc_ref_2pass.candidate.api.json` vs live `oc_ref.api.json`
2. **TQ4:** smoke + eye check of `two_person.b7.candidate.api.json`, `ref2va_16x9.b7.candidate.api.json`, `long_continuation.b7.candidate.api.json` (live non-b7 copies exist)
3. **TQ2 / TQ3** on the TQ1 winner (copies only): VSA `m_vsa.inputs.start_percent` `0.2` vs `0.0`; `ksel.inputs.sampler_name` `res_multistep` vs `euler` + `simple` on 1-pass and 2-pass copies (`er_sde` banned). Optional audio check: `lcm` / `simple` 6–8 steps only if the winner's audio sounds rough.
4. **TQ5:** header-free (`beta7_convert.py`) vs 4-header prompt on the winning graph
5. **Then M5 realism** (after Derrick's TQ picks): fixed-seed 3-arm vs control, strengths 0.60 and 1.00, then 2-pass B2 + winning strength — still disabled in config; do not enable or queue until Derrick's yes

## File apply from `c012e816` (after lock release)

Lease line added (Max's leftover H3-test line was left in place; only the max-alienlane line is removed at the end of this run). Backups: `C:\AI\_archive\20261119\alienlane-apply\live-backup\`. Sources also stored under `...\alienlane-apply\src\`.

| Live path | Action | Verification |
|---|---|---|
| `C:\AI\community\templates\CANDIDATES-TQ.md` | Applied repo TQ3 TenStrip LCM/simple note | sha256 `352cc3dc637387abf03f6d042bc49d4ceb7ad320536e68c46596548c581833f5` (matches `mono` / `c012e816`). Backup sha `3f22a5ac9d39e3b970a6377da44554311c9299652e396619a96186c271da3b2a` |
| `C:\AI\community\skills\flux-klein-prompting\SKILL.md` | Replaced live pre-`c012e816` copy (sha `13489d3d…`, same as repo `alienpc/` skill) with the photographer / Hybrid 98% skill from `x3/community/skills/flux-klein-prompting/SKILL.md` at `c012e816` / `mono` | sha256 `3b7d033b124ab25c26d27a6e4e0f1beaf44789a80217f60490ace72f1e17be6c`. Markers present: photographer persona, Hybrid 98%, `--hybrid` |
| `C:\AI\community\templates\miraclein_refmod.candidate.api.json` | **No write.** Schema fix already live (`none`, `copies_1..8`, `klein9_refmods`, `custom_retention=1.0`). Raw sha `6752bfeb07325819708a4ca2611ab75e5d8e6724ccb90d2cfaeb995492221d4c` differs from repo `61c7c1ae…` only by key order: canonical JSON sha matches `05b37fb9fce223a392b9cbec60d89cf2185374fd2a323adc717d62c4668ad58e` | Left untouched (mtime still 14:36:43 CT) |

Realism LoRA was not enabled. No ComfyUI / llama-swap restart. No git commit on `C:\AI\community`. Original ComfyUI folder not modified. This clone was not committed or pushed; `/workspace/mono-sync` was not checked out.

## Notes

- `records/UNI-APPLY-ALIENPC-A/RESULT.md` exists (2026-11-19 13:52 CT, 12 pytest passed). `UNI-APPLY-ALIENPC-B-AGT1` is the blocked attempt file. `UNI-APPLY-ALIENPC-C/RESULT.md` is still missing on `mono` `a6018891` / current `mono`; A4 proceeded on already-finished renders plus the live schema already present in the RefMod candidate.
