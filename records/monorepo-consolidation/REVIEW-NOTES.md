# Monorepo plan: review notes from the Copilot consolidation chat (2026-11-19)

Adds to [PLAN.md](PLAN.md) at `u58` e03d666. Nothing here changes `u58`, the part branches, or any live checkout. It arrives on GitHub-only `feature/*` branches for Max to pull into Gitea before step S3.

## 1. Windows checkout breaks on four `u58` files (affects S6)

These files have a literal backslash in their names (systemd escaping):

- `hosts/x3/live/systemd/system/mnt-qnap-derek\x2dhomes.automount`
- `hosts/x3/live/systemd/system/mnt-qnap-derek\x2dhomes.mount`
- `hosts/x3/live/systemd/system/mnt-qnap-pi\x2ddrop.automount`
- `hosts/x3/live/systemd/system/mnt-qnap-pi\x2ddrop.mount`

Git for Windows refuses them as index entries (`error: invalid path`). A normal clone of `u58` or `mono` on Windows leaves an empty working tree with every file staged as deleted. A non-cone sparse exclude doesn't help.

Workaround that works (verified 2026-11-19 on Windows, Git for Windows):

```text
git clone --no-checkout --branch <branch> <url> <dir>
git -C <dir> sparse-checkout init --cone --sparse-index
git -C <dir> sparse-checkout set <folders that do not contain hosts/x3/live/systemd>
git -C <dir> checkout <branch>
```

The plan's AlienPc cone set (`alienpc/`, `hosts/alienpc/`, `records/`) works this way. After checkout, running `sparse-checkout set` or `add` again fails with the same error, because it expands the index. So pick the folder list once, at clone time.

Durable fix (recommended before S3): have `scripts/snapshot-live-setup.sh` store systemd unit names in a Windows-safe form (for example replace `\` with `%5C` and keep the real name in a manifest), then rename the four files on `u58`.

## 2. Work on GitHub-only branches that the plan would archive as tags

These branches exist only on GitHub and are not merged into any part branch:

- `feature/x3-u56-render-consolidated`
- `feature/x3-community-u56`
- `feature/x3-render-u56`
- `feature/x3-forge-u56`
- `feature/x3-pi-config-u56`
- `feature/forge-coding-u57`
- `feature/alienpc-only-remediation`

A file-by-file check against the current part tips (`x3-render` 9232545, `x3-community` 6bdcc49, `u58-chat-read-plan` 4cbbba0, `u58` e03d666, `alienpc-community` 6dadffc) found everything already present or replaced by a newer version, except the items below. Each target file was unchanged since the common base (b34b42e), so the ported files are byte-for-byte the reviewed versions.

| Item | Ported to | Branch |
|---|---|---|
| rate-proxy and mcp-proxy: body size limits (413), chunked request handling, header forwarding. Egress firewall: works on first run, allows DNS only to the bridge gateway, drops everything else. Playwright quadlet: plain network name and ExecStartPre firewall. Sandbox: `--userns=keep-id` permissions fix (5 files) | `stage-src/config/...` | `feature/u58-mono-carryover` |
| `probe-pi-thinking.sh` (captures what pi sends per thinking level) | `scripts/probe-pi-thinking.sh` | `feature/u58-mono-carryover` |
| AlienPc ComfyUI remediation pack (`--use-ck-attention`, ComfyUI-only llama-swap yaml, `apply-on-alienpc.ps1` audit/apply) | `hosts/alienpc/comfyui-remediation/` | `feature/u58-mono-carryover` |
| `comm.py` LOST_PROMPT handling plus queue/grid fixes in `run_queue.py`, `run_graph_job.py`, `make_b2_request.py`, `sy_test_graph.json` | same paths | `feature/alienpc-community-carryover` |

Not ported, by decision:

- `apply-on-x3.sh` and its README: retired. The plan's clone-and-symlink switchover replaces the installer.
- `patch-llama-swap-u56.py`: a no-op against the live llama-swap.yaml.
- The Forge launcher copy and the 7-skill exclusion: replaced by the live Forge settings (agent-shared skills only).

Open checks:

- `stage-src/` is the U34 sanitized copy. Confirm whether the X3 actually runs `evo-rate-proxy` / `evo-mcp-proxy` / the playwright quadlet before deploying these files. `hosts/x3/live` holds no live copy of them.
- AlienPc `C:\AI\community` has 131 uncommitted changes (plan Q4). Diff them against `feature/alienpc-community-carryover` before committing either, because they may overlap.
- `apply-on-alienpc.ps1 -ApplyLlamaSwap` overwrites `C:\AI\director\config\llama-swap.yaml`. That file is tracked in the separate `switchyard` repo (see section 3), so applying it leaves that checkout dirty. Its step 6 (community script sync) skips itself in this layout, which is intended: the scripts arrive through `alienpc/community`.
- The pack's README describes the 2026-11-17 snapshot. `hosts/alienpc/comfyui/` holds the newer 2026-11-19 inventory, so run `-Mode Audit` first.

## 3. `switchyard` is not in the plan

`incognitodb86-creator/switchyard` (private) is the AlienPc "director" app. It is Python 3.11+, lives at `C:\AI\director`, and runs a gateway on `:8765`, a dashboard on `:8700`, and llama-swap keepalive/GPU-lock scripts. It owns `config/llama-swap.yaml` and overlaps `hosts/alienpc/launchers`. Its `.agents/rules/00-scope.md` grants an agent "No restrictions" (install, commit, push, delete), which deserves review.

Decision needed from Derrick: keep it as its own repo, or fold it into `mono` as `alienpc/director/` (junction `C:\AI\director`, same method as S6).
