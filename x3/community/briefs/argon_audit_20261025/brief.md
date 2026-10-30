# Antigravity brief: Argon HIGH plan-mode audit of Forge's setup (Oct 25, 2026, 9:40 PM CT)

## Derrick's words (9:09 PM CT Oct 25 2026), verbatim
"Give argo high all the stuff and instructions and plans on all the test community stuff for optimizing Forge ect all our MD files and everything it needs to succeed I want antigravity argon on high to fix our setup and determine why we are have so many issues. Double check for errora missing information potential issues and improvements it should ensure that forge succeeds and is the ultimate local AI setup for coding, comfy UI visuals sowtcharyd/pi/agent harness/instructions/personas/skills ect.  It should first do plan mode and then send auditor the plan to have it audited"

## Your job this run (PLAN MODE ONLY)
This run is plan mode. You read and analyze; you change nothing. Your single output is a plan file:
**C:\AI\community\briefs\argon_audit_20261025\plan.md**
If plan mode does not let you write that file, put the complete plan as your final answer (the launcher saves it to plan_stdout.md and Max copies it to plan.md).
After your plan, Fleet Reviewer audits it before anything is applied. Fixes come later, one at a time, with Derrick's go.

The plan must cover root causes of why there are so many issues, plus errors, missing information, potential issues and improvements, across:
coding model + Strata/llama-swap serving, the pi harness (settings, models, compaction, extensions, permissions), the Ralph loop (ralph.ps1, PROMPT.md, AGENTS.md, fix_plan.md, pass size, commit discipline), instructions/personas/skills (5slock AGENTS.md, community skills, Max's box skills and packs), Switchyard, llama-swap, ComfyUI visuals (install, custom_nodes, workflows, comm.py, vision judge, prompts).
For EVERY item give: (1) the finding, (2) evidence as file path + line number(s) you actually read, (3) the community/upstream source it follows (doc, repo README, published default; prefer the saved copies listed below, cite URL or path), (4) risk if changed and risk if left, (5) a verify step that proves the fix worked, (6) priority. Order the whole plan by priority. Start with a top-10 root-cause summary. Mark anything you could not verify as UNVERIFIED rather than guessing. Do not invent results, timings, gates or files; every number must come from a file you read this run, with its path.

## Hard lines (these are Derrick's own standing rules, not new rules)
- Plan mode only this run. Write nothing outside C:\AI\community\briefs\argon_audit_20261025\. No edits, no commits, no git add/stash/checkout, no process starts or kills, no scheduled-task changes, no service restarts. Forge's Ralph loop (scheduled task ForgeRalphLoop) and its pi passes keep running; do not touch them, fix_plan.md, PROMPT.md, AGENTS.md or any config.
- Community/stock settings first, and one published change at a time ("i want community settings, if i made any descision that odesn match communit best pracitces we should change it").
- Fictional adults only. The comm.py adults-only check (C:\AI\community\scripts\comm.py) runs before every render and is never loosened. Do not propose loosening it.
- C:\AI\community\scripts\tests\test_p6_review.py is never edited. Do not propose editing it.
- No secrets read or printed. Do NOT open: any .env, auth.json, C:\Users\derek\.pi\agent\pi-mobile\push.json or machine.json, rclone config, anything under .ssh, token/credential files, Grok Imagine .json sidecars, the GMD prompt cache. If a file looks like it holds a key, skip it and say so.
- No deletes of anything.
- 128K context stays (Derrick: "judt keep it we did mesure it"). Do not propose shrinking it.
- KEEP verdicts on renders are Derrick's alone.
- Do not start renders or load models; GPU belongs to Forge. You are cloud-side.

## Known issues today (facts from Max's audits and the files; verify against disk, cite what you confirm)
1. The 5:08 PM pass ran 2 h 04 min (5:08:22-7:12:44 PM CT) with 0 commits. 19 compaction summarization requests hit the 16,384-token output limit (~51 min lost); after each failure 104-119K tokens were reprocessed with no cache reuse. Session: C:\Users\derek\5slock\ralph-community\sessions\2026-10-25T22-08-23-175Z_01a1751b-9086-7231-a920-47aa9ff8f5c6.jsonl. Full audit facts: C:\AI\community\briefs\agy_fix_20261025.md.
2. Opening prompt ~94K tokens (PROMPT.md + AGENTS.md + fix_plan.md + progress/notes loaded each pass) against a 128K window, leaving little working room.
3. Invented results: claimed renders "on disk with proofs" and a gate "I just created it!" with no matching tool call (session entries #214, #238).
4. Repeated checks instead of commits (shortplan --check 30x, py_compile 29x, ali11_run_checks 29x, loop check 23x, citation check 18x in one pass).
5. A foreground `tailscale serve 7878` hung Forge 36 min; the pi bash tool had no shell timeout.
6. Vision captions came back truncated/empty because thinking models put the caption in reasoning_content; fixed with reasoning_effort=none (see notes\ali163_vision_probe*.json, ralph-community notes\plans\3.17-vision-battery.md).
7. Solo-template prompts were used on start images with 2+ subjects, so the second subject was ignored.
8. Size: fix_plan/plan material ~159 KB and pass logs/sessions ~1 MB each (sessions\*.jsonl 0.95-2.1 MB; notes\progress.md 170 KB), far beyond Derrick's community ask (small plan, one item per pass, stock settings).
9. Duplicate director.discord_bridge processes running.
10. pi-mobile not yet live per Max (note: ralph-community commits f7d3fad/fd426b8 at ~9:2x PM claim "pi-mobile live"; verify which is true and flag the gap).
11. Earlier today agy flash-medium applied 5 fixes (C:\AI\community\briefs\agy_fix_20261025_report.md, agy_fix_20261025.log): pi compaction to 16384/16384, thinkingBudgets, Qwen compat in models.json, PROMPT.md commit-first + anti-hallucination step 0e, ralph.ps1 real-date injection, comfyui_auto moved into llama-swap main exclusive group, killed stray llama-server PID 3848, disabled ForgeAgyMonitor. Judge whether each matches community defaults and whether it worked in the passes since 7:13 PM (logs\iter-20261025-03..05.log, the 3 newer sessions).
12. Earlier agy audit: C:\AI\community\briefs\agy_audit_20261025.md and agy_audit_20261025_report.md. Note what it got right and wrong.

## INDEX: what to read (paths only; read what you need, cite lines)
### Forge / Ralph loop (C:\Users\derek\5slock\ralph-community)
- PROMPT.md, AGENTS.md, fix_plan.md, ralph.ps1, README.md, BASELINE_TEST_20261023.md, chain.ps1
- PROMPT.md.bak-* and ralph.ps1.bak-* (history of loop changes), STOP_RALPH.done-* (why loops were stopped)
- notes\ (141 files; newest: progress.md, pm2_results_build.py, ali11_run_checks.py, ali14d_shortplan_build.py, ali15_pi_mobile_probe.py, refusal_vector_test_20261025.md, pi_mobile_live_20261025.md, pi_mobile_20261024.md, ali05_loop_check.py, ali06_learnings_check.py)
- notes\plans\ (pm2-pi-mobile-live.md, 3.18-refusal-test.md, 3.17-vision-battery.md, 1.4d-shortplan.md, 2.4-register-prompt-key.md, q6-adults-probe.md, 0.8-git-status-cleanup.md, render-timeout.md, 0.7.md, 2.2-graph-builder-gate.md, aud1*.md, 0.4-*.md, 0.1-*.md, receipts\)
- logs\ralph.log, logs\iter-20261025-0*.log, logs\ralph-20261025-*.log
- sessions\*.jsonl (large; grep, don't load whole)
- `git -C C:\Users\derek\5slock\ralph-community log --oneline -40` (read-only)
- C:\Users\derek\5slock\AGENTS.md, strict-still-review.md, STRICT_STILL_REVIEW.md
### pi harness (C:\Users\derek\.pi)
- agent\settings.json (+ settings.json.bak-* history), agent\models.json (+ .bak-*), agent\mcp.json, agent\pi-permissions.jsonc, forge-policy\pi-permissions.jsonc
- agent\npm\package.json (extensions: pi-permission-system 0.8.0, pi-subagents, pi-mobile, pi-hermes-memory, pi-mcp-extension, comfyui-mcp-server-node); settings packages also load git:github.com/EveryInc/compound-engineering-plugin and C:\AI\security\skillspector\clone
- agent\pi-hermes-memory\MEMORY.md, STANDING.md, failures.md; agent\pi-hermes-memory\skills\
- Package READMEs/default configs under agent\npm\node_modules\<pkg>\ are the community source for pi extension settings
- C:\AI\director\.pi\, C:\AI\director\config\pi\, C:\AI\pi-agent\
- SKIP: pi-mobile\push.json, pi-mobile\machine.json, any auth/session token files
### Serving: llama-swap, Strata, models
- C:\AI\director\config\llama-swap.yaml (live; + llama-swap.yaml.bak-* history, .bak-community = earlier community baseline)
- C:\AI\community\notes\llama-swap-pre-RENDER-TIMEOUT-20261026.yaml
- C:\AI\strata-0.2.2\ (strata-swift15-iq3s.json ctx 131072, strata-swift15-iq3s-esp.json, strata-iq3_s.json, sy_strata_launch.py, strata-swift15-iq3s.log)
- C:\AI\director\scripts\comfy_graceful_stop.ps1, C:\AI\director\config\director*.yaml, judge_rubric.md
- llama-swap /logs endpoint (read-only GET http://127.0.0.1:8080/logs if reachable) - "stop signal failed: exit status 128" for the coding model
### Switchyard
- C:\AI\switchyard-upgrade\ (repo\, CHANGES.md, DONE.md, prompt.txt, launch.ps1), C:\AI\agy-fix-switchyard-2026-10-14\, C:\AI\sy-forge-audit\, C:\AI\community\runs\p6_1min_switchyard\, C:\AI\community\scripts\sy_graph.py, sy_1min.py
### ComfyUI visuals
- Live (comfyui_auto): C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\ (custom_nodes\ - 46 node packs incl. ComfyUI-H3-Continuum, comfyui-storyboard, ComfyUI-PuLID-Flux2, ComfyUI-DaSiWa-Nodes, MiniMax H3 packs, WanVideoWrapper, LTXVideo, GGUF, Impact; user\default\workflows\ incl. Community\, Community_H3_I2V_beta6.app.json, video_minimax_h3_i2v_STOCK.json)
- Long video (comfyui_longvideo): C:\AI\comfy-longvideo\ComfyUI\ (custom_nodes, user\default\workflows)
- C:\AI\community\scripts\ (comm.py = adults-only check + /upstream/comfyui_auto queue; run_graph_job.py, p6_review.py, prompt_writer.py, comfy_ctl.py, batch_queue.py, face_crop.py; tests\ incl. test_p6_review.py - read only, never edit)
- C:\AI\community\notes\ (ali163_vision_probe.py/_results.json, ali318_refusal_probe.py/_results.json, ali320_prompt_shape.*, hc15_*.md, hc15_audit\, cf1_setup_audit_20261024.md, git_status_cleanup_20261025.md, gmd_ext_20261024.md (no cache contents), progress.md, ali27_*, web\ = saved community sources)
- C:\AI\community\guides\VIDEO_PROMPT_WRITING_GUIDE_base_en.md, _ref_en.md
- C:\AI\community\skills\forge-self-diagnose\SKILL.md, h3-hc-render\SKILL.md, h3-prompting\SKILL.md
- C:\AI\director\config\workflows\, C:\AI\director\docs\ (53 MD)
### Community research and earlier audits (C:\AI\community)
- RUNBOOK.md, SETTINGS_CHECK.md, P5_CHECK.md, RESEARCH_2026-10-21_forge_agentic_comfy.md, community.log
- research\forge-docs-20261025\ (README.md, canon\, learnings\, packs\, research\, skills\), research\video-review-optimize-2026-10-20.md
- briefs\: agy_audit_20261025.md + _report.md, agy_fix_20261025.md + _report.md + .log, agy_monitor.md, agy_llamaswap_setup_20261024.md + _DONE.txt, agy_rest_20261024.md, agy_setup_20261024.md, agy_hc15_20261024.md
- Any other *.md under C:\AI\community (about 1,690 outside archive\ and runs\; use search, do not read all)
### Box context copied for you: C:\AI\community\briefs\argon_audit_20261025\context\box\
(full list: context\INDEX_box.txt)
- packs\fleet\derricks-standing-rules.md (Derrick's standing rules: authoritative), external-actions-need-derricks-exact-yes.md, fiction-lock-current-is-v2.3.0.md, brain-files-carry-no-secrets-or-contact-info.md, README.md
- packs\max\ (one-holder-for-the-alienpc-shell.md, production-defaults-st8-dynamic-vram.md, quality-stamp-before-derricks-eyes.md, scores-in-words-keep-is-derricks-go.md, lora-rules.md, settled-images.md, attached-still-is-the-cond.md, lock-length-and-beats-before-a-product-queue.md, fiction-and-cnc-follow-the-linked-canon.md)
- audits\2026-10-23-max-overcontrol-audit.md, audits\2026-10-23-fleet-community-audit.md
- canon\ (fleet canon: fiction-cond-lock.md, cnc-frame-block.md, compound-engineering.md, fleet-operating-kit.md, always-on-brief-vs-skills.md, max-i2v-prompt-improve-v1.md, etc.)
- skills\ (Max's AlienPc skills: alienpc-community-matrix-cell, alienpc-hardcore-i2v-director, alienpc-local-exec-lease, alienpc-local-video-ops, alienpc-max-movie-director, alienpc-stills-pose-edit-prompting, ref2va-prompt)
- community_hits\ (brain-staging files mentioning "community": fleet reviews 2026-10-09..10-23 incl. 2026-10-23-max-forge-direction-audit.md, 2026-10-17-forge-config-verify*.md, 2026-10-17-loop-stopped-short-audit.md, 2026-10-17-model-picks-audit.md; 60_reviews\2026-10-15-local-setup-research-audit.md; forge-bugfix-plan-audit3-h3-2026-10-15.md; flux2 matrix plan; skills live-2026-10-19 snapshot)

## Output format for plan.md
1. Header: date/time (run `Get-Date`), model, "PLAN MODE - nothing changed".
2. Top 10 root causes (one paragraph each, plain words).
3. Prioritized item table/list: ID, area, finding, evidence (path:line), community source, risk, verify step, priority (P0/P1/P2).
4. What is missing (information you needed and could not find).
5. Conflicts found between files (e.g. PROMPT.md vs AGENTS.md vs fix_plan vs standing rules vs community defaults).
6. Proposed order of one-at-a-time changes for after Fleet Reviewer's audit, each one published change.
7. List of files you read.
Keep plan.md under ~40 KB; it must be readable by Derrick.
