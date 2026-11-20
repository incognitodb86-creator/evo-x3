---
title: "PixlStash 2.0 Upgrade, Diverse Hermes Still Picker & ComfyUI Integration Plan (PX1-PX6)"
date: 2026-11-20
type: plan
artifact_contract: ce-unified-plan/v1
authority: Derrick 2026-11-20 ~09:56-10:01 AM CT ("I love it all! lest do it #1 & #2. smart score 2.2 and all the cool futures we are missing")
base_commit: 5415ccc7
author: Opus (VS Code, Windows clone). File-only code + scripts ready; live applies wait on Derrick's go.
---

# PixlStash 2.0 Upgrade & Diverse Hermes Picker (`PX1–PX6`)

Integrates cleanly with the `5415ccc7` Hermes workspaces, Flux aspect-ratio reframing, and M6 Flux likeness A/B.
Verified against upstream `Pikselkroken/pixlstash` `v2.0.1` (`main` @ `510bd129`, 2026-11-20): Smart Score is a
hardcoded 1.0–5.0 NumPy heuristic (`smart_score_utils.py:152-596`) with strong headshot bias (`+0.13 face_mpx`
64²–390²). **Do NOT fork PixlStash** — treat `smart_score >= 2.2` strictly as a quality floor on the picker side
(`None` passes so newly imported Flux stills stay visible), never as the primary sort.

## One-command X3 installer (`scripts/apply-pixlstash-upgrade.sh`)

```bash
# Read-only status (memory.events, dedup counts, penalised tags — zero library browsing):
bash scripts/apply-pixlstash-upgrade.sh --status

# Preview live changes (no edits):
bash scripts/apply-pixlstash-upgrade.sh --dry-run

# Apply PX1 (upgraded picker + Hermes skills) + PX2 (persist 14G/16G memcap, no PixlStash restart):
bash scripts/apply-pixlstash-upgrade.sh --apply

# Optional PX3 Smart Picture Sets (preview first, then create via PixlStash API):
bash scripts/apply-pixlstash-upgrade.sh --create-smart-sets --dry-run
bash scripts/apply-pixlstash-upgrade.sh --create-smart-sets

# Rollback PX1/PX2 cleanly:
bash scripts/apply-pixlstash-upgrade.sh --rollback
```

## Units (`PX1–PX6`)

| ID | Host | Status | Scope & Guardrails | Verification / Gate |
|---|---|---|---|---|
| **PX1** | X3 (code on `mono`) | **READY TO APPLY** | **Upgraded Hermes still picker (`still_candidate_sheet.py`) + canonical `pixlstash-image-library` skill + `h3-render` update.** Smart Score `>= 2.2` floor only (`None` passes); NEVER sorts by `SMART_SCORE`; routes `--character-id`/`--set-id`/`--tag` through `GET /api/v1/pictures` (`sort=CHARACTER_LIKENESS`, avoiding >32k `/pictures/search` SQLite bind limits); filters by `--aspect 9:16|16:9` + `--min-short-edge 768` (sets `needs_reframe=true` if no orientation match, handing off to `5415ccc7` Flux aspect reframing); dedups `stack_id` (1 pick/stack); excludes last 30 `runs/*/pick.json`; stratifies 2 recent imports (`IMPORTED_AT`) + 2 strong matches + 2 random-fresh; supports `--out` contact sheet and `--media-dir` space-free `MEDIA:` symlinks. | Offline `pytest test_still_candidate_sheet.py`: **8 passed**. Live: picker returns diverse fresh stills & `MEDIA:` lines; `hermes skills list` shows `pixlstash-image-library` enabled in default, disabled in `code`. |
| **PX2** (`ST3c`) | X3 | **READY TO APPLY** | **Persist PixlStash memory cap (`14G`/`16G`) + sync stale `scripts/sync-renders.sh`.** Fixes reboot drift where live `10-memcap.conf` body still had `10G`/`12G` despite Derrick's `t2649` `--runtime` bump to `14G`/`16G`. Applied with `daemon-reload` + `set-property` (zero PixlStash restart). Note: `ST3a`/`ST3b` (`sync-renders` detached `pixl-import` + `import_inbox.py` batching/flock) are already live (`RESULT-ST3-pixl-sync-timer.md`) and untouched. Optional housekeeping gated on **Q-PX1**: detach empty default `"Library 1"` (`~/.config/pixlstash/images`) and archive old ~1 GB `_u39`/`_u42` vault backups. | `systemctl --user -M evo@ show pixlstash.service -p MemoryHigh -p MemoryMax` shows 14G / 16G; `memory.events` recorded in `--status`. |
| **PX3** | X3 | **READY (Q-PX2)** | **Smart Picture Sets (PixlStash v2.0 PR `#2740`).** Create render-ready Smart Sets per main OC + orientation (`FCSydny 9:16`, `FCSydny 16:9`, `FCMegan 9:16`, `FCMegan 16:9`) with `smart_score >= 2.2`, `likeness >= 0.55`, non-video, excluding defect tags. Lets Hermes pass `--set-id <id>` (and keeps sets well under the >32k bind limit). | `scripts/apply-pixlstash-upgrade.sh --create-smart-sets` creates sets via API (token on stdin via `curl -K -`, never argv); picker `--set-id` returns orientation-matched stills. |
| **PX4** | X3 | **RUNBOOK / Q-PX2** | **Multi-Tier Deduplication & Stacks + Anomaly Penalty Tuning + Tag Review / Reference Faces (PRs `#2739–#2742`).** Run `--status` first to read `/api/v1/dedup/counts` (counts only) and `GET /api/v1/users/me/penalised-tags` (tag names/weights only, never library contents). Operator runbook below for collapsing near-duplicate bursts into stacks, dialing down false-positive `smart_score_penalised_tags` via `PATCH /api/v1/users/me/config`, and using Tag Review Queue + Reference Face cluster re-centering in PixlStash UI. Note: rating any image across `4–5★` or `1★` resets `smart_score = NULL` vault-wide (`routes/pictures/_crud.py:809-814`) — do rating batches together, not mid-render. | Counts + penalised-tag list reviewed by Derrick; stack collapse reduces repeated burst variations in picker output. |
| **PX5** | AlienPc | **BRIEF / Q-PX3** | **Re-enable `ComfyUI-PixlStash` (`ComfyUI-PixlStash.disabled` @ `e5ce77da`, optional update to latest `Pikselkroken/ComfyUI-PixlStash`).** Under AlienPc lease: rename folder back (or `git pull` pinned SHA), verify `requirements.txt` against `hosts/alienpc/comfyui/pip-freeze.txt` (never touch `torch`), configure X3 PixlStash URL + scoped API token strictly inside ComfyUI Settings (NEVER in workflow JSON or git!). Wire **Face Likeness Gate** into candidate Miraclein/Flux batch templates (pairs directly with M6 Flux likeness A/B!) and optionally **Picture / Video Saver** for Recipe-preserving saves straight to PixlStash. | `/object_info` registers ComfyUI-PixlStash nodes; 1 dry candidate run passes Face Likeness Gate; zero tokens in `/history` or template JSON. |
| **PX6** | X3 / AlienPc | **DOC / Q-PX4** | **Diversity-aware LoRA / RefMod dataset picker (`GET /api/v1/training/character_set_suggestion`, `dataset_picker.py`).** Use PixlStash 2.0's built-in CLIP-diversity picker with `flux2-klein-9b-base` and `minimax-h3-image`/`minimax-h3-motion` presets when selecting 6–12 stills for M2 H3Max RefMod extraction or future Klein9 celeb LoRA training (replaces manual blind picking without exposing library folders). | Single API query returns diverse picture IDs for a chosen character; no secrets logged. |

## PX4 Operator Runbook (Zero-Risk UI / API Checklist)

1. **Inspect before changing anything:** run `bash scripts/apply-pixlstash-upgrade.sh --status` on X3. It prints only:
   - `pixlstash.service` `MemoryHigh`/`MemoryMax` and cgroup `memory.events` (`high` / `max` / `oom`).
   - `GET /api/v1/dedup/counts` (exact/near-duplicate counts only).
   - `GET /api/v1/users/me/penalised-tags` (anomaly tag names + penalty weights only).
2. **Collapse near-duplicate bursts into stacks:** in PixlStash UI → **Duplicates** (or `/api/v1/dedup`), collapse burst
   shoots into Stacks. Once stacked, `still_candidate_sheet.py` automatically picks at most **1 still per `stack_id`**.
3. **Tune noisy anomaly penalties (only if `--status` shows false positives hurting good stills):** use
   `PATCH /api/v1/users/me/config` (`smart_score_penalised_tags`) or PixlStash Settings → Smart Score to lower weights
   for false-positive tags; keep real defect tags (`blurry`, `bad_anatomy`, `deformed`, `watermark`) penalised.
4. **Tag Review Queue & Reference Face Clusters (UI):** open PixlStash UI → **Tag Review** to accept/reject pending
   JoyCaption tags in bulk, and open each OC character (`FCSydny`, `FCMegan`) → **Reference Faces** to remove outlier
   faces and re-center the centroid so `CHARACTER_LIKENESS >= 0.55` stays sharp.

## Q-cards for Derrick (answer in chat before running optional steps)

- **Q-PX1 (housekeeping):** detach empty default `"Library 1"` (`~/.config/pixlstash/images`) and archive old ~1 GB
  `_u39`/`_u42` vault backups after verifying the live vault? Default **yes** (archive first, never delete).
- **Q-PX2 (Smart Sets + dedup/penalties):** create the 4 orientation Smart Sets (`FCSydny`/`FCMegan` `9:16` & `16:9`)
  via `--create-smart-sets` right after `--apply`, and review `--status` output before collapsing dedup stacks?
  Default **yes**.
- **Q-PX3 (AlienPc `ComfyUI-PixlStash`):** re-enable `ComfyUI-PixlStash` on AlienPc (and update past `e5ce77da`?)
  with a scoped token in ComfyUI Settings to wire Face Likeness Gate alongside the M6 Flux A/B? Default **yes**
  (after M6 A/B finishes, or alongside it — under AlienPc lease).
- **Q-PX4 (LoRA / RefMod dataset picker):** use `GET /api/v1/training/character_set_suggestion` for M2 standalone H3
  RefMod extraction? Default **yes** when you resume M2.
