# U41 Result — Still Shape-Check, `--aspect auto`, `--still-mode guide|ref`, and Skill Notes

Date: 2026-11-16 (CT)
Executor: Antigravity (Gemini 4 Hydrogen High) on EVO-X3 (edits in `/home/evo/AI/community` as user `evo`)
Brief: `/home/derekboone/evo-x3/records/U41-shape-check-skill-note-brief-20261116.md`
Mode Plan: `/home/derekboone/evo-x3/records/ref2va-reference-only-mode-plan-20261116.md`

> **Status note:** `--still-mode ref` is implemented, dry-built, and unit-tested, **but untested on a real clip** until Derrick says yes to the later same-seed comparison render after PixlStash setup.

---

## 1. Commit & Files Changed

- **Repo / Branch:** `/home/evo/AI/community`, branch `x3-linux`
- **Commit:** `a4f58a7` (parent `0530815`) — `U41: still shape warning, --aspect auto, --still-mode guide|ref (default guide unchanged), and skill notes`
- **Push status:** `git push gitea HEAD:x3-community` failed with `[rejected] HEAD -> x3-community (non-fast-forward)` because `x3-linux` is `[gitea/x3-community: ahead 2, behind 6]` (contains local U40 `0530815` + U41 `a4f58a7`). Committed locally on `x3-linux`; pre-existing dirty files untouched.
- **Backups:** Saved before editing under `/home/evo/AI/community/_archive/u41-20261116/` (`*.bak-20261116-u41`).
- **Template:** `templates/b2_refmod.api.json` was **not** edited (`git diff` empty; `ref_image_size` remains `"match"`).

Staged and committed files (6 named files only):
1. `scripts/parody/build_request.py`
2. `scripts/parody/submit_parody_run.py`
3. `scripts/parody/render_writer_pipeline.py`
4. `scripts/parody/test_u41_shape_and_ref_mode.py` (new)
5. `skills/h3-parody-identity/SKILL.md`
6. `skills/h3-prompting/SKILL.md`

---

## 2. Pytest Counts

Command: `/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/parody` (from `/home/evo/AI/community` as `evo`):
- **Before (at `0530815`):** `563 passed, 5 skipped` (4.65 s)
- **U41 new tests (`test_u41_shape_and_ref_mode.py`):** `11 passed` (0.35 s)
- **After (final edit):** `574 passed, 5 skipped` (5.00 s)

---

## 3. How Shape-Check Warning & `--aspect auto` Work

Implemented once in `scripts/parody/build_request.py` and shared by `submit_parody_run.py` (both main parody CLI and `writer-run`), `render_writer_pipeline.py`, and `build_request.py` CLI:

- **Metadata-only size read (`read_still_size`):** Uses `PIL.Image.open(p)` → `.size` and closes immediately (never calls `.convert`, encodes, prints pixels, or calls `vision_read`). Returns `None` without raising if missing/unreadable, preserving existing missing-file behavior.
- **`--aspect auto` (`closest_aspect_preset`, `resolve_canvas`):** Picks the closest of the five canonical presets (`9:16` 768×1344, `16:9` 1344×768, `1:1` 1024×1024, `4:3` 1152×864, `3:4` 864×1152) by minimum `abs(still_ratio - preset_ratio)`. `--size WxH` still wins over `--aspect auto`. Explicit `--aspect` (e.g. `16:9`) is never overridden.
- **> 5% warning (`check_still_canvas_shape`):** Warn-only (never blocks or raises); checks `abs(still_ratio - canvas_ratio) / canvas_ratio > 0.05` and prints to `stderr` (and records in `shape_warning` / pipeline warnings):
  - Names still `W×H` + ratio + matching/closest canonical preset, canvas `W×H` + `--aspect` / `--size` source, and canonical `--aspect` suggestion (`9:16`, `16:9`, `1:1`, `4:3`, `3:4`).
  - In `guide` mode: states `MiniMaxH3AddGuide` will center-crop the still to the canvas (naming `top and bottom` when still is narrower, `sides` when wider).
  - In `ref` mode: omits any AddGuide center-crop claim and states instead that the still is used as an un-resized reference on `c0` and is not frame-0 pinned.
- **Pass-through:** Added `--aspect` (including `auto`), `--size`, and `--still-mode` to `submit_parody_run.py writer-run` (which previously fell through to template default `768×1344`) and `render_writer_pipeline.py` (checks shape in `run_clip` and forwards flags in `_bx` to `writer-run`).

---

## 4. How `--still-mode ref` Is Wired (and `guide` Byte-Identical Check)

- **Default (`guide`):** Unchanged locked graph (`img_1` `LoadImage` → `add_guide` `MiniMaxH3AddGuide` at `frame_idx=0`; `refapply.conditioning = ["add_guide", 0]`; `c0.ref_image_size = "match"`; no `ref_image_1` on `c0`; no `<Picture 1>` line in parody prompt).
- **Byte-identical verification:**
  - Direct comparison against pre-edit backup `_archive/u41-20261116/scripts/parody/build_request.py.bak-20261116-u41` on identical inputs:
    - `build_parody_request`: **byte-identical** (`6727` bytes `request.api.json`, identical prompt).
    - `build_writer_request`: **byte-identical** (`8920` bytes `request.api.json`, identical prompt).
  - Unit tests `test_parody_guide_default_is_byte_identical_to_explicit_guide` and `test_writer_guide_byte_identical_and_ref_mode` both pass (`default == explicit guide`).
- **`ref` mode (`--still-mode ref`):**
  - Keeps `img_1` (`LoadImage`) without pre-resizing or cropping the file.
  - Wires `c0.inputs["ref_images.ref_image_1"] = ["img_1", 0]`.
  - Sets `c0.inputs["ref_image_size"] = "max"` (only in `ref` mode).
  - Skips start-still `MiniMaxH3AddGuide` (`add_guide` absent) and leaves `refapply.inputs["conditioning"] = ["c0", 0]`; INDEX/OC look and voice `refmods` stay attached on `c0`; sampler `s0_samp` latent stays `["c0", 1]`.
  - Prepends TenStrip's exact `<Picture 1>` line (`REF_MODE_PICTURE1_LEAD`) to the prompt in `ref` mode only.
  - **S3 + `ref`:** Tested in `test_s3_plus_ref_mode_no_picture_slot_collision` — `ref_images.ref_image_1 = ["img_1", 0]` (start still = Picture 1), `ref_images.ref_image_2 = ["img_s3", 0]` (S3 = Picture 2), `ref_image_size = "max"`, no `add_guide`, no slot collision.

---

## 5. Dry-Build Node Diff (`guide` vs `ref`, No Queue)

Dry-built via `submit_parody_run.py writer-run` with a tiny synthetic `90×160` portrait PNG (`/tmp/u41_synth_portrait.png`) against `--aspect 16:9` (`1344×768`) into `/home/evo/AI/community/runs/u41_dry_guide/` and `/home/evo/AI/community/runs/u41_dry_ref/` (`DRY_RUN` marker written in both):

- **Shape warning (`67.9% diff`):**
  - `guide`: `WARNING: still shape mismatch (67.9% diff): still is 90x160 (ratio 0.562, matches 9:16 preset), canvas is 1344x768 (ratio 1.750, via --aspect 16:9). MiniMaxH3AddGuide will center-crop the still to the canvas (top and bottom can be cut off); pass --aspect 9:16 (or --aspect auto) to match the still, or --still-mode ref.`
  - `ref`: `WARNING: still shape mismatch (67.9% diff): still is 90x160 (ratio 0.562, matches 9:16 preset), canvas is 1344x768 (ratio 1.750, via --aspect 16:9). In --still-mode ref, the still is used as an un-resized reference on c0 and is not frame-0 pinned (matching canvas preset: --aspect 9:16).`
- **Graph diff (`u41_dry_guide/clip/request.api.json` vs `u41_dry_ref/clip/request.api.json`):**
  - `add_guide`: present in `guide` (`MiniMaxH3AddGuide`, `frame_idx=0`); **absent** in `ref`.
  - `c0.inputs["ref_images.ref_image_1"]`: absent (`None`) in `guide`; `["img_1", 0]` in `ref`.
  - `c0.inputs["ref_image_size"]`: `"match"` in `guide`; `"max"` in `ref`.
  - `refapply.inputs["conditioning"]`: `["add_guide", 0]` in `guide`; `["c0", 0]` in `ref`.
  - `refmods`: `mod_1 = minimaxh3_oc_poolclub_v1_refmod_audio`, `mod_2 = minimaxh3_oc_poolclub_v1_refmod_visual` identical in both.
  - `s0_samp.inputs["latent_image"]`: `["c0", 1]` identical in both.
  - `c0.inputs["prompt"]` / `prompt.txt`: `guide` (`3073` chars) has no TenStrip `<Picture 1>` lead; `ref` (`3327` chars) prepends the exact TenStrip `<Picture 1>` one-liner.

---

## 6. Skill Paths Edited vs Only Listed

- **Edited (X3 evo canonical):**
  - `/home/evo/AI/community/skills/h3-parody-identity/SKILL.md` — added `auto` to `--aspect`, added the short `guide` crop vs `--aspect auto` / `--still-mode ref` (untested on real render) note to `--image`, and updated the leftover `approved_characters/vault.db` mention to `~/AI/5slock/libraries/vault.db` only.
  - `/home/evo/AI/community/skills/h3-prompting/SKILL.md` — added the same short `guide` crop vs `--aspect auto` / `--still-mode ref` (untested on real render) note to R14.
- **Not edited (listed only per brief):**
  - Box (Grok Bot workflows): `/home/box/agent-data/workflows/h3-parody-identity/SKILL.md`, `/home/box/agent-data/workflows/h3-prompting/SKILL.md`
  - Fleet brain staging: `/workspace/cos/brain-staging/20_skills/current/h3-parody-identity/SKILL.md`, `/workspace/cos/brain-staging/20_skills/current/h3-prompting/SKILL.md`
  - Internals reference: `skills/h3-parody-identity/references/h3-parody-identity-reference.md`, brain `10_packs/max/h3-parody-identity-reference.md`
  - AlienPc (historical): `C:\AI\community\skills\h3-parody-identity\SKILL.md`, `C:\AI\community\skills\h3-prompting\SKILL.md`
  - `derekboone` X3 clone: `/home/derekboone/AI/community/skills/h3-parody-identity/SKILL.md`, `/home/derekboone/AI/community/skills/h3-prompting/SKILL.md`

---

## 7. Explicit Confirmations

- **No render / no queue:** No GPU lease was taken, `queue-remote.sh` / `run_queue.py` / ComfyUI `/prompt` were never called, and the later same-seed comparison render was **not** queued.
- **No image viewing:** No library stills, PixlStash contents, or `/home/evo/AI/5slock/` images were opened or viewed; all tests and dry builds used tiny synthetic PIL images created in `/tmp` / `tmp_path`, and `read_still_size` reads only `Image.open(path).size` metadata.
- **`--still-mode ref` status:** Implemented, dry-built, and unit-tested only; **untested on a real clip** until Derrick approves the later comparison render.
