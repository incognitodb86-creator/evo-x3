---
title: In a one-axis comparison, a missing shared piece stops the run instead of being rebuilt quietly
tags: [unreviewed, max, harness]
date: 2026-10-09
source: 60_reviews/2026-10-09-max-60s-continuity-plan-review.md
---
- C3 reuses C1's first section so the two chains differ only in reference mode. If that section had failed, C3 would have quietly re-rendered it and broken the comparison (review R8).
- Rule: when a reuse or shared input is unusable, log REUSE_FAIL, exit with its own return code, and skip the dependent chain.
- Say which comparisons are truly one-axis and which are only directional (5s vs 10s changes prompt, length and seam count, R12). With one seed per arm, label the result "n=1, directional".
- Score A vs B as win, lose or tie per seam on unlabeled X/Y sheets before giving any number (R7, pack scores-in-words).
