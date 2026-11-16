---
name: image-render
description: Stage, build, render, and score FLUX.2 Klein 9B-KV + BFS (S2) still images and character pose/identity edits on AlienPc. Use when asked to generate or edit still images, run /render or scripts/make_render.py, score still outputs with face_scores(), or work with fictional adult character reference pools.
---

> EVO-X3: renders run on AlienPc ComfyUI. From the X3, queue only via `~/AI/render/x3/queue-remote.sh <run> --yes-derrick` after Derrick's yes. The PowerShell steps below are AlienPc-side.
# Image Render (`image-render`)

> Render rules live in /home/derekboone/AI/render/AGENTS.md; run render work from /home/derekboone/AI/render.

## Character Rules & Sheets
- **Character sheets:** Load `references/characters/<name>.md` (e.g. [references/characters/sydney.md](references/characters/sydney.md); index in [references/characters/README.md](references/characters/README.md)).
- `/home/derekboone/AI/community/approved_characters` is add-only: never remove, move, or delete an image there.
- Folder-name only on Cond/character sheets (no celeb LoRAs there). Named adult INDEX+RefMod parodies → `h3-parody-identity` (his ask = go).
- Never open, read, or parse Derrick's Grok Imagine prompts or prompt sidecar files. Never open, read, or list `C:\Users\derek\sydney\` or any `talk-persona.md`.

## FLUX Stills Pipeline & Companion Skills
- **FLUX stills (Klein 9B-KV + BFS, S2):** Load companion skill `alienpc-stills-pose-edit-prompting` for prompt structure and graph details (`/home/derekboone/AI/community/templates/flux_stills_s2_kv.api.json`, `/home/derekboone/AI/community/templates/flux_stills_s2_bfs.api.json`, `/home/derekboone/AI/community/templates/flux_stills_s2.README.md`).
- **Build & run:** Build with the `/render` prompt (`/home/derekboone/AI/community/agent-shared/prompts/render.md`) + `/home/derekboone/AI/director/.venv/Scripts/python.exe /home/derekboone/AI/community/scripts/make_render.py`.
- **ComfyUI endpoint:** ComfyUI only via llama-swap: `http://127.0.0.1:8080/comfyui/` (route `comfyui_auto`). Check status with:
  ```powershell
  /home/derekboone/AI/director/.venv/Scripts/python.exe /home/derekboone/AI/community/scripts/comfy_ctl.py status
  ```

## GPU Lock, Approval & Queue Rules
- **Ask Derrick first:** Ask Derrick before any render without his go, or before downloading new models/LoRAs.
- **Stage before asking for a go:** Prepare the order file, run dir, start/reference images, and dry-run output before asking Derrick for a go. After the go, the only step is the launch line.
- **One GPU job at a time:** `run_graph_job.py`, `run_queue.py`, and `make_render.py` take `/home/derekboone/AI/locks/gpu-render.lock` (`rc 7 = GPU_BUSY`). While it is held: no subagents, no model loads, no second job, no `pi-computer-use`; read-only answers are fine.
- **Queue control & report:** `run_queue.py --detach`; a `STOP` file in the run dir halts the batch. Report in `<run_dir>\FORGE_REPORT.md`.

## Scoring & Verification
- **Stills scoring:** Six yes/no checks (`Identity`, `Face`, `Hands`, `Contact`, `Wardrobe`, `OverallQuality`) + `face_scores()` in `/home/derekboone/AI/community/scripts/make_render.py` (`InsightFace`, CPU). Never crown `KEEP`; Derrick gives the 1–5 rating and `KEEP`.
- **Show an image in chat:** Call the `read` tool on the image file.
- **Adults-only tests:**
  ```powershell
  /home/derekboone/AI/director/.venv/Scripts/python.exe -m pytest -q /home/derekboone/AI/community/scripts/tests/test_p6_review.py /home/derekboone/AI/community/scripts/tests/test_guard_scope.py
  ```
