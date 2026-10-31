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
