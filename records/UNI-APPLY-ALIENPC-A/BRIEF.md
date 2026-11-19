Goal: Check AlienPc `C:\AI\community` dirty files (M7), then bridge-apply M4/ST4/ST5 candidate templates and the S2 allowlist script + offline pytest (without hooking S2 into `comm.py`/gate) under the AlienPc lease.

# UNI-APPLY-ALIENPC-A (AlienPc Forge): M7 check + M4/ST4/ST5 candidates + S2 script on AlienPc, Nov 19 2026

Authority: Derrick 2026-11-19 11:11/11:16 CT (Card 2 + Forge execution) and `records/unified-implementation/PLAN.md` + `records/unified-implementation/CODE-REVIEW-20261119-opus-delta.md` ("Apply order for Max", AlienPc side). Max verifies your `RESULT.md` afterwards.

## Needs before launch (do not launch until met; held items stay skipped)
1. **Derrick's live yes** to apply `alienpc/community/` file-only items (`M4`, `ST4`, `ST5` candidate templates + `S2` allowlist script and offline tests) into `C:\AI\community`.
2. **AlienPc lease taken** (following brain `10_packs/max/max-briefing.md` convention, mirrored to `records/status/`).
3. **Max import + pre-cutover bridge complete** from `mono` tip `5ccba67` (or newer):
   - `gitleaks` clean on `947aa26..mono`; Gitea `mono` fast-forwarded (or merged, never force-pushed).
   - Until `MONO-S6` passes smoke: Max bridges `alienpc/community/` commits (`a808401`, `30f9997`, `df6815c`, `4c4d4a6`, `6129330`, `c0c9492`) onto Gitea `alienpc-community` via `git format-patch --relative=alienpc/community/ <range>` + `git am` under the AlienPc lease, then pushes `alienpc-community` to Gitea. (After `MONO-S6`, `C:\AI\community` pulls `mono` directly.)
4. **HELD — do NOT apply unless Derrick explicitly unlocks before launch:**
   - **`INV1`** (`hosts/alienpc/live/pi-agent/AGENTS.md` line 1 fix, mono `1e2dc13`): requires Derrick's answer on which `AGENTS.md` copy is master (`C:\Users\derek\.pi\agent\AGENTS.md` vs `C:\AI\community\agent-shared\AGENTS.md`).
   - **`INV1b`** (`hosts/alienpc/live/pi-agent/AGENTS.md` line 35 scope rule, mono `79ccbc8`, DRAFT): requires Derrick's explicit approval of **Card 38** before copying to `C:\Users\derek\.pi\agent\AGENTS.md` (backup `C:\AI\_archive\20261119\pi-agent\`).
   - **`S2` live hook into `comm.py` / `gpu_lock_gate.py`**: **HELD** — requires Card 6 yes and a Derrick-approved commit to `scripts/allowlist_promoted.json` for any promoted template. Do **not** edit `comm.py` or the gate in this brief.

## Access & Lease
- **Doer:** AlienPc Forge (`C:\Users\derek\forge` -> `5slock`, pi panes `w2V:p3`/`p7`), running as user `derek` (sudo/admin: **no**).
- **Target repo:** `C:\AI\community` (Gitea `alienpc-community`).
- **Backup root:** `C:\AI\_archive\20261119\community\`.
- **Lease:** AlienPc lease (brain `10_packs/max/max-briefing.md`, mirrored to `records/status/`). No GPU is used in this brief; still verify no active render before pulling `C:\AI\community`.

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

3. **Bridge pull into `C:\AI\community`:**
   - Run `git -C C:\AI\community pull --ff-only gitea alienpc-community` (brings bridged `mono` commits:
     - **S2:** `a808401`, `6129330`, `c0c9492` -> `scripts/template_allowlist.py`, `scripts/u55_allowlist_specs.json`, `scripts/allowlist_promoted.json`, `scripts/tests/test_template_allowlist.py`
     - **M4:** `30f9997` -> `templates/miraclein_{t2i,refmod,edit}.candidate.api.json`
     - **ST4:** `df6815c` -> `templates/flux_stills_t2i_klein.candidate.api.json`
     - **ST5:** `4c4d4a6` -> `templates/flux_stills_{pose,layout}_klein.candidate.api.json`)
   - Confirm locked templates and `comm.py` were not modified:
     ```powershell
     git -C C:\AI\community diff -- scripts/comm.py templates/flux_stills_s2_kv.api.json
     ```
   - **DO NOT** hook `template_allowlist.py` into `scripts/comm.py` or `gpu_lock_gate.py`.
   - **DO NOT** apply `INV1` or `INV1b` to `C:\Users\derek\.pi\agent\AGENTS.md` (leave both `SKIPPED (held — Needs before launch)` unless Derrick explicitly unlocked them before launch).

## Tests (CPU / offline only — no GPU, no ComfyUI)

1. **S2 pytest suite:**
   ```powershell
   python -m pytest C:\AI\community\scripts\tests\test_template_allowlist.py -v
   ```
   Expected: **12 passed**.

2. **S2 CLI smoke check on live templates:**
   ```powershell
   python C:\AI\community\scripts\template_allowlist.py C:\AI\community\templates\b2.api.json
   python C:\AI\community\scripts\template_allowlist.py C:\AI\community\templates\b2_omni_rewriter.api.json
   ```
   Expected: `ALLOW b2` (exit 0) for `b2.api.json`; `REFUSE` (exit 1) for `b2_omni_rewriter.api.json`.

3. **M4 / ST4 / ST5 candidate JSON + refusal check:**
   - Verify all 6 `*.candidate.api.json` files parse as valid JSON and that `template_allowlist.py` returns `REFUSE` (exit 1) on every candidate (confirming none are promoted to the live allowlist).

## Rollback
- **NEVER run `git reset --hard`** in `C:\AI\community` (would destroy the 131 unrelated dirty files from M7).
- To roll back cleanly: `git -C C:\AI\community revert --no-edit <pre-pull-HEAD>..HEAD` (or remove only the 10 newly added files and restore any backed-up file from `C:\AI\_archive\20261119\community\`).

## Rules
- **No ComfyUI restart, no ComfyUI-Manager, no model/node downloads, no GPU use, no renders.**
- Do **not** hook `S2` into `comm.py` or the ComfyUI gate (held).
- Do **not** apply `INV1` or `INV1b` without Derrick's explicit answer / Card 38 approval.
- Do **not** open `C:\Users\derek\sydney\`. No secrets on argv or in output.
- Cite `mono` SHAs (`a808401`, `30f9997`, `df6815c`, `4c4d4a6`, `6129330`, `c0c9492`) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `records/UNI-APPLY-ALIENPC-A/RESULT.md` (for Max to file in `evo-x3/records/UNI-APPLY-ALIENPC-A/RESULT.md`), then stop. List `M7 check`, `Bridge pull`, `Tests 1-3`, and `INV1`/`INV1b`/`S2 hook` as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs, pre/post `HEAD` SHAs, `git status -- templates scripts` output, and pytest totals.
