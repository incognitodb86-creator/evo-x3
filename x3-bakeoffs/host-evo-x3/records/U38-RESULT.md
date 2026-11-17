# U38 — Forge Tool Parity Result (2026-11-16)

All 7 steps of `/home/derekboone/evo-x3/records/U38-forge-parity-brief-20261116.md` are complete. No secrets were read, logged, printed, or committed; `homeassistant` and `gitea` entries in `/home/evo/.pi/agent/mcp.json` remain unchanged; `llama-swap`, models, AlienPc, Windows partitions, Sydney files, and U37 were untouched.

## Backup & Config Files

- Backup: `/home/evo/.pi/agent/_archive/mcp.json.bak-u38` (`0600`, `evo:evo`, 590 B)
- Live MCP config: `/home/evo/.pi/agent/mcp.json` (`0600`, `evo:evo`, 2057 B; not committed)
- Secrets/wrappers dir: `/home/evo/.config/forge-mcp/` (`0700`, `evo:evo`; not committed)

## What Was Installed & Versions

| Step | Server (`mcp.json` key) | Package / Binary (Pinned) | Status | Notes |
|---|---|---|---|---|
| 1 | `playwright` | `@playwright/mcp@0.0.85` (`/home/evo/.local/bin/playwright-mcp`) + Playwright Chromium `v1254` (`Google Chrome for Testing 158.0.8127.18`) | **Enabled** | Headless (`--headless --browser chromium --user-data-dir /home/evo/.cache/forge-playwright`). `ldd` confirmed all shared libs present (no `dnf` deps needed). |
| 2 | `searxng` | `mcp-searxng@2.10.1` (`/home/evo/.local/bin/mcp-searxng`) | **Enabled** | `SEARXNG_URL=http://127.0.0.1:8888` (local X3 `searxng` Podman container). |
| 2 | `fetch` | `mcp-server-fetch==2026.11.11` via `/usr/bin/uvx` (`uv` `0.13.7-3.fc44` installed via `dnf`) | **Enabled** | Official MCP fetch server. |
| 3 | `vaultwarden` | `@bitwarden/mcp-server@2026.7.0` (`/home/evo/.local/bin/mcp-server-bitwarden`) + `@bitwarden/cli@2026.10.1` (`/home/evo/.local/bin/bw`) | **Disabled** | Placeholder `/home/evo/.config/forge-mcp/vaultwarden.env` (`0600`) + wrapper `/home/evo/.config/forge-mcp/run-vaultwarden-mcp.sh` (`0700`). Note: Vaultwarden does not run locally on X3 (`/etc/evo-x3/vaultwarden.env` is root-only and was not read), so `BW_SERVER=` is blank for Derrick. |
| 4 | `google-workspace` | `workspace-mcp==2.5.0` (`taylorwilsdon/google_workspace_mcp`, `/home/evo/.local/bin/workspace-mcp`) | **Disabled** | Placeholder `/home/evo/.config/forge-mcp/google-workspace.env` (`0600`), creds dir `google-creds/` (`0700`), wrapper `run-google-workspace-mcp.sh` (`0700`), `--single-user`. |
| 5 | `unifi` | `unifi-network-mcp==0.46.0` (`sirkirby/unifi-network-mcp`, `/home/evo/.local/bin/unifi-network-mcp`) | **Disabled** | Placeholder `/home/evo/.config/forge-mcp/unifi.env` (`0600`) with `UNIFI_READ_ONLY=true` default + wrapper `run-unifi-mcp.sh` (`0700`). |

## Test Summaries (as `evo`)

- **`pi mcp list --json`:**
  - `gitea`: connected, 28 tools (unchanged)
  - `playwright`: connected, 25 tools
  - `searxng`: connected, 4 tools
  - `fetch`: connected, 1 tool
  - `vaultwarden`, `google-workspace`, `unifi`: `disabled` (`"enabled": false`)
  - `homeassistant`: unchanged (`failed` on X3 due to AlienPc `powershell.exe` header command)
- **Live MCP stdio tool call checks (without invoking `llama-swap`):**
  - `playwright`: `browser_navigate` to `https://example.com` -> Page Title `Example Domain`; `browser_evaluate` `() => document.title` -> `"Example Domain"`. Dedicated profile created under `/home/evo/.cache/forge-playwright/`.
  - `searxng`: `searxng_web_search` (`"Model Context Protocol"`) -> returned 3,420 chars of search results (`https://modelcontextprotocol.io`, etc.).
  - `fetch`: `fetch` (`https://example.com`) -> `HTTP/1.1 200 OK`, returned 208 chars (`# Example Domain ...`).

## Docs Written

- `/home/derekboone/evo-x3/records/U38-keys-howto.md` — 1-page setup guide covering `vaultwarden.env`, `google-workspace.env`, `unifi.env`, where to obtain each credential, and the single command to enable each server and restart only the Forge pane.

## What Waits on Derrick

1. **Forge pane reload for enabled tools (`playwright`, `searxng`, `fetch`):** The existing Forge pane (`w4:p1`, started 09:27 CT) was left running to avoid disrupting active sessions; restart the Forge pane (see `U38-keys-howto.md`) whenever ready for Forge to pick up `playwright`, `searxng`, and `fetch` in its live session.
2. **Vaultwarden:** Fill `BW_SERVER`, `BW_SESSION` (and optionally `BW_CLIENTID`/`BW_CLIENTSECRET` or Org `BW_CLIENT_ID`/`BW_CLIENT_SECRET`) in `/home/evo/.config/forge-mcp/vaultwarden.env`, then enable `vaultwarden` in `mcp.json`.
3. **Google Workspace:** Fill `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, and `USER_GOOGLE_EMAIL` in `/home/evo/.config/forge-mcp/google-workspace.env`, complete the one-time OAuth browser sign-in, then enable `google-workspace` in `mcp.json`.
4. **UniFi Network:** Fill `UNIFI_HOST` and `UNIFI_API_KEY` in `/home/evo/.config/forge-mcp/unifi.env` (`UNIFI_READ_ONLY=true` already set), then enable `unifi` in `mcp.json`.
