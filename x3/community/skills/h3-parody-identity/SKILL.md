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
- `h3-hc-render` / `comfy-render` - dials and submit (use `h3-hc-render`, not a missing `video-render`)

## RefLoRA hybrid (U5) + Cond provenance

Always INDEX + RefMod **with Cond** (R10 / FG-11). Cond still must come from `approved_characters` and match `ComfyUI/input/<basename>` by SHA256 (FG-2).

### CLI (`scripts/parody/build_request.py` + `submit_parody_run.py`)

| Flag | Purpose |
|---|---|
| `--image <name>` | ComfyUI/input-relative Cond filename (e.g. `hoot_start.jpg`) |
| `--cond-source <path>` | Absolute/relative path **inside** `approved_characters` (required for fail-closed provenance; if omitted with `--image`, resolver only accepts the file when it uniquely exists under the pool) |
| `--stage-cond` | Copy validated `--cond-source` → `ComfyUI/input/<basename>` and verify SHA256 |
| `--graph-mode single-pass` | Default. Community single-pass `b2_refmod.api.json` (768×1344, 8-step) |
| `--graph-mode two-pass` | KEEP Lokken `b2.api.json` (384×672 → 2× upscale, AddGuide, pass-2 beta/3/0.4) |
| `--refmod-only` / `--disable-reflora` | Skip RefLoRA lookup so Arm A stays RefMod-only even when `*_reflora.safetensors` is on disk |
| `--dry-run` | (`submit_parody_run.py`) build + record only; never queue |

### U5 beta7 smoke arms (Derrick FG-1 keep-both, via Forge)

Cond for all arms: `approved_characters/HOOTERS01/hoot_start.jpg` → `ComfyUI/input/hoot_start.jpg`.

```text
# Arm A — Megan Fox / Jennifer Check, RefMod-only, single-pass
python scripts/parody/submit_parody_run.py --dry-run --refmod-only --graph-mode single-pass \
  --name "Megan Fox" --character "Jennifer Check" --actor "Megan Fox" \
  --description "<Forge vision caption of hoot_start.jpg>" \
  --image hoot_start.jpg --cond-source "C:/Users/derek/5slock/approved_characters/HOOTERS01/hoot_start.jpg" --stage-cond

# Arm B — Megan Fox + RefLoRA hybrid, single-pass
python scripts/parody/submit_parody_run.py --dry-run --graph-mode single-pass \
  --name "Megan Fox" --character "Jennifer Check" --actor "Megan Fox" \
  --description "<same caption>" \
  --image hoot_start.jpg --cond-source "C:/Users/derek/5slock/approved_characters/HOOTERS01/hoot_start.jpg"

# Arm B-2pass — Megan Fox + RefLoRA, Lokken two-pass b2.api.json
python scripts/parody/submit_parody_run.py --dry-run --graph-mode two-pass \
  --name "Megan Fox" --character "Jennifer Check" --actor "Megan Fox" \
  --description "<same caption>" \
  --image hoot_start.jpg --cond-source "C:/Users/derek/5slock/approved_characters/HOOTERS01/hoot_start.jpg"

# Arm D — Emilia Clarke / Daenerys + RefLoRA, single-pass
python scripts/parody/submit_parody_run.py --dry-run --graph-mode single-pass \
  --name "Emilia Clarke" --character "Daenerys Targaryen" --actor "Emilia Clarke" \
  --description "<same or per-arm caption>" \
  --image hoot_start.jpg --cond-source "C:/Users/derek/5slock/approved_characters/HOOTERS01/hoot_start.jpg"
```

Drop `--dry-run` only after Derrick's scoped GPU GO; Forge runs `run_queue.py` end-to-end (not this skill's job to start `ralph.ps1`).

Exact RefMod/RefLoRA id match: `minimaxh3_<id>_v<N>_refmod.safetensors` ↔ `..._reflora.safetensors`. Multi-version ambiguity blocks unless pinned.

## Sources

- Malcolm: `MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md` §6 Prompting with RefMods; `MINIMAX_H3_PROMPTING_GUIDE.md` subject_definitions name pattern; `known-characters/INDEX.md`
- Box decisions: Derrick Nov 5 2026 INDEX good/bad/fence + always INDEX+RefMod; Derrick Nov 5 ~2:25 CT: likeness gate = approved_characters only (screenshots OK in pool)
