# EVO-X3 U23: Render pi chat setup installed, plus a config mirror for Sydney and Forge (2026-11-15)
Max Architect. Derrick, 2:09–2:10 PM CT: "Yes, add the temp Q4 slot and run the blind test", "copy it over", "Do it correctly and ensure the setup and rules are updated", "And transferred over to the setup on x3". 2:34 PM CT: "Any gaps".

**Status:** installed and verified on the X3, **not production.** The live Render, Sydney, Forge and phone chats stay on AlienPc until Derrick OKs the picks (cutover plan: fleet-brain `40_projects/compute-expansion/plans/2026-11-15-1001-evo-x3-chat-cutover-plan.md`). Production llama-swap and pi model mappings are unchanged.

## What is where on the X3
| Item | Path | Matches AlienPc |
|---|---|---|
| Community repo (builders, skills, agent-shared) | `~/AI/community`, branch `x3-linux` | `b81b04f` + `f583442` (AlienPc's uncommitted tree) + `b63cfbb` (Linux paths, key read, Linux `--queue` refusal) |
| Render repo (AGENTS.md, RUN_ME, writer_pipeline, .pi) | `~/AI/render`, branch `x3-linux` | `4254b04` + `93e3c9c` (AlienPc's uncommitted tree) + `d8eca65` (X3 setup) |
| Fleet-brain skills | `~/AI/fleet-brain/20_skills/current` | copy of AlienPc `C:\AI\fleet-brain` @07b4e7f |
| Render docs | `~/AI/render/x3/README-X3.md` | — |
| Launchers | `~/evo-x3/pi-chats/{render,sydney,forge}-pi.sh` | AlienPc `pi_herdr_at_logon.ps1` argv, minus `--remote`/herdr/pi-mobile |
| Remote queue | `~/AI/render/x3/queue-remote.sh <run_dir> --yes-derrick` → `~/evo-x3/scripts/comfy-submit.sh` → https://alienpc.tailf242b2.ts.net:8446 | Derrick: "X3 can queue ComfyUI renders on AlienPc over the tailnet". Not exercised |
| Stills | `~/AI/render/stills/approved_characters/POOL` (104 images) | images only, no vault.db or sidecars |
| RefMods | `~/AI/comfy-alienpc/models/refmods` | 5 OC files real, 1,495 name stubs |

Start Render: `bash ~/evo-x3/pi-chats/render-pi.sh` (one-shot: add `-p --no-session "<ask>"`). Model: Render → `x3-local/gemma4-heretic`.

## Checks
- `verify-serve.sh`: after the Q4 slot was added 401/200; after it was removed 401/200; `/v1/models` = embed-small, flash-next, gemma4-heretic, qwen27b.
- Builder Fix A/B tests (`test_chain_lock_fixAB.py`, b81b04f): 6 passed on the X3.
- Writer pipeline smoke on X3 Q8: READY in 52 s, dry run.
- Launch smoke: Render (9 skills), Sydney (`ok`), Forge (flash-next, 41 skills) all answered.
- Blind Heretic Q8_0 vs Q4_K_M test: 6/6 READY, dry run, nothing queued. Outputs are on the box at `/workspace/maxops/prompts/heretic-q8-vs-q4-blind-20261115/`. KEY.txt is kept separate for Prompt maker's blind scoring.
## Gap audit: AlienPc vs EVO-X3 for each pi chat (2026-11-15, Derrick t1745u "Any gaps")
Read-only comparison, then config-only fixes. Sydney's chats, persona content and memory were not read or copied. No live chat was cut over and no production model mapping changed.

| # | Chat | Area | Gap in plain words | Status |
|---|---|---|---|---|
| 1 | Render | Workspace, AGENTS.md, skills, builders | The X3 had no Render setup at all | **Fixed.** `~/AI/render` + `~/AI/community` cloned at AlienPc's commits, plus AlienPc's uncommitted changes, with only the paths changed for Linux |
| 2 | Render | Launch | AlienPc's Render pane runs a stripped pi (9 skills, no MCP, set extensions) | **Fixed.** `~/AI/render/x3/render-pi.sh` uses the same argv |
| 3 | Render | Python | Builder needed pysbd/pillow/numpy/opencv | **Fixed.** venv `~/AI/render/x3/.venv` |
| 4 | Render | Writer key | The writer pipeline couldn't read the X3 key (pi uses a `!cat` key file) | **Fixed.** Read inside the process, never printed |
| 5 | Render, Sydney | Vision | The X3 Heretic slot is text-only, so Render/Sydney can't look at a new still. The builder itself needs no vision model | **Open.** Needs Derrick's vision pick (bake-off recommends Heretic Q4_K_M + mmproj in one slot) |
| 6 | Render, Sydney | Thinking | AlienPc runs Heretic with thinking medium (PolyStrata); the X3 slot has thinking off | **Open.** Part of the model pick |
| 7 | Render | Queue to AlienPc ComfyUI | `--queue` has no Linux route | **Partly fixed.** `x3/queue-remote.sh` uploads the stills and posts to AlienPc ComfyUI over the tailnet, and on Linux `--queue` refuses and points to it. Never run (no render was approved). It doesn't check AlienPc's GPU lock or lease |
| 8 | Render | GPU lock | AlienPc's `gpu-render.lock` isn't visible from the X3 | **Open** |
| 9 | Render | Stills | Only the 104 POOL images were copied. `stills/comfy_input` (3.3 GB, 12.5k files) and the other approved folders weren't | **Open.** Copy more or mount the QNAP when Derrick says so. PixlStash vaults are never copied |
| 10 | Render | RefMods | 1,500 RefMods live on AlienPc | **Fixed for writing.** The 5 OC RefMods are real files and the rest are 0-byte name stubs, which go stale when AlienPc adds more |
| 11 | Render | Run folders | A relative run path makes the pipeline write under the chat's cwd, outside `runs/` and past the write sandbox (the bash tool isn't covered). The Q4 chat hit this. AlienPc has the same bug | **Open.** Builder fix needs Derrick's OK |
| 12 | Render | Git home | AlienPc b81b04f and its uncommitted changes aren't in Gitea, so the X3 can't `git pull` yet | **Open.** Push from AlienPc, then switch the X3 remote to Gitea |
| 13 | Render | Acceptance | `run_acc4.ps1` is Windows-only | **Open** (minor) |
| 14 | Sydney | Launch config | No Sydney setup on the X3 | **Fixed.** `~/evo-x3/pi-chats/sydney-pi.sh` (same argv as AlienPc, model x3-local/gemma4-heretic), empty workspace `~/AI/sydney` |
| 15 | Sydney | Persona, private files, AGENTS.md, voice, notes, memory | Not copied, by rule | **Open.** For Derrick or Sydney's own lane to move |
| 16 | Forge | Workspace and config | No Forge setup on the X3 | **Fixed.** `~/AI/forge`: AGENTS.md links to `community/agent-shared/AGENTS.md` (as on AlienPc), project settings carry AlienPc's packages (incl. compound-engineering with the same skill filters), skills and prompts; launcher `~/evo-x3/pi-chats/forge-pi.sh` (x3-local/flash-next); `~/.pi/agent/web-search.json` (SearXNG) mirrored |
| 17 | Forge | AGENTS.md content | The rules describe Windows/AlienPc (PowerShell, %USERPROFILE%, Household key folders) | **Open.** Needs an X3 rules pass |
| 18 | Forge | MCP servers | playwright, websearch, fetch, homeassistant, gitea, unifi, google: most carry keys | **Open.** Derrick types the keys / Household creates the accounts |
| 19 | Forge | Tools and loops | `powershell` tool and the `ralph.ps1` loop are Windows-only | **Open** |
| 20 | Forge | Data root | `C:\Users\derek\forge` = 5slock (PixlStash libraries, runs, refs) | **Open, by rule.** Never copied |
| 21 | Phone | Bridge | pi-mobile hub (task `pi-mobile`, 127.0.0.1:7878, Tailscale Serve 8443) and herdr panes (`PiHerdrAtLogon`) don't exist on the X3 | **Open.** Install, Tailscale Serve on the X3 (ACL is Derrick's), and the cutover yes |
| 22 | All | Model mapping | Render/Sydney `gemma4_heretic_poly_think` → `gemma4-heretic` (Q8); Forge `coding_swift15_iq3s_esp` → `flash-next`; `vl_judge`, `qwen3vl_judge`, `joycaption`, `gemma4_heretic_poly` have no X3 slot; `comfyui_*` stays on AlienPc | **Open.** No production mapping changed; waits for Derrick's OK on the picks |
| 23 | All | Not installed | pi-computer-use (headless X3), pi-mobile, herdr | **Open.** By design until the phone cutover |
