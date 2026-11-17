# 2026-10-30 POV oral cell - three methods compared (flags + measured identity, no scores)

Derek's GO 07:0x CT: one clip, her performing oral sex on him, from a first-person start image he
supplied plus a portrait of the approved character. After watching the first clip he said
"her face drifts too much. Let's try other methods? Like using her as the reference image ... you
can do both ways". Three GPU cells were rendered and measured. KEEP is Derek's alone; nothing here is
a score. GPU is IDLE, no lock, models unloaded.

## Cells (all beta7 stock: Euler/simple, 8 steps, shift 12 video / 3 audio, VSA keep_percent 10,
## 384x672 -> LatentUpscaler3D x2 -> 768x1344, 124 frames, 24 fps, 5.167 s, two-pass AddGuide frame 0)

| id | run | axis (one variable per cell) | seed | wall (output mtime - JOB start) |
|---|---|---|---|---|
| a03 | `b1_s51083020` | his POV lap shot as `ref_image_1`, face crops in `ref_image_2/3`, she enters the frame | 51083020 | 134.5 s |
| a02 | `b4_s51083021` | a close crop of **her** portrait as the start frame; his penis/denim/boxers from the prompt words | 51083021 | 126.0 s |
| a01 | `b5_s51083020_lora` | identical to a03 (same prompt bytes, same seed) **plus** `FC_SYDNEY_h3_face_v1` LoraLoader at `strength_model 0.7`, no trigger words in the prompt | 51083020 | 126.0 s |

Objective per cell: `OBJECTIVE ok`, 124 packets, 768x1344, 24 fps, 5.167 s, audio present, 0 redos.
Graphs are clones of the 2026-10-30 rendered-ok 124f sibling; self-checks 17 PASS / 0 DROP (b5: 14 PASS /
0 DROP), no drift outside the per-clip keys, self-destruct probes fired. `gpu_guard` IDLE and
`gpu-render.lock` held by the runner for each job; pytest 26 passed; `comm.guard_ok` True on every prompt.

## The identity instrument (the box's own CPU face tools, no vision model, no GPU)

`notes/bj_pov_face_curve.py` - SCRFD detection + ArcFace embedding per probe (every 4th frame, 31 probes),
cosine against the reference face crop Derek supplied. Warn-only by rule, never a pass.

| id | probes with a face | first frame with a face | ArcFace cos mean | cos min | face width px |
|---|---|---|---|---|---|
| a03 | 22 / 31 | 32 (1.33 s) | 0.4057 | 0.2456 | 298-367 |
| a02 | **31 / 31** | **0** | **0.5495** | **0.4481** | 230-413 |
| a01 | 22 / 31 | 36 (1.50 s) | 0.4059 | 0.2859 | 358-420 |

**Result: the start frame decides face fidelity, not the LoRA.** Her own pixels in frame 0 (a02) raises
mean cosine 0.406 to 0.549 (+35 %) and the floor 0.246 to 0.448 (1.8x), and her face is detected in every
probe from frame 0. The face LoRA on the entering cell (a01) moves the mean by +0.0002 (noise) and the
floor by +0.04: a face the model invents during an entry is not rescued by a LoRA at 0.7.

## Flag tier (Max's scripts, flags only)

Prechecks (`judge/prechecks.py`): all three `jump` (dino prev_min 0.633 / 0.652 / 0.623),
**0 cuts adaptive and 0 content in all three** - the jump is the motion onset, not a cut.
`static_no_transition` not applicable (3 refs).
VLM (`judge/vlm_judge.py`, qwen3vl_judge): `target_reached` **yes on all three** (deep oral contact in the
last frame), `anatomy_defect` **no on all three** (no fused bodies, no malformed genitals, no extra limbs),
`same_scene` yes, `same_people` yes; `start_kept` flagged on all three, which is the design of this family
(the pose must change - the act is the point), recorded as an instrument caveat in the manifest.

## Pack for Derek

`/pi-drop/bj-pov-2026-10-30/pack/a01.mp4 a02.mp4 a03.mp4` + `/pi-drop/bj-pov-2026-10-30/key.csv`
(sizes verified against the key: 2,347,345 / 2,394,931 / 2,396,790). Ids are shuffled so the method is
hidden; the key names the axis and the measured identity numbers. `bj_pov_b1_s51083020.mp4` and the prompt
of record are in the same folder from the first render.

## Next arm the data supports

**a04 = a02's composition + the face LoRA.** Her pixels in frame 0 (the measured driver) plus the LoRA on
top; one axis versus a02. Also open: a native-resolution identity source (FLUX.2 Klein 9B + the box's
`QuadView_klein9b_v1` / `TripleView_klein9b_v1` multi-view LoRAs) - the a02 crop is a 1.5x upscale of a
768-wide portrait, so face detail there is limited by the source, not by the video model. The H3 act LoRA
`MM-H3 - Blowjob v3.safetensors` is on disk with an unverified architecture header: not loaded in any cell
today (R31, one axis at a time).

## Files

Run dirs `C:/AI/community/runs/bj_pov_20261030/{b1_s51083020,b4_s51083021,b5_s51083020_lora}/`
(graph, status.log, objective.json, contact sheet). Prompt files
`C:/Users/derek/sydney/prompts/bj_pov_cell1_20261030.txt`, `.../bj_pov_cell4_20261030.txt`.
Builders `C:/Users/derek/sydney/work/bj_pov_20261030/{build_bj_pov_b1.py,build_bj_pov_b4.py,build_bj_pov_b5_lora.py,
prep.py,make_cell4_assets.py,preflight_check.py}`. Judges `notes/bj_pov_judge_check.py`,
`notes/bj_pov_cmp_check.py`, `notes/bj_pov_face_curve.py`; outputs `review/bj-pov-2026-10-30/judge_out/`
(`face_curve*.json`, `cmp_prechecks/`, `cmp_vlm/`), `review/bj-pov-2026-10-30/{cmp_flags.json,key.csv,pack/}`.
Plan `C:/Users/derek/sydney/plans/2026-10-30-bj-pov-plan.md`. Clips are not in git (`*.mp4`, `runs/` ignored).
