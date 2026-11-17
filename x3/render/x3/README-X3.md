# Render on the EVO-X3 (`~/AI/render/x3/README-X3.md`)
Installed 2026-11-15 by Max Architect. Derrick, 2:09–2:10 PM CT: "Yes, add the temp Q4 slot and run the blind test", "copy it over", "Do it correctly and ensure the setup and rules are updated", "And transferred over to the setup on x3".

**Status: installed and verified, NOT production.** AlienPc `C:\AI\render` stays the live Render chat until Derrick OKs the picks. Cutover of the Render, Sydney, Forge and phone chats waits for that yes (`fleet-brain 40_projects/compute-expansion/plans/2026-11-15-1001-evo-x3-chat-cutover-plan.md`).

## Layout (C:\AI → ~/AI)
| AlienPc | EVO-X3 | How it got there |
|---|---|---|
| `C:\AI\community` (master b81b04f + uncommitted tree) | `~/AI/community`, branch `x3-linux` | git clone of a bundle at b81b04f; commit `f583442` = AlienPc's uncommitted working tree; next commit = Linux paths only |
| `C:\AI\render` (master 4254b04 + uncommitted tree) | `~/AI/render`, branch `x3-linux` | same: bundle clone, snapshot `93e3c9c`, then Linux paths + `x3/` |
| untracked skills, prompts, `.pi`, `writer_pipeline`, `_inputs` (no vault.db) | same relative paths | tar overlay |
| `C:\AI\fleet-brain\20_skills\current` | `~/AI/fleet-brain/20_skills/current` | tar copy, minus `_archive` |
| `C:\AI\render\stills\approved_characters\POOL` images | `~/AI/render/stills/approved_characters/POOL` (104 jpg/png) | images only; no `vault.db`, no caption sidecars |
| `...\ComfyUI\models\refmods` | `~/AI/comfy-alienpc/models/refmods` | 5 OC refmods are real files (metadata read); the other 1,495 are 0-byte name stubs so name lookup works; real files stay on AlienPc |
| `...\ComfyUI\input|output\community` | `~/AI/comfy-alienpc/input|output/community` | local staging only |
| `C:\Users\derek\5slock` (PixlStash) | `~/AI/5slock` (empty) | never copied |

Path rewrite: `x3/linuxize.py` (idempotent, writes `*.bak-x3linux` for untracked files). Non-path changes: `x3/x3_adapt.py`: `wp_llm.py` reads pi's `x3-local` key the way pi does (`!cat` key file, in-process, never printed); `render_writer_pipeline.py --queue --yes-derrick` fills the template and queues via `x3/queue-remote.sh` (`run_queue.py --remote`); `writer_pipeline/config.yaml` endpoint `http://127.0.0.1:8080/v1`, `model_alias: gemma4-heretic`; `AGENTS.md` launch line.

## Start Render on the X3 (also linked at `~/evo-x3/pi-chats/render-pi.sh`)
All agent panes and host services (`herdr-server`, `pi-mobile-hub`, `herdr-panes`) run as user `evo` (uid 1001, no sudo, `/home/evo`), NOT `derekboone`. Phone link runs via `pi-mobile-hub` (`127.0.0.1:7878`) published on Tailscale Serve `https://evo-x3-1.tailf242b2.ts.net:8444` (`herdr-panes.sh` passes `--remote -e pi-mobile -e herdr-agent-state`).
```bash
sudo -n -u evo env XDG_RUNTIME_DIR=/run/user/1001 HOME=/home/evo PATH=/home/evo/.local/bin:/usr/bin bash ~/AI/render/x3/render-pi.sh
```
`render-pi.sh` mirrors AlienPc's production Render pane argv (`C:\AI\director\scripts\pi_herdr_at_logon.ps1` `$renderPiArgs`): `--no-extensions` is kept so project settings do not auto-load plannotator, pi-canvas, pi-say or the compound-engineering plugin; intended extensions are passed with `-e` (pi-permission-system, cc-safety-net, loop-guard, pi-subagents, pi-memory); `--no-mcp`; `--no-skills` + the same 9 skills (video-render, image-render, comfy-render, h3-parody-identity, h3-prompting, h3-max-ref2va-prompt, h3-hc-render, alienpc-hardcore-i2v-director, alienpc-stills-pose-edit-prompting, from `~/AI/community/skills`; on AlienPc the `~/.pi/agent/skills` copies are junctions to the same folders); `--no-context-files`; `--append-system-prompt ~/AI/render/AGENTS.md`.
- Model mapping (Derrick's cutover mapping): Render → `x3-local/gemma4-heretic` (Gemma 4 26B A4B Heretic Q8_0 + official unsloth BF16 mmproj vision, llama.cpp Vulkan, temp 1.0 / top_p 0.95 / top_k 64, 262144 ctx per slot, image budget 560–1120), `--thinking medium` as on AlienPc (thinking is per request). Attach stills as `@path` arguments; a path written only in prose is not sent and the model will invent the outfit.
- Phone & herdr (`evo` user units): `herdr-server.service`, `pi-mobile-hub.service` (`127.0.0.1:7878` -> Tailscale Serve `:8444`), and `herdr-panes.service` (`herdr-panes.sh` reuses restored panes by workspace label/cwd and relaunches with full launcher argv + `--remote`).
- `~/AI/render/.pi/settings.json` (used only by a bare `pi` in this folder for packages/skills, while `pi-subagents` reads its `subagents` block from it: `defaultModel` `x3-local/gemma4-heretic-sub`, `disableThinking: true`, `defaultThinking: "off"`): AlienPc's global package set installed project-local (pi-permission-system 0.8.0, pi-memory 0.4.2, plannotator 0.28.40, pi-canvas 0.1.1, pi-say 1.1.1, compound-engineering @34492307 with AlienPc's skill filters) + `~/AI/...` skills/prompts paths; default model `x3-local/gemma4-heretic`.
- Write sandbox: `~/AI/render/.pi/agent/pi-permissions.jsonc` (write/edit only under `~/AI/community/runs/*`), global floor `~/.pi/agent/pi-permissions.jsonc` (AlienPc policy, `/home/evo` paths + U35 `sudo` / `/etc/evo-x3` deny rules; loaded by this project's `pi-permission-system`).
- Python: `~/AI/render/x3/.venv` (Python 3.14; `requirements-x3.txt`: pysbd 0.3.4, PyYAML 6.0.3, pillow, numpy, opencv-python-headless, pytest).

## Rendering (AlienPc ComfyUI over the tailnet)
Dry run only by default, same as AlienPc: READY writes `prompt.txt`, `clip/request.api.json`, `build_report.json`, `DRY_RUN`. Paste `prompt.txt` to Derrick. Only after his explicit yes for that prompt (and with `render_writer_pipeline.py --queue --yes-derrick` to write `_render_order.json` and queue in one pass):
```bash
bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick [--dry-run]
```
`queue-remote.sh` drives `~/AI/community/scripts/run_queue.py --remote` (`scripts/remote_comfy.py`) against `https://alienpc.tailf242b2.ts.net:8446` (AlienPc Tailscale Serve -> `127.0.0.1:8080/upstream/comfyui_auto`):
- Uploads every `LoadImage` / `LoadAudio` / `LoadVideo` input via `POST /upload/image` (`overwrite=true`), submits `POST /prompt`, polls `/history`, and downloads outputs via `/view` into `<run>/<tag>/`.
- Uses `fcntl.flock` on `~/AI/locks/gpu-render.lock` and detaches via `systemd-run --user`. RTX 2x upscale post-pass is deferred (decision D5).
- Check that no AlienPc render is active first (`:8446/queue` empty or 409, and no `C:\AI\locks\gpu-render.lock`). That POST wakes `comfyui_auto` in AlienPc's exclusive llama-swap group and unloads AlienPc's LLM.

## Re-sync from Gitea (`derekboone` -> `/home/evo`)
`evo` has no Gitea token. `derekboone` fetches and fast-forwards from Gitea (`gitea/x3-community`, `gitea/x3-render`, `gitea/x3-forge`), then root syncs tracked/code changes into `/home/evo/AI/{community,render,forge}` without overwriting `evo`'s runtime directories:
```bash
git -C /home/derekboone/AI/community pull --ff-only gitea x3-community
git -C /home/derekboone/AI/render pull --ff-only gitea x3-render
sudo rsync -a --exclude='.git' --exclude='runs' --exclude='stills' --exclude='_inputs' --exclude='.venv*' --exclude='.pi/npm' --exclude='.pi/git' --exclude='.pi/agent' /home/derekboone/AI/community/ /home/evo/AI/community/
sudo rsync -a --exclude='.git' --exclude='runs' --exclude='stills' --exclude='_inputs' --exclude='.venv*' --exclude='.pi/npm' --exclude='.pi/git' --exclude='.pi/agent' /home/derekboone/AI/render/ /home/evo/AI/render/
sudo chown -R evo:evo /home/evo/AI/community /home/evo/AI/render
```
If user-specific files (`skills/`, `AGENTS.md`, `.pi/agent/pi-permissions.jsonc`) were updated, re-run `python3 ~/AI/render/x3/linuxize.py` as `evo` on those files (`linuxize.py` uses `Path.home()`).

## Known gaps
- Vision: closed 2026-11-15 (mmproj on the Heretic slot, verified on a POOL still; U25 swapped to the official unsloth BF16 mmproj and re-verified).
- GPU lock `~/AI/locks/gpu-render.lock` is local to X3; AlienPc's `C:\AI\locks\gpu-render.lock` is not visible locally (check `:8446/queue` before queueing).
- Upscale post-pass: deferred (D5 — logged and skipped by `remote_comfy.py`).
- `qmd` (`pi-memory` search): `qmd` binary is not installed on `evo` (core `write`/`read`/`scratchpad` tools work; `memory_search` does not).
- RefMod stubs go stale when AlienPc adds RefMods; re-run the manifest step.
- Sydney (`~/AI/sydney`): launcher-only (`sydney-pi.sh`); persona, `AGENTS.md`, chats, voice refs, and memory stay on AlienPc until Derrick's D7 copy.
- Forge MCP servers (`homeassistant`, `unifi`, `gitea`, `vaultwarden`, `google`, `playwright`, `fetch`): not wired on X3 (keys must be typed by Derrick); `pi-computer-use` omitted on headless X3.
- Live render smoke test: dry-run verified only; live POST `/prompt` waits for Derrick's yes on a pasted prompt (D6).

## Blind Q8 vs Q4_K_M test (2026-11-15)
Driver `x3/bakeoff/heretic-q8-vs-q4-20261115/blind_run.sh` (outputs not committed). Temporary llama-swap entry `gemma4-heretic-q4km` and pi model entry were added for the test and removed afterwards (backups: `/etc/evo-x3/llama-swap.yaml.bak-20261115-142702-preq4km`, `~/.pi/agent/models.json.bak-20261115-preq4km`; post-test copies `*.with-q4km-20261115`). Blinded outputs: box `/workspace/maxops/prompts/heretic-q8-vs-q4-blind-20261115/`.

## Model settings (2026-11-15 tune, Derrick t1760u; U25 upgrades t1769s6505)
Full table, sources and live checks: `~/evo-x3/records/U24-model-tuning-20261115.md` (U25 section at the end).

| Slot | Context | KV | Key flags |
|---|---|---|---|
| gemma4-heretic | 2 × 262144 | f16 | official unsloth mmproj BF16 (U25), image 560–1120, -b/-ub 2048, reasoning per request; `gemma4-heretic-sub` alias (maxTokens 4096, thinking off) for Render subagents |
| flash-next (Forge) | 262144, 4 Halogen slots (llama-swap `concurrencyLimit: 4`, `flash-next-sub` alias, U27/U29) | Halogen 0.20.5 native HGN v2 (U26) | effort medium; `flash-next-gufo` = Gufo rollback slot; `flash-next-uncensored` = non-production (U26) |
| qwen27b (Gufo) | 262144 × 2 sessions | Gufo | UD-Q8_K_XL + DFlash2 Q4_K_M draft (U25), Gufo card preset, cache-ram 2 GiB, text-only |
| embed-small | 8192 | – | yarn 0.75, -b/-ub 8192, nomic prefixes |

## X3 Phases 1-5 (2026-11-15, Derrick t1784s6566) - record ~/evo-x3/records/U27-on-track-20261115.md
- Forge: Linux AGENTS.md, ralph loop ~/AI/forge/ralph-community/ralph.sh (bash port), subagents use the parent's model (Forge flash-next, Render heretic; global stays heretic for Sydney).
- Forge project packages load only with --approve (pi project trust); forge-pi.sh and ralph.sh pass it.
- pi-workspace-history 0.5.2 in the Forge project (/undo, /redo, /checkpoint). pi-memory 0.4.2 recall tested across sessions (qmd not installed, so no memory_search).
- Host: sshd keys only and no root login (Tailscale SSH unaffected), tuned accelerator-performance, Open WebUI pinned by digest, llama-swap refuses to start with empty keys.
