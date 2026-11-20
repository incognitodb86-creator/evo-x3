# EVO-X3 live setup snapshot

Copied read-only from the running X3 by `scripts/snapshot-live-setup.sh` (Max Architect, Derrick t2613u).
Live files stay the source of truth; nothing here was edited on the box. Values that are secrets read
`<redacted-in-locked-keyfile>`; units and launchers read keys from owner-only files that are not in git.

Live refresh 2026-11-20 2:56 PM CT (America/Chicago): ran `scripts/snapshot-live-setup.sh` read-only on the X3 into a temp folder after merging PRs #2-#7 (`mono` 95fde8b2) and deploying `h3-render/SKILL.md` to the default, `code`, and `writertest` profiles. Against the 2:08 PM CT copy, `hermes/memories-listing.txt` changed (a directory listing), the live `h3-render` skill now matches the deployed canonical file (sha256 961e5259bfc4a5f1776299e094490f9a2b45e20c4abadfc03e03caf6f16e1fe3), and `hermes/skills/local-edits-to-bundled-skills.diff` updated with that skill. Fresh redacted copies of `profiles/grok/{config.yaml,profile.yaml,SOUL.md}` were added (never `auth.json`); `code` and `writertest` profile files were re-copied and matched the previous snapshot. `README.md`, `hermes-webui/install.txt`, `containers/_archive/`, `community/picker-rollback-hashes.txt`, and `hermes/workspace/AGENTS.md` were kept from the previous copy (the script does not emit them). Canonical `hosts/x3/pixlstash-tagging/import_inbox.py` was not overwritten. `sync-config-copies.sh` was not fully re-run: `/etc/evo-x3` is root-only and the script's first `cp` failed without sudo. AlienPc was not snapshotted (the script only covers the X3).

Live refresh 2026-11-20 2:08 PM CT (America/Chicago): ran `scripts/snapshot-live-setup.sh` read-only on the X3 into a temp folder (no lease, no live changes). Against the 1:21–1:24 PM CT copy only `hermes/memories-listing.txt` changed (a directory listing). Every other file the script emits matched. `README.md`, `hermes-webui/install.txt`, `containers/_archive/`, Hermes profile copies, `community/picker-rollback-hashes.txt`, and `hermes/workspace/AGENTS.md` were kept from the previous copy (the script does not emit them). Canonical `hosts/x3/pixlstash-tagging/import_inbox.py` was not overwritten.

Live refresh 2026-11-20 1:21–1:24 PM CT (America/Chicago): ran `scripts/snapshot-live-setup.sh` read-only on the X3 into a temp folder, plus `sync-config-copies.sh` with sudo reads of `/etc/evo-x3` (directory mode is root-only). Fresh copy includes the live `h3-render` skill (sha256 6f5ba4d71f7326ed94c4b18ec5ac9d6edbbf60073bf40e3da0885f68f66f036f, mtime 1:10 PM CT) with the stop-if-missing line. Hermes profiles: `writertest` and new `code` config/profile/SOUL were re-copied with YAML secret values redacted; the live `gemma` profile directory no longer has those files (only cron locks, not copied). `hermes-webui/install.txt` still records tag `exp-v0.52.723` at commit 3a669b5ab. `README.md` and `containers/_archive/` were kept from the previous copy (the script does not emit them). Canonical `hosts/x3/pixlstash-tagging/import_inbox.py` was not overwritten.

Live refresh 2026-11-20 07:52 CT (America/Chicago): re-ran `scripts/snapshot-live-setup.sh` read-only over `ssh evo-x3-1` into a temp folder (no lease, no live changes; temp folder removed). Against the 07:25 copy only `hermes/memories-listing.txt` changed (a directory mtime). Every other file matched.

Live refresh 2026-11-20 07:25–07:29 CT (America/Chicago): ran `scripts/snapshot-live-setup.sh` read-only on the X3 (lease taken and cleared the same morning). Compared with the 2026-11-19 9:06 PM CT copy, four files changed: `llama-swap/llama-swap.yaml` (ref2va-27b-heretic-q4 ctx 65536; `halogen-only` pins for `gemma4-heretic` and `gemma4-heretic-sub` are commented as a 2026-11-19 test window so those names hit the real Gemma container), `hermes/config.yaml` (read-only Gitea MCP server added), `hermes/memories-listing.txt` (listing only), and `hermes/skills/local-edits-to-bundled-skills.diff` (now a 13-line live edit on `h3-render`). `README.md`, `hermes-webui/install.txt`, and `containers/_archive/` were kept from the previous copy (the script does not emit them). Canonical `hosts/x3/pixlstash-tagging/import_inbox.py` was not overwritten (repo draft remains ahead of live).


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
