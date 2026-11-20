# TQ4 Beta 7 candidate smoke A/B — 2026-11-19 (America/Chicago, CT)

All times are America/Chicago (CT). Doer: Grok Bot executor. This file is a report only; it is not a promotion, and it was not committed from this pass.

## Scope and isolation

- Ran a **read-only re-verification** of the official TQ4 smoke clips already rendered in the A7 stage-1 batch. Did **not** re-queue identical seed/still/prompt jobs. Did **not** auto-promote any candidate. Did **not** touch X3 `:8081`, `x3/*`, or `hosts/x3/*`. Did **not** download Card 24 or LAST `2735733`.
- There is **no** landscape 16:9 2-pass / VSA candidate template. Production `oc_ref_2pass.api.json` is portrait (`c0` 384×672 → 768×1344) with `m_vsa.start_percent=0.2`. The leftover `oc_ref_2pass.candidate.api.json` is the unpromoted VSA 0.0 portrait graph. TQ4 candidates `two_person.b7` and `ref2va_16x9.b7` are 1-pass 1344×768 with VSA 0.0 as authored. No unofficial 16:9 2-pass graph was invented or queued.
- Official TQ4 items (`CANDIDATES-TQ.md`, PLAN Card 45 / A7 order, `A7-QUEUED.md` positions 4–6): `two_person.b7.candidate.api.json`, `ref2va_16x9.b7.candidate.api.json`, `long_continuation.b7.candidate.api.json`.

## Why these clips were not re-rendered tonight

A7 stage 1 already queued and finished all three TQ4 smokes under lease `Max | A7 TQ A/B | 2026-11-19 17:09:10 CT` in `C:\AI\community\runs\a7_tq_ab_20261119\`, using `run_queue.py`, fixed seed **51083601**, the approved arm0 still `still_32964.jpg` (copied, not retyped), the same arm0 prompt (not regenerated; no X3 LLM call), same RefMods as arm0 (2 visual slots filled), no LoRAs, RTX 2x ULTRA post-pass on. `R6-RESULT.md` already recorded `done=6/6`, rc=0, last job OBJECTIVE ok at 17:41:25 CT. Those clips were never written up as `TQ4-RESULT.md` and were never eye-picked.

Re-rendering the same three graphs at the same seed/still/prompt would not be a new A/B. Fresh `ffprobe` + OBJECTIVE checks were run at **22:32 CT** against the saved raw and 2x MP4s. All three still pass.

## Lease and GPU (this pass)

- AlienPc lease `C:\AI\locks\alienpc-lease.txt` was already **0 bytes** (mtime 22:20:21 CT, leftover clear from the earlier REA 30s val). No `gpu-render.lock`.
- GPU at the start of this check: **770 MiB / 16303 MiB, 0%** (Comfy left resident from the earlier `--keep-comfy-process` val; not rendering).
- **No new lease was taken** because no new GPU job was submitted. Lease remains 0 bytes. GPU was not started or unloaded.

## Request facts (graph is authority)

Shared: seed `51083601`, still basename `still_32964.jpg`, `refmods_filled=2`, candidate `m_vsa.start_percent=0.0` (unchanged). `two_person` loads the same still on both `img` and `img2`. `long_continuation` beat 1 is 243f; beat 2 is `win1.extension_frames=238` (OBJECTIVE 481f). Request SHA-256 values match the first-12 prefixes in `A7-QUEUED.md`.

| tag | template | request sha256 | canvas (c0) | raw frames | prompt_id |
|---|---|---|---|---:|---|
| `tq4_two_person_b7` | `two_person.b7.candidate.api.json` | `26bba5b5c40617e0aea30c753d6aa6b6524a4d409221c4b96e535736413e89a8` | 1344×768 | 124 | `19c4ee82-1f2b-47f1-a5b2-9e234d34dc9c` |
| `tq4_ref2va_16x9_b7` | `ref2va_16x9.b7.candidate.api.json` | `55e7275022e5264f638313fa64672681c520650c3135565e7f82ef79a10dc105` | 1344×768 | 124 | `8967b17a-825d-42cf-9b85-0171a3be193e` |
| `tq4_long_continuation_b7` | `long_continuation.b7.candidate.api.json` | `9ff697348eba57fef2f3db145135dcfbed13c09a7db989a3f10d73879aac01e4` | 768×1344 | 243 + 238 → 481 | `bc4fbde3-1306-4deb-84c6-47769e24bc4a` |

## Clip results

Wall times are `JOB end` seconds from each arm `status.log`. OBJECTIVE lines are from the batch `status.log`. `ffprobe` was re-run 22:32 CT. Raw is the graph canvas; 2x is RTX VideoSuperRes 2x ULTRA (nvvfx). Audio is AAC on every file. No automatic clip review.

| tag | JOB start–end (CT) | JOB s | OBJECTIVE | raw MP4 | raw sha256 | 2x MP4 | 2x sha256 | upscale s |
|---|---|---:|---|---|---|---|---|---:|
| `tq4_two_person_b7` | 17:22:42–17:26:22 | **217.2** | **ok** 124f 1344×768 audio yes 3,634,458 B | 3,634,458 B, 1344×768, 24 fps, 124f, 5.167 s, h264+AAC | `804da3502a333033d2f73c321911212a55a550b528dcc17d86e4e989e02a870c` | 16,927,089 B, 2688×1536, 124f | `6a8353f08ce7c894bca5916de57b9b1fb38408e26d3a30381ce5008a4c4b9fb7` | 5.4 (child 2.92) |
| `tq4_ref2va_16x9_b7` | 17:26:25–17:29:29 | **180.9** | **ok** 124f 1344×768 audio yes 3,717,936 B | 3,717,936 B, 1344×768, 24 fps, 124f, 5.167 s, h264+AAC | `506190e35b61bb200f0a92ef79c14fc4358daf85ba6b0703782d22e24f93bd3e` | 17,446,298 B, 2688×1536, 124f | `dbe7ed40a0e794d153e321ed36279a67960701406e6fa365cbbc2c5d719ca3bb` | 5.5 (child 3.0) |
| `tq4_long_continuation_b7` | 17:29:33–17:41:24 | **708.7** | **ok** 481f 768×1344 audio yes 14,808,873 B | 14,808,873 B, 768×1344, 24 fps, 481f, 20.042 s, h264+AAC | `91cb186d53e62197f70a1d198e74cc3bbd697fdf323808d5f58b274dfa91169a` | 66,040,645 B, 1536×2688, 481f | `d69b27f4f4dd0278f82f0c2e6845d2d98a3576c9252ef9ec9337b73fd3b286af` | 10.5 (child 7.98) |

Fresh ffprobe matches OBJECTIVE on frames, canvas, audio presence, and raw byte counts. All three arms **PASS** objective QA.

Output roots:

- `C:\AI\community\runs\a7_tq_ab_20261119\tq4_two_person_b7\`
- `C:\AI\community\runs\a7_tq_ab_20261119\tq4_ref2va_16x9_b7\`
- `C:\AI\community\runs\a7_tq_ab_20261119\tq4_long_continuation_b7\`

Batch closed 17:42:15 CT (`gpu_lock` released, `comfyui_auto` unloaded at 17:41:28 CT).

## Promotion

**Not promoted.** Derrick still eye-picks these three candidates. 16:9 ref routing stays on 1-pass `oc_ref` until that pick and an approved allowlist/production swap. The S2 allowlist continues to refuse `*.candidate.api.json`.

## Restore

Clips and filled requests are already on disk under the A7 run dir. This report does not change live templates. Archive copy: `C:\AI\_archive\20261119\TQ4-RESULT.md`.
