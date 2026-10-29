# H3 prompting - section 4 (moved verbatim from ../SKILL.md, audit 2026-10-29)

## 4. Wording

**R24 - Positives only.** Describe what is seen and heard. No `no X / never X / without X / not / none` stacks in
the prompt body, and a ban list is never the plan: the stock graph has no CFG/negative path (BasicGuider cfg 1),
`H3ContinuumSamplerV39` has no negative key at all, so naming "no X" can add X. Locks are retention markers, not
negatives. (A negative prompt needs `CFGGuider` + `NAGuidance`, about 2x per step - a separate, labelled arm.)

**R25 - Plain concrete wording, no quality buzzwords and no style mash.** Write visible, mechanical, audible detail
in time order; that is what "more descriptive" means. English prose, not JSON, not a POS template, not a thesaurus
of adjectives; skin is matte with visible pores and fine vellus hair and only a soft natural sheen where damp, never
waxy, plastic, airbrushed, oiled, glossy or glistening; realistic proportions with joint definition, real adult body
mass with weight on waist, hips, thighs and breasts, natural elbow and knee hinging, fluid physically plausible
motion; shallow depth of field and the lighting the still shows. No hedge words ("may brace" becomes the action).

**R26 - Sound-word vocabulary.** Use only the real-sound nouns R7 names, each one bound to the action producing it.
This rule is vocabulary only - the shape and placement of audio is R7 and is not repeated here. Never in the paste:
score and foley terminology, onomatopoeia words, dialogue lines (H3 does not do speech on this lane).

**R27 - Contradiction phrases must be absent** (they cancelled the body reference in measurement):
`body proportions` inside crop sentences, `are new and are not taken from`,
`used for the faces and the hair of the two women only`, `These two crops are the only visual references`,
`carries no reference pictures at all`. Assert them absent in the builder gate, and prove the gate fires by
restoring the old wording in a clone (self-destruct probe).

**R28 - Labels keep one meaning** in every section; tags are 1-based by connection order; each subject, garment and
place is described in full once (in `subject_definitions` and at first appearance) and referred to by label after
that. Never describe who someone looks like. Never invent wardrobe, a location or a partner that is not in the
reference - the still Derek attached or named wins.

**R29 - One pose, one finish, one wardrobe path per cell**: no `or` / pick-one forks, no multi-act montage in one
clip, no hedged alternatives. In a chain, subject definitions are identical on every cell, the same Cond still is
used unless Derek supplies new refs, seeds are unique per cell, and the summary says cell N of M and what that cell
must not do.

**R30 - Write to a file, then gate.** Before queueing: re-check every section above, the R10 line on continued
clips, the response dial Derek named (R21), the absence list (R27), the adults-only tests, and
**diff against the baseline cell - only the one axis of this cell may change** (one-variable A/B). Keep section
names and line counts identical to the baseline being compared, so a side-by-side changes references and wording,
never structure.

**R31 - LoRA trigger words only when that LoRA is loaded**, at weight 0.2-0.6 in the paste, and never a general
NSFW LoRA (Mystic and friends) on beta 7. A trigger for a LoRA that is not in the graph is a defect, not a hint.

