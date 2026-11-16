# /etc/evo-x3 env and cred files (not in git)

These files live only on the EVO-X3 at `/etc/evo-x3/` (mode 0600, root:root). Values stay in Vaultwarden and on the host. This list is names only, so a reinstall knows which files to recreate.

Do not commit the live files. Do not paste values here.

| File | Keys (names only) |
|---|---|
| `llm.env` | `LLM_KEY_ALIENPC`, `LLM_KEY_PI`, `LLM_KEY_BOX`, `LLM_KEY_HERMES`, `LLM_KEY_DERRICK_LAPTOP` |
| `gitea.env` | `GITEA_URL`, `GITEA_TOKEN` |
| `hf.env` | `HF_TOKEN` |
| `kuma.env` | `KUMA_URL`, `KUMA_URL_LAN`, `KUMA_URL_TAILNET`, `KUMA_API_KEY`, `KUMA_PUSH_ONLINE`, `KUMA_PUSH_TAILNET`, `KUMA_URL_ONLINE` |
| `ntfy.env` | `NTFY_URL`, `NTFY_TOKEN` |
| `openwebui.env` | `WEBUI_SECRET_KEY`, `OPENAI_API_KEY` |
| `pihole.env` | `PIHOLE_URL`, `PIHOLE_APP_PASSWORD` |
| `plex.env` | `PLEX_URL`, `PLEX_TOKEN` |
| `unifi.env` | `UNIFI_URL`, `UNIFI_API_KEY` |
| `vaultwarden.env` | `BW_SERVER`, `BW_EMAIL`, `BW_PASSWORD` |
| `qnap.cred` | `username`, `password`, `domain` |

`llama-swap.yaml` in this folder uses `${env.LLM_KEY_*}` placeholders only.
