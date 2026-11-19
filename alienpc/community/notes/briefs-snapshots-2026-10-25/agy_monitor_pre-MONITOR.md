# Antigravity monitor brief: Forge Ralph loop watchdog (Derrick 2026-10-24 9:26 PM CT: "Setup Ralph loop and ensure it can recover" / "Maybe have flash low in antigravity monitor it?")
You check on Forge once per run, take at most the fixes below, log one line, and exit. Keep it short.

Paths: loop C:\Users\derek\5slock\ralph-community (ralph.ps1, fix_plan.md, logs\ralph.log, git). Render handoff C:\AI\community\p7\JOB_REQUEST.json. Log: append one line per run to C:\AI\community\briefs\agy_monitor.log with the time (CT), what you saw, and what you did.

1. Alive: is a powershell process running ralph.ps1? If not, run `Start-ScheduledTask -TaskName ForgeRalphLoop` and log RESTARTED.
2. Stalled: if the pi-coding-agent node process (child of ralph.ps1) has run more than 75 minutes AND `git log -1 --format=%ct` is more than 75 minutes old, stop only that node process (Ralph moves to its next pass) and log STALL_KILLED with the last 5 lines of logs\ralph.log.
3. Armed render: if JOB_REQUEST.json names an id whose mp4 (C:\AI\community\runs\<id>\<id>.mp4) does not exist, and no run_graph_job.py process is running: stop the ralph.ps1 process and its pi child, run the render command written in the request's note exactly as written (it runs comm.py's adults-only check and the budget gate itself), wait for it to finish, run any --sheet command the note names, then run `Start-ScheduledTask -TaskName ForgeRalphLoop` and log RENDERED <id> with the result or the error lines. One render per run.
4. Otherwise log OK.

Never: edit Forge's files (ralph.ps1, PROMPT.md, AGENTS.md, fix_plan.md, comm.py, scripts\tests\test_p6_review.py, any graph), delete anything, mark KEEP, look at or score clip images, touch D:\ or E:\ besides reading, or open secrets, .json sidecars or the GMD prompt cache.
