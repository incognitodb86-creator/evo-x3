# Max brief: T2 bigger first pass (2026-10-28 7:23 PM CT)

Derrick's go: "Lets do t2" (7:21 PM CT). Source: notes/2026-10-28-terrace-ab-handoff.md, section T2. One change from B2 only.

1. New dir C:\AI\community\runs\terrace_dom_q5big_20261028_s51083008. Copy B2's build_graph.py from runs\terrace_dom_q5guide_20261028_s51083007, SRC = B2's request.api.json.
2. Change exactly: c0.width 512, c0.height 896; lsu3 "scale by multiplier" 1.5; save.filename_prefix community/terrace_dom_q5big_20261028_s51083008/terrace_dom_q5big_20261028_s51083008. Everything else unchanged (ag0/ag1 kept, ref_image_size max, seed 51083002, prompt bytes, beta/3/0.4 pass 2, chunking true, audio from s0_sep:1). Final canvas must be exactly 768x1344.
3. Build, then render in ONE GPU window: gpu_window.ps1 -Dir <dir> -Tag terrace_dom_q5big_20261028_s51083008 -Frames 243 -Timeout 3600 (gpu_guard IDLE first; adults-only guard stays on).
4. finalize_encode.py with no RTX arg (native crf-18). Upload raw + final to QNAP /pi-drop/ and verify sizes.
5. Write notes/2026-10-28-T2-bigpass-DONE.md: render seconds, file sizes, canvas check. Then stop; no follow-up renders.
PowerShell tool only.