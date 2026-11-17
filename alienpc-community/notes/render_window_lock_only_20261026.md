# The render window is a lock, not a llama-swap group (GPU-LOCK, 2026-10-26)

Plan row: `C:/Users/derek/5slock/ralph-community/fix_plan.md` L130 ("Forge renders through
llama-swap /comfyui itself; the GPU lock is the only gate", Derrick 2026-10-24 3:16 PM CT
"render the clips yourself", 2026-10-25 3:56 AM CT). Record:
`C:/Users/derek/5slock/ralph-community/notes/plans/receipts/Forge-L130.md`.

## The fault, in one line

`notes/rt_window_probe.py` (Ralph's cwd) was red (`RT_WINDOW_PROBE FAULTS RT_PERSISTENT checks=13`)
because it demanded a `persistent: true` llama-swap group for `comfyui_auto`, and
`C:/AI/director/config/llama-swap.yaml` has no `persistent:` key: `comfyui_auto` is a member of the
one `main` group (`swap: true`, `exclusive: true`) with the 5 LLM ids. Three rule files
(`ralph-community/AGENTS.md` render line + L19, `C:/Users/derek/5slock/AGENTS.md`, and the config's
own comment) asserted the flag the file does not contain.

## Why the config is right and the gate was wrong

`persistent` is published as "other groups can never unload this one"
(`C:/AI/community/notes/web/rt_ls_groups-and-matrix.txt:55-57`), i.e. co-residency. Measured on this
box 2026-10-26 06:1x CT with `comfy_ctl.py status` = `running=['comfyui_auto']`, no LLM resident:

```
nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits
16303, 15355, 641
```

`C:/AI/director` commit `66cddc1` (2026-10-25 07:13) put ComfyUI at ~12 GB and the LLM at ~11.5 GB.
Two such backends do not fit in 16 GB, so a persistent non-swapping render group is not reachable
here. `36dadae` (2026-10-25 19:35, "prevent VRAM squeeze", no body) unified the group back into
`main`; its mechanism was sound, its record was missing, and the config comment kept saying
"The group is persistent" - which is how the rule files inherited a claim no file carries (L4).

## What the gate polices now (16 checks, 16 seeds)

| Detector | Enforced mechanism | Seeded past wiring that fires it |
|---|---|---|
| `RT_NO_CO_LOAD` | render model shares the ONE `swap: true` group with the LLM ids → a model load never co-resides two ~11 GB backends | the `66cddc1` persistent group text, copied out of `git show 66cddc1` and inserted verbatim (fires alone) |
| `RT_STOP_DEFERS` | `cmdStop` = `C:/AI/director/scripts/comfy_graceful_stop.ps1`, its `MaxWaitSec` parsed from the live script | the ALI-156 pre-fix plain `taskkill` |
| `RT_UNLOAD_BUDGET` | `unloadTimeout` (1900) above the stop script's own cap (`MaxWaitSec = 1800`) | an `unloadTimeout` under the cap |
| `RT_TTL_SELFHEAL` | `poll < ttl <= 900` (`ttl: 300`): idle self-heal only, published range | the old `ttl: 0` |

`RT_PERSISTENT` is gone. The old 13 checks were the 16 above minus these four, with
`RT_PERSISTENT` in their place (`git show HEAD:notes/rt_window_probe.py | grep -oE "RT_[A-Z_]+" | sort -u`
prints exactly that 13-name set): one check that named a shape the hardware cannot host became four
that name mechanisms this box runs.

## The deferral, counted off the log the stop script writes

`C:/AI/director/logs/comfy-graceful-stop.log` holds 10 `render queue busy (1 job(s)) ... waiting`
rows. Each is matched to its own pid's `stop after Ns` line, so the number is the queue-drain wait
the script measured:

- port `:10004` × 8 → 771, 821, 911, 801, 771, 811, 851, 390 s
- port `:10099` × 2 → 24, 8 s (a 2026-10-24 00:32 pair, before the 10099 route settled)

So the swap waited for the render, never the reverse. The only ~20-minute caller behind the
`:10004` rows was the `ForgeAgyMonitor` scheduled task, now Disabled. After `36dadae` both lock-held
render windows paid: `C:/AI/community/runs/ali163_top5_gi046_s51160001/status.log` (2026-10-25
22:56:28) and `.../ali163_top5_gi046_s51160002/status.log` (23:46:43) end with
`gpu_lock release rc=0` and the mp4 is on disk. 0 evictions inside a lock-held window.

## The lock is the gate (unchanged, and now the only claim the rules make)

`C:/AI/community/scripts/run_graph_job.py` → `comm.guard_ok` (adults) → `gpu_guard.ps1` rc 0 →
`C:/AI/director/scripts/gpu_lock.ps1 -Acquire` (lock file under `C:/AI/locks`, owning PID) →
llama-swap `/prompt` → collect → `gpu_lock.ps1 -Release`. A client stall is exit 6 and never
re-queues: the clip is collected from `ComfyUI/output/community/<id>/`.

## Reproduce

```
python C:/Users/derek/5slock/ralph-community/notes/rt_window_probe.py --check
#  RT_WINDOW_PROBE CLEAN checks=16 comm_sha=6caad36c37b4 region_sha=c06e11e8a474
python C:/Users/derek/5slock/ralph-community/notes/rt_window_probe.py --selftest
#  SELFTEST_OK seeds=16 missed=[] base_dirty=[]
python C:/Users/derek/5slock/ralph-community/notes/gpu-lock-plan-row.py       # dry run, re-measures nvidia-smi + log + gate
python C:/Users/derek/5slock/ralph-community/notes/ali05_loop_check.py        # VERDICT CLEAN, the cross-file rule agreement (L17)
python C:/Users/derek/5slock/ralph-community/notes/ali05_loop_check.py --selftest   # 70 seeded faults, 0 did not fire
python C:/AI/community/scripts/comfy_ctl.py status                             # guard=(0, ['IDLE'])
C:/AI/director/scripts/gpu_guard.ps1                                          # IDLE, rc 0
```

No render, no queue, no LLM request was made by this item. `C:/AI/community/scripts/comm.py` is
untouched: the adults surface stays 488 B, sha256 `c06e11e8a47420f3a5d6dc788aaf0010d778e7059eafb9fad209aab8ec1f5a90`
(`RT_GUARD_REGION` reads it live).
