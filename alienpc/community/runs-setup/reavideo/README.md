# REA-Video run setup (AlienPc) — val30s v1 + v2

Copied 2026-11-20 ~8:45 AM CT (America/Chicago) from AlienPc via Grok Bot local execution (Derrick t3020u). Read-only copy; nothing on AlienPc was changed.
Result record: [records/BENCH-ALIENPC-1/REA-VIDEO-VAL30S-RESULT.md](../../../../records/BENCH-ALIENPC-1/REA-VIDEO-VAL30S-RESULT.md).

The task named `C:\AI\community\runs\reavideo_hotel_vlm2_val30s` (and `_v2`). Those folders do not exist on AlienPc. The real run trees are
`C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s` and `..._v2` (`forge` is a junction to `C:\Users\derek\5slock`). The QNAP copies
(`\\NAS4CBE37.local\renders\runs\reavideo_hotel_vlm2_val30s*`, mapped `R:\runs`) hold only the MP4s.
The fill/launch scripts were never filed; they were found only in `%TEMP%` (`rv30_stage\`, `rv30v2\`, `rv30v2_diag_audio\`) and are copied here so they are not lost.

## Layout

| Here | Source on AlienPc |
|---|---|
| `run-trees/reavideo_hotel_vlm2_val30s/` | `C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\` (non-media only: manifest, `request.api.json` / `packNN.api.json` graphs, stems, QA facts, render logs) |
| `run-trees/reavideo_hotel_vlm2_val30s_v2/` | `...\out\hotel_vlm2_val30s_v2\` (same) |
| `breakdown/hotel_vlm2/breakdown.json` | `...\out\hotel_vlm2\breakdown.json` (the REA breakdown both runs were built from) |
| `scripts/v1_runners/` | `%TEMP%\rv30_stage\runners\*.py` + `%TEMP%\rv30_{check_imports,launch_bridge,wait_and_bridge}.py` (v1) |
| `scripts/v2/` | `%TEMP%\rv30v2\*.py` (incl. `rv30v2_fill_graphs.py`, `rv30v2_launch_queue.py`, `struct_bind.py`, `struct_s2.py`) |
| `scripts/diag_audio/` | `%TEMP%\rv30v2_diag_audio\*.py` + `compare_fast.json` (pack audio-duplication diagnosis; WAV/AAC not copied) |
| `scripts/bridge/` | `%TEMP%\rv30_stage\scripts\h3max_bridge\src\h3max_bridge\` — the bridge copy staged for v1; differs from `x3/community/scripts/h3max_bridge/` on mono |
| `install/` | REA-Video install: `pyproject.toml`, `requires.txt`, `HANDOFF-forge.md` (install record), `capabilities/` (incl. `models/video.yaml`), repo state (`C:\Users\derek\forge\tools\rea-video` @ `e3858539`, editable install, Python 3.12), `pip-freeze-python312.txt`, user prefs `C:\Users\derek\.rea-video\prefs.json` |

Not copied (duplicates already on mono, same sha256): `make_b2_request.py` (= `x3/community/scripts/make_b2_request.py`), `beta7_convert.py` (= `x3/community/scripts/parody/beta7_convert.py`). The staged `scripts/parody/*` copies in `rv30_stage` are the community pipeline files already on mono.

## Redactions and exclusions

- Every prompt and dialogue/on-screen text field is replaced with `<redacted prompt, N chars>`: graph `c0.inputs.prompt`, manifest `clips[].prompt`, each `prompt.txt` (whole file), and in `breakdown.json` the `video_prompt*`, `image_prompt`, `draft`, `action`, `text`/`texts`, `overlay_text`, `on_screen_text`, OCR/subtitle/lyrics/narration/`point(s)`/`beat`/`copy`/`highlights` fields and `whole_video_vlm.summary`. 2,367 fields total.
- Prompt word-hit lists in manifest gate reports (`oral_noun_hits`) are replaced with `<redacted prompt words, N items>`. No RefMod trigger words remain (they only lived in the prompts). RefMod file stems and subject names (FCSydny, Adam Jensen) are kept; they are already in mono records.
- Excluded: all media (MP4/WAV/AAC/M4A/JPG/PNG), `.pyc`, `vlm_cache/`, the per-shot REA `video/` and `survey/` folders, and the two REA env files `C:\Users\derek\.rea-video\env\vlm-*.env` (secrets; names listed in `install/rea-video-user-env-EXCLUDED.txt`).
- Scripts read the LLM key from env/file at run time; no key is in these files. gitleaks 8.30.1 `--no-git`: no leaks.
- Paths still point at `C:\Users\derek\forge\...` and `C:\Users\derek\HardcoreNSFW-TestRuntime\...`; they are records, not runnable from here.
