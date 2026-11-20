---
name: rea-remake
description: "Use when Derrick asks to remake, recreate or parody a source video shot by shot (rea-video breakdown -> Miraclein/Flux stills with RefMod/LoRA -> H3Max Beta 7 clips -> one 2x master). Not for a single clip from one still (use h3-render)."
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [render, h3, flux, rea-video, remake]
    category: creative
    requires_toolsets: [terminal]
---

# REA remake (source video -> Flux stills -> H3Max clips -> master)

Plan: `records/REA-PARODY-PIPELINE/PLAN.md` on mono. Everyone depicted is 18+; a youth cue stops the batch. NSFW is
allowed. A named celebrity parody never gets a celebrity voice audio ref (U56 #2); FCSydny / FCMegan may use OC voice
RefMods as in `h3-render`.

```bash
PY=/home/evo/AI/render/x3/.venv/bin/python3
REA=/home/evo/AI/community/scripts/parody/rea_parody_remake.py
B=/home/evo/AI/community/runs/rea_<YYYYMMDD_HHMM>_<slug>
```

If `$REA` does not exist, stop and say the REA pipeline is not installed yet.

## 1. Breakdown

Derrick gives a rea-video output folder (with `breakdown.json`, `shots/`, `stems/`), already decomposed on AlienPc or
the X3. If he gives only a video, say where it must be decomposed (`rea-video decompose <clip> -o <out> --lang en`) and
stop. Do not install anything.

## 2. Plan (no GPU)

```bash
$PY "$REA" plan "$B" --rea-dir '<rea dir>' --names '<Actor as Character>' --aspect 9:16
# OC lane instead: --character FCSydny
```

On `NOT_READY`, quote it and stop. On `READY`, show `batch_card.md` and a contact sheet of the shot keyframes (copy to
`/home/evo/.hermes/image_cache/`, reply `MEDIA:<file>` on its own line), then ask `Run this batch? (GO / no)` and stop.
Derrick's GO covers the whole batch (h3-render overnight/batch rule): FLUX stills and H3 clips for these shots only.

## 3. FLUX stills (after GO)

For each shot, load `flux-klein-prompting`, read `shots/<id>/raw_still_read.json`, `shot_brief.json` and
`parody_cast_lock.json`, and write `shots/<id>/flux_prompt.txt` (one paragraph, positive only, starts with the reference
anchor when a RefMod is used; `rea_pose` mode opens with `apply pose from image 1 with reference from image 2`). If the
target `--aspect` differs from the source video's orientation (e.g., 9:16 source -> 16:9 `1344x768`, or 16:9 -> 9:16
`768x1344`), explicitly tell FLUX to expand the scene/background naturally to the new edges while keeping the subject's
face, body, and proportions unchanged (`flux_rea_edit` keeps the source reference aspect-preserving and never stretches
it). Then:

```bash
$PY "$REA" flux "$B" --queue --yes-derrick
```

Long runs: terminal tool with `background=true` and `notify_on_complete=true`, then the `process` tool. Never `setsid`
or `nohup`. Show the edited stills (`shots/<id>/_inputs/<id>_edited.png`) as one contact sheet.

## 4. Beta 7 prose and gate

For each shot with an edited still, load `h3-writer` and write `shots/<id>/hermes_prose.txt` from the edited still
(not the source frame: wardrobe, hair and light come from the Flux still), the shot's `camera_h3_vocab`, its frame
count, and its dialogue (25 spoken words max). Set `"position"` in `shot_brief.json` if the shot needs one. Then:

```bash
$PY "$REA" build "$B"
```

`STUCK <id> <reason>`: rewrite that shot's prose once from scratch (never read `wp_lint`/`wp_state`, never
synonym-swap), run `$PY "$REA" build "$B" --shot <id>` once more. Still STUCK: leave the shot out and say so.

## 5. Render, 2x, master

```bash
$PY "$REA" queue "$B" --yes-derrick
$PY "$REA" assemble "$B" --publish
```

Run both with `background=true` + `notify_on_complete=true`. When done, reply with the `MEDIA:` line it prints and one
label line. Also print `$PY "$REA" status "$B"`.

## Hard rules

- Never pass `--queue` or `--yes-derrick` before Derrick's GO for this batch.
- Never edit pipeline code, templates, llama-swap or ComfyUI config. Never browse PixlStash library folders or name
  lists. Never print keys, tokens, RefMod or LoRA triggers.
- Write only under `$B`, the Hermes image cache and pixl-inbox.
