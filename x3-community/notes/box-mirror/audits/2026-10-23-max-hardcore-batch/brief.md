# Max hardcore batch: Forge picks and renders 6 clips at 16:9 with audio (ALI-163). Brief, 2026-10-23 CT

## Community sources (read first)
- Ralph loop. One task per loop, the plan and specs reloaded every loop, AGENTS.md learnings, backpressure: https://ghuntley.com/ralph/
- PRD/tasks pattern. Small stories that each fit one context, a `passes` flag, fresh context per iteration, learnings appended: https://github.com/snarktank/ralph (README)
- Circuit breaker on no-progress or a repeated error, dual exit gate, call limits: https://github.com/frankbria/ralph-claude-code (README)
- 10Eros-Max beta6 settings. 10/3 shift, 8-12 steps, euler/simple works, dense or VSA, never SLA: https://huggingface.co/TenStrip/10Eros-Max
- Sound prompting. Audio is H3's weak spot. Use "soft flesh thudding and skin of the bodies clapping together" and "soft wet sliding sounds": https://huggingface.co/TenStrip/10Eros-Max/discussions/35
- Babble. Describe the background sound in the soundscape: https://huggingface.co/TenStrip/10Eros-Max/discussions/52
- beta6 sometimes looks like low fps. Reword the prompt ("dynamic video, fluid natural motions") or change the seed: https://huggingface.co/TenStrip/10Eros-Max/discussions/68
- A second sampling pass wipes the audio. Decode the stage-1 audio (VAEDecodeAudio) and give it to CreateVideo separately: https://www.reddit.com/r/StableDiffusion/comments/1vt8q3y/
- A refine/upscale/RIFE pass loses the audio, so save the stage-1 audio and mux it back. Source: https://www.reddit.com/r/StableDiffusion/comments/1xbobrr/ (from the Max brief; Reddit blocked our fetch, so I did not re-read it).
- The canvas is local code. ComfyUI `comfy_extras/nodes_minimax_h3.py` defaults to width 1344 / height 768 (step 32), MAX_PIXELS = 768*1344, length on the 17k+5 grid.

## Derrick (verbatim, 2026-10-23 ~7:38-7:40 AM CT)
"Then have forge pick and make more hardcore videos" · "Update it's persona and instructions for this" · card "6 clips, 120 GPU min" · "I want them 16:9" · audio "It needs to be added to the test".

## What changed (AlienPc; the loop was NOT relaunched, STOP_RALPH is still in place)
- `ralph-community\PROMPT.md`: STEP 0 and the breaker text are unchanged. Changes: new title, TASKS header named as the spec, one BATCH paragraph, the writable list (m4a files, still copies into `ComfyUI\input\community\hc\`), CPU-only ffmpeg for audio extract/remux/frame grabs, and a content-lock v2.3.0 link.
- `ralph-community\TASKS.md`: a new batch spec header, HC1-HC6 (one clip each; HC1 also writes the 6-still pick list) and FINAL (verify, .m4a per clip, contact sheet, summary). The old list is `TASKS.md.bak-20261023-batch`.
- `5slock\AGENTS.md`: the Content line links lock v2.3.0. New "Persona: current mission" section (2 lines).
- `ralph-community\ralph.ps1`: param defaults changed from `-GpuCapMin 360 -JobMax 16` to `495 / 32`, plus 1 comment line. Nothing else.
- Backups: `*.bak-20261023-batch` next to each file. Diffs: `/workspace/cos/audits/2026-10-23-max-hardcore-batch/*.diff`.

## Budget (how the runner reads it)
`RunJobs` reads only `used_min` and `jobs` from `logs\p7_budget.json`. It compares them with the **launch params** `$GpuCapMin` / `$JobMax` (ralph.ps1:345-346). The `cap_min`/`job_cap` fields in the file are just echoes written back by `BudgetAdd`. Editing the file would do nothing, so the change is in the ralph.ps1 param defaults: 495 = 375.3 used + 120, and 32 = 26 + 6. I did not use 510/33, because that is 390+120 and would let the batch spend 134.7 min. The gate runs only before a job, so TASKS.md also has Forge stop requesting once used_min > 475 (one ~20-min clip of headroom). Relaunch with no cap args, or pass `-GpuCapMin 495 -JobMax 32` explicitly. An old `-GpuCapMin 390 -JobMax 27` relaunch line would override the new defaults.

## Render settings Forge must keep
The PV2 graph `runs\ali147_pool_promptv2_s51080000\request.api.json` is unchanged except: width 1344 / height 768 on c0+c1, the prompts, img, seed and save prefix. It stays 10Eros_Max_h3_8stepTURBO_beta6_int8, euler/simple, 10 steps, shift 10/3, VSA, 243 + 238/22 = 481 frames, 24 fps, with audio wired dec_a -> CreateVideo in a single pass. Ids `ali147_pool_hc_c<n>_s5110000<n>` pass both runner id regexes.
- Stills: Forge reads the approved library text only (it can't see images). Aspect must be 1.70-1.85, otherwise the still is skipped. There are 18 candidates: BD002/004/006/007/013/076 (1376x768) and GI046/063/072/076/097/102/107/113/114/150/171/173 (16:9). The R2V node scales the reference with its aspect kept, so these need no crop.
- Redo: the harness does it (same seed, then seed+1 = the 2nd seed), and only on objective failures (JOB error, no audio, frames, black/frozen). FINAL adds one REDO line only on a crash (rc 4 / TIMEOUT).

## Preflight (09:0x AM CT, nothing rendered or loaded)
- llama-swap `/health` 200 OK, `/running` `{"running":[]}`. gpu_guard `IDLE`. RTX 5070 Ti 0 %, 1239/16303 MiB. ComfyUI :10004 is not listening (ttl 0). The harness wakes it at job time, and I did not wake it, because waking it loads the model. No JOB_REQUEST.json is pending and no ralph/pi process is running.
- 1344 % 32 = 0 and 768 % 32 = 0. Latent /16 is 84x48. 1344x768 is the node default and exactly MAX_PIXELS. 481 frames = 243 (17*14+5) + 238 continuation, the same as the rendered PV2 arms.
- pytest backpressure: 21 passed. ralph.ps1 parses with 0 errors. 7 open TASKS lines.
- Created the empty folder `ComfyUI\input\community\hc\` (LoadImage must resolve inside input).

## Risks / for Derrick
- The pi permission layer might deny Forge's copy into `ComfyUI\input\community\hc\` or its ffmpeg calls. Either one makes the line [!] with the reason, and Max does the copy.
- Forge can't view stills, so it picks from MANIFEST names. Derrick's contact-sheet KEEP is the quality gate.
- 6 x ~14-16 min ≈ 90-100 GPU min, which leaves little room for harness redos.
- ALI-162 card 1 (drop Kitchen m_attn) is still pending, so the batch keeps the current m_attn.

Linear: https://linear.app/alienpc/issue/ALI-163/max-hardcore-batch-forge-picks-renders-6-clips-169-with-audio
Content lock: /workspace/cos/canon/fiction-cond-lock.md v2.3.0 (AlienPc copy has the same sha256 47a82f5b...).
