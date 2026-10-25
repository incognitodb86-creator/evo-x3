# HC15 start-fidelity audit — why the clips do not start on their start images

Item: `fix_plan.md` FIRST ("They should start closer to the reference image what the fuck? Do an audit
something is wrong", Derrick 2026-10-24 5:49 PM CT). Audited: the six rendered HC15 clips in
`C:/AI/community/runs/hc15_*` + their graphs `C:/AI/community/p7/graphs/ali163_hc15_*.api.json`.
Builder / receipts: `C:/AI/community/notes/hc15_anchor_fix_build.py` (`--metrics --build --check --selftest --sheet`),
`C:/AI/community/notes/hc15_audit_timing.py`. No GPU was touched by this audit.

## Verdict (three findings, in order of size, plus the measured fix)

1. **Nothing pins frame 0.** All six graphs generate with `MiniMaxH3ReferenceToVideo` in all three segments and
   never use a keyframe. `grep` over the six graphs: `first_frame` 0 hits, `last_frame` 0 hits,
   `MiniMaxH3AddGuide` 0 hits, `MiniMaxH3ImageToVideo` 0 hits. A reference image is a *conditioning* input
   (`ref_images.ref_image_1..3` + `<Picture i>` prose); the start frame is generated from noise. The published
   mechanism that anchors a frame is the keyframe/guide path: ComfyUI PR 15439 adds
   `MiniMaxH3AddGuide` "for anchoring image and audio guides at any frame"
   (<https://github.com/Comfy-Org/ComfyUI/pull/15439>, merged 2026-08-13, saved
   `notes/web/hc15_pr15439.json`), and the shipped native template uses `MiniMaxH3ImageToVideo` with
   `first_frame`/`last_frame` (`ComfyUI/templates/video/Minimax_H3/i2v.json`, `io.Input("first_frame", "IMAGE",
   optional=True)` at `comfy_extras/nodes_minimax_h3.py:148`). The Continuum guide states it in one line:
   "First/Last **additionally constrain the video**"
   (<https://raw.githubusercontent.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/main/docs/USER_GUIDE.md>).
2. **Measured, frame 0 is as far from the start still as any later frame** — the clips do not begin near the
   picture, they begin somewhere else. Table below: SSIM/PSNR of frame 0 against the clip's own `LoadImage`
   start still is 0.23–0.35 / 6.1–11.6 dB, and for 4 of 6 clips the *mid* or *last* frame scores higher than
   frame 0. Face identity: best ArcFace cosine of a start-still face against any face in frame 0 is
   0.025–0.404, i.e. 0.5–0.87 of the 0.90 gate this repo already uses for face crops
   (`notes/ali163_hc_r4g2_verify.py:87`). GI063 frame 0: **no face detected at all**.
3. **The pass shape is off the published example, and the sampler is off the model card.** HC15 samples 124 f
   three times (124+141+141 = 362 f = 15.0833 s) at 10 steps with `euler/simple`. The published continuation
   example generates a **243-frame** initial clip and extends it once (`overlap_frames = 22`,
   `extension_frames = 119`, `window_length = 141`) — 2 passes, not 3
   (<https://raw.githubusercontent.com/ttulttul/ComfyUI-Minimax-H3-Continuation/main/README.md>, saved byte-identical
   as `notes/web/hc15_continuation_readme.txt` and `notes/web/03y_continuation_readme.txt`). The model we run
   (TenStrip/10Eros-Max) publishes its sampler table: **"res_multistep/simple 6-8 steps (my go-to for best
   motion quality)"**, and `euler/simple` is listed as "for simple motion and faster tests"
   (<https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md>, saved byte-identical as
   `notes/web/hc15_tenstrip_readme.txt`, verified sha256 `ba3be667…` against
   `notes/web/agy51_tenstrip_readme.md`). Every extra generated window is also a fresh chance to drift, so the
   3-pass shape multiplies finding 1.
4. **Delivered, measured, seed-locked (2026-10-24 19:54 CT).** The three switches above, rendered on clip 1 with
   the same seed 51150001, move frame 0 from SSIM 0.3476 / PSNR 6.74 to **0.9154 / 29.58** and put both
   start-still faces **0.875 / 0.748** (over the 0.45 gate) where they were 0.217 / 0.328. Finding 1 was the
   cause. Full evidence, including the 3-tile frame-0 sheet: "Frame-0 before/after" below.

## Frame 0 vs the start still (measured, `notes/hc15_audit/metrics.json`)

Start still resized to the 1344x768 canvas two ways: `cover` = aspect-preserving center-crop (what
`last_frame` does, `nodes_minimax_h3.py:337 _cover_center_crop`), `stretch` = plain resize (what `first_frame`
does, `:251 _prepare_keyframe_image`). Faces: CPU SCRFD-10G + ArcFace (`notes/hc_r4f_facelib.py`), cosine of
each start-still face against every face detected in the frame, best per source face.

| clip | seed | start still | SSIM f0 (cover) | PSNR f0 | SSIM f0 (stretch) | faces in f0 | best ArcFace cos in f0 | SSIM f181 | SSIM f361 |
|---|---|---|---|---|---|---|---|---|---|
| bd002 | 51150001 | community/hc/BD002.jpg | 0.3476 | 6.74 | 0.3509 | 2 | 0.217 / 0.328 | 0.3646 | 0.2962 |
| bd006 | 51150002 | community/hc/BD006.jpg | 0.2389 | 7.01 | 0.2434 | 2 | 0.404 / 0.059 | 0.2440 | 0.2719 |
| bd013 | 51150003 | community/hc/BD013.jpg | 0.3147 | 6.14 | 0.3165 | 2 | 0.163 / 0.097 | 0.3675 | 0.3653 |
| gi046 | 51150004 | community/hc/GI046.jpg | 0.2928 | 11.63 | 0.2932 | 1 | 0.257 | 0.3164 | 0.3009 |
| gi063 | 51150005 | community/hc/GI063.jpg | 0.3108 | 11.29 | 0.3166 | **0** | none detected | 0.3043 | 0.2850 |
| gi072 | 51150006 | community/hc/GI072.jpg | 0.2315 | 8.51 | 0.2292 | 1 | 0.314 / 0.025 | 0.2495 | 0.2474 |
| **bd002 + anchor** | 51150001 | community/hc/BD002.jpg | **0.9154** | **29.58** | 0.7720 | 2 | **0.875 / 0.748** | 0.5644 | 0.3862 |

The last row is the re-render of the same clip, same seed, with the switch set (`ali163_hc15_bd002_s51150011`):
frame 0 goes from SSIM 0.3476 / PSNR 6.74 to **0.9154 / 29.58**, and the two start-still faces go from
0.217 / 0.328 (both under the 0.45 identity gate) to **0.875 / 0.748** (both over it). Frame 0 is now the
closest frame of the clip, which is what an anchor is supposed to do.

Frame 0 was not the closest frame for bd002 (f181 0.3646 > f0), bd006 (f181 0.2440 > f0), bd013 (f181 0.3675,
f361 0.3653 > f0) and gi072 (f361 0.2474 > f0). Reproduce:
`"C:/Program Files/Python312/python.exe" C:/AI/community/notes/hc15_anchor_fix_build.py --metrics`.

## Graph anatomy (identical in all six; `ali163_hc15_bd002_s51150001.api.json` = 33 nodes)

`c0/c1/c2` = `MiniMaxH3ReferenceToVideo` (canvas 1344x768, `c0.length` 124, `ref_image_size` "max");
`img` = the approved start still → `ref_images.ref_image_1`; `img2` (and `img3` for gi072) = face crops →
`ref_images.ref_image_2/3`; `win1/win2` = `MiniMaxH3GuidedContinuationWindow` (overlap 22, extension 119,
window 141) + `tail1/tail2` guides + `app1/app2` appends → 124+119+119 = 362 f; `ksel` = `euler`,
`s0/s1/s2_sched` = `simple` @ 10 steps, `denoise` 1.0; `m_shift` = shift_video 10.0 / shift_audio 3.0;
`m_vsa` = `dynamic` sparsity, `video_only`=true, topk 0.15; two `SamplerCustomAdvanced` (s0 with `denoise` 1.0,
the continuation sampler keeps its own); `avae` wired to `c0.audio_vae` and `dec_a`; no keyframe node of any
kind. Note for the record: pair clips reference **one** of the two faces (`ref_image_2` only) and the whole
start still as `ref_image_1`.

## Community values, with the URL behind each row

| setting | HC15 shipped | published value | source |
|---|---|---|---|
| start anchor | none (reference conditioning only) | keyframe/guide path: `MiniMaxH3AddGuide` `frame_idx` 0 (same `minimax_keyframes` mechanism as `first_frame`, `nodes_minimax_h3.py:145-149` vs `:220-223`) | <https://github.com/Comfy-Org/ComfyUI/pull/15439> + <https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md> ("Anchoring guides at any frame (#15439)", "Anchoring a guide at a frame is the shared mechanism behind image keyframes") |
| sampler / scheduler | `euler` / `simple` | "res_multistep/simple 6-8 steps (my go-to for best motion quality)"; euler is "for simple motion and faster tests" | <https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md> |
| steps | 10 on all three schedulers | 6–8 (same table); reference-class runs 8–12 = "slower, more complex" | same file |
| denoise | 1.0 | keep the ordinary full-denoise schedule for continuation | <https://raw.githubusercontent.com/ttulttul/ComfyUI-Minimax-H3-Continuation/main/README.md> ("Use the ordinary H3 model and a normal full-denoise schedule") |
| pass shape | 124 f × 3 passes (124+141+141) | "The example first generates a 243-frame clip", then one window `overlap_frames = 22, extension_frames = 119, window_length = 141` | same file (243 = the `(frames-5) % 17 == 0` grid: `(243-5)%17 = 0`, `(22-5)%17 = 0`, `119%17 = 0`, `243+119 = 362 = 15.0833 s @ 24 fps`) |
| canvas | 1344x768 (1.036 MP) | the node's published defaults: `width` 1344, `height` 768 (`nodes_minimax_h3.py:129-130`); docs list 1280x768 = 16:9 and 640x640 = 1:1 for 16 GB cards | <https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md> |
| length per pass | 124 (= ~5 s) | length tooltip: "124 (~5s), 243 (~10s), 362 (~15s). Trained range ~124-362; longer is untested" (`nodes_minimax_h3.py:136`) — HC15's 124 is legal, the published *example* is 243 | same file + continuation README |
| shift | video 10.0 / audio 3.0 | node published defaults | `nodes_minimax_h3.py:193-194` |
| attention | `dynamic` VSA, `video_only` true, topk 0.15 | the card's "ideal configuration" for 16 GB: VSA sparsity ON, video-only ON, topk 0.1–0.2, "Use no cache and no spectrum when you do reference. Do not use SLA sparsity with reference workflows" | <https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md> |
| ref slots | 1 = whole start still, 2/3 = face crops, `ref_image_size` "max" | 32-reference limit, `match`/`max` documented; R2V = "Lock character, style, motion, camera, or voice from reference images" (not a start-frame pin) | <https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md> |

## Timing (item asked: time each segment, compare to community, check the server flags)

Per clip, from `runs/hc15_*/objective.json` + `*.mp4.json` (`notes/hc15_audit/timing.json`):

| clip | frames | wall secs | finished (CT) |
|---|---|---|---|
| bd002 | 362 | 757.4 | 16:59 |
| bd006 | 362 | 752.5 | 17:13 |
| bd013 | 362 | 752.4 | 17:26 |
| gi046 | 362 | 777.1 | 17:40 |
| gi063 | 362 | 787.5 | 17:54 |
| gi072 | 362 | 802.5 | 18:08 |
| bd002 + anchor (2 passes, 8 steps) | 362 | **571.7** | 19:54 |

The 2-pass / 8-step shape measured **571.7 s**, i.e. 181-231 s (24-29 %) faster than the six shipped clips, in
line with the ~250 s the 3-pass shape costs above the published 2-pass example. Same canvas, same 362 f, same
audio path, so the saving is the pass count and the 10→8 steps.

Durable ComfyUI-side lines: `[2026-10-24 17:54:11.206] Prompt executed in 00:13:02` and
`[2026-10-24 18:08:12.679] Prompt executed in 00:13:21` in
`C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/user/comfyui_10004.prev2.log` / `comfyui_10004.prev.log` —
they line up with the gi063 (17:54) and gi072 (18:08) finishes, so 787.5/802.5 wall s = 99.3 % / 99.8 % of the
ComfyUI-side cost: the llama-swap swap-in is ~5 s, not the bottleneck. Server lines from the same files:
`Total VRAM 16275 MB, total RAM 65235 MB`, `Using pytorch attention`.

Per-segment: ComfyUI's Prompt log (`ComfyUI/Prompt_<start>.log[.N]`, one JSON line per prompt with segment
frame lengths as keys and seconds as values) was readable at 18:30 CT and gave, for the 10-step HC15 shape,
**124 f = 179.00 s**, **141 f window = 267.00 s**, audio decode ≈ 35 s (sum 748 s vs 752.4 s wall for bd013).
Those files are gone now (`find -name 'Prompt_*'` under the install = 0 files at 18:55 CT), so the per-segment
row is transcript-captured, and `notes/hc15_audit_timing.py` prints `PROMPT_LOGS_ABSENT` and leaves
`segments: null` — re-run it while a Prompt log exists to refresh the table.

Community timing: no per-clip numbers are published for H3 on a 5070 Ti. The published qualitative statements
are the card's ("Reference model: Slow 8-12 steps, use no cache and no spectrum, more complex", same TenStrip
README) and the docs' VRAM/time table for 16 GB cards (<https://docs.comfy.org/tutorials/video/minimax/
minimax-h3-native.md>). The server flags: llama-swap starts ComfyUI with
`--lowvram --disable-async-offload --disable-pinned-memory --use-ck-attention`
(`C:/Users/derek/.llama-swap.trial.bak:92`, `C:/Users/derek/.llama-swap.yaml.bak-20261022-170635:70`,
`C:/Users/derek/.llama-swap.prev.yaml:70`). None of them changes sampling math: they trade GPU residency for
the LLM window (`swap_delay`, unload) and are the community mitigation for 16 GB + ComfyUI 0.19.x
(<https://github.com/Comfy-Org/ComfyUI/issues/15337> = a 1344x768 H3-with-audio OOM report on a 16 GB RTX 5080
laptop; the llama-swap ComfyUI integration guide <https://github.com/mostlygeek/llama-swap/blob/main/docs/comfyui.md>
documents the swap/unload semantics, default `unload_delay` 300 s). Verdict on timing: **not the reported
defect, and no setting to switch** — ~13 min per 362 f job is the published slow reference/10-step class cost on
16 GB, and 3 passes cost more than the published 2-pass example. The 2-pass shape also cuts ~250 s per clip.

## Root cause, ranked

1. No start-frame keyframe (`first_frame`/`AddGuide frame_idx 0`) in any HC15 graph → frame 0 is free
   generation from noise, conditioned by reference images and prose only.
2. 3 chained generated windows (124 f × 3) where the published example is 243 f + one 141 f window: more
   free-generation windows, more drift, more time.
3. Sampler/steps off the model card's motion-quality setting (`euler`/10 vs `res_multistep`/6-8).
4. Secondary, not switched in this item: prose labels every start image "a woman" (GI046/GI063/GI072 include
   a robot and an orc per Derrick 5:48 PM CT) — that is the **NEXT** fix_plan item, so prompts stayed
   byte-identical here; and pair clips reference only one of the two faces.
5. Ruled out as causes: canvas/MP (node default, docs-sanctioned), shift (node default), VSA settings (match
   the card's "ideal configuration" for reference), denoise (full schedule, as published), server flags
   (no math effect), the 22-frame overlap (motion context only, the guide's documented design), swap overhead
   (~5 s of 787).

## The switch set shipped with this audit (offline, no GPU)

New graph `C:/AI/community/p7/graphs/ali163_hc15_bd002_s51150011.api.json` (27 nodes, 18235 B, sha256
`8a57ebbf456b6f9d74ad1ca2424076041e8ad0c524d15f7f8a7c9a126a57e769`), built by
`notes/hc15_anchor_fix_build.py --build` from the rendered clip-1 graph, prompts byte-identical, seed
51150001 unchanged, canvas 1344x768 unchanged, `ref_image_size` "max" unchanged, shift/VSA/fps/audio path
unchanged:

- **A** new node `g0` = `MiniMaxH3AddGuide` with `frame_idx` 0, `image` = the clip's own `LoadImage` start
  still, `vae`/`latent`/`positive` on the c0 edge, and `s0_guide.conditioning` now fed by `g0` — the published
  anchor mechanism (PR 15439), which is what `MiniMaxH3ImageToVideo.first_frame` compiles to
  (`resolved_frame_index … 0` + `minimax_keyframes`).
- **B** `ksel` = `res_multistep`, `s0_sched`/`s1_sched` steps 8, scheduler `simple`, `denoise` 1.0.
- **C** `c0.length` 243 + one continuation window (22/119/141) = 243+119 = 362 f = 15.0833 s, 2 sampling
  passes instead of 3.

Receipts: `--check` = 13 named detectors (ANCHOR, SAMPLER, GEOMETRY, UNCHANGED, SCOPE, SCHEMA, GATE, INTEGRITY,
ARM, AUDIT-CITED, METRICS, BYTEFORMAT, STALE-SHEET) and `--selftest` = 38 seeded faults, each of which must
fire a named detector and 0 on the real artifact. Measured 2026-10-24 20:20 CT:
`CHECKS real ALL 13 PASS` / `SELFTEST seeds=38 fired=38 silent=0 real_problems=0`.
ARM and METRICS have two states on purpose: before the render they assert the arm is submittable and the
defect is measured; after it they assert the render's own proof (`objective.json ok` + `ffprobe` agreement on
362 f / 1344x768 / 24 fps / audio, 0 blackfreeze) and the measured frame-0 improvement. A receipt that went
red the moment the item was delivered would be worthless.
The handoff for the render itself is
`C:/AI/community/p7/JOB_REQUEST.json` (id `ali163_hc15_bd002_s51150011`, frames 362, 15 min; ledger
`C:/Users/derek/5slock/ralph-community/logs/p7_budget.json` = 472.9/615 min, 38/45 jobs, so the clip fits).

## Frame-0 before/after (the render the item asks for) — delivered

The Ralph pass built the arm and stopped; a GPU window rendered it (a Ralph pass never queues:
`PROMPT.md`, `AGENTS.md`). Evidence on disk:

- clip: `C:/AI/community/runs/ali163_hc15_bd002_s51150011/ali163_hc15_bd002_s51150011.mp4` — 362 f,
  1344x768, 24/1, duration 15.083333, 6,145,778 B, audio stream = `aac`, `objective.json ok=true`,
  `blackfreeze=[]`, wall 571.7 s, finished 19:54:29 CT, sha256
  `31fdc8fcfb1e6594c68d28607a0c49216e1610b9cb7fd3766aa4b7d5476a17b2`.
- arm bytes: `runs/ali163_hc15_bd002_s51150011/request.api.json` is byte-identical to
  `p7/graphs/ali163_hc15_bd002_s51150011.api.json` (18,235 B, sha256
  `8a57ebbf456b6f9d74ad1ca2424076041e8ad0c524d15f7f8a7c9a126a57e769`), so what rendered is what the builder
  wrote.
- frame-0 sheet: `runs/ali163_hc15_bd002_s51150011/ali163_hc15_bd002_s51150011_frame0_sheet.png`
  (2,484,529 B, sha256 `71625c337c64b64b1dbffd1a7bb731d99fe891bff67a452bb6d2bfa0eac0b98e`) — three labelled tiles: start still, BEFORE (clip 1 frame 0, euler/10, 124 f ×3, no anchor)
  SSIM 0.3476 / PSNR 6.74, AFTER (frame 0 of this clip, `AddGuide frame_idx 0`, res_multistep/8, 243+119 f)
  SSIM 0.9154 / PSNR 29.58. Built by `notes/hc15_anchor_fix_build.py --sheet`, ffmpeg + PIL only: no vision
  judge, and KEEP is Derrick's alone. Per-second contact sheet from the render tool:
  `runs/ali163_hc15_bd002_s51150011/ali163_hc15_bd002_s51150011_stills_contact.png`. The sheet and the mp4 live
  in `runs/`, which `.gitignore` ignores, so the durable record is these hashes + `notes/hc15_audit/metrics.json`.
- seed 51150001 unchanged, so the pair is a seed-locked A/B on exactly the three switches.

Not stamped: the GPU window did not add this clip to the ledger (`logs/p7_budget.json` still 472.9/615 min,
38/45 jobs, `updated 2026-10-23T18:53:47`), and there is no `p7/jobs/ali163_hc15_bd002_s51150011.result.json`.
Reported in `notes/needs_derrick.md`, not fixed: the ledger is the loop's budget gate.

## Limits of this audit (read before acting on the numbers)

SSIM/PSNR of a generated frame against a photograph is composition- and lighting-sensitive, so treat the
numbers as a relative signal across the six clips and across frames of one clip, not as an absolute
"similarity to the picture". ArcFace cosine on a 10-step 15 s generation is an identity signal, not a
photometric one. No human or vision-model judge looked at a frame; there is no vision judge in this loop
(`AGENTS.md` hard line). The published res_multistep/6-8 setting is the card author's go-to for the distilled
model, not a ComfyUI mandate. The anchor mechanism's latent-space effect at frame 0 is now measured on this
box, on one clip, seed-locked: SSIM 0.3476 → 0.9154, both start-still faces 0.217/0.328 → 0.875/0.748. That is
n=1: it says the switch set closes the start gap on bd002, not that it fixes the framing of the pair clips, and
the anchor also changes framing (the 3:2 still is stretched to the 16:9 canvas at 0.772 SSIM stretch, so
`first_frame`-style stretch, not `last_frame` center-crop, is what the graph lands). `last_frame`
center-crops, `first_frame` stretches
(<https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md>), so a 3:2 still on a 16:9 canvas
changes framing under the anchor; frame 0 will land close to the still, and framing for the pair clips is the
prompt item's job.
