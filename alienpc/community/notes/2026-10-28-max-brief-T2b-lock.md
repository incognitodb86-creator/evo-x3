# Max brief: T2b = T2 + consistency lock (2026-10-28 7:53 PM CT)

Derrick's go (7:50 PM CT): "Lets run it again with this to see if it makes any difference" + the consistency-lock block. One change from T2 only: the prompt.

1. New dir C:\AI\community\runs\terrace_dom_q5biglock_20261028_s51083009. Copy T2's build_graph.py from runs\terrace_dom_q5big_20261028_s51083008, SRC = T2's request.api.json.
2. Prompt = the exact text of C:\AI\community\notes\2026-10-28-consistency-lock-block.txt (Derrick's words, verbatim), then one blank line, then T2's prompt_seg0.txt unchanged. Update the builder's prompt-bytes assert to the new prompt, and the diff check to allow exactly the prompt + save.filename_prefix (community/terrace_dom_q5biglock_20261028_s51083009/terrace_dom_q5biglock_20261028_s51083009). Everything else identical to T2 (seed 51083002, 512x896 x1.5, ag0/ag1, ref max, beta/3/0.4, chunking, audio s0_sep:1).
3. Adults-only guard (comm.guard_ok) on the new prompt before render. Render in ONE GPU window: gpu_window.ps1 -Dir <dir> -Tag terrace_dom_q5biglock_20261028_s51083009 -Frames 243 -Timeout 3600.
4. finalize_encode.py, no RTX. Upload raw + final to QNAP /pi-drop/, verify sizes.
5. Write notes/2026-10-28-T2b-lock-DONE.md (seconds, sizes, the 2 changed widget values). Then stop.
PowerShell tool only.