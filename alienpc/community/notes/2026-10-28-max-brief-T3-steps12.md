# Max brief: T3 pass-1 steps 12 (2026-10-28 8:25 PM CT)

Derrick's go: "Ralph loop queue it all" (8:16 PM CT). Plan: brain 40_projects/max-fix-tests/plans/2026-10-28-2015-terrace-community-settings-test-plan.md, arm T3. One change from B2 only.

1. New dir C:\AI\community\runs\terrace_dom_q5steps12_20261028_s51083010. Copy B2's build_graph.py from runs\terrace_dom_q5guide_20261028_s51083007, SRC = B2's request.api.json.
2. Change exactly: s0_sched.steps 8 -> 12; save.filename_prefix community/terrace_dom_q5steps12_20261028_s51083010/terrace_dom_q5steps12_20261028_s51083010. Everything else unchanged (c0 384x672 length 243, ag0/ag1 kept, shift 12/3, euler, s0_sched simple denoise 1.0, VSA keep 10, lsu3 x2.0, p2sched beta/3/0.4, still community/TERRACE2_768x1344.png, seed 51083002, B2 prompt bytes). Write graph_diff.txt in the run dir vs B2: must show only those two widgets.
3. comm.guard_ok must pass before render (adults-only guard on). Render in ONE GPU window: gpu_window.ps1 -Dir <dir> -Tag terrace_dom_q5steps12_20261028_s51083010 -Frames 243 -Timeout 3600 (gpu_guard IDLE first).
4. finalize_encode.py with no RTX arg (native crf-18). Upload raw + final to QNAP /pi-drop/ and verify sizes.
5. Write notes/2026-10-28-T3-DONE.md: every widget change, render seconds, file sizes, canvas check. Then stop.
PowerShell tool only.
