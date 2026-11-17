# H3 prompting - section 4 (moved verbatim from ../SKILL.md, audit 2026-10-29)

## 4. Wording

**R24 - Positives only.** Describe what is seen and heard. No `no X / never X / without X / not / none` stacks in
the prompt body, and a ban list is never the plan: the stock graph has no CFG/negative path (BasicGuider cfg 1),
`H3ContinuumSamplerV39` has no negative key at all, so naming "no X" can add X. Locks are retention markers, not
negatives. (A negative prompt needs `CFGGuider` + `NAGuidance`, about 2x per step - a separate, labelled arm.)

**R25 - Plain concrete wording, no quality buzzwords and no style mash.** Write visible, mechanical, audible detail
in time order; that is what "more descriptive" means. English prose, not JSON, not a POS template, not a thesaurus
of adjectives; skin is matte with visible pores and fine vellus hair and only a soft natural sheen where damp, or realistic oiled skin with visible pores (a thin oil sheen that still shows pore texture and fine detail), never
waxy, plastic, airbrushed, glossy or glistening; realistic proportions with joint definition, real adult body
mass with weight on waist, hips, thighs and breasts, natural elbow and knee hinging, fluid physically plausible
motion; shallow depth of field and the lighting the still shows. No hedge words ("may brace" becomes the action).

Untested wording tips (not locked craft):
- When fluids are in shot, describe how they look and move (thickness, pooling, a trickle) rather than just naming them.
- On a hard grip, the knuckles go pale and the color comes back after.
- When a strap or waistband stays on, say how it presses into the skin.

**R26 - Sound-word vocabulary.** Use only the real-sound nouns R7 names, each one bound to the action producing it.
This rule is vocabulary only - the shape and placement of audio is R7 and is not repeated here. Never in the paste:
score and foley terminology, onomatopoeia words, or labeled `overall_soundscape:` / `non_diegetic_music:` headers (spoken dialogue uses `<d>[English] ...</d>` per R7 and `/home/evo/AI/community/skills/h3-max-ref2va-prompt/SKILL.md` R37, and visible on-screen text is R38 there).

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
clip, no hedged alternatives. One primary action per short window; when a scene splits into undress plus act, Beat 1 sizes the undress (124f floor for one standing garment; up to 243f for two or more garments or a lying-down removal) using "pull down" or "slides down" so discarded garments land on a named surface in the still and stay in view, and Beat 2 opens already bare (R12). In a chain, subject definitions are identical on every cell, the same Cond still is
used unless Derek supplies new refs, seeds are unique per cell, and the summary says cell N of M and what that cell
must not do.

**R29a - Long-run sex pacing (all adult 18+ OC, INDEX parody, and RefMod lanes).** One position and one PRIMARY MOTION per window. Across native joins, open from the prior end state: same join, same wardrobe, same camera hold, tempo unchanged unless this beat writes a pull-out and reseat (R19). A position change gets its own get-into-position phase (R16); do not jump from one act to another in one window. A ~60s ask is 3–4 position chapters, not 8 different acts. Camera: one hold that keeps both the join and the face readable; height stays in the R23 sentence.

**R30 - Write to a file, then gate.** Before queueing: re-check every section above, the R10 line on continued
clips, the response dial Derek named (R21), the absence list (R27), the adults-only tests, and
**diff against the baseline cell - only the one axis of this cell may change** (one-variable A/B). Keep section
names and line counts identical to the baseline being compared, so a side-by-side changes references and wording,
never structure.

**R31 - LoRA trigger words only when that LoRA is loaded**, at weight 0.2-0.6 in the paste, and never a general
NSFW LoRA (Mystic and friends) on beta 7. A trigger for a LoRA that is not in the graph is a defect, not a hint.

## Worked example: OC doggy clip, built prompt (writer output after the builder, 2026-11-11)

(This example is an OC in ref still mode, so `<Picture 1>` and `<Audio 1>` are correct. The default guide still mode drops `<Picture 1>`, and named INDEX/celebrity parodies never use `<Audio 1>`.)

One full built prompt for an OC RefMod clip that opens on `<Picture 1>` (G arm, doggy, writer-test v3 build), staying on the still's actual surface (C3: never invent a bed when the still has none) and sliding the panties aside so the clip stays one primary action in one 243f window. Copy the shape, not the words: one camera sentence with one move and one end framing, the opener from the still, one wardrobe line, one move into position, one PRIMARY MOTION with a tempo, the contact line, spoken lines in the OC form `(S1) says in a ... voice, <d>[English] ...</d>`, and closing sound cues. Write a new line for each beat; do not reuse these dirty-talk lines.

```text
subject_definitions:
<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>, and the living room, its light and the opening framing: a living room with a woven rug and a wood floor in soft window light, with <Subject 1> standing barefoot on the woven rug, facing the camera.
<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; an adult woman, twenty-two years of age, with natural adult body mass carried in the waist, hips, thighs and breasts, fair sun-touched skin with visible pores and fine vellus hair, a dry matte finish with only a soft natural sheen where skin is damp, and long blonde hair; she is (S1), and <Audio 1> defines her voice timbre.
<Subject 2> is an adult man, twenty-six years of age, of solid adult build with working forearms and adult weight, the same man for the whole clip; he is (S2).
HAND ANATOMY HARD-LOCKED - exactly five separate fingers, readable knuckles, no melt, merge or extra digit

summary:
[reference generation] <Subject 1> gets on her hands and knees on the woven rug, slides her sheer panties aside, and takes <Subject 2> from behind in the doggy position while they talk dirty to each other.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hairstyle, body, skin and figure are kept from <Picture 1> in every phase
<Subject 2> (appears in [Shot 1]): fully_preserved - his face, build and skin stay the same man throughout
<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - the living room, the woven rug, the wood floor, the room light and the opening framing
<Audio 1> (voice of (S1)): attribute_transfer - her spoken lines take their voice timbre from <Audio 1>
The sheer nude bra, garter belt, sheer panties, thigh-high stockings and choker of <Picture 1>: fully_preserved - they stay on her body as the photograph shows, with the sheer panties pulled aside at her hip

detailed_description:
[Shot 1] The camera pushes in with small amplitude at slow speed, tightening from waist-up to a two-shot down the torso that keeps the join and her face readable throughout, keeping his face in frame. The curtains, rug edges, and wood floor sit at the frame margins. Soft warm daylight from the left window falls across her back and hair. At first, <Subject 1> stands facing the camera on the woven rug in a sheer nude bra, a garter belt, sheer panties, thigh-high stockings and a choker, hands at her sides, weight resting on her left foot, right knee soft, torso stacked over that foot, shoulders slightly cocked. Her sheer nude bra, garter belt, sheer panties, thigh-high stockings and choker stay on her body; <Subject 2> pulls down his trousers, and they drop to the wood floor beside the woven rug and stay there. She turns to her left, weight rolling onto her left foot, right knee soft, hips following the turn a quarter, shoulders opening a little toward the woven rug; the blonde hair swings around the turn a beat, settles on her shoulder. She steps forward, kneels on the woven rug: left knee sinks into the pile, right knee plants beside it, palms press flat on the woven rug, fingers spread wide, readable knuckles, five separate fingers, and she slides the gusset of her sheer panties aside. Her face, shoulders, and hips stay in view; skin shows natural pores, fine vellus hair, natural moisture on the lids, a few flyaway hairs catching the light. She settles onto hands and knees, hips high, lower back arched, knees spread on the woven rug which compresses under her weight, palms braced on the rug which bunches where her palms press. <Subject 2> steps up behind her, grips her hips with both hands, knuckles going pale, and seats fully: penis fully sheathed in her vagina, hips flush against her buttocks, one continuous stroke. PRIMARY MOTION - continuous deep doggy thrust, about one full cycle every half second, full-depth travel, his hips staying in contact with her buttocks, her lower back flexing with each stroke. (S1) says in a low, warm adult woman's voice with a slightly husky edge, tight and breathy with the effort, <d>[English] Split this cunt open, daddy, all the way in.</d> The thrusts deepen; her abdomen compresses with each impact, breasts shift inside the sheer bra with the bounce, blonde hair sways and sticks to the damp skin at her temples, falls free a beat later, settles. The woven rug compresses deeper under her knees, fibers creasing under her palms. (S1) says in a low, warm adult woman's voice with a slightly husky edge, tight and breathy with the effort, <d>[English] Your cock is wrecking me, keep using me.</d> He grips her hips tighter, knuckles blanching, drives full depth; her jaw tightens, mouth opens on a punched breath, eyes squeeze shut, reopen with a clear wet glint, blinks natural. Her pelvis rocks to meet each thrust, thighs spread wider on the woven rug which compresses under her weight, blonde hair stringing across her cheek, a few flyaway hairs moving a beat late and settling. By the end, his hips drive the last deep stroke into her, her fingers curl into the woven rug, knuckles blanching, back arched, breath ragged, eyes wet and open - his hips at full depth, energy alive, motion continuing as the clip cuts. The wood floor creaks under her knees, skin-on-skin impact with each thrust, wet friction, her ragged breath through her nose, his low grunt, the woven rug rustling under her palms.
```
