# Marketplace parity matrix — Heavy ↔ Derek
Updated: 2026-09-12 ~2:48 AM CT (LEARN+PREVENT — clones SoT accepted)

## Skills (Heavy account global; Derek gets via templates/Add)
| Skill | Heavy | Derek target | Status |
|-------|-------|--------------|--------|
| last30days-research | ✅ on disk | via last30days bot + skill | Heavy ✅; Derek via clones-only / New Bot paste until authority clears |
| copy-humanizer | ✅ on disk | via Copy Humanizer bot | Heavy ✅; Derek pending |
| marketplace-parity-ops | ✅ on disk (protocol + SoT rules) | document on Drive handoff README | Heavy ✅; **never browser Add while other client owns `grokbot://`** |
| derek-bot-handoff | ✅ on disk (smoke-before-ready) | Drive bus | ✅ Heavy skill; smoke OPEN |
| tech-deals-watch | ✅ patched (country/currency, quiet watchlist, landed-cost) | optional absorb | Heavy ✅ |
| grok-bot-setup-playbook (Alfred rules) | ✅ | Alfred bot + playbook share | Heavy clone ✅; Derek pending |

## Marketplace bots
| Bot | Heavy | Derek | Status | Notes |
|-----|-------|-------|--------|-------|
| Alfred · Governance | ✅ CreateAgent clone `84d685ba-e5a6-4771-a7d4-97652c7cefe2` | **in progress / clones-only path** | Heavy = **accepted SoT (clone)** | Advisor only; does not replace CoS |
| Haggle · Savings | ✅ CreateAgent clone `cbdea2e7-9170-4c75-bf04-a859ed570b46` | **in progress / clones-only path** | same | Savings; never auto-send |
| last30days | ✅ CreateAgent clone `6af36770-edb6-48d0-bc9c-eff68ba3a91e` | **in progress / clones-only path** | same | Trend research |
| Copy Humanizer | ✅ CreateAgent clone `41be734b-a98c-421d-9a45-74aed4eaff76` | **in progress / clones-only path** | same | Copy QA |
| Researchy | SKIP (Research exists) | skip OK | skipped on Heavy | Complements Research — do not duplicate |
| SEO & AEO Desk | ✅ CreateAgent clone `f6f13a8b-81cc-4a61-baf8-6f13cb30a688` | **in progress / clones-only path** | same | Artframe SEO assist |
| Morning Newspaper | ✅ CreateAgent clone `d3393805-a522-4428-94b6-2c1b5d22e8b1` | **in progress / clones-only path** | same | Personal digest on Derek preferred |
| Overflow Research | template staged (UI v2) + public card scrubbed **PASS** | pending publish/Add | **HOLD publish** (Derrick) | Our handoff bot; SECURITY_AUDIT C14/C15 HOLD |
| Stills/Clips | SKIP Heavy | optional Derek | SKIP | No YT seat on Derek |

## Install path summary
| Account | Path used | Result |
|---------|-----------|--------|
| **Heavy** | Browser Add → wrong account (Derek) → **stopped** | Fallback: **6 CreateAgent clones = accepted SoT** until in-app Heavy Add proven. Soft cap ~45 / ~50. **clones ≠ marketplace imports** |
| **Derek** | Managed browser Add → handler fixed → **authority FAIL** (`deep-link: rejected reason=authority`) | **0 marketplace imports**. Path forward: **New Bot + paste Jobs** (computerUse) and/or Derrick manual in-app Add; twins = **in progress / clones-only** |
| **Overflow** | Scrubbed public card + SECURITY_AUDIT gates 1–13 PASS | Publish **HOLD** — staged ≠ public |

## Hard split (never “same”)
ESPN / Flow / Imagine / Studio seats = Heavy only.  
No `SendToAgent` across Heavy↔Derek — Drive `Grok_Bot_Handoff` only (personal Derek Drive).

## Voice
Grok Voice Agent Builder = separate telephony product (SIP / provisioned number). Google Voice = no connector; browser-only with explicit go.

## Box risk
RAM ~15GB, **no swap** — dual Electron (Heavy + Derek) risky; **quit unused client** before marketplace Adds / long UI.

## Protocol handler
- Desktop: `/home/box/.local/share/applications/grok-bot-derek.desktop`
- Default: `xdg-mime query default x-scheme-handler/grokbot` → `grok-bot-derek.desktop`
- Deep link form: `grokbot://app/v1/bot-template?id=...`
- **Rule:** never browser Add while other client owns handler; Heavy Adds = quit Derek / in-app only.

## SoT decision (2026-09-12 LEARN+PREVENT)
- **Heavy clones = accepted Source of Truth** for parity claims (MITIGATED/ACCEPTED wrong-account CAPA).
- **Derek twins = in progress / clones-only path** until authority clears or Derrick chooses manual in-app Add.
- Learnings: `/workspace/cos/learnings/2026-09-12-dual-setup-redteam-learnings.md`

## Update 2026-09-12 ~2:49 AM CT
- Heavy: CreateAgent clones = **SoT** (marketplace Add unsafe while Derek owns grokbot://).
- Derek: **8 New Bot twins** live (clones-only path). Marketplace Add still authority-FAIL.
- Drive bus smoke: **PASS** Heavy-side (outbox dual-meter-split-result + hostile STOP).
- Overflow public Publish: still host-card HOLD.
- Derek CoS · Overflow created; Google Drive **Connected** (personal) account-wide — closeout `/workspace/cos/status/2026-09-12-derek-failover-closeout.md` (~2:56 AM CT).
