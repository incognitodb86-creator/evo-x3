---
title: A detailed face block plus "same face" at every beat fixes most face lock
tags: [max, face-lock]
date: 2026-10-10
---
- 2026-10-10 face-lock round (beta6 Euler, 8 steps, seed 43029049; stills verdict, second seed pending): the v2 prompts beat their controls on all three tests (pool 5s, pool 10s, two-ref).
- What the v2 prompt does: a neutral face block (shape, eyes, brows, nose, lips, skin, hairline) once in subject_definitions, a short "same face" line at every beat, a hip turn instead of a full spin, and waist-up framing for two-ref clips (faces about 3x larger).
- 1280 px references helped slightly. Swapping the ref slots hurt. Ref size max, a face-crop second reference, a last-frame guide and 12 steps tied while adding 7-44% render time, so don't use them by default.
- Results: /workspace/maxops/facelock-v2-2026-10-10/RESULTS_DRAFT.md
- Video reviewer: A2 beats control on two-ref; 1280 px refs TIE (not a slight beat). The remaining drift is the dark-haired face turning to profile at 2s, so stage two-ref clips without profile turns.
- Seed 2 (7741029) confirmed: A0, A1 and A2 beat their controls again; 1280 px refs (A3) tie on both seeds with the reviewer, so not worth +18% time. The v2 face-block prompt is now the Max default.
