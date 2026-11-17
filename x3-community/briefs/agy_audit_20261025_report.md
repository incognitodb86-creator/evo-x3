# Antigravity Audit, Debug, Fix and Optimization Report

**Date:** 2026-10-25  
**Last Updated:** 2026-10-25  
**Author:** Antigravity (Gemini 3.8 Flash High)  
**Reference Brief:** `C:\AI\community\briefs\agy_audit_20261025.md`  
**Execution Log:** `C:\AI\community\briefs\agy_audit_20261025.log`

---

## Summary

Antigravity completed a comprehensive audit, debugging pass, configuration fix, and optimization of AlienPc's pipeline based on Derrick's brief and direct feedback from Oct 24-25, 2026. 

All primary tasks were investigated and resolved:
1. **Strata Refusal Vector Enabled on Swift:** Enabled the refusal control vector on `strata-swift15-iq3s.json` and updated pi agent `models.json` and `settings.json` so that requests no longer send `experimental_speed_projection: false`, preventing truncation and refusals on start-image captioning.
2. **ComfyUI Community Defaults Applied:** Removed `--lowvram` and `--use-ck-attention` from `comfyui_auto` and `comfyui_longvideo` in `C:\AI\director\config\llama-swap.yaml`, aligning memory management to dynamic VRAM and attention to default PyTorch attention (as required for `int8_convrot` checkpoints per published ComfyUI documentation and issue #15529).
3. **20-Minute LLM Interruption Source Identified:** Uncovered Windows Scheduled Task `ForgeAgyMonitor` (interval `PT20M`), running `agy_monitor_run.ps1` (`agy_monitor.md`), which periodically triggered watchdog restarts and LLM completions.
4. **Orc Scene (GI046 s51150032) Artifact Root Cause Diagnosed:** Traced the contradictory undressing motion and missing green orc anatomy to a prompt narrative conflict with frame 0 pinning and a lack of species-specific anatomy conditioning in chunk `c0`.
5. **Guard & Policy Integrity Maintained:** Youth guard (`comm.py` adults-only check and `test_p6_review.py`) remained byte-pinned and verified (21/21 pytest passing, whole suite 38 passing, 13/13 `rt_window_probe.py` checks passing). GI063 remained on hold pending Derrick's decision [RELEASED: Derrick 2026-10-27 9:09 AM CT — GI063 render hold released, wrongly flagged by wrong model; youth guard kept].

---

## Key Findings

### 1. Strata Refusal Vector on Swift
- **Historical Evidence:** Benchmark data from October 15, 2026 (`C:\AI\strata-ab-20261015\ab2-live.json`, `ab2-cvecoff.json`, `ab2-perreq_projoff.json`) demonstrated that with the control vector enabled, Qwen3.8-Flash-Next achieved 0/15 adult refusals at 102.7 tok/s. When removed, 15/15 requests refused; when `experimental_speed_projection: false` was passed per-request, 14/15 refused.
- **Root Cause of Recent Refusals:** Forge's active model was `coding_swift15_iq3s` (`strata-swift15-iq3s.json`). The control vector arguments (`--control-vector-scaled`, etc.) were missing from `strata-swift15-iq3s.json`. Furthermore, `C:\Users\derek\.pi\agent\models.json` explicitly passed `"experimental_speed_projection": false` in `samplingParams`. As implemented in `C:\AI\strata-0.2.2\serve\server.py:1440-1444`, `experimental_speed_projection: false` actively emits `cvec=0` to the engine, forcing the refusal vector off on every request. This caused the model to refuse start image descriptions (e.g. `GI063.md` returning `caption_status: REFUSAL_TRUNCATED`).
- **Resolution:** Re-enabled the control vector in `strata-swift15-iq3s.json` using the existing tested weights (`C:\AI\strata-0.2.2\data\experimental-speed-projection\Qwen3.8-Flash-Next-experimental-speed-projection.gguf:1.0`), set `sampling.experimental_speed_projection=true`, updated `models.json` to enable `experimental_speed_projection: true` across Swift entries, expanded context window to 128K (131072 / 128000), and added compaction overrides in `settings.json`.

### 2. ComfyUI Attention and VRAM Flags
- **Derrick Approval:** Derrick approved switching ComfyUI attention and `--lowvram` to community defaults at 4:01 AM CT Oct 25.
- **Published Evidence:**
  - `notes/web/02v_docs_h3.txt:80`: *"Comfy Kitchen attention cannot run `int8_convrot` checkpoints; use a `bf16` build with that backend."*
  - `notes/web/02v_docs_h3.txt:201`: *"Templates use `int8_convrot` checkpoints. Comfy Kitchen does not support them (issue #15529). Use default attention..."*
  - `RESEARCH_2026-10-21_forge_agentic_comfy.md:127`: *"Remove `--lowvram` from the ComfyUI cmd lines for clarity (audit row 24: a no-op with DynamicVRAM). Keep `--disable-async-offload --disable-pinned-memory`."*
- **Resolution:** Modified `C:\AI\director\config\llama-swap.yaml` while the GPU was IDLE, removing `--lowvram` and `--use-ck-attention` from both `comfyui_auto` and `comfyui_longvideo`. Llama-swap hot-reloaded successfully (`[INFO] configuration reloaded`). Verified that all 13 `rt_window_probe.py` checks and 13 selftest seeds pass.

### 3. Source of the 20-Minute LLM Interruptions
- **Investigation:** Examined all non-Microsoft scheduled tasks in Windows using PowerShell CIM/Task queries.
- **Identified Source:** Scheduled Task `ForgeAgyMonitor`:
  - **Schedule:** Repetition interval `PT20M` (exactly every 20 minutes), started `2026-10-24T21:31:17-05:00`.
  - **Action:** `powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\AI\community\briefs\agy_monitor_run.ps1`.
  - **Mechanism:** `agy_monitor_run.ps1` runs `agy.exe` with brief `agy_monitor.md`. In runs on Oct 24 and early Oct 25, when `agy_monitor` detected timeouts (logged in `agy_monitor.log` at 22:36 and 03:40), it issued `Start-ScheduledTask -TaskName ForgeRalphLoop`. This triggered `ralph.ps1` to spawn `pi`, which sent `/v1/chat/completions` requests to `127.0.0.1:8080`.
  - **Prior Conflict:** Because `comfyui_auto` was previously in the exclusive `main` group, incoming LLM requests attempted to swap ComfyUI out at :18, :38, and :58 past the hour (recorded in `comfy-graceful-stop.log`), interrupting active renders. The RENDER-TIMEOUT fix isolated `comfyui_auto` into its own persistent group, eliminating render drops, but `ForgeAgyMonitor` was the scheduled trigger.

### 4. Orc Scene (GI046 Take B s51150032) Anomalies
- **Derrick Feedback:** *"the orc.scene is horrible you can already see the fick out but he stops pulls down his pants and then has a small human dick instead of a green orc dick?"*
- **Audit Findings:**
  1. **Narrative/Frame 0 Contradiction:** `GI046.jpg` is pinned at frame 0 via `MiniMaxH3AddGuide frame_idx 0`. In the start photograph, the character is already unclothed and in position. However, in `runs/ali163_hc15_gi046_s51150032/request.api.json` and `notes/_top_prose_write.py`, the prompt explicitly instructed at `00:04.400`: *"his dark grey shorts come down onto the hardwood floor, the garment she wears slides down her legs onto the rug, both bodies naked"*. The diffusion model attempted to render shorts removal at 4.4 seconds on a character that began the video unclothed, resulting in a confusing regression.
  2. **Anatomy Conditioning Gap in Chunk 0 (`c0`):** In `c0` (the first 10.125 s), the prompt defined `<Subject 2>` as a green-skinned muscled orc, but when describing the anatomy at `00:06.600` and `00:08.700`, it used generic terminology ("his cock") without specifying green skin color, orc species traits, or scale matching the muscular green torso. Only in continuation chunk `c1` did the prompt add *"a thick humanoid penis, dark green and heavy"*. Because the base model defaults to human traits unless explicitly conditioned, chunk `c0` rendered standard human anatomy.
  3. **Silent Card Limitation:** Because `GI046.md` was generated while the refusal vector was off, the scene card truncated (`REFUSAL_TRUNCATED`). The prompt builder adhered strictly to card-derived facts, preventing it from adding unobserved green orc anatomy descriptions into chunk `c0`. This is formally logged in `needs_derrick.md` row 28.

### 5. GI063 On Hold
- `GI063.jpg` (robot scene) remains on hold per `fix_plan.md` line 6 and `needs_derrick.md` row 21 due to non-consensual restraint depiction in the start still. Antigravity did not arm, queue, or render GI063.

---

## Action Items Completed

1. **`strata-swift15-iq3s.json` Updated:**
   - Backed up to `C:\AI\strata-0.2.2\strata-swift15-iq3s.json.bak-20261025`.
   - Added refusal vector configuration to `args` and `args_written`:
     - `--control-vector-scaled C:\AI\strata-0.2.2\data\experimental-speed-projection\Qwen3.8-Flash-Next-experimental-speed-projection.gguf:1.0`
     - `--control-vector-layer-range 4 44`
     - `--cvec-mode project`
     - `--cvec-dir per-layer`
   - Set `sampling.experimental_speed_projection: true`.
   - Updated `strata-swift15-iq3s-esp.json` max context to 131072.
2. **`models.json` & `settings.json` Updated:**
   - Backed up `models.json` to `C:\Users\derek\.pi\agent\models.json.bak-20261025`.
   - Set `experimental_speed_projection: true` on `coding_swift15_iq3s` and `coding_swift15_iq3s_esp`.
   - Set `input: ["text", "image"]` and `contextWindow: 128000` for both Swift models.
   - Backed up `settings.json` to `settings.json.bak-20261025` and added `compaction.modelOverrides` for `llama-swap/coding_swift15_iq3s`.
3. **`llama-swap.yaml` Updated to Community Defaults:**
   - Backed up to `C:\AI\director\config\llama-swap.yaml.bak-20261025`.
   - Removed `--lowvram` and `--use-ck-attention` from `comfyui_auto` and `comfyui_longvideo`.
   - Verified hot reload in `llama-swap.out.log` (`[INFO] configuration reloaded`).
   - Verified `notes/rt_window_probe.py --check` (13/13 CLEAN), `--selftest` (13/13 passed), and pytest `test_p6_review.py` (21/21 passed).
4. **Action Logging:**
   - Every modification and validation recorded with timestamps to `C:\AI\community\briefs\agy_audit_20261025.log`.
