# Community runbook (ALI-52) - how to make a video the community way

Written 2026-10-20 for Derrick, plain words. No GPU job was run to write this page. Proof of every number: C:\AI\community\community.log, p4\P4_RESULTS.md, P5_CHECK.md.

## Way A - one clip by hand (App Mode form)
1. Open the ComfyUI UI at http://127.0.0.1:10002 and use App Mode. If nothing answers, ComfyUI is asleep; it wakes when anything asks llama-swap for it (http://127.0.0.1:8080/upstream/comfyui_auto). Wake-up measured 22-23 s.
2. Open C:\AI\community\p3\Community_H3_I2V_beta6.app.json. The community settings are already inside it: 10Eros beta6 int8 UNET, euler sampler + simple scheduler, 10 steps, shift 10 video / 3 audio, VSA (keep_percent 10, start 0.2) on comfy kitchen attention, no LoRA node at all, 5 s, seed 51050001.
3. The form shows only 5 fields: start image, prompt, length in seconds, seed, megapixels.
4. Start image: pick community/FD006_768x1344.png - it is already in ComfyUI\input\community\. For a different still: approved adult (21+) only, already cropped to the output aspect, copied into ComfyUI\input\community\ first.
5. Queue. The clip lands in ComfyUI\output\community\app_h3_i2v_00001_.mp4.

Ignore the template's own help text on the right: it still says "FastVideo FastH3 8-Step V2 / 8 steps". That is stock template prose, not a setting; the graph runs beta6 int8 at 10 steps.

## Way B - a batch (shot list + queue script)
    cd C:\AI\community\scripts
    python batch_queue.py ..\shots\p6_pairs.json p6_pairs --dry-run    # prompts + graphs only, no GPU - safe
    python batch_queue.py ..\shots\p6_pairs.json p6_pairs --no-stitch  # the real renders
    python p6.py                                                       # whole D1 x D2 + 1 minute comparison
Flags: --dry-run stops before any GPU work; --no-upload keeps files off Drive; --no-stitch skips joining and, because the upload sits inside that same block, it also skips the upload. Unknown flags are ignored silently, so a typo'd flag still uploads.

A shot list is a JSON list, one object per shot: id, image (FD006 / FD003 / D15 / D12), image_note, beat, mode i2v (first frame) or r2v (reference), arm short / long_i2v / long_r2v, secs, chunk_secs, chunks (extra beats = latent continuation), seed, w, h, steps, optional antiburn and loras. Working examples: C:\AI\community\shots\ (see P6_PLAN.md). Start images are staged and centre-cropped to the output aspect automatically.

Prompt text is written by Strata (llama-swap, model coding_sc117_strata) from the official H3 guide, one prompt per chunk, adults-only guard plus a word-count check with one retry. Word ranges: short 60-120 per 5 s, long 150-250 per 5 s, ref2va 350-500 flat. If a prompt trips the adults-only guard the job is skipped, not rendered (run.log line "SKIP ... adults-only guard hit").

## Where things land
- ComfyUI's copy: ComfyUI\output\community\<run>\<id>_00001_.mp4.
- Working copy: C:\AI\community\runs\<RUN>\ - each mp4, plus a <name>.mp4.json sidecar (seed, size, steps, render seconds, prompt path), the exact graph that ran (<id>.api.json), all prompt text in runs\<RUN>\prompts\, run.log, results.json.
- Watching: runs\<RUN>\contact_sheet.png (one frame per second, one row per clip) and notes.md. Notes are notes; they block nothing (D14).
- Joined: runs\<RUN>\<RUN>_stitched.mp4 (ffmpeg concat, re-encode fallback if streams differ).
- Drive: exactly one rclone copy of the joined file to gdrive:AlienPc/community/<RUN>. That Drive folder does not exist yet - the first upload creates it. rclone's shared Google client_id is being retired during 2026, so a future 403 means re-auth; that is your call, config was not touched.
- The Switchyard comparison arm (sy_1min.py) joins but never uploads: only the community clip leaves the machine.

## Drafts vs finals
- Draft: 576x1024 (0.59 MP), 8 steps. In App Mode set megapixels 0.3-0.6. Measured: 10 s single chunk 150 s; 20 s two-chunk clip 205-355 s.
- Final: 768x1344 (1.03 MP), 10 steps. In App Mode set megapixels 1.03. Measured: 5 s clip 160 s.
- Same prompt and seed at both sizes, so a draft you like re-runs as a final. That is exactly p5_3shot.json (drafts) vs p6_pairs.json (finals).
- No machine judging: gates, face bands, hand gate and judges are enabled=false, default=false and stay manual tools (D7). You watch the contact sheet.

## How the LLM gets out of the way
The queue script writes all prompts first while Strata is loaded, then calls llama-swap /unload and wakes ComfyUI, then renders one job at a time. In the log that is "UNLOAD LLM(s) ['coding_sc117_strata']" then "COMFY ready v0.38.0 wait=22s vram_free=14.7GiB". Doing it by hand in App Mode does the same thing: if a chat model is loaded when a render starts, llama-swap drops it. Normal - only one thing fits the 5090 at a time. The community path never calls any other llama-swap model and never touches llama-swap.yaml.

## Rolling back (P1 freeze)
- Code: git tag pre-community-2026-10-20 (plus -wip) in C:\AI\director, C:\AI\forge-host, C:\AI\forge-bench, C:\Users\derek\5slock\workflows. Diff or check out that tag.
- Config: originals kept beside the live ones as C:\AI\director\config\llama-swap.yaml.bak-community and director.live.yaml.bak-community.
- ComfyUI: C:\AI\community\p1\comfy-snapshot-20261020.json (cm-cli restore-snapshot), plus p1\env-lock-20261020.txt (ComfyUI and custom-node commits, sha256 of every model used, pip freeze) and the older p1\env-lock-ali80-20261019.txt.
- Nothing in this path edited a live workflow, ComfyUI\user, llama-swap.yaml, Strata/Pi config, or C:\Apps. Every file edited since has a <name>.bak-20261020-ralph next to it.

## Facts still open (not fixed, for your decisions)
- Continuation windows came out at 238 extension frames whatever was requested: the 5 s chunk arm and the 10 s chunk arm both produced 20.04 s clips. Re-check before sizing the D2 chunk arms.
- antiburn is null (off) in every shot list; Anti-Burn 0.5 was approved for the P4 test only (D20).
- Cuts between chunks are separate clips joined at the stitch, not the guide's `[Shot N] At MM:SS.mmm` form inside one clip.
- The 1-minute list has 3 x (10 s + 10 s continuation) = 60.1 s after joining; chunk length 10 s is inside the D4 10-15 s window.
