# Long-Clip Beat Sheet & Multi-Shot Continuity Reference

Last Updated: 2026-11-06

This reference defines the structured beat sheet fields, prompt-compilation rules, and planning invariants for multi-beat and multi-clip long sequences in the H3 / 10Eros-Max pipeline.

## Core Rules & Invariants

1. **One primary beat per clip**:
   Each clip must focus on a single primary dramatic or physical beat. Avoid cramming multiple conflicting story turns into one clip window.
2. **Prefer in-clip `[Shot N]` when it fits**:
   When the planned action and duration fit within the measured single-shot ceiling (<= 243 frames / 10.125s at 24fps), use in-clip `[Shot N]` sub-shots. In-clip shot shifts preserve latent context without seam latency or continuation boundary artifacts.
3. **Don't restate finished actions**:
   Actions completed in previous clips must not be reintroduced or re-described as ongoing actions in subsequent clips. The prompt must advance the narrative state rather than repeating past motion.
4. **Native A/V continuation: bounded verification**:
   The named-parody path with 2+ explicit `--beat` scenes uses native 22-frame A/V latent-tail continuation in ONE graph, not required cuts. `runs/parody_daenerys_2beat_cont_20261106_183156` verified 192 base frames + 187 extension = 379 frames (15.79s), sampled window 209 frames. Each sampled window stays <= 243 frames; RefMod applies every beat and one optional frame-0 image guides beat 1 only. GPU runs with 3+ beats, 24-second continuous output and timed multi-image continuation remain untested; the multi-image test is paused. Longer asks without 2+ explicit beats retain shared-anchor stitched cells.
5. **Dials & Render settings**:
   Do not copy render dials (steps, shifts, CFG, VSA, denoise, sampler) into prompts or beat sheets. All render settings defer to [skills/h3-hc-render/SKILL.md](../../h3-hc-render/SKILL.md).
6. **Image rules**:
   Do not restate or define image rules in prompt skills. All image guidelines defer to `ComfyUI/LANE_IMAGE_RULES.md` in the render runtime (`C:\AI\comfy-alienpc\LANE_IMAGE_RULES.md`).

---

## Required Beat Sheet Fields (9 Fields - Spoken Dialogue & Ambient SFX Separated)

Every long-clip beat sheet entry requires these fields (keep `spoken_dialogue` strictly separate from `ambient_sfx` so stage cues never leak into `<d>[English] ... </d>`):

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **`clip/shot id`** | String | Unique identifier for the clip or shot (e.g., `clip_01`, `c01_s51083601`). |
| **`primary beat`** | String | The single core narrative or physical action occurring in this clip window. Exactly one primary beat per clip. |
| **`opening/ending state`** | String | Precise subject posture, garment state, spatial placement, and scene state at entry (frame 0) and exit (final frame). |
| **`identity/wardrobe/location/prop anchors`** | String | Verbatim `<Subject N>` / `<Picture N>` identity anchors, garment descriptions, room landmarks, and handled props (track prop continuity so hands never duplicate objects). |
| **`camera continuity vs cut`** | String | Explicit camera motion directive (`R23` vocabulary): `The camera holds a static shot.`, `Tracking, slow, small amplitude...`, `Push In, slow, small amplitude...`, or planned hard cut to new angle. |
| **`spoken_dialogue`** | String / Empty | **Literal spoken words ONLY** (plain words ending in `. ? !`, zero timestamps, zero stage cues, zero `<d>` tags). Leave empty (`NONE`) on silent clips so `(S1)` and `<d>[English] ... </d>` are omitted completely. |
| **`ambient_sfx`** | String | Plain room-tone and physical foley sentences emitted **outside** `<d>...</d>` at the end of `detailed_description:` (`R7`). Never put `"No speech"` here (negations condition TTS/audio). |
| **`frame budget`** | Integer / Time | H3 `17k+5` grid (`124` frames = `5.167s`, `243` frames = `10.125s` @ `24 fps`). Native continuation adds extensions in multiples of 17 behind a hidden 22-frame overlap; the sampled window, not cumulative output, is capped at 243 frames. |
| **`method`** | Enum | `in-clip [Shot N]`, `planned cut`, or `native A/V continuation` (two-beat named-parody path verified; longer/multi-image GPU cases untested). |

---

## Beat-Sheet-to-Prompt Compilation Contract (MANDATORY)

1. **Never pass timestamps or stage/SFX notes into `--dialogue` / `<d>[English] ... </d>`**:
   H3's speech synthesizer skips `t=` numbers and speaks non-timestamp text inside `<d>` out loud (`"No speech, bar room tone and glasses"`, `"Paper, card stock"`). Only `spoken_dialogue` enters `<d>[English] ... </d>`; when `spoken_dialogue` is empty/`NONE`, omit `(S1)` and `<d>...</d>` altogether.
2. **Compile `opening/ending state` + `primary beat` + `camera` into `detailed_description:`, NOT as raw headers in `summary:`**:
   - `summary:` must be natural `[reference generation]` prose with zero raw schema labels (`Set:`, `Wardrobe:`, `Opening:`, `Ending:`, `Anchors:`, `Method:`).
   - `[Shot 1]` (no timestamp, R8) must describe that specific clip's real posture, physical action, garment state, and camera framing - never leave a smoke-test default (`"stands facing the camera, weight even on both feet, hands resting lightly at her sides"`) on walking, seated, leaning, or undressing clips.
3. **Preserve the brief's exact wardrobe and tone**:
   When a brief specifies a provocative or scandalous consensual adult parody, carry that exact wardrobe, framing, and dialogue attitude into the beat sheet and compiled `prompt.txt` (passing `comm.guard_ok` vocabulary cleanly; never sanitize into generic filler).

---

## Method Selection Rules (Extend-First Default + Cinematic Planned Cuts)

- **`in-clip [Shot N]` (<= 243 frames / 10.125s)**:
  One continuous `[Shot 1]` is the default. Use 2–3 timed `[Shot N] At MM:SS.mmm, the camera cuts to ...` angles inside one 243f window only when `--shots multi` or coverage is requested.
- **`native A/V continuation` / `--continue` Extension (DEFAULT for > 10.1s same-scene escalation)**:
  Generally prefer **extending** over making isolated single clips and stitching whenever the scene stays in the same room, light, and continuous physical act! One native continuation graph (`GuidedContinuationWindow -> LatentTailGuide -> Sampler -> AppendContinuation`, carrying sampled video + audio latent across the hidden 22-frame airlock with RefMod on every beat, or stateful `--scene <id> --continue <prev_run_dir>` last-frame handoff) preserves body momentum, garment states, and vocal register without hard-reset seams. (Two-beat named-parody GPU path verified at 379f; 3-beat `566f` layout verified in CPU tests.)
- **`planned cut` + Stitched Movie Chapters (Intentional Film Editing)**:
  Use independent single clips + hard cuts (`take_chain_stitch.py`, 60 ms audio crossfade) deliberately when directing a multi-chapter professional movie: changing rooms/locations, time jumps, setup-banter -> bedroom transition, full undress chapter -> new sex position chapter, or distinct reverse/coverage camera setups that should read as intentional cinema edits.

---

## Worked Beat Sheet Example

```markdown
### Clip 01 (`c01_s51083601`)
- clip/shot id: c01_s51083601
- primary beat: Subject leans forward over the polished counter, sliding a chilled glass toward the lens with a slow knowing smirk.
- opening/ending state: Opening: leaning on both forearms against the dark wood bar, torso angled forward. Ending: right fingertips resting on the rim of the glass near foreground, chin tilted slightly up, eyes locked on the lens.
- identity/wardrobe/location/prop anchors: <Subject 1> resolved bio + low-cut crimson halter top, warm amber backbar practicals, single chilled coupe glass in right hand.
- camera continuity vs cut: Push In, slow, small amplitude, from medium waist-up to close chest-and-face framing.
- spoken_dialogue: Stay a second, the game is over, and I am just getting started.
- ambient_sfx: Her voice sits close and warm in the foreground. The glass slides softly across polished wood over a low room hum.
- frame budget: 124 frames @ 24 fps (5.167s).
- method: planned cut

### Clip 02 (`c02_s51083602`)
- clip/shot id: c02_s51083602
- primary beat: Planned cut to side-three-quarter angle as she eases onto the tall leather barstool and crosses one leg slowly.
- opening/ending state: Opening: standing beside the leather barstool with left hand on the seat edge. Ending: seated comfortably on the barstool, shoulders relaxed, breathing steady on the final frame.
- identity/wardrobe/location/prop anchors: <Subject 1> resolved bio + low-cut crimson halter top, dark leather barstool, amber backbar light.
- camera continuity vs cut: The camera holds a static shot.
- spoken_dialogue: NONE
- ambient_sfx: Soft leather creak as she settles onto the barstool, heel clicking lightly against the brass footrest over quiet room tone.
- frame budget: 124 frames @ 24 fps (5.167s).
- method: planned cut
```
