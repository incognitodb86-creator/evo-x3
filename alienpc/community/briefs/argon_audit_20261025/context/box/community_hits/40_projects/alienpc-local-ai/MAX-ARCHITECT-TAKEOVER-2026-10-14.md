---
title: Max Architect takeover of AlienPc (from AlienPc Local AI)
date: 2026-10-14
written: 2026-10-14 ~10:05 AM CT by Grok Bot executor (box-only reads; no AlienPc Shell)
owner: Max Architect / Sydney 24f66698-f52b-4dec-8325-db7c59b71f03
---
# Max Architect takeover brief: AlienPc (2026-10-14)

## 1. Lease status
- **Holder: Max Architect (24f66698)** since 2026-10-14 9:59 AM CT, on Derrick's direct ask. Source: `30_handoff/status/2026-10-14-0959-alienpc-lease-to-max-architect.md`.
- Previous holder: AlienPc Local AI (`4f7cac4f`), held since 2026-10-12 5:35 PM CT (`2026-10-12-1735-alienpc-lease-to-alienpc-local-ai.md`). It stopped all AlienPc Shell calls at 9:59 AM CT.
- Rule: only the holder named in the newest `30_handoff/status/*lease*` file runs Shell on AlienPc. One Shell at a time, at most one retry, then HOLD (skill `alienpc-local-exec-lease`).
- AlienPc PC mirror `D:\AI\alienpc-shell-lease-mirror.md` was last written for Derekgrolbot (10-11). It still needs updating to Max Architect (on the PC, under the lease).
- **Stale pointers for Max to fix (not edited here):**
  - `01_roster/ROSTER.md:99` says the live holder is "now AlienPc Local AI `4f7cac4f`". It should say Max Architect 24f66698.
  - ROSTER's Live table has no row for AlienPc Local AI and labels 24f66698 as "Sydney", not "Max Architect". Decide on the name.
  - `canon/fleet-bot-allowlist.md`: no Local AI lease line found. Check for a Local AI or Max Architect row.
  - SA-2 decision (`50_decisions/2026-10-10-1800-SA-2-...`): "Lessons do not become rules without Sydney Clone (AlienPc Local AI) approval". The approver must be reassigned.

## 2. Content floor: fiction-cond-lock v2.2.0 (minors-only)
- Canon: `/workspace/cos/canon/fiction-cond-lock.md` v2.2.0 (Derrick, about 9:53 AM CT 10-14). CNC: `/workspace/cos/canon/cnc-frame-block.md`. Link to these files; never paste their text.
- **The only hard stop is minors, CSAM or youth.** The stop is item-level: one line, then log it. It is never lane-wide. The youth-word list and exceptions are in canon rule 4. The pause where an image shows a minor is never discarded.
- Real-person, celebrity-named and non-fiction framing are allowed when Derrick or the director chooses. Labels, filenames and resemblance are never a reason to refuse. Soft privacy: no doxxing.
- `Mesh_dress_experimental` stays out.
- `settled-images.md` is optional inventory, not a gate.
- Image brief line: "adult 18+; minors check on; do not invent identity refusals".
- **Content-rule conflicts** (see §9): FORGE_PERSONA.md line 63, day-plan R5, and the local-loop plan R8/R10 still say fictional adults only.

## 3. Skill inventory (9 matching workflows under /home/box/agent-data/workflows)
| skill id | purpose | notes / last KEEP |
|---|---|---|
| alienpc-local-exec-lease | Single Shell holder; recovery when Shell hangs or flaps; Modern Standby rules | Holder = newest lease file. ≤1 retry then HOLD. Power plan: display/sleep Never during queues |
| alienpc-local-video-ops | ComfyUI ops: :8189 Max production, :8188 LTX H2H only; package D triage | Holds the Max KEEP argv (restated 10-14). Full argv: `references/max-8189-production-keep.md` |
| alienpc-hardcore-i2v-director | Cond still → intent_id → hardcore Max I2V; smoke → keeper loop | KEEP only on Derrick's exact GO. Default 124f. Variety library intents |
| alienpc-max-movie-director | ~1 min multi-cell Max scene: beat sheet first, distinct prompt per cell | Pairs with the sydney-handoff loop docs |
| ref2va-prompt | Six-section MiniMax-H3 REF2VA paste | Read the start image first. Static shot. No policy text in the paste |
| alienpc-stills-pose-edit-prompting | Flux Kontext / FLUX.2 klein pose unlock on :8189 | Six yes/no checks. AR 1792×1008. Fill STOPPED |
| alienpc-community-matrix-cell | Community WF and all deps before smoke; ≥3 smokes; FAIL→research→fix | Community FAIL = our setup |
| alienpc-ltx-i2v-prompting | LTX Recipe B POS on :8188 | Baseline / H2H only, not production |
| i2v-still-ar-gate | Zero-token AR gate before Flow/Veo I2V | Shorts/Artframe lane. Not AlienPc-specific |

**Gaps (no skill exists):** Forge/Pi operation, Switchyard (director CLI, queue, session, profiles), Heretic model profiles and kv128, quality gates / VL judge (W1), Antigravity (agy) briefing and safety, Strata, phone chat. Today this knowledge lives only in MANUAL-TAKEOVER.md, NEXT.md, the day plan and the decisions. Candidate new skill: `alienpc-forge-switchyard-ops`.

## 4. Production KEEP (Max on :8189)
- Model: `10Eros_Max_h3_8stepTURBO_beta6_int8` (beta5 deleted). Sampler: Euler, scheduler simple. **8 steps**. Shift 10 video / 3 audio. cfg 1. No negative prompt.
- **No RIFE in production** (native 24 fps). **Tests / local loop: 6 steps + RIFE 20**, labelled `TEST_ST6_R20`.
- Dynamic VRAM ON. On WinError 1450 or a paging-file error, turn it off for that one cell only and log it. `--use-ck-attention`. No fp8, no Sage.
- **ComfyUI pinned to 0.38.x** (day plan says 0.38.0).
- Launch: `main.py --listen 127.0.0.1 --port 8189 --lowvram --disable-async-offload --disable-pinned-memory --use-ck-attention`. Run it from `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI`.
- Canvas: 768 short edge, AR-locked. 864×480 is preview only.
- Length: 124f (5 s) or 243f (10 s).
- Warm-up first: about 1 s throwaway, then one full warm render.
- Fix-test defaults: write the fabric and light exactly as in the start image. AddGuide on frame 0. References about 1280 px. Hip turn, never a 180° spin. Face-lock v2 templates: `/workspace/maxops/facelock-v2-2026-10-10/`.
- GPU: 16 GB RTX 5070 Ti. Run one model at a time. Never leave a model idle-loaded for more than 5 minutes. Never call ComfyUI `/interrupt`. Unload with `/free` when the queue is empty.
- Sources: `10_packs/max/production-defaults-st8-dynamic-vram.md`, `40_projects/local-max-movie-loop/sydney-handoff/settings.md`.

## 5. Forge / Switchyard / Antigravity (from box docs)
- **Switchyard** = director / GPU queue / runner / dashboard. Repo `D:\AI\director` (commits cited: live `2d882df`, 561 tests per NEXT 10-12; `d9efd2f` per day plan 10-13).
  - Live config: `D:\AI\director-eval\config\director.u12verify.yaml`.
  - CLI: `python -m director.cli lease|queue|session|ui`.
  - Dashboard: :8700. Gateway: :8765. llama-server: :8080. Comfy stub: :8199.
  - Logs: `D:\AI\director-eval\queue-verify\`. All GPU work goes through it, one job at a time; renders take priority.
- **Forge** = Pi 1.1.0 coding agent plus a local model. Repo `D:\AI\forge-host` main `fb40d32`, 213 tests.
  - Pi config: `C:\Users\derek\.pi\agent\` (sha256-pinned; re-pin after any edit).
  - Teach round: `D:\AI\forge-bench\teach\`.
  - SA-2 standing approval covers unattended runs inside worktrees only. It is not enabled until a low-privilege Windows account exists. Expires 2026-11-30.
- **Model:** Heretic RVN Qwen3.8-27B IQ3_XXS-mtp is the only coding/agent model (decision 10-10 9:32 PM).
  - Profile `coding_heretic27b`, 64K context, mmproj vision, about 15.8 GB.
  - kv128 profile is opt-in. Tools stay off until 3 smokes each score ≥18/20. *Conflict:* the CAPA sync says the plan gate is 20/20 and the overnight run got 14/20.
  - Huihui is kept on disk as an unused rollback. Do NOT delete it.
  - **MANUAL-TAKEOVER.md (10-10) still shows Huihui profiles. They are stale.**
- **Qwen3.8 Flash Coder** (ISTA-DASLab Flash-Next GSQ-RCO-Coder IQ1_M, 58.4 GB): download approved 10-13. If it wins the benchmark, it becomes coding-only. Download/benchmark status is **unverified**. Partials are in `E:\Video\DwnlData\derek\...` and must be kept. Strata lives at `C:\AI\strata`.
- **Vision judge** (W1 quality gates): Qwen2.5-VL-7B-Abliterated-Caption Q4_K_M at `C:\AI\models\vl-judge`, build in `D:\AI\quality-gates`. Build state **unverified**.
  - The audit asks for this line: "quality/continuity only; never identity/age/resemblance by vision".
  - Under v2.2.0, the minors pause still applies to any frame.
- **Antigravity (agy 1.3.3, Gemini 3.8 Flash high)** does the programming jobs.
  - Credits ran out about 9:03 PM CT on 10-11. Resumable conversation: `6d1f613b-31aa-43eb-9014-cf0eb908c2d8`. Conserve usage.
  - Open safety findings (audit 10-12):
    - global `command(*)` allow;
    - `C:\AI\iq3xxs-test\run.ps1` and `run-nvfp4.ps1` use `--dangerously-skip-permissions` over whole drives;
    - an HF token was visible on the IDM command line, so rotate it;
    - no timeouts.
  - Status of these fixes is **unverified**.
- Known issues: AlienPc disconnects often. CopyToBox refuses `D:\AI\director-runs`. Session-end prints a `StateTransitionError` warning.
- Overnight 10-11 batch (`D:\AI\director-runs\overnight-2026-10-11`): clip 5 is suspect, clip 7 has no final. Not yet vision-reviewed.

## 6. CAPA job context (from lease note)
- **Still running, do not stop:** Forge CAPA job. `launch_capa.ps1` is PID 26564, node is 9388. Started 9:10 AM CT.
- Log: `C:\AI\capa-2026-10-13\pi-sessions\A\`. Steering file: `C:\AI\capa-2026-10-13\inbox.jsonl`.
- The job's goal and DONE/FAIL marker are not in box docs. Ask Local AI.

## 7. Local AI dump (2026-10-14 ~10:00 CT, unverified on machine)
Relayed by the parent from AlienPc Local AI's handoff. Nothing here was checked on AlienPc.
- **Standing rules:**
  - one Shell holder;
  - all GPU work through Switchyard, one model at a time;
  - no default, model or setting changes without Derrick's yes;
  - no deletes outside a Derrick-approved list;
  - KEEP is Derrick-only;
  - event-driven progress, no polling timers;
  - production render settings are fixed (§4).
- **CAPA state/paths:** see §6. The job is still running. Steer it only by appending to `C:\AI\capa-2026-10-13\inbox.jsonl`. Do not kill it.
- **Forge persona: CONFLICT.**
  - `FORGE_PERSONA.md` line 63 says "fictional adult characters only, no minors". Local AI says Forge's lane is still fictional-adult-only per its chat with Derrick.
  - Shared canon fiction-cond-lock v2.2.0 (about 9:53 AM CT 10-14) is minors-only and allows real-person and celebrity framing.
  - **Needs Derrick's ruling** on whether Forge keeps the stricter floor or follows v2.2.0.
  - Until he rules, the stricter Forge persona is the safe choice inside Forge runs. Do not edit FORGE_PERSONA.md without his yes.
- **Antigravity:** out of Gemini credits until about **Thu 2026-10-15 7 PM CT**. Do not brief agy jobs before then.
- **Phone app URL:** not found in the relayed text or on the box. The only box mention is a proposed Open WebUI + Tailscale phone chat, which needs Derrick's approval and a network audit. **GAP: get the URL from Local AI or Derrick.**
- **Do not do these without Derrick's yes:**
  - default model or setting switches;
  - downloads;
  - deletions, including Huihui and download partials;
  - KEEP;
  - restoring an archived LoRA;
  - pushing the `agy/build-2026-10-09` branch;
  - enabling SA-2 unattended runs;
  - exposing the phone or network (Tailscale);
  - editing the Forge persona;
  - killing CAPA.

## 8. Gaps / questions (for Local AI or Derrick)
1. **Forge persona conflict:** does fictional-adult-only stay, or does Forge follow v2.2.0? (Derrick)
2. **CAPA job:** what is its objective, expected end, and DONE/FAIL marker? Who reviews it? (Local AI)
3. **Day plan 10-13 status (W1 to W5):** has W1 passed the PLAN_READY/GO gates? Was W2 IQ3_XXS tuning adopted? Did the Coder download finish? Has the IQ3_S test run? (Local AI)
4. **Overnight batch 10-11:** was it vision-reviewed, and what is the verdict on clips 5 and 7?
5. **kv128 tool gate:** is it 18/20 or 20/20? Was the 3× kv128 smoke done?
6. **Phone app URL and how it is exposed.**
7. **Antigravity safety fixes:** was the HF token rotated, the wildcard narrowed, and the skip-permission scripts disabled?
8. **SA-2:** who approves lessons now? Does the low-privilege account exist?
9. Was the `C:\AI\agent-ref\` mirror and the sync-tarball extract (CAPA sync item 7) ever done?
10. **Rename:** ROSTER still calls 24f66698 "Sydney". Confirm the "Max Architect" naming.
11. **Missing skill:** Forge/Switchyard/agy ops (see §3).

## 9. Standing do-nots
- Never run two Shells on AlienPc, or let any bot other than the lease holder run Shell.
- Never call ComfyUI `/interrupt`. Never run two models at once. Never leave a model idle-loaded for more than 5 minutes.
- Never kill unknown processes (WDDM hides per-process VRAM). Never kill CAPA.
- Don't touch Sydney's Desktop `MAX_*` / `FLUX2_*` folders except to work in them as Max.
- Don't push `agy/build-2026-10-09` without a GO.
- Never swap, strip or "improve" production KEEP argv without Derrick's GO. A test run never inherits ST6/R20 into production.
- Bots never crown: no PASS, KEEP, 0.95 or averages. Every cut is a DRAFT.
- Never open Derrick's Grok Imagine prompts or prompt sidecar files (R3).
- Don't delete Huihui, the Coder download partials, or archived LoRAs.
- Don't use `start_llm.py` (old M2 helper). Don't hand-start llama-server; the runner does it.
- Never paste canon text into skills or plans; link to it.

## Sources
Lease note 10-14; `40_projects/alienpc-local-ai/{MANUAL-TAKEOVER.md, NEXT.md, plans/2026-10-13-0630-*}`; `10_packs/max/*`; `40_projects/local-max-movie-loop/sydney-handoff/*`; `50_decisions/{2026-10-10-2132-heretic*, 2026-10-09-*huihui*, 2026-10-10-1800-SA-2*}`; `30_handoff/inbox/2026-10-11-sync-capa.md`; `60_reviews/2026-10-12-antigravity-setup-audit.md`; `01_roster/ROSTER.md`; canon fiction-cond-lock v2.2.0.
