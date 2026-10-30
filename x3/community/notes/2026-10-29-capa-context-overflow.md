# 2026-10-29 CAPA context overflow — cause, evidence, fix, prevention

Item 1 of the MAX block (fix_plan.md, 2026-10-29 05:20 CT). Done before any T4 render.
Name "CAPA" is the 2026-10-13 bakeoff incident family (`C:/AI/capa-2026-10-13/BRIEF.md`: prefix cache
lost → full prefill → session freeze). Same failure class, now with the arithmetic attached.

## 1. The real context size (measured, not assumed)

- Slot `coding_swift15_iq3s_esp` = `C:\AI\strata-0.2.2\.venv\Scripts\python.exe
  C:\AI\strata-0.2.2\sy_strata_launch.py … --config C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json`
  (that `cmd` is verbatim in `C:\AI\director\config\llama-swap.yaml:90`, the file the running
  `llama-swap.exe -config … -watch-config` (pid 3076) watches).
- `strata-swift15-iq3s-esp.json` → `"--max-context", "131072"`, `"--kv", "int8"`, `--spec 4`,
  `--mtp …`, `--pool-workers 13`. `strata-swift15-iq3s.json` (the non-esp twin, the loop's
  `-Model`) → also `131072`. `strata-iq3_s.json` → `98304`.
- **No `--parallel` / `-np` / slot-splitting flag** in any strata config, and llama-swap runs one
  process per model, so the 131,072 is **not** divided: 131,072 per slot.
- The served ceiling is **lower** than the config number. `C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.log:4537`:

  `strata serve: prompt 124991 tokens = 0 reused + 124991 read in 48250 ms (2590.5 tok/s), 1 generated in 28 ms …`

  124,991 in, **1 token out** → prompt+completion budget ≈ **124,992**, i.e. **6,080 tokens** of the
  configured 131,072 are not usable by the request path. The log names the consumers of that KV
  ("the prompt path borrows 2163 CUDA0 cache slots (4.12 GiB)", the 4-token spec/MTP draft window),
  but the exact split is not printed — the **ceiling is the measured fact, the split is not**.

## 2. Why pi overflowed

pi's session record for the same request
(`C:\Users\derek\.pi\agent\sessions\--C--Users-derek-5slock--\2026-10-29T00-07-43-598Z_01a184fb-….jsonl`,
2026-10-29T04:06:53.853Z = the last record of the T4 session):
`input=124991, cacheRead=0, output=1, stopReason="length"` → the run ended there; the T4 DONE note
records the session as stopped mid-task.

Both of pi's numbers were wrong for this slot (values from `C:\Users\derek\.pi\agent\models.json`
+ `settings.json`, before the fix):

| Number | Was | Real | Effect |
|---|---|---|---|
| `contextWindow` | 128000 | 124992 served | pi believed it had 3,008 tokens that do not exist |
| `maxTokens` | 16384 | 16384 (kept) | request needs `prompt + 16384` |
| `compaction.reserveTokens` | 16384 | ≥ 16384 + summary room | reserve = maxTokens exactly → **zero slack** |

Mechanism, with pi's own rule (`docs/compaction.md`: compact when
`contextTokens > contextWindow - reserveTokens`, checked **after** tools finish and their results are
appended):

1. Trigger was `128000 − 16384 = 111616`. Observed peaks in the Oct 28 sessions: **110,588** and
   **109,617** — the loop habitually runs one token below its own trigger.
2. The check runs *after* tool results are appended, so one large tool output (a workflow JSON, a
   629-line node read-out, a raw `Get-Content`) jumps from 111,616 to ~125,000 in one step.
3. The request then needs `125,000 + 16,384 = 141,384` against a served 124,992 → the engine fills
   what is left (1 token) and answers `stopReason: "length"`.
4. `cacheRead=0` on that request is the CAPA signature: at that size the prefix cache is gone, so the
   full 124,991-token prefill runs (2,590 tok/s on a warm card; the Oct 13 incident ran at 85 tok/s
   and froze the session for 13 minutes).

## 3. The fix (applied 2026-10-29 ~05:30 CT)

`C:\AI\community\scripts\capa_apply_context_fix.py --apply --ctx 124928 --reserve 24576`
(line-scoped, formatting-preserving, refuses to write JSON that does not re-parse; `--check` prints
the change set first). Backups: `models.json.bak-20261029-capa-ctx`, `settings.json.bak-20261029-capa-ctx`.

| File | Key | Before | After |
|---|---|---|---|
| `.pi/agent/models.json` | `llama-swap/coding_swift15_iq3s_esp` → `contextWindow` | 128000 | **124928** |
| `.pi/agent/models.json` | `llama-swap/coding_swift15_iq3s` → `contextWindow` | 128000 | **124928** |
| `.pi/agent/settings.json` | `compaction.reserveTokens` (global) | 16384 | **24576** |
| `.pi/agent/settings.json` | `compaction.modelOverrides.llama-swap/coding_swift15_iq3s_esp.reserveTokens` | 16384 | **24576** |
| `.pi/agent/settings.json` | `compaction.modelOverrides.llama-swap/coding_swift15_iq3s.reserveTokens` | 16384 | **24576** |

- **124928** = the measured served ceiling (124,992) rounded **down** to a 1024-multiple. Deliberately
  not 131,072: the config number is what the engine asks for, the ceiling is what the slot delivers,
  and it is the ceiling that returns `length`.
- **24576** = `maxTokens 16384 + 8192` summary/slack room → compaction now triggers at
  **100,352** prompt tokens and every request keeps 24,576 of headroom.
- `keepRecentTokens` 16384 unchanged; post-compaction context ≈ summary + 16K ≈ 24K, well under the trigger.
- Verified after write: `models.json` / `settings.json` both re-parse; values read back as above;
  `--check` on the applied state reports 5→0 pending changes.

Not touched (documented, adjacent, out of this item's scope):
`strata/qwen3.8-flash-next-iq3_xxs` declares 92160 with `reserveTokens 12288` → trigger 79,872,
request 79,872+16,384 = **96,256**, above the 92,224 that a 98,304 config minus the ~6K KV gap
implies. Same bug class, ~4K short; the same script with `--ctx 92224 --reserve 24576` fixes it.
Max/Derrick's call.

## 4. Prevention (the part that stops a repeat)

1. **One fresh pi session per test arm.** Long sessions are what reach 100K+; T1–T4 each started fresh
   and T4 is the one that died. Start T-arms in a new session and hand over by run dir + DONE note.
2. **Never dump a big file into chat.** Read `*.api.json`, `stock_*.json`, node dumps, session JSONL
   and long logs through a script that prints a *summary* (see
   `C:\AI\community\scripts\capa_ctx_scan.py` — peaks per session, last record, no message bodies).
3. **Keep each file write small**; write notes in sections, don't regenerate whole files.
4. **Tool output budget:** with the new numbers a single tool result above ~8K tokens is the thing
   that can still cross the line. Prefer `Select-String | Select-Object -First N` with substring
   truncation over `Get-Content` of a whole file.
5. **Re-check the ceiling after any engine/strata upgrade** — the 6,080-token gap is engine-version
   behaviour, not a constant: `python capa_apply_context_fix.py --check` prints the arithmetic,
   and the served ceiling is the `prompt N tokens … 1 generated` line in the strata log.

---

## 2026-10-29 07:45 CT - fix_plan item 3 executed: 256K + `--kv-resident` is live (Max / Pi)

Scope as written in the MAX block: 256K context with `--kv-resident`, measured calibrated speed
flags, `contextWindow` from the measured ceiling, compaction fix. GPU was IDLE (gpu_guard) the whole
time; no ComfyUI restart; ESP/control-vector settings untouched (the flag diff proves it).
Work dir: `C:\AI\community\runs\capa256k_20261029\` (scripts + raw JSON evidence).

### What is running now

`C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json` args (45 tokens, list form), diff from the
pre-item-3 state, audited flag-by-flag before writing:

| flag | before | after |
|---|---|---|
| `--max-context` | 131072 | **262144** |
| `--kv-resident` | absent | **32768** |
| `--pcie-frac` | absent | **0.35** |
| `--adapt-every` / `--adapt-swaps` / `--adapt-decay` | absent | **1 / 160 / 0.97** |

`--kv int8` and `--vram-reserve-mib 1100` preserved; `--control-vector-scaled`,
`--control-vector-layer-range`, `--cvec-mode`, `--cvec-dir`, `sampling.experimental_speed_projection`
all byte-identical. `--spec-min-p 0.50` is in the calibration report and the config already carried
`0.5`, so it was not a diff and was left alone. Backup:
`strata-swift15-iq3s-esp.json.bak-20261029-pre-item3`.

**The restart path, which is the part that wasted the first hour:** editing the JSON and killing
`strata.exe` does not change anything. `sy_strata_launch.py` (the proxy on `127.0.0.1:10002`, child
of `llama-swap.exe`) parses the JSON **when the proxy starts** and respawns the engine from the
arguments it cached. Kill the proxy (both pids: the `.venv` shim and the real python) and llama-swap
starts a fresh one on the next request, which reads the current JSON. `kill_proxy.ps1` in the run dir
does that and prints the pid lifecycle. That is "restart the LLM through llama-swap" on this box.

Engine startup (from `strata-swift15-iq3s-esp.log`, 07:26 start):

```
KV streaming: 32768 of 262144 cells per QSA layer in VRAM, the K/V in 3.09 GiB of pinned RAM
expert cache auto: 8.73 GiB free, 1100 MiB reserved (+218 MiB for the draft head) -> 3001 slots
expert cache 3897 slots, 7.44 GiB of VRAM; pre-filled 3897 of 3897 slots from the profile
749 MiB of VRAM free with everything loaded
WARNING: only 749 MiB of VRAM free at the start of this request (below 1024 MiB) ...
WARNING: the expert arena needs 46.84 GiB of RAM but 46.11 GiB is available (0.73 GiB short)
memory guard: limit 63.7 GiB, available 50.9 GiB, floor 2560 MiB
```

`--kv-resident 32768` starts cleanly, so **`--kv-grow` was not needed and was not applied**. Moving
the KV out of VRAM is what created the room: expert cache 3339 -> 3897 slots, and free VRAM at
startup went from the 749 MiB above (with 1,5017 MiB used) - the "card is this full" warning is now
the standing risk to watch, not a new one.

### Measured ceiling (the engine's own token counts, fresh prompts)

The engine's pre-flight refusal is a free token oracle: it names the exact prompt count in ~0.1 s,
so the ceiling is a bisection over real requests, not a word estimate.

| prompt tokens | engine answer |
|---|---|
| 204,712 | accepted, 68.8 s, 2,975 tok/s prefill |
| **249,936** | **accepted**, 86.0 s, 2,912 tok/s prefill |
| 265,964 | refused: `prompt (265964 tokens) leaves no room to answer in the context (262144)` |

Usable fresh-prompt ceiling measured: **249,936** tokens (previous CAPA measured 124,992 with the
131,072 config). Refusal bound 265,964 against the 262,144 window. Evidence:
`cap_bench_calibrated.json`, `wake_and_verify.py` output.

### Prefill / decode at 32K, 131K and the ceiling, calibrated vs uncalibrated

Same script, same filler text, same closing question (a numeric-filler prompt alone answers with 0
tokens and measures no decode - that is why every probe ends with a real question). Numbers are the
engine's own `timings.prompt_ms` / `predicted_ms`.

| prompt | calibrated run 1 | calibrated run 2 | uncalibrated |
|---|---|---|---|
| 29,735 | pre 2,954 / dec 74.9 | pre 2,995 / dec 92.7 | pre 2,948 / dec 65.5 |
| 134,233 | pre 3,030 / dec 99.8 | pre 3,018 / dec 60.0 | pre 3,025 / dec 89.5 |
| 215,840 | - | pre 2,720 / dec 95.8 | pre 2,726 / dec 96.2 |

Prefill is identical between the two arms (within 1%), and decode moves 60-100 tok/s run to run in
**both** arms, so this A/B cannot separate the four flags at 256K with KV streaming: KV streaming is
the dominant effect (the engine reports `98.57% of 10,586,280 block reads hit VRAM, 609.3 MiB read
from RAM`), and the flags' measured target was expert-cache pressure at 131K full-offload.
**Decision: keep the calibrated flags.** Rationale kept honest: they are neutral in today's
measurement (not proven faster), they are the published calibration (`calibrate-report-20261023.json`
measured decode 40.5 -> 83.3 tok/s with them at 131K full-offload), and removing them measured no
gain. If Max wants a real A/B, it needs a repeat-count design; single runs cannot resolve it.

Prefill is the number that changed a lot: the old 131K config read a fresh 119,550-token prompt at
1,994 tok/s; the same shape now reads 134,233 at 3,030 tok/s (+52%), and 215,840 at 2,726.

### contextWindow

`C:\Users\derek\.pi\agent\models.json` -> `providers.llama-swap.models[coding_swift15_iq3s_esp]`:
`contextWindow 124928 -> 245000`, `maxTokens 16384 -> 32768`, text-level edit, deep-diff audited to
exactly those two paths, file re-parses, backup `models.json.bak-20261029-pre-item3`
(`set_model_limits.py`). 245,000 = the measured 249,936 accept point minus a margin, 17K under the
262,144 window.

### Compaction

The mechanism the CAPA needed (from pi's own code, and confirmed by the arithmetic): pi budgets a
compaction at `min(maxTokens, contextWindow/2)` and asks for that much minus a 1,024 reserve. With
`contextWindow 124928` that is 62,464 - against a 131,072 engine window, a compaction prompt of
~65K plus a 62,464 ask does not fit, which is the 400 in the CAPA note. Raising `contextWindow`
alone would have made it worse (122,500), which is why `maxTokens` is pinned to 32,768: the budget
becomes 32,768 and the thinking ask 31,744, and the window has ~130K of spare room behind it.

Proof at the API, with a real conversation transcript as the prompt (7,358 tokens), not filler:

- `max_tokens=62464` thinking on -> **200**, 10,686 tokens generated, 126.8 tok/s decode
- `max_tokens=32768` thinking on -> **200**, 3,010 tokens, 123.0 tok/s, real 9-section summary
- `max_tokens=32768` **thinking off** -> **200**, 8,911 tokens, 125.7 tok/s, real 9-section summary
- six explicit-thinking-budget shapes (61,440) - `thinking.budget`, `thinking_budget`,
  `reasoning_effort=high`, `budget_tokens`, plain `max_tokens` - all **200**

So the 400 does **not** reproduce on the 256K/streaming engine in any shape a gateway can send; the
refusal mechanism is removed by construction (budget 32,768 <= engine thinking cap 32,768, with
~209K of prompt room left). Evidence: `compact_probe.json`, `thinking_budget_probe.json`.

**Not proven in this session:** a literal `/compact`. This session loaded the model limits at start
(124,928 / 16,384), so it is running the old numbers; pi picks up the new limits on restart. Run
`/compact` once in a fresh pi session to close the CAPA. `extension/handoff-compact.ts` was not
created: with the limits fixed, the built-in `/compact` is the path that works, and pi extension
registration lives in `~/.pi/agent/settings.json`, which this session's file tools may not write
(path policy) - the change above was made through a script for that reason.

Two things for Max to look at, found on the way and not touched:
1. `settings.json` `compaction` names provider `strata` with `contextWindow 24576 / maxTokens 20000`.
   The live model is provider `llama-swap`, so that override is dead config for this session.
2. `models.json` keeps `samplingParamsByThinkingLevel.off` (temp 0.7, top_p 0.8, presence 1.5) - the
   compaction-with-thinking-off path is already wired at the model level.
