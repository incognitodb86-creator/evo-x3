# U37 Sydney copy + Forge tool keys — 2026-11-16 (Derrick t1881u)

Times are America/Chicago (CT).

## Sydney
- Source on AlienPc was `C:\Users\derek\sydney` (not `C:\AI\sydney`, which does not exist).
- Copied byte-for-byte via LAN Taildrop as `sydney-workspace.tar` (14,204,313,600 bytes), received 9:21 AM CT.
- Extracted to `/home/evo/AI/sydney`: 7,095 files, 3,353 dirs, 14G. File count matched the AlienPc source. Permissions tightened to 700/600, owner `evo`.
- Private files were not opened. Top-level names include `AGENTS.md`, `PERSONA_private.md`, `INSTRUCTIONS_private.md`, `private/`, `ralph/`, `voice/`, `work/`, `_archive/`, `.git`.
- Pi sessions from `C:\Users\derek\.pi\agent\sessions\--C--Users-derek-sydney--` (90 files, 117,767,988 bytes, exact match) were installed at:
  - `/home/evo/.pi/agent/sessions/--home-evo-AI-sydney--` (new cwd)
  - `/home/evo/.pi/agent/sessions/--C--Users-derek-sydney--` (original name)
- `herdr-panes.sh` default PANES is now `render forge sydney` (backed up first).
- Live evidence 9:24–9:25 AM CT: pane `w5:p1`, cwd `/home/evo/AI/sydney`, status idle, launcher `/home/evo/evo-x3/pi-chats/sydney-pi.sh` with default model `x3-local/gemma4-heretic` (no `SYDNEY_MODEL` override). After the Sydney pi process was stopped, `systemctl --user restart herdr-panes` relaunched her (`sydney workspace restored, pane w5:p1 has no agent; relaunching`). Render and Forge stayed idle on their existing sessions.

Archive still on X3 (mode 600, dir 700): `/home/derekboone/AI/_xfer/incoming/sydney-workspace.tar` (14G) and `sydney-sessions2.tar` (113M).

## Forge tool keys
Copied from AlienPc into `/home/evo/.config/forge-mcp/` (dir 700, files 0600, owner evo):
- `GITEA_ACCESS_TOKEN` from Windows Credential Manager target `gitea/forge-mcp` (len 40)
- `HA_AUTHORIZATION` from AlienPc `mcp.json` Home Assistant header (len 96)
- UniFi CA certs from `C:\ProgramData\forge-mcp\certs\`

Live `mcp.json` on X3: `/home/evo/.pi/agent/mcp.json` (0600, evo). Servers: `homeassistant`, `gitea`. Not committed.

- Gitea: Linux `gitea-mcp` v1.13.0 at `/home/evo/.local/bin/gitea-mcp`, wrapper `/home/evo/.config/forge-mcp/run-gitea-mcp.sh`. Token checks out: `https://qnap.tailf242b2.ts.net/api/v1/version` returned 200 `{"version":"28.2.0"}`. MCP handshake listed 28 read-only tools (repo/issue/PR/search/etc.).
- Home Assistant: key is in place, URL `http://192.168.0.196/api/mcp` (same as AlienPc). From the X3 this host is currently unreachable (`No route to host` on ports 80 and 8123).
- Forge pane was relaunched at 9:27 AM CT (`w4:p1`, idle, new session) so it would load `mcp.json`. Render and Sydney were left running.

## Not copied (missing or not in the live AlienPc MCP config)
- UniFi: `mcp.json` on AlienPc points at Credential Manager target `forge-mcp/unifi`, but that target is not present. Certs were copied anyway.
- Google Workspace: `C:\ProgramData\forge-mcp\google\` exists but is empty (no `client_secret.json` or credentials).
- Vaultwarden: `vw-pi` tools and Credential Manager targets `forge-mcp-vw-pi-master` / `forge-mcp-vw-pi-api` exist on AlienPc, but Vaultwarden is not in the live `mcp.json`.
- Playwright, websearch, and fetch need no keys; their Windows binaries were not Linux-installed in this pass.

## LLM key file
`/home/evo/.config/evo-x3/llm.env` is already mode 0600, owner `evo`, 76 bytes. The chats running as `evo` need this file to talk to the local models.

