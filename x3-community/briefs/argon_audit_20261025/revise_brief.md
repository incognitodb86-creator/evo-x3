# Antigravity revise brief: Argon HIGH plan v2 (PLAN MODE ONLY) - Oct 25, 2026, 10:20 PM CT

## Derrick's words, verbatim
- 9:09 PM CT: "Give argo high all the stuff and instructions and plans on all the test community stuff for optimizing Forge ect all our MD files and everything it needs to succeed I want antigravity argon on high to fix our setup and determine why we are have so many issues. Double check for errora missing information potential issues and improvements it should ensure that forge succeeds and is the ultimate local AI setup for coding, comfy UI visuals sowtcharyd/pi/agent harness/instructions/personas/skills ect.  It should first do plan mode and then send auditor the plan to have it audited"
- 10:14 PM CT: "Have Argon high revise the plan in plan mode using Fleet Reviewer's audit, then send it back for another audit"
- 10:15 PM CT: "I don't remember those kitchen attention? I want best practices and community guidance? Geared on what works best on my setup"
- 10:17 PM CT: "Community adults only. I want community fucking swttings"

## Inputs (all in C:\AI\community\briefs\argon_audit_20261025\)
- brief.md: the original brief. Its hard lines, index and output rules all still apply.
- plan.md: your v1 plan.
- context\fleet_audit.md: Fleet Reviewer's audit of v1 (verdict NOT READY): findings A-1..A-10, K-1, K-2, G-1, the section 7 fix list (12 items) and the section 8 checks.

## The ask
Revise plan.md into **C:\AI\community\briefs\argon_audit_20261025\plan_v2.md** (if plan mode blocks the write, give the full plan as your final answer; the launcher saves it to plan_v2_stdout.md).
1. Address EVERY audit finding: A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9, A-10, K-1, K-2, G-1, and each of the 12 fix-list items. Start plan_v2 with a table: finding ID | how v2 addresses it (item/step ID) | or why not, with evidence (path:line).
2. Re-read live files now; do not trust v1 or old copies:
   - K-1: C:\AI\director\config\llama-swap.yaml around line 97 (Select-String for lowvram / use-ck-attention with line numbers), the live ComfyUI process argv (read-only: Get-CimInstance Win32_Process for main.py, CommandLine only), comm.py `attention=` defaults (lines ~75 and ~123), and whether the active H3 UNET is an int8_convrot build (from its saved model card or file metadata; do not load it). If the CLI flags are gone, drop that half of v1's A6-02 and root cause 9.
   - K-2 (read-only): run `git -C C:\Users\derek\5slock\ralph-community show --stat f7d3fad fd426b8` and `netstat -ano | findstr :7878` (or Get-NetTCPConnection -LocalPort 7878) now, plus `tailscale serve status` if it is read-only. Say whether a Forge pass was running at that moment (logs\ralph.log tail). Do not start, stop or serve anything. The tailnet URL goes in plan_v2 as `<tailnet>`, not the real hostname.
   - Also do the read-only checks in the audit's section 8 that you can (settings.json extensions headless-guard-and-truncate.ts / protected-paths.ts; grep scripts for direct /prompt posts incl. C:\AI\community\notes\ali173_pw1d_run.py; longest render in C:\AI\community\p7\jobs\*.result.json; discord_bridge PIDs; Switchyard repo state; ALI-162 status if found in files).
3. Every step in v2 uses the audit's template: owner (Forge), one change, verify, rollback, log/commit, as a fix_plan.md item. Antigravity and Max don't edit Forge's files. Mark which steps need Derrick's go (process stops, Switchyard merge, comm.py edits) and which run under gpu_guard.ps1 rc 0.
4. **Settings choice rule (Derrick 10:15 PM and his Oct 19 standing rule: community best practice overrides his conflicting past decisions).** For attention, and for every other setting, pick the community/official-docs best practice for THIS hardware: AlienPc's GPU and VRAM as found on disk (cite where you found the GPU model/VRAM, e.g. gpu_guard.ps1, logs, strata configs). Cite the source. Give a fixed-seed A/B as the verify step. Don't keep a past choice just because it was recorded (e.g. the Oct 9 ck-attention KEEP in context\box\packs\max\production-defaults-st8-dynamic-vram.md); note it, then follow the community/official guidance for this setup.
5. Derrick's 10:17 PM words ("Community adults only. I want community fucking swttings") answer the audit's points on the adults-only check (A-1..A-3, negative prompts) and on custom controls (A-6 cap, A-8 secret scanner, A-9 guard extensions). Take them as his words and apply them to those items. They don't add rules. His standing line still applies: the adults-only check stays on before every render and is never loosened.
6. Keep plan_v2 SHORTER than v1 (v1 was 78 KB; aim for under 40 KB). Cut the file list to the files you actually used for v2.

## Hard lines (Derrick's own standing rules, same as brief.md)
- Plan mode only. Write nothing outside C:\AI\community\briefs\argon_audit_20261025\. No edits, commits, git writes, process starts/stops, scheduled-task changes, service restarts, tailscale serve changes, renders or model loads. Forge's Ralph loop and its pi passes keep running untouched; don't touch fix_plan.md, PROMPT.md, AGENTS.md or any config.
- Community/stock settings first; one published change at a time.
- Fictional adults only. The comm.py adults-only check runs before every render and is never loosened.
- C:\AI\community\scripts\tests\test_p6_review.py is never edited (new tests go in a new file).
- No secrets read or printed (no .env, auth.json, pi-mobile push.json/machine.json, rclone config, .ssh, tokens, Grok Imagine .json sidecars, GMD prompt cache).
- No deletes. 128K context stays. KEEP verdicts are Derrick's alone.
- Every number must come from a file or command you ran this run, with its path. Mark anything unchecked as UNVERIFIED.
