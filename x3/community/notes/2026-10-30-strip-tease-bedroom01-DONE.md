# 2026-10-30 strip tease, BEDROOM01, 124 f - DONE

Interactive request from Derek (14:02 CT): "Pick an image from the approved folder and give me a 5 second strip tease".
One clip, stock path (h3-hc-render s6 a-g), B2 default recipe, no plan and no brief behind it.
Box: `gpu_guard` IDLE, lock acquired/released inside the job, one job, nothing killed, no config touched, B2 default unchanged.

## 1. The pick (a, and the pick-scan rule)

- **Chosen: `approved_characters\BEDROOM01\01_BEDROOM_LINGERIE.jpg`** - approved by Derek verbatim 2026-10-18 6:34 AM CT
  ("Approve the bedroom lingerie image and add it to the catalog"), card `BEDROOM01\CHARACTER.md`, INDEX.csv row BEDROOM01,
  Google Flow original, fictional adult.
- Why it answers a strip tease: one solo adult woman, standing, fully framed head to feet, wardrobe on, a bedroom - the act is
  wardrobe coming off, so no partner, no invented location, no position-unlock.
- **Never animated in this lane:** a scan of all 1,513 `*.api.json` graphs under `runs/`, `p*/`, `notes/`, `templates/`
  counts every `LoadImage` input; BEDROOM01 appears in 0 of them. (The old strip-tease cell HC4 = `GI107.jpg` appears in
  6 graphs, so it is not a fresh pick; `notes/hc_picks_20261023.md:8,22`.)
- Native aspect 768x1376 (ar 0.558) = the portrait family of the 768x1344 canvas, so the start image is used **uncropped**.
- Start image staged as a byte-identical copy, no crop, no resize:
  `ComfyUI\input\community\strip_tease_20261030_bedroom01\BEDROOM01_LINGERIE.jpg`, sha256
  `91cbcc123635a46cfa11982888930d38835cb2ee1af4892162de10d6e60aac3d` - equal to the approved original
  (`01_BEDROOM_LINGERIE.jpg`) and to the pre-existing copy in `ComfyUI\input\` root. Run-dir copy `start_IMAGE.jpg` same sha.
- Seed 51103001 - grepped absent from the whole tree before use (unique per cell, one seed per clip).

## 2. Caption (b) - my own model, one ask, one image

`read` on the run-dir copy of the start image (Derek's "pick an image" plus stock path b). Facts used in the prompt:
long straight centre-parted blonde hair past the chest, blue eyes, calm face; a rigid silver open collar at the throat; a
small gem at the navel; a pale nude sheer underwired bra with a criss-cross strap detail at the centre front and narrow
shoulder straps; a pale nude sheer high-waisted high-cut brief with a wide opaque waistband, a sheer mesh front panel with
curved struts, four garter straps with metal clips; pale nude sheer thigh-high stockings; barefoot, feet together, arms at
her sides, left palm on her outer thigh; a bright bedroom, floor-to-ceiling windows with sheer white curtains behind her,
soft diffuse daylight, a low platform bed with a cream quilted headboard and cream bedding at the right, polished honey-toned
wood floor with soft reflections; vertical head-to-feet framing, camera at chest height, shallow depth of field.

## 3. Prompt (c) - h3-prompting, one act, one wardrobe path

`runs\strip_tease_20261030_bedroom01\strip_tease_bedroom01_s51103001\prompt.txt`, 11,105 B, 1,922 words,
sha256 `a28b4d77f68e5e94430f788eae7b59763c1ff652b530c1a11916e2b08e2a215e`.
Sections R5 in order: subject_definitions / summary / retention_analysis / detailed_description; no `continuation:` (single
clip). R6 `[reference generation]`. R2 "a grown woman aged 28 by canon declaration", fictional adult, no youth-guard term.
R11 both verbatim identity clauses + the five-finger hand lock + TenStrip #63-shaped retention lines.
**R12 clothing clause with the garment's named end state**: the bra leaves her body in one continuous stroke and stays
bunched in her right hand at thigh height for the rest of the clip, plus the matching "is an action in the story" line, so
the bare chest reads as the same body the photograph shows. R13/R14: `<Picture 1>` = identity + wardrobe + room + framing;
`<Subject 2>` = the bra as its own subject; `<Subject 3>` = the rest of the wardrobe that stays on; `<Subject 4>` = the room.
R17 PRIMARY MOTION = one continuous strip-tease draw, one full strip-and-slide cycle, large amplitude, hands in contact with
the fabric the whole time. R19 contact geometry: her own thumbs/fingertips keep grip of the fabric, the underband stays in
skin contact as it travels down her torso, wrists and forearms stay in frame, readable outline where her hands meet her body.
R16: the first 1.1 s establishes from the standing pose of the photograph, then the act. R18 literal anatomy (breasts,
areolae, nipples, sternum, ribs, belly, hips, thighs), body mass locked to `<Picture 1>`. R23 "The camera holds a static
shot." verbatim, locked-off tripod, fixed framing/focal length, no reveal. R8 four timed beats
(0.0-1.1 / 1.1-2.4 / 2.4-3.9 / 3.9-5.17 s) totalling 5.17 s, zero transition words. R24/R25: positives-only body, matte
skin with visible pores, zero oiled/glossy/sheen/glistening. R7: audio is two plain cue sentences at the end of
`detailed_description` (room tone, fabric brush, elastic tick, rustle in her fist, sole on wood, even breath through the
nose) - **no `overall_soundscape:` and no `non_diegetic_music:` block**. R21: Derek named no response dial for this
request, so the face stays calm, flat, chin level, eyes on the lens at her own pace - nothing added to it. R29: one pose,
one finish, one wardrobe path; the brief, the stockings, the collar and the navel gem stay on. R31: no LoRA in the graph, so
no trigger word. R30: the graph diff gate below shows only the five per-run fields.

Gate `notes\strip_tease_20261030_gate.py` (new, in git): **GATE PASS** - section order, the R11/R12/R23/R6/R17/R2 required
clauses present, R27 phrases absent, no transition word in `detailed_description`, no negation word outside the hand lock,
no banned skin word, no retired audio block, no youth-guard term, beats contiguous from 0.0 and totalling 5.17 s (124 f @ 24).
**Self-destruct probe fired**: on the old terrace baseline the required-clause detector fires, the absence detector fires and
the `overall_soundscape:` detector fires, so a green gate here can fail. `scripts/prompt_stats.py` run on the file
(1,922 words total; 1007 in `detailed_description`, beats 113/122/210/190 words).

## 4. Gate and graph (d, e)

- `C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py`
  = **26 passed in 4.21 s**. `comm.guard_ok(prompt)` = **True**, denied strings: none. (Guard files untouched.)
- Build: `scripts/make_b2_request.py --arm-dir runs\strip_tease_20261030_bedroom01\strip_tease_bedroom01_s51103001
  --prompt-file ...\prompt.txt --seed 51103001 --image community/strip_tease_20261030_bedroom01/BEDROOM01_LINGERIE.jpg
  --prefix community/strip_tease_20261030_bedroom01/strip_tease_bedroom01_s51103001/strip_tease_bedroom01_s51103001 --frames 124`
  → `request.api.json` 16,714 B, sha256 `3cf43c30c0c8e6887300f830a624de547575eed10082e96f4e4d72e144ce2d0d`, 26 nodes.
- **Diff gate vs `templates\b2.api.json`** (independent key-by-key compare, not the builder's own word): the changed keys are
  exactly `c0.prompt`, `img.image`, `noise.noise_seed`, `save.filename_prefix` - all inside the allowed five; `c0.length`
  124 equals the template value so it is unchanged. `LoadImage` resolves on disk; `(124-5) % 17 == 0`; the H3 node set is
  `c0` ReferenceToVideo + `ag0`/`ag1` AddGuide + `m_shift`, one ref slot.

## 5. Render and objective proof (f)

- 2026-10-30 14:16:32 CT `gpu_guard rc=0 IDLE`, `gpu_lock acquire rc=0 pid 11532`, LLM unloaded, 14:17:21 JOB start
  prompt_id `82db58f2-c0c2-479b-8d4b-fddeb2998e7e`, 14:20:22 **JOB end ok**, 14:20:23 comfyui_auto unloaded, lock RELEASED.
- **OBJECTIVE line:** `OBJECTIVE ok strip_tease_bedroom01_s51103001 image=False frames=124 size=768x1344 audio=True dur=5.167 bytes=1195673`.
- `objective.json` ok=true, attempts=1, **blackfreeze=[]**, collected_from_disk=false → **0 redos, one paid window**.
- Independent ffprobe: video `768,1344,24/1,124` packets; format duration `5.166688` s; stream lines `h264 ... video` and
  `aac ... audio ... stereo` (5.17 s, 124 frames = the requested 5 second clip on the H3 grid).
- mp4 sha256 `4d57992416df2d662d9dfa1b08e51e826a687e16324114d5a676b54e1f2b0efd`, 1,195,673 B.
- Contact sheet (generator output): `strip_tease_bedroom01_s51103001_stills_contact.png`, 881,524 B, sha256 `28d6c158…`.
- **True wall time = 139.5 s** (ComfyUI output mtime 14:19:40.47 minus the `JOB start` line), **1.125 s/frame**; the runner's
  `secs=180.1` is poll-quantized (ceiling only, `comm.POLL_SEC = 60`). Context, no claim: B2 at 124 f measured 140.9/162.3/140.5 s
  on three seeds (mean 142.1 s) - this prompt is 11,105 B against their 14,160 B, same cost, so prompt length is not a cost dial.
- No vision judge, no score, no precheck, no zoom pass on rendered explicit output. **KEEP is Derek's alone.**

## 6. One deviation, recorded

At **14:05:41 CT** Max's commit `bb1290f` changed `skills/h3-hc-render/SKILL.md` s6f and `templates/b2.README.md` to name
**`run_queue.py --run-dir ... --detach` as the only render path** ("run_graph_job.py is a helper run_queue.py imports;
never run it directly"). I had read the skill minutes earlier, and the copy I read still named `run_graph_job.py <run_dir>
<id> --frames <n>` for one clip, so I submitted the single clip through `run_graph_job.py` at 14:17. Same gates ran
(guard_ok before POST, gpu_guard IDLE, lock acquire/release, static check, objective check), one job, one window, rc=0.
The clip is **paid and objective-ok, so it is not re-rendered** (a paid render is never re-rendered). Next single clip goes
through `run_queue.py --run-dir ... --detach`. No rule was edited here; this note is the record.

## 7. Delivery

- QNAP pi-drop (new folder + new file, no overwrite, no delete): `pi_qnap.py mkdir /pi-drop/strip-tease-2026-10-30`,
  `pi_qnap.py put … /pi-drop/strip-tease-2026-10-30/strip_tease_bedroom01_s51103001.mp4` → `ls` shows
  **1,195,673 B**, byte-equal to the local file. **Filename for Derek: `strip_tease_bedroom01_s51103001.mp4`.**
- Files: run dir `runs\strip_tease_20261030_bedroom01\` (start image copy, `strip_tease_bedroom01_s51103001\{prompt.txt,
  request.api.json, the mp4, objective.json, status.log, contact sheet}`) - `runs/` and `*.mp4` are gitignored, so the record
  is this note, the gate script and the key numbers. Gate in git: `notes\strip_tease_20261030_gate.py`.
- Box at 14:30 CT: `gpu_guard` IDLE, no lock held, comfyui_auto unloaded, llama-swap alive, no config change, B2 default
  unchanged, nothing killed.
