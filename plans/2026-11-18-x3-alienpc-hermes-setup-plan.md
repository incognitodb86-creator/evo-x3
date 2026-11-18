# EVO-X3 + AlienPC agent setup plan (v3.2: verified and simplified)

- **Status:** Active, v3.2, 2026-11-18 (evening). Goals unchanged. The starting point reflects the live Nov 17-18 state (next section), and v3.2 folds in the pre-Phase-0 red-team audit. This plan itself changes nothing on the machines.
- **Owner:** Derrick. Steps marked **Y** need his yes at the time.
- **Executor:** Max (GrokBot) via agy or Forge on the X3. Console-only steps (Tailscale ACL, typing keys) are Derrick's.
- **Tracking issue:** https://github.com/incognitodb86-creator/evo-x3/issues/1
- **Source of truth for machine state:** Gitea `derrick/evo-x3`. This GitHub repo is a snapshot.
- **Settings rule:** use the vendor-documented setting or one already proven on this box. Where neither exists, the plan says so and tests it before use.

## Starting point (live, 2026-11-18 evening)

Goals, decisions and phases are unchanged; the steps now start from this state. Everything below is committed on Gitea and GitHub at matching commits: X3 branch `u58` at `92bb886`, AlienPC `alienpc-community` at `3efb9ce` and `alienpc-render` at `c13e73a`. The branches fold into one repo on Thursday.

| Area | Now | Source |
|---|---|---|
| X3 main model | One resident model: Halogen 0.20.7 with the huihui uncensored HGN in slot `flash-next-uncensored`, preloaded when llama-swap starts and never unloaded (`ttl: 0`). A `halogen-only` profile pins `flash-next`, `flash-next-sub`, `gemma4-heretic` and `gemma4-heretic-sub` to it, so Gemma never loads. Vision is on. 4 slots share one 524,288-position KV pool, and thinking is capped at 8,192 tokens. | `u58` `2d73543`, `4ab1d15` |
| Memory recipe | Halogen's shared-host recipe: `HALOGEN_WEIGHTS_LOCK=1` (62 GiB locked), unlimited memlock, `vm.compact_unevictable_allowed=0`. About 17 GiB is left for everything else. | `2d73543`; gufo phase-1 RESULT (08:35 addendum) |
| Side models | ref2va-27b disabled ("not used"). JoyCaption on demand (`:8084`, 5-minute TTL). embed-small still configured on `:8083`. qwen27b unchanged; requesting it evicts the resident model. | `2d73543` |
| Panes | Forge-X3: `x3-local-coding/flash-next-uncensored` (temperature 0.6), thinking medium. Render-X3: `x3-local/flash-next-uncensored`, thinking low, the short `OPERATOR.md`, and stills from the PixlStash API. Thinking `off` broke tool calls, so Render moved to `low`. Sydney no longer starts on the X3. | `2d73543`, `32a46c0` |
| Tagger | `u42-pixlstash-tagger` disabled since Nov 17 (crash loop). PixlStash capped at 8 GB of memory. | gufo phase-1 RESULT (09:43 addendum) |
| gufo | Tested Nov 17 on 0.34.0. Tools, the 4-caller test and speed passed: prose decode 50 tok/s on the 18K bake-off fixture, against 61 for Halogen huihui in U26. The memory gate failed while Gemma and ref2va were resident, so it was reverted. The test also found an SELinux relabel (`:Z` on the other slots) that breaks gufo's file reads; the fix is `--security-opt label=disable` on its slot. | gufo phase-1 RESULT |
| v2 cutover | The johnlockejrr Huihui **v2** HGN (sha-verified, `/srv/models/flash-next-uncensored-v2-hgn`) was added as a new slot, with the aliases repointed to it. llama-swap refused the config (duplicate alias) and crash-looped for 24 minutes until the backup was restored. v2 never loaded, so it is untested. | `92bb886` |
| Other weights on disk | Huihui v2 GGUF `UD-Q4_K_XL-V2` (111 GB, sha-verified, no vision file) at `/srv/models/flash-next-uncensored-huihui-v2`. | gufo phase-1 RESULT |
| Chats and loops | U58 (Forge plan rev 2, in progress): Forge's compaction never fires (reserve 131,072 on a 262,144 window). Chats ran to 236K tokens with no compaction and lost the thread, and Max reports the shared KV pool at 98%. U58 fixes compaction and sets one session folder and one launcher per pane. Forge has no `loop-guard.ts`; Render loads `auto-continue.ts`. | `u58-chat-read-plan` `48f6f06` |
| AlienPC | Finished clips go to the QNAP `renders` share at `runs/<run>/clip/`. Render picks stills through the PixlStash API, has a write sandbox, and has the X3 prompt policy ported. | `98fbc30`, `5465fde`, `e8a1fcb`, `afcb86a` |

## What changed from v2

Every v2 claim was re-checked on 2026-11-18 against the repo records and primary sources (section 8). v3 drops what the evidence does not need.

| v2 item | Finding | v3 |
|---|---|---|
| AlienPC job service (HTTP verbs, token, Windows worktrees, git WIP handoff) plus preempt hooks in `queue-remote.sh`, `comfy-guarded.ps1` and `gpu_lock_gate.py` | Not needed. The AlienPC's ComfyUI stop command already waits for the render queue (ALI-156), and llama-swap waits for in-flight requests before a swap. Tailscale SSH cannot run as a server on Windows anyway. | pi always runs on the X3 and uses the AlienPC's Swift model over the network. When a render starts, the same pi session resumes on the X3 model (section 3). |
| Two Hermes profiles; two Forge panes | One Hermes profile without web tools removes web input. Repo files, RAG documents and dropped pictures still reach it, so P4.3 and P4.4 fence what it can do. For Forge, the Nov 16 audit's one-pane option with approval prompts is enough. | `Hermes-X3` and `Forge-X3`. A split stays an option (OD2). |
| Hermes `command_allowlist` as a fence | Wrong. It only pre-approves commands Hermes would flag as dangerous; other commands never needed approval. | The fence is Hermes's API-server toolset list plus the `evo` account (no sudo). |
| New model IDs (`flash-next-default`) and ports 8081..8086 | Members of an exclusive group share one port by design. Renaming forces every caller to change. | Keep all model IDs and ports. `flash-next` runs whatever wins Phase 0. |
| Skills `render-write`, `ref2va-rewrite`, `caption-image`, `pi-status`, `ask-grok` | Existing launchers and pipelines already do these jobs. | One `pi-job` script (roles `code`, `review`, `render`) with a status file. GrokBot stays manual. |
| Candidates: Quat3rnion Swift HGN, dymoo fork, Gemma gufo extension, censored Swift on gufo | Never load-tested, need a 250 GB gated download, list only Unsloth Gemma files, or fail D4. | Two candidates plus the proven slot (Phase 0). |
| QNAP copy of 341 GiB before testing; "<200-character paths" | About 684 GiB is free and candidates are tested one at a time. Public weights can be downloaded again. Git for Windows has an official long-path setting. | Manifest, then delete with a yes; `core.longpaths`. |
| Kept from v2 | Live Tailscale ports, tagger thrash, open gufo bugs, Swift's ESP setting, memory limits. | Carried into v3. |

## 1. Goal and acceptance

**Goal.** Derrick talks to one local assistant, **Hermes-X3**, in a phone browser (Open WebUI over Tailscale). Hermes answers on the uncensored Flash-Next that is the X3's main model and hands coding to **pi**. pi uses **Swift on the AlienPC** whenever the AlienPC is not rendering, and the X3's Flash-Next otherwise. Every chat shows which machine it is on. The agents stop looping, and both machines lose their clutter.

**Operator acceptance (AC-OP).** In Open WebUI (`https://evo-x3-1.tailf242b2.ts.net:8443`), model `Hermes-X3`:

1. A general question: answered.
2. A request a stock model refuses: answered, no refusal.
3. "Fix <small bug> in <repo>" while the AlienPC is idle: Hermes starts a job. Asking "status?" shows it running on `alienpc` Swift in its own worktree. It ends `DONE` with a commit on a job branch.
4. The same while a render is running on the AlienPC: the job runs on the X3's `flash-next`. Then start a render while a step-3 job is running: the render is not interrupted, and the job carries on with `flash-next` in the same pi session.

Also: every herdr and pi-mobile chat label ends in `-X3` or `-AlienPC`, and a deliberately impossible task ends `STUCK` at its time limit instead of looping.

**Cheapest falsifying check:** P0.1, about an hour with no restart: C2-C5 on the live Halogen v1 slot. It sets the bar every other candidate has to beat. If nothing beats it, it stays.

## 2. Decisions

| ID | Decision (Derrick, 2026-11-18) |
|---|---|
| D1 | pi is the only coding harness on both machines. |
| D2 | Hermes Agent runs always on, on the X3, as one profile, `Hermes-X3`. It hands coding and render prompts to pi launchers and never edits code itself. |
| D3 | GrokBot keeps running. Derrick talks to it directly when he wants it; Hermes has no GrokBot link. |
| D4 | Uncensored by default for the chat and coding models: Hermes's model, Forge, Swift. Gemma Heretic is already uncensored. JoyCaption, ref2va-27b and qwen27b are tools inside existing pipelines, not chat models. |
| D5 | X3 engines: Halogen, gufo and llama.cpp behind llama-swap, each model on the engine where it passes. Model IDs and ports stay as they are. |
| D6 | `flash-next` is the X3's one main model, for Hermes and for X3 coding. Everything else swaps with it through llama-swap. This is the community pattern: one strong shared model, specialist models loaded on demand. |
| D7 | Jobs per model. `flash-next` (the resident slot, live since Nov 17): Hermes, X3 coding fallback, render prompts and pictures (vision on). Swift (AlienPC): coding and review whenever the AlienPC is not rendering. `gemma4-heretic`: pinned to the resident slot, so it loads nothing. JoyCaption: on demand for tagging. ref2va-27b: disabled. `embed-small`: embeddings, or the NPU embedder if Halogen wins G0 (P4.10). `qwen27b`: unchanged, manual use only (stock model, so it can refuse). |
| D8 | The AlienPC keeps its Strata setup. Its GPU is for ComfyUI renders and Swift. |
| D9 | Render first: a render is never interrupted (the existing ALI-156 stop command waits for the render queue). A coding job using the AlienPC moves to the X3 model when a render starts, in the same pi session. |
| D10 | Batch jobs do not thrash the main model. Since Nov 17 the pins already do this. The PixlStash tagger (disabled since Nov 17) comes back on a nightly timer once P4.6 fixes it. JoyCaption shares memory with `flash-next` only if the memory test shows room. |
| D11 | Access: the existing Open WebUI on `:8443`. Hermes's API stays on loopback. No new Tailscale ports on the X3. |
| D12 | Model downloads one at a time, each with a yes. |
| D13 | Every live change needs Derrick's yes at that moment. |
| D14 | eGPU later. Nothing here blocks it: it becomes another llama-swap backend. |
| D15 | Every chat is labeled `<Role>-<Host>`: Hermes-X3, Forge-X3, Render-X3, Sydney-X3, Forge-AlienPC, Render-AlienPC, Sydney-AlienPC. Labels only; folders and launcher files keep their names. |
| D16 | Hygiene: git and etckeeper replace `.bak` copies. Run outputs go to `_runs/` and agent checkouts to `_worktrees/`, the folder `ralph.sh` already uses. Cold weights that can be downloaded again are deleted after a manifest, with a yes. |

Superseded, kept for history: U9/R5 "AlienPC render-only" and audit item I10 (by D8 and D9); U34 "Flash-Next on Halogen stock" (by gate G0); the Oct 10 plan's model choice (its safety ideas are kept).

Not in this plan: render-graph fixes (frame snapping, RefMod `max_frames`, template promotion) belong in the render repo's own fix list. Considered and rejected, so they aren't proposed again (section 8):
- `amd_iommu=off`: no speed gain on this box, and it removes the NPU.
- Porting the retired 1,233-line AlienPC guard/truncator: pi already truncates tool output.
- Running the empyrealworks Swift file on stock gufo: it needs a build upstream declined.
- A second picture-search index (`embeddinggemma-2` or `wemm-embedding-4b` over the library): PixlStash already ranks pictures with its own CLIP and SBERT embeddings. The other unused NPU models are also left out: `flux2-klein-4b`, `qwen3.5-2b` and the deciders. ComfyUI and Flash-Next already do those jobs.

## 3. How it fits together

```
Phone browser --Tailscale :8443--> Open WebUI (X3, 127.0.0.1:3000, host network)
                                     --> Hermes-X3 API (127.0.0.1:8642, key) --> llama-swap :8080, model "flash-next"

Hermes runs, as user evo (pi-job is installed root-owned, so jobs can't edit it; one job at a time):
  pi-job code   <repo> "<task>"   new worktree ~/AI/_worktrees/<id> on a job branch, then pi -p on the X3
  pi-job review <repo> "<what>"   same, read-only tools
  pi-job render "<ask>"           Render launcher one-shot (dry run: writes the prompt, queues nothing)
  pi-job render --still <path> "<ask>"   same, with a picture Derrick dropped in chat (P4.8)
  pi-job queue <run> <code>       queue-remote.sh <run> --yes-derrick, only with the code sent to Derrick's phone (P4.11)
  pi-job status <id>
pi model for code/review: alienpc/coding_swift15_iq3s_esp if the AlienPC is free at job start, else x3-local-coding/flash-next-uncensored.
"Free at start" = the X3's own render lock is free (flock -n ~/AI/locks/gpu-render.lock). The AlienPC can't see that lock,
which an X3-queued render holds through ComfyUI's wake-up, the still upload and the gaps between clips.
Every pi-job run:  pi -p --session-dir <run dir> --model <model> --thinking low "<task>"
On the AlienPC, pi calls the fail-fast gate, which answers 503 at once while a render is running or ComfyUI is loaded.
pi stops, and pi-job resumes the same session once on the X3, from the same worktree (--continue picks the newest session for that folder):
  pi -p --session-dir <run dir> --continue --model x3-local-coding/flash-next-uncensored --thinking low "Continue from where you stopped and finish the task."
No poller and no mid-turn kill.

AlienPC, unchanged except one new gate process and one new tailnet port:
  Swift (Strata) <- llama-swap :8080 <- GPU lock gate :8085 (waits; local panes, unchanged)
                                     <- fail-fast gate :8086 (same script, --fail-if-busy, /v1 only) <- Tailscale Serve :8447 (new, X3 only)
  ComfyUI        <- llama-swap /upstream/comfyui_auto <- Tailscale Serve :8446 (existing)
```

Why render-first holds with this small addition:

- A render request waits for the Swift answer already in flight, then llama-swap swaps. llama-swap's scheduler "defers the swap until those callers finish", so a render waits at most one answer.
- Once ComfyUI (`comfyui_auto` or `comfyui_longvideo`) is loaded or the AlienPC's `gpu-render.lock` is held, the next Swift request gets 503. So a Swift request can't unload ComfyUI between a render's wake-up and its `/prompt`.
- Even if one slipped through, ComfyUI's stop command waits for the render queue (ALI-156, up to 1800 s).
- An explicit llama-swap `/unload` kills in-flight requests. pi-job treats any failed request like a 503.

## 4. Memory (X3, 120 GiB GPU limit)

| Model | Size on this box | Source |
|---|---|---|
| Halogen huihui HGN (resident: 4 slots, 524K pool, vision) | 89.7 GiB engine total, 62 GiB of it locked; about 17 GiB left for everything else | gufo phase-1 RESULT (08:35 and 08:49 addenda) |
| gufo Flash-Next UD-Q4_K_XL | Holds all ~106 GiB of weights in memory. On 0.34.0, 2 x 262K left 8 GiB free with embed-small, and 1 x 131K left 18.5 GiB. 0.35.0 reserves a full context per session, so 2 x 131K falls between those. | gufo phase-1 RESULT; gufo v0.35.0 `docs/cli.md` |
| JoyCaption | about 9.4 GiB, on demand | gufo phase-1 RESULT (U1a) |
| embed-small | 0.13 GiB | gufo phase-1 RESULT (U1a) |
| P4.10 NPU set (Halogen only) | about 2.5 GB for embeddings, reranker and the guard's reader model; about 6.5 GB with text-to-speech. Can't be swapped out. | Halogen NPU and agent-guard docs |
| qwen27b Q8 + DFlash2 | 70.2 GiB; replaces the resident model while loaded | U24 |
| ref2va-27b | disabled (19.4 GiB if re-enabled) | `2d73543` |
| PixlStash | capped at 8 GB | gufo phase-1 RESULT (09:43 addendum) |

- One main model stays resident through the pins, so the matrix router is no longer needed.
- gufo sessions: `--sessions 2 --context 131072`. Hermes needs at least 64K, and pooled sessions exist only on gufo's unreleased main branch.
- Halogen's 4 slots share one 524,288-position KV pool, so one long chat can evict the others' caches (U58). Every caller of the resident slot is therefore capped at 131,072 tokens (4 x 131,072 = the pool): Hermes, Forge, Render, pi-job and the subagents (P1.10).
- Under `WEIGHTS_LOCK`, a co-tenant that overcommits memory gets Halogen OOM-killed, and Halogen refuses to start with less than 16 GiB free ("refusing to pin", Nov 17). Load side models only after a MemAvailable check, and restart Halogen only through a full llama-swap restart, which preloads it before any side model.

## 5. Phases

**Y** = needs Derrick's yes at the time.

Phase 0 checks reuse existing fixtures; nothing new is built:

- **C1 Load:** load time, GTT used, MemAvailable.
- **C2 Parallel:** `u34/pool_test.py` at the planned session count.
- **C3 Refusals:** the U26 probes (benign_sysadmin, adult_fiction, explicit_adult) comply 3/3.
- **C4 Tools:** the U6 three-step tool chain 3/3 with tool-call IDs intact (gufo #780), plus 2 requests with `tool_choice: "none"` (gufo #1232 is open: "returns the call as text 8/8 times").
- **C5 Coding:** the Pi part of `deepu105/quant-bench` (11 Aider polyglot tasks; the community benchmark Derrick shared). Record pass count and wall time.
- **C6 Vision (required):** the bake-off vision card. Render-X3, the contact-sheet picker (P4.5) and Hermes's pictures have used the resident model's vision since Nov 17.

**Every llama-swap config change** (Phase 0 tests, P3.1, P4.10) goes through one small apply script:
1. Back up the yaml and restart llama-swap.
2. Wait up to 3 minutes for llama-swap's `/health`, the resident model `ready` in `/running` (it preloads), and verify-serve's 401/200.
3. If any check fails, restore the backup and restart.

The Nov 18 v2 cutover stayed broken for 24 minutes without this, and `/health` alone would miss a model that fails to load. A test that replaces the resident model runs only while the X3 and AlienPC panes (and Hermes, once installed) are idle and no render is queued, as on Nov 17.

### Phase 0: snapshot and test on the X3 (the baseline is restored after each test)

| ID | Step | Pass | Stop |
|---|---|---|---|
| P0.0 | The snapshot is done (`u58` `92bb886`). Ask Max which loop steps (extensions, thinking budgets, sampler) and U58 phases are in flight, so tests don't collide with a pane restart. Also ask whether a local "deferpatch" lives inside `node_modules/pi-permission-system`, as a Nov 18 review claimed; it isn't in any snapshot repo. If it does, P1.6's upgrade must re-check it. The tagger is already off. | In-flight list recorded. | — |
| P0.1 **Y** | Baseline, no restart: C2-C5 on the live Halogen v1 slot (C1 numbers come from Nov 17). | Recorded. | — |
| P0.2 **Y** | Halogen 0.20.7 with the Huihui v2 HGN (on disk, untested). Swap it into the resident slot by changing only the model folder in `cmd`, keeping the slot ID, `HALOGEN_MODEL_ID`, aliases and pins. The failed Nov 18 cutover changed all of them; adding a slot and repointing aliases is what crash-looped llama-swap. If Halogen ships a newer draft head, try it too: speculative decoding changes speed only, never the answers. | C1-C5. | — |
| P0.3 **Y** | gufo 0.35.0 (0.34.0 was tested Nov 17) with the Huihui v2 GGUF on disk (`UD-Q4_K_XL-V2`). Downloads: the 0.35.0 image and the GGUF's vision file (907 MB). Pass the vision file with `--mmproj`, because gufo only finds one named `mmproj-BF16.gguf` by itself. Same slot, `cmd` only:<br>- `--served-model-name flash-next-uncensored` (the name `useModelName` sends).<br>- `--sessions 2 --context 131072 --preserve-thinking on` (a valid 0.35.0 flag).<br>- `--reasoning-effort medium --reasoning-budget 8192`: gufo defaults to `xhigh`, and these match Halogen's defaults, so C5 compares like with like.<br>- `--cache-ram-bytes 2147483648`: the archived slot's value; the default would overcommit memory.<br>- The Nov 17 SELinux fix: `--security-opt label=disable`, models mounted `:ro` without `:Z`. Try the existing shared MTP file (`/srv/models/flash-next/mtp-...-Q8_0.gguf`) with `--speculative mtp`: drafts are checked, so a mismatch costs only speed. If it won't load, use `--speculative off`. The slot keeps `concurrencyLimit: 4`; gufo queues beyond 2 sessions, as in the Nov 17 4-caller test. | C1-C5 pass. | Load fails, or C3 or C4 fail. Try NeosQ only if both v2 files fail. |
| P0.4 **Y** | Memory: load the leading candidate plus embed-small, then read MemAvailable. Load JoyCaption (one request) only if MemAvailable is at least 13.5 GiB: JoyCaption's 9.4 GiB plus the 4 GiB margin the Nov 17 test used, which is also the NPU engine's own floor. If Halogen leads and P4.10's NPU set is planned, add its 2.5 GB (6.5 GB with TTS) to that threshold. Under `WEIGHTS_LOCK`, an overcommit kills Halogen rather than failing softly. | MemAvailable stays at least 4 GiB (the Nov 17 test passed at 5.8 GiB); no OOM; no Halogen restart. | Below the threshold before JoyCaption: don't load it; P4.6 tags with the main model's vision. |
| G0 | Pick what the resident slot runs. Candidates: Halogen v1 (baseline), Halogen v2 and gufo. Among candidates passing C1-C4 and C6, take the most C5 tasks passed; on a tie, gufo (Derrick's preference); then speed. | — | Nothing beats the baseline: keep Halogen v1. |

After each candidate test, restore the baseline `cmd` with the apply script; only P3.1 makes a winner permanent. Check free disk first (565 GB on Nov 17, before two ~111 GB downloads finished). Delete a losing candidate's files only after G0, with a yes, and keep at least 100 GiB free.

**Watch:** gufo PR #1036 (per-request residual projection). Once it ships, test the gufo-proven `ethanwtodd` Swift file with a refusal projection. That is the same method Strata uses for Swift on the AlienPC.

### Phase 1: stop the loops (Nov 16 audit; coordinate with P0.0)

| ID | Step | Pass |
|---|---|---|
| P1.1 | B4 is done: the X3's live trees are on Gitea (U58 finding 6) and mirrored to GitHub at matching commits. Remaining: Thursday's fold of the branches (`u58`, `alienpc-community`, `alienpc-render` and the older `x3-*` branches) into one repo, keeping `/home/evo` paths and the `agent-shared/extensions` folder. Give `evo` its own Gitea token (I12). | A fresh clone starts Forge with all skills, and the live config matches the repo. |
| P1.2 | B3: one lock method for the X3's `gpu-render.lock`. `ralph.sh` and `queue-remote.sh` already use `flock -n` (U58). Check that `run_queue.py --remote` does too, and remove any 0-byte PID-style lock file left behind, which Ralph reads as "GPU busy". | A 2-item Ralph loop runs with no 1-hour waits, and a dry-run queue doesn't block it afterwards. |
| P1.3 | I2: before each Ralph loop, clear stale `fix_plan.md` items. Each pass runs a skill-load smoke test and a file-count cap from `git diff --stat`, and may not edit skills or AGENTS.md. One worktree per loop. | A planted stale item and a planted 30-file rewrite are both refused. |
| P1.4 | I3: mark the 6 known failing tests xfail with reasons. | The suite is green, and a new failure fails it. |
| P1.5 | I8: short Always / Ask / Never AGENTS.md files. Replace the `.bak` rule in `community/agent-shared/AGENTS.md` (line 16) with "commit to git; etckeeper for /etc". | No contradictions left between the files. |
| P1.6 **Y** | I9: subagents use `flash-next-uncensored-sub`, which already exists in llama-swap and models.json (131K context, low reasoning effort). Upgrade pi-subagents to 0.88.1 or later with explicit context inheritance. If P0.0 confirms the deferpatch, check it is still there after the upgrade. | A subagent loads no model. |
| P1.7 **Y** | B1: agy runs as `evo`, in a per-job worktree, with a time limit. | A test agy job cannot sudo and stops at its limit. |
| P1.8 **Y** | B2 (OD2): Forge-X3 asks before vault reads, Gitea writes and outbound sends, using the installed pi-permission-system extension. pi itself never asks per tool call, and its `--approve` flag only trusts project settings (pi docs). Headless runs deny those tools. | A planted "read the vault" prompt asks first in Forge-X3 and is denied in Ralph. |
| P1.9 | Loop limits: load `loop-guard.ts` (stops a third identical tool call) in every pane; Forge doesn't have it yet (U58). Check that Render's `auto-continue.ts` never re-prompts an unchanged context. Run every headless job (Ralph, pi-job) under `timeout` (for example `ralph.sh`'s 3,600 s pass limit), because pi has no turn or time limit of its own. Pass `--thinking` explicitly, because a new pi session otherwise starts at medium (pi docs): use `low` or higher, never `off`, which broke tool calls on this model (`32a46c0`). On timeout, write a `STUCK` status note. | A planted impossible task ends `STUCK` at its limit. |
| P1.10 | U58, owned by the Forge plan (rev 2): one session folder (`sessionDir`), one launcher per pane, working compaction, then one pane restart with checks inside the pane. This plan adds one requirement for U58's values, from the shared 524,288-position KV pool. Set every X3 models.json entry for the resident slot (`x3-local/*`, `x3-local-coding/*`, the `-sub` names) to `contextWindow: 131072`. Use compaction `keepRecentTokens: 20000` and a `reserveTokens` at least the entry's `maxTokens` (32,768 for the main entries, 16,384 for the `-sub` entries), so prompt plus reply stays under 131,072. Main chats then compact at about 98K, and four callers fit the pool. U58's 32,768 reserve on a 262K window would let a chat reach 229K, close to the 236K that filled the pool. This caps Forge chats at 131K. Phase 4 starts after U58's restart check passes. | U58's GATE passes: Forge compacts once past about 98K and keeps going, and `/resume` shows the full history. |

### Phase 2: names and hygiene

| ID | Step | Pass |
|---|---|---|
| P2.1 **Y** | Labels. On the X3, `herdr-panes.sh` creates each workspace with `--label "$name"`: add a label map (render → Render-X3, forge → Forge-X3, and sydney → Sydney-X3 if that chat comes back; it no longer starts on the X3) and relabel the existing workspaces. Do the same on the AlienPC in `C:\AI\director\scripts\pi_herdr_at_logon.ps1` (Forge-AlienPC, Render-AlienPC, Sydney-AlienPC). Each launcher passes one identity line ("You are Forge-X3 on evo-x3") through pi's append-system-prompt option. Don't put it in `community/agent-shared/AGENTS.md`, which both machines load. Folder names, launcher files and pi state folders stay the same. | herdr and pi-mobile show the new labels, and each chat names its host when asked. |
| P2.2 **Y** | Clean up. Write a manifest first (repo, revision and sha256 for each file), then delete only after a yes: `/srv/bakeoff` (341 GiB), unused `~/rocm` (9.9 GiB), the aborted U34 backup (5.2 GiB) and the old Q4 27B file (17 GiB). After P6 passes, also delete Flash-Next files that neither llama-swap.yaml nor its rollback file use. Copy to QNAP only what can't be downloaded again: results, logs, custom conversions. | About 370 GiB freed now; manifest in Gitea. |
| P2.3 | Layout. pi-job and Ralph logs go to `~/AI/_runs/` (gitignored). Render runs stay in `community/runs/`; fix U23 gap 11 so a relative run path can't write outside it. Agent checkouts go in `~/AI/_worktrees/` (where `ralph.sh` already puts them) and are removed once their branch merges. Delete existing `_archive/*.bak-*` files after the next verified QNAP backup. On the AlienPC, run `git config --system core.longpaths true` (Git for Windows' fix for "Filename too long"). Once P4.6 fixes the tagger, run it from a nightly systemd timer. | No new `.bak` files for a week, and the evo-x3 snapshot clones on the AlienPC. |
| P2.4 **Y** (Derrick, admin console) | Tailscale ACL, only for the ports that have no login of their own. U8 found no ACL on Nov 15 (allow-all); the Oct 30 NT-1 rule may have changed that, so download the current policy first.<br>Don't rewrite the tailnet into an allow-list. That risks cutting flows this plan doesn't list: Max's SSH, Gitea, Kuma and backups to the QNAP, household devices, and the AlienPC panes' calls to the X3's `:443`.<br>Instead, keep today's access and cut out one port block, `8443-8447`, on the X3, the AlienPC and the QNAP. That covers Open WebUI plus `/renders`, pi-mobile, the AlienPC's PixlStash, ComfyUI and Swift, and the QNAP's ntfy:<br>1. Those three hosts get port ranges that skip the block (`1-8442,8448-65535`).<br>2. Every other device keeps `:*`, listed by name or tag, because a rule can't subtract.<br>3. Narrow rules for the block: Derrick's devices get it on all three hosts; the X3 also gets AlienPC `:8446-8447`; the X3 and the AlienPC get QNAP `:8447` (ntfy).<br>4. Put the allow and deny cases in the policy's `tests` section, so a wrong edit can't be saved.<br>If anyone else uses Open WebUI, give `/renders` its own port instead. Required before P4.9 and P5.1. | Each deny test is refused; Derrick's phone still reaches `:8443`; Max's SSH and the AlienPC panes still reach the X3. |

### Phase 3: X3 model cutover (after G0)

| ID | Step | Pass |
|---|---|---|
| P3.1 **Y** | llama-swap.yaml: the resident slot runs the G0 winner. Keep its ID (`flash-next-uncensored`), its `-sub` settings, `useModelName`, the preload hook and the `halogen-only` pins. Every caller (`flash-next`, `gemma4-heretic`, Hermes, the AlienPC panes) then follows with no edits, so change only the slot's `cmd`. Save the old `cmd` as a rollback file, as U34 did, and apply it with the health-check restart (Phase 0). gufo uses P0.3's flags (including `--served-model-name flash-next-uncensored`, without which every pinned caller fails) plus `--stall-timeout-ms 120000`: per gufo's docs, a hang then exits like a crash and llama-swap restarts it. Commit with etckeeper. P1.10's 131,072 window already fits gufo's 2 x 131K sessions. | verify-serve gives 401 without a key and 200 with one; C2 and C3 pass; a `gemma4-heretic` request is answered with no model load; Forge-X3, Render-X3 and the AlienPC panes still answer. |

### Phase 4: Hermes-X3

| ID | Step | Pass |
|---|---|---|
| P4.1 **Y** | Install Hermes Agent as `evo` with the official installer, and record its version or commit; update it only with a yes, because P4.8 relies on behavior that is in Hermes's code but not its docs. Run `hermes gateway install` (systemd user service) and `loginctl enable-linger evo` (a sudo step; Max runs it after a yes). Provider: llama-swap as an OpenAI-compatible endpoint at `http://127.0.0.1:8080/v1`, model `flash-next`, key `LLM_KEY_HERMES` (already in llama-swap's key list). Pin `context_length` to 131072 (P1.10), because Hermes misreads llama.cpp context sizes (issue #155853) and the KV pool is shared. Vision: `flash-next` (vision is on in the resident slot and read a picture correctly on Nov 17); if the G0 winner has no vision, set `auxiliary.vision` to `joycaption` (on demand, no main-model swap). If replies come back empty, raise the reply token limit or set reasoning effort low. Don't turn thinking off: on this model that broke tool calls (`32a46c0`). | Hermes answers and survives a reboot. |
| P4.2 **Y** | API server: `API_SERVER_ENABLED=true`, an `API_SERVER_KEY`, bound to `127.0.0.1:8642`. In Open WebUI (Admin > Settings > Connections), add `http://127.0.0.1:8642/v1` with that key. Open WebUI uses host networking, so loopback works; its environment settings only apply on first launch, so add it in the UI. Name the model `Hermes-X3` and keep Open WebUI's own web search off for it. | The phone reaches Hermes-X3 on :8443, and port 8642 is not reachable from the tailnet. |
| P4.3 | `pi-job`, one short script plus one Hermes skill explaining when and how to call it. The source lives in the evo-x3 repo; it's installed root-owned at `/usr/local/bin/pi-job` (mode 0755), so a job can't edit its own checks.<br>- **Roles:** `code`, `review`, `render` (dry run) and `queue <run> <code>`. `queue` runs `queue-remote.sh <run> --yes-derrick` only with the run's ntfy code from P4.11 (OD10), and stays off until P4.11 passes.<br>- **One job at a time:** a second request is refused with the running job's ID.<br>- **Running:** it detaches at once through `systemd-run --user`, as `queue-remote.sh` does, so a Hermes restart doesn't kill the job. That unit starts with a clean environment, so pi-job sets `HOME` and `PATH` (including `~/.local/bin`) itself; the launchers load their own keys, such as Render's `PIXL_KEY`. It prints a job ID and writes `~/AI/_runs/<id>/status` and `log`; `pi-job status <id>` reads them. Arguments go to commands as separate arguments, never through `bash -c`. `code` reports `DONE` only if the job branch has a new commit; otherwise `STUCK`. That way a refusal or a held tool call can't pass as finished. Hermes's own background tool can't push results into Open WebUI (Hermes docs: API-server completions are "never autonomous new model turns"), so the status file is the check, plus one ntfy line when a job ends (P4.11). | Hermes starts a job and reports its status when asked; a job with no commit ends `STUCK`. |
| P4.4 | Safety. Hermes's API-server toolsets: terminal, files, memory and skills; no web or browser (OD3). Hermes runs as `evo`, which has no sudo. Keys: `evo` already has its own key file, `~/.config/evo-x3/llm.env` (U35: 0600, only `LLM_KEY_PI`; `evo` can't read `/etc/evo-x3`). Add `LLM_KEY_HERMES` there for Hermes. Check that `evo` still can't read `/etc/evo-x3/llm.env`: U35 verified it on Nov 16, but the Nov 17 `models.json.example` names the root file. Set `agent.max_turns`, which is unlimited by default (for example 40; long work goes to pi-job). Keep `unattended_mode: deny` and set a short `approvals.timeout` (for example 30 s), because Open WebUI's streaming requests still wait for approval on flagged commands. `command_allowlist` only pre-approves flagged commands and is not a fence. Keep Hermes's `memories/` and `skills/` folders, and nothing else, in a local git repo with a nightly commit, so anything Hermes writes into its own instructions shows up in a diff. Ignore `.env*`, `*.token`, `cache/` and `sessions/` (keys, dropped pictures and chats), and never push the repo anywhere. | A flagged command is refused quickly; a runaway turn stops at `max_turns`; `evo` can't read `/etc/evo-x3/llm.env`; all panes still answer. |
| P4.10 **Y** | Search, voice and guard (OD9). Settings go in Open WebUI's admin UI (Documents and Audio pages), because its environment settings apply only at first launch. Each setting gets Open WebUI's existing llama-swap key in its API-key field, because llama-swap's keys cover every route.<br><br>**If G0 picks Halogen**, the NPU runs inside the resident `flash-next-uncensored` slot (Halogen's NPU doc):<br>1. **Host:** the newest EVO-X3 BIOS. Afterwards, check the UMA setting is still the minimum (`mem_info_vram_total` 1 GiB, GTT 120 GiB), because a BIOS update can reset it. Leave IOMMU on (never `amd_iommu=off`), and hold the fabric clock with Halogen's host unit `deploy/host/halogen-fabric-clock.service`. Don't use the `/sys:/host/sys` mount, which would give the container write access to host sysfs.<br>2. **Weights:** the slot's model folder is mounted read-only, so Halogen can't fetch NPU files itself. After a yes, download `peonist-ai/halogen-npu-qwen3-embedding-0.6b`, `-qwen3-reranker-0.6b` and the guard's reader `peonist-ai/halogen-spotter-0.6b` (the guard otherwise fetches it itself, which the read-only mount blocks). Add `-qwen3-tts-0.6b-customvoice` if wanted. Put each in `/srv/models/halogen-npu/<model name>` and record each file's sha256. Create an empty `npu` folder inside both the v1 and v2 model folders (a mount point in a read-only mount must already exist, and switching models then never fails), then mount `-v /srv/models/halogen-npu:/models/npu:ro`.<br>3. **Slot:** add `--device /dev/accel/accel0`, that mount, `HALOGEN_NPU_MODELS=qwen3-embedding-0.6b,qwen3-reranker-0.6b` (plus TTS if wanted) and `HALOGEN_AGENT_GUARD=watch`. Leave `embed-small` configured (0.13 GiB) as the fallback.<br>4. **Routing:** pin the NPU names to `flash-next-uncensored` in the `halogen-only` profile, like the other names; don't add a second alias list, which is what crash-looped llama-swap on Nov 18. Remove `useModelName` from the slot, because it would rename NPU requests to the LLM. Halogen sends any name it doesn't know to Flash-Next, so `flash-next`, `gemma4-heretic` and the `-sub` names should still work; test each.<br>5. **Open WebUI:**<br>- Embeddings: engine OpenAI at `http://127.0.0.1:8080/v1`, model `qwen3-embedding-0.6b`, query prefix `Instruct: Given a question, retrieve passages that answer it` + newline + `Query:`. Re-index existing documents after the switch.<br>- Reranker: hybrid search on, external reranker `http://127.0.0.1:8080/v1/rerank`, model `qwen3-reranker-0.6b`.<br>- Speech to text: Open WebUI's built-in Whisper. Halogen's ASR takes WAV only, and phones record webm.<br>- Optional text to speech: engine OpenAI, model `qwen3-tts-0.6b-customvoice`, one of the nine preset voices. Halogen refuses mp3, so if the read-aloud test fails, set `AUDIO_TTS_OPENAI_PARAMS` to `{"response_format":"wav"}`.<br>6. **Guard:** `watch` only. `hold` applies to the whole container, and a held call becomes a plain reply, so headless pi jobs would look finished. Read its counters at Halogen's own `http://127.0.0.1:8081/metrics`, not through llama-swap.<br><br>**If G0 picks gufo:** no NPU, because Halogen's NPU models need its Flash-Next loaded and only one Flash-Next fits in memory. Instead: use `embed-small` (check it answers; it was reported down on Nov 18) with the `search_query: ` and `search_document: ` prefixes its card requires; use the built-in Whisper; no reranker, guard or TTS. | **Halogen path:**<br>- The startup log names each NPU model and the guard.<br>- A 30-minute test with `pool_test.py` and an embedding loop running together causes no hang and no `amdxdna` errors other than the documented `-28` retries.<br>- An embedding request through llama-swap returns a 1,024-number vector, which proves it reached the NPU.<br>- `flash-next`, `gemma4-heretic` and `-sub` still answer.<br>- A PDF in Open WebUI answers a question from its contents.<br>- A reply is read aloud (if TTS is on).<br>- The guard's counters show at `:8081/metrics`.<br><br>On any hang, remove the NPU settings and device, restore `useModelName`, and use the gufo path's settings.<br><br>**Gufo path:** the PDF question works. |
| P4.11 **Y** | ntfy approval codes and job pings (OD10). Reuse the private `ntfy-renders` server on the QNAP (v2.35.0, deny-all, tailnet-only `:8447`, topic `renders-a7gma8xg`), which Derrick's Pixel already reads as `pixel-sub`. Max runs these steps over `ssh qnap` after a yes, the same way as the Oct 30 build:<br>1. Add a user `x3-pub` with `write-only` access to that topic and nothing else, and create a token for it. Store the token in an `evo`-owned 0600 file, `~/.config/evo-x3/ntfy-x3.token`, never printed. `/etc/evo-x3/ntfy.env` (root-only, another client) stays untouched.<br>2. P2.4's ACL lets the X3 reach the QNAP's `:8447`. The Oct 30 rule allowed only the AlienPC and the Pixel.<br>3. `pi-job render` makes a 6-digit code per run and sends it with high priority: "Run `<id>`, prompt `<first 8 characters of prompt.txt's sha256>`: code `<code>`, 15 min". No prompt text goes to the lock screen, and the chat shows the same 8 characters above the prompt. pi-job keeps only a salted hash of the code, the prompt's hash, an expiry 15 minutes out and a 3-try counter in the run folder. `pi-job queue <run> <code>` checks all four, refuses if `prompt.txt` changed after the code was sent, and the code then dies. Job-end pings use the same token.<br>`x3-pub` is write-only, so `evo` (and Hermes) can send but never read the topic; the code is only readable on the phone. | A render push with its code and prompt hash arrives on the Pixel. A wrong or expired code is refused, and so is a right code after `prompt.txt` changes; the right one queues once and not again. Reading the topic with the X3 token gets 403. |

### Phase 4b: PixlStash (finding stills, tagging, one media home)

PixlStash already runs on the X3 with the 32,964-picture library (moved there per the Nov 16 location plan, option B). These steps use its official features, following the top-ranked option in the Nov 16 PixlStash study.

| ID | Step | Pass |
|---|---|---|
| P4.5 **Y** | Finding stills. Already done on both machines: Render queries the PixlStash API with a read-only key (semantic search, or a character's pictures newest first) and reads the top result (`5465fde`; the X3's `OPERATOR.md`). Remaining: rank instead of taking the first hit, using PixlStash's own scores: semantic search (`/api/v1/pictures/search?query=`, CLIP plus SBERT on descriptions) inside the character, then smart score (which penalises defects such as bad hands) and face likeness of at least 0.55, the threshold the tagger already uses. It returns the top 6. Picking (OD8, decided): a small helper builds one labelled 2 x 3 contact sheet of the 6, and the resident vision model picks from it in one vision call, then reads only the winner in full to write `still_read.json`. Update the RUN_ME / AGENTS rule from "never browse library pictures" to "never browse library pictures, except this candidate sheet". Character-name lookup: add the one-line `WHERE p.file_path = ?` filter to the builder's local, read-only `vault.db` query (`resolve.py`), so it stops scanning 116,876 faces; no new API client. Check that PixlStash's 8 GB memory cap holds under these searches. | Five sample asks each produce a sheet and a sensible pick, and the chosen still reaches the run folder. |
| P4.6 | Tagging. The tagger has been disabled since Nov 17 (crash loop: missing `submit_parody_run`); fix that first. Choose the tagging model against Derrick's ~20 hand-tagged pictures: the main model's vision (resident, nothing to load) or JoyCaption (on demand, 9.4 GiB, only when P0.4's memory check allows). Better descriptions also improve semantic search. Lock one "render-ready" set per character using PixlStash's sets and tag review queue. Within those sets only (hundreds of pictures, not all 32,964), add structured tags: `ar:` and `people:` computed from image size and PixlStash's face count (no model needed), and `shot:`, `pose:`, `facing:` from the chosen model. Optionally pre-fill the `still_read.json` fields there too. | Tagger fixed and model chosen; render-ready sets locked and tagged; searches can filter on `shot:` and `pose:`. |
| P4.7 **Y** (OD7, decided) | One home for finished images and videos: the X3 PixlStash library. Finished renders land in one X3 folder, `/srv/renders` (owned by `evo`, mode 0755, symlinked from `~/AI/media/renders`). It lives outside `/home/evo` (mode 0700, with SELinux home labels) so the root `tailscaled` can serve it (P4.9). PixlStash's folder watch imports it. X3-queued renders already download their outputs to the X3, so they are copied into it. Every file gets a unique name, `<run_id>.mp4` (each run's clip is called `clip.mp4`). Every copy goes to a hidden temporary name in the same folder and is renamed only when complete, so the folder watch never imports a half-written file. AlienPC renders already land on the QNAP `renders` share as `runs/<run_id>/clip/clip.mp4` (`98fbc30`), where Derrick looks today; a timer on the X3 copies new clips from that share into the folder. The copy method (a read-only mount using the X3's existing QNAP credentials, or rsync over SSH) is chosen at build time. QNAP keeps the backup, and the database stays on the X3's local disk (the study's rule: never open `vault.db` over a network share). | A render from each machine shows up in PixlStash, searchable, within a few minutes. |
| P4.8 | Picture dropped in chat. Derrick drops a picture into Open WebUI with his ask ("10 s video from this"). Hermes's API server saves base64 PNG, JPEG, GIF or WebP images (up to 10 per message) under `~/.hermes/cache/documents/native-inputs/` and adds `[Image attached at: <path>]` to the message. This is in Hermes's code (`gateway/session_api_media.py`) but not its docs. The skill passes that path to `pi-job render --still <path> "<ask>"`. pi-job refuses any path whose real path is outside `~/.hermes/cache/documents/native-inputs/`, then copies the picture into the run folder and the PixlStash intake folder, so it also lands in the library (OD7). Render skips the search and reads the given still; RUN_ME already allows "any still path Derrick names". Fallback if a Hermes update drops the hint: upload the picture to PixlStash and ask for "my latest upload". | A dropped picture produces a `READY` prompt from that exact still and shows up in PixlStash. |
| P4.9 **Y** | Viewing results in chat, after P2.4. Share the renders folder read-only on Open WebUI's existing port: `sudo tailscale serve --bg --https=8443 --set-path=/renders /srv/renders` (serving a folder needs root). It reuses `:8443`'s certificate and ACL, so the X3 gets no new port (D11). The share has no login, so `:8443`'s ACL must cover only Derrick's devices. When a job finishes, Hermes replies with the file's address: Open WebUI shows pictures inline, and a video opens in the phone's player. | `https://evo-x3-1.tailf242b2.ts.net:8443/renders/` lists files and Open WebUI still loads at `/`. A finished render's picture shows inline and its video plays. A device outside the ACL is refused. |

### Phase 5: AlienPC Swift lane

| ID | Step | Pass |
|---|---|---|
| P5.1 **Y** | On the AlienPC, after P2.4:<br>1. Add a `--fail-if-busy` option to `gpu_lock_gate.py`, about 20 lines. In that mode the gate forwards only `/v1/*` (404 for anything else, so callers can't reach `/unload` or ComfyUI). On a chat or completion request it answers 503 at once, instead of waiting up to 1800 s, in two cases: `gpu-render.lock` has a live PID, or llama-swap's local `/running` (checked with the request's own key) lists any `comfyui*` model or any model that is stopping, which is how a swap in progress shows. That covers `comfyui_auto`, `comfyui_longvideo`, and a render that has just asked for ComfyUI. Known cost, accepted: ComfyUI stays loaded for its idle timer after a render (300 s for `comfyui_auto`, 600 s for `comfyui_longvideo`), and jobs started in that window run on the X3.<br>2. Start a second gate instance at logon: `--port 8086 --fail-if-busy`. The existing `:8085` instance keeps waiting for local panes, unchanged.<br>3. Publish root to root: `tailscale serve --bg --https=8447 http://127.0.0.1:8086`. `/v1/...` then maps 1:1, with no path doubling, and the rollback is `tailscale serve --https=8447 off`. If the AlienPC's llama-swap uses API keys, give the X3 its own (Derrick types it). | From the X3, `/v1/models` on `:8447` works and `/unload` doesn't. A chat request gets 503 within a second while ComfyUI is loaded. A device outside the ACL is refused. |
| P5.2 | On the X3, add an `alienpc` provider to evo's `~/.pi/agent/models.json`: `api` openai-completions, `baseUrl` `https://alienpc.tailf242b2.ts.net:8447/v1`, a key read from a 0600 file, and the `coding_swift15_iq3s_esp` entry copied from the AlienPC's live models.json with its own `contextWindow`. An old snapshot says 92,160 and Strata's config allows 131,072, so copy the live value rather than guessing. Keep `samplingParams.experimental_speed_projection: true`: the Oct 25 audit found that sending `false` turns Swift's refusals back on. | `pi -p --model alienpc/coding_swift15_iq3s_esp` answers and passes C3. |
| P5.3 | pi-job uses the AlienPC when the X3's render lock is free at job start (section 3). Every run uses `pi -p --session-dir <run dir> --thinking low`. If pi stops on a 503 or any failed request, pi-job resumes once on the X3 from the same worktree. If the session already holds at least one model reply, it uses `--continue --model x3-local-coding/flash-next-uncensored` and a "Continue from where you stopped and finish the task." prompt (pi's `--continue` picks the newest session for that folder). If the very first request failed, there's nothing to continue, so it starts fresh on the X3 with the original task. A session only moves from the AlienPC to the X3, never back, so the X3's 131K window can't be too small. Test how pi exits on a 503 (exit code or last session entry) and key the resume on that. Also test that pi retries a 429 from the X3's busy slots rather than failing. | AC-OP step 4 passes: a render started mid-job isn't interrupted, and the job finishes on the X3 in the same session. |
| P5.4 **Y** | AlienPC pane models (OD5, decided). U34 pre-staged a change (alienpc-director `b5d964a`): at the next AlienPC logon, Forge-AlienPC moves to the X3's `flash-next`, and Render-AlienPC and Sydney-AlienPC move to the X3's Gemma. Decided by Derrick on 2026-11-18: revert only the Forge line, so Forge-AlienPC keeps local Swift (D8). Render and Sydney stay on the X3's `gemma4-heretic`, which the pins have served from the resident uncensored model since Nov 17, so the AlienPC GPU stays free for ComfyUI and Swift. Do this before the next AlienPC logon. | After a logon, Forge-AlienPC runs local Swift. |

### Phase 6: acceptance

| ID | Step | Pass |
|---|---|---|
| P6.1 | AC-OP end to end from a phone. | All four results as described in section 1. |
| P6.2 | A deliberately impossible task on each lane (AlienPC Swift and X3 Flash-Next). | Both end `STUCK` at their limit with a status note. |
| P6.3 | Rollback drill: restore the previous llama-swap.yaml, then the new one again. | 5 minutes or less each way. |

### Phase 7: eGPU (notes only)

- **Separate backend.** The eGPU gets its own engine instance behind llama-swap, with its own model names: llama.cpp, or the `llama-halo-hybrid` fork, which marks the R9700 as production. First candidate: `gemma4-heretic` (and ref2va-27b), so render prompts can use Gemma again without touching the resident model.
- **Pin engines to the iGPU.** gufo crashed with a second GPU present (gufo #696), so pin it to the iGPU (`HIP_VISIBLE_DEVICES` / `ROCR_VISIBLE_DEVICES`). Halogen hides extra GPUs itself (Halogen #188: an EVO-X3 with a 7900 XT over OCuLink).
- **Card notes.** If an R9700 drops off the bus at idle, turn ASPM L1 off. No reports found for the Arc Pro B70.

### Later (after P6 passes, or sooner if Derrick asks)

Small improvements, not fixes; each stays inside an existing script. Pick any one at a time.

| ID | Improvement | Size |
|---|---|---|
| L1 | ntfy **Copy** button on the approval push. ntfy's documented `copy` action ("useful for one-time passcodes") puts `queue <run_id> <code>` on the clipboard to paste into Hermes. Check that the QNAP's v2.35.0 shows it; without it the push still works. | One header in P4.11 |
| L2 | **Poster image:** one ffmpeg frame grab per clip into `/srv/renders/<run_id>.jpg`, so Hermes's reply shows a picture above the video link instead of a blank player. | A few lines in P4.7 |
| L3 | **Abandoned worktrees:** nightly, for worktrees in `~/AI/_worktrees` older than 7 days, save `git status` and `git diff` to the job's `_runs` folder, then `git worktree remove` and `prune`. P2.3 only cleans up merged branches today. | A few lines in the P2.3 timer |
| L4 | **Contact sheet in chat:** copy P4.5's 2 x 3 sheet to `/srv/renders/sheets/`, show it in the dry-run reply, and add `pi-job render --pick N` so Derrick can choose another panel before rendering. | Small |
| L5 | **`pi-job status` overview** with no job ID: the resident model and MemAvailable, whether the AlienPC is rendering, and the last 3 jobs with their result links. For one-tap use from the phone, save "status" as an Open WebUI prompt; no Open WebUI Action button, which would need a new host endpoint and could bypass Hermes. | Small |
| L6 | **STUCK bundle:** when a job ends `STUCK`, pi-job writes `~/AI/_runs/<id>/escalate.md` with the task, `git status` and diff, and the last 3 tool errors from the session, ready to paste into GrokBot (D3). | A few lines in P4.3 |
| L7 | **Syntax check after edits:** a small pi extension runs `python3 -m py_compile`, `bash -n` or `jq empty` on the edited file and adds the error to the tool result only when something is broken, so the model fixes it on the next call instead of looping. Test first that pi's extension API can add to a tool result. Look at pi's own "text not found" message before adding a whitespace hint. | About 40 lines in `agent-shared/extensions` |
| L8 | **Fast prompt edit:** `pi-job recompile <run_id>` reruns only the writer pipeline's linter and graph filler after Derrick changes a line of `prompt.txt`. It must pass the same READY / NOT_READY gate, and it sends a new code tied to the new prompt hash (P4.11). | Small |

### For the render repo (handoff, not plan steps)

Render-graph changes belong in the render repo's own fix list (section 2). These came from a Nov 18 review. Treat them as same-seed tests, because its benchmark numbers have no source and it got the `comfyui_auto` timer wrong (it's 300 s, not 900).
- **NVIDIA sysmem fallback:** set "CUDA - Sysmem Fallback Policy" to "Prefer No Sysmem Fallback" for ComfyUI's `python.exe`, then compare step 1's time before and after.
- **VSA check:** read the ComfyUI log of one `beta7_int8HQ` run for the "no `to_gate_compress` layers" line. Only if it appears, try `sol-attn` on the same seed.
- **`--fast fp16_accumulation`:** a small numeric change. Compare frames on the same seed before keeping it. The current `comfyui_auto` command has no `--use-ck-attention`; check whether that was intended.
- **Face-box crop:** if PixlStash's face table stores boxes, crop the chosen still to 9:16 or 16:9 around the face instead of center-cropping.
- **Set-to-RefMod compiler:** rebuild a character's RefMod from its locked "render-ready" PixlStash set (P4.6). RefMods are already used today.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Uncensored model with tools: injected text in repo files, RAG documents or dropped pictures meets no refusal. | Hermes has no web or browser tools; `evo` has no sudo and only its own two keys (P4.4); the guard watches (P4.10); `DONE` needs a commit (P4.3); queueing a render needs the code sent to Derrick's phone (P4.11). Forge asks before vault reads, Gitea writes and outbound sends; headless runs deny them. |
| Open gufo bugs: #1232 (`tool_choice: "none"`), #1198 (load refused after a cold boot), crashes on long runs. | C4 tests #1232. For #1198, use gufo's documented workaround (`--cache-ram-bytes off`, or boot with `kho=off`). llama-swap restarts gufo on the next request. |
| The uncensored files are community requants, not official. | C1-C5 on this box. The Halogen huihui slot is the proven fallback. |
| The huihui abliteration may cost quality: one source, the dymoo fork README, scored it 56% against 90% for the base model. | C5 compares all candidates on the same tasks. |
| Swift's licence: free up to US$1M revenue. | Personal use. |
| Every `flash-next` reload costs about 25 s. | One main model; batch jobs at night; the eGPU later. |
| A llama-swap config error takes every X3 model down (Nov 18: 24 minutes of crash loops). | The health-check restart restores the backup within a minute (Phase 0). |
| Halogen's 4 slots share one KV pool: one long chat evicts the others' caches (U58: Forge at 236K, pool at 98%). | Every caller capped at 131,072, with main chats compacting near 98K (P1.10). |
| Under `WEIGHTS_LOCK`, a co-tenant that overcommits memory gets Halogen OOM-killed, and Halogen refuses to start with less than 16 GiB free. | JoyCaption loads only after the P0.4 memory check; the NPU set is trimmed to about 2.5 GB; ref2va stays off; qwen27b stays manual. Halogen restarts go through a full llama-swap restart, which preloads it before side models. |
| More callers share the resident model's 4 slots: the panes and their subagents, Hermes, pi-job, the AlienPC panes and the nightly tagger. llama-swap answers 429 above `concurrencyLimit`; the Nov 17 tests counted 429s. | pi-job runs one job at a time and the tagger runs at night. P5.3 checks that pi retries a 429 instead of failing. |
| The tailnet has no ACL yet (U8), and the new shares have no login. | P2.4 before P4.9 and P5.1. |
| The new AlienPC LLM port. | Tailnet-only, ACL from P2.4, `/v1` only, plus a key if llama-swap uses keys. |
| Hermes approvals can stall Open WebUI for up to `approvals.timeout`. | A short timeout; Hermes's work goes through pi-job, which needs no approval. |
| NPU and GPU at once can hard-hang Strix Halo, even with the fabric clock held (ROCm/TheRock#8709). | Newest BIOS, the clock hold, and P4.10's 30-minute test; any hang turns the NPU off. |
| NPU models live in the resident container: while it is unloaded (a qwen27b request or a Phase 0 test), search and voice are off. NPU memory can't be swapped out (about 2.5 GB for P4.10's set, 6.5 GB with TTS). | The pins keep it resident. P0.4 counts the NPU memory when Halogen is the candidate. |

## 7. Open decisions

| ID | Decision | Default |
|---|---|---|
| OD1 | Try uncensored Swift on the X3 (119 GB download, no refusal or quality data)? | **Dropped in v3.2.** The AlienPC Swift lane covers coding. |
| OD2 | Forge-X3: one pane with approval prompts, or separate web and ops panes? | One pane. |
| OD3 | Hermes web search. Hermes has a native SearXNG plugin and the X3 already runs SearXNG. If it is turned on, use a second profile that cannot run pi-job. | Off. |
| OD4 | eGPU model and first workload. | When bought. |
| OD5 | AlienPC panes after U34's pre-staged change (P5.4). | **Decided (Derrick, 2026-11-18):** Forge-AlienPC back to local Swift; Render and Sydney stay on the X3's `gemma4-heretic` (served by the resident uncensored model through the pins since Nov 17). |
| OD6 | Hermes channel. The Hermes community mostly uses Telegram or Discord gateways, which also push job results. | Open WebUI (decided); a gateway is optional later. |
| OD7 | Home for finished images and videos (P4.7). | **Decided (Derrick, 2026-11-18):** the X3 PixlStash library, with QNAP as backup and as the AlienPC drop point. |
| OD8 | Picking stills (P4.5). | **Decided (Derrick, 2026-11-18):** the resident vision model picks from a 2 x 3 contact sheet of the top 6; the no-view rule is relaxed for candidate sheets only. |
| OD9 | NPU uses and the engine choice (P4.10). | **Decided (Derrick, 2026-11-18), trimmed after the audit:** G0 keeps the gufo tie-break. If Halogen wins: embeddings and reranker, optional text to speech, and the guard in `watch` only. Speech to text stays on Open WebUI's Whisper (Halogen takes WAV only), and `d3-nano` is dropped. If gufo wins, use the plain fallbacks. |
| OD10 | Approving `pi-job queue`. Hermes can read anything pi-job writes, so a code shown in chat can't prove Derrick said yes. | **Decided (Derrick, 2026-11-18): an ntfy code (P4.11).** The code is sent only to Derrick's phone, and `queue` needs it. Limit: Hermes runs as `evo`, which can reach ComfyUI on `:8446` directly, so the code stops mistaken or self-approved queuing, not a deliberately hostile agent with a shell. P4.4's fences cover that. |

## 8. Evidence (checked 2026-11-18)

| Claim | Verdict | Source |
|---|---|---|
| X3 Serve ports: 443 llama-swap, 8443 Open WebUI, 8444 pi-mobile | Verified | U8, U22, U36 |
| Open WebUI uses host networking and binds 127.0.0.1:3000 | Verified | U22 |
| AlienPC Serve ports: 8444, 8445 PixlStash, 8446 ComfyUI; 8447 free | Verified | `alienpc-comfyui-config/tailscale_serve_status.txt` (Nov 17) |
| AlienPC ComfyUI stop waits for the render queue (ALI-156: 1800 s cap, `unloadTimeout` 1900) | Verified in the Oct 26 config; P0.0 confirms the live one | `alienpc-community/notes/llama-swap-pre-RENDER-TIMEOUT-20261026.yaml` |
| The GPU lock gate holds LLM requests only while `gpu-render.lock` has a live PID | Verified | `gpu_lock_gate.py` |
| llama-swap: swaps wait for in-flight requests; explicit unload does not; `apiKeys` cover all routes; matrix router since v202; persistent groups can't be unloaded by other groups | Verified | llama-swap main: `scheduler/fifo.go`, `router/base.go`, `server.go`, groups-and-matrix guide |
| pi: `--session` resumes a session file; `--model` overrides the saved model; no turn or time limit flag; `--approve` only trusts project files | Verified | pi `docs/cli.md`, `docs/security.md`, `src/core/sdk.ts` |
| Hermes: the API server needs `API_SERVER_ENABLED` and `API_SERVER_KEY`; `command_allowlist` is not a fence; no push to API sessions; `max_turns` unlimited by default; SearXNG plugin; 64K minimum | Verified | Hermes `llms-full.txt`; NousResearch/hermes-agent |
| gufo 0.35.0 (Nov 17): full context reserved per session; pooling only on main (#1258); #1036, #1232, #1198 and #957 open | Verified | gufo release notes, `docs/cli.md` at v0.35.0, issues |
| NeosQ uncensored UD-Q4_K_XL: Unsloth type table, MTP and vision included, tested on gufo and Halogen | Verified from the card | HF `NeosQ/Qwen3.8-Flash-Next-Uncensored-UD-Q4_K_XL` |
| ethanwtodd Swift requant: same tensor types as Unsloth UD-Q4_K_XL; tested on gufo; censored | Verified | HF `ethanwtodd/Swift-1.5-Qwen3.8-Flash-Next-Q4_K_XL-GGUF` |
| v2 said the Quat3rnion Swift HGN was load-tested | Wrong: the card says it was never loaded | HF `Quat3rnion/halogen-swift1.5-qwen3.8-flash-next-v2-abliterated` |
| v2 relied on the Swift heretic HGN download command | Wrong repo: it redirects to the ReverseEngineer repo | HF `johnlockejrr` Swift HGN repos |
| Halogen 0.20.7 with a GGUF: runs in the previous, non-concurrency mode; still 4 slots | Verified | Halogen `CHANGELOG.md` |
| Tailscale SSH server on Windows | Not supported | tailscale.com/kb/1193 |
| Memory (Nov 17): Halogen huihui 89.7 GiB at a 524K pool, 62 GiB locked, about 17 GiB left; JoyCaption 9.4 GiB; embed-small 0.13 GiB; qwen27b 70.2 GiB | Verified | gufo phase-1 RESULT (U1a, 08:35, 08:49); U24 |
| Tagger: disabled Nov 17 (crash loop); 32,964 pictures in the library | Verified | gufo phase-1 RESULT (09:43); U42 |
| Live X3: one resident uncensored Halogen 0.20.7 slot with pins, preload, vision, 4 slots / 524K pool; ref2va off; JoyCaption on demand | Verified (committed config) | `u58` `2d73543`, `4ab1d15` |
| Thinking `off` broke Render and Forge tool calls on this model; `low` fixed it | Verified (commit) | `u58` `32a46c0` |
| gufo 0.34.0 on this box: tools 3/3, 4 callers with no 429s, prose decode 50 tok/s; memory gate failed with Gemma and ref2va resident; SELinux `:Z` relabel fix | Verified | `records/2026-11-17-gufo-phase1-RESULT.md` |
| Huihui v2 HGN cutover failed on a duplicate alias; v2 never loaded | Verified | `u58` `92bb886` |
| Forge compaction never fires; chats reached 236K tokens | Verified (U58 read-only audit; the 98% pool figure is Max's) | `u58-chat-read-plan` `48f6f06` |
| AlienPC clips land on the QNAP share at `renders/runs/<run>/clip/` | Verified | `alienpc-community` `98fbc30` |
| `.bak` copies come from a written rule | Verified | `community/agent-shared/AGENTS.md` line 16 |
| U34 pre-staged the AlienPC panes onto X3 models for the next logon | Verified | U34-rollout-done |
| Swift is uncensored only with ESP (`experimental_speed_projection: true`) | Verified | `agy_audit_20261025_report.md` |
| Community pattern: one strong model shared by all agents; llama-swap TTL unloading for specialists; Hermes with gufo and Flash-Next in use | Verified (Reddit, Sep-Oct 2026; gufo #715) | PullPush archive of r/StrixHalo, r/LocalLLM, r/hermesagent |
| PixlStash has CLIP and SBERT semantic search, face groups and likeness, a smart score with a defect penalty, sets with a tag review queue, folder-watch import and an MCP server | Verified (official docs) | `pixlstash-integration-findings-20261116.md`; pixlstash.dev |
| PixlStash library and server live on the X3 (location plan option B) | Verified | `pixlstash-location-plan-20261116.md`; U42, U44 |
| A new pi session starts at medium thinking unless `--thinking` is passed; `qwen-chat-template` sends `enable_thinking: false` at off | Verified | pi `docs/settings.md`, `src/core/sdk.ts`, `ai/src/api/openai-completions.ts` |
| Hermes's API server saves a base64 image from chat and tells the model `[Image attached at: <path>]`; it has no file-upload route | Verified in code (docs only partly) | NousResearch/hermes-agent `gateway/session_api_media.py`, `api_server.py`; `llms-full.txt` |
| With `qwen-chat-template`, pi needs no `thinkingLevelMap` to turn thinking off (that map matters only for the plain `openai` format) | Verified | pi `ai/src/api/openai-completions.ts` |
| `amd_iommu=off` speeds up this box | Wrong: U19 measured on and off as a wash, and the NPU device disappears when it is off | `bakeoff/RESULTS.md` U19 rows |
| X3 Forge needs AlienPC's tool-output truncator | Not needed: pi's bash keeps the last 50 KB by itself, and the 1,233-line guard was retired in the Oct 23-25 "make pi stock" reset | `forge-opus-verify` notes; `archive/2026-10-23-prereset` |
| Stock gufo 0.35.0 runs `empyrealworks` Swift abliterated | Wrong: its Q4_1 tensors need a gufo build upstream declined (#906) | HF card; gufo #906 |
| Halogen runs small models on the NPU beside Flash-Next, behind the same port, chosen per request by `model`. Covers embeddings, reranking, speech to text (WAV only), text to speech (WAV or PCM, no mp3), `d3-nano` picture questions and the agent guard (`watch`/`hold`, not a security boundary) | Verified | peonist.ai/halogen/docs/NPU, /docs/agent-guard |
| Halogen has no NPU-only mode; the two-container setup starts no NPU engine | Verified (no such mode documented) | Halogen `docs/FLAGS.md`, `docs/NPU.md` |
| NPU needs the IOMMU on, the fabric clock held, the newest BIOS; hangs are still possible (TheRock#8709) | Verified | Halogen `docs/NPU.md` |
| gufo's documented NPU use is EmbeddingGemma 2 text (`--npu`, about 30% of its GPU speed) | Verified | gufo `docs/models/embeddinggemma-2.md` |
| Open WebUI takes OpenAI-compatible embeddings, an external reranker URL, a query prefix, OpenAI-compatible speech to text and text to speech, and extra TTS parameters | Verified | docs.openwebui.com env-configuration: `RAG_OPENAI_API_BASE_URL`, `RAG_EXTERNAL_RERANKER_URL`, `RAG_EMBEDDING_QUERY_PREFIX`, `AUDIO_STT_ENGINE`, `AUDIO_TTS_OPENAI_PARAMS` |
| Open WebUI has API-key fields for embeddings, the external reranker, speech to text and text to speech | Verified | docs.openwebui.com env-configuration: `RAG_OPENAI_API_KEY`, `RAG_EXTERNAL_RERANKER_API_KEY`, `AUDIO_STT_OPENAI_API_KEY`, `AUDIO_TTS_OPENAI_API_KEY` |
| gufo 0.35.0 has `--preserve-thinking`, `--served-model-name`, `--stall-timeout-ms`, `--cache-ram-bytes` and `--max-pending` (default 16) | Verified | gufo `docs/cli.md` at v0.35.0 |
| Tailscale Serve: serving a folder needs root; `off` needs the original flags | Verified | tailscale.com/docs/reference/tailscale-cli/serve |
| No Tailscale ACL was ever applied | Verified (Nov 15) | `serve/U8-serve-and-cross-wiring.md` |
| `:8446` reaches only `comfyui_auto`; the AlienPC also runs `comfyui_longvideo` in the same group | Verified | `alienpc-comfyui-config/llama-swap_comfy_entries.yaml`, `tailscale_serve_status.txt` |
| An X3-queued render holds only the X3's lock, which the AlienPC gate can't see | Verified | `x3-render/x3/README-X3.md` (Known gaps), `queue-remote.sh` |
| Swift's AlienPC `contextWindow`: 92,160 in the only snapshot; Strata allows 131,072; "128,000" unconfirmed | Verified as stated | `pi_config_snapshots/models-pre-VIS.json`; argon progress notes |
| pi provider custom headers: no example found, so the fail-fast mode is a separate gate port rather than a request header | Checked | repo models.json files |
| Private ntfy server `ntfy-renders` on the QNAP: v2.35.0, deny-all, tailnet `:8447`, topic `renders-a7gma8xg`, write-only `pi-pub` token on the AlienPC; NT-1 ACL was still Derrick's console step on Oct 30 | Verified (build record) | `fleet-brain` `40_projects/compute-expansion/plans/2026-10-30-render-ntfy-qnap-build-plan.md` |
| ntfy has a `copy` action button for one-time codes, shown in the Android app | Verified | docs.ntfy.sh/publish (copy action) |
| AlienPC ComfyUI idle timers: `comfyui_auto` 300 s, `comfyui_longvideo` 600 s | Verified | `alienpc-comfyui-config/llama-swap_comfy_entries.yaml` |
| PixlStash imports `.mp4`, `.webm` and `.mov` videos, and the tagger tags their frames | Verified | `records/U49-RESULT.md` |
| `evo` has its own key file (`~/.config/evo-x3/llm.env`, 0600, only `LLM_KEY_PI`) and can't read `/etc/evo-x3` | Verified (Nov 16) | `records/U35-redteam-fixes-20261116.md` |
| gufo's Flash-Next reads images through an mmproj file (next to the model, or `--mmproj`) and thinks at `xhigh` by default | Verified | gufo `docs/models/qwen3.8-flash-next.md` at v0.35.0 |
| Halogen's guard adds `halogen-spotter-0.6b` and fetches it with `HALOGEN_DOWNLOAD` | Verified | peonist.ai/halogen/docs/agent-guard |
| Halogen refuses to pin its weights with less than 16 GiB free | Verified (Nov 17) | gufo phase-1 RESULT (09:43 addendum) |
| pi: `--session-dir` and the `sessionDir` setting move session storage; `--continue` resumes the newest session for the current folder | Verified (pi docs as quoted in U58) | `u58-chat-read-plan` `records/U58/PLAN.md`, section 2 |
| `ralph.sh` puts its worktrees in `~/AI/_worktrees` | Verified | `x3-forge/ralph-community/ralph.sh` |
| The X3 has no `:8445` PixlStash share (that list is the AlienPC's) | Verified | `x3-serve-after-u22.json`; `alienpc-comfyui-config/tailscale_serve_status.txt` |

## 9. Rollback

- **llama-swap.yaml:** etckeeper history plus the rollback file. Restore and restart in 5 minutes or less.
- **Weights:** the files in use before cutover stay on disk until P6 passes.
- **Hermes:** `systemctl --user stop`; Open WebUI keeps talking to llama-swap directly.
- **NPU (P4.10):** remove `HALOGEN_NPU_MODELS`, `HALOGEN_AGENT_GUARD`, the accel device and the NPU mount from the `flash-next-uncensored` command; restore `useModelName` and remove the NPU pins; point Open WebUI back at `embed-small`.
- **AlienPC:** `tailscale serve --https=8447 off`, stop the `:8086` gate, and revert the P5.4 line.
- **Renders share:** `sudo tailscale serve --https=8443 --set-path=/renders off`.
- **ntfy (P4.11):** `ntfy user del x3-pub` in the `ntfy-renders` container (its token dies with it), and delete `~/.config/evo-x3/ntfy-x3.token`.
