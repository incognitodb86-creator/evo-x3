# H7 + H8 Result (2026-11-19)

**Plan:** `records/unified-implementation/PLAN.md` rows H7, H8 (brief: `records/H7-H8-agy-brief-20261119.md`)
**Overall status:** PASS

---

## H7: Hermes WebUI

- **Repository / Install path:** `https://github.com/nesquena/hermes-webui.git` cloned as user `evo` at `/home/evo/hermes-webui`
- **Pinned commit:** `6c4aaaaf0beae8a95addc2c2b7e340203b7dd72b` (`master`, `docs(changelog): stamp v0.52.701 stable section (promotion) (#9190)`)
- **Systemd user unit:** `/home/evo/.config/systemd/user/hermes-webui.service` (`enabled`, `active (running)`)
- **Port / Bind:** `127.0.0.1:8787` (loopback only; verified via `ss -tlnp`). No Tailscale serve port added (`tailscale serve status` unchanged; Open WebUI on `127.0.0.1:3000` untouched).
- **Gateway wiring:**
  - `HERMES_WEBUI_CHAT_BACKEND=gateway`
  - `HERMES_WEBUI_GATEWAY_BASE_URL=http://127.0.0.1:8642`
  - `HERMES_WEBUI_GATEWAY_USE_RUNS_API=true` (enables Runs API + visible WebUI approval cards)
  - `HERMES_API_URL=http://127.0.0.1:8642`
  - `MEDIA_ALLOWED_ROOTS=/home/evo/AI/5slock/libraries`
  - `EnvironmentFile=%h/.config/evo-x3/llm.env` (provides `API_SERVER_KEY` without duplicating any key)
- **Health check:** `GET http://127.0.0.1:8787/health` -> HTTP 200 (`"status": "ok"`).

---

## H8: PixlStash Skill + Approvals

### Skill change
- **File:** `/home/evo/.hermes/skills/pixlstash-image-library/SKILL.md`
- **Backup path:** `/home/evo/.hermes/_archive/pixlstash-image-library-SKILL.md.bak-20261119-h8`
- **Summary of changes:**
  - Replaced direct `vault.db` sqlite queries and scratch `.py` script instructions with `curl` + `jq` lookups against PixlStash's HTTP API on `http://127.0.0.1:9537`:
    - `GET /api/v1/characters` to resolve character IDs
    - `GET /api/v1/pictures` with `character_id=`, repeatable `tag=` / `rejected_tag=`, `format=JPEG&format=PNG`, `fields=id,file_path,format,score,smart_score`, `sort=`, `limit=`
    - `GET /api/v1/tags` (filtered via `jq`) for exact tag discovery
    - `GET /api/v1/pictures/search` via `curl -sSG --data-urlencode "query=..."` (noting not to combine `character_id=` with `/pictures/search` on large character sets, which hits SQLite's 32,766 bind-variable limit)
  - Explicitly forbids `write_file`, scratch `.py` files, `vault.db` queries, `python3 -c`, and heredocs (`<<EOF`).
  - Reads the read-only Bearer token inside the command from `/home/evo/.config/pixlstash/render-read.token` (`$(cat /home/evo/.config/pixlstash/render-read.token)`); no token value is stored in the skill, commands, logs, or this report.
  - Exposes selected images via space-free symlinks `/home/evo/.hermes/image_cache/pixl_<id>.<ext>` -> `/home/evo/AI/5slock/libraries/<file_path>` and emits `MEDIA:/home/evo/.hermes/image_cache/pixl_<id>.<ext>` lines (required because PixlStash library subpaths with spaces truncate at the first space under `MEDIA:([^\s\)\]]+)` in Hermes WebUI).
- **`hermes-gateway.service`:** Not restarted (`skill_view` reads `SKILL.md` dynamically from disk; verified active and unchanged).

### Approval investigation & change
- **Root cause of today's block:** Checked `/home/evo/.hermes/logs/agent.log` and `state.db` (`api-c21d84f1b201489f`). Hermes's first `terminal` call (`id=699`) ran `python3 - <<'EOF'` (because the previous skill directed `vault.db` Python queries), matching Hermes's `script execution via heredoc` guard in `tools/approval_detection.py`. Over `/v1/chat/completions` (Open WebUI), `api_server` could not deliver the interactive approval prompt (`API server uses HTTP request/response, not send()`), so the prompt timed out after `approvals.timeout: 30`s.
- **Stock Hermes findings (`hermes approvals test` + `tools/approval*.py`):**
  - Read-only `curl` GET requests to `http://127.0.0.1:9537` with `-H "Authorization: Bearer $(cat /home/evo/.config/pixlstash/render-read.token)"` piped to `jq` (and `ln -sf`) match **zero** `DANGEROUS_PATTERNS` guards and return `verdict: allow (exit 0)`.
  - `command_allowlist` in `tools/approval_floors.py` intentionally skips commands containing `$(...)` or pipes (`_has_allowlist_shell_operator`), and adding a trailing-wildcard `curl` glob would be overly broad (could cover `-d @...` uploads).
  - Enabling `HERMES_WEBUI_GATEWAY_USE_RUNS_API=true` in `hermes-webui.service` ensures that any command that *does* trigger an approval in Hermes WebUI surfaces as a visible approval card rather than failing silently.
- **Approval config change & backup:** None needed in `/home/evo/.hermes/config.yaml` (`approvals.mode: manual`, `approvals.unattended_mode: deny`, `approvals.timeout: 30` preserved as-is; no `config.yaml` backup created because `config.yaml` was not modified).

---

## End-to-End Test ("H8 test")

- **WebUI session ID:** `5763d1cdff20` (WebUI title: `H8 test`; `state.db` session ID: `5763d1cdff20`, source: `api_server`)
- **Tool calls in `~/.hermes/state.db` (in order):**
  1. `skill_view`
  2. `terminal`
  3. `terminal`
  4. `terminal`
- **Counts:**
  - Total tool calls: `4`
  - `write_file` calls: `0`
  - Scratch scripts / `vault.db` references: `0`
  - Token occurrences in session messages: `0`
  - `MEDIA:` image lines returned: `5` (5 unique)
  - WebUI `/api/media` inline render checks (`HTTP 200`, `image/jpeg`): `5 / 5`
- **Verdict:** **PASS**

---

## Cleanup

- `/home/derekboone/AI/locks/x3-lease.txt` cleared (0 bytes).
- Note: Do not run `git add -A` on `~/evo-x3`; only `records/H7-H8-RESULT.md` was written in `~/evo-x3`.
