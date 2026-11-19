# Stills unlock CAPA detail (Kontext / Flux2)

## Flux unlock NEG wiring (CAPA 2026-10-01)
Wardrobe unlock: real `CLIPTextEncode(NEG)` → KSampler.negative. **Ban** `ConditioningZeroOut`. POS = INSTRUCT + Target scene + LOCKED. Cite `CAPA_FLUX_NEG_ZEROOUT_2026-10-01.md`.

## Act-first unlock POS (LOCKED 2026-10-02)
**Ban remove-clothes theater** as the lead for Flux.2 / Kontext unlock INSTRUCT.
P188 / Klein **4B** paste opened with “Completely remove [garments]…” then named anatomy → fabric residual, no bare join (Bot FAIL).
**Do:** lead with the **penetrative sex act** (erect penis in pussy from behind, wet labia around shaft, bare hip join, dual waist grip, doggy); clothes = **short ban only** (`no bikini bottom, no briefs`); preserve identity/pose/boots/light/framing; Adults 21+; real NEG (no ZeroOut; zero garment nouns in NEG).
Cite pack `/workspace/FAIR_FLUX2_ACTFIRST_UNLOCK_PROMPT/` · smoke `FAIR_FLUX2_KLEIN9B_P163_ACTFIRST_2026-10-02`.

## Flux wardrobe unlock Pass A→B (2026-10-01 / anatomy CAPA 2026-10-02)
**Ban:** garment nouns in NEG; mega INSTRUCT without anatomy replacement; NSFW_MASTER as clothes-remove; mask alone while prompt emits fabric; **“bare skin / continuous skin / fill mask” alone as unlock POS** (P184–P186 FAIL mode → fabric residual, shadow crotch, or barbie-smooth).
**HARD — Unlock must name anatomy under fabric:** Pass A POS must positively specify what replaces the removed bottoms — e.g. erect penis, vagina/pussy, bare labia/vulva at join, penetrative rear join (penis in pussy). Community undress LoRA captions expose named genitals after remove; vague bare-skin language is under-specified. Cite `FLUX_KONTEXT_ANATOMY_UNLOCK_PROMPT_2026-10-02.md` + pack `FAIR_FLUX_P188_ANATOMY_UNLOCK_PROMPT/`.
**Pass A:** Remove [named bottoms once] → **expose named anatomy** (not bare-skin-only). NEG zero garment nouns. Lower mask. Optional clothes-remove LoRA @0.7–1.0 with trigger. Prefer P188 paste.
**Pass B:** only after Bot affirms anatomy visible (erect penis + vulva/labia + penetrative join). Optional NSFW_MASTER ≤0.45. Max HOLD until unlock PASS.

## Kontext unlock mask path (CAPA P182)
**Ban** hybrid ReferenceLatent(full VAEEncode) + KSampler←VAEEncodeForInpaint. **Do:** one latent Scale→VAEEncode→ReferenceLatent→same latent (+ optional SetLatentNoiseMask). Cite `CAPA_P182_MASK_FOG_REFERENCE_LATENT_2026-10-01.md`.

## Briefs-only reinforce (CAPA P184 2026-10-02)
After P183 near-miss (woman pelvis bare; man briefs residual; Cond already topless):
**Ban:** scoring KEEP-top on topless Cond; wide lower mask + clothes_remover@0.90 + `remove clothes` labeled briefs-only (2/3 kept briefs; top stays gone).
**Do:** Max unlock gate = **bare hip-join**. If Bot affirms (e.g. P184 s01), offer Derrick crown → Pass B. Briefs residual: man-crotch-only tight mask; drop LoRA or ≤0.55; or Flux Fill man-briefs ROI. Restore top only from Cond that still has top (P163 trunk). Cite `CAPA_P184_BRIEFS_REINFORCE_2026-10-02.md`.

## Contact reinforce (after pose PASS, contact soft)
Cond = pose-PASS BEST. Strengthen rear penetrative contact; same AR; ≥3 seeds. Stall ~0.78–0.82 → change graph/adapter, not another same reinforce.
