---
name: video-render
description: Stage, build, queue, and evaluate I2V / H3 (MiniMax-H3 / 10Eros-Max B2) video clips and batches on AlienPc via make_b2_request.py and run_queue.py. Use when asked to build or run video renders, stage video A/B tests, check status.log OBJECTIVE lines, upload finished clips to QNAP pi-drop, or work with fictional adult character video workflows.
---
# Video Render (`video-render`)

> Render rules live in C:\AI\render\AGENTS.md; run render work from C:\AI\render.

## Character Rules & Sheets
- **Character sheets:** Load `references/characters/<name>.md` (e.g. [references/characters/sydney.md](references/characters/sydney.md); index in [references/characters/README.md](references/characters/README.md)).
- **Approved-still character-sheet renders:** Folder-name only on Cond/character sheets (no celeb LoRAs there); named adult INDEX+RefMod parodies use `h3-parody-identity` (see exception below). Vision never decides identity/age.
- **Exception - named celebrity/character parody video:** When Derrick asks for a named character, actor, or celebrity parody video, load companion skill `h3-parody-identity` (single-pass INDEX + RefMod via `submit_parody_run.py`, approved duration/aspect options and one optional frame-0 AddGuide image); celebrity names like "Sydney Sweeney" resolve against INDEX/RefMods and are not local `C:\Users\derek\sydney\` persona paths.
- **Exception - adult writer-run video from a start still (`C:\AI\render`):** When Derrick asks you to write or render an adult clip from a start still using the Gemma 4 26B A4B Heretic (PolyStrata, arm A) writer pipeline, run from `C:\AI\render`, write `still_read.json`, and run `render_writer_pipeline.py` (or `submit_parody_run.py writer-run` only when `writer_down`/error; `base.api.json` is optional/do not build it). All adult RefMods (OC such as `FCSydny` -> `poolclub` visual + audio, INDEX/celebrity, PixlStash-tagged across `approved_characters\vault.db` and `C:\Users\derek\5slock\libraries\vault.db`) and all voice refs (`*_refmod_audio` + `<Audio 1>`) are allowed; 18+ (`guard_ok`/youth lint) is the only content rule. Dry by default (`READY` builds `prompt.txt` and `clip\request.api.json` without queueing); never pass `--queue` without Derrick's yes. On `NOT_READY`, report the reason, rewrite at most once, then stop.
- Never open, read, or parse Derrick's Grok Imagine prompts or prompt sidecar files. Never open, read, or list `C:\Users\derek\sydney\` or any `talk-persona.md`.

## Companion Video Skills
- **Video (i2v / H3) companion skills:**
  - `alienpc-hardcore-i2v-director` (intent, director card)
  - `h3-prompting` (prompt text R1-R31, all lanes; cites live learnings in `C:\AI\community\notes\forge-learnings.md`; the 10-28 updates note is archived in `C:\AI\_archive\2026-10-30-forge-simplify\`, read only when needed)
  - `h3-max-ref2va-prompt` (**the standing REF2VA paste lane for Max**, R32-R44: reference labels for images/video/audio, task-type tags, retention, frame anchors, style opening, language, speech form, node contract, chain lane, its own gate). Load it with `h3-prompting` for picture-reference Max clips; named INDEX + RefMod parodies defer to `h3-parody-identity` for their locked graph and tested prompt/voice/soundscape contract.
  - `h3-hc-render` (graph, gate, proof)
  - `h3-parody-identity` (named celebrity / actor / character parody lane: single-pass 768x1344 INDEX + RefMod via `scripts\parody\submit_parody_run.py`, autonomous 1-clip chat recipe)

## Video Render Settings & Workflow (`## Render`)
- **ComfyUI only via llama-swap:** `http://127.0.0.1:8080/comfyui/` (route `comfyui_auto`). Check status with:
  ```powershell
  C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\comfy_ctl.py status
  ```
- **Current KEEP settings (B2):** `10Eros_Max_h3_8stepTURBO_beta7_int8HQ` + TE `qwen3vl_32b_minimax_h3_nvfp4_awq`; 1-pass parody uses `b2_refmod.api.json` (see `h3-parody-identity`).
- **Canvas & frame math:** 768x1344 (B2; 1344x768 only when a brief asks) @ 24 fps; H3 frames with `(frames - 5) % 17 == 0` (e.g. 124, 243). For ordinary single-cell B2, `--frames` on run_queue must equal `c0.length`; native parody continuation expects cumulative base + extension frames, as built by `submit_parody_run.py`. If WinError 1450 / paging-file errors return, turn dynamic VRAM off for that one cell and log it.
- **Retired:** :8188/:8189, Switchyard, Wan 2.2, Flux.1 Kontext, RIFE on default path. Stills = FLUX.2 Klein 9B.
- **Not defaults:** (experiments only when Derrick names them): STEPS-20, SPARSEsol, Sage, fp8, non-Turbo, SaveH3Embedding, RefMods outside h3-parody-identity, Fill, WAN. Name model file in every run record.
- **One clip or a batch (ordinary B2; named parodies and OC writer submits use the exceptions above):** Build requests with `C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\make_b2_request.py` (`templates\b2.api.json` = B2, default), then `run_queue.py`; steps, launch line, and `--frames`: `C:\AI\community\templates\render-queue-template.md`. `run_queue.py` is the only render path. Launch detached (`run_queue.py --detach`), then end your turn.
- **Lock & batch control:** `run_graph_job.py` and `run_queue.py` take `C:\AI\locks\gpu-render.lock` (`rc 7 = GPU_BUSY`). While it is held: no subagents, no model loads, no second job, no `pi-computer-use`; read-only answers are fine. A `STOP` file in the run dir halts the batch. Report in `<run_dir>\FORGE_REPORT.md`.
- **Stage before asking for a go:** Prepare the order file, run dir, start images, and `run_queue.py --dry-run` output. Ask Derrick first before any render without his go or downloading new models/LoRAs. After the go, the only step is the launch line. (Exception: when Derrick asks in chat for a single named celebrity/character parody video, his chat prompt is the go for the requested clip/continuation/stitched set at the approved duration: up to 243 frames single-shot; 2+ explicit `--beat` scenes use native A/V-tail continuation in one graph; longer asks without 2+ explicit `--beat` scenes are refused by submit_parody_run.py (give 2+ distinct beats); do not use the beatless stitched fallback. Follow `h3-parody-identity`'s single-call submit + wait + QNAP upload recipe without staging first.)
- **Pre-planned test:** Build and render; no new audit/drift/order/contact-sheet scripts; one go covers pilots and the main queue; decide what the plan answers, note it in `DONE`, keep going; stop only for an ask-first item.
- **Video check & scoring:** Check the `OBJECTIVE` line in `<run_dir>\status.log` + `Identity`/`Quality`/`Motion` in words; batch result: `<run_dir>\_render_queue.log` (`BATCH closed rc=<n> reason=<why>`). Never crown `KEEP`; Derrick gives the 1-5 rating and `KEEP`.
- **One-off clip:** Reply to Derrick right after its `OBJECTIVE ok` line; no `DONE` note or extra records for it.
- **Finished clips:** Upload to QNAP `pi-drop` with `C:\AI\community\scripts\pi_qnap.py put` and tell Derrick the filename; never start a web or file server.
- **Test plans & adults-only tests:**
  - Test plans: copy `C:\AI\community\plans\_TEMPLATE.md` to `C:\AI\community\plans\<date-time>-<name>-plan.md`.
  - Adults-only tests:
    ```powershell
    C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py
    ```
