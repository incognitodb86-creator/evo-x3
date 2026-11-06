---
pending_upload: true
title: h3-parody-identity full reference & history (active 4bc9bba 1-pass baseline + superseded 2-pass archive)
updated: 2026-11-06
owner: Max Architect 3 (governed by Alfred · Chief of staff)
---
# `h3-parody-identity` — Full Reference

Active skill (`< 6,000 B`): `/home/box/agent-data/workflows/h3-parody-identity/SKILL.md` (mirrored at `20_skills/current/h3-parody-identity/SKILL.md` and `C:\AI\community\skills\h3-parody-identity\SKILL.md`, junctioned from `C:\Users\derek\.pi\agent\skills\h3-parody-identity`).

## 0. Dynamic pipeline (T1 U1–U5, Derrick `t260s1142` / `t261u` / `t263u` / `t264u` / `t271u`, Nov 6, 2026)

Code: `C:\AI\community\scripts\parody\{build_request.py, resolve.py, submit_parody_run.py}` + `test_parody_dynamic.py`. Template files on disk stay hash-locked (`b2_refmod.api.json` `3A6AD9AD…`, `b2.api.json` `124FB133…`); all changes are made to the in-memory graph.

### 0.1 Measured 16 GB VRAM ceiling (RTX 5080, 16,303 MiB) — why single shots cap at 243f

| Frames | Seconds | Canvas | Sampling wall | s/frame | Peak VRAM | Verdict |
|---|---|---|---|---|---|---|
| 124 | 5.17 | 768x1344 | 2m 52s (queue 10:54:49 → OBJECTIVE 10:57:41) | 1.39 | — | ok |
| 243 | 10.125 | 1344x768 | 5m 29s (11:22:29 → 11:27:58) | 1.35 | 15,412 MiB | ok, linear |
| 362 | 15.08 | 1344x768 | > 16 min, aborted (STOP file 11:45:43) | — | 15,847 MiB (spill to shared RAM) | **FAIL** (`t271u`) |

`SINGLE_CLIP_MAX_FRAMES = 243`. `--frames > 243` raises `ValueError`; `--seconds > 10.125` auto-splits into shared-anchor cells. A 15–20 s video renders as 2 cells (e.g. 2x175f, 2x192f, or 243f + 124f) in one GPU batch in ~8 min instead of >15 min. `H3_HARD_MAX_FRAMES = 362` stays only as the trained-limit clamp for `snap_h3_frames(max_frames=...)`.

### 0.2 CLI reference (`submit_parody_run.py`; `build_request.py` takes the single-clip subset)

- Identity: `--name` (req), `--character`, `--actor`, `--description` (req, no word cap), `--tone`.
- Content: `--scene` (rich; first sentence → `summary:` when > 180 chars or multi-sentence), `--summary`, `--dialogue` (spoken words only), `--end-action`, `--pronoun she|he|they`.
- Length: `--frames N` (H3 grid, ≤ 243) or `--seconds S` (`snap_h3_frames`: `(f-5) % 17 == 0`, 56..243). `--beat` (repeat) + `--beat-dialogue` / `--beat-camera` / `--beat-seconds` → cells.
- Canvas: `--aspect 9:16|16:9|1:1|4:3|3:4|portrait|landscape|widescreen|square` (768x1344, 1344x768, 1024x1024, 1152x864, 864x1152) or `--size WxH` (multiples of 32, 256..2048).
- Camera: `--camera "<framing, lens, motion>"`; motion words (push, pull, pan, tilt, track, dolly, handheld, orbit, crane, zoom, follow, move, sweep, arc) drop `Camera locked off, no zoom, no pan.`; default `[static medium shot, eye level, 50mm lens, shallow depth of field]` + locked-off tail.
- Images (U2): `--image` 1..4, full path or sub-path inside `C:\Users\derek\5slock\approved_characters` or `\\NAS4CBE37.local\home\AlienPc-approved\approved_characters`; any `sydney` path or anything outside the pools → `ValueError`. Staged to `ComfyUI\input\community\parody_ref_<sha10>_<stem>.<ext>`, wired as `img_N` LoadImage → `c0.ref_images.ref_image_N`; prompt gains `<Picture N> is the <--image-role> for [Shot 1].`, `[reference generation]` in summary and a `retention_analysis:` block. No `--image` → zero LoadImage nodes and zero `<Picture N>` tags (R33).
- Second subject (U4): `--name2 --character2 --actor2 --description2 --dialogue2 --pronoun2`; RefMods merge 4 + 4 into `mod_1..mod_8` (spare slots go to whoever has more); `(S2)` line in `subject_definitions`, accurate `Non-speaking characters:`, `(S2): <d>…</d>` when it speaks; the scene/summary drop the `(S1)` prefix, so write `(S1)`/`(S2)` inside `--scene`.
- Run control: `--seed`, `--slug`, `--run-dir`, `--dry-run`, `--wait`, `--qnap-put`, `--wait-timeout` (default 3 h).

### 0.3 Prompt tweaks (`t261u` / `t263u`)
- Removed `Adult cast, adults-only, fictional 18+ adult scene.` from `summary:`; `(S1) <name> - an adult performer, age 28+, …` satisfies `comm.adult_stated` (`format_parody_prompt` now checks `guard_ok` **and** `adult_stated`). `comm.py` and the guard tests are untouched.
- Zero word caps anywhere (resolve/build/submit). A 600-word scene is a CPU test.

### 0.4 `--wait --qnap-put` and the shared-anchor stitch flow
1. All graphs are built in memory first (guard, KEEP dials and the frame cap fail before `run_dir` exists).
2. Single clip → tag `clip`. Cells → `c01_s<seed>`, `c02_s<seed+1>`, … (each with its own `request.api.json` + `prompt.txt`), same resolved identity, RefMod slots, canvas and staged images; `_render_order.json` carries `"cell_contract": true` so `run_queue.py` renders all of them in ONE lock window.
3. `run_queue.py --size WxH --frames N --detach` (graph is the OBJECTIVE authority), then poll `_render_queue.log` for a new `BATCH closed rc=N`.
4. rc 0: single → copy `<run>\clip\clip.mp4` (fallback newest `ComfyUI\output\community\<run>\clip_*.mp4`) to `<run>\clip.mp4`; cells → ensure each `<run>\<cell>\<cell>.mp4` (run_queue copies them; fallback from ComfyUI output), run `scripts\queue\take_chain_stitch.py <run> --name stitched` (hard cuts + 60 ms audio crossfade, ffprobe-uniform check; discovers cells by `^c\d{2}_s\d+$`, `render_ok.json` optional), copy `_stitch\stitched.mp4` to `clip.mp4`.
5. `--qnap-put` → `pi_qnap.py put <run>\clip.mp4 pi-drop/<run>.mp4`. JSON out: `batch_rc`, `objective`, `final_mp4`, `qnap_path`, `wait_seconds`, compact `resolved`. Exit 0 only when the batch and finalize (and upload, if asked) succeed; 7 = GPU busy.

### 0.5 Review notes
- `wide10s` (243f 1344x768 dolly push-in) review: hands lifting a mug to sip warped the thumb at the rim and the sip got cut off → the skill now says hands rest still on a prop and no sipping, including in `--end-action`.
- The 50mm static default crops hands out of frame; when hands matter, frame waist-up with the tabletop at 35mm.

### 0.6 History
- 2026-11-06 10:47 `9cfab36`: lighting-cue gate + tone dedupe + one-call fast path (PowerShell recipe).
- 2026-11-06 T1: dynamic pipeline above; the PowerShell polling recipe is replaced by `submit_parody_run.py … --wait --qnap-put`; the 11.4 KB skill (brain `ac28bee`) was trimmed to < 6,000 B with these internals moved here.

---

## 1. Active Locked Baseline (`4bc9bba` / `ab72d88`, Derrick Nov 6, 2026 `t218u` & `t375s1715`)
- **Graph (`templates/b2_refmod.api.json`)**: Single-pass `768x1344`, `8` steps (`euler` / `simple`, `shift` `12.0` video / `3.0` audio, `cfg=1.0`, `denoise=1.0`) on `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`.
- **Identity (`INDEX + RefMod` only)**: `MiniMaxH3RefModsLoader` (`mod_1..mod_8`, `strength=1.0`) → `MiniMaxH3RefModApply` (`retention=1.0`). Zero `RefLoRA` (`ComfyUI-MiniMaxH3RefLoRA.disabled`, weights archived to `C:\AI\_archive\2026-11-06-refmod-only\`), zero `2-pass` upscaler, zero `LoadAudio` / `ref_audio` voice ref, zero `LoadImage` start photo by default.
- **Direct execution**: Queue `run_queue.py` directly on saved `request.api.json` or `submit_parody_run.py` output — no `pi.ps1`, no `ralph.ps1`, no local LLM load. Any new CLI flag, ComfyUI node/input, multi-file edit, or test arm requires a 1:1 question card yes from Derrick first.
- **Dialogue / beat-sheet hygiene**: Never pass beat-sheet timestamps (`t=00.00.000-...`), `"No speech"`, foley/SFX cues (`room tone`, `glass clink`, `heels on wood`), or backticks inside `--dialogue` / `<d>...</d>` (H3 TTS speaks stage cues out loud). Pass spoken words only inside `<d>...</d>`, and omit `<d>` (`dialogue=None`) on silent clips. Always inspect generated `prompt.txt` before `run_queue.py`.

---

## 2. Full `4bc9bba` + BA-1 Skill Text (Pre-Trim Reference)

```markdown
---
name: h3-parody-identity
description: INDEX + RefMod parody/identity lane for MiniMax H3 — use when a run names a character or actor from Malcolm's known-characters INDEX (or equivalent), stacks RefMods, and needs name + biometric description in the prompt. Not for ordinary picture-ref REF2VA pastes (h3-max-ref2va-prompt) or shared R1–R31 paste shape (h3-prompting).
---

# H3 parody / identity lane (INDEX + RefMod)

Community way (Malcolm Rey, HF `malcolmrey/various` h3-center docs, Sep 2026): RefMod usage is a **separate** guide from base H3 prompting. With RefMods loaded, skip positional `<Picture N>` identity tags and put the **name + biometric description** in `subject_definitions`.

## When to load

- Derrick asks for a named character / actor / celeb likeness parody run.
- Resolver hits INDEX good / bad / onthefence (onthefence = treat like bad).
- Any run that loads `MiniMaxH3RefModsLoader` for identity.

Do **not** load for ordinary approved-still REF2VA pastes that only use `<Picture N>` refs — those stay on `h3-max-ref2va-prompt` + `h3-prompting`.

## Hard bans (Derrick)

1. **Stills / conds / refs only from `approved_characters`.** That folder is the whole likeness gate (movie/TV screenshots OK once they are in the pool after the one-time adults-only check). No separate "no real-person photos" rule.
2. Image/adults-only rules live only in the ComfyUI/render folder `AGENTS.md` - do not add new Forge global `AGENTS.md` rules without Derrick's card yes.
3. Never Sydney paths.
4. KEEP dials unchanged (B2 / REF2VA 10strip eros beta7 stock). No 9th RefMod slot (loader max 8).

## INDEX status → what is native

| INDEX status | Face / look | Voice |
|---|---|---|
| **good** | H3-native from the name (still apply INDEX + matching RefMod + description) | native |
| **bad** / **onthefence** | look from RefMod (name alone is not enough for look) | native voice may still work |

Always apply **both** INDEX resolution and RefMods (never RefMod-only or prompt-only). When character and actor both resolve, stack both matching RefMods + INDEX assets. If stacked RefMods would exceed 8 slots: keep character matches and highest INDEX status; drop the rest.

## Prompt shape (RefMod lane)

Community install/usage guide pattern:

```text
subject_definitions:
<Subject 1> <INDEX Character or Actor Name>, <short biometric / wardrobe description>...

detailed_description:
... framing of <Subject 1> ...
```

Malcolm prompting guide also uses:

`<Subject 1> <Character Name> (played by <Actor Name>) from <Show>`

plus explicit physical traits in the shot lines.

On this box for parody:

1. Put the **INDEX name** (character and/or actor as the resolver chose) in `subject_definitions`.
2. Add a **short description** (face/hair/body/wardrobe cues) — name alone is incomplete.
3. With RefMods loaded, do **not** rely on `<Picture N> is the reference image defining…` for that subject's face (that is the picture-ref lane). Optional stills come only from approved_characters (scene/body/wardrobe or Cond/start — including movie/TV screenshots already in the pool).
4. Still obey shared motion/adults/speech rules from `h3-prompting` (R1–R31) and REF2VA section order from `h3-max-ref2va-prompt` when the graph is REF2VA — only the **identity binding** changes here.

## RefMod wiring (reminder)

`MiniMaxH3RefModsLoader` (mod_1…mod_8) → `MiniMaxH3RefModApply` on the REF2VA / I2V conditioning path. Prefer 2–3 RefMods per persona when available. Unused slots = `(none)`.

## Cinema / cuts / poses (not this skill)

Community (Malcolm H3 Prompting Guide + TenStrip HF 10Eros-Max notes) puts **camera angles, in-clip cuts, transitions, and motion** in the shared prompting rules - not in a separate identity doc. On this box that means:

- Shot headers, cut verbs, camera vocab (R8 / R23), speech, adults floor: `h3-prompting`
- REF2VA section order, style opening (R39), TenStrip retention/audio shape: `h3-max-ref2va-prompt`
- Cond still -> intent / director card / package triage: `alienpc-hardcore-i2v-director`
- Still pose unlock before I2V: `alienpc-stills-pose-edit-prompting`

This skill only changes **identity binding** (INDEX + RefMod + name/description). It does not invent a second camera grammar.

## Sibling skills

- `h3-prompting` - shared R1-R31 (includes camera / cuts)
- `h3-max-ref2va-prompt` - picture-ref REF2VA paste / R32-R44 / TenStrip-shaped retention+audio
- `alienpc-hardcore-i2v-director` - Cond-to-clip director card (angles as intent + camera hold)
- `alienpc-stills-pose-edit-prompting` - pose unlock on stills
- `h3-hc-render` / `comfy-render` / `video-render` - dials and submit
## Sources

- Malcolm: `MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md` §6 Prompting with RefMods; `MINIMAX_H3_PROMPTING_GUIDE.md` subject_definitions name pattern; `known-characters/INDEX.md`
- Box decisions: Derrick Nov 5 2026 INDEX good/bad/fence + always INDEX+RefMod; Derrick Nov 5 ~2:25 CT: likeness gate = approved_characters only (screenshots OK in pool)
```

---

## 3. Superseded Archive — Nov 6, 2026 6:43 AM `2-pass` Skill Text (`7,614 B`, RETIRED by `ab72d88` / `t375s1715`)
Kept verbatim per non-deletion rule for audit history only; **do not run 2-pass or strip `<scenedirect>`/`overall_soundscape:` from `4bc9bba` without a new Derrick card yes**.

```markdown
---
name: h3-parody-identity
description: >-
  Use when a MiniMax H3 run names a character or actor from INDEX (or
  equivalent), wires standalone RefMod on two-pass B2 (beta7_int8HQ, no RefLoRA,
  no start photo by default), or compiles multi-clip parody prompts from a beat
  sheet without spoken stage-cue leakage or static [Shot 1] boilerplate.
---
# MiniMax H3 Parody Identity (`INDEX + RefMod`)

One shared pipeline for every named character or actor parody run on MiniMax H3 (`10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`). Never build a separate skill or code path per celebrity — resolve every character or actor through the same `INDEX` + standalone `RefMod` lookup and two-pass B2 builder.

## 1. Identity & Render Stack (Two-Pass B2, `INDEX + RefMod` Only)

1. **Checkpoint & two-pass B2 geometry**:
   - Use `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` across both stages (sharper skin texture and contrast at ~110–135s/clip than the 18.7 GB `activation_learned_HQ` checkpoint).
   - **Pass 1 (`384x672`, 8 steps)**: `euler` / `simple`, `shift` `12` (video) / `3` (audio), `denoise=1.0`, `cfg=1.0`. Separate latent via `MiniMaxH3SeparateAVLatent`: Pass-1 audio (`s0_sep:1`) drives final `dec_a` directly.
   - **Latent upscale**: `MinimaxH3LatentUpscaler3D` (`Comfyui_Minimax_h3_latent_Upscaler` pack) upscales Pass-1 video (`s0_sep:0`) 2x to `768x1344`, recombined with Pass-1 audio via `MiniMaxH3CombineAVLatent` (`av_latent_override`).
   - **Pass 2 (`768x1344`, 3 steps)**: `euler` / `beta`, `shift` `12` / `3`, `denoise=0.4`, `cfg=1.0` for full-frame face and skin detail while preserving Pass-1 voice cadence.
2. **Standalone `INDEX + RefMod` only (no `RefLoRA`)**:
   - Wire `MiniMaxH3RefModsLoader` (`mod_1..mod_8` from `models/refmods/minimaxh3_<id>_v<N>_refmod.safetensors`, `strength=1.0`) -> `MiniMaxH3RefModApply` (`retention=1.0`) once into the positive conditioning feeding **both** Pass-1 (`s0_guide`) and Pass-2 (`s1_guide`).
   - Do **not** attach `RefLoRA` (`MiniMaxH3LoraLoaderModelOnly` / `LoraLoaderModelOnly`) on named-parody runs: `INDEX + RefMod` alone preserves the model's native voice timbre and cadence without synthetic vocal coloration.
   - **Fail closed on silent empty RefMod**: if a matching `models/refmods/minimaxh3_<id>_v<N>_refmod.safetensors` file exists on disk, `loaded_refmods` in `assets.json` must be non-empty (`mod_1 != "(none)"`). Never silently render name-only when a standalone RefMod is installed.
3. **No start photo by default; `approved_characters` is the entire still gate**:
   - Named-character/actor parody runs use **no start photo by default** (`--image` omitted -> omit `LoadImage`, `MiniMaxH3AddGuide`, and `<Picture 1>` everywhere in the graph and prompt).
   - When an optional scene/wardrobe still (`Cond`) is passed, it must come **only** from the `approved_characters` pool (movie/TV screenshots in that pool are allowed once admitted; do not layer a separate "no real-person photos" ban on top of `approved_characters`).
   - Optional `Cond` stills always stack **on top of** `INDEX + RefMod` — never run `Cond`-only for a named character.

## 2. Clean Five-Section Prompt Contract (`h3-prompting` R5 + R32–R42)

Keep `prompt.txt` strictly visual and acoustic — compliance metadata belongs in `run_record.json`, never in conditioning text:

1. **`subject_definitions:`**:
   - `<Subject 1> is the woman in <Video 1>.` (binds the `RefMod` conditioning route).
   - `<Subject 1> <Name>, <resolved character/actor biometric + wardrobe description>, the only person in the clip` — **one** full description (never paste another still's facial caption onto a named subject, and never append `"a fictional adult, canon age 28"`, `"styled in parody tone"`, or `(character ..., actor ...)` parentheticals). Stated adult age (21+) lives naturally inside the biometric description (`"25-year-old woman"`).
   - Include `<Picture 1> is the start frame of [Shot 1] for setting, light and framing` **only** when `ref_image_1` is wired in the graph.
2. **`summary:`**:
   - `[reference generation] <natural prose summary of who, where, wardrobe, and the single physical transition/action of this clip>.`
   - Never append `"One adult performer, adults-only."` or policy prose.
   - Never dump raw beat-sheet field labels (`Set:`, `Wardrobe:`, `Props kept in hand:`, `Opening:`, `Ending:`, `Anchors:`, `Camera:`, `Method: planned cut`) into `summary:`.
3. **`retention_analysis:`**:
   - `<Subject 1> (appears in [Shot 1]): fully_preserved - face, hair, body, skin, wardrobe` (plus `<Picture 1>` line only when `Cond` is wired).
4. **`detailed_description:` — Real Per-Clip Camera, Action & Clean Speech**:
   - **Style line** (`The target video is a realistic photographic portrait of <Name>...`), followed by the clip's **actual camera line** (`R23` vocabulary: `The camera holds a static shot.`, `Tracking, slow, small amplitude...`, `Push In, slow, small amplitude...`) — never leave a hardcoded static camera line on a tracking/push-in clip.
   - **`[Shot 1] 00:00.000 - <end_clock>` must carry the clip's real pose and motion**: compile the beat sheet's opening posture, primary physical action, garment state, prop handling, and ending posture directly into `[Shot 1]`. Never leave smoke-test boilerplate (`"stands facing the camera, weight even on both feet, hands resting lightly at her sides... PRIMARY MOTION - small steady upper-body sway"`) on multi-clip scenes where the subject walks, sits, leans, undresses, or drinks, because H3 obeys `[Shot 1]` over `summary:`.
   - **Speech `<d>[English] ... </d>` holds ONLY spoken words**:
     - When the character speaks, emit `<Subject 1> <Name> (S1) ... says, <d>[English] <spoken words only></d>` with punctuation limited to `, . ? !`.
     - **Never** pass beat-sheet timestamps (`t=00.00.000-...`), `"No speech"`, foley/SFX cues (`room tone`, `glass clink`, `paper, card stock`, `heels on wood`), backticks, or nested `<d>` tags into `--dialogue` / `<d>...</d>`. H3's TTS skips `t=` numbers and speaks stage cues out loud.
     - On silent clips, omit `(S1)` and `<d>...</d>` completely (`dialogue=None`).
   - **Plain ambient sound sentences** at the end of `detailed_description:` carry room tone and physical foley outside `<d>...</d>`. Never include `overall_soundscape:` or `non_diegetic_music:`.

## 3. Pre-Render Gates & Brief Fidelity

1. **Builder / test validation (fail closed before queuing)**:
   - Reject any `dialogue` input containing `t=\d`, `<d>`, `</d>`, backticks, `"no speech"` (case-insensitive), or `"room tone"`.
   - Reject raw beat-sheet schema headers (`Opening:`, `Ending:`, `Anchors:`, `Method:`) inside `summary:` or `detailed_description:`.
   - Verify ComfyUI `/object_info` exposes every node class in `request.api.json` (`submit_parody_run.py --dry-run`) before starting a batch.
   - Enforce `comm.guard_ok` and `comm.adult_stated` fail-closed at build time and write compliance fields (`guard_ok`, `adult_stated`, `character`, `actor`, `tone`, `description_sha256`) to `run_record.json`.
2. **Tone fidelity & prompt readback**:
   - Preserve the exact wardrobe, framing, and consensual adult/provocative parody tone specified in the user's brief (never sanitize a requested provocative parody into tame generic filler, while keeping `comm.guard_ok` vocabulary clean and zero non-consensual themes).
   - On multi-clip runs, inspect a sample of generated `prompt.txt` files (including silent and spoken cells) before `run_queue.py` launches so `<d>...</d>`, `[Shot 1]`, and `loaded_refmods` are verified before GPU spend.
```
