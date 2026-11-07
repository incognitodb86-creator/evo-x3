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

Internals, full CLI, VRAM measurements and history: `references/h3-parody-identity-reference.md` (brain: `10_packs/max/h3-parody-identity-reference.md`). Read it only when changing the pipeline.

## Locked baseline (Derrick, Nov 5–6, 2026)

- `templates/b2_refmod.api.json`, 1-pass, `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, 8 steps `euler`/`simple`, shift 12.0/3.0, RefModsLoader → RefModApply `retention 1.0`, plus `run_queue.py` default NVIDIA `RTX VSR ULTRA 2x @ 24fps` (`1536x2688` / `2688x1536`, keeps `<tag>_raw.mp4`; `--no-upscale` opt-out). **No RefLoRA, no 2-pass sampler, no `ref_audio`.** New nodes or dials need Derrick's yes.
- INDEX + RefMod always; `submit_parody_run.py` resolves `aliases.json`, INDEX and RefMods itself and fails closed when a non-`good` name has no RefMod. Report that error; never download weights.
- Images only from `approved_characters` (`LANE_IMAGE_RULES.md`). Never any `sydney` path. Never minor-coded words (`girl`, `teen`, `school`, `kid`, `child`, `minor`, `student`, `cheerleader`, `dorm`) — `guard_ok` blocks the submit.
- Derrick's chat ask for a named parody **is** the go for one clip, continuation or stitched set. Ask first only for batches or downloads.

## Writing the arguments (Reference §0.5 & §0.7)

Use enough concrete detail to describe the scene clearly; avoid repetition and contradictions.
- `--description`: concrete biometrics (face, eyes, brows, lips, skin, hair) + scenario outfit + accessories. No `featuring` prefix, no `adult` filler, no `styled in ... tone` (builder adds identity, vocal-timbre anchor, age and tone).
- `--scene`: multi-sentence setting, fabrics, lighting (neon, 2 AM, bulbs, candlelight… replaces default late-afternoon light), and motion. Observed risks: sipping from a mug/glass warped the rim thumb and cut off the sip in tested clips (also in `--end-action`); splayed fingers on hips/tables risk warping. Options: rest five-finger hands on a prop in frame (glass stem, mug, purse strap, lapel), relax at sides/lap, follow `--image`, or frame tighter. First sentence becomes `summary:` unless `--summary` is passed.
- **Voice fidelity**: Pair the actor with their iconic `INDEX` character (`--character` + `--actor`) AND end `--scene` before speech with an explicit vocal-timbre + delivery cue matching the speaker (Reference §0.5). Peppy cues (`amused, teasing`, `bubbly`) raised pitch in tested clips while composed cues (`a wry tired smile`, `calm deadpan poise`) stayed near register — match delivery to the speaker.
- `--camera`: shot scale + lens + movement (`medium-wide waist-up shot including tabletop, 35mm lens, slow dolly push-in`). Motion words drop "camera locked off". Tight framing without waist-up/tabletop context (default static 50mm medium) often crops hands; frame wider when hands matter.
- `--aspect`: `9:16` (default 768x1344 → 1536x2688), `16:9` (1344x768 → 2688x1536), `1:1`, `4:3`, `3:4`; or `--size WxH`.
- `--seconds`: one continuous shot up to **10 s (243f; 15 s single shots fail on 16 GB)**. Longer, beatless asks → stitched cells.
- **2+ `--beat`** (+ `--beat-*`): ONE graph, native 22f AV latent-tail continuation, no stitch; RefMod every beat, `--image` beat 1 only, windows ≤ 243f; reuse beat 1's camera and continue prior beat's end state (airlock). Verified 379f. Reference §0.7.
- `--dialogue`: spoken words only (~8–15 words per 5 s). No timestamps, tags, backticks, "no speech", "room tone". Omit for silent clips. `--end-action`: verb phrase without subject (`holds a wry smile and winks slowly`; sipping risks cutoff); `--pronoun he|they` when needed.
- Optional `--image <approved_characters path>`: guides frame 0 composition, outfit, pose, lighting and setting via `MiniMaxH3AddGuide` (`frame_idx=0`, no `<Picture N>` in text) while `RefMod` applies face likeness (retained face/pitch in a tested pair, not universal proof). **When `--image` is passed, match its wardrobe, lighting, setting, and pose — never contradict the still.**
- Optional second person: `--name2/--character2/--actor2/--description2/--dialogue2`; write `(S1)`/`(S2)` inside `--scene`.

Name mapping: prefer pairing `INDEX` character + actor (`--name "<Actor>" --character "<Character>" --actor "<Actor>"`; Reference §0.5) — improved voice likeness in tested clips even on `INDEX: bad` rows; use actor-alone only when no `INDEX` row exists.

## Autonomous recipe — ONE command, then reply

```powershell
& 'C:\AI\director\.venv\Scripts\python.exe' 'C:\AI\community\scripts\parody\submit_parody_run.py' `
  --name '<Actor>' --character '<Character>' --actor '<Actor>' --tone 'satirical adult parody' `
  --seconds 10 --aspect 16:9 --camera '<framing + motion>' `
  --description '<biometrics + outfit>' --scene '<scene + hands on prop + voice cue>' `
  --dialogue '<spoken words only>' --end-action '<holds a wry smile>' --wait --qnap-put
```

- Submits, holds no LLM turn during render, waits for `BATCH closed`, finalizes RTX 2x `<run_dir>\clip.mp4` (stitches cells only), uploads `pi-drop/<run>.mp4`, and prints JSON (`final_mp4`, `qnap_path`, `objective`, `batch_rc`).
- **Do NOT** poll in PowerShell or run `ls`, `dir`, `ffprobe` or QNAP listings afterwards. Exit 0 → reply straight in chat with `final_mp4`, `qnap_path`, `OBJECTIVE`, and one sentence on scene/line. Exit 7 / `gpu_busy` → say GPU is busy and stop. `ValueError` → quote it, fix your wording once if yours, else stop.

## Sibling skills

`h3-prompting`, `h3-max-ref2va-prompt`, `video-render` / `comfy-render`.
