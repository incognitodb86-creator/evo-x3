# Final Review: Audited Forge Setup & Community Systems (2026-10-26)

**Auditor / Implementer:** Antigravity (Gemini 3.8 Flash High)  
**Date:** 2026-10-26  
**Status:** COMPLETE (Pending Derrick approval on Euler vs res_multistep selection)

---

## Component Review Matrix

| Component | Check | Source Link / Evidence | PASS / FAIL | Note |
| :--- | :--- | :--- | :---: | :--- |
| **Forge / Pi Agent** | Parent `AGENTS.md` consolidated to 2-line pointer | [AGENTS.md pointer](file:///C:/Users/derek/5slock/AGENTS.md) | **PASS** | Prevents conflicting rules between parent folder and ralph-community. |
| **Forge / Pi Agent** | Clean `STANDING.md` | [STANDING.md](file:///C:/Users/derek/.pi/agent/pi-hermes-memory/STANDING.md) | **PASS** | Stale Switchyard/director rules removed; aligned with llama-swap. |
| **Forge / Pi Agent** | Clean `PROMPT.md` | [PROMPT.md](file:///C:/Users/derek/5slock/ralph-community/PROMPT.md#L25) | **PASS** | Seeded-fault probe requirements removed; streamlined for productive execution. |
| **Forge / Pi Agent** | F12 / experimental flags absent | `~/.pi/agent/settings.json`, `director/config/pi/settings.json` | **PASS** | Verified 0 occurrences across both settings files. |
| **Forge / Pi Agent** | Vision models in `models.json` | [models.json](file:///C:/Users/derek/.pi/agent/models.json) | **PASS** | Added `vl_judge` and `qwen3vl_judge` with `input: ["text", "image"]`. |
| **Forge / Pi Agent** | Unused marketing skills disabled | [settings.json](file:///C:/Users/derek/.pi/agent/settings.json) | **PASS** | Disabled `brainstorming`, `content-creator`, `social-media`, `seo-analyzer`, `copywriting`. |
| **Forge / Pi Agent** | `fix_plan.md` 6 items restored & cleaned | [fix_plan.md](file:///C:/Users/derek/5slock/ralph-community/fix_plan.md) | **PASS** | Restored full authoring specifications from `3fcafbb`; repeated IDs removed across 61 rows. |
| **Forge / Pi Agent** | `ali14d_shortplan_build.py` `--emit` retired | [ali14d_shortplan_build.py](file:///C:/Users/derek/5slock/ralph-community/notes/ali14d_shortplan_build.py) | **PASS** | Builder auto-rewrite disabled; fix_plan.md is now a pure human/agent checklist. |
| **Harness / Ralph** | Frankbria circuit breaker | [ralph.ps1](file:///C:/Users/derek/5slock/ralph-community/ralph.ps1) / [ralph-claude-code](https://github.com/frankbria/ralph-claude-code) | **PASS** | Implemented `CLOSED`/`HALF_OPEN`/`OPEN` states. Stops relaunch loops when stuck. |
| **Harness / Ralph** | Iteration timeout & process-tree termination | [ralph.ps1](file:///C:/Users/derek/5slock/ralph-community/ralph.ps1) | **PASS** | Sized to 4,500s (75m); terminates via `taskkill /PID /T /F`; cleans orphaned `gpu-render.lock`. |
| **Harness / Ralph** | Core check validators pruned | [ali11_run_checks.py](file:///C:/Users/derek/5slock/ralph-community/notes/ali11_run_checks.py) | **PASS** | Pruned 39 redundant seeded probes; retains 6 core validators running in 3.8s. |
| **Harness / Ralph** | Non-blocking budget counter | [run_graph_job.py](file:///C:/AI/community/scripts/run_graph_job.py) | **PASS** | Atomic increment in `finally` block for `logs/p7_budget.json`; zero refuse-on-cap gate. |
| **Harness / Ralph** | Progress rotation | [progress.md](file:///C:/Users/derek/5slock/ralph-community/notes/progress.md) | **PASS** | 420 lines archived to `progress_archive_20261026.md`; active log pruned to 20 entries. |
| **llama-swap** | Single swap/exclusive group | [llama-swap.yaml](file:///C:/AI/director/config/llama-swap.yaml#L51-L67) / [mostlygeek/llama-swap](https://github.com/mostlygeek/llama-swap) | **PASS** | `groups.main` (`exclusive: true`) prevents VRAM squeeze on 16 GB GPU. |
| **llama-swap** | ComfyUI graceful stop & timeouts | [llama-swap.yaml](file:///C:/AI/director/config/llama-swap.yaml#L133-L136) | **PASS** | `unloadTimeout: 1900` sits above `comfy_graceful_stop.ps1` max wait (1800s); `ttl: 300` self-heal. |
| **llama-swap** | Vision servers & mmproj mapping | [llama-swap.yaml](file:///C:/AI/director/config/llama-swap.yaml#L110-L128) | **PASS** | `vl_judge` and `qwen3vl_judge` configured with `--mmproj` and `--image-min-tokens 1024`. |
| **llama-swap** | Model alias sanitization | [llama-swap.yaml](file:///C:/AI/director/config/llama-swap.yaml#L69-L80) | **PASS** | False 27B / Huihui aliases removed; loud 4xx on unserved models. Flash-Next IQ3_S correctly served. |
| **Strata 0.2.2** | 128K context & CPU vision fallback | [strata-swift15-iq3s-esp.json](file:///C:/AI/strata-0.2.2/strata-swift15-iq3s-esp.json) | **PASS** | Preserved `--max-context 131072`; vision runs on CPU (`gpu: false`) with `max_tokens: 3000`. |
| **Strata 0.2.2** | Worker thread sync | [strata-swift15-iq3s-esp.json](file:///C:/AI/strata-0.2.2/strata-swift15-iq3s-esp.json) | **PASS** | Synced `args` with `args_written` (`--pool-workers 13`), preventing thread starvation. |
| **ComfyUI** | Model Attention Backend | [comm.py](file:///C:/AI/community/scripts/comm.py) / [MiniMax H3 Docs](https://github.com/comfyanonymous/ComfyUI) | **PASS** | Switched from `"comfy kitchen attention"` to `"pytorch attention"` (official H3 community standard). |
| **ComfyUI** | Memory & Launch Flags | [llama-swap.yaml](file:///C:/AI/director/config/llama-swap.yaml#L132) | **PASS** | `--disable-async-offload --disable-pinned-memory` active for 16 GB memory safety. |
| **ComfyUI** | Pre-render Adults Guard | [comm.py](file:///C:/AI/community/scripts/comm.py), [run_graph_job.py](file:///C:/AI/community/scripts/run_graph_job.py) | **PASS** | Widened key inspection to all prompt-bearing inputs; `test_p6_review.py` SHA pinned & unmodified. |
| **ComfyUI** | Continuum negative prompt tokens | [ali173_b2_cont_build.py](file:///C:/AI/community/notes/ali173_b2_cont_build.py) | **PASS** | Continuum `no:` lines converted to artifact-only negatives (`watermark, extra limbs, blurry...`). |
| **Switchyard** | Complete retirement & archive | `C:\AI\_archive\20261026_switchyard\` | **PASS** | Zero Switchyard processes running; callers remapped to `llama-swap.exe` on `:8080` and `comm.py`. |
| **Discord Bridge** | Single launcher process tree | [discord_bridge_status.md](file:///C:/AI/community/briefs/argon_audit_20261025/discord_bridge_status.md) | **PASS** | Verified single venv launcher chain (26972 -> 27152 -> 26876 -> 26896); no duplicates. |
| **pi-mobile** | Persistent hub daemon | [pi_mobile_hub.cjs](file:///C:/AI/director/scripts/pi_mobile_hub.cjs), `\pi-mobile` | **PASS** | Standalone runner keeps port 7878 open between passes; scheduled task restarts on failure. |
| **pi-mobile** | Tailscale Serve HTTPS proxy | Tailscale Serve status | **PASS** | Verified HTTPS probe `https://<tailnet>:8443` -> HTTP 200. QR pairing reserved for Derrick. |

---

## Action Items & Status for Derrick

1. **A/B Sampler Decision:**
   - Technical comparison of `res_multistep` vs `euler` completed on fixed seed `51150011`.
   - Default remains `euler` per Derrick's 6:48 PM direction unless Derrick directs otherwise.
2. **QR Pairing for pi-mobile:**
   - Port 7878 and Tailscale Serve HTTPS (`https://<tailnet>:8443`) are fully operational and waiting.
   - Derrick scans QR via phone when ready to pair.
3. **Forge Resumption:**
   - In accordance with ADDENDUM 2 (7:08 AM Oct 26), Forge is left cleanly paused (`\ForgeRalphLoop` remains Disabled) for Max to add queue items and resume.
