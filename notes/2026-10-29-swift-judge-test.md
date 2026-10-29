# Swift as clip judge - test only (2026-10-29, 2:47-3:20 PM CT)

Derrick's ask: run the judge test with the box default `coding_swift15_iq3s_esp` (Swift-Qwen3.8-Flash-Next IQ3_S + ESP,
served by Strata, pictures through `strata-vision.exe`) on the same 36 p15v2 clips, so it can be compared with
`qwen3vl_judge`. **Test only**: the judge default is not changed, nothing is wired into a workflow, no render, no
delete, no KEEP. Baseline: commit `5f9d97a`. Max scores both runs against the same labels and the 3-fold held-out split.

## 1. Script changes (the only code change in this task)

`judge\vlm_judge.py` and `judge\vlm_variants.py` gained two options and nothing else moved:

- `--model` - default stays `qwen3vl_judge` (and `out\vlm` / `out\audit2` stay the default folders). The per-model
  unload now unloads **the model named by `--model`**, still never the global `/unload`.
- `--out` - output folder; a relative path resolves against the current directory (both runs used absolute paths).

Kept byte-for-byte: the prompt text, the five checks and their defect answers, the 2x4 storyboard + full-size last
frame, the zoom frames, `response_format json_schema` (strict, reason maxLength 200), `max_tokens 2048`,
`temperature 0.0`, `seed 42` (variants), `enable_thinking: false`. Unchanged behaviour for the Qwen default:
`git diff` is only the option plumbing plus three test-only robustness guards:

1. `parse_json` - strict `json.loads`; **only** if that fails, take the first balanced JSON object (the same rule the
   server's own extractor uses) and write `"parse":"extracted"` so it is visible, never silent.
2. logprobs failures are caught -> `p_defect` becomes `{}` instead of losing a good answer.
3. `vlm_judge.py`: a per-clip `try/except` writes an `{"error": ...}` record and continues, so one bad clip cannot
   cost the whole 36-clip run and the GPU lock. `vlm_variants.py` already had this. Both now record `"model"` and,
   in the variants, a per-clip `"secs"` (the shipped audit2 Z run predates this, so it has no per-clip times).

## 2. Smoke test (1 clip) - `.venv\Scripts\python.exe vlm_judge.py --match p15v2_a_w2_img_gi201 --model coding_swift15_iq3s_esp --out judge\out\swift_smoke`

14:47:34 -> 14:48:02 CT, 27 s under lock, 25.4 s in the call. Swift **accepted the three images and the
`json_schema` response_format as sent**: `finish: stop`, `parse: direct`, all 5 checks answered, 25 words-reason style,
flags `['start_kept']`. **No fallback to prompt-JSON was needed**, so the prompt was not changed.

What Strata does with `json_schema` (from `C:\AI\strata-0.2.7\serve\structured.py`, confirmed live): it appends an
"OUTPUT FORMAT REQUIREMENT ... JSON Schema" directive to the system turn and validates the reply - the native engine has
no grammar decoder, so the schema is **not** decoding-constrained the way llama.cpp constrains `qwen3vl_judge`. A failed
generation is an error, never a silent retry. `jsonschema` is **not installed in the Strata venv**, so the check is only
"the answer is one JSON object". Client-side check of all 108 Swift calls (`check_swift_conformance.py`, untracked):
**0 schema violations** - required keys, `yes`/`no` only, no extra fields, every reason <= 200 chars. Same check on the
Qwen folders: 0 violations. `parse: direct` 108/108, no truncation (`finish: stop` in all 108), no errors, no retry.
Swift returned usable logprobs on **108/108** calls (the shipped `out\vlm` predates logprobs and has none),
but read them with care: Strata rewrites the content for `json_schema`, so its token/answer alignment is a documented
caveat - do not use Swift's `p_defect` side by side with Qwen's.

## 3. The two full runs (same 36 clips, same frames, same prompts)

```
.venv\Scripts\python.exe -u vlm_judge.py --match p15v2_ --model coding_swift15_iq3s_esp --out C:\AI\community\judge\out\swift_a
.venv\Scripts\python.exe -u vlm_variants.py --variants Z --model coding_swift15_iq3s_esp --out C:\AI\community\judge\out\swift_z
```

GPU: `gpu_guard.ps1` = IDLE before both, `gpu_lock.ps1 -Acquire` pid 24424 (14:49:20) and pid 32344 (15:02:46),
`-Release` at 15:01:27 and 15:19:54. One job at a time, no render was running, nothing was preempted, the lock was
released at the end of each run and only the Swift model was unloaded.

**Same-input proof (objective):** all 36 storyboard JPEGs in `out\swift_a` are byte-identical to `out\vlm`
(SHA-256), and every zoom frame index in `out\swift_z\Z` equals the one in `out\audit2\Z`. The prompt text and the
target-pose lines are read from the same files by the same code. So the two judges saw the same pictures.

Wall time (`secs` per clip is the HTTP call; the "under lock" total also covers the lock handshake):

| | per clip min / median / max | sum over 36 clips | under lock |
|---|---|---|---|
| Qwen `out\vlm` (baseline) | 3.9 / 4.4 / 10.5 s | 163.6 s | ~9 min GPU for 4 prompt runs + smoke (audit note) |
| **Swift `out\swift_a`** | **18.7 / 19.0 / 25.5 s** | **708.3 s** | **726 s** |
| Qwen `out\audit2\Z` | not recorded (predates `secs`) | 181 s (variant total, `out\audit2\run.log`) | - |
| **Swift `out\swift_z\Z`** | **26.8 / 27.0 / 33.7 s** | **997.5 s** | **998 s** |

Swift is 4.3x slower per clip on the 3-image call and 5.5x on the 2-call zoom (the CPU picture reader is the cost:
`vision.gpu = false`, `max_tokens 3000` per picture, 10 threads). The `capswift` clips are the slowest in both runs
(~25 s / ~33 s, longest prompt). Cost of the polite unload: Swift is the box's default coding model and the model this
session runs on, so every run end forced a reload. Nothing measured a cold start - the first clip of each run cost
+6 s over the median, and the reload between runs stayed inside the ~1.5 min between my tool calls.

## 4. Per-clip results

Flags only; no KEEP. `A` = `vlm_judge` (5 checks), `Z` = worst-frame zoom (2 checks). Column key order:
`same_scene same_people start_kept target_reached anatomy_defect`; `F` after the dots = that model flagged the clip,
`F` in a Z column = the README rule (a defect answer on any zoomed frame), with the checks named in alphabetical order. `A+Z` = the shipped
two-tier FLAG rule. Times in seconds per clip.

| clip | qwen A | swift A | qwen Z | swift Z | A+Z qwen | A+Z swift | q secs | swift secs | swiftZ secs |
|---|---|---|---|---|---|---|---|---|---|
| a_w2_capjoy_gi102_missionary | .FF.. F | .FF.. F |  |  | F | F | 4.2 | 19.0 | 27.2 |
| a_w2_capjoy_gi201_against_wall | ..... | .F... F | | F same_scene,anatomy_defect | | F | 4.6 | 19.0 | 27.3 |
| a_w2_capswift_gi102_missionary | ..... | ..... | | | | | 4.6 | 19.2 | 27.0 |
| a_w2_capswift_gi201_against_wall | ..... | ..... | | | | | 4.3 | 18.9 | 27.0 |
| a_w2_img_gi102_missionary | ..... | ..... | | | | | 4.5 | 19.0 | 27.0 |
| a_w2_img_gi201_against_wall | ..... | ..F.. F | | | | F | 4.3 | 18.9 | 27.1 |
| a_w7_capjoy_gi102_missionary | ..F.. F | .FF.. F | | F anatomy_defect | F | F | 4.8 | 19.1 | 26.9 |
| a_w7_capjoy_gi201_against_wall | ..... | .F... F | | F anatomy_defect | | F | 4.3 | 19.3 | 27.1 |
| a_w7_capswift_gi102_missionary | ..... | ...FF F | | | | F | 10.5 | 25.3 | 33.2 |
| a_w7_capswift_gi201_against_wall | ..F.. F | ..F.. F | | | F | F | 4.5 | 24.8 | 32.7 |
| a_w7_img_gi102_missionary | F.FF. F | FFFFF F | F same_scene | F same_scene,anatomy_defect | F | F | 4.0 | 19.3 | 27.0 |
| a_w7_img_gi201_against_wall | ..F.. F | .FF.. F | | F anatomy_defect | F | F | 4.3 | 18.9 | 27.1 |
| a_w8_capjoy_gi102_missionary | ..... | ..... | | | | | 4.5 | 19.1 | 27.2 |
| a_w8_capjoy_gi201_against_wall | ..... | ..... | | | | | 4.3 | 18.7 | 27.2 |
| a_w8_capswift_gi102_missionary | ..... | ..... | | | | | 4.5 | 18.9 | 27.2 |
| a_w8_capswift_gi201_against_wall | ..... | ..... | | F anatomy_defect | | F | 4.3 | 18.7 | 27.0 |
| a_w8_img_gi102_missionary | ..... | ..... | | | | | 4.3 | 19.1 | 26.9 |
| a_w8_img_gi201_against_wall | ..... | ..F.. F | | | | F | 4.3 | 19.1 | 27.0 |
| b_w2_capjoy_gi102_missionary | ..... | .F... F | | | | F | 4.1 | 19.0 | 27.1 |
| b_w2_capjoy_gi201_against_wall | ..... | ..... | | | | | 4.5 | 18.7 | 26.8 |
| b_w2_capswift_gi102_missionary | ..... | ..... | | | | | 4.4 | 18.9 | 27.0 |
| b_w2_capswift_gi201_against_wall | ..... | ...FF F | | | | F | 4.4 | 19.0 | 27.2 |
| b_w2_img_gi102_missionary | ..... | ..... | | F anatomy_defect | | F | 4.5 | 19.0 | 27.0 |
| b_w2_img_gi201_against_wall | ..... | ...FF F | | F same_scene,anatomy_defect | | F | 4.3 | 19.4 | 27.0 |
| b_w7_capjoy_gi102_missionary | ..... | .F... F | | F anatomy_defect,same_scene | | F | 3.9 | 18.9 | 27.2 |
| b_w7_capjoy_gi201_against_wall | ..... | ..... | | F anatomy_defect | | F | 4.4 | 19.1 | 27.0 |
| b_w7_capswift_gi102_missionary | ..F.. F | ...F. F | | | F | F | 4.5 | 24.6 | 32.6 |
| b_w7_capswift_gi201_against_wall | ...F. F | ...FF F | | | F | F | 4.4 | 25.5 | 33.7 |
| b_w7_img_gi102_missionary | ..F.. F | ...FF F | | F anatomy_defect | F | F | 4.6 | 18.8 | 27.1 |
| b_w7_img_gi201_against_wall | ..... | ..... | | | | | 4.4 | 18.9 | 26.8 |
| b_w8_capjoy_gi102_missionary | ..F.. F | .F... F | | | F | F | 4.1 | 18.9 | 26.8 |
| b_w8_capjoy_gi201_against_wall | ..F.. F | ..... | | F same_scene,anatomy_defect | F | F | 4.6 | 19.5 | 26.9 |
| b_w8_capswift_gi102_missionary | ..... | ...FF F | | | | F | 4.3 | 19.0 | 27.0 |
| b_w8_capswift_gi201_against_wall | ...F. F | ...FF F | | | F | F | 4.2 | 19.0 | 26.8 |
| b_w8_img_gi102_missionary | ..... | ..... | | | | | 4.4 | 18.9 | 26.9 |
| b_w8_img_gi201_against_wall | ..... | ..... | F same_scene | F same_scene,anatomy_defect | F | F | 4.5 | 18.9 | 27.5 |

(36 clips; `out\swift_compare.csv` is the machine-readable version of this table, one row per clip with every field.)
The table was re-checked by hand against the data with `check_note_table.py` (untracked): it re-derives every column
from the JSON files and diffs it against the markdown - 36 rows, 0 mismatches, no clip left out.

## 5. Counts (flags only - Max scores the labels, this is not a score)

| tier | Qwen (baseline) | Swift (this test) |
|---|---|---|
| `vlm_judge` alone | 11/36 flagged | **20/36 flagged** |
| zoom `Z` alone | 2/36 | **13/36** |
| `vlm_judge` OR `Z` (the shipped FLAG rule) | 12/36 | **25/36** |

Answered-as-a-defect per check, all 36 clips: Qwen `same_scene 1, same_people 1, start_kept 9, target_reached 3,
anatomy_defect 0`; Swift `same_scene 1, same_people 9, start_kept 7, target_reached 9, anatomy_defect 8`. Zoom: Qwen
`same_scene 2, anatomy_defect 0`; Swift `same_scene 6, anatomy_defect 13`. Per-check agreement Swift vs Qwen:
`same_scene 36/36, same_people 28/36, start_kept 30/36, target_reached 30/36, anatomy_defect 28/36`.
Reason text length is comparable (median 94 vs 87 chars, max 134 vs 136), so Swift is not answering shorter.

Read it as: Swift is **not** format-limited (schema clean, no truncation, no fallback prompt needed, logprobs present) -
it is **looser on the questions**. Its 9 `same_people` and 9 `target_reached` flags against Qwen's 1 and 3 are where the
extra flags come from, and the zoom turns into a real flag source (13/36) because Swift answers `anatomy_defect: yes`
where Qwen never did. On the one clip both models flagged in every way (`a_w7_img_gi102`) they agree. Whether those
extra flags are catches or false alarms is Max's label run to say, on the same labels and the 3-fold held-out split
(Qwen reference: 8/14 bad + 3/22 false for the current prompt, 9/14 + 3/22 with the zoom).

## 6. Files

- `judge\out\swift_smoke\` (1 clip smoke), `judge\out\swift_a\` (36 JSON + 36 storyboard jpgs),
  `judge\out\swift_z\Z\` (36 JSON - note the extra `Z` folder, the same layout as `out\audit2\Z`).
- `judge\out\swift_a.log`, `swift_z.log`, `swift_smoke.log`, `swift_summary.txt` (this note's tables),
  `swift_compare.csv` (per-clip machine-readable, 30 columns).
- Untracked test-only helpers I wrote for this note: `judge\summarize_swift_run.py`, `judge\check_swift_conformance.py`,
  `judge\check_note_table.py`.
- Committed: `judge\vlm_judge.py`, `judge\vlm_variants.py`, this note. Nothing was deleted, no KEEP, no render,
  no default change, no README change (the README still describes `qwen3vl_judge` as the judge).
