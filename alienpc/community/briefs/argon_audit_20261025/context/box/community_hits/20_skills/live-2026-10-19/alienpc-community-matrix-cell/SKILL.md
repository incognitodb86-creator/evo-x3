---
name: AlienPc community matrix cell
description: >-
  use this for every AlienPc community matrix cell (A–G, C2, F retries) before
  queue and after FAIL — download community WF+all weights first, as-published
  smoke 1, ≥3 smokes, FAIL→research→fix, still AR wins, community FAIL=OUR
  SETUP; pairs with alienpc-local-video-ops
---
> **Current setup:** see [local-video-ops](sand-workflow:alienpc-local-video-ops) "Current setup" banner (single source; judge/identity/KEEP rules live there, stills rules in [stills pose-edit](sand-workflow:alienpc-stills-pose-edit-prompting)).

# AlienPc community matrix cell

## When
Every AlienPc community matrix cell on Comfy/LTX — before queue, after FAIL, before KEEP/abandon. Pairs with [alienpc-local-video-ops](sand-workflow:alienpc-local-video-ops).

**Production SoT B:** Flux+Max on **llama-swap :8080/comfyui** (backend :10002). `:8188` (LTX) and `:8189` are retired; old LTX matrix cells = archived baseline/H2H evidence only, no live LTX host. Max community smokes use MiniMax-H3 stock templates — not LTX GOLDEN.

## HARD — Download community WF + ALL deps BEFORE smoke (LOCKED 2026-09-25 ~14:11 CT Derrick CAPA)
1. If community/publisher ships a **10Eros (or target-stack) I2V + image-lock WF**, that is the baseline — **not** our freestyle graph.
2. **Before smoke 1:** download the **WF JSON + every required ckpt/LoRA/node weight**; verify each path on AlienPc disk; write a have/missing checklist.
3. When Derrick’s goal is **match community**, smoke 1 = **as-published community WF** (whole recipe). **Forbidden** as smoke 1: GOLDEN+one-knob, bare Official SS, “close one gap then invent the rest.”
4. Gap analysis vs our GOLDEN = name **downloads and diffs** — not permission to freestyle.
5. Do **not** queue a smoke that will fail for a missing weight you have not tried to fetch.
6. Derrick must never have to yell “download the existing workflows.”

## HARD — ≥3 smokes + frames after each (LOCKED ~13:55 CT)
≥3 smokes before quit/move-on. After EACH: frames + what failed → community/official RT → match community LoRA/settings → fix → next. Only after 3rd fail → mark down. Community working WF → replicate.

## HARD — FAIL → research → fix → then smoke (LOCKED ~13:52 CT)
After Identity/Quality/Motion FAIL: written why + legal fixes before next `/prompt`. Refuse seeds-only / Way-B / jump while root open.

## HARD — Condition still AR wins (LOCKED ~14:00 CT CAPA)
Still AR wins over published latent defaults. Prefer match latent ÷32 to still; don’t crop still to fit 960×544 unless Derrick picks that path. Preflight: still W×H · latent W×H · AR match.

## HARD — no-H benchmark (LOCKED ~13:56 CT)
Matrix2 H = archive only. Success = Identity+Quality+Motion vs Condition still + community/official recipes.

## HARD — community FAIL = OUR SETUP
Until written RT vs working community recipe + fix + ≥2 post-fix valids (quit ≥3). Community LoRA/settings = baseline. No abandon/jump/Likeness escape/Fix-C.

## HARD — no New Bot · Comfy single lease · I2V rebuild order · dial≠T2V
As prior locks: one client_id lease (one GPU job at a time; llama-swap's exclusive group swaps ComfyUI out if any other model in the group is called mid-job); I1→I2/I3→S1→M1→L1; Ingredients/bypass = METHOD only; review MD `job: I2V` or `job: METHOD`.

## Preflight (refuse queue if fail)
> 2026-10-19: this short checklist + the saved API workflow and ComfyUI's own validation (`POST /prompt` node_errors, `GET /object_info`) is the config check before each test; the 98-check preflight and per-clip judges are retired (Derrick 9:12 AM CT "Yes, retire them"; archive /workspace/cos/_archive/retired-gates-2026-10-19/).
- [ ] Community WF identified + **all deps on disk** (or Derrick-explicit control)
- [ ] As-published match when goal is community match
- [ ] Still W×H + latent W×H AR match
- [ ] Prior FAIL addressed with fix-first delta
- [ ] Live knobs read; no illegal grafts; output prefix set
- [ ] If cell is **Max/H3**: Comfy ≥0.30 native nodes · stock `video_minimax_h3_{i2v,t2v,r2v}.json` (1-min path prefer **r2v/REF2VA first**) · Max quant in UNET — **not** GOLDEN CondSafe/10S Recipe B graft · license NOT a CoS gate · ~4–15s/clip (1-min = multi-clip)

## After each smoke
Frames to Derrick + scores vs Condition still; RT; scoreboard; continue to ≥3 or clear watch.

## Canon
`/workspace/cos/research/alienpc-ltx-stack-2026-09-25/`

## HARD — overnight / Integrity / Max-first / scripts (pointers)
Do not fork full text — canonical under [local-video-ops](sand-workflow:alienpc-local-video-ops) `../alienpc-local-video-ops/references/`:
- overnight scout≠KEEP · fair one-axis · empty POS never winner · POS dialect by host → `overnight-horrible-capa.md`
- scripts thumbs/collage ONLY · no auto-score → `video-integrity-motion-amp.md`
- Max-first 10-step (~1-min) · Flux2 F1 deferred → `max-first-product-order.md`
- Flux2 stills fair order = stills lane METHOD only (cell1-first) — cite Plan `status/ce-plan-alienpc-fair-matrix-replicate-2026-10-02.md`

## EXPERIMENTAL / DO NOT DEFAULT
STEPS-20 / non-Turbo beta-25 A/B / SaveH3Embedding / dual Shell / Fill / GOLDEN-as-fake-community — see ops `../alienpc-local-video-ops/references/experimental-do-not-default.md`.
