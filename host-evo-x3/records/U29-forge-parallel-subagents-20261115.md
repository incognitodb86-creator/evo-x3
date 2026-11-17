---
pending_upload: true
title: U29 Forge parallel subagents and Halogen 4-slot proof test
tags: [evo-x3, u29, flash-next, halogen, pi-subagents]
---

# U29: Forge parallel subagents + 4-slot proof test

Date: 2026-11-15 CT. Approval: Derrick card t1811s6675. Runner: Max Architect (executor).
Community way: llama-swap official aliases (https://llama-swap.ai/features/names-and-aliases, accessed 2026-11-15 CT) + installed pi-subagents 0.83.1 docs/configuration.md and docs/models.md → reuse. Subagent contextWindow 131072 (brief's first option; official docs do not favor 65536).

## What changed
- llama-swap.yaml: backup `/etc/evo-x3/llama-swap.yaml.bak-20261115-192840-pre-u29`
- models.json: backup `/home/derekboone/.pi/agent/models.json.bak-20261115-192840-pre-u29`
- subagent/config.json: backup `/home/derekboone/.pi/agent/extensions/subagent/config.json.bak-20261115-192840-pre-u29`
- forge settings: backup `/home/derekboone/AI/forge/.pi/settings.json.bak-20261115-192840-pre-u29`
- `/etc/evo-x3/llama-swap.yaml`: added `aliases: [flash-next-sub]` and `useModelName: flash-next` on the official `flash-next` slot only. `concurrencyLimit` stays 4. No Halogen engine flags changed (no pool raise, no KV8, no slot change). Render's `gemma4-heretic` block was not edited.
- `~/.pi/agent/models.json`: added `x3-local` model `flash-next-sub` with `contextWindow` 131072 and `maxTokens` 8192. Parent `flash-next` stays 262144 / 32768. File mode 0600; not committed (contains an API key).
- `~/AI/forge/.pi/settings.json`: `subagents.defaultModel` set to `x3-local/flash-next-sub`. Render's Heretic subagent setting was left alone. User-level `~/.pi/agent/settings.json` was left alone.
- `~/.pi/agent/extensions/subagent/config.json`: `parallel.concurrency` 3, `globalConcurrencyLimit` 4, `maxActiveAsyncRunsPerSession` 4, `maxSubagentDepth` 1 (official 0.83.1 keys).

## Quick check (3 Forge subagents)
```
{
  "rc": 0,
  "got": {
    "apple": true,
    "banana": true,
    "cherry": true
  },
  "used_sub_model": true,
  "swapped": false,
  "log_hits": [
    "[INFO] <flash-next> Health check passed on http://127.0.0.1:8081/health",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:39726 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:39730 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK",
    "INFO:     10.88.0.1:51810 - \"POST /v1/chat/completions HTTP/1.1\" 200 OK"
  ],
  "parent_reported_concurrent": true
}
```
Output tail (truncated):
```
Done — three `worker` children in one parallel fan-out.

| Child | Output | Model |
|---|---|---|
| task-1 | `APPLE` | x3-local/flash-next-sub:high |
| task-2 | `BANANA` | x3-local/flash-next-sub:high |
| task-3 | `CHERRY` | x3-local/flash-next-sub:high |

No model was passed on any child; all three inherited the parent's model.

They ran at the same time: all three started within ~30 ms of each other (t=588116/588132/588143) and finished at staggered times (CHERRY 594.2s→, BANANA, APPLE last at 604.1s) — overlapping execution, not sequential. Total wall time ~16 s.


```

## A–D proof test

| Phase | Elapsed | Needles | HTTP | finish_reason | Peak GTT GiB | Min MemAvail GiB | Peak queued | Peak longest_wait_s | Peak busy_regions | Restarted | tok/s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 15.3s | 4/4 | [200, 200, 200, 200] | ['stop', 'stop', 'stop', 'stop'] | 27.04 | 90.97 | 0 | 0 | 4 | False | prefill 894.5 / decode 11.7 |
| B | 186.6s | 4/4 | [200, 200, 200, 200] | ['stop', 'stop', 'stop', 'stop'] | 27.04 | 90.79 | 0 | 0 | 2 | False | prefill 940.2 / decode 21.8 |
| C | 582.9s | 4/4 | [200, 200, 200, 200] | ['stop', 'stop', 'stop', 'stop'] | 27.04 | 90.79 | 0 | 0 | 2 | False | prefill 878.5 / decode 21.3 |
| D | 149.8s | 4/4 | [200, 200, 200, 200] | ['stop', 'stop', 'stop', 'stop'] | 27.04 | 91.13 | 0 | 0 | 4 | False | prefill 1209.4 / decode 12.4 |

**Overall: PASS** (VERIFIED on the X3). llama-swap MainPID 99654 and NRestarts 0 throughout; flash-next container PID unchanged in every phase; peak GTT 27.04 GiB (within ~2 GiB of the 27 GiB reserved pool); MemAvailable stayed above 90 GiB; no 503, no silent truncation (`finish_reason=stop` on all 16 streams); no Halogen engine flags changed.

Notes on the table:
- The averaged prefill/decode tok/s in the table mix waiting time into the first-token clock. Engine-reported prefill on the first request of each wave is the real rate: A 1744, B 1827, C 1700, D child 1931 / parent 1697 tok/s. Last-in-wave decode was about 28–74 tok/s.
- Phase C overcommit: `/health` `queued` stayed 0, but 4 requests were `in_flight` at the start and only 2 were in the KV pool at a time (`busy_regions` peak 2). Prefill was serialized (~145 s apart). The engine logged `kv pool: no room for 251136 positions; forgot the region` while dropping LRU *cache* entries (not live requests) to admit the next 243k prompt. Pool peaked at 522752/524288 (100%). All 4 then completed with needle hits. No 503 (queue timeout is 3600 s; none waited that long).
- Phase D: 200k parent plus three 16k children all admitted (`busy_regions` 4). The pool was already ~96% from C's residual cache, so the engine again dropped LRU cache regions; all 4 needles hit.
- A SIGHUP config reload right after the alias edit raced a warmup request (HTTP 500, "upstream command exited prematurely"). A second load 33 s later brought official flash-next back (GTT 27.01 GiB). llama-swap was not restarted.

## Quick check (plain)
One Forge `pi` run from `~/AI/forge` spawned three worker subagents in one parallel fan-out. They all used `x3-local/flash-next-sub` (the new default; `:high` is a thinking-level suffix, not a model swap), returned APPLE / BANANA / CHERRY, started within ~30 ms of each other, and overlapped (journal shows three `/v1/chat/completions` POSTs at 19:29:49.402). No other exclusive-group model was started. Wall time ~16 s. Render's Heretic subagent setting was not changed.

Per-phase details (no prompt text):
### A
- A1: http=200 finish=stop hit=True fact=U29-5ZJ74TDD ttft=8.19356107711792 total_s=12.3 toks={'prompt_tokens': 4685, 'completion_tokens': 39, 'prefill_tok_s': 571.8, 'decode_tok_s': 9.5} err=None answer_head='U29-5ZJ74TDD'
- A2: http=200 finish=stop hit=True fact=U29-JQX39BTZ ttft=5.426023721694946 total_s=12.2 toks={'prompt_tokens': 4683, 'completion_tokens': 38, 'prefill_tok_s': 863.1, 'decode_tok_s': 5.6} err=None answer_head='U29-JQX39BTZ'
- A3: http=200 finish=stop hit=True fact=U29-A9AV3ZYD ttft=2.726356267929077 total_s=11.9 toks={'prompt_tokens': 4681, 'completion_tokens': 37, 'prefill_tok_s': 1716.9, 'decode_tok_s': 4.0} err=None answer_head='U29-A9AV3ZYD'
- A4: http=200 finish=stop hit=True fact=U29-GWJBV4W4 ttft=10.985711574554443 total_s=12.4 toks={'prompt_tokens': 4684, 'completion_tokens': 38, 'prefill_tok_s': 426.4, 'decode_tok_s': 27.5} err=None answer_head='U29-GWJBV4W4'
- Interesting engine log lines: 5
  - `serve_api: mtp 199 tok in 2.79s = 71.26 t/s | 61 rounds, commit 3.25/round | prompt 21988 (21969 cached, 99.9%), prefill 0.10s (19 new) | detok 20us/tok | pool 96000/524288 18% | think off`
  - `serve_api: mtp 37 tok in 9.20s = 4.02 t/s | prompt 4681, prefill 2.68s = 1744 t/s | detok 41us/tok | 36 tok with the head off | pool 116480/524288 22% | think on, closed at 1 by answer room | closest earlier: 3 tokens shared with a request `
  - `serve_api: mtp 38 tok in 6.76s = 5.62 t/s | 1 rounds, commit 2.00/round | prompt 4683, prefill 2.67s = 1754 t/s | detok 19us/tok | 36 tok with the head off | pool 116480/524288 22% | think on, closed at 1 by answer room | closest earlier: 3`
  - `serve_api: mtp 39 tok in 4.10s = 9.51 t/s | 3 rounds, commit 2.67/round | prompt 4685, prefill 2.73s = 1714 t/s | detok 17us/tok | 31 tok with the head off | pool 116480/524288 22% | think on, closed at 1 by answer room | closest earlier: 3`
  - `serve_api: mtp 38 tok in 1.38s = 27.57 t/s | 4 rounds, commit 2.75/round | prompt 4684, prefill 2.75s = 1702 t/s | detok 14us/tok | 26 tok with the head off | pool 116480/524288 22% | think on, closed at 1 by answer room | closest earlier: `
- Full samples: `~/u29-parallel/A.json`
### B
- B1: http=200 finish=stop hit=True fact=U29-9ZUQJKUV ttft=90.33390593528748 total_s=109.0 toks={'prompt_tokens': 81131, 'completion_tokens': 91, 'prefill_tok_s': 898.1, 'decode_tok_s': 4.9} err=None answer_head='U29-9ZUQJKUV'
- B2: http=200 finish=stop hit=True fact=U29-ZYA5HPHJ ttft=44.518579721450806 total_s=62.2 toks={'prompt_tokens': 81132, 'completion_tokens': 89, 'prefill_tok_s': 1822.4, 'decode_tok_s': 5.0} err=None answer_head='U29-ZYA5HPHJ'
- B3: http=200 finish=stop hit=True fact=U29-BAZ2HMNF ttft=136.29600977897644 total_s=155.0 toks={'prompt_tokens': 81131, 'completion_tokens': 89, 'prefill_tok_s': 595.3, 'decode_tok_s': 4.8} err=None answer_head='U29-BAZ2HMNF'
- B4: http=200 finish=stop hit=True fact=U29-5UBL4UX4 ttft=182.27394270896912 total_s=183.5 toks={'prompt_tokens': 81131, 'completion_tokens': 86, 'prefill_tok_s': 445.1, 'decode_tok_s': 72.6} err=None answer_head='U29-5UBL4UX4'
- Interesting engine log lines: 4
  - `serve_api: mtp 89 tok in 17.62s = 5.05 t/s | 24 rounds, commit 3.71/round | prompt 81132, prefill 44.40s = 1827 t/s | detok 29us/tok | pool 282368/524288 54% | think on | closest earlier: 7 tokens shared with a request 5s ago, then its prom`
  - `serve_api: mtp 91 tok in 18.65s = 4.88 t/s | 26 rounds, commit 3.50/round | prompt 81131, prefill 45.73s = 1774 t/s | detok 28us/tok | pool 365568/524288 70% | think on | closest earlier: 7 tokens shared with a request 5s ago, then its prom`
  - `serve_api: mtp 89 tok in 18.65s = 4.77 t/s | 26 rounds, commit 3.42/round | prompt 81131, prefill 45.83s = 1770 t/s | detok 27us/tok | pld 1 rounds, 1.00 acc/round | pool 421632/524288 80% | think on | closest earlier: 7 tokens shared with `
  - `serve_api: mtp 86 tok in 1.17s = 73.28 t/s | 25 rounds, commit 3.44/round | prompt 81131, prefill 45.84s = 1770 t/s | detok 17us/tok | pld 1 rounds, 3.00 acc/round | pool 421632/524288 80% | think on | closest earlier: 7 tokens shared with `
- Full samples: `~/u29-parallel/B.json`
### C
- C1: http=200 finish=stop hit=True fact=U29-WCQTWEYU ttft=433.57568359375 total_s=452.4 toks={'prompt_tokens': 242916, 'completion_tokens': 87, 'prefill_tok_s': 560.3, 'decode_tok_s': 4.6} err=None answer_head='U29-WCQTWEYU'
- C2: http=200 finish=stop hit=True fact=U29-42HYTPHK ttft=143.5514075756073 total_s=164.8 toks={'prompt_tokens': 242920, 'completion_tokens': 87, 'prefill_tok_s': 1692.2, 'decode_tok_s': 4.1} err=None answer_head='U29-42HYTPHK'
- C3: http=200 finish=stop hit=True fact=U29-8M54PHJW ttft=288.60930132865906 total_s=309.2 toks={'prompt_tokens': 242923, 'completion_tokens': 91, 'prefill_tok_s': 841.7, 'decode_tok_s': 4.4} err=None answer_head='U29-8M54PHJW'
- C4: http=200 finish=stop hit=True fact=U29-UBCNC2T3 ttft=578.5795586109161 total_s=579.8 toks={'prompt_tokens': 242921, 'completion_tokens': 87, 'prefill_tok_s': 419.9, 'decode_tok_s': 72.2} err=None answer_head='U29-UBCNC2T3'
- Interesting engine log lines: 12
  - `kv pool: no room for 251136 positions; forgot the region at 51968 (1 cache entries, 0 chunks; the least recently used of 4 in the way)`
  - `kv pool: no room for 251136 positions; forgot the region at 92672 (3 cache entries, 0 chunks; the least recently used of 3 in the way)`
  - `kv pool: no room for 251136 positions; forgot the region at 147456 (3 cache entries, 0 chunks; the least recently used of 2 in the way)`
  - `kv pool: no room for 251136 positions; forgot the region at 230656 (3 cache entries, 0 chunks; the least recently used of 1 in the way)`
  - `kv pool: no room for 251136 positions; forgot the region at 313856 (3 cache entries, 0 chunks; the least recently used of 2 in the way)`
  - `kv pool: no room for 251136 positions; forgot the region at 397056 (3 cache entries, 0 chunks; the least recently used of 1 in the way)`
  - `serve_api: mtp 87 tok in 21.25s = 4.09 t/s | 29 rounds, commit 3.00/round | prompt 242920, prefill 142.92s = 1700 t/s | detok 33us/tok | pld 1 rounds, 2.00 acc/round | pool 522752/524288 100% | think on | closest earlier: 7 tokens shared wi`
  - `kv pool: no room for 251136 positions; forgot the region at 20992 (3 cache entries, 0 chunks; the least recently used of 1 in the way)`
  - `serve_api: mtp 91 tok in 20.52s = 4.43 t/s | 28 rounds, commit 3.25/round | prompt 242923, prefill 144.85s = 1677 t/s | detok 28us/tok | pool 522752/524288 100% | think on | closest earlier: 7 tokens shared with a request 193s ago, then its`
  - `kv pool: no room for 251136 positions; forgot the region at 272128 (3 cache entries, 0 chunks; the least recently used of 1 in the way)`
  - `serve_api: mtp 87 tok in 18.79s = 4.63 t/s | 26 rounds, commit 3.35/round | prompt 242916, prefill 144.78s = 1678 t/s | detok 32us/tok | pld 1 rounds, 3.00 acc/round | pool 522752/524288 100% | think on | closest earlier: 7 tokens shared wi`
  - `serve_api: mtp 87 tok in 1.18s = 73.66 t/s | 24 rounds, commit 3.62/round | prompt 242921, prefill 144.82s = 1677 t/s | detok 19us/tok | pool 522752/524288 100% | think on | closest earlier: 7 tokens shared with a request 193s ago, then its`
- Full samples: `~/u29-parallel/C.json`
### D
- Dparent: http=200 finish=stop hit=True fact=U29-FVBMN8EM ttft=146.64271092414856 total_s=147.5 toks={'prompt_tokens': 202776, 'completion_tokens': 37, 'prefill_tok_s': 1382.8, 'decode_tok_s': 44.6} err=None answer_head='U29-FVBMN8EM'
- Dchild1: http=200 finish=stop hit=True fact=U29-35YLLSJM ttft=17.80270481109619 total_s=43.8 toks={'prompt_tokens': 16549, 'completion_tokens': 38, 'prefill_tok_s': 929.6, 'decode_tok_s': 1.5} err=None answer_head='U29-35YLLSJM'
- Dchild2: http=200 finish=stop hit=True fact=U29-GPYT682F ttft=8.648586988449097 total_s=33.3 toks={'prompt_tokens': 16548, 'completion_tokens': 38, 'prefill_tok_s': 1913.4, 'decode_tok_s': 1.5} err=None answer_head='U29-GPYT682F'
- Dchild3: http=200 finish=stop hit=True fact=U29-F3N43LLN ttft=27.046398162841797 total_s=47.2 toks={'prompt_tokens': 16549, 'completion_tokens': 38, 'prefill_tok_s': 611.9, 'decode_tok_s': 1.9} err=None answer_head='U29-F3N43LLN'
- Interesting engine log lines: 9
  - `kv pool: no room for 16896 positions; forgot the region at 512 (3 cache entries, 0 chunks; the least recently used of 4 in the way)`
  - `kv pool: no room for 16896 positions; forgot the region at 5632 (3 cache entries, 0 chunks; the least recently used of 3 in the way)`
  - `kv pool: no room for 16896 positions; forgot the region at 10752 (3 cache entries, 0 chunks; the least recently used of 2 in the way)`
  - `kv pool: no room for 16896 positions; forgot the region at 15872 (3 cache entries, 0 chunks; the least recently used of 1 in the way)`
  - `kv pool: no room for 16896 positions; forgot the region at 20992 (4 cache entries, 0 chunks; the least recently used of 1 in the way)`
  - `serve_api: mtp 38 tok in 24.65s = 1.54 t/s | prompt 16548, prefill 8.57s = 1931 t/s | detok 45us/tok | 37 tok with the head off | pool 505088/524288 96% | think on, closed at 1 by answer room | closest earlier: 7 tokens shared with a reques`
  - `serve_api: mtp 38 tok in 25.95s = 1.46 t/s | prompt 16549, prefill 9.11s = 1817 t/s | detok 29us/tok | 37 tok with the head off | pool 505088/524288 96% | think on, closed at 1 by answer room | closest earlier: 7 tokens shared with a reques`
  - `serve_api: mtp 38 tok in 20.15s = 1.89 t/s | 2 rounds, commit 6.00/round | prompt 16549, prefill 9.20s = 1799 t/s | detok 26us/tok | 26 tok with the head off | pool 505088/524288 96% | think on, closed at 1 by answer room | closest earlier:`
  - `serve_api: mtp 37 tok in 0.81s = 45.63 t/s | 2 rounds, commit 5.50/round | prompt 202776, prefill 119.48s = 1697 t/s | detok 24us/tok | 26 tok with the head off | pool 505088/524288 96% | think on, closed at 1 by answer room | closest earli`
- Full samples: `~/u29-parallel/D.json`

Lease released: 2026-11-15 7:50 PM CT (America/Chicago). Raw samples stay in `~/u29-parallel/` (mode 0700); the hdr file was removed after the run. models.json was not committed (it holds an API key).
