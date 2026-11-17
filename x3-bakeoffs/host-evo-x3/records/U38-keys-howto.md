# U38 — Forge MCP Keys How-To (Vaultwarden, Google Workspace, UniFi)

All three servers are installed as `evo` and configured **disabled** (`"enabled": false`) in `/home/evo/.pi/agent/mcp.json`. Edit the matching `0600` env file under `/home/evo/.config/forge-mcp/`, then run the one-liner at the bottom to enable it and restart the Forge pane. **Never commit** `mcp.json` or anything in `/home/evo/.config/forge-mcp/`.

---

## 1. Vaultwarden (`vaultwarden`)

- **File to edit:** `sudo -iu evo nano /home/evo/.config/forge-mcp/vaultwarden.env` (keep `0600`)
- **Variables:**
  - `BW_SERVER=` — Your Vaultwarden base URL (e.g., `https://...`, same server URL used in `/etc/evo-x3/vaultwarden.env` or your QNAP/Vaultwarden web vault).
  - `BW_SESSION=` — Session token from `bw unlock --raw` (required for vault read/write on this headless server, because interactive OS password dialogs aren't available).
  - `BW_CLIENTID=` & `BW_CLIENTSECRET=` — Optional personal API key if signing `evo`'s `bw` CLI in non-interactively via `bw login --apikey`.
  - `BW_CLIENT_ID=` & `BW_CLIENT_SECRET=` — Optional Organization API credentials (for `*_org_*` admin tools only).
  - `BW_API_BASE_URL=` & `BW_IDENTITY_URL=` — Optional self-hosted overrides if using Org API tools (e.g., `<BW_SERVER>/api` and `<BW_SERVER>/identity`).
- **Where to get the keys:**
  - **Personal API key (`BW_CLIENTID` / `BW_CLIENTSECRET`):** Vaultwarden web vault → **Account Settings → Security → Keys → View API Key**.
  - **Session token (`BW_SESSION`):** As `evo`, run:
    ```bash
    sudo -iu evo bash -c 'bw config server "<YOUR_VAULTWARDEN_URL>" && bw login && bw unlock --raw'
    ```
    Paste the printed token into `BW_SESSION=` in `vaultwarden.env`.
  - **Org API key (optional):** Organization → **Settings → My Organization → API Key**.

---

## 2. Google Workspace (`google-workspace`)

- **File to edit:** `sudo -iu evo nano /home/evo/.config/forge-mcp/google-workspace.env` (keep `0600`)
- **Variables:**
  - `GOOGLE_OAUTH_CLIENT_ID=` — OAuth 2.0 Desktop/Web Client ID.
  - `GOOGLE_OAUTH_CLIENT_SECRET=` — OAuth 2.0 Client Secret.
  - `USER_GOOGLE_EMAIL=` — Your Google account email (used in `--single-user` mode).
  - `WORKSPACE_MCP_CREDENTIALS_DIR=/home/evo/.config/forge-mcp/google-creds` *(pre-filled, `0700`)*.
  - `OAUTHLIB_INSECURE_TRANSPORT=1` *(pre-filled for localhost OAuth callback)*.
- **Where to get the keys & sign in:**
  1. **Google Cloud Console** (`console.cloud.google.com`) → select/create project → **APIs & Services → Library** (enable Gmail, Calendar, Drive, Docs, Sheets, etc. as needed) → **Credentials → Create Credentials → OAuth client ID** (Desktop app, or Web app with `http://localhost:8000/oauth2callback` redirect URI). Copy Client ID and Client Secret into `google-workspace.env`.
  2. **One-time OAuth sign-in:** Run `workspace-mcp` once over SSH port-forward (`ssh -L 8000:127.0.0.1:8000 ...`) or on a browser session to complete the Google OAuth consent flow; tokens are saved into `/home/evo/.config/forge-mcp/google-creds/`.

---

## 3. UniFi Network (`unifi`)

- **File to edit:** `sudo -iu evo nano /home/evo/.config/forge-mcp/unifi.env` (keep `0600`)
- **Variables:**
  - `UNIFI_HOST=` — UniFi OS console / UDM IP or hostname (e.g. `192.168.1.1` or `192.168.0.x`, without `https://`).
  - `UNIFI_API_KEY=` — Local UniFi Network API key (preferred over username/password).
  - `UNIFI_PORT=443`, `UNIFI_SITE=default`, `UNIFI_VERIFY_SSL=false` *(pre-filled; UDM CA certs are already copied at `/home/evo/.config/forge-mcp/certs/udm-console-443.pem` if you want to pin `UNIFI_NETWORK_SSL_FINGERPRINT` or `SSL_CERT_FILE` and set `UNIFI_VERIFY_SSL=true`)*.
  - `UNIFI_READ_ONLY=true` *(pre-filled; enforces read-only tools by default)*.
- **Where to get the key:**
  - **UniFi OS / Network UI** (`https://<UNIFI_HOST>`): **Control Plane → Admins & Users** (or **Settings → Control Plane → Integrations**) → **Create API Key** (read-only role recommended; `UNIFI_READ_ONLY=true` also blocks mutations in the MCP server).

---

## Enable & Restart Forge Pane (One Command)

Replace `<SERVER>` with `vaultwarden`, `google-workspace`, or `unifi`:

```bash
sudo -iu evo bash -c 'S=<SERVER>; python3 -c "import json,os; p=os.path.expanduser(\"~/.pi/agent/mcp.json\"); d=json.load(open(p)); d[\"mcpServers\"][\"$S\"][\"enabled\"]=True; json.dump(d,open(p,\"w\"),indent=2); os.chmod(p,0o600)" && pi mcp list && P=$(herdr pane list | jq -r ".result.panes[]|select(.cwd==\"/home/evo/AI/forge\")|.pane_id" | head -n1) && PID=$(herdr pane process-info --pane "$P" | jq -r ".result.process_info.foreground_processes[]|select(.name==\"pi\")|.pid" | head -n1) && [ -n "$PID" ] && kill -INT "$PID" && sleep 2; PANES=forge bash /home/evo/evo-x3/scripts/evo-agent-host/herdr-panes.sh'
```

*(Note: `herdr-panes.sh` only relaunches the Forge pane if its `pi` process exited; Render and Sydney panes are left untouched.)*
