# U53 Result — Forge Batch from Fleet Reviewer's Audit (EVO-X3)

Date: 2026-11-16 (CT)
Brief: `/home/derekboone/evo-x3/records/U53-forge-batch-brief-20261116.md`
Audit: `/home/derekboone/evo-x3/records/2026-11-16-forge-audit.md`

---

## Per-Item Status

1. **B3, Ralph lock:** **DONE**
   - Updated `/home/evo/AI/forge/ralph-community/ralph.sh` `gpu_busy()` to test `$GpuLockPath` with `flock -n "$GpuLockPath" true` (matching `queue-remote.sh` / `remote_comfy.py`) instead of treating a 0-byte or PID-less file as busy.
   - Verified with a 2-item smoke loop (`-Max 3 -CommandOverride ...`, no GPU, no renders) while `/home/evo/AI/locks/gpu-render.lock` was present at 0 bytes: completed both passes with 0 waits and exited `PLAN_COMPLETE`. Also verified negative case with an active `flock` on a temp lock file (`GPU_BUSY` -> `GPU_DEFERRED`).
2. **B4, Gitea restore:** **DONE**
   - Fast-forwarded `/home/evo/AI/forge` to `gitea/x3-forge` (`e0f5dc0`) preserving `/home/evo` paths, added `/home/evo/AI/community/agent-shared/extensions/.gitkeep`, committed `/home/evo/AI/community` (`x3-linux`) and `/home/evo/AI/forge` (`main` -> `x3-forge`) by explicit path only, verified `gitleaks` clean, and pushed to Gitea (`evo` already held Gitea push credentials; see I12 below).
   - Proved with a fresh clone of `x3-community` and `x3-forge` into `/tmp/u53-b4-restore/AI/` and a dry start (`pi --approve --offline --list-models`, no model load, no agent launched).
3. **I2, Forge loop safety checks:** **DONE**
   - Implemented in `/home/evo/AI/forge/ralph-community/ralph.sh`, `/home/evo/AI/forge/ralph-community/PROMPT.md`, and `/home/evo/AI/community/agent-shared/skills/ralph-loop/SKILL.md`:
     - Clears and archives stale `fix_plan.md` unchecked items (`>12h` old or older than a finished `DONE.txt`, plus `-ClearStale`).
     - Creates one git worktree per loop under `~/AI/_worktrees/ralph-<day>-<pid>/{forge,community}` on branch `ralph-<day>-<pid>-*` (`RALPH_FORGE_WORKTREE` / `RALPH_WORKTREE`).
     - Denies edits to `skills/` and `AGENTS.md` inside loops both via loop-scoped `PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR` (`pi-permissions.jsonc` tool + bash deny rules) and post-pass backpressure verification.
     - Enforces a per-pass `git diff --stat` file cap (`-MaxDiffFiles 10` default) across touched worktrees/repos.
     - Runs a per-pass backpressure check (`run_backpressure`) including a skill-load smoke test (`16` skills loaded, `0` errors, `AGENTS.md` symlink, `agent-shared/extensions`, no `.bak-*` files in `skills/`), reverting the worktree and `fix_plan.md` on failure.
   - All 4 automated `-CommandOverride` safety tests (stale clear, worktree + skill-load smoke pass, protected-path reject/revert, diff-cap reject/revert) passed.
4. **I3, fix the failing tests (no `xfail`):** **DONE**
   - Fixed the real bug in `scripts/comm.py`: derived `W` from `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` (`__file__`) instead of `r"C:\AI\community"`, fixing `comm.LOG` (`comm.py:29`) and all 3 `test_run_queue_one_at_a_time.py` failures.
   - Derived `COMMUNITY` from `__file__` in `scripts/make_b2_request.py` and `scripts/make_bfs_request.py`, fixing the 4 `test_b2_lora_param.py` failures and the `test_phase1_still.py` collection error.
   - Added `__file__`-derived `scripts` dir to `CANDIDATES` in `scripts/tests/test_free_comfy_args.py`, fixing the `StopIteration` collection error.
   - Updated `scripts/tests/_keep_comfy_writer_raw.txt` for U52's 18+ guard and updated `test_run_queue_keep_comfy_process.py::test_default_off_end_to_end_writer_run_argv` to pass `yes_derrick=True` and check `--yes-derrick` on Linux (`--detach` on Windows).
   - Fixed `scripts/tests/test_run_queue_cell_contract.py` `setUp()` to save/restore `(run_queue, comm, rgj)` module dicts via `addCleanup` so `run_queue.main()` on Linux does not leak `remote_comfy.enable()` into `test_run_queue_one_at_a_time.py`.
   - Both `pytest -q tests` and `pytest -q parody` are green with 0 failures, 0 errors, and 0 `xfail`.
5. **I8, rule-8 sweep of Forge `AGENTS.md`:** **DONE**
   - Trimmed `/home/evo/AI/community/agent-shared/AGENTS.md` from 43 lines / 7,920 bytes to 32 lines / 4,323 bytes (`Commands & Paths` / `Always` / `Ask Derrick First` / `Never`), keeping every useful rule and resolving all contradictions:
     - Lease rule aligned with `records/evo-x3-lease-README.md` (restarts take the lease; only read-only checks and quick one-off read commands skip it).
     - Backup rule aligned with `PROMPT.md` L4 (`_archive/<file>.bak-<date>` except inside isolated git-worktree Ralph loops).
     - MCP lines updated to U38 state (`gitea`, `playwright`, `searxng`, `fetch` enabled; `vaultwarden`, `google-workspace`, `unifi`, `homeassistant`, desktop control, phone delivery, voice playback not wired / awaiting keys).
   - Updated launcher L6 note in `/home/evo/AI/forge/launcher/forge-pi.sh`, `/home/evo/evo-x3/pi-chats/forge-pi.sh`, and `/home/derekboone/evo-x3/pi-chats/forge-pi.sh`.
6. **I9 (part), subagent model per pane:** **DONE**
   - Left `npm:pi-subagents@0.83.1` un-upgraded (per rule).
   - Updated `/home/evo/.pi/agent/settings.json` `subagents.defaultModel` from `x3-local/gemma4-heretic` to `x3-local/flash-next-sub` so standalone `pi` sessions outside `~/AI/render` or `~/AI/sydney` do not evict Forge's `flash-next`.
   - Created per-pane `PI_CODING_AGENT_DIR` directories under `/home/evo/.pi/panes/{forge,render,sydney}/` (symlinking shared agent state to `~/.pi/agent/*`, with pane-specific `settings.json`: `forge` -> `x3-local/flash-next-sub`, `render` -> `x3-local/gemma4-heretic-sub`, `sydney` -> `x3-local/gemma4-heretic-sub`) and exported `PI_CODING_AGENT_DIR` in `forge-pi.sh`, `render-pi.sh`, and `sydney-pi.sh`.
   - Verified with `pi --approve --offline --list-models` for `forge` and `render`. Neither Forge's nor Render's live pane was restarted (Forge's live session already gets `flash-next-sub` from `~/AI/forge/.pi/settings.json` and will pick up `PI_CODING_AGENT_DIR` + updated `AGENTS.md` on next pane restart).
7. **I11, per-run worktree and lease-line convention for future `agy` runs:** **DONE**
   - Added `/home/derekboone/evo-x3/records/agy-launcher-convention.md` and `/home/derekboone/evo-x3/records/agy-launch-TEMPLATE.sh` (verified `bash -n` and verified refusal `rc=2` when `LEASE_FILE` is missing on mutating runs).
   - Did not modify `U53-agy-launch.sh` or `U53-agy-start.sh`.
8. **I12, evo's Gitea token:** **BLOCKED**
   - Checked `evo` without printing any token values:
     - `evo` **does** hold Gitea tokens in two places:
       1. The write-capable `evo-x3` token (`sha256:45948ebcf749...`, len 40 — identical to `GITEA_TOKEN` already stored in `0600 root:root` `/etc/evo-x3/gitea.env`) in `/home/evo/.config/git/evo-x3-gitea` (`0600 evo:evo`) and `/home/evo/.git-credentials` (`0600 evo:evo`, read by `/home/evo/.gitconfig` `helper = store`).
       2. The read-only `forge-mcp` token (`sha256:498226108400...`, len 40) in `/home/evo/.config/forge-mcp/GITEA_ACCESS_TOKEN` (`0600 evo:evo`, read by `/home/evo/.config/forge-mcp/run-gitea-mcp.sh`).
     - **Block reason:** Per U35 (`U35-redteam-fixes-20261116.md`), `/etc/evo-x3` has `setfacl -m u:evo:--- /etc/evo-x3` and `gitea.env` is `0600 root:root` (`sudo -n -u evo cat /etc/evo-x3/gitea.env` -> `Permission denied`), and `evo` has no `sudo` and `pi-permissions.jsonc` denies `*/etc/evo-x3*`. Pointing `evo`'s readers (`git` and `run-gitea-mcp.sh`) at `/etc/evo-x3` cannot work while U35's ACL lock is intact, and relaxing `/etc/evo-x3`'s ACL would expose `/etc/evo-x3/llama-swap.yaml` (`0644 root:root`) and bypass U35's boundary. Because readers could not verify against `/etc/evo-x3`, no old copies were deleted. (Decision needed from Derrick/Max: either revoke/delete `evo`'s `.git-credentials` and `.config/git/evo-x3-gitea` and keep pushes on `derekboone`/Max per U35 while keeping the read-only MCP token in `evo`'s `0600` config, or approve a root-level helper/ACL design.)

- **Pane restart note:** Forge's pane and Render's pane were **not** restarted during U53.

---

## Files Changed and Backup Paths

| File | Backup Path |
|---|---|
| `/home/evo/AI/forge/ralph-community/ralph.sh` | `/home/evo/AI/forge/ralph-community/_archive/ralph.sh.bak-20261116-u53` |
| `/home/evo/AI/forge/ralph-community/PROMPT.md` | `/home/evo/AI/forge/ralph-community/_archive/PROMPT.md.bak-20261116-u53` |
| `/home/evo/AI/forge/launcher/forge-pi.sh` | `/home/evo/AI/forge/launcher/_archive/forge-pi.sh.bak-20261116-u53` |
| `/home/evo/evo-x3/pi-chats/forge-pi.sh` | `/home/evo/evo-x3/pi-chats/_archive/forge-pi.sh.bak-20261116-u53` |
| `/home/derekboone/evo-x3/pi-chats/forge-pi.sh` | `/home/derekboone/evo-x3/pi-chats/_archive/forge-pi.sh.bak-20261116-u53` |
| `/home/evo/evo-x3/pi-chats/sydney-pi.sh` | `/home/evo/evo-x3/pi-chats/_archive/sydney-pi.sh.bak-20261116-u53` |
| `/home/evo/AI/render/x3/render-pi.sh` | `/home/evo/AI/render/x3/_archive/render-pi.sh.bak-20261116-u53` |
| `/home/evo/.pi/agent/settings.json` | `/home/evo/.pi/agent/_archive/settings.json.bak-20261116-u53` |
| `/home/evo/AI/community/agent-shared/AGENTS.md` | `/home/evo/AI/community/agent-shared/_archive/AGENTS.md.bak-20261116-u53` |
| `/home/evo/AI/community/agent-shared/skills/ralph-loop/SKILL.md` | `/home/evo/AI/community/agent-shared/skills/ralph-loop/_archive/SKILL.md.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/comm.py` | `/home/evo/AI/community/scripts/_archive/comm.py.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/make_b2_request.py` | `/home/evo/AI/community/scripts/_archive/make_b2_request.py.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/make_bfs_request.py` | `/home/evo/AI/community/scripts/_archive/make_bfs_request.py.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/tests/test_free_comfy_args.py` | `/home/evo/AI/community/scripts/tests/_archive/test_free_comfy_args.py.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/tests/_keep_comfy_writer_raw.txt` | `/home/evo/AI/community/scripts/tests/_archive/_keep_comfy_writer_raw.txt.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/tests/test_run_queue_cell_contract.py` | `/home/evo/AI/community/scripts/tests/_archive/test_run_queue_cell_contract.py.bak-20261116-u53` |
| `/home/evo/AI/community/scripts/tests/test_run_queue_keep_comfy_process.py` | `/home/evo/AI/community/scripts/tests/_archive/test_run_queue_keep_comfy_process.py.bak-20261116-u53` |
| `/home/evo/AI/community/agent-shared/extensions/.gitkeep` | *(new file)* |
| `/home/evo/.pi/panes/{forge,render,sydney}/settings.json` | *(new per-pane dirs/files)* |
| `/home/derekboone/evo-x3/records/agy-launcher-convention.md` | *(new file)* |
| `/home/derekboone/evo-x3/records/agy-launch-TEMPLATE.sh` | *(new file)* |

---

## Commits & Push Results

All commits verified clean with `gitleaks` (`no leaks found`) and pushed normally (no force push):

- **`/home/evo/AI/community` (`x3-linux` -> `gitea/x3-community`, `10de4d0..1e47c40`):**
  - `1313227` — `U53 B4: commit evo /home/evo paths, actions.log, and agent-shared/extensions`
  - `631180b` — `U53 I2: document Ralph loop safety checks in ralph-loop skill`
  - `9a7a806` — `U53 I3: fix portable paths, U52 writer fixture, and cell_contract remote leak; all tests green`
  - `1e47c40` — `U53 I8: rule-8 sweep and trim of Forge AGENTS.md (fix lease, backup, MCP contradictions)`
- **`/home/evo/AI/forge` (`main` -> `gitea/x3-forge`, `e0f5dc0..a9bce6b`):**
  - `68ac0ff` — `U53 B3+B4: linuxize forge paths to /home/evo and test ralph GPU lock via flock -n`
  - `9680e2b` — `U53 I2: add Ralph loop safety checks (stale fix_plan clear, worktrees, backpressure/skill smoke, diff cap, skills/AGENTS deny)`
  - `8fe09bf` — `U53 I8: update forge-pi.sh L6 note for X3 evo/herdr pane`
  - `a9bce6b` — `U53 I9: pin per-pane PI_CODING_AGENT_DIR for Forge subagent model`
- **`/home/evo/AI/render` (`x3-linux` -> `gitea/x3-render`, `f5e2a67..793f4cd`):**
  - `793f4cd` — `U53 I9: pin per-pane PI_CODING_AGENT_DIR for Render subagent model` *(also pushed existing local `99bc01b` and `a53dedd`)*
- **`/home/derekboone/evo-x3` (`main` -> `gitea/x3-pi-config`, `7129de8..41068a4`):**
  - `25c23e8` — `U53 I8: update pi-chats/forge-pi.sh L6 note for X3 evo/herdr pane`
  - `41068a4` — `U53 I11: add per-run worktree and lease-line convention note and agy launcher template`

---

## Fresh-Clone Dry-Start Output (B4)

Cloned `x3-community` (`1313227`) and `x3-forge` (`68ac0ff`) into `/tmp/u53-b4-restore/AI/{community,forge}`:

```text
extensions dir: OK
AGENTS.md symlink resolves: /tmp/u53-b4-restore/AI/community/agent-shared/AGENTS.md
forge-pi.sh bash -n: OK
ralph.sh bash -n: OK
settings.json valid JSON: OK
no /home/derekboone refs in forge files: OK
provider  model                  context  max-out  thinking  images
x3-local  flash-next             262.1K   32.8K    yes       no
x3-local  flash-next-sub         131.1K   8.2K     yes       no
x3-local  flash-next-uncensored  262.1K   32.8K    yes       no
x3-local  gemma4-heretic         262.1K   32.8K    yes       yes
x3-local  gemma4-heretic-sub     262.1K   4.1K     no        no
x3-local  qwen27b                262.1K   32.8K    yes       no
```

---

## Smoke-Loop Output (B3)

Ran `/home/evo/AI/forge/ralph-community/ralph.sh -Max 3 -CommandOverride ...` with 0-byte `/home/evo/AI/locks/gpu-render.lock` present (archived under `/home/evo/AI/forge/_archive/ralph-smoke-u53-20261116/`):

```text
-rw-r--r--. 1 evo evo 0 Nov 16 16:12 /home/evo/AI/locks/gpu-render.lock
2026-11-16T16:19:09 iter 1 of 3 start
2026-11-16T16:19:09 iter 1 : PI_MEMORY_DIR=/home/evo/AI/fleet-brain/25_memory/shared (process scope, this pass only)
2026-11-16T16:19:11 iter 1 : pass complete rc=0
2026-11-16T16:19:13 iter 2 of 3 start
2026-11-16T16:19:13 iter 2 : PI_MEMORY_DIR=/home/evo/AI/fleet-brain/25_memory/shared (process scope, this pass only)
2026-11-16T16:19:15 iter 2 : pass complete rc=0
2026-11-16T16:19:17 iter 3 of 3 start
2026-11-16T16:19:17 iter 3 : PLAN_COMPLETE - no open item, loop stopped
DONE.txt: iter=3 max=3 done=true reason=plan_complete
```

Negative check (active `flock` held on `/tmp/ralph-u53-b3-smoke/held.lock`):

```text
2026-11-16T16:19:17 iter 1 of 1 start
2026-11-16T16:19:17 iter 1 : GPU_BUSY defers the pass (flock held on /tmp/ralph-u53-b3-smoke/held.lock) - no LLM request while a GPU job runs; waited 0 of 1
2026-11-16T16:19:18 iter 1 : GPU_DEFERRED - the GPU window outlasted 1 waits (flock held on /tmp/ralph-u53-b3-smoke/held.lock); skipping this pass, no LLM request
```

---

## Pytest Totals (Final Run After All Edits)

Python: `/home/evo/AI/render/x3/.venv/bin/python`, CWD: `/home/evo/AI/community/scripts`

- `pytest -q tests`: **`142 passed, 2 skipped`** in `7.13s` (0 failed, 0 errors, 0 xfail)
  - Skipped (`skipUnless` on Linux/missing AlienPc files): `tests/test_b2_lora_param.py:60` (archived `FC_ARIANA.api.json`), `tests/test_web_fetch.py:144` (`C:/AI/community/notes/web`).
- `pytest -q parody`: **`581 passed, 5 skipped`** in `14.22s` (0 failed, 0 errors, 0 xfail)
