# U41 brief: still shape-check + skill note + `--still-mode ref` (after U40)

Written Mon Nov 16 2026, late morning CT, by Max for Antigravity (Gemini 4 Hydrogen High) on the X3.
Updated the same morning after Derrick t1941u ("Implement"): this batch now also implements the reference-only still mode. It is no longer plan-only.

Approvals:

- Shape check + skill note, and write the later plan: Derrick t1940s7144 — "Do the shape check and skill note, and write a plan for a ref2va reference-only mode to test later."
- Implement that mode in this same batch: Derrick t1941u, "Implement".

The plan to follow for mode wiring is `/home/derekboone/evo-x3/records/ref2va-reference-only-mode-plan-20261116.md` (box source `/workspace/maxops/plans/ref2va-reference-only-mode-plan-20261116.md`; copied next to this brief). Implement the code, unit tests, and a dry-build graph diff. Do **not** queue the later same-seed 16:9 comparison render in the plan's Test section. That still waits on Derrick's yes after PixlStash setup.

## When to start

U40 is already finished and Max verified it. RESULT: `/home/derekboone/evo-x3/records/U40-RESULT.md` (written 10:47 AM CT). Community commit `0530815`. Max re-ran parody pytest read-only: **`562 passed, 6 skipped`**. Render repo is clean at `2904e1b`. Community is ahead 1 with a pre-existing dirty tree (~41 items, linuxize/prior sync, including the two skill files you will edit). Leave dirty files alone unless you touch them. Do not start if a U40 process is still writing those scripts (it is not; U40 exited 10:47 AM CT).

## Source of truth

Work **only** in the evo repos, as user `evo`:

- `/home/evo/AI/community` — branch `x3-linux`, HEAD should be `0530815` (or whatever U40's RESULT lists if it moved). Do not use `/home/derekboone/AI/community` as a substitute (different HEAD).

You are launched as `derekboone`. `/home/evo/AI` is mode 700. For every read or write under `/home/evo/**`, write a script file (for example `/tmp/u41-step.sh`), then run:

```
sudo -n -iu evo bash /tmp/u41-step.sh
```

No nested quoting one-liners. Python: `/home/evo/AI/render/x3/.venv/bin/python`.

## HARD RULES

- Back up each file before editing: `*.bak-20261116-u41` next to the file, or copy to `_archive/`. Never delete; archive.
- No renders, no queueing, no GPU, no lease. Dry builds and unit tests only. Do not run the plan's later same-seed queued comparison (`guide` vs `ref` on a real still).
- Never view images. Never open PixlStash library contents, stills, or anything under `/home/evo/AI/5slock/` as pictures. For the shape check, read **width and height only** with PIL (`Image.open(path)` → `.size`, then close). Do not `.convert`, save, encode, print pixels, or call `vision_read()` (that path base64-encodes the still). Unit tests and dry builds must use tiny synthetic images you create, not library stills.
- Never pass tokens or secrets on argv, and never print them.
- No `git add -A` in community. Stage named files only. Clear commit message.
- Do **not** edit `templates/b2_refmod.api.json` itself. Leave the locked template as the guide-mode baseline (`ref_image_size` stays `match` in the file; no `ref_image_*` wired there). All `--still-mode ref` wiring and the `ref_image_size=max` flip happen in `build_request.py` at request-build time, and only when `ref` is requested. Default `guide` must stay byte-identical to today's `request.api.json`.
- Do not touch Windows partitions, USB X3BACKUP, BIOS, LUKS, Tailscale, llama-swap.yaml, Sydney private files, or the original ComfyUI folder.

## Work

Do all of A, B, and C in this batch.

### A. Shape check (warn only, never block)

In `scripts/parody/submit_parody_run.py` (main submit **and** `writer-run`) and the OC wrapper `scripts/parody/render_writer_pipeline.py` (this tree has no other `submit_*.py`; OC goes through `writer-run` / `render_writer_pipeline.py`):

1. After the still path is known and before the graph is built, read the still's pixel size (PIL, metadata only). If the file is missing, keep today's missing-file behavior; do not add a new hard fail for a readable still whose shape mismatches.
2. Compare the still's aspect (`width/height`) to the canvas aspect from `build_request.resolve_canvas`. Canvas presets today: `9:16`/`portrait` 768x1344 (default), `16:9`/`landscape`/`widescreen` 1344x768, `1:1`/`square` 1024x1024, `4:3` 1152x864, `3:4` 864x1152, or `--size WxH`.
3. If they differ by **more than 5%** (relative: `abs(still_ratio - canvas_ratio) / canvas_ratio > 0.05`), print a clear warning that names:
   - the still's width×height and its ratio (and the matching preset name if it has one),
   - the canvas width×height and the `--aspect` / `--size` that produced it,
   - that `MiniMaxH3AddGuide` will **center-crop** the still to the canvas, so the top and bottom (portrait on 16:9) or the sides (landscape on 9:16) can be cut off,
   - the `--aspect` value that matches the still (canonical names: `9:16`, `16:9`, `1:1`, `4:3`, `3:4` — not the aliases).
   - In `--still-mode ref`, the warning should still mention the mismatch, but it must not claim AddGuide will crop (AddGuide is skipped). Say instead that the still is used as an un-resized reference on `c0` and is not frame-0 pinned.
4. Add `--aspect auto`: pick the closest of those five supported presets (minimum aspect-ratio distance). Do not invent a custom `--size`. `--size` still wins over `--aspect`. An explicit `--aspect 16:9` with a portrait still must **warn**, not auto-switch. `auto` is the only case that picks a canvas from the still.
5. Hook `writer-run` too. That subparser has `--still` today but **no** `--aspect`. Add `--aspect` / `--size` / `--aspect auto` there and thread them through to whatever already sets the canvas (today it falls through to the template default 768x1344). Pass the same flags from `render_writer_pipeline.py`.
6. Warn only. Never block a submit or a dry build over a mismatch.
7. Put the size-read helper in one place (prefer `build_request.py` next to `resolve_canvas`, or a small shared function) so both entry points use it. Do not reuse `vision_read`.

### B. `--still-mode guide|ref` (implement now)

Add `--still-mode guide|ref`, default **`guide`**. Plumb it through:

- `scripts/parody/submit_parody_run.py` — main parody CLI and the `writer-run` subparser
- `scripts/parody/render_writer_pipeline.py` — OC entry, pass-through
- `scripts/parody/build_request.py` — the actual graph wiring

**`guide` (default):** today's locked graph, unchanged. `img_1` LoadImage → `MiniMaxH3AddGuide` at `frame_idx=0`; `refapply.conditioning` moved to `["add_guide", 0]` when a guide is wired; sampler latent stays `c0.1`; `c0` has no `ref_image_*` on the default path; template `ref_image_size` stays `match`. A unit test **must** prove that, with identical inputs, default/`guide` `request.api.json` is **byte-identical** to today's builder output (before this change). That test is a hard requirement.

**`ref` mode** — request.api.json changes only around the still, per the plan:

- Keep `img_1` (`LoadImage`). Do not pre-resize or crop the file.
- Wire `c0.inputs["ref_images.ref_image_1"] = ["img_1", 0]`.
- Do **not** add `add_guide` (or any `MiniMaxH3AddGuide` for the start still). Skip the LoadImage → AddGuide frame-0 path.
- Leave `refapply.conditioning` as `["c0", 0]` (the template's wiring). `refmods` / `refapply` stay on `c0`. INDEX look and voice RefMods do not move.
- Sampler latent stays `c0.1` (empty latent).
- Set `c0` `ref_image_size` to **`max`** in `ref` mode only (keep aspect; official meaning: downscale only if the short edge is over 2048). Do not silently flip `guide` mode to `max`.
- Prompt: prepend TenStrip's one-liner, then the normal scene prompt. Use this exact string (do not rephrase):

  `<Picture 1> is the correct scene identity. All lighting, lighting hue, color palette, visual output style, camera angle, camera focal length, camera orbit, camera framing, background, background objects, and characters fully preserved from <Picture 1>.`

  This **breaks** today's parody U2 rule ("never name the still in the text") in `ref` mode only. `guide` keeps U2 and must not gain this line.

**S3:** today's S3 path already uses `c0.inputs["ref_images.ref_image_1"]` for the start still and adds `img_s3`. `ref` mode plus an S3 still must not collide: Picture 1 = start still, Picture 2 = S3. Read the live S3 wiring at implement time and cover it with a unit test.

**Dry-build (required, no queue):** using a tiny synthetic still you create (not a library image), dry-build the same inputs once with `--still-mode guide` and once with `--still-mode ref` (include a 16:9 canvas vs a portrait synthetic still so the shape warning is exercised). Write both `request.api.json` files and a short node diff in RESULT: show that `ref` has `ref_image_1` → `img_1`, has no start-still `MiniMaxH3AddGuide`, keeps RefMods/voice on `c0`, sets `ref_image_size=max`, and includes the `<Picture 1>` line; and that `guide` still has AddGuide frame 0, no that prompt line, and `ref_image_size` unchanged. Do not queue.

### C. Skill note (one short addition each)

Add one short note that the start still is frame 0 and is center-cropped to the canvas in the default (`guide`) path, so match `--aspect` to the still (or use `--aspect auto`), or pass `--still-mode ref` so the still is an un-resized reference on `c0` and is not cropped. **`--still-mode ref` is implemented but untested on a real render until Derrick runs the later test.** Do not describe `ref` as shipping or proven.

Canonical files for this job (X3 evo, edit these):

- `/home/evo/AI/community/skills/h3-parody-identity/SKILL.md` — best home: the `--aspect` bullet (~line 27) and/or the `--image` bullet (~line 31), which already say AddGuide `frame_idx=0`.
- `/home/evo/AI/community/skills/h3-prompting/SKILL.md` — best home: R14, which already says "Frame 0 is pinned whenever a Cond still or AddGuide is used."

Leftover U40 doc note (fix if you already have the skill file open; do not sweep other docs unless you touch them): `h3-parody-identity/SKILL.md` still mentions `approved_characters/vault.db` as a PixlStash lookup. The code now uses only `/home/evo/AI/5slock/libraries/vault.db`. If you edit that sentence, point it at the merged vault only. Do not browse the vault.

Other copies (list in RESULT; do **not** try to edit the box or AlienPc from this X3 job):

- Box (Grok Bot workflows): `/home/box/agent-data/workflows/h3-parody-identity/SKILL.md`, `/home/box/agent-data/workflows/h3-prompting/SKILL.md`
- Fleet brain staging: `/workspace/cos/brain-staging/20_skills/current/h3-parody-identity/SKILL.md`, `/workspace/cos/brain-staging/20_skills/current/h3-prompting/SKILL.md`
- Internals reference (no required edit): `skills/h3-parody-identity/references/h3-parody-identity-reference.md` and brain `10_packs/max/h3-parody-identity-reference.md`
- AlienPc (agents moved off this machine; path still exists historically): `C:\AI\community\skills\h3-parody-identity\SKILL.md`, `C:\AI\community\skills\h3-prompting\SKILL.md`
- derekboone X3 clone (do not edit): `/home/derekboone/AI/community/skills/h3-parody-identity/SKILL.md`, `.../h3-prompting/SKILL.md`

Keep the note short. Do not rewrite the skills.

## Tests

From `/home/evo/AI/community`, as evo:

```
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/parody
```

Post-U40 baseline that must still hold: **`562 passed, 6 skipped`**. The older U37 floor (555/6) also holds. Record before/after counts. After this batch the count must be **at least** `562 passed, 6 skipped`, plus the new tests.

Add unit tests for:

- Shape check: 5% warning on / off, warning text (crop + suggested `--aspect` in `guide`; no false AddGuide-crop claim in `ref`), `--aspect auto` picking the closest preset, explicit `--aspect` not being overridden, `writer-run` / pipeline pass-through, and that a mismatch never raises.
- `--still-mode guide` (default) produces a `request.api.json` that is **byte-identical** to today's builder output on the same inputs.
- `--still-mode ref` wires un-resized `img_1` to `c0.ref_image_1`, skips start-still AddGuide, keeps RefMods/voice on `c0`, sets `ref_image_size=max`, and prepends the exact TenStrip `<Picture 1>` line.
- S3 + `ref` does not collide on picture slots (Picture 1 = start still, Picture 2 = S3).
- Use synthetic PIL images only.

## Commit and stop

Scoped commit, named files only, message that says it is a warning + `--aspect auto` + `--still-mode guide|ref` (default guide unchanged) + skill note; not a default-graph change and not a queued test. Push to `gitea/x3-community` if you can; if push is blocked (U40 was, missing Gitea creds for `evo`), commit locally and say so.

Write `/home/derekboone/evo-x3/records/U41-RESULT.md` (as derekboone) and stop. Include: files changed, commit hash, pytest before/after, how `--aspect auto` and the 5% warning work, how `--still-mode ref` is wired, the dry-build node diff (`guide` vs `ref`), the byte-identical `guide` test result, skill paths edited vs only listed, confirmation of no render, no queue, and no image viewing, and that `ref` is untested on a real clip until Derrick says yes. Then stop. Do not start the later comparison render, do not queue, do not wait for a render yes.
