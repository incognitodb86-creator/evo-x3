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

## RefLoRA (dual-half hybrid) - all three layers when a match exists

Community: Malcolm `ComfyUI-MiniMaxH3RefLoRA` (one `.safetensors` = LoRA weights + RefMod reference). Installed at ComfyUI `custom_nodes/ComfyUI-MiniMaxH3RefLoRA`; hybrids live in `models/loras/MinimaxH3/reflora/` (verified copies, never junctions).

- **Automatic:** `resolve_identities(..., reflora_dir=...)` looks for the exact pair `<id>_refmod` -> `<id>_reflora.safetensors`. Present + valid -> **INDEX + RefMod + RefLoRA**. Absent -> **INDEX + RefMod** fallback (reason recorded in `assets.json`). Present but broken (no LoRA tensors, stripped weights, unknown member equivalence) -> **block**, no fallback, no auto-download.
- **INDEX is never dropped** when RefLoRA is on: name + biometric description stay in `subject_definitions`; good/bad/fence voice semantics are unchanged.
- **Visual members only** (`components=Visual`); packed audio is never loaded - native voice stays with INDEX.
- **One injection route:** Load H3 RefLoRA patches MODEL (+CLIP) after the B2 model stack; its `mods` go to one `Apply H3 RefLoRA` chained after the RefMod Apply; `attach_to_model=false`. Never also load the hybrid in a generic LoRA loader.
- **Provenance:** a standalone RefMod byte-identical to the packed member is injected once (from the hybrid); distinct ones are both kept; total references stay <= 8.
- **Cond required:** the RefLoRA branch needs an approved still (`--image community/<file>.png`, staged from `approved_characters`) on the REF2VA Picture input; missing Cond blocks.
- **KEEP B2 unchanged:** graph is grafted from `templates/b2_refmod.api.json`; `reflora.frozen_diff` allows only identity/Cond/run fields. Pack example render settings are not adopted. Derived reference: `templates/b2_reflora.api.json`.
- GPU smoke (Megan Fox / Jennifer Check bad-row A/B + Daenerys control) needs Derrick's separate GPU GO.

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
