# Audit: /workspace/llm-brainstorm/local-setup-research.md (2026-10-15) — report-only
Audited 2026-10-15 ~9:00 AM CT, box copy only. AlienPc was not touched.

**URL tally:** 35 distinct http(s) URLs (excluding localhost). **35/35 load (HTTP 200), 0 dead, 0 403.**
- Support for the claims was checked on the priority items below. The other links (ComfyUI MCPs, LTX, Hermes docs, gbrain) load and match their one-line descriptions at a skim, but I did not check them line by line.
- Local `[L]` claims (`server.py:1022`, local hashes, the EF0724C5… built-in hash) **cannot be verified from the box**.

**Verdict:** mostly accurate. It isn't "fully verified" yet: one P1 and several P2 caveats remain.
**Counts:** P0 0 · P1 2 · P2 5 · P3 2

## Priority checks
| Claim | Result |
|---|---|
| Strata per-request vector-off switch | **Exists in the docs (VERIFIED).** Upstream DETAILS.md (fetched 10-12): "A loaded vector is on for every request unless it says otherwise… the API takes `"experimental_speed_projection": false` in the request body… Switching drops the conversation cache once… Switched off, the output is token-for-token the stock model's." It applies to *whatever vector is loaded*, including alesha's. alesha's card quote also checks out. The code line `server.py:1022` is [L], unverifiable here. **Untested through the Switchyard gateway on :8765** (the doc says so). |
| alesha vector hash | **VERIFIED.** HF API LFS oid for `Huihui-Qwen3.8-Flash-Next-refusal-direction-r.gguf` = `59f9ae8b4372107ae79044278a4406bdfe8f8861fe599aa5848515f0d072be38`, size 483,520. It matches the doc. Its evidence (0/10 refusals, KL 0.005-0.023, 5/5 OMP) is **maintainer-only** and comes from 10 prompts on IQ3_S/IQ2_XS; IQ3_XXS was not tested. The doc says this. |
| SC117 IQ3_XXS abliterated repo | **VERIFIED.** `IQ3_XXS/…abliterated-IQ3_XXS-00001-of-00002.gguf` 47,342,144,896 + `-00002` 28,800,138,432 = **76.14 GB** ✓. Also present: IQ3_S (55.06 + 28.80 = 83.86 ✓), IQ2_XS (39.67 + 28.80), Q2_0, mmproj, MTP, `strata/rt`. The "byte-level transplant from orcarouter" description is the maintainer's own. **New:** IQ2_XS shard 1 (39.67 GB) is on HF, so AlienPc's missing shard can be re-downloaded rather than counted as "unusable". |
| LCB v6 91.9 / SWE-bench Pro 62.5 | **Vendor-only.** The Qwen/Qwen3.8-Flash-Next card table reads "LiveCodeBench v6 91.9 90.3 …", "SWE-bench Pro 62.5 61.7 …", full precision, 256K context, best of two harnesses (card footnote). The doc cites the **trohrbaugh mirror**, not the Qwen card. I found no independent reproduction, and nothing at IQ3_XXS with the vector. |
| ik_llama "4.4× slower" | **VERIFIED but narrow.** It's a single-user issue (#1765): one 5070 Ti, **Gemma4 26B-A4B UD-Q4_K_XL, MoE experts on CPU, -c 95232, q8 KV**. The issue says "token generation is about 4.4x slower on the same machine", with ik tg128 5.25-7.10 t/s. ik's prefill was *faster* ("much faster prompt processing"). The doc generalizes this to "avoid for hybrid MoE on this card", which is broader than the evidence. |
| Gemma-4 Heretic 11/100 | **VERIFIED as a maintainer claim.** llmfan46 card: "11/100 Uncensored vs 100/100 Original". It's the Heretic tool's own refusal count, not independent. |
| pi-hermes-memory | **VERIFIED.** pi.dev package and GitHub chandra447 exist. v0.9.10, MIT, with `session_search`, `memory_search` and `skill_manage` on the page. The secret-scanning claim was not checked. |

## Findings
- **P1 / 75 — The coding recommendation leans on vendor and maintainer scores alone.** The table's "best vendor scores" (LCB 91.9, SWE-Pro 62.5…) are full-precision Qwen numbers at 256K context. Nothing independent exists, and nothing at IQ3_XXS with route-tail skip and the vector. The doc labels them "Vendor", but it cites a mirror (trohrbaugh) instead of the Qwen card.
  **Fix:** cite `huggingface.co/Qwen/Qwen3.8-Flash-Next`. Mark the scores "vendor, full precision, not reproduced". Let the local bake-off (16/21, 20/20 [P]) be the deciding evidence.
- **P1 / 50 — "127–145 tok/s warm" vs the 105.7 median is still mixed.** Both are [P] (prior box docs). The context, KV-resident setting and prompt-length conditions aren't stated in this doc, and the 96K configs were possibly unapproved (see the grounding-report audit, 9e11c91).
  **Fix:** quote the conditions for each number, and use 64K / 32K resident (which the doc recommends) as the measured baseline.
- **P2 / 75 — The orcarouter RAM headroom is overstated.** "57.6 − 49.8 ≈ 8 GiB" ignores the engine and host buffers (~3-5 GiB, from earlier Strata math), so the real figure is **≈ 3-5 GiB**. That's the same tight class as NVFP4. SC117 IQ3_XXS shard 1 is 44.09 GiB vs base 43.81, which is about the same RAM as today (~14 GiB free); the doc doesn't say so.
- **P2 / 75 — The commit headroom figures disagree.** This doc says "8.6 GiB with Strata loaded [P]"; the grounding report says "13.2 GiB left of an 83.7 GiB limit". State which config and time each was measured at.
- **P2 / 50 — The ik_llama verdict is over-generalized** (see the table above). **Fix:** "slower TG for Gemma4 CPU-expert offload in one report; prefill faster".
- **P2 / 50 — The RAM/VRAM budgets are right, but some VRAM figures are estimates.** I checked them:
  - **Strata phase:** about 40 GiB arena + about 3 GiB engine leaves 57.6 − 43 ≈ **14-15 GiB** ✓.
  - **H3 render:** about 35 GiB RAM ✓.
  - **Strata + H3 together:** about 75 GiB > 57.6 ✓, so they can't co-reside.
  - **27B Heretic:** about 14.4-14.9 GiB VRAM ✓; it can't sit beside H3 on 16.3 GB.
  - **9B Q8 VL:** 8.87 + 0.86 + about 0.53 KV + about 1 compute ≈ **11.3 GiB** ✓.
  - **Gemma-4 "15.9 GiB at Q4":** doesn't fit 16.3 − 0.85 GB with any KV, so it needs CPU offload (the doc implies this).
  - Mark H3 VRAM "10-12 GB" and the swap times as [UNVERIFIED] (the doc already does).
- **P2 / 50 — The per-request toggle is untested through the gateway.** The doc lists this as a risk. Make it a gate: send one `experimental_speed_projection:false` request via :8765, and check that the Strata Monitor/log marks it "stock" before any Forge use.
- **P3 / 50 — The license note** ("Qwen Community License 1.0 / Apache 2.0, cards disagree") is unresolved. Check the Qwen card's license field.
- **P3 / 25 — gbrain and the ComfyUI MCPs are unverified on Windows/Pi** (the doc flags this). Fine as written.

## Maintainer-only or unverifiable claims (keep flagged)
- **Maintainer-only:**
  - alesha's KL, refusal and OMP numbers
  - SC117's transplant method and Swift "52-63% less thinking"
  - orcarouter's "±2 points" and 77.7 tok/s on a 5090
  - Gemma 11/100
  - Qwen vendor scores
  - ISTA "matches base on AIME25"
- **Unverifiable from the box ([L]/[P]):** `server.py:1022`, the built-in vector hash EF0724C5…, the 127-145 tok/s, 16/21 and 20/20 results, and the commit headroom.
