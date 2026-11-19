# SPIKE: Max :8189 text encoder (TE) on GPU, cached, or split (stop paying 6–7 min per new prompt paste)

**When_CT:** 2026-10-08 ~12:45 PM CT · **Owner:** Max Research executor (research only) · **AlienPc / Comfy :8189 not touched** (no Shell, no queue, no /free, no argv change) · no messages sent
**Locks:** KEEP = Derrick exact GO only · fiction adults 21+ · never invent metrics (NO_DATA = nobody measured it) · Shell = Dial XOR CoS XOR Derek twin
**Note on derived numbers:** every number below is either quoted from a source or labeled **derived** (arithmetic on sourced numbers). Derived numbers are not measurements.

## TLDR
1. **Root cause is the CPU placement, not the TE size.** On ComfyUI master (read today), with `--disable-dynamic-vram`, `--lowvram` does exactly one thing: it puts the TE on the CPU. UNET partial loading is identical with or without it. Our 32B nvfp4 TE therefore runs its forward pass on the CPU for every new paste.
2. **The best option is O1: drop `--lowvram` only (the parked W3).** The TE then streams through the GPU with Comfy's normal partial loading, and the UNET is evicted while the TE encodes. The closest analog is a 16 GB 4070 Ti S on Windows with NODDV: encode took **~5 s text-only and ~10 s with an image**, after a reserve fix (#15316). Without that fix the image case hung **1+ min**. AlienPc: **NO_DATA**.
3. **O1b adds `--reserve-vram 2.5`.** This is #15316's own workaround for the image-token activation spike. It is a separate one-axis arm.
4. **Caching does not help new pastes.** Comfy already skips the TE when the prompt, canvas, length and refs are unchanged. The built-in `Save Conditioning` **cannot** save REF2VA conditioning that has the VAE wired (it raises on `minimax_refs`).
5. **Smaller TEs are fallbacks only.** GGUF Q4_K_M (19.76 GB) is *larger* than our nvfp4 (15.69 GB). Q3 abliterated and ClipProj 4B add quality risk. MultiGPU was archived 2026-09-30.
6. Every argv arm needs **Derrick exact GO**. W3 was deferred by Derrick's 10-06 ~10:17 CT "defer ALL risky" call. No KEEP is claimed.

## Current state (local files)
| Fact | Value | Path |
|---|---|---|
| Production argv (KEEP 2026-10-02 Derrick GO) | `main.py --listen 127.0.0.1 --port 8189 --lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory --use-ck-attention` | `/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md` |
| TE file | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` · **15,687,142,551 B (14.61 GiB)** · nvfp4 AWQ · 2054 keys · first-64MB sha256 `6ea22c95…3420` · Comfy logged TE ~14,960 MB loaded | `/workspace/MAX_REF_ORC_BJ_S0_2026-10-02/meta/HOSTBUFFER_RT_2026-10-02.md` §1 · `…/CAPA_MAX_REF_S0_HOSTBUFFER_2026-10-02.md` |
| UNET | `10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors` · 13,997,668,774 B (13.04 GiB) · turbo baked in (no LoRA node in harness graph) | same · `/workspace/cos/tmp_opt_queue.py` L9, L48–70 |
| VAEs | video `minimax_h3_video_vae_int8_convrot` 2.81 GB · audio fp32 0.61 GB | HOSTBUFFER_RT §1 |
| Graph | `CLIPLoader(type=minimax, device=default)` → `MiniMaxH3ReferenceToVideo` (clip+vae+audio_vae+prompt+W/H/length+`ref_image_size=match`+ref_image_1) → BasicGuider → SamplerCustomAdvanced | `/workspace/cos/tmp_opt_queue.py` L48–70 |
| Speed SoT row | R0 ST8 768×1344×124 ≈ **139–142 s** (hot) | `/workspace/cos/gbrain/04_memory/max-studio-2026-10-08/2026-10-08_project_alienpc-max-local-llm-NEXT.md` |
| `--lowvram` meaning (ERRATA3) | under NODDV = **TE→CPU only**; UNET streaming happens in NORMAL_VRAM too | `/workspace/cos/research/2026-10-06-max-8189-keep-vs-official-community-optimize.md` ERRATA3 · `/workspace/cos/audits/2026-10-06-keep-vs-official-ERRATA3-fairness-auditor.md` |
| CPU-TE cost flagged before | "TE encode time on CPU … vs on GPU … isn't measured" | `/workspace/cos/research/2026-10-06-max-keep-vs-official-10eros-community.md` Unknowns |
| 6–7 min encode per new paste | **User-reported** (this brief). No logged per-node TE timing found in local files | (grep of research/status/audits/gbrain/MAX_* for TE encode timing: none) |
| W3 drop-lowvram | MUST_TEST "GO HIGH", 480×864 124f, OOM→restore | `/workspace/cos/research/2026-10-06-max-optimize-complete-candidate-matrix.md` row 16 |
| W3/W4/W7/R7/R9 deferred | Derrick exact GO ~10:17 CT 2026-10-06: R3 author first, "defer ALL risky incl. W3/W4" | `/workspace/cos/audits/2026-10-06-r3-hold-lift-and-tenstrip-upscale-fairness-auditor.md` · `…/2026-10-06-r3-before-w3-order-hold-fairness-auditor.md` |
| W4 DynVRAM | RISK_OK_ONE_SMOKE; HostBuffer 1450 history; upstream PR #15944 open (as of 10-06) | candidate-matrix row 18 · `2026-10-02-max-8189-setup-optimized.md` §6 |
| R9 `--fast fp16_accumulation` | SHOULD_TEST last, "may affect quality" | candidate-matrix row 24 |
| W5 pinned-only | ran 2026-10-06 @480×864×124 simple: sA 125.9 s / sB 44.1 s, TECH ok | `/workspace/cos/gbrain/05_projects/max-optimize-2026-10-06/2026-10-06_project_alienpc-max-optimize-matrix-NEXT.md` |
| W6 async | started then driver crash 10:17 CT; no result | same |
| Sysmem fallback lock | **NEVER** set "Prefer No Sysmem Fallback" for Comfy `python.exe` or Global (Derrick HARD lock 2026-10-08) → VRAM overrun on Comfy shows as a *silent slowdown*, not always an OOM | `/workspace/cos/gbrain/04_memory/max-studio-2026-10-08/2026-10-08_PATCH_pc-optimize-auditor-FAIL.md` item 9 |
| RAM | "64 GB" in 10-02 audit; 10-08 checklist still lists CPU/RAM as **UNKNOWN / to verify** | `2026-10-02-max-8189-setup-optimized.md` §3 · `…/2026-10-08_PATCH_pc-optimize-auditor-FAIL.md` item 16 |
| Single GPU, KF CPU (no iGPU) | desktop is driven from the same 5070 Ti | candidate-matrix W13 · local-llm auditor E2 |
| Prior encode-cache knowledge | Comfy execution cache keys on node inputs; `/free` evicts; image change can evict UNET | `/workspace/cos/research/2026-10-02-why-max-rewarm.md` |

## Mechanism (ComfyUI master `46493d82`, 2026-10-08 10:35 AM CT, read today)
- `model_management.text_encoder_device()`: `--gpu-only` or aimdo (DynVRAM) → GPU. Otherwise **HIGH/NORMAL_VRAM → GPU** and **LOW_VRAM/NO_VRAM → CPU**. `--lowvram` sets LOW_VRAM. So `--novram` also keeps the TE on CPU.
- `load_models_gpu()`: partial load (`lowvram_model_memory`) runs for **LOW_VRAM and NORMAL_VRAM** (`lowvram_available = True` by default). Dropping `--lowvram` changes **only** where the TE runs. `unet_offload_device` and `unet_inital_load_device` do not change.
- Windows ≥15 GB card: `EXTRA_RESERVED_VRAM` = 600+100 MB. `minimum_inference_memory` = 0.8 GiB + reserve ≈ **1.5 GiB**. With `--reserve-vram 2.5` the reserve is 2.5 GiB, so the floor ≈ 3.3 GiB.
- Stock `CLIPLoader.device` offers only `default` / `cpu`. There is **no per-node "force GPU"** while `--lowvram` is set.
- H3 TE = Qwen3-VL-32B truncated to 50 layers. Its output is the layer-50 hidden state `[seq, 5120]` plus `minimax_token_tags`. In REF2VA, **each ref image goes through the vision tower into the TE sequence** (`<Picture i>: <vision block>` before the prompt). So a new paste re-runs the vision part too.
- `MiniMaxH3ReferenceToVideo` does VAE ref-encode, TE tokenize and `encode_from_tokens_scheduled` **in one node**. Its cache key includes prompt, width, height, **length**, ref_image_size and images. Changing only `length` therefore re-runs the 32B TE.
- Under `match`, refs are scaled to the canvas pixel area. One image costs H·W/1024 positions (#15316 comment). **Derived:** 768×1344 → ~1,008 positions per ref and 480×864 → ~405. A 350–500-word paste adds its own text tokens (count NO_DATA).
- Built-in `SaveConditioning` saves tensors and scalar options only. It **raises `ValueError` on `minimax_refs`** (a list of dicts), which is added when the VAE is wired. It works only on a REF2VA node with no VAE (TE-only probe).

## Ranked options
VRAM budget at encode time on AlienPc (**derived**): 16.3 GB total (L8 "15.85/16.3 GB"). Subtract desktop share **D (NO_DATA)** and the Comfy floor of 1.5 GiB (3.3 GiB with reserve 2.5). The TE never has to co-reside with the UNET: Comfy evicts the UNET before loading the TE and reloads it for sampling. The relevant check is TE + activations against free VRAM, **not** TE + UNET. TE + UNET together = 15.69 + 14.0 GB > 16 GB, which is why `--gpu-only`/`--highvram` are dead (candidate-matrix standing fact).
TE activation peak above weights, measured by j2gg0s on the int8 TE (4090D): 550 pos 1.27 GB · 1,382 pos 1.52 GB · 1,966 pos 1.86 GB · 4,654 pos 2.29 GB. The floor includes one 500 MiB fp32 cast of the largest MLP (#15316).

### O1. Drop `--lowvram` only: TE on GPU with streamed partial load (W3) · **TOP**
- **Mechanism:** NORMAL_VRAM → `text_encoder_device` = cuda. Comfy evicts the UNET, loads as much of the TE as fits (free − 1.5 GiB) and streams the rest per layer from RAM. The forward then runs on nvfp4 tensor cores, which the 5070 Ti supports. After encode the TE is offloaded and the UNET reloads for sampling.
- **Exact change (argv only):** `main.py --listen 127.0.0.1 --port 8189 --disable-dynamic-vram --disable-async-offload --disable-pinned-memory --use-ck-attention`. Nodes and files are unchanged. The startup console should print `Set vram state to: NORMAL_VRAM`.
- **VRAM math (derived):** TE 14.61 GiB. Resident ≈ 16.3 GB − D − 1.5 GiB. If D ≈ 1 GiB (hypothetical, D is NO_DATA), ~13.4 GiB is resident and ~1.2 GiB streams per encode. Activations for ~1.5–2k positions are ~1.5–1.9 GB (j2gg0s, int8 analog), which is **at or above the 1.5 GiB floor**. This is exactly the #15316 edge.
- **Expected encode:** seconds (analog, not AlienPc):
  - #15316: RTX 4070 Ti S 16 GB, Windows 10, `--disable-dynamic-vram`. T2V node ~5 s; I2V node hung **1+ min** until the reserve fix brought it to ~10 s.
  - j2gg0s: int8 27 GB TE partially offloaded on a 4090D, encode **9.0 s patched vs ~10 s unpatched**.
  - ClipProj MEASUREMENTS: 32B prefill **0.385 s**; streaming 14.6 GB once over PCIe4 x8 ≈ 1 s (128 GB RAM, OS-cached). Their quote "30 minutes against 30 seconds" (u/hum_ma) is CPU fallback vs GPU, second-hand.
  - **AlienPc encode: NO_DATA.** Unpinned + sync transfers will be slower than the pinned analogs by an unmeasured amount.
- **Added cost:** a new paste now evicts and reloads the 13 GB UNET (unpinned, sync). Reload time **NO_DATA**. Measure it as the sampler-node delta in the A/B.
- **OOM risk:** MEDIUM. The UNET path is code-identical, so the sampling OOM risk should be unchanged in theory (unmeasured). The TE image-encode can overrun its budget (#15316). Because sysmem fallback is locked ON for Comfy, an overrun likely shows as a **silent slow encode** (shared-memory spill) rather than an OOM. That is why encode time and shared-GPU-memory are stop criteria.
- **Quality risk:** LOW. Same weights. GPU nvfp4 kernels and the CPU dequant path will not be bit-identical, so expect small differences at the same seed. The GPU path is what every DynVRAM and official user runs, because aimdo puts the TE on GPU. The A/B checks this with a cond cosine and Derrick's eyes.
- **Rollback:** restart with the KEEP argv (re-add `--lowvram`). No files change.

### O1b. O1 + `--reserve-vram 2.5` (W12a)
- **Mechanism:** raises Comfy's floor to ~3.3 GiB. The TE then holds less weight resident and streams more, but has room for the image-token activation spike. This is #15316's documented workaround ("using `--reserve-vram 2.5` does help"). PR #15316 (a `memory_estimation_function` for the H3 TE) is **still open and not in master** (verified in the source today).
- **Exact change:** O1 argv + `--reserve-vram 2.5`.
- **VRAM math (derived):** TE resident ≈ 16.3 − D − 3.3 GiB (≈11.5 GiB if D ≈ 1 GiB), so ~3 GiB streams per encode. The 2.5 GiB reserve also applies during **sampling**, so the UNET gets ~1.8 GiB less VRAM and sampling may slow. Sampling impact **NO_DATA**.
- **Expected encode:** ~10 s on the #15316 analog. AlienPc **NO_DATA**.
- **OOM risk:** LOW–MEDIUM (more headroom). **Quality risk:** same as O1. **Rollback:** KEEP argv.

### O2. Cache hygiene (no argv change; complements O1; zero quality risk)
- **Mechanism:** Comfy's in-process output cache (`--cache-ram` default) skips node 6 when prompt, canvas, **length**, refs and ref_image_size are all unchanged. Seed, steps, sampler and scheduler re-rolls already skip the TE.
- **Exact practice:** do not `POST /free` between same-prompt rolls (`free_memory` resets caches; see `2026-10-02-why-max-rewarm.md`). Do not change `length` or canvas while iterating seeds on one paste. Do not run `--cache-none`.
- **Gain:** seconds instead of minutes on **repeat** prompts only (cached node = ~0 s). **New pastes: no gain.**
- **Persistent cache across restarts:** built-in `SaveConditioning`/`ConditioningLoader` would need a custom node to re-attach `minimax_refs` (VAE ref latents) after loading. No such node is known (NO_DATA). The community `SaveH3Embedding` keeps only the text rows for `embedding:` use (`/workspace/cos/research/2026-10-02-reddit-h3-ref2va-embedding-COMPLETE/SaveH3Embedding.py`). **OOM risk:** none. **Rollback:** n/a.

### O3. O1 (or O1b) + re-enable pinned memory (W5 on top)
- **Mechanism:** pinned RAM speeds up the TE stream and the UNET reload that O1 adds. Comfy blog: 10–50% when weights spill. Tomiigo (5070 Ti): `--disable-pinned-memory` ≈ +1/5 runtime (180 s vs 150 s). Windows page-locks **40%** of RAM vs 90% on Linux (Tomiigo). **Derived:** at 64 GB that is ~25.6 GB pinnable, versus TE 15.7 + UNET 14.0 GB.
- **Exact change:** remove `--disable-pinned-memory` from the winning O1 argv.
- **Expected gain:** NO_DATA on AlienPc at 768×1344. W5 at 480×864 ran 2 TECH-ok cells (125.9 s / 44.1 s, not a fair pair).
- **OOM/stability risk:** MEDIUM (HostBuffer 1450 history was aimdo-path, which NODDV bypasses, but this was never isolated one-axis at 768). **Quality risk:** none expected. **Rollback:** re-add the flag.

### O4. DynamicVRAM ON (W4): official default path
- **Mechanism:** with aimdo, `text_encoder_device` = GPU, plus async offload and pinned memory. Linux 5070 Ti analog runs (Tomiigo) include the TE encode on GPU inside 165–195 s total jobs at an 8 GB cap. Encode not timed separately: NO_DATA.
- **Exact change:** remove `--disable-dynamic-vram --disable-async-offload --disable-pinned-memory` and `--lowvram` (inert under DynVRAM).
- **Risk:** HIGH. This is the HostBuffer WinError 1450 fail class on this box (#15255/#15269, local CAPA). It stays parked (W4 deferred). **Rollback:** KEEP argv.

### O5. ComfyUI-MultiGPU `CLIPLoaderMultiGPU` with device `cuda:0`, keeping `--lowvram`
- **Mechanism:** a per-node TE device override. Same effect on the TE as O1, but the rest of the argv stays at KEEP.
- **Change:** install the custom node and swap node 3 to `CLIPLoaderMultiGPU(clip_name=TE, type=minimax, device=cuda:0)`.
- **Risk:** the repo is **archived 2026-09-30, "no longer maintained"**. Compatibility with current master (quant ops / H3) is NO_DATA. Adds a custom-node dependency for no mechanistic gain over O1. Use only if O1 shows a side effect that O5 would avoid; none is known. **Rollback:** swap back to `CLIPLoader`.

### O6. Smaller or different TE file (only if O1/O1b fail)
| File | Size | Fits fully in VRAM at encode? (derived) | Quality risk | Notes |
|---|---|---|---|---|
| nvfp4_awq (current) | 15.69 GB | No (streams ~1–3 GiB) | reference | smallest **official** TE (Comfy-Org tree: bf16 51.51 · int8_convrot 27.14 · nvfp4_awq 15.69) |
| joeygambino Q4_K_M GGUF + mmproj F16 | 19.76 + 1.2 GB ("~16.5 GB resident") | No, **larger than nvfp4** | low–med | no VRAM win; needs ComfyUI-GGUF CLIPLoaderGGUF or H3-Multishot `H3ClipLoaderAny`; GGUF dequant overhead vs native nvfp4 |
| pottokao Q3_K_S_vis (abliterated) | ~12.6 GB | Borderline: 12.6 + ~1.5–1.9 activations + D + 1.5 floor ≈ 16.3 GB | **MED–HIGH** | abliterated weights drift the cond (ClipProj measured the abliterated gap *widening*; InstaSD: "placebo", may cost adherence); Q3 fidelity loss |
| ClipProj 4B/8B + matrix | 4.5–4.9 GB | Yes | **MED** | v3.1: image scores overlap 32B but "cosine is blind to countable attributes"; ref2va needs resident mode; ClipProj's own bench: total time **not measurably different** from 32B-on-GPU (175 vs 178 s), so the gain exists only vs CPU-TE |
- Expected encode for these on AlienPc: **NO_DATA**. Each needs a download + Derrick GO. **Rollback:** reselect the nvfp4 file.

### O7. Separate process / second machine encode (park)
- **Idea:** run the TE elsewhere (another Comfy with a REF2VA node without VAE + `SaveConditioning`) and ship the `[seq,5120]` tensor (~tens of MB, derived) back.
- **Blockers:** a custom loader must re-attach `minimax_refs` (NO_DATA, none found). llama.cpp cannot reproduce H3's layer-50 un-normed hidden state, deepstack vision and picture labels without custom code. pottokao's text-only GGUF is "plain llama.cpp text-encoder use", not a ComfyUI feed. Other GPU machines: NO_DATA. Not worth it while O1 is untested.

### O8. Image-prefix KV reuse (park)
- REF2VA places ref vision tokens before the prompt in a causal LM, so a prefix-KV cache could skip the image part on new pastes. No implementation found: NO_DATA.

### Dead on this box (do not test)
- `--gpu-only` / `--highvram`: TE + UNET can't co-reside.
- `--novram`: TE stays on CPU per code, and adds transfer.
- `--fp8_e4m3fn-text-enc`: measured kitchen-float8 break on 10-02; the TE is already nvfp4.
- `--fast-disk`: dynamic-only.
- MultiGPU DisTorch split of the TE across GPU+RAM: duplicates what native partial load already does in O1.

## A/B packet for AlienPc (do not run without Derrick exact GO · Dial/CoS lease · METHOD label)
**Held constant (all arms):** same Cond still, same prompts P1/P2/P3 (frozen .txt files of real 350–500-word REF2VA pastes), seed **71** (METHOD fair twin) and **72** for the cache check, **ST8**, `res_multistep`, scheduler = the R0 SoT row's scheduler (default `simple`, W3+ held baseline), shift 12/3, **768×1344 portrait × 124f**, `ref_image_size=match`, TURBO w4a8, ck ON, `:8188` closed, no LLM loaded, no other GPU app.
**Arms (one axis each, in order):**
| Arm | argv delta vs KEEP | GO |
|---|---|---|
| **A0** baseline | none (KEEP) | run-packet GO |
| **B1** | − `--lowvram` | W3 un-defer GO |
| **B2** | B1 + `--reserve-vram 2.5` | GO (one-axis vs B1) |
| **C1** (optional) | best of B1/B2 − `--disable-pinned-memory` | separate GO |
| **A0-post** | back to KEEP (bracket and rollback check) | covered by run GO |

**Per arm, cells in order:**
1. Restart Comfy with the arm argv. Confirm the console line `Set vram state to: LOW_VRAM` (A0) or `NORMAL_VRAM` (B/C).
2. Warm (unscored, per skill): ~1 s sacrificial, then a full 124f cell with **P1**.
3. **S1 (scored):** full cell **P2**, seed 71. This prompt has never been encoded in this process.
4. **S2 (scored repeat):** full cell **P3**, seed 71.
5. **S3 (cache check):** full cell P3, seed 72. Expect node 6 in `execution_cached` and near-zero encode.
6. **S4 (TE-only probe):** P2 through `LoadImage → CLIPLoader → MiniMaxH3ReferenceToVideo` (**no vae / audio_vae**) → `SaveConditioning` (prefix `conditioning/TEPROBE_<arm>`). This gives pure encode time plus a cond file for the cosine check.

**Record per scored cell:** node-6 seconds (encode), node-11 seconds (sampler, includes UNET reload), total `execution_start→execution_success` seconds, peak `memory.used` (nvidia-smi), shared GPU memory during node 6, console `Requested to load MiniMaxH3TEModel_` / `loaded partially|completely … MB loaded, … MB offloaded` lines with timestamps, mp4 path.

### Commands (PowerShell on AlienPc; paths assumed from harness: verify with `Test-Path` first)
```powershell
# 0) pre-flight (read-only)
$CR  = 'C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI'
$PY  = "$CR\.venv\Scripts\python.exe"
$PK  = 'C:\Users\derek\Desktop\MAX_TE_GPU_SPIKE_2026-10-08'   # new pack dir
Test-Path $PY; New-Item -ItemType Directory -Force "$PK\logs","$PK\clips","$PK\meta" | Out-Null
(Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum/1GB   # verify RAM (64 GB unverified)
nvidia-smi --query-gpu=name,memory.used,memory.total,driver_version --format=csv  # idle desktop share = D
Get-NetTCPConnection -LocalPort 8188 -State Listen -ErrorAction SilentlyContinue  # must be empty

# 1) argv per arm
$BASE = @('-u','main.py','--listen','127.0.0.1','--port','8189')
$KEEP = $BASE + @('--lowvram','--disable-dynamic-vram','--disable-async-offload','--disable-pinned-memory','--use-ck-attention')
$B1   = $BASE + @('--disable-dynamic-vram','--disable-async-offload','--disable-pinned-memory','--use-ck-attention')
$B2   = $B1 + @('--reserve-vram','2.5')
$C1   = $BASE + @('--disable-dynamic-vram','--disable-async-offload','--use-ck-attention')   # + '--reserve-vram','2.5' if B2 won
$ARM='A0'; $ARGV=$KEEP   # set per arm

# 2) stop current :8189 (only under the GO + lease)
Get-NetTCPConnection -LocalPort 8189 -State Listen -ErrorAction SilentlyContinue |
  Select-Object -Expand OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force }

# 3) GPU + shared-memory loggers (separate windows; stop with Ctrl+C after the arm)
Start-Process nvidia-smi -ArgumentList "--query-gpu=timestamp,memory.used,memory.total,utilization.gpu,pcie.link.gen.current,pcie.link.width.current --format=csv -lms 500 -f $PK\logs\$ARM`_nvsmi.csv" -WindowStyle Minimized
Start-Process typeperf -ArgumentList "`"\GPU Adapter Memory(*)\Shared Usage`" `"\GPU Adapter Memory(*)\Dedicated Usage`" -si 1 -f CSV -o $PK\logs\$ARM`_gpumem.csv -y" -WindowStyle Minimized

# 4) launch Comfy with timestamped console log (dedicated PowerShell window)
Set-Location $CR
& $PY @ARGV 2>&1 | ForEach-Object { '{0:HH:mm:ss.fff} {1}' -f (Get-Date), "$_" } | Tee-Object -FilePath "$PK\logs\$ARM`_console.log"
```
**Per-node encode timer.** Save as `$PK\meta\te_timer.py`. Run it with Comfy's own venv, because aiohttp ships with Comfy. The input is an API-format workflow JSON: export via UI "Export (API)" or dump `build()` from the harness `opt_queue.py`.
```python
# te_timer.py — queue one API workflow on :8189 and log per-node wall seconds from the websocket
import asyncio, aiohttp, json, time, uuid, argparse, datetime
ap = argparse.ArgumentParser()
ap.add_argument("--wf", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--prompt-file"); ap.add_argument("--prompt-node", default="6")
ap.add_argument("--seed", type=int); ap.add_argument("--seed-node", default="7")
a = ap.parse_args()
wf = json.load(open(a.wf, encoding="utf-8"))
if a.prompt_file: wf[a.prompt_node]["inputs"]["prompt"] = open(a.prompt_file, encoding="utf-8").read()
if a.seed is not None and a.seed_node in wf: wf[a.seed_node]["inputs"]["noise_seed"] = a.seed
async def main():
    cid = str(uuid.uuid4()); rows = []; cached = []
    async with aiohttp.ClientSession() as s:
        async with s.ws_connect(f"ws://127.0.0.1:8189/ws?clientId={cid}", max_msg_size=0) as ws:
            r = await s.post("http://127.0.0.1:8189/prompt", json={"prompt": wf, "client_id": cid})
            pid = (await r.json())["prompt_id"]; t0 = time.perf_counter(); cur, tc = None, t0; status = "?"
            async for msg in ws:
                if msg.type != aiohttp.WSMsgType.TEXT: continue
                m = json.loads(msg.data); d = m.get("data", {}) or {}
                if d.get("prompt_id") not in (None, pid): continue
                now = time.perf_counter(); t = m.get("type")
                if t == "execution_cached": cached = d.get("nodes", [])
                elif t == "executing":
                    if cur is not None: rows.append({"node": cur, "s": round(now - tc, 2)})
                    cur, tc = d.get("node"), now
                    if cur is None: status = "success"; break
                elif t == "execution_success": status = "success"; break
                elif t in ("execution_error", "execution_interrupted"):
                    status = t; rows.append({"error": (d.get("exception_message") or "")[:500]}); break
            out = {"ts_ct": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CT"), "prompt_id": pid,
                   "status": status, "total_s": round(time.perf_counter() - t0, 2), "cached_nodes": cached, "nodes": rows}
            open(a.out, "w").write(json.dumps(out, indent=1)); print(json.dumps(out))
asyncio.run(main())
```
```powershell
# scored cell example (arm A0, S1)
& $PY "$PK\meta\te_timer.py" --wf "$PK\meta\wf_full_768x1344x124_ST8.json" --prompt-file "$PK\meta\P2.txt" --seed 71 --out "$PK\logs\A0_S1.json"
# TE-only probe (S4): wf_teprobe.json = nodes 1,3,6(no vae/audio_vae),20 SaveConditioning
& $PY "$PK\meta\te_timer.py" --wf "$PK\meta\wf_teprobe.json" --prompt-file "$PK\meta\P2.txt" --out "$PK\logs\A0_S4.json"
```
**Cond cosine (A0 CPU-TE vs B GPU-TE; run on AlienPc or copy files to the box).** Informational only. No pass threshold is sourced, so none is set.
```python
import sys, torch; from safetensors.torch import load_file
a, b = load_file(sys.argv[1])["conditioning"].float().flatten(), load_file(sys.argv[2])["conditioning"].float().flatten()
print("shape_equal", a.shape == b.shape, "cos", torch.nn.functional.cosine_similarity(a, b, dim=0).item(), "max_abs", (a - b).abs().max().item())
```
(Expected to work because the REF2VA node without a VAE emits no `minimax_refs`. If `SaveConditioning` still raises, skip the cosine and rely on Derrick's eyes.)

**Stop criteria (stop the arm, restore KEEP):**
- Any OOM, `HostBuffer`/WinError 1450, access violation, or `Allocation on device` in the console.
- On B/C arms, node-6 encode **> 60 s**, or shared GPU memory rising during node 6. This is the #15316 hang class (the analog was 1+ min unfixed vs ~10 s fixed). The 60 s threshold is a proposed criterion, not a sourced number. If B1 trips it, run B2. If B2 trips it, stop.
- Sampler node slower than A0 by a margin Derrick calls material. Record it; Derrick decides.
- **Quality:** any visible drift on Derrick's eyes between A0 S1 and the arm's S1 (same seed). Stop and do not promote.

**Rollback (after every non-A0 arm, and finally):** stop :8189, then relaunch with `$KEEP`. Confirm `Set vram state to: LOW_VRAM`. Run A0-post S1 (same P2, seed 71) to bracket drift. Stop the nvidia-smi and typeperf loggers. **No KEEP from bots.** A winner stays CANDIDATE until Derrick's exact GO.

**Scoreboard row fields:** arm · cell · prompt id · seed · canvas×len · steps/sampler/sched · argv · node6_s · node11_s · total_s · cached_nodes · peak_VRAM_MiB · shared_peak · TECH ok · OOM/1450 · cond cos/max_abs (S4) · mp4 · label METHOD.

## What needs Derrick's GO
1. **Run this packet on AlienPc.** It restarts :8189 per arm, needs the Shell lease, and takes production Max offline while it runs.
2. **Un-defer W3 → arm B1** (drop `--lowvram`). He deferred it 2026-10-06 ~10:17 CT.
3. **Arm B2** (`--reserve-vram 2.5`) and optional **C1** (re-enable pinned), each one-axis.
4. **Any KEEP argv change** after his eyes on A0 vs winner.
5. **Only if O1 fails:** downloads/installs for O6 (GGUF Q3/Q4, H3-Multishot loader, ClipProj) or O5 (archived MultiGPU).

## Unknowns / NO_DATA
| Item | Status |
|---|---|
| AlienPc TE encode time on GPU (B1/B2) | **NO_DATA**. Analogs only (#15316 ~5–10 s; ClipProj 0.385 s prefill) |
| Current 6–7 min CPU encode | user-reported; never logged per node → A0 S1/S4 will measure it |
| UNET evict→reload cost per new paste under unpinned/sync | **NO_DATA** |
| Desktop VRAM share D on AlienPc | **NO_DATA** (read idle `nvidia-smi` in pre-flight) |
| System RAM 64 GB | unverified (pre-flight command above) |
| Text token count of a 350–500-word paste | NO_DATA (derived ~1,008 positions per ref at 768×1344) |
| Whether B1 sampling walls equal A0 (code says the UNET path is identical) | unmeasured |
| GPU vs CPU cond numeric difference and visible effect | NO_DATA → S4 cosine + Derrick's eyes |
| Pinned memory stability at 768×1344 under NODDV | NO_DATA (W5 only at 480×864) |
| GGUF Q3_K_S / ClipProj quality on REF2VA with these Conds | NO_DATA |
| MultiGPU compatibility with current master | NO_DATA (archived 2026-09-30) |
| Image-prefix KV reuse / remote-encode attach node | none found |
| Measured big-LLM-TE encode on 16 GB for Wan/Hunyuan/Qwen-Image | none found with numbers. LTX-2 16 GB users report CPU TE "slow" and GPU-streamed "much faster" (qualitative, #303) |

## Sources (all accessed 2026-10-08 CT)
1. ComfyUI startup flags: `--lowvram` "No effect when dynamic VRAM is enabled. Otherwise, runs text encoders on CPU"; `--reserve-vram`; `--cache-ram` default. https://docs.comfy.org/development/comfyui-server/startup-flags (accessed 2026-10-08)
2. ComfyUI `model_management.py` @ master `46493d82` (2026-10-08 10:35 AM CT): `text_encoder_device`, `load_models_gpu` partial-load for LOW+NORMAL, `EXTRA_RESERVED_VRAM`, `minimum_inference_memory`. https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/model_management.py (accessed 2026-10-08)
3. ComfyUI `cli_args.py` (lowvram/novram/gpu-only/reserve-vram/cache flags). https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/cli_args.py (accessed 2026-10-08)
4. ComfyUI `nodes.py` `CLIPLoader` device = default/cpu only. https://github.com/Comfy-Org/ComfyUI/blob/master/nodes.py (accessed 2026-10-08)
5. ComfyUI `comfy/text_encoders/minimax.py` (Qwen3-VL-32B truncated to 50 layers, vision blocks in sequence) and `comfy_extras/nodes_minimax_h3.py` (REF2VA node does VAE + TE in one node). https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py · https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py (accessed 2026-10-08)
6. ComfyUI `comfy_extras/nodes_cond.py` `SaveConditioning`/`ConditioningLoader` (raises on non-tensor options). https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_cond.py (accessed 2026-10-08)
7. ComfyUI PR/issue #15316 (opened 2026-08-05, updated 2026-08-31, open): 4070 Ti S 16 GB Windows NODDV encode ~5 s T2V / 1+ min→~10 s I2V; `--reserve-vram 2.5` tip; j2gg0s activation table and 9.0 vs ~10 s. https://github.com/Comfy-Org/ComfyUI/issues/15316 (accessed 2026-10-08)
8. Comfy-Org/MiniMax-H3 repack (lastModified 2026-09-29): TE files bf16 51.51 / int8_convrot 27.14 / nvfp4_awq 15.69 GB; "nvfp4 text encoder does not require Blackwell". https://huggingface.co/Comfy-Org/MiniMax-H3 (accessed 2026-10-08)
9. MiniMaxAI/MiniMax-H3 official card (lastModified 2026-08-13): "H3-Encoder uses the full pretrained weights of Qwen3-VL-32B and provides the hidden states from its 50th layer". https://huggingface.co/MiniMaxAI/MiniMax-H3 (accessed 2026-10-08)
10. Comfy H3 tutorial. https://docs.comfy.org/tutorials/video/minimax/minimax-h3 (accessed 2026-10-08)
11. TenStrip 10Eros-Max README (lastModified 2026-09-08): TURBO = baked turbo delta; no TE guidance. https://huggingface.co/TenStrip/10Eros-Max (accessed 2026-10-08)
12. ClipProj README + MEASUREMENTS (last commit 2026-08-17 CEST): 32B prefill 0.385 s, ~1 s stream, 175/174/178 s totals, CPU fallback "30 minutes against 30 seconds", single-GPU guidance, abliterated gap. https://github.com/nicolab28/ComfyUI-ClipProj · https://github.com/nicolab28/ComfyUI-ClipProj/blob/main/MEASUREMENTS.md (accessed 2026-10-08)
13. opensourcefactory ClipProj test (2026-08-10): normal-mode LoRA patch failure caveat (turbo LoRA; our TURBO file has no LoRA node). https://www.opensourcefactory.dev/2026/08/i-replaced-minimax-h3s-32b-text-encoder.html (accessed 2026-10-08)
14. InstaSD H3 text-encoder guide (12–16 GB → GGUF Q4-class; abliterated = placebo/adherence risk). https://www.instasd.com/post/minimax-h3-text-encoder-guide-comfyui (accessed 2026-10-08)
15. joeygambino H3 encoder GGUF (lastModified 2026-08-07): Q4_K_M 19.76 GB, Q5_K_M 23.21 GB, mmproj 1.2 GB required for refs. https://huggingface.co/joeygambino/MiniMax-H3-encoder-GGUF (accessed 2026-10-08)
16. pottokao abliterated Q3_K_S GGUF (lastModified 2026-09-23): ~11.5 GB text-only / ~12.6 GB `_vis` for ComfyUI. https://huggingface.co/pottokao/MiniMax-H3-TextEncoder-Qwen3VL-32B-abliterated-GGUF (accessed 2026-10-08)
17. ComfyUI-MultiGPU README (archive notice: "archived on 30 September 2026", last commit 2026-09-20). https://github.com/pollockjj/ComfyUI-MultiGPU (accessed 2026-10-08)
18. city96 ComfyUI-GGUF README (CLIPLoaderGGUF; stock only merges mmproj for qwen2vl per joeygambino). https://github.com/city96/ComfyUI-GGUF (accessed 2026-10-08)
19. Tomiigo minimax-h3-16gb (5070 Ti, Linux): pinned +1/5, Windows 40% page-lock, 165–195 s jobs. https://github.com/Tomiigo/minimax-h3-16gb (accessed 2026-10-08)
20. LTX-2 16 GB analog (qualitative CPU-TE slow vs GPU-streamed fast). https://github.com/Lightricks/ComfyUI-LTXVideo/issues/303 · LTXV Save/Load Conditioning: https://docs.ltx.video/open-source-model/integration-tools/ltx-2-comfy-ui-nodes.md (accessed 2026-10-08)

## Verify
- [x] TLDR ≤6 lines · local facts with paths · ranked options with mechanism/argv/VRAM/encode/OOM/quality/rollback
- [x] A/B packet: baseline + one-axis arms, same seed/prompt/ST8/canvas, PowerShell, per-node timer, stop criteria, rollback to KEEP
- [x] NO_DATA wherever unmeasured; derived numbers labeled; no KEEP claimed; AlienPc untouched; no messages sent
- [x] ≥3 dated primary URLs (20 listed, accessed 2026-10-08)

## Memory (research-to-fleet-memory)
**Standing fact promoted** as a constraint, not a decision: Fleet Memory 04_memory Doc `2026-10-08_constraint_max-h3-te-placement-cache-quant` · id `1inqARqryu6ydTfBGLW2hNW0sCPbBiiUfaMw0Vu5uH5E` (created 2026-10-08 12:44 PM CT, personal Drive).
Promoted, all source-code or repo facts:
- `--lowvram` is the only thing putting the TE on CPU under NODDV.
- The REF2VA cache key includes `length`.
- `SaveConditioning` can't persist REF2VA cond when the VAE is wired.
- GGUF Q4_K_M (19.76 GB) is larger than nvfp4 (15.69 GB).
- MultiGPU was archived 2026-09-30.
- #15316 is still open; its workaround is `--reserve-vram 2.5`.
**Not promoted:** "drop `--lowvram` fixes the encode." That is a hypothesis until the A/B runs on Derrick's GO.
