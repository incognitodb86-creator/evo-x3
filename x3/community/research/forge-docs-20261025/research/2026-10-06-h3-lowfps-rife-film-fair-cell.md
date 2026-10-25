# RESEARCH — H3 low-FPS gen → RIFE/FILM → 24fps fair cell — 2026-10-06 ~1:57 PM CT

**Owner:** Max Research (cites only) · **Ask:** Derrick GO via Dial brainstorm+plan · **Dial owns** fair Plan/Work · no KEEP/PASS/0.95  
**Separate from:** Flux E1C face · torch.compile (PARTIAL prior; not this cell)  
**Prior speed context (no argv re-litigate):** `2026-10-02-max-h3-faster-gen-no-quality-loss.md` · `2026-10-06-max-8189-keep-vs-official-community-optimize.md`  
**Locks:** fiction adults 21+ nomenclature · KEEP = Derrick exact GO only · wall = canvas×length not argv

## TLDR
**Default = Fannovel16 `ComfyUI-Frame-Interpolation` → RIFE VFI (`rife47.pth` HAVE on live :8189) · prefer gen@12 → 2× → 24 over gen@8 → 3×.** FILM = better large-motion *theory* (Google ECCV’22) but **FILM weights NO_DATA/missing** on this host. Native Comfy `Frame Interpolate` (RIFE/FILM safetensors) = folder stub only. Official H3 = **native 24fps** frame grid — no official low-FPS mode. Peel/fabric quality of low-FPS+VFI vs native-24 on Max KEEP = **NO_DATA** (never A/B’d); expect ghosting/smear/false-smooth; audio not healed by VFI.

## Pack comparison (default for Max KEEP post-gen)

| Pack / node | What it is | Speed / VRAM | Large motion / peel | On :8189 Max | Verdict |
|---|---|---|---|---|---|
| **ComfyUI-Frame-Interpolation** (Fannovel16) **RIFE VFI** | Custom pack; RIFE 4.0–4.9; category `…/VFI` | Fast / light | Practical default; ghost/trail/warp on large displace (community) | **HAVE** pack + **`ckpts/rife/rife47.pth`** (~21 MB) | **DEFAULT** for fair cell |
| Same pack **FILM VFI** | Google FILM via pack; large-disocclusion design | Heavier than RIFE | Paper SoT for large motion / disocclusion sharpness | Pack HAVE · **FILM ckpt NO_DATA** (only rife/ under ckpts) | Secondary arm **after** install |
| **Native Comfy** `FrameInterpolationModelLoader` + `Frame Interpolate` | Core (kijai CORE-29); models in `models/frame_interpolation/` | Managed offload | RIFE or FILM via Comfy-Org HF (`rife_v4.25/4.26`, `film_net_fp16`) | Folder **EXISTS** · weights = placeholder only | Optional if Dial drops HF safetensors; **not** ready now |

**Install names:** `git clone https://github.com/Fannovel16/ComfyUI-Frame-Interpolation` → `ComfyUI/custom_nodes/` (+ Windows `install.bat`). Models: pack auto/`ckpts/rife/*.pth` **or** HF `Comfy-Org/frame_interpolation` → `models/frame_interpolation/`. Practical-RIFE author default for most scenes = **4.25** (4.24+ noted good for diffusion post); live HAVE = **rife47** (older anime-leaning line) — fair cell may stay on 47 for zero-install, or Dial adds 4.25/4.26 on exact GO (one-axis weight swap).

**Verified path (AlienPc read-only 2026-10-06 ~1:57 CT):** live `:8189` = `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` (NODDV+ck argv) · CFI = **HAVE** · `…\ckpts\rife\rife47.pth` = **HAVE** · FILM ckpt = **missing** · native FI weights = **missing**.

## Peel / motion quality risk (gen@8 or @12 → interp→24 vs native 24)

| Risk | Evidence | Status for Max KEEP |
|---|---|---|
| **Ghosting / trailing / warp** on limbs, fabric, contact | Practical-RIFE issues (e.g. ghosting/trailing on clothing/arms); RIFE ECCV flow limits | **Likely** @8 (3×) > @12 (2×) |
| **Smear / frame-blend** when displace ≫ flow | FILM paper: large motion → blurry/disocclusion fail on prior methods; RIFE users report blend on fast move | **Likely** peel/fabric |
| **False-smooth hides Motion breaks** | Interp invents in-betweens; Integrity can look “OK” while gen was choppy | **Method risk** — eyes vs R0 required |
| **ID melt / contact smear** | **NO_DATA** on H3 REF2VA KEEP path | Label + freeze Cond |
| **Audio / A/V** | H3 length = frames **at 24fps**; AV joint denoise. VFI is **video-only** — fewer gen frames ⇒ shorter/different audio; community RIFE delivery keeps native audio clock | **HIGH product risk** — fair cell must lock audio policy (native short vs stretch vs mute compare) |
| **H3 “thinks” higher speed** | Reddit low-FPS H3: half duration @24 latent then save as 12fps may add motion blur | **OPEN** — cite community, not official |

**Official:** open weights generate **24fps**; `length` = frame count at 24fps (124≈5s). There is **no** documented H3 fps widget — “gen@8/12” = fewer frames on **17k+5** grid, then VFI up to 24 playback. Apples: same wall-clock ≈5s ⇒ ~39f@8 / ~56–73f@12 / 124f@24 (snap to grid).

## Fair-cell recipe stub (for Dial Plan · one axis = fps/interp)

| ID | Gen frames (≈5s honesty) | Post | Out |
|----|--------------------------|------|-----|
| **R0** | 124 @ native 24 | none | baseline SoT |
| **R12** | ~56–73 (12fps semantics) | RIFE VFI **2×** → ~24 | **preferred hack** |
| **R8** | ~39 (8fps semantics) | RIFE VFI **3×** → ~24 | stress arm |
| **R12F** | same as R12 | FILM VFI 2× | only after FILM ckpt install |

**Freeze:** host `:8189` argv · Cond/prompt · ST8+`simple` · canvas (name 480×864 preview **or** 768×1344) · seed set (≥3 shared uncached) · REF2VA weights. **Do not** change: steps/scheduler/attn/NODDV this cell. **Audio:** declare policy before queue. **KEEP:** Derrick eyes only. Gate line: `GO RIFE fair` (optional `GO RIFE fair 768`).

## Recommend
1. **Default node:** CFI **RIFE VFI** + existing **`rife47.pth`** (zero install).  
2. **Default fps axis start:** **12 → 2× → 24** (lower hallucination load than 8→3×).  
3. FILM / RIFE-4.25+ / native Comfy-Org weights = **optional follow-on** after R12 lands — not blockers.  
4. Do **not** treat wall-cut as quality-neutral until R0 eyes pass peel/fabric/ID.

## Sources (≥3 primaries)
1. Comfy MiniMax H3 guide — native **24fps**, length @24fps — https://docs.comfy.org/tutorials/video/minimax/minimax-h3  
2. MiniMaxH3ReferenceToVideo — `length` frame count at 24fps — https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo  
3. Fannovel16 ComfyUI-Frame-Interpolation README — RIFE VFI 4.0–4.9 + FILM VFI — https://github.com/Fannovel16/ComfyUI-Frame-Interpolation  
4. Practical-RIFE README — 4.24+ for diffusion post; default **4.25** — https://github.com/hzwer/Practical-RIFE  
5. FILM ECCV’22 / arXiv — large motion + disocclusion / Gram sharpness — https://arxiv.org/abs/2202.04901 · https://github.com/google-research/frame-interpolation  
6. Comfy-Org frame_interpolation HF — native RIFE/FILM safetensors — https://huggingface.co/Comfy-Org/frame_interpolation  
7. ComfyUI core Frame Interpolate (CORE-29) — https://github.com/Comfy-Org/ComfyUI/commit/db85cf03ff33f5be09d02f2a52334971209d25d5  

**NO_DATA:** Max KEEP peel A/B for low-FPS+VFI; FILM ckpt on :8189; whether rife47 ≪ 4.25 for this Cond.
