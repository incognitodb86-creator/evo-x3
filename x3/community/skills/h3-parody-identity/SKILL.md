---
name: h3-parody-identity
description: >-
  INDEX + RefMod parody/identity lane for MiniMax H3 — use when a run names a
  character or actor from Malcolm's known-characters INDEX (or equivalent),
  stacks RefMods on single-pass 768x1344 B2 (beta7_int8HQ, no RefLoRA, no
  2-pass, no voice ref), and puts name + biometric description in the prompt.
---
# H3 parody / identity lane (INDEX + RefMod)

Community way (Malcolm Rey, HF `malcolmrey/various` h3-center docs, Sep 2026): RefMod usage is a **separate** guide from base H3 prompting. With RefMods loaded, skip positional `<Picture N>` identity tags and put the **name + biometric description** in `subject_definitions`. Full reference and history: `/workspace/cos/brain-staging/10_packs/max/h3-parody-identity-reference.md`.

## When to load

- Derrick asks for a named character / actor / celeb likeness parody run.
- Resolver hits INDEX `good` / `bad` / `onthefence` (`onthefence` = treat like `bad`).
- Any run that loads `MiniMaxH3RefModsLoader` for identity.

Do **not** load for ordinary approved-still REF2VA pastes that only use `<Picture N>` refs — those stay on `h3-max-ref2va-prompt` + `h3-prompting`.

## Locked baseline & hard bans (Derrick, Nov 5–6, 2026)

1. **Single-pass `768x1344` (`4bc9bba` / `ab72d88`, `templates/b2_refmod.api.json`)**: `8` steps (`euler` / `simple`, `shift` `12.0` video / `3.0` audio) on `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` + `MiniMaxH3RefModsLoader` (`strength_1: 1.0`) → `MiniMaxH3RefModApply` (`retention: 1.0`). **No `RefLoRA`, no `2-pass` upscaler, no `ref_audio` / voice ref, and no start photo by default.** Any new flag, node, or input requires Derrick's yes on a 1:1 question card first.
2. **Stills / conds / refs only from `approved_characters`.** That folder is the whole likeness gate (movie/TV screenshots OK once in the pool after the one-time adults-only check). No separate "no real-person photos" rule. Never Sydney paths.
3. Image/adults-only rules live only in the ComfyUI/render folder `AGENTS.md` — never add Forge global `AGENTS.md` rules without Derrick's card yes.
4. KEEP dials unchanged (`B2` / REF2VA 10strip eros beta7 stock). Max 8 RefMod slots (`mod_1…mod_8`; unused = `(none)`).

## INDEX status → what is native

| INDEX status | Face / look | Voice |
|---|---|---|
| **good** | H3-native from the name (still apply INDEX + matching RefMod + description) | native |
| **bad** / **onthefence** | look from RefMod (name alone is not enough for look) | native voice may still work |

Always apply **both** INDEX resolution and RefMods (never RefMod-only or prompt-only). When character and actor both resolve, stack both matching RefMods + INDEX assets (cap at 8 slots: keep character matches and highest INDEX status first). Fail closed if an installed RefMod resolves to empty `loaded_refmods`.

## Prompt shape (`4bc9bba` `build_request.py`)

```text
subject_definitions:
(S1) <Character> - an adult performer, age 28+, featuring <Character/Actor clause>, <biometric + wardrobe description>, styled in parody tone.

summary:
(S1) <scene summary>. Adult cast, adults-only, fictional 18+ adult scene. Non-speaking characters: none. No singing, no rapping, no songs, no music, no narration, no voice-over.

detailed_description:
[static medium shot, eye level, 50mm lens, shallow depth of field]
...
<scenedirect>
(S1): <d>[English in <Actor or Character>'s natural speaking voice] <spoken words only></d>
</scenedirect>
...
overall_soundscape:
quiet room ambience, soft natural room tone; the single close-micd human voice in the foreground.
no_dubs: no extra dubbing, no studio VO, no dubbing actors, no voice actors.
```

1. Put the **INDEX name** (character + actor per resolver) and **concrete biometric + wardrobe cues** in `subject_definitions` (avoid double `"featuring"` when passing `--description` to `submit_parody_run.py`).
2. Inside `<d>...</d>`, pass **spoken dialogue words only** — never beat-sheet timestamps (`t=00.00.000-...`), `"No speech"`, foley/SFX cues (`room tone`, `glass clink`), or backticks (H3 speaks stage cues aloud). On silent clips, omit `<d>...</d>` (`dialogue=None`).
3. Read generated `prompt.txt` before launching `run_queue.py` directly on ComfyUI (no `pi.ps1` / `ralph.ps1` wrapper for renders or tests).

## Sibling skills & sources

- `h3-prompting` (R1–R31), `h3-max-ref2va-prompt` (picture-ref REF2VA), `alienpc-hardcore-i2v-director`, `alienpc-stills-pose-edit-prompting`, `h3-hc-render` / `comfy-render` / `video-render`.
- Malcolm: `MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md` §6; `MINIMAX_H3_PROMPTING_GUIDE.md`; `known-characters/INDEX.md`.
- Derrick decisions: Nov 5, 2026 (`INDEX + RefMod`, BA-1 `approved_characters` gate) & Nov 6, 2026 (`t218u`/`t375s1715`: `4bc9bba` 1-pass `768x1344` baseline locked; `RefLoRA`, `2-pass`, and `ref_audio` retired).
