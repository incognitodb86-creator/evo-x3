# Antigravity monitor brief: Forge Ralph loop watchdog (Derrick 2026-10-24 9:26 PM CT: "Setup Ralph loop and ensure it can recover" / "Maybe have flash low in antigravity monitor it?"). Cut to restart-only 2026-10-25 (Derrick 3:56 AM CT, Alfred audit).
You check on Forge once per run, take at most the one fix below, log one line, and exit.

Paths: loop C:\Users\derek\5slock\ralph-community (ralph.ps1, logs\ralph.log). Log: append one line per run to C:\AI\community\briefs\agy_monitor.log with the time (CT), what you saw, and what you did.

1. Alive: is a powershell process running ralph.ps1? If not, run `Start-ScheduledTask -TaskName ForgeRalphLoop` and log RESTARTED.
2. Otherwise log OK.

Render window rule (fix_plan MONITOR, 2026-10-25): before step 1, read C:\AI\locks\gpu-render.lock. If it exists and its first number is a LIVE process id, a render owns the GPU: do NOT start ForgeRalphLoop (a fresh loop pass is an LLM request, and that is what killed 2 of the last 3 renders), log `RENDER_BUSY pid=<pid>` and exit. A dead pid in that file is a stale lock - ignore it, exactly as C:\AI\director\scripts\gpu_guard.ps1 does. Your own model calls go to a hosted service, never to llama-swap, so you are not the LLM caller; keep the one line per run.

Never: stop or kill any process, render or queue anything, edit any file except the log, delete anything, mark KEEP, look at clips, or open secrets, .json sidecars or the GMD prompt cache.
