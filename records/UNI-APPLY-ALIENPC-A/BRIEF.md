Goal: Check AlienPc `C:\AI\community` dirty files (M7), then apply (staged patch) M4/ST4/ST5 candidate templates and the S2 allowlist script + offline pytest (without hooking S2 into `comm.py`/gate) under the AlienPc lease.

# UNI-APPLY-ALIENPC-A (AlienPc Forge): M7 check + M4/ST4/ST5 candidates + S2 script on AlienPc, Nov 19 2026

Authority: Derrick 2026-11-19 11:11/11:16 CT (Card 2 + Forge execution) and `records/unified-implementation/PLAN.md` + `records/unified-implementation/CODE-REVIEW-20261119-opus-delta.md` ("Apply order for Max", AlienPc side). Max verifies your `RESULT.md` afterwards.

## Needs before launch (do not launch until met; held items stay skipped)
1. **Derrick's live yes in chat:** Card 1 (live apply for `alienpc/community/` file-only items: `M4`, `ST4`, `ST5` candidate templates + `S2` allowlist script and offline tests into `C:\AI\community`) answered in chat (Max records id). (Card 33 M7 dirty check is answered: checked in step 1 below, Derrick 2026-11-19 12:29 CT, side chat.)
2. **AlienPc lease free** (AlienPc lease per brain `10_packs/max/max-briefing.md`). The doer takes it as ONE line (`<who> | <what> | <start time>`) and clears it when done; no lease-taken/released files, no brain or `records/status/` mirrors, no git commit for the lease, no message to Derrick.
3. **Max import + bridge patch staged** from `mono` tip `bab584a (or newer at Max import)`:
   - **ONE BRANCH (`mono` ONLY — Derrick 2026-11-19 ~13:05 CT):** `mono` is the ONLY branch anyone pushes from now on (no pushes to `alienpc-*`, `x3-*`, or `u58` anywhere). `gitleaks` clean on `947aa26..mono`; Gitea `mono` fast-forwarded (or merged, never force-pushed).
   - `C:\AI\community` does **not** track `derrick/evo-x3`: its upstream is the separate Gitea repo `derrick/alienpc-community-pc` (`master`), and its remote URL carries a credential (monorepo Q6), so never run `git remote -v` or print that URL. Until `MONO-S6` passes smoke (recommended next — it ends the bridge), Max stages one local patch on the X3 instead of a pull or part-branch push:
     `git diff --binary 947aa26 <mono-sha> --relative=alienpc/community/ -- alienpc/community > /home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-A.patch`
     and gives the patch sha256 in the launch message. (`mono` SHAs in it: `a808401`, `30f9997`, `df6815c`, `4c4d4a6`, `6129330`, `c0c9492`, plus the M4 `Miraclein_4.5_9b_NVFP4` enum sync once landed on `mono`.)
   - If `MONO-S6` already passed: `C:\AI\community` is a junction into the `mono` clone; skip the patch and run `git -C C:\AI\evo-x3 pull --ff-only` instead (then the same tests).
4. **Separate / held items — do NOT apply in this brief:**
   - **`INV1`:** **superseded by `AGT1`** (Derrick 2026-11-19 12:29 CT, side chat: one file, master = `C:\Users\derek\.pi\agent\AGENTS.md`, community `agent-shared/AGENTS.md` becomes a pointer; separate apply in [UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md](../UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md)).
   - **`INV1b` (Card 38):** **APPROVED** (Derrick 2026-11-19 12:29 CT, side chat: brief from X3/Max, AlienPc Forge is the hands) — no longer held; **ships with `AGT1`** in [UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md](../UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md).
   - **`S2` live hook into `comm.py` / `gpu_lock_gate.py`**: **HELD** — requires Card 6 answered in chat (Max records id) and a Derrick-approved commit to `scripts/allowlist_promoted.json` for any promoted template. Do **not** edit `comm.py` or the gate in this brief.

## Access & Lease
- **Doer:** AlienPc Forge (`C:\Users\derek\forge` -> `5slock`, pi panes `w2V:p3`/`p7`), running as user `derek` (sudo/admin: **no**).
- **Target repo:** `C:\AI\community` (Gitea `derrick/alienpc-community-pc`, branch `master`).
- **Backup root:** `C:\AI\_archive\20261119\community\`.
- **Lease:** AlienPc lease (brain `10_packs/max/max-briefing.md`): ONE line `alienpc-forge | UNI-APPLY-ALIENPC-A | <start time>` at start, cleared when done or blocked; no status files, mirrors, commits, or messages for the lease.
- **No GPU is used in this brief**; still confirm no active render before touching `C:\AI\community`:
  ```powershell
  Test-Path C:\AI\locks\gpu-render.lock
  curl.exe -s -o NUL -w "%{http_code}`n" https://alienpc.tailf242b2.ts.net:8447/health
  ```
  Expected: `False` and `200`. Stop if a render is active.

## Work (stop on first failure)

1. **M7 dirty-files check FIRST (hard stop on overlap):**
   - Run:
     ```powershell
     git -C C:\AI\community status -- templates scripts
     ```
   - Background (Plan M7): `C:\AI\community` has ~131 dirty files.
   - **STOP immediately** and report `BLOCKED (M7 overlap)` if any dirty or untracked file overlaps the incoming paths below:
     - `templates/miraclein_t2i.candidate.api.json`
     - `templates/miraclein_refmod.candidate.api.json`
     - `templates/miraclein_edit.candidate.api.json`
     - `templates/flux_stills_t2i_klein.candidate.api.json`
     - `templates/flux_stills_pose_klein.candidate.api.json`
     - `templates/flux_stills_layout_klein.candidate.api.json`
     - `scripts/template_allowlist.py`
     - `scripts/u55_allowlist_specs.json`
     - `scripts/allowlist_promoted.json`
     - `scripts/tests/test_template_allowlist.py`

2. **Record HEAD and back up any pre-existing target files:**
   - Record `git -C C:\AI\community rev-parse HEAD` for `RESULT.md`.
   - Create `C:\AI\_archive\20261119\community\` and copy any pre-existing file from the list in step 1 into it (expect none; all 10 are new files).

3. **Apply the staged patch to `C:\AI\community` (no pull, no remote access):**
   - Allowed X3 command for this brief (Plan finding 14; no `-AsDerek`, no sudo; **read-only copy allowed even while X3 Forge holds the X3 lease**): copy the patch only:
     `scp x3:/home/derekboone/evo-x3/_bridge/UNI-APPLY-ALIENPC-A.patch C:\AI\_archive\20261119\community\`
   - Check `(Get-FileHash C:\AI\_archive\20261119\community\UNI-APPLY-ALIENPC-A.patch -Algorithm SHA256).Hash` equals the sha256 Max gave; stop if not.
   - `git -C C:\AI\community apply --check C:\AI\_archive\20261119\community\UNI-APPLY-ALIENPC-A.patch`, then the same without `--check`.
   - Commit only these 10 paths, even if other files are staged: `git -C C:\AI\community add -- <10 paths from step 1>` then
     `git -C C:\AI\community commit -m "UNI-APPLY-ALIENPC-A: S2 allowlist + M4/ST4/ST5 candidates (mono 5ccba67)" -- <10 paths>`.
   - Don't push. Report the new HEAD so Max's `MONO-S6` freeze accounts for it.
   - Confirm locked templates and `comm.py` were not modified:
     ```powershell
     git -C C:\AI\community diff HEAD~1 HEAD --stat -- scripts/comm.py templates/flux_stills_s2_kv.api.json
     ```
   - **DO NOT** hook `template_allowlist.py` into `scripts/comm.py` or `gpu_lock_gate.py`.
   - **DO NOT** touch `C:\Users\derek\.pi\agent\AGENTS.md` in this brief (`INV1` is superseded by `AGT1`; approved `INV1b` ships with `AGT1` in [UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md](../UNI-APPLY-ALIENPC-B-AGT1/BRIEF.md)).
## Tests (CPU / offline only — no GPU, no ComfyUI; keep `PYTHONDONTWRITEBYTECODE=1` to avoid littering the dirty repo)

1. **S2 pytest suite:**
   ```powershell
   $env:PYTHONDONTWRITEBYTECODE="1"
   python -m pytest -p no:cacheprovider C:\AI\community\scripts\tests\test_template_allowlist.py -v
   ```
   Expected: **12 passed** (no `.pytest_cache` or `__pycache__` written into `C:\AI\community`).

2. **S2 CLI smoke check on live templates:**
   ```powershell
   $env:PYTHONDONTWRITEBYTECODE="1"
   python C:\AI\community\scripts\template_allowlist.py C:\AI\community\templates\b2.api.json
   python C:\AI\community\scripts\template_allowlist.py C:\AI\community\templates\b2_omni_rewriter.api.json
   ```
   Expected: `ALLOW b2` (exit 0) for `b2.api.json` (**note:** if `b2.api.json` is in the M7 dirty list and differs from `mono`, `REFUSE` is expected — log it without failing the check); `REFUSE` (exit 1) for `b2_omni_rewriter.api.json`.

3. **M4 / ST4 / ST5 candidate JSON + refusal check:**
   - With `$env:PYTHONDONTWRITEBYTECODE="1"`, verify all 6 `*.candidate.api.json` files parse as valid JSON and that `template_allowlist.py` returns `REFUSE` (exit 1) on every candidate (confirming none are promoted to the live allowlist).

## Rollback
- **NEVER run `git reset --hard`** in `C:\AI\community` (would destroy the 131 unrelated dirty files from M7).
- To roll back cleanly: `git -C C:\AI\community revert --no-edit HEAD` (the one apply commit), or remove only the 10 newly added files and restore any backed-up file from `C:\AI\_archive\20261119\community\`.

## Rules
- **No ComfyUI restart, no ComfyUI-Manager, no model/node downloads, no GPU use, no renders.**
- Do **not** hook `S2` into `comm.py` or the ComfyUI gate (held).
- Do **not** apply `INV1` or `INV1b` without Derrick's explicit answer / Card 38 approval.
- Do **not** open `C:\Users\derek\sydney\`. No secrets on argv or in output.
- Cite `mono` SHAs (`a808401`, `30f9997`, `df6815c`, `4c4d4a6`, `6129330`, `c0c9492`) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `C:\AI\_archive\20261119\UNI-APPLY-ALIENPC-A-RESULT.md` (Max collects and files it into `evo-x3/records/UNI-APPLY-ALIENPC-A/RESULT.md`), then stop. List `M7 check`, `Patch apply`, `Tests 1-3`, and `INV1`/`INV1b`/`S2 hook` as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs, pre/post `HEAD` SHAs, patch sha256, `git status -- templates scripts` output, and pytest totals.
