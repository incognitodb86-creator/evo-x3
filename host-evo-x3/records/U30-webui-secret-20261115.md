# U30 — Open WebUI secret off process argv (MF-12), 2026-11-15

Authority: Derrick t1815u "Yes and yes" (Open WebUI secret fix).
Executor: Max (Grok Bot executor), 7:15–7:16 PM CT Nov 15 2026.

Antigravity MF-12 said `WEBUI_SECRET_KEY` sat on uvicorn argv and was world-readable in `/proc/<pid>/cmdline`. The live container already loaded the key from `/etc/evo-x3/openwebui.env` (root 0600) via Quadlet `EnvironmentFile`. A pre-change scan found no secret values in `ps -ef`, `/proc/*/cmdline`, `podman inspect` Args/Cmd, or the unit file. The official image `start.sh` still launches the server as `exec env WEBUI_SECRET_KEY=... python3 -m uvicorn ...`, which can put the key on a command line. U22 noted that risk. This change bypasses `start.sh`, keeps the key in the env file only, and rotates it.

## Backups (taken 7:15:04 PM CT, America/Chicago)
- Unit: `/etc/containers/systemd/open-webui.container.bak-20261115-191504`
- Full set (dir mode 0700): `/var/backups/evo-x3/u30-webui-secret-20261115-191504/`
  - `open-webui.container` (unit copy, no secrets)
  - `openwebui.env` (root 0600; previous secret; not in etckeeper; `/etc/evo-x3/*.env` is gitignored)

## Changes
- `/etc/containers/systemd/open-webui.container`: added `Exec=` so the container runs `/usr/local/bin/python3 -m uvicorn open_webui.main:app --host 127.0.0.1 --port 3000 --forwarded-allow-ips * --workers 1 --ws-per-message-deflate true` (WORKDIR `/app/backend`). Image `start.sh` is no longer used. `EnvironmentFile=/etc/evo-x3/openwebui.env` is unchanged. Non-secret `Environment=` lines are unchanged. Image digest is unchanged (`ghcr.io/open-webui/open-webui@sha256:59b912d4246103c7285de0e9a5f2f6586614c06b4c4e46edc51a8f29e7b099a5`).
- `/etc/evo-x3/openwebui.env`: `WEBUI_SECRET_KEY` rotated to a new 64-hex-char value generated on the X3 and written straight to this file (mode 0600, atomic replace). `OPENAI_API_KEY` was not changed. Values were never printed, logged, or passed on a command line.
- Restarted only `open-webui.service` (daemon-reload + restart at 7:15:29 PM CT) after confirming no mid-chat (no HTTP in the prior 5 minutes, no established sockets on 3000/8443). Health OK at 7:15:49 PM CT. `llama-swap.service` was not touched (stayed active, MainPID 99654 throughout).

Users are signed out of Open WebUI once. That is expected after the rotation.

## Verification (7:15–7:16 PM CT, America/Chicago)
| Check | Result |
|---|---|
| `WEBUI_SECRET_KEY` (new or old) in `ps -ef` | not present |
| Secret values in `/proc/*/cmdline` | not present |
| uvicorn cmdline | `/usr/local/bin/python3 -m uvicorn open_webui.main:app --host 127.0.0.1 --port 3000 --forwarded-allow-ips * --workers 1 --ws-per-message-deflate true` (no `start.sh`, no `WEBUI_SECRET_KEY`) |
| uvicorn `/proc/<pid>/cmdline` mode | 0444 (world-readable, but no secret on it) |
| uvicorn `/proc/<pid>/environ` | mode 0400 (root only); contains the new key; does not contain the old key |
| `podman inspect` Args / Cmd / Entrypoint | uvicorn args only; no secret values; Entrypoint null |
| `podman inspect` Config.Env | has the new key (environment, not argv); does not have the old key |
| Quadlet and generated unit file | no secret values; `EnvironmentFile=` / `podman --env-file /etc/evo-x3/openwebui.env`; no `--env WEBUI_SECRET_KEY=` |
| `openwebui.env` mode | 0600 root:root |
| `GET http://127.0.0.1:3000/health` | 200 `{"status":true}` |
| `GET http://127.0.0.1:3000/` | 200 `text/html` title Open WebUI |
| `GET https://evo-x3-1.tailf242b2.ts.net:8443/health` from the X3 and from the box | 200 `{"status":true}` |
| `GET https://evo-x3-1.tailf242b2.ts.net:8443/` from the X3 and from the box | 200 `text/html` title Open WebUI (TLS verify ok from the box) |
| `/api/config` | `features.enable_login_form=true`, `features.enable_signup=false`, `features.auth=true` |
| `llama-swap.service` | still active, MainPID unchanged (99654) |
| `open-webui.service` | active (running) since 7:15:29 PM CT, NRestarts=0 |

Note: a naive grep of `systemctl cat open-webui.service` can match the new comment that quotes `start.sh`'s `WEBUI_SECRET_KEY=...` pattern. That comment has no secret value. The generated `ExecStart=` line uses `--env-file` only.

## Restore
```bash
sudo cp /etc/containers/systemd/open-webui.container.bak-20261115-191504 /etc/containers/systemd/open-webui.container
sudo cp /var/backups/evo-x3/u30-webui-secret-20261115-191504/openwebui.env /etc/evo-x3/openwebui.env
sudo chmod 600 /etc/evo-x3/openwebui.env
sudo systemctl daemon-reload
sudo systemctl restart open-webui.service
```
Restoring the old env file signs everyone out again (the restored key is the previous one). Do not print the file.

## Not done
- Did not remount `/proc` with `hidepid=2` (not in the approved task).
- Did not change `OPENAI_API_KEY`, llama-swap, Tailscale Serve, or the Open WebUI image.
