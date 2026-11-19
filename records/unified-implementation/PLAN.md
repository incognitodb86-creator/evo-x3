---
title: "Unified implementation plan: F4 + Linux changes + Miraclein + REA-Video"
date: 2026-11-19
type: plan
artifact_contract: ce-unified-plan/v1
product_contract_source: derrick-chat (t2631u, t2632u)
execution: code
tier: T2 Durable (Derrick asked for a plan file; >1 device; four source plans)
author: Max Architect (executor subagent). PLAN ONLY. Nothing applied on the X3 or AlienPc.
review: skipped here; outside AI (Opus via GitHub Copilot) reviews this file on GitHub (Derrick t2631u)
pending_upload: true
---

Related: [Hermes two-path plan](../hermes-direct-render/PLAN.md) · [monorepo plan](../monorepo-consolidation/PLAN.md) · source plans on `evo-x3-all` (blob SHAs verified 2026-11-19 ~10:28 AM CT):
[Linux LX1-LX9](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-18-alienpc-linux-plan-changes.md) `078da632` ·
[Miraclein M0-M5](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-19-alienpc-miraclein43-refmods-h3max-realism-plan.md) `ca1a6a94` ·
[REA-Video RV0-RV5](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-19-rea-video-h3max-beta7-plan.md) `591680d8` ·
[Follow-up F4](https://github.com/incognitodb86-creator/evo-x3/blob/evo-x3-all/plans/2026-11-18-x3-alienpc-followup-plan.md) `f2120900`

# Unified implementation plan (F4 + LX + M + RV)

PLAN ONLY. No live change, install, download, render, lease, or merge is started by this file. Source IDs are kept (`W*`, `G*`, `H*`, `R*`, `S*`, `L*`, `LX*`, `M*`, `RV*`). No source item is dropped; optional items stay optional. Labels: VERIFIED = read live or hashed on 2026-11-19 between 10:28 and 10:32 AM CT (America/Chicago); ASSUMPTION = must be tested in the step that uses it.

## Goal Capsule

| Field | Value |
|---|---|
| Objective | Carry out the four new reviewer plans as one sequenced body of work, without redoing what is already live, and without stepping on the Hermes or monorepo plans already on `u58`. |
| Means | File-only edits go to Opus on GitHub first. Live X3 work goes to X3 Forge (`/home/evo/AI/forge`, one-line goal + `records/<id>/BRIEF.md` + `RESULT.md`) or Hydrogen (`agy`, `gemini-4-hydrogen`) when a strong live run is needed. Max writes briefs, imports Opus commits, verifies RESULT files, and does only tiny or direct fixes. Flux and ComfyUI stay on AlienPc, queued from the X3. |
| Authority | Derrick t2631u (pull the four plans; ce-brainstorm + ce-plan; conserve usage; Forge + Hydrogen; Flux/ComfyUI on AlienPc, prompts on X3) and t2632u (fourth owner: Opus on GitHub for file-only work). |
| Out of scope until their own yes | Hermes two-path setup (`records/hermes-direct-render/PLAN.md`). Monorepo merge (`records/monorepo-consolidation/PLAN.md`, Q1-Q7 still open). The Linux dual-boot plan itself (rev 4, reviewed NOT READY Nov 16) — `LX1-LX9` amend that plan; they are not a go to install Linux. QNAP general cleanup (deferred). |

## One-page summary

Four sibling plans landed on GitHub `evo-x3-all` this morning (blob SHAs above, VERIFIED). F4 is the trunk: X3 Gufo stays primary for daily chat and coding, AlienPc stays render-first with opportunistic Swift (`ESP off`) when idle, and the specialized tracks (Linux amendments, Miraclein RefMods + realism LoRA, REA-Video shot breakdown) hook into F4's writer bakeoff (`W1-W4`), safety (`S1-S2`), speed tests (`R1-R7`), and Hermes closeout (`H1-H6`).

Work is done in waves so independent tracks run in parallel. File-only work is handed to Opus on GitHub (Copilot can only see GitHub). Max later fetches that commit, reviews the diff, scans for secrets, applies it under a lease, verifies, and pushes to Gitea (GitHub already has Opus's commit; Max fast-forwards Gitea to the same SHA). Live runs, installs, downloads, GPU, secrets, and test renders stay off GitHub and go to X3 Forge, Hydrogen, or Max under an AlienPc lease.

There is **no live AlienPc Forge / pi coding chat today** (VERIFIED against `hosts/SETUP-MAP.md`, `hosts/alienpc/**`, and the `alienpc-community` / `alienpc-render` trees: only an Oct 23 archived `ralph-community` and a historical Start Menu "Start Forge" shortcut, not a current coding pane). This plan does not invent one. Until Derrick asks to set one up, AlienPc GPU and install work is Max under an AlienPc lease, with prompts and queueing from the X3 as they are now (`render-pi.sh` / `render_writer_pipeline.py` / `queue-remote.sh`).

Remaining Antigravity / Hydrogen usage is **UNKNOWN**: `agy` on the X3 has no stock usage or quota subcommand (VERIFIED `agy help`, 10:31 AM CT). Use Hydrogen only where a strong live coding or scoring pass is worth it (`W1` analysis, hard packages if Opus does not take them). Prefer Opus for file-only work so both Max and Hydrogen are saved.

Nothing below starts until Derrick (or Opus's review plus Derrick's yes) says go.

## Derrick's asks (word for word, with pass test and gate)

| ID | Ask | Pass test | Gate |
|---|---|---|---|
| R-ASK1 | Pull the four new plans and implement all of them the best way, conserving usage. | This file lists every source ID from those four plans, with owner, machine, lease, verify artifact, and rollback. No ID is dropped. | Max (this plan). Execution starts only on Derrick's yes. |
| R-ASK2 | Use X3 Forge and AlienPc Forge where they can, and remaining Hydrogen, so Max's usage stays low. | Each item names an owner. File-only items prefer Opus. Live X3 coding/tests prefer Forge or Hydrogen. Max is brief / apply / verify / tiny fix only. | Owner column in the item table. |
| R-ASK3 | All Flux and ComfyUI work continues on AlienPc, with prompts and writing made on the X3 like the current setup. | No second ComfyUI, no Flux/Comfy work on the X3, no in-graph writer after the approval hash. Prompts come from X3 Gufo / `W1-W3` winner / later Hermes paths. | S2 allowlist (no LLM nodes); standing render path. |
| R-ASK4 | Fourth owner: Opus on GitHub for file-only work. Max pulls the commit and applies it on the machine. | Every item is marked Opus-eligible or not. The import-and-apply step below is followed after each Opus commit. | Max-apply; secrets scan must be clean. |

## Product Contract (merged requirements, short)

Brainstorm was kept short: the four source plans already state what to build. This section only records the merge, the overlaps, and the conflicts. There is no separate ce-brainstorm file.

- Keep live state from F4 section 0: Gufo `0.35.0` `flash-next-uncensored-v2` is X3 daily driver and primary coder; do not redo G0; do not switch X3 to Swift 1.5 today; Halogen stays cold rollback. `U56 Decision #1` (header-free Beta 7) and `U56 Decision #2` (no voice ref on named parodies) stay in force.
- Shared contract for every Beta 7 prompt path (writer pipeline, duckyshell, pytraveler, REA-Video, later Hermes Path A/B): one `beta7_convert.py` + live `lint.py`. No second converter.
- Flux / Klein9 / Miraclein / H3 LoRA / ComfyUI node work: AlienPc ComfyUI `0.38.0` at `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` only, under lease, git-clone installs (never Manager web UI once `S1` is `strong`).
- Every H3 render needs Derrick's yes in his Hermes chat. `queue-remote.sh` already runs RTX 2x; `sync-renders` publishes only clips with `render_ok.json.upscale`.
- `pi-job code` / `review` stay. Only the render part of `pi-job` may retire later, and only on Derrick's yes after the Hermes bakeoff (Hermes plan R13). `H1` flips coding to X3-primary; it does not retire render.
- Never view PixlStash library contents. `M2` may use stills Derrick picks or a path list; Max counts only.
- Gitea is primary. GitHub is the reviewer's only view, so every Gitea push is followed by a fast-forward GitHub push from the box. No force push. No `git add -A`.

## Conflicts, overlaps, and holds

| # | Conflict or overlap | Rule in this plan |
|---|---|---|
| C1 | Hermes two-path plan vs `H4` skill prune vs `W3` duckyshell | All three share `beta7_convert.py` and `lint.py`. `H4` must keep / adapt the planned `h3-writer` skill (Path B) and `OPERATOR.md` desk; it must not invent a third writer path or install an unguarded ComfyUI MCP. Hermes U0-U9 stay held until that plan is reviewed and Derrick says go. |
| C2 | Monorepo vs all file work | Until `mono` exists and Q1-Q7 are answered, Opus edits the **current part branches** in [SETUP-MAP](https://github.com/incognitodb86-creator/evo-x3/blob/u58/hosts/SETUP-MAP.md), not only the `evo-x3-all` snapshot. Do not start filter-repo / live symlink cutover in the middle of path-sensitive edits. Freeze, then monorepo (Wave 5). |
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
| C14 | Downloads over ~5 GB | `W2` arms (15-18 GB), Miraclein TE+VAE if missing (~9 GB), and FP8 fallback (8.46 GB) each need a yes. NVFP4 is 4.82 GB: still ask, because it is close and Civitai login is required. REA-Video CPU caches (~67+149 MB) are under the bar; still mention them at `RV0` yes. |
| C15 | `evo-x3-all` is a snapshot | Reviewer plan commits already landed there. Implementation edits belong on the live part branches (`u58`, `x3-community`, `x3-render`, `alienpc-community`, …). After each apply, Max mirrors Gitea → GitHub so Copilot stays current. |

## Owners and usage strategy

| Owner | What they do | What they never do |
|---|---|---|
| **Opus on GitHub** | File-only: AGENTS.md, OPERATOR.md, SOUL, skills, config *text* (llama-swap.yaml, Hermes `config.yaml`, pi settings, systemd unit text), briefs, docs, scripts and templates that do not need a live run. Preferred for all of that (t2632u). | Live runs, installs, downloads, GPU, secrets, test renders, Gitea, X3, AlienPc, force pushes. |
| **X3 Forge** | Live X3 execution of a one-line goal plus `records/<id>/BRIEF.md`; writes `RESULT.md`. Chooses its own method. Good for `wp_accept` runs, `RV0` CPU decompose, `H1` concurrent Hermes+code test, `H5` sample after the scaffold exists, unit tests after an apply. | Starting its own renders without Derrick's Hermes yes. Editing `llama-swap.yaml` during a render. |
| **AlienPc Forge** | **Not available today** (VERIFIED). Do not invent it. Proposed later only on Derrick's yes: a Windows pi pane at `C:\AI\forge` with the same BRIEF/RESULT pattern, reached only when `:8447 --fail-if-busy` says idle, never during ComfyUI. | — |
| **Hydrogen** (`agy`, `gemini-4-hydrogen` on the X3) | Hard live coding or scoring that is worth the remaining (unknown) quota: `W1` bakeoff analysis if Forge should not judge quality, or `RV2` if Opus does not take the package. Prefer low/medium effort; reserve xhigh for a stuck scoring or a hard test failure. | File-only work Opus can do. Secret handling. Renders. |
| **Max-apply / Max-verify** | Briefs, import-and-apply (below), RESULT checks, tiny or direct fixes, Gitea+GitHub mirrors. AlienPc installs and GPU steps until a Forge exists there. | Guessing. Viewing PixlStash contents. Running Render jobs (queue only after Derrick's yes). |
| **Derrick** | Decision cards, Hermes-chat render yes, Tailscale Admin, logins (Civitai), any secret typing except the already-allowed PixlStash token copy, downloads over ~5 GB, new software, deletes, widened access. | — |

## Opus on GitHub

Opus can only read and write files in `incognitodb86-creator/evo-x3`. It has no X3, AlienPc, Gitea, or chat access, so this file and the source plans must carry the context.

**Which branch to edit** (from SETUP-MAP; do not dump everything onto `evo-x3-all`):

| Kind of file | Branch | Typical paths |
|---|---|---|
| This plan, host config, Hermes config/SOUL/skills list, systemd unit *text*, pi-job script copies, briefs | `u58` | `records/`, `config/`, `hosts/x3/hermes/`, `hosts/x3/systemd/`, `config/bin/`, `config/pi-evo/` |
| OPERATOR.md, writer_pipeline, `queue-remote.sh` | `x3-render` | repo root |
| `beta7_convert.py`, `lint.py` hooks, H3 skills, U55 templates, `remote_upscale.py`, `run_queue.py` | `x3-community` | `scripts/parody/`, `skills/`, `templates/` |
| X3 Forge records / ralph-community | `u58-chat-read-plan` | repo root |
| AlienPc API templates and community scripts | `alienpc-community` | `templates/`, `scripts/` |
| AlienPc render scripts | `alienpc-render` | repo root |

**Opus-eligible items (preferred):** `W3` converter (`beta7_convert.py` + tests), `W4` config *drafts*, `G2` template `unet_name` edits, `G4` AGENTS.md / `writer_prompt.md` audit, `H1` `pi-job` routing *script*, `H2` Hermes config *draft* (no keys), `H3` routine and unit *text*, `H4` skill prune/adapt, `H5` cookiecutter + Makefile + AGENTS.md, `R5` poll interval, `S2` allowlist *script*, `L1-L8`, `LX1-LX9` documentation amendments to the Linux plan, `M4` candidate API template *drafts*, `RV1` capabilities YAML, `RV2` `h3max_bridge.py` package (tests included). Hermes Path B `h3-writer` skill *after* that plan is approved.

**Not Opus:** `W1`/`W2` live bakeoffs, `W3` duckyshell install, `W5`, `G3` / any test render, `H1` ACL apply and ntfy token, `H2` live SSRF proxy, `H6` NPU, `R1-R4`/`R6-R7`, `S1`, `M0-M5` live installs and A/B, `RV0`/`RV3-RV5` live, secrets, downloads, GPU.

**Import-and-apply (Max, after each Opus commit):**

1. On the box: `git fetch origin <branch>` and note the new SHA. Review the full diff. Run `gitleaks` (or the repo's usual secret scan) on that range. Stop on any secret, credential, or `.env` / token file. Do not print secrets.
2. Fast-forward that same SHA to Gitea (`git push gitea <sha>:refs/heads/<branch>`, no force). Gitea stays primary and matches GitHub.
3. On the machine that owns the checkout (X3 lease for X3 paths, AlienPc lease for AlienPc paths): back up the touched files under `_archive/<date>/`, then `git pull --ff-only` from Gitea. Do not restart llama-swap, Hermes, or ComfyUI unless the item says so, and never edit `llama-swap.yaml` during a render.
4. Run the item's verify command. If it fails, roll back from the backup / `git revert` (no force) and record it. If it passes, leave a short `records/<id>/APPLY.md` and mirror any additional local commit to Gitea, then GitHub.
5. A declined or dirty secret scan is final for that commit. Ask Opus to rewrite without the secret; do not scrub history unless Derrick says so.

## Waves (order)

Independent tracks inside a wave run in parallel. A blocked item does not hold a later item that does not depend on it. X3 work does not wait on AlienPc clips.

- **Wave 0 — Review and cards (no live change).** Opus reviews this file plus the Hermes and monorepo plans. Derrick answers the cards in "Decision cards" that unblock Wave 1 (`S1`, `S2`, `W3` converter, whether to start file-only now). Hermes U0-U9 and monorepo S0-S7 stay held.
- **Wave 1 — Shared safety and converters (unblocks the rest).** `S1` (live, Derrick yes). `S2` script (Opus) then apply + planted-graph test (Max, AlienPc lease). `beta7_convert.py` (Opus, `x3-community`). `H5` harness (Opus). `G4` file audit (Opus). `H4` skill prune/adapt (Opus; keep planned `h3-writer`). `R5` (Opus + apply). Optional `L1-L8` file work (Opus) can start here; live verify later.
- **Wave 2 — Parallel tracks.** **Writer:** `W1` (X3 Forge runs the harness; Hydrogen scores if needed; 0 GB download). `G2` files then smoke (Derrick yes). `G6` before `W4`. `W2` only if Derrick wants more after `W1`. `W3b` duckyshell install after license card. **Speed (AlienPc lease, no quality-changing stack until R2/R6 yes):** `R1` measure, then `R2-R4`, `R6`/`R7` later. **H1 closeout:** `P2.4` (Derrick in Tailscale Admin), `P4.11` token (secret, Max), `pi-job` X3-primary script (Opus then apply), Phase 5 `P5.1`/`P5.2`/`P5.4` on AlienPc (Max; Tailscale Serve stays off unless a separate yes). `H2` after `P2.4`. `H3` after ntfy is in place. **Miraclein:** `M0-M5` on AlienPc under lease, one step at a time, Derrick yes per install/download/restart/promotion. **REA-Video:** `RV0` on X3 (CPU) in parallel with Miraclein; `RV1` (Opus); `RV2` after converter + harness; `RV3`/`RV5` after render yes; `RV4` only with a separate yes.
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
| W3a | **yes** (`x3-community` `scripts/parody/beta7_convert.py` + tests) | Max-apply, then X3 Forge tests | X3 | X3 | M | One shared Beta 7 converter used by duckyshell, pytraveler, REA-Video, and later Hermes. | Unit tests + `lint.py` READY, 0 header violations on fixtures. | Revert the commit. |
| W3b | no | Max, Derrick yes | X3 and/or AlienPc | matching | M | Install duckyshell Standalone v0.1.10 if license is open. Point at X3 `/v1`. Never Direct GGUF/Ollama on AlienPc. Pass copied prompts through `W3a`. | App starts; one converted prompt passes `lint.py`. | Uninstall the app; no ComfyUI change. |
| W3c | no (config has keys) | Derrick card C5, then Max | AlienPc | AlienPc | M | Optional API Universal Writer + FX6 leak test. Off `S2` allowlist. | FX6 planted key absent from `/history`, metadata, QNAP outputs. | Disable the node; no key left in graphs. |
| W3d | no | Derrick render yes, Max queues | AlienPc via X3 | AlienPc | M | Same-seed 3-ask video check of pipeline vs duckyshell vs (if kept) API writer. | Three clips; Derrick pick recorded. | Candidate graphs only; production templates untouched. |
| W4 | draft **yes** (`x3-render` `writer_pipeline/config.yaml`, llama-swap fragment) | Max-apply after `G6`; Derrick yes to reload | X3 | X3 | M | Deploy W1-W3 winner without daytime thrash, as in F4. | Render-X3 / pipeline / duckyshell hit the winner; 0 interactive swaps. | Restore previous yaml from `_archive`. |
| W5 | no | Derrick optional | X3 | X3 | M | `jc-test` vs live JoyCaption only if Derrick tags ~20 pictures. | Best match stays on the 04:00 timer. | Keep live JoyCaption. |
| G2 | **yes** (`x3-community` / `alienpc-community` templates: `unet_name` only) | Max-apply; Derrick yes for 1 smoke each | both | both | M | `two_person`, `long_continuation`, `ref2va_16x9` to `beta7_int8HQ` (or R2 winner later). Size/frames unchanged. | `fill_request.py` dry-check; 1 smoke clip per template after yes. | Restore template backups. |
| G3 | no | Derrick render yes | AlienPc via X3 | AlienPc | S | After G2: 16:9 `--still-mode ref` vs `guide`, same seed. | One pair; crop/head-foot notes in RESULT. | No template promotion unless yes. |
| G4 | **yes** (AGENTS.md / `writer_prompt.md`) | Max-apply; Derrick card for voice-RefMod | X3 | X3 | S | Confirm ref-mode and hardcore rules still reach the writer. Leave `poolclub_refmod_audio` unchanged until the card. | Audit note in `records/G4/`. | Revert skill text. |
| G6 | no | Derrick decision | — | — | S | Does Sydney follow the writer pin or point at `flash-next-uncensored-v2`? Do this before W4. Do not open Sydney files to plan it. | Answer recorded. | — |
| H1a P2.4 | ACL *text* already drafted; apply is Derrick | Derrick in Tailscale Admin | — | — | S | Narrow ACL for ports with no login (`8443-8447`); same tag on Windows and Linux nodes. Serve stays off unless a separate yes. | ACL active in the console. | Derrick reverts the ACL. |
| H1b P4.11 | no (secret) | Max, Derrick yes | X3 | X3 | S | Write-only ntfy token in `/home/evo/.config/evo-x3/ntfy-x3.token` `0600`. Never commit it. | Token file mode 0600; a test notify works; not in git. | Remove the file. |
| H1c pi-job routing | **yes** (`u58` `config/bin/pi-job` / scripts; do not touch unrelated dirty copies) | Max-apply, X3 Forge live test | X3 (+ AlienPc idle probe) | X3, maybe AlienPc | M | X3 Gufo primary for `code`/`review`; opportunistic AlienPc Swift `ESP off` only when `:8447 --fail-if-busy` says idle or both Gufo sessions are busy. | Simultaneous Hermes chat + `pi-job code` on X3, 0 swaps; idle AlienPc path never interrupts a render. `PHASE-5-RESULT.md`. | Restore previous `pi-job`. |
| H1d P5.1/P5.2/P5.4 | no | Max | AlienPc | AlienPc | M | Finish AlienPc Phase 5 verification. | `PHASE-5-RESULT.md` committed. | Per main plan. |
| H2 | config *draft* **yes** (`u58` `hosts/x3/hermes/`) | Max-apply after H1a; live SSRF proxy is Max + Derrick yes | X3 | X3 | M | SearXNG search; network-layer SSRF block of loopback/tailnet/link-local except SearXNG. Approvals stay manual / unattended deny. | Search works; planted fetch to `:8080` and AlienPc `:8446` is blocked. | Restore Hermes config; remove proxy. |
| H3 | unit/routine *text* **yes** | Max-apply | X3 | X3 | S | Read-only morning status + weekly worktree report via ntfy. Avoid 04:00 JoyCaption window. | One on-time ntfy with zero secrets, 0 swaps. | Disable the timer. |
| H4 | **yes** (Hermes + pi skills) | Max-apply | X3 | X3 | M | Prune the 45 stock skills; adapt keepers to X3 paths, `U56 Decision #1`, `pi-job`, SearXNG, `/srv/renders`. Keep planned `h3-writer`. No unguarded Comfy MCP. | Hermes loader + `SKILL_SMOKE_OK`; no broken paths. | Restore skill tree from backup. |
| H5 | **yes** (template, Makefile, AGENTS.md) | Max-apply; X3 Forge does the sample change | X3 | X3 | M | `cookiecutter-uv` + `make check-all` required before `pi-job code` returns DONE on repos that have it. Used by `RV2`. | Sample tool: change + `make check-all` green, else not DONE. | Leave legacy scripts alone. |
| H6 | no | Optional, Derrick yes; Max | X3 | X3 | L | Gufo NPU offload with fabric-clock hold (`ROCm/TheRock#8709`). One service at a time, 15 min stress. | 0 hangs, `NRestarts=0`, `MemAvailable >= 4 GiB`. | Disable `--npu` immediately on hang. |
| R1 | no | Max | AlienPc | AlienPc | S | Per-stage timing, no change. | Timing table in `records/R1/`. | None. |
| R2 | no (test graphs only) | Derrick yes, Max queues | AlienPc via X3 | AlienPc | M | `beta7_activation_learned_HQ` vs `int8HQ`, 3 seeds, 2-pass and 1-pass, blind pick. | Tie or better on both graphs. | Keep `int8HQ` in production templates. |
| R3 | no | Derrick yes | AlienPc | AlienPc | S | `--disable-fast-disk` only if R1 logs `fast_disk=True`. Keep `--disable-pinned-memory`. | Median faster and frames match. | Restore argv. |
| R4 | no | Derrick yes | AlienPc | AlienPc | S | `Prefer No Sysmem Fallback` for ComfyUI `python.exe`. | Faster and 0 OOM in 5 renders. | Driver Default. |
| R5 | **yes** (`x3-render` `queue-remote.sh`) | Max-apply | X3 | none for the file | S | Poll "BATCH closed" every 5 s instead of 30 s. | Notice is faster; renders unchanged. | Revert the script. |
| R6 | no | Later, Derrick yes | AlienPc | AlienPc | M | `--fast fp16_accumulation`, then `cublas_ops`, one at a time. Never `fp8_matrix_mult` or `autotune`. | Blind same-seed tie or better. | Drop the flag. |
| R7 | no | Later, own job, Derrick yes | AlienPc | AlienPc | L | ComfyUI upgrade from `0.38.0`. Snapshot first. Can also unblock Klein9 `comfy_api.latest` if M3 fails. | Every template still renders; median not slower. | Restore snapshot. |
| S1 | no | Derrick yes, Max | AlienPc | AlienPc | S | Manager `strong` on `comfyui_auto` and `comfyui_longvideo`. Installs via git clone only. | Manager install/restart via `:8446` refused; B2 still renders. | Restore `config.ini`. |
| S2 | script **yes** | Max-apply + live test | AlienPc | AlienPc | M | Allowlist: 8 U55 + `b2` + `b2_refmod` + 3-node RTX VSR graph + later promoted templates. No LLM-node graphs. Prompt/seed/inputs/RefMods/frames/prefix may vary. | Planted extra node refused; 1 B2 and 1 `pi-job upscale` pass. | Disable the check; keep publishing path. |
| L1 | **yes** | Max-apply | X3 | X3 when verifying | S | ntfy Copy button on approval (`queue <run_id> <code>`). | QNAP v2.35.0 shows Copy. | Revert `pi-job` header. |
| L2 | **yes** | Max-apply | X3 | X3 when verifying | S | Poster frame grab per clip into `/srv/renders/<run_id>.jpg`. | Hermes shows a preview. | Revert `sync-renders`. |
| L3 | **yes** | Max-apply | X3 | X3 when verifying | S | Nightly stale worktrees >7 days: save status/diff, then remove+prune. | Timer report in `_runs`. | Disable that timer line. |
| L4 | **yes** | Max-apply | X3 | X3 when verifying | S | Contact sheet in chat + `pi-job render --pick N`. | Sheet in dry-run reply. | Revert those lines. |
| L5 | **yes** | Max-apply | X3 | X3 when verifying | S | `pi-job status` overview (no job ID). | Status prints model, memory, last 3 jobs. | Revert the subcommand. |
| L6 | **yes** | Max-apply | X3 | X3 when verifying | S | STUCK bundle `escalate.md` with task, diff, last errors. | File written on STUCK. | Revert those lines. |
| L7 | **yes** | Max-apply | X3 | X3 when verifying | S | Syntax check extension (`py_compile` / `bash -n` / `jq empty`). | Errors appear in tool output. | Remove the extension. |
| L8 | **yes** | Max-apply | X3 | X3 when verifying | S | `pi-job recompile <run_id>` after prompt edit; new P4.11 code. | New code matches new prompt hash. | Revert the subcommand. |

### Miraclein (`M0-M5`) — AlienPc ComfyUI only, prompts from X3

| ID | Opus file? | Owner | Machine | Lease | Size | What | Verify | Rollback |
|---|---|---|---|---|---|---|---|---|
| M0 | no | Max, Derrick yes | AlienPc | AlienPc | S | Pre-flight: ≥25 GB free, no GPU job, check TE/VAE/Beta 7 presence, snapshot `ComfyUI-MiniMaxH3Mod` at `517e8c41`, archive under `ComfyUI\_archive\20261119_pre_miraclein\`. | Backup + snapshot exist. | — (this is the rollback base). |
| M1 | no | Max, Derrick yes | AlienPc | AlienPc | M | Update MiniMaxH3Mod to pinned `54f93eb6`. Import smoke on 0.38.0. Do not overwrite torch / OpenCV. | `comfyui_auto` starts clean; existing RefMod smoke still works. | `git checkout 517e8c41` + restart. |
| M2 | no | Max, Derrick yes; Derrick picks stills | AlienPc | AlienPc | M | Standalone H3 RefMod extract (node and/or CLI). No PixlStash library viewing. Header-free prompt, omit `<Picture N>`. | New RefMod loads; 1-clip likeness check by Derrick. | Delete the new `.safetensors`; leave `models\refmods\` otherwise untouched. |
| M3 | no | Max, Derrick yes (download + clone) | AlienPc | AlienPc | L | Miraclein NVFP4 4.82 GB + TE/VAE if missing + Flux2Klein9Mod. **Import-check `comfy_api.latest` on 0.38.0 first.** FP8 only if NVFP4 fails (8.46 GB, separate yes). | Zero import errors; 4 Klein9 nodes in `/object_info`. | Remove the new node and weights; if import fails, defer to R7 or a local shim (Derrick yes). |
| M4 | template *draft* **yes** | X3 writes prompts; Max runs stills; Derrick judges | AlienPc via X3 | AlienPc | M | Candidate start-still / edit templates (never overwrite locked Flux stills). 3 stills: T2I, RefMod, single-change edit. Peak VRAM < 16 GB, warm 6-15 s. | All 3 succeed; Derrick checks identity + skin. | Keep candidates; do not promote. |
| M5 | no | Derrick yes, Max queues | AlienPc via X3 | AlienPc | L | Realism LoRA A/B, header-free prompt, arms A/B/C as in the source plan (no `er_sde`). Promote + add to S2 only on yes. | Blind pick + timings recorded. | Remove LoRA / candidate templates; H3Mod back to `517e8c41` if needed. |

### REA-Video (`RV0-RV5`) — breakdown on X3, render on AlienPc

| ID | Opus file? | Owner | Machine | Lease | Size | What | Verify | Rollback |
|---|---|---|---|---|---|---|---|---|
| RV0 | no | X3 Forge, Derrick yes to clone + small CPU caches | X3 | X3 | M | Isolated `uv` venv, `.[asr]`, `--lang en` decompose of one 10-15 s clip; one shot to live Gufo; `lint.py`. | English `breakdown.json` + stems; 1 prompt READY, 0 header violations. | Remove the venv/clone; caches stay unless Derrick wants them gone. |
| RV1 | **yes** | Max-apply | X3 | none for the file | S | User capability YAML for `minimax-h3-10eros-beta7` under `~/.rea-video/` (upgrade-safe). | `rea-video models minimax-h3-10eros-beta7` + `validate_capabilities.py` clean. | Delete the user YAML. |
| RV2 | **yes** (prefer Opus; Hydrogen only if the package stalls) | X3 Forge runs `make check-all` | X3 | X3 | L | `h3max_bridge.py` with H5 harness: 17k+5 snap, `ffmpeg -an` proxies, `--refmod`, llama-swap call, shared `beta7_convert.py`. | `make check-all` green, including header-ban tests. | Revert the package. |
| RV3 | no | Derrick Hermes yes; Max queues | AlienPc via X3 | AlienPc | M | One frozen-template clip + RTX 2x + publish. | Clip in `/srv/renders`; Derrick visual/audio check. | Frozen copy only; production templates untouched. |
| RV4 | no | Optional, separate yes each node | AlienPc | AlienPc | M | Guide / AudioRefine nodes, 0.38.0 import check, fixed-seed A/B. | Keep only if Derrick scores an improvement. | Remove the node. |
| RV5 | no | Max after 2+ approved clips | X3 | none | S | Hard-cut concat only (no crossfades, no capsule-cinema). Publish final. | Joined mp4 plays with synced audio; record committed. | Keep the parts; drop the join. |

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

## Decision cards

Answer these in chat, or let Opus recommend and then confirm. Defaults below are Max's recommendation where one is safe; cards without a default stay open.

1. **Go ahead with this unified plan?** (hold all live work until yes.) Recommended: yes, as plan-only until you also say yes per live step.
2. **Start Wave 1 file-only now** (Opus on GitHub for `W3a`, `H4`, `H5`, `S2` script, `R5`, `LX` docs) **before** the Hermes and monorepo plans are fully reviewed? Recommended: yes for those file-only items; still hold Hermes U0-U9 and monorepo S0-S7.
3. **Hermes two-path plan:** go / hold / change after Opus reviews it? (Already waiting.)
4. **Monorepo Q1-Q7:** Max's recommendations are already in that plan (yes / tags only / keep u58 at root / scan-and-commit AlienPc dirty files / untrack mcp.json backups / credential manager / archive the two AlienPc repos). Confirm or override there.
5. **`S1`:** set ComfyUI-Manager to `strong` on both AlienPc instances now?
6. **`S2`:** build the server-side template allowlist (optional in F4; recommended here)?
7. **`W2`:** run Stage 2 downloads only if W1 loses? Recommended: yes, that default.
8. **`G6`:** Sydney follows the writer pin, or points at `flash-next-uncensored-v2`? Answer before W4. Do not ask Max to open Sydney files.
9. **`G4`:** keep `poolclub_refmod_audio` for `FCSydny` / `FCMegan`, or change? Leave unchanged until answered.
10. **`W3c` / LX8.1:** keep the API Universal Writer node? (One answer for Windows and later Linux.)
11. **`P2.4`:** apply the drafted Tailscale ACL in the Admin Console? Tailscale Serve stays off unless you also say yes.
12. **`P4.11`:** place the write-only ntfy token (you confirm; Max does not print it)?
13. **`H1c`:** flip `pi-job code`/`review` to X3-primary + opportunistic AlienPc Swift (`ESP off`)?
14. **`W3b`:** install duckyshell Standalone if its license is open?
15. **`H6`:** try Gufo NPU offload (hang risk; fabric-clock hold required)? Recommended: later, after Waves 1-2.
16. **`W5`:** tag ~20 `jc-test` pictures? Recommended: skip unless you want it.
17. **`RV4`:** consider Guide / AudioRefine nodes? Separate yes each, and only after RV0-RV3.
18. **`R2`/`R3`/`R4`/`R6`/`R7` and each `M*` / `RV0` / `RV3` step:** yes at the time, not in advance. `R6`/`R7` stay later.
19. **Miraclein downloads:** yes to NVFP4 (4.82 GB, Civitai login is yours)? Yes to TE+VAE if missing (~9 GB)? FP8 only if NVFP4 fails.
20. **Build an AlienPc Forge later?** Not required for this plan. If yes, it would be a new Windows pi pane at `C:\AI\forge`, idle-only, same BRIEF/RESULT pattern — a separate small plan, not invented here.

## Grounding (read-only, 2026-11-19 10:28-10:32 AM CT, America/Chicago)

- Source blobs on `evo-x3-all` match the stated SHAs (`git hash-object`, VERIFIED).
- X3 `~/evo-x3` is `u58` at `e03d666`, clean tracked tree, tracking `gitea/u58` (VERIFIED). Unrelated untracked files were left alone, including anything under Sydney panes (not opened).
- Ports up: `127.0.0.1:8080` (llama-swap), `:8642` (Hermes), Tailscale `:8443` and `:8445`. Disk ~936 GB free on root (VERIFIED). `/srv` is the same volume.
- X3 Forge: `/home/evo/AI/forge` exists (evo-owned; this login cannot list it). `pi-chats/forge-pi.sh` and `/home/derekboone/AI/forge` are present (VERIFIED).
- `agy` is installed; models include `gemini-4-hydrogen-*`. No stock usage/quota command (VERIFIED). Remaining Hydrogen usage: UNKNOWN.
- AlienPc Forge / pi coding chat: not present in the committed inventory (VERIFIED). ComfyUI inventory path matches `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI`.
- Hermes and monorepo plans are already on `u58` (Gitea + GitHub) and in the brain under `40_projects/`.

## Verification Contract

| Check | How |
|---|---|
| No source ID dropped | Every `W* G* H* R* S* L* LX* M* RV*` ID appears in the item tables (G1/G5/F4§0 marked already done). |
| File-only vs live | Opus column is yes only for work that is a GitHub file edit with no live run, install, download, GPU, or secret. |
| Render gate | Every render row names Derrick's Hermes-chat yes. |
| Apply path | Each Opus commit follows import-and-apply; Gitea SHA equals GitHub SHA after the push. |
| Machines | Flux/ComfyUI rows are AlienPc; prompt-writing rows are X3. |

## Definition of Done (for a future work run, not this file)

Wave items marked DONE in `records/unified-implementation/RESULT.md` with evidence; leases cleared; decision answers recorded; Gitea and GitHub tips match; no secrets in git.

## Rollback (plan file)

This commit adds only `records/unified-implementation/PLAN.md`. Revert that commit if needed. No live checkout, service, or other branch is changed.

## Appendix: research-core record

research-core used: yes, §0 community line only (QUICK). Question: how to sequence the four already-reviewed plans with Hermes + monorepo without leftover usage. Window: the four plans' own evidence tables (Nov 18-19) plus live read-only checks (Nov 19 10:28-10:32 AM CT). No new web research this turn; claims stay attributed to those source evidence tables. Community/stock setups preferred: `cookiecutter-uv`, `JuneYaooo/rea-video`, upstream Hermes skills, git-clone Comfy nodes, existing `wp_accept.py` / `lint.py` / `pi-job` / `queue-remote.sh`.

CE steps: plan Durable (this file) · brainstorm: short merge only, no separate doc (Derrick / parent) · doc review: skipped here, handed to Opus on GitHub · work not started · compound n/a.
