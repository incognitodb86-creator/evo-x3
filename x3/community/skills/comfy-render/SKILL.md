---
name: comfy-render
description: Run ComfyUI render workflows on AlienPc (B2 video, stills) via llama-swap (standing policy route http://127.0.0.1:8080/comfyui/; comm.py:6 currently sets /upstream/comfyui_auto — discrepancy unresolved). Named INDEX + RefMod parodies defer to h3-parody-identity and submit_parody_run.py.
---

> EVO-X3: renders run on AlienPc ComfyUI. From the X3, queue only via `~/AI/render/x3/queue-remote.sh <run> --yes-derrick` after Derrick's yes. The PowerShell steps below are AlienPc-side.

# ComfyUI Render (`comfy-render`)

- **Named-parody precedence:** For named character, actor, or celebrity INDEX + RefMod parodies, defer to `h3-parody-identity` (`submit_parody_run.py` / `run_queue.py`).
- **Render & likeness rules:** Live in `/home/derekboone/AI/render/AGENTS.md` and `/home/derekboone/AI/comfy-alienpc/LANE_IMAGE_RULES.md` (adults 18+ only, `guard_ok` on every submit, one GPU job at a time via `gpu-render.lock`; approved-still character-sheet runs stay fictional folder-names only, while named parody runs follow `h3-parody-identity`).

## Workflow Execution
- **Legacy / do-not-call:** `scripts/render_workflow.py` is legacy: it bypasses `gpu-render.lock` and the locked baseline. Do not call it; all submissions go through `run_queue.py` or `submit_parody_run.py`.
- Standing policy route (`video-render` / `image-render` / prior `AGENTS.md`) is `http://127.0.0.1:8080/comfyui/`, whereas `/home/derekboone/AI/community/scripts/comm.py:6` currently sets `BASE = "http://127.0.0.1:8080/upstream/comfyui_auto"` (unresolved code-vs-policy discrepancy; configured `ignorePaths` alone does not prove identical wake behavior; never call backend port `:10004` directly).
Never copies template workflows; points directly to canonical templates in `/home/derekboone/AI/community/templates/`.
