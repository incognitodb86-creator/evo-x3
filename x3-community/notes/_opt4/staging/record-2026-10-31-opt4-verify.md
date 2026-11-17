# 2026-10-31 OPT4 - verify + test strata tuning, close-out (Forge, ralph)

Status: **DONE**. Item: `fix_plan.md` OPT4 (Max applied 2026-10-31 per Derrick 12:44 CT). The two sweep
halves are closed in their own items: OPT4a kept `--pool-workers 13`, OPT4b kept the default placement
(no `--pool-affinity`). This pass closed the parent item's remaining clauses: rerun
`C:\AI\community\notes\strata-bench.ps1` x3, confirm `vision threads=6` / `vision.exe 0.1.54
(engine-028)` / `resident budget 32 GiB` are live, keep a setting only if within 5% of best, and carry
before/after numbers for every setting. Full section with tables:
`C:\AI\community\notes\strata-tuning-2026-10-31.md` → "OPT4 close-out", ends `DONE`.
Data: `C:\AI\community\notes\_opt4\` (`run_opt4_final.ps1`, `bench.jsonl`, `final.log`,
`final.result.json`, `summarize_opt4.py`).

## Kept configuration (live, proved)

| knob | live state | proof |
|---|---|---|
| `--pool-workers` | `13` | live engine pid 26492 command line (started 21:16:59, after the OPT4b config write) |
| `--pool-affinity` | absent (= `all`) | same command line; config has no affinity pair, bytes == `.bak-opt4a` (3202 B) |
| `--resident-budget-gib` | **absent** (arena mode) | same command line; `.bak-1328` = 32, `.28gib-1251` = 28, both on disk |
| `--kv-resident` | `32768` (untouched, different flag) | same command line |
| vision `--threads` | `6` | running `strata-vision.exe` pid 31008 (start 21:16:56) `--threads 6 --max-tokens 3000` |
| vision binary | engine-028 / 0.1.54 | ExecutablePath `C:\AI\strata-engine-028\engine\0.1.54-windows-x86_64-cuda-cuda13\strata-vision.exe`, SHA-256 `4ab880a2657f2407...` == `engine-component.json`; `strata.exe` `107ef7fa3b33976c...` == manifest; `BUILD.json` `version 0.1.54`, `commit 8c1aea4bca1b`, `cuda 13.0` |

## The x3 at the kept state (22:12:45-22:12:58 CT)

`strata-bench.ps1 -Runs 3 -Tag opt4-final` through llama-swap :8080, temp 0, 1905 prompt / 256 completion
tokens, inside `notes\_opt4\run_opt4_final.ps1` (GPU lock ACQUIRED pid 2628 → RELEASED pid 2628 in a
`finally`, `NO LOCK` at end). RAM free 2.03 → 2.57 GB, VRAM used 14219 MiB before and after, no memory
error, no 5xx.

| run | wall_s | pp_tps | tg_tps |
|---|---|---|---|
| 1 | 4.45 | 1659.7 | 116.8 |
| 2 | 4.08 | 1739.9 | 129.9 |
| 3 | 4.09 | 1739.0 | 128.5 |
| **median** | **4.09** | **1739.0** | **128.5** |

vs the item's starting baseline (pp ~617, tg ~83 / 79.5-85.7, wall 7.0-8.0 s) = **+182% prefill, +55%
decode, -42% wall**. vs OPT5 arena medians (1720.5 / 125.0 / 4.16) = +1.1% / +2.8% / -1.7% = the same
state inside noise. vs OPT4b P-all at the identical config (1684.8 / 117.6 / 3.31) = +3.2% / +9.3% /
+24% wall; the tg move is inside the 6.2-10.8% noise floor measured in OPT4b, and the wall move is
queueing (this pass's own chat traffic shares the slot; 1905/1739 + 256/128.5 = 3.1 s of the 4.09 s).
No setting was changed by this run.

## The resident-budget clause: the item's expectation is older than OPT5

The item asks to confirm `resident budget 32 GiB` is live. It is not, and the live state is the kept one:

1. `.bak-1328` (3277 B) = `--resident-budget-gib 32` — the state the item expects.
2. Max's 28 GiB test `.28gib-1251` = `--resident-budget-gib 28`: prompt read 655 → 498 tok/s (-24%), log
   warned the prompt lend region had 0 of 1859 slots in RAM → Max reverted.
3. Derrick 13:28 CT "remove the RAM budget setting and benchmark it" → OPT5 removed the flag; it passed
   every keep bar (decode +46-57%, wall -41%, prefill +179% vs a floor of 586) → **removal is kept**.
4. OPT4a/OPT4b kept `--pool-workers 13` and the flag-free placement, so the live file equals `.bak-opt4a`
   (3202 B), which has no resident-budget flag.

Nothing restored; `.bak-1328` is on disk if Max wants 32 GiB back. The item's "keep a setting only if
within 5% of best" is satisfied: every live setting is the best-measured option of its arms, and nothing
inside the noise band was kept as a win.

## Not touched

No config write in this pass, no llama-swap / ComfyUI / strata restart, nothing installed, downloaded,
moved, deleted or rendered, no other flag touched, GPU lock released.
