# 2026-11-03 - REF2VA split into its own skill (h3-max-ref2va-prompt)

**FIX / DONE** - Derek's ask: "Ensure our ref2va is a separate skill for h3max and our setup."
Companion review: `notes/2026-11-03-h3-upstream-prompt-skill-review.md` (read-only, earlier the same day).

## What exists now

- **New skill: `h3-max-ref2va-prompt`** - `C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md` (234 lines) +
  `references\chain-lane.md` (37 lines). Rules **R32-R44**, scoped to MiniMax H3-Max / 10Eros-Max beta7 on this box,
  REF2VA = the standing lane (AGENTS.md route updated).
- **`h3-prompting` keeps R1-R31** (cross-lane rules) + a new section 9 "rule index and rule homes" so any `R<n>`
  citation resolves from one table. It states the lane split in its frontmatter and section 0, adds checklist item 12
  (REF2VA pastes run the second gate), and its section 7 pointer now names the new skill.
- **Old lane files moved, nothing deleted:** `references\ref2va-lane.md` and `references\ref2va-chain-lane.md`
  originals → `C:\AI\community\archive\2026-11-03-ref2va-split\`; thin pointer files left at the old paths so every
  old citation resolves. Backups `*.bak-20261103-ref2va-split` next to each edited file.

## Rule provenance (new rules only)

| Rule | Content | Source |
| --- | --- | --- |
| R32 | hosted `overall_soundscape:` / `non_diegetic_music:` stay out; they are H3-Context-IR output | MiniMax-H3 README ("H3-Context-IR is not included in this open-source release"); TenStrip HF #77; local R7 kept |
| R33 | full label set `<Picture>/<Video>/<Audio>/<Subject>`, limits, presentation order, audio label index-paired to a video, audio never in the text-encoder vision path; **our graph wires `ref_images.ref_image_1` only, so `<Video N>`/`<Audio N>` are a labelled arm** | `nodes_minimax_h3.py:243-284,335`, `comfy/text_encoders/minimax.py:3-13,178`, upstream ref-en §2; `scripts/comm.py:120-149` |
| R34 | task-type tag vocabulary + selection rules, and the honest subset this graph can emit | upstream ref-en §3 |
| R35 | role-scoped retention markers, per-shot listing, added action is not a fidelity loss, audio markers, no `(Sx)` in `retention_analysis` | upstream ref-en §4 |
| R36 | ref-mode frame anchors as prose, storyboard-reference line for chain panels, **the I2VA/FL2VA/L2VA alignment line must not be pasted into REF2VA** (no core node injects it) | upstream ref-en §2.2, §5.3; base-en §2.1; `nodes_minimax_h3.py` (no such string) |
| R37 | speech form `<d>[English] ...</d>` + `(S1)` IDs + voice-over + lips-closed + `[unclear]` + punctuation rules; tokens exist on this box; **speech never measured here** | `minimax.py:32` (`<d>` 151669, `</d>` 151670, `<|cutoff|>` 151671, lyrics/caption tokens); base-en §4.4, ref-en §5.4 |
| R38 | all sections English; original language only inside `<d>` and for visible on-screen text, quoted verbatim untranslated | upstream ref-en preamble, base-en §4.5 |
| R39 | style opening: 1-2 sentences before `[Shot 1]`, derived from the start image's records | upstream ref-en §5.2; local R14/R23 unchanged |
| R40 | `<scenetrans>` is not in this build's token table → prose continuity; `<|cutoff|>` is real; token names exactly as in the table | `minimax.py:32` |
| R41 | length provenance: upstream's 350-500 words is the hosted writer's style target; R9 (no cap) wins; hard limit is the tokenizer overflow | ref-en §5.2; `minimax.py:160` |
| R42 | a paste must match what the graph can feed (builder contract) | `scripts/comm.py:120-149` |
| R43 | chain cells: shared definitions, identical labels/ordinals, latent-tail mechanism, one axis per cell | `comm.py build()` (continuation nodes), R28-R30 |
| R44 | REF2VA gate runs after the shared gate; both pass before staging | this split |

## Corrections made to existing text (evidence, not preference)

- `references/wording.md` **R26** said "dialogue lines (H3 does not do speech on this lane)". That parenthetical is a
  brief lock stated as a model fact: the tokens for speech exist locally (`minimax.py:32`), the "no-speech on every
  arm" line comes from Derek's brief lock (`notes/2026-10-30-terrace-b2v2-changelog.md:128,131`), and speech has
  never been measured on this lane. R26 now says the default is off and points to R37/R38 for the arm.
- Upstream is **not installed** as a second skill (`npx skills add ... --skill h3-prompt-writing`): two skills stating
  the same rules would break the "each rule in exactly one skill" check of `notes/2026-10-29-forge-cleanup-plan.md` (U2).

## Wiring updated (so the new skill is actually loaded)

- `C:\AI\community\agent-shared\AGENTS.md` (hard link of `C:\Users\derek\.pi\agent\AGENTS.md`, both names proven by
  `fsutil hardlink list`) - video route now names `h3-max-ref2va-prompt` as the standing REF2VA lane.
- `C:\Users\derek\.pi\agent\skills\video-render\SKILL.md` - companion list.
- `C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\SKILL.md` - the REF2VA paste-shape path now points at
  the new skill instead of the archived lane file.
- `C:\Users\derek\5slock\ralph-community\PROMPT.md` line 1 - a Ralph pass for video/render items loads the new skill.
  (Flag for Derek: this changes what every future loop pass loads; it is the wiring his ask implies.)

## Checks run

- Rule-number integrity across `C:\AI\community\skills\*`: R1-R44 all defined, **no rule defined twice**, **zero
  citations to an undefined rule** (script in this job; the earlier "dups" were bold `**R1-R31**` ranges matching the
  definition regex, so those bold ranges were rewritten to plain text - the machine check for `**R<n> -` is now clean).
- No live file cites a moved lane file except pointers, archives, and old scan logs.
- Frontmatter `name:` matches the directory; both new files parse as markdown.
- `git status` of `C:\AI\community` reviewed before commit; no deletions, only moves + new files.

## Open for Derek

1. The speech arm (R37) is a **labelled test cell** if he ever wants it: it needs his GO and a A/B, because it has
   never been measured here.
2. `<Video N>` / `<Audio N>` in a paste require a builder change in `scripts/comm.py` (R33/R42). Not built - say the
   word and I'll stage the arm.
3. Nothing was rendered; GPU untouched.
