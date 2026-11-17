# Argon Medium review-and-improve brief: pi / llama-swap / ComfyUI / ralph / Forge (2026-10-26) — FINAL

Status: FINAL, approved by Derrick 9:39 AM CT Oct 26 ("Launch Argon medium, and have Forge pause after its current pass."). Launched by Max Architect 2 under the AlienPc lease.

You are Antigravity on Gemini 4 Argon Medium, the REVIEWER + IMPLEMENTER (Derrick, 9:21 AM CT Oct 26: "I want to put this on antigravity argon medium and have it improve and optimize pi/llama swap comfy ui ect. double check for errors missing information potential issues and debug. ensuring best practices and community guidance is met"). This is ONE run. Do the to-do items below in order, one change at a time, then stop. Do not ask questions; if an item is blocked or needs Derrick, log why in progress.md and move to the next item.

Working folder (to create on AlienPc when approved): C:\AI\community\briefs\argon_medium_20261026\
- Prior run (read first): C:\AI\community\briefs\argon_audit_20261025\ — plan_v3.md (sha C0D3DC42...), flash_impl_brief.md + ADDENDUM_0705.md, progress.md, final_review.md, ab_test_res_vs_euler.md, switchyard_callers.md, discord_bridge_status.md.
- Fleet Reviewer audit: C:\AI\community\briefs\argon_audit_20261025\context\fleet_audit_r2.md (box copy: brain-staging/60_reviews/fleet/2026-10-25-argon-forge-plan-audit.md), round 1 (A-1..A-10, K-1, K-2, G-1) and round 2 (N2-1..N2-11).
- Protected-file hashes taken before this run: pre_hashes.txt in the working folder (written by Max Architect 2 before launch).
- Progress log you keep: progress.md (working folder). Append one entry per action: time CT, step ID, files, commit hash, verify command + result, rollback. Read-only checks get entries too.

## Usage
Pre-launch `agy -p "/usage"` at 9:46 AM CT Oct 26: Gemini 4 Argon weekly limit 47% remaining (resets Oct 31 12:57 PM CT); Gemini models weekly 76% (Oct 31 2:35 PM CT), five-hour 63% (today 12:02 PM CT); Claude/GPT weekly 50%, five-hour 100%. Do not run /usage or other slash commands yourself.

## Forge during this run
Forge is PAUSED by Max Architect 2 for this run; do not resume it. Derrick 9:44 AM CT: "why dont we stop it now" — Max Architect 2 disabled \ForgeRalphLoop and stopped ralph PID 2700 + pi PID 5072 (taskkill /T /F) at 9:45 AM CT, mid iter 1 of 10 (started 9:00). No GPU lock left (C:\AI\locks empty). Log: C:\AI\community\briefs\argon_audit_20261025\forge_pause.log; marker forge_paused.txt in this folder. Never enable or start \ForgeRalphLoop or ralph.ps1. Item M8 may edit fix_plan.md text-only under its rules; never the MAX block.

## Derrick's words (quote them as his answers; they are not "rules")
- 9:21 AM Oct 26: "check with max to see what changes we need to make still and how forge did. Iw ant to put this on antigravity argon medium and have it improve and optimize pi/llama swap comfy ui ect. double check for errors missing information potential issues and debug. ensuring best practices and communtiy gudiance is met"
- 7:08 AM Oct 26: "Yes, have Forge rebuild the GI063 card from the uncensored captions only"
- 8:23 AM Oct 26: "yea it needs to have the vision model redo them"
- 6:00 AM Oct 26: "Don't waste usage"
- 5:59 AM Oct 26: "Have antigravity review forge and llama swap and stuff and comfy make sure they are setup and config correctly"
- 10:15 PM Oct 25: "I don't remember those kitchen attention? I want best practices and community guidance? Geared on what works best on my setup"
- 10:17 PM Oct 25: "Community adults only. I want community fucking swttings"
- 6:48 PM Oct 25: "Sort out the Comfy Kitchen attention conflict"; "Go back to Euler, 5-second clips and 350–500 word prompts"

## HARD LIMITS (any breach = stop the item, log it, do not work around it)
1. Community/stock first. Start from the published default (official docs, README, config example, or a cited community thread). One published change at a time, own commit, verify, rollback line. No new controls, daemons, watchers or scripts unless needed and justified in progress.md with the source link.
2. Youth guard: fictional adults only. comm.py's adults-only check (guard_ok) runs before every render and is NEVER loosened or bypassed; you may only widen its scope. p6_review.guard_check is never edited. No vision judge on rendered explicit output; vision never decides identity or age. No celebrity/real-person LoRAs.
3. Protected files never change: C:\AI\community\scripts\tests\test_p6_review.py (sha C3C2E169...), mcp.json, pi-permissions.jsonc (C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc). Verify their sha256 against pre_hashes.txt at start and end.
4. Secrets: never print, cat, copy or put in a command or file any token, key, password, rclone config, auth.json, .env, or credential file. Write the tailnet host as <tailnet>. Never open Grok Imagine .json sidecars or the GMD prompt cache.
5. No deletes anywhere. Archive = copy or move into a dated archive folder. No git push, no reset --hard, no force anything.
6. GI063 stays on render hold. Do not render GI063 (any seed) and do not queue it. Never touch D:\Apps\finance-app* or any UniFi folder.
7. GPU lock: anything using the GPU runs only when `powershell -NoProfile -File C:\AI\director\scripts\gpu_guard.ps1` returns rc 0, through run_graph_job.py and the gpu-render.lock path. Never kill or restart ComfyUI mid-render. Never interrupt a running Forge pass.
8. No quota spend beyond this run: no paid APIs, no other agent launches, no downloads of models. Renders only where a to-do item names one (fixed seed, test only).
9. KEEP decisions are Derrick's. Where a test would change a KEEP, record the result and leave the default as is.
10. 128K context (131072) stays on every model that has it.
11. One change per commit; commit message starts with the step ID ("M3: ..."). Commit in the repo the file belongs to (C:\AI\community, C:\Users\derek\5slock\ralph-community, C:\AI\director). Files outside git: back up as <file>.bak-20261026m-<stepid> first and log it.
12. Long commands in the background; poll their log; never block a shell over ~10 minutes.
13. Do not edit the MAX block at the top of fix_plan.md. Report what it lacks (item M7) for Max to fix.

## To-do list (in this order; step IDs M0..M14)

0. **M0: pre-flight (read-only).** Hash protected files vs pre_hashes.txt. Record: ralph/pi PIDs and pass number, open count from ralph.log, `git log --since 08:50` in ralph-community, community, director; llama-swap /health, /running, /v1/models; ComfyUI state via llama-swap (/running only — do not hit /comfyui unless gpu_guard IDLE, it loads the model); GPU lock files under C:\AI\locks; nvidia-smi name (it is an RTX 5070 Ti 16 GB). Log the Forge pause state per the placeholder above.

1. **M1: re-audit the prior final_review.md and fix its errors (doc fixes only, in a new final_review section, never rewrite history).**
   (c) It says "RTX 4080"/"NVIDIA RTX 4080" (also in ab_test_res_vs_euler.md); the card is an RTX 5070 Ti 16 GB (nvidia-smi). It cites https://github.com/comfyanonymous/ComfyUI as the "MiniMax H3 Docs"; find and cite the real H3 doc/workflow source (the model card or ComfyUI template/blog page that states the attention default) or mark UNVERIFIED.
   (n) It scores Switchyard and S7-skills PASS; both are FAIL (see M2, M3). Re-score every row against a cited source with evidence you ran today.

2. **M2: REPORT-ONLY (options and evidence, no change). (a) archived director.switchyard still imported. Present options, DO NOT pick or implement.** director cli.py, queue.py, config.py and comfy_client.py still import director.switchyard (moved to C:\AI\_archive\20261026_switchyard\ in director 04b7f9e), so `python -c "import director.cli"` fails, and discord_bridge /queue commands may break (the running bridge, PIDs 26972→27152→26876→26896 since Oct 23, loaded the old code and will fail on restart). Read-only: list every import site (path:line), run the import in the director venv without starting anything, and check which discord_bridge commands reach those modules. Write three options with effort, risk and rollback: (1) repoint to llama-swap (:8080) + ComfyUI's own /prompt queue via comm.py/run_graph_job.py (guard intact); (2) retire the dependent commands (archive, not delete); (3) restore director.switchyard from the archive. Log as NEEDS DERRICK.

3. **M3: (b) S7-skills disabled nonexistent names. The ONLY change allowed: correct the 5 wrong `compound-engineering-plugin:*` entries in settings.json (backup first, logged) and name the real loaded skills. Any other skills change (disabling a real skill) is REPORT-ONLY: propose, do not apply.** settings.json disables `compound-engineering-plugin:brainstorming`, `:content-creator`, `:social-media`, `:seo-analyzer`, `:copywriting`. The installed compound-engineering-plugin skills are named ce-* (ce-brainstorm, ce-promote, ce-product-pulse, ce-proof, ce-test-xcode, ...; plus lfg, wtf, council-mode, pi-subagents). Confirm the real loaded names from pi's own skill listing (pi docs on settings `skills` filters), check whether the five filters matched anything, and propose a list of real names to disable with one-line reasons. Note: the brief said 4 nonexistent; the live file has 5 entries — count which actually match.

4. **M4: (d) fake rc=124 line in ralph.log.** logs\ralph.log lines ~802-804 (2026-10-26T08:05:30 "iter 1 : ITERATION_TIMEOUT ... PI_NONZERO rc=124 ... open=53") came from the S10-timeout dry test (`-IterationTimeoutSec 2 -CommandOverride ...`), not a real Forge pass. Do not edit or strip the line. Propose (and, if stock-compatible, add in one commit) a way for test runs to write to a separate log (e.g. -LogPath for -CommandOverride runs) so dry tests never pollute the production log; append a dated annotation line only if ralph.ps1 has a documented annotate path. Also: plan_v3 S12-1 (copy ralph.log then strip NUL bytes) was never executed — log it as open.

5. **M5: (e) pi-mobile 7878 port-bind risk.** \pi-mobile task keeps pi_mobile_hub.cjs (node PID 21748) listening on 127.0.0.1:7878. The npm:pi-mobile package loaded as a pi extension in each Forge pass may also try to bind 7878 (EADDRINUSE). Read the pi-mobile package docs/source for its port setting and documented hub/standalone mode; grep the latest logs\iter-*.log for 7878/EADDRINUSE (p: check the next pass logs); state whether a conflict happens and which component the community setup expects to own the port. Propose the stock fix; implement only if it is a documented setting change and one commit. Note the prior Tailscale check curled from AlienPc itself, not another device (audit K-2/N2-10 part 3): flag it.

6. **M6: (f) S10 timeout sized from one render.** 4,500 s = longest render 3,048 s + 1,200 s queue, but a pass can run several renders. From p7\jobs\*.result.json, runs\*\status.log and logs\iter-*.log, measure renders per pass (max and p90) and per-pass wall time; recompute per audit N2-7 (renders per pass × longest render + queue). Compare with frankbria/ralph-claude-code timeout guidance. Propose the value; change it only in one commit with the numbers in progress.md.

7. **M7: (g)/(l) Oct 25 lines dropped from the MAX block. Report only; Max edits the block.** Commit ad0a2d4 (ralph-community, local/unpushed, 08:59 CT) replaced the MAX block and removed the Oct 25 lines, including: the earlier GI063 hold reason (needs_derrick.md row 21: Forge's own caption reads the start image as non-consensual), Derrick's 7:49 AM GI046 orc feedback, the 3:56 AM render/caption choice, the 7:49–8:02 AM Strata refusal-vector pick, 10:46 AM, 11:10 AM, 12:46 PM, 1:55 PM, 4:51 PM, 6:41–6:48 PM picks, 7:12 PM and 7:56 PM lines. Use `git -C ralph-community show ad0a2d4 -- fix_plan.md`. List which still matter as open work vs which are done (with receipts), so Max can restore them below the block.

8. **M8: (k) repeated-ID cleanup incomplete.** fix_plan.md ticked rows still repeat IDs (live lines incl. "**4** 4 4 4 4 4 4", "**1.4a** 1.4a 1.4a ...", 1.4d, 2.1b, 2.1c, 2.1a, 2.7b, 3.1a). Also duplicate rows (E5 appears twice). Fix only if Forge is paused (placeholder) — one commit "M8: ...", text-only, archive copy first, open count unchanged before/after. Otherwise list them for Forge.

9. **M9: REPORT-ONLY (options and evidence, no change, no render). (h) Euler vs res_multistep is undecided; (j) A/B confound.** Euler is meant to be the default (Derrick 6:48 PM). Facts read today: the S8 "pytorch attention" check render (runs\ali163_s8_pytorch_s51150011) used sampler_name "res_multistep", and the S9 render (runs\ali163_s9_euler_s51150011, its own folder, mp4 present) used "euler"; both pytorch attention, noise_seed 51150001. So the graph template's default may still be res_multistep, not Euler — verify comm.py/graph defaults and E5 receipt. Old Max reported the Euler clip saved as runs\ali163_s8_pytorch_s51150011\ali163_s8_pytorch_s51150011_00002_.mp4 — that file was NOT found on 10-26 9:30 CT; confirm. No render and no default change in this run. Leave the decision to Derrick.

10. **M10: (i) Comfy Kitchen attention test idea (TEST ONLY).** Reddit r/comfyui H3 thread https://www.reddit.com/r/comfyui/comments/1xfrdh3/ reports Comfy Kitchen attention ~2x faster than PyTorch attention. Read the thread and the ComfyUI/Comfy Kitchen docs for compatibility with the int8 (comfy_quant, no convrot) checkpoint. If gpu_guard IDLE and the run is approved, ONE fixed-seed render (seed 51150011, euler, identical graph, attention the only change), technical signals only (rc, frames, black/frozen, runtime, bytes). Default stays pytorch attention; result is a card for Derrick.

11. **M11: (m) forgesafe lines.** The archive C:\Users\derek\5slock\notes\AGENTS.20261026.archived.md (60 lines, "forgesafe", Oct 20) has the shell rules (bash tool = Git Bash; "Denied only: secrets (.env*, rclone, keys/tokens, credential stores), edits to scripts/comm.py + its test, ComfyUI restart mid-render"; prefer read/grep tools; deny-class notes). ralph-community\AGENTS.md (39 lines) has the hard lines and shell names but NOT the "Denied only" list. Report which archived rules are still enforced elsewhere (pi-permissions.jsonc — read only, do not edit) and propose the minimal lines to carry over (AGENTS.md stays under 40 lines per its own header).

12. **M12: line-by-line check of plan_v3.md against the Fleet Reviewer audit (context\fleet_audit_r2.md), to find any audit fix plan_v3 dropped.** Go line by line through every audit finding and fix-list entry (A-1..A-10, K-1, K-2, G-1, §8 checks 1–10, N2-1..N2-11) and mark in progress.md: applied in plan_v3 + executed (commit) / applied but not executed / dropped. Box pre-check found these gaps — confirm each:
    - N2-7 "renders per pass" missing from plan_v3 (timeout from one render) → M6.
    - A-7 "vision never decides identity or age" and "no celebrity/real-person LoRAs" not in plan_v3 (only in the brief's hard limits).
    - K-2/N2-10 part 3: HTTPS check "from another device" missing; S-pimobile curled from AlienPc.
    - Fix #5: ALI-162 items 1 and 5 status never checked.
    - §8 #9: Switchyard 91/91 tests / bf76b64 fast-forward never answered (superseded by retirement, but the import breakage in M2 shows the caller census missed director's own modules).
    - A-10/A-4: no "Risk:" lines in plan_v3 steps.
    - S12-1 ralph.log NUL strip: in plan_v3, not executed.
    - N2-8: "name the Step 10 skills" — named, but wrong names (M3).
    - R2-7 #6: "Max updates his pack line" for Oct 9 KEEP superseded — not done (item o; brain-staging/10_packs/max/production-defaults-st8-dynamic-vram.md line 15 still says ck-attention KEEP). Flag for Max only; you cannot edit box files.

13. **M13: component review vs official docs and community guidance (cite links: official page or official repo only, else UNVERIFIED).** For each, read the live config, compare with the source, log mismatches, fix only stock/documented ones one at a time:
    - pi: C:\Users\derek\.pi\agent\settings.json, models.json (vl_judge, qwen3vl_judge entries), C:\AI\director\config\pi\settings.json, compaction/retry/httpIdleTimeoutMs, packages list. Source: pi coding agent docs (https://www.npmjs.com/package/@earendil-works/pi-coding-agent and its repo docs: settings, models, skills, cli-integration / --print exit codes).
    - llama-swap: C:\AI\director\config\llama-swap.yaml — groups (exclusive), ttl, unloadTimeout vs comfy_graceful_stop.ps1, -watch-config (the Oct 25 10:22 PM failure was a config reload killing the running model; assess whether -watch-config should stay on during passes), aliases, vision mmproj, 128K. Source: https://github.com/mostlygeek/llama-swap (README, config.example.yaml, wiki).
    - ComfyUI: launch argv (--disable-async-offload --disable-pinned-memory), attention, queue, custom nodes, workflows. Sources: https://github.com/comfyanonymous/ComfyUI (README, `python main.py --help`/cli_args.py), https://docs.comfy.org.
    - ralph loop: ralph.ps1 (circuit breaker, -IterationTimeoutSec, stuck=3, log encoding), PROMPT.md, AGENTS.md, fix_plan.md shape. Sources: https://github.com/frankbria/ralph-claude-code, https://ghuntley.com/ralph/.
    - Forge scheduled tasks (\ForgeRalphLoop every 10 min: LastTaskResult 0x800710E0 "already running" is expected; check the instance policy is IgnoreNew), \pi-mobile, and the oddly named "\Switchyard llama-swap" task (it launches llama-swap; name only — report, don't rename).
    - Forge's own 09:12 commit 2554abc reports "scene_card_gate selftest BROKEN 1 silent seed": check and report.

14. **M14: final review.** The GPU is an NVIDIA GeForce RTX 5070 Ti 16 GB (nvidia-smi); name it that way everywhere. Every docs citation must be the official page or official repo (project README, official docs site, model card); never a guessed or unrelated URL; if you cannot find the official source, write UNVERIFIED instead of a link. Write final_review.md in the working folder: table Component | Check | Source link | PASS/FAIL | Note, one row per check, evidence you ran this run. Include pi, llama-swap, ComfyUI, ralph loop, Forge config, youth guard (pytest test_p6_review.py test_guard_scope.py + sha), GI063 not rendered (no runs\*gi063* newer than 2026-10-25 11:28 AM). FAIL honestly; no PASS without a source and a check.

15. **M15: interrupted pass 1 review (keep or revert, no deletes; report first, act only on clear cases with the reason logged).** Forge was stopped at 9:45 AM CT mid iter 1 (09:00 start), while working its CARD-VL2 row (rebuild the GI063/GI046 cards from fresh vl_judge captions; no render). State at the stop:
    - ralph-community: `git status` clean, HEAD 2554abc (09:12 CARD-VL2 row + plan + receipt); logs\iter-20261026-01.tmp.log is 0 bytes (pi --print output lost; the pi session JSONL in ralph-community\sessions is the record).
    - C:\AI\community UNCOMMITTED from the pass (09:21–09:44): modified `notes/top_card_vl_build.py` (09:22); untracked `notes/card_vl2_author.py` (09:44:35, possibly half-written), `notes/card_vl2_build.py` (09:43), `notes/card_vl2_patch_base.py`, `notes/_splice.py`, `notes/_splice2.py`, `notes/_entry_record_line.txt`, `notes/card_rebuild_results.json`, `notes/card_rebuild_facts/GI046.json` + `GI063.json` (09:44:37), `notes/scenes/raw/GI046_vl2_[A|B|C].txt` and `GI063_vl2_[A|B|C].txt` (09:26, the new vl_judge captions), `notes/ali320_prompt_shape.{py,json}`. Also modified `briefs/agy_monitor.out.txt` (owner unknown).
    - C:\AI\director has many modified tracked files (AGENTS.md, GEMINI.md, config/director*.yaml, docs/...) not touched since 09:00 (older, owner unknown): list them with dates, report only.
    For each: py_compile / json.tool, compare with the CARD-VL2 receipt plan, and record keep / revert / leave-for-Forge in progress.md. Never delete; never touch the GI063 render hold; no captioning reruns unless gpu_guard IDLE and logged.

## Scope notes (everything is in this brief; no mid-run addenda expected)
- REPORT-ONLY items: M2 (director.cli repoint/retire/restore), M9 (Euler vs res_multistep), any skills change beyond M3's 5-entry correction, M7 (MAX block), M11 (forgesafe lines). Options + evidence only.
- No plan-first pass: implement mode (--mode auto), items in order.

## End of run
Last lines of progress.md: summary table (step ID | commit | verify | result), the list of NEEDS DERRICK items, sha256 of pre/post protected files and of final_review.md. Do not resume or pause Forge unless the placeholder above says so. Do not run /usage.

## Decisions Derrick still owes (do not decide these; list them in final_review.md)
1. Sampler: Euler (default, 6:48 PM pick) or res_multistep, after M9 confirms what the default really is.
2. director.switchyard imports (M2): repoint to llama-swap + ComfyUI queue, retire the commands, or restore.
3. GI063 render go (needs_derrick.md row 34a; row 21 consent question from Oct 25).
4. Forge paused or running during this Argon Medium run (placeholder above).
5. Which real pi skills to disable (M3 list).
6. pi-mobile: who owns port 7878 (hub task vs the pi extension) and QR pairing (M5).
(Max to confirm this is the same six he tracks; also pending from earlier: Comfy Kitchen re-test card from M10, budget caps question from audit A-6.)

## Launch (run by Max Architect 2 after Derrick's 9:39 AM CT go)
Model id: `gemini-4-argon-medium`, confirmed 9:42 AM CT Oct 26 by `agy models` ("gemini-4-argon-medium	Gemini 4 Argon (Medium)").
Run script (copy of flash_impl_run.ps1's shape) C:\AI\community\briefs\argon_medium_20261026\argon_medium_run.ps1:
```
Set-Location C:\AI
$b='C:\AI\community\briefs\argon_medium_20261026'
"[$(Get-Date -Format o)] argon_medium start pid=$PID" | Out-File -Append "$b\argon_medium.log"
$dirs = @('C:\AI','C:\Users\derek\5slock','C:\Users\derek\.pi','C:\Users\derek\HardcoreNSFW-TestRuntime')   # no D:\AI\director (absent), no finance/UniFi paths
$add = foreach($d in $dirs){ '--add-dir'; $d }
& 'C:\Users\derek\AppData\Local\agy\bin\agy.exe' -p "Read and carry out the brief at C:\AI\community\briefs\argon_medium_20261026\argon_medium_brief.md. Do the to-do items M0..M14 in order, one change per commit with its step ID, logging each in progress.md in that folder. Obey every HARD LIMIT in the brief." --model gemini-4-argon-medium --mode auto --dangerously-skip-permissions @add --print-timeout 0 --log-file "$b\argon_medium.agy.log" *> "$b\argon_medium_stdout.md"
"[$(Get-Date -Format o)] argon_medium end exit=$LASTEXITCODE" | Out-File -Append "$b\argon_medium.log"
powershell -NoProfile -ExecutionPolicy Bypass -File "$b\hashes_m.ps1" -Out post_hashes.txt | Out-Null
```
Started hidden: `Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File','C:\AI\community\briefs\argon_medium_20261026\argon_medium_run.ps1' -WindowStyle Hidden -PassThru` (record the PID).
