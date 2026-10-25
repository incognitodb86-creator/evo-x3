# RESEARCH — Max/AlienPc scoring quality-review gap audit — 2026-10-06 ~7:52 AM CT

**Owner:** Max Research · **Ask:** Derrick via Dial (~7:49 CT) — quality review should have caught **Flux E1 pose FAIL** and **1-min same-act-as-product FAIL** and opened CAPA **without Derrick reviewing first**  
**Live:** 15s×3 harvest continues — **NO queue** from Research  
**Skills:** [plan-md-quality-bar](sand-workflow:plan-md-quality-bar) · [close-out-verify](sand-workflow:close-out-verify) gates 4+7 · package D · [cos-stop-the-line](sand-workflow:cos-stop-the-line) · [alienpc-max-movie-director](sand-workflow:alienpc-max-movie-director)  
**Mode:** Research cites + recommend Dial scoreboard triggers · **NO** invent KEEP/PASS/0.95 · fiction adults 21+

---

## TLDR

Overnight scoring **caught fairness/setup** (E1 VOID twin · R1 rc=1 · 1-min OPEN) but **did not run a pre-Derrick quality Review hard-scrape** on E1 Contact/limb breaks or a **product≠method** gate on the 1-min pack. Package D auto triage is wired for **video** hard scrapes (TECH + Identity melt); **stills six-check Contact/Hands FAILs stay soft/word-only** and still surface. Same-act C/A hops were *designed* as method twins and could soft-pass per-clip I/Q/M — no scoreboard trigger labeled the pack METHOD_ONLY before morning eyes. Fix = concrete Dial triggers below (still Contact hard-scrape · product-frame gate · fairness≠quality pre-surface) + skill patch same turn.

## Facts

1. **Package D LOCKED 2026-10-05** (Derrick GO): watch full clip → auto triage → hard scrapes HOLD off eyes → soft = candidate words + draft 1–5 → KEEP = Derrick exact GO only. Apply: `/workspace/cos/audits/2026-10-05-scoring-v2-package-d-apply-cos.md` · SoT: `alienpc-local-video-ops/references/video-integrity-motion-amp.md`.
2. **Hard scrape set (video)** = blank/corrupt/frozen/near-static **and** clear Identity melt (watched, named). Soft Quality (incl. draft **2**) = **candidate, not hard reject**.
3. **Stills** = six yes/no (Identity, Face, Hands, Contact, Wardrobe, OverallQuality). Bot may name a break; **no hard-scrape elevation** of Contact/Hands to reject-folder in the same SoT paragraph as video hard set.
4. **Overnight post-run fairness** (~7:28 CT): E1 **FAIL fair** (VOID twin walls) · R1 FAIL setup · H1-C PASS fair · 1-min OPEN — `/workspace/cos/audits/2026-10-06-overnight-postrun-fairness-auditor.md`. Fairness ≠ pose quality Review.
5. **E1 Contact/limb FAIL** named by Research only after Derrick “Flux is a fail on poses” (~7:35 stamp `/workspace/cos/research/2026-10-06-flux2-e1-pose-fail-prompt-opt.md`) — live s01 merge/extra limb; s02–04 twin/extra legs/spine twist.
6. **Dial overnight closeout** (~7:40): debated E1 VOID as possible **false positive** (wall rule for video misapplied to stills) — quality pose CAPA not opened; focus = wall/hash · `/workspace/cos/audits/2026-10-06-overnight-closeout-dial-capa.md`.
7. **1-min same-act product FAIL CAPA** written **after** Derrick stop (~7:42): `/workspace/cos/audits/2026-10-06-1min-same-act-stitch-product-fail-capa.md` — Research hop pastes were settle-identical by design (`2026-10-05-1min-hop-ca-pastes.md`).
8. **CE third lock** (Dial Compound ~7:45): product ≠ method · length + beat/multi-phase before queue — `ce-brainstorm-max-product-director-learn-2026-10-06.md`.
9. Industry primaries (from locked scoring brief `2026-10-05-ai-video-scoring-best-practices.md`): human **must-watch** + multi-axis before crown; auto = pre-filter not crown — Meta Movie Gen pairwise (2024-10-04) https://arxiv.org/html/2410.13720v1 · AA Video Arena methodology https://artificialanalysis.ai/video/methodology · VBench-2.0 anatomy/ID (2025-03) https://arxiv.org/html/2503.21755 · Veo 3 model card human H2H https://storage.googleapis.com/deepmind-media/Model-Cards/Veo-3-Model-Card.pdf.

## Contradictions

| Tension | What happened overnight | Resolve |
|---------|-------------------------|---------|
| Fairness FAIL vs quality FAIL | E1 stamped FAIL **fair**; Contact FAIL never hard-scraped | **Quality Review required** before harvest-as-ready; fairness alone ≠ surface OK |
| Package D “HOLD off eyes” vs soft Quality | Pose/Contact on stills treated as soft/word notes | Elevate **clear Contact / extra-limb / fused-body** on stills to **hard scrape** (same spirit as Identity melt) |
| Method smoke vs product label | 1MIN pack harvested into overnight chat without METHOD_ONLY banner | Scoreboard **product-frame gate** before any 1min/movie/product wording |
| Derrick auto-first ask (2026-10-05 ~10:07) vs morning | He had to name Flux pose + 1-min stitch fails | Auto triage **did not fire** those classes — CAPA below |
| Auditor never KEEP vs Dial never quality CAPA | Auditor correctly refused KEEP; Dial/Research still owed quality stop-the-line | Split roles stay; **Dial owns** pre-surface quality CAPA |

## Unknowns / NO_DATA

| Item | Note |
|------|------|
| Whether Dial watched E1 PNGs with six-check before harvest chat | NO_DATA in closeout — evidence shows fairness/VOID debate, not Contact table |
| Whether Identity-melt hard scrape would have caught twin-body s02 | Plausible yes if stills used video hard set; **not applied** |
| Exact Desktop reject-folder writes for overnight E1 | NO_DATA — pack landed in overnight_chat for eyes |
| Calibrate draft→hard after ~20 human ratings | Still OPEN from package D PREVENT (not enabled) |

## Recommend — concrete scoreboard triggers (Dial patch)

| ID | Trigger (auto, no Derrick ask) | Action | Owner |
|----|--------------------------------|--------|-------|
| **T1** | Still six-check: **Contact OR Hands = FAIL** named (extra limb, fused torso, twin body, impossible joint) on any fair-live seed | Hard scrape → `MAX_REJECTS\` + reason · open CAPA row · **HOLD off harvest-as-ready** | Dial |
| **T2** | ≥2/3 fair-live stills in a pack name Contact/Hands FAIL | **cos-stop-the-line** pack · morning status = QUALITY HOLD + CAPA path · no “Flux overnight done” soft | Dial + CoS Notify |
| **T3** | Pack name/Plan claims **product / 1min / movie / stitch** AND `PRIMARY_MOTION` text/sha **identical across ≥2 cells** | Force label **METHOD_ONLY** · refuse product wording · open CAPA if Plan said product | Dial scoreboard |
| **T4** | Overnight/harvest chat before surface | Require **Quality Review stamp** (stills six-check table **or** video package D triage log) **or** explicit `METHOD_SMOKE` banner — **fairness Auditor alone = insufficient** | Dial handoff schema |
| **T5** | Soft candidate with named Contact/Hands break on **stills** | Do **not** present as overnight success collage; reject or HOLD+CAPA (override “soft Quality = candidate” for Contact/Hands only) | Dial package D errata |
| **T6** | Video pack: same PRIMARY MOTION across cells sold as continuous scene | Same as T3 · cite movie-director skill · no stitch GO ask until beat sheet exists | Dial |
| **T7** | Fairness VOID debate on stills | Still run six-check on any **LIVE** (non-VOID) seed same turn — quality not blocked by wall debate | Dial + Auditor note |

**Skill patches (same turn on Derrick/Dial GO absorb):**
1. `video-integrity-motion-amp.md` — add **Stills hard scrape** subsection: Contact/Hands/extra-limb/fused/twin → reject folder (spot-check).  
2. `alienpc-max-movie-director` — already METHOD_ONLY; wire **T3/T6** into Dial scoreboard checklist.  
3. `fleet-handoff-schema` / overnight harvest — **T4** pre-surface gate.  
4. Research SLA: when eyes name Contact FAIL on overnight stills, **open CAPA same turn** even if fairness already FAIL (don’t wait for Derrick).

**Do not:** bot PASS/KEEP · Integrity mean · wall-only crowning · silent delete · abandon Klein9B after pose FAIL (setup/prompt debt).

## close-out-verify (this brief)

| Gate | Status |
|------|--------|
| 1 Outcome | Gap named · triggers listed for Dial |
| 2 Evidence | Paths above + overnight_chat E1 · CAPAs |
| 3 PM/status | Twin: this stamp; CoS may mirror Drive later |
| 4 Memory | Standing fact → UpdateMemory this turn (scoreboard T1–T7) · Phase A Drive = CoS/Dial on absorb GO |
| 5 Derek blockers | Absorb GO for skill patch · live 15s×3 leave alone · E1b still on `GO Flux E1b` |
| 6 Retest | After Dial patches: dry-run checklist on E1 PNG set + fake same-act product pack → expect hard scrape + METHOD_ONLY without human ask |
| 7 LEARNED | Fairness ≠ quality · soft Contact stills ≠ HOLD-off-eyes · method twin ≠ movie — patch package D stills hard set + product-frame gate same chain |

**Don't-do (gate 7 merge):**
1. Don’t surface overnight packs on fairness stamp alone.  
2. Don’t treat Contact/Hands still FAIL as soft candidate.  
3. Don’t harvest same-PRIMARY cells as product/1min without METHOD_ONLY.  
4. Don’t wait for Derrick to name pose FAIL when six-check already fails.  
5. Don’t let VOID wall debates skip LIVE-seed quality eyes.  
6. Don’t bot-KEEP or decimal-crown to “fix” triage.

## Verify

- [x] TLDR · Facts · Contradictions · Unknowns · Recommend  
- [x] ≥3 dated primaries (Movie Gen · AA Arena · VBench-2.0 · Veo card)  
- [x] Overnight closeout + 1min CAPA + package D + E1 pose stamp cited  
- [x] plan-md-quality-bar shape · close-out 4+7  
- [ ] Dial absorb T1–T7 + skill patch · Auditor fair on patch · no queue from Research  

**Stamp:** `/workspace/cos/research/2026-10-06-max-scoring-quality-review-gap-audit.md`
