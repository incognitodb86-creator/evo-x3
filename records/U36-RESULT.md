# U36 Consolidation Result — Mon Nov 16 2026 (America/Chicago)

Executor: Antigravity (Gemini 4 Hydrogen High)
Window: `2026-11-16 08:24:43 CST` – `2026-11-16 08:39:00 CST` (America/Chicago)

---

## Item Status & Evidence

### 1. `herdr` duplicate workspaces — **DONE** (`08:25–08:26 CST`, re-verified `08:38:29 CST`)
- Closed stale shell-only workspaces `w1` (`render`) and `w2` (`forge`) via `herdr workspace close` as `evo`.
- Updated `/home/evo/evo-x3/scripts/herdr-panes.sh` (and synced to `/home/derekboone/evo-x3/scripts/evo-agent-host/herdr-panes.sh`, commit `6d28e10` on `gitea/x3-pi-config`) to query `herdr pane list` + `herdr workspace get` instead of `herdr agent list` (which only lists panes with a live agent), matching restored panes by workspace label or cwd and relaunching in place.
- Restart test (`sudo systemctl restart user@1001.service` at `08:26:05 CST`, and again at `08:37:27 CST`):
  - `systemctl --user is-active herdr-server pi-mobile-hub herdr-panes` -> `active`, `active`, `active`
  - `herdr workspace list` -> exactly 2 workspaces: `[{"id":"w3","label":"render","status":"idle"},{"id":"w4","label":"forge","status":"idle"}]`
  - `herdr agent list` -> `[{"pane":"w3:p1","cwd":"/home/evo/AI/render","status":"idle"},{"pane":"w4:p1","cwd":"/home/evo/AI/forge","status":"idle"}]`
  - `/home/evo/evo-x3/logs/herdr-panes.log` -> `render workspace restored, pane w3:p1 has no agent; relaunching` and `forge workspace restored, pane w4:p1 has no agent; relaunching`.

### 2. Gap tables (R5, t1739u) — **DONE** (`08:30 CST`)
- Written to `/home/derekboone/evo-x3/records/U36-gap-tables-20261116.md` (committed `6d28e10` on `gitea/x3-pi-config`).
- Covers Render, Forge, Sydney across all 12 rows (`workspace/cwd`, `AGENTS.md`, `skills`, `extensions/packages`, `MCP`, `model`, `thinking`, `permissions`, `launcher argv`, `loop (ralph.sh)`, `memory (pi-memory / qmd)`, `phone (/remote)`).
- **AlienPc read-only comparison note:** Direct SSH from X3 to AlienPc (`100.64.221.102:22` and `192.168.0.175:22`) timed out and `https://qnap.tailf242b2.ts.net/derrick/alienpc-director.git` returned `Repository not found`; AlienPc baseline values (`pi_herdr_at_logon.ps1`, `C:\Users\derek\.pi\agent\settings.json`) are cited from prior verified X3 records (`U23`, `U33`, `U34`) and launcher headers. Live Windows diffing requires `box` SSH access if needed.
- **`qmd` decision:** Recorded as open gap (not installed). `@tobilu/qmd@2.8.3` pulls `node-llama-cpp@3.20.0` + native builds/models and `evo` npm prefix is `/usr/local`; `pi-memory@0.4.2` core tools (`write`/`read`/`scratchpad`) work without `qmd`, while `memory_search` is unavailable.
- **Forge `ralph.sh`:** Verified `0` diff vs `x3-forge` `e9730b3` (`bash -n` OK; `PROMPT.md` path updated to `/home/evo/AI/forge/ralph-community`).
- **Forge MCP servers:** Placeholders only listed in `U36-gap-tables-20261116.md` (`Home Assistant`, `UniFi`, `Gitea MCP`, `Vaultwarden`, `Google`, `Playwright`, `Fetch`; `pi-web-access` SearXNG `127.0.0.1:8888` already active).
- **Sydney (D7):** Launcher-only (`sydney-pi.sh`); listed what Derrick (or Sydney's lane) must copy to `/home/evo/AI/sydney`.

### 3. Forge workspace (D8) — **DONE** (`08:29 CST`)
- Confirmed `/home/evo/AI/forge` is `285M` (no bulk copy of AlienPc's 61.5 GB `forge` folder).
- Confirmed `git -C /home/evo/AI/forge` is at `330dd23` (`gitea/x3-forge`, above `e9730b3`), containing `.gitignore`, `.gitleaks.toml`, `.pi/settings.json` (plus installed `.pi/npm` and `.pi/git` CE plugin), `AGENTS.md` symlink, `launcher/forge-pi.sh`, `ralph-community/{PROMPT.md,ralph.sh}`.
- Recorded what `/home/evo/AI/forge` lacks vs AlienPc in `U36-gap-tables-20261116.md` (61.5 GB `5slock`/runs/refs data, MCP servers/keys, `qmd` binary for `memory_search`, `pi-computer-use`/`ralph.ps1`, Gitea push token).

### 4. `evo` trees vs git (portable paths + rsync docs) — **DONE** (`08:33–08:35 CST`)
- Made hard-coded `/home/derekboone` paths portable across `derekboone` and `evo` (using `Path(__file__).resolve()`, `os.path.abspath(__file__)`, `os.path.expanduser`, `Path.home()`, and `~/` in `render/.pi/settings.json`; locked `submit_parody_run.py` and render `skills/*` / `AGENTS.md` untouched):
  - `~/AI/community` (`7731a05`, pushed `gitea/x3-community`): `scripts/run_queue.py` (`ROOT`, `UPSCALE_PY`), `scripts/parody/{build_request.py,render_writer_pipeline.py,resolve.py,run_record.py,sync_refmods.py,voice_refmod_trim.py,wp_compile_prompt.py}`, `scripts/queue/chain_queue.py`.
  - `~/AI/render` (`f309f84`, pushed `gitea/x3-render`): `x3/linuxize.py`, `writer_pipeline/config.yaml`, `writer_pipeline/acceptance/{wp_accept.py,t3_plan.py}`, `.pi/settings.json`, `x3/README-X3.md`.
- Synced updated portable files plus P1b `x3/queue-remote.sh` into `/home/evo/AI/{community,render}` with `chown evo:evo`.
- Tests verified after edits:
  - As `derekboone`: `38 passed in 2.85s` (`test_p6_review.py`, `test_guard_scope.py`, `test_remote_comfy.py`); `ROOT= /home/derekboone/AI/community`; `auto_still` resolved `POOL_F047.jpg`.
  - As `evo`: `38 passed in 2.83s` (`test_p6_review.py`, `test_guard_scope.py`, `test_remote_comfy.py`).
- Documented the `derekboone` pull + root `rsync` + `chown evo:evo` update workflow in `~/AI/render/x3/README-X3.md`.

### 5. Docs + rollback notes + Gitea push — **DONE** (`08:34 CST`)
- Updated `~/AI/render/x3/README-X3.md` (Rendering via `queue-remote.sh` / `run_queue.py --remote`, phone `:8444`, agents as `evo`, `evo` tree rsync workflow, Known gaps).
- Updated `~/evo-x3/pi-chats/README.md` (and synced to `/home/evo/evo-x3/pi-chats/README.md`).
- Appended rollback rows to `~/evo-x3/records/U34-rollback-notes.txt` (`herdr-panes herdr-server pi-mobile-hub` disable, `tailscale serve --https=8444 off`, `dnf swap ffmpeg ffmpeg-free` + remove `rpmfusion-free-release`, P1b + U36 backups).
- Ran `gitleaks git --staged --no-banner --redact .` before every commit and `gitleaks git --no-banner --redact --log-opts "gitea/<branch>..HEAD" .` before every push (0 leaks found in all 3 repos):
  - `x3-community`: `7731a05`
  - `x3-render`: `f309f84`
  - `x3-pi-config`: `6d28e10` (plus final commit for `.gitignore` + `U36-RESULT.md`)

### 6. Smoke-render prep (D6, NO QUEUE) — **DONE** (`08:35 CST`)
- Verified `/home/evo/AI/community/runs/_x3_remote_dryrun_20261116` (`clip` + `audiotest`) as `evo` with `--dry-run`:
  - `bash /home/evo/AI/render/x3/queue-remote.sh /home/evo/AI/community/runs/_x3_remote_dryrun_20261116 --yes-derrick --dry-run` -> exited `0` (`clip: guard ok; nodes 22; uploads: image community/parody_ref_3d35921873_POOL_F034.jpg (701195B ...)`, `probe: :8446 answered HTTP Error 409: Conflict`, `dry run: no lock, upload or POST made`).
- No render was queued; no `POST /prompt` was sent.

#### Exact prompt text for Derrick's approval (`/home/evo/AI/community/runs/_x3_remote_dryrun_20261116/prompt.txt`):
```text
subject_definitions:
<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>, and high-rise apartment, its light and the opening framing: high-rise apartment, lit by soft evening light from window, rim lighting on skin, with <Subject 1> leaning, standing.
<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; an adult woman in her twenties, curvy, damp skin with a soft natural sheen and visible pores, wet, and blonde, damp, straight; she is (S1), and <Audio 1> defines her voice timbre.
<Subject 2> is an adult man, 28 years of age, of athletic build, in dark trousers; he is (S2). He is not in <Picture 1>; he enters during the clip.
HAND ANATOMY HARD-LOCKED - exactly five separate fingers, readable knuckles, no melt, merge or extra digit

summary:
[reference generation] An adult woman and her partner have missionary sex by a window.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hairstyle, body, skin and figure are kept from <Picture 1> in every phase
<Subject 2> (enters during the clip): he is not in <Picture 1>; keep the look the writer named once he is in frame
<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - high-rise apartment, the wooden sideboard, the floor, the light and the opening framing
<Audio 1> (voice of (S1)): attribute_transfer - her spoken lines take their voice timbre from <Audio 1>
The sheer white halter dress of <Picture 1>: partially_preserved - it stays on her body, pulled aside or slid up so the join is clear

detailed_description:
[Shot 1] The camera is a medium shot on a 50mm lens, capturing the pair at waist height with a shallow depth of field, framed by the soft evening light from the window. At first, (S1) leans against the wooden sideboard, her damp blonde hair catching the light, her sheer white halter dress clinging to her wet, curvy skin. (S1) shifts her weight, and (S2) guides her down so she lies back on her back on the sideboard, her hips level with his as he stands at the edge between her legs; she braces her weight on her elbows against the wood, the surface smooth under her damp skin. (S2) pulls her dress aside to one side at her hip, where it stays. His penis pushes into her vagina from the front until his hips are flush against her, and he stays buried in her. As it builds, PRIMARY MOTION - frontal thrusts, full-depth travel, one stroke every second; her breasts bounce under the sheer fabric and her damp hair whips against the sideboard. (S1) says in a low, warm adult woman's voice with a slightly husky edge, tight and breathy with the effort, <d>[English] You are being so boring.</d> (S2) says in a contrasting deep, steady adult man's voice, low and hoarse, <d>[English] Shut up and feel this.</d> By the end, (S1) smirks defiantly even as her chest heaves, her hips lifting to meet his driving thrusts. A wet, sliding sound accompanies his entry, followed by the rhythmic slap of skin on skin, and her sharp, bratty exhale.
```

#### Exact command after Derrick says yes (rebuild without `DRY_RUN` via `submit_parody_run.py --queue` to write `_render_order.json`, then queue):
```bash
sudo -n -u evo env XDG_RUNTIME_DIR=/run/user/1001 HOME=/home/evo PATH=/home/evo/.local/bin:/usr/bin \
  bash ~/AI/render/x3/queue-remote.sh <run_dir_built_with_--queue> --yes-derrick
```
(Note: `_x3_remote_dryrun_20261116` has `DRY_RUN` marker `x3 remote dry-run scratch: never queue` and both `clip` + `audiotest` in `_render_order.json`; `queue-remote.sh` intentionally refuses `DRY_RUN` dirs until rebuilt with `submit_parody_run.py --queue`.)

### 7. `pi-mobile` pairing QR — **DONE** (`08:38:22 CST`)
- Added `"publicUrl": "https://evo-x3-1.tailf242b2.ts.net:8444"` to `/home/evo/.pi/agent/pi-mobile/config.json` (mode `0600`) so `pi-mobile` emits the Tailscale HTTPS Serve URL instead of loopback only, then restarted `user@1001.service` so `pi-mobile-hub.service` holds `:7878` and `:8444` returns `200`.
- Generated pairing QR via `pi-mobile`'s `HubLink.request("pair", {})` + `qrcode` as `evo` without printing any URL or secret:
  - `QR_OK origin=https://evo-x3-1.tailf242b2.ts.net:8444 bytes=4505 expiresAt=2026-11-16T14:48:22.508Z`
- Saved as `0600` PNG (`512x512`) at `/home/evo/evo-x3/records/pi-mobile-qr.png` and copied with `sudo` (`0600`, `derekboone:derekboone`) to `/home/derekboone/evo-x3/records/pi-mobile-qr.png` (added to `evo-x3/.gitignore`).
- **TTL note:** `pi-mobile` `PAIRING_TTL` is 10 minutes (`expiresAt` `08:48:22 CST`); if expired before scanning, regenerate via `/remote pair` in a pi pane or re-run the `HubLink` `pair` call as `evo`.

---

## What Derrick Must Do
1. **Scan the `pi-mobile` QR:** `/home/derekboone/evo-x3/records/pi-mobile-qr.png` (and `/home/evo/evo-x3/records/pi-mobile-qr.png`, mode `0600`). Regenerate if >10 min has elapsed since `08:38:22 CST`.
2. **Type Forge's MCP keys (placeholders in `U36-gap-tables-20261116.md`):** `Home Assistant`, `UniFi`, `Gitea MCP`, `Vaultwarden`, `Google`, plus decide if `Playwright`/`Fetch` or `@tobilu/qmd` (`memory_search`) should be installed for `evo`.
3. **`agy` sign-in as `evo`:** `agy` currently runs as `derekboone` only.
4. **Yes on the smoke-render prompt (D6):** Review the pasted `prompt.txt` above, rebuild a non-`DRY_RUN` run with `submit_parody_run.py --queue`, and approve `bash ~/AI/render/x3/queue-remote.sh <run> --yes-derrick`.
5. **Sydney's private files (D7):** Copy Sydney's persona/`AGENTS.md`/chats/memory/voice refs to `/home/evo/AI/sydney` (or let Sydney's own lane do it), then start with `PANES=sydney bash /home/evo/evo-x3/scripts/herdr-panes.sh`.

---

## Changes & Backups

| File Changed | Backup Path |
|---|---|
| `/home/evo/evo-x3/scripts/herdr-panes.sh` | `/home/evo/evo-x3/_archive/herdr-panes.sh.bak-20261116-082541-u36` |
| `/home/derekboone/evo-x3/scripts/evo-agent-host/herdr-panes.sh` | `/home/derekboone/evo-x3/_archive/u36/evo-x3/scripts/evo-agent-host/herdr-panes.sh.bak-20261116-u36` |
| `/home/derekboone/evo-x3/pi-chats/README.md` | `/home/derekboone/evo-x3/_archive/u36/evo-x3/pi-chats/README.md.bak-20261116-u36` |
| `/home/evo/evo-x3/pi-chats/README.md` | `/home/evo/evo-x3/_archive/u36/pi-chats-README.md.bak-20261116-u36` |
| `/home/derekboone/evo-x3/records/U34-rollback-notes.txt` | `/home/derekboone/evo-x3/_archive/u36/evo-x3/records/U34-rollback-notes.txt.bak-20261116-u36` |
| `/home/derekboone/evo-x3/.gitignore` | `/home/derekboone/evo-x3/_archive/u36/evo-x3/.gitignore.bak-20261116-u36` |
| `/home/evo/.pi/agent/pi-mobile/config.json` | `/home/evo/evo-x3/_archive/u36/pi-mobile-config.json.bak-20261116-u36` |
| `/home/evo/AI/render/x3/queue-remote.sh` (synced P1b) | `/home/evo/evo-x3/_archive/u36/queue-remote.sh.bak-20261116-u36` |
| `/home/derekboone/AI/community/scripts/{run_queue.py,queue/chain_queue.py,parody/*.py}` (9 files) | `/home/derekboone/evo-x3/_archive/u36/community/.../*.bak-20261116-u36` |
| `/home/derekboone/AI/render/{x3/linuxize.py,x3/README-X3.md,writer_pipeline/config.yaml,writer_pipeline/acceptance/*.py,.pi/settings.json}` (6 files) | `/home/derekboone/evo-x3/_archive/u36/render/.../*.bak-20261116-u36` |
| New records created | `/home/derekboone/evo-x3/records/U36-gap-tables-20261116.md`, `/home/derekboone/evo-x3/records/U36-RESULT.md`, `/home/evo/evo-x3/records/pi-mobile-qr.png` (`0600`), `/home/derekboone/evo-x3/records/pi-mobile-qr.png` (`0600`) |
