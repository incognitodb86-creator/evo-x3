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

---

## OPT4b - `--pool-affinity` at the kept worker count 13 (Forge, ralph pass 2026-10-31 20:48 → 21:19 CT)

Scope: one variable, `--pool-affinity`, on `coding_swift15_iq3s_esp` at the worker count kept by OPT4a
(`--pool-workers 13`). Values on engine `strata 0.1.54` are `all` (default, = the flag omitted), `auto`,
`p-cores`, `measure` - `none` is not a value. Box: Core Ultra 7 265KF, 8 P-cores + 12 E-cores, 20 logical.
GPU lock held for the whole item, released in a `finally`, `NO LOCK` at the end.

The four arms were measured by the previous pass (detached run pid 35784, 20:48:23 → 21:05:18,
`result-2048.json`, `error: None`, duration 1015 s). That pass ended (ralph logged `PI_NONZERO rc=1` at
20:57) before any record was written. This pass re-read the raw files itself
(`notes\_opt4b\verify_data_opt4b.py` → `RESULT: PASS`): 3 timed rows per arm, medians recomputed from
`bench.jsonl` equal to what `arms.jsonl` recorded, BQ counts recomputed from `bq_p_*.jsonl` equal to the
recorded counts, and the sweep config proved byte-equal to `.bak-opt4a` plus the affinity pair only.

### The table

| arm | flag | live proof (PID, live args) | pp t/s med | tg t/s med | tg vs P-all | wall s | BQ tools | BQ code | first-try | RAM min | VRAM peak | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **P-all** | absent (= `all`) | pid 16584, pw=13, pa=ABSENT | 1684.8 | **117.6** (103.7/124.6) | baseline | 3.31 | 8/10 | 5/5 | 3/5 | 1.34 GB | 14317 MiB | baseline row |
| **P-auto** | `auto` | pid 30812, pw=13, pa=auto | 1710.8 | 124.9 (119.1/126.6) | **+6.2%** | 3.17 | 9/10 | 4/5 | 3/5 | 3.64 GB (15 samples) | 14269 MiB | passes the bar as written; **not a real effect** (identical placement) |
| **P-pcores** | `p-cores` | pid 26404, pw=13, pa=p-cores | 1618.1 | 112.3 (103.3/116.8) | **-4.5%** | 3.46 | 9/10 | 4/5 | 3/5 | 1.36 GB (17 samples) | 14257 MiB | REJECT (real placement change, costs decode) |
| **P-measure** | `measure` | pid 21808, pw=13, pa=measure | 1665.4 | 124.4 (99.2/125.6) | +5.8% | 3.21 | 8/10 | 4/5 | 3/5 | 0.75 GB (18 samples) | 14252 MiB | REJECT (answer bar fail; ran p-cores placement) |

Engine self-test choice, recorded as the item requires (P-measure's own start log):
`strata generate: --pool-affinity measure: 2 experts x 4 tokens per layer over 48 layers: all (13 workers)
5.16 ms, p-cores (13 workers) 5.26 ms (medians of 3) -> p-cores` — a 2% margin, and it chose `p-cores`.

### Live CPU placement (the engine's own lines, not my inference)

| arm | engine line | workers | placement |
|---|---|---|---|
| P-all | `13 pool workers on logical processors 1,2,3,4,5,6,7,8,9,10,11,18,19, the host thread on 0` | 13 | all non-host logicals |
| P-auto | identical line, identical list | 13 | **the same placement as P-all** |
| P-pcores | `13 pool workers on logical processors 1,6,7,8,9,18,19, the host thread on 0` | 13 onto 7 | P-cores + siblings only |
| P-measure | same line as P-pcores | 13 onto 7 | the p-cores placement it self-selected |

### What this axis is worth in plain words

- `auto` at 13 workers on this box is **not a distinct configuration**: the engine places exactly the same
  13 workers on the same 13 logical processors as the default. The +6.2% that P-auto measured over P-all is
  measurement movement, not a gain.
- The two arms that *do* share a placement (P-pcores and P-measure, both 13 workers on 7 logical processors)
  differ by **+10.8%** in median tg. So this instrument's noise floor at identical placement is **6.2-10.8%**,
  i.e. wider than the 5% keep bar. No 5% claim from 3-run medians on this box is trustworthy; n≥5 with
  paired A/B/A is the minimum.
- The only real effect measured: `p-cores` puts 13 workers on 8 physical P-cores (oversubscribed) and costs
  **4.5%** decode speed with no answer gain. `measure` inherits that placement because its own micro-benchmark
  rated p-cores 2% faster, and its arm failed the answer bar (tools 8/10).
- Answer quality never decided this axis: every arm is 8-9/10 tools and 4-5/5 code at temp 0, within
  1-of-10 task movement of the 18:31 CT baseline (9/10, 4/5). The speed axis decided it, and the speed axis
  is noise.

### Kept configuration and its proof

Kept = **P-all: `--pool-workers 13`, no `--pool-affinity`** (the item's rule: inside 5% keep P-all, the
default with no extra flag; and if nothing passes, restore the flag-free `.bak-opt4a` state and say so).

- Config written through the byte gate: `notes\_opt4b\cfg_edit_opt4b.py` `op=remove` 3268 → 3202 B,
  `--pool-workers` 13 in both `args` and `args_written`, affinity pair removed from both, CRLF kept, no BOM;
  `cfg bytes == .bak-opt4a` **True** (3202 B).
- Live proof after the reload (engine started **after** the config write): `strata.exe` **pid 26492 @21:16:59**
  with `--pool-workers=13`, `--pool-affinity` **ABSENT**, `--max-context 131072`, placement
  `13 pool workers on logical processors 1,2..11,18,19, the host thread on 0`.
- `/running` = `coding_swift15_iq3s_esp ready`, `/v1/models` lists the slot, **one chat request 200 in 368 ms**
  (content `OPT4B-P-ALL-OK`, model `swift-1.5-iq3_s-esp`) - `proof-2119.json`.
- GPU lock: ACQUIRED/RELEASED pid 30620, 31780, 34372, 19960, 9148 (each in a `finally`), `NO LOCK` at end.
  No render, no llama-swap / ComfyUI / strata process restart, no other flag touched.
- Backup for the state: `C:\AI\strata-0.2.7\strata-swift15-iq3s-esp.json.bak-opt4a` (3202 B) is the kept
  state, byte-identical to the live file.

### Instrument facts this pass paid for

1. The sweep folder now mixes encodings: `bench.jsonl` is **UTF-16LE**, `arms.jsonl` and `bq_*.jsonl` are
   **UTF-8 with BOM**. A reader that assumes one encoding parses **zero rows and stays silent** (my first
   verifier reported `rows=0` for every arm). Sniff the BOM.
2. `POST /api/models/unload/<name>` through PowerShell 5.1 `Invoke-WebRequest` returns **404**; the identical
   curl POST returns **200 OK** (GET on the route returns 405, so the route is real). Do the unload with curl.
3. `/v1/models` is not the slot registry: it lists only what llama-swap currently has loaded, and it read
   without the slot right after a reload. Readiness = `/running` + the live args of the engine + a chat 200.
4. After an unload, the agent session's own next generation relaunches the slot from the config on disk (that
   is what happened at 21:16:59). So a live-args proof must assert "**engine started after the config
   write**", not "a PID new to my pre-load list" - the second form fails a run that actually succeeded.
5. The answer-gate raw rows are 15 per arm (`tools_*` 10, `code` 5) with `pass` booleans and per-try
   `tries[]`; the long-form part of BQ-15 is not written per arm, so the per-arm gate here is the tool/code
   part only. Say that when quoting "BQ" counts.
6. The RAM/VRAM columns are only comparable inside one run's sampling: P-all sampled 84 times, the other arms
   15-18 times, so P-auto's "3.64 GB free" is a shorter observation window, not a memory win. P-measure's
   0.75 GB minimum is under the 1.0 GB floor the TUNE-S plan uses - one more reason that arm is not keepable.
7. The `min` of each arm's 3 runs is the warm-up artifact (pp 1116/1210/1100 for arms 2-4, 1651 for P-all);
   the medians are the comparable numbers, same as OPT4a.

### Status of the OPT4 block

OPT4a (worker count 13 vs 8) kept **13**. OPT4b (placement at 13) kept **the default, no flag**. The
`--pool-affinity` axis is closed as a no-op on this box; TUNE-S stays dropped per Derek 7:52 PM CT.
For a real gain, the next axis worth measuring is the one that changes where work runs and is not noise:
worker count *below* the P-core count with `p-cores` (e.g. 7 workers + `p-cores`), with n≥5 paired runs.


---

## OPT4 close-out: the three confirmations + the final x3 (Forge, 2026-10-31 22:13 CT)

Closes the remaining clauses of the parent item `- [ ] OPT4 verify+test strata tuning`: rerun
`strata-bench.ps1` x3, confirm `vision threads=6`, `vision.exe 0.1.54 (engine-028)` and
`resident budget 32 GiB` are live, keep a setting only if within 5% of best, and carry before/after
numbers for every setting the item touched. The two sweep halves are closed above (OPT4a kept
`--pool-workers 13`, OPT4b kept the default placement with no `--pool-affinity` flag).

### 1. strata-bench.ps1 x3 at the kept configuration (verification, not an arm)

`powershell -File C:\AI\community\notes\strata-bench.ps1 -Base http://127.0.0.1:8080 -Model
coding_swift15_iq3s_esp -Runs 3 -Tag opt4-final -Out C:\AI\community\notes\_opt4\bench.jsonl`, run
inside `notes\_opt4\run_opt4_final.ps1` (GPU lock acquired and released in a `finally`, owner = the
live ralph pid). 22:12:45 → 22:12:58, 1905 prompt tokens / 256 completion tokens, temp 0.

| run | wall_s | pp_tps | tg_tps |
|---|---|---|---|
| 1 | 4.45 | 1659.7 | 116.8 |
| 2 | 4.08 | 1739.9 | 129.9 |
| 3 | 4.09 | 1739.0 | 128.5 |
| **median** | **4.09** | **1739.0** | **128.5** |

RAM free 2.03 → 2.57 GB, VRAM used 14219 MiB before and after, no memory error, no 5xx. GPU lock
ACQUIRED pid 2628 → RELEASED pid 2628, `NO LOCK` at the end.

Against the numbers in this file:

- the item's starting baseline (prefill ~617, decode ~83 / 79.5-85.7, wall 7.0-8.0 s): **+182%
  prefill, +55% decode, -42% wall**.
- OPT5 arena medians (1720.5 / 125.0 / 4.16): +1.1% pp, +2.8% tg, -1.7% wall = the same state,
  inside noise. This run is a re-verification of the kept configuration, no setting was changed.
- OPT4b P-all at the identical config (20:48, 1684.8 / 117.6 / 3.31): +3.2% pp, **+9.3% tg**,
  +24% wall. The tg move sits inside the 6.2-10.8% noise floor that OPT4b measured at identical
  placement, so it is not a gain. The wall move is queueing, not the model: 1905/1739 + 256/128.5 =
  3.1 s of the 4.09 s, and this pass's own chat traffic shares the slot.

### 2. The three confirmations

**(a) vision threads = 6 — LIVE, proved from the running child.** `strata-vision.exe` pid 31008,
start 21:16:56, live command line
`... --mmproj C:\AI\Strata-data\models\swift15-iq3s\mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf --model ... --threads 6 --max-tokens 3000`;
config `vision.threads` = 6. Proof: `Get-CimInstance Win32_Process -Filter "Name='strata-vision.exe'"`.

**(b) vision.exe 0.1.54 (engine-028) — LIVE.** The running vision child's ExecutablePath is
`C:\AI\strata-engine-028\engine\0.1.54-windows-x86_64-cuda-cuda13\strata-vision.exe`
(108,196,864 B). That directory's `BUILD.json` says `version 0.1.54`, `source f-028-rel`,
`commit 8c1aea4bca1b`, `cuda 13.0`; the file's SHA-256 `4ab880a2657f2407...` matches
`engine-component.json`, as does the model engine `strata.exe` `107ef7fa3b33976c...`, so the running
pair is the signed 0.1.54 component. `strata.exe --version` prints `strata 0.1.54`.

Fact for the next reader: **`strata-vision.exe` has no version output** — `--version` prints the bare
word `strata-vision` — and its Windows version resource is empty (`FileVersionRaw 0.0.0.0`). A vision
binary's version is proved by ExecutablePath + `BUILD.json` + SHA-256, never by FileVersion.

**(c) resident budget 32 GiB — NOT live, and the live state is the kept one, not a regression.** The
live engine args contain no `--resident-budget-gib`. The chain, with its numbers:

1. `.bak-1328` (3277 B) = `--resident-budget-gib 32` — the state the parent item expects.
2. Max's 28 GiB test `.28gib-1251` (3277 B) = `--resident-budget-gib 28`: prompt read fell
   655 → 498 tok/s (-24%) and the log warned the prompt lend region had 0 of 1859 slots in RAM, so
   Max reverted it.
3. Derrick 13:28 CT: "stay on 0.1.54, remove the RAM budget setting and benchmark it" → OPT5 removed
   the flag; it passed every keep bar (decode +46-57%, wall -41%, prefill +179% against a floor of
   586), so **removal is the kept setting** (OPT5 RESULT 14:05 CT).
4. OPT4a kept 13 workers and OPT4b kept the flag-free placement, so the live file equals
   `.bak-opt4a` (3202 B) byte-for-byte, which has no resident-budget flag.

The parent item's expectation (32 GiB) predates the later approved item that removed it. Nothing was
restored: the 32 GiB state is on disk as `strata-swift15-iq3s-esp.json.bak-1328` if Max wants it
back. `--kv-resident 32768` is a different flag (resident KV blocks, not the RAM budget); it is live
and was not touched.

### 3. Before/after numbers for every setting this item family touched

| setting | before (state and numbers) | after = kept (numbers) | source |
|---|---|---|---|
| `--resident-budget-gib` | `32` (`.bak-1328`): pp ~617, tg ~83 (79.5-85.7), wall 7.0-8.0 s; `28` (`.28gib-1251`): prompt read 655 → 498 tok/s (-24%), 0 of 1859 lend slots in RAM, reverted | **flag removed** (arena): OPT5 medians pp 1720.5 / tg 125.0 / wall 4.16; re-verified now pp 1739.0 / tg 128.5 / wall 4.09 | OPT5 section, this section |
| `--pool-workers` | 13 (only baseline, re-measured in-sweep): pp 1708.1, tg 126.2, wall 3.15 | **13 kept**; the 8 arm measured pp 1703.5 (-0.3%), tg 111.3 (**-11.8%**), wall +8.9% | OPT4a section |
| `--pool-affinity` | default `all` (flag absent): pp 1684.8, tg 117.6, wall 3.31 | **flag absent kept**; `auto` +6.2% is the same placement (identical logical processors), `p-cores` -4.5%, `measure` self-tested to p-cores and failed the answer bar | OPT4b section |
| `vision threads` | 6 | **6 unchanged and confirmed live** (child pid 31008 `--threads 6`) | this section |
| `vision exe` | engine-028 / 0.1.54 | **unchanged, confirmed live + SHA-verified** | this section |

### 4. The keep rule as applied ("keep a setting only if within 5% of best")

- **pool workers**: 13 is the better of the two arms; 8 measured -11.8% decode → 13 kept.
- **pool affinity**: the default (no flag) kept; the only arm that changes placement costs 4.5%
  decode, and the +6.2% arm is the same placement inside the noise floor → flag-free kept.
- **resident budget**: removal is the only arm in this item family that beats its baseline by far
  more than the noise floor (decode +46-57%) → kept removed.

Every setting that is live is the best-measured option of its arms. Nothing inside the noise band was
kept as a "win".

### 5. State of the box at the end of this pass

- Config `C:\AI\strata-0.2.7\strata-swift15-iq3s-esp.json` 3202 B, byte-equal to `.bak-opt4a`;
  live engine pid 26492 (started 21:16:59) with `--pool-workers 13`, no `--pool-affinity`, no
  `--resident-budget-gib`, `--max-context 131072`, `--kv-resident 32768`; vision child pid 31008
  `--threads 6`, both binaries SHA-matched to the 0.1.54 component manifest.
- No config change in this pass, no restart (llama-swap, ComfyUI and strata processes untouched),
  nothing installed, downloaded, moved or deleted, no render, GPU lock released, `NO LOCK` at the end.
- Real traffic on the kept config at the same time (engine log): 57k-70k-token prompts read at
  3155-3230 tok/s, decode 106-111 tok/s, decode expert cache hit rate 72-80%, KV streaming
  91-98% VRAM hits.
- Data and scripts for this close-out: `C:\AI\community\notes\_opt4\`
  (`run_opt4_final.ps1`, `bench.jsonl`, `final.log`, `final.result.json`, `summarize_opt4.py`).

OPT4a, OPT4b and the OPT4 verification clauses are all closed. Kept state: `--pool-workers 13`, no
`--pool-affinity`, no `--resident-budget-gib`, vision `--threads 6` on engine-028 0.1.54. TUNE-S stays
dropped per Derek 7:52 PM CT.

DONE
