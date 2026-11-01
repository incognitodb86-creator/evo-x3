# strata tuning - 2026-10-31

Bench harness: `C:\AI\community\notes\strata-bench.ps1` (via llama-swap :8080, model `coding_swift15_iq3s_esp`, one ~1.9K-token prompt, `max_tokens=256`, `temperature=0`, thinking off). Raw rows: `C:\AI\community\notes\strata-bench-results.jsonl`. Engine: 0.1.54 (engine-028), config `C:\AI\strata-0.2.7\strata-swift15-iq3s-esp.json`. GPU lock `C:\AI\locks\gpu-render.lock` held for every measurement below that this file reports from Forge.

Status: OPT5 done (below). OPT4 (pool workers / affinity) not run in this pass - it is its own item. No DONE line yet.

## OPT5 - arena (no `--resident-budget-gib`) vs the kept resident-32 numbers

Derrick 13:28 CT: stay on 0.1.54, remove the RAM budget setting, benchmark it. Max Architect 2 removed `--resident-budget-gib 32` from the config (backup `.bak-1328`) and reloaded at 13:46:38. Item: fix_plan OPT5.

### State proved before measuring
- Live engine line `2026-10-31 13:50:43 engine started:` has **no** `--resident-budget-gib`; every earlier line today has `--resident-budget-gib 32`. strata.exe PID 33748 (started 13:50:43), strata-vision PID 25684. Engine 0.1.54, `--max-context 131072 --kv int8 --kv-resident 32768 --pool-workers 13`, unchanged otherwise.
- Arena load in the log: `expert arena read unbuffered`, `loaded 46.84 GiB at 5.52 GiB/s`, `session is up (engine 0.1.54)`. No `resident RAM mode:` line (that line only appears in the resident-budget builds, e.g. `32.00 GiB of experts in RAM (page-locked)`).
- GPU lock was free, acquired by this pass (`ACQUIRED pid 25832`), released after (`RELEASED pid 25832`). No other GPU job. VRAM 14238/16303 MiB used by the model server.

### Numbers (median of 3, same script, same prompt)

| set | time | config live in the process | pp tok/s | tg tok/s | wall s |
|---|---|---|---|---|---|
| baseline `budget32_1/2/3` | 12:52-12:53 | resident budget 32 GiB | 606.6 / 622.0 / 617.5 | 82.6 / 84.7 / 79.5 | 7.2 / 7.1 / 7.3 |
| baseline `max2-arena-before` (runs 2-3) | 13:45 | resident budget 32 GiB (engine line 13:44:18) | 597.6 / 629.5 | 77.6 / 85.7 | 7.50 / 7.03 |
| **OPT5 `opt5-arena`** | 13:59:20-28 | arena, no resident budget (engine line 13:50:43) | **1640.5 / 1720.5 / 1733.0** | **110.3 / 130.5 / 125.0** | **4.57 / 4.08 / 4.16** |

OPT5 medians: pp 1720.5, tg 125.0, wall 4.16 s. Kept baseline medians (the item's numbers): pp ~617, tg ~80-85, wall 7.0-8.0.

### Bars from the item, applied
- decode: 125.0 vs 79.5-85.7 -> +46% to +57%. **PASS** (must improve)
- wall: 4.16 s vs 7.0-8.0 s -> -41%. **PASS** (must improve)
- prefill: 1720.5 vs ~617 -> +179%, far above the >= 586 floor. **PASS** (must be no more than 5% worse)

**Result: KEEP. No revert, no reload, no unload.** The live config and the live process are already the arena config, which is the kept state; nothing was written to the config in this pass. `strata-swift15-iq3s-esp.json.bak-1328` (with `--resident-budget-gib 32`) stays as the revert path if Max ever wants it back.

### Why these pp/tg are not cache-inflated
The strata log shows exactly three requests in that window, my three, contiguous, no interleaved traffic:
`prompt 1902 tokens = 0 reused + 1902 read in 1159 ms (1640.5 tok/s), 256 generated in 2322 ms (110.3 tok/s)` and the same shape for 1906 (1720.5 / 130.5) and 1904 (1732.9 / 125.0). `0 reused` = no prefix-cache credit; the reported pp/tg match the wall time. (Long prompts by other clients do get prefix reuse, e.g. `prompt 46149 tokens = 0 reused + 46149 read in 14135 ms (3264.8 tok/s)`, `prompt 33654 = 33404 reused` -> its 358.9 tok/s is a reuse artifact, so never compare pp across prompt sizes.)

### Memory (the item asked to record any memory errors)
- RAM free 0.64 GB before the bench, 1.16 GB after. No memory error, no OOM, no refused request during the bench; log shows only `strata verify: captured the 5-token window (upload no error, sync no error)`.
- Startup notes of the arena path, worth knowing: `cudaHostRegister of the whole arena FAILED (out of memory)` -> it falls back to `45 slices pinned (43 GiB)`; `large pages refused for 50295996416 B (GetLargePageMinimum=2097152, VirtualAlloc error 1314); using 4 KB pages`; `pinned-memory headroom: holding 800 MiB ... 640 MiB handed back after the expert arena`. So the arena runs on 4 KB pages with slice pinning, and there is under 1 GiB of free RAM while it is loaded.

### Caveats (read before quoting these numbers)
1. **Warm state.** The arena process had ~9 minutes of heavy traffic (25K-46K-token requests, adaptive tier at 1060 rounds / 47K experts swapped) before my 3 runs. The baseline triples were measured right after their reloads. Part of the gap is plausibly warm expert cache / adaptive tier, not only the removed flag. The direction is still clear: run 1 after ~1 minute idle (1640.5 / 110.3 / 4.57 s) beats the warmed baseline triple.
2. This is not a clean one-variable A/B. To isolate the flag, Max would need one cold triple per config (unload/reload each through llama-swap, same warm-up protocol). Not done here: the item forbade extra sweeps, and OPT4 owns the pool/worker tests.
3. Quality was not tested; this is speed only.

## OPT4 - not run in this pass
Pool workers 13 vs 8, `--pool-affinity`, vision threads=6 check: untouched. The baseline rows `baseline / after1 / after2 / after3` in the jsonl (12:47-12:50) are Max's earlier sets: pp 654.6 -> 498.5, tg 59.7 -> 68-72, wall 8.2 -> 8.3-8.6 - his numbers, not re-verified by this pass.

## OPT4a - `--pool-workers` 13 vs 8 on coding_swift15_iq3s_esp (run 2026-10-31 20:22:45-20:33:14 CT)

Ralph pass `ralph-opt4`, one item, GPU lock held by the run for the whole item (`gpu_lock.ps1` ACQUIRED pid 12712
-> RELEASED, then the finish step ACQUIRED pid 17356 -> RELEASED, `NO LOCK` at the end). No render ran while the
lock was held.

Instruments: `notes\_opt4a\run_opt4a_v2.ps1` (arms, proof, timing, decision, restore, all in one item with a
`finally` release), `notes\_opt4a\cfg_edit_opt4a.py` (byte-precise cfg edit), `notes\_opt4a\bq_counts.py`
(answer-bar counts from the BQ jsonl), `notes\_opt4a\finish_restore13.py` (the live-args proof for the kept value).
Data: `C:\AI\community\notes\_opt4a\` = `bench.jsonl`, `arms.jsonl`, `arms.log`, `bq_w13.jsonl`, `bq_w8.jsonl`;
pass logs in `ralph-community\notes\_opt4a\` = `run-v2.log`, `result-2022.json`, `finish-13.log/json`, sampler CSVs.

| arm | flag (one variable) | live-args proof | n | pp med t/s (min/max) | tg med t/s (min/max) | wall med s (min/max) | BQ tools | BQ code | first-try | answer bar | RAM free min | VRAM peak | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W13 | `--pool-workers 13` (live value, re-measured as the only baseline) | new strata.exe pid 31216 @20:22:59, live `--pool-workers=13`, `--pool-affinity=ABSENT`, engine log start 20:22:57 pw=13 | 3 | 1708.1 (1261.6/1717.4) | 126.2 (115.7/132.9) | 3.15 (3.05/3.73) | 8/10 | 4/5 | 3/5 | fail (tools) | 1.51 GB | 14281 MiB | baseline |
| W8 | `--pool-workers 8` | new strata.exe pid 8952 @20:24:52, live `--pool-workers=8`, `--pool-affinity=ABSENT`, engine log start 20:24:50 pw=8 | 3 | 1703.5 (1244.5/1708.5) | 111.3 (98.5/117.0) | 3.43 (3.31/4.14) | 9/10 | 4/5 | 3/5 | pass | 1.76 GB | 14258 MiB | **REJECT** |

**Decision: keep 13.** W8's median decode is **-11.8%** vs W13 (111.3 vs 126.2 t/s), prefill -0.3%, wall +8.9%
(slower). The keep bar was >= +5% median `tg_tps`; it is not close, so 13 stays. `.bak-opt4a` (3202 B, pool-workers
13 in `args` + `args_written`) was restored and verified **byte-for-byte equal**, then the slot was reloaded and the
kept flags were proved live: new engine pid 7268 with `--pool-workers=13`, `--pool-affinity` absent, `/v1/models`
lists `coding_swift15_iq3s_esp`, `/running` ready, chat 200 in 267 ms (28.8 s cold load).

Read the speed numbers honestly:
- Each arm's first of the 3 runs is a warm-up artifact (pp 1261.6 / 1244.5, tg 115.7 / 98.5); the medians are the
  2nd/3rd runs. The item's method is the median of 3, and that is what is recorded.
- The same config moved ~4% between two W13 measurements of this evening's setup (20:20 run tg 121.4, 20:24 run tg
  126.2). The W8 gap (-11.8%) is well outside that spread, and every W8 run is below every W13 run, so the
  direction is not measurement noise.
- RAM free during the item was 1.44-1.76 GB, VRAM peak ~14.3 GB on both arms: 8 workers gave ~0.25 GB more RAM
  headroom and no speed. That is not enough to keep a flag that costs 12% decode.

Read the answer scores honestly (accuracy-before-speed is the rule, so say what it did and did not decide):
- W8 passed the bar (tools 9/10, code 4/5, first-try 3/5); W13 measured 8/10 tools, i.e. one task under its own
  18:31 CT baseline of 9/10. The suite resolves at 1-task steps, so this is single-task movement, not a measured
  accuracy difference between 13 and 8 workers (same weights, same prompts, temp 0; 1 of 10 tasks).
- So accuracy did not block the keep here - the speed bar did. Nothing about 8 workers looks like an accuracy gain
  either: prefill and decode are the same or worse and the code/first-try scores are identical (4/5, 3/5).

Method facts worth keeping:
- `GET /running` answers **200 with an empty body** when nothing is loaded. That read is the positive proof of
  absence; the 18:39 draft treated it as a failed read and retried to the deadline. Fixed in `run_opt4a_v2.ps1`.
- The unload path is `POST /api/models/unload/coding_swift15_iq3s_esp`; the first unload of a session empties
  `/running` in 0-1 s. A **second** unload in the same session can leave `/running` at `ready` for >240 s (the
  2026-10-31 18:41 and 20:30 pattern) - llama-swap relaunched the slot from the on-disk config while the proof
  loop polled (engine pid 26296 @20:26:54, pw=13), so the stall is not a stuck engine: the config on disk is what
  the next load uses. `finish_restore13.py` proved the kept state in 30 s (unload 1.0 s, load 28.8 s).
- `C:\AI\community\notes\_opt4a\bench.jsonl` is UTF-16LE (shared file, `Add-Content` keeps an existing file's
  encoding): a `-like '*"tag":"x"*'` filter silently matches 0 rows. Parse each line and compare the `tag`
  property. The first attempt of this item wrote 3 real W13 rows and collected 0 because of this.
- `args`/`args_written` is a **flat** list: the flag string and its value are separate elements, so a value change
  is a changed index (the slot after `--pool-workers`), not a `(flag, newvalue)` pair. The old cfg-edit assert
  from `strata_cfg_edit.py` cannot pass on that layout; the OPT4a copy asserts on the index and on exactly 2
  changed lines. That file also has **no BOM** (3202 B, CRLF), so `strata_cfg_edit.py`'s BOM assert fails on it.
- `Start-Process -WindowStyle Hidden` is how a detached item runs from a pass. `DETACHED_PROCESS` for
  powershell.exe is not: it exits rc=0 with zero output and never runs the script (measured).
- The live box is at 1.4-1.8 GB RAM free with the model loaded, so prefill/decode jitter of a few percent is
  expected; 5% is the right keep bar and 3-run medians are the right instrument.

Answer to the axis: **fewer workers is not free.** On this box 8 workers = 12% slower decode, same prefill,
+0.25 GB RAM free, no accuracy change. 13 stays; the slot keeps answering.

Next (not run here): OPT4b `--pool-affinity` all/auto/p-cores/measure at the kept count 13, same method.
