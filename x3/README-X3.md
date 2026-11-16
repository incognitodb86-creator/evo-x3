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

Path rewrite: `x3/linuxize.py` (idempotent, writes `*.bak-x3linux` for untracked files). Non-path changes: `x3/x3_adapt.py`: `wp_llm.py` reads pi's `x3-local` key the way pi does (`!cat` key file, in-process, never printed); `submit_parody_run.py --queue` refuses on Linux and points to `x3/queue-remote.sh`; `writer_pipeline/config.yaml` endpoint `http://127.0.0.1:8080/v1`, `model_alias: gemma4-heretic`; `AGENTS.md` launch line.

## Start Render on the X3 (also linked at `~/evo-x3/pi-chats/render-pi.sh`)
```bash
ssh derekboone@evo-x3-1.tailf242b2.ts.net
bash ~/AI/render/x3/render-pi.sh                          # interactive
bash ~/AI/render/x3/render-pi.sh -p --no-session "<ask>"  # one-shot
```
`render-pi.sh` mirrors AlienPc's production Render pane argv (`C:\AI\director\scripts\pi_herdr_at_logon.ps1` `$renderPiArgs`): `--no-extensions` + pi-permission-system, cc-safety-net, loop-guard; `--no-mcp`; `--no-skills` + the same 9 skills (video-render, image-render, comfy-render, h3-parody-identity, h3-prompting, h3-max-ref2va-prompt, h3-hc-render, alienpc-hardcore-i2v-director, alienpc-stills-pose-edit-prompting, from `~/AI/community/skills`; on AlienPc the `~/.pi/agent/skills` copies are junctions to the same folders); `--no-context-files`; `--append-system-prompt ~/AI/render/AGENTS.md`.
- Model mapping (Derrick's cutover mapping): Render → `x3-local/gemma4-heretic` (Gemma 4 26B A4B Heretic Q8_0 + official unsloth BF16 mmproj vision, llama.cpp Vulkan, temp 1.0 / top_p 0.95 / top_k 64, 262144 ctx per slot, image budget 560–1120), `--thinking medium` as on AlienPc (thinking is per request). Attach stills as `@path` arguments; a path written only in prose is not sent and the model will invent the outfit.
- Left out on purpose: `--remote`, `herdr-agent-state.ts`, pi-mobile (herdr 0.9.5 is installed but not wired; the phone bridge is not on the X3; the phone cutover is gated).
- `~/AI/render/.pi/settings.json` (used only by a bare `pi` in this folder, not by the launcher): AlienPc's global package set installed project-local (pi-permission-system 0.8.0, pi-memory 0.4.2, plannotator 0.28.40, pi-canvas 0.1.1, pi-say 1.1.1, compound-engineering @34492307 with AlienPc's skill filters) + skills/prompts paths; default model x3-local/gemma4-heretic.
- Write sandbox: `~/AI/render/.pi/agent/pi-permissions.jsonc` (write/edit only under `~/AI/community/runs/*`), global floor `~/.pi/agent/pi-permissions.jsonc` (AlienPc policy, paths translated; only loaded by this project's pi-permission-system).
- Python: `~/AI/render/x3/.venv` (Python 3.14; `requirements-x3.txt`: pysbd 0.3.4, PyYAML 6.0.3, pillow, numpy, opencv-python-headless, pytest).

## Rendering (AlienPc ComfyUI over the tailnet)
Dry run only by default, same as AlienPc: READY writes `prompt.txt`, `clip/request.api.json`, `build_report.json`, `DRY_RUN`. Paste prompt.txt to Derrick. Only after his yes for that prompt:
```bash
bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick
```
It uploads the graph's LoadImage stills to AlienPc ComfyUI (`/upload/image`) and posts the graph with `~/evo-x3/scripts/comfy-submit.sh` (https://alienpc.tailf242b2.ts.net:8446). That wakes `comfyui_auto` in AlienPc's exclusive llama-swap group and unloads AlienPc's LLM: check AlienPc's GPU/lease first. Not exercised yet (no render queued during install).

## Re-sync from AlienPc
Bundle + uncommitted patch + overlay (see `~/AI/_xfer/render-20261115/`), then `git apply`, `x3/linuxize.py`, `x3/x3_adapt.py`. Gitea `derrick/alienpc-community-pc` is one commit behind AlienPc (b81b04f unpushed), so the bundle route was used.

## Known gaps
- Vision: closed 2026-11-15 (mmproj on the Heretic slot, verified on a POOL still; U25 swapped to the official unsloth BF16 mmproj and re-verified).
- GPU lock `~/AI/locks/gpu-render.lock` is local and never held; AlienPc's lock is not visible from the X3.
- Not installed: pi-mobile (phone cutover is a separate gated step), pi-computer-use (headless box). herdr 0.9.5 is installed in ~/.local/bin but not configured.
- Refmod stubs go stale when AlienPc adds refmods; re-run the manifest step.

## Blind Q8 vs Q4_K_M test (2026-11-15)
Driver `x3/bakeoff/heretic-q8-vs-q4-20261115/blind_run.sh` (outputs not committed). Temporary llama-swap entry `gemma4-heretic-q4km` and pi model entry were added for the test and removed afterwards (backups: `/etc/evo-x3/llama-swap.yaml.bak-20261115-142702-preq4km`, `~/.pi/agent/models.json.bak-20261115-preq4km`; post-test copies `*.with-q4km-20261115`). Blinded outputs: box `/workspace/maxops/prompts/heretic-q8-vs-q4-blind-20261115/`.

## Model settings (2026-11-15 tune, Derrick t1760u; U25 upgrades t1769s6505)
Full table, sources and live checks: `~/evo-x3/records/U24-model-tuning-20261115.md` (U25 section at the end).

| Slot | Context | KV | Key flags |
|---|---|---|---|
| gemma4-heretic | 2 × 262144 | f16 | official unsloth mmproj BF16 (U25), image 560–1120, -b/-ub 2048, reasoning per request |
| flash-next (Forge) | 262144, 4 Halogen slots (llama-swap concurrencyLimit 1 until Phase 1 lands) | Halogen 0.20.5 native HGN v2 (U26) | effort medium; `flash-next-gufo` = Gufo rollback slot; `flash-next-uncensored` = non-production (U26) |
| qwen27b (Gufo) | 262144 × 2 sessions | Gufo | UD-Q8_K_XL + DFlash2 Q4_K_M draft (U25), Gufo card preset, cache-ram 2 GiB, text-only |
| embed-small | 8192 | – | yarn 0.75, -b/-ub 8192, nomic prefixes |

## X3 Phases 1-5 (2026-11-15, Derrick t1784s6566) - record ~/evo-x3/records/U27-on-track-20261115.md
- Forge: Linux AGENTS.md, ralph loop ~/AI/forge/ralph-community/ralph.sh (bash port), subagents use the parent's model (Forge flash-next, Render heretic; global stays heretic for Sydney).
- Forge project packages load only with --approve (pi project trust); forge-pi.sh and ralph.sh pass it.
- pi-workspace-history 0.5.2 in the Forge project (/undo, /redo, /checkpoint). pi-memory 0.4.2 recall tested across sessions (qmd not installed, so no memory_search).
- Host: sshd keys only and no root login (Tailscale SSH unaffected), tuned accelerator-performance, Open WebUI pinned by digest, llama-swap refuses to start with empty keys.
