

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
