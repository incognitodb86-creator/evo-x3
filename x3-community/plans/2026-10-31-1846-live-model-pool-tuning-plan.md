# Live Swift model: fastest settings without hurting answers (v2, 2026-10-31 19:40 CT)

v2 supersedes v1 (18:46 CT, pool-workers only). v2 answers Derek's direct brief of 19:34 CT:
**threads, batch sizes and context lengths, one at a time, tokens/s measured for each, answers
checked each time, keep the winner, hand back a table.** Nothing has been run from v1 or v2.

## Goal

Find the fastest configuration of the live coding model `coding_swift15_iq3s_esp`
(strata 0.1.54 engine-028, llama-swap :8080) that does not lower its answer quality, keep it,
and give Derek a table of every arm.

**Done when:** `notes\strata-tuning-2026-10-31.md` has a section with one row per arm (tok/s +
answer score + verdict), a "what I kept" line, the live config file matches the kept arm with a
backup and a live-args proof, `progress.md` / `actions.log` / brain records exist, and Derek has
the table in chat.

## Live state (read-only, verified 19:35-19:40 CT 2026-10-31)

- `llama-swap.exe` PID 32452 (up 13:50:27) `-config C:\AI\director\config\llama-swap.yaml -listen 127.0.0.1:8080 -watch-config`. **The config is a persistent file**, not memory-only (v1's headline fact was wrong, corrected here).
- Running slot: `coding_swift15_iq3s_esp` → `C:\AI\strata-0.2.7\sy_strata_launch.py ... --config C:\AI\strata-0.2.7\strata-swift15-iq3s-esp.json --port 10002`. **The model's flags live in that JSON** (`args` + a duplicate `args_written`), so every arm is one byte-precise edit of that file (the proven editor `notes\strata_cfg_edit.py` keeps the UTF-8 BOM, CRLF, and the 2× duplication).
- Current live flags (the incumbent = baseline arm A0): `--pool-workers 13`, **no** `--pool-affinity`, `--prefill auto`, `--max-context 131072`, `--kv int8`, `--kv-resident 32768`, `--spec 4 --spec-min-p 0.5`, `--mtp`, control vector 4-44 project, `--vram-reserve-mib 1600`, `--pcie-frac 0.35`, `--adapt-*`. v1's "--context 4096, a 12k prompt will not fit" is **wrong**: capacity is 131072, so the context axis is testable and OPT1/OPT3's stated blocker does not exist.
- Box: Intel Core Ultra 7 265KF, **20 physical cores (8P+12E), 20 logical, hybrid** → the engine's default `--pool-workers 0` = 19; `p-cores` = P-cores + siblings; `--pool-affinity measure` is documented for exactly this case ("hybrid CPUs, native packs: all and p-cores are timed on the pack's own experts at start"). RAM 64 GB, **1 GB free with the model resident** (engine WS 49.3 GB). VRAM 16303 MiB total, **14322 MiB used**. No GPU render, no gpu lock, `strata-vision` threads=6.
- `--batch N` (decode batch, 2..8) is opt-in for `--serve` and needs "**VRAM like the main one**" per slot → at 14.3/16.3 GB it will very likely refuse. The viable "batch size" knob on this box is the prompt-batch `--prefill CHUNK` (auto = largest lendable chunk ≤ 8192; `auto:16384` allowed). Both are measured.
- Reload method that works on this box (OPT4a, NV1b): `POST http://127.0.0.1:8080/api/models/unload/coding_swift15_iq3s_esp`, wait for `/running` empty, next chat request loads the model with the new flags. `POST /unload` (bare) returns 405 - not the path.
- Answer baseline to beat (measured 18:31 CT, same model, temp 0): **BQ tools 9/10, code 4/5, first-try 3/5**, suite wall **115 s** (model 57.0 s / 20 requests). Instruments already on disk: `notes\bq-suite\run_bq.py` + `summarize.py` (self-tested), `notes\strata-bench.ps1` (timings from the engine's own `prompt_per_second` / `predicted_per_second`), `notes\strata_cfg_edit.py`, `C:\AI\director\scripts\gpu_lock.ps1`.
- Speed reference points (not the baseline; they are Max's, at other prompts/settings): live 15:00 CT pp256 101.6 / pp1024 96.6 / tg128 81.2, chat first token 2.23 s; NV1d decode at 2K ~131-136 tok/s; isolated engine at w13 123.5/113.0/87.9, w8 117.4/104.1/86.3. The live-vs-isolated gap (~20-25%) is why **every arm is measured on the live server**, and why A0 is re-measured in this sweep as the only baseline used.

## Method

One driver, `C:\AI\community\notes\_tune\run_arms.py`, holding `C:\AI\locks\gpu-render.lock` for
the whole sweep, one arm at a time. Per arm:

1. Write the arm's flags into the JSON (backup once; every write strict-parsed, re-read, and asserted to change **only** the named flags, in both `args` and `args_written`), then `POST /api/models/unload/...` and wait for `/running` empty.
2. Warm: one chat request (loads the model with the new flags, result discarded).
3. **Prove the arm is live**: read the new `strata.exe` command line and log the flag values from the process itself, plus the engine log lines for pool/affinity/context. An arm whose live args do not match is a FAIL row, not a number.
4. Speed: `strata-bench.ps1` -Runs 3 (fixed ~2K-token prompt; `pp_tps`, `tg_tps`, `wall_s`) → median, plus TTFT from the warm request. n=3, median, min/max recorded.
5. Answers: `run_bq.py` (10 BFCL tool-call + 5 Aider code items, temp 0) → `summarize.py`. 115 s, so **every** arm carries its own answer score - this is the "check the answers still come out right" per setting, not a spot check at the end.
6. Safety: RAM free minimum and VRAM peak during the arm, engine exits/OOM/timeouts.
7. Append a row to `notes\_tune\arms.jsonl`, log to `notes\_tune\arms.log`, restore nothing (the next arm's write comes next).

**The self-brain rule** (NV1a lesson: a ralph pass runs on the slot it tunes, so a pass must not
need the model after it unloads it): the driver is invoked per arm-slice and the **last** thing a
pass does is apply the next arm and unload; the pass then ends. The next pass starts on the new
config. Nothing asks the model a question after an unload inside a pass.

Idle machine, no renders, lock held, one engine process, 10 s settle between servers, no
`--kv-resident` change (Max measured 28 GiB = 24% slower prompt read and reverted it), no
ComfyUI/strata-0.2.7/llama-swap.yaml change beyond the model JSON.

## Arms (one variable each; A0 = incumbent)

| id | axis | change from A0 |
|---|---|---|
| A0 | baseline | none (re-measure w13 in this sweep, the only bar used) |
| T1 | threads | `--pool-workers 19` (engine default on this 20-core CPU) |
| T2 | threads | `--pool-workers 8` |
| T3 | threads | `--pool-workers 4` |
| T4 | threads | best T + `--pool-affinity measure` (self-times `all` vs `p-cores`) |
| T5 | threads | best T + `--host-core last` (GPU interrupts land on the first logical processor) |
| B1 | batch | `--batch 2` (decode slots - viability/VRAM ceiling probe) |
| B2 | batch | `--prefill 512` (prompt batch, small chunks) |
| B3 | batch | `--prefill 2048` |
| B4 | batch | `--prefill auto:16384` (bigger prompt batch, needs bigger lend buffers) |
| C1 | context | `--max-context 32768` |
| C2 | context | `--max-context 8192` |

Context arms also run one long-context answer check at a ~6k-token prompt with 3 planted needles
(fits C1 and C2) so "answers still right" is tested inside the reduced window, not just at 2K.

## Acceptance and keep rule

- **Answer gate (hard, per arm):** BQ tools ≥ 9/10, code ≥ 4/5, first-try code ≥ 3/5, 0 timeouts,
  0 engine errors/OOM. Any miss = the arm is reported and **not** kept.
- **Speed:** keep the arm with the highest median tg128 among arms that pass the answer gate, and
  it must beat A0 by **≥5%** (Max's rule). Improvement < 5% = the same; on a tie inside 5% take
  fewer workers / fewer flags (thermal + power headroom, per v1).
- **Context arms are never kept below 131072** (Ask 2): a smaller capacity removes long-context
  ability, which is an answer regression by definition. They are measured so the table can say
  what the capacity costs. A C-win is only kept if Derek says yes to the trade.
- **Safety:** RAM free ≥ 1.0 GB and VRAM peak ≤ 15.4 GB and no pinned-memory exhaustion.
- If nothing beats A0 by 5%: **keep A0**, write that in the table, and restore the file from the
  backup byte-for-byte.
- A stopped/partial arm is recorded as such; never replaced by a number from the isolated engine.

## Cost and impact

11 arms + A0. Each arm = unload + model load (49 GB resident) + warm + 3 timed runs + 115 s
answer suite ≈ **6-9 min**, so ~90-120 min of model time in **5-7 ralph passes**
(`-Max 9 -PassLimitSec 3600`). Each arm takes the live chat model down ~1-3 min: **11 short
interruptions** of the model pi and Sydney talk on. Back-to-back in one evening; a `STOP` file in
`notes\_tune\` halts the sweep between arms and leaves the last applied config clearly logged.

## Risks

- **RAM 1 GB free at rest**: `--prefill auto:16384` (B4) may hit pinned-memory exhaustion (NV1b
  saw it on the NVFP4 pack). B4 runs last in its block; a refusal is recorded as "not viable on
  this box", never retried by cutting `--kv-resident`.
- **B1 `--batch 2` needs a second session's VRAM.** Expected refusal; the row is still the answer
  to "try batch sizes".
- **Live-slot restarts are the model's own brain** (pi's provider). Mitigation: the self-brain
  rule above, Ask 1, and `STOP`.
- **Transient exit 137** on engine teardown (seen 18:20 CT): known artifact, retry once, never a row.
- **Answer gate is n=1** (15 items): stated as a smoke gate; a drop blocks the keep and is carded.
- **Thermal drift across a 2-hour sweep**: A0 is measured first and again after the last arm;
  a >5% A0 drift invalidates cross-arm comparison and is reported.

## Asks (Derrick, 2 questions)

1. **Live-slot restarts** - yes/no: 11 unload+reload cycles of `coding_swift15_iq3s_esp`
   (1-3 min each, llama-swap's own unload, no llama-swap process restart, gpu lock held).
   Needed because the AGENTS.md keep says never touch llama-swap/strata/pi processes.
2. **Context axis** - (a) measure only, always keep 131072, or (b) allow a smaller context to be
   kept if it wins by ≥5% (shortens the longest chat/session this model can serve).

## Records

`notes\_tune\arms.jsonl` + `arms.log` + driver + BQ rows, the OPT4-S section of
`notes\strata-tuning-2026-10-31.md`, `notes\progress.md`, `notes\actions.log` (START/DONE via
`tools\append_actions_log.py`), fix_plan ticks, config backup `strata-swift15-iq3s-esp.json.bak-<time>`,
brain record + learning (tagged unreviewed), commit + push. Max's open OPT4a/OPT4b items are
untouched (they are covered by T1-T5 and reported to him).

**STATUS: DROPPED by Derek 2026-10-31 7:52 PM CT** - his words: "Drop the TUNE-S sweep for now and don't run it. Finish only the two open items in your fix_plan.md, OPT4a and OPT4b." Nothing from this plan was run and it touched no config. The live-model work he asked for is the two existing items OPT4a (pool-workers 13 vs 8) and OPT4b (worker CPU affinity); their text in `C:\Users\derek\5slock\ralph-community\fix_plan.md` now carries the corrected method - engine 0.1.54 affinity values are all / auto / p-cores / measure, "none" is not one of them (omitting the flag = all) - plus the per-arm answer gate, on his rule "Accuracy comes before speed". The 11-arm table design stays here for reference only.