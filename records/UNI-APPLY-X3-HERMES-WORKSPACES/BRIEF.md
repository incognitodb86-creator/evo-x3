# UNI-APPLY-X3-HERMES-WORKSPACES (X3 Forge or Derrick): two Hermes workspaces (render + code) with Flash-Next presets, Nov 20 2026

Derrick, 2026-11-20 ~8:17 AM CT & ~9:07 AM CT (orchestrator chat): approved two workspaces (render + code) on Qwen
Flash-Next with D1 `presence_penalty: 0.0` (A/B `1.5` later), D2/D2b code thinking `medium` / `8192` default budget,
D3 archive `gemma` profile + restore pins (keep 25 GiB weights), D4 keep `30-workspace.conf` during apply and test the
WebUI profile chip first, D7 pin `ref2va-27b-heretic-q4 -> flash-next-uncensored-v2`. Plan:
[F4 follow-up](../source-plans/2026-11-18-x3-alienpc-followup-plan.md) item **H7**. Replaces the blocked outside Opus
brief ([REVIEW-20261120-opus.md](../UNI-OPUS-HERMES-WORKSPACES/REVIEW-20261120-opus.md)).

## One-command installer (`scripts/apply-hermes-workspaces.sh`)

Run from any freshly pulled `mono` clone on EVO-X3 (never relies on stale `/home/derekboone/evo-x3`):

```bash
bash scripts/apply-hermes-workspaces.sh --dry-run
bash scripts/apply-hermes-workspaces.sh --apply
# Rollback if needed:
bash scripts/apply-hermes-workspaces.sh --rollback
```

## Goal

Keep today's render chat (the `default` profile) and add one coding chat (a new `code` profile). Both stay on the one
resident Gufo `0.35.0` slot `flash-next-uncensored-v2` (zero swaps, `concurrencyLimit: 4`, both `-sub` aliases intact)
via 3 zero-swap `setParamsByID` aliases (all keys VERIFIED in Gufo `0.35.0` source):

| Workspace / Slot | Hermes profile | Model name | Sampler (Gufo `0.35.0`) | Thinking | cwd |
|---|---|---|---|---|---|
| Render | `default` | `flash-next-render` | Qwen Instruct: temp 0.7, top_p 0.8, top_k 20, min_p 0, presence 0.0 (D1; `--render-presence 1.5` for A/B) | off (`enable_thinking: false` + Hermes `false`) | `/home/evo/workspace` |
| Code | `code` (new, cloned) | `flash-next-code` | Qwen Thinking (C5 11/11): temp 1.0, top_p 0.95, top_k 20, min_p 0, presence 0.0 | `medium` in BOTH `model.reasoning_effort` and `agent.reasoning_effort`; Gufo `8192` default budget | `/home/evo/AI/hermes-code` |
| Background aux | Both profiles `auxiliary.{compression,vision,approval,title_generation}` | `flash-next-aux` | Deterministic: temp 0.35, top_p 0.9, top_k 20, min_p 0, presence 0.0 | off (`enable_thinking: false`) | — |

## What the script does (all reversible)

1. Checks no `pi-job` is RUNNING, takes one-line X3 lease (`/home/derekboone/AI/locks/x3-lease.txt`, auto-cleared via
   `trap` on exit/error).
2. Backs up `/etc/evo-x3/llama-swap.yaml` -> `/etc/evo-x3/_archive/llama-swap.yaml-20261120-preWS` and
   `/home/evo/.hermes/` -> `/home/evo/.hermes/_archive/20261120-ws/` (refuses to overwrite existing pre-WS backups).
3. Comment-preserving patch of `/etc/evo-x3/llama-swap.yaml` (keeps live `ref2va` ctx, `-sub` aliases, `concurrencyLimit: 4`),
   adds `flash-next-render`, `flash-next-code`, `flash-next-aux`, restores `gemma4-heretic` + `gemma4-heretic-sub` pins,
   and pins `ref2va-27b-heretic-q4` (D3/D7). Restarts `llama-swap`, waits for `/running`, and **probes all 3 aliases via
   `curl -K -` (key on stdin, never on argv) BEFORE touching Hermes**.
4. Patches `/home/evo/.hermes/config.yaml` via Python `yaml` (`model.default: flash-next-render`, `auxiliary.* -> flash-next-aux`,
   preserves `key_env`, `secrets.command`, `guard-render-queue.sh`) and installs `hosts/x3/hermes/workspaces/render/AGENTS.md`
   (adds the 1-line `gufo#388` no-think tool retry rule).
5. Clones `code` profile (`hermes profile create code --clone --no-alias`), installs `code/AGENTS.md` and clean coding
   `code/MEMORY.md`, patches `profiles/code/config.yaml` via Python `yaml` (`model.default: flash-next-code`, **both**
   `model.reasoning_effort: medium` and `agent.reasoning_effort: medium`, `terminal.cwd: /home/evo/AI/hermes-code`,
   `skills.external_dirs: []`, disables render/PixlStash skills, routes `auxiliary.* -> flash-next-aux`, keeps `pi-job`
   and `guard-render-queue.sh`).
6. Archives `/home/evo/.hermes/profiles/gemma` -> `_archive/20261120-ws/profiles-gemma` (keeps 25 GiB weights on disk).
7. Restarts `hermes-gateway`, runs `/running`, Render oneshot, Code oneshot (`pwd` + `pi-job`), and `code skills list`
   smoke checks, and writes `records/UNI-APPLY-X3-HERMES-WORKSPACES/RESULT.md`.

## WebUI D4 check (after `--apply`)

Open Hermes WebUI, pick profile `code`, and ask `pwd`. If WebUI forces `/home/evo/workspace` (due to
`hermes-webui.service.d/30-workspace.conf`), archive that drop-in and restart `hermes-webui`:

```bash
sudo -n -iu evo mv /home/evo/.config/systemd/user/hermes-webui.service.d/30-workspace.conf /home/evo/.hermes/_archive/20261120-ws/
sudo -n systemctl --user -M evo@ restart hermes-webui
```
