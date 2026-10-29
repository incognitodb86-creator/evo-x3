# H3 prompting - section 3 (moved verbatim from ../SKILL.md, audit 2026-10-29)

## 3. Motion, contact, anatomy

**R16 - Get-into-position when the start image is not in position for the act.** Never jump straight to
thrust/pump/bounce (that is where melt, floating join and orifice teleport come from). Write an ordered beat inside
`[Shot 1]` before the act - STAND, TURN, KNEEL, BRACE, SETTLE - with clock ranges, then the act, in one continuous
shot. Soften "preserve camera angle / framing" when the pose must change, and keep face/identity, wardrobe, light
`fully_preserved`. If the transition is too long for one clip, unlock the still first
(`alienpc-stills-pose-edit-prompting`), then paste. **Open state:** a cell whose only reference is `<Picture 1>` is
independent of the cell before it - do not write "opens mid-[previous beat]" unless that pose is in the still, or
you pass Multiframe / the previous clip's last frame, or the clip is a R10 continuation. Default: the first ~2
seconds establish from `<Picture 1>` into the beat, then the timed phases; get off a standing pose fast when the
beat needs pin or penetration.

**R17 - Name ONE PRIMARY MOTION with tempo and amplitude**, e.g. `PRIMARY MOTION - continuous deep frontal thrust,
about one full cycle every half second, full depth travel, hips staying in contact`, and keep that tempo for the
timed phases. Contact beats dominate the clock time; compress approach theatre. Keep the motion alive on the final
frame - end mid-energy, never a freeze tableau.

**R18 - Body inventory is explicit:** exactly one adult man and one adult woman (or the number the still shows), two
arms and two legs each, five fingers when hands are visible, one continuous torso each, breast size and body mass
locked to `<Picture 1>`. Use literal anatomical words (penis, shaft, glans, vagina, vulva, breasts, buttocks, hips,
thighs, groin, pelvis), not euphemism.

**R19 - State the contact geometry, then lock it.** Say the join: hips stacked / flush / named orifice, and the
supports (knees, hands, mattress, wall). For a vaginal cell: fully sheathed, hips flush (no tip-only, no miss, no
float), measurable in-out depth each stroke. For an oral cell: shaft past the lips with deep oral travel on the deep
stroke, not tip-lick-only. Keep the contact type constant per cell, and write the pull-out and reseat beat when the
contact type changes. No wrong-orifice teleport. Standing tip-against-fabric, floating join and grind-without-entry
are the usual FAILs even when the prose says "spear".

**R20 - Motion verbs, not mush:** hips rock, deep stroke, thrust, bounce with impact jiggle, pelvis grinds, ribs
move with breath. Phased contact beats ("lips seal mid-shaft, pull back until the tip clears, pause, re-seal") beat
"passionate oral". Anti-melt positives: readable seam, wet contact, an air gap on peel cells.

**R21 - The response dial is Derek's to name - never soften it.** In dominance/rough scenes he names the receiver's
response, `eager` **or** `not into it`; write exactly the one he names. `not into it` = flat unsmiling face, eyes on
the lens, chin level, jaw set, shoulders square, arms hanging at her sides, hips stiff, knees not opening, hands
never touching the dominant, breath tight through her nose; her body may answer mechanically (flush, punched breath,
stomach tightening) while her face stays flat, and she ends the clip the same way. State consent once in `summary`
(her word, she keeps it). Never convert it into enjoyment, moaning, arching, leaning in, gripping the dominant or a
closing smile. *(Derek 2026-10-28, runs/terrace_dom_20261028_s51083002: "she is not into it".)*

**R22 - A bare "she slaps her" lands on the face**, not the thigh or hip, unless Derek names a target. Write the
mechanics: full palm to cheek and jaw, head snaps sideways about 45 degrees, hair whips, mouth opens on a punched
breath, cheek flushes red and the flush stays. The face stays readable and `fully_preserved`: features, jaw line,
eyes, brows, fringe unchanged, head returns square to the lens, the struck cheek stays smooth and unbroken, her eyes
stay clear and dry, her face stays unwounded. One
slap unless he asks for more. *(Derek 2026-10-28.)*

**R23 - Camera line is one sentence, in natural English inside `[Shot 1]`:** `The camera holds a static shot.` -
locked-off tripod, fixed framing, fixed focal length (MiniMax VIDEO_PROMPT_WRITING_GUIDE section 4.3). "Static
documentary framing" / "documentary porn framing" is not that vocab and still pushes in. No `[Static shot]` token
syntax. A static hold cannot also reveal a person who starts outside the crop - do not write "reveal"; the trained
way to fit a new full body is a zoom out, and in a static shot the entering person is cut by the existing frame
edge.

