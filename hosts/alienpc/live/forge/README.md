# Forge working root (C:\Users\derek\forge -> C:\Users\derek\5slock)

`C:\Users\derek\forge` is an NTFS junction to `C:\Users\derek\5slock` and is the working root for the Forge agent (pi coding agent and Ralph loop).

## Paths and lanes
- `C:\Users\derek\forge` -> junction to `C:\Users\derek\5slock` (canonical working path for Forge).
- `C:\Users\derek\sydney` -> separate private talk lane directory (not a junction to `5slock`), with its own `AGENTS.md` and `ralph\` subfolder.
- `C:\AI\render` -> render executor lane root (`C:\AI\render\AGENTS.md`; queued requests come from X3).

## Which ralph folder is live
- ralph-community\  LIVE loop: ralph.ps1, PROMPT.md, fix_plan.md, specs\, notes\, logs\ (global AGENTS.md is C:\Users\derek\.pi\agent\AGENTS.md; there is no AGENTS.md in ralph-community\ or 5slock\)
- ralph\           legacy (kept, not used)
- ralph-forgeup\    legacy (kept, not used)

## Key folders
- runs\       per-render run dirs (request.api.json, status.log)
- workflows\  ComfyUI workflow files
- refs\, approved_characters\, stills\  reference and start images
- notes\      older notes (loop notes live in ralph-community\notes)
- logs\       logs
- archive\    archived files

## Elsewhere
- Index of everything: C:\AI\community\notes\INDEX.md
- Skills: `C:\AI\community\skills` and `C:\Users\derek\.pi\agent\skills`
  - Keep linked on AlienPc: `comfy-render`, `video-render`, `image-render`, `h3-hc-render` (execution parts), `ralph-loop`, `rea-video`.
  - Unlink on AlienPc (move links, keep targets): `h3-prompting`, `h3-max-ref2va-prompt`, `h3-parody-identity`, `alienpc-hardcore-i2v-director`, `alienpc-stills-pose-edit-prompting`.
- Rendered clips: C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\<tag>\
