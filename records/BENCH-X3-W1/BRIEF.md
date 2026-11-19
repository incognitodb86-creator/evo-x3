Goal: After `UNI-APPLY-X3-D` has a `RESULT.md`, run the writer benchmark W1 on the EVO-X3 with models already on disk (no downloads), so Derrick can pick the writer model and sampler from results.

# BENCH-X3-W1 (X3 Forge, Hydrogen scores if needed): writer benchmark, Nov 19 2026

Authority: Derrick 2026-11-19 13:46 CT ("we should run benchmarks first, to determine our settings for everything") and `records/uplan/PLAN.md` item `W1` / "Order of work" step X5. Arms and test set: `records/source-plans/2026-11-18-x3-alienpc-followup-plan.md` W1 row and line 43. Max verifies your RESULT; Derrick ranks blind in chat.

## Needs before launch (ALL required)
- `/home/derekboone/evo-x3/records/UNI-APPLY-X3-D/RESULT.md` exists (W1 must test the SK1 writer prompt we keep).
- X3 lease free; no active render; Derrick told the quiet-window time in chat (arms 2/3 unload Gufo, so Hermes chat, Render and X3 coding pause) and the AlienPc lane is not running a test in that window.

## Access & Lease
- Doer: X3 Forge as `evo`; lease line `forge-x3 | BENCH-X3-W1 | <start time>` in `/home/derekboone/AI/locks/x3-lease.txt`, cleared when done or blocked.
- Work dir (outside git, prompts never go into records): `/home/evo/AI/_runs/W1/`.

## Work (stop on first failure)
1. **Arms available?** For each arm, check the weights exist (`ls -la`, sizes only) under `/srv/models` and whether llama-swap has the entry: Arm 1a/1b `flash-next-uncensored-v2` (live), Arm 2 `gemma4-heretic` Q8_0 + mmproj, Arm 3 `ref2va-27b` Q4_K_M + mmproj (commented out of llama-swap since 2026-11-17, t2263u). Missing weights -> that arm is `SKIPPED` (no downloads; W2 is a separate Derrick yes).
2. **Test set (16 asks, F4 line 43):** `writer_pipeline/acceptance/wp_accept.py` suite `ten` (10 asks on 3 stills) + the 2 named-parody asks from `community/scripts/parody/test_u54_named_e2e.py` (12 H3 asks) + the 4 creative-writing asks from F4. Dry runs only: never queue a render.
3. **Arm 1a / 1b first (no quiet window):** live Gufo with sampler A, then Qwen's native non-thinking sampler (temp 0.7-1.0, top_p 0.95, top_k 20, min_p 0). Use a copy of `writer_pipeline/config.yaml` per arm; never edit the live one. Check the pipeline does not send conflicting `enable_thinking` + `reasoning_effort`.
4. **Quiet window (arms 2 and 3):** at the time Derrick was told, back up `/etc/evo-x3/llama-swap.yaml`, load each arm (Arm 3 entry uncommented for the window only), run the 16 asks, then restore the backup with `scripts/apply-llama-swap.sh` (it health-checks and rolls back on failure) and confirm Gufo is resident again. Arm 3 also does 2-stage rewriting of Arm 1b's draft through `beta7_convert.py`. Record Arm 3's refusal rate first (stock, not abliterated).
5. **Score per arm:** first-try READY count (/12), refusals (/16), still/ask drift (invented `<Picture 2>`, wrong pose or clothes), seconds per prompt, `lint.py` header violations. Hydrogen scores only if a count needs judgment.
6. **Blind pack for Derrick:** 4 H3 asks + 4 creative asks, arms relabelled A-D, in `/home/evo/AI/_runs/W1/blind/` (outside git). Max shows it to Derrick in Hermes chat; Derrick ranks there.

## Rollback
- `llama-swap.yaml` restored from the step-4 backup (`apply-llama-swap.sh`); per-arm config copies deleted. Nothing downloaded, nothing to delete.

## Rules
- No downloads, no renders, no live `config.yaml` edit. No adult prompt text in records or RESULT (counts and timings only). Never read or print keys.

STOP CONDITION: write `/home/derekboone/evo-x3/records/BENCH-X3-W1/RESULT.md` (per-arm table: READY /12, refusals /16, drift, s/prompt, skipped arms and why; blind pack path), clear the lease, then stop. The winner is Derrick's pick; `W4` is briefed after.
