# 2026-11-02 H3 LoRA A/B (runs/h3_lora_ab_20261102) - L6 proof, flags, pack: DONE (pack delivery blocked)

Three single-axis LoRA cells on the measured identity driver a02 (`runs/bj_pov_20261030/b4_s51083021`),
rendered by L5 2026-11-02 13:51-14:45 CT under Derek's "Go do ot" (a launch GO for these 3 clips only,
not a KEEP, not a Phase pick). This note is measurement only: flags and measured identity numbers, no
scores, no quality claim, no KEEP. **KEEP is Derek's alone.** GPU is closed: `C:\AI\locks\` has only
`_removed`, `comfy_ctl.py status` = `comfy_ok=False guard=(0, ['IDLE'])`.

## Cells (one axis each: LoRA file + strength on the model chain)

Prompt bytes (`sha256 d73b6036ebc927bdc74d…`, 0 trigger words), seed 51083021, dials, canvas
384x672 -> x2 -> 768x1344, 3 ref slots and 124 frames are the a02 base's, byte for byte (proved by
`build_b2_cell.py --verify` + the 26/26 L4 stage check, see `2026-11-02-l4` records).

| cell | LoRA | strength_model | author strength | seed |
|---|---|---|---|---|
| c1_face_lora_07 | `FC_SYDNEY_h3_face_v1.safetensors` | 0.7 | (the a04 arm the Oct 30 data asks for) | 51083021 |
| c2_charswap_10 | `H3_charswap_v15.safetensors` | 1.0 | 1.0 (adopted) | 51083021 |
| c3_realism_04 | `H3_realism_people_v1.safetensors` | 0.4 | 1.0 (reduced for our merged beta7) | 51083021 |

All three files are L3 **FIT** by header (mapped tensor pairs 100 %: 208/208, 104/104, 208/208), and all
three carry no `.alpha` keys = effective alpha 1.0, so 0.4/0.7/1.0 read on one ruler.

## 1. Objective (the item's command, run per clip 2026-11-02 15:0x CT)

```
ffprobe -v error -select_streams v:0 -count_packets \
  -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0 <clip>
```

| cell | width,height,fps,packets | audio | duration | bytes | clip sha256 (first 20) | wall s (driver `JOB end`) |
|---|---|---|---|---|---|---|
| c1_face_lora_07 | `768,1344,24/1,124` | `aac,audio` | 5.166688 | 2,304,919 | `8839a2c21bbe598c05b2` | 153.8 |
| c2_charswap_10 | `768,1344,24/1,124` | `aac,audio` | 5.166688 | 2,558,369 | `96144664fdfed4c205fc` | 118.3 |
| c3_realism_04 | `768,1344,24/1,124` | `aac,audio` | 5.166688 | 2,318,348 | `076ac63b950106eb1270` | 117.9 |

**3/3 objective pass**: 124 packets, 768x1344, 24/1, audio stream present, `',audio' in line` form.
Gate output as logged (`<run_dir>\status.log`): `OBJECTIVE ok` for all three at 14:41:08 / 14:43:06 /
14:45:04, `BATCH closed rc=0 … done=3/3`, lock ACQUIRED 13:51:27 / RELEASED 14:45:05. **Redos = 3**
(every `DONE` line says `retry=True`) - the L5 RESULT names the cause to the file and it is carded to
Max; the L6 item's own clause is 3/3 ok + 0 redos, so clause 2 was not met by L5 and is not met here.
Wall seconds are the delivered (retry) renders, `JOB end … secs=`. The Oct 30 same-geometry clips ran
126.0/134.5 s (a02/a03, `2026-10-30-bj-pov-three-methods-DONE.md`), so these are in the same band;
the comparison is uncontrolled (time of day, cache, LLM unloaded) - **no speed claim**.
Reproducibility fact from L5: the two attempts are byte-size-identical and sha256-DIFFERENT, so a clip
sha is a per-render fingerprint, never a reproducibility test, and equal size does not mean copied file.

## 2. Identity instrument (warn-only, never a pass; CPU SCRFD + ArcFace, no vision model, no GPU)

`C:\AI\community\notes\bj_pov_face_curve.py` (not edited; pointed by
`5slock\ralph-community\notes\_lora_l6\l6_face_curve.py`, 26 s per clip), reference
`C:\Users\derek\sydney\work\bj_pov_20261030\face_a.png` = 279,389 B sha256 `90ef7b874b780447…`, proven
**byte-identical** to the ComfyUI input copy the Oct 30 table used, so these cosines sit on the same
ruler as the a01/a02/a03 rows. Every 4th frame = 31 probes per clip.
JSON: `C:\AI\community\review\h3-lora-ab-2026-11-02\judge_out\face_curve_<cell>.json`.

| id | probes with a face | first frame with a face | ArcFace cos mean | cos min | face width px |
|---|---|---|---|---|---|
| a02 baseline (Oct 30, no LoRA) | 31 / 31 | 0 | 0.5495 | 0.4481 | 230-413 |
| c1_face_lora_07 (face LoRA 0.7) | 31 / 31 | 0 | **0.5697** | 0.4506 | 230-455 |
| c2_charswap_10 (charswap 1.0) | 31 / 31 | 0 | 0.5407 | 0.4473 | 230-420 |
| c3_realism_04 (realism 0.4) | 31 / 31 | 0 | 0.5505 | **0.4655** | 230-431 |

Deltas vs the a02 baseline (same seed, same prompt bytes, same start frame - one axis):
c1 **+0.0202 mean / +0.0025 min** (+3.7 % mean); c2 **-0.0088 mean / -0.0008 min**;
c3 **+0.0010 mean / +0.0174 min** (floor +3.9 %).
Reading of the numbers, not a judgment: the face LoRA at 0.7 raises the mean; the character-swap LoRA at
author strength 1.0 lowers it slightly; the realism LoRA at 0.4 leaves the mean where it is and lifts the
floor. All three keep a detected face in every probe from frame 0 - that is the a02 start-frame effect
the Oct 30 result already measured, and it is unchanged by any of the three LoRAs.
**Warn-only instrument: these are not scores, and no cell is crowned by them.**

## 3. Judge flags only (Max's scripts, not edited; driver `C:\AI\community\notes\h3_lora_ab_judge_check.py`)

Prechecks (`judge\prechecks.py`, CPU) 3/3; VLM (`judge\vlm_judge.py`, `qwen3vl_judge`, one call per
clip, GPU lock ACQUIRED/RELEASED by the driver pid 13528, 88.7 s/clip, model unloaded after, no other
model touched). Outputs `review\h3-lora-ab-2026-11-02\judge_out\{prechecks,vlm}\*.json`, grids saved.
Counts only, no quality claim:

| cell | precheck flags | cuts adaptive/content | dino prev_min | dino start_last | VLM flags | VLM answers (5 checks) |
|---|---|---|---|---|---|---|
| c1_face_lora_07 | `jump` | 0 / 0 | 0.4963 | 0.3001 | **none** | 5/5 non-defect |
| c2_charswap_10 | `jump` | 0 / 0 | 0.5709 | 0.3127 | **none** | 5/5 non-defect |
| c3_realism_04 | `jump` | 0 / 0 | 0.6183 | 0.2877 | **none** | 5/5 non-defect |

Total flag counts: `jump` 3/3 (0 cuts in all three - the jump is the motion onset, the same pattern as
the Oct 30 cells); `anatomy_defect` 0/3; `same_scene`/`same_people`/`start_kept` answered yes (no
defect) 3/3; `static_no_transition` not applicable (three-ref graph); `target_reached` not applicable
(no named target pose in this family). The instrument caveat is written into the manifest and every
output row, as the Oct 30 driver does.

## 4. Blind pack (staged locally; QNAP delivery blocked by approval, not by the pack)

Built by the `--pack` stage of `notes\h3_lora_ab_judge_check.py`: neutral ids from a **documented**
shuffle (`PACK_RNG_SEED = "h3-lora-ab-2026-11-02"`), key.csv opened only after the scores are in.
`C:\AI\community\review\h3-lora-ab-2026-11-02\pack\{a01,a02,a03}.mp4` + `key.csv` (sizes 2,558,369 /
2,318,348 / 2,304,919 B == the delivered clips; key names the cell, LoRA, strength, seed, prompt sha,
the measured face numbers and the flag lists).
**The instrument the item names, `C:\AI\community\assets\make_blind_pack.py`, does not exist** (searched:
no `make_blind_pack.py` and no `C:\AI\community\assets\` anywhere on the box; the shipped pack builders are
`notes\terrace_retest_judge_check.py` / `notes\terrace_retest_v2_judge_check.py`). I reused that pattern
in the new driver instead of inventing a fifth path.
Delivery to QNAP `pi-drop/h3-lora-ab-2026-11-02/` **did not run**: `pi_qnap.py` needs an approval this
non-interactive ralph pass cannot get ("requires approval, but no interactive UI is available"). Pack is
staged and the exact four `put` lines + `mkdir` are recorded in
`5slock\ralph-community\notes\_lora_l6\qnap_put.sh`. Blocker note + BLOCKED line:
`C:\AI\community\notes\2026-11-02-forge-blocker.md`.

## 5. What the A/B says (measurement, not a decision)

Under the a02 recipe, at fixed seed, one axis at a time, on this box:
- a face LoRA at 0.7 on top of the start-frame driver moved the ArcFace mean +3.7 % and the floor +0.6 %;
- a character-swap LoRA at author strength 1.0 moved identity slightly down (-1.6 % mean) - it is a
  swap-to-a-supplied-face tool and there is no swap target in this prompt, so the direction is consistent
  with the tool's purpose; this is an interpretation, not a measurement;
- a realism LoRA at 0.4 moved the mean +0.2 % (noise) and the floor +3.9 %.
None of the three changed the objective result, the face-detection rate (31/31 from frame 0), or the flag
profile (0 VLM flags, `jump` + 0 cuts on all three). The measured identity driver stays the start frame
(Oct 30: +35 % mean), not any LoRA at these strengths.
**Deciding KEEP is Derek's; the pack is for his eyes, and the four open asks are in
`C:\AI\community\notes\needs_derrick.md` (L6 card).**

## Files

Run dir `C:\AI\community\runs\h3_lora_ab_20261102\` (graphs, `graph_self_check.txt`, `status.log`,
`render_ok.json`, contact sheets; `runs/` is gitignored). Review stage
`C:\AI\community\review\h3-lora-ab-2026-11-02\` (`judge_manifest.json`, `judge_flags.json`,
`judge_out/{face_curve_*,prechecks,vlm}/`, `pack/`, `key.csv`). Instruments
`C:\AI\community\notes\{bj_pov_face_curve.py,h3_lora_ab_judge_check.py}` (the second is new, the first
unedited), driver `5slock\ralph-community\notes\_lora_l6\{l6_face_curve.py,objective.txt,prechecks.log,
vlm_and_pack.log,qnap_put.sh,l6_append.py}`. State of record:
`2026-11-02-lora-state-refresh.md`, `2026-11-02-l2-route1-downloads.md`, the L4/L5 RESULTs in
`fix_plan.md`, and `2026-10-30-bj-pov-three-methods-DONE.md` for the baseline rows.
Nothing deleted, moved, renamed or overwritten on the NAS, in `models\loras`, in `approved_characters`
(`INDEX.csv` untouched) or on `E:`; no model load, no render, no config write in this pass.
