# PLAN-v3.2 Phase 0 Result (P0.0 Complete; Waiting on Derrick **Y** for P0.1–P0.4)

- **Date:** 2026-11-18 14:14 CST
- **Branch / Base commit:** `evo-x3` branch `u58` (`50e84a8`)
- **X3 Lease (`/home/derekboone/AI/locks/x3-lease.txt`):** `0` bytes (read-only checks + staged scripts/records only; no live restarts or config edits run)
- **Status:** `P0.0` **PASS**; stopped at **`P0.1 Y`–`P0.4 Y`** awaiting Derrick's approval.

---

## 1. P0.0 Snapshot, In-Flight State, and Readiness Checks

### 1.1 Live `llama-swap` and Resident Model (`BRIEF.md` v2 cutover state)
- `llama-swap.service`: `active (running)` since `2026-11-18 13:49:44 CST` (`Main PID: 1844542`).
- Resident model in `/running` (`HTTP 200`): `flash-next-uncensored-v2` (`state: "ready"`, `ttl: 0`), served by `ghcr.io/peonist-ai/halogen-flash-server@sha256:773073448dc9ff4a8c6b6c278802e254fd5f1546764e27531aeb3b77cb13482e` (`0.20.7`), weights `/srv/models/flash-next-uncensored-v2-hgn` (`johnlockejrr/Huihui-Qwen3.8-Flash-Next-abliterated-v2-HGN`).
- Halogen `127.0.0.1:8081/health`: `status: "ok"`, `version: {"api": "0.20.7", "engine": "0.20.7", "match": true}`, `vision.enabled: true`, `slots: 4`, `slot_ctx: 262144`, `kv_pool_positions: 524288`, `drafter_default: "mtp"`, `drafter_weights_loaded: true`, `chat_template.probe: "passed"`.
- `verify-serve.sh` (`https://evo-x3-1.tailf242b2.ts.net/v1/models`):
  - `no key: 401`
  - `LLM_KEY_BOX: 200`
- Live `/etc/evo-x3/llama-swap.yaml` and repo `config/llama-swap.yaml` match byte-for-byte (`sha256: b11edc691be44ef0137a144ef4b5cd9710ee771a3f9ddbb7d991fffb69840e85`).
- Memory & GTT baseline (while `flash-next-uncensored-v2` is resident):
  - `MemTotal: 130476452 kB`
  - `MemFree: 5212504 kB`
  - `MemAvailable: 23398000 kB` (~22.3 GiB)
  - `Mlocked: 66001200 kB` (~62.9 GiB)
  - `/sys/class/drm/card1/device/mem_info_gtt_total: 128849018880` (120.0 GiB)
  - `/sys/class/drm/card1/device/mem_info_gtt_used: 29824745472` (~27.78 GiB)
  - `/sys/class/drm/card1/device/mem_info_vram_total: 1073741824` (1.0 GiB)
  - `/sys/class/drm/card1/device/mem_info_vram_used: 163053568` (~155.5 MiB)
- Disk free (`/dev/mapper/fedora-root` mounted on `/`): `1.7T` size, `1.1T` used, `600G` available (`64%`).

### 1.2 In-Flight Loop Steps, U58 Phases, Tagger, and Queued Render (`P0.0`)
- **Tagger:** `u42-pixlstash-tagger.service` and `u42-pixlstash-tagger.timer` are both `inactive` (disabled since Nov 17).
- **Render `c6c416c5` (`BRIEF.md`):** Completed cleanly on AlienPC ComfyUI before any Phase 0 work touched the X3:
  - `/home/evo/AI/community/runs/sydney_hesitant_stand/_render_queue.log`: `2026-11-18T14:01:09-06:00 DONE pos=1 tag=clip ok 768x1344 192f audio yes ... bytes=2527471 retry=False`, `BATCH closed rc=0 ... comfyui_auto unloaded, lock released`.
  - `/home/evo/AI/community/runs/sydney_hesitant_stand/_run_queue.out.log`: `2026-11-18 14:01:09 CT gpu_lock release rc=0 released`.
- **Panes (`herdr pane list` as `evo`):**
  - `w3:p1` (`render`, `/home/evo/AI/render`): `agent_status: "idle"` (`flash-next-uncensored-v2 • low`, footer `28.4%/262k`).
  - `w4:p1` (`forge`, `/home/evo/AI/forge`): `agent_status: "idle"` (`(x3-local-coding) flash-next-uncensored-v2 • medium`, footer `0.0%/262k`).
- **Loop steps & U58 status (from commits `32a46c0`, `4ab1d15`, `50e84a8`, `u58-chat-read-plan` `44bc639` and live file inspection):**
  - **Completed on live X3:**
    - `loop-guard.ts` and `auto-continue.ts` (including `EN_DEFER` and 400-char threshold) are present in `/home/evo/AI/render/.pi/extensions/` and `auto-continue.ts` + `loop-guard.ts` are present in `/home/evo/AI/forge/.pi/extensions/`.
    - Render and Forge default models switched to `flash-next-uncensored-v2` (Render `--thinking low`, Forge `--thinking medium`, `thinkingBudgets` `{minimal: 1024, low: 2048, medium: 4096, high: 8192}` in `/home/evo/AI/forge/.pi/settings.json`).
    - Live `/home/evo/.pi/agent/settings.json`, `/home/evo/AI/forge/.pi/settings.json`, `/home/evo/.pi/panes/forge/settings.json`, and `/home/evo/.pi/panes/render/settings.json` have `compaction.modelOverrides` (`reserveTokens: 32768`, `keepRecentTokens: 20000` for main models; `16384` / `20000` for `-sub`), and pane `settings.json` files set `sessionDir: "/home/evo/.pi/agent/sessions"`.
  - **Still open / drift to handle in Phase 1 (P1.10 / U58):**
    - Live `/home/evo/.pi/agent/models.json` (and `config/pi-evo/models.json.example`) still sets `contextWindow: 262144` on main resident-slot entries (`flash-next`, `flash-next-uncensored`, `flash-next-uncensored-v2`, `gemma4-heretic`, `gemma4-heretic-sub`) rather than `131072`.
    - Tracked `config/pi-evo/forge-project-settings.json` still differs from live `/home/evo/AI/forge/.pi/settings.json` (`thinkingBudgets` `8192/16384` and `compaction.reserveTokens: 131072` vs live `modelOverrides`).
    - U58's synthetic compaction gate test (confirming one compaction entry near ~98K on the 131K window) is not yet recorded as passed.
    - No active background `agy` run on loopfix (`agy-hydrogen` tmux session has only the finished `21d6520f` v2 cutover process).

### 1.3 Weights & Benchmark Fixtures Verified on Disk
- **Resident Halogen v2 HGN:** `/srv/models/flash-next-uncensored-v2-hgn` (present, live).
- **Huihui v2 GGUF (`P0.3` candidate):** `/srv/models/flash-next-uncensored-huihui-v2` was deleted per `BRIEF.md`, **but** the 4 sha256-verified shards of `huihui-ai/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba` (`104 GiB`, `sha_exit=0` in `sha256.check`) remain at `/srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/` (`Qwen3.8-Flash-Next-UD-Q4_K_XL-00001-of-00004.gguf` .. `00004`).
- **Shared MTP GGUF (`P0.3`):** `/srv/models/flash-next/mtp-Qwen3.8-Flash-Next-shared-Q8_0.gguf` (`2.6G`).
- **Existing C2/C3/C4/C6 fixtures in `~/evo-x3`:**
  - C2: `u34/pool_test.py` (currently targets `"model": "flash-next"`, 2x200K + 2x32K; for 131K / gufo 2x131K planned session counts it needs parameterization).
  - C3: `bakeoff/u26/refusal_key.py`.
  - C4: `records/gufo-phase1-20261117/bench_auth.py` (`--tasks tool`) + a 2-request `tool_choice: "none"` check.
  - C5: `deepu105/quant-bench` is **not** cloned on disk yet (existing coding fixtures are `bakeoff/u26/forge_task.py` and `bench_auth.py --tasks code`).
  - C6: `bakeoff/bench/vision_bench.py` + `bakeoff/bench/vision-test.png`.

---

## 2. Phase 0 Deliverable Created

- **`/home/derekboone/evo-x3/scripts/apply-llama-swap.sh`** (`0755`):
  - Validates YAML syntax, checks for duplicate model/alias IDs across `models` and `filters.setParamsByID`, verifies `hooks.on_startup.preload` targets exist, and runs `/usr/local/bin/llama-swap -config <candidate> -validate` with `/etc/evo-x3/llm.env` sourced in a root subshell.
  - Requires an active lease in `/home/derekboone/AI/locks/x3-lease.txt` for live apply.
  - Backs up `/etc/evo-x3/llama-swap.yaml` to `/etc/evo-x3/_archive/llama-swap.yaml.bak-YYYYMMDD-HHMMSS`, installs candidate (`0644 root:root`), restarts `llama-swap.service`, and polls up to `180s` (`NRestarts == 0`, `http://127.0.0.1:8080/health == 200`, preloaded model(s) `state == "ready"` in `/running`, and `verify-serve.sh` returning `no key: 401` and `LLM_KEY_BOX: 200`).
  - Auto-restores the backup and restarts `llama-swap` on any failure.
  - **Checks run after final edit:**
    - `bash -n /home/derekboone/evo-x3/scripts/apply-llama-swap.sh` -> exit `0`
    - `/home/derekboone/evo-x3/scripts/apply-llama-swap.sh --validate-only /home/derekboone/evo-x3/config/llama-swap.yaml` -> exit `0`, `YAML and unique-alias check passed. Preload models: flash-next-uncensored-v2`, `config is valid: 7 model(s), 0 peer(s)`.

---

## 3. Open Questions Requiring Derrick's **Y** (Stop Before P0.1–P0.4)

1. **`P0.1 Y` & `P0.2 Y` (Live Halogen 0.20.7 + Huihui v2 HGN checks, no restart):**
   - `BRIEF.md` notes the v2 HGN cutover (`flash-next-uncensored-v2`) is already live and the v1 HGN folder is deleted, so `P0.1` and `P0.2` converge onto testing the live `flash-next-uncensored-v2` slot without restarting `llama-swap`.
   - **Question:** May we run C2–C6 on the live `flash-next-uncensored-v2` slot now (`P0.1`/`P0.2`), and for **C5** (`deepu105/quant-bench`, 11 Aider polyglot tasks), should we clone `deepu105/quant-bench` onto the X3 (~small repo) to run those 11 tasks or substitute the existing `bakeoff/u26/forge_task.py` + `bench_auth.py` coding checks?

2. **`P0.3 Y` (gufo 0.35.0 + Huihui v2 GGUF candidate test):**
   - Even though `/srv/models/flash-next-uncensored-huihui-v2` was deleted, all 4 sha256-verified shards (`104 GiB`) of `huihui-ai/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba` are still on disk in `/srv/bakeoff/Huihui-Qwen3.8-Flash-Next-abliterated-v2-GGUF@cbc7fba/`.
   - **Question:** Do you want us to run `P0.3` (`gufo-runtime:0.35.0` image pull + `907 MB` `mmproj-Qwen3.8-Flash-Next-BF16.gguf` download + temporary resident-slot swap via `apply-llama-swap.sh` for C1–C6, then restore Halogen v2 HGN), or skip `P0.3` and proceed to `G0` with Halogen 0.20.7 + Huihui v2 HGN?

3. **`P0.4 Y` (Memory co-residency check):**
   - Live `MemAvailable` with `flash-next-uncensored-v2` alone is `~22.3 GiB`.
   - **Question:** May we run `P0.4` on the `G0` winner (`embed-small` load + `MemAvailable` check, followed by one `joycaption` request only if `MemAvailable` meets the `>= 13.5 GiB` floor, plus `+2.5 GB` / `+6.5 GB` if Halogen NPU models in P4.10 are planned)?
