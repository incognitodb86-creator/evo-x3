# Flux stills host table (:8189)

| Host | Role | Status (local) |
|------|------|----------------|
| **Flux.1 Kontext** (`flux1-dev-kontext_fp8_scaled`) | Current treadmill · pose / face / wardrobe CAPAs | HAVE · proven TECH (P157/P176/P177) · QUALITY often <0.95 |
| **FLUX.2 [klein] 4B distilled FP8** | TECH OK · **QUALITY FAIL** unlock (P163+P188 2026-10-02) | HAVE · fabric residual / no bare join · keep as VRAM-safe fallback |
| **FLUX-KLEIN-9B-FP8-NSFW** (community) | Optional NSFW A/B if 4B under-delivers anatomy | HAVE |
| **FLUX.2 klein community NSFW 9B FP8** | **Default next unlock smoke** after Derrick GO 9B | HAVE · `FLUX-KLEIN-9B-FP8-NSFW` + TE `qwen_3_8b_fp8mixed` + `flux2-vae` · YES-with-knobs on 5070 Ti |
| **FLUX.2 klein 9B official FP8** | Prefer after BFL gate accept | BLOCKED (HF 403) until license |
| **flux1-fill / Fill** | — | **STOPPED** — do not install or smoke |
| Qwen Image Edit / Z-Image polish | Parked / non-primary for hard pose | Do not crown as production stills |

Cite: `/workspace/cos/status/ce-plan-flux2-alienpc-2026-10-02.md` · research stamp `2026-10-02-flux2-max-skill-research.md`.
