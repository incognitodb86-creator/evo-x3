# Flux Kontext wardrobe-unlock prompt audit — 2026-10-01

**Scope:** Why P179/P180/P181 clothes snap-back (9/9 Bot vision) on AlienPc despite fixed NEG+LOCKED, real CLIPTextEncode NEG, NSFW_MASTER@0.40 (P180), geometric lower mask (P181). Cond = clothed doggy P163 BEST. Adults 21+ fiction only.  
**Method:** WebSearch + WebFetch (ComfyUI docs, BFL negative-prompt guide, ComfyUI Wiki, Fuser Kontext guide Jun–Sep 2026, CivArchive undress LoRAs, 9elements Fill+Redux Mar 2025, prior `RESEARCH_FLUX_KONTEXT_OPTIMIZE_2026-10-01.md`).  
**No smoke run** — research + paste drafts only.

---

## 1) What we used (failed paste)

### INSTRUCT (exact)
```text
Change the reference so the rhinestone micro-bikini bottom is removed and the man's dark briefs are fully down or off, leaving both adults bare at the pelvis with clear rear penetrative contact visible at the hip seam (not fabric-covered). Keep the same all-fours doggy pose, dual waist-grip with no hair-pull, white thigh-high boots if present, warm bedroom doorway light, framing, and both adults' facial identity, hair, and skin. One medium two-shot. No text, watermark, diptych, or face swap.
```

### LOCKED_POS
```text
bare from the waist down (no bikini bottom); briefs fully down or off; pelvis flush penetrative contact; doggy dual waist grip; bedroom.
```

### NEG
```text
rhinestone bikini bottom, micro-bikini covering pussy, lingerie blocking seam, dark briefs covering penis, underwear on, fabric over genitals, clothes between bodies, dry hump through fabric, standing pose, standing rear, hair pull, hair grip, hand in hair, face drift, identity drift, plastic skin, waxy skin, diptych, split panel, text, watermark, child, minor, teen, underage, 8k, masterpiece, ReActor
```

### Graph CAPA (post-audit)
| Cell | Change vs prior |
|------|-----------------|
| POS | INSTRUCT + Target scene + LOCKED |
| NEG | real CLIPTextEncode (not ZeroOut) |
| P180 | NSFW_MASTER_FLUX @ 0.40 |
| P181 | geometric lower mask |
| Cond | clothed doggy P163 BEST |

### Result
**Clothes snap-back 9/9** (Bot vision). Wardrobe unlock FAIL despite NEG/LOCKED/graph fixes.

---

## 2) What failed (symptom → mechanism)

| Symptom | Likely mechanism (evidence) |
|---------|------------------------------|
| Pelvic garments redraw / persist | **Clothes-lock / Cond fidelity:** Kontext is trained to preserve reference context; clothed P163 Cond is a strong prior. Dev has NSFW mitigations that resist bare pelvis (community: r/StableDiffusion “Flux Kontext Dev can not do N*FW”). |
| Fixing NEG did not help | **Flux negation is weak / harmful:** BFL official: Flux models don’t support negative prompts; naming unwanted concepts often *generates* them ([BFL Working Without Negative Prompts](https://docs.bfl.ml/guides/prompting_guide_t2i_negative)). Listing `rhinestone bikini bottom`, `dark briefs…` in NEG is a garment-token leak path. |
| Naming garments in INSTRUCT | **Re-draw tokens:** Community undress LoRA authors: specify garment *once* for removal, then describe **positive replacement** (bare skin). Long “remove X / keep Y / also contact” prompts re-attend to fabric nouns. |
| Undress + penetrative contact same pass | **Multi-goal competition:** Official Comfy + our prior research: **one change per pass**; step-by-step (outer→inner→bare, then contact). Contact+undress asks the model to invent anatomy *and* fight Cond fabric simultaneously → defaults to fabric. |
| KEEP boots / pose / grip / light / both faces | **Preserve clause overload + wardrobe continuity:** Preserve is correct for identity, but “keep … boots” + “change bikini/briefs” in one long sentence keeps a *clothed-scene* schema active. |
| NSFW_MASTER@0.40 | **Wrong-tool assist:** Prior AlienPc research: NSFW_MASTER is **Flux-dev** LoRA, optional ≤0.55 after *contact* stall — not a clothes-remove adapter. Will not override Kontext clothes-lock. |
| Geometric lower mask (P181) alone | **Necessary but not sufficient:** Mask helps *localize* edit; if prompt still names fabric + NEG leaks garment tokens + Cond is fully clothed ReferenceLatent, mask region can still synthesize fabric. Face-out-of-mask is correct for identity ([Apatero outfit-swap](https://apatero.com/blog/flux-kontext-outfit-swap-preserve-face)). |
| Real CLIP NEG vs ZeroOut | Correct CAPA for *anatomy/diptych* bans; **not** the wardrobe unlock lever on Flux. |

---

## 3) Research findings (2025–2026 community / official)

### 3.1 Official / Comfy prompt grammar
- **Structure:** `Change/Remove/Replace [specific part]. While preserving [face, hair, pose, framing, lighting, background].` Avoid `Transform the person…` ([ComfyUI Flux Kontext Dev](https://docs.comfy.org/tutorials/flux/flux-1-kontext-dev), [ComfyUI Wiki Jun 2025](https://comfyui-wiki.com/en/tutorial/advanced/image/flux/flux-1-kontext)).
- **One edit per pass;** complex multi-change → step-by-step (clothes first, then action/contact).
- **Token budget:** Wiki cites ~**512 token** prompt ceiling — our INSTRUCT+LOCKED+scene paste is long and dilutes the remove verb.
- **Region language:** Paint/red-frame ROI + `Change the clothing in the red framed area…` (Lilys / Paint Editor recipes, 2026). Dev: semi-transparent ROI mark often beats thin red box.
- **Fuser (Sep 2026):** Say what changes, not full scene; preserve clause is mandatory for identity; branch from clean Cond, don’t over-chain ([Fuser Kontext editing guide](https://fuser.studio/articles/flux-kontext-editing-guide)).

### 3.2 Negation / garment leak
- BFL: `"without clothes"` → prefer **`bare skin` / `natural form`**; do **not** pile garment nouns in NEG ([docs.bfl.ml](https://docs.bfl.ml/guides/prompting_guide_t2i_negative)).
- Production writeups (search-indexed Apatero recipes): Kontext often **ignores NEG**; phrase preservation positively (`Keep face, pose, lighting identical`), not `no underwear`.

### 3.3 Working undress / clothing-removal patterns
| Pattern | What works | Source |
|---------|------------|--------|
| **Short remove + positive bare** | `Completely remove the subject's [exact garment]. … Maintain identical camera angle, framing… The rest of the image remains the same, only remove [garment] to expose bare skin.` | CivArchive / TensorArt Kontext Remove Clothes LoRA captions; celebdeep local undress guide |
| **Name the garment once (color+type)** | `white crop-top and jean shorts` not vague `clothes` | Same LoRA readmes |
| **Trigger + LoRA** | `Remove the clothes.` / `remove clothes` @ weight ~0.7–1.5 on **Kontext-trained** clothes-remove LoRA | CivArchive clothes-remover; anime variant trigger `Remove the clothes.` |
| **Stepwise** | Outer → inner → bare; then contact on bare trunk | Comfy step-by-step; our `RESEARCH_FLUX_KONTEXT_OPTIMIZE` §8.3 |
| **Mask clothing ROI only** | Face/hair/bg outside mask = physical freeze | Apatero outfit-swap; ComfyWiki marking |
| **Fill inpaint (not full Kontext denoise)** | FLUX.1 Fill [dev] + feathered lower mask + crop-stitch; Redux optional for garment *swap* | [HF Fill-dev](https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev); [9elements Redux+Fill Mar 2025](https://9elements.com/blog/ai-clothes-swaps-with-flux-redux-and-flux-fill/) |
| **change_clothes LoRA denoise** | If pose wanders at denoise 1.0, try **~0.90**; ≤0.85 may freeze change | CivArchive Kontext_change_clothes comments |
| **Inpaint anatomy LoRAs** | PussyDiffusion-class: **best on Fill/inpaint**, face drifts in full txt2img; keep face out of mask | CivArchive comments |

### 3.4 Known Kontext clothes-lock / NSFW failure mode
- Dev ships **NSFW/CSAM mitigations**; community reports bare/undress often **re-clothes** or no-ops without a Kontext undress LoRA or Fill path (r/StableDiffusion NSFW threads; LoRA authors train difference pairs clothed→nude).
- **ReferenceLatent / Cond stickiness:** clothed BEST Cond wins when edit is under-specified or multi-goal; “no-change” is a documented Dev failure mode (ComfyUI Wiki).
- **Outfit swap ≠ undress:** Swap-to-another-garment is native-strong; **remove-to-bare** is the harder edit and often needs LoRA or Fill.

### 3.5 Prior AlienPc research alignment
From `RESEARCH_FLUX_KONTEXT_OPTIMIZE_2026-10-01.md` / skill diff:
- Undress = **MED–HIGH** native if stepwise; clothes-remove LoRA only after prompt FAIL.
- NSFW_MASTER = contact assist, **not** wardrobe unlock.
- Ban stacking clothes-remove + change_clothes + RefControl same cell.
- Templates §8.3 already prefer **Remove [named garment], leaving [what remains]** — our failed paste violated stepwise + piled contact into the same instruct.

---

## 4) Prompt WRT diagnosis (our paste)

| Axis | Verdict | Detail |
|------|---------|--------|
| **Length** | FAIL | Single mega-instruct: remove×2 + contact + pose + grip + boots + light + both IDs + shot type. Dilutes remove; near/over soft token budget when concatenated with Target+LOCKED. |
| **Conflicting KEEP clothes** | FAIL-ish | `white thigh-high boots if present` is OK *alone*, but coupled with bikini/briefs nouns keeps “lingerie set” schema. Prefer Pass A: boots only as preserve; **do not** name bottoms except in remove clause once. |
| **Garment names in POS/INSTRUCT** | FAIL | `rhinestone micro-bikini bottom`, `dark briefs` appear as durable visual tokens; model redraws them under Cond pressure. Better: one remove sentence → then **bare pelvis / skin continuity** language without repeating garment nouns. |
| **NEG garment list** | FAIL (likely leak) | Explicit bikini/briefs/underwear/fabric tokens in NEG contradict BFL positive-framing guide; high risk of snap-back. Keep NEG for **pose residues + safety + diptych** only. |
| **Penetrative contact same edit as undress** | FAIL | Two hard edits. Cond is fabric-covered doggy; inventing flush contact *and* removing fabric → model picks fabric (safer prior + mitigation). Split: undress → then contact reinforce on bare Cond. |
| **Kontext clothes-lock mode** | FAIL (expected)** | Clothed P163 ReferenceLatent + Dev mitigations + no Kontext clothes-remove LoRA → 9/9 snap-back matches community “cannot undress” reports. Graph NEG/mask/NSFW_MASTER do not address root. |
| **LOCKED_POS “no bikini bottom”** | FAIL-ish | Negation inside LOCKED (`no bikini bottom`) = same leak pattern. Prefer positive: `bare pelvis, continuous skin at hip seam`. |
| **Graph CAPA** | Partial good | Real NEG encode + lower mask = correct *hygiene*; wrong *primary* levers for wardrobe unlock. |

**Root cause (ranked confidence):**  
1. Multi-goal undress+contact on clothed Cond (high).  
2. Garment-token leak in INSTRUCT/NEG/LOCKED (high).  
3. Dev clothes-lock / NSFW mitigation without undress LoRA or Fill (high).  
4. NSFW_MASTER used as unlock (medium — wrong tool).  
5. Prompt length / preserve overload (medium).

---

## 5) Ranked next levers (evidence cites; no smoke)

| Rank | Lever | Why | Cite |
|------|-------|-----|------|
| **L1** | **Two-pass split:** Pass A = pelvis undress only (short remove + bare-skin POS); Pass B = contact reinforce on Pass-A bare Cond | Official one-edit chaining; our optimize §8.3 / R3 | Comfy docs; RESEARCH_FLUX_KONTEXT_OPTIMIZE |
| **L2** | **Rewrite INSTRUCT/LOCKED/NEG:** strip garment nouns from NEG; positive bare language; remove once; preserve face/pose/boots without re-listing bottoms | BFL negation guide; undress LoRA captions | docs.bfl.ml; CivArchive remove-clothes |
| **L3** | **Lower-ROI mask + Fill or Kontext clothes-remove LoRA** (one adapter only): Fill+feathered pelvis mask OR Kontext undress LoRA @0.7–1.0 with trigger; face outside mask | Fill blends structure; LoRA trained clothed→nude | HF Fill-dev; 9elements; CivArchive; our R6 |
| **L4** | Region prompt: `Change only clothing in the masked / red-framed lower area to bare skin…` | Paint-editor / marking recipes | Lilys; ComfyWiki marking |
| **L5** | If using change_clothes / undress LoRA and pose drifts: denoise **~0.90** fair cell (not ≤0.85 freeze) | CivArchive change_clothes comments | CivArchive 1729159 |
| **L6** | Drop NSFW_MASTER from wardrobe cells; reserve ≤0.4 for **contact** pass after bare Cond exists | Prior AlienPc optimize | RESEARCH_FLUX_KONTEXT_OPTIMIZE |
| **L7** | Optional: Flux Redux garment style only for *swap*; for bare prefer Fill empty-mask fill with bare-skin prompt | 9elements = swap not nude | 9elements Mar 2025 |
| **L8** | Do **not** stack RefControl + undress + NSFW_MASTER | Thrash ban | optimize §6 |

**Top 3 for next fair cell:** **L1 → L2 → L3**.

---

## 6) Exact better paste drafts (research-supported)

Use **Pass A** until Bot vision confirms bare pelvis; only then **Pass B**. Adults 21+ fiction. Cond for A = P163 clothed doggy BEST. Cond for B = Pass A winner.

### Pass A — wardrobe unlock only (no contact invent)

**INSTRUCT:**
```text
Remove the rhinestone micro-bikini bottom and the man's dark briefs completely. Replace that fabric with continuous bare skin at both adults' pelvis and hips. Preserve exact facial features, hair, skin tone, all-fours doggy pose, dual waist-grip hand placement, white thigh-high boots, warm bedroom doorway light, camera angle, framing, and medium two-shot. The rest of the image remains the same. Adults 21+ fiction. No text, watermark, diptych, or face swap.
```

**LOCKED_POS:**
```text
bare pelvis and hips on both adults; continuous skin at the hip seam; all-fours doggy; dual waist grip; white thigh-high boots; bedroom doorway light; medium two-shot.
```

**NEG (no garment nouns):**
```text
standing pose, standing rear, hair pull, hair grip, hand in hair, face drift, identity drift, plastic skin, waxy skin, diptych, split panel, collage, text, watermark, child, minor, teen, underage, 8k, masterpiece, ReActor, extra people
```

**Graph notes for A:** Guidance ~2.5 · CFG 1 · steps 28–30 · EmptySD3 from KontextScale · **lower geometric / painted mask** covering bikini bottom + briefs only · face/hair/boots outside mask · **no NSFW_MASTER** · optional **Kontext clothes-remove LoRA @ 0.8–1.0** with trigger phrase in INSTRUCT if prompt-only fails · alt path: **Flux Fill** same mask + prompt `bare skin continuity at pelvis, no fabric`.

---

### Pass B — contact reinforce on bare Cond (after A PASS)

**INSTRUCT:**
```text
Change only the hip contact so the pelvises are flush with clear rear penetrative contact visible at the hip seam. Preserve exact facial features, hair, skin tone, bare pelvis state, all-fours doggy pose, dual waist-grip, boots, lighting, framing, and medium two-shot. Do not add fabric or underwear. Adults 21+ fiction. No text, watermark, or diptych.
```

**LOCKED_POS:**
```text
bare pelvis; flush rear penetrative contact at hip seam; doggy dual waist grip; boots; bedroom; medium two-shot.
```

**NEG:**
```text
fabric over genitals, clothes between bodies, dry hump through fabric, underwear on, standing pose, hair pull, face drift, identity drift, plastic skin, diptych, split panel, text, watermark, child, minor, teen, underage, 8k, masterpiece, ReActor
```
*(Garment nouns only here as Cond residues after A proved bare — still prefer POS bare language over NEG; drop these if snap-back returns.)*

**Graph notes for B:** Cond = Pass A bare still · optional NSFW_MASTER @ **0.35–0.45** · mask hip-seam ROI only · same Guidance/CFG.

---

### Ultra-short variant (if long INSTRUCT still snaps)

**INSTRUCT_A_SHORT:**
```text
Completely remove the bikini bottom and the briefs. Bare skin at the pelvis only. Keep faces, hair, doggy pose, waist grip, boots, light, and framing identical.
```

**INSTRUCT_A_REGION (if red/mask frame used):**
```text
Change the clothing in the masked lower area to bare skin. Keep faces, hair, pose, boots, lighting, and background unchanged.
```

---

## 7) Sources (key)

1. ComfyUI — Flux Kontext Dev tutorial / prompt techniques: https://docs.comfy.org/tutorials/flux/flux-1-kontext-dev  
2. ComfyUI Wiki — Kontext Dev prompts (updated 2025-06-29): https://comfyui-wiki.com/en/tutorial/advanced/image/flux/flux-1-kontext  
3. BFL — Working Without Negative Prompts: https://docs.bfl.ml/guides/prompting_guide_t2i_negative  
4. Fuser — Kontext editing guide (2026-09-28 runs): https://fuser.studio/articles/flux-kontext-editing-guide  
5. Apatero — Outfit swap preserve face (mask clothing ROI): https://apatero.com/blog/flux-kontext-outfit-swap-preserve-face  
6. 9elements — Flux Redux + Fill clothes swap (2025-03-18): https://9elements.com/blog/ai-clothes-swaps-with-flux-redux-and-flux-fill/  
7. HF — FLUX.1 Fill [dev]: https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev  
8. CivArchive — Kontext remove-clothes / change_clothes LoRA captions + denoise 0.9 tip  
9. Local: `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/RESEARCH_FLUX_KONTEXT_OPTIMIZE_2026-10-01.md`

---

## 8) Bottom line

P179–P181 did not fail because NEG was “unfixed” or ZeroOut lingered. They failed because **(a)** Flux treats garment names in NEG/LOCKED as attractors, **(b)** undress+penetrative contact in one instruct loses to clothed Cond, and **(c)** Dev clothes-lock needs **short positive bare language + lower mask + (if needed) Kontext undress LoRA or Fill**, not NSFW_MASTER. Next fair: **Pass A paste above → vision gate bare → Pass B contact**.
