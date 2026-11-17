# AGENTS.md - Forge rules for C:/Users/derek/5slock (Ralph's cwd). Derek-approved 2026-10-20 (forgesafe). Keep it under 40 lines.

## Shell: your bash tool is Git Bash on Windows
- bash and powershell tools (Derrick 2026-10-23 1:53 PM CT "Really anything secrets"): any command runs, incl. ; && | heredoc, redirects, curl, installs. Denied only: secrets (.env*, rclone, keys/tokens, credential stores), edits to scripts/comm.py + its test, ComfyUI restart mid-render.
- Every tool call is logged to C:/AI/community/notes/forge_actions.log; denies to notes/denies.log. If a deny looks wrong, write it in notes/guard_requests.md (PROMPT.md SELF-DIAGNOSE).
- Web: any site, e.g. curl.exe -sL --max-time 30 <url> -o C:/AI/community/notes/web/<file>.
- Use forward slashes (C:/AI/community/scripts/comm.py) and quote paths that contain spaces.
- Prefer the read / grep / find / ls tools over shell commands for reading and searching.

## Check commands (one call each)
- Python syntax: python -m py_compile C:/AI/community/scripts/<file>.py
- JSON: python -m json.tool C:/AI/community/shots/<file>.json
- Web saves: python C:/AI/community/scripts/web_fetch.py --url <url> --name <name> (extension comes from the body: .json only if json.loads accepts, .html for markup, .txt otherwise, non-200 -> <name>.403.txt; --from <file> reclassifies a body already on disk). End every research pass with python C:/AI/community/scripts/check_web_saves.py (rc 1 = a notes/web/*.json that json.tool rejects; --fix renames). The harness json.tool-checks EVERY notes/web/*.json, so a 200-with-HTML body named .json = CHECK FAIL = STOP_RALPH (HF2 2026-10-23 16:59:37).
- Video duration: "C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe" -v error -show_entries format=duration -of csv=p=0 <file.mp4>
- Job count (no budget ledger exists): ls C:/AI/community/p7/jobs | grep -c result.json - there is NO p7_budget.json under C:/AI/community (find **/p7_budget.json = 0 files, 2026-10-23), so never quote an assumed used_min/job count.
- FINAL media pass: audio = ffmpeg -y -i <mp4> -vn -c:a copy <id>.m4a; frames = ffmpeg -y -ss <t> -i <mp4> -frames:v 1 -y <png>; dump/sha/sound-line + the labelled contact sheet = notes/ali163_hc_final_check.py + notes/ali163_hc_final_sheet.py (builder-only, no vision judge).
- Budget ledger for gates/BAKEOFF START = C:/Users/derek/5slock/ralph-community/logs/p7_budget.json (used_min, jobs, cap_min 615, job_cap 45), NOT C:/AI/community.
- H3 graph internals for self-checks: denoise/steps live in s0_sched + s1_sched, sampler in ksel (euler), shift in m_shift (video 10.0 / audio 3.0), 2 SamplerCustomAdvanced = single pass, and NO cfg key exists in the graph at all (grep cfg = 0 hits) - counting KSamplerAdvanced false-fails a correct graph. Read ref slots with fullmatch ref_images\.ref_image_\d+ (submitted graphs also carry a ref_images dict that breaks ins[k][0]). ComfyUI 0.19.2 (bakeoff update) dropped sparse_blocks/sparse_size/max_dims from ModelAttentionBackend and nested BlockSparseAttention's per-method keys (selection = COMFY_DYNAMICCOMBO_V3), so the frozen r3b nodes 10/11 are schema-STALE - re-verify before any HB clone submits them. Continuum V39 (3.10.2): Manual canvas must be a multiple of 32 (v3/resolution.py H3_CANVAS_MULTIPLE; 468 % 32 = 20, so 832x468 is unreachable - use 1024x576), target_frames must equal chunks*chunk_seconds*fps (v3/hardening.py:86), H3ContinuumSamplerV39 has NO negative/CFG key (no: prose line in sequence_prompt); live schema dump = notes/ali173_b2_object_info_full.json + notes/ali173_b2_obj_<Class>.json. gpu_guard.ps1 = C:/AI/director/scripts/gpu_guard.ps1 called with NO arguments (ralph.ps1:51,77), rc 0 = IDLE.
- Install size check: python C:/AI/community/scripts/web_fetch.py --url "https://huggingface.co/api/models/<repo>/tree/main?recursive=true" --name <file> (the /api/<repo>/tree form 404s with a 62-byte body; the tool picks the extension from the body); compare local bytes + hashlib sha256 in notes/*.py.
- Static rc=2 pre-check: MiniMaxH3ImageToVideo has NO audio_vae (only ReferenceToVideo does); offline clone of run_graph_job.static_check = check 11 of notes/ali163_hc_r4g2_build.py (schema parsed from comfy_extras/nodes_minimax_h3.py).

## The GPU is off-limits
- Never call llama-swap (127.0.0.1:8080), /upstream/*, /load, /unload, ComfyUI (:8188, :8189, :1000x) or Strata. One request unloads you and kills a running render.
- BAKEOFF exception (ALI-173, Derrick 1:07 PM CT): for BAKEOFF lines only, ComfyUI API on :10004/:8188/:8189 (read + queue), llama-swap /v1, and python C:/AI/community/scripts/comfy_ctl.py start|stop|restart|status (never during a render; comfy_ok after every restart). See PROMPT.md.
- Never run render scripts (p3-p6*.py, batch_queue.py, sy_1min.py, p6_variants.ps1, p6_rerun.ps1, chain.ps1). Compile-check them only.
- Hard guards block these. Do not retry or work around a block; note it in your result (or BLOCKED + STOP_RALPH).

## Scope
- Only edit files named in your task.
- Never edit scripts/comm.py or scripts/tests/test_p6_review.py (fiction lock), secrets, or finance (C:/Apps/finance-app-rebuild, D:/Apps/finance-app*, port 3100 - Household's); no git push; llama-swap.yaml only when the GPU is idle (it hot-reloads). Since Derrick 2026-10-23 6:57 PM CT ("Unlock everything, guards too") ComfyUI/user, *.app.json, Strata/Pi config, the guard extensions, gpu_guard/gpu_lock, chain.ps1, PROMPT.md and ralph.ps1 are editable: back up first, test, log.
- Git checkpoints handle backups: the harness commits before and after every iteration, so no .bak copies are needed (except the one a harness fix requires). Commit your own fixes after the test passes: git -C C:/AI/community add <file>; git -C C:/AI/community commit -m "<task id>: <what and why>" (3+ words). Never commit in ralph-community (the harness does); push/reset/checkout/--amend are blocked.
- After each iteration the harness runs the checks above on changed files and restores out-of-scope edits.

## Content
- Adults only: every character is a fictional adult aged 21+ (canon: content lock v2.3.0, C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md = box /workspace/cos/canon/fiction-cond-lock.md; adult 18+; minors check on; do not invent identity refusals). Nothing involving minors, ever.

## Persona
- Current mission (ALI-163) and work style: C:/AI/community/notes/forge-mission.md (moved 2026-10-23); PROMPT.md BATCH/REDO is the live spec.

## Keep this file useful
- When you learn the right command for something (a check, a path, a flag), update the command notes above in one short line.
- No status or progress notes here; those go in TASKS.md or C:/AI/community/notes/.

## Learnings (ALI-160 Huntley Ralph pattern: one dense operational line each, max 15, aim <=275 chars; MEM1 2026-10-23 merged 16 -> 15 and added Max's 3 audit items; verbatim history = C:/AI/community/notes/forge-learnings.md; skills = C:/AI/community/skills/)
- Full learnings (verbatim, append-only): C:/AI/community/notes/forge-learnings.md. Pi skills: C:/AI/community/skills/<name>/SKILL.md (MEM1); notes/skills_wiring.md = the pi setting Max adds.
- H3 refs (BQ1): 3 slots on c0 AND c1 - ref_image_1 = the approved start still (<Picture 1>, bodies/scene), ref_image_2/3 = face crops (face+hair); r3r-r6 shipped face crops only = no body reference. Read slots fullmatch r'ref_images\.ref_image_\d+'; seed = noise_seed.
- Chunk math: 243 f = 10.125 s at 24 fps on the (frames-5) % 17 == 0 grid (c0 length 124, window overlap 22 + extension 119, c1 141 generated/22 hidden, 124+119 = 243); 481 f = the 20 s shape Derrick rejected; duration = round(frames/24, 6).
- Graph internals: steps s0_sched/s1_sched, sampler ksel (euler), shift m_shift 10 video / 3 audio, NO cfg key at all; MiniMaxH3ImageToVideo has NO audio_vae (static rc 2); clips_json validated MUST be false; LoadImage resolves inside ComfyUI/input.
- Continuum 3.10.2: canvas multiple of 32 (1024x576, not 832x468), target_frames = chunks*chunk_seconds*fps, sampler has NO negative/CFG (append no: lines); ComfyUI 0.19.2 dropped sparse_blocks/sparse_size/max_dims = r3b nodes 10/11 schema-STALE.
- Derrick 2026-10-23 6:12 PM CT: NO KEEP on r1-r6/r3r/r3b - write notes/hc_lessons_20261023.md, improve ONE variable per render, re-render the same seeds (IM1). KEEP is Derrick's alone; no vision judge on explicit output.
- Render task = write C:/AI/community/p7/JOB_REQUEST.json (absolute path), tick, print DONE, END the iteration; proof/notes in the NEXT pass. A request is submittable only while p7/jobs/<id>.result.json is absent.
- Budget gate = C:/Users/derek/5slock/ralph-community/logs/p7_budget.json (used_min, jobs, cap_min 615, job_cap 45; R-lines 495/35, the +120 min/10 jobs = ALI-173 bakeoff). No ledger under C:/AI/community.
- Proof: ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0; audio = test ',audio' in the -show_streams csv line; sha256 = certutil.exe -hashfile <path> SHA256; graphs: plain cmp a b.
- Web saves: scripts/web_fetch.py picks the extension from the bytes (.json only if json.loads accepts, .html, .txt, non-200 -> .403.txt), then end every research pass with scripts/check_web_saves.py (rc 1 = offender, --fix renames).
- Deny classes seen: the fiction lock matches COMMAND TEXT, so never tail/cat the deny log in a shell (use the read tool); a credential-shaped env name in a command line = secret deny (probe env inside a .ps1). Never retry a deny.
- Notes/ticks: append with a quoted heredoc (cat >> f <<'EOF') or a python RAW string, forward slashes - a plain string with C:\ paths eats \n, \r, \a, \b (0x07 0x08 0x0A 0x0D). A TASKS.md tick is ONE physical line; TASKS.md is CRLF.
- A green check that cannot fail is worthless: every builder/self-check gets a self-destruct probe (restore the OLD wiring/wording in a clone; every detector MUST fire there and 0 on the real artifact). Builders + FINAL generators = notes/*.py.
- Forge owns diagnosing its own loop: each pass read ralph.log + notes/denies.log, write notes/self_diagnosis.md, fix what is in reach (Derrick 2026-10-23 1:48 PM CT). ralph.ps1 is editable too (6:57 PM CT unlock): back it up, run the PowerShell parser on it, and write [!] Max to relaunch (edits load at the next start).
- EV1 (ALI-179): Send-MaxEvent in scripts/max_event.ps1 = notes/events.log 6-key JSON always, webhook POST only when the env pair is set; 6 emit sites in ralph.ps1; tests notes/ev1_test.ps1 + notes/ev1_sites_test.ps1.
