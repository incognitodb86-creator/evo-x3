# notes INDEX (folder -> purpose). Max2, U4, 2026-10-29. Keep under 60 lines. Derrick 11:55 CT: two roots, clear jobs (community way).

## Where is... (one hop)
- Clip judge (flags only, no KEEP): C:\AI\community\judge\README.md (prechecks.py = scene-cut + DINO/CLIP vs start image, CPU; vlm_judge.py = qwen3vl_judge per-check yes/no, json_schema)
- Prompt rules: C:\AI\community\skills\h3-prompting\SKILL.md (detail in its references\)
- Render settings + stock render path: C:\AI\community\skills\h3-hc-render\SKILL.md section 6 (default graph C:\AI\community\p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json)
- Start Forge: herdr agent "forge" (started at logon by C:\AI\director\scripts\pi_herdr_at_logon.ps1); loop by hand: C:\Users\derek\5slock\ralph-community\ralph.ps1 -Max 10
- Start Sydney (talk lane): C:\AI\community\talk\talk.ps1
- Loop files: C:\Users\derek\5slock\ralph-community\ (PROMPT.md, AGENTS.md, fix_plan.md, specs\, notes\, logs\ralph.log)
- Outputs: clips in C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\<tag>\; run dirs (request, status.log) in C:\Users\derek\5slock\runs\<run>\
- Archive (moved, never deleted): C:\AI\_archive\<date-reason>\MANIFEST.md; older batches in notes\_archive\

## C:\AI\community\notes (lasting knowledge: lessons, decisions, how-tos, audits; future QNAP brain)
- top level: DONE notes, plans, check scripts (*.py), actions.log (one line per action), progress.md
- _archive\: dated archive-only moves (each batch has MANIFEST.txt with sha8); nothing deleted
- audits\, review\, learnings\: audit reports, review notes, learnings
- web\: saved web pages (provenance-checked by check_web_saves)
- scenes\, hc_final_frames\, hc15_audit\, bq1d_frames\, face_r4f\, face_r4g2\: render review frames and audits
- box-mirror\: copies of box files mirrored to AlienPc
- pi_config_snapshots\, briefs-snapshots-2026-10-25\: config and brief snapshots
- card_rebuild_facts\, top_card_vl_facts\: vision fact extracts
- gmd_ext_20261024\: GMD extension notes

## C:\Users\derek\5slock\ralph-community\notes (loop working notes: progress, plan, handoffs, DONE notes, verdicts)
- top level: loop DONE notes, handoffs, progress.md, loop scripts
- _archive\: dated archive-only moves (MANIFEST.txt)
- p15_*, p15v2_*: p15 prompts, verdicts, captions, review images
- bk26_*: bk26 prompts, asks, verdicts
- policy_snapshots\, rules-snapshots-2026-10-25\, stock-pi-2026-10-25\: rule and config snapshots
- handoff-src\, candidates\, vis\, learnings\, .forge11\: handoff sources, candidates, visuals, learnings, permission test fixtures
