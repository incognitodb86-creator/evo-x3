---
name: h3-parody-identity
description: >-
  INDEX + RefMod celebrity/character parody and writer lane for MiniMax H3 — use for any named character, actor, celebrity, or writer-run video on the locked
  1-pass beta7_int8HQ graph (all adult RefMods and voice refs allowed; 18+ only), including
  autonomous chat execution from /home/derekboone/AI/render or writer-run builds.
---

> EVO-X3: renders run on AlienPc ComfyUI over Tailscale Serve (`https://alienpc.tailf242b2.ts.net:8446`). After Derrick's yes, run `render_writer_pipeline.py` with `--queue --yes-derrick` so it writes and queues in one pass (queue-remote.sh; adults guard and pytest gate stay).
# H3 parody / identity lane (INDEX + RefMod)

Internals, CLI, VRAM: `references/h3-parody-identity-reference.md` (brain: `10_packs/max/h3-parody-identity-reference.md`). Read only when changing pipeline.

## Locked baseline (Derrick, Nov 5–6, 2026; synced 2026-11-13)

- `templates/b2_refmod.api.json`, 1-pass, `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, 8 steps `euler`/`simple`, shift 12.0/3.0, RefModsLoader → RefModApply `retention 1.0`, plus `run_queue.py` default NVIDIA `RTX VSR ULTRA 2x @ 24fps` (`1536x2688` / `2688x1536`, keeps `<tag>_raw.mp4`; `--no-upscale` opt-out; on X3 remote mode, 2x upscale post-pass is deferred to AlienPc). **All adult RefMods (OC, INDEX, PixlStash-tagged in `~/AI/5slock/libraries/vault.db`; on the X3, PixlStash tags resolve on AlienPc only so pass `--character`/`--names`) and all voice refs (`*_refmod_audio` + `<Audio 1>`) are allowed; 2-pass is retired and 18+ (`guard_ok` / youth lint) is the only content rule.** New nodes/dials need Derrick's yes.
- INDEX + RefMod + voice refs resolve automatically in `resolve.py` + `fill_request.py` (`FCSydny` attaches `minimaxh3_oc_poolclub_v1_refmod_audio` and `minimaxh3_oc_poolclub_v1_refmod_visual`); report errors if a requested name has no local weights instead of downloading anything.
- Never open any `sydney` path (`~/AI/sydney/`). Never use minor-coded words (`underage`, `minor`, `child`, `children`) — `guard_ok` blocks the submit (`18+` only content rule).
- Writer-run lane (`~/AI/render`, Gemma 4 26B A4B Heretic arm A: `--provider x3-local --model gemma4-heretic` Q8_0 llama.cpp Vulkan + BF16 mmproj on the EVO-X3; `--provider llama-swap --model gemma4_heretic_poly` on AlienPc): use `render_writer_pipeline.py` (flags `--ask --position --still --still-read --character FCSydny --frames --shots --shot-count --scene --continue --partner2-still --template`) or `fill_request.py` when `writer_output.txt` is already written; after Derrick's yes, run `render_writer_pipeline.py` with `--queue --yes-derrick` (write and queue in one pass; no dry run first).
- On the EVO-X3, always stop dry at `READY`, paste `prompt.txt` to Derrick, and queue only after his explicit yes via `bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick`. Ask first for batches or downloads.

## Writing the arguments (Reference §0.5, §0.7)

Use concrete detail to describe the scene clearly; avoid repetition and contradictions.
- `--description`: concrete biometrics (face, eyes, brows, lips, skin, hair) + scenario outfit + accessories. No `featuring` prefix, no `adult` filler, no `styled in ... tone` (builder adds identity, vocal-timbre anchor, age and tone).
- `--scene`: multi-sentence setting, fabrics, lighting (neon, 2 AM, bulbs, candlelight… replaces default late-afternoon light), and motion. Observed risks: sipping from a mug/glass warped the rim thumb and cut off the sip in tested clips (also in `--end-action`); splayed fingers on hips/tables risk warping. Options: rest five-finger hands on a prop in frame (glass stem, mug, purse strap, lapel), relax at sides/lap, follow `--image`, or frame tighter. First sentence becomes `summary:` unless `--summary` is passed.
- **Voice fidelity**: Pair the actor with their iconic `INDEX` character (`--character` + `--actor`); the voice cue goes at the end of `--scene` before speech, with an explicit vocal-timbre + delivery cue matching the speaker (Reference §0.5). Peppy cues (`amused, teasing`, `bubbly`) raised pitch in tested clips while composed cues (`a wry tired smile`, `calm deadpan poise`) stayed near register.
- `--camera`: shot scale + lens + movement (`medium-wide waist-up shot including tabletop, 35mm lens, slow dolly push-in`). No locked-off tail; a still camera is one positive framing sentence, with amplitude and speed only when it moves. Tight framing without waist-up/tabletop context (default static 50mm medium) often crops hands; frame wider when hands matter.
- `--aspect`: `9:16` (default 768x1344 → 1536x2688), `16:9` (1344x768 → 2688x1536), `1:1`, `4:3`, `3:4`, or `auto` (closest preset to the start still); or `--size WxH`.
- `--seconds`: one continuous shot up to **10 s (243f; 15 s single shots fail on 16 GB)**. Longer, beatless asks → stitched cells.
- **2+ `--beat`** (+ `--beat-*`): ONE graph, native 22f AV latent-tail continuation, no stitch; RefMod every beat, `--image` beat 1 only, windows ≤ 243f; reuse beat 1's camera and continue prior beat's end state (airlock). Verified 379f. Reference §0.7.
- `--dialogue`: spoken words only (~8–15 words per 5 s). No timestamps, tags, backticks, "no speech", "room tone". Omit for silent clips. `--end-action`: verb phrase without subject (`holds a wry smile and winks slowly`; sipping risks cutoff); `--pronoun he|they` when needed.
- Optional `--image <approved_characters path>`: guides frame 0 composition, outfit, pose, lighting and setting via `MiniMaxH3AddGuide` (`frame_idx=0`, no `<Picture N>` in text) while `RefMod` applies face likeness (retained face/pitch in a tested pair, not universal proof). In the default (`guide`) path, the start still is frame 0 and is center-cropped to the canvas, so match `--aspect` to the still (or use `--aspect auto`), or pass `--still-mode ref` so the still is an un-resized reference on `c0` and is not cropped (`--still-mode ref` is implemented but untested on a real render until Derrick runs the later test). **When `--image` is passed, match its wardrobe, lighting, setting, and pose — never contradict the still.**
- Optional second person: `--name2/--character2/--actor2/--description2/--dialogue2`; write `(S1)`/`(S2)` inside `--scene`.

Name mapping: prefer pairing `INDEX` character + actor (`--name "<Actor>" --character "<Character>" --actor "<Actor>"`; Reference §0.5) — improved voice likeness in tested clips even on `INDEX: bad` rows; use actor-alone only when no `INDEX` row exists.

## Write and queue in one pass after Derrick's yes (X3 recipe)

1. After Derrick's yes (and after confirming AlienPc's GPU/lease is free), write and queue in one pass with the ONE writer command (`render_writer_pipeline.py`, which calls `fill_request.py` with a saved template in `templates/` and queues via `run_queue.py`) and `--queue --yes-derrick`:
```bash
~/AI/render/x3/.venv/bin/python ~/AI/community/scripts/parody/render_writer_pipeline.py <run_dir> \
  --ask "<ask>" --position <act> --still <still_path> \
  --character "<Character>" --actor "<Actor>" --names "<Character>" "<Actor>" \
  --queue --yes-derrick
```
(Without `--queue --yes-derrick`, `render_writer_pipeline.py` runs dry and stops at `READY`.)
- **Do NOT** poll manually; `--wait` waits for `BATCH closed` in `_render_queue.log` (`rc=0` ok; `rc=7` GPU busy). On `ValueError`, quote it, fix wording once if yours, else stop. After `rc=0`, optionally upload `<run_dir>/clip/clip.mp4` to QNAP `pi-drop/` per `AGENTS.md`.

## Sibling skills

`h3-prompting`, `h3-max-ref2va-prompt`, `video-render` / `comfy-render`.
