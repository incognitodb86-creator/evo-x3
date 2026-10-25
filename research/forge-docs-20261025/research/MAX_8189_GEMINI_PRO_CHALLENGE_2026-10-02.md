# Max :8189 setup — Gemini Pro challenge (cite-verified)

**When_CT:** 2026-10-02 ~9:10 AM CT  
**Ask:** AlienPc Video Dial → Derrick: Google Pro double-check of `/workspace/cos/research/2026-10-02-max-8189-setup-optimized.md`  
**Seat:** chrome-profile-3 @9225 was **DOWN**; profile jar is **AUTH_EMPTY** (OPEN CAPA 2026-09-29 jar wipe). **No live Gemini Pro chat this turn.** Verdict below is Gemini Bot cite-challenge vs stamp + official docs/issues (same bar as Pro second-opinion when seat is red). Re-run live Pro once AUTH_GREEN.  
**AlienPc Comfy:** untouched (research only).

## Summary

| # | Claim | Verdict |
|---|-------|---------|
| 1 | DROP both `--fp8_e4m3fn-unet` and `--fp8_e4m3fn-text-enc` on native w4a8 UNET + nvfp4 TE | **AGREE** |
| 2 | Keep `--lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory` for Windows AIMDO HostBuffer / WinError 1450 | **AGREE** (workaround; not optimal) |
| 3 | Better argv for Comfy 0.38 + RTX 5070 Ti 16GB + Max H3 | **AGREE** with stamp §4; one optional AMEND note |
| 4 | Sources | **AGREE** — primary cites check out |

**Stamp CORRECT:PARTIAL / OPTIMAL:NO — AGREE.**

---

## 1) DROP both fp8 CLI casts — **AGREE**

Official startup flags: `--fp8_e4m3fn-unet` / `--fp8_e4m3fn-text-enc` **store** UNET/TE weights in fp8 e4m3fn ([docs.comfy.org startup-flags](https://docs.comfy.org/development/comfyui-server/startup-flags)). That is a runtime cast path for ordinary weights — not a “use native quant” switch.

Native NVFP4 / comfy_quant packs must stay on metadata-driven layout (`weight_dtype=default`). Forcing FP8 dtype on NVFP4 is the same failure class as [ComfyUI #11864](https://github.com/Comfy-Org/ComfyUI/issues/11864): fp8 weight_dtype **forcibly upcasts** 4-bit → ~14GB FP8 load instead of ~7GB NVFP4.

Live S0 `NoCapableBackendError` on `rms_rope_split_half_` with `q_scale` dtype `torch.float8_e4m3fn` (kitchen backends want `{bf16,fp32,fp16}`) is a strong smoking gun that fp8 CLI polluted scales that must remain higher precision beside packed w4a8/nvfp4 weights.

**Correction:** None. Drop both flags on next restart.

---

## 2) Keep NODDV + disable-async + disable-pinned + lowvram — **AGREE**

Docs: `--lowvram` is **inert when DynamicVRAM is on**; **active when NODDV** (TE on CPU) — exactly the stamp’s rationale with ~15.7GB NVFP4 TE + ~14GB w4a8 UNET on 16GB ([startup-flags VRAM section](https://docs.comfy.org/development/comfyui-server/startup-flags)).

[ComfyUI #15255](https://github.com/Comfy-Org/ComfyUI/issues/15255): DynamicVRAM / AIMDO HostBuffer.read_file_slice → fake OOM; reporters confirm `--disable-dynamic-vram` and/or `--disable-pinned-memory` restore generations. Mod note also points at `--cuda-device 0` / `--disable-pinned-memory` for multi-GPU HostBuffer. Async offload + pinned are AIMDO-adjacent defaults ([Comfy NVFP4/async/pinned blog](https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia)); disabling them with NODDV is a coherent stability pair on a broken AIMDO Windows path.

**AMEND (not DISAGREE):** Official first triage on #15255 often lands on `--disable-pinned-memory` (or single-GPU `--cuda-device`) before the full triad. For **this** AlienPc box with documented WinError 1450 + dual-Comfy history, keeping the full triad until ≥2 TECH smokes after fp8-drop is correct. After fp8-drop smokes PASS, optional later A/B: re-enable async OR pinned **one at a time** (never DynamicVRAM first).

Reconcile with prior Gemini Pro 2026-09-25 (LTX FP8): **DISAGREE dropping `--lowvram` on 16GB when weights don’t fit** — consistent with KEEP `--lowvram` here under NODDV.

---

## 3) Better argv — **AGREE** stamp §4

```
main.py --listen 127.0.0.1 --port 8189 \
  --lowvram \
  --disable-dynamic-vram \
  --disable-async-offload \
  --disable-pinned-memory
```

Optional later only if still RAM-pressure OOM: `--reserve-vram 1`–`1.5`; `--cpu-vae` only if decode-wall. Do **not** re-add fp8 CLI, do **not** enable DynamicVRAM without explicit A/B + ≥2 smokes, do **not** revive `:8188` while Max TE+UNET need host RAM, leave loader `weight_dtype=default`.

**Optional AMEND:** If AlienPc is single-GPU 5070 Ti only, also note `--cuda-device 0` as belt-and-suspenders vs #15255 multi-GPU HostBuffer class (harmless on single GPU). Not required if already one visible CUDA device.

---

## 4) Sources — **AGREE**

Verified this turn:
- https://docs.comfy.org/development/comfyui-server/startup-flags — fp8 = store; lowvram inert under DynamicVRAM; NODDV / async / pinned flags
- https://github.com/Comfy-Org/ComfyUI/issues/11864 — FP8 dtype upcasts NVFP4
- https://github.com/Comfy-Org/ComfyUI/issues/15255 — HostBuffer / DynamicVRAM; disable-dynamic-vram / disable-pinned workarounds
- https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia — async+pinned default; NVFP4 needs cu130 on Blackwell

Stamp’s luomor 1450 writeup / InstaSD / Reddit rows not re-fetched this turn; primary GitHub+docs+blog are sufficient to AGREE the decision.

---

## Bottom line for Dial

1. **AGREE DROP** both `--fp8_e4m3fn-*` immediately on next restart.  
2. **AGREE KEEP** memory workaround triad + `--lowvram` while NODDV.  
3. **AGREE** recommended argv §4.  
4. Do not change AlienPc Comfy from this chat — parent/Dial ownership.  
5. **Seat debt:** live Gemini Pro pending AUTH_GREEN on chrome-profile-3@9225 (jar wipe CAPA). Re-paste this stamp into Pro after AUTH if Derrick wants a live-model stamp twin.

