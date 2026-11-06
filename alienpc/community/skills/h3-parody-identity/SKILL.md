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

- `templates/b2_refmod.api.json`, 1-pass, `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, 8 steps `euler`/`simple`, shift 12.0/3.0, RefModsLoader → RefModApply `retention 1.0`. **No RefLoRA, no 2-pass, no `ref_audio`.** New nodes or dials need Derrick's yes.
- INDEX + RefMod always; `submit_parody_run.py` resolves `aliases.json`, INDEX and RefMods itself and fails closed when a non-`good` name has no RefMod. Report that error; never download weights.
- Images only from `approved_characters` (`LANE_IMAGE_RULES.md`). Never any `sydney` path. Never minor-coded words (`girl`, `teen`, `school`, `kid`, `child`, `minor`, `student`, `cheerleader`, `dorm`) — `guard_ok` blocks the submit.
- Derrick's chat ask for a named parody **is** the go for one clip or one stitched clip set. Ask first only for batches or downloads.

## Writing the arguments (no word cap — 500+ words welcome)

- `--description`: face, eyes, brows, lips, skin, hair, scenario outfit, accessories. No `featuring` prefix, no `adult` filler, no `styled in ... tone` (the builder adds identity, age and tone).
- `--scene`: rich, literal, multi-sentence: setting, fabrics, lighting (neon, 2 AM, bulbs… replaces the default late-afternoon light), motion, and **both five-finger hands resting still on a prop in frame** (glass stem on the table, mug on the counter, purse strap, lapel) or relaxed in the lap. Never splayed fingers on hips or tables, and never lift a mug or glass to the mouth to sip (rim thumb warps, the sip gets cut off) — also not in `--end-action`. The first sentence becomes the summary unless you pass `--summary`.
- `--camera`: e.g. `medium-wide waist-up shot including tabletop, 35mm lens, slow dolly push-in`. Motion words drop "camera locked off". Default is a static 50mm medium shot, which crops hands, so frame wider when hands matter.
- `--aspect`: `9:16` (default 768x1344), `16:9` (1344x768), `1:1`, `4:3`, `3:4`; or `--size WxH`.
- `--seconds`: one continuous shot up to **10 s (243f, ~5.5 min render; 15 s single shots fail on 16 GB)**. Longer asks, or several `--beat "<scene>"` (with optional `--beat-dialogue`, `--beat-camera`, `--beat-seconds`), render shared-anchor cells in one GPU batch, stitched into one `clip.mp4`.
- `--dialogue`: spoken words only (~8–15 words per 5 s). No timestamps, tags, backticks, "no speech", "room tone". Omit for a silent clip. `--end-action` sets how she finishes (replaces the stock nod); `--pronoun he|they` when needed.
- Optional `--image <approved_characters path>` (1–4) anchors composition/wardrobe/setting via `<Picture N>`; identity still comes from the RefMod.
- Optional second person: `--name2/--character2/--actor2/--description2/--dialogue2`; write `(S1)`/`(S2)` inside `--scene`.

Name mapping: character → `--name "<Actor>" --character "<Character>" --actor "<Actor>"` (e.g. Jennifer Check → Megan Fox); a celebrity alone → `--name` and `--actor` both set to the name.

## Autonomous recipe — ONE command, then reply

```powershell
& 'C:\AI\director\.venv\Scripts\python.exe' 'C:\AI\community\scripts\parody\submit_parody_run.py' `
  --name '<Actor>' --character '<Character>' --actor '<Actor>' --tone 'satirical adult parody' `
  --seconds 10 --aspect 16:9 --camera '<framing + motion>' `
  --description '<rich biometrics + outfit>' --scene '<rich literal scene, hands on a prop>' `
  --dialogue '<spoken words only>' --end-action '<closing expression, no sip>' --wait --qnap-put
```

- It submits, holds no LLM turn during the render, waits for `BATCH closed`, writes `<run_dir>\clip.mp4` (stitching cells if any), uploads `pi-drop/<run>.mp4`, and prints JSON with `final_mp4`, `qnap_path`, `objective`, `batch_rc`.
- **Do NOT** write a PowerShell polling loop, and do **NOT** run `ls`, `dir`, `ffprobe` or a QNAP listing afterwards (`pi-drop` is on `G:`, already uploaded). Exit 0 → reply straight in chat with `final_mp4`, `qnap_path`, the `OBJECTIVE` line, and one sentence on the scene and line.
- Exit 7 / `gpu_busy` → say the GPU is busy and stop. A `ValueError` (missing RefMod, guard word, frames > 243, bad image path) → quote it, fix your arguments once if it was your wording, otherwise stop.
- Only read `aliases.json` / list RefMods if Derrick asks what exists or a spelling fails.

## Sibling skills

`h3-prompting` (shared R-rules), `h3-max-ref2va-prompt` (picture-ref REF2VA without RefMods), `video-render` / `comfy-render` (queue mechanics).
