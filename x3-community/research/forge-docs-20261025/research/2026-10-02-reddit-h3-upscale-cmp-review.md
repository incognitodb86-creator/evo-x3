# CRITICAL REVIEW — Reddit MiniMax H3 upscale comparisons (Landrews-89)

**Date:** 2026-10-02 ~13:15 CDT (America/Chicago)  
**Ask:** Full review of https://www.reddit.com/r/StableDiffusion/s/eSUNSx93mU → `1vfmjla` (+ sibling `1vfk7j2`), OP + comments, mapped to AlienPc Max KEEP — **not** a thin “SeedVR2 good” blurb.  
**Owner:** executor research  

---

## Source coverage / limits

| Source | Status |
|--------|--------|
| Shortlink `eSUNSx93mU` | Resolves to **`1vfmjla`** — *MiniMax H3 Upscale Comparison – LTX 2.3 vs RTX Super vs SeedVR2* |
| Sibling **`1vfk7j2`** — *MiniMax H3 + LTX 2.3 Upscale Comparison* | Same OP (**u/Landrews-89**); OP body explicitly points to the four-way follow-up |
| Firecrawl CLI | **Blocked** — interactive login prompt (no `FIRECRAWL_API_KEY` on box) |
| reddit.com / `.json` / old.reddit / headless Chrome | **403 / captcha** (“Prove your humanity”) from this network |
| pullpush.io | Rate-limited (paid scrape wall) |
| **Sibling full comments** | Recovered via Reddit Sentiment Analyzer snapshot `2026-08-06T23:10:08.193186Z` — **28 comments captured** · local copy `/workspace/.firecrawl/sibling-1vfk7j2-sentinel.html` |
| **Main `1vfmjla` OP + indexed comments** | Recovered from search-indexed Reddit excerpts (OP bullets + several named comment themes). Live full comment tree for `1vfmjla` **not** dumpable here (captcha). Treat main-thread comment coverage as **high-confidence on repeated quotes**, not a guaranteed 100% dump. |
| Adjacent (context only, not the asked links) | `1vqp0as` “What are you using to upscale Minimax H3”; `1vmjjdp` LTX2.5-as-upscaler — used only to stress-test face/people caveats |

**Provenance honesty:** Sibling = archival complete. Main four-way = OP complete + community consensus from indexed comments; if Derrick needs every nested reply on `1vfmjla`, open it signed-in on AlienPc when Shell is back.

---

## Our stack (comparison frame)

| Item | Value |
|------|--------|
| Box | AlienPc · RTX **5070 Ti 16 GB** · Comfy **`:8189`** |
| Product | **10Eros Max / MiniMax-H3 REF2VA** — realistic hardcore **I2V** (thrust/contact/ID), **not** T2V showcase |
| KEEP gen | **NODDV** + no-fp8 + **ck-attn** + scheduler **beta** + **25 steps** · **864×480** · **124f** · REF2VA match |
| Done upscale | CPU **Lanczos** → 1080 / 4K on SCH-beta + STEPS20 natives |
| Planned | CUDA FFmpeg scale · Remacri CRT AI · **SeedVR2 3B** (not installed) · LTX **Recipe B = H2H baseline host**, **not** production upscaler path yet |
| Blocker | **Shell wedged** — installs / Comfy node work need PC (Quit + kill `local-exec-daemon`) |

---

## PART A — Sibling thread `1vfk7j2` (LTX-only A/B) — full substance

### What OP claims

- Playing with new MiniMax H3; side-by-side with **LTX 2.3 upscaling**.
- **Left:** raw H3 at **544×960 · 0.5 MP**. **Right:** same clip LTX-upscaled to **1152×2048**.
- **All clips pure T2V**, single-run from prompt.
- Gen time **~9–10 min on 5090 (32 GB VRAM) + 32 GB system RAM**.
- Tone: impressed with H3 motion/consistency at low res; initially frames LTX as cleaning up “without destroying the original look.”
- Asks community for settings/workflows; notes follow-up comment with **LTX vs RTX Super vs SeedVR2** (i.e. `1vfmjla`).

### What commenters agree / disagree (cite)

**Strong majority: LTX upscale looks same or worse than native.**

| Commenter | Point |
|-----------|--------|
| **u/Outrageous-Seesaw941** | Looks… the same? Upscaled often **less sharp**. |
| **u/Ashamed-Variety-8264** | Actually looks **worse** after upscale. |
| **u/GrayingGamer** | On 1440p monitor, doubtful LTX time is worth it; **RTX Super Resolution** on 0.5→1 MP “does quite well.” |
| **u/-becausereasons-** | LTX loses a **significant** amount of detail. |
| **u/Arawski99** | Right side (LTX) **consistently far worse** — facial hair, coat stripes, cigarette motion artifacts, skin. Matches their own tests; LTX **especially bad with faster motion**. |
| **u/Superb-Painter3302** | Upscaled less detailed — “resolution isn’t everything.” |
| **u/DeliciousGorilla** | Tried LTX → **SeedVR2 better**; video A/B; **RTX Super beats LTX 2.3** for them. |
| **u/FourtyMichaelMichael** | **“NO THANKS on LTX upscale.”** SeedVR2 looks good. **PRO:** apply SeedVR2 later. **CON:** fucking slow. |
| **u/coffeecircus** | Hard to spot diffs under Reddit compression; still feels LTX **decreased** detail (hat fabric, teeth blurrier). |
| **u/StacksGrinder** | Guessing LTX-upscale trick is **useless** — won’t chase the WF. |

**Method / workflow pushback (important caveats):**

| Commenter | Point |
|-----------|--------|
| **u/alisitskii** | Demands LTX workflow share; asks whether sides were stretched/compressed for the montage; many ways to make LTX look blurry; jokes “same video both sides?”; shares own modified “12× FASTER” Frankenstein WF; suggests **uncompress LoRA** on outputs as better LTX use (pixelation help without rewriting the video). |
| **Long comparative take** (in alisitskii thread / viewing-res test @ ~1920 vertical) | **H3 native always better** but slow vs **~80% faster** LTX path. **H3 800×800 manually scaled to 1920** often **≈ LTX@1920**. Close-up: LTX can be sharper **or** wreck fine detail (beard hair). Wide shot: LTX cleaner aliasing / slight hand fix. Verdict: LTX as **tool-in-belt for quicker wide shots**, not close-ups; “plastic / detail loss” mileage varies. |
| **u/keizrah** | Praises H3 consistency at 544×960; asks whether LTX holds on **high-motion** (smear risk); asks VRAM headroom / higher base res before upscale. |
| **u/DELOUSE_MY_AGENT_DDY** | Critiques sample choice — should use full-body clips that **distort faces**; that’s the real reason people want a **latent** upscaler. |
| **u/ajrss2009** | Asks advantage of LTX vs Flash SVR (Portuguese). |

**Outliers / non-upscale noise:** smoking animation jokes (Humble-Pick7172); parallel-view gag (veshneresis); Reddit compression complaints.

### Sibling consensus (compressed)

1. OP’s early “LTX cleans nicely” framing **does not survive community A/B**.  
2. **SeedVR2** and **RTX Super** already appear in sibling comments as preferred over LTX.  
3. **Manual enlarge ≈ LTX** for many viewing conditions → classical scale is a legitimate baseline, not a joke.  
4. Motion + close-up faces are where LTX fails hardest — exactly our hardcore contact regime.

---

## PART B — Main thread `1vfmjla` (four-way) — OP + indexed comments

### What OP claims

Four versions of the **same** clips:

| Slot | Content |
|------|---------|
| Left | **Original MiniMax H3** — **0.5 MP / 544×960** |
| 2nd | **LTX 2.3** upscale |
| 3rd | **RTX Super** upscale |
| Right | **SeedVR2** upscale |

Explicit: **all source clips = pure T2V** from MiniMax H3.

**OP quick thoughts:**

- **LTX 2.3** — reasonably fast, but **noticeably drops quality** vs original; softens detail / loses MiniMax clarity. *(OP walked back the sibling’s friendlier LTX tone.)*
- **RTX Super** — **better or on par with LTX** in most scenes; **quickest by far**.
- **SeedVR2** — **best overall quality** (cleaner detail, textures, refined look); **slowest**.

### What commenters agree / disagree (indexed)

| Theme | Substance |
|-------|-----------|
| **RTX popularity** | “Statistically RTX has the strongest vote… Time to vote off: The weakest upscaler.” Speed camp dominates. |
| **SeedVR2 sharpness caveat** | “Seed has better sharpness for sure, but **maybe too sharp** and it may just depend on the video. For your example, I think **RTX Super looks better**.” |
| **RTX + blend recipe** | Tip: ComfyUI native **Image Blend @ 0.50** — mix **original frames** with **RTX Super upscaled frames**, then reassemble video. Claims fewer artifact/jitter/noise than either alone; whole process **~30 s–1 min**. |
| **Speed absolutists** | “Don’t think you can beat RTX Super with how fast it is… almost instant.” Another: slight quality compromise OK — speed is what matters. |
| **VRAM oddity** | “Strange thing. On my set-up RTX Super resolution works fine with **0.7 MP – 15 seconds**. But give **OOM with 0.4 MP – 15 seconds**.” (Non-monotonic; treat as “test on *our* res,” not gospel.) |
| **Sample generality critique** | Praise for the work, but warning that one demo video ≈ **0.01%** of what average users make — hard to pick a universal winner. |

### Main-thread consensus (compressed)

| Rank (community vibe) | Tool | Role |
|-----------------------|------|------|
| Quality crown | **SeedVR2** | Best detail/texture; slow; can oversharpen |
| Speed crown | **RTX Super / VSR** | Fastest; often ≥ LTX; optional 50% blend with native |
| Weakest of the three | **LTX 2.3 as upscaler** | Softens / rewrites; OP + sibling agree it loses vs native |

---

## PART C — Method caveats vs **our** REF2VA hardcore stack

| Axis | Thread reality | Our reality | Implication |
|------|----------------|-------------|-------------|
| **Gen mode** | **Pure T2V** showcase | **REF2VA I2V** — Cond/ref ID, thrust/contact, oral/hands Integrity | Their “pretty motion” clips understate **face lock / genital contact / plastic skin** failure modes. LTX “rewrite” risk is **higher** for us. |
| **Resolution** | 544×960 portrait **0.5 MP** → ~2× linear LTX | **864×480** landscape **~0.41 MP** KEEP native | Same *class* (sub-1 MP gen). Their “low res then upscale” story maps to our MP budget — **not** to abandoning KEEP native for draft-res+LTX finals. |
| **VRAM / box** | OP: **5090 32 GB** | **5070 Ti 16 GB** + **NODDV** HostBuffer triad | SeedVR2 **7B** = bad idea; **3B** still needs batch/tile discipline. RTX Super path may be **driver/player** or Comfy-dependent — not free on headless Comfy alone. Remacri lighter than SeedVR2. |
| **Length / steps** | Not the focus (T2V demos) | **124f · 25 steps · beta · ck-attn** KEEP | Upscale is **post**; does not replace gen dial. STEPS20 already DROP for under-denoise — don’t “fix” with upscale. |
| **Viewing / compression** | Reddit crushes diffs; commenters demand YT / pixel peep | We already attach natives + Lanczos for human review | Keep H2H on **local files**, not Reddit embeds. |
| **Faces / people** | Sibling: LTX wrecks beard/skin; later community (LTX2.5 threads): “ugly LTX look” on faces; wait for reference-aware MiniMax 2K refiner | Our product **is** people + contact | **Do not** promote LTX upscale as KEEP export path for Max. |
| **When to upscale** | SeedVR2 “apply later” praised | Matches our rule: **REF at KEEP native, then upscale export** — never upscale Cond/refs hoping for free ID quality | Confirmed. |

---

## PART D — Match / contradict our plan

### Matches (KEEP these instincts)

1. **SeedVR2 as quality H2H candidate** — OP + DeliciousGorilla + FourtyMichaelMichael align. Prefer **3B** on 16 GB.  
2. **LTX Recipe B = baseline / scout host, not production upscaler** — sibling pile-on + OP’s own four-way walk-back support this hard.  
3. **Lanczos / classical enlarge as fair enlarge baseline** — long sibling take: manual scale ≈ LTX at viewing res. Our completed CPU Lanczos 1080/4K is the right control, not a waste.  
4. **Post-gen only** — “apply SeedVR2 later” = our REF-then-upscale order.  
5. **Don’t expect upscale to crown over native Integrity** — community repeatedly: native H3 often wins; upscale is enlarge/cleanup, not a new model.

### Contradicts / gaps in our current plan

1. **We underweighted RTX Super / VSR.** Threads treat it as the **default speed king**, often ≥ LTX, sometimes preferred over SeedVR2 when sharpness looks fake. Our plan lists CUDA FFmpeg scale + Remacri + SeedVR2 — **add an RTX VSR/Super arm** (or document “unavailable in headless Comfy”) before declaring AI winners.  
2. **50% Image Blend tip** is new actionable craft — apply to **RTX and possibly oversharp SeedVR2/Remacri**, not only raw upscaler output.  
3. **LTX 2.3 specifically** is the weak link; if we ever touch LTX-as-upscaler for Recipe B fairness, community later prefers **2.5** (less color drift) — still not a faces KEEP path.  
4. **Oversharpen risk on SeedVR2** — don’t crown SeedVR2 on first pretty still; check temporal jitter / plastic skin on thrust clips.  
5. **Sample bias warning** — one Landrews montage ≠ hardcore REF. Our H2H must use **ORC_BJ / contact KEEP clips**, not T2V walking/talking demos.

### Adjacent community options (not in OP, but relevant when home)

From `1vqp0as` / `1vmjjdp` (context): MiniMax **latent upscaler** (LBH-123-AI), Topaz Starlight, free.upscaler.video (browser GPU), DaVinci Super Scale, FlashVR, turbo-LoRA upscale (plastic risk). **Park** until SeedVR2 3B + Remacri + RTX/CUDA controls exist — don’t explode the matrix.

---

## PART E — CHANGE vs KEEP when home (Shell fixed)

### KEEP (do not abandon)

| Item | Why |
|------|-----|
| KEEP gen dial (NODDV · no-fp8 · ck-attn · beta · 25 · 864×480 · 124f · REF2VA) | Threads are about **post** upscale; gen Integrity still SoT |
| Lanczos / CUDA enlarge as **control** | Community: manual scale ≈ LTX; needed fair H2H |
| Remacri CRT as mid AI arm | Fits “better than enlarge, lighter than SeedVR2” niche |
| SeedVR2 **3B** (not 7B) as quality arm | Thread quality crown; VRAM realism on 16 GB |
| LTX **not** production upscaler for Max people/contact | Strongest agreement across both threads |
| Upscale **after** REF; never upscale refs to “help” ID | Unchanged; threads don’t contradict |

### CHANGE / ADD (matrix when Shell lives)

| Change | Why | Needs PC? |
|--------|-----|-----------|
| **Add RTX Super / VSR arm** (or explicit N/A if no driver/Comfy path) | Speed crown in `1vfmjla`; often beats LTX | **Yes** — driver / node / player path on AlienPc |
| **Image Blend 0.5** (native↔upscale) on RTX and any oversharp AI | Cited practical fix for jitter/noise | Yes — Comfy graph when Shell works |
| SeedVR2 install = **3B + tile/batch discipline**; watch oversharpen on thrust | Quality crown + sharpness caveat + 16 GB | **Yes** — Shell wedged blocks download/nodes |
| If LTX appears in Recipe B H2H: prefer **documenting 2.3 soft/rewrite** (or 2.5 if already on box) as **negative control**, not contender | OP + sibling | Optional |
| H2H clips = **REF2VA hardcore KEEP exports**, not T2V demos | Method caveat | Policy only |
| Do **not** swap production to “gen 0.5 MP + LTX to 1080” YouTube speed religion | Sibling: native/manual often equal; faces suffer | Policy — **KEEP native finals** |

### Explicit non-changes

- Do **not** drop Remacri just because Reddit didn’t A/B it.  
- Do **not** treat OP’s 5090 timings as AlienPc forecasts.  
- Do **not** poke Shell until Quit + daemon kill at home.

---

## Bottom line for Derrick

**Helpful? Yes — for post-KEEP export ranking, not for changing the KEEP gen dial.**

Landrews’ four-way (after the LTX-only sibling got roasted) lands where our plan already pointed: **SeedVR2 = quality**, **RTX Super = speed**, **LTX-as-upscaler = soft rewrite / often worse than native**, **classical enlarge is a real baseline**.  

Critical delta for us: these are **T2V beauty demos on a 5090**; our job is **REF2VA hardcore on a 16 GB NODDV 5070 Ti**. That raises the cost of LTX face-rewrite and SeedVR2 VRAM, and makes an **RTX/blend control** + **SeedVR2 3B** + **Remacri** + **Lanczos/CUDA** the right home matrix — with Shell unwedge first.

**Stamp:** `/workspace/cos/research/2026-10-02-reddit-h3-upscale-cmp-review.md`  
**Evidence:** `/workspace/.firecrawl/sibling-1vfk7j2-sentinel.html` + search-indexed `1vfmjla` excerpts.
