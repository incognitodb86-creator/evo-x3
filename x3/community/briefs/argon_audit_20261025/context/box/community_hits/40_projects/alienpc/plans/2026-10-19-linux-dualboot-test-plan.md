---
title: Linux dual-boot A/B test on AlienPc (measure only; no migration yet)
created: 2026-10-19 09:30 CT
author: Max Architect (executor via CoS)
owner: Max Architect (single AlienPc executor)
lane: AlienPc Local LLM Setup
status: awaiting Derrick phase-0 approval
research: /workspace/cos/audits/2026-10-19-linux-vs-windows-alienpc.md
standing_rules: /workspace/cos/brain-staging/10_packs/fleet/derricks-standing-rules.md
expected_quota_pct: ~2% (planning + Linear only this turn); phases 1–3 ~8–15% if Max guides live; phase 0 money is Derrick's
hardware_known: RTX 5070 Ti 16 GB; Alienware Aurora R16 (from Linear doc AlienPc current setup)
stack_note: Wan 2.2 + generation-time RIFE retired; A/B uses 10Eros H3 + llama-swap/Strata (ALI-80; current-setup doc). FastH3 Omni preferred if landed by test day.
hygiene: Alfred 2026-10-19 ~10:40 AM CT — Linear ALI-90/93/95 + sequential blocks + off-goal
---

## Goal
Measure whether **native Ubuntu 24.04 LTS on a separate second SSD** beats current Windows for the **current** AlienPc stack (10Eros H3 I2V — no Wan 2.2, no generation-time RIFE — plus llama-swap/Strata Forge) **before migrating anything**. Success = Derrick has one A/B table and chooses migrate / stay / hybrid. Nothing starts until Derrick approves phase 0.

## Community path (do this, not custom)
- Keep Windows intact on its current disk. **Never repartition the Windows disk.**
- Install Ubuntu 24.04 LTS on a **new/second SSD** only (community dual-boot pattern; Pop!_OS optional if Derrick prefers Nvidia-friendly defaults).
- NVIDIA **proprietary** driver (Ubuntu `ubuntu-drivers` / nvidia-driver-xxx); enroll MOK if Secure Boot stays on.
- Put ComfyUI models and GGUFs on the **Linux ext4 filesystem** (not `/mnt/windows`); stock Comfy + 10Eros H3 path + llama-swap/llama.cpp CUDA builds (Wan 2.2 and generation-time RIFE are retired — see Linear doc *AlienPc current setup* and ALI-80).
- Agents: Antigravity CLI (`agy`) and Gemini CLI both officially support Linux (agy install script for Linux; Gemini CLI lists Ubuntu 20.04+). Prefer `agy` if unpaid Gemini CLI redirected to Antigravity (2026-06).
- Research backing: `/workspace/cos/audits/2026-10-19-linux-vs-windows-alienpc.md`.

## Preconditions / stop rules
- Max is sole AlienPc executor for this plan; no parallel AlienPc GPU work during A/B.
- Lane rule: **max 3 In Progress**; this parent stays **Backlog/Todo** until Derrick opens phase 0.
- Stop if: Windows disk would be repartitioned; any delete of Windows AI data; install fails Secure Boot/GPU and guide cannot recover in one session; A/B metrics incomplete; quota burn would exceed card without Derrick OK.
- Rollback anytime: reboot → Windows (Linux SSD unused or left installed but unused).

## Phases
| Phase | Who | Work | Approval card |
|------|-----|------|----------------|
| **0** | Derrick | Buy or choose second SSD; approve plan + money | **Card A:** drive purchase/money + go/no-go |
| **1** | Derrick + Max guide | Backup critical Windows paths (list only); install Ubuntu 24.04 on second SSD; BIOS boot order / Secure Boot / MOK as needed | **Card B:** BIOS/boot changes; **Card C:** Ubuntu ISO download + install (no Windows repartition) |
| **2** | Max (on Linux boot) | Stock ComfyUI **10Eros H3** + llama-swap/Strata; optional `agy`/Gemini CLI smoke (no Wan 2.2, no gen RIFE) | **Card D:** downloads/installs on Linux SSD only |
| **3** | Max | **ONE** identical real job on both OSes: one **10Eros H3 I2V** clip (`10Eros_Max_h3_8stepTURBO_beta6_int8`, or **FastH3 Omni**-based 10Eros if it has landed by then; **no RIFE in generation**, per ALI-80) + one **llama-swap/Strata** Forge prompt; record s/step, total wall time, peak VRAM (nvidia-smi), tok/s, errors | none beyond Card D if already approved; no deletes |
| **4** | Derrick | Decide: migrate primary AI to Linux / stay Windows / hybrid dual-boot | **Card E:** decision (no auto-migrate) |

## Success criteria
- Phase 3 table filled for Win vs Linux on the same job (10Eros H3 I2V + Strata Forge; numbers + error log paths).
- Windows still boots unchanged; no Windows AI data deleted.
- Derrick decision recorded on the Linear parent.

## Risks
- **agy/Gemini on Linux:** supported per Google docs; headless/SSH may need keyring/D-Bus — smoke in phase 2 before relying on agents.
- **Grok Bot / local-exec on Linux side:** Windows Grok Bot connection does not automatically cover a Linux boot; plan assumes Max guides via chat + Derrick at keyboard until Linux-side agent path is proven.
- **Windows paths in scripts:** `C:\…` / `D:\…` Switchyard/Forge scripts will not run as-is on Linux; A/B uses stock community installs, not a full path port.
- **Alienware/NVIDIA:** Secure Boot blocks unsigned nvidia modules until MOK enroll or Secure Boot off (common Alienware dual-boot reports). Exact chassis SKU unconfirmed; Optimus less likely on desktop but still verify `nvidia-smi` before A/B. Some Alienware Aurora *laptops* are Ubuntu-certified; treat desktop as uncertified until proven.
- **VRAM/WSL:** do not use WSL2 for this A/B (research: extra VRAM + `/mnt` I/O pain).

## Approval cards (must ask Derrick — one at a time)
1. **A — Phase 0:** buy/choose second SSD + approve this plan (money).
2. **B — Phase 1:** BIOS/boot order / Secure Boot / MOK.
3. **C — Phase 1:** download Ubuntu ISO + install onto second SSD only.
4. **D — Phase 2:** Comfy/llama/`agy` downloads and installs on Linux.
5. **E — Phase 4:** migrate / stay / hybrid (no silent cutover).

## Budget
- This planning turn: ~2% expected quota (research already done; Linear + plan only).
- Live phases 1–3 (Max guiding): estimate **8–15%** of weekly quota if guidance is chat-heavy; log actual % on the Linear issue per rule 8.
- Phase 0 SSD cost: Derrick only (outside AI quota).

## Out of scope
- Repartitioning or shrinking Windows.
- WSL2 as the test host.
- Migrating Switchyard/Forge production paths before phase 4 decision.
- Touching AlienPc before Card A.

## Handoff (10 lines)
1. Plan file: this path.
2. Research: `/workspace/cos/audits/2026-10-19-linux-vs-windows-alienpc.md`.
3. Linear parent: Linux dual-boot A/B (awaiting Derrick); sub-issues = phases 0–4.
4. Owner: Max Architect; status Backlog/Todo until Card A.
5. Community: second SSD + Ubuntu 24.04 + proprietary NVIDIA + models on Linux FS.
6. A/B: one 10Eros H3 I2V clip (no gen RIFE; FastH3 Omni if landed) + one llama-swap/Strata Forge prompt; metrics s/step, wall, peak VRAM, tok/s, errors.
7. Agents: agy + Gemini CLI Linux-supported (verify smoke phase 2).
8. Rollback: boot Windows.
9. No AlienPc changes this turn.
10. Safe to start a fresh chat after Derrick answers Card A.
