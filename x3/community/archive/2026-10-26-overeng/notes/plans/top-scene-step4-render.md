# TOP-SCENE step 4 - the GI046 render (Derrick 2026-10-25 3:41 AM CT "why are those strip videos and not written based on the images")

Goal: render the card-faithful GI046 clip (the orc + the blonde woman, written from
`notes/scenes/GI046.md` + `notes/scenes/GI046.facts.json`) through llama-swap `/comfyui`
in ONE gated window, then prove it off disk. This is order 1 of 2 in Max's 9:30 PM CT
naming (`notes/needs_derrick.md` row 18) and it is also the orc half of ORC-ROBOT
(Derrick 2026-10-24 8:39 PM CT "I want the two videos the orc and the robot fucking video").

Files:
- graph  `C:/AI/community/p7/graphs/ali163_hc15_gi046_s51150032.api.json` (20,278 B, staged 06:35 CT)
- arm    `C:/AI/community/runs/ali163_hc15_gi046_s51150032/request.api.json` (byte-identical)
- queue  `C:/AI/community/p7/JOB_REQUEST.json` (id in top level AND jobs[], frames 362, 30 min)
- render `C:/AI/community/scripts/run_graph_job.py` (comm.run -> guard_ok on every prompt
  string before the /prompt POST; gpu_guard rc 0 + gpu_lock.ps1 -Acquire for the window)
- proof  `C:/AI/community/runs/ali163_hc15_gi046_s51150032/` mp4 copy + contact sheet +
  `C:/AI/community/notes/hc15_top_render_20261025.md`

Test / gates run BEFORE queueing (all green this pass):
- `python notes/rt_window_probe.py --check` (ralph-community) = RT_WINDOW_PROBE CLEAN 13/13
- `C:/AI/director/scripts/gpu_guard.ps1` (no args) = IDLE rc 0
- `python scripts/comfy_ctl.py status` = guard (0, ['IDLE'])
- `pytest -q scripts/tests/test_p6_review.py` = 21 passed
- `python notes/hc15_anchor_carry_build.py --top-check` = every ck_* PASS, arm reads the two free ids

Done-when:
1. `p7/jobs/ali163_hc15_gi046_s51150032.result.json` written by the runner (rc 0), and
   the mp4 present in `runs/ali163_hc15_gi046_s51150032/`.
2. ffprobe v:0 = 1344x768, 24/1, 362 +/- 33 frames, an audio stream, and certutil sha256 recorded.
3. Contact sheet built by the runner (objective, no vision judge).
4. On a client stall (exit 6) the clip is COLLECTED from
   `ComfyUI/output/community/ali163_hc15_gi046_s51150032/`, never re-rendered.
5. One tick + commit in the same commit; GI063 stays armed for the next window, and it
   stays behind `notes/needs_derrick.md` row 21 (the bound+distressed card vs the words)
   which is Derrick's call, not a prose fix.

No KEEP, no ranking, no vision judge on rendered output (Derrick's alone).

## Outcome 2026-10-25 08:00 CT (box clock; this plan was written 07:20:09 and the render landed 07:31:28)

DONE this pass, measured off disk, gates green:
- GI046 take B `ali163_hc15_gi046_s51150032` is registered as a render receipt: 1344x768, 24/1, 362/362 packets decoded,
  h264 + aac, 15.083333 s, 9,395,988 B, sha256 6cf9a239bb2d6b83.., byte-identical in `runs/<id>/` and
  `ComfyUI/output/community/<id>/ali163_hc15_gi046_s51150032_00001_.mp4`; `objective.json` ok=true, blackfreeze=[],
  outcome=ok, collected_from_disk=false; `status.log` carries the gated window (gpu_guard rc=0 IDLE, lock ACQUIRED pid 1348,
  JOB end ok secs=661.8, OBJECTIVE ok frames=362 size=1344x768 audio=True, lock RELEASED pid 1348). It ran off the current
  card-faithful prose record (mtime 06:35:37 CT), so it IS that record's render (GI046: 370 words, 0 negation tokens, 29/29
  verbatim card quotes).
- `ck_top_arm` is free-only: `top_arm_ids()` = TOP_ORDER minus every take with a video in the ComfyUI output dir. The arm is
  `['ali163_hc15_gi063_s51150031']`; a spent id can never be a queue entry, and an all-spent arm FAILS with a named reason
  ("arm nothing, strike the still, or record Derrick's decision") instead of printing an empty jobs list.
- `render_evidence_fires()` + `prose_render_count()` make the receipt row falsifiable: the cited status.log tokens, the cited
  objective.json fields (ok/frames/w/h/fps/audio/duration/secs/blackfreeze/outcome/collected_from_disk), the p7/jobs presence
  claim and the runs mp4 presence claim are each re-measured, and the note must name the take carrying the current prose record.
  Six new seeds, all fire: `--top-selftest` = 76 seeds all fired with the real artifacts clean; `--top-check` clean on 4 TOP
  graphs; `ck_nogpu` clean; `test_p6_review.py` 21 passed; `notes/rt_window_probe.py --check` 13/13.
- The manifest note states the measured result.json truth per row (`result.json absent, 0 result.json` on the clean render,
  because that queue receipt does not survive the pass boundary).

LESSON (AGENTS.md L20): a render's `p7/jobs/<id>.result.json` is not durable - the directory has 57 tracked files, no `*gi046*`
row, newest write 2026-10-24 12:27:18 CT, and `runs/` is gitignored (`.gitignore:10`). The durable proof is
`runs/<id>/{<id>.mp4,<id>.mp4.json,objective.json,status.log,<id>_stills_contact.png}` + the manifest receipt row the builder
re-measures. And a mid-pass probe you do not cross-check is a claim, not evidence (L4/L8/L10): my first probe of this window
printed fields (a result.json, a lock-release file) that two later tools measured as absent.

STILL OPEN / DERRICK: row 21 (GI063 restraint + distress on the card; render as the card supports, drop GI063, or pick a
replacement start image). GI063 is staged - graph 27 nodes clean, arm entry, manifest row, prose 370 words / 19/19 quotes - and
is NOT queued. KEEP on the GI046 clip is Derrick's alone; the review surface is `runs/<id>/<id>_stills_contact.png`
(1,155,992 B) + the mp4, and `notes/ali27_review_loop_build.py --build` copies them into `review/hc169/` on demand.

## Unarm, measured 2026-10-25 08:45 CT (after Derrick's 7:49 AM judgment)
Max's MAX row (fix_plan.md line 6) bars GI063 s51150031/s51150032 until needs_derrick.md row 21 is answered, and Derrick judged the GI046 render (row 26) horrible, so nothing is armable: `top_arm_ids()` = [] because GI046 take B is spent (9,395,988 B on disk) and GI063's free takes belong to a held still (`TOP_ONHOLD`). `--top-arm` now DELETES p7/JOB_REQUEST.json in that state instead of writing it, and `ck_top_arm` fails if the file exists while nothing is armable, naming each job's measured reason (SPENT bytes/sha/stamp, or ON HOLD with the MAX quote). Reason: PROMPT.md makes a request file submittable, so leaving it armed is an order to queue a paid clip or a clip under a hold. `ck_top_manifest` carries Derrick's judgment on the judged clip (his words + verdict) and `render_evidence_fires` re-measures every field of a render row. Gate count 75 seeds. Next step needs Derrick: row 21 (GI063 consent) and row 28 (the orc anatomy words, card-silent).
