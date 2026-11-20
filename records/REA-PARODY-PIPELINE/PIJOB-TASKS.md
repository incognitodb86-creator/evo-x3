# REA parody pipeline: pi-job unit tasks (local LLM)

Plan: [PLAN.md](./PLAN.md). Derrick 2026-11-20 ~9:19 AM CT wants the local LLM to build this through the Hermes
coding workspace, as the test that the coding workspace works.

## How to run a unit

1. Derrick, in the Hermes **code** chat: `Run REA unit C1` (then C2, ... one at a time, after the previous is DONE).
2. Hermes reads this file in the worktree and runs, with the unit's task text exactly as written below:
   `pi-job code /home/evo/AI/_worktrees/rea-parody "<task text of the unit>"`
3. Hermes gives the job ID, waits (`pi-job wait <id> --timeout 170`, several rounds), then reports `DONE` + the commit
   SHA, or `STUCK` + the `detail=` line. No auto retry. Each unit is sized for the default 60-minute limit. If one
   reports `timed_out_after=60m`, Derrick can say "rerun C<n> with 2 hours" and Hermes adds `--timeout-min 120`
   (max 480). The partial work stays in the worktree, so pi continues from it.
4. After `DONE`, Hermes runs the unit's **Check** command itself (read-only) and reports pass/fail counts.

Rules for every unit (pi must follow them; they are repeated in each task text as "Common rules"):

- Work only in the repo at the current directory, on branch `pi/rea-parody`. Change only the files the task names.
- Tests are offline: no network, no GPU, no ComfyUI, no llama-swap. Mock `subprocess.run`, HTTP and the vision chat.
- Python 3.12+, standard library + numpy + Pillow only (no scipy, no librosa, no new dependencies).
- Run the task's test command and make it pass before committing. Also run `test_flux_h3_redteam.py` and
  `test_prose_file_gate.py` to make sure nothing else broke.
- Commit once with `git add <exact paths>` (never `git add -A` or `.`), message `rea C<n>: <short summary>`. No push.
- Never print or read keys, `.env`, `llm.env`, `auth.json`, `models.json`, `*.token`. Never weaken an 18+ check.

Common test command prefix (the X3 render venv):

```bash
cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q
```

---

## C1: onset probe

**Task text:**

```text
REA unit C1. Create x3/community/scripts/parody/rea_onset_probe.py and x3/community/scripts/parody/test_rea_onset_probe.py.
rea_onset_probe.py: read a 16-bit PCM WAV with the wave module (mono or stereo -> mono float), compute a spectral-flux
onset envelope with numpy (frame 2048, hop 512, Hann window, half-wave rectified flux, normalized 0..1), pick peaks
above mean+1*std with a 0.1 s minimum gap, estimate BPM from the autocorrelation of the envelope limited to 60-180 BPM.
Public functions: load_wav_mono(path) -> (samples: np.ndarray float32, sr: int); onset_envelope(samples, sr) -> (env, times);
detect_onsets(env, times) -> list[float]; estimate_bpm(env, sr, hop=512) -> float | None;
probe(wav_path, shots=None) -> dict with keys "source", "sr", "bpm", "onsets" (seconds, 3 decimals),
"shots" (for each shot dict {"id","start","end"}: {"id", "beats": onsets inside the window, "strongest": time of the
largest envelope value inside the window or None}). CLI: rea_onset_probe.py <wav> [--breakdown breakdown.json]
[-o onset_beats.json]; with --breakdown take shot windows from breakdown["shots"][i] keys "id"/"shot_id" and
"start"/"end" (seconds), skipping shots without both. Default input when a directory is given: <dir>/stems/music.wav,
else <dir>/stems/original.wav. Print one line "DONE <out_path> bpm=<bpm> onsets=<n>".
Tests (synthetic audio written to tmp_path, no fixtures from disk): a 120 BPM click track (short 1 kHz bursts every
0.5 s, 8 s, 22050 Hz) -> bpm within 115..125 and at least 12 onsets, each within 0.05 s of a true click; silence ->
onsets == [] and bpm is None; stereo file works; shot windows return only their beats; CLI writes valid JSON.
Common rules: change only these 2 files; offline tests; stdlib+numpy only; run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_rea_onset_probe.py`
and make it pass; commit once with git add of the exact paths, message "rea C1: onset probe"; no push; no secrets.
```

**Check:** `... -m pytest -q test_rea_onset_probe.py`

---

## C2: shot plan helpers

**Task text:**

```text
REA unit C2. Create x3/community/scripts/parody/rea_shot_plan.py and x3/community/scripts/parody/test_rea_shot_plan.py.
Read build_request.py functions align_h3_frames and the constants SINGLE_CLIP_MAX_FRAMES and H3_FPS first and reuse
them (import build_request as br). Public functions:
1) plan_frames(seconds: float, beats: list[float] | None = None, shot_start: float = 0.0) -> list[dict].
   frames = round(seconds * br.H3_FPS). If frames < 56: one part {"frames": 56, "trim_to_frames": frames}.
   If 56 <= frames <= br.SINGLE_CLIP_MAX_FRAMES: one part {"frames": br.align_h3_frames(frames), "trim_to_frames": frames}
   (trim only when the aligned value is larger). If longer: split into parts of at most SINGLE_CLIP_MAX_FRAMES frames,
   moving each cut to the nearest beat (absolute seconds, so subtract shot_start) within +-1.0 s when beats are given;
   each part gets {"frames": aligned, "trim_to_frames": its real frames, "suffix": "a"/"b"/..., "continue_from":
   previous suffix or None}. Expected: 1.2 s -> [{"frames":56,"trim_to_frames":29}]; 6.583 s -> frames 158;
   14.0 s -> 2 parts, each frames <= 243, second has continue_from "a".
2) camera_vocab(move: str) -> str. Map free text camera moves to H3 words: amplitude small|medium|large and speed
   slow|medium|fast. static/locked/held/tripod -> "held static"; push/dolly in/zoom in -> "<speed> push-in with <amp>
   amplitude"; pull/dolly out/zoom out -> "<speed> pull-back with <amp> amplitude"; pan left/right, tilt up/down,
   orbit/arc, handheld/shaky -> same pattern with that move name. Speed words: slow/gentle/subtle -> slow,
   quick/fast/whip/rapid -> fast, else medium. Amplitude: slight/small/subtle -> small, big/wide/large/sweeping ->
   large, else medium. Unknown -> "held static".
3) build_cast_lock(names: list[str] | None, character: str | None, lane: str, aspect: str, shots: list[dict]) -> dict.
   lane "parody" when names are given, "oc" when character is FCSydny or FCMegan (case-insensitive). canvas [768,1344]
   for 9:16, [1344,768] for 16:9. flux_identity: for the first name, refmod = "fk9_<lowercase alnum>_v1_refmod",
   lora = "klein9/fk9_<lowercase alnum>_v1_prodigy.safetensors" (same naming as flux_still._hybrid_stack_for_name;
   import flux_still and call it). h3_identity: {"allow_audio_ref": lane != "parody", "names": names,
   "character": character}. shot_overrides: per shot {"shot_id", "parts" (from plan_frames), "camera_h3_vocab"}.
   Raise ValueError when both names and character are empty, or when aspect is not 9:16 or 16:9.
4) write_batch_card(batch_dir: Path, cast_lock: dict, shots: list[dict]) -> Path: writes batch_card.md with one table
   row per shot part (shot id, seconds, frames, trim, camera words, flux mode) and the line "Reply GO to run this batch."
   No prompt prose in the card.
Tests: the three plan_frames examples above; beat-aligned split moves the cut onto a beat inside the window;
camera_vocab for at least 8 phrases; cast lock parody -> allow_audio_ref False and FCSydny -> lane "oc" and
allow_audio_ref True; ValueError cases; batch card file has one row per part.
Common rules: change only these 2 files; offline tests; stdlib+numpy only; run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_rea_shot_plan.py test_flux_h3_redteam.py`
and make it pass; commit once with git add of the exact paths, message "rea C2: shot plan helpers"; no push; no secrets.
```

**Check:** `... -m pytest -q test_rea_shot_plan.py test_flux_h3_redteam.py`

---

## C3: FLUX rea templates + 2-LoRA cap

**Task text:**

```text
REA unit C3. Add two candidate templates and wire them into flux_still.py.
1) x3/community/templates/flux_rea_edit.candidate.api.json: start from miraclein_edit.candidate.api.json. Replace the
   size path so the LoadImage output goes through one ImageScale node (upscale_method "lanczos", crop "disabled",
   width 768, height 1344) before VAEEncode, and EmptyFlux2LatentImage / Flux2Scheduler use fixed width 768 and
   height 1344 (no GetImageSize links). Add Klein9RefModsLoader + Klein9RefModApply on BOTH the positive and negative
   paths exactly like miraclein_refmod.candidate.api.json nodes "12", "13", "14" (retention "fully_preserved (1.0)",
   all mod_N "none"); the RefMod apply nodes take the ReferenceLatent outputs as their conditioning and feed the
   CFGGuider. Keep UNET Miraclein_4.5_9b_NVFP4.safetensors, euler, 12 steps, CFG 1.1, the LoadImage title "image1".
2) x3/community/templates/flux_rea_pose.candidate.api.json: start from flux_stills_pose_klein.candidate.api.json.
   Change UNETLoader to Miraclein_4.5_9b_NVFP4.safetensors, remove the FluxKVCache node and rewire its consumers to
   the model output before it, set steps 12, sampler euler, CFG 1.1, replace any ImageScaleToTotalPixels /
   ResizeImageMaskNode on the input images with ImageScale (lanczos, crop "disabled", 768x1344), fix the latent and
   scheduler to 768x1344, keep the refcontrol_v2_poses LoRA at 0.9 and the DWPreprocessor, and add the same pos+neg
   RefMod nodes as above.
3) flux_still.py: add MODES "rea_edit" and "rea_pose" pointing at the two files. In _inject_flux_loras count the
   LoraLoaderModelOnly nodes with strength_model > 0 after injection; if more than 2, raise ValueError("FLUX LoRA cap
   is 2 active LoRAs (got N)"). Do not change any other behavior or default.
4) x3/community/scripts/parody/test_flux_rea_templates.py: both JSON files load; every link target node exists; no
   FluxKVCache, no GetImageSize, no ImageScaleToTotalPixels or ResizeImageMaskNode; ImageScale has crop "disabled" and
   768x1344; build_flux_still(mode="rea_edit", refmods=["Sydney Sweeney"], image=<tmp png>, dry_run=True) is READY with
   retention "fully_preserved (1.0)" on both apply nodes and the anchor sentence; rea_pose with one celeb LoRA has
   exactly 2 active LoRAs; rea_pose with 2 extra LoRAs raises ValueError; plain t2i with one LoRA still works.
   Monkeypatch fill_request._stage_still and fill_request.pixl_abs so no file leaves tmp_path.
Common rules: change only these 4 files; do not touch production templates (files without .candidate); offline tests; run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_flux_rea_templates.py test_flux_h3_redteam.py`
and make it pass; commit once with git add of the exact paths, message "rea C3: flux rea templates + lora cap"; no push; no secrets.
```

**Check:** `... -m pytest -q test_flux_rea_templates.py test_flux_h3_redteam.py`

---

## C4: orchestrator `plan`

**Task text:**

```text
REA unit C4. Create x3/community/scripts/parody/rea_parody_remake.py with subcommands plan and status, and
x3/community/scripts/parody/test_rea_parody_remake.py. Use rea_shot_plan (C2) and rea_onset_probe (C1).
`plan <batch_dir> --rea-dir <dir> (--names NAME... | --character FCSydny|FCMegan) [--lane parody|oc]
[--aspect 9:16|16:9] [--shots shot_001,shot_002]`:
- batch_dir must be an absolute path under /home/evo/AI/community/runs/ whose last part starts with "rea_"
  (tests pass a tmp root through an env var REA_RUNS_ROOT that overrides /home/evo/AI/community/runs).
- Read <rea-dir>/breakdown.json. Shots are breakdown["shots"]; each has an id ("id" or "shot_id"), "start", "end"
  (seconds) and a first keyframe path. Find the keyframe as <rea-dir>/shots/<id>_first.jpg, else the shot's
  "keyframe"/"first_frame" key relative to rea-dir. Missing keyframe -> NOT_READY for the whole batch.
- If <rea-dir>/onset_beats.json is missing and <rea-dir>/stems has music.wav or original.wav, run
  rea_onset_probe.probe() and save onset_beats.json into the batch dir.
- For each selected shot create <batch_dir>/shots/<id>/ with _inputs/<id>_first.jpg (copy), and raw_still_read.json
  from render_writer_pipeline._ensure_still_read_raw(shot_dir, still, None, client, cfg, log) where cfg comes from
  render_writer_pipeline's config loader and client is wp_llm.Client(cfg, log). Rename the produced still_read.json to
  raw_still_read.json (the H3 build later writes its own still_read.json for the edited still).
- 18+ gate, fail closed: if wp_lint.YOUTH_RE or wp_lint.UNDER18_AGE_RE matches the JSON text of the read, or
  build_request._check_writer_18plus raises, write <shot_dir>/clip_NOT_READY.txt, stop the whole batch with
  "NOT_READY 18+ gate <id>: <match>" and exit 3. No later stage may run for that batch.
- Write <shot_dir>/shot_brief.json: {"shot_id", "seconds", "parts", "camera_h3_vocab" (from the breakdown camera
  move text via camera_vocab), "dialogue" (breakdown ASR text for the shot, cut to 25 words), "sfx" (list of strings
  if present), "beats"} and keep a "seed": per shot int (51083601 + index) so shots never share a seed.
- Write <batch_dir>/parody_cast_lock.json (rea_shot_plan.build_cast_lock) and batch_card.md (write_batch_card).
- Print "READY plan <batch_dir> shots=<n> parts=<m>".
`status <batch_dir>`: print one line per shot: id, which of raw_still_read.json, flux_prompt.txt,
_inputs/<id>_edited.png, hermes_prose.txt, build_report.json (status), clip/render_ok.json exist.
Tests: build a fake rea dir in tmp_path (breakdown.json with 2 shots 6.583 s and 14.0 s, two small JPEGs made with
Pillow, a stems/music.wav click track); monkeypatch _ensure_still_read_raw to write a canned adult read and count
calls. Cases: 2-shot plan creates 2 isolated shot dirs with their own files, seeds differ, shot_002 has 2 parts;
a youth cue in the canned read gives exit 3, clip_NOT_READY.txt, and zero calls for the remaining shots; parody lane
cast lock has allow_audio_ref False; FCSydny gives lane "oc"; batch_dir outside the runs root is refused; status
prints both shots.
Common rules: change only these 2 files; offline tests (mock vision/HTTP); run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_rea_parody_remake.py test_rea_shot_plan.py test_prose_file_gate.py`
and make it pass; commit once with git add of the exact paths, message "rea C4: plan stage"; no push; no secrets.
```

**Check:** `... -m pytest -q test_rea_parody_remake.py test_rea_shot_plan.py test_prose_file_gate.py`

---

## C5: orchestrator `flux` + `build`

**Task text:**

```text
REA unit C5. Extend x3/community/scripts/parody/rea_parody_remake.py and test_rea_parody_remake.py with subcommands
flux and build. Do not change plan/status behavior.
`flux <batch_dir> [--shot ID] [--queue --yes-derrick]`: refuse --queue without --yes-derrick (exit 3). For each shot
(or the one given) that has no clip_NOT_READY.txt: read <shot_dir>/flux_prompt.txt (written by Hermes; missing ->
"NOT_READY <id> flux_prompt.txt missing", skip the shot). Mode: shot_brief or cast lock "flux_mode" if set, else
"rea_edit"; "rea_pose" when the cast lock shot override says new_pose. Call flux_still.build_flux_still(
<shot_dir>/flux, prompt, mode, refmods=[cast_lock refmod], loras=[] or the hybrid LoRA when the cast lock has
"hybrid": true (then refmod_strength 0.85 and retention "partially_preserved (0.7)"), image=<shot_dir>/_inputs/<id>_first.jpg,
width/height from the cast lock canvas, seed from shot_brief, character/names from the cast lock, dry_run=not queue).
With --queue call flux_still.queue_flux_still(<shot_dir>/flux) and copy the returned still to
<shot_dir>/_inputs/<id>_edited.png. One shot at a time; a failed shot is reported and the next shot continues.
`build <batch_dir> [--shot ID]`: for each shot with _inputs/<id>_edited.png and hermes_prose.txt and no
clip_NOT_READY.txt, run render_writer_pipeline.py in a subprocess with the venv python (sys.executable) and args:
<shot_dir> --prose-file <shot_dir>/hermes_prose.txt --still <edited png> --still-mode guide --position <shot_brief.json "position" (Hermes sets it when it writes the prose), default "talk"> --ask "rea remake <id>" --frames <first part frames> --aspect <cast lock aspect> and --names ...
(parody) or --character ... (oc). Never pass --queue, --yes-derrick or --fix-once. Read <shot_dir>/build_report.json
and record {"id","status","reason"} in <batch_dir>/build_status.json. NOT_READY shots print "STUCK <id> <reason>" (Hermes
may rewrite the prose once and run build for that shot again; the script never loops).
Tests (mock flux_still.build_flux_still / queue_flux_still and subprocess.run): flux without --yes-derrick + --queue
exits 3 with zero queue calls; dry flux builds one call per shot with mode rea_edit and the shot seed; hybrid cast
lock passes 0.85 / 0.7 / the prodigy LoRA; a shot missing flux_prompt.txt is skipped and the other continues;
--queue copies the still to _inputs/<id>_edited.png; build passes --prose-file and --names for parody, never --queue,
--yes-derrick or --fix-once; a NOT_READY build_report gives STUCK and build_status.json has both shots; the parody lane
build args contain no audio/voice flags.
Common rules: change only these 2 files; offline tests; run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_rea_parody_remake.py test_flux_rea_templates.py test_prose_file_gate.py`
and make it pass; commit once with git add of the exact paths, message "rea C5: flux and build stages"; no push; no secrets.
```

**Check:** `... -m pytest -q test_rea_parody_remake.py test_flux_rea_templates.py test_prose_file_gate.py`

---

## C6: color match + master assembly

**Task text:**

```text
REA unit C6. Create x3/community/scripts/parody/rea_color_match.py and x3/community/scripts/parody/test_rea_color_match.py.
Functions: sample_frames(mp4, n=5) -> list of HxWx3 uint8 arrays read with one ffmpeg subprocess per frame
(-ss <t> -frames:v 1 -f rawvideo -pix_fmt rgb24), times spread evenly over the clip duration from ffprobe;
channel_stats(frames) -> (mean[3], std[3]) per RGB channel; transfer_expr(src_stats, ref_stats) -> ffmpeg lutrgb
filter string applying out = (val - src_mean) * (ref_std / src_std) + ref_mean per channel, clipped 0..255, with
std floor 1.0; skip (return None) when every channel mean differs by < 2 and std ratio is within 0.95..1.05;
build_master_cmd(clips: list[dict], out_path, bgm=None, bgm_db=-14) -> list[str] where each clip dict has "path",
"trim_to_frames" (int or None) and "lut" (str or None). The command uses one ffmpeg call: per input
[i:v] -> optional lutrgb -> optional trim=end_frame=N,setpts=PTS-STARTPTS, [i:a] -> optional atrim=end=N/24,asetpts;
then concat=n=K:v=1:a=1 (hard cuts, no crossfade); optional bgm input mixed with amix after volume=<bgm_db>dB under
the concat audio; output -c:v libx264 -crf 16 -pix_fmt yuv420p -r 24 -c:a aac -b:a 192k. CLI:
rea_color_match.py <out.mp4> <clip1.mp4> [<clip2.mp4> ...] [--trim i=N]... [--bgm music.wav] [--bgm-db -14]
[--dry-run] (dry run prints the command and exits 0). The first clip is the color reference.
Tests (no real ffmpeg: mock subprocess.run / check_output and feed synthetic arrays): channel_stats on solid colors;
transfer_expr maps a dark synthetic clip toward the reference mean (apply the same math in numpy and check);
identical stats -> None; build_master_cmd has concat=n=2, no xfade, trim for a padded shot, amix only with bgm, the
-14 dB volume, crf 16 and -r 24; CLI --dry-run prints the command.
Common rules: change only these 2 files; offline tests; stdlib+numpy only; run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_rea_color_match.py`
and make it pass; commit once with git add of the exact paths, message "rea C6: color match and master"; no push; no secrets.
```

**Check:** `... -m pytest -q test_rea_color_match.py`

---

## C7: orchestrator `queue` + `assemble`

**Task text:**

```text
REA unit C7. Extend x3/community/scripts/parody/rea_parody_remake.py and test_rea_parody_remake.py with subcommands
queue and assemble. Do not change plan/status/flux/build behavior.
`queue <batch_dir> --yes-derrick [--shot ID]`: refuse without --yes-derrick (exit 3). For each shot whose
build_status.json entry is READY and that has no clip_NOT_READY.txt, in shot order, run
["bash", "/home/evo/AI/render/x3/queue-remote.sh", <shot_dir>, "--yes-derrick"] (path overridable by env
REA_QUEUE_REMOTE for tests), then wait for <shot_dir>/clip/render_ok.json with an "upscale" object, polling every
15 s up to 40 minutes (both values overridable for tests). Only start the next shot after DONE or FAIL. Record
{"id","status","clip"} in <batch_dir>/queue_status.json. Never queue a shot twice if queue_status already says DONE.
`assemble <batch_dir> [--bgm] [--publish]`: collect the 2x clip of every DONE shot in order (render_ok.json "clip",
default clip/clip.mp4), trim_to_frames from shot_brief parts, compute luts against the first clip with
rea_color_match (sample_frames, channel_stats, transfer_expr), run build_master_cmd to <batch_dir>/final_2x.mp4
(--bgm uses <rea-dir>/stems/music.wav recorded in the cast lock or batch meta, -14 dB). --publish copies final_2x.mp4
to /srv/renders/<batch_name>_final_2x.mp4 only if that folder is writable, else prints a note. Print
"DONE assemble <path>" and a line "MEDIA:<path>".
Tests (mock subprocess.run and time.sleep; fake render_ok.json files): queue without --yes-derrick exits 3 with zero
calls; two READY shots are queued in order, one at a time; a NOT_READY shot is never queued; a shot already DONE in
queue_status.json is skipped; timeout marks FAIL and continues; assemble builds one ffmpeg command with both clips in
order, the trim for the padded shot, and amix only with --bgm; --publish skips cleanly when /srv/renders is missing.
Common rules: change only these 2 files; offline tests; run
`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q test_rea_parody_remake.py test_rea_color_match.py test_prose_file_gate.py test_flux_h3_redteam.py`
and make it pass; commit once with git add of the exact paths, message "rea C7: queue and assemble"; no push; no secrets.
```

**Check:** `... -m pytest -q test_rea_parody_remake.py test_rea_color_match.py test_prose_file_gate.py test_flux_h3_redteam.py`

---

## What Max checks after C7 (C8)

- `git log --oneline mono..pi/rea-parody` shows 7 commits `rea C1`..`rea C7`, each touching only its listed files.
- Full parody suite in the worktree: `cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q`.
- gitleaks pre-push on the box; then fast-forward mono, push GitHub, mirror Gitea.
- Record which model ran each unit (pi-job `detail=` shows `model=alienpc` or `model=x3`) and any STUCK in
  `records/REA-PARODY-PIPELINE/RESULT-CODING.md`. That file is the coding-workspace test result.
