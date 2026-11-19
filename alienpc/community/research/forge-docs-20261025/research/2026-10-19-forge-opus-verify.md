# Forge / Strata Opus claim verify (2026-10-19)

Research + compare only. No installs, downloads, or config changes.
AlienPc offline; "our setting" = box copies / prior read-only audits only.

**Primary sources fetched this pass:**
- https://raw.githubusercontent.com/Niko1221/Strata/main/docs/DETAILS.md
- https://raw.githubusercontent.com/Niko1221/Strata/main/docs/MODELS.md
- https://raw.githubusercontent.com/Niko1221/Strata/main/docs/LLAMA_SWAP.md
- https://raw.githubusercontent.com/Niko1221/Strata/main/docs/AI_SETUP.md
- https://github.com/Niko1221/Strata/releases (v0.1.45 2026-10-17; v0.2.0-beta 2026-10-19)
- https://github.com/Niko1221/Strata/issues/3110 (vhotseat; VRAM/RAM figures)
- https://huggingface.co/Qwen/Qwen3.8-Flash-Next (and 27B card) language table
- https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/settings.md
- https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/models.md (+ models.md search snippet for `compat.thinkingFormat`)
- https://github.com/earendil-works/pi/issues/10540 , #10024
- Pi bash truncate: DEFAULT_MAX_BYTES = 50KB (badlogic/pi-mono truncate.ts / earendil docs)
- Community: r/LocalLLaMA threads on 27B+Pi (agent use mixed)

**Box evidence for "our setting":**
- `/workspace/sh/cfg.yaml` (`coding_sc117_strata`, 27B profiles)
- `/workspace/research/flash-next-strata-claims-2026-10-16.md` (live Strata JSON summary)
- `/workspace/cos/plans/2026-10-17-forge-max-pipeline.md`, `2026-10-17-pipeline-py-spec.md` (llama-swap exclusive group)
- `/workspace/cos/audits/2026-10-17-consistency-check.md` (64K vs 96K; Switchyard vs llama-swap)
- `/workspace/cos/audits/2026-10-17-forge-config-audit-files/agy_1017/preflight_check.py` (Pi `models.json=92160`)
- `/workspace/forge-bench/HERETIC_VS_HUIHUI.md`, `/workspace/forge-bench/HARNESS.md` (27B tool smoke)
- Finance: `/workspace/cos/plans/2026-10-18-ce-plan-finance-app-rebuild-forge.md` (64K Forge)

---

## Claim table

| # | Opus claim | Verdict (source) | Our current setting (box) | Change needed? |
|---|---|---|---|---|
| 1 | Strata #3110: 5070 Ti 16GB + 64GB, Flash-Next IQ3_XXS @128K via Strata+Pi ≈ **14.7 GB VRAM / ~44 GB RAM** | **Verified** as the measurement quoted in https://github.com/Niko1221/Strata/issues/3110 (vhotseat demo, **Linux**, MiniMax H3). Not an official Strata DETAILS row; same ballpark as MODELS IQ3_XXS **47.0 GB RAM+VRAM** / DETAILS ~43 GB experts + ~6 GB. | Live Forge model is IQ3_XXS Strata (`coding_sc117_strata` → `C:\AI\strata\strata-iq3_xxs-switchyard.json`). Prior box note: peak **15540 MiB** (IQ2_XS SC117 smoke), not a fresh 128K IQ3_XXS VRAM/RAM capture on AlienPc. | none (info only). Confirm numbers on AlienPc when online. |
| 2 | Installer preselects **IQ3_S** for 64 GB; keep **IQ3_XXS** when sharing with ComfyUI | **Partly outdated / conflicting.** New MODELS "Pick by memory" (RAM+VRAM): **64 GB → IQ3_S**. AI_SETUP.md still: **64 GB → iq2_xs (recommended)**. README table also still iq2_xs-leaning. "Keep XXS with Comfy" is reasonable ops advice, **not** a documented installer rule. | We already run **IQ3_XXS** (good for sharing headroom). AlienPc 64+16 = **80 GB RAM+VRAM** → new table would preselect IQ3_S. | **setting only** if someone runs setup again: pin `--model IQ3_XXS` so setup does not "upgrade" to IQ3_S (0.1.44.1 notes setup once switched users to IQ3_S). No download unless switching size. |
| 3 | Run `START-HERE.bat --calibrate` once, then `BENCH.bat` | **Partly verified / partly wrong.** `--calibrate` is real (DETAILS / AI_SETUP; ~15–30 min). **BENCH.bat** exists but 0.2.0-beta release notes: *"`strata bench run` and `BENCH.bat` do not implement"* the draft benchmark protocol — do not treat as a polished gate. | No box proof calibrate was run on AlienPc. | **needs approval** to run calibrate (CPU-busy, reloads model). BENCH optional / weak until protocol lands. |
| 4 | Strata keys outside `args`: `tool_call_recovery:true`, `reasoning_close_retry:true`, `reasoning_loop_recovery:"recover"`, `expert_profile_save:"expert-profile-learned.bin"`, `prevent_sleep:true`, sampling `{1.0, 0.95, 20}`; TCR 98.3% vs 92.9%; expert profile +13–19% decode | **Verified** as documented opt-ins in DETAILS.md (tool_call_recovery corpus numbers; expert_profile_save +13–19% on **Arc Pro B70**, kind-of-work specific; prevent_sleep Windows-only; sampling matches Qwen thinking defaults). | Oct 16 read of live JSON: sampling **`temperature 0.6` only** (not 1.0/0.95/20); **no** evidence on box of tool_call_recovery / reasoning_* / expert_profile_save / prevent_sleep being set. Refusal **cvec project L1–47 ON**. | **setting only** (edit `strata-iq3_xxs-*.json`): add recovery keys + Qwen sampling; add expert_profile_save path. Ranked high. |
| 5 | Vision off / CPU for Forge (GPU vision reserves **~1.4 GB**) | **Verified** (DETAILS/MODELS: GPU vision keeps ~1.4 GB; &lt;24 GB cards default **CPU** reader in recent setup; `--vision off\|cpu\|gpu`). | **`vision: true`** on `coding_sc117_strata` (cfg.yaml); Oct 16 note: `vision.gpu: true`, BF16 mmproj. | **setting only**: set vision **off** or **cpu** for Forge coding (frees ~1.4 GB expert slots). Aligns with our own Oct 16 recommendation. |
| 6 | `strata connect pi --write` / `--check` | **Verified** (AI_SETUP.md §8; 0.2.0-beta Terminal). Older source trees used START-HERE/setup without `strata connect`. | not found on box whether `strata connect` was ever run; Pi wired manually historically. | **setting only** / optional: `--check` when online; `--write` only with Derrick OK (overwrites Pi config after backup). |
| 7 | Windows: Task Scheduler **Normal** + **highest privileges** (else ~24× slower load); Lock pages in memory; NVIDIA **Prefer No Sysmem Fallback** (102 → 13.7 tok/s); watch "MiB of VRAM free…", raise `--vram-reserve-mib` if &lt;1 GiB | **Verified** (DETAILS Windows Task Scheduler table; large pages; #781 Prefer No Sysmem / free-VRAM line; LOW warning). | Oct 16: scheduled task "Switchyard llama-swap" **priority 4 (Normal)** already. Lock pages / Prefer No Sysmem / live free-MiB: **not found on box**. `vram-reserve` was **1200** MiB in Oct 16 note. | **setting / OS policy** (needs admin for Lock pages + NVIDIA Control Panel). Verify free MiB after load when online. |
| 8 | Pi `models.json` compat `{thinkingFormat:"openai", supportsReasoningEffort:true}`; contextWindow **98304**, maxTokens **32768**; settings compaction reserve **16384** / keepRecent **20000**; retry.provider.maxRetries **0**; httpIdleTimeoutMs **600000** (default 300000); defaultThinkingLevel **high** | **Partly wrong / partly verified.** Compaction defaults **16384/20000** verified (settings.md). `retry.provider.maxRetries` default **0** verified. `httpIdleTimeoutMs` default **300000** verified; **600000** is a raise, not the default. `defaultThinkingLevel` **built-in default is `medium`**, not high — setting high is a choice. **`thinkingFormat:"openai"` not in published enum** (docs list `reasoning_effort`, `openrouter`, `deepseek`, `qwen`, `chat-template`, …). `supportsReasoningEffort:true` is a real compat field. | Preflight comment: Pi **contextWindow=92160** (not 98304). Strata `--max-context 98304` (Oct 16). Full `models.json` / `settings.json` copies: **not found on box** (only `forge-bench/config/pi-permissions.bench.jsonc`). Finance plan still says **64K** Forge. Consistency audit: 64K vs **96K** drift. | **setting only** when online: align Pi contextWindow with Strata max-context; set `thinkingFormat` to a **documented** value (`reasoning_effort` if using OpenAI-style effort); consider defaultThinkingLevel high; optionally raise idle timeout. |
| 9 | Pi bash keeps last **50 KB**, no setting; APPEND_SYSTEM note re pasting files (pi#10540); extensions changing tools mid-run break prompt cache (pi#10024); **badlogic/pi-skills** official; skills in `~/.agents/skills/` | **Mostly verified.** 50 KB default truncate verified (truncate.ts). #10540 / #10024 exist and match Opus topics. Skills dirs `~/.agents/skills/` verified (pi.dev / skills.md). **badlogic/pi-skills** repo exists (HTTP 200); Pi also documents Agent Skills locations. | 32 KB tool-output concern in forge-preflight audits is about **Tee-Object dumping preflight into context**, not Pi's bash cap. APPEND_SYSTEM / pi-skills install on AlienPc: **not found on box**. | **setting only**: add APPEND_SYSTEM line for #10540 if missing; avoid mid-run tool toggles (#10024). Cloning pi-skills = **needs approval** (git clone). |
| 10 | llama-swap: call `server.py` with `--port ${PORT}` (not run-*.bat); checkEndpoint `/health`; healthCheckTimeout **300**; STRATA_ALLOWED_HOSTS hostnames only; **vhotseat Linux-only** | **Verified** (LLAMA_SWAP.md; #3110 "Not tested: Windows"). | Live: llama-swap on **:8080**, exclusive group `main` with `comfyui_auto` + `coding_sc117_strata` + judges (`forge-max-pipeline` / pipeline-py-spec, Oct 17 read). Exact cmd/checkEndpoint/timeout on box: **partial** (yaml not copied to box). vhotseat N/A on Windows. | Confirm yaml when online. **Do not** expect vhotseat on AlienPc Windows. |
| 11 | Strata **v0.1.45** (Oct 17) byte-identical for Flash-Next, adds Qwen3.6-35B-A3B; update with UPDATE.bat | **Verified but outdated.** v0.1.45 published 2026-10-17 (Flash-Next answers byte-identical to 0.1.44.1; adds Qwen3.6). **Latest as of this research: v0.2.0-beta (2026-10-19)** — app/Terminal/engine package **0.1.45.3**; update via `UPDATE.bat` / `strata update` / Settings. | Oct 16 AlienPc note: Strata **v0.1.42**. | **needs approval** to update (install/engine replace). Not required for claim accuracy. |
| 12 | Benchmarks: Flash-Next IQ3_XXS SWE-Pro **62.5** vs 27B **61.7**; DeepSWE **58.7** vs **42.2**; Flash-Next reload ~**47 GB**; 27B fits GPU, swaps in seconds | **Verified** (HF Qwen3.8-Flash-Next / 27B language tables — scores are **full models**, not IQ3_XXS specifically). MODELS IQ3_XXS **47.0 GB** RAM+VRAM matches "moves ~47 GB". 27B dense on 16 GB with useful context is community + our smoke (peak ~**14874 MiB** IQ3_XXS-mtp 64K). | 27B profiles **already on disk** in cfg.yaml (`coding_huihui27b`, `coding_heretic27b`, …): 64K, tools_allowed, smoke **Forge 5/5 tool turns**. Rollback path documents Heretic. | **test** (setting/profile swap via llama-swap) — see §27B recommendation. No new download if using existing IQ3_XXS-mtp files. |

### Extra: vector-off / expert-skip A/B
Opus did not number this; task asked for our results. **Not found on box** as a completed A/B with numbers. Oct 12 research planned alesha vector on/off; Oct 16 note says vector **already ON**, no vector-off baseline recorded for IQ3_XXS agent quality.

### Extra: 32 KB tool-output cap extension
**not found** as a Pi extension on box. Audits refer to preflight Tee-Object ~32 KB into Forge context (`2026-10-17-forge-config-verify.md` F16).

---

## (a) Wrong or outdated Opus claims

1. **`thinkingFormat:"openai"`** — not in current Pi `compat.thinkingFormat` enum; use a documented value (likely `reasoning_effort` with `supportsReasoningEffort`).
2. **`defaultThinkingLevel high` as if default** — Pi default is **`medium`**; high is an explicit setting.
3. **`httpIdleTimeoutMs 600000 (default 300000)`** wording mixes recommendation with default — default is 300000; 600000 is optional raise.
4. **Installer "64 GB → IQ3_S" as sole truth** — conflicts with AI_SETUP still recommending **iq2_xs**; new RAM+VRAM table does say IQ3_S at 64 GB tier.
5. **Strata v0.1.45 as current tip** — superseded same week by **0.2.0-beta** / engine **0.1.45.3**.
6. **#3110 as a Strata hardware cert** — it is a **vhotseat feature issue**; figures are a Linux demo quote (still useful).
7. **BENCH.bat as a solid post-calibrate gate** — release notes say protocol not implemented yet.
8. **Pi contextWindow 98304 as our setting** — box preflight recorded **92160**; Strata max-context was 98304.
9. **Implied "27B and Flash-Next can share GPU with render"** thread — Opus correctly notes neither can; our llama-swap **exclusive** group already forces unload. Swap time still matters **between** renders, not during.

---

## (b) Top missing settings (ranked)

1. **Qwen thinking sampling + tool/reasoning recovery keys on Strata JSON** — T1.0 / top_p 0.95 / top_k 20; `tool_call_recovery`, `reasoning_close_retry`, `reasoning_loop_recovery` — **setting only**. Highest impact for agent reliability per DETAILS.
2. **Forge vision off or CPU** — reclaim ~1.4 GB VRAM for experts — **setting only**.
3. **`expert_profile_save`** learned profile — **setting only** (file write on clean exit); expect decode gain only after learning on our workload.
4. **Align Pi `models.json` contextWindow / maxTokens with live Strata `--max-context`** and fix `thinkingFormat` to a documented value — **setting only**; confirm 64K vs 96K with Derrick (finance plan still 64K).
5. **`prevent_sleep: true`** on Windows Strata config — **setting only**.
6. **OS: Prefer No Sysmem Fallback + Lock pages in memory** — **needs admin / approval**; large speed/stability win if free-VRAM is near 0.
7. **Confirm Task Scheduler Normal + highest privileges** on whatever starts llama-swap/Strata today — **setting only** (task props); priority 4 already noted for old Switchyard task.
8. **`--calibrate` once** after config stable — **needs approval** (15–30 min, heavy).
9. **Strata update 0.1.42 → 0.1.45.x / 0.2.0-beta** — **needs approval** (install).
10. **APPEND_SYSTEM.md file-delivery line (#10540)** — **setting only**.

---

## (c) 27B for ComfyUI control — recommendation: **TEST (lean yes for Comfy driver; keep Flash-Next for hard coding)**

**Reasons (ours + sources):**

1. **Neither model shares the GPU with a render.** Our llama-swap `main` group is `swap: true, exclusive: true` with `comfyui_auto` + `coding_sc117_strata` ([forge-max-pipeline.md](file:///workspace/cos/plans/2026-10-17-forge-max-pipeline.md)). Forge must stay quiet while Comfy holds the card — same rule for 27B.
2. **Swap time does matter between phases**, not during renders. Flash-Next IQ3_XXS residency is ~**47 GB** RAM+VRAM (MODELS) / ~44 GB RAM + ~14.7 GB VRAM (#3110). Reloading that after every Comfy batch is slow. Dense **Qwen3.8-27B IQ3_XXS-mtp** already in cfg.yaml peaks ~**14.9 GB**, fully GPU-resident, reload measured in our stack as normal llama-server bring-up (seconds–low minutes), not tens of GB of expert arena.
3. **Tool calling for our Forge smoke:** Huihui/Heretic 27B IQ3_XXS-mtp **5/5 tool turns**, needle 2/2 (`cfg.yaml` tools_clearance; forge-bench). Good enough for short Ralph tasks: edit workflow JSON, POST `/prompt`, poll `/history`, rename/stitch.
4. **Quality gap is task-dependent.** HF: SWE-bench Pro **62.5 vs 61.7** (near tie); DeepSWE **58.7 vs 42.2** (large). Comfy orchestration is short-horizon tool use → 27B plausible. **Finance-app rebuild** (multi-file, 64K units) leans Flash-Next / keep MoE for hard coding.
5. **Community:** r/LocalLLaMA has both "27B good enough I stopped using API" and "useless for agentic coding" threads — config-sensitive; our own 5/5 smoke beats generic Reddit for the Comfy-control question.
6. **Which quant on 16 GB:** stick to **existing IQ3_XXS-mtp** profiles (`coding_heretic27b` / `coding_huihui27b`, `-c 65536`, q8 KV) — already cleared for tools. IQ3_S (~12+ GB weights) is tighter with useful context; not required for a Comfy-driver test. Vision off for the driver profile.

**Practical test plan (when AlienPc online, Derrick OK):** llama-swap profile swap only — point Pi/Forge at `coding_heretic27b` (or huihui) for one Max loop of Comfy control tasks; keep `coding_sc117_strata` for finance units; measure unload→Comfy ready and Comfy→LLM ready wall times + tool success rate. No new download if weights present.

---

## (d) Must check on AlienPc when online

1. Live files: `C:\AI\strata\strata-iq3_xxs-switchyard.json` (or current), `D:\AI\director\config\llama-swap.yaml`, `C:\Users\derek\.pi\agent\models.json`, `settings.json`, `pi-permissions.jsonc`, any `APPEND_SYSTEM.md`.
2. Strata version (`strata --version` / git describe / About tab) vs 0.1.45 / 0.2.0-beta.
3. After model load: log line **"MiB of VRAM free with everything loaded"**; nvidia-smi used MiB; confirm `--vram-reserve-mib`.
4. Presence of opt-in keys (claim 4) and actual sampling block; vision gpu/cpu/off.
5. Pi contextWindow vs Strata `--max-context` (92160 vs 98304 vs finance 64K).
6. llama-swap model `cmd` uses `server.py --port ${PORT}` + `/health` + timeout 300.
7. Task Scheduler: Normal + highest privileges; Lock pages; Prefer No Sysmem Fallback.
8. Confirm 27B GGUF paths still on disk; one timed swap Comfy↔27B vs Comfy↔Flash-Next.
9. Whether calibrate / expert-profile-learned.bin already exist.
10. Vector-off A/B still undone if uncensor quality is in scope.

---

*Generated 2026-10-19 America/Chicago. No configs modified.*
