# Strict still/panel review (Max) — THE one rubric (stills-skill six checks: Identity=5/8, Face=8, Hands+Contact=1, Wardrobe=3, Overall quality=9; plus strict 2,4,6,7). Used by Max and EVERY judge; judge prompts load this file, not their own copies.
Judge input: IMAGE 1 = identity reference only; IMAGE 2 = candidate (see stills skill "Judge harness").
Fictional adults only. Judge craft, not content. Reject on ANY fail; never "good enough".

Check each image at full size:
1. Anatomy: genitals physically placed right; for sex, penetration actually visible, penis attached to the man and entering her; nothing protruding through/in front of her body; no extra/fused limbs or hands, correct finger count.
2. Pose matches the beat exactly (e.g. "from behind" = he is directly behind her, hips to buttocks, not beside her).
3. Clothing state matches the beat (top off means bare breasts; nude means nude).
4. Framing: full-length when asked; not cropped to medium shots.
5. Continuity: same face, hair, jewelry, boots as the reference.
6. No text, numbers, labels or watermarks.
7. Video-start fit: pose must match where the clip begins.

8. Face identity: same face as IMAGE 1 at full size (eyes, nose, jaw, ears). FAIL if drift is visible at full size, or the face metric is above the acceptable band for this pose class.
   Face metric (ranks candidates, never clears one alone): ArcFace FaceEmbedDistance on HER face only (woman's head crop or best-matching detected face); full-image scores on two-person images are invalid. Bands (cosine distance): ≤0.35 strong, ≤0.55 acceptable, >0.55 FAIL c8. **Production gate stays ≤0.35** until Derrick reviews the 0.55 test arm (2026-10-17 2:57 AM CT). Calibrate bands on known-same pairs from this setup; profile / small faces score lower (separate band pending calibration).
9. Overall quality: sharp, no smearing, artifacts, plastic skin or melted detail; anything you wouldn't show Derrick = FAIL.
Output per image: FAIL per broken check with a one-line reason (plus a suggested prompt fix), or "no breaks found in checks 1–9". Never write PASS or KEEP (skill rule). KEEP = Derrick only.
Review at full size, one image at a time. A contact sheet is for layout only, never for review.
Known failure: Klein "from behind" often puts the penis forward between her thighs — fix with side-profile camera + "groin pressed to her buttocks, shaft entering her from behind, nothing in front of her body".
