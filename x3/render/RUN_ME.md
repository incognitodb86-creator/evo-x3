# Render Pi Session Guide (`~/AI/render/RUN_ME.md`)
Last Updated: 2026-11-16

Quickstart for running the H3 writer pipeline from `~/AI/render` (EVO-X3 Linux and AlienPc Windows).

## 0. EVO-X3 Section (Linux)
- **User & launcher**: All Render pi panes run as user `evo` (uid 1001, `/home/evo/AI/render`), launched via `~/AI/render/x3/render-pi.sh` (loads `x3-local/gemma4-heretic`, `--thinking medium`, stripped extensions/skills, `~/AI/render/AGENTS.md`):
  ```bash
  sudo -n -u evo env XDG_RUNTIME_DIR=/run/user/1001 HOME=/home/evo PATH=/home/evo/.local/bin:/usr/bin bash /home/evo/AI/render/x3/render-pi.sh
  ```
- **Python venv**: Use `/home/evo/AI/render/x3/.venv/bin/python3` (`~/AI/render/x3/.venv/bin/python3`); do not call bare `/usr/bin/python3` or Windows `.venv/Scripts/python.exe`.
- **Write and queue in one pass**: after Derrick's yes (and confirming AlienPc's GPU/lease is free), run `render_writer_pipeline.py` or `submit_parody_run.py writer-run` with `--queue --yes-derrick`. That writes the prompt and queues on AlienPc ComfyUI over Tailscale Serve `https://alienpc.tailf242b2.ts.net:8446` in one pass (no dry-run rebuild). `Max Architect 2026-11-16 (Derrick t2036u, t2039u)`:
  ```bash
  bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick [--dry-run]
  ```
- **GPU lock & stills**: `~/AI/locks/gpu-render.lock` (`flock`) is only a local X3 submitter lock — AlienPc's `C:\AI\locks\gpu-render.lock` is invisible from the X3. Pick stills from `~/AI/render/_inputs` or `~/AI/render/stills/approved_characters/POOL`; PixlStash `vault.db` is not on the X3, so pass `--character`/`--names`. Full X3 details: `~/AI/render/x3/README-X3.md`.

## 1. Launch `pi` Correctly (AlienPc Reference; Model, CWD, Permissions, Guard)
- **Working directory**: `/home/derekboone/AI/render` (reads `/home/derekboone/AI/render/AGENTS.md` and `.pi\agent\pi-permissions.jsonc`).
- **Model override (mandatory)**: `C:\Users\derek\.pi\agent\settings.json` defaults to `coding_swift15_iq3s_esp`. **Never** run Render chats on that coding default. Always pass Gemma 4 26B A4B Heretic on PolyStrata (`gemma4_heretic_poly_think`, `--thinking medium`):
  ```powershell
  Set-Location /home/derekboone/AI/render
  pi --approve --model llama-swap/gemma4_heretic_poly_think --thinking medium
  ```
  - For an automated single-turn check add `-p --no-session "<prompt>"`.
  - Pipeline internal LLM alias (`/home/derekboone/AI/render/writer_pipeline/config.yaml`): `gemma4_heretic_poly_think` with `thinking: false`, frozen sampler **arm A** (`temperature: 1.0`, `top_p: 0.95`, `top_k: 64`, `min_p: 0.10`, `n_candidates: 3`, `min_ready_score: 60`).
- **Write sandbox (`/home/derekboone/AI/render/.pi/agent/pi-permissions.jsonc`)**: `edit` and `write` are denied everywhere under `/home/derekboone/AI/render` and elsewhere, and allowed **only** under `/home/derekboone/AI/community/runs/*`.
- **Loop guard (`C:\Users\derek\.pi\agent\extensions\loop-guard.ts`)**: aborts 3 identical tool calls in a row and caps `submit_parody_run.py` / `render_writer_pipeline.py` calls per run folder at `4` (`RUN_LIMIT = 4`). Stop and report `NOT_READY` instead of retrying in a loop.
- **GPU lock**: Before sending model requests or calling the pipeline, confirm `/home/derekboone/AI/locks/gpu-render.lock` is not held (`False`). Never start a job while ComfyUI renders hold the lock.

## 2. Normal Run Workflow (Dry Only by Default)
1. Pick a start still (under `_inputs`, `stills\approved_characters`, or `stills\comfy_input`), inspect it with `read`, and create one run folder under `/home/derekboone/AI/community/runs/<run_name>`.
2. Write `<run_dir>\still_read.json`: `{"read": {room, place, surface, bed, sheets, floor, pose, facing_camera, framing, light, people, garments, build, skin, hair}, "source": "<still path>"}`.
3. After Derrick's yes, run the autonomous writer pipeline with `--queue --yes-derrick` (write and queue in one pass; no dry run first):
   ```powershell
   python3 /home/derekboone/AI/community/scripts/parody/render_writer_pipeline.py `
     '/home/derekboone/AI/community/runs/<run_name>' --ask '<ask>' --position '<position>' `
     --still '<still path>' --character FCSydny
   ```
   Optional flags when needed:
   - `--frames <N>` (cap frames <= 243, e.g. for two reference stills)
   - `--shots single|multi` and `--shot-count <k>` (multi-shot cuts inside `[Shot N]`)
   - `--scene <scene_id>` and `--continue '<prev_run_dir>'` (stateful continuation chains)
   - `--partner2-still '<still>'` (`S3` reference still for MMF/FFM)
   - `--still-read '<path>'` (reuse a pre-written `still_read.json`)
4. **Manual fallback (only if pipeline prints `writer_down` or errors)**: write `<run_dir>\writer_output.txt` directly with plain headers (`subject_definitions:`, `summary:`, `retention_analysis:`, `detailed_description:`, optional `continuation:`), then validate via:
   ```powershell
   python3 /home/derekboone/AI/community/scripts/parody/submit_parody_run.py writer-run `
     '/home/derekboone/AI/community/runs/<run_name>' --ask '<ask>' --position '<position>' `
     --still '<still path>' --character FCSydny
   ```
   Additional `writer-run` flags: `--frames <N>`, `--shots single|multi`, `--continued`, `--partner2-still '<still>'`, `--s3-look '<look>'`, `--s3-in-frame`, `--partner-type <type>`, `--partner-type2 <type>`, `--names <name>...`. (`base.api.json` is optional — `submit_parody_run.py` loads `templates\b2_refmod.api.json` read-only if absent.)
5. Check output and stop:
   - `READY` writes `<run_dir>/prompt.txt`, `<run_dir>/clip/request.api.json`, and `<run_dir>/build_report.json`. With `--queue --yes-derrick` it also queues and writes `_render_order.json` (no `DRY_RUN` leftover).
   - Report the `READY` / `NOT_READY` status line, `<run_dir>/pick.json` path, and `submitted=`. **Never pass `--queue` or `--yes-derrick` unless Derrick explicitly approved queueing.**

## 3. Characters, RefMods, Voice Refs, and Stills Vaults
- **All adult RefMods and all voice refs are allowed**: OC RefMods, INDEX celebrity/character RefMods, PixlStash-tagged identities, and voice refs (`*_refmod_audio` + `<Audio 1>`) are all supported by `writer-run`.
- **`FCSydny`**: resolves automatically to `minimaxh3_oc_poolclub_v1_refmod_visual` and `minimaxh3_oc_poolclub_v1_refmod_audio` (`<Audio 1>` voice timbre).
- **Stills & PixlStash vaults (`submit_parody_run.py` `_PIXLSTASH_VAULTS`)**: tag-resolution looks up character tags in the merged Stills library `~/AI/5slock/libraries/vault.db` (POOL folder fallback at `~/AI/render/stills/approved_characters/POOL`) (path/tag lookup only — never open/browse library pictures, captions, sidecars, or face groups).
- **Content rule**: Only `18+` adults-only applies (`guard_ok` and youth lint stay locked). Never use minor-coded terms.

## 4. Prompt Compilation & Acceptance
- Recompile `writer_prompt.md` from `/home/derekboone/AI/render/AGENTS.md` after editing craft rules:
  ```powershell
  python3 /home/derekboone/AI/community/scripts/parody/wp_compile_prompt.py
  python3 /home/derekboone/AI/community/scripts/parody/check_writer_prompt_rules.py `
    /home/derekboone/AI/community/scripts/parody/render-master-rules-20261113.json /home/derekboone/AI/render/writer_pipeline/writer_prompt.md
  ```
- Target is `77/77 PASS` (`hard_fail=0 soft_fail=0`). Never edit `render-master-rules-20261113.json` or builder internals from Render sessions.
- Acceptance & 30+ clip planner live under `/home/derekboone/AI/render/writer_pipeline/acceptance/` (`wp_accept.py`, `t3_plan.py`).

## 5. Forbidden in Render Sessions
- Writing outside `/home/derekboone/AI/community/runs/*`.
- Queueing without Derrick's explicit yes (`--queue`).
- Reading builder internals (`build_request.py`, `submit_parody_run.py`, `acts.yaml`), `.env`/keys/tokens, or `C:\Users\derek\sydney\`.
- Opening or HTTP-querying PixlStash library contents/captions.
- Editing `llama-swap.yaml`, ComfyUI install, or interrupting active GPU renders (`/home/derekboone/AI/locks/gpu-render.lock`).
