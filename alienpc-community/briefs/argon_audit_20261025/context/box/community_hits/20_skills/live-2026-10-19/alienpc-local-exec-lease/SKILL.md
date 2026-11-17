---
name: AlienPc local-exec lease
description: >-
  use this when AlienPc Shell hangs, ListMachines says connected but Shell is
  dead, local-exec-daemon leftover, temporarily unreachable, two bots (e.g. CoS and
  Max lane owner) might dual-hit Shell, or before starting AlienPc Shell work while away from the PC
---
# AlienPc local-exec lease

## When
AlienPc (or any registered desktop) Shell hangs, dual bots may share the PC, or Derrick is away and local-exec needs recovery rules.

## Detect
- ListMachines `connected: true` but Shell never returns stdout (even a one-line Write-Output)
- Read / CopyToBox may still work
- "temporarily unreachable" flaps on AwaitShell
- Optional signal: Grok Bot `dune-reliability` session `childDeaths.node` rising (CAPA 2026-10-05)

## Correct (on that PC)
1. All bots **HOLD** — stop AlienPc Shell (no retry-spam)
2. If Derrick **login/unlock** just woke the PC: wait **~30–60s** → **one** Shell smoke (Modern Standby path — CAPA 2026-10-05 ~9:17 CT)
3. If unlock does **not** restore Shell: tray **Quit** Grok Bot → Task Manager end **Grok Bot** + **local-exec-daemon** (if present) → relaunch → wait **~1 minute** → one probe
4. **One** owner only; then resume work
5. If a Comfy matrix was mid-run: **do not re-queue** — check `/queue` + `/history/{prompt_id}` → harvest → resume driver **skip ok metas**

## Prevent
1. **Single lease:** only the holder named in the latest AlienPc lease file (brain-staging/30_handoff/status/*lease*) runs Shell on AlienPc. Others ask that holder and wait for its release line. Announce HOLD/clear on handoff.
2. Hang >15–30s empty → stop; **≤1** Shell retry then HOLD — do not stack more Shells.
3. PowerShell-native on Windows (`;`, not bash `&&`).
4. Before travel: install remote GUI (AnyDesk/TeamViewer/RDP) so Quit+relaunch works off-site.
5. **Modern Standby (LOCKED 2026-10-05 ~9:17 CT):** if login/unlock restores Shell, cause class = S0 idle (Kernel-Power 506) — set display-off AC **Never** during Max queues; Quit/kill is secondary.
6. **Comfy-authoritative matrices (LOCKED 2026-10-05):** write `prompt_id` early; survive driver/Shell death; harvest from Comfy history on resume. Shell channel ≠ Comfy.
7. Chat room message-cap ≠ render loss — Desktop pack paths are SoT for clips.
8. Flap log fields: ListMachines · smoke · `childDeaths.node` · Comfy prompt_id · driver PID alive?


9. **During Max queues on AC (Research 2026-10-06 `d7e086a9…`):** screen/display off = **Never** · sleep = **Never** · **no auto-lock** · leave **Grok Bot window frontmost**. PowerToys Awake does **not** work on lock screen — change the power plan instead. Verify with `powercfg /requests` + absence of Kernel-Power **506**.
10. Next flap: pull `%APPDATA%\Grok Bot\local-exec-daemon.log` and `%USERPROFILE%\.grokbot\` (staff/community paths) + Event Log 506/507 before blaming only sleep.
11. Timeout eviction: after a timed-out Shell/copy, wait ~1 min and start a **new turn** (machine roster fixed at turn start) — do not immediate retry-spam.

## Do not / EXPERIMENTAL forbidden
- Dual Shell, any two bots (was Dial+CoS) (**FORBIDDEN** — CAPA 2026-10-02 wedge)
- Expect phone app or Update Grok Bot's Computer to fix local-exec (cloud box only)
- Kill-by-agent when Shell itself is the dead channel (cannot taskkill through it)
- Retry-spam / invent parallel claimants while lease broken
- Blame classic sleep without Event Log check — also check Kernel-Power **506/507** (Modern Standby). First flap window 0 Kernel-Power 18:00–20:20 was a **false negative** (already in S0 since ~5:55 PM)
- Ignore **Modern Standby (Kernel-Power 506 Idle Timeout)** when unlock/login restores Shell (2026-10-05 ~21:14 CT) — classic Sleep after=Never can still S0; set **display off AC = Never** during matrices
- Treat a single-holder (Max lane owner) lease as “immune” — a solo holder can still flap (Node/local-exec)

Ops mirror: [alienpc-local-video-ops](sand-workflow:alienpc-local-video-ops) `../alienpc-local-video-ops/references/local-exec-lease-full.md`.

## Stamp
- `/workspace/cos/audits/2026-10-02-alienpc-local-exec-wedge-capa.md` (dual-Shell)
- `/workspace/cos/audits/2026-10-05-alienpc-shell-flap-rca.md`
- `/workspace/cos/audits/2026-10-05-alienpc-shell-flap-capa.md` (Dial-only residual)
- `/workspace/cos/audits/2026-10-05-alienpc-shell-flap-repeat-rca.md` (Modern Standby)
- `/workspace/cos/audits/2026-10-05-alienpc-shell-flap-modern-standby-auditor.md`

## Still-running processes (required in every lease file)
Each lease grant/release file lists processes still running on AlienPc at handoff (pid, who started them, what they do) and who owns them. A lease move does **not** kill background jobs. Never kill AlienPc Local AI / Forge / Antigravity processes from a lease change alone — only the process owner or Derrick stops them.

