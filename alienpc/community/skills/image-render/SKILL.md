---
name: image-render
description: Stage, build, render, and score FLUX.2 Klein 9B-KV + BFS (S2) still images and character pose/identity edits on AlienPc. Use when asked to generate or edit still images, run /render or scripts/make_render.py, score still outputs with face_scores(), or work with fictional adult character reference pools.
---

# Image Render (`image-render`)

> Render rules live in C:\AI\render\AGENTS.md; run render work from C:\AI\render.

## Character Rules & Sheets
- **Character sheets:** See [references/characters/README.md](references/characters/README.md) and OC/PixlStash identity rules in [../h3-parody-identity/SKILL.md](../h3-parody-identity/SKILL.md).
- `C:\AI\community\approved_characters` is add-only: never remove, move, or delete an image there.
- Folder-name only on Cond/character sheets (no celeb LoRAs there). Named adult INDEX+RefMod parodies → `h3-parody-identity` (dry-build first; X3 queues renders or local `run_queue.py` after his yes).
- Never open, read, or parse Derrick's Grok Imagine prompts or prompt sidecar files. Never open, read, or list `C:\Users\derek\sydney\` or any `talk-persona.md`.

## FLUX Stills Pipeline & Companion Skills
- **FLUX stills (Klein 9B-KV + BFS, S2 — locked default):** Load companion skill `alienpc-stills-pose-edit-prompting` for locked S2 prompt structure and graph details (`C:\AI\community\templates\flux_stills_s2_kv.api.json`, `C:\AI\community\templates\flux_stills_s2_bfs.api.json`, `C:\AI\community\templates\flux_stills_s2.README.md`).
- **FLUX.2 Klein / Miraclein 4.5 prompting & candidate templates (`M4` / `ST4` / `ST5`):** Load `flux-klein-prompting` for prompt text on T2I, Klein9 RefMod, ReferenceLatent single-change edits, RefControl poses (`refcontrol_v2_poses`), and H3Max start-stills (`768x1344` portrait). Candidate templates: `C:\AI\community\templates\flux_stills_t2i_klein.candidate.api.json`, `C:\AI\community\templates\flux_stills_pose_klein.candidate.api.json`, `C:\AI\community\templates\flux_stills_layout_klein.candidate.api.json` (plus M4 Miraclein 4.5 / Klein9 RefMod candidates). S2 remains the locked default until `M4` promotes Miraclein 4.5.
- **Build & run:** Build with the `/render` prompt (`C:\AI\community\agent-shared\prompts\render.md`) + `C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\make_render.py`.
- **ComfyUI endpoint:** ComfyUI only via llama-swap: `http://127.0.0.1:8080/comfyui/` (route `comfyui_auto`). Check status with:
  ```powershell
  C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\comfy_ctl.py status
  ```

## GPU Lock, Approval & Queue Rules
- **Ask Derrick first:** Ask Derrick before any render without his go, or before downloading new models/LoRAs.
- **Stage before asking for a go:** Prepare the order file, run dir, start/reference images, and `run_queue.py --dry-run` output before asking Derrick for a go. After the go, launch detached (`run_queue.py --detach`) and end your turn.
- **One GPU job at a time:** `run_graph_job.py` and `run_queue.py` take `C:\AI\locks\gpu-render.lock` (`rc 7 = GPU_BUSY`). While it is held: no subagents, no model loads, no second job, no `pi-computer-use`; read-only answers are fine.
- **Queue control & report:** `run_queue.py` is the only render path; a `STOP` file in the run dir halts the batch. Report in `<run_dir>\FORGE_REPORT.md`.

## Scoring & Verification
- **Stills scoring:** Six yes/no checks (`Identity`, `Face`, `Hands`, `Contact`, `Wardrobe`, `OverallQuality`) + `face_scores()` in `C:\AI\community\scripts\make_render.py` (`InsightFace`, CPU). Never crown `KEEP`; Derrick gives the 1–5 rating and `KEEP`.
- **Show an image in chat:** Call the `read` tool on the image file.
- **Adults-only tests:**
  ```powershell
  C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py
  ```
