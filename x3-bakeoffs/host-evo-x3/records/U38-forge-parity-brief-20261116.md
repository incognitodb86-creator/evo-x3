# U38 Forge tool parity (Derrick t1886, Nov 16 2026)
Goal: Forge (pi chat as user evo, MCP config /home/evo/.pi/agent/mcp.json, secrets dir /home/evo/.config/forge-mcp/ 0700) gets its own tools like Max: a Playwright browser, web search + fetch, Vaultwarden, Google Workspace, UniFi.

HARD RULES
- Back up mcp.json to /home/evo/.pi/agent/_archive/mcp.json.bak-u38 first. Never delete; archive.
- Never print, log, echo or put on argv any secret. Never create API keys, accounts, OAuth clients or Tailscale keys. Derrick types every key himself.
- Never commit mcp.json or anything under forge-mcp. Keep homeassistant and gitea entries unchanged.
- Do not restart llama-swap, touch models, AlienPc, Windows partitions, or Sydney files. Do not interfere with the other agy run (U37).
- Use official or most-used community MCP servers, pinned versions, run as evo.

STEPS
1. Playwright: install @playwright/mcp (Microsoft) + chromium for user evo (npx playwright install chromium; system deps via sudo dnf if needed). Headless, own profile dir /home/evo/.cache/forge-playwright. Add to mcp.json.
2. Web search + fetch: if SearXNG runs on the X3, add a SearXNG MCP (mcp-searxng) pointed at it; add the official fetch MCP (mcp-server-fetch via uvx). Add both.
3. Vaultwarden: install the official Bitwarden MCP server (@bitwarden/mcp-server) + bw CLI, server URL = the X3 Vaultwarden. Create placeholder /home/evo/.config/forge-mcp/vaultwarden.env (0600) with the variable NAMES it needs, values blank. Add the entry disabled until filled.
4. Google Workspace: install the most-used community server (taylorwilsdon/google_workspace_mcp). Placeholder google-workspace.env (0600) with OAuth client id/secret variable names. Entry disabled until Derrick provides the OAuth client and signs in.
5. UniFi: install the most-used community UniFi Network MCP (e.g. sirkirby/unifi-network-mcp), read-only tools by default. Placeholder unifi.env (0600) with host + API key names. Entry disabled until filled.
6. Test: as evo, list tools for each enabled server (pi non-interactive or MCP inspector). Playwright must open https://example.com and return its title; search must return results; fetch must fetch a page.
7. Write a 1-page how-to /home/derekboone/evo-x3/records/U38-keys-howto.md: for Vaultwarden, Google Workspace and UniFi, the exact file to edit, variable names, where Derrick gets each key, and the one command to enable it and restart the Forge pane.

STOP CONDITION: write /home/derekboone/evo-x3/records/U38-RESULT.md (what installed, versions, test summaries, what waits on Derrick), then stop.
