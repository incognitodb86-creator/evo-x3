# REA pipeline: render workspace test (R1-R4)

Plan: [PLAN.md](./PLAN.md). Derrick 2026-11-20 ~9:19 AM CT: the render workspace test should "verify both flux and
h3max with refmods and lora". Everything below happens in the Hermes **render** chat (default profile,
`flash-next-render`). Derrick says each ask in his own words; the lines below are what Hermes should do and what Max
checks afterward. Adults 18+ only; NSFW allowed.

## Before R1

- H7 applied (`scripts/apply-hermes-workspaces.sh --apply`), including the updated `guard-render-queue.sh`.
- For R4 only: C1-C7 merged and deployed (C8), `rea-remake` skill installed (C9).
- M6 Flux likeness A/B done, or Derrick accepts the current `flux_still.py` defaults (RefMod `fully_preserved (1.0)`,
  anchor sentence, RefMod on positive and negative).
- AlienPc idle, X3 lease free, no pi-job running.

## R1: Flux still, RefMod only

Ask: a Miraclein still of Sydney Sweeney (any scene). Hermes follows `h3-render` section 1 "New Miraclein / Flux
still": writes the prompt with `flux-klein-prompting`, dry-runs `flux_still.py --refmod 'Sydney Sweeney'`, shows it,
queues only after Derrick's yes.

Checks:
- `<run>/still/request.api.json`: `Klein9RefModsLoader.mod_1 = fk9_sydneysweeney_v1_refmod` (stem, no `.safetensors`),
  both `Klein9RefModApply` nodes `fully_preserved (1.0)`, CFGGuider negative -> the RefMod apply node.
- Prompt starts with the reference anchor sentence.
- `flux_meta.json` `names` includes Sydney Sweeney; a copy of the PNG lands in `/home/evo/AI/pixl-inbox/`.
- Derrick's eye: does it look like her? (yes / partly / no)

## R2: Flux still, RefMod + celeb LoRA (hybrid)

Ask: same scene with the RefMod and LoRA together. Hermes uses `flux_still.py --hybrid 'Sydney Sweeney'`.

Checks:
- One `LoraLoaderModelOnly` with `klein9\fk9_sydneysweeney_v1_prodigy.safetensors` at 0.60 (backslash), RefMod
  strength 0.85, retention `partially_preserved (0.7)`.
- AlienPc ComfyUI console has no `lora key not loaded` line for that run.
- Derrick's eye compared with R1.

## R3: H3Max clip from the R1 still (H3 RefMod)

Ask: animate the R1 still (pick it from PixlStash or name the run). Hermes follows `h3-render` sections 3-5.

Checks:
- `build_report.json` READY; the celeb is picked up from `flux_meta.json` (names) and linked to the INDEX character.
- `clip/request.api.json` has the H3 visual RefMod in `mod_1` and the template that `pick_template()` chose (t3013u
  original 1-pass setup).
- Parody lane: no celebrity voice audio ref and no `<Audio N>` binding in the prompt (U56 #2).
- Queued only after Derrick's yes; 2x clip comes back as `MEDIA:`.
- H3 LoRA: the H3 realism LoRA is off (M5 closed, t2885u), so R3 tests H3 RefMods only unless Derrick turns a LoRA on
  for this run (`--realism-lora`), in which case `clip/request.api.json` shows it and its trigger.

## R4: REA 2-shot remake

Ask: remake this clip as a Sydney Sweeney parody (Q-RP1 / Q-RP2 decide where it was decomposed and which clip).
Hermes follows the `rea-remake` skill: plan -> batch card -> GO -> FLUX prompts + stills -> Beta 7 prose -> build ->
queue -> assemble.

Checks:
- Two isolated shot folders, different seeds, `raw_still_read.json` per shot, `parody_cast_lock.json`
  `allow_audio_ref: false`.
- FLUX stills use `rea_edit` or `rea_pose` candidate templates at exactly 768x1344 (or 1344x768).
- Each `hermes_prose.txt` describes the edited still (Flux wardrobe and light), not the source frame.
- Any `STUCK` shot was rewritten once at most.
- `final_2x.mp4` plays, hard cuts, color close across cuts, padded short shots trimmed back.
- Derrick's eye on likeness and motion.

## Result

Max writes `records/REA-PARODY-PIPELINE/RESULT-RENDER.md`: R1-R4 PASS / FAIL / SKIPPED, run folder names, the checks
above, and Derrick's eye calls with his message ids. No images or prompt prose in git.
