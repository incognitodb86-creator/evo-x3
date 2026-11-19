Goal: After `UNI-APPLY-X3-D` has a `RESULT.md`, run the writer benchmark W1 on the EVO-X3 with models already on disk (no downloads), so Derrick can pick the writer model and sampler from results.

# BENCH-X3-W1 (Hydrogen runs it, Max verifies): writer benchmark, Nov 19 2026

Authority: Derrick 2026-11-19 13:46 CT ("we should run benchmarks first, to determine our settings for everything") and `records/uplan/PLAN.md` item `W1` / "Order of work" step X5. Arms and test set: `records/source-plans/2026-11-18-x3-alienpc-followup-plan.md` W1 row and line 43. Max verifies your RESULT; Derrick ranks blind in chat.

## Changes from Max, 2026-11-19 14:20 CT (Derrick t2753u, t2754u, t2759u)
- **Benchmark first:** Derrick moved W1 ahead of `UNI-APPLY-X3-D`, so the X3-D RESULT is no longer needed. W1 tests the writer prompt that is live now; record its `writer_prompt.md` sha256 in RESULT so the SK1 change can be compared later.
- **Doer is Hydrogen** (agy, `gemini-4-hydrogen-medium`, user derekboone, using `sudo -n -u evo` for evo files), not X3 Forge, because Forge shares the model being swapped.
- **Arm 4 added (Derrick t2751u/t2752u):** Swift 1.5 Qwen3.8 Flash-Next IQ4_XS at `/srv/models/swift15-iq4xs/` (3 shards, still downloading). Run it only if `download.done` exists and every shard's sha256 matches `files.json`; otherwise mark it `SKIPPED (download not finished)` and finish the other arms.
- **Quiet window:** Derrick is told in chat that it starts as soon as arms 1a/1b finish. AlienPc lane has no test running.

## Needs before launch (ALL required)
- X3 lease free (`/home/derekboone/AI/locks/x3-lease.txt` empty); no active render (`/home/evo/AI/community/runs` has no running job and AlienPc ComfyUI queue is empty).

## Access & Lease
- Doer: Hydrogen (agy) as derekboone; evo-owned files through `sudo -n -u evo` with `cd /tmp`. Lease line `hydrogen | BENCH-X3-W1 | <start time>` in `/home/derekboone/AI/locks/x3-lease.txt` while you load/unload models or touch llama-swap; clear it (empty the file) when done or blocked. No commits, no messages.
- Work dir (outside git, prompts never go into records): `/home/evo/AI/_runs/W1/`.

## Work (stop on first failure)
1. **Arms available?** For each arm, check the weights exist (`ls -la`, sizes only) under `/srv/models` and whether llama-swap has the entry: Arm 1a/1b `flash-next-uncensored-v2` (live), Arm 2 `gemma4-heretic` Q8_0 + mmproj, Arm 3 `ref2va-27b` Q4_K_M + mmproj (commented out of llama-swap since 2026-11-17, t2263u), Arm 4 Swift IQ4_XS (see Changes; no llama-swap entry yet: add a window-only entry using llama.cpp model-card settings, ESP off, largest context that fits with Gufo unloaded). Missing weights -> that arm is `SKIPPED` (no downloads; W2 is a separate Derrick yes).
2. **Test set (16 asks, F4 line 43):** `writer_pipeline/acceptance/wp_accept.py` suite `ten` (10 asks on 3 stills) + the 2 named-parody asks from `community/scripts/parody/test_u54_named_e2e.py` (12 H3 asks) + the 4 creative-writing asks from F4. Dry runs only: never queue a render.
3. **Arm 1a / 1b first (no quiet window):** live Gufo with sampler A, then Qwen's native non-thinking sampler (temp 0.7-1.0, top_p 0.95, top_k 20, min_p 0). Use a copy of `writer_pipeline/config.yaml` per arm; never edit the live one. Check the pipeline does not send conflicting `enable_thinking` + `reasoning_effort`.
4. **Quiet window (arms 2, 3 and 4):** at the time Derrick was told, back up `/etc/evo-x3/llama-swap.yaml`, load each arm (Arm 3 entry uncommented for the window only), run the 16 asks, then restore the backup with `scripts/apply-llama-swap.sh` (it health-checks and rolls back on failure) and confirm Gufo is resident again. Arm 3 also does 2-stage rewriting of Arm 1b's draft through `beta7_convert.py`. Record Arm 3's refusal rate first (stock, not abliterated).
5. **Score per arm:** first-try READY count (/12), refusals (/16), still/ask drift (invented `<Picture 2>`, wrong pose or clothes), seconds per prompt, `lint.py` header violations. You score; use judgment only where a count needs it.
6. **Blind pack for Derrick:** 4 H3 asks + 4 creative asks, arms relabelled A-E, in `/home/evo/AI/_runs/W1/blind/` (outside git). Max shows it to Derrick; Derrick ranks there.

## Rollback
- `llama-swap.yaml` restored from the step-4 backup (`apply-llama-swap.sh`); per-arm config copies deleted. Nothing downloaded, nothing to delete.

## Rules
- Never touch the gemma4-heretic slot's permanent entry (load it for the window only, then restore the backup). Never kill llama-swap; use `scripts/apply-llama-swap.sh`. Never read Sydney's chats, persona or memory. Never open PixlStash library contents.
- No downloads, no renders, no live `config.yaml` edit. No adult prompt text in records or RESULT (counts and timings only). Never read or print keys.

STOP CONDITION: write `/home/derekboone/evo-x3/records/BENCH-X3-W1/RESULT.md` (per-arm table: READY /12, refusals /16, drift, s/prompt, skipped arms and why; blind pack path), clear the lease, then stop. The winner is Derrick's pick; `W4` is briefed after.
