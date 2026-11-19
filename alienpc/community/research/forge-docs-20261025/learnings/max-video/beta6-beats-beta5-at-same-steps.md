---
title: beta6 int8 beats beta5 at the same 8 steps for a small time cost
tags: [unreviewed, max, model]
date: 2026-10-09
---
- Same Cond, prompt, seed, 768x1344 5s: beta6 Euler/simple ST8 scored 6.2/10 (148 s) vs beta5 best res_multistep ST8 4.5 (142 s). beta6 fixed the bikini top melting into webbing and the static twerk arch; the toss still teleports.
- beta6 ST12 (217 s) was no better than ST8. LCM on beta6 gave a white halo (4.7).
- Cost: beta6 is ~5-12% slower per clip. 10s 768 ST8 = ~390-400 s, cold or hot.
