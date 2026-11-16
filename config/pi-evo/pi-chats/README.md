# pi chats on the EVO-X3

Launchers for Derrick's pi chats on the X3. Installed 2026-11-15 and **not production** until Derrick OKs the picks. See `~/evo-x3/records/U23-render-pi-chats-20261115.md` (gap table) and `~/AI/render/x3/README-X3.md`.

- `render-pi.sh`: Render (`~/AI/render`, x3-local/gemma4-heretic). Links to `~/AI/render/x3/render-pi.sh`.
- `sydney-pi.sh`: Sydney launch config only. Persona and private files are not on the X3.
- `forge-pi.sh`: Forge config mirror (`~/AI/forge`, x3-local/flash-next). No MCP servers yet.

Renders run on AlienPc ComfyUI and are queued only after Derrick's yes: `~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick`.
