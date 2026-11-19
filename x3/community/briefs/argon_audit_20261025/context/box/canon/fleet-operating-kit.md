# Fleet operating kit — durable canon
**Updated:** 2026-09-10 ~10:05 PM CT  
**Owner:** Chief of Staff  
**Skill:** [grok-bot-setup-playbook](sand-workflow:grok-bot-setup-playbook) (absorbed fleet-operating-kit 2026-10-19, ALI-87)  
**Research cite:** `/workspace/cos/research/grokbot-secrets-useful-templates-2026-09-10.md`  
**Seats:** `/workspace/cos/browser-seats.md`  
**Account×Product:** `/workspace/cos/research/fleet-exhaustive-2026-09-10/ACCOUNT_PRODUCT_MATRIX.md`

---

## Shared computer vs screens (not security)

- **One shared cloud VM** for all Bots on Derrick’s account — `/workspace` files, browser cookies/sessions, CLI credentials are shared.
- **Screens** are parallel computer-use work surfaces only. They are **not** a security or login-isolation boundary.
- One Bot = one computer-use task on its screen at a time.
- Seat exclusivity (`browser-seats.md` + [single-session-exclusivity-capa](sand-workflow:single-session-exclusivity-capa)) is **ops discipline**, not product isolation.
- Never invent Chrome (`chrome-profile-N` via bare `box-chrome` / DISPLAY `:5`). Named profile dirs only.
- Official: docs.x.ai overview · computer-and-apps · faq (see research S1).

## Auto Review ON + recommended Require Approval

- **Live:** `autoReviewInstructions.isEnabled` = **true** in `/home/box/sand-data/settings.json` (re-read this setup).
- CoS **cannot** toggle Auto Review by tool — Derrick Settings: [Auto Review](grokbot://app/v1/settings?id=auto-review).
- Auto Review covers shell, plugins, computer use, routine/automation writes, and **subagent / Cloud Agent launches**.
- Personal rules: **Require Approval** vs Always Allow (Require wins). Keep rules **narrow**.
- **Recommended Require Approval list (Derrick):**
  - Send email / outbound messages on Derrick’s behalf
  - YouTube Shorts **Public** publish
  - Delete Bots / bulk deletes
  - Drive wipe / bulk trash / share broadening
  - Pay / purchase / billing changes
  - Imagine generate or library move without Derrick “go”
- Do **not** “allow everything in the browser.”
- Current `allowInstructions` (3) are Chrome/sandbox/computer-use allows; `blockInstructions` is empty — hygiene still needs Derrick’s narrow Require rules in Settings UI.
- Official: research S6 · approvals-security · prod.cursor.com/docs/grok-bot/security.

## Secure secrets (no chat paste)

- Never paste passwords, tokens, OTP, passkeys, or payment details into chat.
- Use **secure secret request** (masked; excluded from transcript; not shown to the model) for supported connections.
- Otherwise: **computer takeover** — Bot hands the screen; Derrick completes 2FA / CAPTCHA / payment / identity.
- Prefer connectors (`@`) over browser when available; OAuth stays on the connector backend.
- Official: research S7 · computer-and-apps · approvals-security.

## Lanes (skills / routines)

| Lane | Owner | Skills / routines |
|------|-------|-------------------|
| Weekday brief | CoS | routine `weekday-morning-brief` · [cos-weekday-morning-brief](sand-workflow:cos-weekday-morning-brief) |
| Household money | Finance / CoS digest | routine `household-money-digest` · [household-money-tracker](sand-workflow:household-money-tracker) · personal Google only |
| Imagine dump / Drive | Imagine Director | [imagine-dump-ops](sand-workflow:imagine-dump-ops) · [imagine-drive-port-originals](sand-workflow:imagine-drive-port-originals) · [imagine-seat-preflight](sand-workflow:imagine-seat-preflight) · dual seats; dest DerekBoone GIL |
| Fantasy season | ESPN Seat + GM crew | routines waiver/Sunday · espn-single-seat-draft (archived 2026-10-19, ALI-87; see [single-session-exclusivity-capa](sand-workflow:single-session-exclusivity-capa)) · clicks only on `chrome-profile-13` |
| Shorts pipeline | Shorts crew / Flow Seat / Studio | [youtube-shorts-ops](sand-workflow:youtube-shorts-ops) · [shorts-product-qa](sand-workflow:shorts-product-qa) · Flow @9340 · Studio `youtube-shorts` · **PRODUCT_PASS** before Public |
| Adversarial CAPA | Fleet Auditor · CAPA | [adversarial-double-check-bot](sand-workflow:adversarial-double-check-bot) · [bot-fleet-audit](sand-workflow:bot-fleet-audit) · Friday `weekly-fleet-scorecard` |
| Box RAM / Chrome | CoS | [box-chrome-resource-capa](sand-workflow:box-chrome-resource-capa) · routine `box-ram-chrome-watch` + webhook |
| Setup / fleet kit | CoS | [grok-bot-setup-playbook](sand-workflow:grok-bot-setup-playbook) (absorbed fleet-operating-kit) · [setup-notify-card](sand-workflow:setup-notify-card) |

### Armed routines snapshot (2026-09-10)

| Routine | Recommended |
|---------|-------------|
| `weekday-morning-brief` | enabled |
| `household-money-digest` | enabled |
| `box-ram-chrome-watch` | **resume** (CoS) |
| `weekly-fleet-scorecard` | **resume** (Friday CAPA) |
| `fantasy-season-waiver-watch` | **resume** |
| `fantasy-sunday-lineup-check` | **resume** |
| `fantasy-tuesday-waiver-check` | keep **paused** (duplicate of season waiver) |
| `box-resource-webhook-alert` | enabled |

CoS resumes routines — executors do **not** call `update_state` for routine resume.

## Hard locks (pointer — playbook is source of truth)

- Imagine = `imagine-dl` **and** `imagine-derek` only — never profile-5 / CDP 9227 / box-chrome `:5`
- Drive dest = `gdrive_derek:Grok_Imagine_Library_DerekBoone/{Images,Videos}` only
- Flow = `chrome-profile-flow-derek` @ CDP **9340**
- Spark = `chrome-profile-3` @ CDP **9225**
- Studio primary = `chrome-profile-youtube-shorts`
- Shorts Public requires **PRODUCT_PASS**
- No Chrome invent · No deletes / email / pay / Public without Derrick go

## Pointers

| Artifact | Path |
|----------|------|
| This canon | `/workspace/cos/canon/fleet-operating-kit.md` |
| Fleet operating kit skill | merged into `sand-workflow:grok-bot-setup-playbook` (2026-10-19, ALI-87) |
| Setup playbook | `sand-workflow:grok-bot-setup-playbook` |
| Seats matrix | `/workspace/cos/browser-seats.md` |
| Account×Product | `/workspace/cos/research/fleet-exhaustive-2026-09-10/ACCOUNT_PRODUCT_MATRIX.md` |
| Secrets · Useful · Templates | `/workspace/cos/research/grokbot-secrets-useful-templates-2026-09-10.md` |
| Notify pattern | `/workspace/cos/notify/` + [setup-notify-card](sand-workflow:setup-notify-card) |

---
*Canon only — no deletes, email, pay, or Public actions from this file.*

## Compound engineering (full workflow)

**Skill:** [compound-engineering](sand-workflow:compound-engineering) · **DoD:** [close-out-verify](sand-workflow:close-out-verify) gate 7  
**Drive guideline:** `14_compound-engineering-full-workflow` (`1cPbCL5Ng7cpCmGoYddyjsZH_CZMYd2lrpzvJFtBGPt4`)

Loop: **Ideate → Brainstorm → Plan → Work → Simplify → Review → Polish → Compound → Repeat**

Aliases: `/CE Ideate` · `/CE Brainstorm` · `/CE Plan` · `/CE Work` · `/CE Simplify` · `/CE Review` · `/CE Polish` · `/CE Compound` · `/CE LFG`

Hard: chat claim ≠ done without close-out-verify + Compound LEARNED. Skill exists but not loaded = operator failure → patch same turn. Do not install Claude CE plugin on the shared box.
