# U59 Result

## Run 1 (2026-11-20 10:46:01 CST – 10:49:46 CST, BLOCKED at S2)

- **Overall status:** BLOCKED at S2 (`apply-hermes-workspaces.sh --apply` failed waiting for `flash-next-uncensored-v2` on `/running`)
- **S0 (Preflight):** **DONE** (`mono` at `b683bba` / `b683bba5`, 15 pre-existing dirty entries, lease empty, no active `pi-job-*` units)
- **S1 (`USER.md` cleanup):** **DONE**
  - `default removed 1 entry; 578 -> 488 chars; backup /home/evo/.hermes/_archive/default-USER.md.bak-20261120-u59`
  - `code absent`
  - Lease cleared immediately after (`0` bytes).
- **S2 (`apply-hermes-workspaces.sh`):** **BLOCKED** at Step 1 (`FAIL: flash-next-uncensored-v2 not ready in /running; run --rollback`); `--rollback` exited `0` (`Missing backup: /etc/evo-x3/_archive/llama-swap.yaml-20261120-preWS`).
- **S3, S4, S5, Tests:** **SKIPPED** (blocked at S2).

---

## Run 2 (2026-11-20 11:11:14 CST – 11:13:10 CST, S0–S5 DONE; 4/5 Tests DONE, 1 Test BLOCKED)

- **Start time (CT):** 2026-11-20 11:11:14 CST
- **End time (CT):** 2026-11-20 11:13:10 CST
- **Lease (`/home/derekboone/AI/locks/x3-lease.txt`):** 0 bytes at start, managed by S2/S3 installers, taken and cleared to 0 bytes for S4.

### Steps (S0–S5)

- **S0. Preflight:** **DONE**
  - `git -C ~/evo-x3 status -sb`: `## mono...gitea/mono`
  - `git -C ~/evo-x3 rev-parse HEAD`: `14575c7ddcaaf513e319ad6b919d92168cdc6c0c` (`14575c7`, matches `14575c7d`)
  - `git -C ~/evo-x3 status --porcelain`: exact 15 pre-existing entries from `PREEXISTING-DIRTY.txt`
  - `/home/derekboone/AI/locks/x3-lease.txt`: `0` bytes
  - `sudo -n systemctl --user -M evo@ list-units 'pi-job-*' --no-legend`: no active units (`pi-job-20261120-070728-code…` listed as `loaded failed failed`)
- **S1. Remove stale Hermes memory entry (`USER.md`):** **DONE** (completed in Run 1; confirmed still holds)
  - Confirmed read-only: `default clean=True len=488`, `code absent`
  - Run 1 output lines:
    - `default removed 1 entry; 578 -> 488 chars; backup /home/evo/.hermes/_archive/default-USER.md.bak-20261120-u59`
    - `code absent`
  - Backup path: `/home/evo/.hermes/_archive/default-USER.md.bak-20261120-u59`
- **S2. H7 Hermes workspaces:** **DONE**
  - `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --dry-run`: exited `0`, no `BLOCKED` printed.
  - `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --apply`: exited `0`.
  - H7 RESULT path: `/home/derekboone/evo-x3/records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md`
- **S3. PixlStash PX1 + PX2:** **DONE**
  - `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --status`: exited `0`
  - `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --dry-run`: exited `0`
  - `bash ~/evo-x3/scripts/apply-pixlstash-upgrade.sh --apply`: exited `0`, picker pytest `8 passed in 0.11s`, backups in `/home/evo/AI/_archive/20261120-pixlstash-upgrade`.
- **S4. C0, the REA coding clone:** **DONE**
  - Lease written and cleared to `0` bytes right after.
  - Cloned `mono` into `/home/evo/AI/_worktrees/rea-parody` on branch `pi/rea-parody`, `venv ok`.
- **S5. RESULT and local commit:** **DONE**
  - Updated `/home/derekboone/evo-x3/records/U59-RESULT.md` and committed `records/U59-RESULT.md` and `records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md` by path on `mono` (no push).

### Tests

- **S2 H7 RESULT probes & skills check:** **DONE**
  - Probes in `--apply` output: `PASS flash-next-render: HTTP 200 reasoning=False`, `PASS flash-next-aux: HTTP 200 reasoning=False`, `PASS flash-next-code: HTTP 200 reasoning=True`.
  - Hooks: `All shell hooks look healthy.`
  - Render oneshot names `h3-render` (`h3-render renders video; pi-job handles code (code|review).`).
  - Code oneshot names `pi-job` (`pwd: /home/evo — code changes go through the pi-job skill (pi-job code <repo> "<task>").`).
  - Code skills check: `pi-job` enabled; `h3-render` and `h3-writer` disabled.
- **S2 `pi-job code --help` & `FORGE_KEEP_CWD` check:** **DONE**
  - `pi-job code --help 2>&1 | grep -c -- --timeout-min`: `2`
  - `sudo -n -u evo grep -c FORGE_KEEP_CWD /home/evo/evo-x3/pi-chats/forge-pi.sh`: `2`
- **S3 `pixlstash.service` MemoryHigh / MemoryMax:** **DONE**
  - `MemoryHigh=15032385536`
  - `MemoryMax=17179869184`
- **S3 live picker check (`still_candidate_sheet.py`):** **BLOCKED**
  - Command exited `1` with `urllib.error.HTTPError: HTTP Error 400: Bad Request` in `_fetch_candidates` -> `_get_json(primary_url, tok)`, so no JSON dict was emitted.
- **S4 `rea-parody` branch & venv check:** **DONE**
  - `sudo -n -u evo -H env -C /home/evo git -C /home/evo/AI/_worktrees/rea-parody status -sb`: `## pi/rea-parody`
  - S4 printed `venv ok`

### Required Summary Fields (Run 2)

- **Start / End times (CT):** `2026-11-20 11:11:14 CST` / `2026-11-20 11:13:10 CST`
- **H7 RESULT path:** `/home/derekboone/evo-x3/records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md`
- **S1 output lines and backup paths (from Run 1, confirmed still holding):**
  - `default removed 1 entry; 578 -> 488 chars; backup /home/evo/.hermes/_archive/default-USER.md.bak-20261120-u59`
  - `code absent`
- **S3 memcap values, `memory.events` and dedup counts:**
  - Pre-apply (`--status`): `ActiveState=active`, `MemoryCurrent=10123231232`, `MemoryHigh=10737418240`, `MemoryMax=12884901888`; `memory.events`: `low 0`, `high 7749`, `max 0`, `oom 0`, `oom_kill 0`, `oom_group_kill 0`, `sock_throttled 30`.
  - Post-apply: `ActiveState=active`, `MemoryCurrent=10123337728`, `MemoryHigh=15032385536`, `MemoryMax=17179869184`; `memory.events`: `low 0`, `high 7749`, `max 0`, `oom 0`, `oom_kill 0`, `oom_group_kill 0`, `sock_throttled 30`.
  - Dedup counts (`/api/v1/dedup/counts`): `HTTP_CODE:403` (`{"detail":"Token is read-only"}`) — known non-blocking **FINDING**.
  - Penalised tags count (`/api/v1/users/me/penalised-tags`): `14` (`HTTP_CODE:200`).
  - **FINDING (known non-blocking from launch brief):** live pictures payload names the likeness field `character_likeness`, not `likeness_score` (not directly observed in Run 2 due to the live picker HTTP 400 error).
- **Picker-check dict:** none (BLOCKED on `HTTP Error 400: Bad Request`)
- **S4 branch line:** `## pi/rea-parody`
- **Every rollback run:** none in Run 2 (Run 1 ran `bash ~/evo-x3/scripts/apply-hermes-workspaces.sh --rollback`)
- **Local commit SHA:** committed in S5 on `mono` (see `git -C ~/evo-x3 log -1 --format=%H` and final report)
