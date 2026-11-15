# EVO-X3 U21: on-box agent harness (pi + subagents + herdr), 2026-11-15

Authority: Derrick t1712u "Yes I want all of that and agent harness and stuff", t1713u "I want the ultimate swtup".
Executor: Max (Grok Bot executor), 11:37–11:50 AM CT.

## Installed (official / community methods)
| Piece | Version | Method |
|---|---|---|
| Node.js LTS | 24.18.0 (npm 11.16) | Fedora 44 `dnf install nodejs24 nodejs24-npm` |
| pi coding agent | @earendil-works/pi-coding-agent 1.5.0 (same as AlienPc) | `npm i -g` with prefix `~/.local` (no root) |
| pi-subagents | 0.83.1 (same pin as AlienPc) | `pi install npm:pi-subagents@0.83.1` |
| cc-safety-net | 2.7.0 (AlienPc pin) | `pi install` |
| @juicesharp/rpiv-todo | 2.15.0 (AlienPc pin) | `pi install` |
| pi-web-access | 0.46.0 (AlienPc pin) | `pi install` |
| herdr | 0.9.5 (same as AlienPc) | official `https://herdr.dev/install.sh` to `~/.local/bin` |

Not copied from AlienPc on purpose: pi-mobile (phone hub stays on AlienPc until cutover), pi-computer-use (headless box), pi-canvas, plannotator, pi-say, pi-memory, pi-permission-system (needs its own policy file), the CE git package and AlienPc's Windows skill paths.

## Config (no secrets in files below)
- `~/.pi/agent/models.json` (0600): provider `x3-local` → `http://127.0.0.1:8080/v1` (loopback llama-swap). `apiKey` is `!cat ~/.config/evo-x3/llm-key`, so pi reads the key at request time; nothing on a command line. Models: gemma4-heretic (default), qwen27b, flash-next — the current production llama-swap names.
- `~/.config/evo-x3/llm-key` (0600 derekboone): copy of `LLM_KEY_PI` from `/etc/evo-x3/llm.env`, written via sudo stdout redirect, never printed. Leak check: key string not found in any test log, pi dir or subagent tmp dir.
- `~/.pi/agent/settings.json`: defaultProvider x3-local, defaultModel gemma4-heretic, thinking off, telemetry/analytics off, `subagents.defaultModel = x3-local/gemma4-heretic`. Backup: `settings.json.bak-20261115-harness`.
- Repo copies: `harness/pi/`.

## Tests (logs on X3 in `~/evo-x3/harness-tests/`; summary in `harness/tests/`)
llama-swap had been stopped by the bake-off at 10:50 CT with no engine on the GPU (GTT used 0.02 GiB, no podman containers). Started it only for the test window, then stopped it again at ~11:43 CT to leave the bake-off state as found. llama-swap.yaml untouched.

| Test | Time CT | Result | Evidence |
|---|---|---|---|
| Tool calls: `read` canary.txt + `bash` `uname -n && nproc` on gemma4-heretic | 11:40 | **PASS** | structured `read` and `bash` tool calls, both ok; answer `X3-HARNESS-CANARY-7731, evo-X3, 32` |
| Subagent: parent launches `scout` via pi-subagents, waits, returns result | 11:41 | **PASS** | `subagent` → async run b958180d, `bg_wait` done in 18.4 s; child used `x3-local/gemma4-heretic` with its own read/bash/write calls; parent answer `SUBAGENT_RESULT: X3-HARNESS-CANARY-7731` |
| herdr binary | 11:39 | installed, `herdr 0.9.5`; no panes/sessions created (no persistent agents on the X3 until Derrick picks roles after the bake-off) |

## Also added (gap audit, reversible)
- `evo-x3-config-backup.timer` (daily, root-only 0600 tarballs of /etc/evo-x3, llama-swap unit, ttm.conf, grub default, pi settings/models in `/var/backups/evo-x3`, keeps 14). First run 11:43 CT OK. Source in `ops/config-backup/`. Undo: `systemctl disable --now evo-x3-config-backup.timer`.

## Rollback
`npm rm -g @earendil-works/pi-coding-agent`; `rm -rf ~/.pi ~/.config/evo-x3/llm-key ~/.local/bin/herdr`; `dnf remove nodejs24 nodejs24-npm`.
