# Long-Clip Beat Sheet & Multi-Shot Continuity Reference

Last Updated: 2026-11-05

This reference defines the structured beat sheet fields and planning invariants for multi-beat and multi-clip long sequences in the H3 / 10Eros-Max pipeline.

## Core Rules & Invariants

1. **One primary beat per clip**:
   Each clip must focus on a single primary dramatic or physical beat. Avoid cramming multiple conflicting story turns into one clip window.
2. **Prefer in-clip `[Shot N]` when it fits**:
   When the planned action and duration fit within the single-clip frame ceiling (<= 124 frames / ~5-8s), use in-clip `[Shot N]` sub-shots. In-clip shot shifts preserve latent context without seam latency or continuation boundary artifacts.
3. **Don't restate finished actions**:
   Actions completed in previous clips must not be reintroduced or re-described as ongoing actions in subsequent clips. The prompt must advance the narrative state rather than repeating past motion.
4. **C2V runtime is UNPROVEN**:
   Native A/V carry across C2V continuation boundaries is **UNPROVEN** on this box. Pipelines must report C2V continuation as unavailable and never claim native audio/video carry until proven by hardware validation.
5. **Dials & Render settings**:
   Do not copy render dials (steps, shifts, CFG, VSA, denoise, sampler) into prompts or beat sheets. All render settings defer to [skills/h3-hc-render/SKILL.md](../../h3-hc-render/SKILL.md).
6. **Image rules**:
   Do not restate or define image rules in prompt skills. All image guidelines defer to `ComfyUI/LANE_IMAGE_RULES.md` in the render runtime (`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\LANE_IMAGE_RULES.md`).

---

## Required Beat Sheet Fields

Every long-clip beat sheet entry requires the following 8 fields:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **`clip/shot id`** | String | Unique identifier for the clip or shot (e.g., `clip_01`, `c01_s1001`, `[Shot 1]`). |
| **`primary beat`** | String | The single core narrative or physical action occurring in this clip window. Exactly one primary beat per clip. |
| **`opening/ending state`** | String | Precise subject posture, garment state, spatial placement, and scene state at entry (frame 0) and exit (final frame). |
| **`identity/wardrobe/location/prop anchors`** | String | Verbatim `<Subject N>` / `<Picture N>` identity anchors, garment descriptions, room landmarks, and handled props. |
| **`camera continuity vs cut`** | String | Explicit camera motion directive: continuous camera tracking/panning/holding vs. planned hard cut to new angle. |
| **`dialogue boundaries`** | String | Timed speech cues, verbal lines, or explicit silence boundaries with start and stop timestamps (e.g. `00:01.000 - 00:03.500`). |
| **`frame budget`** | Integer / Time | Total requested frame allocation and duration at target fps (e.g., `124 frames @ 24fps = 5.167s`). |
| **`method`** | Enum | Execution method: `in-clip [Shot N]`, `planned cut`, or `C2V` (note: C2V runtime marked UNPROVEN). |

---

## Method Selection Rules

- **`in-clip [Shot N]` (Preferred)**:
  Used when beats, angle changes, or micro-actions fit within a single generation window (<= 124 frames). Employs timed `[Shot 1]`, `[Shot 2]` headers without seam re-encoding.
- **`planned cut`**:
  Used when transitioning between distinct scene locations, camera setups, or beats exceeding single-clip limits. Generates independent cells stitched via hard video cuts with audio crossfades.
- **`C2V` (UNPROVEN)**:
  Continuation chaining using 22-frame overlap conditioning (`contextLengthFrames=22`). Marked **UNPROVEN** on this box due to unverified native A/V carry. Use planned cuts or in-clip shots unless explicitly authorized for C2V experimentation.

---

## Worked Beat Sheet Example

```markdown
### Clip 01 (`c01_s1001`)
- clip/shot id: clip_01
- primary beat: Character stands from desk, walks across room to window.
- opening/ending state: Opening: seated at oak desk, hands on blotter. Ending: standing at window sill looking outward.
- identity/wardrobe/location/prop anchors: <Picture 1> identity anchor, tailored navy blazer, office interior, brass lamp.
- camera continuity vs cut: Continuous medium tracking shot following character movement to window.
- dialogue boundaries: "I knew you would call." (00:00.500 - 00:02.200); ambient room silence (00:02.200 - 00:05.167).
- frame budget: 124 frames @ 24 fps (5.167s).
- method: in-clip [Shot N]

### Clip 02 (`c02_s1002`)
- clip/shot id: clip_02
- primary beat: Character turns from window to face the doorway.
- opening/ending state: Opening: standing at window sill looking outward. Ending: facing camera with alert expression.
- identity/wardrobe/location/prop anchors: <Picture 1> identity anchor, tailored navy blazer, window frame, door in background.
- camera continuity vs cut: Planned cut to reverse wide angle from doorway looking toward window.
- dialogue boundaries: Silence; sharp footfall turn on floor (00:00.800).
- frame budget: 124 frames @ 24 fps (5.167s).
- method: planned cut
```
