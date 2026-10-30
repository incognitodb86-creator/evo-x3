# 2026-10-29-terrace-retest-plan — B2 vs the stock LokkenJP graph, then one setting at a time

Owner: Forge (plan drafted from Max's brief `briefs\2026-10-29-terrace-retest-plan.md` + Max's audit
`briefs\2026-10-29-2040-forge-brief2-check.md`). GO: Derek 8:19 PM ("do the plan, do the work tonight"),
Max 9:10 PM brief 3 = run it autonomously with recovery. Status: **arms built and self-checked; rendering
tonight.** Judge scores are **flags only** for the machines; **Derek scores the winners** next page.

## Question
Does the community stock graph (`simple_v2`, LokkenJP) beat our B2 on the same start frame at 5 s /
768×1344, and if it does, which single setting closes the gap?

## Hypothesis
**H1** B2 (int8HQ + `er_sde`/`simple` + conv_v1_bf16 upscaler + Add Guide, 384×672 → ×2) scores above
the stock graph's finished file at the same frame/length, same prompt, three seeds. **H0** no gap ≥ 1.0.
**Mechanism** the four settings where B2 differs from stock by choice (model, sampler+scheduler,
upscaler, guide). **Baseline** B2 s51083002 (keeper, 243 f ≈ 240 s). **Single-variable** B2 + one change.
**Negative control** S4 `ref_image_size: max → match` (T4's #74 fix = the flicker cause) must get worse.
**Sample** 3 seeds × 2 systems; Stage 2 one seed per setting, 3 seeds only for a flagged winner.

## Design (2 stages, 15 graphs, all 124 f = 5.17 s)
Stage 1 — B2 × 3 seeds, T4c (stock) × 3 seeds. T4c = `simple_v2` with **only** the start frame loaded,
B2's prompt, a fixed seed, Duration 5.0 (→ **124 f** through the graph's own formula), portrait
`9:16 @ 0.25 MP` → pass-1 **384×672** (B2's own pass-1 canvas) and the shipped `1.0 MP` upscaler →
**768×1344**; everything else as shipped (int8-activation model, `er_sde`+`sgm_uniform` 8 / `beta` 3,
fp16 upscaler, no guides, RTX 1.2 → 928×1600, grain, crf 18). **T4c is judged on its `_raw` file**
(768×1344, pre-RTX/pre-grain); the processed file is recorded, not judged. `t4g` (guides wired on) is
built as an optional extra cell — the stock UI turns the two Add Guides on through the rgthree
follow-the-loader relay, and the converter's static pass-through drops them, so plain T4c has none.
Stage 2 — S1-S8 on B2, seed 51083002, reference = Stage-1 B2 s51083002.

| arm | the one change | why |
|---|---|---|
| S1 | `euler`+`simple` → `er_sde`+`sgm_uniform` | the stock sampler pair |
| S2 | int8HQ → int8-activation HQ | which checkpoint is cleaner (T4 12/12) |
| S3 | conv_v1_bf16 → fp16 upscaler | the stock upscaler |
| S4 | `ref_image_size: max → match` | the #74 flicker fix — negative control |
| S5 | both Add Guides off | are the guides carrying identity? |
| S6 | 8 → 6 steps | T4's 6-step KEEP |
| S7 | `euler` → `res_multistep` | the #74 sampler |
| S8 | + one prompt line | identity: `<Picture 1> is the correct scene identity, the main subject, the character to animate.` = LokkenJP's exact words from TenStrip/10Eros-Max **discussion #74** (saved: `notes\web\hf_tenstrip_disc74_2026-10-29.md`); 335 chars, sha256 `dae7567438227802b08d6276faece019759c43958199f97cb2482c5daf8e2908`. Nothing else in the prompt moves. |

## Gates, in this order, before every render
1. `python -m pytest scripts\tests\test_p6_review.py scripts\tests\test_guard_scope.py -q -p no:cacheprovider`
   from `C:\AI\community` — must pass, else no render.
2. `comm.guard_ok` over the graph's prompt strings (what `run_graph_job.py` runs).
3. **Prompt hash from the `api.json` being submitted** (B2 arms = `fcad1c379bf097f3…`; S8 = B2 + only
   the added line, verified by stripping it).
4. Graph diff vs the baseline = the declared keys and nothing else; **T4c diffed against
   `_ui2api\api_T4.json`** (`simple_v2` as runned, id-aligned 1:1 — against the raw stock file the
   enabled LoadImage shifts ids by +1 from 19 and inert nodes materialise, which is not key-comparable).
5. Frame count 124 and canvas 768×1344 computed from the graph's own widgets, then enforced by
   `run_graph_job.py --frames 124`.
Self-check (`notes\terrace_retest_arms_audit.py`) = the same list over all 15 built arms. **An arm that
fails is dropped and logged, never hand-edited and run.** Table: `notes\2026-10-29-terrace-retest-diff.md`.

## Judge, budget, stops
`judge\prechecks.py` + `judge\vlm_judge.py --variants Z` on every clip, T4c on its `_raw`; flags only.
One job at a time through `run_graph_job.py` + `C:\AI\locks\gpu-render.lock`; 124 f ≈ 3 min B2, ≈ 4 min
T4c, so the full 15-run queue ≈ 55 min GPU, 17 runs ≈ 75 min if every flagged arm gets 2 seeds.
Recovery per brief 3: on an error/OOM/WinError 1450/ComfyUI crash → log it, `comfy_ctl.py` restart, free
the lock, retry that arm **once unchanged**; second failure drops the arm and a blocker note; never change
settings to make an arm pass; never kill llama-swap, strata or the pi-mobile hub; if the adults test, the
guard, or < 30 GB free disk blocks everything → stop and write `notes\2026-10-30-terrace-BLOCKED.md`.
Stop the queue after 3 consecutive failures or a > 30 % runtime overrun vs the estimates.
Adoption needs: mean > B2 by ≥ 1.0 on a 0–10 blind scale, wins ≥ 2 of 3 seeds, zero negative-control
failures, and no unexplained ≥ 30 % runtime overrun; B2 stays the default graph in
`p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json` until Derek adopts a passing arm.

## Appendix — file and number checks (verified 2026-10-29, read-only)
- **B2 of record** `runs\terrace_dom_q5guide_20261028_s51083007\request.api.json` (20,072 B, 26 nodes,
  sha256 `8d1d1a41e9915f2a…`) = `p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json`; prompt
  13,128 chars sha256 `fcad1c379bf097f3…`; seed `51083002`; pass-1 384×672 ×2.0 → 768×1344; 243 f.
- **Stock** `runs\terrace_dom_q5stockv2_20261028_s51083011\stock_simple_v2.json` sha256
  `a315ac74a24a14d4…` (35 UI nodes, 3 subgraph defs, instances 151/152/178; 128 inputs inert);
  converter `t4_ui2api3.py` unchanged; converted baseline `_ui2api\api_T4.json` (41 nodes).
  Frame formula `max(5, round(a*24)) + (5 - (max(5, round(a*24)) % 17)) % 17` → 5.0 s = 124, 10 s = 243,
  15 s = 362; **121 is not reachable** (all values are 5 mod 17).
- **Start frame** `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\TERRACE2_768x1344.png`
  1,352,963 B, IHDR 768×1344 (ratio 4:7, not 9:16 = 0.5625). Canvas stated as **4:7, 768×1344**.
- **Geometry math** (installed `nodes_resolution.py`, `multiple = 32`): 9:16 @ 0.25 MP → 384×672
  (latent 48×84). Installed `minimax_h3_latent_upscaler_3d.py` `mode=megapixels, 1.0, align 32`,
  ds 8 → scale 2.0158 → 768×1344, then RTX ×1.2 → 928×1600 (rounded to 32) on the processed file only.
- **Runtime facts** T4 10 s stock = 588.4 s wall (`notes\2026-10-29-T4-stock-v2-render-DONE.md`) → ≈ 360 s
  at 124 f; B2 5 s 243 f = 240.1 s → ≈ 125 s at 124 f. Disk 896.2 GB free. Judges 488 / 362 lines.
- **Arm dirs** `runs\terrace_retest_20261029\<arm>_s<seed>\` with `request.api.json`, `graph_diff.txt`,
  `build_graph.py`, `build.log`; builders `_build_b2_arms.py` / `_build_t4c.py`; S8 text `_src\`.
- **Not for pass/fail** `60_reviews\` (the template's path does not exist) — review packs go to
  `review\<topic>\` as in `review\hc169\`. Judge flags are informational; Derek scores.
