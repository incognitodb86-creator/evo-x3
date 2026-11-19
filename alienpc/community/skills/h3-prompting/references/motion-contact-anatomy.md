# H3 prompting - section 3 (moved verbatim from ../SKILL.md, audit 2026-10-29)

## 3. Motion, contact, anatomy

**R16 - Get-into-position when the start image is not in position for the act.** Never jump straight to
thrust/pump/bounce (that is where melt, floating join and orifice teleport come from). Write an ordered beat inside
`[Shot 1]` before the act - STAND, TURN, KNEEL, BRACE, SETTLE - in time-ordered prose per R8, then the act, in one continuous
shot. Soften "preserve camera angle / framing" when the pose must change, and keep face/identity, wardrobe, light
`fully_preserved`. If the transition is too long for one clip, unlock the still first
(`alienpc-stills-pose-edit-prompting`), then paste. If the still already shows a fused wrist, an extra finger, or a floating join, unlock or fix the still before writing the act. **Open state:** a cell whose only reference is `<Picture 1>` is
independent of the cell before it - do not write "opens mid-[previous beat]" unless that pose is in the still, or
you pass Multiframe / the previous clip's last frame, or the clip is a R10 continuation. Default: the first ~2
seconds establish from `<Picture 1>` into the beat, then the timed phases; get off a standing pose fast when the
beat needs pin or penetration.

**R17 - Name ONE PRIMARY MOTION with tempo and amplitude**, e.g. `PRIMARY MOTION - continuous deep frontal thrust,
about one full cycle every half second, full depth travel, hips staying in contact`, and keep that tempo for the
timed phases. Contact beats dominate the clock time; compress approach theatre. Keep the motion alive on the final
frame - end mid-energy, never a freeze tableau. Any camera move follows R23 (one move per shot). A pose-to-pose clip may end on a written settle: the move comes to rest while breath, hair and fabric keep a little life.

**R18 - Body inventory is explicit:** exactly one adult man and one adult woman (or the number the still shows), two
arms and two legs each, five fingers when hands are visible (palm-heel and thumb-hook landmarks, and naming a hand by its frame edge once left and right are ambiguous), one continuous torso each, breast size and body mass
locked to `<Picture 1>`. Use literal anatomical words (penis, shaft, glans, vagina, vulva, breasts, buttocks, hips,
thighs, groin, pelvis), not euphemism. Action does not change body mass. A flex, lift or hard thrust keeps the same
shoulder, arm, breast and thigh size as `<Picture 1>`; write the effort as tension and breath, not new muscle.

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
mechanics: full palm to cheek and jaw, head snaps sideways toward near-profile, hair whips, mouth opens on a punched
breath, cheek flushes red and the flush stays. The face stays readable and `fully_preserved`: features, jaw line,
eyes, brows, fringe unchanged, head returns square to the lens, the struck cheek stays smooth and unbroken, her eyes
stay clear and dry, her face stays unwounded. One
slap unless he asks for more. *(Derek 2026-10-28.)*

**R23 - Camera line is one sentence, in natural English inside `[Shot 1]`:** `The camera holds a static shot.` -
locked-off tripod, fixed framing, fixed focal length (MiniMax VIDEO_PROMPT_WRITING_GUIDE section 4.3). "Static
documentary framing" / "documentary porn framing" is not that vocab and still pushes in. No `[Static shot]` token
syntax. A static hold cannot also reveal a person who starts outside the crop - do not write "reveal"; the trained
way to fit a new full body is a zoom out, and in a static shot the entering person is cut by the existing frame
edge. Zoom changes the focal length while the camera body stays still; push-in and pull-out (dolly) physically move the camera. The official verb list, used with amplitude and speed in one natural sentence: push in / pull out, zoom in/out, truck, pan, tilt, pedestal, arc or track beside, roll. One move per shot remains (cite R17 for the single PRIMARY MOTION). Arc is a normal official camera verb, subject to that one-move-per-shot tip.

For sex and other close physical action, that one sentence also names scale, height, angle, lens, and what must stay in frame. Use real film shot names (cowboy shot, medium shot, medium long shot) instead of describing a homemade crop. Wides blur faces; use waist-up to mid framing that keeps the contact and a readable face in view. Per-position starting points (general guidance, not tested): missionary low between the knees or a close two-shot; doggy and reverse cowgirl low rear three-quarter or hip-height side that keeps the join and her face readable; cowgirl slightly high three-quarter or a tight mid-shot down the torso; oral a close two-shot or low; `POV` only when the brief asks for it. A 10-15 s sex beat stays one continuous `[Shot 1]` hold; cut only when the new shot adds information the current framing cannot show (a close-up of the join, a face close-up, a POV). Do not cut to a slightly tighter shot of the same angle; if you need tighter, write a slow push in with small amplitude (official H3 guide sections 4.2-4.3). Default is a locked static shot; write `Shake Slightly` or a small handheld sway only when the brief asks. Instead of a locked static hold, one motivated move: slow push-in, tilt, pedestal, or arc, with type, amplitude, speed. Do not stack several moves in one shot. Do not default every clip to a medium-wide, deep depth-of-field, head-to-knees profile. Name the light with the camera line (R8): describe light as it falls and reflects inside the frame. Name an emitter such as a lamp, neon sign or window only when it's visible. Never write "behind the camera". Name the light's direction, quality (soft or hard), colour temperature, and how it falls on skin and fabric (name the emitter only if it is in frame) - specular on oiled or wet skin, light through sheer cloth, a faint subsurface glow through thin skin (ears, fingers, pressed flesh). The environment answers the body (light bounce off stone or linen, a breeze on a hem that falls back with weight).



**R23a - Weight, gravity and contact for every pose change (Max Architect 3, Derek yes 2026-11-09).** When a beat
changes the pose, write the body mechanics in plain words, in order: where the weight sits first (which foot, knee
or hand carries it), the shift (weight moves onto the left leg, hips follow, torso turns about a quarter turn), the
named contact points and surfaces (hand on the wall, knee on the mattress, foot planted), and a stable ending
position. Name gravity or drag on loose parts so they settle instead of floating: fabric falls with natural weight
and drag, hair follows the turn a beat late, then settles. Use speed words H3 reads (unhurried, weighted, sudden).
Use plain direction words for angles (three-quarter turn, near-profile, head tilts slightly down), not degree
numbers. Feet and hands stay connected to the surfaces they touch unless the beat lifts them. Source: MiniMax
prompt guide, Siray and Max H3 motion guides (checked 2026-11-09); numeric angles are not used by any source found.

**R23b - Load, pressure, follow-through, and angles (held poses included).**
R23a already covers weight shift, named contacts, and gravity on fabric/hair
when a pose changes. Also do this:

- Held poses count. Even when she is standing or sitting still, name the
  load-bearing limb and keep the torso stacked over it in plain words
  (`weight rests on her left foot, right knee soft, torso stacked over that
  foot`). Held/standing poses: uneven weight, a soft free knee, a slightly cocked hip, a slight lower-back arch, soft shoulders, and fabric tension from that stance. Do not use jargon like "center of gravity" or "inertia."
- Body angles in plain directions, not degrees. Name hip direction, shoulder
  direction, and head tilt separately when they differ (`hips face the window,
  shoulders open a little toward camera, head tilts slightly down`). A
  three-quarter or near-profile turn is enough; no degree numbers (R23a).
  Keep this distinct from the camera's height.
- Pressure is visible. Where a limb meets a soft or loose surface, say how
  that surface answers (`the mattress sinks under her knee`, `the rug
  compresses under the planted foot`, `the blouse bunches where her palm
  presses`).
- Bracing shows: a hand braced on a surface, weight shifting into that support.
- Hands: see R18.
- Secondary lag: hair, fabric and soft tissue answer a beat later, then settle.
- Gaze has a target and blinks stay natural - a living face, not a dead unblinking stare.
- Follow-through, then settle. After a turn, step, or stop, trailing parts
  continue a beat and then come to rest (`the jacket swings after the turn,
  then hangs`). Official H3 wording: pieces "lose momentum and settle." Do
  not freeze hair, fabric, and limbs at the same instant.
- Camera height lives in the R23 sentence, not in the body-angle line. Add
  one height cue when it matters (`chest-level`, `hip height`, `looking
  slightly down`). A static hold is one locked framing sentence (scale, height, lens, who is in frame), with no zero-amplitude or no-zoom stack. If the camera moves, write one move (type + amplitude + speed).

Write only what changes the picture. Do not pad with force-physics vocabulary,
and do not add negative "no sliding / no floating" stacks (R24, R25). (Untested tips for fluid appearance, grip pale-knuckles, and strap pressure: see wording.md R25).
