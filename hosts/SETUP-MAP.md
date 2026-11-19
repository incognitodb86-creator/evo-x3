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
| Full live X3 snapshot, one folder per program: llama-swap (Gufo/Halogen/strix launch lines), container images + digests, Hermes, pi (evo + derekboone, extensions, packages, panes), herdr, PixlStash server config, system + evo user units, /usr/local/bin, Forge MCP launchers, aria2, agy/tailscale versions. Refresh with `scripts/snapshot-live-setup.sh` | `u58` | `hosts/x3/live/` (see its README.md) |
| AlienPc ComfyUI (version, custom node list with commits, extra_model_paths, settings, launch scripts, pip freeze) | `u58` | `hosts/alienpc/comfyui/` |
| AlienPc launchers (comfy-guarded, llama-swap control) | `u58` | `hosts/alienpc/launchers/` |
| AlienPc live snapshot (global pi agent, Forge loop, skill links map) | `u58` | `hosts/alienpc/live/` (see its README.md) |
| AlienPc global pi folder (`C:\Users\derek\.pi\agent\`: AGENTS.md, settings.json, pi-permissions.jsonc, web-search.json, extensions) | `u58` | `hosts/alienpc/live/pi-agent/` |
| AlienPc Forge (`C:\Users\derek\forge` -> `5slock`: README, x3run.ps1/x3put.ps1, ralph-community) | `u58` | `hosts/alienpc/live/forge/` |
| AlienPc render repo (C:\AI\render) | `alienpc-render` | repo root |
| AlienPc community repo (C:\AI\community) | `alienpc-community` | repo root |

Not included on purpose: keys, .env files, token files, auth.json, state DBs, chat sessions/memory, PixlStash library, models, video/image outputs, venvs, third-party clones (pinned in `hosts/x3/SOURCES.md`).

Note on commit 1f4004a: its message only names the AlienPc snapshot, but it also contains `hosts/x3/live/`,
`scripts/snapshot-live-setup.sh`, the refreshed `hosts/x3/pixlstash-tagging/*.py`, the pre-Gufo config backup under
`records/gufo-phase1-20261117/` (Sydney pane left out) and the C5 bench logs/results under `records/plan-v32/c5-results/live/`
(build trees, auth.json, models.json left out). Two executors shared one index on the X3; all of it was gitleaks-scanned (no leaks).
