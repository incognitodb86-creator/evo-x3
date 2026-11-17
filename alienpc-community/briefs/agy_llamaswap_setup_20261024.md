# Antigravity (Flash High) brief: llama-swap + render path setup, Oct 24 2026 4:37 PM CT

Derrick, 4:36 PM CT (verbatim): "Eug, you need to have forge fix it self like wtf. Why hasn't it started or used lama swap? Use antigravity flash high to set everything up and ensure llama swap and what not is optimize and used"

## The problem
Forge (pi + ralph.ps1 in C:\Users\derek\5slock\ralph-community, model coding_swift15_iq3s served by llama-swap :8080) has staged 6 HC15 clips (C:\AI\community\runs\hc15_*) but rendered 0. Its reason (C:\AI\community\notes\needs_derrick.md row 13): its own LLM and ComfyUI (llama-swap entry comfyui_auto, run_graph_job.py through /comfyui/) share one GPU in an exclusive swap, so it won't queue a render mid-pass. It also treats the p7_budget caps as hard (Derrick left them editable = soft).

## Your job
1. First commit Forge's uncommitted work in ralph-community as-is ("Forge WIP before agy setup"). Read notes\plans\0.2-ca2.md (Forge's started audit plan) and fix_plan.md item 0.2 CA2.
2. Do the 0.2 CA2 community usage audit yourself now: for the Ralph loop + pi, llama-swap (swap groups, ttl, unload, healthCheck, the documented ComfyUI upstream guide https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md and llama-swap README/config docs), pi request timeouts, ComfyUI queueing, render, stitch: table of what we do now | community | URL | match. Switch every mismatch to the published community setting in the same pass. Write notes\ca2_usage_audit_20261024.md and commit.
3. Make the render path actually work from Forge's loop the community way (e.g. the loop queues the render through llama-swap's ComfyUI route and the LLM's next request waits for the swap back, with pi's documented timeout long enough; or whatever the llama-swap docs publish). Use only published community settings; no custom scripts or guards.
4. Prove it end to end: render HC15 clip 1 (C:\AI\community\runs\hc15_bd002_s51150001, its staged job) to mp4, with ffprobe showing 1344x768-class 16:9, ~15 s, audio track if the workflow has audio. Then render the other 5 staged clips. No time limit on GPU jobs; only stop if a job hard-fails twice. Make a contact sheet per clip (stills every second) next to each mp4.
5. Write a short how-it-works note into Forge's AGENTS.md (Forge owns that file; keep it short) so Forge renders through llama-swap itself on future passes. Mark needs_derrick row 13 resolved with a link to the audit.
6. Restart Forge's loop when done: Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\Users\derek\5slock\ralph-community\ralph.ps1','-Max','10' -WindowStyle Hidden
7. Write C:\AI\community\briefs\agy_llamaswap_setup_20261024_DONE.txt: what changed (each setting, old -> new, URL), commits, mp4 paths + ffprobe lines, contact sheet paths, anything not done and why.

## Hard limits (do not break)
- Secrets: never print, open or put API keys/tokens inline; never dump rclone config; never open Grok Imagine .json sidecars or the GMD prompt cache.
- Fictional adults only. comm.py adults-only check runs before every render. tests\test_p6_review.py must pass (21 tests) and is never edited (sha256 C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213).
- Never score explicit content with a vision judge.
- Archive, never delete. KEEP is only Derrick's.
- Do not touch C:\Apps\finance-app-rebuild, the Shoebox :443 chain, GMD, or Household's files.
- Community settings only, with a source URL for each change; nothing custom.