Goal: Apply unified-plan `mono` groups 1-3 on the EVO-X3 (R5, ST2+L4 desk text, ST1, W3a, RV1, RV2, H5, H4, L7, ST3+L2 pair, H3 units) under the X3 lease, stopping on first failure in any group.

# UNI-APPLY-X3-A (X3 Forge): Apply unified-plan groups 1-3 on EVO-X3, Nov 19 2026

Authority: Derrick 2026-11-19 11:11/11:16 CT (Card 2 file-only work + Forge execution strategy) and `records/unified-implementation/PLAN.md` + `records/unified-implementation/CODE-REVIEW-20261119-opus-delta.md` ("Apply order for Max", groups 1-3, X3 side). Max verifies your `RESULT.md` afterwards.

## Needs before launch (Max / Derrick checklist — do not launch until met)
- **Derrick's live yes in chat:** Card 1 (live apply), Card 26 (`ST1` default), and Card 12 (`P4.11` ntfy token for H3 timers) answered in chat (Max records id).
- **X3 lease free** (`/home/derekboone/AI/locks/x3-lease.txt` empty). The doer takes it at start (one line, see Access & Lease). No lease-taken/released files, no brain or `records/status/` mirrors, no git commit for the lease, no message to Derrick.
- **No active render** on X3/AlienPc (required for R5 and `sync-renders`), and **not during the Hermes bakeoff window** (Plan C16).
- **Max import + pre-cutover bridge complete** from `mono` tip `bab584a (or newer at Max import)`:
  - **ONE BRANCH (`mono` ONLY — Derrick 2026-11-19 ~13:05 CT):** `mono` is the ONLY branch anyone pushes from now on (no further pushes to `x3-render`, `x3-community`, `alienpc-*`, or `u58` anywhere). `gitleaks` clean on `947aa26..mono`; Gitea `mono` fast-forwarded (or merged, never force-pushed).
  - Until `MONO-S5` passes smoke: Max's 12:49 CT bridge pushes (`x3-render` `a24f81b`, `x3-community` `f90c5bb`) already carry ST1, R5, ST2, L4, W3a, H5, RV1, RV2, ST4, and ST5, so this brief's `--ff-only` pulls stay valid. For any newer `x3/*` change before `MONO-S5`, Max applies it **locally** onto the live checkout (`git format-patch --relative=<prefix>/ <range>` + `git am` or staged patch) and does **NOT** push any part branch. (After `MONO-S5`, live checkouts pull `mono` directly.)
  - Root-copy files (`config/`, `hosts/`) are read from the fetched `mono` checkout at `/home/derekboone/evo-x3` (or Max's staged path) and installed per the Install table below.

- **If `MONO-S5` already passed:** `/home/evo/AI/render` and `/home/evo/AI/community` are symlinks into the `mono` clone; skip the part-branch bridge and run `git -C /home/evo/AI/evo-x3 pull --ff-only` instead. Everything else in this brief is unchanged.

## Access & Lease
- **Doer:** X3 Forge (`/home/evo/AI/forge`, pi panes `w4:p1-p3`), running as `evo`. Use `sudo` only where an Install row says `sudo: yes` (`/usr/local/bin/sync-renders`).
- **Live checkouts:** `/home/evo/AI/render` (Gitea `x3-render`), `/home/evo/AI/community` (Gitea `x3-community`), `/home/derekboone/evo-x3` (`mono`, read-only source for root-copy installs).
- **Backup root:** `/home/evo/AI/_archive/20261119/` (create `mkdir -p /home/evo/AI/_archive/20261119/{hermes,systemd-user,rea-video-capabilities}` first).
- **Lease take:** write ONE line to `/home/derekboone/AI/locks/x3-lease.txt`: `x3-forge | UNI-APPLY-X3-A | <start time>`. If the file is not empty, stop.
- **Lease release:** truncate `/home/derekboone/AI/locks/x3-lease.txt` (`: > /home/derekboone/AI/locks/x3-lease.txt`) when done or blocked. No status files, mirrors, commits, or messages for the lease.

## Work (stop on first failure in any group)

### Step 0 — Pre-pull dirty check, HEAD record, and backups (run before any pull)
- Confirm no render is running: `ps aux | grep -E 'queue-remote|run_queue' | grep -v grep` (must be empty).
- Check live checkouts for dirty touched paths:
  ```bash
  git -C /home/evo/AI/render status --porcelain
  git -C /home/evo/AI/community status --porcelain
  ```
  **STOP** if any file touched by items 1–7 is dirty.
- Record pre-pull HEADs for `RESULT.md` and rollback:
  ```bash
  git -C /home/evo/AI/render rev-parse HEAD
  git -C /home/evo/AI/community rev-parse HEAD
  ```
- Create backup dirs and take all pre-pull backups first:
  ```bash
  mkdir -p /home/evo/AI/_archive/20261119/{hermes,systemd-user,rea-video-capabilities}
  cp -a /home/evo/AI/render/x3/queue-remote.sh /home/evo/AI/_archive/20261119/queue-remote.sh
  cp -a /home/evo/AI/render/OPERATOR.md /home/evo/AI/_archive/20261119/OPERATOR.md
  cp -a /home/evo/AI/render/RUN_ME.md /home/evo/AI/_archive/20261119/RUN_ME.md
  cp -a /home/evo/AI/render/x3/still_candidate_sheet.py /home/evo/AI/_archive/20261119/still_candidate_sheet.py
  cp -a /home/evo/AI/community/agent-shared/AGENTS.md /home/evo/AI/_archive/20261119/community-AGENTS.md
  ```

### Group 1 — Docs, data, and low-risk poll change

1. **R5 (`queue-remote.sh` 5 s poll)** — Source on `mono`: `x3/render/x3/queue-remote.sh` (`73b5390`).
   - Bridge apply (after Step 0 backups): `git -C /home/evo/AI/render pull --ff-only gitea x3-render` (also lands items 2 and 4).
   - Verify: `bash -n /home/evo/AI/render/x3/queue-remote.sh && grep -n "sleep 5" /home/evo/AI/render/x3/queue-remote.sh`.
   - Rollback: restore `/home/evo/AI/_archive/20261119/queue-remote.sh` or `git -C /home/evo/AI/render revert --no-edit <pre-pull-HEAD>..HEAD` (no force).

2. **ST2 desk text + L4 `OPERATOR.md` line** — Source on `mono`: `x3/render/OPERATOR.md` (`abb6235`, `19ffe51`), `x3/render/RUN_ME.md` (`abb6235`).
   - Bridge apply: landed via the `x3-render` pull in item 1 (backed up in Step 0; docs only, for the legacy pi Render chat — **primary path is Hermes (`h3-writer` addendum, held with H9)**).
   - Verify: `grep -n "NOT_READY" /home/evo/AI/render/OPERATOR.md /home/evo/AI/render/RUN_ME.md` and `grep -n "contact_sheet.jpg" /home/evo/AI/render/OPERATOR.md`.
   - Rollback: restore backups from `/home/evo/AI/_archive/20261119/` or `git revert` to `<pre-pull-HEAD>` (no force).

3. **RV1 (`rea-video` user capability YAML)** — Source on `mono`: `x3/community/agent-shared/rea-video/capabilities/models/video.yaml`, `x3/community/agent-shared/rea-video/capabilities/prompting.yaml`, `x3/community/agent-shared/rea-video/README.md`, `x3/community/scripts/tests/test_rv1_capabilities.py` (`d83ac47`).
   - Bridge apply (after Step 0 backups): `git -C /home/evo/AI/community pull --ff-only gitea x3-community`. (X3-side ST4/ST5 inert candidate templates `templates/flux_stills_{t2i,pose,layout}_klein.candidate.api.json`, mono `fc540d3`/`3861193`, ride along on this pull — do not promote them.)
   - User YAML install: back up any existing `/home/evo/.rea-video/capabilities/` to `/home/evo/AI/_archive/20261119/rea-video-capabilities/`, then copy `video.yaml` -> `/home/evo/.rea-video/capabilities/models/video.yaml` and `prompting.yaml` -> `/home/evo/.rea-video/capabilities/prompting.yaml` (`evo:evo 0644`, sudo: **no**).
   - Verify: `pytest -q /home/evo/AI/community/scripts/tests/test_rv1_capabilities.py` (2 passed). If `rea-video` (RV0) is already installed, also run `rea-video models minimax-h3-10eros-beta7` and `python3 /home/evo/AI/tools/rea-video/scripts/validate_capabilities.py`; otherwise mark the live CLI check SKIPPED (RV0 not installed).
   - Rollback: restore `/home/evo/AI/_archive/20261119/rea-video-capabilities/` and `git revert` on `x3-community` to `<pre-pull-HEAD>` if needed.

### Group 2 — Code, harness, Hermes skills prune, and pi syntax-check extension

4. **ST1 (fresh candidate sheet)** — Source on `mono`: `x3/render/x3/still_candidate_sheet.py`, `x3/render/x3/test_still_candidate_sheet.py` (`d7320bb`).
   - Bridge apply: landed via the `x3-render` pull in item 1 (backed up in Step 0).
   - Verify: `/home/evo/AI/render/x3/.venv/bin/python3 -m unittest discover -s /home/evo/AI/render/x3 -p "test_still_candidate_sheet.py" -v` (5 passed).
   - Rollback: restore `/home/evo/AI/_archive/20261119/still_candidate_sheet.py` or `git revert` to `<pre-pull-HEAD>` (no force).

5. **W3a (shared Beta 7 prompt converter)** — Source on `mono`: `x3/community/scripts/parody/beta7_convert.py`, `x3/community/scripts/parody/test_beta7_convert.py` (`49c6de6`).
   - Bridge apply: landed via the `x3-community` pull in item 3.
   - Verify: `pytest -q /home/evo/AI/community/scripts/parody/test_beta7_convert.py` (5 passed; covers `wp_lint.lint` READY + 0 header violations).
   - Rollback: `git revert` on `x3-community` to `<pre-pull-HEAD>` (no force).

6. **RV2 (`h3max_bridge` H5 package)** — Source on `mono`: `x3/community/scripts/h3max_bridge/{AGENTS.md,Makefile,pyproject.toml,src/h3max_bridge/__init__.py,src/h3max_bridge/h3max_bridge.py,tests/test_h3max_bridge.py}` (`6be684a`).
   - Bridge apply: landed via the `x3-community` pull in item 3.
   - Verify: `make -C /home/evo/AI/community/scripts/h3max_bridge check-all` (ruff + ty + pytest 6 passed).
   - Rollback: `git revert` on `x3-community` to `<pre-pull-HEAD>` (no force).

7. **H5 files (Python harness + `AGENTS.md` gate)** — Source on `mono`: `x3/community/agent-shared/AGENTS.md`, `x3/community/agent-shared/python-harness/uv-template/**` (6 files), `x3/community/agent-shared/python-harness/sample-tool/**` (6 files) (`a823877`).
   - Bridge apply: landed via the `x3-community` pull in item 3 (backup of `AGENTS.md` taken in Step 0).
   - Verify: `make -C /home/evo/AI/community/agent-shared/python-harness/sample-tool check-all` (ruff + ty + pytest 3 passed).
   - Rollback: restore `/home/evo/AI/_archive/20261119/community-AGENTS.md` and `git revert` on `x3-community` to `<pre-pull-HEAD>` (no force).

8. **H4 (archive pruned Hermes skills + install `pi-job` SKILL.md)** — Source on `mono`: `hosts/x3/hermes/SKILLS-PRUNE.md`, `hosts/x3/hermes/skills/pi-job/SKILL.md` (`9ebe5a0`, rebased on live snapshot `eabc8c7`, plus **`ef1fc2b` L9** `MEDIA:` inline-clip lines — install from the same `mono` tip).
   - Install table: dest `/home/evo/.hermes/skills/pi-job/SKILL.md`, owner/mode `evo:evo 0644`, sudo: **no**, backup `/home/evo/AI/_archive/20261119/hermes/skills/`.
   - Copy `/home/evo/.hermes/skills/` to `/home/evo/AI/_archive/20261119/hermes/skills/` before changes.
   - Create `/home/evo/.hermes/skills-archived/` and move the skills listed for removal in `/home/derekboone/evo-x3/hosts/x3/hermes/SKILLS-PRUNE.md` into `/home/evo/.hermes/skills-archived/` (leaving **19** active skills — `pixlstash-image-library` kept; `h3-writer` remains reserved).
   - Install: `install -m 0644 /home/derekboone/evo-x3/hosts/x3/hermes/skills/pi-job/SKILL.md /home/evo/.hermes/skills/pi-job/SKILL.md`.
   - Verify: run `hermes skills list` — expected: **19** active skills (`pixlstash-image-library` and `pi-job` listed), 0 broken paths / frontmatter errors.
   - **H2 comment copy (delta #14, `hosts/x3/hermes/config.yaml`, mono `ef51f83`):** `SKIPPED (held with H2)` — do **not** merge `config.yaml` until live SSRF proxy + H1a + Derrick yes; record as `SKIPPED (held with H2)` in `RESULT.md`.
   - Re-snapshot: **Max closeout step** (record `snapshot: pending Max` in `RESULT.md`).
   - Rollback: move archived skills back from `/home/evo/.hermes/skills-archived/` and restore `/home/evo/AI/_archive/20261119/hermes/skills/`.

9. **L7 (`syntax-check.ts` pi extension)** — Source on `mono`: `config/pi-evo/extensions/syntax-check.ts` (`53cde1c`, `eda5b67`).
   - Install table: dest `/home/evo/.pi/agent/extensions/syntax-check.ts`, owner/mode `evo:evo 0644`, sudo: **no**, backup `/home/evo/AI/_archive/20261119/syntax-check.ts` (if pre-existing).
   - Install: `install -m 0644 /home/derekboone/evo-x3/config/pi-evo/extensions/syntax-check.ts /home/evo/.pi/agent/extensions/syntax-check.ts`.
   - Verify (broken-file test on box):
     ```bash
     T=/tmp/l7-test-$$ && mkdir -p "$T" && printf 'def broken(:\n' > "$T/bad.py"
     pi -p --no-session "Edit $T/bad.py to add '# test' on line 1; leave the syntax error intact."
     find "$T" -name __pycache__
     rm -rf "$T"
     ```
     Expected: tool output appends syntax-check stderr (`SyntaxError` / `[syntax-check]`) and `find "$T" -name __pycache__` prints nothing.
   - Note self-load: X3 Forge runs `pi` as `evo`, so `syntax-check.ts` will also load into Forge's own panes on next start; note this in `RESULT.md`.
   - Rollback: remove `/home/evo/.pi/agent/extensions/syntax-check.ts` (or restore backup).

### Group 3 — ST3 pair (`sync-renders` + `import_inbox.py`), L2 poster frame, and H3 units

10. **ST3 pair + L2 + ST7 (`sync-renders` + `import_inbox.py`, install together)** — Source on `mono`:
    - `config/bin/sync-renders` (`79a706a`, `60ef314`, `a5a86ce`, **`990ffd0` ST7**) -> `/usr/local/bin/sync-renders` | `root:root 0755` | sudo: **yes** | backup `/home/evo/AI/_archive/20261119/sync-renders`
    - `hosts/x3/pixlstash-tagging/import_inbox.py` (`79a706a`, `a5a86ce`) -> `/home/evo/AI/pixlstash-tagging/import_inbox.py` | `evo:evo 0755` | sudo: **no** | backup `/home/evo/AI/_archive/20261119/import_inbox.py`
    - **ST7 coordination (`990ffd0`):** `config/bin/sync-renders` now also carries `ST7` (QNAP publish moved to the nightly 03:30 timer). Pull `sync-renders` from the **same `mono` tip** as `records/UNI-APPLY-X3-C-QNAP-NIGHTLY/BRIEF.md`; **default: install `X3-A`'s `sync-renders` + `import_inbox.py` together with `X3-C`'s nightly script/units in one window** (or run `X3-C` immediately after `X3-A`).
    - Pre-install syntax check (no-write AST parse):
      ```bash
      bash -n /home/derekboone/evo-x3/config/bin/sync-renders
      python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' /home/derekboone/evo-x3/hosts/x3/pixlstash-tagging/import_inbox.py
      ```
    - Back up both live files and install together:
      ```bash
      cp -a /usr/local/bin/sync-renders /home/evo/AI/_archive/20261119/sync-renders
      cp -a /home/evo/AI/pixlstash-tagging/import_inbox.py /home/evo/AI/_archive/20261119/import_inbox.py
      sudo install -o root -g root -m 0755 /home/derekboone/evo-x3/config/bin/sync-renders /usr/local/bin/sync-renders
      install -m 0755 /home/derekboone/evo-x3/hosts/x3/pixlstash-tagging/import_inbox.py /home/evo/AI/pixlstash-tagging/import_inbox.py
      ```
      (Do **not** edit `pixlstash.service.d/10-memcap.conf` — Card 23 `ST3(c)` is already resolved live, Derrick 2026-11-19 12:29 CT, side chat.)
    - Exact ST3 + L2 checks:
      1. `bash -n /usr/local/bin/sync-renders && python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' /home/evo/AI/pixlstash-tagging/import_inbox.py`.
      2. Trigger one sync (`systemctl --user start evo-renders-sync.service` or run `/usr/local/bin/sync-renders` with no active render) and verify sync exits in `< 30 s`.
      3. Confirm `pixl-import.service` stays active after `sync-renders` exits (when inbox is non-empty) AND while `pixl-import.service` is active run:
         ```bash
         /home/evo/.venvs/pixlstash/bin/python /home/evo/AI/pixlstash-tagging/import_inbox.py
         ```
         Expected: JSON output contains `"stopped_reason": "locked"` without touching files.
      4. L2 check: confirm the poster-frame ffmpeg block in `/usr/local/bin/sync-renders` passes `bash -n` and (if a synced 2x clip exists) test poster extraction to `/tmp/l2-test.jpg` (remove `/tmp/l2-test.jpg` after) or confirm `/srv/renders/<run_id>.jpg` on the next synced clip.
      5. Note MINOR N5: non-hidden sidecar files in the inbox will harmlessly re-trigger `pixl-import`; do not patch here, just note in `RESULT.md` if observed.
    - Re-snapshot: **Max closeout step** (record `snapshot: pending Max` in `RESULT.md`).
    - Rollback: restore `/home/evo/AI/_archive/20261119/sync-renders` (`sudo install -o root -g root -m 0755`) and `/home/evo/AI/_archive/20261119/import_inbox.py` (`install -m 0755`).

11. **H3 read-only ntfy systemd user units** — Source on `mono`: `hosts/x3/systemd/user/evo-morning-status.{service,timer}`, `hosts/x3/systemd/user/evo-weekly-worktrees.{service,timer}` (`6d54d3e`, `c49ef7a`).
    - Install table: dest `/home/evo/.config/systemd/user/`, owner/mode `evo:evo 0644`, sudo: **no**, backup `/home/evo/AI/_archive/20261119/systemd-user/` (if existing).
    - Install the 4 unit files (`install -m 0644`), then run `systemctl --user daemon-reload && systemctl --user enable --now evo-morning-status.timer evo-weekly-worktrees.timer`.
    - Verify:
      1. `systemd-analyze --user verify /home/evo/.config/systemd/user/evo-morning-status.service /home/evo/.config/systemd/user/evo-weekly-worktrees.service`.
      2. `systemctl --user list-timers evo-morning-status.timer evo-weekly-worktrees.timer` (confirm 07:00 daily and Sun 08:00 weekly — outside 04:00 JoyCaption window).
      3. Run `systemctl --user start evo-morning-status.service` once (requires `P4.11` ntfy token in place) and verify exit 0, one ntfy message sent with 0 secrets, and 0 llama-swap model swaps.
    - Re-snapshot: **Max closeout step** (record `snapshot: pending Max` in `RESULT.md`).
    - Rollback: `systemctl --user disable --now evo-morning-status.timer evo-weekly-worktrees.timer`, remove the 4 unit files (or restore backup), and `systemctl --user daemon-reload`.

## Closeout (Max only, after `RESULT.md`)
- As `derekboone` in `/home/derekboone/evo-x3`: run `scripts/snapshot-live-setup.sh` and `scripts/sync-config-copies.sh`, run `gitleaks`, and commit snapshot updates by explicit path. (Forge never runs these scripts as `evo`.)

## Rules
- **Stop on first failure in any group.** Do not skip a failed install/test and continue mutating later items in the same group.
- No `llama-swap.yaml` edits. No service restarts beyond `systemctl --user daemon-reload` / enabling the H3 timers and triggering `evo-renders-sync.service`.
- No renders. Nothing runs during an active render.
- Never read, print, or copy secrets (`auth.json`, `mcp.json`, `models.json`, `.env`, `*.token`, `/etc/evo-x3/*`, `~/.ssh`). Never view PixlStash library contents.
- Cite `mono` SHAs (never worker branch SHAs) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-A/RESULT.md`, then stop. List Step 0, items 1-11, and `H2 comment copy (delta #14)` (`SKIPPED (held with H2)`) as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs, pre-pull HEADs, backup paths, exact verify commands + pass/fail outputs, L7 self-load note, `snapshot: pending Max`, and rollback status if triggered.
