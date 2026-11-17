# Max :8189 setup audit — ComfyUI 0.38.0 / RTX 5070 Ti 16GB

**Date:** 2026-10-02 (America/Chicago)  
**Scope:** Research only. Did not touch AlienPc, kill S0, or restart Comfy.  
**Live argv (confirmed at audit start):**
```
main.py --listen 127.0.0.1 --port 8189 \
  --fp8_e4m3fn-unet --fp8_e4m3fn-text-enc \
  --lowvram --disable-dynamic-vram \
  --disable-async-offload --disable-pinned-memory
```

## Verdict

| Axis | Result |
|------|--------|
| **CORRECT** | **PARTIAL** |
| **OPTIMAL** | **NO** |

**One-liner:** Memory fallback triad (NODDV + disable-async-offload + disable-pinned-memory) is the right *workaround* for this Windows AIMDO/HostBuffer box; the two `--fp8_e4m3fn-*` CLI casts are **incorrect and harmful** with native w4a8 UNET + nvfp4 TE — drop them immediately on next restart (parent/Dial action; this agent did not restart).

---

## 1. Sources consulted

| Source | URL | Relevance |
|--------|-----|-----------|
| ComfyUI issue #15255 | https://github.com/Comfy-Org/ComfyUI/issues/15255 | DynamicVRAM HostBuffer → OOM; `--disable-dynamic-vram` confirmed fix |
| ComfyUI issue #15269 | https://github.com/Comfy-Org/ComfyUI/issues/15269 | AIMDO 0.4.11 second-gen VRAM Allocation failed; NODDV fixes |
| ComfyUI issue #14250 | https://github.com/Comfy-Org/ComfyUI/issues/14250 | HostBuffer + WAN; `--disable-pinned-memory` fix |
| HostBuffer 1450 Chinese writeup | https://www.luomor.com/blog/2026/09/01/comfyui-报错-hostbuffer-read_file_slice-failed-error1450-终极解决教程/ | WinError 1450 = ERROR_NO_SYSTEM_RESOURCES; aimdo async IO; COMFYUI_DISABLE_AIMDO=1 |
| Official startup flags | https://docs.comfy.org/development/comfyui-server/startup-flags | `--lowvram` inert when DynamicVRAM on; FP8 flags = *store* weights in fp8; async/pinned/NODDV semantics |
| InstaSD VRAM guide (2026-08) | https://www.instasd.com/post/comfyui-vram-offloading-guide | 16GB H3 community: stock defaults + 64GB RAM; first triage `--disable-pinned-memory`; `--lowvram` dead under DynamicVRAM |
| Reddit r/comfyui 5060 16GB | https://www.reddit.com/r/comfyui/comments/1svix8a/oom_errors_after_comfy_update_and_how_im_getting/ | `--reserve-vram` + `--lowvram` + `--disable-pinned-memory` community recipe |
| Comfy blog NVFP4/async/pinned | https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia | Async+pinned default; help when offloading; NVFP4 needs cu130 on Blackwell |
| GitHub #11864 | https://github.com/Comfy-Org/ComfyUI/issues/11864 | Setting weight_dtype/fp8 on NVFP4 **forcibly upcasts** 4-bit → FP8 (~14GB load vs ~7GB) |
| Quant load-errors guide | https://localaimaster.com/blog/comfyui-quantization-format-errors | Leave `weight_dtype=default` on pre-quant files; fp8 dropdown is a cast for bf16, fights metadata |
| Legacy FP8 blog (2023) | https://github.com/comfyanonymous/ComfyUI_Blog/blob/master/_posts/2023-12-19-Update.md | `--fp8_e4m3fn-unet/text-enc` = runtime cast of MODEL/CLIP into fp8 storage |
| HF / H3 16GB recipes | sakamakismile NVFP4, smeltcore 4070TiS, wildminder performance guide | 16GB Max/H3: use native quants; DynamicVRAM preferred when healthy; 64GB RAM |
| Live S0 fail (parent steer) | prompt_id `1b214838` | `NoCapableBackendError rms_rope_split_half_ — q_scale dtype torch.float8_e4m3fn not in {bf16,fp32,fp16}` |

---

## 2. Argv flag-by-flag

| Flag | Status | Notes |
|------|--------|-------|
| `--listen 127.0.0.1 --port 8189` | **KEEP** | Local SoT; :8188 closed per Derrick GO — correct RAM isolation |
| `--fp8_e4m3fn-unet` | **DROP** | Legacy cast. W4A8 UNET already has `comfy_quant` layout. Cast pollutes scales → kitchen `rms_rope_split_half_` rejects `q_scale` as float8_e4m3fn (S0 fail 1b214838). Same class as #11864 upcast. |
| `--fp8_e4m3fn-text-enc` | **DROP** | TE is already `qwen3vl_32b_minimax_h3_nvfp4_awq` (~15.7GB). CLI fp8 cast fights native NVFP4/AWQ metadata; redundant at best, harmful at worst. |
| `--lowvram` | **KEEP while NODDV** | Docs: inert under DynamicVRAM; **active** when NODDV — TE on CPU. Needed for 15.7GB TE + 14GB UNET on 16GB card without AIMDO streaming. |
| `--disable-dynamic-vram` | **KEEP (workaround)** | Required on this box: DynamicVRAM/AIMDO → HostBuffer WinError 1450. Community + #15255/#15269. Not “optimal,” but correct until AIMDO fixed. |
| `--disable-async-offload` | **KEEP (with NODDV)** | Async offload is AIMDO-adjacent DMA path; researched fallback pair with disable-pinned. Costs speed; stability first for Max load. |
| `--disable-pinned-memory` | **KEEP** | First-line HostBuffer/OOM triage on Windows 16GB (#14250, InstaSD, Reddit). Do not remove while NODDV stack is live. |

---

## 3. vs community “best” for 16GB Max H3

**Healthy AIMDO box (community ideal):**
```
python main.py   # stock: DynamicVRAM + async-offload + pinned ON
# triage if OOM: --disable-pinned-memory, then --vram-headroom 1
# 64GB system RAM; native NVFP4/W4A8/INT8 quants; weight_dtype=default
```

**This AlienPc box (broken AIMDO HostBuffer 1450):**
Ideal DynamicVRAM path is **unavailable**. Correct local target is classic estimate-based `--lowvram` + disable AIMDO DMA helpers, **without** fp8 CLI casts.

| Ideal community | Our live | Gap |
|-----------------|----------|-----|
| DynamicVRAM ON | OFF (NODDV) | Forced by HostBuffer 1450 — not optional |
| async-offload ON | OFF | Stability pairing with NODDV |
| pinned ON (disable only if OOM) | OFF | Correct for this fail class |
| No fp8 CLI on native quants | **fp8 CLI ON** | **Bug — drop** |
| Single Comfy | :8188 closed | Correct after GO |
| 64GB RAM | 64GB | Match |
| torch cu130 | 2.15.dev cu130 | Match (needed for NVFP4 kernels on 5070 Ti) |

---

## 4. Recommended argv (next restart — do not apply in this research turn)

```
main.py --listen 127.0.0.1 --port 8189 \
  --lowvram \
  --disable-dynamic-vram \
  --disable-async-offload \
  --disable-pinned-memory
```

Optional later (only if still RAM-pressure OOMs after drop-fp8 smokes):
- `--reserve-vram 1` or `1.5` (Windows desktop share)
- `--cpu-vae` only if VAE decode OOMs after successful sample (InstaSD “decode wall”)

**Do NOT add** without a new red-team:
- `--enable-dynamic-vram` / remove NODDV
- re-add `--fp8_e4m3fn-*`
- second Comfy on :8188
- `--fast` / `--use-sage-attention` until ≥2 valid TECH smokes

---

## 5. What NOT to change

- Port `:8189`, bind `127.0.0.1`
- Model files: `10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors`, `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`, video int8 VAE + audio fp32
- Workflow mode: MiniMaxH3ReferenceToVideo REF2VA, 864×480, 124f, 25 steps (TECH settings separate from argv)
- Keep `:8188` dead while Max TE+UNET load needs ~15GB+ host RAM
- UNETLoader / CLIPLoader `weight_dtype` / precision dropdowns: leave **default** so `comfy_quant` metadata drives layout

---

## 6. Risk of re-enabling Dynamic VRAM

| Risk | Severity | Evidence |
|------|----------|----------|
| HostBuffer.read_file_slice / WinError 1450 | **HIGH** | Local fail history + #15255 + 1450 writeup |
| Second-gen AIMDO “VRAM Allocation failed (non OOM)” | HIGH | #15269 |
| Access violation under dual-Comfy RAM pressure | MEDIUM (mitigated) | Local NODDV crash with :8188 up; :8188 now closed |
| Performance regression vs healthy DynamicVRAM | Accepted cost | Classic lowvram slower; stability > speed until AIMDO patch |

**Policy:** Dynamic VRAM stays **OFF** on production `:8189` until a Comfy/AIMDO release survives Max TE+UNET load **and** ≥2 consecutive TECH smokes with DynamicVRAM ON and no HostBuffer. Re-enable only as an explicit A/B, not a silent default flip.

---

## 7. S0 fail chain (interpreted)

1. DynamicVRAM ON → AIMDO HostBuffer WinError 1450  
2. NODDV alone + :8188 up → access violation after TE ~15GB  
3. NODDV + disable-async + disable-pinned + :8188 closed → past load into sampler  
4. **New:** SamplerCustomAdvanced `NoCapableBackendError` on `rms_rope_split_half_` because `q_scale` is `torch.float8_e4m3fn` but kitchen eager/cuda backends for that op only accept `{bf16, fp32, fp16}` — strongly attributable to `--fp8_e4m3fn-unet` / `--fp8_e4m3fn-text-enc` casting scales that must stay higher precision alongside w4a8/nvfp4 packed weights.

---

## 8. Bottom line for Dial / parent

- **CORRECT: PARTIAL** — memory workaround stack yes; fp8 CLI no.  
- **OPTIMAL: NO** — cannot use DynamicVRAM (broken on this Windows AIMDO path); fp8 flags actively break kitchen RoPE.  
- **Next restart argv:** drop both `--fp8_e4m3fn-*`; keep the four memory flags + listen/port.  
- **This turn:** research + stamp only; AlienPc / S0 untouched.
