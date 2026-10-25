---
title: Max render time tracks steps and frames, not sampler or shift
tags: [max, speed]
date: 2026-10-09
---
- Hot 768x1344 5s (124f), dynamic VRAM on: ~74 s @4, ~104 s @6, ~135-160 s @8 across res_multistep, er_sde, LCM, Euler and shift 10 vs 12.
- 10s (243f) is ~2.6x a 5s clip. Cold start costs only ~8 s with dynamic VRAM.
- Remacri 4x costs ~3x render time; RIFE 2x looked worse than native frames on Derrick's review.
