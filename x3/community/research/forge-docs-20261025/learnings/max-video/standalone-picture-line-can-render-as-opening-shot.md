---
title: A standalone <Picture N> line can render that reference as the clip's opening shot
tags: [max]
date: 2026-10-09
source: 60_reviews/max-clips/2026-10-09-full-day-audit.md
---
- TWOREF_B opened on a 0.29 s near-still of the Picture 2 head-and-shoulders portrait (dusk, palms), then hard-cut to the forest at 0.33 s. The frame diff was 65 vs ~1 before and ~9 after.
- The prompt had a standalone `<Picture 2>:` line describing the ref's own crop and light. That matches the official reading of a standalone Picture as a frame/composition anchor (research 2026-10-09-h3-face-lock-prompting.md, 3a).
- For identity-only refs, cite the picture inside its `<Subject N>` and don't describe the ref's crop or light. Check the first 0.5 s of every multi-ref clip for a cut.
