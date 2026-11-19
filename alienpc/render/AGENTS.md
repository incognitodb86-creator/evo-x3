# AGENTS.md - Render executor (C:\AI\render, AlienPc RTX 5070 Ti 16 GB)

Global rules: `C:\Users\derek\.pi\agent\AGENTS.md`.
Old H3 prompt-writer book archived at `_archive\AGENTS.writer-book-20261119.md` (do not load).

## Role
- X3 writes prompts and builds render requests (`request.api.json` / `prompt.txt`).
- AlienPc is the render executor: run what is queued from X3; never rewrite or re-author prompts here.

## Execution
- Pre-built requests: load `video-render` (or `image-render` / `comfy-render` for stills/workflows) and run queued batches via `run_queue.py`.
- Workflow/template JSON work only when a brief asks for it (load `comfy-render`).
- Show a rendered still/frame inline with the `read` tool when reporting.

## GPU lock & safety
- While `C:\AI\locks\gpu-render.lock` is held, send no model requests and start no second GPU job; wait for the render to finish.
- One GPU job at a time; a render always wins over delegated work.
- Never queue a render without Derrick's go (or an approved X3/Max queued request).
- Never delete files without Derrick's OK (move to `_archive\`). Never touch `llama-swap`, `gpu_lock_gate`, `strata`, `pi-mobile`, or ComfyUI install/config unless a BRIEF from X3/Max with a Derrick id names the change.
- Never read, print, or log `.env` files, keys, tokens, `PIXL_KEY`, or `C:\Users\derek\sydney\`.
