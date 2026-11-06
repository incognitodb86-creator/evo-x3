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

1. **No real-person photos** as refs/conds (no celeb stills into `ref_images` / LoadImage / encode inputs).
2. Image/adults-only rules live only in the ComfyUI/render folder `AGENTS.md` — do not add new Forge global `AGENTS.md` rules without Derrick's card yes.
3. Optional stills only from `approved_characters` (fictional pool). Never Sydney paths.
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
3. With RefMods loaded, do **not** rely on `<Picture N> is the reference image defining…` for that subject's face (that is the picture-ref lane). Optional approved_characters stills are scene/body/wardrobe conds only, never real-person photos.
4. Still obey shared motion/adults/speech rules from `h3-prompting` (R1–R31) and REF2VA section order from `h3-max-ref2va-prompt` when the graph is REF2VA — only the **identity binding** changes here.

## RefMod wiring (reminder)

`MiniMaxH3RefModsLoader` (mod_1…mod_8) → `MiniMaxH3RefModApply` on the REF2VA / I2V conditioning path. Prefer 2–3 RefMods per persona when available. Unused slots = `(none)`.

## Sibling skills

- `h3-prompting` — shared R1–R31
- `h3-max-ref2va-prompt` — picture-ref REF2VA paste / R32–R44
- `h3-hc-render` / `comfy-render` / `video-render` — dials and submit

## Sources

- Malcolm: `MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md` §6 Prompting with RefMods; `MINIMAX_H3_PROMPTING_GUIDE.md` subject_definitions name pattern; `known-characters/INDEX.md`
- Box decisions: Derrick Nov 5 2026 INDEX good/bad/fence + always INDEX+RefMod; FP-1 name likeness OK, no real photos as refs/conds
