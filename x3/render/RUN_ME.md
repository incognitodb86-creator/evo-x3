# Render Pi Session Guide (`/home/derekboone/AI/render/RUN_ME.md`)
Last Updated: 2026-11-14

Quickstart for running the H3 writer pipeline from `/home/derekboone/AI/render` on AlienPc.

## 1. Launch `pi` Correctly (Model, CWD, Permissions, Guard)
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
3. Run the autonomous writer pipeline (dry by default; paste prompt.txt to Derrick and add `--queue` only after he approves it):
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
   - `READY` writes `<run_dir>\prompt.txt`, `<run_dir>\clip\request.api.json`, `<run_dir>\build_report.json`, and `<run_dir>\DRY_RUN`.
   - Report the `READY` / `NOT_READY` status line and `<run_dir>\pick.json` path. **Never pass `--queue` unless Derrick explicitly approves queueing.**

## 3. Characters, RefMods, Voice Refs, and Stills Vaults
- **All adult RefMods and all voice refs are allowed**: OC RefMods, INDEX celebrity/character RefMods, PixlStash-tagged identities, and voice refs (`*_refmod_audio` + `<Audio 1>`) are all supported by `writer-run`.
- **`FCSydny`**: resolves automatically to `minimaxh3_oc_poolclub_v1_refmod_visual` and `minimaxh3_oc_poolclub_v1_refmod_audio` (`<Audio 1>` voice timbre).
- **Stills & PixlStash vaults (`submit_parody_run.py` `_PIXLSTASH_VAULTS`)**: tag-resolution looks up character tags across `/home/derekboone/AI/render/stills/approved_characters/vault.db` and Stills libraries `/home/derekboone/AI/5slock/libraries/vault.db` (path/tag lookup only — never open/browse library pictures, captions, sidecars, or face groups).
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
