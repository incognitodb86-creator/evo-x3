# U31 — Implement open Antigravity audit fixes (Derrick approved)

You are Google Antigravity **Orchestrator (Argon)** (`gemini-pro-orchestrator-g1-pro`). Implement the open items in `~/evo-x3/records/agy-redteam-review-20261115.md`. This is an implementation run, not report-only.

Approved by Derrick: t1819u ("Ok continue address and fix") and the card answer "Yes, hand the audit fixes to the Antigravity Orchestrator" (after t1821u). A previous Max job working on these same fixes was stopped mid-run around 19:49 CT on 2026-11-15. Do not revert its work. Verify what already landed, finish what is incomplete, and record every item as fixed / skipped(why) / deferred.

Working directory: `~/evo-x3`. Record: `~/evo-x3/records/U31-agy-audit-fixes-20261115.md` with per-item status and backup paths.

## Already applied by the stopped Max job (verify, do not redo blindly)

Inspect live files against the backups listed below. If an item is already correct, mark it **fixed (pre-applied, verified)** and move on. If it is half-applied, finish it (new `.bak-<timestamp>` first).

### Priority items (do these first if still open)

- **MF-03** — Looks applied at 19:39:58 CT. Live `~/.pi/agent/pi-permissions.jsonc` (backup `pi-permissions.jsonc.bak-20261115-193958`): leftover AlienPc `5slock` path rules dropped; `edit`/`write` denied on `~/AI/forge/ralph-community/*.sh` and `logs/*`, plus bash write-guards. Confirm no `5slock` allow/deny path rules remain (a comment mentioning the drop is fine) and that Forge can still *execute* `ralph.sh`.

- **MF-08** — Looks applied in `/etc/evo-x3/llama-swap.yaml` at 19:47:31 CT (backups `llama-swap.yaml.bak-20261115-194720-pre-u31-yaml` and `...-194731-pre-u31-yaml`). The rollback `flash-next-gufo` slot uses `--name llama-swap-flash-next-gufo`. Production `flash-next` still uses `--name llama-swap-flash-next`. Confirm no two slots share a Podman `--name`.

- **MF-15** — Already committed in `~/AI/render` as `c0d356d` ("X3 Render docs and launcher (U31 / Antigravity MF-15, MF-06)"). Confirm `AGENTS.md` PIPELINE / ONE COMMAND points at the X3 venv and `queue-remote.sh`, not AlienPc `--queue` / bare `python3` / PolyStrata.

- **MF-06** — Same commit `c0d356d`. `render-pi.sh` still uses `--no-extensions` on purpose (to avoid plannotator / pi-canvas / pi-say / compound-engineering) and now passes intended extensions with `-e`: `pi-permission-system`, `cc-safety-net`, `loop-guard`, `pi-subagents`, `pi-memory`. Confirm those five are the intended set and that they actually load.

### Render subagent cap (partially applied; rerun the test)

Goal: Render's Heretic subagents use a `~/.pi/agent/models.json` alias on the **same** `gemma4-heretic` llama-swap slot, `maxTokens` about 4096, thinking off, with an enforced timeout. Keep Heretic at **2 slots** (`-np 2`, `concurrencyLimit: 2`). Do not add a new exclusive-group member.

Already applied at 19:47:20–19:47:32 CT (then re-applied at 19:47:31):
- `models.json` now has `gemma4-heretic-sub` (`reasoning: false`, `maxTokens: 4096`). Do **not** commit `~/.pi/agent/models.json` (it holds a key). Backups: `models.json.bak-20261115-194720-pre-u31-models` and `...-194731-pre-u31-models`.
- `~/AI/render/.pi/settings.json` `subagents.defaultModel` is `x3-local/gemma4-heretic-sub` (uncommitted). Backups: `settings.json.bak-20261115-194720-pre-u31-render-settings` and `...-194731-pre-u31-render-settings`.
- `llama-swap.yaml` `gemma4-heretic` has `aliases: [gemma4-heretic-sub]`, `useModelName: gemma4-heretic`, and `--no-slots` was removed. Heretic still `-np 2` / `concurrencyLimit: 2`.
- A first Render subagent test already ran 19:47:34–19:48:41 CT and reported PASS (`rc 0`, 67.7s, timeout enforced, Heretic still np2, no crash). **Caveat: `used_sub_alias` was false.** The job then reloaded production `flash-next` (health 200 at 19:48:53 CT). Logs are in `~/u31-render-sub/` (`run.console`, `result.json`). Do **not** read or print `~/u31-render-sub/hdr` (leftover auth header from the stopped job).

**Rerun the Render subagent test once.** Confirm the subagent actually uses the `gemma4-heretic-sub` alias (maxTokens 4096, thinking off), Heretic stays at 2 slots, the timeout is enforced if it overruns, then put production back on `flash-next` if you swapped away. Only SIGHUP or restart llama-swap when no request is in flight. As of 19:54 CT, `llama-swap` was idle with `llama-swap-flash-next` loaded (service MainPID from 19:07:27 CT; container recycled at 19:48 during the earlier test).

### Other pre-applied work to verify

- **MF-11 (partial):** live `open-webui.container` has `ENABLE_SIGNUP=false` (edit 19:43:04 CT; backup `open-webui.container.bak-20261115-194300`). The running container was still the pre-edit instance as of 19:54 CT (~38 minutes up, started ~19:16 during U30). Reloading the unit would be needed for this to go live; only do that if it is safe and idle, otherwise defer and list it. Do not touch Tailscale or the unit's secret EnvironmentFile.
- **MF-12:** already done earlier (U30, Derrick t1815u). Do not redo. Skip as already done.
- **MF-09:** already done (Heretic rolled back to np2 after the np4 crash; do not raise Halogen to 4 at 262K). Skip as already done.
- **SF-01 (partial):** `~/AI/render/.pi/extensions/loop-guard.ts` is modified and uncommitted (plus untracked `loop-guard-test.mjs`). Backup `loop-guard.ts.bak-20261115-194227`. Finish/verify the regex, Linux path, and `runCounts` reset fixes, then commit if good.
- **SF-03 (partial):** `--no-slots` already removed from the live `gemma4-heretic` command. Confirm. Do not change `podman run --rm` persistence without listing it as needing Derrick's choice.
- **SF-09 (partial):** `~/evo-x3/bakeoff/RESULTS.md` updated 19:42 CT (backup `RESULTS.md.bak-20261115-194227`). Community `agent-shared/AGENTS.md` clarifications and Windows-only queue test `skipif`s are committed: `98c0bc4`, then `faa32e8` (newline restore on the three test files). Uncommitted: `notes/actions.log` plus various pre-existing untracked community paths — do not `git add` unrelated untracked trees, and never `git add -A` in `~/AI/community`.

### Leftover files from the stopped job (do not delete; do not print secrets)

- Backups named `*.bak-20261115-19*` / `20*` that are **not** U29 (`*-pre-u29`): see the record; leave them in place.
- `/tmp/u31-stage/` (staged copies of AGENTS, permissions, loop-guard, RESULTS, render-pi.sh).
- `/tmp/llama-swap.u31pre.yaml` (root-owned yaml copy, 19:28 CT).
- `/tmp/u31-webui-count.py`
- `~/u31-render-sub/` including scripts and **`hdr` (do not read/print/copy)**.
- `~/evo-x3/records/U27-on-track-20261115.md.bak-20261115-192508` (U27 record edit, not this job's main work).

## Skip (Derrick's decisions or already done)

- **MF-07** — no pi-model-swap guard.
- **MF-13** — no approval-prompt / sandbox rewrite that conflicts with "no approval prompts; keep the deny list".
- **MF-04** — do not add approval prompts; do not loosen `fix_plan.md` / `progress.md` denies in a way that conflicts with Derrick's deny-list decision. If a deadlock remains, list it as deferred with the conflict explained.
- **MF-09** and **MF-12** — already done (see above).

## Then the medium and low items

Work through remaining Must-Fix (MF-01, MF-02, MF-05, MF-10, MF-11 if still open, MF-14, MF-16, MF-17 as applicable) and Should-Fix (SF-01 through SF-09) that you can complete safely.

**Skip and list** anything risky or that needs Derrick's choice, including:
- **SF-02** relocating Halogen weights or large copies/moves under `/srv`.
- **SF-05** choosing a SearXNG home (QNAP vs new X3 container).
- **SF-06** SSH hardening, `tuned`, `amdgpu.gttsize` / `ttm.pages_limit`, BIOS-adjacent or reboot-required changes, llama-swap fail-open auth guard if it risks locking him out.
- **SF-08** cloning or copying `kyuz0/local-agent-builder` (licensing). Derrick separately approved a deep-research bake-off after setup; do not start that bake-off here.
- Fleet pack file edits — list needed pack changes instead. Do not edit pack text.
- Open WebUI image re-pin or container rebuilds that are not required for the already-applied secret fix.
- Anything that would touch Windows partitions, BIOS, USB X3BACKUP, Tailscale, Sydney, or PixlStash.

## Hard rules

- Back up every file before you edit it (`.bak-<timestamp>`).
- Never put secrets on command lines and never print them. Never read `/etc/evo-x3/*.env`, `*.cred`, `~/u31-render-sub/hdr`, or key files. Do not pass `LLAMA_SWAP_KEY` or any secret on a command line.
- Do not commit `~/.pi/agent/models.json`.
- Do not touch Windows partitions, BIOS, USB X3BACKUP, or Tailscale.
- Do not edit fleet pack files (list needed changes in the record instead).
- Do not read Sydney's chats, persona, or memory. Do not view PixlStash library contents. Do not touch the original ComfyUI folder.
- Do not delete anything; use `_archive` if you must move a file.
- Only restart llama-swap (or SIGHUP it) when no request is in flight. After any swap for a test, restore production `flash-next` if you left something else loaded.
- No new spending, no firmware, no LUKS, no slot/model re-pulls.
- Do not use `git add -A` in `~/AI/community`.
- `~/evo-x3` is **not** a git repository today (no `.git`). Do **not** `git init` it. Write the U31 record under `~/evo-x3/records/`. Commit `/etc` changes with **etckeeper** after a secret-safe review. Commit on-topic changes in the existing repos `~/AI/render` (branch `x3-linux`) and `~/AI/community` (branch `x3-linux`) only. `gitleaks` was not installed on this host as of 19:54 CT; do not install it. Review diffs carefully so no secrets are committed, and note "gitleaks unavailable" in the record.
- etckeeper already has uncommitted changes: `containers/systemd/open-webui.container`, `evo-x3/llama-swap.yaml`, plus several `*.bak-*` untracked backups. Include the real config edits; do not commit secret files. Prefer not to flood etckeeper with every `.bak-*` unless that is existing practice.
- Skip and list anything risky or needing Derrick's choice.

## Record and done condition

Write `~/evo-x3/records/U31-agy-audit-fixes-20261115.md` with:
- start/end times in America/Chicago,
- per item: fixed / skipped(why) / deferred, with backup paths,
- which of the stopped job's edits you verified vs finished,
- Render subagent rerun result (alias used or not, timeout, slot count, production model restored),
- etckeeper / git commit hashes,
- leftovers and anything still needing Derrick.

When finished, production should still be `flash-next` unless a documented in-flight reason prevents the restore.
