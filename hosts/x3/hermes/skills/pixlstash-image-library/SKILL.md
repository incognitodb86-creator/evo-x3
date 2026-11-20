---
name: pixlstash-image-library
description: "Use when finding or picking diverse stills from the local PixlStash library (Smart Score >= 2.2 floor only, never primary sort, orientation-aware, stack-deduped, recent-pick excluded)."
version: 2.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [pixlstash, stills, images, render]
    category: creative
    requires_toolsets: [terminal]
---

# PixlStash image library (diverse picker)

Use `/home/evo/AI/render/x3/still_candidate_sheet.py` whenever Derrick asks to find or pick stills of his characters
(`FCSydny`, `FCMegan`, etc.), Smart Sets, or scenes from PixlStash (`127.0.0.1:9537`).

## Hard rules
- **Never sort by `SMART_SCORE`** (`sort=SMART_SCORE` repeats the same 5 sharp close-up headshots every time). Smart
  Score `>= 2.2` is strictly a **quality floor** (`None` always passes so brand-new unscored Flux/imported stills stay
  visible).
- **Never pass `character_id=` to `/api/v1/pictures/search`** (large character libraries >32k hit SQLite bind limits).
  `still_candidate_sheet.py` automatically routes `--character-id` / `--set-id` / `--tag` through `GET /api/v1/pictures`
  ranked by `CHARACTER_LIKENESS` + stratified recent imports (`IMPORTED_AT`) + random-fresh candidates.
- **Never write scratch `.py` files, never run `python3 -c`, never use heredocs (`<<EOF`), never browse `/home/evo/AI/5slock/libraries/`, `vault.db`, tag dumps, or character lists.**
- **Never print, echo, or log `/home/evo/.config/pixlstash/render-read.token`.** The picker script reads it internally.

## Commands

```bash
PY=/home/evo/AI/render/x3/.venv/bin/python3
PICK=/home/evo/AI/render/x3/still_candidate_sheet.py
```

### 1. Pick stills for a render (2x3 contact sheet, orientation-matched)
Pass `--aspect 9:16` (portrait) or `--aspect 16:9` (landscape) to match the requested H3Max video canvas so
`MiniMaxH3AddGuide` does not center-crop off faces:

```bash
$PY "$PICK" --character-id 1 --aspect 9:16 --out /home/evo/.hermes/image_cache/candidates_sydny.png
```
- `FCSydny` = `--character-id 1`, `FCMegan` = `--character-id 2`.
- If a render-ready Smart Picture Set exists (e.g. `FCSydny 9:16` / `FCSydny 16:9`), prefer `--set-id <id>`.
- Optional filters: repeatable `--tag <tag>`, `--rejected-tag <tag>`, `--query '<scene words>'`, `--limit 6`,
  `--min-smart-score 2.2` (default), `--page 2` or `--exclude <id1,id2,...>` to see a fresh batch.
- Show the contact sheet inline on its own line (never inside a code fence):
  `MEDIA:/home/evo/.hermes/image_cache/candidates_sydny.png`
- **Aspect fallback (`needs_reframe: true` in JSON output):** if no still matches the requested orientation, the picker
  falls back and marks `"needs_reframe": true`. In that case, pre-reframe the chosen still with
  `flux_still.py --mode edit --image <still> --width <W> --height <H>` (after Derrick's yes) before passing it to
  `oc_guide` / `MiniMaxH3AddGuide`.

### 2. Show individual stills directly in chat (e.g. "find me 5 images of FCSydny in office attire")
Use `--media-dir /home/evo/.hermes/image_cache` so the script creates space-free symlinks and prints ready-to-paste
`MEDIA:` lines:

```bash
$PY "$PICK" --character-id 1 --tag office --limit 5 --media-dir /home/evo/.hermes/image_cache
```

Copy each printed `MEDIA:/home/evo/.hermes/image_cache/pixl_<id>.<ext>` line into your reply on its own line (never
inside a code fence).

### 3. Free-text scene search (no character filter)
```bash
$PY "$PICK" --query 'warm bedroom window light' --aspect 9:16 --limit 5 --media-dir /home/evo/.hermes/image_cache
```
