# Render Pi Session Guide (`/home/evo/AI/render/RUN_ME.md`)
Last Updated: 2026-11-16

Quickstart for running the H3 writer pipeline on EVO-X3 Linux (`/home/evo/AI/render`).

## 0. EVO-X3 Launch & Queue
- **User & launcher**: Render pi panes run as user `evo` (uid 1001, `/home/evo/AI/render`), launched via `/home/evo/AI/render/x3/render-pi.sh` (loads `x3-local/gemma4-heretic`, `--thinking medium`, `h3-parody-identity` + `h3-prompting` skills, `/home/evo/AI/render/AGENTS.md`):
  ```bash
  sudo -n -u evo env XDG_RUNTIME_DIR=/run/user/1001 HOME=/home/evo PATH=/home/evo/.local/bin:/usr/bin bash /home/evo/AI/render/x3/render-pi.sh
  ```
- **Python venv**: Use `/home/evo/AI/render/x3/.venv/bin/python3`.
- **Write and queue in one pass**: after Derrick says yes (and confirming AlienPc GPU/lease is free), run `render_writer_pipeline.py` with `--queue --yes-derrick`. That writes the prompt and queues on AlienPc ComfyUI over Tailscale Serve `https://alienpc.tailf242b2.ts.net:8446` via `queue-remote.sh` (which holds the X3 submitter lock `/home/evo/AI/locks/gpu-render.lock`).
  ```bash
  bash /home/evo/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick [--dry-run]
  ```

## 1. Per-Clip Workflow (the ONE writer command)
1. Pick a start still from `/home/evo/AI/render/_inputs`, any still path Derrick names, or via the PixlStash API by `character_id` (`FCSydny` = `1`, `FCMegan` = `2`; `file_path` is relative to `/home/evo/AI/5slock/libraries/`), inspect it with `read`, and create one run folder under `/home/evo/AI/community/runs/<run_name>`.
2. Write `<run_dir>/still_read.json`: `{"read": {room, place, surface, bed, sheets, floor, pose, facing_camera, framing, light, people, garments, build, skin, hair}, "source": "<still path>"}`.
3. Run the ONE writer command (dry by default; add `--queue --yes-derrick` only after Derrick says yes):
   ```bash
   /home/evo/AI/render/x3/.venv/bin/python3 /home/evo/AI/community/scripts/parody/render_writer_pipeline.py \
     /home/evo/AI/community/runs/<run_name> --ask "<ask>" --position "<position>" \
     --still "<still path>" [--character "<Character>"] [--actor "<Actor>"] [--names "<Name>" ...]
   ```
   Optional flags:
   - `--frames <N>` (cap frames <= 243, e.g. for two reference stills)
   - `--shots single|multi` and `--shot-count <k>` (multi-shot cuts inside `[Shot N]`)
   - `--scene <scene_id>` and `--continue <prev_run_dir>` (stateful continuation chains)
   - `--partner2-still <still>` (`S3` reference still for MMF/FFM)
   - `--still-read <path>` (reuse a pre-written `still_read.json`)
   - `--n-candidates <N>` (A/B test flag; default 1)
4. Check output and stop:
   - `READY` writes `<run_dir>/prompt.txt`, `<run_dir>/clip/request.api.json`, and `<run_dir>/build_report.json`. With `--queue --yes-derrick` it also queues and writes `_render_order.json`.
   - Report the `READY` / `NOT_READY` status line, `<run_dir>/pick.json` path, and `submitted=`. **Never pass `--queue` or `--yes-derrick` unless Derrick explicitly approved queueing.**

## 2. Characters, RefMods, Voice Refs, and Stills Vault
- **All adult RefMods and all voice refs are allowed**: OC RefMods, INDEX celebrity/character RefMods, PixlStash-tagged identities, and voice refs (`*_refmod_audio` + `<Audio 1>`) are all supported.
- **Vault on X3**: `/home/evo/AI/5slock/libraries/vault.db` is on the X3. Never open or browse library pictures, captions, sidecars, or face groups; look up stills only via the PixlStash API with `character_id` (and `$PIXL_KEY` in env, never printed).
- **Content rule**: Only `18+` adults-only applies (`guard_ok` and youth lint stay locked). Never use minor-coded terms.

## 3. Prompt Compilation & Acceptance
- Recompile `writer_prompt.md` from `/home/evo/AI/render/AGENTS.md` after editing craft rules:
  ```bash
  /home/evo/AI/render/x3/.venv/bin/python3 /home/evo/AI/community/scripts/parody/wp_compile_prompt.py
  /home/evo/AI/render/x3/.venv/bin/python3 /home/evo/AI/community/scripts/parody/check_writer_prompt_rules.py \
    /home/evo/AI/community/scripts/parody/render-master-rules-20261113.json /home/evo/AI/render/writer_pipeline/writer_prompt.md
  ```
- Target is `77/77 PASS`.

## 4. Forbidden in Render Sessions
- Writing outside `/home/evo/AI/community/runs/*`.
- Queueing without Derrick explicit yes (`--queue --yes-derrick`).
- Reading builder internals (`build_request.py`, `submit_parody_run.py`, `acts.yaml`), `.env`/keys/tokens, or `/home/evo/AI/sydney/`.
- Opening or browsing PixlStash library contents/captions.
- Editing `llama-swap.yaml`, ComfyUI install, or interrupting active GPU renders (`/home/evo/AI/locks/gpu-render.lock`).
