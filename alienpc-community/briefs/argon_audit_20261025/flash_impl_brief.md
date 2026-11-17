# Flash High implement brief: Forge audited plan (2026-10-26)

You are Antigravity on Gemini 3.8 Flash High, the IMPLEMENTER (Derrick, 10:16 PM Oct 25: "After it passes the audit have antigravity flash high implement all the changes and setup forge and optimize or whatever"). This is ONE run. Do all 12 to-do items below in order, one change at a time, then stop. Do not ask questions; if an item is blocked, log why in progress.md and move to the next item.

Working folder: C:\AI\community\briefs\argon_audit_20261025\
- Plan v2: plan_v2.md (in this folder)
- Fleet Reviewer audit: context\fleet_audit_r2.md (read the "Round 2" section, R2-0..R2-8). Verdict: READY WITH FIXES.
- Protected-file hashes taken before this run: pre_impl_hashes.txt (this folder).
- Progress log you keep: progress.md (this folder). Append one entry per change: time CT, step ID, files, commit hash, verify command + result, rollback.

## Derrick's words (quote them as his answers; they are not "rules")
- 9:09 PM Oct 25: "Give argo high all the stuff and instructions and plans on all the test community stuff for optimizing Forge ect all our MD files and everything it needs to succeed I want antigravity argon on high to fix our setup and determine why we are have so many issues. Double check for errora missing information potential issues and improvements it should ensure that forge succeeds and is the ultimate local AI setup for coding, comfy UI visuals sowtcharyd/pi/agent harness/instructions/personas/skills ect."
- 10:15 PM: "I don't remember those kitchen attention? I want best practices and community guidance? Geared on what works best on my setup"
- 10:16 PM: "After it passes the audit have antigravity flash high implement all the changes and setup forge and optimize or whatever"
- 10:17 PM: "Community adults only. I want community fucking swttings"
- 5:58 AM Oct 26: "Also why are we still using switchyard and not llama swap and them community or whatevet?"
- 5:59 AM: "Have antigravity review forge and llama swap and stuff and comfy make sure they are setup and config correctly"
- 6:00 AM: "Don't waste usage"
- 6:01 AM, approving the to-do list below: "Ok have it do it"
- Earlier (6:48 PM Oct 25): "Sort out the Comfy Kitchen attention conflict"; "Go back to Euler, 5-second clips and 350–500 word prompts".

## HARD LIMITS (any breach = stop the item, log it, do not work around it)
1. Secrets: never print, cat, copy or put in a command any token, key, password, rclone config, auth.json, .env, or credential file. Never open Grok Imagine .json sidecars or the GMD prompt cache.
2. GPU lock: anything that uses the GPU (renders, model loads, vision probes) runs only when `powershell -NoProfile -File C:\AI\director\scripts\gpu_guard.ps1` returns rc 0, and goes through the normal gpu-render.lock path (run_graph_job.py). Never kill ComfyUI mid-render.
3. Youth guard: fictional adults only. comm.py's adults-only check (guard_ok) runs before every render and is NEVER loosened; you may only widen its scope. C:\AI\community\scripts\tests\test_p6_review.py is never edited (sha must match pre_impl_hashes.txt). p6_review.guard_check is never edited.
4. No vision judge on rendered explicit output. Captioning START images is fine. Vision never decides identity or age.
5. GI063 stays held. Never touch D:\Apps\finance-app* or any UniFi folder.
6. No deletes, anywhere. Archive = copy or move into a dated archive folder. No `git push`. No `git reset --hard`, no force anything.
7. 128K context (131072) stays on every model that has it.
8. No renders until Step 0 (A6-01a) and Step 1a are committed and verified.
9. KEEP decisions are Derrick's. Where a test result would change a KEEP (except the Comfy Kitchen item, see To-do 5), record the result and leave the default as is.
10. Do not merge switchyard-upgrade and do not turn on its flags (confirm_free / as_model_enabled / stall_ladder_enabled).
11. One change per commit. Every commit message starts with the step ID (e.g. "S1a: ..."). Commit in the repo the file belongs to (C:\AI\community, C:\Users\derek\5slock\ralph-community, C:\AI\director, ...). Files outside a git repo: back up as <file>.bak-20261026-<stepid> first and log in progress.md.
12. Long commands (renders, pytest that touches models): start them in the background, poll their log; never leave a blocking shell over ~10 minutes.

## To-do list (approved, do in this order)
Map each to the plan steps; use the step IDs below in commits and progress.md.

1. **S-plan: write plan_v3.md** in this folder = plan_v2 with the audit's round-2 fixes applied:
   - N2-1: Flash High is the implementer, under the AlienPc lease and the GPU lock, step IDs in commits and progress.md (replace "Owner: Forge ... Antigravity and Max do not edit Forge's files").
   - N2-3: split Step 1. 1a = guard key scope in run_graph_job.py + comm.py + tests/test_guard_scope.py. 1b = Continuum `no:` lines become community artifact-only negatives (now APPROVED by Derrick, artifact-only).
   - N2-2: Step 9(b) res_multistep is an APPROVED A/B test vs Euler (one fixed seed). Euler stays the default unless Derrick picks otherwise.
   - N2-4: split Step 6 into 6a (Strata max_tokens) and 6b (judge request params only). guard_check in p6_review.py untouched; 6b verify adds pytest test_p6_review.py test_guard_scope.py + sha check.
   - N2-5: Switchyard is NOT merged (d9efd2f is in director, b6384bc is not). Replace Step 12(b) with the Switchyard retirement (To-do 8).
   - N2-6 / R2-2: Step 8 rests on the community default ("pytorch attention", H3 docs default), NOT the convrot claim. Re-read the checkpoint header and log what it really says.
   - N2-7: measure render times before setting any timeout; the timeout kills the whole process tree and releases the GPU lock (comfy_graceful_stop.ps1 or lock check); verify with a forced short timeout on a dry pass.
   - N2-8: 9(a) is two variables (ref_image_size, MiniMaxH3AddGuide): split them. Step 10: name every skill disabled. Step 11: state which of args / args_written is right and why; defer any control-vector sweep. Step 2: check BOTH C:\Users\derek\.pi\agent\settings.json and C:\AI\director\config\pi\settings.json. Step 4: verify = rc 0 and log the time (drop "<10s").
   - N2-10: pi-mobile persistent is APPROVED; add a real HTTPS check through tailscale serve.
   - N2-9 / N2-11: relabel Derrick's words as his quoted answers; fix the header time.
   - Comfy Kitchen (To-do 5) and Switchyard (To-do 8) and the vision models (To-do 4) are in scope.
   Then sha256 plan_v3.md into progress.md. Follow plan_v3 for everything after this.

2. **S-pause: pause Forge.** ralph.ps1 has NO stop file. Max already set up the pause before this run: the scheduled task \ForgeRalphLoop is disabled (so it won't relaunch), and a watcher (forge_pause_watch.ps1, log forge_pause.log in this folder) waits for the current pi pass (PID 36784) to exit on its own, then stops the ralph PowerShell (PID 2908) between passes. Never kill a pass mid-render. Do the S-plan item while you wait. Before you edit ANY Forge, community, director or pi file, wait until forge_paused.txt exists in this folder (check about every 2 minutes with a short sleep). Also confirm no pi --print process is running and ComfyUI has no running job. If it doesn't exist after 90 minutes, log "S-pause: still waiting" and do only the read-only parts (caller search, render-time measurement) until it appears. To resume (to-do 12): `Enable-ScheduledTask -TaskName ForgeRalphLoop` and `Start-ScheduledTask -TaskName ForgeRalphLoop`, then log the new ralph PID.

3. **S0, S1a, S1b: guard.** S0 = plan Step 0 (ali173_pw1d_run.py through comm.guard_ok and comm.BASE; verify with one guarded dry submit, no real render). S1a = widen guard_ok key scope in run_graph_job.py and comm.py to every prompt-bearing input (prompt, text, prompt_1..6, clips_json, sequence_prompt, value) + tests/test_guard_scope.py; pytest both test files green; test_p6_review.py sha unchanged. S1b = community artifact-only negatives on Continuum `no:` lines (e.g. "no: watermark, text overlay, logos, extra limbs, deformed hands, blurry, camera cuts"). The adults-only check before every render stays, never loosened.

4. **S-pi: clean up pi settings and models.json.** Plan Steps 2 (AGENTS.md consolidation, STANDING.md, F12 check in both settings.json files) and the models.json part of Step 11. Add the uncensored vision models that are ALREADY defined in C:\AI\director\config\llama-swap.yaml (Defiant Fable Heretic 9B with its mmproj; qwen3-vl-8b-abliterated) to C:\Users\derek\.pi\agent\models.json with input ["text","image"], using the exact llama-swap model ids. Do not download models. json.tool both files.

5. **S8: Comfy Kitchen attention -> community default.** comm.py ModelAttentionBackend default "comfy kitchen attention" -> "pytorch attention" (H3 docs default). First ONE fixed-seed check render on seed 51150011 (gpu_guard rc 0, via run_graph_job.py), changing only that input. Log "Oct 9 KEEP superseded 2026-10-26 (Derrick 10:15 PM: community best practice)". Switch the default unless that render fails or is clearly broken (judge only by technical signals: errors, black/blank frames, runtime, file size — no vision judge on explicit output); if it fails, keep ck-attention and flag it in final_review.md.

6. **S10-timeout: measure render times, then set ralph's timeout.** Read all p7\jobs\*.result.json (and run results) for render durations and renders per pass; compute timeout = renders per pass x longest render + queue time, with the numbers in progress.md. Implement in ralph.ps1 (backup first) so a timeout kills the whole pi process tree, then runs C:\AI\director\scripts\comfy_graceful_stop.ps1 or verifies gpu-render.lock is released. PowerShell AST parse = 0 errors; verify with a forced short timeout on a dry pass (no render). Also do plan Step 10 (1) progress.md rotation (archive copy first) and (2) non-blocking p7_budget.json counter, each its own commit.

7. **S7-trim: trim Forge's skills and instructions to community defaults.** Plan Steps 3, 4, 5, 10(1): plain markdown fix_plan.md (archive first). The overnight plan-builder rewrite repeated ID tokens in ticked rows ("TOP-SCENE TOP-SCENE ...") and cut six open items down to "DRAFT-NEEDS-AUTHORING" (ORC-ROBOT, H3-RESEARCH, NOW-P3, AUD1, ALI-173-STORYBOARD, SUBJECT-LABELS). Restore their full text from git (`git -C ralph-community show 3fcafbb:fix_plan.md`) into the plain fix_plan.md, and stop the builder from rewriting fix_plan.md (archive ali14d_shortplan_build.py's --emit use; don't delete it). prune ali11_run_checks.py to real validators, align rt_window_probe/AGENTS.md with llama-swap groups, disable unused skills — list every skill by name in progress.md. Copy before trimming; nothing deleted.

8. **S-switchyard: retire Switchyard (ARCHIVE, never delete).** First find EVERY caller: search C:\AI\director, D:\AI\director, director.yaml, scripts (.ps1/.py/.bat/.cmd), Forge PROMPT.md/AGENTS.md/skills, pi settings, and scheduled tasks (Get-ScheduledTask | look at Actions). Write the caller list to switchyard_callers.md (path:line, what it does). Repoint each one: model swapping -> llama-swap (its API on the existing llama-swap port, with community ttl/groups settings from the llama-swap README/config example); renders -> ComfyUI's own /prompt queue through comm.py (guard intact), with ComfyUI's built-in memory flags (community defaults, no custom flags). One caller per commit. Then MOVE the Switchyard folder(s) to a dated archive, e.g. C:\AI\_archive\20261026_switchyard\ (stop any Switchyard process only after nothing calls it; record PIDs). Do not merge switchyard-upgrade or enable its flags. Verify: no remaining caller references (re-run the search), llama-swap /v1/models answers, ComfyUI /system_stats answers.

9. **S-bridge: discord_bridge.** Re-check the process tree (Get-CimInstance Win32_Process, ParentProcessId, CommandLine without printing env/tokens). The plan says 26972->27152->26876->26896 is ONE venv launcher chain. Stop a copy ONLY if a second independent bridge instance really exists; keep one running. If no duplicate: stop nothing and log that.

10. **S-pimobile: pi-mobile always on over Tailscale** as a persistent service (scheduled task at logon or equivalent community way, restart on failure), port 7878. Verify: 7878 has a listener between passes (Get-NetTCPConnection -LocalPort 7878 -State Listen) and an HTTPS request through `tailscale serve` (https://<tailnet-host>:8443) returns a response (curl.exe -sS -o NUL -w "%{http_code}"). Never write the tailnet host name into committed files; use <tailnet>. QR pairing is Derrick's; note it.

11. **S9: A/B res_multistep vs Euler**, one fixed seed (51150011), only after S0 and S1a are verified, gpu_guard rc 0, everything else identical. Record render paths, runtimes and technical stats only (no vision judge). Euler stays default; Derrick decides. If time allows, 9(a) split: ref_image_size "match" alone, then MiniMaxH3AddGuide alone, each its own render, results logged, default unchanged unless clearly community default with no KEEP conflict.

12. **S-final: final review.** Check the live setup end to end against official docs or community sources (cite links): Forge/pi (settings.json both, models.json, ralph.ps1, PROMPT.md, AGENTS.md, skills), llama-swap (llama-swap.yaml, model args, ttl/groups, vision models + mmproj, 128K context), ComfyUI (launch flags, attention, memory flags, queue, custom nodes, workflows). Fix mismatches one at a time (own commit each, step ID "S12-<n>"). Write final_review.md here: a table Component | Check | Source link | PASS/FAIL | Note. Then RESUME Forge the same way it was launched (remove the stop file / relaunch ralph.ps1 the recorded way) and confirm the new ralph PID in progress.md.

## End of run
Last lines of progress.md: a summary table (step ID | commit | verify | result), the list of anything that needs Derrick, and sha256 of plan_v3.md and final_review.md. Do not run `/usage` or other slash commands; Max does that.

## ADDENDUM from Derrick, 7:05 AM CT Oct 26 (in scope; do these too)
(A) He said: "Yes, add restoring the six plan items". During S7-trim, while Forge is paused, restore the FULL text of the six fix_plan.md items that the plan rebuild cut down to "DRAFT-NEEDS-AUTHORING" (ORC-ROBOT, H3-RESEARCH, NOW-P3, AUD1, ALI-173-STORYBOARD, SUBJECT-LABELS). Use the last good version of each from git history (e.g. `git -C C:\Users\derek\5slock\ralph-community log -p -- fix_plan.md`; 3fcafbb has them). Also remove the repeated ID words in ticked rows (e.g. "TOP-SCENE TOP-SCENE TOP-SCENE ..." -> one "TOP-SCENE"). Commit as "S7-restore: ...". Then fix the plan builder (ali14d_shortplan_build.py / its --emit) so it can never rewrite fix_plan.md like this again (community Ralph: fix_plan.md is a plain markdown checklist the agent edits; the builder must not emit into it). Its own commit "S7-builder: ...".
(B) For S10-timeout (the loop step): find out why pi exited nonzero at 10:22 PM Oct 25 (ralph passes 7, 8, 9; see logs\iter-20261025-*.log and logs\ralph.log) and write the cause in progress.md. Make sure that when ralph stops itself (STOPPED / stuck exit 2, or a timeout), the \ForgeRalphLoop scheduled task does NOT relaunch it until the cause is fixed. Use a community frankbria/ralph-claude-code style circuit breaker (its documented CLOSED/HALF_OPEN/OPEN state file that the loop checks at start and that a human or a fixing commit resets), not a new custom script. Commit "S10-breaker: ...". Report both in progress.md.


## ADDENDUM 2, 7:08 AM CT (overrides to-do 12's resume)
Do NOT resume Forge at the end. Leave \ForgeRalphLoop disabled and write 'S-final: Forge left paused for Max to resume' in progress.md. Max adds one queue item to fix_plan.md and resumes Forge himself. Do not edit the Max block at the top of fix_plan.md beyond what S7-restore needs.

