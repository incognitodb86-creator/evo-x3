---
title: FLUX.2 Klein 9B defaults from the 2026-10-10 matrix
tags: [flux2, settings]
date: 2026-10-10
---
- FLUX.2 is image-only (text-to-image and reference edits); there is no video.
- Keep: FLUX-KLEIN-9B-FP8-NSFW, 4 steps, CFG 1, euler (or res_multistep) with simple/Flux2Scheduler. About 3.8 s per image at 768x1376 warm on AlienPc.
- 3 steps is softer; 6 and 8 add nothing visible. CFG above 1 doubles the time (negative pass) and only adds contrast, overcooked by 2.5. ddim/ddim_uniform breaks (duplicate figures, smeared anatomy), so never use it.
- 9B clearly beats 4B (4B is 3x faster but flatter skin and light, less faithful).
- 896x1600 to 1088x1936 is crisper with more fabric and skin detail at about 5-7 s per image, but reframes tighter.
- MS_real_and_Details_klein loads on 9B with no key errors; effect is subtle texture. Optional, strength 0.6-1.0.
- Edits: the relight works, but the pose drifts even with a "keep pose unchanged" line, which does little. Lock the pose another way (reference, or a smaller ask).
- Negative prompts do nothing at CFG 1; write positively.
- Source: /workspace/maxops/flux2-2026-10-10/ (sheets, per-cell results)
