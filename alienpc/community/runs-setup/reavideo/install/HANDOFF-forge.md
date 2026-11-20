# rea-video on AlienPc (Forge) — install record, 2026-11-17

Upstream: https://github.com/JuneYaooo/rea-video (cloned --depth 1 here).
Purpose: reverse-engineer a video shot by shot (filmed / AI / coded), output a
report.html + VIDEO.md breakdown package, then plan a remake.

## What is installed

- CLI `rea-video` (+ `videomd`) — editable install of this repo, extras `[ocr]`,
  Python 3.12.10 (`C:\Program Files\Python312`).
  Scripts land in `C:\Users\derek\AppData\Roaming\Python\Python312\Scripts`,
  which was **added to the user PATH** (first entry). Open a new shell, or use:
  `$env:Path = "C:\Users\derek\AppData\Roaming\Python\Python312\Scripts;" + $env:Path`
- Skill for pi: junction `C:\Users\derek\.pi\agent\skills\rea-video`
  → `C:\Users\derek\forge\tools\rea-video\skills\rea-video`. SKILL.md is Chinese;
  it drives the agent workflow (survey → decompose → summary → review → apply-review).
- Prefs (`C:\Users\derek\.rea-video\prefs`): `lang en`, `reviewer pi-forge`,
  note = no VLM configured, agent does the visual review.

## Box facts

- ffmpeg 8.0.1 and ffprobe already on PATH — fine.
- cv2 conflict: `[ocr]` pulls in `opencv-python` which fights
  `opencv-python-headless` over the same `cv2` dir. Fixed with
  `pip uninstall -y opencv-python` then
  `pip install --force-reinstall --no-deps "opencv-python-headless>=4.8,<5"`.
  Re-run that pair after any reinstall of `[ocr]`.
- Unrelated warning: `iopaint 1.6.0` wants Pillow 9.5 / transformers — pre-existing,
  untouched.

## Not configured (deliberate)

- **VLM**: needs OpenAI-compatible vision endpoint via
  `REA_VLM_BASE_URL` / `REA_VLM_API_KEY` / `REA_VLM_MODEL` (or `--env-file`).
  Tools-only mode is offline and free, ~99% on original files; platform-recompressed
  downloads need a VLM or my own image review (`review` + `apply-review`).
- **ASR** (`pip install sherpa-onnx`) for spoken lines with no burned subtitles.
- **capsule-cinema** repo — needed only for `remake-plan` / `remake-run` /
  `capsule-draft`. Not installed.

## Verified

- `rea-video --help`, `prefs`, `models` (79 lines; includes `minimax-h3`,
  `minimax-h3-max`, `minimax-h3-image` — our own model is in its capability map).
- `rea-video probe clips/R2_DarkRoast_S1.mp4` → AI generation, MiniMax/Hailuo
  metadata signature, 768x1120@24. Correct for a H3 clip from this box.

## First real run (not done yet — GPU/audio model downloads)

```powershell
rea-video decompose <video>.mp4 -o out\<name> --lang en
rea-video summary out\<name>\breakdown.json   # check the "VLM:" line
```

First `decompose` auto-downloads ~67 MB UVR MDX-Net + ~149 MB BandIt v2 into
`~\.cache\rea-video\models` (CPU only, no GPU lock needed). Add `--no-stems
--no-packaging` for a fast text-only pass. Outputs: `report.html`,
`breakdown.json`, `VIDEO.md` + `video/` (read the VIDEO.md card first, never
breakdown.json), `storyboard.jpg`, per-shot contact sheets in `shots/`.
