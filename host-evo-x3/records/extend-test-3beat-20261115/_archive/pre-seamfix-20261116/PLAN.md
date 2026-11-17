# Extend test - 3 beats, one native latent-tail graph (Prompt maker, 2026-11-15)

**One-line plan:** one continuous bent-over doggy take on GI183 + FCSydny in a single graph - beat 1 (192f base) turns her over the bed edge and enters by ~3 s at a steady one stroke a second, beat 2 (+187f) wraps her hair and goes hard at two a second, beat 3 (+187f) drops to long deep strokes with a grind as he climbs toward his peak (no finish).

- Approval: Derrick, card t283s974 (Nov 15, 7:53 PM CT) - redesign into small extend groups and test first. Nothing renders until Derrick sees these three prompts and says yes.
- Position id: `doggy` (alias "from behind"), standing bent-over-the-bed-edge variant. v2 c09-c11 doggy is on all fours on the bed; that needs a ~4.5 s climb-on (v2 c09) and would miss the enter-by-3 s spec from the GI183 standing pose, so beat 1 bends her over the low bed edge instead. Same cast, room, light and side lock (he screen left, she screen right).
- Wardrobe: GI183 state (clip 1), as Max specified, not the v2 c09 naked state. Beat 1 pulls the bikini bottom aside to her right buttock (away from the near-side camera) and slides his briefs to mid-thigh before entry (R12/W5); top, belly chain, necklace and boots stay on for the whole take. Beats 2-3 open with that state written into Shot 1.
- Frames: 192 + 187 + 187 = 566 visible frames (23.583 s). Beats 2-3 sample a 209f window each (22f hidden overlap + 187f), all windows <= 243f; `_layout_chain` picks ext 187 (17x11) for a 187 ask. Base 192 = 17x11+5.
- Refs: start still GI183 (`--image`, beat 1 frame 0 only) + FCSydny RefMod (every beat). Continuation beats carry no image (builder refuses one).
- Shot times in beats 2-3 are measured from the start of the 209f sampled window; its first 0.917 s is the hidden overlap, so every Shot 1 cut sits at >= 3.25 s (>= 2.33 s visible).
- Shot 1 of each beat opens on the framing the previous beat ended on (MCU_HER_3Q -> MCU_HER_3Q, MED_HIP -> MED_HIP), so the latent tail is not asked to jump framing at the join.
- Files: `beats_data.py` (source), `build_extend.py` (rebuild + v2 `lint()` reused unchanged + builder-gate mirrors), `beat1.txt`-`beat3.txt`, `lint_report.json`.

### Beat 1 (`beat1.txt`)
- clip/shot id: extend3_b1
- primary beat: Bent-over doggy at the bed edge: from the GI183 stand he turns her by the hair, bends her over, clears the join and enters by ~3 s; steady one-a-second thrusts.
- opening/ending state: Opening: Frame 0 = GI183: standing on the hardwood, he leans in at screen left in navy briefs, right hand on her breast, thigh between her legs; she stands at screen right in the pink sheer string bikini, belly chain, necklace, white over-the-knee boots, eyes on the lens. Ending: Bent over the low bed edge facing screen right, palms on the sheets, boots apart on the floor; he stands behind at screen left, joined, both hands on her hip bones, steady one-a-second thrusts running; framing = her face MCU (MCU_HER_3Q).
- identity/wardrobe/location/prop anchors: <Subject 1>/<Subject 2> v2 bios verbatim (S1_BIO/S2_BIO), v2 ROOM + LIGHT verbatim; pink sheer bikini top on, bikini bottom pulled aside to her right buttock, belly chain, necklace, white over-the-knee high-heel boots on; his navy boxer briefs at mid-thigh; low bed edge, grey-lavender sheets, grey headboard, charcoal wall, hardwood floor, lamp on nightstand at frame left. No handled props.
- camera continuity vs cut: Shot 1 00:00.000 FULL_STILL (static); Shot 2 00:03.250 MED_HIP (static); Shot 3 00:06.000 MCU_HER_3Q (static). One take across beats; cuts are in-window `[Shot N]` cuts only.
- spoken_dialogue: Your pussy's dripping down my balls. | Deeper. Ruin me on that cock.
- ambient_sfx: Skin claps on every stroke, the low bed creaks under her palms, and her moans catch on each impact.
- frame budget: 192 visible frames (8.000 s)
- method: native A/V continuation, base window
- end_action (for the builder's beat_closer / `--end-action`): stays bent over the low bed edge with her palms on the grey sheets while his steady strokes keep landing

### Beat 2 (`beat2.txt`)
- clip/shot id: extend3_b2
- primary beat: Same bent-over doggy, harder: he wraps her hair around his fist, hauls her up into a deep arch and speeds to two hard strokes a second.
- opening/ending state: Opening: (inherits beat 1 end, latent tail) Bent over the bed edge, joined, steady strokes running; her face MCU framing. Ending: Her back arched deep, head and shoulders pulled up by the hair wrapped in his right fist, his left hand on her hip, hard two-a-second thrusts running; framing = side medium at hip height (MED_HIP).
- identity/wardrobe/location/prop anchors: <Subject 1>/<Subject 2> v2 bios verbatim (S1_BIO/S2_BIO), v2 ROOM + LIGHT verbatim; pink sheer bikini top on, bikini bottom pulled aside to her right buttock, belly chain, necklace, white over-the-knee high-heel boots on; his navy boxer briefs at mid-thigh; low bed edge, grey-lavender sheets, grey headboard, charcoal wall, hardwood floor, lamp on nightstand at frame left. No handled props.
- camera continuity vs cut: Shot 1 00:00.000 MCU_HER_3Q (static); Shot 2 00:03.250 HIGH_REAR (static); Shot 3 00:06.250 MED_HIP (static). One take across beats; cuts are in-window `[Shot N]` cuts only.
- spoken_dialogue: Scream for it. Let the whole building hear. | Pull harder. Fuck me raw.
- ambient_sfx: Skin slaps hard on each drive, a sharp gasp breaks from her with every pull of her hair, and the grey headboard knocks the charcoal wall.
- frame budget: 187 visible frames (+7.792 s), sampled window 209f (8.708 s) incl. 22f hidden overlap
- method: native A/V continuation, extension 1
- end_action (for the builder's beat_closer / `--end-action`): stays bent over the low bed edge, arched deep with her hair in his fist while his hard thrusts keep landing

### Beat 3 (`beat3.txt`)
- clip/shot id: extend3_b3
- primary beat: Same bent-over doggy, deep and slow: he lets her hair go, takes her hips and shifts to long full-length strokes with a grind at depth, building toward his climb.
- opening/ending state: Opening: (inherits beat 2 end, latent tail) Arched deep, hair in his fist, hard thrusts running; side medium at hip height. Ending: Bent over the bed edge, his palms on her hips, long deep strokes still landing; his face MCU, jaw clenched, breath ragged, close to his peak (no finish in this beat).
- identity/wardrobe/location/prop anchors: <Subject 1>/<Subject 2> v2 bios verbatim (S1_BIO/S2_BIO), v2 ROOM + LIGHT verbatim; pink sheer bikini top on, bikini bottom pulled aside to her right buttock, belly chain, necklace, white over-the-knee high-heel boots on; his navy boxer briefs at mid-thigh; low bed edge, grey-lavender sheets, grey headboard, charcoal wall, hardwood floor, lamp on nightstand at frame left. No handled props.
- camera continuity vs cut: Shot 1 00:00.000 MED_HIP (static); Shot 2 00:03.500 INSERT_JOIN (static); Shot 3 00:05.750 MCU_HIM_3Q (static). One take across beats; cuts are in-window `[Shot N]` cuts only.
- spoken_dialogue: Stay buried. Give me every drop. | Fuck, I'm close. Squeeze that cunt.
- ambient_sfx: A wet slide sounds on each long stroke, the low bed creaks as she rocks back, and his breath grunts through his teeth.
- frame budget: 187 visible frames (+7.792 s), sampled window 209f (8.708 s) incl. 22f hidden overlap
- method: native A/V continuation, extension 2
- end_action (for the builder's beat_closer / `--end-action`): stays bent over the low bed edge, rocking back onto his long deep strokes as he nears his climax

## Builder notes for Max (read from the box copy `/workspace/u6/writer_pipeline_20261113/live/`, may be older than AlienPc)

- `build_continuation_request` (build_request.py ~4811) is present. For each beat after the first it calls `build_parody_request(continuation=True, images=None, prior_closer=beat_closer(previous beat))`, and `continuation_scene` puts a lead-in in front of the beat's scene text. Because these beats have `[Shot 2+]` cuts, it picks `CONTINUATION_LEAD_IN_DYNAMIC` ("The shot continues from the last seen moment: <prior pose/wardrobe>, and the shot never resets to a starting photo. ..."). So the beat files do not carry their own lead-in or the h3-prompting R10 `[video continuation] ... <Video 1>` line; the parody lane's builder format takes precedence there.
- That path assembles prompts with `format_parody_prompt` (parody/`--beat` CLI), not from a writer-format prompt.txt. On this box copy, the writer-run hook's only multi-beat route is the automatic 2-beat undress+act split (submit_parody_run.py ~1255). I found no route that feeds three writer-format prompt.txt files into one continuation graph. Max has to wire that path (or paste these sections) for the test.
- Beats 2-3 still define `<Picture 1>` as GI183 for identity, the way v2 continued clips do (R10/R11: a chunk with no `<Picture N>` drifts), but no image is staged on continuation beats. If the live builder rejects or strips a `<Picture 1>` that has no staged image, swap that line for RefMod-only identity wording. That needs a call from Max; it is not settled here.
- `_validate_continuation_place_transition`: beats 2-3 contain no place word (no 'bedroom'), so there is no room-change error. `beat_closer` takes the last sentence of each beat's scene unless `end_action` is passed, so pass the end_action lines above.
- The multi-shot act check reads only Shot 1. Shot 1 act words: b1 'enters her', b2 'inside her' + 'strokes', b3 'glans stays inside her' + 'strokes'.
