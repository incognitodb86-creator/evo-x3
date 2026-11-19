Goal: Apply unified-plan `mono` groups 1-3 on the EVO-X3 (R5, ST2+L4 desk text, ST1, W3a, RV1, RV2, H5, H4, L7, ST3+L2 pair, H3 units) under the X3 lease, stopping on first failure in any group.

# UNI-APPLY-X3-A (X3 Forge): Apply unified-plan groups 1-3 on EVO-X3, Nov 19 2026

Authority: Derrick 2026-11-19 11:11/11:16 CT (Card 2 file-only work + Forge execution strategy) and `records/unified-implementation/PLAN.md` + `records/unified-implementation/CODE-REVIEW-20261119-opus-delta.md` ("Apply order for Max", groups 1-3, X3 side). Max verifies your `RESULT.md` afterwards.

## Needs before launch (Max / Derrick checklist — do not launch until met)
- **Derrick's live yes** for applying groups 1-3 on EVO-X3 (Card 1 live apply, Card 26 ST1 default, Card 12 `P4.11` ntfy token confirmed for H3 timers).
- **X3 lease taken** (`30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-taken-x3-forge-uni-apply-x3-a.md`, mirrored to `records/status/`). Max writes/mirrors take and release files on brief issue/closeout unless X3 Forge is verified writable to the brain (Card 28 / M2).
- **No active render** on X3/AlienPc (required for R5 and `sync-renders`), and **not during the Hermes bakeoff window** (Plan C16).
- **Max import + pre-cutover bridge complete** from `mono` tip `5ccba67` (or newer):
  - `gitleaks` clean on `947aa26..mono`; Gitea `mono` fast-forwarded (or merged, never force-pushed).
  - Until `MONO-S5` passes smoke: Max bridges `x3/render/` commits onto Gitea `x3-render` (never `x3-linux`) via `git format-patch --relative=x3/render/ <range>` + `git am`, and `x3/community/` commits onto Gitea `x3-community` via `git format-patch --relative=x3/community/ <range>` + `git am`, then pushes both part branches to Gitea. (After `MONO-S5`, live checkouts pull `mono` directly.)
  - Root-copy files (`config/`, `hosts/`) are read from the fetched `mono` checkout at `/home/derekboone/evo-x3` (or Max's staged path) and installed per the Install table below.

- **If `MONO-S5` already passed:** `/home/evo/AI/render` and `/home/evo/AI/community` are symlinks into the `mono` clone; skip the part-branch bridge and run `git -C /home/evo/AI/evo-x3 pull --ff-only` instead. Everything else in this brief is unchanged.

## Access & Lease
- **Doer:** X3 Forge (`/home/evo/AI/forge`, pi panes `w4:p1-p3`), running as `evo`. Use `sudo` only where an Install row says `sudo: yes` (`/usr/local/bin/sync-renders`).
- **Live checkouts:** `/home/evo/AI/render` (Gitea `x3-render`), `/home/evo/AI/community` (Gitea `x3-community`), `/home/derekboone/evo-x3` (`mono`, read-only source for root-copy installs).
- **Backup root:** `/home/evo/AI/_archive/20261119/` (create `mkdir -p /home/evo/AI/_archive/20261119/{hermes,systemd-user,rea-video-capabilities}` first).
- **Lease take:** `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-taken-x3-forge-uni-apply-x3-a.md` (mirrored to `records/status/`).
- **Lease release:** `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-released-x3-forge-uni-apply-x3-a.md` (mirrored to `records/status/`).

## Work (stop on first failure in any group)

### Group 1 — Docs, data, and low-risk poll change

1. **R5 (`queue-remote.sh` 5 s poll)** — Source on `mono`: `x3/render/x3/queue-remote.sh` (`73b5390`).
   - Confirm no render is running (`ps aux | grep -E 'queue-remote|run_queue' | grep -v grep` is empty).
   - Back up `/home/evo/AI/render/x3/queue-remote.sh` to `/home/evo/AI/_archive/20261119/queue-remote.sh`.
   - Bridge apply: `git -C /home/evo/AI/render pull --ff-only gitea x3-render` (this single pull also brings items 2 and 4 if Max bridged `x3/render/` together; back up items 2 and 4 first before pulling!).
   - Verify: `bash -n /home/evo/AI/render/x3/queue-remote.sh && grep -n "sleep 5" /home/evo/AI/render/x3/queue-remote.sh`.
   - Rollback: copy `/home/evo/AI/_archive/20261119/queue-remote.sh` back (or `git revert` on `x3-render`, no force).

2. **ST2 desk text + L4 `OPERATOR.md` line** — Source on `mono`: `x3/render/OPERATOR.md` (`abb6235`, `19ffe51`), `x3/render/RUN_ME.md` (`abb6235`).
   - Back up `/home/evo/AI/render/OPERATOR.md` and `/home/evo/AI/render/RUN_ME.md` to `/home/evo/AI/_archive/20261119/` before the `x3-render` pull.
   - Bridge apply: same `x3-render` `--ff-only` pull in `/home/evo/AI/render`. (Hermes `h3-writer` addendum stays held.)
   - Verify: `grep -n "NOT_READY" /home/evo/AI/render/OPERATOR.md /home/evo/AI/render/RUN_ME.md` and `grep -n "contact_sheet.jpg" /home/evo/AI/render/OPERATOR.md`.
   - Rollback: restore backups from `/home/evo/AI/_archive/20261119/` (or `git revert`, no force).

3. **RV1 (`rea-video` user capability YAML)** — Source on `mono`: `x3/community/agent-shared/rea-video/capabilities/models/video.yaml`, `x3/community/agent-shared/rea-video/capabilities/prompting.yaml`, `x3/community/agent-shared/rea-video/README.md`, `x3/community/scripts/tests/test_rv1_capabilities.py` (`d83ac47`).
   - Before pulling `x3-community`, back up `/home/evo/AI/community/agent-shared/AGENTS.md` to `/home/evo/AI/_archive/20261119/community-AGENTS.md` (for item 7).
   - Bridge apply: `git -C /home/evo/AI/community pull --ff-only gitea x3-community`. (Note: X3-side ST4/ST5 inert candidate templates `templates/flux_stills_{t2i,pose,layout}_klein.candidate.api.json`, mono `fc540d3`/`3861193`, ride along on this pull — do not promote them.)
   - User YAML install: back up any existing `/home/evo/.rea-video/capabilities/` to `/home/evo/AI/_archive/20261119/rea-video-capabilities/`, then copy `video.yaml` -> `/home/evo/.rea-video/capabilities/models/video.yaml` and `prompting.yaml` -> `/home/evo/.rea-video/capabilities/prompting.yaml` (`evo:evo 0644`, sudo: **no**).
   - Verify: `pytest -q /home/evo/AI/community/scripts/tests/test_rv1_capabilities.py` (2 passed). If `rea-video` (RV0) is already installed, also run `rea-video models minimax-h3-10eros-beta7` and `python3 /home/evo/AI/tools/rea-video/scripts/validate_capabilities.py`; otherwise mark the live CLI check SKIPPED (RV0 not installed).
   - Rollback: restore `/home/evo/AI/_archive/20261119/rea-video-capabilities/` and `git revert` on `x3-community` if needed.

### Group 2 — Code, harness, Hermes skills prune, and pi syntax-check extension

4. **ST1 (fresh candidate sheet)** — Source on `mono`: `x3/render/x3/still_candidate_sheet.py`, `x3/render/x3/test_still_candidate_sheet.py` (`d7320bb`).
   - Back up `/home/evo/AI/render/x3/still_candidate_sheet.py` to `/home/evo/AI/_archive/20261119/still_candidate_sheet.py` before the `x3-render` pull.
   - Bridge apply: landed via the `x3-render` pull in item 1.
   - Verify: `/home/evo/AI/render/x3/.venv/bin/python3 -m unittest discover -s /home/evo/AI/render/x3 -p "test_still_candidate_sheet.py" -v` (5 passed).
   - Rollback: restore `/home/evo/AI/_archive/20261119/still_candidate_sheet.py` (or `git revert`, no force).

5. **W3a (shared Beta 7 prompt converter)** — Source on `mono`: `x3/community/scripts/parody/beta7_convert.py`, `x3/community/scripts/parody/test_beta7_convert.py` (`49c6de6`).
   - Bridge apply: landed via the `x3-community` pull in item 3.
   - Verify: `pytest -q /home/evo/AI/community/scripts/parody/test_beta7_convert.py` (5 passed; covers `wp_lint.lint` READY + 0 header violations).
   - Rollback: `git revert` on `x3-community` (no force).

6. **RV2 (`h3max_bridge` H5 package)** — Source on `mono`: `x3/community/scripts/h3max_bridge/{AGENTS.md,Makefile,pyproject.toml,src/h3max_bridge/__init__.py,src/h3max_bridge/h3max_bridge.py,tests/test_h3max_bridge.py}` (`6be684a`).
   - Bridge apply: landed via the `x3-community` pull in item 3.
   - Verify: `make -C /home/evo/AI/community/scripts/h3max_bridge check-all` (ruff + ty + pytest 6 passed).
   - Rollback: `git revert` on `x3-community` (no force).

7. **H5 files (Python harness + `AGENTS.md` gate)** — Source on `mono`: `x3/community/agent-shared/AGENTS.md`, `x3/community/agent-shared/python-harness/uv-template/**` (6 files), `x3/community/agent-shared/python-harness/sample-tool/**` (6 files) (`a823877`).
   - Bridge apply: landed via the `x3-community` pull in item 3 (backup of `AGENTS.md` already taken in item 3).
   - Verify: `make -C /home/evo/AI/community/agent-shared/python-harness/sample-tool check-all` (ruff + ty + pytest 3 passed).
   - Rollback: restore `/home/evo/AI/_archive/20261119/community-AGENTS.md` and `git revert` on `x3-community` (no force).

8. **H4 (archive 27 Hermes skills + install `pi-job` SKILL.md)** — Source on `mono`: `hosts/x3/hermes/SKILLS-PRUNE.md`, `hosts/x3/hermes/skills/pi-job/SKILL.md` (`9b796d9`).
   - Install table: dest `/home/evo/.hermes/skills/pi-job/SKILL.md`, owner/mode `evo:evo 0644`, sudo: **no**, backup `/home/evo/AI/_archive/20261119/hermes/skills/`.
   - Copy `/home/evo/.hermes/skills/` to `/home/evo/AI/_archive/20261119/hermes/skills/` before changes.
   - Create `/home/evo/.hermes/skills-archived/` and move the exact 27 skills listed for removal in `hosts/x3/hermes/SKILLS-PRUNE.md` into `/home/evo/.hermes/skills-archived/` (leaving 18 active skills; `h3-writer` remains reserved).
   - Install `hosts/x3/hermes/skills/pi-job/SKILL.md` -> `/home/evo/.hermes/skills/pi-job/SKILL.md` (`0644`, `evo:evo`).
   - Verify: run Hermes skill loader check confirming `SKILL_SMOKE_OK` (18 active skills, 0 broken paths, valid `pi-job` YAML frontmatter). Do **not** merge `hosts/x3/hermes/config.yaml` (H2 stays held until live SSRF proxy + H1a + Derrick yes).
   - Re-snapshot: run `scripts/snapshot-live-setup.sh`.
   - Rollback: move archived skills back from `/home/evo/.hermes/skills-archived/` and restore `/home/evo/AI/_archive/20261119/hermes/skills/`.

9. **L7 (`syntax-check.ts` pi extension)** — Source on `mono`: `config/pi-evo/extensions/syntax-check.ts` (`53cde1c`, `eda5b67`).
   - Install table: dest `/home/evo/.pi/agent/extensions/syntax-check.ts`, owner/mode `evo:evo 0644`, sudo: **no**, backup `/home/evo/AI/_archive/20261119/syntax-check.ts` (if pre-existing).
   - Verify (broken-file test on box): load pi with the extension and edit a throwaway broken `.py` (and `.sh` / `.json`) under `/tmp/l7-test-$$` to confirm syntax-check stderr is appended to tool output and **no `__pycache__`** directory is created. Remove `/tmp/l7-test-$$` afterwards.
   - Rollback: remove `/home/evo/.pi/agent/extensions/syntax-check.ts` (or restore backup).

### Group 3 — ST3 pair (`sync-renders` + `import_inbox.py`), L2 poster frame, and H3 units

10. **ST3 pair + L2 (`sync-renders` + `import_inbox.py`, install together)** — Source on `mono`:
    - `config/bin/sync-renders` (`79a706a`, `60ef314`, `a5a86ce`) -> `/usr/local/bin/sync-renders` | `root:root 0755` | sudo: **yes** | backup `/home/evo/AI/_archive/20261119/sync-renders`
    - `hosts/x3/pixlstash-tagging/import_inbox.py` (`79a706a`, `a5a86ce`) -> `/home/evo/AI/pixlstash-tagging/import_inbox.py` | `evo:evo 0755` | sudo: **no** | backup `/home/evo/AI/_archive/20261119/import_inbox.py`
    - Pre-install syntax check: `bash -n <mono>/config/bin/sync-renders && python3 -m py_compile <mono>/hosts/x3/pixlstash-tagging/import_inbox.py`.
    - Back up both live files to `/home/evo/AI/_archive/20261119/` and install both together. (Do **not** edit `pixlstash.service.d/10-memcap.conf` — ST3(c) is held for Card 23.)
    - Exact ST3 + L2 checks:
      1. `bash -n /usr/local/bin/sync-renders && python3 -m py_compile /home/evo/AI/pixlstash-tagging/import_inbox.py`.
      2. Trigger one sync (`systemctl --user start evo-renders-sync.service` or run `/usr/local/bin/sync-renders` with no active render) and verify sync exits in `< 30 s`.
      3. Confirm `pixl-import.service` stays active after `sync-renders` exits (when inbox is non-empty) AND a concurrent second `import_inbox.py` run against the same inbox returns `stopped_reason="locked"` without touching files.
      4. L2 check: confirm the poster-frame ffmpeg block in `/usr/local/bin/sync-renders` passes `bash -n` and (if a synced 2x clip exists) test poster extraction to `/tmp/l2-test.jpg` (remove `/tmp/l2-test.jpg` after) or confirm `/srv/renders/<run_id>.jpg` on the next synced clip.
      5. Note MINOR N5: non-hidden sidecar files in the inbox will harmlessly re-trigger `pixl-import`; do not patch here, just note in `RESULT.md` if observed.
    - Re-snapshot: run `scripts/snapshot-live-setup.sh` and `scripts/sync-config-copies.sh`.
    - Rollback: restore `/home/evo/AI/_archive/20261119/sync-renders` (`sudo install -o root -g root -m 0755`) and `/home/evo/AI/_archive/20261119/import_inbox.py` (`install -m 0755`).

11. **H3 read-only ntfy systemd user units** — Source on `mono`: `hosts/x3/systemd/user/evo-morning-status.{service,timer}`, `hosts/x3/systemd/user/evo-weekly-worktrees.{service,timer}` (`6d54d3e`, `c49ef7a`).
    - Install table: dest `/home/evo/.config/systemd/user/`, owner/mode `evo:evo 0644`, sudo: **no**, backup `/home/evo/AI/_archive/20261119/systemd-user/` (if existing).
    - Run `systemctl --user daemon-reload && systemctl --user enable --now evo-morning-status.timer evo-weekly-worktrees.timer`.
    - Verify:
      1. `systemd-analyze --user verify /home/evo/.config/systemd/user/evo-morning-status.service /home/evo/.config/systemd/user/evo-weekly-worktrees.service`.
      2. `systemctl --user list-timers evo-morning-status.timer evo-weekly-worktrees.timer` (confirm 07:00 daily and Sun 08:00 weekly — outside 04:00 JoyCaption window).
      3. Run `systemctl --user start evo-morning-status.service` once (requires `P4.11` ntfy token in place) and verify exit 0, one ntfy message sent with 0 secrets, and 0 llama-swap model swaps.
    - Re-snapshot: run `scripts/snapshot-live-setup.sh`.
    - Rollback: `systemctl --user disable --now evo-morning-status.timer evo-weekly-worktrees.timer`, remove the 4 unit files (or restore backup), and `systemctl --user daemon-reload`.

## Rules
- **Stop on first failure in any group.** Do not skip a failed install/test and continue mutating later items in the same group.
- No `llama-swap.yaml` edits. No service restarts beyond `systemctl --user daemon-reload` / enabling the H3 timers and triggering `evo-renders-sync.service`.
- No renders. Nothing runs during an active render.
- Never read, print, or copy secrets (`auth.json`, `mcp.json`, `models.json`, `.env`, `*.token`, `/etc/evo-x3/*`, `~/.ssh`). Never view PixlStash library contents.
- Cite `mono` SHAs (never worker branch SHAs) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-A/RESULT.md`, then stop. List each item (1-11) as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs, backup paths, exact verify commands + pass/fail outputs, snapshot confirmation, and rollback status if triggered.
