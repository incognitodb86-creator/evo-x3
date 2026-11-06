---
name: h3-parody-identity
description: >-
  INDEX + RefMod celebrity/character parody lane for MiniMax H3 — use when asked
  for a parody video of any named character, actor, or celebrity on the locked
  1-pass beta7_int8HQ graph (no RefLoRA, no 2-pass, no voice ref), including
  autonomous chat execution from C:\AI\render with one submit_parody_run.py
  call.
---
# H3 parody / identity lane (INDEX + RefMod)

Maintainer internals, full CLI, VRAM measurements and history: `references/h3-parody-identity-reference.md` (brain: `10_packs/max/h3-parody-identity-reference.md`). Read it only when changing the pipeline.

## Locked baseline (Derrick, Nov 5–6, 2026)

- `templates/b2_refmod.api.json`, 1-pass, `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, 8 steps `euler`/`simple`, shift 12.0/3.0, RefModsLoader → RefModApply `retention 1.0`, plus `run_queue.py` default NVIDIA `RTX VSR ULTRA 2x @ 24fps` (`1536x2688` / `2688x1536`, keeps `<tag>_raw.mp4`; `--no-upscale` opt-out). **No RefLoRA, no 2-pass sampler, no `ref_audio`.** New nodes or dials need Derrick's yes.
- INDEX + RefMod always; `submit_parody_run.py` resolves `aliases.json`, INDEX and RefMods itself and fails closed when a non-`good` name has no RefMod. Report that error; never download weights.
- Images only from `approved_characters` (`LANE_IMAGE_RULES.md`). Never any `sydney` path. Never minor-coded words (`girl`, `teen`, `school`, `kid`, `child`, `minor`, `student`, `cheerleader`, `dorm`) — `guard_ok` blocks the submit.
- Derrick's chat ask for a named parody **is** the go for one clip or one stitched clip set. Ask first only for batches or downloads.

## Writing the arguments (no word cap — 500+ words welcome)

- `--description`: concrete biometrics (face, eyes, brows, lips, skin, hair) + scenario outfit + accessories. No `featuring` prefix, no `adult` filler, no `styled in ... tone` (the builder adds identity, vocal-timbre anchor, age and tone).
- `--scene`: rich, literal, multi-sentence: setting, fabrics, lighting (neon, 2 AM, bulbs… replaces default late-afternoon light), motion, and **both five-finger hands resting still on a prop in frame** (glass stem on table, mug on counter, purse strap, lapel) or relaxed at her sides/lap. Never splayed fingers on hips/tables, and never lift a mug/glass to sip (rim thumb warps, sip gets cut off) — also not in `--end-action`. First sentence becomes `summary:` unless `--summary` is passed.
- **Voice fidelity**: Pair the actor with their iconic `INDEX` character (`--character` + `--actor`) AND end `--scene` before speech with an explicit vocal-timbre + composed delivery cue matching the real speaker (e.g. `Speaking in Sydney Sweeney's exact Cassie Howard voice, with her low, breathy, laid-back vocal timbre and natural vocal fry:` or `Emilia Clarke's exact Daenerys Targaryen voice, crisp British RP contralto cadence and calm authority:`). Avoid peppy cues (`amused, teasing`, `bubbly`, `playful grin`) on lower-voiced speakers — they push pitch up 30–45 Hz; use composed cues (`a wry tired smile`, `calm deadpan poise`).
- `--camera`: e.g. `medium-wide waist-up shot including tabletop, 35mm lens, slow dolly push-in`. Motion words drop "camera locked off". Default is static 50mm medium (crops hands, so frame wider when hands matter).
- `--aspect`: `9:16` (default 768x1344 → 1536x2688), `16:9` (1344x768 → 2688x1536), `1:1`, `4:3`, `3:4`; or `--size WxH`.
- `--seconds`: one continuous shot up to **10 s (243f, ~5.5 min; 15 s single shots fail on 16 GB)**. Longer asks, or several `--beat "<scene>"` (`--beat-dialogue`, `--beat-camera`, `--beat-seconds`), render shared-anchor cells in one GPU batch, stitched into one `clip.mp4`.
- `--dialogue`: spoken words only (~8–15 words per 5 s). No timestamps, tags, backticks, "no speech", "room tone". Omit for silent clips. `--end-action`: verb phrase without subject (`holds a wry smile and winks slowly`, no sip); `--pronoun he|they` when needed.
- Optional `--image <approved_characters path>`: anchors frame 0 composition, outfit, pose and setting via `MiniMaxH3AddGuide` (`frame_idx=0`, no `<Picture N>` in text); `RefMod` still carries the celebrity's face likeness onto the clip while keeping voice intact.
- Optional second person: `--name2/--character2/--actor2/--description2/--dialogue2`; write `(S1)`/`(S2)` inside `--scene`.

Name mapping: always prefer pairing `INDEX` character + actor (`--name "<Actor>" --character "<Character>" --actor "<Actor>"`, e.g. `Cassie Howard` + `Sydney Sweeney`, `Daenerys Targaryen` + `Emilia Clarke`, `Jennifer Check` + `Megan Fox`) — naming the `INDEX` character improves voice likeness even on `INDEX: bad` rows; use actor-alone only when the actor has no `INDEX` character row.

## Autonomous recipe — ONE command, then reply

```powershell
& 'C:\AI\director\.venv\Scripts\python.exe' 'C:\AI\community\scripts\parody\submit_parody_run.py' `
  --name '<Actor>' --character '<Character>' --actor '<Actor>' --tone 'satirical adult parody' `
  --seconds 10 --aspect 16:9 --camera '<framing + motion>' `
  --description '<rich biometrics + outfit>' --scene '<rich scene + hands on prop + exact character/actor voice cue>' `
  --dialogue '<spoken words only>' --end-action '<holds a wry smile, no sip>' --wait --qnap-put
```

- Submits, holds no LLM turn during render, waits for `BATCH closed`, writes RTX 2x `<run_dir>\clip.mp4` (stitching cells if any), uploads `pi-drop/<run>.mp4`, and prints JSON (`final_mp4`, `qnap_path`, `objective`, `batch_rc`).
- **Do NOT** poll in PowerShell or run `ls`, `dir`, `ffprobe` or QNAP listings afterwards. Exit 0 → reply straight in chat with `final_mp4`, `qnap_path`, `OBJECTIVE`, and one sentence on scene/line. Exit 7 / `gpu_busy` → say GPU is busy and stop. `ValueError` → quote it, fix your wording once if yours, else stop.

## Sibling skills

`h3-prompting`, `h3-max-ref2va-prompt`, `video-render` / `comfy-render`.
