# Remacri vs native NVIDIA upscale — 2026-10-05

**Ask:** Remacri or our native NVIDIA stuff?
**Recommend:** Remacri for the export arm after a native ~768 survivor. NVIDIA NVENC is the encode, not the upscale. RTX VSR is an optional A/B arm, not a swap.
**Not a standing fact.**

## TLDR

1. Remacri = post enlarge for display size. Keep it after a native that already looks right.
2. NVENC = H.264 write. It is not an upscaler.
3. RTX Video Super Resolution = temporal enlarge node already cataloged; not A/B'd better than Remacri on these contact clips.
4. Neither fixes mushy hands or contact. That is generate.
5. Fix Remacri: one Lanczos after 4× (`downscale_ratio=1`), not double resample.

## Sources

- `/workspace/cos/research/2026-10-02-upscale-remacri-vs-nvidia.md`
- `/workspace/cos/research/2026-10-02-remacri-settings-check.md`
- `/workspace/cos/research/2026-10-02-free-video-upscalers.md`
