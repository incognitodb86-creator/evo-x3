# pi chats on the EVO-X3

Launchers for Derrick's pi chats on the X3. All agent panes and host services (`herdr-server`, `pi-mobile-hub`, `herdr-panes`) run as user `evo` (uid 1001, no sudo) from `/home/evo`. See `~/evo-x3/records/U36-gap-tables-20261116.md` and `~/AI/render/x3/README-X3.md`.

- `render-pi.sh`: Render (`/home/evo/AI/render`, `x3-local/flash-next-uncensored`, `--thinking low`). Links to `/home/derekboone/AI/render/x3/render-pi.sh`. Live in herdr pane `render` (`--remote`, `pi-mobile`, `herdr-agent-state.ts`).
- `forge-pi.sh`: Forge (`/home/evo/AI/forge`, `x3-local-coding/flash-next-uncensored`, `--thinking medium`, `thinkingBudgets.medium=4096`). Live in herdr pane `forge` (`--remote`). No MCP servers with keys yet (Derrick types keys).
- `sydney-pi.sh`: Sydney launch config only. Persona and private files are not on the X3 (D7); not auto-started by `herdr-panes.sh`.

Phone link: `pi-mobile-hub` (`127.0.0.1:7878`) published via Tailscale Serve `:8444`.
Session root: `~/.pi/agent/sessions/` (shared across panes via `sessionDir` in pane `settings.json`, phone via `pi-mobile`, and plain shell). Resume via `/resume` in a pane, from the phone, or `pi --continue` in the repo directory.
Renders run on AlienPc ComfyUI and are queued only after Derrick's yes on a pasted prompt:
`bash ~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick` (drives `scripts/run_queue.py --remote`).
