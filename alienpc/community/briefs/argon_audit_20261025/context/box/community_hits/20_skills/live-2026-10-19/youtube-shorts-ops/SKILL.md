---
name: youtube-shorts-ops
description: >-
  use this when running Ancient History YouTube Shorts — includes mandatory stage owners (T2I/I2V/assembly/upload); Artframe lane uses artframe-ops instead but shared seats/QA apply. Wave 2 absorb (2026-09-24): former micro-card checklists for storyboard, animation-direction, character-lock, cinematography, continuity, retention-hooks, learning-design, and actionable-cited-decisions live in Absorbed sections below.
---
# YouTube Shorts ops (Ancient History + Artframe cross-link)

## When
Produce/research/scale Ancient History Shorts on derek.boone86. For **Artframe / `@Artframe`** art-as-subject Shorts, do **not** run this as the lane SoT — use [artframe-ops](sand-workflow:artframe-ops) (L4 default [artframe-l4-side-feature-lore-zoom-out](sand-workflow:artframe-l4-side-feature-lore-zoom-out)). Shared seats/QA below still apply.

## Owners (must stay filled — audit FAIL if blank)
| Stage | Owner |
|-------|--------|
| Pipeline SoT (Ancient) | YouTube Shorts |
| Pipeline SoT (Artframe) | **Artframe bot** + [artframe-ops](sand-workflow:artframe-ops) |
| Sources / persona | [shorts-historian](sand-workflow:shorts-historian) → CoS gate |
| Deep Research export | Gemini → Drive 06_Deep_Research |
| T2I stills (Ancient) | Gem-first → **Google Pics** edit ([google-pics-stills](sand-workflow:google-pics-stills)); Imagine only specialty/go |
| T2I stills (Artframe) | Gem-first → **Google Pics** → Visual QA; never Cursor GenerateImage; Flow T2I fallback only if Pics blocked |
| I2V generate + retries | **Upload Pics masters** → Flow Seat animate (4–8s; 2–3 takes/beat) |
| **Assembly / scene download** | **Flow Seat** + [flow-scenebuilder-shorts](sand-workflow:flow-scenebuilder-shorts) / [shorts-multi-clip-i2v-assembly](sand-workflow:shorts-multi-clip-i2v-assembly) |
| Captions / VO bed (post only) | [shorts-editor-post](sand-workflow:shorts-editor-post) — does **not** own assemble |
| Studio upload | [shorts-studio-ops](sand-workflow:shorts-studio-ops) — Artframe masters → **Artframe channel only**; seat `chrome-profile-youtube-shorts` |
| Product QA | [shorts-product-qa](sand-workflow:shorts-product-qa) — **PRODUCT_PASS** before Public; refuse without VISUAL_QA_PASS |
| Viral research | [shorts-trends-research](sand-workflow:shorts-trends-research) |
| Continuity (multi-clip) | [shorts-continuity](sand-workflow:shorts-continuity) · gate [shorts-visual-qa](sand-workflow:shorts-visual-qa) (Continuity bot deleted 2026-09-12) |

## Account×Product / Seats (LOCKED 2026-09-10+)
| Product | Account | Chrome / CDP | Notes |
|---------|---------|--------------|-------|
| YouTube Studio | derek.boone86 | `chrome-profile-youtube-shorts` | Never invent profile-N |
| Flow (Derek) | derek.boone86 | `chrome-profile-flow-derek` @ **9340** | Never invent :20 |
| Flow (incognito) | incognitodb86 | `chrome-profile-flow-incognito` | CoS/Derrick go only; never mix with derek |
| Gemini + **Google Pics** | derek.boone86 | `chrome-profile-3` @ **9225** reuse | `pics.new`; Not profile-6 |
| Imagine | Max lane owner (ROSTER) only | imagine-dl / imagine-derek / Fork-5 @9227 | Shorts never drives; legacy chrome-profile-5 banned |

## Hard locks
- No Public without Derrick go **and** [shorts-product-qa](sand-workflow:shorts-product-qa) **PRODUCT_PASS**
- Artframe Public also needs [artframe-legal-pass](sand-workflow:artframe-legal-pass)
- SOURCES_PASS alone insufficient
- Auto-FAIL: letterbox, ken-burns-only, no real I2V, landscape masters for I2V
- [box-chrome-resource-capa](sand-workflow:box-chrome-resource-capa) before heavy Flow
- Never bare `box-chrome` / DISPLAY `:20` / `chrome-profile-20`

## Wave 1 craft PASS (fleet consolidate)
Pre-Public craft checklists now live in Absorbed sections on this hub + [shorts-product-qa](sand-workflow:shorts-product-qa) / [shorts-visual-qa](sand-workflow:shorts-visual-qa):
- This hub: **Absorbed: shorts-retention-hooks**, **Absorbed: shorts-learning-design**
- Product QA hub: sound-mood, discoverability-seo, community-tone (+ publish a11y/trust gates)
- Visual QA hub: accessibility (visual), trust-labels (visual chrome)
- Still external: [audience-psych-review](sand-workflow:audience-psych-review)

## Wave 2 motion / craft PASS (fleet consolidate 2026-09-11)
**Before I2V lock / Scenebuilder:** showrunner invokes Absorbed sections below (same order as former micro pills):
- **Absorbed: shorts-storyboard**
- **Absorbed: shorts-cinematography**
- **Absorbed: shorts-animation-direction**
- **Absorbed: shorts-character-lock** when recurring avatar/kit
- **Absorbed: shorts-continuity** across multi-clip — **no Continuity bot**; Visual QA files `CONTINUITY_PASS|HOLD|FAIL`
- [shorts-i2v-camera-motion-cards](sand-workflow:shorts-i2v-camera-motion-cards) (still standalone)

Also: **Absorbed: shorts-actionable-cited-decisions** whenever Derrick answers become durable guidelines or sources conflict.

## Subagent-first
[token-efficiency-capa](sand-workflow:token-efficiency-capa) (Absorbed: shorts-crew-token-capa). Status=files.

## Verify
- [ ] Stage owners filled
- [ ] Wave 1 + Wave 2 Absorbed checklists run (or HOLD noted)
- [ ] Artframe cross-link [artframe-ops](sand-workflow:artframe-ops) present
- [ ] PRODUCT_PASS before Public

## Failure
Invent Chrome / ken-burns Public → [cos-stop-the-line](sand-workflow:cos-stop-the-line).


## Phase 0 skill cites (2026-09-26)
Standalone skills now exist for specialist absorb (verify in Phase 2 before park/Delete):
- Trends: [shorts-trends-research](sand-workflow:shorts-trends-research) — dated files + URLs or NO_DATA; never invent views
- Script: [artframe-script](sand-workflow:artframe-script) + Copy Humanizer VO ear; SCRIPT_SCORECARD ≥95
- Editor: [shorts-editor-post](sand-workflow:shorts-editor-post)
- Continuity: [shorts-continuity](sand-workflow:shorts-continuity)
- Policy/YPP: [shorts-policy-ypp](sand-workflow:shorts-policy-ypp)
- Studio: [shorts-studio-ops](sand-workflow:shorts-studio-ops) · seat `chrome-profile-youtube-shorts`
- Analytics: [shorts-analytics](sand-workflow:shorts-analytics) · NO_ANALYTICS allowed
- Historian: [shorts-historian](sand-workflow:shorts-historian)

## Absorbed: shorts-storyboard (Wave 2 2026-09-24)
**When:** building beat-boards / shot lists so every 1.5–2s has on-screen action (0–3s hook + density).

**Checklist**
- [ ] Hook beat 0–3s named
- [ ] Beat every ~1.5–2s with visible action
- [ ] Maps to CAMERA + MOTION cards
- [ ] Captions/VO slots noted
- [ ] Duration target ~25–35s unless exception

**Output:** `STORYBOARD.md` / beat table. Status=files.

## Absorbed: shorts-cinematography (Wave 2 2026-09-24)
**When:** locking camera / DP notes for Military/Ancient/figure Shorts I2V beats (angles, moves, lens/DoF, per-clip cards).

**Checklist**
- [ ] One CAMERA_CARD per beat (start+end frame intent)
- [ ] Move named (push/pull/pan/orbit) — no vague “cinematic”
- [ ] 9:16 composition; reject landscape pads
- [ ] Duration 4–8s per I2V clip unless showrunner exception
- [ ] Hand to Animation / Flow with F2V start+end stills when required

**Output:** `CAMERA_CARD_C*.md` + LOCK note. Status=files.

**Hand-off:** Showrunner / Flow Seat executes.

## Absorbed: shorts-animation-direction (Wave 2 2026-09-24)
**When:** directing what moves on screen in AI Shorts (bodies, formations, cloth, map blocks) vs locked kit.

**Checklist**
- [ ] MOTION_BRIEF per beat: what moves / what stays locked
- [ ] No invent props/spray/effects not in kit SHOW
- [ ] Prefer subject motion over ken-burns-only
- [ ] Jelly/morph = FAIL → rematch take
- [ ] Duration aligned to camera card (usually 6–8s)

**Output:** `MOTION_BRIEF_C*.md` + LOCK. Status=files.

**Hand-off:** Flow generates; Visual QA judges morph; showrunner owns cadence.

## Absorbed: shorts-character-lock (Wave 2 2026-09-24)
**When:** locking recurring Field Guide/Commander/Helen-class avatar + era kit packs so Shorts keep recognition.

**Checklist**
- [ ] Character bible / kit pack cited
- [ ] LOOKALIKE / fictional-adult rules if applicable
- [ ] Face/kit nouns stable across episode
- [ ] No known real image (exact public match, canon rule 4); minors check always on (canon rule 4)
- [ ] Stills match locked kit before I2V

**Output:** Kit lock path + PASS/HOLD. Status=files.

**Hand-off:** Showrunner + Historian/Visual QA.

## Absorbed: shorts-continuity (Wave 2 2026-09-24)
**When:** across multi-clip Shorts for face/kit/armor consistency, screen direction, last-frame→next-clip match.

**Owner (2026-09-12):** No dedicated Continuity bot. Process = this Absorbed checklist. Gate owner = **Shorts Visual QA** before APPROVE_STILLS / Scenebuilder. Product QA refuses Public without `CONTINUITY_PASS` on multi-clip.

**Checklist**
- [ ] Kit/armor/face consistent across clips
- [ ] Screen direction coherent (or intentional reverse cut noted)
- [ ] Last frame of clip N matches first of N+1 when continuous
- [ ] No teleporting props/landscape
- [ ] Hard cuts OK; soft morph blends = FAIL

**Output:** `CONTINUITY_PASS|HOLD|FAIL` note with beat list. Status=files.

## Absorbed: shorts-retention-hooks (Wave 2 2026-09-24)
**When:** before freezing titles, thumbnails, or 0–3s openings for Helen/Military or Artframe (art-story) Shorts.

**HARD:** Promise must be paid off in the video (no empty clickbait). Specific curiosity > vague mystery.

**Checklist**
- [ ] Hook in first 1–3s (visual + on-screen or VO)
- [ ] Title = concrete question or tension the Short answers
- [ ] Thumb readable at phone size; face/art focal point clear
- [ ] Mid-retention beat every ~1.5–2s (Storyboard alignment)
- [ ] End loop or payoff line for rewatch

**Output:** `/workspace/youtube-shorts/retention/HOOK_<slug>.md` or `/workspace/painted-past/retention/` with PASS/WARN/FAIL + 2 A/B alts.

**Cites:** Curious Shorts CHI ’25; science-comm curiosity-gap; Audience Psych fluency lenses.

## Absorbed: shorts-learning-design (Wave 2 2026-09-24)
**When:** before SCRIPT freeze on edu Shorts (Helen forks, Artframe painting stories, military lore).

**HARD:** Viewer should leave with one clear takeaway; structure question → evidence → answer. YPP anti-slop: original insight required.

**Checklist**
- [ ] One learning objective stated internally
- [ ] Hook question matches objective
- [ ] Evidence beats cite-backed (SOURCES / RESEARCH)
- [ ] Misconception addressed if relevant (CONFLICT_MAP fork labeled)
- [ ] Closing line restates takeaway without new claims

**Output:** `LEARNING_<slug>.md` PASS/WARN under series or painted-past/research.

**Hand-off:** Cites → Historian / Artframe Research · Psych → Audience Psych

## Absorbed: shorts-actionable-cited-decisions (Wave 2 2026-09-24)
**When:** whenever Derrick asks a process/format/history question whose answer should shape future Shorts work — and whenever research finds **conflicting** sources.

**Hard locks**
1. Same turn (or next research beat): write a **decision-log** entry and/or update canon/skill — chat-only answers are FAIL.
2. Artifact must be **actionable, repeatable, consistent** (owner, steps, verify, STOP, evidence path).
3. Historical/visual claims always follow `SOURCE_STANDARD.md` cites — no unsourced “real look.”
4. **Conflicts → multiple Shorts:** file `series/<topic>/CONFLICT_MAP.md`; one episode per fork; never mush into one uncited truth.
5. CoS pings affected bots with file paths (status=files).

**Paths**
- Canon: `/workspace/youtube-shorts/canon/ACTIONABLE_CITED_DECISIONS.md`
- Logs: `/workspace/youtube-shorts/decision-log/`
- Sources gate: `/workspace/youtube-shorts/SOURCE_STANDARD.md`

CE: follow [fleet-ce-adapter](sand-workflow:fleet-ce-adapter) (ce-plan · ce-doc-review · ce-work · ce-compound).
