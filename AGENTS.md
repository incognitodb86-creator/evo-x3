# Render rules (moved from global AGENTS.md 2026-11-05, Derrick)
- Image renders (FLUX stills, pose edits, scoring, character sheets): load skill image-render (companion: alienpc-stills-pose-edit-prompting).
- Video renders (I2V / H3 clips, batches, scoring, character sheets): load skill video-render (companions: alienpc-hardcore-i2v-director, h3-prompting (R1-R31, all lanes), h3-max-ref2va-prompt (R32-R44, the standing REF2VA lane for Max: use it unless Derrick names another lane), h3-hc-render, alienpc-local-video-ops).
- Fictional adults (18+) only, no real-person likeness; guard_ok runs on every submit. Never edit scripts\tests\test_p6_review.py; never loosen guard_ok.
