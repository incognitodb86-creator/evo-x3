# TenStrip / 10Eros-Max — author preferred local upscale path?

**Date:** 2026-10-06 (CT scrape)  
**Owner:** Max Research  
**Question:** Does TenStrip (Civitai/CivArchive 2851079, HF TenStrip/10Eros-Max, PromptHero mirror, HF Stuubs) name a preferred **local** upscale path (node and/or model) for MiniMax-H3 / 10Eros-Max outputs?

## ANSWER

**NO_DATA** — author does **not** name a preferred local upscale path (SeedVR / Remacri / ESRGAN / Ultimate SD / pixel SR / named post-process enlarge).

Do not treat community SeedVR2 / Remacri / MMH3-UltimateUpscale / H3 HIGHLY ORGANIZED WORKFLOW as TenStrip author advice.

## Primary sources checked

| Source | URL | Page date / last-updated |
|---|---|---|
| HF author README | https://huggingface.co/TenStrip/10Eros-Max (raw README.md) | scrape 2026-10-06; no upscale section |
| CivArchive card id 2851079 beta5 | https://civarchive.com/models/2851079?modelVersionId=3294059 | Created 2026-09-07 · Updated 2026-10-06 |
| PromptHero mirror | https://prompthero.com/ai-models/h3-eros-max-2851079-download/h3-eros-max-beta5 | Updated October 6, 2026 |
| HF Stuubs (community, not author) | https://huggingface.co/Stuubs/10eros_Max_Ref2va | scrape 2026-10-06 — quant/ref2va only |
| Official MiniMax-H3 (context only) | https://huggingface.co/MiniMaxAI/MiniMax-H3 | scrape 2026-10-06 |
| Secondary (kombitz) | https://www.kombitz.com/2026/09/07/10eros-max-the-new-minimax-h3-model/ | 2026-09-07 — no upscale path |

## Exact author wording (closest hits)

### 1) Model card — resolution smear, not an upscaler recipe
CivArchive / PromptHero (TenStrip description), Known quirks:

> Low resolution detail smearing - Some finger digits and fine motion will smear more at low resolution, also a problem in base model. As memory use gets more efficient increase resolution or work on the composition to get around it.

**Interpretation:** raise native gen resolution / composition — **not** a named post-process upscale node/model.

### 2) Author comment — turbo-look mitigation via latent contrast (not preferred 2K path)
CivArchive comments, **tenstrip**, 2026-09-13:

> For the turbo look mitigation you can use a sampler like LCM/simple 6-8 steps or use the latent contrast node from https://github.com/Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler and reduce to 0.85 to preserve the norms from the turbo which eliminates that.

**Interpretation:** points at Tr1dae pack for **turbo look / latent contrast**, not a preferred local enlarge/2K upscale path for finished outputs. Still **NO_DATA** for author-preferred upscale path.

### 3) HF TenStrip/10Eros-Max README
Sampling setups only (`er_sde/beta`, `res_multistep/simple`, `LCM/simple`, etc.). **Zero** hits for: upscale, 2K, SeedVR, Remacri, ESRGAN, Ultimate SD, latent upscale, post-process enlarge.

### 4) Stuubs/10eros_Max_Ref2va
Explicit community quant of TenStrip weights. No upscale guidance. Not author.

## Official MiniMax context (not TenStrip; confirms Dial prior)

From MiniMax-H3 README:

> The shorter side is set to 768 pixels by default. 2K generation can be achieved with H3-Regenerate-2K  
> H3-Base: … producing results at 768p resolution.  
> H3-Regenerate-2K: … regenerate the output at 2K resolution. … **Due to the complexity of the system, this module is not yet open-sourced.**

Hosted 2K ≠ open-weight local native. Aligns with Dial: official ~768 short edge; hosted Regenerate-2K.

## Explicitly NOT author advice (community only)

- SeedVR2 / RTX VSR workflows on Civitai — third-party
- Remacri / ESRGAN still upscalers — unrelated cards
- “(Simple Workflow) MiniMax H3 — 10Eros + Semantic Bridge + Ultimate Upscale” — third-party graph using H3 3D latent upscaler
- CivArchive “H3 HIGHLY ORGANIZED WORKFLOW” (uses 10Eros Max + MinimaxH3LatentUpscaler3D) — **not** authored by TenStrip

## Dial handoff (3 lines)

1. **NO_DATA** — TenStrip does not name a preferred local upscale node/model on HF / CivArchive 2851079 / PromptHero.  
2. Closest author text: “increase resolution” for low-res smear + Sep 13 comment on Tr1dae **latent contrast 0.85** for turbo-look (not 2K enlarge).  
3. Keep Dial priors: native ~768 short edge; hosted H3-Regenerate-2K; community SeedVR2/RTX ≠ author; LTX spatial upscaler not for Max.

## Method

WebSearch + WebFetch + curl of primary README/card pages on 2026-10-06 CT. No room/Dial message from this stamp.
c145a9933c9209faabfaec947c921a853213745574c56fbfb02c47c3817b8374  /workspace/cos/research/2026-10-06-tenstrip-author-upscale-path.md
