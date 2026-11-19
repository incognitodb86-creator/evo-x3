---
title: The AlienPc speed orchestrator skipped every arm even though ComfyUI was up
tags: [unreviewed, max, harness]
date: 2026-10-09
---
- orchestrate_169_speed.ps1 logged ARM_SKIP BASE/ASYNC 6 minutes apart with no COMFY_UP or COMFY_FAIL lines, even though each ComfyUI log reached "Starting server" and a manual Invoke-RestMethod to /system_stats worked.
- Suspect: Start8189 returns pipeline output from L (Tee-Object), or throws inside the hidden 5.1 host, so its return value isn't a clean bool. Fix: make L write with Add-Content only (no pipeline output), have Start8189 return [bool], and log the caught exception text.
- 2026-10-09 ~5:03 PM CT: Sydney stopped the run, restarted ComfyUI on the KEEP argv by hand and wrote SPEED_END so the audio tests could start. The speed retest is still owed.
