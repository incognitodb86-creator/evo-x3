---
name: image-render
description: Stage, build, render, and score FLUX.2 Klein 9B-KV + BFS (S2) still images and character pose/identity edits on AlienPc. Use when asked to generate or edit still images, run /render or scripts/make_render.py, score still outputs with face_scores(), or work with fictional adult character reference pools.
---

> EVO-X3: renders run on AlienPc ComfyUI over Tailscale Serve (`https://alienpc.tailf242b2.ts.net:8446`). From the X3, dry-build first and queue only via `bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick` after Derrick's yes.
# Image Render (`image-render`)

> Render rules live in ~/AI/render/AGENTS.md; run render work from ~/AI/render.

## Character Rules & Sheets
- **Character sheets:** See [references/characters/README.md](references/characters/README.md) and OC/PixlStash identity rules in [../h3-parody-identity/SKILL.md](../h3-parody-identity/SKILL.md).
- `~/AI/community/approved_characters` is add-only: never remove, move, or delete an image there.
- Folder-name only on Cond/character sheets (no celeb LoRAs there). Named adult INDEX+RefMod parodies → `h3-parody-identity` (dry-build first, then `queue-remote.sh` after his yes).
- Never open, read, or parse Derrick's Grok Imagine prompts or prompt sidecar files. Never open, read, or list `~/AI/sydney/` or any `talk-persona.md`.

## FLUX Stills Pipeline & Companion Skills
- **FLUX stills (Klein 9B-KV + BFS, S2 — locked default):** Load companion skill `alienpc-stills-pose-edit-prompting` for locked S2 prompt structure and graph details (`~/AI/community/templates/flux_stills_s2_kv.api.json`, `~/AI/community/templates/flux_stills_s2_bfs.api.json`, `~/AI/community/templates/flux_stills_s2.README.md`).
- **FLUX.2 Klein / Miraclein 4.5 prompting & candidate templates (`M4` / `ST4` / `ST5`):** Load `flux-klein-prompting` for prompt text on T2I, Klein9 RefMod, ReferenceLatent single-change edits, RefControl poses (`refcontrol_v2_poses`), and H3Max start-stills (`768x1344` portrait). Candidate templates: `~/AI/community/templates/flux_stills_t2i_klein.candidate.api.json`, `~/AI/community/templates/flux_stills_pose_klein.candidate.api.json`, `~/AI/community/templates/flux_stills_layout_klein.candidate.api.json` (plus M4 Miraclein 4.5 / Klein9 RefMod candidates). S2 remains the locked default until `M4` promotes Miraclein 4.5.
- **Build & run:** Build with the `/render` prompt (`~/AI/community/agent-shared/prompts/render.md`) + `~/AI/render/x3/.venv/bin/python ~/AI/community/scripts/make_render.py`.
- **ComfyUI endpoint:** On X3, AlienPc ComfyUI is over Tailscale Serve `https://alienpc.tailf242b2.ts.net:8446` (llama-swap `comfyui_auto`; AlienPc local: `http://127.0.0.1:8080/comfyui/`). Check non-waking status with:
  ```bash
  curl -sS -o /dev/null -w "%{http_code}\n" https://alienpc.tailf242b2.ts.net:8446/system_stats
  # 409 = ComfyUI unloaded/idle; 200 = loaded. Or dry-probe:
  bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick --dry-run
  ```

## GPU Lock, Approval & Queue Rules
- **Ask Derrick first:** Ask Derrick before any render without his go, or before downloading new models/LoRAs.
- **Stage before asking for a go:** Prepare the order file, run dir, start/reference images, and `run_queue.py --remote --dry-run` output before asking Derrick for a go. After his yes, queue via `bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick`.
- **One GPU job at a time:** On the X3, `~/AI/locks/gpu-render.lock` (`flock`) is only a local single-submitter lock — AlienPc's `C:\AI\locks\gpu-render.lock` is not visible here. Before queueing via `queue-remote.sh`, verify AlienPc's GPU and lease are free (do not rely on the local X3 lock file alone). While a remote job runs: no second render job; read-only answers are fine.
- **Queue control & report:** `queue-remote.sh <run_dir> --yes-derrick` drives `run_queue.py --remote --detach`; a `STOP` file in the run dir halts the batch. Report in `<run_dir>/FORGE_REPORT.md`.

## Scoring & Verification
- **Stills scoring:** Six yes/no checks (`Identity`, `Face`, `Hands`, `Contact`, `Wardrobe`, `OverallQuality`) + `face_scores()` in `~/AI/community/scripts/make_render.py` (`InsightFace`, CPU). Never crown `KEEP`; Derrick gives the 1–5 rating and `KEEP`.
- **Show an image in chat:** Call the `read` tool on the image file.
- **Adults-only tests:**
  ```bash
  ~/AI/render/x3/.venv/bin/python -m pytest -q ~/AI/community/scripts/tests/test_p6_review.py ~/AI/community/scripts/tests/test_guard_scope.py
  ```
