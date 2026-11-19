# Where the full setup lives (GitHub incognitodb86-creator/evo-x3, mirrored from Gitea derrick/evo-x3)

Snapshot 2026-11-19 (Derrick t2613u). Live machines are the source of truth; these are copies with secrets removed.

| Part | Branch | Path |
|---|---|---|
| X3 Render (OPERATOR.md, AGENTS.md writer book, RUN_ME.md, writer_pipeline, x3/render-pi.sh, queue-remote.sh) | `x3-render` | repo root |
| X3 community (render_writer_pipeline.py, run_queue.py, remote_comfy/remote_upscale, H3 skills, 17 templates) | `x3-community` (also `x3-linux`) | repo root |
| X3 Forge (ralph-community, loop-guard, records) | `u58-chat-read-plan` | repo root |
| X3 host: llama-swap.yaml, systemd, quadlets, host config, /usr/local/bin scripts (pi-job, sync-renders) | `u58` | `config/` |
| X3 pi (evo user settings, Render/Forge project settings, launchers, models.json.example) | `u58` | `config/pi-evo/` |
| Hermes (config.yaml redacted, SOUL.md, pi-job skill, skills list, gateway unit) | `u58` | `hosts/x3/hermes/`, `hosts/x3/systemd/user/` |
| pi mobile hub (7878), herdr panes, comfy-submit | `u58` | `hosts/x3/evo-home-scripts/` |
| PixlStash tagger code | `u58` | `hosts/x3/pixlstash-tagging/` |
| Plans and records (incl. Hermes direct-render plan) | `u58` | `records/` |
| AlienPc ComfyUI (version, custom node list with commits, extra_model_paths, settings, launch scripts, pip freeze) | `u58` | `hosts/alienpc/comfyui/` |
| AlienPc launchers (comfy-guarded, llama-swap control) | `u58` | `hosts/alienpc/launchers/` |
| AlienPc render repo (C:\AI\render) | `alienpc-render` | repo root |
| AlienPc community repo (C:\AI\community) | `alienpc-community` | repo root |

Not included on purpose: keys, .env files, token files, auth.json, state DBs, chat sessions/memory, PixlStash library, models, video/image outputs, venvs, third-party clones (pinned in `hosts/x3/SOURCES.md`).
