---
name: h3-parody-identity
description: >-
  INDEX + RefMod celebrity/character parody and writer lane for MiniMax H3 — use for any named character, actor, celebrity, or writer-run video on the locked
  1-pass beta7_int8HQ graph (18+ only), including
  autonomous chat execution from /home/evo/AI/render or writer-run builds.
---

> EVO-X3: renders run on AlienPc ComfyUI over Tailscale Serve (`https://alienpc.tailf242b2.ts.net:8446`).
> **Hermes Path B (default on EVO-X3):** Hermes writes the 4-header Beta 7 prompt itself (`h3-writer`), saves it to `<run_dir>/hermes_prose.txt`, and runs `render_writer_pipeline.py <run_dir> --prose-file <run_dir>/hermes_prose.txt ...` dry (never call the Python writer model). Queue only after Derrick's yes via `queue-remote.sh <run_dir> --yes-derrick`.
> *(Legacy pi Render Path A: dry-run `render_writer_pipeline.py --ask ...` without `--prose-file`, only if Derrick explicitly asks for the old pi render path.)*
# H3 parody / identity lane (INDEX + RefMod)

Internals, legacy CLI, VRAM: `references/h3-parody-identity-reference.md`. Read only when changing pipeline code.

## Locked baseline (Derrick, Nov 5–6, 2026; synced 2026-11-17 U56)

- Saved `10Eros_Max_h3_8stepTURBO_beta7_int8HQ` templates in `/home/evo/AI/community/templates/` (`plain`, `oc_guide`, `oc_ref`, `named_parody`, `talk`, etc.), 1-pass, 8 steps `euler`/`simple`, shift 12.0/3.0, RefModsLoader → RefModApply `retention 1.0`, plus `run_queue.py` default NVIDIA `RTX VSR ULTRA 2x @ 24fps` (`1536x2688` / `2688x1536`, keeps `<tag>_raw.mp4`; `--no-upscale` opt-out; on X3 remote mode, 2x upscale post-pass runs on AlienPc).
- **RefMod & Voice Rules (U56):**
  - **OC with audio weights (`FCSydny`):** Attach both visual and audio RefMods (`minimaxh3_oc_poolclub_v1_refmod_visual` + `minimaxh3_oc_poolclub_v1_refmod_audio` with `<Audio 1>`). `FCMegan` is a visual-only alias for Megan Fox (treated like a named parody below, no `<Audio 1>`).
  - **Named INDEX / celebrity parodies:** Attach visual RefMods **only** (`audio_refs` empty, **never** `<Audio 1>`). Voice comes exclusively from the character+actor voice line in `detailed_description:` (`(S1) says in <Actor>'s exact <Character> voice with signature vocal timbre, <cue>: <d>[English] ...</d>`).
  - **`--still-mode guide` (default) vs `--still-mode ref`:** In default `guide` mode, the start still pins frame 0 via `MiniMaxH3AddGuide` and **`<Picture 1>` is omitted**. `<Picture 1>` and the `[reference generation]` summary prefix appear **only** when `--still-mode ref` is passed.
  - **Local PixlStash vault on X3:** `/home/evo/AI/5slock/libraries/vault.db` is local on the EVO-X3; search stills via the PixlStash HTTP API (`character_id=1` for `FCSydny`, `2` for `FCMegan`), never by browsing folders. Report errors if a requested name has no local RefMod weights instead of downloading anything.
- Never use minor-coded words (`underage`, `minor`, `child`, `children`) — `guard_ok` blocks the submit (`18+` is the only content rule).
- **Single Writer Command (`/home/evo/AI/render`, `flash-next-uncensored` on EVO-X3):** Always use `render_writer_pipeline.py` (or `fill_request.py` when `writer_output.txt` already exists):
  - Flags supported on `render_writer_pipeline.py`: `<run_dir> --ask "<ask>" --position "<position>" --still "<still>" [--still-read "<json>"] [--character "<Character>"] [--actor "<Actor>"] [--names "<Name>" ...] [--frames <N>] [--shots single|multi] [--shot-count <k>] [--scene "<scene_id>"] [--continue "<prev_run_dir>"] [--partner2-still "<still>"] [--still-mode guide|ref] [--aspect 9:16|16:9] [--size WxH] [--template <name>] [--lora "<file>[:<strength>[:<trigger>]]"] [--realism-lora [<strength>]] [--queue --yes-derrick]`.
  - **Flux-generated celeb still auto-pickup:** When `--still` points to a still created with `flux_still.py` (or any ComfyUI PNG containing a Klein9 celeb RefMod or `loras/klein9/` celeb LoRA in its metadata / `flux_meta.json`), `render_writer_pipeline.py` and `fill_request.py` automatically detect the celebrity, link her to `INDEX.md` / `INDEX_BAD.md` + `aliases.json` for her iconic character & **text** vocal-timbre cue (visual RefMod only; never attach a celebrity voice audio ref per U56 #2), and attach her H3Max visual RefMod without re-specifying `--character`/`--names`.
  - **H3Max Beta 7 LoRAs (`M5` dropped):** The `fal/MiniMax-H3-Realism-People-LoRA` (`--realism-lora` / `r34l1sm`) was dropped and archived (Derrick t2885u). Do **not** pass `--realism-lora` or emit `r34l1sm` unless Derrick explicitly requests an H3 LoRA test for a specific run (for other H3 LoRAs, `--lora <file>[:<strength>[:<trigger>]]` remains supported).
  - *(Do **not** pass retired classic `submit_parody_run.py` flags such as `--description`, `--camera`, `--dialogue`, `--end-action`, or `--pronoun` to `render_writer_pipeline.py`; put scene/camera/quoted `<d>` dialogue inside `--ask`.)*

## Craft & Voice Guidance for `--ask` / `writer_output.txt`

Use concrete detail to describe the scene clearly; avoid repetition and contradictions:
- **Biometrics & Outfit:** Concrete biometrics (face, eyes, brows, lips, skin, hair) + scenario outfit + accessories. When `--still` is passed, keep the still for face/body/light/framing; if the ask specifies a different setting, wardrobe, or lines, the ask wins.
- **Hands & Props:** Observed risks: sipping from a mug/glass warped the rim thumb and cut off the sip in tested clips; splayed fingers on hips/tables risk warping. Prefer five-finger hands resting on a prop in frame (glass stem, purse strap, lapel), relaxed at sides/lap, or framed tighter.
- **Voice Fidelity (Named Parodies — Both `INDEX.md` and `INDEX_BAD.md` + Solo Celebrities):** Visual RefMods (`minimaxh3_<name>_v1_refmod`) lock the celebrity's face even when she sits in `INDEX_BAD.md`, while naming her in the speech tag triggers H3's audio weights for her voice! Prefer pairing the actress with her iconic `INDEX` character (`<Actor>'s exact <Character> voice with signature vocal timbre`; auto-mapped in `aliases.json` + `_DEFAULT_ICONIC_VOICE_ROLE` across 95+ actresses, even on `INDEX_BAD` rows like Sydney Sweeney / Cassie Howard or Megan Fox / Jennifer Check). When a celebrity has no separate character role (singers, models, creators like Sabrina Carpenter, Dua Lipa, Olivia Rodrigo, Billie Eilish, Madison Beer, Emily Ratajkowski), `<Actor>'s exact voice with signature vocal timbre` + her visual RefMod still carries her face and voice cleanly. Always lock the pitch/timbre cue to her low/chest/vocal-fry signature right before `<d>`, putting rough/CNC/taboo distress into quiet breath breaks and clipped pacing—never high/shrill/bubbly pitch adjectives that shift F0 +30–45 Hz.
- **Multi-Beat Sequencing (Extend-First Default vs. Planned Movie Cuts):** Every run writes a 9-field `<run_dir>/beat_sheet.json` (timestamps never enter `prompt.txt`). Past `243f` (`10.1 s`), **default to extending** (`--scene <id> --continue <prev_run_dir>` or native 22f AV latent-tail continuation) whenever staying in one continuous physical act/room so motion and audio flow without reset seams; use **separate planned-cut / stitched clips** intentionally when directing a multi-scene movie (location shifts, time jumps, distinct position chapters, or reverse-angle coverage setups).
- **Photorealism & Anti-AI Texture:** Always anchor unretouched 35mm cinema optics (24mm/35mm/50mm/85mm/135mm prime, shallow optical depth of field, motivated key/rim separation, shadow film grain) and matte skin with visible pores, fine vellus hair, natural joint creases, and elastic flesh compression under grip—never airbrushed, waxy, plastic, or glossy sheen.
- **Default Rough/Dominant/Taboo Stance:** On sex, oral, partner, and strip clips, heavy dominant leverage, CNC/overridden resistance, and raw situational or adult taboo family dirty talk (secrecy, proximity risk, authority, ownership, spoken contractions + connected Command -> Cracked Reply arc) are the default unless the ask explicitly asks for soft/gentle/romantic. Pure non-sex talk/parody setup clips follow the ask's genre attitude.
- **Aspect & Duration:** `9:16` (`768x1344`, default) or `16:9` (`1344x768`, when the plan asks). Single continuous shot up to **10.1 s (`243f` on the `17n+5` H3 grid; 15 s single shots fail on 16 GB VRAM)**.
- **Spoken Dialogue & Sound:** At most `2.5` spoken words per second (`2-3` lines on talk-only clips). Every quoted `<d>[English] ...</d>` line in `--ask` is preserved verbatim. End `detailed_description:` with 1–3 plain diegetic sound sentences (never `overall_soundscape:` or `non_diegetic_music:` headers).

## Write and queue in one pass after Derrick's yes (X3 recipe)

1. After Derrick's yes (and after confirming AlienPc's GPU/lease is free), write and queue in one pass with the ONE writer command (`render_writer_pipeline.py`, which calls `fill_request.py` with a saved template in `templates/` and queues via `run_queue.py`) and `--queue --yes-derrick`:
```bash
~/AI/render/x3/.venv/bin/python ~/AI/community/scripts/parody/render_writer_pipeline.py <run_dir> \
  --ask "<ask>" --position <act> --still <still_path> \
  --character "<Character>" --actor "<Actor>" --names "<Character>" "<Actor>" \
  --queue --yes-derrick
```
(Without `--queue --yes-derrick`, `render_writer_pipeline.py` runs dry and stops at `READY`.)
- **Do NOT** poll manually. On `ValueError`, quote it, fix wording once if yours, else stop. After `rc=0`, optionally upload `<run_dir>/clip/clip.mp4` to QNAP `pi-drop/` per `AGENTS.md`.

## Sibling skills

`h3-prompting`, `h3-max-ref2va-prompt`, `video-render` / `comfy-render`.
