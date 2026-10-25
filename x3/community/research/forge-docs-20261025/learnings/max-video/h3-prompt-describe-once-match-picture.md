---
title: H3 REF2VA prompts describe the subject once and match the picture
tags: [unreviewed, max, prompting]
date: 2026-10-09
---
- Six official sections; ~350-500 words in detailed_description; describe appearance once in subject_definitions and once at first appearance, then reuse the label (V3 repeated "ice-blue" 7x).
- No negative prompt, no (word:1.3) weights, no chat template in the H3 TE.
- Face hold comes more from steps, ref_image_size=max and not-frame-filling faces than from words.
- Background change: prompt-only can work; editing the still first is more reliable (/workspace/cos/research/2026-10-09-background-swap-prompting.md).
