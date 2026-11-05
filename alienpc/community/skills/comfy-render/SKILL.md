---
name: comfy-render
description: Run ComfyUI render workflows on AlienPc (face/LoRA video, stills) via http://127.0.0.1:8080/upstream/comfyui_auto. Uses API-format templates with parameters set per request before queueing. Use when asked to render B2 video with face LoRA or stills on AlienPc.
---

# ComfyUI Render (`comfy-render`)

Render rules (adults only, no real likeness, guard_ok, GPU lock) live in `C:\AI\render\AGENTS.md`.

## Workflow Execution
Calls ComfyUI via `http://127.0.0.1:8080/upstream/comfyui_auto` by reusing `C:\AI\community\scripts\comm.py`.
Never copies template workflows; points directly to canonical templates in `C:\AI\community\templates\`.
