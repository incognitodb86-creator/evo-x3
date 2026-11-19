# U39 PixlStash move — RESULT

Date: Monday 16 Nov 2026, America/Chicago (CT)

## Outcome

The merged Stills `libraries` vault is on the X3 and is the active library in a new official PixlStash 2.0.1 server, bound to localhost only. AlienPc’s live PixlStash, libraries, ComfyUI, and GPU were not stopped or changed. `approved_characters` was not copied, per Derrick (t1925u). The parody script was not edited.

## What moved

- Source: `C:\Users\derek\5slock\libraries` on AlienPc, excluding `.pixlstash-thumbnails` and the live `vault.db` / WAL / SHM.
- `vault.db` on the X3 is the sqlite backup-API snapshot taken at `C:\Users\derek\_pixlstash_xfer\payload\libraries\vault.db` while PixlStash stayed running on AlienPc.
- Method: direct LAN TCP stream, 192.168.0.175 → 192.168.0.166:49817. X3 firewall allowed TCP 49817 only from 192.168.0.175 for the transfer, then the rule and listener were removed (confirmed: no rich rules, port not listening).
- Destination: `/home/evo/AI/5slock/libraries`, owner `evo`, directories 700, files 600.
- Throughput: started 10:27:19 CT, finished 10:58:07 CT (1848.3 s). Logical 55,538,579,919 bytes, wire 55,687,628,800 bytes, 28.73 MiB/s. Receiver tar exit 0.
- After extract, two SQLite sidecar files (`vault.db-wal` 0 bytes, `vault.db-shm` 32,768 bytes) appeared and were removed once nothing had the database open. File count then matched exactly.

## Verification

| Check | Expected | Result |
| --- | --- | --- |
| File count (no thumbnails; snapshot db, not live db) | 77,379 | 77,379 |
| Logical bytes (payload at end of stream) | 55,538,579,919 | 55,538,579,919 (wire 55,687,628,800). After extract, a 0-byte WAL and 32,768-byte SHM appeared and were removed once; file count then was 77,379. The running server has since reopened the db, so WAL/SHM exist again and the folder is slightly larger from normal server use. |
| `vault.db` SHA-256 | `b6458f280faea2e29d2e205bd4bff1d4a7781a22de2eab171413ea9b1cf0fd3d` | match |
| Sampled SHA-256 (vault.db + 20 files) | 21 | 21 matched, 0 failed |
| Pictures via `GET /api/v1/pictures/count` (READ and ALL tokens) | 32,964 | 32,964 |
| Faces | 116,876 | 116,876 by read-only `COUNT(*)` on the attached `vault.db` (same file the server uses). The official API has no library-wide face total (only per-character / per-picture face routes). Characters via API: 2. |
| Parody pytest (`/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/parody` from `/home/evo/AI/community`) | pass | 563 passed, 5 skipped in 4.71s |

One Windows-absolute `folder_mapping_commit.root_path` row was rewritten to `/home/evo/AI/5slock/libraries` after a sqlite backup of the db to `/home/evo/AI/5slock/_u39_vault.db.bak-prerewrite`. Windows-prefix count: 1 before, 0 after.

AlienPc staging `C:\Users\derek\_pixlstash_xfer` was deleted after verification. The live AlienPc library was left in place.

## Server and tokens

- Install: official `pixlstash` 2.0.1 in `/home/evo/.venvs/pixlstash` (CPython 3.13.18 via uv). `default_device` is `cpu`.
- Service: systemd --user unit `pixlstash.service` for `evo`, enabled, linger already yes. Active and listening on `http://localhost:9537` (`127.0.0.1` and `::1` only).
- Active library: `libraries` at `/home/evo/AI/5slock/libraries`. An empty default “Library 1” under `~/.config/pixlstash/images` is still registered and is not active.
- Token files (0600, owner `evo`; values not recorded here):
  - `/home/evo/.config/pixlstash/tagger-write.token` — scope ALL (write-capable; the API does not mint a separate WRITE scope)
  - `/home/evo/.config/pixlstash/render-read.token` — scope READ
- Owner login secret: `/home/evo/.config/pixlstash/owner.password` (0600). The first-start env file was removed after the account was claimed so the password is not left in the process environment.

## Parody script note

`submit_parody_run.py` was not edited. `_PIXLSTASH_VAULTS` is still defined there (around line 730). Nearby lines still mention `approved_characters` (including lines 726–727 and 734). That folder was not copied to the X3, so any path to `approved_characters` will not resolve until the later repoint fix lands. Pytest still passed.

## Left for Derrick

- Later fix to repoint the parody script at the merged vault only.
- No tagging pass was run.
- Optional: detach empty “Library 1” if you do not want it listed.
- Optional: if you later want PixlStash face/tag work on the X3 GPU, the user service currently logs that GPU utilisation sampling sees no CUDA device and is set to CPU so it does not contend with llama-swap. That can be revisited separately.
- The pre-rewrite vault backup is still at `/home/evo/AI/5slock/_u39_vault.db.bak-prerewrite` (0600, evo). Say if you want it removed.
