# RESEARCH — Max / MiniMax-H3 REF2VA **reference images** best practices — 2026-10-02

**When_CT:** 2026-10-02 ~9:25 AM CT (America/Chicago)  
**Owner:** CoS executor (research-only) · **Machine:** AlienPc `:8189` Comfy **0.38** · TenStrip lean REF  
**Ask (Derrick):** Best practice for reference images on Max REF2VA — keep Cond / swap / add better or different photos?  
**Scope:** Official MiniMax + Comfy R2V · local prompt/Plan canon · community character-sheet practice  
**Out of scope:** HostBuffer / DynamicVRAM argv (covered separately) · Dial ping · invent KEEP · auto-score scripts  

**Product lock:** Cond **ORC_BJ** = `/workspace/FAIR_FLUX_ORC_BJ_2026-10-02/inputs/COND_HC3.jpg` (HC3 oral/neon · **1792×1008** · ~0.49 MB) · Goal ~1-min multi-clip after TECH · scripts = thumbs/collage only  

---

## One-liner

**For ORC_BJ S0 / first TECH: KEEP single Cond `COND_HC3.jpg` as the only `ref_image_1`.** Do **not** swap or multi-angle until ≥1 TECH clip lands and human review shows a *specific* identity failure. Extra / “better” photos help only when they add **missing complementary evidence** (profile, wardrobe detail, partner ID) **and** the six-section prompt binds each label — they hurt when they contradict Cond, duplicate it, or inflate ref tokens on a 16 GB HostBuffer-sensitive box.

---

## Recommendation for ORC_BJ probe (keep / swap / add)

| Decision | Verdict | Why |
|----------|---------|-----|
| **KEEP** `COND_HC3.jpg` as sole REF for S0 / re-smoke | **YES — default** | Locked Plan Cond · oral+neon+both subjects+contact already in one frame · TenStrip lean REF = single still OK · local prompting research: “Extra refs: none for S0” |
| **SWAP** Cond for a “prettier” still | **NO** unless Derrick renames Cond | Swap resets identity baseline mid-probe; still pack was TECH scout (~0.94 still score) not KEEP; prettier ≠ ACT continuity |
| **ADD** 2nd+ angle / face crop / partner sheet | **HOLD until post-TECH failure** | Official allows ≤9; community says add only complementary views. On AlienPc Max TURBO-hybrid + AIMDO, every extra image = more ref tokens every step → slower + HostBuffer risk. Escalate one axis after clip review |
| **ADD** `PICK_HC3_neon.jpg` as 2nd ref | **NO** | Same WxH and **identical byte size** as Cond on disk — near/duplicate; ArtArch: near-duplicates weaken the brief |
| **USE video refs** (`ref_videos`) for S0 | **NO** | Motion refs are a later knob (camera/pacing). S0 product is still identity + oral motion from text. Video refs also burn VRAM/tokens |
| **`ref_image_size`** | Prefer **`match`** until ID mid-clip fails | Comfy default; `max` = stronger fidelity but refs ride every step (several× slower). S0 already saw HostBuffer on `max` then `match` — image practice ≠ argv fix, but do not stack `max` + multi-ref while HostBuffer open |

### Practical ladder (after first TECH clip exists)

1. **Human watch** thumbs/collage: Face/ID mid-clip · oral contact hold · wardrobe · neon · motion amp.  
2. If **face drifts on turns / occlusion only** → add **one** complementary still (profile or ¾ face), bind as `<Picture 2>` or cite inside `<Subject 1>` — keep Cond as composition `<Picture 1>`.  
3. If **wardrobe/neon rewrite** → do **not** add a different wardrobe photo; strengthen `fully_preserved` + literal wardrobe/neon in prompt (or regenerate Cond with same act).  
4. If **partner (green male) ID weak** → optional partner-only clear still as separate Subject from `<Picture N>` — only if Cond male is ambiguous.  
5. If **identity OK but motion weak** → prompt/steps/sampler first; **not** more stills.  
6. Multi-clip ~1 min → same Cond (or light FL2VA beat stills) across segments; Multiframe/Add Guide ≥0.34 is timeline anchors, not “more beauty refs.”

---

## Best practices (count, clarity, angle, wardrobe, neon)

### Count & roles (official)

| Rule | Source | Conf. |
|------|--------|-------|
| ≤ **9** reference images · ≤3 videos · ≤3 audio · ≤ **12** mixed files | MiniMax HF Ref2VA · Platform video-generation guide · Comfy `MiniMaxH3ReferenceToVideo` | **High** |
| Image dims API: each side **256–5760**; AR roughly **0.4–2.5** | Platform / Runware H3 docs | **High** (API; Comfy downscales to 2048 short edge, never upscales) |
| Tag by **connection order** 1-based (`<Picture N>` / `<Video N>` / `<Audio N>`) | Comfy R2V tutorial | **High** |
| **Assign each ref a job** in text (identity / style / motion / camera / voice) | Comfy R2V prompting tips | **High** |
| Image alone is **not** a binding — restate appearance in subject_definitions + shots | Official ref-en · ai-muninn dual-character bench | **High** |
| `<Picture N>` = concrete frame/composition anchor; `<Subject N>` = reusable identity unit; cite Picture inside Subject when image is only identity source | Local `MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` | **High** |
| One subject may come from **multiple** assets — state what each provides | Official ref-en §2.1 | **High** |

### Clarity / quality of each still

| Practice | Why | Conf. |
|----------|-----|-------|
| **Subject fills most of the frame** | Reddit R2V: max fidelity when subject occupies most space; portraits for people | **Med-High** |
| **Clear, sharp, uncluttered** — no labels, watermarks, heavy overlays | Comfy + community; overlays become “scene content” | **High** |
| Prefer **≤ ~1–2 MP** useful content under `match`; giant sheets get area-scaled down | Reddit + Comfy `match` = scale to generation pixel area | **Med-High** |
| Cond **1792×1008 (~1.8 MP, ~16:9)** is **in-band** for H3 native ~1 MP canvas — fine; do not upscale | Cond metadata this turn | **High** |
| Crop to target AR yourself when possible (esp. I2VA stretch path); R2V more tolerant of AR mismatch across refs | Reddit thread · Comfy I2V stretch notes | **Med** |
| Neutral background for **identity-only** character sheets (avoid baking unwanted room into scene) | Reddit character-sheet thread · ArtArch | **Med-High** |
| For **act Cond** (ORC_BJ): **keep neon + oral geometry** — that still *is* the scene + contact lock, not a clean sheet | Local Plan / ORC_BJ axes | **High** |

### Angle / multi-view

| Practice | Why | Conf. |
|----------|-----|-------|
| Start **1** strong primary (face+body+act as needed) | Lean TenStrip · S0 Plan · token/VRAM | **High** |
| Complementary set if needed: face close-up · front full · profile/¾ · back — **not** near-duplicates | Reddit · ArtArch · JahJedi sheet guidance | **Med-High** |
| Prefer **separate LoadImage slots** under `match` (each scaled to gen area) vs packing 4 views into one collage that then shrinks | Reddit: match scales total area; collage panels shrink harder | **Med** |
| Under `max` (2048 short edge): layout can pack more info, but **costly every step** — avoid on 16 GB until HostBuffer closed | Comfy tooltip · local CAPA HostBuffer | **High** |
| Profile matters more than a 2nd beauty front shot when failures are **turns / occlusion** | ArtArch continuity article | **Med** |
| Two characters: make them **visually distinct**; bind each image→Subject in text | ai-muninn n=2 bench | **High** |

### Wardrobe match

| Practice | Why | Conf. |
|----------|-----|-------|
| All refs for one Subject must agree on **wardrobe, age cues, hair, accessories** | Conflicting evidence → model averages / invents | **High** (ArtArch + official retention) |
| `fully_preserved` wardrobe in retention_analysis + describe any undress as **motion**, not silent vanish | Local Max prompting research · AUDIT | **High** |
| Do **not** add a “better bikini” photo that differs from Cond mid-probe | Wardrobe teleport / ID fight | **High** |
| Size locks in prose (“petite breasts”) counter Max inflate — stills help only if Cond already shows size | AUDIT §8 · local prompting | **Med-High** |

### Neon / scene

| Practice | Why | Conf. |
|----------|-----|-------|
| ORC_BJ Cond already carries neon — treat as `<Subject>` environment `fully_preserved` | Local prompt pack | **High** |
| Extra “cleaner neon” stills that change fixtures/color can **rewrite** the scene | Same as wardrobe conflict | **Med-High** |
| Identity-only sheets should use **neutral** BG so neon doesn’t fight Cond scene | Reddit character sheets | **Med** |
| Blue-cast / random camera failure modes on Max often = **wrong prompt dialect** (I2VA prose on REF), not missing neon photo | TenStrip · local CAPA | **High** |

### Still vs video refs

| Use | When | Conf. |
|-----|------|-------|
| **Still(s)** | Identity, wardrobe, style, composition anchor | **High** (default for ORC_BJ) |
| **Video ref** | Motion / camera / pacing / edit source (2–15s each, total ≤15s, ≥5 frames) | **High** (official limits) |
| Do not use video ref to “fix” HostBuffer or replace oral motion prose | Wrong tool | **High** |
| Stock Max hybrid may **dilute** per-frame video-ref accuracy vs dedicated Ref2VA builds | Stuubs / exhaustive research | **Med** |

### Prompt + sampling that make images work

| Practice | Source |
|----------|--------|
| Six-section REF dialect; labels stable across sections | Official ref-en |
| Restate look at first appearance in each shot (label ≠ identity) | ai-muninn · official examples |
| `ref_image_size=match` first; `max` only if ID fidelity fails | Comfy R2V |
| Identity-critical: avoid Lightning 4-step on R2V (refs starved); prefer ~20 base / raise ~25 if drift | Comfy tutorial |
| Sampler: `res_multistep` + `beta`/`normal` often better than `simple` on reference-heavy | Comfy R2V tips |
| Cache/spectrum **OFF** on reference shots (TenStrip/AUDIT) | Local AUDIT |
| Wire Autogrow as `ref_images.ref_image_1` on Comfy 0.38 | Local Dial S0 |

---

## When different refs help vs hurt

### Help (add or swap **after** a measured failure)

| Situation | What to add / change | Notes |
|-----------|----------------------|-------|
| Face OK front, fails on **profile / turn** | One clear profile or ¾ still | Bind to same `<Subject 1>`; keep Cond as pose/contact |
| Face OK, **accessory/logo** wrong | One tight crop of that detail | Reddit: detail crop for logos |
| Two people merge / bleed | Separate clear sheets per person + distinct looks + explicit bindings | ai-muninn |
| Need recurring voice | `ref_audio` / video soundtrack — **not** a still | Official |
| Multi-beat ~1 min chain | Same identity Cond across segments; optional Multiframe timestamp stills | Exhaustive Path #1/#3 |
| Pure identity sheet (no act pose) | Neutral BG multi-angle sheet **instead of** cluttered act still — only if product is character lock not act continuity | Community sheets |

### Hurt (do **not** for ORC_BJ now)

| Anti-pattern | Why it hurts |
|--------------|--------------|
| Swap Cond mid-S0 for “better face” | Breaks oral/neon/contact lock; resets fair baseline |
| Duplicate / near-duplicate 2nd photo (`PICK_HC3_neon` twin) | No new evidence; wastes tokens |
| Conflicting wardrobe, hair, age, lighting across refs | Model invents composite person |
| 4-panel collage under **`match`** without need | Each panel shrinks; less face pixels than one clear still |
| Many refs + **`max`** on 16 GB AIMDO | Token×steps cost; HostBuffer / WinError 1450 risk |
| Extra beauty fronts when failure is **motion amp** | Stills don’t write pump motion — prompt/length/steps do |
| Doggy / standing stills as REF on oral Cond | Act teleport |
| Classic I2VA first-frame thinking (“this still = only frame 0”) | REF2VA stills are **who**, not always **when** (unless tagged as Picture composition anchor) |
| Auto-score scripts crowning ID from stills | Scripts = thumbs/collage only (user lock) |

---

## Official + community citations

### Official

| Source | URL / path | Takeaway used |
|--------|------------|---------------|
| MiniMax-H3 README Ref2VA limits | https://huggingface.co/MiniMaxAI/MiniMax-H3 | ≤9 images · ≤3 videos · ≤3 audio · ≤12 mixed |
| Platform video generation guide | https://platform.minimax.io/docs/guides/video-generation | Image size/AR bands · role=reference_image |
| Comfy MiniMax H3 tutorial (R2V tips) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | Tag order · assign jobs · match vs max · Lightning starves refs · res_multistep |
| Comfy `MiniMaxH3ReferenceToVideo` | https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo | ref_image_size · ≤9 · never upscale · tokens every step |
| Official ref-en prompt guide (local) | `…/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` | Picture vs Subject · multi-asset subjects · retention markers |
| HF h3-prompt-writing skill | https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing | Same dialect as local ref-en |

### Community / author

| Source | Takeaway used |
|--------|---------------|
| ai-muninn Ref2VA two-character bench (2026-09) | Restate appearance; binding is text; match default; similar-looking dual untested |
| Reddit r/StableDiffusion H3 ref resolution / character sheets | Subject fill frame; ≤~1–2 MP under match; front/back/close-up enough; collages vs separate slots |
| ArtArch “Character Consistency With Multiple References” | Complementary not duplicate; conflict hurts; check mid-clip not only open |
| JahJedi MiniMax-H3-Character-Sheet (HF) | Neutral equal-scale multi-view documentation sheets |
| TenStrip / 10Eros-Max · Stuubs Ref2VA · local AUDIT / exhaustive | Prefer REF even for one still; hybrid may dilute video-ref; lean S0 |
| Local `2026-10-02-max-h3-prompting-best-practices.md` | Extra refs none for S0; match first; ORC_BJ oral lock |
| Local HostBuffer CAPA | max→match attempted; image practice separate from argv; avoid stacking max+multi-ref |

### Local product facts (this probe)

| Item | Value |
|------|-------|
| Cond | `COND_HC3.jpg` **1792×1008** · oral/neon HC3 |
| Twin on disk | `PICK_HC3_neon.jpg` same size+bytes → do not dual-wire |
| Node | `MiniMaxH3ReferenceToVideo` on `:8189` Comfy **0.38.0** |
| UNET | TenStrip TURBO-hybrid w4a8 lean REF (stock ref2va DiT MISS) |
| Script policy | Thumbs/collage only — no auto PASS |

---

## Bottom line for Derrick

1. **Keep Cond.** One clear act still that already encodes Face + oral contact + wardrobe + neon + partner is the correct S0 REF set.  
2. **Different photos help later** when they supply a **missing angle or subject**, not when they are prettier duplicates.  
3. **Better resolution alone** rarely beats a correct complementary view + six-section binding; `max` is a fidelity knob with a high step-cost — not the first fix while HostBuffer is open.  
4. After TECH: fail-specific add (profile / partner / detail), one-axis, human review via collage.  
5. ~1-min product = multi-clip chain with **stable Cond identity**, not nine beauty refs in S0.

---

**No Dial ping · no smoke · no invent KEEP** from this research alone.
