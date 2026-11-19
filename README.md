# EVO-X3 + AlienPc all-in-one snapshot (updated Nov 19, 2026, Derrick t2613u)

Each folder is the exact tree of one Gitea branch (Gitea derrick/evo-x3 stays the source of truth; GitHub mirrors it).
Start with `x3-host-u58/hosts/SETUP-MAP.md`, then `x3-host-u58/hosts/x3/live/README.md`.

| Folder | Branch @ commit | What it is |
|---|---|---|
| x3-render | x3-render @ 92325452 | X3 Render: OPERATOR.md, AGENTS.md writer book, RUN_ME.md, writer_pipeline, render-pi.sh, queue-remote.sh |
| x3-community | x3-community @ 6bdcc49c | X3 community: render_writer_pipeline.py, run_queue.py, remote ComfyUI/upscale, H3 skills, templates |
| x3-forge | u58-chat-read-plan @ 4cbbba00 | X3 Forge (ralph-community, loop-guard, records) - live Forge branch |
| x3-host-u58 | u58 @ 4cd04c71 | X3 host: hosts/x3/live (llama-swap with Gufo/Halogen, Hermes, pi, herdr, PixlStash, systemd, bin, containers), config/, records/ and plans incl. records/hermes-direct-render/PLAN.md; hosts/alienpc (ComfyUI inventory, launchers) |
| alienpc-render | alienpc-render @ 5c3450d4 | AlienPc C:\AI\render |
| alienpc-community | alienpc-community @ 6dadffc4 | AlienPc C:\AI\community |
| x3-bakeoffs, x3-pi-config | unchanged since Nov 17-18 | older bakeoff and pi-config branches |
| alienpc-comfyui-config | Nov 17 snapshot | older AlienPc ComfyUI copy; newer one is x3-host-u58/hosts/alienpc/comfyui |
| plans | - | plan v3.2 and AlienPc dual-boot plan |

No keys, .env, token files, auth.json, DBs, sessions/memory, PixlStash library, models, outputs or venvs.
