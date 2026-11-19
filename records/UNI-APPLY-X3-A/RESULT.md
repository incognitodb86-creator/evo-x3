# UNI-APPLY-X3-A — RESULT (X3 Forge, 2026-11-19)

Doer: X3 Forge (`evo`), staged source `/home/evo/AI/_staging/mono-c390622` (mono `c390622`; work began against staged `d80617f`, brief re-read at `c390622` per Max 1:45 PM CT — groups 1–2 unaffected). This RESULT.md is written to the writable staged copy at `/home/evo/AI/_staging/mono-d80617f/records/UNI-APPLY-X3-A/` (the `mono-c390622` tree is read-only to `evo`).
Lease: held for Forge by Max (take/release skipped per Max).

**Summary: items 1–9 DONE (item 6 needed one documented local fix), item 10 BLOCKED on `sudo` (`import_inbox.py` half installed), item 11 SKIPPED pending Derrick.**

Pre-pull HEADs (recorded before any pull):
- `/home/evo/AI/render` @ `9232545` → now `a24f81b`
- `/home/evo/AI/community` @ `6bdcc49` → now `f90c5bb` + local fix commit `827d012` (see item 6)

## Step 0 — Pre-pull checks & backups — DONE
- `ps aux | grep -E 'queue-remote|run_queue' | grep -v grep` → empty (no render).
- Dirty files in live checkouts touched none of items 1–7 paths (render: `.pi/settings.json`, `writer_pipeline/dialogue_blacklist.jsonl`; community: `notes/actions.log`).
- `mkdir -p /home/evo/AI/_archive/20261119/{hermes,systemd-user,rea-video-capabilities}` OK.
- Backups taken before pulls: `_archive/20261119/{queue-remote.sh,OPERATOR.md,RUN_ME.md,still_candidate_sheet.py,community-AGENTS.md}` (all `cp -a`).

## Group 1

### 1. R5 `queue-remote.sh` 5 s poll (mono `73b5390`) — DONE
- `git -C /home/evo/AI/render pull --ff-only gitea x3-render` → fast-forward `9232545..a24f81b` (4 commits).
- Verify: `bash -n /home/evo/AI/render/x3/queue-remote.sh` OK; `grep -n "sleep 5"` → line 63: `until grep -q "BATCH closed" "$RUN/_render_queue.log" 2>/dev/null; do sleep 5; done`. PASS.

### 2. ST2 desk text + L4 `OPERATOR.md` (mono `abb6235`, `19ffe51`) — DONE
- Landed via the same `x3-render` pull.
- Verify: `grep -n "NOT_READY" OPERATOR.md RUN_ME.md` → multiple hits in both files (uploaded-still hard gate, hard-stops list, status line); `grep -n "contact_sheet.jpg" OPERATOR.md` → line 15 (`--out <crun>/contact_sheet.jpg`). PASS.

### 3. RV1 `rea-video` user capability YAML (mono `d83ac47`) — DONE
- `git -C /home/evo/AI/community pull --ff-only gitea x3-community` → fast-forward `6bdcc49..f90c5bb` (6 commits; ST4/ST5 candidate templates `fc540d3`/`3861193` rode along, not promoted).
- YAML install: no pre-existing `/home/evo/.rea-video/` (backup dir `_archive/20261119/rea-video-capabilities/` stays empty); installed `video.yaml` → `~/.rea-video/capabilities/models/video.yaml`, `prompting.yaml` → `~/.rea-video/capabilities/prompting.yaml`, both `evo:evo 0644`.
- Verify: `pytest -q scripts/tests/test_rv1_capabilities.py` → **2 passed**. PASS.
- Live CLI check: **SKIPPED** — RV0 not installed (no `rea-video` on PATH, no `/home/evo/AI/tools/rea-video`).

## Group 2

### 4. ST1 fresh candidate sheet (mono `d7320bb`) — DONE
- Landed via item-1 pull (backup taken in Step 0).
- Verify: `/home/evo/AI/render/x3/.venv/bin/python3 -m unittest discover -s /home/evo/AI/render/x3 -p "test_still_candidate_sheet.py" -v` → **Ran 5 tests … OK**. PASS.

### 5. W3a shared Beta 7 converter (mono `49c6de6`) — DONE
- Landed via item-3 pull.
- Verify: `pytest -q scripts/parody/test_beta7_convert.py` → **5 passed**. PASS.

### 6. RV2 `h3max_bridge` (mono `6be684a`) — DONE with local fix
- Landed via item-3 pull.
- First verify run: `make -C /home/evo/AI/community/scripts/h3max_bridge check-all` → ruff OK, ty OK, pytest **2 failed** — `ModuleNotFoundError: No module named 'yaml'`: `h3max_bridge.load_beta7_convert()` (runtime path, line 323) imports `scripts/parody/beta7_convert.py` → `build_request.py` → `import yaml`, but `pyproject.toml` had `dependencies = []` (undeclared transitive dep; passes only where the ambient env provides yaml).
- Minimal fix (not an assertion rewrite): `pyproject.toml` `dependencies = ["pyyaml>=6.0"]` + `uv lock`; re-run `make check-all` → lint OK, typecheck OK, **6 passed**. PASS after fix.
- Deviation committed locally on `x3-community`: `827d012` “h3max_bridge: declare pyyaml …” (unpushed; mono-only-push rule — **Max: upstream this one-line fix to mono**).

### 7. H5 harness + `AGENTS.md` gate (mono `a823877`) — DONE
- Landed via item-3 pull (`AGENTS.md` backup in Step 0).
- Verify: `make -C /home/evo/AI/community/agent-shared/python-harness/sample-tool check-all` → lint OK, typecheck OK, **3 passed**. PASS.
- Note: the verify run generated untracked `agent-shared/python-harness/sample-tool/uv.lock` (left for Max closeout to commit or ignore).

### 8. H4 Hermes skills prune + `pi-job` (mono `9ebe5a0`, rebased on live snapshot `eabc8c7`) — DONE
- Backup: `cp -a /home/evo/.hermes/skills /home/evo/AI/_archive/20261119/hermes/skills` before changes.
- Moved exactly the 27 REMOVE-list skills into `/home/evo/.hermes/skills-archived/` (relative subpaths preserved; emptied category dirs incl. `apple/`, `email/`, `media/`, `note-taking/`, `social-media/` moved along with their `DESCRIPTION.md` stubs).
- Installed `hosts/x3/hermes/skills/pi-job/SKILL.md` → `/home/evo/.hermes/skills/pi-job/SKILL.md` (`evo:evo 0644`).
- Verify: 19 `SKILL.md` on disk. `hermes skills list` → “0 hub-installed, 16 builtin, 2 local — 18 enabled, 0 disabled”; `pi-job` and `pixlstash-image-library` both listed (local/enabled); 0 broken paths / frontmatter errors.
  - Count note for Max: `hermes skills list` shows 18, not 19, because `devops/sdlc-review` is toolset-gated (`requires_toolsets: [kanban]`, `environments: [kanban]`) and never appears in the default-profile listing. This gating predates the prune (pre-prune: 46 `SKILL.md` on disk vs 41 listed). All 19 kept skills are on disk and valid.
- **H2 comment copy (delta #14, `hosts/x3/hermes/config.yaml`, mono `ef51f83`): SKIPPED (held with H2)** — `config.yaml` not merged.
- snapshot: pending Max (closeout step; Forge did not run `snapshot-live-setup.sh` as `evo`).
- Rollback path: move archived skills back + restore `_archive/20261119/hermes/skills`.

### 9. L7 `syntax-check.ts` pi extension (mono `53cde1c`, `eda5b67`) — DONE
- No pre-existing `/home/evo/.pi/agent/extensions/syntax-check.ts` (backup slot empty).
- `install -m 0644 .../config/pi-evo/extensions/syntax-check.ts /home/evo/.pi/agent/extensions/syntax-check.ts` → `evo:evo 0644`.
- Verify (broken-file test): `T=/tmp/l7-test-$$; mkdir -p "$T"; printf 'def broken(:\n' > "$T/bad.py"; pi -p --no-session "Edit $T/bad.py to add '# test' on line 1; leave the syntax error intact."` → edit landed and the post-edit syntax check reported `SyntaxError: invalid syntax` at line 2 (stderr appended to tool output); `find "$T" -name __pycache__` printed nothing; temp dir removed. PASS.
- **Self-load note:** `syntax-check.ts` will also load into X3 Forge’s own pi panes (including this one) on next start.

## Group 3

### 10. ST3 pair + L2 (`sync-renders` + `import_inbox.py`) — BLOCKED (sudo)
- Pre-install syntax checks (staged sources): `bash -n sync-renders` OK; `ast.parse(import_inbox.py)` OK.
- Backups: `_archive/20261119/sync-renders` and `_archive/20261119/import_inbox.py` taken (`cp -a`, pre-install versions preserved).
- `install -m 0755 hosts/x3/pixlstash-tagging/import_inbox.py` → `/home/evo/AI/pixlstash-tagging/import_inbox.py` `evo:evo 0755`. **Installed.**
- `sudo -n install -o root -g root -m 0755 ... /usr/local/bin/sync-renders` → **BLOCKED**: the Forge pane permission policy denies `sudo` to `evo` (“is not permitted to run … (matched `*sudo *`)”, hard stop, no retry/bypass). `/usr/local/bin` is `root:root drwxr-xr-x`, so a non-sudo install is impossible. Live `/usr/local/bin/sync-renders` is still the 2026-11-19 07:45 build (diff confirms it lacks the L2 poster-frame block and still carries the old `publish_x3` path).
- Checks completed: installed `import_inbox.py` `ast.parse` OK; live smoke `/home/evo/.venvs/pixlstash/bin/python /home/evo/AI/pixlstash-tagging/import_inbox.py` → `{"files": 0, "batches": 0, "imported": 0, "duplicate": 0, "failed": 0, "timed_out": 0, "remaining": 0, "elapsed_s": 0.0, "stopped_reason": "done"}` in <1 s (inbox had no pending files).
- Checks not run (require the new `sync-renders`): (2) sync trigger <30 s; (3) `pixl-import.service` transient-unit lock + concurrent-run `stopped_reason="locked"` (note: `pixl-import` is a `systemd-run --user --unit=pixl-import --collect` transient unit and only exists while importing); (4) L2 poster extraction.
- N5 note: no non-hidden sidecar files observed in `/home/evo/AI/pixl-inbox` (only `_failed/`, `_imported/`, `.import_inbox.lock`).
- snapshot: pending Max. Rollback: not triggered (`sync-renders` untouched; `import_inbox.py` restorable from backup).
- **Action for Max/Derrick:** run `sudo install -o root -g root -m 0755 /home/evo/AI/_staging/mono-c390622/config/bin/sync-renders /usr/local/bin/sync-renders` (or grant the Forge pane sudo), then run item 10 checks 2–4.

### 11. H3 read-only ntfy systemd user units (mono `6d54d3e`, `c49ef7a`) — SKIPPED
- SKIPPED pending Derrick (launch grant covered through item 10; Card 12 ntfy live-run check deferred). Unit files not installed.

## Rules compliance
- No `llama-swap.yaml` edits; no service restarts; no renders started; no secrets read.
- Stop-on-first-failure observed: the only failure class hit was the item-10 sudo block (plus the item-6 dependency bug, fixed minimally in-scope).
- snapshot: pending Max (with `sync-config-copies.sh` and `gitleaks` at closeout).

## Max closeout 2026-11-19

- `sync-renders` installed by Max 13:57 CT (America/Chicago). `sudo` is blocked for `evo`, so Max ran the install. Live `/usr/local/bin/sync-renders` is `root:root` mode `0755`, mtime 2026-11-19 13:57:15 CT, and `cmp` matches the staged `mono-c390622` copy at `/home/evo/AI/_staging/mono-c390622/config/bin/sync-renders`. Item 10 install is complete.
- Item 10 checks 2–4 still need a real render and stay pending (sync trigger <30 s; `pixl-import` transient-unit lock + concurrent-run `stopped_reason="locked"`; L2 poster extraction).
- Item 11 (H3 read-only ntfy systemd user units) pending Derrick.
