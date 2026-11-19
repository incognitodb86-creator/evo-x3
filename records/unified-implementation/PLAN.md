---
title: "Unified implementation plan: F4 + Linux changes + Miraclein + REA-Video + Stills intake (single plan for review)"
date: 2026-11-19
type: plan
artifact_contract: ce-unified-plan/v1
product_contract_source: derrick-chat (t2631u, t2632u, t2640u, t2641u-t2646u)
execution: code
tier: T2 Durable (Derrick asked for a plan file; >1 device; four source plans)
author: Max Architect (executor subagent). PLAN ONLY. Nothing applied on the X3 or AlienPc.
audit: live read-only audit of AlienPc + X3, 2026-11-19 10:42-10:55 AM CT (section "Live audit")
review: skipped here; outside AI (Opus via GitHub Copilot) reviews this file on GitHub (Derrick t2631u)
pending_upload: true
---

Related: [Hermes two-path plan](../hermes-direct-render/PLAN.md) · [monorepo plan](../monorepo-consolidation/PLAN.md) · [Opus review (2026-11-19)](./REVIEW-20261119-opus.md) · source plans on `evo-x3-all` (blob SHAs verified 2026-11-19 ~10:28 AM CT):
[Linux LX1-LX9](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-18-alienpc-linux-plan-changes.md) `078da632` ·
[Miraclein M0-M5](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-19-alienpc-miraclein43-refmods-h3max-realism-plan.md) `ca1a6a94` ·
[REA-Video RV0-RV5](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-19-rea-video-h3max-beta7-plan.md) `591680d8` ·
[Follow-up F4](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-18-x3-alienpc-followup-plan.md) `f2120900`

# Unified implementation plan (F4 + LX + M + RV + ST)

**Status 2026-11-19:** Reviewed by Opus (`VERDICT: CHANGES`, [REVIEW-20261119-opus.md](./REVIEW-20261119-opus.md)); findings 1-15 and Derrick's 2026-11-19 decisions (mono delivery + Card 2 file-only go) applied in this revision; delta re-review pending.

## For Opus reviewer (read this first)

This is the ONE plan to review (Derrick t2646u). It stands alone: every fact it relies on is restated here with its live evidence. Copilot (Opus) sees only this GitHub repo; it has no access to the X3, AlienPc, Gitea, the QNAP or the chat.

**Source plans (GitHub `incognitodb86-creator/evo-x3`, branch `evo-x3-all`; blob ids re-hashed 2026-11-19 10:43 AM CT):**

| ID range | Path | Blob | Commit |
|---|---|---|---|
| Linux `LX1-LX9` | [plans/2026-11-18-alienpc-linux-plan-changes.md](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-18-alienpc-linux-plan-changes.md) | `078da632` | `1bca1b8` |
| Miraclein `M0-M5` | [plans/2026-11-19-alienpc-miraclein43-refmods-h3max-realism-plan.md](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-19-alienpc-miraclein43-refmods-h3max-realism-plan.md) | `ca1a6a94` | `e51ab03` |
| REA-Video `RV0-RV5` | [plans/2026-11-19-rea-video-h3max-beta7-plan.md](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-19-rea-video-h3max-beta7-plan.md) | `591680d8` | `05e8112` |
| Follow-up F4 `W* G* H* R* S* L*` | [plans/2026-11-18-x3-alienpc-followup-plan.md](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-18-x3-alienpc-followup-plan.md) | `f2120900` | `96b71aa` |
| Hermes two-path `U0-U9` (cross-linked, held) | [records/hermes-direct-render/PLAN.md](https://github.com/incognitodb86-creator/evo-x3/blob/u58/records/hermes-direct-render/PLAN.md) | branch `u58` | — |
| Monorepo `S0-S7` (cross-linked, held) | [records/monorepo-consolidation/PLAN.md](https://github.com/incognitodb86-creator/evo-x3/blob/u58/records/monorepo-consolidation/PLAN.md) | branch `u58` | — |

**What to check:**
1. Every source ID above appears in the item tables with an owner from the four doers (X3 Forge, AlienPc Forge, Hydrogen, Opus) or Derrick; nothing dropped, nothing invented.
2. The "Live audit" table: each claim names its live evidence. Flag any row whose evidence does not support its verdict.
3. Owner split: Opus only gets file-only work; nothing live, no GPU, no installs, no downloads, no secrets. Max only writes briefs, imports Opus commits, verifies RESULT files and handles secrets.
4. Stills intake (`ST1-ST5`): design and gates against the 18+ rule, the "never view PixlStash library contents" rule, and the in-chat render yes.
5. Inventory: every AGENTS.md / OPERATOR.md / skill / template used by the long-run video setup has a GitHub location you can open. Skipped files have a stated reason.
6. Conflicts with the Hermes and monorepo plans (table "Conflicts, overlaps, and holds").

**How your work comes back (import-and-apply; Derrick 2026-11-19 11:11/11:16 CT):** file work is done in VS Code on Derrick's PC (GitHub Copilot: Opus or Gemini), committed on `opus/<group>` branches, and pushed to GitHub branch `mono` (or the old part branches until `mono` is live; see "Which branch to edit"). Max fetches `mono` on the box, reviews the diff, runs gitleaks on the range, fast-forwards Gitea (if Gitea moved, merge on the box — never force), then the matching doer applies it on the machine under that machine's lease (using the `u58` Install line for copy paths) and verifies. A dirty secret scan rejects the whole commit.


PLAN ONLY for live hosts (Card 2 file-only work approved by Derrick 2026-11-19 11:11/11:16 CT; nothing applied on X3 or AlienPc until Max imports and the machine's Forge applies under lease). Source IDs are kept (`W*`, `G*`, `H*`, `R*`, `S*`, `L*`, `LX*`, `M*`, `RV*`); in briefs, prefix borrowed IDs to avoid collisions (`F4-S1`, `F4-R1`, `MONO-S5`, `HERMES-R6`, `AUD-A5`, `Q#` for cards 1-35). Under `ce-unified-plan/v1`, the Waves + Item tables stand in for `S#` steps, and key technical decisions (`KTD#`) / assumptions (`A#` with tests) live in the Product Contract, Conflicts (`C1-C17`), Live Audit, and Missing Info cards (`27-35`). No source item is dropped; optional items stay optional. Labels: VERIFIED = read live or hashed on 2026-11-19 between 10:28 and 10:32 AM CT, re-audited live 10:42-10:55 AM CT (America/Chicago); ASSUMPTION = must be tested in the step that uses it.

## Goal Capsule

| Field | Value |
|---|---|
| Objective | Carry out the four new reviewer plans as one sequenced body of work, without redoing what is already live, and without stepping on the Hermes or monorepo plans already on `u58`. |
| Means | Four doers (Derrick t2641u-t2643u): Opus/Gemini in VS Code on Derrick's PC for file-only work (pushed to GitHub `mono` via `opus/<group>`); X3 Forge (`/home/evo/AI/forge`) for live X3 work; AlienPc Forge (`C:\Users\derek\forge`) for live AlienPc work and, over `ssh x3` / `ssh x3-evo`, X3 builds and tests when X3 Forge is idle and has released the X3 lease; Hydrogen (`agy` on the X3) for hard live coding/scoring. Each live job is a one-line goal + `records/<id>/BRIEF.md` → `RESULT.md`. Max writes briefs, imports Opus commits, verifies RESULT files and handles secrets. Flux and ComfyUI stay on AlienPc, prompts are written on the X3. |
| Authority | Derrick t2631u (pull the four plans; ce-brainstorm + ce-plan; conserve usage; Forge + Hydrogen; Flux/ComfyUI on AlienPc, prompts on X3) and t2632u (fourth owner: Opus on GitHub for file-only work). |
| Also in this file | Stills intake `ST1-ST5` (t2645u) and the AGENTS/OPERATOR/skills/templates inventory with GitHub locations (t2644u). |
| Out of scope until their own yes | Hermes two-path setup (`records/hermes-direct-render/PLAN.md`). Monorepo merge (`records/monorepo-consolidation/PLAN.md`, Q1-Q7 still open). The Linux dual-boot plan itself (rev 4, reviewed NOT READY Nov 16) — `LX1-LX9` amend that plan; they are not a go to install Linux. QNAP general cleanup (deferred). |

## One-page summary

Four sibling plans landed on GitHub `evo-x3-all` this morning (blob SHAs above, VERIFIED). F4 is the trunk: X3 Gufo stays primary for daily chat and coding, AlienPc stays render-first with opportunistic Swift (`ESP off`) when idle, and the specialized tracks (Linux amendments, Miraclein RefMods + realism LoRA, REA-Video shot breakdown) hook into F4's writer bakeoff (`W1-W4`), safety (`S1-S2`), speed tests (`R1-R7`), and Hermes closeout (`H1-H6`).

Work is done in waves so independent tracks run in parallel. File-only work is handed to Opus on GitHub (Copilot can only see GitHub). Max fetches that commit, reviews the diff, scans for secrets and fast-forwards Gitea to the same SHA; X3 Forge or AlienPc Forge then applies it under that machine's lease and verifies. Live runs, installs, downloads, GPU work and test graphs go to X3 Forge, AlienPc Forge (which can also run X3 tests over SSH) or Hydrogen; secrets stay with Max; renders queue only on Derrick's Hermes-chat yes. A new Stills intake track (`ST1-ST5`) fixes the same-still problem, uploads, slow imports, no-image and pose/background references.

**AlienPc Forge is live** (VERIFIED live, audit A1-A5): pi chats in herdr workspace `w2V` at `C:\Users\derek\forge` (a junction to `C:\Users\derek\5slock`, not a git repo), newest session written 7:26 AM CT, default model `coding_swift15_iq3s_esp` on AlienPc llama-swap; Render's AlienPc chat is at `C:\AI\render`. Since today it reaches the X3 over SSH (`ssh x3` = derekboone, `ssh x3-evo` = evo; audit A3), so it can also build and run X3 tests. AlienPc-side scripts, installs, Comfy node setup and still graphs go to AlienPc Forge with a BRIEF and RESULT file, only while `:8447` says idle; Max verifies. Prompts and queueing stay on the X3 as now (`render-pi.sh` / `render_writer_pipeline.py` / `queue-remote.sh`).

Remaining Antigravity / Hydrogen usage is **UNKNOWN**: `agy` on the X3 has no stock usage or quota subcommand (VERIFIED `agy help`, 10:31 AM CT). Use Hydrogen only where a strong live coding or scoring pass is worth it (`W1` analysis, hard packages if Opus does not take them). Prefer Opus for file-only work so both Max and Hydrogen are saved.

Nothing below starts until Derrick (or Opus's review plus Derrick's yes) says go.

## Derrick's asks (word for word, with pass test and gate)

| ID | Ask | Pass test | Gate |
|---|---|---|---|
| R-ASK1 | Pull the four new plans and implement all of them the best way, conserving usage. | This file lists every source ID from those four plans, with owner, machine, lease, verify artifact, and rollback. No ID is dropped. | Max (this plan). Execution starts only on Derrick's yes. |
| R-ASK2 | Use X3 Forge and AlienPc Forge where they can, and remaining Hydrogen, so Max's usage stays low. | Each item names one of the four doers (Opus, X3 Forge, AlienPc Forge, Hydrogen) or Derrick. File-only items prefer Opus. Max is brief / import / verify / secrets only. | Owner column in the item table. |
| R-ASK3 | All Flux and ComfyUI work continues on AlienPc, with prompts and writing made on the X3 like the current setup. | No second ComfyUI, no Flux/Comfy work on the X3, no in-graph writer after the approval hash. Prompts come from X3 Gufo / `W1-W3` winner / later Hermes paths. | S2 allowlist (no LLM nodes); standing render path. |
| R-ASK4 | Fourth owner: Opus on GitHub for file-only work. Max pulls the commit, scans it, fast-forwards Gitea; the machine's Forge applies it. | Every item is marked Opus-eligible or not. The import-and-apply step below is followed after each Opus commit. | Max-apply; secrets scan must be clean. |

## Live audit (2026-11-19, 10:42-10:55 AM CT, read-only)

Derrick t2640u: the earlier draft said there was no AlienPc Forge because it read only repo files. Every current-state claim below was re-read live on AlienPc (PowerShell) and the X3 (`ssh`, `sudo -n -u evo`). Nothing was changed on either machine. Sydney's chats, persona and memory were not opened; PixlStash library contents, tags, names and its journal were not read (counts and service stats only).

| # | Claim (where) | Live evidence | Verdict |
|---|---|---|---|
| A1 | AlienPc Forge is live at `C:\Users\derek\forge` (summary, owners) | `herdr pane list`: workspace `w2V`, pi panes `w2V:p3` and `w2V:p7` titled "π - forge", cwd `C:\Users\derek\forge`; sessions in `.pi\agent\sessions\--C--Users-derek-forge--\`, newest written 7:26 AM CT. `forge` is a junction to `C:\Users\derek\5slock` (its README); it is not a git repo. | CORRECT (detail added) |
| A2 | Max does AlienPc installs and GPU steps "until a Forge exists there" (owners, Max row) | AlienPc Forge exists (A1). | WRONG, removed. AlienPc live work is AlienPc Forge's. |
| A3 | AlienPc Forge cannot reach the X3 (implied by earlier owner rows) | `ssh x3` → `derekboone@evo-X3`; `ssh x3-evo` → `evo`, lists `/home/evo/AI/{community,forge,render}` (10:44 AM CT). `~\.ssh\config` has `Host evo-x3-1 evo-x3-1.tailf242b2.ts.net x3` (derekboone) and `Host x3-evo` (evo), key `x3_alienpc_ed25519`. Forge's global AGENTS.md section "EVO-X3 access" tells it to use `C:\Users\derek\forge\x3run.ps1` (bash as `evo`, `-AsDerek` for derekboone) and `x3put.ps1` (small files). | FIXED by Max today (t2641u-t2643u); AlienPc Forge can build and run X3 tests. |
| A4 | AlienPc Render chat at `C:\AI\render` | pane `w35:p1` "π - render", session started Nov 18 9:26 PM CT, last written 7:40 AM CT. No `OPERATOR.md` on AlienPc; `C:\AI\render\AGENTS.md` is tracked. | CORRECT |
| A5 | AlienPc Forge model | `.pi\agent\settings.json` `defaultModel: coding_swift15_iq3s_esp` (AlienPc llama-swap `127.0.0.1:8080`, Strata at `C:\AI\strata-0.2.7`; the yaml header still says Strata 0.2.8). | NEW FACT. F4/H1c say opportunistic Swift with ESP **off**; AlienPc Forge's own default is the `_esp` slot. See card 21. |
| A6 | X3 Forge at `/home/evo/AI/forge` (owners, grounding) | pi panes `w4:p1` ("Forge-X3"), `w4:p2`, `w4:p3`; repo branch `u58-chat-read-plan` = `gitea/u58-chat-read-plan` `4cbbba0`, clean. `AGENTS.md` is a symlink to `../community/agent-shared/AGENTS.md`. | CORRECT |
| A7 | X3 Render | pi panes `w3:p1-p4`, cwd `/home/evo/AI/render`, local branch `x3-linux` tracking `gitea/x3-render` `9232545`, 1 modified data file (`writer_pipeline/dialogue_blacklist.jsonl`). **Branch-name trap (Finding 15):** GitHub `x3-linux` (`6bdcc49`) is the **community** tip, not render. Briefs must always name the remote branch (`x3-render`, or `mono` path `x3/render/`) and never `x3-linux`. | CORRECT (trap noted) |
| A8 | Sydney | X3: no pi process in a Sydney folder. AlienPc: herdr workspace `w31` cwd `C:\Users\derek\sydney`, PowerShell only, no pi agent. Not opened. | exists; not read |
| A9 | Hydrogen = `agy` on the X3, usage unknown (summary, grounding) | `agy` at `/home/derekboone/.local/bin/agy` (not on the evo user). 3 agy runs alive since Nov 18 (2x `gemini-4-hydrogen-high`, 1x `gemini-pro-orchestrator-g1-pro`). `agy --help` has no usage/quota flag. AlienPc also has `agy.exe`. | CORRECT; usage still UNKNOWN |
| A10 | X3 daily driver = Gufo `0.35.0` `flash-next-uncensored-v2`; Halogen cold (Product Contract) | running container `llama-swap-flash-next-uncensored-v2`, `gufo version 0.35.0 (0260e11)`; `hooks.on_startup.preload: flash-next-uncensored-v2`; profile `halogen-only` pins `flash-next-uncensored`, `flash-next`, `gemma4-heretic` (+`-sub`) to `flash-next-uncensored-v2`. Halogen slots defined, not running. `embed-small` also resident (`:8083`). | CORRECT. Hermes plan R8 called this "Halogen"; corrected there. |
| A11 | Ports up: 8080, 8642, Tailscale 8443/8445 (grounding) | Loopback: 3000 Open WebUI, 7878 hub, 8080 llama-swap, 8081 Gufo, 8083 embed, 8642 Hermes, 8888 SearXNG, 9537 PixlStash. `tailscale serve status` (tailnet only): 443→8080, 8443→3000 + `/renders/`→`/mnt/qnap/renders/runs`, 8444→7878, 8445→9537. | INCOMPLETE, fixed |
| A12 | "Tailscale Serve stays off unless a separate yes" (H1d, cards) | Serve is already ON on both machines (tailnet only). AlienPc: 8443→7878, 8444→7889, 8445→9537, 8446→llama-swap `/upstream/comfyui_auto`, 8447→8086 (`gpu_lock_gate.py --fail-if-busy`). | WORDING WRONG. Meaning kept: no NEW Serve port without Derrick's yes. |
| A13 | Idle probe `:8447 --fail-if-busy` (H1c, AlienPc Forge) | 8447 → `127.0.0.1:8086` `gpu_lock_gate.py --port 8086 --fail-if-busy` (started 7:10 AM CT); 8085 is the plain gate. | CORRECT |
| A14 | AlienPc ComfyUI `0.38.0` at `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` (Product Contract) | `comfyui_version.py` 0.38.0; started on demand by AlienPc llama-swap model `comfyui_auto` (ttl 900); second instance `comfyui_longvideo` at `C:\AI\comfy-longvideo\ComfyUI` (0.38.0). Neither running at 10:47 AM CT (GPU 478 MiB, 0 %). No `gpu-render.lock`. | CORRECT |
| A15 | S1 Manager `strong` not done | both `user\__manager\config.ini`: `security_level = normal`. | CORRECT (open) |
| A16 | M0/M1: MiniMaxH3Mod at `517e8c41` | `git log -1` = `517e8c4`. `_archive\20261119_pre_miraclein` absent. | CORRECT (M0 not started) |
| A17 | M3/card 19: TE + VAE "if missing (~9 GB)" | `models\text_encoders\qwen_3_8b_fp8mixed.safetensors` 8.07 GB and `models\vae\flux2-vae.safetensors` 0.31 GB present. Not present: `ComfyUI-Flux2Klein9Mod`, `models\refmods-klein9\`, Miraclein weights, `h3-realism-people-t2v-i2v-r2v.safetensors`. | TE/VAE already there: no ~9 GB download. Fixed. |
| A18 | R2 compares `beta7_activation_learned_HQ` vs `int8HQ` (no download listed) | Only `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` (22.9 GB) is on disk; `activation_learned_HQ` has only a HF cache `.metadata` stub. | WRONG: R2 needs a re-download (>5 GB, Derrick yes). Fixed + card 22. |
| A19 | pytraveler rewriter node | `custom_nodes\MiniMax-H3-Prompt-Rewriter-ComfyUI` at `c8fca44` (local commit "Accept autogrow ref_* kwargs…", dir created Oct 5). Also enabled: `ComfyUI-MiniMaxH3-Prompt-Writer`. | CORRECT (F4). It is installed and enabled in production ComfyUI; S2 must keep LLM-node graphs off the allowlist. |
| A20 | REA-Video `RV0`: clone on the X3 needs a yes | No clone on the X3, no `~/.rea-video`. AlienPc already has `C:\Users\derek\forge\tools\rea-video` (upstream `JuneYaooo/rea-video` `e385853`, cloned Nov 17 9:43 PM CT, no venv) and its skill is linked into AlienPc pi. | NEW FACT. RV0 still needs the X3 clone (CPU decompose next to Gufo); AlienPc copy is reference only. |
| A21 | aria2 downloader on the X3 | `aria2 1.37.0` RPM installed Nov 15 8:56 AM CT; config dir `/home/evo/.config/aria2`; tracked copy `hosts/x3/live/aria2/aria2.conf`. AlienPc: no `aria2c`. | DONE on X3 (not in this plan's open list) |
| A22 | Tools | X3: git, gitleaks, uv, ffmpeg, herdr, pi, tailscale present; `gh` absent (by rule); `git-filter-repo` absent on X3, AlienPc and the box. AlienPc: git, gh, gitleaks (`C:\AI\tools\gitleaks`), uv, ffmpeg, node, herdr 0.9.5. | Monorepo A2 still an assumption (install needed on the box). |
| A23 | X3 `~/evo-x3` at `e03d666` (grounding) | at 10:45 AM CT audit was `dcb91e5` (behind `u58` `e0c446f` / `65fa220`); 96 untracked paths (not opened). | STALE, updated |
| A24 | X3 disk ~936 GB free | `df`: 935 GB free on `/` (= `/srv`). AlienPc: C: 125.7 GB, D: 27.7 GB free. | CORRECT (M0 ≥25 GB passes on C:) |
| A25 | X3 lease | `/home/derekboone/AI/locks/x3-lease.txt` exists, 0 bytes (local lock stub only; authoritative lease record is the brain `30_handoff/status/*-evo-x3-lease-*.md` / `records/status/` per `records/evo-x3-lease-README.md`; see "Leases" below). | — |
| A26 | AlienPc global AGENTS.md "is a hard link of `C:\AI\community\agent-shared\AGENTS.md`" (its own line 1) | git hashes differ (`e6a57d9` vs tracked `f0a2141`). | WRONG in that file; both copies now in GitHub (Inventory). Fix is an Opus item (`INV1`). |
| A27 | Monorepo plan's live-checkout list | Omits AlienPc Forge (`C:\Users\derek\forge` → `5slock`, not git) and the AlienPc global pi folder. | GAP, fixed in monorepo plan |
| A28 | Monorepo: AlienPc dirty counts 131 / 9; remotes with embedded login | `git status --porcelain` count 131 (`C:\AI\community`) and 9 (`C:\AI\render`); both `gitea` remotes carry a login in the URL (value not shown). HEADs `6dadffc` / `5c3450d` = `gitea/alienpc-community` / `gitea/alienpc-render`. | CORRECT |
| A29 | X3 PixlStash health (input to `ST3`) | `pixlstash` 2.0.1; `MemoryCurrent` 8.90 GB vs `MemoryHigh` 8 GB; swap at its 2 GB cap; cgroup `memory.events high` = 2,370,429 since 8:50 AM CT; CPU 8,046 s in ~2 h (~113 %); one `import_inbox.py` running 2.5 min with 5 files in the inbox. | NEW FACT (cause of slow import, see ST3) |
| A30 | `hosts/SETUP-MAP.md` lacks AlienPc Forge | grep: only X3 Forge rows. | CORRECT (Opus item `INV2`) |
| A31 | Source blob ids | `git rev-parse origin/evo-x3-all:<path>` = `078da632`, `ca1a6a94`, `591680d8`, `f2120900`. | CORRECT |

Could not verify: remaining Hydrogen/Antigravity quota (no command); the size of the `activation_learned_HQ` file (not on disk); whether llama-swap actually serves the `halogen-only` pins at runtime (config read only; `/running` needs the llama-swap key, not used).

### Corrections carried into the cross-linked plans (same commit)

- Hermes plan: R8 said the model is "Halogen/llama-swap `flash-next-uncensored`"; live, that name is pinned to Gufo `flash-next-uncensored-v2` (A10), so O4 is answered at config level. "Who finishes" said Max does U0-U9 himself; now X3 Forge applies U0-U9 from a brief, Max handles the WebUI password file and verifies. D3/Serve wording aligned with A12. Cross-link to `ST2` added.
- Monorepo plan: live-checkout list now includes AlienPc Forge (`C:\Users\derek\forge` → `5slock`, not git) and the AlienPc global pi folder, with `hosts/alienpc/live/` as their tracked copy; `git-filter-repo` missing on the box/X3/AlienPc noted (A22); S5/S6 owners moved to X3 Forge / AlienPc Forge.

## Product Contract (merged requirements, short)

Brainstorm was kept short: the four source plans already state what to build. This section only records the merge, the overlaps, and the conflicts. There is no separate ce-brainstorm file.

- Keep live state from F4 section 0: Gufo `0.35.0` `flash-next-uncensored-v2` is X3 daily driver and primary coder; do not redo G0; do not switch X3 to Swift 1.5 today; Halogen stays cold rollback. `U56 Decision #1` (header-free Beta 7) and `U56 Decision #2` (no voice ref on named parodies) stay in force.
- Shared contract for every Beta 7 prompt path (writer pipeline, duckyshell, pytraveler, REA-Video, later Hermes Path A/B): one `beta7_convert.py` + live `lint.py`. No second converter.
- Flux / Klein9 / Miraclein / H3 LoRA / ComfyUI node work: AlienPc ComfyUI `0.38.0` at `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` only, under lease, git-clone installs (never Manager web UI once `S1` is `strong`).
- Every H3 render needs Derrick's yes in his Hermes chat. `queue-remote.sh` already runs RTX 2x; `sync-renders` publishes only clips with `render_ok.json.upscale`.
- `pi-job code` / `review` stay. Only the render part of `pi-job` may retire later, and only on Derrick's yes after the Hermes bakeoff (Hermes plan R13). `H1` flips coding to X3-primary; it does not retire render.
- Never view PixlStash library contents. `M2` may use stills Derrick picks or a path list; Max counts only.
- Gitea is primary on the box. Per Derrick 2026-11-19 (11:11/11:16 CT), file-only work is authored in VS Code on Derrick's PC on `opus/<group>` branches and pushed to GitHub `mono` (new monorepo); Max fetches `mono` on the box, reviews, runs gitleaks, fast-forwards Gitea (or merges if Gitea moved; never force), and keeps GitHub and Gitea synced. No force push. No `git add -A`.

## Conflicts, overlaps, and holds

| # | Conflict or overlap | Rule in this plan |
|---|---|---|
| C1 | Hermes two-path plan vs `H4` skill prune vs `W3` duckyshell | All three share `beta7_convert.py` and `lint.py`. `H4` must keep / adapt the planned `h3-writer` skill (Path B) and `OPERATOR.md` desk; it must not invent a third writer path or install an unguarded ComfyUI MCP. Hermes U0-U9 stay held until that plan is reviewed and Derrick says go. |
| C2 | Monorepo vs all file work | Per Derrick 2026-11-19 (11:11/11:16 CT), file-only work lands on `opus/<group>` branches and is pushed to GitHub `mono` (see "Which branch to edit" for `mono` folders; keep the old part-branch names until `mono` is live). Do not start live symlink/junction cutover (`MONO-S5`/`S6`) in the middle of path-sensitive live applies; freeze first. |
| C3 | `G2` template `unet_name` vs `R2` `activation_learned_HQ` | `G2` may switch the three beta6 templates to `beta7_int8HQ` first. If `R2` wins, update those three (and others) to the winner in one follow-up, still without changing size/frames. Never overwrite locked templates in place; edit copies then promote on yes. |
| C4 | `W4` gemma4 pin vs `G6` (Sydney) | Do `G6` (Derrick card) before any `W4` change to the `gemma4-heretic` pin. Do not open Sydney's persona, chats, or memory to decide this. |
| C5 | `W3` item 3 (API Universal Writer) is the same decision as Linux review D3 / `LX8.1` | One yes for both OSes. If kept: FX6 leak test, `MINIMAX_H3_API_ADMIN_TOKEN`, and Linux vault key later. If dropped: AlienPc holds no LLM key. In-graph writers stay off the `S2` allowlist either way. |
| C6 | `S2` allowlist is also `LX8.2` / review BL3 | One allowlist for Windows now and Linux later, including the 3-node `remote_upscale.py` RTX VSR graph. Promote Miraclein / Realism templates only after Derrick's A/B yes. |
| C7 | `LX3` is `S1` (Manager `strong`) | Do `S1` once on Windows now; Linux build starts from the same setting. |
| C8 | `LX4` needs `R1-R7` first | Linux U10 must compare against tuned Windows, not today's untuned baseline. Do not start Linux dual-boot work in this plan. |
| C9 | `RV2` depends on `W3` `beta7_convert.py` and `H5` `cookiecutter-uv` harness; writer model is the `W1-W3` winner (or live Gufo until then) | Build the converter and harness in Wave 1. `RV0` (CPU decompose + one Gufo lint) can start in parallel and does not wait for the winner. `RV3` waits for a converter, a frozen template, and Derrick's render yes. |
| C10 | REA-Video mentions `P4.11` ntfy codes and in-chat yes | In-chat Hermes yes is mandatory for every H3 render. `P4.11` is a phone-side supplement, not a bypass. |
| C11 | `H1` vs Hermes plan on `pi-job` | Flip coding to X3-primary (`H1`). Do not retire `pi-job render` until the Hermes bakeoff winner is chosen and Derrick says yes. |
| C12 | `M2` PixlStash stills vs no-view rule | Derrick picks the 6-12 stills (or a path list). Max and Forge do not open the PixlStash library or name tags. |
| C13 | Closed-source rule (only Halogen allowed) | Confirm `duckyshell` Standalone license is open before `W3b` install. Miraclein is a Civitai weight Derrick already planned; still needs his yes at download time (login is his). No other closed software. |
| C14 | Downloads over ~5 GB | `W2` arms (15-18 GB) and FP8 fallback (8.46 GB) each need a yes (Miraclein TE `qwen_3_8b_fp8mixed` + `flux2-vae` are already on AlienPc, A17). NVFP4 is 4.82 GB: still ask, because it is close and Civitai login is required. REA-Video CPU caches (~67+149 MB) are under the bar; still mention them at `RV0` yes. |
| C15 | `evo-x3-all` is a snapshot | Reviewer plan commits already landed there. Do not edit `evo-x3-all`; file-only work lands on `opus/<group>` branches and pushes to GitHub `mono` (or the live part branches until `mono` is live). Max imports on the box (fast-forward Gitea, or merge if Gitea moved; never force) and mirrors back to GitHub. |
| C16 | Hermes plan vs unified `R5`, `L1-L8`, `ST3` (Finding 10) | Hermes plan line 91 says it does not change `queue-remote.sh`, `run_queue.py`, or `sync-renders`, while unified `R5`/`L2`/`ST3` change them. Rule: no `R5`/`L*`/`ST3` apply during the Hermes bakeoff window (or re-baseline after apply), and Hermes `R6`'s "new PixlStash entry exists" check waits for `ST3`'s detached `pixl-import` unit to complete. |
| C17 | Cross-plan: Monorepo `MONO-S2`/`S5`/`S6` vs Forge owners (Finding 9) | Tracked in [records/monorepo-consolidation/PLAN.md](../monorepo-consolidation/PLAN.md) (owned by the monorepo chat; not edited here). `MONO-S5` renames `/home/evo/AI/forge` (X3 Forge's own cwd), so X3 Forge cannot run `S5` on itself — hand `S5` to AlienPc Forge over SSH or Max; `MONO-S2` freeze also requires no Forge job running. `MONO-S6` junction-swaps `C:\AI\community` under AlienPc Forge's skill links — stop AlienPc Forge pi panes first and re-test skill links after swap. Monorepo R5 "mirror via gh" must run on the box (not X3, where `gh` is absent by rule, A22). |

## Owners and usage strategy (four doers, Derrick t2641u-t2643u)

| Owner | What they do | What they never do |
|---|---|---|
| **Opus on GitHub** (VS Code Copilot: Opus or Gemini) | File-only work in VS Code on Derrick's PC, committed on `opus/<group>` branches and pushed to GitHub `mono` (or part branches until `mono` is live): AGENTS.md, OPERATOR.md, SOUL, skills, config *text* (llama-swap.yaml, Hermes `config.yaml`, pi settings, systemd unit text), briefs, docs, scripts and templates that need no live run, unit tests that run offline. Preferred for all of that (t2632u). | Live runs, installs, downloads, GPU, secrets, test renders, Gitea, X3, AlienPc, force pushes. |
| **X3 Forge** (`/home/evo/AI/forge`, pi panes `w4:p1-p3`) | Live X3 work from a one-line goal + `records/<id>/BRIEF.md`; writes `RESULT.md`. Applies imported Opus commits on X3 checkouts under the X3 lease, runs `wp_accept`, `RV0`, `RV2 make check-all`, `H1` concurrency test, `H5` sample, unit tests, Hermes U0-U9 config. | Starting renders without Derrick's Hermes-chat yes. Editing `llama-swap.yaml` during a render. Handling secret values. |
| **AlienPc Forge** (`C:\Users\derek\forge` → `5slock`, pi panes `w2V:p3`/`p7`, model `coding_swift15_iq3s_esp`) | Live AlienPc work from a BRIEF/RESULT: Comfy node installs (git clone + pip, never Manager UI), template candidates, R1-R7 setup steps, S1/S2 apply + planted-graph test, M0-M4, ST4/ST5 graphs, Phase 5 checks. **Standing-rule prerequisite (Finding 1):** `hosts/alienpc/live/pi-agent/AGENTS.md` line 35 currently forbids stopping/restarting/reconfiguring llama-swap, gpu_lock_gate, Strata, or ComfyUI install/config; Derrick must approve `INV1b` (scoping line 35 to "unless a BRIEF with a Derrick id names the change") before any AlienPc Forge live step (`S1`, `M1`, `M3`, `R3`, `R4`, `R6`, `R7`, `W3c`, `H1d`). **GPU-sharing rule (Finding 2):** its own LLM (`coding_swift15_iq3s_esp`) shares the 16 GB GPU with `comfyui_auto`, so before GPU steps (`S2`, `M0-M5`, `ST4/ST5`, `R1-R7`) test what `:8447 --fail-if-busy` reports while Swift is loaded and run either (a) pointed at X3 Gufo over tailnet or (b) via a fixed script whose result Forge reads afterward (Cards 21, 29). **Also builds and runs X3 tests** over SSH (`ssh x3` / `ssh x3-evo`, or `x3run.ps1` / `x3put.ps1`) **only after X3 Forge releases the X3 lease** (under its own take/release files, never while X3 Forge holds the lease). GPU work only when `:8447` (`--fail-if-busy`) says idle; follows `C:\AI\locks\gpu-render.lock` rules from `C:\AI\render\AGENTS.md`. | ComfyUI work during a render. Any render queue without Derrick's yes. Editing X3 files or running commands outside the brief. Opening `C:\Users\derek\sydney\`. |
| **Hydrogen** (`agy`, `gemini-4-hydrogen-*`, derekboone on the X3) | Hard live coding or scoring worth the remaining (unknown) quota: `W1` scoring, `RV2` if Opus does not take it, `H6` NPU trial, a stuck test failure. Low/medium effort by default. | File-only work Opus can do. Secrets. Renders. |
| **Max** (this bot) | Writes briefs, imports Opus commits (fetch GitHub `mono` → review diff → gitleaks → fast-forward Gitea, or merge if Gitea moved, never force → hand the apply to the machine's Forge under lease), verifies RESULT files, handles every secret (ntfy token, key files, redactions), mirrors Gitea↔GitHub. | Doing live work a Forge can do. Guessing. Viewing PixlStash contents. Running Render's jobs. |
| **Derrick** | Decision cards, Hermes-chat render yes, Tailscale Admin, logins (Civitai), typing new keys, downloads over ~5 GB, new software, deletes, widened access. | — |

Render queueing is unchanged: the Render pipeline (`queue-remote.sh <run_dir> --yes-derrick`) queues only after Derrick's yes in his Hermes chat. Rows that say "queue" mean that path, not Max.

### Leases (four doers, Finding 3)

One holder per host at a time (`records/evo-x3-lease-README.md`); every other doer stays read-only on that host while a lease is held.
- **X3 lease:** authoritative record is the newest brain file `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-{taken,released}-<holder>-<job>.md` (mirrored to `records/status/`). `/home/derekboone/AI/locks/x3-lease.txt` (A25) is only a local lock stub, not the lease record.
- **AlienPc lease:** matching host lease file (`*-alienpc-lease-{taken,released}-<holder>-<job>.md`) plus `C:\AI\locks\gpu-render.lock` and `:8447 --fail-if-busy` for GPU work.
- **Cross-host rule:** AlienPc Forge runs X3 builds/tests **only after X3 Forge releases the X3 lease**, under its own take/release files — never while X3 Forge is busy holding the lease. Hydrogen follows the same rule.
- **In every BRIEF:** name the exact take and release file paths and who writes them (the doer directly if it can reach the brain, or Max on brief issue/closeout — see Card 28 / M2).

### Cross-machine access (fixed 2026-11-19)

- **AlienPc → X3:** works (A3). `ssh x3` = `derekboone@evo-x3-1.tailf242b2.ts.net`, `ssh x3-evo` = `evo@…`, key `C:\Users\derek\.ssh\x3_alienpc_ed25519` (comment `alienpc-max-to-x3`), host key in `known_hosts` (fingerprint checked by Max, `SHA256:FCVUPIRi…`). Forge's AGENTS.md already points it at `x3run.ps1` (default user `evo`) and `x3put.ps1`.
- **Scope rule (Finding 14):** each BRIEF lists the exact allowed X3 commands. No `x3run.ps1 -AsDerek` or `sudo` unless the brief explicitly names it. Log every `x3run` command in `RESULT.md`.
- **X3 → AlienPc:** unchanged; only through the render path (`queue-remote.sh`, AlienPc llama-swap `/upstream/comfyui_auto` via Serve `:8446`) and the idle probe `:8447`.
- No Tailscale SSH, no new auth keys, no new Serve ports.

## Opus on GitHub

File-only work is done in VS Code on Derrick's PC (GitHub Copilot: Opus or Gemini), committed on `opus/<group>` branches, and pushed to GitHub branch `mono` (Derrick 2026-11-19 11:11/11:16 CT). It has no X3, AlienPc, Gitea, or chat access, so this file and the source plans must carry the context.

**Which folder to edit on `mono`** (per [records/monorepo-consolidation/PLAN.md](../monorepo-consolidation/PLAN.md); keep the old part-branch names below *until `mono` is live*, and never edit `evo-x3-all` or name the ambiguous `x3-linux` branch — see A7 / Finding 15):

| Kind of file | `mono` folder | Old part branch (until `mono` is live) | Typical paths |
|---|---|---|---|
| This plan, host config, Hermes config/SOUL/skills list, systemd unit *text*, pi-job script copies, briefs | repo root (`u58` content) | `u58` | `records/`, `config/`, `hosts/x3/hermes/` (proposals; `hosts/x3/live/` is the read-only snapshot), `hosts/x3/systemd/`, `config/bin/`, `config/pi-evo/` |
| OPERATOR.md, writer_pipeline, `queue-remote.sh`, `x3/still_candidate_sheet.py` | `x3/render/` | `x3-render` (never `x3-linux`) | `x3/render/` (part root) |
| `beta7_convert.py`, `lint.py` hooks, H3 skills, U55 templates, `remote_upscale.py`, `run_queue.py` | `x3/community/` | `x3-community` | `x3/community/{scripts/parody/,skills/,templates/}` |
| X3 Forge records / ralph-community | `x3/forge/` | `u58-chat-read-plan` | `x3/forge/` (part root) |
| AlienPc API templates and community scripts | `alienpc/community/` | `alienpc-community` | `alienpc/community/{templates/,scripts/}` |
| AlienPc render scripts | `alienpc/render/` | `alienpc-render` | `alienpc/render/` (part root) |
| AlienPc global pi + Forge loop copies (no live repo on AlienPc for these) | repo root (`hosts/alienpc/live/`) | `u58` | `hosts/alienpc/live/` |

**Opus-eligible items (preferred):** `W3` converter (`beta7_convert.py` + tests), `W4` config *drafts*, `G2` template `unet_name` edits, `G4` AGENTS.md / `writer_prompt.md` audit, `H1` `pi-job` routing *script*, `H2` Hermes config *draft* (no keys), `H3` routine and unit *text*, `H4` skill prune/adapt, `H5` cookiecutter + Makefile + AGENTS.md, `R5` poll interval, `S2` allowlist *script*, `L1-L8`, `LX1-LX9` documentation amendments to the Linux plan, `M4` candidate API template *drafts*, `RV1` capabilities YAML, `RV2` `h3max_bridge.py` package (tests included). Hermes Path B `h3-writer` skill *after* that plan is approved. Stills: `ST1` script + test, `ST2` desk text, `ST3` script text, `ST4`/`ST5` candidate template drafts. Inventory: `INV1`, `INV1b`, `INV2`, `INV3`.

**Not Opus:** `W1`/`W2` live bakeoffs, `W3` duckyshell install, `W5`, `G3` / any test render, `H1` ACL apply and ntfy token, `H2` live SSRF proxy, `H6` NPU, `R1-R4`/`R6-R7`, `S1`, `M0-M5` live installs and A/B, `RV0`/`RV3-RV5` live, secrets, downloads, GPU.

**Import-and-apply (Max imports; the machine's Forge applies), after each `opus/<group>` push to GitHub `mono` (Finding 5 / M1 resolved 2026-11-19):**

1. On the box: `git fetch origin mono` (or `<part-branch>` until `mono` is live) and note the new SHA. Review the full diff. Run `gitleaks` on that range. Stop on any secret, credential, or `.env` / token file. Do not print secrets.
2. Push to Gitea: fast-forward Gitea `mono` (`git push gitea <sha>:refs/heads/mono`, no force). If Gitea has moved ahead (e.g. a live X3 Render or Forge commit), **merge** on the box (`git merge --no-ff` — **never force-push**), re-run gitleaks on the merge, push Gitea, then mirror back to GitHub.
3. X3 Forge (X3 paths, X3 lease) or AlienPc Forge (AlienPc paths, AlienPc lease) gets a BRIEF with the SHA and lease take/release paths: back up the touched files under `_archive/<date>/`, then `git pull --ff-only` from Gitea for live git checkouts (`x3/render/`, `x3/community/`, `x3/forge/`, `alienpc/render/`, `alienpc/community/`). For **`u58` / root copy paths** (which do not deploy themselves on `git pull`; Finding 4), execute the BRIEF's **Install** line below and re-run `snapshot-live-setup.sh` / `sync-config-copies.sh` so the tracked copy matches live. Do not restart llama-swap, Hermes, or ComfyUI unless the item says so, and never edit `llama-swap.yaml` during a render.
4. The Forge runs the item's verify command and writes `RESULT.md`; Max checks it. If it fails, roll back from the backup / `git revert` (no force) and record it. If it passes, leave a short `records/<id>/APPLY.md` and mirror any additional local commit to Gitea, then GitHub.
5. A declined or dirty secret scan is final for that commit. Ask Opus to rewrite without the secret; do not scrub history unless Derrick says so.

**Install rule for `u58` / root copies (Finding 4 — one canonical copy per file):**

| Items | Canonical repo copy (edit this one) | Live destination | Owner / mode | Sudo? | Backup |
|---|---|---|---|---|---|
| `H1c`, `L1`, `L4-L6`, `L8` | `config/bin/pi-job` | `/usr/local/bin/pi-job` | `root:root 0755` | yes | `_archive/<date>/pi-job` |
| `ST3`, `L2` | `config/bin/sync-renders` (canonical over `hosts/x3/live/bin/sync-renders`) | `/usr/local/bin/sync-renders` | `root:root 0755` | yes | `_archive/<date>/sync-renders` |
| `ST3` | `hosts/x3/pixlstash-tagging/import_inbox.py` | `/home/evo/AI/pixlstash-tagging/import_inbox.py` | `evo:evo 0755` | no | `_archive/<date>/import_inbox.py` |
| `H2`, `H3`, `H4` | `hosts/x3/hermes/` for H2/H4 proposals and `hosts/x3/systemd/user/` for H3 units (`scripts/snapshot-live-setup.sh` runs `rm -rf hosts/x3/live` on every snapshot, so proposals never live there; merge only the changed keys into live) | `/home/evo/.hermes/` | `evo:evo 0644` (`0600` for secrets) | no | `_archive/<date>/hermes/` |
| `INV1`, `INV1b` | `hosts/alienpc/live/pi-agent/` | `C:\Users\derek\.pi\agent\` | user `derek` | no | `_archive\<date>\pi-agent\` |
| `INV*` (Forge) | `hosts/alienpc/live/forge/` | `C:\Users\derek\forge\` | user `derek` | no | `_archive\<date>\forge\` |

## Waves (order)

Independent tracks inside a wave run in parallel. A blocked item does not hold a later item that does not depend on it. X3 work does not wait on AlienPc clips.

- **Wave 0 — Review and cards (no live change).** Opus reviewed this file (`VERDICT: CHANGES`, 2026-11-19); findings 1-15 applied here, delta re-review pending. Derrick approved Card 2 (file-only work now) and `mono` delivery. Derrick answers remaining cards that unblock live Wave 1 (`INV1b`, `S1`, `S2`, etc.). Hermes U0-U9 stay held.
- **Wave 1 — Shared safety and converters (unblocks the rest).** `INV1`, `INV1b` (Derrick approves before any AlienPc Forge live ComfyUI/llama-swap step, Finding 1), `INV2`, `INV3` (Opus, files only). `S1` (live, Derrick yes, AlienPc Forge). `S2` script (Opus) then apply + planted-graph test (AlienPc Forge, AlienPc lease). `beta7_convert.py` (Opus, `x3/community/`). `H5` harness (Opus). `G4` file audit (Opus). `H4` skill prune/adapt (Opus; keep planned `h3-writer`). `R5` (Opus + apply under X3 lease). Optional `L1-L8` file work (Opus) can start here; live verify later.
- **Wave 2 — Parallel tracks.** **Writer:** `W1` (X3 Forge runs the harness; Hydrogen scores if needed; 0 GB download). `G2` files then smoke (Derrick yes). `G6` before `W4`. `W2` only if Derrick wants more after `W1`. `W3b` duckyshell install after license card. **Speed (AlienPc lease, no quality-changing stack until R2/R6 yes):** `R1` measure, then `R2-R4`, `R6`/`R7` later. **H1 closeout:** `P2.4` (Derrick in Tailscale Admin), `P4.11` token (secret, Max), `pi-job` X3-primary script (Opus then apply), Phase 5 `P5.1`/`P5.2`/`P5.4` on AlienPc (AlienPc Forge; no new Tailscale Serve port without a separate yes). `H2` after `P2.4`. `H3` after ntfy is in place. **Miraclein:** `M0-M5` on AlienPc (AlienPc Forge) under lease, one step at a time, Derrick yes per install/download/restart/promotion. **Stills:** `ST1` + `ST3` (Opus, then X3 Forge) early, they fix today's pain; `ST4`/`ST5` (AlienPc Forge) after `S2`; `ST2` rides Hermes Wave 3 but its OPERATOR.md line can land in the pi Render chat now. **REA-Video:** `RV0` on X3 (CPU) in parallel with Miraclein; `RV1` (Opus); `RV2` after converter + harness; `RV3`/`RV5` after render yes; `RV4` only with a separate yes.
- **Wave 3 — Hermes two-path setup**, only after that plan is reviewed and Derrick says go. Feed it the `W1-W3` winner and the shared converter. Coding hand-off test uses the post-`H1` X3-primary `pi-job`.
- **Wave 4 — Linux amendments go live** only after the Linux dual-boot plan is READY and Windows `R1-R7` have produced a tuned baseline. Until then, Opus may edit the Linux plan documents (`LX1-LX9`).
- **Wave 5 — Monorepo**, only after Q1-Q7 and a freeze (no open path-sensitive work).

## Item table

Size: S = small file or one command, M = a half-day live pass, L = multi-step with yes gates. Lease: none / X3 / AlienPc. Rollback is always backup first, then the noted undo.

### F4 — already done (do not redo)

| ID | Owner | Machine | Lease | Size | Verify | Rollback |
|---|---|---|---|---|---|---|
| F4 §0, G0, G1, G5 | — | — | — | — | Already live per F4 section 0 (`pi-job upscale` `cedca353`, Gufo resident). | — |

### F4 — writer, gaps, Hermes closeout, speed, safety, later small items

| ID | Opus file? | Owner (live / apply) | Machine | Lease | Size | What | Verify | Rollback |
|---|---|---|---|---|---|---|---|---|
| W1 | no | X3 Forge (run) + Hydrogen (score if needed) + Derrick blind pick | X3 | X3 (quiet window if unloading Gufo) | L | 16-ask bakeoff, models already on `/srv/models`. Arms 1a/1b/2/3 as in F4. No conflicting Gufo thinking flags. | Per-arm READY/refusal/drift/timing table + Derrick's blind ranking. `records/W1/RESULT.md`. | Restore `llama-swap` pins; no downloads to delete. |
| W2 | no | Derrick yes first, then same as W1 | X3 | X3 | L | Optional Stage 2, 1 download at a time, only if W1 loses. | Beats W1 on READY + Derrick pick, else delete the losing download. | Delete losing files; restore pins. |
| W3a | **yes** (`x3-community` `scripts/parody/beta7_convert.py` + tests) | Max imports; X3 Forge applies + tests | X3 | X3 | M | One shared Beta 7 converter used by duckyshell, pytraveler, REA-Video, and later Hermes. | Unit tests + `lint.py` READY, 0 header violations on fixtures. | Revert the commit. |
| W3b | no | X3 Forge (X3 side) / AlienPc Forge (AlienPc side), Derrick yes | X3 and/or AlienPc | matching | M | Install duckyshell Standalone v0.1.10 if license is open. Point at X3 `/v1`. Never Direct GGUF/Ollama on AlienPc. Pass copied prompts through `W3a`. | App starts; one converted prompt passes `lint.py`. | Uninstall the app; no ComfyUI change. |
| W3c | no (config has keys) | Derrick card C5; AlienPc Forge installs, Max places the key | AlienPc | AlienPc | M | Optional API Universal Writer + FX6 leak test. Off `S2` allowlist. | FX6 planted key absent from `/history`, metadata, QNAP outputs. | Disable the node; no key left in graphs. |
| W3d | no | Derrick Hermes yes; Render path queues; AlienPc Forge builds candidate graphs | AlienPc via X3 | AlienPc | M | Same-seed 3-ask video check of pipeline vs duckyshell vs (if kept) API writer. | Three clips; Derrick pick recorded. | Candidate graphs only; production templates untouched. |
| W4 | draft **yes** (`x3-render` `writer_pipeline/config.yaml`, llama-swap fragment) | Max imports; X3 Forge applies after `G6`; Derrick yes to reload | X3 | X3 | M | Deploy W1-W3 winner without daytime thrash, as in F4. | Render-X3 / pipeline / duckyshell hit the winner; 0 interactive swaps. | Restore previous yaml from `_archive`. |
| W5 | no | Derrick optional | X3 | X3 | M | `jc-test` vs live JoyCaption only if Derrick tags ~20 pictures. | Best match stays on the 04:00 timer. | Keep live JoyCaption. |
| G2 | **yes** (`x3-community` / `alienpc-community` templates: `unet_name` only) | Max imports; X3 Forge + AlienPc Forge apply; Derrick yes for 1 smoke each | both | both | M | `two_person`, `long_continuation`, `ref2va_16x9` to `beta7_int8HQ` (or R2 winner later). Size/frames unchanged. | `fill_request.py` dry-check; 1 smoke clip per template after yes. | Restore template backups. |
| G3 | no | Derrick render yes | AlienPc via X3 | AlienPc | S | After G2: 16:9 `--still-mode ref` vs `guide`, same seed. | One pair; crop/head-foot notes in RESULT. | No template promotion unless yes. |
| G4 | **yes** (AGENTS.md / `writer_prompt.md`) | Max imports; X3 Forge applies; Derrick card for voice-RefMod | X3 | X3 | S | Confirm ref-mode and hardcore rules still reach the writer. Leave `poolclub_refmod_audio` unchanged until the card. | Audit note in `records/G4/`. | Revert skill text. |
| G6 | no | Derrick decision | — | — | S | Does Sydney follow the writer pin or point at `flash-next-uncensored-v2`? Do this before W4. Do not open Sydney files to plan it. | Answer recorded. | — |
| H1a P2.4 | ACL *text* already drafted; apply is Derrick | Derrick in Tailscale Admin | — | — | S | Narrow ACL for ports with no login (`8443-8447`); same tag on Windows and Linux nodes. Serve is already on for those ports (audit A12); no new Serve port without a separate yes. | ACL active in the console. | Derrick reverts the ACL. |
| H1b P4.11 | no (secret) | Max (secret), Derrick yes. Note: `/home/evo/.config/evo-x3/ntfy-x3.token` already exists (audit; contents not read) — verify mode/scope instead of creating | X3 | X3 | S | Write-only ntfy token in `/home/evo/.config/evo-x3/ntfy-x3.token` `0600`. Never commit it. | Token file mode 0600; a test notify works; not in git. | Remove the file. |
| H1c pi-job routing | **yes** (`u58` `config/bin/pi-job` / scripts; do not touch unrelated dirty copies) | Max imports, X3 Forge applies + live test; AlienPc Forge checks the AlienPc side (its default is `coding_swift15_iq3s_esp`, ESP on — card 21) | X3 (+ AlienPc idle probe) | X3, maybe AlienPc | M | X3 Gufo primary for `code`/`review`; opportunistic AlienPc Swift `ESP off` only when `:8447 --fail-if-busy` says idle or both Gufo sessions are busy. | Simultaneous Hermes chat + `pi-job code` on X3, 0 swaps; idle AlienPc path never interrupts a render. `PHASE-5-RESULT.md`. | Restore previous `pi-job`. |
| H1d P5.1/P5.2/P5.4 | no | AlienPc Forge | AlienPc | AlienPc | M | Finish AlienPc Phase 5 verification. Serve is already on for 8443-8447 (audit A12); no new Serve port. | `PHASE-5-RESULT.md` committed. | Per main plan. |
| H2 | config *draft* **yes** (`hosts/x3/hermes/config.yaml`; merge only `web:` + `platform_toolsets.api_server` into live) | Max imports; X3 Forge applies after H1a; live SSRF proxy is X3 Forge + Derrick yes | X3 | X3 | M | SearXNG search; network-layer SSRF block of loopback/tailnet/link-local except SearXNG. Approvals stay manual / unattended deny. | Search works; planted fetch to `:8080` and AlienPc `:8446` is blocked. | Restore Hermes config; remove proxy. |
| H3 | unit/routine *text* **yes** | Max imports; X3 Forge applies | X3 | X3 | S | Read-only morning status + weekly worktree report via ntfy. Avoid 04:00 JoyCaption window. | One on-time ntfy with zero secrets, 0 swaps. | Disable the timer. |
| H4 | **yes** (Hermes + pi skills) | Max imports; X3 Forge applies | X3 | X3 | M | Prune the 45 stock skills; adapt keepers to X3 paths, `U56 Decision #1`, `pi-job`, SearXNG, `/srv/renders`. Keep planned `h3-writer`. No unguarded Comfy MCP. | Hermes loader + `SKILL_SMOKE_OK`; no broken paths. | Restore skill tree from backup. |
| H5 | **yes** (template, Makefile, AGENTS.md) | Max imports; X3 Forge applies + sample change | X3 | X3 | M | `cookiecutter-uv` + `make check-all` required before `pi-job code` returns DONE on repos that have it. Used by `RV2`. | Sample tool: change + `make check-all` green, else not DONE. | Leave legacy scripts alone. |
| H6 | no | Optional, Derrick yes; Hydrogen | X3 | X3 | L | Gufo NPU offload with fabric-clock hold (`ROCm/TheRock#8709`). One service at a time, 15 min stress. | 0 hangs, `NRestarts=0`, `MemAvailable >= 4 GiB`. | Disable `--npu` immediately on hang. |
| R1 | no | AlienPc Forge | AlienPc | AlienPc | S | Per-stage timing, no change. | Timing table in `records/R1/`. | None. |
| R2 | no (test graphs only) | Derrick yes (download + renders); AlienPc Forge builds graphs; Render path queues | AlienPc via X3 | AlienPc | M | `beta7_activation_learned_HQ` vs `int8HQ`, 3 seeds, 2-pass and 1-pass, blind pick. **Needs a re-download first:** only `int8HQ` (22.9 GB) is on disk; `activation_learned_HQ` has only a HF cache stub (audit A18, card 22). | Tie or better on both graphs. | Keep `int8HQ` in production templates. |
| R3 | no | Derrick yes; AlienPc Forge | AlienPc | AlienPc | S | `--disable-fast-disk` only if R1 logs `fast_disk=True`. Keep `--disable-pinned-memory`. | Median faster and frames match. | Restore argv. |
| R4 | no | Derrick yes; AlienPc Forge | AlienPc | AlienPc | S | `Prefer No Sysmem Fallback` for ComfyUI `python.exe`. | Faster and 0 OOM in 5 renders. | Driver Default. |
| R5 | **yes** (`x3/render/queue-remote.sh`, part branch `x3-render`) | Max imports; X3 Forge applies | X3 | X3 (apply edits live render checkout; no active render) | S | Poll "BATCH closed" every 5 s instead of 30 s. | Notice is faster; renders unchanged. | Revert the script. |
| R6 | no | Later, Derrick yes; AlienPc Forge | AlienPc | AlienPc | M | `--fast fp16_accumulation`, then `cublas_ops`, one at a time. Never `fp8_matrix_mult` or `autotune`. | Blind same-seed tie or better. | Drop the flag. |
| R7 | no | Later, own job, Derrick yes; AlienPc Forge | AlienPc | AlienPc | L | ComfyUI upgrade from `0.38.0`. Snapshot first. Can also unblock Klein9 `comfy_api.latest` if M3 fails. | Every template still renders; median not slower. | Restore snapshot. |
| S1 | no | Derrick yes; AlienPc Forge (both still `security_level = normal`, audit A15) | AlienPc | AlienPc | S | Manager `strong` on `comfyui_auto` and `comfyui_longvideo`. Installs via git clone only. | Manager install/restart via `:8446` refused; B2 still renders. | Restore `config.ini`. |
| S2 | script **yes** | Max imports; AlienPc Forge applies + live test | AlienPc | AlienPc | M | Allowlist: 8 U55 + `b2` + `b2_refmod` + 3-node RTX VSR graph + later promoted templates. No LLM-node graphs. Prompt/seed/inputs/RefMods/frames/prefix may vary. | Planted extra node refused; 1 B2 and 1 `pi-job upscale` pass. | Disable the check; keep publishing path. |
| L1 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | ntfy Copy button on approval (`queue <run_id> <code>`). | QNAP v2.35.0 shows Copy. | Revert `pi-job` header. |
| L2 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | Poster frame grab per clip into `/srv/renders/<run_id>.jpg`. | Hermes shows a preview. | Revert `sync-renders`. |
| L3 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | Nightly stale worktrees >7 days: save status/diff, then remove+prune. | Timer report in `_runs`. | Disable that timer line. |
| L4 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | Contact sheet in chat + `pi-job render --pick N`. | Sheet in dry-run reply. | Revert those lines. |
| L5 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | `pi-job status` overview (no job ID). | Status prints model, memory, last 3 jobs. | Revert the subcommand. |
| L6 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | STUCK bundle `escalate.md` with task, diff, last errors. | File written on STUCK. | Revert those lines. |
| L7 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | Syntax check extension (`py_compile` / `bash -n` / `jq empty`). | Errors appear in tool output. | Remove the extension. |
| L8 | **yes** | Max imports; X3 Forge applies | X3 | X3 when verifying | S | `pi-job recompile <run_id>` after prompt edit; new P4.11 code. | New code matches new prompt hash. | Revert the subcommand. |

### Miraclein (`M0-M5`) — AlienPc ComfyUI only, prompts from X3

| ID | Opus file? | Owner | Machine | Lease | Size | What | Verify | Rollback |
|---|---|---|---|---|---|---|---|---|
| M0 | no | AlienPc Forge, Derrick yes | AlienPc | AlienPc | S | Pre-flight: ≥25 GB free, no GPU job, check TE/VAE/Beta 7 presence, snapshot `ComfyUI-MiniMaxH3Mod` at `517e8c41`, archive under `ComfyUI\_archive\20261119_pre_miraclein\`. | Backup + snapshot exist. | — (this is the rollback base). |
| M1 | no | AlienPc Forge, Derrick yes | AlienPc | AlienPc | M | Update MiniMaxH3Mod to pinned `54f93eb6`. Import smoke on 0.38.0. Do not overwrite torch / OpenCV. | `comfyui_auto` starts clean; existing RefMod smoke still works. | `git checkout 517e8c41` + restart. |
| M2 | no | AlienPc Forge, Derrick yes; Derrick picks stills | AlienPc | AlienPc | M | Standalone H3 RefMod extract (node and/or CLI). No PixlStash library viewing. Header-free prompt, omit `<Picture N>`. | New RefMod loads; 1-clip likeness check by Derrick. | Delete the new `.safetensors`; leave `models\refmods\` otherwise untouched. |
| M3 | no | AlienPc Forge, Derrick yes (download + clone) | AlienPc | AlienPc | L | Miraclein NVFP4 4.82 GB + Flux2Klein9Mod (TE `qwen_3_8b_fp8mixed` and `flux2-vae` are already present, audit A17). **Import-check `comfy_api.latest` on 0.38.0 first.** FP8 only if NVFP4 fails (8.46 GB, separate yes). | Zero import errors; 4 Klein9 nodes in `/object_info`. | Remove the new node and weights; if import fails, defer to R7 or a local shim (Derrick yes). |
| M4 | template *draft* **yes** | X3 writes prompts; AlienPc Forge runs stills; Derrick judges | AlienPc via X3 | AlienPc | M | Candidate start-still / edit templates (never overwrite locked Flux stills). 3 stills: T2I, RefMod, single-change edit. Peak VRAM < 16 GB, warm 6-15 s. | All 3 succeed; Derrick checks identity + skin. | Keep candidates; do not promote. |
| M5 | no | Derrick yes; AlienPc Forge builds arms; Render path queues | AlienPc via X3 | AlienPc | L | Realism LoRA A/B, header-free prompt, arms A/B/C as in the source plan (no `er_sde`). Promote + add to S2 only on yes. | Blind pick + timings recorded. | Remove LoRA / candidate templates; H3Mod back to `517e8c41` if needed. |

### REA-Video (`RV0-RV5`) — breakdown on X3, render on AlienPc

| ID | Opus file? | Owner | Machine | Lease | Size | What | Verify | Rollback |
|---|---|---|---|---|---|---|---|---|
| RV0 | no | X3 Forge, Derrick yes to clone + small CPU caches (AlienPc already has an upstream clone `e385853` at `C:\Users\derek\forge\tools\rea-video`, reference only; audit A20) | X3 | X3 | M | Isolated `uv` venv, `.[asr]`, `--lang en` decompose of one 10-15 s clip; one shot to live Gufo; `lint.py`. | English `breakdown.json` + stems; 1 prompt READY, 0 header violations. | Remove the venv/clone; caches stay unless Derrick wants them gone. |
| RV1 | **yes** | Max imports; X3 Forge applies | X3 | none for the file | S | User capability YAML for `minimax-h3-10eros-beta7` under `~/.rea-video/` (upgrade-safe). | `rea-video models minimax-h3-10eros-beta7` + `validate_capabilities.py` clean. | Delete the user YAML. |
| RV2 | **yes** (prefer Opus; Hydrogen only if the package stalls) | X3 Forge runs `make check-all` | X3 | X3 | L | `h3max_bridge.py` with H5 harness: 17k+5 snap, `ffmpeg -an` proxies, `--refmod`, llama-swap call, shared `beta7_convert.py`. | `make check-all` green, including header-ban tests. | Revert the package. |
| RV3 | no | Derrick Hermes yes; Render path queues | AlienPc via X3 | AlienPc | M | One frozen-template clip + RTX 2x + publish. | Clip in `/srv/renders`; Derrick visual/audio check. | Frozen copy only; production templates untouched. |
| RV4 | no | Optional, separate yes each node | AlienPc | AlienPc | M | Guide / AudioRefine nodes, 0.38.0 import check, fixed-seed A/B. | Keep only if Derrick scores an improvement. | Remove the node. |
| RV5 | no | X3 Forge after 2+ approved clips | X3 | none | S | Hard-cut concat only (no crossfades, no capsule-cinema). Publish final. | Joined mp4 plays with synced audio; record committed. | Keep the parts; drop the join. |

### Linux amendments (`LX1-LX9`) — documents now, live in Wave 4

| ID | Opus file? | Owner now | Later live | Notes |
|---|---|---|---|---|
| LX1 | **yes** (Linux plan text) | Opus docs | After Linux plan is READY | Already decided: render-first + opportunistic Swift, not "ComfyUI-only" / "no local LLM". |
| LX2 | ACL text with H1a | Derrick | Same ACL covers the Linux node tag | Narrow form of review D1 option B. |
| LX3 | docs | — | Equals S1 | Manager `strong` or no Manager. |
| LX4 | docs | — | After R1-R7 | Tuned Windows baseline; same protocol; real ~142 s not poll-rounded 180 s. |
| LX5 | docs | — | U10 row | Headless vs desktop session; headless becomes default only if it matters and Grok Bot can run without a desktop. |
| LX6 | docs | — | — | Do not plan on the unverified 22-53% / 1.6x Linux claims. Linux plan's 5-15% estimate stands until U10 measures. |
| LX7 | docs | — | U10 rows | Linux-only tuning: drop `--disable-pinned-memory`, fast-disk both ways, cold vs warm, plus LX5. No sol-attn / Sage / `torch.compile`. |
| LX8 | docs | Cards C5 + S2 | Same answers on Linux | Writer node + allowlist parity, including RTX VSR if Linux runs it. |
| LX9 | docs | — | U8 on Ubuntu 24.04 `sm_120` | Test both `nvvfx` and `ComfyUI_Nvidia_VFX_Nodes`. If unsupported, pick an explicit fallback before cutover (Derrick yes). |

## Stills intake (`ST1-ST5`, Derrick t2645u)

Goal: the start still for a render is fresh, can come from Derrick's own upload with no wait, can be generated when there is none, and can follow a reference pose or background. Flux/ComfyUI work stays on AlienPc; prompts are written on the X3. **18+ is the only content stop for every path — both text and images (Finding 7):** text asks and writer outputs pass `wp_lint` hard stops (`youth_hint`/`scale_adult`/`_MINOR_RE`), and every uploaded still (`ST2`) and `ST5` input/reference image must pass a still vision read (`still_read.json`) plus lint as a hard `NOT_READY` **before** any AlienPc GPU job (see Card 30 / M4 on the `still_read` adult/scale field). Max and the Forges never open PixlStash library pictures, tags or names; only the generated 2x3 contact sheet is shown, as today (OPERATOR.md).

### What is live today (VERIFIED read-only, 10:46-10:52 AM CT)

- **Same image every time:** `/home/evo/AI/render/x3/still_candidate_sheet.py` `build_sheet()` (line 37) calls `/api/v1/pictures/search` with `limit=30`, drops videos, filters `likeness_score >= 0.55` when a `character_id` is given, then `sorted(..., key=(round(score,4), smart_score, likeness_score), reverse=True)[:6]` (lines 54-62). Same query → same 30 hits → same top 6 → same pick. No memory of past picks, no shuffle, no "another one" path. Runs already record the chosen still in `<run_dir>/pick.json` (`"still"`; read by `render_writer_pipeline.py` line 1691); 39 run folders exist.
- **Upload path:** the pipeline accepts `--still <path>` (Hermes plan F6), so a file can be used directly. Hermes WebUI (not installed yet) stores chat uploads under `~/.hermes/webui/attachments/<session_id>/` (or `HERMES_WEBUI_ATTACHMENT_DIR`) and hands the agent the absolute path (nesquena/hermes-webui README + PR #2319, #2382).
- **Slow import:** `/usr/local/bin/sync-renders` line 92 runs `/home/evo/AI/pixlstash-tagging/import_inbox.py` synchronously inside the 2-minute `evo-renders-sync` service. `import_inbox.py` (30 lines) posts batches of 50 to `/api/v1/pictures/import` (timeout 600 s), then polls `/import/status` every 3 s in `while True` with no overall timeout. PixlStash 2.0.1 at that moment: 8.90 GB used vs `MemoryHigh=8G` (drop-in `10-memcap.conf`), swap full at `MemorySwapMax=2G`, `memory.events high` 2,370,429, ~113 % CPU. The cgroup is being throttled at its memory ceiling while its own pipeline (faces → quality → captions → embeddings → tagging → smart score, per PixlStash's architecture doc) runs on new pictures, so the import task's status advances slowly and the sync service waits on it.
- **AlienPc ComfyUI (HardcoreNSFW-TestRuntime, read-only listing):** installed and enabled: `comfyui_controlnet_aux` (DWPose/depth/canny preprocessors), `ComfyUI_essentials`, `ComfyUI-VideoHelperSuite`, MiniMaxH3Mod, H3 Multishot/Continuum, both prompt-writer nodes. Disabled: `ComfyUI-PuLID-Flux2`, `ComfyUI-PixlStash`, KJNodes, Impact. Models: `flux-2-klein-9b-kv-fp8` (9.1 GB), `FLUX-KLEIN-9B-FP8-NSFW` (8.5 GB), TE `qwen_3_8b_fp8mixed`, `flux2-vae`, LoRAs `refcontrol_pose`, `refcontrol_v2_poses` (RefControl Klein 9B pose), `bfs_head_v1` (head swap), `MS_real_and_Details_klein`, `klein_snofs_v1_4`, Triple/QuadView. Empty: `controlnet`, `clip_vision`, `style_models`, `ipadapter`. Templates: `flux_stills_s2_bfs.api.json`, `flux_stills_s2_kv.api.json`.
- **H3 side already supports:** `--still-mode ref|guide`, `--partner2-still`, `--continue` (Hermes plan F6).

### Community / official way, adapted

- FLUX.2 Klein does reference editing natively (one or two reference images + an instruction); pose transfer uses the RefControl Klein 9B pose LoRA with a DWPose map as image 1 and the identity reference as image 2, trigger "apply pose from image 1 with reference from image 2", LoRA 0.8-1.0 (thedeoxen/refcontrol README and HF card; yanokusnir-ai/one-node-flux-2-klein POSE mode). A RefControl **depth** LoRA exists for "same layout/background" (HF `refcontrol-FLUX.2-klein-9B-reference-depth-lora`, small LoRA, not installed).
- FLUX.1 tools (Redux, Kontext, FLUX.1 ControlNet-Union, XLabs IP-Adapter) target FLUX.1-dev and would each need a separate 10-24 GB model family. → adapt: do not add them; Klein 9B + RefControl covers pose and layout on what is already installed.
- PixlStash import is task based (`POST /pictures/import` → `task_id`, poll `/pictures/import/status`); its own web client gives up after 600 polls (commit `79e2946`). → adapt: same, with a time cap, run detached from the render path.

### Items

| ID | Opus file? | Owner (live / apply) | Machine | Lease | Size | What | Verify | Rollback | Gate |
|---|---|---|---|---|---|---|---|---|---|
| ST1 | **yes** (`x3-render` `x3/still_candidate_sheet.py` + test) | Max imports; X3 Forge applies + runs test | X3 | X3 | S | Fresh sheet: read the last N (default 20) `runs/*/pick.json` `"still"` values and exclude them; widen search to `limit=60`; keep the top 18 by the same key, then `random.sample` 6 (seed logged in the sheet summary so a sheet can be rebuilt); add `--exclude <id,…>` / `--page 2` so "another one" excludes everything already shown this ask; if fewer than 6 remain, fall back to the excluded ones last. No change to filters (videos, likeness ≥ 0.55). | Offline unit test with a mocked search: same query twice gives different sheets; recent picks never in the first 6 when ≥6 others exist; `--exclude` honoured. One dry ask in Derrick's chat shows a new sheet on "another one". | Restore the script from `_archive`. | Derrick's yes to apply (live script). |
| ST2 | **yes** (OPERATOR.md desk text + `render_writer_pipeline.py` `--still` doc; Hermes `h3-writer` addendum) | Max imports; X3 Forge applies | X3 | X3 | S | Uploaded image = the still. Hermes copies the attachment path into `<run_dir>/_inputs/` and passes `--still <run_dir>/_inputs/<file>`; the still vision read (`still_read.json`) plus 18+ lint runs on that file as a hard `NOT_READY` **before** any AlienPc GPU job (Finding 7, Card 30). No PixlStash call before the render. After the run is set up, the file is dropped into `/home/evo/AI/pixl-inbox/` for the normal background import (unless Derrick overrides in Card 34). | Dry ask with an attached test image: pipeline reaches "Render this?" with `pick.json` pointing at `_inputs/`; PixlStash not contacted during the ask (log); mocked `still_read` youth fixture stops `NOT_READY` before GPU (never real images). | Revert desk text. | Part of Hermes U5/U6 (held until that plan's go); the pi Render chat gets the same OPERATOR.md line. |
| ST3 | **yes** (`u58` `hosts/x3/pixlstash-tagging/import_inbox.py` copy, `config/bin/sync-renders` canonical copy) | Max imports; X3 Forge applies (via `u58` Install rule); Derrick yes for the memory cap | X3 | X3 | M | (a) `sync-renders` starts the import detached using **only** `systemd-run --user --unit=pixl-import --collect …` (Finding 6: `evo-renders-sync.service` is `Type=oneshot` with default `KillMode=control-group`, which kills `&` children on exit; the fixed unit name doubles as the lock, so treat "unit exists" as skip). (b) `import_inbox.py`: overall time cap (e.g. 15 min) and per-batch cap, then leave unfinished files in the inbox for the next pass; batch 10 instead of 50; log counts and timings only. (c) Memory (Finding 11, Card 23): current `10-memcap.conf` is `MemoryHigh=8G`, `MemoryMax=10G`, `MemorySwapMax=2G` (raised 5G→8G today, t2584); proposal is `MemoryHigh=12G`, `MemoryMax=14G`, `MemorySwapMax=2G` (or keep `8G / 10G / 2G` and accept slower tagging). (d) Tagging after import stays PixlStash's own background pipeline; no tag reads by us. | Upload of 5 files: sync service exits < 30 s and `pixl-import` unit is still running after `evo-renders-sync.service` exits; files appear as PixlStash entries (count only) within the cap; `memory.events high` rate falls after (c) with `MemAvailable >= 4 GiB` while Gufo + PixlStash are at cap. | Restore both scripts; remove drop-in change. | Derrick yes for (c); no restart of PixlStash during a render; no apply during Hermes bakeoff window (C16). |
| ST4 | template *draft* **yes** (`alienpc/community/` / `x3/community/` `templates/flux_stills_t2i_klein.api.json` candidate) | X3 writes the still prompt (Gufo / W1 winner); AlienPc Forge builds + tests the graph | AlienPc via X3 | Build/test: AlienPc lease; Runtime: none (uses `run_queue` + `gpu-render.lock` + `:8447 --fail-if-busy`) | M | No image given: X3 writes a short Klein prompt (adult cue required, same 18+ hard stops as `wp_lint`), queues a Klein 9B T2I still on AlienPc via the existing `remote_comfy`/`run_queue` path guarded by `C:\AI\locks\gpu-render.lock` and `:8447 --fail-if-busy` (no new endpoint, never collides with video renders), saves it to `<run_dir>/_inputs/`, shows it in chat, and continues the normal flow (still read → prompt → "Render this?"). Use the existing `flux_stills_s2_kv` graph as the base. | 3 dry asks: still produced in < 30 s warm, saved under `_inputs/`, flow reaches "Render this?"; a youth-cue ask stops `NOT_READY` before any GPU job; runtime guard defers when `:8447` reports busy. | Keep candidate template only. | Split (Finding 8): (1) Build/test runs under the AlienPc lease with Derrick's test go; (2) Runtime requires Derrick's one-time yes to enable in-chat T2I still generation (every subsequent H3 video render still requires Derrick's in-chat yes). |
| ST5 | template *draft* **yes** (`templates/flux_stills_pose_klein.api.json`, `..._layout_klein.api.json`) | AlienPc Forge builds + tests; X3 writes prompts | AlienPc via X3 | Build/test: AlienPc lease; Runtime: `run_queue` + `gpu-render.lock` + `:8447` | M | Reference for pose or background: **18+ image gate (Finding 7):** every ST5 input/reference image runs `still_read.json` + lint as a hard `NOT_READY` **before** any AlienPc GPU job (Card 30). Pose = DWPose (installed) map as image 1 + identity still as image 2 + `refcontrol_v2_poses` 0.8-1.0 + RefControl trigger; background/layout = Klein reference edit with the reference as image 1 ("place the person from image 2 in the scene of image 1"); optional RefControl depth LoRA (small download, card 24). The new still then feeds H3 as today (`--still-mode ref|guide`, `--partner2-still` for a second person). | 2 pose + 2 background tests: pose/scene matches by Derrick's eye; peak VRAM < 16 GB with ComfyUI alone; mocked `still_read` youth fixture stops `NOT_READY` before any AlienPc job (never real images). | Candidate templates only. | Derrick yes for the depth LoRA download and for promotion. |

Downloads for ST4/ST5: none required (Klein 9B, TE, VAE, pose LoRA, DWPose present). Optional: RefControl depth LoRA (small). FLUX.1 Redux/Kontext/IP-Adapter: not planned (each >5 GB and a second model family).

## Inventory: agent instructions, skills and templates in GitHub (Derrick t2644u)

Checked 2026-11-19 10:47-10:55 AM CT by git blob hash (live file vs branch tip on Gitea = GitHub). Excluded on purpose: anything under a Sydney folder, Sydney chats/persona/memory, PixlStash library data, chat transcripts/sessions, run folders (`runs/`, `run/`, `acceptance/`: per-run prompts and graphs), npm package copies, the original ComfyUI folder, credential files (`auth.json`, `mcp.json`, `models.json`, `.env*`).

| File(s) | Machine path | GitHub location | Status |
|---|---|---|---|
| Render `AGENTS.md`, `OPERATOR.md`, `RUN_ME.md`, `writer_pipeline/writer_prompt.md`, `.pi/settings.json`, `.pi/extensions/*`, `x3/still_candidate_sheet.py` | X3 `/home/evo/AI/render` | branch `x3-render` (`9232545`) | already there (checkout clean except a data file) |
| Community skills (9: alienpc-hardcore-i2v-director, alienpc-stills-pose-edit-prompting, comfy-render, h3-hc-render, h3-max-ref2va-prompt, h3-parody-identity, h3-prompting, image-render, video-render) with `references/`, `scripts/` | X3 `/home/evo/AI/community/skills` | branch `x3-community` `skills/` (`6bdcc49`) | already there |
| `agent-shared/AGENTS.md` (= X3 Forge `AGENTS.md` via symlink), `agent-shared/prompts/*`, `agent-shared/skills/ralph-loop` | X3 `/home/evo/AI/community/agent-shared` | branch `x3-community` | already there |
| Templates: 15 tracked `*.api.json` (b2, b2_fc_sydney_lora, b2_omni_rewriter, b2_refmod, faces/FC_SYDNEY, flux_stills_s2_bfs, flux_stills_s2_kv, long_continuation, named_parody, oc_guide, oc_ref, plain, ref2va_16x9, talk, two_person) | X3 `/home/evo/AI/community/templates` | branch `x3-community` `templates/` | already there |
| `b2_fc_sydney_lora_s05.api.json`, `b2_fc_sydney_lora_s08.api.json` | X3 `/home/evo/AI/community/templates` | — | **skipped**: matched by the repo's own `*sydney*` ignore rule (line 75) and each carries a baked long prompt string in node `c0`; card 25 asks Derrick |
| X3 Forge `.pi/settings.json`, `.pi/extensions/*`, `ralph-community/PROMPT.md`, records | X3 `/home/evo/AI/forge` | branch `u58-chat-read-plan` (`4cbbba0`) | already there (clean) |
| Hermes `SOUL.md`, `config.yaml`, custom skill `pi-job/SKILL.md`, skill list + local-edit diff | X3 `/home/evo/.hermes` | `u58` `hosts/x3/live/hermes/` | already there (hashes match). 313 other skill files are Hermes bundled skills (identical to `hermes-agent` `ae2a81ccc0` except `ascii-video`, covered by `local-edits-to-bundled-skills.diff`). No Hermes profiles exist yet. |
| pi evo `AGENTS.md`, `settings.json`, `pi-permissions.jsonc`, `trust.json`, `web-search.json`, `extensions/herdr-agent-state.ts`, `extensions/subagent/config.json` | X3 `/home/evo/.pi/agent` | `u58` `hosts/x3/live/pi-evo/agent/` | already there |
| pi evo `extensions/pi-permission-system/config.json` | X3 `/home/evo/.pi/agent/extensions/…` | `u58` `hosts/x3/live/pi-evo/agent/extensions/pi-permission-system/config.json` | **updated** (was `802952f`, now `1b60a61`) |
| pi derekboone `settings.json` | X3 `/home/derekboone/.pi/agent/settings.json` | `u58` `hosts/x3/live/pi-derekboone/agent/settings.json` | **updated** (was `b6a00d2`, now `7628a35`) |
| pi evo `pi-mobile/config.json` | X3 `/home/evo/.pi/agent/pi-mobile/config.json` | `u58` `hosts/x3/live/pi-evo/agent/pi-mobile/config.json` | already there (Finding 12 fix: tracked) |
| pi evo `memory/`, `missions/`, `state/` | X3 `/home/evo/.pi/agent` | — | skipped: runtime state, not instructions |
| `import_inbox.py`, `sync-renders` | X3 `/home/evo/AI/pixlstash-tagging/`, `/usr/local/bin/` | `u58` `hosts/x3/pixlstash-tagging/`, `config/bin/`, `hosts/x3/live/bin/` | already there |
| AlienPc Render `AGENTS.md`, `.pi/agent/pi-permissions.jsonc` | AlienPc `C:\AI\render` | branch `alienpc-render` (`5c3450d`) | already there. 7 untracked `_handoff/*/PROMPT.md` coding briefs: skipped (old one-off briefs, not live instructions) |
| AlienPc community skills (same 9) + `agent-shared/AGENTS.md`, `agent-shared/skills/ralph-loop`, 6 `templates/*.api.json` | AlienPc `C:\AI\community` | branch `alienpc-community` (`6dadffc`) | already there (these paths clean; the 131 dirty files are elsewhere, monorepo Q4). Untracked `agent-shared/skills/google-voice-texts/`: skipped (texting skill, disabled in pi settings, not video) |
| AlienPc global pi `AGENTS.md`, `settings.json`, `pi-permissions.jsonc`, `web-search.json`, `extensions/loop-guard.ts`, `extensions/pi-permission-system/config.json`, `extensions/subagent/config.json` | AlienPc `C:\Users\derek\.pi\agent\` | `u58` `hosts/alienpc/live/pi-agent/` | **added** (none were in the repo; `herdr-agent-state.ts` is identical to the X3 copy) |
| AlienPc skill links (11 directory symlinks) | AlienPc `C:\Users\derek\.pi\agent\skills\` | `u58` `hosts/alienpc/live/README.md` (table) | **added** as a map; targets tracked in `alienpc-community`; `rea-video` points at upstream `JuneYaooo/rea-video` `e385853` |
| AlienPc Forge `README.md`, `x3run.ps1`, `x3put.ps1`, `.pi/bin/ps-ladder.cmd`, `ralph-community/{PROMPT.md, ralph.ps1, README.md, .gitignore}` | AlienPc `C:\Users\derek\forge` (→ `5slock`, not a git repo) | `u58` `hosts/alienpc/live/forge/` | **added** |
| AlienPc Forge `ralph-community/fix_plan.md` | same | — | **skipped**: per-task state that quotes an adult render ask verbatim (no adult prompt text in git) |
| AlienPc ComfyUI node list, pip freeze, launchers | AlienPc ComfyUI | `u58` `hosts/alienpc/comfyui/`, `hosts/alienpc/launchers/` | already there (not re-hashed this pass) |

Secret scan: gitleaks `--no-git` over every staged copy: no leaks; plus an `rg` key/token/password pattern pass: 0 hits.

Opus items from the inventory: `INV1` fix line 1 of AlienPc global AGENTS.md (it is not a hard link) or decide which copy is master; `INV1b` (Finding 1) scope `hosts/alienpc/live/pi-agent/AGENTS.md` line 35 to add `"unless a BRIEF with a Derrick id names the change"` (Derrick approves before any AlienPc Forge live ComfyUI/llama-swap/driver step); `INV2` add AlienPc Forge, AlienPc global pi folder and `hosts/alienpc/live/` to `hosts/SETUP-MAP.md`; `INV3` extend `scripts/snapshot-live-setup.sh` docs with an AlienPc section (Max/AlienPc Forge runs it; Opus edits text only).

## Decision cards

Answer these in chat, or let Opus recommend and then confirm. Defaults below are Max's recommendation where one is safe; cards without a default stay open.

1. **Go ahead with this unified plan?** (hold all live work until yes.) Recommended: yes, as plan-only until you also say yes per live step.
2. **Start Wave 1 file-only now — APPROVED by Derrick (2026-11-19 11:11/11:16 CT, verbal, this chat).** File-only work now in progress in VS Code on Derrick's PC (`opus/<group>` branches): **render** (`ST1`, `R5`, `ST2`, `G4`); **community-code** (`W3a`, `H5`, `RV1`, `RV2`); **templates** (`G2`, `S2`, `M4`, `ST4`, `ST5`); **u58-pijob** (`H1c`, `ST3`, `L1-L8`, `INV1`, `INV1b`, `INV2`); **hermes** (`H4`, `H2`, `H3`). Commits land on `mono`; **not live until Max imports, scans, and the machine's Forge applies under lease.** Hermes U0-U9 live work stays held. (`LX1-LX9` docs wait on Card 32 / M6 path confirmation.)
3. **Hermes two-path plan:** go / hold / change after Opus reviews it? (Already waiting.)
4. **Monorepo Q1-Q7:** Max's recommendations are already in that plan (yes / tags only / keep u58 at root / scan-and-commit AlienPc dirty files / untrack mcp.json backups / credential manager / archive the two AlienPc repos). Confirm or override there.
5. **`S1`:** set ComfyUI-Manager to `strong` on both AlienPc instances now?
6. **`S2`:** build the server-side template allowlist (optional in F4; recommended here)?
7. **`W2`:** run Stage 2 downloads only if W1 loses? Recommended: yes, that default.
8. **`G6`:** Sydney follows the writer pin, or points at `flash-next-uncensored-v2`? Answer before W4. Do not ask Max to open Sydney files.
9. **`G4`:** keep `poolclub_refmod_audio` for `FCSydny` / `FCMegan`, or change? Leave unchanged until answered.
10. **`W3c` / LX8.1:** keep the API Universal Writer node? (One answer for Windows and later Linux.)
11. **`P2.4`:** apply the drafted Tailscale ACL in the Admin Console? (Serve already forwards 443/8443-8445 on the X3 and 8443-8447 on AlienPc, tailnet only; no new Serve port unless you also say yes.)
12. **`P4.11`:** a file `/home/evo/.config/evo-x3/ntfy-x3.token` already exists (not read). Confirm it is the write-only token, or replace it (Max handles it; never printed)?
13. **`H1c`:** flip `pi-job code`/`review` to X3-primary + opportunistic AlienPc Swift (`ESP off`)? See card 21 for AlienPc Forge's own model.
14. **`W3b`:** install duckyshell Standalone if its license is open?
15. **`H6`:** try Gufo NPU offload (hang risk; fabric-clock hold required)? Recommended: later, after Waves 1-2.
16. **`W5`:** tag ~20 `jc-test` pictures? Recommended: skip unless you want it.
17. **`RV4`:** consider Guide / AudioRefine nodes? Separate yes each, and only after RV0-RV3.
18. **`R2`/`R3`/`R4`/`R6`/`R7` and each `M*` / `RV0` / `RV3` step:** yes at the time, not in advance. `R6`/`R7` stay later.
19. **Miraclein downloads:** yes to NVFP4 (4.82 GB, Civitai login is yours)? TE + VAE are already on AlienPc (no ~9 GB download). FP8 (8.46 GB) only if NVFP4 fails.
20. *(Removed: AlienPc Forge already exists and is used as an owner above.)*
21. **AlienPc Forge model:** it defaults to `coding_swift15_iq3s_esp` (ESP on) while F4/H1c want opportunistic Swift with ESP off. Keep Forge on `_esp` and use `coding_swift15_iq3s` only for `pi-job` overflow, or switch Forge too? Recommended: keep Forge as is; H1c uses the non-ESP slot.
22. **`R2` download:** re-download `10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ` (>5 GB, size not re-verified; the `int8HQ` sibling is 22.9 GB) to AlienPc `models\diffusion_models\`? Recommended: only if you still want the R2 A/B; F4's evidence puts its speed (127.0 s vs 143.8 s) within seed noise in Terrace v3.
23. **`ST3` PixlStash memory (Finding 11):** Current `10-memcap.conf` is `MemoryHigh=8G`, `MemoryMax=10G`, `MemorySwapMax=2G` (raised 5G→8G today, t2584); PixlStash sits above 8G with swap full and 2.37 M throttle events since 8:50 AM CT. Proposal: raise to `MemoryHigh=12G`, `MemoryMax=14G`, `MemorySwapMax=2G` (verify `MemAvailable >= 4 GiB` with Gufo + PixlStash at cap), or keep `8G / 10G / 2G` and accept slower imports? Restart only when no render or import runs.
24. **`ST5` depth LoRA:** download the RefControl Klein 9B depth LoRA (small, HF `thedeoxen/refcontrol-FLUX.2-klein-9B-reference-depth-lora`) for "same background/layout" stills? Pose needs nothing new.
25. **Inventory:** the two FCSydny LoRA strength variants (`b2_fc_sydney_lora_s05/_s08.api.json`) are kept out of git by the `*sydney*` ignore rule and carry a baked prompt. Leave them out (default), or add them with the prompt node blanked?
26. **`ST1` behaviour:** exclude the last 20 picks and sample 6 of the top 18 (default), or keep the old fixed top 6 behind a `--fixed` flag only?
27. **(M1 — RESOLVED 2026-11-19 11:11/11:16 CT) Opus/Gemini delivery & Gitea divergence:** File-only work is authored in VS Code on Derrick's PC on `opus/<group>` branches and pushed to GitHub `mono`. Max fetches `mono` on the box, reviews, runs gitleaks, fast-forwards Gitea (if Gitea moved: merge on the box, never force), then the machine's Forge applies under lease.
28. **(M2) Lease take/release files for pi Forges and Hydrogen (Finding 3):** Can X3 Forge, AlienPc Forge, and Hydrogen write directly to the brain `30_handoff/status/`, or does Max write/mirror the take and release files in `records/status/` for every brief? Recommended: Max writes take/release in brain + `records/status/` on brief issue/closeout unless verified writable.
29. **(M3) AlienPc GPU sharing during Forge GPU steps (Finding 2):** Before running `S2`, `M0-M5`, `ST4/ST5`, or `R1-R7`, verify what `:8447 --fail-if-busy` reports while `coding_swift15_iq3s_esp` is resident and whether starting `comfyui_auto` evicts it. Choose operating mode: (a) point AlienPc Forge at X3 Gufo over tailnet while driving ComfyUI, or (b) run a fixed script from the brief and let Forge read the output afterward. Recommended: (b) for scripted tests, (a) if interactive.
30. **(M4) `still_read` adult/scale signal (Finding 7):** Does `still_read.json` already produce an adult/scale field for uploaded (`ST2`) and reference (`ST5`) images, or should we add one before enabling `ST2`/`ST5`? Recommended: verify schema first; add an explicit adult/scale stop before any GPU job.
31. **(M5) `pick.json` `"still"` format:** Confirm whether `runs/*/pick.json` `"still"` stores a PixlStash picture ID or a file path so `ST1` excludes recent picks accurately. Recommended: support both ID and basename/path in `ST1` (verify against live `pick.json`).
32. **(M6) Live editable path for Linux dual-boot plan (`LX1-LX9`):** Where does the editable Linux dual-boot plan live (only the `evo-x3-all` snapshot is linked, and C15 forbids editing the snapshot)? Recommended: confirm path on `mono`/`u58` before `LX1-LX9` edits land.
33. **(M7) AlienPc `C:\AI\community` dirty files vs `templates/`:** Confirm whether any of the 131 dirty files on AlienPc `C:\AI\community` overlap `templates/` before `G2`, `ST4`, or `ST5` apply (`git pull --ff-only` would fail on overlap). Recommended: check `git status -- templates/` in the first AlienPc brief.
34. **(M8) Auto-importing `ST2` uploads into PixlStash:** Auto-copy uploaded stills in `ST2` into `/home/evo/AI/pixl-inbox/` after run setup (default), or only on explicit ask? Recommended: auto-import (default).
35. **(M9) Open sizes & licenses:** Confirm `activation_learned_HQ` file size before `R2` download (Card 22) and `duckyshell` Standalone license before `W3b` install (Card 14).

## Grounding (read-only)

First pass 2026-11-19 10:28-10:32 AM CT; full live re-audit 10:42-10:55 AM CT. The audit table ("Live audit", A1-A31) replaces the earlier bullet list; the earlier list relied on committed inventory for AlienPc and missed AlienPc Forge.

- Source blobs on `evo-x3-all` match (A31). Hermes and monorepo plans are on `u58` (Gitea + GitHub) and in the brain under `40_projects/`.
- X3 `~/evo-x3` checkout was at `dcb91e5` during the 10:45 AM CT audit (behind `u58` `e0c446f` / `65fa220`, A23).
- Remaining Hydrogen usage: UNKNOWN (A9).

## Verification Contract

| Check | How |
|---|---|
| No source ID dropped | Every `W* G* H* R* S* L* LX* M* RV*` ID appears in the item tables (G1/G5/F4§0 marked already done). |
| File-only vs live | Opus column is yes only for work that is a GitHub file edit with no live run, install, download, GPU, or secret. |
| Render gate | Every render row names Derrick's Hermes-chat yes. |
| Apply path | Each `opus/<group>` push to GitHub `mono` follows import-and-apply (fast-forward Gitea or merge if Gitea moved, never force; `u58` copies use the Install rule + re-snapshot). |
| Machines | Flux/ComfyUI rows are AlienPc; prompt-writing rows are X3. |
| Owners | Every live row names X3 Forge, AlienPc Forge, Hydrogen, the Render path (queue) or Derrick; Max appears only for briefs, imports, verify, secrets. |
| Audit | Each "Live audit" row cites a command or file read; no row relies on repo files alone for live state. |
| Stills | `ST1` unit test (different sheets, recent picks excluded); `ST2` no PixlStash call during an ask with an upload + mocked `still_read` 18+ stop; `ST3` sync service < 30 s and `pixl-import` unit survives exit; `ST4`/`ST5` stills in `_inputs/` with text + image 18+ stops before GPU and runtime GPU lock guard. |
| Inventory | Every row in the inventory table is "already there", "added", "updated" or "skipped + reason"; gitleaks clean on added files. |

## Definition of Done (for a future work run, not this file)

Wave items marked DONE in `records/unified-implementation/RESULT.md` with evidence; leases cleared; decision answers recorded; Gitea and GitHub tips match; no secrets in git.

## Rollback (plan file)

The plan commits touch only `records/*/PLAN.md` and the read-only copies under `hosts/alienpc/live/` and two files under `hosts/x3/live/`. Revert the commit if needed. No live checkout, service, or other branch is changed.

## Appendix: research-core record

research-core used: yes, §0 community line only (QUICK). Question: how to sequence the four already-reviewed plans with Hermes + monorepo without leftover usage. Window: the four plans' own evidence tables (Nov 18-19) plus live read-only checks (Nov 19 10:28-10:32 AM CT). Audit pass added web research for Stills intake only (accessed 2026-11-19): thedeoxen/refcontrol README + HF cards (Klein 9B pose/depth LoRAs), yanokusnir-ai/one-node-flux-2-klein (POSE mode needs DWPose + RefControl), Pikselkroken/pixlstash commit `79e2946` (task-based import, 600-poll client cap) and architecture doc `aaa9206` (post-import pipeline stages), nesquena/hermes-webui README + PR #2319/#2382 (attachment inbox path). Other claims stay attributed to the source evidence tables. Community/stock setups preferred: `cookiecutter-uv`, `JuneYaooo/rea-video`, upstream Hermes skills, git-clone Comfy nodes, existing `wp_accept.py` / `lint.py` / `pi-job` / `queue-remote.sh`.

CE steps: plan Durable (this file) · brainstorm: short merge only, no separate doc (Derrick / parent) · doc review: skipped here, handed to Opus on GitHub · work not started · compound n/a.
