# Flux Kontext anatomy unlock prompt — 2026-10-02 (~06:58 CT)

**Scope:** Rewrite Pass A wardrobe-unlock INSTRUCT so AlienPc Flux Kontext stills show **explicit adult anatomy under removed fabric** (erect penis, vulva/pussy, penetrative rear join) — not vague “bare skin / fill mask.” Adults 21+ fiction. **No smoke** this turn.  
**Cond target:** doggy Cond (woman all-fours, man behind, dual waist grip, white thigh-high boots). Stack: Flux Kontext `:8189`; optional `clothes_remover` LoRA; single-latent CAPA (P182).  
**Prior fail lineage:** P179–P186 (see audit + CAPAs below).

---

## 1) Why P179–P186 failed (prompt axis)

| Cell | Paste pattern | Bot outcome | Mechanism |
|------|---------------|-------------|-----------|
| P179–P181 | Remove named garments + “clear rear penetrative contact” mega; **garment nouns in NEG** | Clothes snap-back 9/9 | Garment-token leak + multi-goal + Dev clothes-lock ([audit 2026-10-01](FLUX_KONTEXT_WARDROBE_UNLOCK_PROMPT_AUDIT_2026-10-01.md)) |
| P183 | Bottom-only remove → “bare at pelvis” | Woman bare; **top also stripped**; briefs residual on some seeds | “Bare skin” under-specifies replacement; LoRA broad |
| P184 | `remove clothes` + briefs → continuous bare skin | Briefs clear **1/3**; no anatomy named | Bare-skin fill ≠ genitals |
| P185 | Tight mask + LoRA@0.50; remove briefs → bare | Briefs residual 2/3; shadow fake | Same under-spec + ReferenceLatent fabric lock |
| P186B | **“Fill masked region with continuous bare skin”** only | Briefs/dark fabric all 3 | Classic FAIL mode: empty/skin continuity without naming **what anatomy replaces fabric** |

**Root (prompt):** Community undress LoRAs train **remove garment → expose named anatomy** (`breasts`, `vagina`, `penis`). Saying only “bare skin / continuous skin” leaves the model free to redraw fabric, shadow, or barbie-smooth crotch. Derrick’s correction (t493): *you must specify what is below.*

---

## 2) Research findings (5 cites)

1. **CivArchive — FLUX KONTEXT REMOVE CLOTHES LoRA captions**  
   Working captions **name genitals in the positive after-remove clause**: e.g. *“Completely remove the subjects clothes. … expose her … clean shaven vagina. Maintain identical camera angle… The rest of the image remains the same, only remove her clothes to expose her naked body.”* Name the garment once for consistency (`white crop-top and jean shorts`).  
   https://civarchive.com/tensorart/models/883573373693599330/versions/883573373693599330

2. **BFL — Working Without Negative Prompts**  
   Flux does not support NEG the way SD does; naming exclusions often **generates** them. Prefer positive replacement: *“without clothes” → “bare skin / natural form”* — and for unlock, go further: name the **visible anatomy** that occupies the space, not only “bare.” Ban garment nouns in NEG.  
   https://docs.bfl.ml/guides/prompting_guide_t2i_negative

3. **r/StableDiffusion — Flux Kontext Dev NSFW limits**  
   Base Dev resists undress / genital edits without NSFW LoRA + explicit prompt. Workarounds: intermediate denoise prompt + LoRA strength; *“change her shirt to her naked body”*; clothes-remover LoRA. Barbie-smooth / panties re-draw are expected failure modes.  
   https://www.reddit.com/r/StableDiffusion/comments/1llpsk1/flux_kontext_dev_can_not_do_nfw/

4. **Getphat FLUX Reality NSFW (HF) — doggy / vaginal sex templates**  
   Explicit positive tags/clauses: *doggystyle, vaginal sex, pussy, erect/big veiny penis, penis, hetero*; doggy example names **pussy + penis** in the same natural-language scene. Euphemism (“from behind”) without anatomy under-delivers.  
   https://huggingface.co/Jonjew/GetphatFLUXRealityNSFW/blob/main/README.md

5. **Fuser / Comfy Kontext grammar + prior AlienPc audit**  
   Specific verb + part (*Remove/Change [garment]*), mandatory preserve clause, one primary edit per pass preferred; our prior audit still bans garment nouns in NEG and mega undress+contact when possible — **but** undress captions that *replace fabric with named anatomy/join* are the supported Pass A pattern when Derrick requires genitals visible under fabric.  
   https://fuser.studio/articles/flux-kontext-editing-guide · local `FLUX_KONTEXT_WARDROBE_UNLOCK_PROMPT_AUDIT_2026-10-01.md`

**Extra pattern (celebdeep / TensorArt undress guides, search-indexed):** *“Completely remove the subject’s [exact garment]. … expose her [breasts/vagina]. Maintain identical… only remove … to expose …”* — detail beats vague “nude.”

---

## 3) Design rules for P188 Pass A paste

1. **Remove bottoms once** (name color/type once in the remove sentence only). Do **not** repeat garment nouns in LOCKED or NEG.  
2. **Positive replacement = anatomy**, not “bare skin alone”: erect penis; vaginal penetration / penis in pussy; bare labia/vulva visible at the join.  
3. **Preserve** faces, hair, skin tone, all-fours doggy, dual waist-grip, white thigh-high boots, warm bedroom light, framing, medium two-shot.  
4. **NEG:** pose residues + identity/safety/diptych only — **zero** bikini/briefs/underwear/fabric tokens.  
5. **Optional LoRA:** prepend trigger `remove clothes.` only when `clothes_remover` is loaded; else omit.  
6. **Graph (when smoked later):** single-latent CAPA; lower pelvis mask; clothes_remover optional ≤0.90; **no** NSFW_MASTER on unlock; Fill UNET still missing on TR — do not fake Fill.  
7. **Pass B** (later): flush hip-seam / contact reinforce **after** Bot affirms anatomy visible — not another “bare skin” cell.

---

## 4) Canonical paste (P188)

See Desktop pack: `/workspace/FAIR_FLUX_P188_ANATOMY_UNLOCK_PROMPT/`

### INSTRUCT (primary)
```text
Completely remove the woman's rhinestone micro-bikini bottom and the man's dark briefs. Under that fabric show explicit adult anatomy: the man's erect penis penetrating the woman's vagina from behind (penis in pussy), with her bare labia and vulva visible at the join and his bare pelvis with no briefs. Preserve exact facial features, hair, skin tone, all-fours doggy pose, dual waist-grip hand placement, white thigh-high boots, warm bedroom doorway light, camera angle, framing, and medium two-shot. The rest of the image remains the same; only remove those two garments to expose the erect penis, bare vulva, and penetrative rear join. Adults 21+ fiction. No text, watermark, diptych, or face swap.
```

### LOCKED_POS
```text
erect penis in pussy; vaginal penetration from behind; bare labia and vulva visible at hip join; man's bare pelvis; woman's bare pelvis; all-fours doggy; dual waist grip; white thigh-high boots; bedroom doorway light; medium two-shot.
```

### NEG (zero garment nouns)
```text
standing pose, standing rear, hair pull, hair grip, hand in hair, face drift, identity drift, plastic skin, waxy skin, barbie smooth crotch, mosaics, censor bar, diptych, split panel, collage, text, watermark, child, minor, teen, underage, 8k, masterpiece, ReActor, extra people, blurry, deformed
```

### INSTRUCT_SHORT (token-budget / LoRA cell)
```text
remove clothes. Completely remove the bikini bottom and the briefs. Show the man's erect penis penetrating her vagina from behind, bare labia and vulva visible at the join. Keep faces, hair, doggy pose, waist grip, boots, light, and framing identical.
```

### INSTRUCT_LORA (when clothes_remover loaded @0.7–1.0)
```text
remove clothes. Completely remove the woman's rhinestone micro-bikini bottom and the man's dark briefs. She and he are now bare at the pelvis: erect penis penetrating her vagina from behind, penis in pussy, bare labia and vulva visible at the join. Maintain identical facial features, hair, all-fours doggy pose, dual waist-grip, white thigh-high boots, camera angle, framing, and perspective. The rest of the image remains the same, only remove those garments to expose the erect penis, bare vulva, and penetrative rear join. Adults 21+ fiction.
```

---

## 5) Diff vs last failed pastes

| | P186B (FAIL) | P188 (this) |
|--|--------------|-------------|
| Replacement | continuous bare skin | erect penis + vagina/pussy + labia/vulva + penetrative join |
| Garment in INSTRUCT | none (Fill language) | named **once** in remove clause |
| Garment in NEG | none | none |
| Anatomy words | none | required positive locks |

---

## 6) Skill patch note

`alienpc-stills-pose-edit-prompting`: **Unlock must name anatomy under fabric; “bare skin alone” is a FAIL mode** (shadow crotch / fabric residual / barbie smooth). Cite this doc + CAPA_P184/P185/P186.

---

## 7) Bottom line

P179–P186 chased remove/fill without telling Kontext **what genitals and join replace the fabric**. Community undress captions and NSFW Flux templates succeed when POS says **expose vagina / erect penis / penis in pussy**. P188 paste does that; NEG stays garment-free; smoke only on Derrick GO (not this turn).
