# P7 playbook - review, keep top 3, optimise (harness-owned: Forge reads this, never edits it)
Prepared 2026-10-20 evening for Derek. Research behind it: `C:\AI\community\research\video-review-optimize-2026-10-20.md`.
All characters are fictional adults aged 21+ (canon: `C:\Users\derek\5slock\plans\canon\fiction-cond-lock.md`). Nothing involving minors, ever.

## 1. How GPU work happens (the only way)
You never render, never run `p6_review.py` / `batch_queue.py`, never call llama-swap or ComfyUI. The loop's LLM and ComfyUI share one
exclusive llama-swap group: one model request from you while a render runs kills the render. Instead you write ONE file per iteration,
`C:\AI\community\p7\JOB_REQUEST.json`, as the last thing before ticking. After you exit, `ralph.ps1` validates it, waits for
`gpu_guard.ps1` = IDLE and low GPU utilisation, runs the jobs one by one (pi is not running), writes `C:\AI\community\p7\jobs\<id>.result.json`
for each, and only then starts the next iteration.

```json
{"request_id": "p7_r1_probes", "jobs": [ {job}, {job}, {job} ]}          // 1-3 jobs
```
Render job (shots file MUST be `C:\AI\community\shots\<id>.json`; output folder `C:\AI\community\runs\<id>\`; id `^p7_[a-z0-9_]{3,48}$`, never reused):
```json
{"kind": "render", "id": "p7_r1_c1_ab07", "stitch": false,
 "reuse_prompts": [{"src_run": "p6_1min_ab05", "src_id": "p6_1min_ab05_seg2", "dst_id": "p7_r1_c1_ab07_seg2"}]}
```
- `stitch`: false for single-segment probes, true for full one-minute renders. Uploads are always off (`--no-upload`).
- `reuse_prompts`: copies the parent's already-written H3 prompt files (`<src_id>_c0_*.txt`, `_c1_*.txt`) to the new id so batch_queue does
  NOT ask the LLM for new wording - the knob is then the only change. Leave a segment out of `reuse_prompts` only when its beat text changed
  (knobs `cut_*`, `p_*`): batch_queue then writes fresh prompts for it with the LLM (between iterations, before ComfyUI wakes).
  Segment ids of the parents: `p6_1min_community` -> `p6_1min_seg1..3`; other P6 runs -> `<run>_seg1..3`; P7 runs -> `<run>_seg1..3`.
Review jobs (all local: ffmpeg + CPU metrics + local VLM `qwen3vl_judge`):
```json
{"kind": "review", "id": "p7_r1_rank", "preset": "p6"}                                       // -> runs\P6_RANKING.md/.json
{"kind": "review", "id": "p7_r1_probe_review", "pairs": ["p6_1min_ab05:seg2=p7_r1_c1_ab07:seg2"]} // 1-3 PARENT=CHILD -> p7\reviews\<id>\review.md/.json
{"kind": "review", "id": "p7_final_rank", "cands": ["p7_r2_c1_ab07_full", "p6_1min_ab05"]}  // 2-5 runs ranked together
```
Result file `p7\jobs\<id>.result.json`: `ok`, `rc`, `wall_min`, `budget_used_min`, `budget_cap_min`, `outputs`, `note`, optional `refused`
(`budget` | `gpu-busy`). A malformed request gets `p7\jobs\request_iterNN.result.json` instead.

## 2. Shot rules (the harness runs `p6_review.py checkshots` and refuses anything else)
Copy the parent's shot object(s) from its shots file (`shots\p6_1min_community.json`, `shots\p6_1min_ab05.json`, `shots\p6_1min_cuts.json`,
`shots\p6_1min_cuts_ab05.json`, or the parent's `shots\p7_*.json`) and change ONLY the knob and the `id`.
Allowed keys: id, image, image_note, beat, chunks, chunk_secs, mode, arm, secs, seed, w, h, steps, antiburn. Fixed: image D15 (same approved
adult still as the parent), 768x1344, mode r2v, arm long_r2v, secs 10, chunk_secs 10, at most one chunk, no loras. 1-3 shots per file.
Ids: `<job id>_segN`, keeping the parent's segment number N (a probe of segment 2 is `<job id>_seg2`).

## 3. Knobs - ONE per probe, everything else identical to the parent
| knob | id tag | change | reuse prompts | use when (parent's latest review) |
|---|---|---|---|---|
| anti-burn up | `ab05` / `ab07` | antiburn null -> 0.5, 0.5 -> 0.7 (LoRA applies to chunk 2 only) | yes | burn_exposure is the lowest dim, `severe_burn` flag, or objective sat_drift_max > 0.15 or clip_late_max > 0.03 |
| anti-burn down | `ab03` | 0.5 or 0.7 -> 0.3 | yes | burn is fine but chunk 2 looks flat/soft (sharp_drift_min < -0.4) on an anti-burn parent |
| steps | `st12` | steps 10 -> 12 | yes | temporal_consistency or artifacts is the lowest dim |
| seed | `sd` + 4 digits | seed + 1000 on the probed segment | yes | no dim is clearly lowest (spread < 0.5), or the previous knob for this slot was rejected twice |
| cut timing | `cut4` / `cut6` | "about five seconds in" -> "about four" / "about six" seconds in (cuts parents only) | no (beat changed) | pacing_cuts is the lowest dim on a `*_cuts*` parent |
| prompt clause | `pid` / `pexp` / `pmot` | append exactly ONE clause to the end of `beat` AND of the chunk: pid " Her face, hairstyle and body stay exactly the same throughout." / pexp " Soft, even, natural lighting with no overexposure." / pmot " Slow, smooth, continuous movement with natural weight." | no (beat changed) | identity_consistency (pid), burn (pexp, only after ab07 failed), motion_quality or prompt_adherence (pmot) |
Not available as knobs here (report, do not attempt): CFG / guidance (the 10Eros turbo model runs BasicGuider = CFG 1, no negative prompt),
sigma shift (locked 10 video / 3 audio by C2), resolution, LoRAs, mode, chunk length (238-frame continuation finding), sampler.
Tie order when two dims are equally lowest: burn_exposure > artifacts > temporal_consistency > identity_consistency > pacing_cuts > prompt_adherence > motion_quality.
Never try the same knob twice in a row on a slot unless the last try was promoted. Probe the parent's `weakest_segment` (from its review json; default 2).

## 4. Promotion and parents
- `p6_review.py compare` gives each pair a verdict: **PROMOTE** = the child wins the swapped-order pairwise comparison in both orders AND its
  composite >= parent + 0.25, or composite >= parent + 0.75 alone; never when it raises more hard flags. Otherwise **KEEP_PARENT** (or NO_DATA).
- Only a PROMOTE probe earns a full one-minute render (same knob applied to all 3 segments; seeds unchanged; `reuse_prompts` for all 3 unless
  the knob changed beat text). A full render whose full review verdict is PROMOTE becomes that slot's new parent; otherwise the parent stays.
- Hard caps: 3 rounds x 3 slots; at most 1 full render per slot per round and 3 full renders in all of P7; GPU budget 360 min and 16 jobs
  (harness-enforced; `refused: budget` in a result means stop optimising and go to the final tasks).
- Switchyard (`p6_1min_switchyard`) is not a batch_queue shot list: if it ranks top 3 it stays on the board as a fixed reference and the
  next community-path video takes its slot.

## 5. Leaderboard `C:\AI\community\runs\P7_LEADERBOARD.md`
Header line, then a "Slots" table (slot | current parent run | parent composite | weakest seg | lowest dims) and a "History" table with one
row per probe and per full render: round | slot | job id | knob | value | parent | probe verdict | full verdict | composite (child/parent) |
GPU min used so far. Keep old rows; update the Slots table each round.

## 6. GPU time (measured on this RTX 5070 Ti, 768x1344, 10 steps)
One 20 s segment (10 s base + 10 s continuation) = 812-837 s render + ~50 s ComfyUI wake (p6_1min_cuts run.log); a full minute = 3 segments
~42 min (+ ~5 min LLM prompt writing only when prompts are not reused). Probe = 1 segment ~15 min. Reviews: P6 rank of 5 videos ~20-30 min
(55 judge calls), a 3-pair probe review ~8-10 min, a full-vs-parent review ~6-8 min per pair.
