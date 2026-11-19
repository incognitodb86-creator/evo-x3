---
name: alienpc-stills-pose-edit-prompting
description: Write FLUX stills prompts on AlienPc for the adopted S2 workflow (Klein 9B-KV pass 1, then BFS head-swap pass 2). Use before any FLUX.2 Klein still, pose/angle/scene change of an approved still, or start frame for a Max clip. Not for video prompts (h3-prompting).
---
# AlienPc FLUX stills prompting (S2, 2026-10-31)

> For Miraclein 4.5, Klein9 RefMod, RefControl pose/layout, and general FLUX.2 Klein still prompts, use [flux-klein-prompting](../flux-klein-prompting/SKILL.md).
> This file keeps the locked Oct 31 S2 (`flux-2-klein-9b-kv-fp8` + `bfs_head_v1`) rules unchanged until `M4` promotes Miraclein 4.5.

> Render rules live in C:\AI\render\AGENTS.md; run render work from C:\AI\render. Character sheets: [references/characters/sydney.md](references/characters/sydney.md).

## When
- Any FLUX still from an approved character: a new pose, camera angle or scene; start frames for Max/H3 clips.
- Not for video prompts: use h3-prompting.

## Setup
- Workflow = S2, adopted by Derrick 1:16 AM CT Oct 31 ("Adopt S2 as the FLUX stills workflow now").
- Settings, files and node order: C:\AI\community\templates\flux_stills_s2.README.md (do not restate or change them here).
- Run it with `make_render.py still <id|pick> [count]` (pass 1 then pass 2). One GPU job at a time via run_queue.py and C:\AI\locks\gpu-render.lock.

## Pass 1 prompt (Klein 9B-KV): change -> keep -> light/style
Klein reads the prompt as written and weights what comes first (BFL). So:
1. **Change first**: "Show the woman from image 1" + the new pose, then the camera angle, framing, then the scene.
2. **Keep second**: "Keep the same face, hairstyle and hair color" (name the hair when it matters).
3. **Light/style last**: one light source and "photoreal".
- Prose, not keyword lists. About 30-80 words. Refer to the reference as "image 1".
- One clear change per prompt; real pose/angle/scene change (a prompt that asks for no change makes near-copies: in Phase 1, 42 of 59 scored face_sim ≥0.85).
- Say what is there, not what isn't: there is no negative prompt at CFG 1.

Examples that worked in the redo (40_projects/max-fix-tests/plans/2026-10-30-flux-stills-redo-plan.md):
- "Show the woman from image 1 seated on a stone bench, leaning forward, seen in left profile, full body. Keep the same face, hairstyle and hair color. Soft overcast daylight, photoreal."
- "Show the woman from image 1 seated on a wooden chair, leaning slightly forward with her forearms resting on her knees, seen from a front three-quarter angle at eye level, full body, in a bright modern apartment living room with large windows. Keep the same face, hairstyle and hair color (wet shoulder-length dark-blonde hair swept back). Soft overcast daylight from the windows, photoreal."
- Grid that worked: 3 poses (seated, walking, back turned looking over the shoulder) x 3 angles (front 3/4, profile, low 3/4) x 2 scenes.

## Two women in the still
- Name the target by position plus one trait: "The woman on the right with dark hair turns her back to the camera and looks over her shoulder in a cafe. Keep her face and hair from image 1; the blonde woman on the left is unchanged. Warm window light, photoreal."
- Never "the woman" alone when two are present (the redo put the head on the wrong woman in every two-woman item).

## Pass 2 prompt (BFS head swap)
- Use the BFS prompt in flux_stills_s2_bfs.api.json word for word. Do not edit it per job.
- Picture 1 = the pass-1 output (body), Picture 2 = the head reference. Never reverse them (BFS card: body first, face second).

## Checks
- Score face match only against the approved still. Bots name breaks; KEEP = Derrick only.
- Viewing a still needs Derrick's specific permission (alienpc-pi-rules).

## Hard rules
- Characters come from approved_characters (read-only, add-only).
- The minors keyword guard (run_queue guard_graph) stays on; a blocked prompt means stop and report, never reword around it.
- No face-swap or restore beyond the BFS LoRA; no ReActor, PuLID, InstantID, FaceDetailer.
- Content rules: /workspace/cos/canon/fiction-cond-lock.md and /workspace/cos/canon/cnc-frame-block.md (link only).

Sources (opened 2026-10-31): BFL FLUX.2 prompting guide https://docs.bfl.ai/guides/prompting_guide_flux2 ; BFL prompt reference (klein) https://docs.bfl.ml/guides/prompting_unified_reference ; BFL multi-reference editing https://docs.bfl.ai/guides/prompting_editing_multi_reference ; BFS Klein guide https://huggingface.co/Alissonerdx/BFS-Best-Face-Swap/blob/main/docs/flux-2-klein.md ; nomadoor Klein workflows https://comfyui.nomadoor.net/en/basic-workflows/flux-2-klein/
