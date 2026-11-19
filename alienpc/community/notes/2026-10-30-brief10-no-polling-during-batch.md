# brief10: stop the timed checks; wait once until the batch ends (Derrick 11:01 AM CT: "implement the fix now")

Why: the stalls at 10:28, 10:44 and 11:00 (pos 20, 23, 27) each came seconds after one of your timed status checks returned. Your next model turn makes llama-swap stop comfyui_auto to load your model, so the clip in flight is lost and retried after ~4 min. (Phase 2 plan item S11.)

Do now, in this order:
1. Do NOT stop or touch the batch (PID 17268), ComfyUI, llama-swap or the lock.
2. Make exactly ONE tool call and nothing else: a blocking wait that returns only when the batch exits, with the longest tool timeout you can set (60+ min):
   powershell: Wait-Process -Id 17268 -ErrorAction SilentlyContinue; Get-Content C:\AI\community\runs\terrace_settings_v3_20261030\_render_queue.log -Tail 6
   No timed polls, no log reads, and no other tool or model calls until it returns. If your tool times out anyway, re-run the same single wait right away without any other step.
3. After the batch exits (not before): add one line to C:\AI\community\scripts\run_queue.py's usage note and AGENTS.md: "After launching a batch, make one blocking wait on the batch PID; make no model calls until it exits (llama-swap swaps ComfyUI out when the model loads)." Commit it, then reply to Max with the DONE/FAIL counts.
