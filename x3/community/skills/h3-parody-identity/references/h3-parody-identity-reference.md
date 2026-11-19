---
pending_upload: true
title: h3-parody-identity full reference & history (active 4bc9bba 1-pass baseline + superseded 2-pass archive)
updated: 2026-11-06
owner: Max Architect 3 (governed by Alfred · Chief of staff)
---
# `h3-parody-identity` — Full Reference

Active skill (`< 6,000 B`, a cap not a fixed byte count): AlienPc's live copy is `/home/derekboone/AI/community/skills/h3-parody-identity/SKILL.md`. Intended mirror destinations — not claimed to be in sync until a SHA256 comparison after an edit has proved it — are `20_skills/current/h3-parody-identity/SKILL.md`, `10_packs/max/h3-parody-identity-reference.md` and `20_skills/current/h3-parody-identity/references/h3-parody-identity-reference.md`. The Linux box path `/home/box/agent-data/workflows/h3-parody-identity/SKILL.md` was not updated by this pass. On AlienPc, `C:\Users\derek\.pi\agent\skills\h3-parody-identity` is a junction to the community skill; `C:\Users\derek\.pi\agent\skills\comfy-render` is a standalone plain directory copy, verified separately.

## 0. Dynamic pipeline (T1 U1–U5, Derrick `t260s1142` / `t261u` / `t263u` / `t264u` / `t271u`, Nov 6, 2026)

Code: `/home/derekboone/AI/community/scripts/parody/{build_request.py, resolve.py, submit_parody_run.py}` + `test_parody_dynamic.py`. Template files on disk stay hash-locked (`b2_refmod.api.json` `3A6AD9AD…`, `b2.api.json` `124FB133…`); all changes are made to the in-memory graph.

### 0.1 Measured 16 GB VRAM ceiling (RTX 5080, 16,303 MiB) — why single shots cap at 243f

| Frames | Seconds | Canvas | Sampling wall | s/frame | Peak VRAM | Verdict |
|---|---|---|---|---|---|---|
| 124 | 5.17 | 768x1344 | 2m 52s (queue 10:54:49 → OBJECTIVE 10:57:41) | 1.39 | — | ok |
| 243 | 10.125 | 1344x768 | 5m 29s (11:22:29 → 11:27:58) | 1.35 | 15,412 MiB | ok, linear |
| 362 | 15.08 | 1344x768 | > 16 min, aborted (STOP file 11:45:43) | — | 15,847 MiB (spill to shared RAM) | **FAIL** (`t271u`) |

`SINGLE_CLIP_MAX_FRAMES = 243`. `--frames > 243` raises `ValueError`; `--seconds > 10.125` with no beats auto-splits into shared-anchor cells (2+ `--beat` builds one native continuation graph instead, §0.7). A 15–20 s single-`--seconds` video renders as 2 cells (e.g. 2x175f, 2x192f, or 243f + 124f) in one GPU batch in ~8 min instead of >15 min. `H3_HARD_MAX_FRAMES = 362` stays only as the trained-limit clamp for `snap_h3_frames(max_frames=...)`.

### 0.2 CLI reference (`submit_parody_run.py`; `build_request.py` takes the single-clip subset)

- Identity: `--name` (req), `--character`, `--actor`, `--description` (req, no word cap), `--tone`.
- Content: `--scene` (rich; first sentence → `summary:` when > 180 chars or multi-sentence), `--summary`, `--dialogue` (spoken words only), `--end-action`, `--pronoun she|he|they`.
- Length: `--frames N` (H3 grid, ≤ 243) or `--seconds S` (`snap_h3_frames`: `(f-5) % 17 == 0`, 56..243). `--beat` (repeat 2+) + `--beat-dialogue` / `--beat-camera` / `--beat-seconds` → one native latent-tail continuation graph (§0.7).
- Canvas: `--aspect 9:16|16:9|1:1|4:3|3:4|portrait|landscape|widescreen|square` (768x1344, 1344x768, 1024x1024, 1152x864, 864x1152) or `--size WxH` (multiples of 32, 256..2048).
- Camera: `--camera "<framing, lens, motion>"`. There is no locked-off tail. When the scene has a `The camera holds ...` sentence, the `[cam]` header is derived from it; otherwise the default header is `[static medium shot, eye level, 50mm lens, shallow depth of field]`. A still camera is one positive framing sentence (official H3 §4.3); add amplitude and speed only when the camera moves.
- Images (U2, live `d53e082` / Nov 6): `--image` takes **exactly one** `approved_characters` path (full path or sub-path inside `/home/derekboone/AI/5slock/approved_characters` or `\\NAS4CBE37.local\home\AlienPc-approved\approved_characters`); `>1` raises `ValueError`; any `sydney` path or anything outside the pools → `ValueError`. Staged to `ComfyUI\input\community\parody_ref_<sha10>_<stem>.<ext>`, wired as `img_1: LoadImage` → `add_guide: MiniMaxH3AddGuide` (`frame_idx=0`) → `refapply: MiniMaxH3RefModApply` (conditioning chain `c0 → add_guide → refapply → s0_guide`). **No** `c0.ref_images`, **no** `<Picture N>` / `[reference generation]` / `retention_analysis:` in the prompt — Qwen sees text-only, so voice stays intact. Derrick (`t314u`, watched clips): `RefMod` still drives the celebrity's face likeness onto the AddGuide shot (e.g. Emilia Clarke face on a generic apartment still) while keeping voice. Omit `--image` for RefMod-only composition; pass `--image` to pin frame-0 composition/wardrobe/pose/setting.
- Second subject (U4): `--name2 --character2 --actor2 --description2 --dialogue2 --pronoun2`; RefMods merge 4 + 4 into `mod_1..mod_8` (spare slots go to whoever has more); `(S2)` line in `subject_definitions`, accurate `Non-speaking characters:`, `(S2): <d>…</d>` when it speaks; the scene/summary drop the `(S1)` prefix, so write `(S1)`/`(S2)` inside `--scene`.
- Run control: `--seed`, `--slug`, `--run-dir`, `--dry-run`, `--wait`, `--qnap-put`, `--wait-timeout` (default 3 h).

### 0.3 Prompt tweaks (`t261u` / `t263u`)
- Removed `Adult cast, adults-only, fictional 18+ adult scene.` from `summary:`. `format_parody_prompt` checks `comm.guard_ok` only; prompts no longer must contain 'adult' or a stated age (Derrick 2026-11-11 t835u).
- Zero word caps anywhere (resolve/build/submit). A 600-word scene is a CPU test.

### 0.4 `--wait --qnap-put` and the shared-anchor stitch flow
1. All graphs are built in memory first (guard, KEEP dials and the frame cap fail before `run_dir` exists).
2. Single clip or 2+ `--beat` continuation → tag `clip` (one graph). Long `--seconds` cells → `c01_s<seed>`, `c02_s<seed+1>`, … (each with its own `request.api.json` + `prompt.txt`), same resolved identity, RefMod slots, canvas and staged images; `_render_order.json` carries `"cell_contract": true` so `run_queue.py` renders all of them in ONE lock window.
3. `run_queue.py --size WxH --frames N --detach` (graph is the OBJECTIVE authority), then poll `_render_queue.log` for a new `BATCH closed rc=N`. Default post-pass (`be7fd28`): NVIDIA `RTX Video Super Resolution ULTRA 2x @ 24fps` (e.g. `768x1344` → `1536x2688`); keeps `<tag>_raw.mp4` beside the upscaled `<tag>.mp4`; `--no-upscale` opts out.
4. rc 0: single → copy `<run>\clip\clip.mp4` (fallback newest `ComfyUI\output\community\<run>\clip_*.mp4`) to `<run>\clip.mp4`; cells → ensure each `<run>\<cell>\<cell>.mp4` (run_queue copies them; fallback from ComfyUI output), run `scripts\queue\take_chain_stitch.py <run> --name stitched` (hard cuts + 60 ms audio crossfade, ffprobe-uniform check; discovers cells by `^c\d{2}_s\d+$`, `render_ok.json` optional), copy `_stitch\stitched.mp4` to `clip.mp4`.
5. `--qnap-put` → `pi_qnap.py put <run>\clip.mp4 pi-drop/<run>.mp4`. JSON out: `batch_rc`, `objective`, `final_mp4`, `qnap_path`, `wait_seconds`, compact `resolved`. Exit 0 only when the batch and finalize (and upload, if asked) succeed; 7 = GPU busy.

### 0.5 Review notes
- `wide10s` (243f 1344x768 dolly push-in) review: hands lifting a mug to sip warped the thumb at the rim and the sip got cut off; splayed fingers on hips/tables risked warping. These are **observed risks in tested clips, not absolute bans**: the skill gives options — rest five-finger hands on a prop in frame (glass stem, mug, purse strap, lapel), relax them at sides/lap, follow `--image`, or frame tighter — and notes that sipping in `--scene`/`--end-action` risks the same cutoff.
- The 50mm lens on its own does not set the crop; **tight framing does**. The default static medium has no waist-up/tabletop context, so it is a tight crop and drops hands out of frame; when hands matter, frame waist-up with the tabletop at 35mm. A wider framing at 50mm keeps hands in frame.
- **Practical descriptive guidance** — the scene aspects plus delivery, all written as plain descriptive text (the builder adds identity, the vocal-timbre anchor, age and tone):
  - *appearance*: `--description` with concrete biometrics — face, eyes, brows, lips, skin, hair; no `featuring` prefix, no `adult` filler, no `styled in … tone`.
  - *wardrobe*: the scenario outfit and accessories; when `--image` is passed, describe its wardrobe and never contradict the still.
  - *setting*: `--scene` multi-sentence setting and fabrics; its first sentence becomes `summary:` unless `--summary` is passed.
  - *lighting*: name the light (neon, 2 AM, bulbs, candlelight) to replace the default late-afternoon light — the lighting-cue gate of `9cfab36` is why an explicit cue is needed.
  - *framing/movement*: `--camera` with shot scale + lens + movement. There is no locked-off tail; a still camera is one positive framing sentence, with amplitude and speed only when it moves. Frame wider when hands matter (above).
  - *actions*: what happens in the shot, with hands placed as above; in multi-beat work each beat continues the prior beat's end state (§0.7).
  - *dialogue/delivery*: `--dialogue` spoken words only (~8–15 words per 5 s, no timestamps, tags, backticks, "no speech", "room tone"), and `--scene` ends before speech with an explicit vocal-timbre + delivery cue (below). Spoken lines are natural in-character talk (reacting, teasing, answering, asides to someone present), never narrating or describing what she is doing on screen, never stage directions or counts.
- **Nov 6 afternoon voice findings** (`acoustic.py` + Derrick `t314u` watched the clips; `videoReview` was wrong on both face and voice):
  - `MiniMaxH3AddGuide frame_idx=0` does **not** shift pitch register on a byte-identical Daenerys pair (`172 Hz` nophoto vs `176 Hz` photo) and **does not** wipe RefMod face — Clip 2 with a generic apartment still still looked like Emilia Clarke; RefMod carries face likeness onto the AddGuide shot while keeping voice. Scope: this is **one measured pair on one generic apartment still**, not universal `AddGuide` proof; the skill wording says "retained face/pitch in a tested pair".
  - Upbeat expression cues (`"amused, teasing"`, `bubbly`) raised median F0 **+30–45 Hz** while calm/composed cues (`"a wry tired smile"`, `"calm deadpan poise"`) + explicit vocal-timbre phrasing stayed near register (~`200 Hz`) **in the tested Cassie/Sweeney clips** — measured on that set, **not universal**; match delivery to the speaker.
  - Keep the speaking-line form (voice wording and a short concrete pitch/texture/pace cue stay outside `<d>`; only the `[English]` tag and the verbatim spoken words go inside, official H3 guide section 4.4):
    - `(S1) says in Sydney Sweeney's exact Cassie Howard voice with signature vocal timbre, a low, soft, breathy voice with light vocal fry, unhurried: <d>[English] words</d>`
    - `(S1) says in Emilia Clarke's exact Daenerys Targaryen voice with signature vocal timbre, a crisp British RP contralto cadence and calm authority: <d>[English] words</d>`
  - The Nov 6 tests showed the exact-voice name alone stayed at about 232 Hz, while adding the breathy vocal-fry cue brought it to about 200 Hz. Keep mood words that raise pitch (like `amused, teasing half-smile`) away from the speaking line.
  - Pairing the actor with their iconic INDEX character (`--character` + `--actor`; e.g. Cassie Howard + Sydney Sweeney, Daenerys Targaryen + Emilia Clarke, Jennifer Check + Megan Fox) produces **stronger voice likeness** than the actor name alone — Derrick confirmed Cassie Howard beat Sydney-alone — even on `INDEX: bad` rows. RefMod (`kind: video`) carries no audio tokens; character+actor naming in the prompt is the voice lever. Use actor-alone only when the actor has no `INDEX` character row.
  - The writer form above is the contract. The builder (`build_request.py`) still emits the voice line without a description and with a trailing `She uses ... voice ... consistently` sentence; that would be a code change, and this documentation pass does not change the builder.

### 0.7 Native multi-beat continuation (2026-11-06, Derrick t358u–t374u; commit `1ac31d7`)
- Trigger: 2+ non-empty `--beat` (`submit_parody_run.py` `elif beats and len(...) > 1`). Builder: `build_request.build_continuation_request`. One graph, one `clip.mp4`, no stitch. A long `--seconds` with no beats still uses the §0.4 shared-anchor cells (`test_long_seconds_auto_split`).
- Nodes (installed `comfyui-minimax-h3-continuation`, `example_workflows/guided_continuation.json`): beat 1 = normal graph (`AddGuide frame_idx=0` only if `--image`); each later beat = `MiniMaxH3GuidedContinuationWindow` → `MiniMaxH3LatentTailGuide` → `SamplerCustomAdvanced` → `MiniMaxH3AppendContinuation`. Beat 2 reads beat 1's sampled AV latent `["s0_samp", 0]` (not `c0` output 1, the unsampled latent); beat 3+ read `["c<n-1>_append", 0]`. `s0_sep` decodes the last append.
- Frame math: overlap 22 (17k+5), extension multiple of 17; sampled window = overlap + extension ≤ 243; final = previous + extension; the hidden overlap is trimmed from video and audio by the append node. `run_queue.graph_expect` adds every `extension_frames`.
- RefMod on every beat (`c<n>_refapply` → `LatentTailGuide.positive`); start photo beat 1 only.
- Prompt airlock: beat 2+ text starts with the builder's lead-in (same framing, pose, wardrobe, light, natural micro-motion, no angle change or reset), then the beat's action — keep beat 1's camera on every beat and continue the prior beat's **end state**, with only natural micro-motion across the 22-frame join. Pass beat 1's camera as every `--beat-camera`; a different camera at the join contradicts the lead-in. `--image`/`AddGuide` on beat 1 only, `RefMod` on every beat (nodes above).
- Documentation scope: this section documents the graph the code already builds (`1ac31d7`). The Nov 6 documentation pass changed no runtime file, CLI flag, ComfyUI node, dial, test, endpoint, route, default, or graph template.
- Verified: `runs\parody_daenerys_2beat_cont_20261106_183156`, 2 beats 192 + 187 ext = 379f (15.79 s), window 209; OBJECTIVE ok, RTX 2x 1536x2688 24fps, audio 15.79 s; ComfyUI ~603 s + upscale 19.6 s; tests 57 pass (continuation, dynamic, phase1). Derrick viewed it: looks good. Not tested: 3+ beats on GPU, ~60 s clips (runtime unmeasured), seam/voice on other scenes.
- Code changes go to Forge as one direct turn for 1–3 steps, `ralph.ps1` only for 4+ step multi-pass code jobs; renders queue `run_queue.py` directly on the saved graph (no `pi.ps1`/`ralph.ps1`).

### 0.6 History
- 2026-11-06 10:47 `9cfab36`: lighting-cue gate + tone dedupe + one-call fast path (PowerShell recipe).
- 2026-11-06 T1: dynamic pipeline above; the PowerShell polling recipe is replaced by `submit_parody_run.py … --wait --qnap-put`; the 11.4 KB skill (brain `ac28bee`) was trimmed to < 6,000 B with these internals moved here.
- 2026-11-06 `be7fd28`: `run_queue.py` default NVIDIA RTX VSR ULTRA 2x @ 24fps post-pass (keeps `<tag>_raw.mp4`; `--no-upscale` opt-out).
- 2026-11-06 afternoon: AddGuide U2 wiring documented; Derrick `t314u` confirmed RefMod face survives AddGuide + character/actor pairing improves voice; prompt-builder voice/end-action hygiene upgrade.

---

## 1. Active Locked Baseline (`4bc9bba` / `ab72d88`, Derrick Nov 6, 2026 `t218u` & `t375s1715`)
- **Graph (`templates/b2_refmod.api.json`)**: Single-pass `768x1344`, `8` steps (`euler` / `simple`, `shift` `12.0` video / `3.0` audio, `cfg=1.0`, `denoise=1.0`) on `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors`.
- **Identity (`INDEX + RefMod + PixlStash tags`)**: `MiniMaxH3RefModsLoader` (`mod_1..mod_8`, `strength=1.0`) → `MiniMaxH3RefModApply` (`retention=1.0`). All adult RefMods (OC, INDEX, PixlStash-tagged) are allowed, with stills from the PixlStash API or any image path; voice refs (`*_refmod_audio` + `<Audio 1>`) are for OCs only; named INDEX/celebrity parodies get the visual RefMod only and never `<Audio 1>` (main SKILL.md) (e.g. `FCSydny` -> `poolclub` visual + audio); 2-pass upscaler is retired; `18+` (`guard_ok` / youth lint) is the only content rule. `LoadImage` start photo (`img_1`) is used when `--image` or `writer-run --still` is passed.
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
- Weight, gravity, load, pressure, follow-through and angles (R23a/R23b): `h3-prompting` `references/motion-contact-anatomy.md`
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
Kept verbatim per non-deletion rule for historical audit reference only; superseded by Section 1 above (2-pass is retired; **today's code allows all adult RefMods; voice refs (`*_refmod_audio` + `<Audio 1>`) are for OCs only; named INDEX/celebrity parodies get the visual RefMod only and never `<Audio 1>` (main SKILL.md); `18+` is the only content rule**). Do not run 2-pass or treat historical notes below as current locks.

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
   - `<Subject 1> <Name>, <resolved character/actor biometric + wardrobe description>, the only person in the clip` — **one** full description (never paste another still's facial caption onto a named subject, and never append `"a fictional adult"`, `"styled in parody tone"`, or `(character ..., actor ...)` parentheticals).
   - Include `<Picture 1> is the start frame of [Shot 1] for setting, light and framing` **only** when `ref_image_1` is wired in the graph.
2. **`summary:`**:
   - `[reference generation] <natural prose summary of who, where, wardrobe, and the single physical transition/action of this clip>.`
   - Never append `"One adult performer, adults-only."` or policy prose.
   - Never dump raw beat-sheet field labels (`Set:`, `Wardrobe:`, `Props kept in hand:`, `Opening:`, `Ending:`, `Anchors:`, `Camera:`, `Method: planned cut`) into `summary:`.
3. **`retention_analysis:`**:
   - `<Subject 1> (appears in [Shot 1]): fully_preserved - face, hair, body, skin, wardrobe` (plus `<Picture 1>` line only when `Cond` is wired).
4. **`detailed_description:` — Real Per-Clip Camera, Action & Clean Speech**:
   - **Style line** (`The target video is a realistic photographic portrait of <Name>...`), followed by the clip's **actual camera line** (`R23` vocabulary: `The camera holds a static shot.`, `Tracking, slow, small amplitude...`, `Push In, slow, small amplitude...`) — never leave a hardcoded static camera line on a tracking/push-in clip.
   - **`[Shot 1]` (no timestamp, R8) must carry the clip's real pose and motion**: compile the beat sheet's opening posture, primary physical action, garment state, prop handling, and ending posture directly into `[Shot 1]`. Never leave smoke-test boilerplate (`"stands facing the camera, weight even on both feet, hands resting lightly at her sides... PRIMARY MOTION - small steady upper-body sway"`) on multi-clip scenes where the subject walks, sits, leans, undresses, or drinks, because H3 obeys `[Shot 1]` over `summary:`.
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
   - Enforce `comm.guard_ok` fail-closed at build time and write compliance fields (`guard_ok`, `character`, `actor`, `tone`, `description_sha256`) to `run_record.json`.
2. **Tone fidelity & prompt readback**:
   - Preserve the exact wardrobe, framing, and consensual adult/provocative parody tone specified in the user's brief (never sanitize a requested provocative parody into tame generic filler).
   - On multi-clip runs, inspect a sample of generated `prompt.txt` files (including silent and spoken cells) before `run_queue.py` launches so `<d>...</d>`, `[Shot 1]`, and `loaded_refmods` are verified before GPU spend.
```
