# AlienPc AI launchers - ALI-150 v2 (2026-10-21)

Shortcuts that open pages, folders and windows on this PC. Rebuilt after the audit `_brief\AUDIT_46.md`
(score 46/100, verdict HOLD). Everything in this folder was **written, not run**: no shortcut, script, service,
port, GPU job, model, render, swap or loop was started by the builder. When you click one, that is the first run.

The v1 set (29 shortcuts + 10 wrappers) is in `_archive_v1\` - nothing was deleted. `_disabled_audit_HOLD\` was
left untouched (the supervisor keeps it).

Read the line for the button you want, then click it. Nothing here runs a GPU job by itself.

---

## The 15 buttons (root of this folder, in number order)

| # | Button | What happens when you click it | GPU | Stop / undo |
|---|--------|-------------------------------|-----|-------------|
| 01 | Open AI README | Opens this file. | no | - |
| 02 | Check GPU (read only) | `gpu_guard.ps1 -Gpu` prints `IDLE` (safe) or `BUSY: <reason>` and why. Window stays open. | reads only | nothing to stop, it only reads |
| 03 | Open llama-swap UI | Browser page `http://127.0.0.1:8080/ui`: which model is loaded, the model list, what is running. Opening the page loads no model. | no | close the tab |
| 04 | llama-swap Status (read only) | Prints: `GET /health`, `GET /running`, the keepalive scheduled task state, the process list. If llama-swap is down it says so and changes nothing. | reads only | nothing to stop, it only reads |
| 05 | Stop llama-swap (kills loaded model) | Guard check, then a typed `YES`, then `POST /api/models/unload`, then it ENDS the keepalive task and the llama-swap process. | frees it | bring it back with 06, or log off and on |
| 06 | Restart llama-swap (kills loaded model) | Same guard + typed `YES` + unload, then starts the keepalive task exactly as logon does and polls `/health` up to 60 s. No model is preloaded. | frees it, then reloads the service | no model loads until the next request |
| 07 | Open ComfyUI (GPU guarded) | Runs `gpu_guard.ps1 -Gpu` first. Busy -> a message box with the reason, nothing opens. Idle -> opens `http://127.0.0.1:8080/upstream/comfyui_auto/`. | **yes: opening that page loads ComfyUI and swaps out the LLM in use** | close the tab; use 05 to free the GPU |
| 08 | Open Finance App | Opens `http://127.0.0.1:3100` **only if the port is already listening**. If not, a message box tells you how to start it and starts nothing. | no | close the tab |
| 09 | Start Finance App (one instance) | Port check first. Listening -> says "already running", starts nothing. Not listening -> runs the Startup item `FinanceApp.vbs` **once** (the documented start path). | no | there is no stop script for the Finance app (known gap, see the plan) |
| 10 | Open Stash Library | Opens `http://127.0.0.1:9999` only if Stash is listening; otherwise points at its Startup item (`Stash.lnk` runs `C:\AI\stash\start-stash-hidden.vbs`) and starts nothing. | no | close the tab |
| 11 | Open Switchyard Dashboard | `C:\AI\director\tools\dcli.ps1 ui` (pins `DIRECTOR_CONFIG` to `director.live.yaml`, starts the dashboard if not up) -> page `http://127.0.0.1:8700`. | no | leave the window; the dashboard has no stop button here |
| 12 | Start Forge (GPU guarded) | `C:\AI\director\scripts\forge.ps1`: runs the GPU guard (no `-Gpu`, exit 3 = refused) and opens the coding CLI in that window so **you** type the task. Interactive, never a headless one-click run. | guard first | type `/exit` in that window, or close it |
| 13 | Stop Discord Bridge | `C:\AI\Launchers\scripts\discord-bridge.ps1 -Action Stop` -> `discord_bot_service.ps1 -Stop`. The bridge answers Discord chat; a model loads only when it forwards a request. | no | start it: same file with `-Background` (its Startup item does that at logon) |
| 14 | Stop a Loop (asks which) | Asks 1 finance / 2 community / 3 ForgeUp / 4 all chains, shows any stop text already in that file, asks before overwriting, then writes `manual stop by Derek <time>`. The loop stops at the end of its current step. | no | button 15 removes a stop file, one file at a time, asking each time |
| 15 | Clear Loop Stop Files (asks per file) | For each stop file: path, time, its text, then Y/N. **Enter = keep.** The chain stop file is never removed without an explicit `Y` for that exact file. | no | - |

Buttons 05, 06, 07, 12, 13, 14, 15 open a window that stays open (`-NoExit`) so you can read the answer.

**No loop has a Start button on purpose** (audit finding: a one-click start of a Ralph loop is a big GPU
commitment). Start them through `C:\AI\director\scripts\overnight_chain.ps1` or the supervisor, then use 14 to stop one.

## `Folders\` - 15 folder shortcuts

All are `explorer.exe "<path>"`: they open a folder, run nothing, load nothing. The `.lnk` files live in
`Folders\` so the root stays short.

| Shortcut | Opens |
|----------|-------|
| AI Folder | `C:\AI` |
| Apps Folder | `C:\Apps` |
| Switchyard (director) Folder | `C:\AI\director` |
| Switchyard Queue Folder | `C:\AI\director-queue` (the queue `gpu_guard.ps1:128` reads) |
| Switchyard Verify Queue Folder | `C:\AI\director-eval\queue-verify` |
| Runs and Outputs Folder | `C:\AI\director-runs` |
| Switchyard Logs Folder | `C:\AI\director\logs` (keeps `llama-swap-keepalive.log`, `llama-swap.out.log`, `llama-swap.err.log`, chain logs) |
| Community (video) Folder | `C:\AI\community` (referenced by `gpu_guard.ps1:7,70-77,83-84` - do not move) |
| Review Cut (HC169) Folder | `C:\AI\community\review\hc169` - the standing review folder (fix_plan 2.7): `review_cut.mp4` + `contact_sheet.png` + `review_table.md`, rebuilt by `C:\AI\community\notes\ali27_review_loop_build.py --build` in a loop pass, gate row `review_loop_check` in `notes\ali11_run_checks.py`. No GPU, no start button - it only opens a folder. |
| Stash Data Folder | `C:\AI\stash` |
| Finance Live Folder | `C:\Apps\finance-app` |
| Finance Rebuild Folder (no start button) | `C:\Apps\finance-app-rebuild` - its `start-prod.cmd` starts the **live** app, so there is no start button for it (finding F4) |
| Ralph Finance Loop Folder | `C:\Users\derek\5slock\ralph` |
| Ralph Community Loop Folder | `C:\Users\derek\5slock\ralph-community` |
| Ralph ForgeUp Loop Folder | `C:\Users\derek\5slock\ralph-forgeup` (its `ralph.ps1:2,5,29` name `C:\AI\forge-upgrades` - do not move that) |
| Windows Startup Items | `...\\Start Menu\\Programs\\Startup` |

---

## The real pages and ports (from `_brief\RECON_v2.md`, read 2026-10-21 ~5:20 PM)

| Port | What is there | How it starts | Used by |
|------|---------------|---------------|---------|
| 8080 | llama-swap (the Switchyard model loader): `/ui`, `/health`, `GET /running`, `POST /api/models/unload`, `/upstream/<model_id>` | scheduled task `Switchyard llama-swap` at logon -> `llama_swap_keepalive.ps1` (a loop, no parameters, starts llama-swap every 30 s if it is down) | 03, 04, 05, 06, 07 |
| 8080 `/upstream/comfyui_auto/` | ComfyUI, a llama-swap member (`llama-swap.yaml:91`); long video build = `/upstream/comfyui_longvideo/` (`:103`) | llama-swap loads it when the page is opened - that is why 07 is guarded | 07 |
| 3100 | Finance app (live build) | Startup `FinanceApp.vbs` -> `C:\Apps\finance-app\start-prod.cmd`. **No stop script exists.** | 08, 09 |
| 8700 | Switchyard dashboard | `dcli.ps1 ui` starts it if not up | 11 |
| 9999 | Stash image library | Startup `Stash.lnk` -> `C:\AI\stash\start-stash-hidden.vbs` | 10 |
| 8188 | **nothing listens here** (the old long-video ComfyUI port). Startup also holds a stale Edge shortcut `ComfyUI.lnk` pointing at `http://127.0.0.1:8188/` - reported, not changed. | - | no button uses it |

## The GPU guard, in its own words

`C:\AI\director\scripts\gpu_guard.ps1` (line 22-23 parameters):
`-NoHttp`, `-TimeoutSec`, `-SelfTest`, `-LockFile` (default `C:\AI\locks\gpu-render.lock`), `-Gpu`,
`-UtilMax` (30), `-GpuSamples`, `-NvSmiText`. **There is no `-Guard` switch** - the v1 wrappers used one,
which is why they never worked (finding F6). There is no `C:\AI\locks\gpu.lock` either (finding F7).

- prints `IDLE` and exits `0`; prints `BUSY: <reasons>` and exits `1`; a guard error prints `BUSY: guard error` and exits `2` (fails closed)
- checks: render processes; running jobs in `C:\AI\director-queue`; the image generator's own `/queue`;
  the lock file **only when its pid is alive** (a dead pid is stale and ignored); with `-Gpu` also `nvidia-smi` utilisation over 30 %
- how to call it: `powershell -NoProfile -ExecutionPolicy Bypass -File C:\AI\director\scripts\gpu_guard.ps1 -Gpu`

Buttons 05, 06, 07 use exactly that. 05/06 additionally **refuse** when `C:\AI\locks\gpu-render.lock` exists, and
show its text (pid, time, note) so you can see whether it is stale; only remove a lock by hand when that pid is gone.

## Stop files, and which loop reads which (read from the scripts)

| File | Read by | Written by |
|------|---------|------------|
| `C:\Users\derek\5slock\ralph\STOP_RALPH` | the finance loop **only** (`ralph.ps1:334,348`; it does **not** read `STOP_CHAIN`) | you (button 14), and `ralph.ps1:40` writes it itself on a failure |
| `C:\Users\derek\5slock\ralph-community\STOP_RALPH` | the community loop (`:267`), `chain.ps1:9` | you, the loop itself (`:33`) |
| `C:\Users\derek\5slock\ralph-forgeup\STOP_RALPH` | the ForgeUp loop (`:350,370-371,385-386`) - it also reads `STOP_CHAIN` | you, the loop itself |
| `C:\AI\locks\STOP_CHAIN` | the ForgeUp loop and `overnight_chain.ps1:11,31` | you, the chain, agents |

A stop file is often deliberate - an agent, the chain, or a loop that hit a failure put it there. That is why
button 15 shows the text and asks per file, and why 14 shows the existing text before writing over it.

## Startup items (what runs at logon - read, not changed)

- `FinanceApp.vbs` -> starts the live Finance app on 3100
- `Stash.lnk` -> `wscript.exe C:\AI\stash\start-stash-hidden.vbs` (9999)
- `DiscordForgeBridge.lnk` -> `discord_bot_service.ps1 -Background` (the bridge; there is **no** `Discord Switchyard Bridge.cmd`)
- `ComfyUI.lnk` -> stale Edge app pointing at the dead `:8188` page (reported in the plan, not touched)
- Tailscale (all users)
- llama-swap is **not** a Startup item: it is the scheduled task `Switchyard llama-swap` (at logon).

## Scripts in `scripts\` (what each button calls, and what is safe)

| File | Used by | Behaviour |
|------|---------|-----------|
| `llama-swap-status.ps1` | 04 | read only: two GETs, the task state, the process list. No start, no end, no unload, no model load. |
| `llama-swap-control.ps1` | 05, 06 | `-Action Stop\|Restart`: refuses on the render lock or a busy GPU, asks `Type YES`, unloads through the API, ends the task then the process; Restart starts the task and polls `/health` 60 s. Never `Disable-ScheduledTask`, never `Unregister`. |
| `comfy-guarded.ps1` | 07 | guard first, message box on BUSY, opens the upstream page on IDLE. |
| `open-ai-status.vbs` | 03 | opens `/ui` (v1 opened the llama-swap root page). |
| `open-finance.vbs` | 08 | valid VBScript, port check by **exit code**, opens only when listening, starts nothing. |
| `start-finance.vbs` | 09 | port check by exit code, then the Startup `FinanceApp.vbs` once, never a second instance. |
| `open-stash.vbs` | 10 | port check by exit code, opens 9999 only if listening, names the real Startup item. |
| `dcli-ui.vbs` | 11 | `dcli.ps1 ui`. |
| `discord-bridge.ps1` | 13 | `-Action Stop\|Status\|Start` -> the service's own `-Stop` / `-Status` / `-Background`. |
| `stop-loop.ps1` | 14 | asks which loop, shows the current text, writes one stop file. |
| `clear-stop-files.ps1` | 15 | shows each file, asks Y/N, default keep. |

Long video ComfyUI has no button: open `http://127.0.0.1:8080/upstream/comfyui_longvideo/` in a browser when you
want it (it loads that build and swaps out the LLM, so check 02 first).

## Rebuild and check (no shortcut runs these)

```
powershell -NoProfile -ExecutionPolicy Bypass -File C:\AI\Launchers\_tools\build-launchers.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File C:\AI\Launchers\_tools\check-syntax.ps1
python C:\AI\Launchers\_tools\check-vbs.py
```

`build-launchers.ps1` writes the 15 root + 15 `Folders\` `.lnk` files from one table, then reads every `.lnk`
back and prints target / arguments / working directory / icon / description and whether each path exists.
Last run: `built 30 shortcuts`, `MISSING: targets 0 | args paths 0 | working dirs 0 | icons 0`.
A `.lnk` is not launched by the builder, and this task launched nothing.

## What is archived, and what is outside this folder

- `_archive_v1\lnk\` - the 29 v1 root shortcuts (numbers 01-33, 39).
- `_archive_v1\scripts\` - the 10 v1 wrappers that used `-Guard` / `gpu.lock` / `:8188` / invalid VBScript:
  `clear-stop-files.cmd`, `comfy-guarded.cmd`, `desktop-cmd.vbs`, `discord-bridge-start.vbs`, `discord-bridge-stop.cmd`,
  `forge-rebuild-finance.cmd`, `llama-swap-control.cmd`, `llama-swap-keepalive.cmd`, `open-url.vbs`, `stop-file.cmd`.
- `_disabled_audit_HOLD\` - untouched (the supervisor owns it).
- Start Menu `Programs\AlienPc AI\` still holds 4 v1 copies (`01`, `16 Run GPU Check`, `17 Open AI Status Page`,
  `24 Start Forge`) and the Desktop holds `AlienPc AI.lnk`. All 5 targets still exist and the two that point at
  my scripts now get the fixed behaviour (17 opens `/ui`, 16 is the `-Gpu` check). **Deleting or renaming them is
  your call - this task was not allowed to write outside `C:\AI\Launchers`.** If you want Start Menu entries for
  the v2 names, say so and the next run can build them.

Full audit and evidence: `_brief\AUDIT_46.md`, `_brief\RECON_v2.md`, `_brief\REFS_v2.md`,
what was done now: `_brief\RESULT_v2.md`. The disk-cleanup plan is a **proposal only**:
`C:\AI\ORGANIZE_PLAN_2026-10-21.md`.
