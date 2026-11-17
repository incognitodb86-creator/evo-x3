# PixlStash library location — 16 Nov 2026

Community way: official remote access is the REST API (and optional ComfyUI-PixlStash nodes) over the LAN or Tailscale, with tokens from Settings → API Tokens ([api](https://pixlstash.dev/api.html), [README](https://github.com/Pikselkroken/pixlstash), accessed 16 Nov 2026 CT). A library is a folder of pictures plus its database; move it with `pixlstash-cli libraries backup` / `restore`, or copy the folder to local disk and `attach` / `relocate`. ComfyUI shares model folders with `extra_model_paths.yaml` on a network drive ([ComfyUI docs](https://docs.comfy.org/basic-concepts/models)). No official PixlStash guide was found for putting `vault.db` on SMB/NFS → adapt: use a share only for a file copy or for ComfyUI models, never to open the database over the network.

## Recommendation

Put the library on the X3 and run the PixlStash server there. Leave AlienPc’s copy untouched until the X3 side checks out. Do not leave the server on AlienPc and “just read the files” over a share, and do not point an X3 PixlStash at `vault.db` on an SMB/NFS mount.

The tagging model and Render already live on the X3; AlienPc is meant to stay render-only, and its 16 GB GPU is busy with ComfyUI. SQLite is designed for a local disk ([SQLite over a network](https://sqlite.org/useovernet.html)): put a network link in the file channel and you risk corruption and a sharp slowdown. PixlStash’s own write/ALL tokens are allowed only from loopback or RFC 1918 (`is_local_ip`). Tailscale `100.64.0.0/10` is deliberately excluded from that gate (widened only for library host-ops). A write token from the X3 to an AlienPc server over Tailscale IPv4 would 403 unless you weaken `require_local_for_write` or go through a LAN/RFC 1918 address. Read-only share tokens work from any IP, which is enough to fetch a still, not enough to tag.

Read-only check of both vaults (16 Nov 2026 CT, counts only, no filenames or image content): all 32,964 and all 489 `picture.file_path` rows are relative (zero `C:\` or Unix-absolute prefixes), so a folder copy plus `attach` should find the pictures. Each vault has one Windows-absolute `folder_mapping_commit.root_path`. In approved_characters only, all 489 `tags_file` and 489 `description_file` values are Windows-absolute — verify those sidecars after attach; do not rewrite paths unless attach/restore leaves them broken.

## Options

- **A — leave it on AlienPc, X3 uses the API.** Official for still search. Tagging and write tokens fight the Tailscale write gate and AlienPc GPU contention. Today’s Render script still looks for local `vault.db` paths that are empty on the X3. Tailscale Serve HTTPS from the X3 already failed once this session.
- **B — move to the X3 (pick this).** Official Linux install (`pip` + systemd, or Docker GPU) on [install](https://pixlstash.dev/install.html). Library on local disk next to the server. Render talks to localhost. Tagging stays on the X3. AlienPc copy is the rollback.
- **C — network the drives (SMB/NFS over Tailscale), keep one library.** Fine later for ComfyUI models (community pattern: scoped share + `extra_model_paths.yaml`). Fine as a copy pipe. Bad as the home of `vault.db`. A read-only image share does not replace the API or a local server. If you add shares, scope them to named folders, prefer read-only, and allow TCP 445 only from the tailnet (`100.64.0.0/10`), never the internet. LAN IPs are faster at home than a DERP relay; this morning’s Taildrop already ran on the LAN. This option does not change the pick: the library still wants a local disk on the X3.

## Copy method (no new access)

AlienPc → X3 already works: this morning Sydney’s 14 GB workspace went by `tailscale file cp` (Taildrop) on the LAN and landed in `/home/derekboone/AI/_xfer/incoming`. Use the same path for both library folders (~52.8 GB total; 801 GB free on the X3). No new SSH key. After it lands, move the folders to `/home/evo/AI/5slock/{libraries,approved_characters}` so the current parody script’s paths exist, then attach both libraries. Official `libraries backup` is also fine, but the archive includes `hub.db` (login and token secrets) — owner-readable only, never chat or git. Stop PixlStash on AlienPc for the copy so the database is consistent.

## Steps (nothing runs until you say yes)

1. Stop PixlStash on AlienPc. Taildrop both library folders (or one official backup per library) to the X3 incoming folder; leave the AlienPc originals in place.
2. Install PixlStash on the X3 the official way. Place the folders under `/home/evo/AI/5slock/`. `pixlstash-cli libraries attach` both (one is open at a time; a token can be set to every library).
3. Mint the API token in Settings on the X3 (owner, local). Store it in an X3 0600 secret file, never in chat or git.
4. Smoke check counts only (32,964 and 489) and that approved-character sidecars still resolve. Do not open images. Then point Render at the local API.

**Rollback:** start AlienPc’s existing app again. Stop and detach the X3 server. Nothing on AlienPc was changed.

**You need to OK:** this location pick; the X3 install; the Taildrop of both libraries (~53 GB); minting the token in the UI and saving it on the X3; and, only if you want it later, a scoped SMB/NFS share for ComfyUI models — not for `vault.db`.
