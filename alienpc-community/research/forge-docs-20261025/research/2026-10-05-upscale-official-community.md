# Upscaling — official vs community — 2026-10-05

**Ask:** What do official guidance and community say about upscaling?
**Scope:** MiniMax-H3 / Max I2V. Pages opened: Comfy H3 tutorial, Comfy SeedVR2. Local community notes already cited. Not a standing fact.

## TLDR

1. **Official Comfy H3:** generate at native ~768 short edge (~1 MP). Frames above that do not hold detail. Soft = resolution first. For 2K, generate native then upscale in a **separate** pass.
2. **Official MiniMax:** open weights default short edge 768. Hosted 2K is a regenerate path, not open-weight native.
3. **Official SeedVR2 (Comfy):** one-step diffusion restore/upscale; conservative; temporal for video. Separate product from H3 generate.
4. **Community:** Remacri = enlarge/export arm; RTX VSR = faster temporal enlarge; SeedVR2 = sharper but can redraw. Reddit H3 threads: SeedVR2 quality, RTX speed, latent LTX upscale worse than native.
5. **Neither Remacri nor VSR invent anatomy.** Soft hands stay a generate problem.
6. **Recommend:** native ~768 first; Remacri after survivor for display size; SeedVR2 only as a later A/B if Remacri loses and redraw risk is accepted.

## Official (opened)

Comfy MiniMax H3 (`https://docs.comfy.org/tutorials/video/minimax/minimax-h3`):
- Open weights: 768 short edge, ~1 MP, 24 fps, ~15 s.
- Full quality 16:9: 1344×768 (0.98 MP). Skip 1.0 MP over area cap.
- "Frames well above the native canvas do not hold detail… a later upscaling pass cannot recover what the generation step left out."
- "For 2K output, generate at the native canvas and upscale in a separate pass."
- "Steps do not add sharpness the native canvas cannot resolve, so a soft frame is a resolution problem first."

Comfy SeedVR2 (`https://docs.comfy.org/tutorials/utility/seedvr2`):
- One-step diffusion restoration/upscale from ByteDance Seed.
- "Conservative upscaling: preserves original structure and detail while enhancing clarity."
- Image and video templates. Not part of the H3 generate graph.

## Community (local notes + prior opens)

| Source | Says |
|--------|------|
| Free upscalers note 2026-10-02 | Stay on Remacri for enlarge. RTX VSR present, not proven better. SeedVR2 **disk-installed 2026-10-06** (NumZ node + 3B FP8); Comfy restart pending idle; redraw risk on contact still applies. |
| Remacri vs NVIDIA 2026-10-02 | Remacri is mid CUDA export arm, not a scored win over VSR. NVENC = encode only. |
| Reddit H3 upscale cmp (cited in that note) | SeedVR2 = quality rumor; RTX = speed; do not drop Remacri for silence. |
| Civitai low-VRAM H3 packs | Often generate 864×480 for VRAM; that is preview, not upscale advice. |

## Recommend for our stack

1. Generate at official quality canvas (~768 short edge).
2. Remacri after a native survivor for ~1080 export; one Lanczos after 4×.
3. Do not use upscale to fix mushy hands/contact.
4. RTX VSR optional A/B; SeedVR2 only if Remacri loses and redraw is acceptable.

## Sources

- https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- https://docs.comfy.org/tutorials/utility/seedvr2
- `/workspace/cos/research/2026-10-02-free-video-upscalers.md`
- `/workspace/cos/research/2026-10-02-upscale-remacri-vs-nvidia.md`
- `/workspace/cos/research/2026-10-05-max-setup-official-vs-community.md`
