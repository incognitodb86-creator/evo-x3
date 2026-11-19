# A and C rendered + post-processed — 2026-10-28 16:20 CT
Ran per notes/2026-10-28-max-brief-abc-reset.md (steps 1-5). No new scripts; one PowerShell call per render.

## Arms (constants per ab_q4_q5_brief_2026-10-28.md: beta7 int8HQ, euler/simple, shift 12/3, VSA keep_percent 10 start 0 end 1 dense_blocks "0,1", comfy kitchen attention, ref_image_size match, TERRACE2_768x1344.png, 243f @ 24fps, seed 51083002, prompt v2 sha 46352afd2a64637a)

| arm | dir | steps | render s | s/frame | raw bytes | final bytes |
|---|---|---|---|---|---|---|
| A (Q4 native) | runs/terrace_dom_q4_20261028_s51083004 | 8 | 360.1 | 1.48 | 4,377,514 @768x1344 | 7,569,752 @920x1616, 5981 kbps |
| C (12 steps) | runs/terrace_dom_c12_20261028_s51083006 | 12 | 480.2 | 1.98 | 4,587,989 @768x1344 | 7,430,335 @920x1616, 5871 kbps |

- C/A = 1.33x cost (brief predicted ~1.5x). Both: 243 frames, 10.125 s, audio present, 0 re-queues, one job each, OBJECTIVE ok, guard IDLE after every window.
- Post: raw kept as `*_raw.mp4`, RTXVideoSuperResolution 1.2x ULTRA (graph in `<run>/post/`), then libx264 slow crf 18 + `-c:a copy` → `*_final.mp4`. RTX measured here: **60.1 s for 243 frames at 920x1616 (0.25 s/frame)** — the brief's 2-4 min/clip estimate was ~3x too high. Output is aligned to 8: 768x1344 → **920x1616** (not the brief's 922x1613).
- Delivered to /pi-drop/: A_raw, A_final, C_raw, C_final (sizes verified against the local files).

## The one code change
`scripts/post_graph_build.py`: the RTX nested input key is `resize_type.scale` (V3 dynamic combo prefixes with the *parent input name*, not the node id). The old key `scale` produced static `rtx.scale: not an input of RTXVideoSuperResolution` (node id prefix in the message). Self-check updated to the same key. RTX smoke cell `runs/rtx_smoke_20261028` now passes: 60.1 s, 24f, 304x536 out, audio kept.

## 16:37 CT, Derek: "Why did you do different resolutions????" / "For a and c"
Derek wants the deliverables compared at a matched resolution, so each arm now ships a native-size final too. Naming convention from here on:
- `*_raw.mp4` = the render, untouched (768x1344)
- `*_rtx12.mp4` = RTX 1.2x ULTRA output (920x1616)
- `*_final.mp4` = **crf-18 of the RAW, native 768x1344** (`finalize_encode.py` with the RTX arg omitted)
- `*_final_rtx920.mp4` = the RTX path encoded at crf-18 (renamed copy of the earlier `_final.mp4`, nothing deleted)

| arm | native final | rtx920 final |
|---|---|---|
| A | 6,054,428 B, 768x1344, 4784 kbps | 7,569,752 B, 920x1616, 5981 kbps |
| C | 6,035,029 B, 768x1344, 4768 kbps | 7,430,335 B, 920x1616, 5871 kbps |

All 8 files (raw / rtx12 / final / final_rtx920 per arm) are on /pi-drop/, sizes verified. CPU encodes only, no GPU window, guard stayed IDLE.

## B (Q5, official 3D latent-upscaler two-pass) — Derek: "Ok restart and do the other test", 16:40-17:00 CT
`comfy_ctl.py restart` at 16:40 (stop → start → COMFY_OK). `MinimaxH3LatentUpscaler3D` registered after the restart (`objinfo_has.py` present_exact=True, dump 2644 nodes); checkpoint `minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors` 690,592,992 B in `models/latent_upscale_models/`, and the node's own `model_name` COMBO lists exactly that file.

**Three static-validation failures fixed in `runs/terrace_dom_q5_20261028_s51083005/build_graph.py`** (the graph had never been submitted before, so these were first-contact bugs, all confirmed against the live node spec, no new scripts):
1. `mode` is a `COMFY_DYNAMICCOMBO_V3` whose inner widget is named `scale` → the API key must be `mode.scale` (the same class of bug as the RTX `resize_type.scale`).
2. `SplitSigmas` has **no `split_at` input**; the required widget is `step` (INT, default 0). `comm.build` already emits `s0_split` with a stale `split_at` key, so the graph carried both — the extra key is itself a static error; it is now popped.
3. `MinimaxH3LatentUpscaler3D` has a **required `force_unload`** (BOOLEAN, node default True) → set `true` (the node's own default, so no deviation from the community path) and self-checked.
Also repaired `scripts/probe_full.py` (a stray duplicate loop at the top made it a SyntaxError; the `probe()` function and its driver were intact) — it is the tool that read the live specs above.

Gates: 25 build self-checks ok, diff gate vs arm A `changed=none` (the 8 two-pass nodes are the declared arm), `pytest test_p6_review.py` 21 passed, prompt byte-identical in all three arms (2284 words / 13,128 chars / sha `fcad1c379bf097f3`), one job, 0 re-queues, guard IDLE after every window.

| arm | render s | s/frame | raw B (768x1344) | final (native crf-18) | rtx12 / final_rtx920 (920x1616) |
|---|---|---|---|---|---|
| A 8 steps | 360.1 | 1.48 | 4,377,514 · 3459 kbps | 6,054,428 · 4784 | 5,291,919 / 7,569,752 · 5981 |
| C 12 steps | 480.2 | 1.98 | 4,587,989 · 3625 | 6,035,029 · 4768 | 5,559,517 / 7,430,335 · 5871 |
| **B Q5 two-pass** | **240.1** | **0.99** | 11,560,944 · **9135** | 13,976,114 · 11043 | 14,404,237 / 17,662,059 · 13955 |

B is the **fastest** arm (0.99 s/frame vs A's 1.48) and its encode carries 2.6x the bitrate at the same crf — the latent upscaler's output is much higher-frequency. Not proof of quality: h264 pays for grain.

**Motion (motion_check.py, same script, all three raws).** Noise floors: A 5.486, C 5.837, **B 11.183** — B's whole-frame micro-difference is 2x A's, so cross-arm comparison is not valid on the absolute numbers, and its `right/floor` ratios normalise that texture away. Right-half thirds: A 6.96/5.12/4.01 (ends 0.25x), C 8.17/5.22/3.88 (ends 0.42x), **B 12.75/12.75/12.09** with no mid-clip or ending collapse and only one LOW-ALL bucket (10.0 s). Reading: B keeps the receiver moving through the 8-10 s window that A and C both lose — but part of that energy is texture, and Derek's watch is the judge. B's peak whole-frame event is at t=7.75 s (62.79).

**Audit hygiene:** the `verify_cell.py` copy in B's dir is the **v2 cell's** audit (it asserts seed 51083003, er_sde, `up`/`ksel2`/`g2`/`p2sched` node names, 3,071,104 B, 300.1 s). 12 of its checks FAIL on B for exactly that reason; every arm-independent check (beta7 int8HQ, shift 12/3, VSA keep 10, ck attention, ref match, canvas/fps, decode-from-pass-2, cond, prompt byte-equality, no loras/RIFE/pixel upscale, single chunk, no black/frozen, 1 job, contact sheet) is ok. Per-cell audit scripts must be written per arm — recorded so the next cell does not inherit a foreign audit.

All 12 files (4 per arm: raw / rtx12 / final-native / final-rtx920) are on `/pi-drop/`, sizes verified against the local files. GPU released, `gpu_guard` IDLE.

## Not done (needs Derek)
- ~~**B (Q5)**~~ — rendered 2026-10-28 16:55 CT after Derek's "Ok restart and do the other test" (see the section above).
- No KEEP/PASS judged; no files deleted.
