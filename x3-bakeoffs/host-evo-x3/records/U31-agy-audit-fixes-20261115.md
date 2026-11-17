# U31 — Antigravity Audit Fixes Record (2026-11-15)

- **Brief:** `/home/derekboone/evo-x3/records/U31-agy-brief.md`
- **Audit reviewed:** `/home/derekboone/evo-x3/records/agy-redteam-review-20261115.md`
- **Authority:** Derrick t1819u ("Ok continue address and fix") and card answer ("Yes, hand the audit fixes to the Antigravity Orchestrator", post-t1821u)
- **Runner:** Google Antigravity Orchestrator (Argon) + Execution model (with verification of the prior stopped Max job's ~19:39–19:49 CT edits)
- **Session start (America/Chicago):** `2026-11-15 19:55:17 CST (-06:00)` (implementation execution started `20:06:45 CST`)
- **Session end (America/Chicago):** `2026-11-15 20:12:33 CST (-06:00)` (verified final health after write)
- **Secret scan note:** `gitleaks` unavailable on host; all git and etckeeper diffs manually audited prior to commit (zero secrets staged or committed; `~/.pi/agent/models.json` not committed).

---

## Stopped Max Job (~19:39–19:49 CT): Verified vs Finished in U31

| File / Area | Stopped Job State | U31 Action |
|---|---|---|
| `~/.pi/agent/pi-permissions.jsonc` (`MF-03`) | `5slock` path rules removed, `forge/ralph-community/*.sh` + `logs/*` `edit`/`write` denies and bash write-guards added | **Verified** (`ralph.sh` executable and `bash -n` OK; no `5slock` allow/deny rules left) |
| `/etc/evo-x3/llama-swap.yaml` (`MF-08`, `SF-03`, `gemma4-heretic-sub`) | `flash-next-gufo` `--name llama-swap-flash-next-gufo`, `--no-slots` removed from `gemma4-heretic`, `aliases: ["gemma4-heretic-sub"]` + `useModelName: "gemma4-heretic"` added, uncommitted in etckeeper | **Verified** all 6 slot Podman `--name` values unique, `-np 2` / `concurrencyLimit: 2` intact, and **committed in etckeeper (`9a3b135`)** |
| `/home/derekboone/.pi/agent/models.json` | Added `gemma4-heretic-sub` (`reasoning: false`, `maxTokens: 4096`) | **Verified** metadata via Python (no keys printed); left uncommitted per rule |
| `~/AI/render/AGENTS.md`, `x3/render-pi.sh`, `x3/README-X3.md` (`MF-15`, `MF-06`) | Committed as `c0d356d` in `~/AI/render` (`x3-linux`) | **Verified** commit `c0d356d` and all 5 extension paths; **finished** `README-X3.md` sync for `subagents` and U27/U29 `flash-next` concurrency (`513fd09`) |
| `~/AI/render/.pi/settings.json` + Render subagent test | `subagents.defaultModel` set to `x3-local/gemma4-heretic-sub`, but first test ran `worker` with `:high` thinking (`used_sub_alias: false`, acceptance rejected) | **Finished**: added `"disableThinking": true` and `"defaultThinking": "off"` in `settings.json`, **reran test** (`scout` resolved `x3-local/gemma4-heretic-sub` with `thinkingLevel: "off"`, `live_heretic_slots: 2`, `rc: 0`), committed (`513fd09`) |
| `~/AI/render/.pi/extensions/loop-guard.ts` + `loop-guard-test.mjs` (`SF-01`) | Modified & untracked test in `~/AI/render`, uncommitted | **Finished**: added `BOOL_FLAGS` handling in `runDirFromCmd` so boolean flags (`--continued`, `--s3-in-frame`, etc.) never swallow `<run_dir>`, added test #8, verified `loop-guard unit tests OK 8`, committed (`513fd09`) |
| `/etc/containers/systemd/open-webui.container` (`MF-11`) | `ENABLE_SIGNUP=false` edited at 19:43 CT, running container still pre-edit, uncommitted in etckeeper | **Finished**: confirmed idle (`0` requests in prior 5 min), ran `systemctl daemon-reload && systemctl restart open-webui.service`, verified `ENABLE_SIGNUP=false` live and `/api/config` `"enable_signup":false`, **committed in etckeeper (`9a3b135`)** |
| `~/evo-x3/bakeoff/RESULTS.md` (`MF-14`, `SF-09`) | Updated 19:42 CT with 7:45 PM status block | **Verified** 7:45 PM status update on disk (`qwen27b` co-resident math retracted, U6 3/3 262K recorded, Halogen path noted) |
| `~/AI/community/agent-shared/AGENTS.md` + parody test `skipif` (`SF-09`) | Committed as `98c0bc4` and `faa32e8` (`x3-linux`), `notes/actions.log` uncommitted | **Verified** commits + ran `pytest` on parody tests (`526 passed, 6 skipped in 3.43s`) |

---

## Per-Item Status (`agy-redteam-review-20261115.md`)

### Must-Fix Items

| ID | Status | Summary & Verification | Backups |
|---|---|---|---|
| **MF-01** | **fixed (finished in U31, verified)** | Reconciled documentation drift (`~/AI/render/x3/README-X3.md` updated for U27/U29 `concurrencyLimit: 4`, `flash-next-sub`, `gemma4-heretic-sub`, and `pi-subagents` reading `~/AI/render/.pi/settings.json`; `RESULTS.md` 7:45 PM CT status block verified). | `~/AI/render/x3/README-X3.md.bak-20261115-200719`, `~/evo-x3/bakeoff/RESULTS.md.bak-20261115-194227` |
| **MF-02** | **fixed (pre-applied, verified)** | `flash-next` (`concurrencyLimit: 4`, `flash-next-sub` alias) and `gemma4-heretic` (`-np 2`, `concurrencyLimit: 2`, `gemma4-heretic-sub` alias) are synchronized with `forge/.pi/settings.json` (`x3-local/flash-next-sub`), `render/.pi/settings.json` (`x3-local/gemma4-heretic-sub`), and `subagent/config.json`. Verified by U29 A–D parallel test and U31 Render subagent rerun. | `/etc/evo-x3/llama-swap.yaml.bak-20261115-192840-pre-u29`, `.../194720-pre-u31-yaml`, `.../194731-pre-u31-yaml` |
| **MF-03** | **fixed (pre-applied, verified)** | `~/.pi/agent/pi-permissions.jsonc` dropped leftover AlienPc `5slock` allow/deny rules (only explanatory comment on line 222 remains), added `edit`/`write` denies for `/home/derekboone/AI/forge/ralph-community/*.sh` and `/home/derekboone/AI/forge/ralph-community/logs/*` at lines 224–227, and added bash write-guards at lines 292–303. Verified `bash -n /home/derekboone/AI/forge/ralph-community/ralph.sh` passes and execution remains permitted (`-rwxr-xr-x`). | `/home/derekboone/.pi/agent/pi-permissions.jsonc.bak-20261115-193958` |
| **MF-04** | **skipped (Derrick's deny-list decision)** | Brief explicitly rules out adding approval prompts or loosening `fix_plan.md` / `progress.md` denies in a way that conflicts with Derrick's deny-list policy. Note from live verification: `community/fix_plan.md` and `community/progress.md` do not exist on X3; Forge's active loop uses `/home/derekboone/AI/forge/ralph-community/{PROMPT.md,fix_plan.md,notes/progress.md}`, which remain writable under `/home/derekboone/AI/*` while `/home/derekboone/AI/community/{PROMPT.md,fix_plan.md,progress.md}` stay denied. | None |
| **MF-05** | **fixed (pre-applied, verified)** | `~/.pi/agent/extensions/subagent/config.json` already updated in U29 (`globalConcurrencyLimit: 4`, `parallel.concurrency: 3`, `maxActiveAsyncRunsPerSession: 4`, `maxSubagentDepth: 1`). Verified against `llama-swap` `flash-next` (`concurrencyLimit: 4`). | `/home/derekboone/.pi/agent/extensions/subagent/config.json.bak-20261115-192840-pre-u29` |
| **MF-06** | **fixed (finished in U31, verified)** | Pre-applied commit `c0d356d` keeps `--no-extensions` intentionally (excluding `plannotator`, `pi-canvas`, `pi-say`, `compound-engineering`) and passes the 5 intended extensions via `-e` (`pi-permission-system`, `cc-safety-net`, `loop-guard`, `pi-subagents`, `pi-memory`). Verified all 5 paths exist, `pi-subagents` + `pi-permission-system` loaded and enforced policies during the U31 rerun, and `README-X3.md` was updated to document `pi-subagents` reading `subagents` from `~/AI/render/.pi/settings.json`. | `~/AI/render/x3/render-pi.sh.bak-20261115-193958`, `~/AI/render/x3/README-X3.md.bak-20261115-200719` |
| **MF-07** | **skipped (Derrick's decision)** | No `pi-model-swap` guard per brief ("no pi-model-swap guard") and `U27` findings. | None |
| **MF-08** | **fixed (pre-applied, verified & committed)** | `/etc/evo-x3/llama-swap.yaml` `flash-next-gufo` slot uses `--name llama-swap-flash-next-gufo`; all 6 slots use distinct Podman `--name` values (`llama-swap-flash-next`, `llama-swap-flash-next-uncensored`, `llama-swap-flash-next-gufo`, `llama-swap-gemma4-heretic`, `llama-swap-qwen27b`, `llama-swap-embed-small`). Committed via `etckeeper` (`9a3b135`). | `/etc/evo-x3/llama-swap.yaml.bak-20261115-194720-pre-u31-yaml`, `.../194731-pre-u31-yaml` |
| **MF-09** | **skipped (already done / U29 proved)** | Heretic already rolled back to `-np 2` / `concurrencyLimit: 2` after U27 np4 crash (not raised to 4). Halogen `flash-next` (`concurrencyLimit: 4`, `262K`) already tested in U29 A–D parallel proof test (16/16 streams `finish=stop`, peak GTT 27.04 GiB, 0 crashes). | `/etc/evo-x3/llama-swap.yaml.bak-20261115-190727-heretic-np4-crash` |
| **MF-10** | **fixed (pre-applied, verified)** | Gate 0 equivalents already executed via U6 3-run 262K protocol (`~/u6-262k/`, 3/3 pass, 18:41 CT) and U29 A–D 4-slot parallel proof (`~/u29-parallel/`, 16/16 pass). Chat cutover remains held pending Derrick's explicit approval (`README-X3.md`). | None |
| **MF-11** | **fixed (finished in U31, verified & committed)** | Pre-applied `ENABLE_SIGNUP=false` in `/etc/containers/systemd/open-webui.container`; verified existing container had 1 user (`role='admin'`, `count_user=1`, `count_auth=1`) and had 0 requests in prior 5 min; ran `systemctl daemon-reload && systemctl restart open-webui.service`; verified `ENABLE_SIGNUP=false` in `podman inspect` env, `http://127.0.0.1:3000/health` `{"status":true}`, and `http://127.0.0.1:3000/api/config` `"enable_signup":false, "auth":true`. Committed via `etckeeper` (`9a3b135`). | `/etc/containers/systemd/open-webui.container.bak-20261115-194300` |
| **MF-12** | **skipped (already done in U30)** | Already resolved in U30 (`open-webui.container` bypasses `start.sh` via `Exec=`, `WEBUI_SECRET_KEY` rotated in `openwebui.env` `0600`). Not redone. | `/etc/containers/systemd/open-webui.container.bak-20261115-191504` |
| **MF-13** | **skipped (Derrick's policy decision)** | Brief forbids approval-prompt / sandbox rewrites conflicting with "no approval prompts; keep the deny list". | None |
| **MF-14** | **fixed (pre-applied, verified)** | `~/evo-x3/bakeoff/RESULTS.md` 7:45 PM CT status block explicitly retracts `qwen27b` as an always-resident helper following U25 UD-Q8_K_XL upgrade (notes only a small 3B–8B model fits safely beside Heretic). | `~/evo-x3/bakeoff/RESULTS.md.bak-20261115-194227` |
| **MF-15** | **fixed (pre-applied, verified)** | Committed in `~/AI/render` (`c0d356d`): `AGENTS.md` `PIPELINE` and `THE ONE COMMAND` now invoke `/home/derekboone/AI/render/x3/.venv/bin/python3` (Python 3.14), `Gemma 4 26B A4B Heretic Q8_0 on llama.cpp Vulkan`, `queue-remote.sh`, and X3 `POOL`/`_inputs` still rules (`vault.db` and `stills/comfy_input` noted as uncopied/AlienPc-only). | `~/AI/render/x3/README-X3.md.bak-20261115-193958` |
| **MF-16** | **fixed (pre-applied, verified) / deferred (optional evals)** | `RESULTS.md` 7:45 PM CT status block downgrades Q8 vs Q4 to a short smoke test, notes U6 formal 3-run 262K protocol (`~/u6-262k/`, 3/3 pass), and notes EQ-Bench Creative Writing v3 / RULER were not run (paid judge not approved; chat cutover held). | `~/evo-x3/bakeoff/RESULTS.md.bak-20261115-194227` |

### Should-Fix Items

| ID | Status | Summary & Verification | Backups |
|---|---|---|---|
| **SF-01** | **fixed (finished in U31, verified & committed)** | Finished `~/AI/render/.pi/extensions/loop-guard.ts` (added `BOOL_FLAGS` check so boolean flags before `<run_dir>` are not treated as consuming the next token, kept Linux path case, and stopped clearing `runCounts` on `agent_settled` or trip) and added case #8 (`--continued /tmp/R6`) to `loop-guard-test.mjs`. Verified `node loop-guard-test.mjs` -> `loop-guard unit tests OK 8`. Committed in `~/AI/render` (`513fd09`). | `~/AI/render/.pi/extensions/loop-guard.ts.bak-20261115-194227`, `.../200719`, `.../loop-guard-test.mjs.bak-20261115-200719` |
| **SF-02** | **fixed (pre-applied in U27) / skipped (weight move & locking changes)** | Halogen weights already moved in U27 Dispatch 3 to `/srv/models/flash-next-halogen` (`/srv/bakeoff/halogen-models` is a symlink), verified mounted in `llama-swap.yaml`. Halogen 0.20.5 engine startup logs show `62.1 GiB of weights locked in RAM` (`Pin::None` applies only to the `47.7 GiB` disk-backed n-gram table). No further `/srv` moves run per brief. | `/etc/evo-x3/llama-swap.yaml.bak-20261115-185401-pre-u27-phase1-4` |
| **SF-03** | **fixed (pre-applied, verified & committed) / deferred (container persistence)** | `--no-slots` removed from `gemma4-heretic` in `/etc/evo-x3/llama-swap.yaml` and verified live (`http://127.0.0.1:8081/slots` returned 2 slots during U31 rerun). Committed via `etckeeper` (`9a3b135`). Changing `podman run --rm` persistence deferred for Derrick's choice. Note: `embed-small` retains `--no-slots` per existing config. | `/etc/evo-x3/llama-swap.yaml.bak-20261115-194720-pre-u31-yaml`, `.../194731-pre-u31-yaml` |
| **SF-04** | **partial (pre-applied) / deferred (Test #3 formal check)** | Verified `~/.pi/agent/models.json` `flash-next` name already updated to `X3 local Qwen3.8-Flash-Next native HGN v2 (Halogen 0.20.5)` and `maxTokens: 32768` matches Halogen's runtime `max_tok 32768`. Render subagent alias `gemma4-heretic-sub` (`maxTokens: 4096`, `reasoning: false`) added and verified. Deferred: adding `supportsReasoningEffort` / running `full-audit` Test #3 to confirm `pi` thinking flags vs `HALOGEN_REASONING_EFFORT=medium` and `thinkingBudgets`. | `/home/derekboone/.pi/agent/models.json.bak-20261115-194720-pre-u31-models`, `.../194731-pre-u31-models` |
| **SF-05** | **skipped (needs Derrick's choice)** | SearXNG home (QNAP `192.168.0.147:8888` vs X3 container) left unchanged per brief. `~/.pi/agent/web-search.json` still points to `http://192.168.0.147:8888`. | None |
| **SF-06** | **skipped (risky / needs Derrick's choice & reboot)** | Note: U27 Phase 4 already hardened `sshd` (`PermitRootLogin no`, `PasswordAuthentication no` in `/etc/ssh/sshd_config.d/00-x3-hardening.conf`), enabled `tuned` (`accelerator-performance`), pinned Open WebUI digest (`@sha256:59b912d4...`), and added `evo-llama-swap` empty-key exit 78 guard (`10-empty-key-guard.conf`, verified `401`/`200`). Skipped in U31 per brief: removing deprecated `amdgpu.gttsize=122880` from kernel cmdline (`/proc/cmdline` still carries `amdgpu.gttsize=122880 ttm.pages_limit=31457280`), Open WebUI re-pin, or altering llama-swap auth guard. | None |
| **SF-07** | **skipped (U27 verified `pi-workspace-history`; compaction test deferred)** | U27 Phase 5 already tested `pi-workspace-history@0.5.2` (`/undo` drill passed) in Forge. Render compaction threshold (`reserveTokens: 24576` vs ~95K) deferred until Render evaluation / cutover. | None |
| **SF-08** | **skipped (needs clean-room scaffold / future bake-off)** | `kyuz0/local-agent-builder` was not cloned or copied (unlicensed). Deep-research / coding bake-offs not started in U31 per brief. | None |
| **SF-09** | **fixed (pre-applied, verified)** | Verified `~/evo-x3/records/U26-huihui-hgn-20261115.md` exists; `~/evo-x3/bakeoff/RESULTS.md` updated; `~/AI/community` commits `98c0bc4` and `faa32e8` clarify `AGENTS.md` (propose-vs-apply `llama-swap.yaml`, pinned CE GitHub exception, `pi 1.5.2`, same-slot subagent aliases) and mark the 5 Windows-only queue/vault tests `@pytest.mark.skipif(sys.platform != "win32")`. Verified `/home/derekboone/AI/render/x3/.venv/bin/pytest -q /home/derekboone/AI/community/scripts/parody/` passes **526 passed, 6 skipped in 3.43s**. Note: `render_writer_pipeline.py` retains CRLF endings (intentionally preserved to match AlienPc source). | `~/evo-x3/bakeoff/RESULTS.md.bak-20261115-194227` |

### Windows / AlienPc Carry-Over Notes
- **`pi-permissions.jsonc` PowerShell/AlienPc rules:** `5slock` rules removed (`MF-03`); remaining non-blocking Windows/AlienPc path rules (`director`, `Launchers`, `skillspector`, PowerShell bash rules) left intact under Derrick's deny-list constraint (`MF-13`).
- **`render` and `forge` `.pi/settings.json` desktop packages (`pi-say`, `pi-canvas`, `plannotator`):** `render-pi.sh` explicitly passes `--no-extensions` + `-e` to prevent loading those in Render sessions (`MF-06`). Leaving `forge/.pi/settings.json` / `render/.pi/settings.json` package lists aligned with AlienPc avoids unintended drift without Derrick's OK.
- **`AGENTS-forge.md` line 40 (`Set PYTHONIOENCODING=utf-8`):** Untouched in `98c0bc4` (`actions.log` / `AGENTS.md` still has that phrasing for Windows parity).

---

## Render Subagent Rerun Result (`~/u31-render-sub/rerun_render_sub_test.py`)

- **Why the first 19:48 test reported `used_sub_alias: false`:**
  1. Built-in `pi-subagents` agents (`worker`, `scout`, etc.) specify `thinking: high` / `thinking: low` in frontmatter, so `render/.pi/settings.json` having only `subagents.defaultModel` caused the first test to launch `x3-local/gemma4-heretic-sub:high`.
  2. The first test script (`u31_yaml_and_render_sub_test.py`) searched parent stdout prose for `"gemma4-heretic-sub"` instead of reading `pi-subagents` run metadata (`/tmp/pi-subagents-uid-1000/artifacts/*_meta.json` and `status.json`).
- **U31 Rerun configuration:** Added `"disableThinking": true` and `"defaultThinking": "off"` to `~/AI/render/.pi/settings.json` (`subagents` block), then ran `timeout -k 20 240 bash ~/AI/render/x3/render-pi.sh -p --no-session` asking for one `scout` subagent.
- **Measured result (`~/u31-render-sub/result.json`, run ID `cc6aa45b-4576-4ea0-a62e-15a83f8c8a70`):**
  - `rc`: `0`, `elapsed_s`: `102.0` (`finished_in_time: true`, `timeout_enforced_if_overrun: true`, `timed_out: false`, `crashed: false`)
  - Parent stdout (`rerun-render-sub-test.out`): `4.`
  - Subagent model (`cc6aa45b-4576-4ea0-a62e-15a83f8c8a70_scout_meta.json` & `status.json`):
    - `requestedModel`: `x3-local/gemma4-heretic-sub`
    - `model`: `x3-local/gemma4-heretic-sub` (`used_sub_alias: true`)
    - `resolvedModel`: `{"provider": "x3-local", "model": "gemma4-heretic-sub"}`
    - `sub_max_tokens_4096`: `true` (`models.json` `maxTokens: 4096`, `reasoning: false`)
  - Thinking state: `thinking_off: true` (`status.json` `steps[0].thinking`: unset/`null`, child transcript `thinkingLevel: "off"`, no `:high`/`:low` suffix). *Observation:* because `models.json` sets `reasoning: false` on `gemma4-heretic-sub`, `pi` omits `chat_template_kwargs: {enable_thinking: false}` and `llama-server` (`--reasoning-format deepseek`) still emitted a short `reasoning_content` trace before replying; switching to `reasoning: true` with `defaultThinking: "off"` would actively send `enable_thinking: false` if desired later.
  - Slot count: `live_heretic_slots: 2` (queried live via `http://127.0.0.1:8081/slots` while `llama-swap-gemma4-heretic` was running) and `llama-swap.yaml` remains `-np 2` / `concurrencyLimit: 2` (`heretic_still_np2: true`).
  - Production restore: Immediately reloaded `flash-next` (`flash_next_reload_status: 200`); `podman ps` showed `["open-webui", "llama-swap-flash-next"]`; `bash ~/evo-x3/scripts/verify-serve.sh` passed (`no key: 401`, `LLM_KEY_BOX: 200`).

---

## Commits & Hashes

| Repo | Branch | Commit Hash(es) | Scope |
|---|---|---|---|
| `/etc` (`etckeeper`) | `master` | `9a3b135a4681d095ee3ed0e2cd9929aa11d0ef2b` (`9a3b135`) | `.etckeeper`, `containers/systemd/open-webui.container`, `evo-x3/llama-swap.yaml` |
| `~/AI/render` | `x3-linux` | `c0d356d569264d9200b83d46b4773b34602f4190` (`c0d356d`, prior job)<br>`513fd09bd9e8fa1eb701ab0356db2293e9b7ac2b` (`513fd09`, U31 finish) | `AGENTS.md`, `x3/render-pi.sh`, `.pi/extensions/loop-guard.ts`, `.pi/extensions/loop-guard-test.mjs`, `.pi/settings.json`, `x3/README-X3.md` |
| `~/AI/community` | `x3-linux` | `98c0bc42eb53c5e22380fdbf3c26cb79d1831b7a` (`98c0bc4`, prior job)<br>`faa32e8574e46168a57995517691c9aa21b9da70` (`faa32e8`, prior job) | `agent-shared/AGENTS.md` + `pytest.mark.skipif` on 3 parody test files (`notes/actions.log` modified, left uncommitted) |
| `~/.pi/agent/models.json` | — | **Not committed** (holds key-read command) | `gemma4-heretic-sub` alias |

---

## Fleet-Brain Pack Changes Needed (Not Edited Directly)

Per rule ("Do not edit fleet pack files; list needed pack changes instead"):
1. **`10_packs/max/max-briefing.md` / `10_packs/fleet/derricks-standing-rules.md`:** Update EVO-X3 model/slot summary (`flash-next` on Halogen 0.20.5 with `concurrencyLimit: 4` and `flash-next-sub`, `flash-next-gufo` rollback, `gemma4-heretic` at `-np 2` with `gemma4-heretic-sub` alias, `qwen27b` Q8+DFlash2 not co-resident with Heretic).
2. **`10_packs/fleet/derricks-standing-rules.md` / Render pack notes:** Record that X3 Render launcher (`~/AI/render/x3/render-pi.sh`) uses `--no-extensions` + explicit `-e` flags, `x3/.venv/bin/python3` (Python 3.14), `queue-remote.sh` to AlienPc, and `POOL`/`_inputs` stills only (no local `vault.db`).
3. **Host hardening / Open WebUI notes:** Record `ENABLE_SIGNUP=false` active (`1` admin user) and `WEBUI_SECRET_KEY` env-only launch (U30).

---

## Leftovers Preserved & Items Needing Derrick

### Preserved Leftovers (Not Deleted)
- Backups `*.bak-20261115-19*` and `*.bak-20261115-20*` beside edited files (including `/etc/*.bak-*` untracked in etckeeper, `~/.pi/agent/*.bak-*`, `~/AI/render/**/.bak-*`, `~/evo-x3/bakeoff/RESULTS.md.bak-20261115-194227`, `~/u31-render-sub/result.json.bak-20261115-200757`).
- `/tmp/u31-stage/` (plus `actions.log.bak-20261115-200701`), `/tmp/llama-swap.u31pre.yaml`, `/tmp/u31-webui-count.py`.
- `~/u31-render-sub/` (including `hdr`, `u31_yaml_and_render_sub_test.py`, `rerun_render_sub_test.py`, `result.json`, logs — `hdr` never read/printed/copied).
- `~/evo-x3/records/U27-on-track-20261115.md.bak-20261115-192508`.

### Still Needing Derrick's Choice / Approval
1. **Render subagent `gemma4-heretic-sub` server-side `enable_thinking` (`SF-04` / `models.json`):** `pi` passed `thinkingLevel: "off"`, but because `models.json` sets `reasoning: false` on `gemma4-heretic-sub`, `llama-server` still emitted a brief `reasoning_content` block. Confirm if you want `reasoning: true` on `gemma4-heretic-sub` (with `defaultThinking: "off"`) so `pi` explicitly sends `chat_template_kwargs: {enable_thinking: false}`.
2. **SearXNG home (`SF-05`):** Bring QNAP (`192.168.0.147:8888`) online vs host SearXNG on EVO-X3 and update `~/.pi/agent/web-search.json`.
3. **Kernel cmdline `amdgpu.gttsize=122880` (`SF-06`):** Drop deprecated `amdgpu.gttsize` on next reboot (keeping `ttm.pages_limit=31457280`).
4. **Container persistence (`SF-03`) & Render compaction threshold (`SF-07`):** Whether to evaluate persistent stopped containers instead of `podman run --rm` for RAM prompt-cache retention, and whether to test ~95K compaction (`reserveTokens: 167144`) for Render.
5. **Halogen `full-audit` Test #3 (`SF-04`):** Confirm `supportsReasoningEffort` vs `qwen-chat-template` behavior against Halogen `HALOGEN_REASONING_EFFORT=medium`.
6. **Clean-room research/coding bake-offs (`SF-08`, `MF-16`) & fleet-brain pack edits:** Pending Derrick's scheduling/approval (and note `~/AI/render/stills/` remains untracked in `~/AI/render` by design from initial setup).
