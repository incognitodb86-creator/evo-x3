# Hermes cleanup + live X3 community 1690ce54 + dual-host snapshot

When: 2026-11-19 9:01-9:10 PM CT (America/Chicago). Doer: Max X3 lane (executor). Authority: already-approved Hermes cleanup (`t2965s10385`, overnight/batch `t2970u`) plus live X3 `mono` `1690ce54` pull and dual-host snapshot. llama-swap Gemma redirect and ref2va context window were not changed (await Derrick).

## Part A — Hermes (EVO-X3)

- Backup: `/home/evo/_archive/20261119-hermes-cleanup/` (config.yaml, SOUL.md, skills tree, WebUI version, community files that were overwritten).
- Workspace: `/home/evo/workspace/AGENTS.md` (3,670 B, under 8 KB). `terminal.cwd=/home/evo/workspace`. WebUI drop-in `/home/evo/.config/systemd/user/hermes-webui.service.d/30-workspace.conf` sets `HERMES_WEBUI_DEFAULT_WORKSPACE=/home/evo/workspace`.
- Thinking off: `model.reasoning_effort=false`, `auxiliary.vision.reasoning_effort=false`, and `agent.reasoning_effort=false` kept in the file. Hermes Agent v0.23.3 schema warns that `agent.reasoning_effort` is unrecognized on `config get` (`Did you mean: agent.reasoning_echo`) but runtime `parse_reasoning_effort` still treats YAML `false` / `none` as disabled; WebUI follows `model.reasoning_effort`.
- Slim native `h3-render` v2.0.0 and `h3-writer` v2.0.0 installed to `/home/evo/.hermes/skills/creative/` (`build-hermes-skills.sh --check` OK). No Python writer/judge; 18+ `wp_lint` + `fill_request.py` dry-run + `queue-remote.sh`. Long commands use terminal `background=true` and `notify_on_complete=true`, then the `process` tool (never `setsid`/`nohup`). Overnight/batch only on an explicit ask; summary in chat + a file; no new ntfy unless Derrick asks.
- hermes-webui: was `exp-v0.52.718-1-g6c4aaaaf0`; now **`exp-v0.52.723`** (`3a669b5ab`, 8:17 PM CT). Picked over stable `v0.52.702` because live Agent is v0.23.3 and 723 fixes cached-conversation reuse on newer Agents (#9149/#9150). `hermes-gateway` and `hermes-webui` restarted at **9:05:14 PM CT**, both `active (running)`. Leftover gateway kernel sessions from the earlier dry-run were cleared. `/usr/bin/python3 -m pip` is not installed; `bootstrap.py`/`server.py` py_compile OK on the existing system Python, no extra pip install.

## Part B — live `/home/evo/AI/community`

- Live tree is still the `x3-community` repo at `827d012` with pre-existing local diffs (not a `mono` clone). Promotion files from `mono` `4d909034`/`1690ce54` were copied after backup. `fill_request.py` live matched mono minus the 2-pass hunks; mono file applied.
- SHA256 matches: `templates/oc_ref_2pass.api.json` = `1d3ec1da3ef8f2f2d8f111e52697713685d9084cb2271cc0aac8fc32e1882c9c`; `scripts/allowlist_promoted.json` = `834d1d0a65e3bec938167ddf5f58ac5aaefa75024bdf4a1a4b94fef2195a71c4`.
- Also copied test deps `template_allowlist.py`, `u55_allowlist_specs.json`, and `test_template_allowlist.py`.
- Tests in `/home/evo/AI/community` with `/home/evo/AI/render/x3/.venv/bin/python3 -m pytest`: **19 passed** (6 `test_pick_template_2pass.py` + 13 allowlist) at 9:04 PM CT.

## Part C — dual-host snapshot

- X3: `snapshot-live-setup.sh` and a sudo-capable `sync-config-copies` into staging, then installed into `hosts/x3/live` and `config/` (tracked `config/bin` extras and the retired open-webui container archive were kept; not dropped by the sync overwrite).
- AlienPc (read-only, machine `AlienPc`): community HEAD still `8eec1d3d` (recorded 9:07:39 PM CT); on-disk promo hashes match the same two SHA256s. ComfyUI checkout `a277b5bf`. Model inventory was not re-counted. `sydney/`, `models.json`, and `git remote -v` in community/render were not opened. CRLF-only recopies were not committed.

## Also verified

- **pi-job thinking:** live `/usr/local/bin/pi-job` still uses `--thinking medium` on AlienPc Swift (`PI_JOB_ALIENPC_THINKING`, default `medium`) and `low` on the X3 Gufo fallback. Not changed.
- **gbrain-sync:** last run `SYNC_DONE` 2026-11-19 8:28 PM CT. No brain files were written in this job; Fleet Architect can update the two brain-staging files separately.
- **`/home/derekboone/evo-x3`:** left unpushed / not fast-forwarded. It is still at stale `a383932` with local snapshot edits; this commit is from the box `/workspace/mono-sync` clone.

## Lease

One-line lease taken 9:01 PM CT in `/home/derekboone/AI/locks/x3-lease.txt`. `x3-lease.txt.bak-hermes3m-20261119` was left untouched. Lease cleared after this push.
