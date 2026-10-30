---
name: shorts-product-qa
description: >-
  use this before any Ancient History or Artframe Short goes Public — refuse Public without VISUAL_QA_PASS; Auto-FAIL landscape/letterbox/ken-burns/missing I2V/wrong-channel; LEGAL+PRODUCT+channel+Derrick for Artframe; PRODUCT_PASS gate. Phase 0 absorb (2026-09-26): Product QA Job uniqueness.
---
# Shorts product QA (pre-Public)

## When
Before any Military/Ancient/figure **or Artframe** Short goes Public. **PRODUCT_PASS** required. Artframe must also clear [artframe-quality-bar-95](sand-workflow:artframe-quality-bar-95) ≥95.

## Owner
Independent hard-gate **skill call** under YT Shorts / Artframe (bot absorb Phase 2). Studio must not Public without PRODUCT_PASS. **Refuse Public if VISUAL_QA_PASS missing** — AR 9:16 alone is not enough.

## Auto-FAIL conditions (any one = FAIL / no PRODUCT_PASS)
1. **Landscape masters** (width ≥ height) used as Shorts source
2. Landscape **letterbox** into 9:16
3. **Ken-burns-only** / slideshow-only / nearly-static caption-change “motion”
4. Content AR not true vertical (incl. Flash-Lite landscape promoted to masters)
5. **Missing real I2V** (stills-only packaged as “done”)
6. I2V without on-disk `CAMERA_CARD` + `MOTION_BRIEF` files
7. Captions unreadable muted
8. Duration outside ~25–35s without documented exception
9. **Artframe wrong-channel upload** (Ancient `@derekboone704` / empty Artframe channel id)
10. **Artframe Public without** [artframe-legal-pass](sand-workflow:artframe-legal-pass) `LEGAL_PASS` file
11. Artframe Public without Derrick go + PRODUCT_PASS + channel id

## Wave 1 craft PASS (pre-Public)
| Gate | Where checklist lives now |
|------|---------------------------|
| A11Y | [shorts-visual-qa](sand-workflow:shorts-visual-qa) Absorbed visual + **Absorbed: shorts-accessibility (publish)** below |
| SEO | **Absorbed: shorts-discoverability-seo** below |
| Hook | [youtube-shorts-ops](sand-workflow:youtube-shorts-ops) Absorbed: shorts-retention-hooks |
| Sound | **Absorbed: shorts-sound-mood** below |
| Trust / AI honesty / YPP | [shorts-visual-qa](sand-workflow:shorts-visual-qa) Absorbed visual chrome + **Absorbed: shorts-trust-labels (publish)** below |
| Learning | [youtube-shorts-ops](sand-workflow:youtube-shorts-ops) Absorbed: shorts-learning-design |
| Psych | [audience-psych-review](sand-workflow:audience-psych-review) |
| Post-publish tone | **Absorbed: shorts-community-tone** below |

## Wave 2 motion artifacts
Confirm showrunner ran Absorbed craft on [youtube-shorts-ops](sand-workflow:youtube-shorts-ops) (storyboard · cinematography · animation-direction · continuity — **Visual QA** owns continuity gate; Continuity bot deleted 2026-09-12 · character-lock when applicable) · [shorts-i2v-camera-motion-cards](sand-workflow:shorts-i2v-camera-motion-cards). Multi-clip: refuse Public without `CONTINUITY_PASS`.

## Artframe extras
- Lane SoT: [artframe-ops](sand-workflow:artframe-ops)
- Quality: [artframe-quality-bar-95](sand-workflow:artframe-quality-bar-95)
- Legal: [artframe-legal-pass](sand-workflow:artframe-legal-pass) — **LEGAL_PASS required for Artframe Public**
- Channel id must be Artframe (not empty / not Ancient)
- CONTEXT_PACK when/where on-screen
- Trust honesty for photoreal / morph beats

## Steps
1. Wave 1 + Wave 2 craft confirm (Absorbed sections + Visual QA)
2. ffprobe + 3 frames + motion note (prove not ken-burns-only)
3. Artframe: confirm LEGAL_PASS + channel id + SCORE_95 ≥95
4. Write PRODUCT_PASS / FAIL under `/workspace/cos/status/` or episode `audit/`
5. FAIL/HOLD → Private only; Artframe: **no** Ancient Private either

## Fleet consolidate
Wave 1/2 specialist bots deletable after Auditor verify **and** Phase 0/2 skill absorb. Hard gates stay **independent skill calls** (never generator self-APPROVE).

## Absorbed: shorts-sound-mood (Wave 2 2026-09-24)
**When:** before Editor locks VO bed + music for any Short.

**HARD:** Music must be cleared (YT Audio Library or commercial license via Artframe Rights / Policy path). Mood supports curiosity/emotion without drowning VO.

**Checklist**
- [ ] Bed licensed; path logged
- [ ] Duck under VO; no lyric clash with captions
- [ ] Tempo matches hook energy then settle for evidence
- [ ] No copyright-trap trending audio for monetized edu
- [ ] SFX sparse; not meme-spam

**Output:** `SOUND_<slug>.md` with track id/source + mood notes.

## Absorbed: shorts-discoverability-seo (Wave 2 2026-09-24)
**When:** before Studio metadata lock (title, description, hashtags, playlist).

**HARD:** Searchable + honest. No keyword stuffing. Curiosity title must match content (trust skill).

**Checklist**
- [ ] Title: primary entity + angle (painting name / Helen fork / battle)
- [ ] Description: first 2 lines carry searchable claim + Sources
- [ ] 3–5 relevant hashtags max
- [ ] Playlist: Helen series vs Artframe art-story separated
- [ ] Chapters/pins if long-form later

**Output:** `SEO_<slug>.md` with final title options A/B.

## Absorbed: shorts-community-tone (Wave 2 2026-09-24)
**When:** replying to comments, pinning comments, or drafting community posts for Helen/Artframe channels (post-publish).

**HARD:** Speak as Derrick’s channel voice: warm, factual, non-smug. Correct errors with cites; don’t dunk. Never invent history in replies.

**Checklist**
- [ ] Factual corrections cite a source or say “uncertain”
- [ ] AI/reconstruction questions get honesty labels
- [ ] No political pile-ons; redirect to the painting/claim
- [ ] Harassment → hide/report, don’t escalate

**Output:** Draft replies in `/workspace/youtube-shorts/community/` or painted-past/community/; showrunner approves send.

## Absorbed: shorts-accessibility (publish gate) (Wave 2 2026-09-24)
Publish-side lines from former `shorts-accessibility` (visual checklist lives on [shorts-visual-qa](sand-workflow:shorts-visual-qa)).

**When:** before PRODUCT_PASS / Public — require A11Y evidence.

**Publish checklist**
- [ ] `A11Y_<slug>.md` (or Visual QA note covering a11y) is PASS or WARN with accepted residual
- [ ] Captions present and readable muted (aligns Auto-FAIL #7)
- [ ] Letterbox / landscape pad = Product Auto-FAIL (Product owns letterbox; Visual owns readability)

**Hand-off:** Product QA owns letterbox + publish gate; Visual QA owns readability/a11y visual.

## Absorbed: shorts-trust-labels (publish gate) (Wave 2 2026-09-24)
Publish-side lines from former `shorts-trust-labels` (on-screen visual chrome lives on [shorts-visual-qa](sand-workflow:shorts-visual-qa)).

**When:** before Private/Public — Studio / YPP honesty.

**Publish HARD**
- [ ] Synthetic/AI disclosure in YouTube Studio when realistic AI-altered
- [ ] `TRUST_<slug>.md` PASS/WARN accepted; Studio checklist item checked
- [ ] Description honesty matches on-screen labels (no documentary-footage implication)

**FAIL (publish):** Deepfake of living people; unlabeled “true face” of myth figures; fake archival footage claims — block PRODUCT_PASS. Deepfake here = an exact public-image match of a real living person (canon rule 4); resemblance, a name label or a vision guess alone is not.

**Hand-off:** Policy · YPP for sensitive; Visual QA for slop; Rights for licenses.


## HARD — Refuse Public without VISUAL_QA_PASS (Phase 0 2026-09-26)
- No PRODUCT_PASS / Public if [shorts-visual-qa](sand-workflow:shorts-visual-qa) `VISUAL_QA_PASS` missing.
- Check physics/coherence fails surfaced by Visual QA (screen direction, load paths, gravity).
- Artframe: LEGAL + PRODUCT + channel id + Derrick go.
- Log product holds to LEARNINGS when Visual QA was skipped.

## Absorbed Job uniqueness (Phase 0 2026-09-26 — Shorts Product QA)
Own pre-publish PRODUCT_PASS for Military/Ancient **and** Artframe; refuse Public without VISUAL_QA_PASS; Artframe LEGAL+channel+Derrick.

CE: follow [fleet-ce-adapter](sand-workflow:fleet-ce-adapter) (ce-plan · ce-doc-review · ce-work · ce-compound).
