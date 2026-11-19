---
name: comfy-render
description: Run ComfyUI render workflows on AlienPc (B2 video, stills) via llama-swap (standing policy route http://127.0.0.1:8080/comfyui/; comm.py:6 currently sets /upstream/comfyui_auto — discrepancy unresolved). Named INDEX + RefMod parodies defer to h3-parody-identity and render_writer_pipeline.py.
---

# ComfyUI Render (`comfy-render`)

- **Named-parody precedence:** For named character, actor, or celebrity INDEX + RefMod parodies, defer to `h3-parody-identity` (`render_writer_pipeline.py` / `run_queue.py`; AlienPc backup writer writes prompts dry, X3 queues renders or local `run_queue.py` after Derrick's yes).
- **Render & likeness rules:** Live in `C:\AI\render\AGENTS.md` and `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\LANE_IMAGE_RULES.md` (adults 18+ only, `guard_ok` on every submit, one GPU job at a time via `C:\AI\locks\gpu-render.lock`; approved-still character-sheet runs stay fictional folder-names only, while named parody runs follow `h3-parody-identity`).

## Workflow Execution
- **Legacy / do-not-call:** `scripts/render_workflow.py` is legacy: it bypasses `gpu-render.lock` and the locked baseline. Do not call it; all submissions go through `run_queue.py` (directly or via `render_writer_pipeline.py --queue --yes-derrick`).
- Standing policy route (`video-render` / `image-render` / prior `AGENTS.md`) is `http://127.0.0.1:8080/comfyui/`, whereas `C:\AI\community\scripts\comm.py:6` currently sets `BASE = "http://127.0.0.1:8080/upstream/comfyui_auto"` (unresolved code-vs-policy discrepancy; configured `ignorePaths` alone does not prove identical wake behavior; never call backend port `:10004` directly).
Never copies template workflows; points directly to canonical templates in `C:\AI\community\templates\`.
