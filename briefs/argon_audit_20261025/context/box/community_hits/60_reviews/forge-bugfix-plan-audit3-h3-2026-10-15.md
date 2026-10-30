# Fleet Reviewer audit #3: Forge bugfix plan, community fold-in + H3 fit (2026-10-15)

**Role:** Independent, report-only. Nothing changed except this file.
**Plan:** `/workspace/docs/plans/2026-10-15-1513-fix-forge-bugfix-setup-plan.md` (**283 lines**, rev 15:47 CT)
**Diffed against:**
- `.bak-20261015-1546-pre-community` (371 lines)
- `.bak-20261015-1526-pre-reaudit` (828 lines)

**Research:** `/workspace/research/community-replacements-2026-10-15.md`; `/workspace/research/storyboard-nodes-2026-10-15.md`
**Skills read:** `/home/box/agent-data/workflows/{alienpc-hardcore-i2v-director, alienpc-max-movie-director, ref2va-prompt, alienpc-ltx-i2v-prompting}`
**AlienPc:** read-only (`Get-ChildItem`/`Get-Content`) on `C:\AI\llama-swap-trial\`. Nothing touched. The trial is **live** (the `timeline.csv` last row is 15:49:24, llama resident at 8989 MiB).
**Derrick confirmations accepted as given:**
- 3:33 PM: "yes i confirm both" (D1–D6 + the Switchyard-only model-load rule).
- 3:40 PM: community-first standing rule.

The plan's own quotes for D7/D8/D9 (3:26/3:28/3:46) are now cited, so the attribution gap from audit #2 is closed.

## Verdict: **NOT READY** (as written)

Phases 0–2 for Antigravity at ~6:35 PM CT are logically intact, but three blockers make the canonical file unsafe to hand over:
- (B1) the file no longer *contains* most of the unit text;
- (B2) the llama-swap adopt path kills ComfyUI mid-render and loads models outside Switchyard;
- (B3) nothing in the plan targets MiniMax H3.

All three are text fixes, roughly 45–60 minutes. Once they land, plus H1–H3, this becomes **READY-WITH-FIXES**.

## Counts
| Severity | Count |
|---|---|
| Blocker | 3 |
| High | 6 |
| Medium | 6 |
| Low | 3 |
| **Total** | **18** |

Prior gates (N1–N10, PB/PH) re-checked: **N1–N6, N8–N10 still present** (often only as one-liners). **N7 dropped.** All PB/PH test detail exists only in the backups (B1).

## Must-fix
1. **B1:** Restore the full unit text and test scenarios into the canonical file.
2. **B2:** Keep ComfyUI out of llama-swap. Route every model load through Switchyard. Add a "no kill mid-render" pass criterion.
3. **B3:** Add the H3 production binding to U19–U21, U44 and the evals.
4. **H1:** Fix the U43 pass criteria. The measured swaps fail.
5. **H2:** Reconcile the trial already running with the plan's sequencing (step 7, after Phase 0).
6. **H3:** Forbid comfy-mcp/comfyui-mcp as agent tools pointed at :8189. Read-only or Switchyard-proxied only.

## Blockers

**B1: The canonical plan was gutted.** It shrank from 828 to 283 lines, and "Test scenarios" blocks fell from 41 to 6. Units U7, U9, U25, U26, U27, U22–U24, U11, U34, U35, U37, U42, U31 and U32 now read "Prior Full text", but that text lives only in `.bak-20261015-1526-pre-reaudit` and `.bak-…1546-pre-community`. Other gaps:
- Appendix A says "Keep prior … body" and doesn't include it.
- **N7** (service account can still read `upstream.key` and :8080 health after the ACL change) is missing from the canonical file entirely.
- KTD1–13 are compressed into one line.

An executor reading only the canonical file loses the tests that closed PB/PH/N items. Fix: merge the 1526 unit bodies back in, then add the community deltas.

**B2: The llama-swap adopt path conflicts with the render-safety rule and the Switchyard-only model-load rule (D7).** Evidence from the trial `config.yaml`:
- `comfyui_auto` is a llama-swap *model*.
- Its `cmd` launches ComfyUI `main.py`.
- `cmdStop: taskkill /T /F /PID ${PID}`.
- `compat.ignoreWebsockets: true`.

In `r3.csv`, "darkroast while comfyui_auto ws open" loaded in **5.5 s**, so ComfyUI was force-killed even with an open websocket. With ws-watching on (`comfyui_wsoff`), it took 46.7 s.

After adopt, any LLM request (Forge, Dark Roast judge, promptfoo, lm-eval) that arrives during an H3 render will **taskkill ComfyUI mid-render**. llama-swap also starts llama-server and ComfyUI itself, so it is a second model loader outside Switchyard. That violates D7 unless Switchyard is its only client and the claim lives in Switchyard.

The plan's supersede table moves the "U5 idle-reload/owner adopt" path to llama-swap, but llama-swap has no ComfyUI-busy/VRAM guard. That reopens **PB3/N1**.

Fix:
- (a) ComfyUI stays under Switchyard and is never a llama-swap model.
- (b) llama-swap listens on loopback, and only Switchyard calls it, after its claim and its ComfyUI-idle check.
- (c) Add U43 pass criteria: "LLM request during an executing ComfyUI prompt → refused or queued, ComfyUI PID unchanged" and "nothing loads a model except via Switchyard".
- (d) Restate D7 as "llama-swap is Switchyard's executor only".

**B3: No H3 targeting anywhere in the plan.** `rg` for H3/beta6/Euler/shift/RIFE/Extender/Rewriter/Ref2VA in the canonical plan finds **zero** production-stack references. "H3" appears only in "in-graph Strata during H3". The gaps:
- U19–U21 (storyboard/U7c) say "Prior gates" and nothing about H3.
- U44 stitch is generic.
- The promptfoo eval is refusal-only.
- The ADOPT row for H3 Extender/Rewriter in research §3 was **not carried into the plan's community map**.

The full required binding is in the H3 fit section below.

## High

**H1: llama-swap timings verified from the CSVs, and they fail the plan's own criterion.**
| Swap | llama-swap (CSV) | Switchyard reference (P1 audit U5/U6) |
|---|---|---|
| Strata→ComfyUI | cold **50.2 s**; warm **20.4 / 20.4 s** (r1 #2, #3) | U5-T1 run 2: strata_gone 0.45 s + comfy 10.8 s ≈ **11.3 s** |
| ComfyUI→Strata | **39.9 / 41.0 / 40.0 s** (median 40.0) | U5-T2: 42.1 s first, then **3.4 / 3.4 s** warm |
| Strata→Dark Roast | 14.4 / 13.7 s | U6: 28.5 → 10.5 / 12.5 s |
| ComfyUI→Dark Roast | 5.5 s | n/a |
| Dark Roast→ComfyUI | 20.1 s | n/a |
| Unload-all | 0.8 s (10361→419 MiB) | n/a |

What this shows:
- **Claim confirmed:** ~20 s warm and ~40 s back, against 3.4 s. ComfyUI→Strata is about **12×** slower, and Strata→ComfyUI is ~1.8× slower than ~11 s.
- **It's not apples to apples, and it's worse than it looks.** llama-swap *restarts the ComfyUI process* (`mib_after` ≈ 700–900 MiB, an empty ComfyUI). The 20 s doesn't include reloading the H3 beta6 int8 weights on the first render. Switchyard's `to_comfy` keeps ComfyUI alive.
- `swap.log` has `[WARN] <darkroast> upstream process exited unexpectedly`.

The plan's pass rule, "median swaps ≤ ref×1.25 **or documented**", lets an outright failure through. Remove "or documented". Require timing measured to the first H3 render actually starting.

**H2: The trial is running out of sequence.** The plan puts U43 at **step 7**, after Phase 0, with Switchyard stopped. On disk:
- The trial started 15:33 (`inventory-before.txt`).
- `r1`–`r3` ran 15:35–15:44.
- `config.yaml` was re-edited at 15:46, and `swap.pid` was rewritten at 15:46.
- At 15:49 it is still sampling, with llama resident.

That's before orphan release, U39 or U40. The trial also uses a separate ComfyUI install (`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI`, ports 10001+, llama-swap on :9292). Whether that is the production :8189 install is UNVERIFIED.

Fix: move U43 into the plan's present tense. Record that the Switchyard runner and :8189 were idle or stopped during r1–r3, or mark the timings as non-production. Require the trial to stop, and VRAM to be under 1 GB, before U0.

**H3: comfy-mcp and comfyui-mcp as agent tools would allow ComfyUI POSTs while busy.** Research §1 recommends trialling Comfy-Org comfy-mcp "for Forge/Antigravity tools with `COMFY_LOCAL_URL=http://127.0.0.1:8189`". Its run/queue/`free_memory` tools POST straight to :8189:
- That bypasses Switchyard (D7 and the live "Nothing outside Switchyard may POST to :8189").
- `free_memory` while a prompt is executing is exactly the busy POST that PH3 forbids.

artokun comfyui-mcp's interrupt→`/free` ladder is the same risk if installed as a tool. The plan only says U8 "borrows recipes", which is fine, but it doesn't forbid installing either MCP as a live tool. Fix: "No ComfyUI MCP (either) wired to :8189 for agents. Patterns only, or read-only `system_stats`/queue GET, or via a Switchyard proxy."

**H4: Evals don't check H3 prompt-format compliance.** promptfoo (U15/U18) measures refusal honesty for Dark Roast, which is good, but nothing checks that director output is valid **six-section Ref2VA**. The checks should cover:
- `subject_definitions`/summary/retention_analysis/detailed_description/soundscape/music
- the official `Static Shot` wording
- no NEG ban laundry
- no LTX/flat POS
- the get-into-position beats when Cond ≠ act

These all come from the `ref2va-prompt` and `alienpc-hardcore-i2v-director` skills. Fix: add promptfoo assertions built from those rules, plus the Rewriter's **Prompt Check** node (storyboard research T4) as a second check.

**H5: Promptor and the in-graph LLM risk.** 1038lab ComfyUI-MiniMax-H3-Promptor **exists** (GitHub page fetched; H3-specific "cinema-production-grade prompts"). It is **not installed**, and research lists it as "local unload before video", meaning it runs its own LLM *inside* ComfyUI. That is a second model loader (D7) and a co-residence risk on 16 GB. Prefer the already-installed **pytraveler Rewriter "Guide Prompt (any LLM)"** (zero weights), feeding Dark Roast through Switchyard with thinking off and ~2048 output. If Promptor is trialled, use its prompt templates only, not its loader. The plan names neither, so it must state this choice.

**H6: The community "director" defaults are non-H3.** artokun comfyui-mcp's director skill is **WAN FLF / Z-Image / Qwen Edit** (research §3). seesee75 **MiniMaxH3-Director** is an "**LTX Director port**" (storyboard research row 19), and LTX Director itself is not installed: ComfyUI-LTXVideo fails to import on 0.38. The plan should explicitly reject both as U7c directors, and keep Dark Roast plus the H3 Extender (Motion Context OFF).

## Medium
- **M1: U44 stitch has no H3 parameters.** VHS Video Combine / ffmpeg concat must match H3 output:
  - fps after **RIFE 20** on test cells, and native fps on production 8-step cells;
  - never mix the two in one stitch;
  - carry the H3 **audio** track (H3 audio VAE) through the VHS audio input or ffmpeg `-c copy`;
  - use the Extender's "Save Individual Clips" with hard cuts as input.

  Add a test: 2 H3 clips → stitched duration = sum, audio present, fps unchanged.
- **M2: lm-eval-harness doesn't measure U28's criteria.** U28 measures task pass, tool-use success and no unauthorized llama spawn. lm-eval measures few-shot LM tasks. Use lm-eval for perplexity/MMLU-style comparison, but keep the fixed coding/tool tasks (or inspect_ai, already TRIAL in research) for the decision data. Model loads for lm-eval must go through Switchyard (D7), with Strata unloaded first.
- **M3: promptfoo telemetry and data.** NSFW fiction prompts must not leave the box or AlienPc. Require `PROMPTFOO_DISABLE_TELEMETRY=1`, a local provider only, and no cloud sharing/`share` (research notes the OpenAI-org ownership).
- **M4: Velorn trial.** It has 100+ MCP tools that can drive ComfyUI. "Document wiring or skip POSTs" is too soft. Require Velorn to point at a non-production ComfyUI or run open-only, never :8189.
- **M5: The community-first rule is applied unevenly.** It's applied well for the load/unload, eval, stitch, monitor and Forge harness rows, and keep-custom is justified for the leases (U0/U2/U4/U39). But the research's **ADOPT** verdict for H3 Extender + Rewriter Guide Prompt (the most relevant community nodes for U19–U21) is missing from the plan's community map. U19 still implies a custom vision planner with no community-first line.
- **M6: The U45 nvitop install** is a pip install on AlienPc with no target interpreter named and no idle gate beyond "when idle". Name the venv. It must not install into the ComfyUI venv.

## Low
- **L1:** The H3 Extender README calls itself the "final feature release" (storyboard research). Treat it as a maintenance risk: pin the commit (5183ad4).
- **L2:** The WebFetch star counts read 0 for both Promptor and Extender, which conflicts with research (246/334). Existence is confirmed; the star counts are unverified by this tool.
- **L3:** `config.yaml` includes a `badcheck`/`darkroast_ttl30` test profile at `-c 4096`. Make sure no adopt config carries those over. The Dark Roast default is 32K (KTD4).

## H3 fit: required binding (to add to U19, U20, U21, U44, U15/U18)
Production stack (from the `alienpc-hardcore-i2v-director` KEEP block):
- `10Eros_Max_h3_8stepTURBO_beta6_int8`, Euler simple, **8 steps**, **shift 10** (audio 3)
- ck-attention, no fp8, ComfyUI 0.38.x pinned, :8189
- default length 124f
- tests and local loop: **6 steps + RIFE 20**
- preview 864×480, quality ~768 short edge

| Plan piece | Current | H3-native target | Mismatch |
|---|---|---|---|
| Director prompt template (U19) | "vision storyboard", generic | Dark Roast + **Rewriter Guide Prompt (any LLM)** Ref2VA guide (~10k ctx, thinking off, ~2048 out) → six-section Ref2VA per `ref2va-prompt` skill | **Generic** |
| Prompt node / rewriter | none named | pytraveler Rewriter (installed; zero-weight nodes only); Promptor templates optional, no in-graph LLM | **Missing** |
| Extender | none named | tritant **H3 Extender**, Motion Context OFF, Prompt/Reference Pack Bridge, Save Individual Clips | **Missing** |
| Storyboard step (U20 tests) | L2a–e only | add asserts: six sections present, `Static Shot` wording, no NEG laundry, get-into-position beats, single subject_definitions block | **Generic** |
| U7c render cells (U21) | "Prior gates" | stock **H3 I2V (`MiniMaxH3ImageToVideo`) / REF2VA (`MiniMaxH3ReferenceToVideo`)** workflows, KEEP sampler settings; T6–T8 at 6 steps + RIFE 20 per test rule | **Unbound** |
| Stitch (U44) | VHS/ffmpeg generic | VHS/ffmpeg with H3 fps/RIFE and audio rules (M1) | **Generic** |
| Eval (promptfoo) | refusal only | + Ref2VA format assertions + Rewriter Prompt Check (H4) | **Missing H3** |
| Community director | comfyui-mcp skills (WAN/Z-Image) | patterns only | **WAN-specific** if used |
| Timeline director | MiniMaxH3-Director suggested in research | LTX Director port; not for U7c | **LTX-derived** |
| LTX Director | not in plan (good) | — | OK. Keep excluded (not installed; LTXVideo import fails) |
| `alienpc-ltx-i2v-prompting` | not cited (good) | LTX :8188 baseline only | OK. Must not be used for Max |
| Flux | Flux/Klein stills remain the upstream step (skill) | — | OK (stills only) |

Web check (light): `github.com/1038lab/ComfyUI-MiniMax-H3-Promptor` and `github.com/tritant/ComfyUI_MiniMax_H3_Extender` both resolve and describe H3-specific nodes. pytraveler Rewriter and LTX Director facts come from the storyboard research (READMEs read 2026-10-15).

## Prior-gate regression check
| Gate | Status in canonical plan |
|---|---|
| N1 idle_profile null until U5 | Kept (U0 step 5, U5) |
| N2 reusable U39 per deploy | Kept |
| N3 U39 before T6 / after T8 | Kept |
| N4 U0 named `session end` + ComfyUI GET | Kept, with forbidden list |
| N5 heal idle and session-free | One-liner only |
| N6 Antigravity owns U0/U4 | Kept (Phase 0 now waits for ~6:35) |
| N7 ACL readability test | **Dropped** (B1) |
| N8 U37 VRAM + unload | One-liner only |
| N9 Hermes injected hash | Kept (U13) |
| N10 U40 ComfyUI-idle | Kept |
| One GPU job / co-residence | Stated. **Undermined by the llama-swap adopt path (B2)** |
| No kill or POST during render | **Violated by the llama-swap `taskkill` of ComfyUI (B2) and the comfy-mcp tool path (H3)** |
| Switchyard-only model load (D7) | **Conflicts with llama-swap and Promptor loaders unless subordinated (B2, H5)** |

## Paths
- Report: `/workspace/audits/forge-bugfix-plan-audit3-h3-2026-10-15.md`
- Staging copy: `/workspace/cos/brain-staging/60_reviews/forge-bugfix-plan-audit3-h3-2026-10-15.md` (local commit only)
- Trial evidence (AlienPc, read-only): `C:\AI\llama-swap-trial\{r1,r2,r3}.csv`, `config.yaml`, `swap.log`, `timeline.csv`

*Report only. No plan, AlienPc, ComfyUI or llama-swap changes. No pushes.*
