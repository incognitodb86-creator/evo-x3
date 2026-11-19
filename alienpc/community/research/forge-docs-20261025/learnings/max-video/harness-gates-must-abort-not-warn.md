---
title: Every AlienPc harness check must stop the run, never just log a warning
tags: [max, harness]
date: 2026-10-09
source: 60_reviews/2026-10-09-max-60s-continuity-plan-review.md
---
- The 60s plan only logged the launch settings (ck-attention, dynamic VRAM on, async offload and pinned memory off). If a restore had failed, all 34 renders would have silently run on the wrong settings (review R2).
- Rule: any setting the fair test depends on gets an orchestrator check that aborts with its own return code (e.g. ARGV_MISMATCH), plus the same check inside the queue script.
- Each run gets one wait cap of about 3x the expected render time. A prompt ID that's missing from both the queue and the history for 3 polls is LOST_PROMPT, not "keep waiting". ComfyUI keeps history in memory, so a restart erases it (R1: a 4-hour hang).
- Waiting on a marker in an orchestrator log needs a deadline and must match only lines written after this run started (R14).
