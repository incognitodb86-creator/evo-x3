# AlienPc local-exec lease (LOCKED 2026-10-02 · Dial-only + Modern Standby 2026-10-05)

Evidence: Dial+CoS dual Shell ~11:28–11:50 CT · ListMachines `connected:true` while Shell empty-stdout forever · forum leftover-daemon / connected-but-dead local computer.
**2026-10-05 evening:** Dial-only flaps · `childDeaths.node` rising · **Modern Standby (S0) Kernel-Power 506 Idle Timeout** via display-off AC ~60s (classic Sleep=Never still S0) · unlock/login restores NodeService · Comfy kept ST8 6/6 — Shell ≠ Comfy ≠ chat 3-msg cap.

1. **One Shell owner:** the holder in the latest `30_handoff/status/*lease*` file only (was Dial). Others never run Shell on AlienPc; ask that holder. Never parallel Shell. **Single-owner ≠ immune.**
2. **Hang = stop:** empty Shell >~15–30s → **≤1 retry then HOLD**.
3. **Recover:** unlock/login wake first (wait 30–60s + one smoke) if that matches Derrick’s action; else Quit Grok + kill `local-exec-daemon` → relaunch → ~1 min → one probe.
4. **Prevent (Derrick, during Max queues):** display-off AC **Never** (`powercfg /change monitor-timeout-ac 0`) — Sleep after=Never alone does **not** stop S0.
5. **Detect:** ListMachines connected/false · `childDeaths.node` · Kernel-Power **506/507**.
6. **Comfy-authoritative matrices:** write `prompt_id` early; no re-queue; harvest history; skip ok metas.
7. **Chat cap ≠ render loss:** Desktop pack = SoT.
8. PowerShell-native; remote GUI before travel.
9. Stamps: Oct 2 dual-Shell · `/workspace/cos/audits/2026-10-05-alienpc-shell-flap-rca.md` · `…-capa.md` · `…-repeat-rca.md` · Auditor `…-capa-auditor.md` · `…-modern-standby-auditor.md`

Also see dedicated skill: [AlienPc local-exec lease](sand-workflow:alienpc-local-exec-lease).
