---
title: Live user skills snapshot 2026-10-19 (full copies)
date: 2026-10-19
---
# Live skills snapshot (2026-10-19 CT)

Full copies of the 69 live user skills from the Heavy box (`/home/box/agent-data/workflows/<name>/`), SKILL.md plus reference .md files, so the Derek account can install the exact setup. Archived skills are not included (the 11 archived 2026-10-19 under ALI-87 moved to `_archive/2026-10-19/20_skills/live-2026-10-19/`). Refreshed 2026-10-19 ~9:15 AM CT after the token-efficiency changes (ALI-83/85/87). Copies, not live: the box workflows folder is the source of truth; re-export to refresh.

Masking: Google account emails are replaced with `<derek-main-account>` / `<incognito-account>` (pack rule brain-files-carry-no-secrets-or-contact-info). Everything else is verbatim. Box paths (`/workspace/...`), CDP ports and AlienPc paths are pointers that only the Heavy box/AlienPc can reach.

To install on another account: create a skill with the same name and paste SKILL.md (restore the real account name where masked); put each `references/*.md` beside it.

| Skill | Description | Files |
|---|---|---|
| [alienpc-community-matrix-cell](alienpc-community-matrix-cell/SKILL.md) | use this for every AlienPc community matrix cell (A–G, C2, F retries) before queue and after FAIL — download community WF+all weights first, as-publis... | 2 |
| [alienpc-hardcore-i2v-director](alienpc-hardcore-i2v-director/SKILL.md) | use this when Derrick wants Condition stills animated into hardcore I2V keepers on AlienPc — Flux/Klein then Max H3 via llama-swap :8080/comfyui (back... | 3 |
| [alienpc-local-exec-lease](alienpc-local-exec-lease/SKILL.md) | use this when AlienPc Shell hangs, ListMachines says connected but Shell is dead, local-exec-daemon leftover, temporarily unreachable, two bots (e.g. ... | 1 |
| [alienpc-local-video-ops](alienpc-local-video-ops/SKILL.md) | use this when inventorying, configuring, leasing, or quality-gating AlienPc ComfyUI — llama-swap :8080/comfyui (backend :10002) Max production, packag... | 7 |
| [alienpc-max-movie-director](alienpc-max-movie-director/SKILL.md) | use this when building a multi-clip Max (~1 min) product scene on AlienPc — beat sheet first, distinct progressive prompts per cell, continuity wiring... | 1 |
| [alienpc-stills-pose-edit-prompting](alienpc-stills-pose-edit-prompting/SKILL.md) | Use before any AlienPc FLUX.2 Klein 9B still: pose/wardrobe edits of a start image, per-shot start frames, or a 2x2 storyboard sheet for H3 Ref2VA. Cu... | 4 |
| [artframe-i2v-paste-gate](artframe-i2v-paste-gate/SKILL.md) | use this before any Artframe Omni/Grok I2V spend — verify Flow/Imagine pastes match the Gemini Pro / share production script (Camera Motion, Subject M... | 1 |
| [artframe-l4-side-feature-lore-zoom-out](artframe-l4-side-feature-lore-zoom-out/SKILL.md) | use this for Artframe Shorts that start on a secondary figure/detail in the painting (not the main hero), tell that lore with hard when/where, then zo... | 1 |
| [artframe-legal-pass](artframe-legal-pass/SKILL.md) | use this before Artframe publish — LEGAL_PASS for plates, music, fonts, AI commercial ToS | 1 |
| [artframe-ops](artframe-ops/SKILL.md) | use this when running Artframe lane Shorts — Derrick pipeline viral→research→script→outline→prompt-pack→Pics→APPROVE→dual Omni 1.1 Flash + Grok Video ... | 7 |
| [artframe-photo-paint-morph-experiment](artframe-photo-paint-morph-experiment/SKILL.md) | use this when testing Artframe hooks that morph photoreal ↔ painting, use a hybrid seam, or L4 feature→lore→zoom-out→painting (e.g. Napoleon backgroun... | 1 |
| [artframe-quality-bar-95](artframe-quality-bar-95/SKILL.md) | use this before marking any Artframe stage DONE / STILLS_APPROVED_FOR_I2V / I2V / Public — ≥95 scorecard with mandatory VISUAL_QA_PASS (physics+histor... | 1 |
| [artframe-research](artframe-research/SKILL.md) | use this when compiling Artframe episode art-history research packs with cited sources, CONTEXT_PACK when/where, and punch-ready wrong-assumption + ho... | 1 |
| [artframe-script](artframe-script/SKILL.md) | use this when writing Artframe VO scripts and on-screen captions with L4 CONTEXT_PACK when/where; SCRIPT_SCORECARD ≥95 before DONE; Spokenness-weighte... | 1 |
| [artframe-stills-approve](artframe-stills-approve/SKILL.md) | use this when CoS · Campaign (or Artframe lane director) is about to set STILLS_APPROVED_FOR_I2V — checklist after Visual QA ≥95; Derrick end-product ... | 1 |
| [audience-psych-review](audience-psych-review/SKILL.md) | use this when reviewing channel names, titles, thumbnails, stills, or videos for attention/fluency/curiosity-gap/emotion and cultural accessibility be... | 1 |
| [aura-gem-json-prep-and-double-check](aura-gem-json-prep-and-double-check/SKILL.md) | use this when prepping Aura / Nano Banana Gem for Mode A — full instruction review without summarizing, then JSON convert + adversarial double-check b... | 1 |
| [bot-fleet-audit](bot-fleet-audit/SKILL.md) | use this when auditing Grok Bot assistants, or when a failure needs ISO correction, corrective action, and preventive action | 1 |
| [box-chrome-resource-capa](box-chrome-resource-capa/SKILL.md) | use this when the shared box is RAM-starved, OOM-kills Chrome/node, or bare box-chrome invents Fork-* / banned profiles — claim-or-quit + hard binary ... | 1 |
| [copy-humanizer](copy-humanizer/SKILL.md) | use this when rewriting drafts so they read human — especially Artframe / YouTube VO scripts + burned-in captions with WPM/cadence math, Spokenness ≥2... | 1 |
| [cos-browser-dispatch](cos-browser-dispatch/SKILL.md) | use this when deciding which bot/profile may open a browser, or when two bots both need browser access — named seats only; never bare box-chrome or Fo... | 1 |
| [cos-stop-the-line](cos-stop-the-line/SKILL.md) | use this when Chief of Staff must halt a dump, Drive port, multi-agent job, or edu still side-door because quality, Chrome sprawl, go-gate failure, or... | 1 |
| [cos-subagent-dispatch](cos-subagent-dispatch/SKILL.md) | use this when Chief of Staff must farm heavy work, run a finish-to-end go chain, or decide executor vs teammate Bot vs connector — Plan first; full ov... | 2 |
| [fantasy-news-scout](fantasy-news-scout/SKILL.md) | use this when scouting fantasy football news or analyzing ADP/ECR/projections that move waiver, lineup or trade value — cited bullets and named boards... | 1 |
| [fantasy-strategy-cot](fantasy-strategy-cot/SKILL.md) | use this when researching fantasy football strategy, draft plans, or pressure-testing the board with chain-of-thought | 1 |
| [fleet-brain](fleet-brain/SKILL.md) | Use when reading from or writing to the shared Grok Fleet Brain (Drive, and its box working copy where CE skills write), or when deciding where a piec... | 1 |
| [fleet-ce-adapter](fleet-ce-adapter/SKILL.md) | Use with every Compound Engineering (ce-*) skill on the fleet: where CE files land, which ce- skill to use for a job's size, what needs Derrick's yes,... | 1 |
| [fleet-handoff](fleet-handoff/SKILL.md) | Use when work must continue in another bot or on the other Grok account (task hand-off, phase hand-off, usage failover), and when picking up a handoff... | 1 |
| [flow-scenebuilder-shorts](flow-scenebuilder-shorts/SKILL.md) | use this when assembling Shorts in Google Flow Scenebuilder (Add to Scene, trim, preview, download scene) for ~25–35s vertical timelines — named Flow ... | 1 |
| [gbrain-sync](gbrain-sync/SKILL.md) | use this when the shared Drive brain (gbrain / Grok Fleet Memory) needs updating from the box brain, after any brain, canon or research change, or bef... | 1 |
| [gem-first-image-generate](gem-first-image-generate/SKILL.md) | use this before ANY edu/Helen/Military/Artframe still — History/Naughty Gem Mode A on disk first; refuse wrong-lane ecommerce/AURA JSON in Artframe/Hi... | 1 |
| [gemini-second-opinion](gemini-second-opinion/SKILL.md) | use this when CoS needs a Gemini web second opinion or should offload Ancient History Shorts fact+visual research to Gemini Deep Research / Pro / Flas... | 1 |
| [gemini-spark-cdp-reuse](gemini-spark-cdp-reuse/SKILL.md) | use this when Gemini Spark or any agent opens Gemini/Deep Research on chrome-profile-3 — force CDP reuse instead of box-chrome tab sprawl; HARD ban ba... | 1 |
| [google-pics-stills](google-pics-stills/SKILL.md) | use this when generating or refining Shorts/Artframe stills in Google Pics (pics.new) before Flow I2V — Gem-first FULL JSON (never master_prompt alone... | 1 |
| [google-spark-auth](google-spark-auth/SKILL.md) | use this when chrome-profile-3 @ 9225 shows Google sessionexpired, accountchooser, password challenge, or rate-limit — HOLD; never bot-type password; ... | 1 |
| [grok-bot-setup-playbook](grok-bot-setup-playbook/SKILL.md) | use this when creating, restructuring or auditing Grok Bots, skills, routines, channels, seats, Auto Review or secrets so the fleet follows official s... | 1 |
| [grok-bot-success-scorecard](grok-bot-success-scorecard/SKILL.md) | use this when scoring Chief of Staff or the bot fleet against goals — weekly health and outcome rubric | 1 |
| [historical-image-gem](historical-image-gem/SKILL.md) | use this when compiling Ancient History / battlefield / Artframe / epoch image prompts — Mode A via V.E.R.I.T.A.S. V139.2 Gem; force aspect_ratio 9:16... | 1 |
| [household-money-tracker](household-money-tracker/SKILL.md) | use this when tracking household bills, Scenic vs Canyon money, utilities, HOA, mortgage, or Frost alerts — always on derek.boone86 personal Google wi... | 1 |
| [i2v-still-ar-gate](i2v-still-ar-gate/SKILL.md) | use this before any Flow I2V — run the zero-token i2v-still-ar-gate.py so landscape stills cannot burn credits | 1 |
| [imagine-drive-port-originals](imagine-drive-port-originals/SKILL.md) | use this when porting Grok Imagine dump files to Google Drive as originals only — ALL seats destination is DerekBoone on derek.boone86; includes video... | 1 |
| [imagine-dump-ops](imagine-dump-ops/SKILL.md) | use this when running or babysitting a Grok Imagine History/library dump or heavy Imagine browser job on the shared box | 1 |
| [imagine-raster-generate](imagine-raster-generate/SKILL.md) | use this when executing Grok Imagine generates from a Max-lane-locked PASTE only — no silent LIVE lock edits; adults 18+ fiction; report land/filter; ... | 1 |
| [imagine-seat-preflight](imagine-seat-preflight/SKILL.md) | use this before any Imagine GMD/dump on imagine-dl or imagine-derek — enforce one Google account per seat, download dir, AUTH_GREEN chip, HD Priority,... | 1 |
| [last30days-research](last30days-research/SKILL.md) | use this when researching what people actually say about a topic in the last ~30 days with dated cited sources (last30days pattern; runs on research-c... | 1 |
| [nano-banana-4-up-best-pick](nano-banana-4-up-best-pick/SKILL.md) | use this when generating Flow/Gemini Nano Banana images for pipeline (always 4 gens then best-pick; Pro or NB2 for production, Lite for tests only), o... | 1 |
| [naughty-image-gem](naughty-image-gem/SKILL.md) | use this when compiling spicy / naughty / editorial figurative image prompts — run Mode A through A.U.R.A. Nano Banana V137.1 Gem before any Flow or G... | 1 |
| [ref2va-prompt](ref2va-prompt/SKILL.md) | use this when writing a MiniMax-H3 REF2VA prompt for Max on AlienPc — read the start image first (fabric opacity, wet/dry, light, crop), six sections,... | 1 |
| [research-core](research-core/SKILL.md) | Use this before any web research that has to produce cited claims (facts, trends, sentiment, news, best practice). It covers the shared plan, gather, ... | 1 |
| [setup-notify-card](setup-notify-card/SKILL.md) | use this when posting setup assumptions, actions, open questions, and verify checklists — ALWAYS tell Derrick in chat (and the CoS Needs-you list) any... | 1 |
| [shorts-analytics](shorts-analytics/SKILL.md) | use this when logging post-publish Shorts metrics on Ancient or Artframe — retention 0–3s, viewed-vs-swiped, AVD, hook tests; never invent views/RPM; ... | 1 |
| [shorts-best-prompting](shorts-best-prompting/SKILL.md) | use this when writing or auditing T2I/I2V/Deep Research prompts for Ancient History YouTube Shorts so kit nouns, SHOW/AVOID, hook-first, Path B quaran... | 1 |
| [shorts-continuity](shorts-continuity/SKILL.md) | use this when multi-clip Shorts need CONTINUITY_PASS before Scenebuilder/Public — kit/face/armor consistency, last-frame→next-clip match; AR alone ≠ P... | 1 |
| [shorts-editor-post](shorts-editor-post/SKILL.md) | use this when polishing Shorts after Scenebuilder/Artframe plate export — captions, VO bed, burn CONTEXT_PACK when/where + AI honesty; does not own Fl... | 1 |
| [shorts-flow-reference-i2v](shorts-flow-reference-i2v/SKILL.md) | use this before Helen/Ancient Flow I2V — locks reference-image tutorial craft + STILLS_APPROVED + cards + Classical kit Ingredients | 1 |
| [shorts-google-source-verify](shorts-google-source-verify/SKILL.md) | use this when verifying Shorts historical or Artframe art-history claims or cited URLs — independent web double-check against the trusted-site allowli... | 1 |
| [shorts-historian](shorts-historian/SKILL.md) | use this when locking historical accuracy + visual authenticity for Military/Ancient or Artframe lore packs — SHOW/AVOID, CONTEXT_PACK when/where, Tie... | 1 |
| [shorts-i2v-camera-motion-cards](shorts-i2v-camera-motion-cards/SKILL.md) | use this before Flow I2V — refuse if CAMERA_CARD/MOTION_BRIEF files missing OR stills not 9:16 OR STATUS≠STILLS_APPROVED_FOR_I2V; Artframe lane linked | 1 |
| [shorts-multi-clip-i2v-assembly](shorts-multi-clip-i2v-assembly/SKILL.md) | use this when assembling Ancient History Shorts from T2I stills + multi-clip I2V — prefer Flow Scenebuilder sequence download, then Editor captions/VO... | 1 |
| [shorts-policy-ypp](shorts-policy-ypp/SKILL.md) | use this when gating YouTube/YPP safety before Product QA/Studio Public on Ancient or Artframe Shorts — trust/synthetic disclosure; wrong-channel ban;... | 1 |
| [shorts-product-qa](shorts-product-qa/SKILL.md) | use this before any Ancient History or Artframe Short goes Public — refuse Public without VISUAL_QA_PASS; Auto-FAIL landscape/letterbox/ken-burns/miss... | 1 |
| [shorts-stills-first-approve](shorts-stills-first-approve/SKILL.md) | use this for Ancient History Shorts stills-first pipeline — History Gem keyframes, Derrick approve stills then animate prompts, then Flow/Scenebuilder... | 1 |
| [shorts-studio-ops](shorts-studio-ops/SKILL.md) | use this when claiming YouTube Studio for Ancient or Artframe uploads — sole seat chrome-profile-youtube-shorts; never Artframe→@derekboone704; Public... | 1 |
| [shorts-trends-research](shorts-trends-research/SKILL.md) | use this when researching viral hooks/formats for Military/Ancient History Shorts or Artframe/Mae-style art Shorts — write dated trend files with URLs... | 1 |
| [shorts-visual-qa](shorts-visual-qa/SKILL.md) | use this ALWAYS before APPROVE_STILLS / I2V / Public — history, anatomy, AI-slop, AND physics/coherence (screen direction, load paths, gravity, ropes)... | 1 |
| [single-session-exclusivity-capa](single-session-exclusivity-capa/SKILL.md) | use this when any live service kicks duplicate sessions (ESPN, ticketing, banking, auctions) so only one agent holds the browser seat | 1 |
| [tech-deals-watch](tech-deals-watch/SKILL.md) | use this when scanning for tech/AI/IDE/subscription promos Derrick might miss — Cursor Ultra bundles, SuperGrok, Google AI, Antigravity, credit sales;... | 1 |
| [token-efficiency-capa](token-efficiency-capa/SKILL.md) | use this when Derrick hits usage limits or asks to cut Grok Bot token burn across routines, chats, and fleet chatter. Wave 2 absorb (2026-09-24): uniq... | 1 |
| [youtube-shorts-ops](youtube-shorts-ops/SKILL.md) | use this when running Ancient History YouTube Shorts — includes mandatory stage owners (T2I/I2V/assembly/upload); Artframe lane uses artframe-ops inst... | 1 |
