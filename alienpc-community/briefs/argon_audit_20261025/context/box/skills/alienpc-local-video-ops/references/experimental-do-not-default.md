# EXPERIMENTAL / DO NOT DEFAULT (park until Derrick GO + fair A/B)

These paths are **not** production defaults. Do not auto-invoke or promote into KEEP without exact Derrick GO and a fair evidence pack.

| Path | Status | Why parked |
|------|--------|------------|
| Turbo beta6 int8 (`10Eros_Max_h3_8stepTURBO_beta6_int8`) | **KEEP (production, Derrick 2026-10-09)** | Euler · 8 steps · shift 10; tests 6 steps + RIFE 20 |
| Non-Turbo beta / 25 steps | Optional quality A/B only | Former Oct 2 KEEP; not default |
| Lightning / EasyCache / Spectrum | DROP | Speed matrix — not promoted; Integrity risk |
| STEPS-20 | DROP | Faster wall, Integrity under-denoise |
| SPARSEsol | DROP | Activated but slower vs KEEP |
| Sage attention | Skipped | Not in production argv |
| fp8 | DROP | HostBuffer 1450 / kitchen float8. Old "DynVRAM peel DROP / NODDV KEEP" (superseded 2026-10-09: dynamic VRAM ON is KEEP) |
| Dynamic VRAM ON | KEEP (production default, Derrick 2026-10-09) | Oct 8: cold first run 116.2s → 44.1s, hot unchanged. Old "HOLD until AIMDO ≥2 TECH" (superseded 2026-10-09: dynamic VRAM ON is KEEP). If WinError 1450 / paging-file errors return, disable dynamic VRAM for that single cell and log it. REVALIDATE after rebuild. |
| SaveH3Embedding / Qwen→embedding ID lock | Parked fair A/B | Community node; only after prose six-section locks fail; Shell required |
| RefMods (malcolmrey) adapters | Parked | Separate product from REF2VA; not tenowg node |
| Dual Shell Dial+CoS on AlienPc | FORBIDDEN | CAPA wedge 2026-10-02 — single lease only |
| flux1-fill / Fill | STOPPED | Do not install or smoke |
| Official FLUX.2 klein 9B (BFL) | BLOCKED | HF 403 until license |
| WAN I2V | Deferred | Not production SoT |
| Z-Image / Qwen as production stills crown | Parked | Non-primary for hard pose unlock |

**KEEP stays:** beta6 int8 Turbo + Euler + **8 steps** + shift 10 + dynamic VRAM ON + no-fp8 + `--use-ck-attention` + ComfyUI 0.38.x pinned + REF2VA match. Tests: 6 steps + RIFE 20. All defaults REVALIDATE after rebuild.

Grok Bot skill format has **no** `disable-model-invocation` frontmatter (Cursor-only). Experimental = this body mark + require Derrick GO — do not invent Cursor fields.
