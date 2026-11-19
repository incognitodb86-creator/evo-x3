# EVO-X3 live setup snapshot

Copied read-only from the running X3 by `scripts/snapshot-live-setup.sh` (Max Architect, Derrick t2613u).
Live files stay the source of truth; nothing here was edited on the box. Values that are secrets read
`<redacted-in-locked-keyfile>`; units and launchers read keys from owner-only files that are not in git.

| Program | Folder |
|---|---|
| llama-swap (model router; Gufo, Halogen and strix toolboxes are launched from its `cmd:` lines) | `llama-swap/` |
| Container images incl. gufo-runtime, halogen-flash-server, strix toolboxes (tags + digests) | `containers/images.txt` |
| SearXNG quadlet; retired Open WebUI quadlet (removed 2026-11-19, Derrick t2688u) | `containers/`, `containers/_archive/` |
| Hermes WebUI (tailnet chat UI since 2026-11-19: Serve 8443 `/` → 127.0.0.1:8787; nesquena/hermes-webui @ 6c4aaaa in `/home/evo/hermes-webui`, code not copied) | `systemd/evo-user/hermes-webui.service` |
| Forge + Render project `.pi` (settings, extensions incl. auto-continue.ts) | `pi-evo/projects/` |
| Hermes Agent (config, SOUL, custom skills, edits to bundled skills, version) | `hermes/` |
| pi (evo: settings, permissions, MCP, models example, extensions, packages, panes) | `pi-evo/agent`, `pi-evo/panes` |
| pi chat launchers (Render, Forge) and evo-x3 scripts (pi-mobile hub, herdr panes, comfy-submit) | `pi-evo/pi-chats`, `pi-evo/evo-x3-scripts` |
| pi (derekboone, Max's harness) | `pi-derekboone/agent` |
| herdr | `herdr/` + `systemd/evo-user/herdr-*.service` |
| PixlStash server config (no DB/library/tokens) | `pixlstash/` ; tagger code in `../pixlstash-tagging/` |
| systemd: system units (llama-swap, QNAP mounts, backups, kuma) and evo user units (Hermes gateway, PixlStash, tagger, renders sync, pi-mobile) | `systemd/` |
| /usr/local/bin scripts (pi-job, sync-renders, fr-readonly, config backup/rsync) | `bin/` |
| Forge MCP launchers (tokens read from evo-only files) | `forge-mcp/` |
| aria2, agy, tailscale (version + serve status), nested community repos | `aria2/`, `agy/`, `tailscale/`, `nested-repos.txt` |

Render, community and Forge are their own branches: `x3-render`, `x3-community`, `u58-chat-read-plan` (Forge).

Not in git on purpose: `.env` files, `/etc/evo-x3/*.env|*.cred`, `*.token`, `auth.json`, `models.json` (example kept),
PixlStash DB/library/password/tokens, Hermes `state.db`/sessions/memories/cron outputs, ssh keys and authorized_keys,
herdr session snapshots, pi sessions/memory, the Sydney pane, models, outputs, venvs, node_modules.
