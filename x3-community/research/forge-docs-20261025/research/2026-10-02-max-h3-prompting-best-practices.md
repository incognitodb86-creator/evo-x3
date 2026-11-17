# RESEARCH — Max / 10Eros-H3 prompting best practices (REF2VA-first · ORC_BJ) — 2026-10-02

**When_CT:** 2026-10-02 ~8:15 AM CT (America/Chicago)  
**Owner:** CoS executor (research-only) · **Machine:** AlienPc `ecc21911-e61e-44fb-80b1-4bbe46bc56bd`  
**Ask (Derrick):** Best practices for prompting **Max / 10Eros** · REF2VA-first on Cond **ORC_BJ**  
**Scope:** Local canon + official MiniMax/Comfy + TenStrip author · **NO Dial ping · NO smoke · NO invent KEEP**  
**Product lock:** Max-first REF probe Plan · Cond = `FAIR_FLUX_ORC_BJ_2026-10-02/inputs/COND_HC3.jpg` (HC3_hulk_oral_ponytail_pump) · P157/P163 retired for this probe

---

## One-liner

**REF2VA uses a six-section prompt (not LTX POS, not base-en 3-field I2VA).** For ORC_BJ S0: wire Cond as `<Picture 1>` / subject refs · `fully_preserved` Face/ID/wardrobe/neon · PRIMARY MOTION = **oral pump / ponytail grip** (not doggy thrust paste) · length ≥124f · mute OK · TECH≠PASS · KEEP=Derrick GO only.

---

## Local canon we already have

### Official guides landed on box (read first)

| File | Role |
|------|------|
| `cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` | **REF2VA six-section** rewrite format (labels, retention markers, shot body) |
| `…/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_base_en.md` | T2VA / I2VA / FL2VA / L2VA · 3 core fields + alignment lines |
| `…/RESEARCH_MINIMAX_H3_FL2VA_2026-10-01.md` | Mode clarity matrix · dialect cheat · fair METHOD |
| `…/AUDIT_10EROS_MAX_SMOKE_READY_2026-10-01.md` §5–8 | TenStrip REF prefer · sampling · failure modes · literal contact |
| `…/CAPA_PROMPT_SKILL_LOCK_2026-10-01.md` | Prompt FAIL → patch skill same turn (not pack notes alone) |
| `cos/research/2026-10-02-10eros-max-hybrid-exhaustive.md` | Modes · length 4–15s · multi-clip · REF lean · anti C5 |
| `MAX_PROMPT_LTX_PARITY_2026-10-01/` | Motion-amp HARD · FL2VA/I2VA thrust paste packs (**adapt** for oral; do not paste doggy into BJ Cond) |
| Skills: `alienpc-hardcore-i2v-director` · `alienpc-local-video-ops` · `alienpc-ltx-i2v-prompting` | Max-first REF · no LTX POS into Max · motion amp FAIL = Integrity FAIL |
| Plan: `status/ce-plan-max-first-ref-probe-2026-10-02.md` | S0 REF · Cond ORC_BJ lock · gates |

### Mode → prompt shape (must not conflate)

| Mode | Cond job | Prompt shape | Node / template |
|------|----------|--------------|-----------------|
| **T2VA** | none | 3 fields: `integrated_multimodal_description` · `overall_soundscape` · `non_diegetic_music` | t2v / ImageToVideo t2va |
| **I2VA** | first frame @ 0.00s | Alignment line + 3 fields | `video_minimax_h3_i2v.json` first-only |
| **FL2VA** | first + last bookends | Dual-picture alignment + 3 fields; prefer single shot path | same I2V + last_frame |
| **L2VA** | last frame only | Last-frame alignment + 3 fields | build from I2V |
| **REF2VA** ★ | refs (1–N images/videos/audio) — **not** classic first-frame I2V | **Six sections in order** | `video_minimax_h3_r2v.json` · `MiniMaxH3ReferenceToVideo` |

**TenStrip / 10Eros-Max author rule (High):** even a **single still** → use **REF2VA format**, not classic I2V prose. I2V-style on Max hybrid → random camera / blue cast / identity drift. (PromptHero beta2 · AUDIT §6 · exhaustive research.)

### REF2VA six sections (fixed order)

1. `subject_definitions` — labels `<Subject N>` / `<Picture N>` / `<Video N>` / `<Audio N>`  
2. `summary` — `[task-type + …]` short paragraph  
3. `retention_analysis` — one line per label + fixed markers (`fully_preserved` · `partially_preserved` · `attribute_transfer` · `weak_reference`; audio: `fully_copy` · `partially_copy` · `reference` · `weak_reference`)  
4. `detailed_description` — style 1–2 sentences → `[Shot N]` timeline with labels inline · ~350–500 words for generation tasks  
5. `overall_soundscape` — ambience + physical / non-verbal SFX  
6. `non_diegetic_music` — audience-only score **or `N/A`**

### Local motion / Integrity canon (parity packs + skills)

| Lock | Rule |
|------|------|
| PRIMARY MOTION | Must be **obvious** act motion matching Cond (thrust packs = doggy/standing; **ORC_BJ = oral pump**) — Face `fully_preserved` is **concurrent**, not the product |
| Ban | soft-thrust-as-product · starved ~3s/73f Face cells · identical-bookend freeze crowned as PASS |
| Length | Default **≥124f (~5s)**; fair L1 toward **~8–15s** trained band |
| Score | Hostile **video** Integrity (ID hold mid-clip · anatomy · contact · **motion amp**) — never InsightFace / bookend auto as PASS |
| C5 | **VOID** — identical FL2VA bookends can fake Integrity |
| KEEP | Derrick exact GO only · TECH ≠ QUALITY PASS |
| Cond ORC_BJ | Still pack ~**0.94** TECH 3/3 · **KEEP=no** · OK for **S0 TECH scout** labeled; not a still QUALITY PASS crown |

### Cond ORC_BJ facts (for subject_definitions)

| Item | Value |
|------|-------|
| Path | `/workspace/FAIR_FLUX_ORC_BJ_2026-10-02/inputs/COND_HC3.jpg` |
| Trunk | **HC3_hulk_oral_ponytail_pump** (morning HC oral / neon) |
| Vision axes (stills) | identity · oral_contact · anatomy_named · pose_lock · neon_scene · no_censor |
| Seen elements (Bot notes) | tip-in-mouth / oral seal · hands on shaft · ponytail grip · choker · bikini preserved · neon scene |
| BEST still eye (not KEEP) | Flux out s25109002 oral seal — **Cond for Max = COND_HC3.jpg** unless Derrick renames |

---

## Official + community best practices

### Official MiniMax (HF ref-en / base-en + h3-prompt-writing skill)

| Practice | Takeaway | Conf. |
|----------|----------|-------|
| Mode pick first | REF vs I2VA/FL2VA = **different prompt schema** | **High** |
| REF = relationship-led | Define what each asset **contributes**, then how it is preserved/transferred | **High** |
| Labels stay stable | Same `<Subject N>` / `<Picture N>` across all six sections | **High** |
| Summary task prefix | e.g. `[reference generation]` · `[keyframe completion + reference generation]` — combine with ` + `, no duplicate types | **High** |
| `<Picture N>` vs `<Subject N>` | Picture = concrete frame/composition anchor; Subject = reusable identity/appearance unit. Single Cond often = both: Subject from Picture + Picture as Shot 1 anchor | **High** |
| detailed_description | Style before `[Shot 1]` · playback order · insert labels at first appearance · **observable** actions not plot summary | **High** |
| Camera | Motion type + optional amplitude + speed in natural English inside the shot | **High** |
| Dialogue | `(Sx)` + `<d>[Language] …</d>` · preserve source words | **High** |
| Sound split | Diegetic/synced in body · ambience in soundscape · audience-only score in music (`N/A` OK) | **High** |
| English body | Dialogue/lyrics/on-screen text keep original language | **High** |

Sources: local `MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_{ref,base}_en.md` · HF `MiniMaxAI/MiniMax-H3/docs/` · https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing

### Official Comfy (R2V tutorial + MiniMaxH3ReferenceToVideo)

| Practice | Takeaway | Conf. |
|----------|----------|-------|
| Tag by connection order | `<Picture N>` / `<Video N>` / `<Audio N>` **1-based** matching wired slots | **High** |
| Assign each ref a job | identity / style / motion / camera / voice — explicit beats vague “use this” | **High** |
| Limits | ≤9 images · ≤3 videos · ≤3 audio · ≤12 mixed | **High** |
| `ref_image_size` | `match` = speed; **`max`** = stronger identity (slower; refs ride every step) | **High** |
| Sampler for REF | `res_multistep` + **`beta` or `normal`** often beats `simple` on reference-heavy prompts | **Med-High** (Comfy R2V tips) |
| Turbo / Lightning on R2V | Short schedules (e.g. 4 steps) **starve** reference tokens → pose/face drift — prefer **base ~20 steps** when identity-critical; raise toward ~25 if still drifting | **High** (Comfy tutorial) |
| Cache / spectrum on REF | **OFF** for accuracy (TenStrip + AUDIT) | **High** |
| Native canvas | ~768 short edge / ~1 MP (e.g. 1344×768) · AR-lock Cond | **High** |
| Duration | Trained **~124–362f (~5–15s)** @ 24fps · longer untested | **High** |
| Separate DiT | Stock **ref2va** weights ≠ fl2va; Max TURBO-hybrid often **swapped into** R2V template — dialect still REF | **High** |

Sources: https://docs.comfy.org/tutorials/video/minimax/minimax-h3 · https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo · stock `video_minimax_h3_r2v.json`

### TenStrip / 10Eros-Max + AlienPc audits

| Practice | Takeaway | Conf. |
|----------|----------|-------|
| Prefer REF prompting | Single still = reference, not classic I2V | **High** (author) |
| Literal contact prose | “lips seal shaft / tongue / stroke” > empty NEG bans (bans can amplify) | **Med-High** |
| Size locks | Explicit breast size from Cond (“petite breasts”) counters Max inflate | **Med-High** |
| Contact teleport | Name contact type continuously (oral stays oral) | **Med-High** |
| Wardrobe vanish | `fully_preserved` wardrobe + describe any undress as motion | **Med** |
| Sampling (author) | `res_multistep/simple` 6–8 turbo motion · non-turbo full steps better AV · concept LoRAs 0.2–0.6 after TECH | **Med** |
| Dedicated Max Ref2VA checkpoint | Optional if hybrid REF tracking weak (Stuubs / TenStrip ref2va builds) — **not** S0 blocker | **Med** |
| Motion amp | Clone LTX **command** motion intent — for BJ Cond = pump/bob/grip, **not** thrust paste | **High** (local CAPA) |

Sources: HF TenStrip/10Eros-Max · PromptHero beta2 · Stuubs/10eros_Max_Ref2va · AUDIT §6–8 · MAX_PROMPT_LTX_PARITY NOTES

### Community prompt guides (secondary)

| Source | Useful + caveats |
|--------|------------------|
| Leadde / DomoAI / minimaxh3.co prompt blogs | Restate official six-section + “one job per ref” + debug table — **do not invent KEEP**; use as teaching restatement |
| Prompt builders | Help format; still validate against ref-en markers |
| Hosted H3-Context-IR | Free-form may work on **API**; local Comfy fair cells should still use **structured six-section** for repeatability |

---

## REF2VA template for ORC_BJ (six-section skeleton)

**Fiction adults 21+ only.** Cond = `COND_HC3.jpg` wired as **ref_image_1** → `<Picture 1>`.  
**No invented KEEP** — this is Dial POS draft for S0 TECH / later L1; labels `scout` until fair Integrity.

**Adapt note:** Prior parity packs are **doggy / standing-rear thrust**. ORC_BJ Cond is **oral / ponytail pump** — PRIMARY MOTION must match Cond continuity (oral seal + pump), not thrust teleport.

```text
subject_definitions:
<Picture 1> is the first-frame / composition anchor for [Shot 1], the Cond still COND_HC3 (HC3_hulk_oral_ponytail_pump): neon night scene, fair woman with ponytail and choker in bikini on knees / oral pose, large green muscular adult male partner, oral tip-in-mouth contact, hands on shaft, ponytail grip visible as in the still.
<Subject 1> is the adult woman (21+) whose Face/ID, hairline, ponytail, choker, bikini/wardrobe, skin tone, and body proportions come from <Picture 1>.
<Subject 2> is the large green muscular adult male partner (21+) whose Face/ID, body scale, skin/green tone, and genital appearance come from <Picture 1>.
<Subject 3> is the neon night environment in <Picture 1> (neon glow, background fixtures, color cast, framing depth).

summary:
[reference generation] The target video continues the oral act from <Picture 1> with <Subject 1> and <Subject 2> in <Subject 3>. Face/ID, wardrobe, neon scene, and oral contact type stay locked to the Cond while <Subject 1> performs clear rhythmic oral pumping with ponytail grip; single continuous shot; no dialogue; no non-diegetic music.

retention_analysis:
<Picture 1> ([Shot 1] opening composition / identity source): fully_preserved - opening pose, oral contact geometry, neon framing, and subject placements guide [Shot 1]; motion develops forward without rewriting identities.
<Subject 1> (appears in [Shot 1]): fully_preserved - Face/ID (eye spacing, nose, lips, jaw, hairline), ponytail, choker, bikini/wardrobe, and body proportions retained every frame.
<Subject 2> (appears in [Shot 1]): fully_preserved - Face/ID, green muscular body scale, and genital identity retained; contact type remains oral (no vaginal/anal teleport).
<Subject 3> (appears in [Shot 1]): fully_preserved - neon night lighting, background, and color cast retained (no blue-cast rewrite).

detailed_description:
The target video is realistic live-action hardcore porn, continuous single shot, photoreal skin and body weight, neon night practicals.
[Shot 1] Opens locked on the composition of <Picture 1>: <Subject 1>, the adult woman with ponytail and choker in bikini, holds oral tip-in-mouth contact with <Subject 2>, the large green muscular adult male; her hands grip his shaft; neon environment <Subject 3> fills the background. Identity: <Subject 1> Face/ID fully_preserved every frame; <Subject 2> Face/ID fully_preserved; bikini, choker, ponytail, and neon fully_preserved from <Picture 1>. Camera holds a static documentary porn framing — no push-in, no orbit, no random cut.
PRIMARY MOTION (must be obvious oral sex motion — not micro-shimmer, not soft pose hold, not freeze): rhythmic oral pumping. <Subject 1> slides her mouth forward and back along the shaft in clear strokes with visible wet seal; lips stay wrapped; tongue and cheeks move with the stroke; her hands stroke the shaft in time; the free hand (or partner hand) grips and tugs her ponytail on beat; her head bobs with measurable amplitude; breasts and torso rock slightly with each stroke; saliva sheen and wet contact sounds sync to motion. Tempo about one pump every half second, sustained the full clip — never freeze, never soft sway only, never still tableau. Oral contact type stays locked (no contact teleport). Petite breast size locked to Cond (no inflate). Ends still mid-pump energy with the same identities and neon scene — no wardrobe vanish, no identity rewrite.

overall_soundscape:
Quiet neon-room hush under low electrical hum; wet oral contact and soft skin stroke on the shaft; fabric rustle from bikini straps; low breathing and muffled moans without intelligible speech.

non_diegetic_music:
N/A
```

### Optional knobs (change **one** after S0 TECH — not invent KEEP)

| Knob | S0 default | Later only |
|------|------------|------------|
| Length | 124f (~5s) TECH → L1 climb 8–15s | multi-clip chain for ~60s |
| `ref_image_size` | start `match` for speed; if ID drifts try `max` | one-axis |
| Steps | Prefer ~20 base if Lightning starves refs; TURBO-hybrid author 6–8 if TECH OK | AV quality → non-turbo |
| Camera | static lock (reduces blue/orbit failure) | small push only after motion PASS |
| Extra refs | none for S0 (single Cond) | add angle stills only if ID fails |
| Audio | mute / N/A music OK for v1 picture | dialogue later |

---

## Anti-patterns (do not)

| Anti-pattern | Why it fails |
|--------------|--------------|
| **Paste LTX Recipe B POS** / CondSafe / JoyAI / 10S prose into Max TE | Wrong dialect · CAPA / skills HARD ban |
| **Classic I2VA 3-field** on Max hybrid when author says REF | Random camera · blue lighting · weak retention (TenStrip) |
| **Doggy thrust POS** on **ORC_BJ oral Cond** | Act teleport / Cond discontinuity |
| Soft thrust / Face-only chase / starved ~3s Face cells | C5-class freeze · motion amp FAIL |
| Identical FL2VA bookends + soft motion crowned PASS | VOID C5 |
| Empty NEG bans (“no inflate / no anal”) as the plan | H3 may amplify bans — use literal preserve + size locks |
| Plot summary instead of shot timeline | Official: avoid plot-only detailed_description |
| New labels mid-prompt / renumber subjects | Retention breaks |
| Turbo 4-step Lightning on identity-critical R2V | Refs under-applied (Comfy) |
| Cache / spectrum on reference shots | Accuracy loss (author) |
| Claim single Generate = 60s | Official 4–15s · multi-clip required |
| Crown TECH / InsightFace / still ~0.94 as Max KEEP | KEEP=Derrick GO · ORC_BJ still KEEP=no |
| Dial ping / queue from this research alone | Needs env + Max GO |

---

## Recommendation for Dial S0

**Precondition (not this doc):** live Comfy ≥0.30 + native `MiniMaxH3ReferenceToVideo` · Derrick exact **Max GO** · Cond `COND_HC3.jpg` HAVE · `:8189` only · single lease · label **scout**.

| # | Dial S0 lock |
|---|--------------|
| 1 | Mode **REF2VA** · template `video_minimax_h3_r2v.json` · node `MiniMaxH3ReferenceToVideo` |
| 2 | Cond **ORC_BJ** = `ref_image_1` / `<Picture 1>` · AR-lock native Cond WxH · Resolution ~0.3–0.4 MP for TECH (or Cond AR @ ~1 MP class after TECH) |
| 3 | POS = **six-section skeleton above** (oral pump) — freeze one INSTRUCT pack · do **not** paste doggy FL2VA files or LTX POS |
| 4 | Length **124f** first TECH · 1 seed OK for TECH · fair ≥3 only when crowning |
| 5 | Sampler: start author-compatible (`res_multistep` + simple/beta per stack) · **Lightning OFF** if ID critical · cache/spectrum **OFF** |
| 6 | `ref_image_size=match` first · TE CPU offload as inventory · UNET = HAVE TURBO-hybrid w4a8 (swap into R2V) |
| 7 | Score: graph TECH only for S0 · then hostile **video** Integrity (oral contact hold · ID mid-clip · motion amp of pump · neon/wardrobe) — **never** auto bookend / IF as PASS |
| 8 | Next after TECH: L1 length/Integrity in trained band → optional I2VA/FL2VA sub-knob **only if REF fails** → chain scout for ~60s — Flux2 still unlock **deferred** |
| 9 | **No Dial ping from CoS** until Derrick asks · **no invent KEEP** |

**Prompt pick theory (answer Derrick “how do you determine what prompt?”):**  
1) Mode → dialect (REF six-section here).  
2) Cond act → PRIMARY MOTION class (oral pump for ORC_BJ).  
3) Official retention markers for Face/ID/wardrobe/scene.  
4) Local CAPA: command motion + concurrent `fully_preserved`, not Face-ladder.  
5) Freeze one pack → fair smoke scores it → one-knob only after Integrity.

---

## Source index

**Local:** MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_{ref,base}_en · RESEARCH_MINIMAX_H3_FL2VA · AUDIT_10EROS_MAX_SMOKE_READY · CAPA_PROMPT_SKILL_LOCK · 2026-10-02-10eros-max-hybrid-exhaustive · MAX_PROMPT_LTX_PARITY_2026-10-01 · FAIR_FLUX_ORC_BJ_2026-10-02 · ce-plan-max-first-ref-probe · alienpc-hardcore-i2v-director / local-video-ops SKILL.md  

**Official web:** HF MiniMaxAI/MiniMax-H3 docs + h3-prompt-writing skill · Comfy MiniMax H3 tutorial · MiniMaxH3ReferenceToVideo node · Comfy-Org `video_minimax_h3_r2v.json`  

**Author / community:** TenStrip/10Eros-Max · PromptHero H3 Eros Max beta2 · Stuubs/10eros_Max_Ref2va · Leadde / DomoAI H3 prompt blogs (secondary restatement)

---

*Research only · 2026-10-02 ~8:15 AM CT · no Dial ping · no smoke · no invent KEEP*
