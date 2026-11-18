# PLAN-v3.2 Phase 1 Result (`P1.1`–`P1.5` Complete; Stopped at `P1.6 Y`–`P1.8 Y`)

- **Date:** 2026-11-18 15:51 CST
- **Branch / Base commit:** `evo-x3` branch `u58` (`47cbc8a`)
- **X3 Lease (`/home/derekboone/AI/locks/x3-lease.txt`):** `0` bytes
- **Status:** `P1.1`–`P1.5` **PASS**; stopped at **`P1.6 Y`**, **`P1.7 Y`**, **`P1.8 Y`** awaiting Derrick's approval (`P1.9` and `P1.10` follow after `P1.6`–`P1.8`).
- **Pre-approved (`3:49 PM CT`):** Derrick pre-approved **`P3.1`** to cut over the permanent resident slot to **Gufo `0.35.0` + Huihui v2 GGUF** (G0 winner) when execution reaches Phase 3, keeping Halogen v2 config as rollback.

---

## 1. Completed Phase 1 Steps (`P1.1`–`P1.5`)

| ID | Summary | Verification & Real Output |
|---|---|---|
| **P1.1 (B4 / I12)** | Verified `/home/evo/AI/forge` (`u58-chat-read-plan`, `44bc639`) and `/home/evo/AI/community` (`x3-linux`, `59831a2`) push to `gitea` (`https://qnap.tailf242b2.ts.net/derrick/evo-x3.git`), use `/home/evo` paths, and keep `/home/evo/AI/community/agent-shared/extensions` (`.gitkeep`). Thursday multi-branch fold (`u58`, `alienpc-community`, `alienpc-render`, `x3-*`) remains scheduled for Thursday; `I12` `evo` Gitea token status recorded per `U53-RESULT.md`. | `git branch -vv` & `git remote -v` verified in `/home/evo/AI/forge` and `/home/evo/AI/community`; `x3-linux` pushed to `gitea/x3-community` cleanly. |
| **P1.2 (B3 lock)** | Confirmed `ralph.sh` (`flock -n "$GpuLockPath" true`), `queue-remote.sh` (`flock -n "$LOCK" true`), and `run_queue.py --remote` (`remote_comfy.py` `fcntl.flock(..., LOCK_EX \| LOCK_NB)`) all use `flock`. Removed unused stale 0-byte `/home/derekboone/AI/locks/gpu-render.lock` (Nov 16). Verified live 0-byte `/home/evo/AI/locks/gpu-render.lock` reports free (`flock -n` exit `0`). | 2-item Ralph smoke test (`-CommandOverride`) completed 2 passes + `PLAN_COMPLETE` in **`8s`** (0 waits); `queue-remote.sh /home/evo/AI/community/runs/sydney_hesitant_stand --yes-derrick --dry-run` ran cleanly (`probe: :8446 answered HTTP Error 409: Conflict`, `dry run: no lock, upload or POST made`); post-dry-run 2-item Ralph loop completed in **`8s`** (`PLAN_COMPLETE`, 0 waits). |
| **P1.3 (I2 Ralph safety)** | Verified `/home/evo/AI/forge/ralph-community/ralph.sh` clears stale `fix_plan.md` items (`>12h`), runs per-loop worktrees (`~/AI/_worktrees`), enforces skill-load smoke test (`SKILL_SMOKE_OK`), enforces `git diff --stat` file cap (`-MaxDiffFiles 10`), and denies edits to `skills/` and `AGENTS.md` (`PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR`). | Live smoke run triggered `STALE_FIX_PLAN_CLEARED (fix_plan.md older than 12h (99577s))` archiving stale Nov 17 `fix_plan.md` to `/home/evo/AI/forge/ralph-community/_archive/fix_plan.stale-20261118-153518.md`, and logged `SKILL_SMOKE_OK skills=1 changed_files=0` and `BACKPRESSURE_OK (changed_files=0 cap=10)` on every pass. |
| **P1.4 (I3 xfail)** | Backed up `/home/evo/AI/community/scripts/tests/test_p6_review.py` to `scripts/tests/_archive/test_p6_review.py.bak-20261118-p14`. Wrapped `Clips.setUpClass` `ffmpeg` setup to catch `RuntimeError("U3 CPU fixture blocked ...")` from `parody/test_c2v_context.py`'s process-wide `sys.addaudithook`, and called `pytest.xfail(...)` in `Clips.setUp`. Committed and pushed on `x3-linux` (`59831a2`). | Standalone: `pytest -q -p no:cacheprovider tests/test_p6_review.py` -> **`21 passed in 3.09s`**.<br>Combined: `pytest -q -p no:cacheprovider tests parody` -> **`689 passed, 3 skipped, 6 xfailed in 7.69s`** (exit `0`, `0 errors`, `0 failed`). |
| **P1.5 (I8 AGENTS.md)** | Backed up `/home/evo/AI/community/agent-shared/AGENTS.md` to `agent-shared/_archive/AGENTS.md.bak-20261118-p15`. Replaced the `_archive/*.bak` rule with `- Commit to git; etckeeper for /etc (no .bak copies).` and updated the test gate line to `6 xfailed` (`0 errors, 0 failed`). Verified `/home/evo/.pi/agent/AGENTS.md` (8 lines) and `/home/evo/AI/forge/AGENTS.md` symlink have no contradictions. Committed and pushed (`59831a2` on `gitea/x3-community`). | Diff reviewed; `x3-linux` pushed cleanly (`bdb49f0..59831a2 x3-linux -> x3-community`). |

---

## 2. Open Questions Requiring Derrick's **Y** (`P1.6 Y`–`P1.8 Y`)

1. **`P1.6 Y` (I9 — `pi-subagents` upgrade + subagent model/inheritance):**
   - Currently `npm:pi-subagents@0.83.1` is installed in `/home/evo/.pi/agent/settings.json` and `/home/evo/.pi/panes/*/settings.json`. Also, `/home/evo/.pi/agent/settings.json` still lists `subagents.defaultModel: "x3-local/flash-next-sub"` and `/home/evo/.pi/panes/render/settings.json` lists `"x3-local/flash-next-uncensored-v2"` instead of `flash-next-uncensored-v2-sub` (131K context, low reasoning effort).
   - **Question:** Do I have your yes to upgrade `pi-subagents` to `0.88.1` or later, enable explicit context inheritance, and align `subagents.defaultModel` across user and pane settings to `x3-local/flash-next-uncensored-v2-sub` (so subagents never load a new model or use 262K)?

2. **`P1.7 Y` (B1 — `agy` runs as `evo` with worktree + time limit):**
   - Currently `agy` runs on the X3 execute as `derekboone` (with sudo).
   - **Question:** Do I have your yes to update the `agy` launcher convention/template (`~/evo-x3/records/agy-launch-TEMPLATE.sh` / new `evo`-safe wrapper) so future `agy` coding runs execute as user `evo` (no sudo), inside a per-job git worktree under `~/AI/_worktrees`, with a hard wall-clock `timeout`, and verify a test `agy` job cannot `sudo` and stops at its limit?

3. **`P1.8 Y` (B2 / OD2 — Forge-X3 permission prompts vs headless deny):**
   - **Question:** Do I have your yes to update `/home/evo/.pi/agent/pi-permissions.jsonc` (and headless Ralph/job policy) so interactive `Forge-X3` prompts for confirmation before vault reads, Gitea writes, and outbound sends, while headless runs (`ralph.sh`, `pi-job`) deny those tools outright, and verify with the planted `"read the vault"` check in both Forge-X3 and Ralph?
