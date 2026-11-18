# EVO-X3 + AlienPC agent setup plan (v3: verified and simplified)

- **Status:** Active, v3, 2026-11-18. Planning only; nothing on the X3 or AlienPC has been changed.
- **Owner:** Derrick. Steps marked **Y** need his yes at the time.
- **Executor:** Max (GrokBot) via agy or Forge on the X3. Console-only steps (Tailscale ACL, typing keys) are Derrick's.
- **Tracking issue:** https://github.com/incognitodb86-creator/evo-x3/issues/1
- **Source of truth for machine state:** Gitea `derrick/evo-x3`. This GitHub repo is a snapshot.
- **Settings rule:** use the vendor-documented setting or one already proven on this box. Where neither exists, the plan says so and tests it before use.

## What changed from v2

Every v2 claim was re-checked on 2026-11-18 against the repo records and primary sources (section 8). v3 drops what the evidence does not need.

| v2 item | Finding | v3 |
|---|---|---|
| AlienPC job service (HTTP verbs, token, Windows worktrees, git WIP handoff) plus preempt hooks in `queue-remote.sh`, `comfy-guarded.ps1` and `gpu_lock_gate.py` | Not needed. The AlienPC's ComfyUI stop command already waits for the render queue (ALI-156), and llama-swap waits for in-flight requests before a swap. Tailscale SSH cannot run as a server on Windows anyway. | pi always runs on the X3 and uses the AlienPC's Swift model over the network. When a render starts, the same pi session resumes on the X3 model (section 3). |
| Two Hermes profiles; two Forge panes | One Hermes profile without web tools has no untrusted input. For Forge, the Nov 16 audit's one-pane option with approval prompts is enough. | `Hermes-X3` and `Forge-X3`. A split stays an option (OD2). |
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

**Cheapest falsifying check:** P0.1, one evening: gufo 0.35.0 with the uncensored NeosQ file. If it fails, the proven Halogen uncensored slot is the fallback. If both fail, stop and decide with Derrick.

## 2. Decisions

| ID | Decision (Derrick, 2026-11-18) |
|---|---|
| D1 | pi is the only coding harness on both machines. |
| D2 | Hermes Agent runs always on, on the X3, as one profile, `Hermes-X3`. It hands coding and render prompts to pi launchers and never edits code itself. |
| D3 | GrokBot keeps running. Derrick talks to it directly when he wants it; Hermes has no GrokBot link. |
| D4 | Uncensored by default for the chat and coding models: Hermes's model, Forge, Swift. Gemma Heretic is already uncensored. JoyCaption, ref2va-27b and qwen27b are tools inside existing pipelines, not chat models. |
| D5 | X3 engines: Halogen, gufo and llama.cpp behind llama-swap, each model on the engine where it passes. Model IDs and ports stay as they are. |
| D6 | `flash-next` is the X3's one main model, for Hermes and for X3 coding. Everything else swaps with it through llama-swap. This is the community pattern: one strong shared model, specialist models loaded on demand. |
| D7 | Jobs per model. `flash-next`: Hermes, X3 coding fallback, and pictures if its vision works. Swift (AlienPC): coding and review whenever the AlienPC is not rendering. `gemma4-heretic`: render prompts (Render-X3). `ref2va-27b`, JoyCaption: inside the existing render and tagging pipelines. `embed-small`: embeddings. `qwen27b`: unchanged, manual use only (stock model, so it can refuse). |
| D8 | The AlienPC keeps its Strata setup. Its GPU is for ComfyUI renders and Swift. |
| D9 | Render first: a render is never interrupted (the existing ALI-156 stop command waits for the render queue). A coding job using the AlienPC moves to the X3 model when a render starts, in the same pi session. |
| D10 | Batch jobs do not thrash the main model. The PixlStash tagger is paused during tests and runs nightly once its backlog is done. JoyCaption and ref2va-27b share memory with `flash-next` only if the memory test shows room. |
| D11 | Access: the existing Open WebUI on `:8443`. Hermes's API stays on loopback. No new Tailscale ports on the X3. |
| D12 | Model downloads one at a time, each with a yes. |
| D13 | Every live change needs Derrick's yes at that moment. |
| D14 | eGPU later. Nothing here blocks it: it becomes another llama-swap backend. |
| D15 | Every chat is labeled `<Role>-<Host>`: Hermes-X3, Forge-X3, Render-X3, Sydney-X3, Forge-AlienPC, Render-AlienPC, Sydney-AlienPC. Labels only; folders and launcher files keep their names. |
| D16 | Hygiene: git and etckeeper replace `.bak` copies. Run outputs go to `_runs/` and agent checkouts to `worktrees/`. Cold weights that can be downloaded again are deleted after a manifest, with a yes. |

Superseded, kept for history: U9/R5 "AlienPC render-only" and audit item I10 (by D8 and D9); U34 "Flash-Next on Halogen stock" (by gate G0); the Oct 10 plan's model choice (its safety ideas are kept).

## 3. How it fits together

```
Phone browser --Tailscale :8443--> Open WebUI (X3, 127.0.0.1:3000, host network)
                                     --> Hermes-X3 API (127.0.0.1:8642, key) --> llama-swap :8080, model "flash-next"

Hermes runs, as user evo:
  ~/AI/bin/pi-job code   <repo> "<task>"   new worktree ~/AI/worktrees/<id> on a job branch, then pi -p on the X3
  ~/AI/bin/pi-job review <repo> "<what>"   same, read-only tools
  ~/AI/bin/pi-job render "<ask>"           Render launcher one-shot (dry run; queueing still needs Derrick's yes)
  ~/AI/bin/pi-job status <id>
pi model for code/review: alienpc/coding_swift15_iq3s_esp if the AlienPC is free, else x3-local/flash-next.
While on the AlienPC, pi-job re-checks every 30 s. If a render started, it stops pi and resumes the
same session (pi --session <file> --model x3-local/flash-next).

AlienPC, unchanged except one new tailnet port:
  Swift (Strata) <- llama-swap 127.0.0.1:8080 <- GPU lock gate 127.0.0.1:8085 <- Tailscale Serve :8447 /v1 (new, X3 only)
  ComfyUI        <- llama-swap /upstream/comfyui_auto <- Tailscale Serve :8446 (existing)
  "Free" = GET https://alienpc.tailf242b2.ts.net:8446/api/queue returns 409 (ComfyUI not loaded) or an empty queue.
```

Why render-first holds without new machinery:

- A render request waits for the Swift answer already in flight, then llama-swap swaps. llama-swap's scheduler "defers the swap until those callers finish", so a render waits at most one answer.
- A Swift request during a render cannot kill the render. ComfyUI's stop command waits for the render queue (ALI-156, up to 1800 s). pi-job avoids that wait by moving to the X3.
- Local AlienPC renders hold `gpu-render.lock`, and the gate already holds LLM requests while it is held.
- An explicit llama-swap `/unload` does kill in-flight requests. pi-job treats a failed request like a render start and resumes on the X3.

## 4. Memory (X3, 120 GiB GPU limit)

| Model | Size on this box | Source |
|---|---|---|
| Halogen uncensored Flash-Next (huihui HGN) | 88.9 GiB engine total | llama-swap.yaml U26 comment |
| gufo Flash-Next UD-Q4_K_XL (stock or NeosQ) | 108-115 GiB at 1 x 262K. gufo 0.35.0 reserves a full context per session, so 2 x 131K costs about the same. | archived gufo slot; gufo v0.35.0 `docs/cli.md` |
| gemma4-heretic Q8_0 (-np 4) + JoyCaption | about 50 GiB together | U48 |
| qwen27b Q8 + DFlash2 | 70.2 GiB | U24 |
| ref2va-27b | 19.1 GiB | U48 |
| JoyCaption | about 9 GiB | U47 |
| embed-small | under 1 GiB | llama-swap.yaml |

- `flash-next`, `gemma4-heretic` and `qwen27b` stay in today's exclusive group: one loaded at a time.
- gufo sessions: `--sessions 2 --context 131072`. Hermes needs at least 64K, and pooled sessions exist only on gufo's unreleased main branch.
- If P0.4 shows less than 8 GiB free with JoyCaption and ref2va-27b loaded next to `flash-next`, switch llama-swap to its documented matrix router (v202 and later; the X3 runs v272) with three allowed sets: {flash-next, embed-small}, {gemma4-heretic, ref2va-27b, joycaption, embed-small} and {qwen27b, embed-small}. The render pipeline keeps Gemma and ref2va together, and Flash-Next never shares memory with them.

## 5. Phases

**Y** = needs Derrick's yes at the time.

Phase 0 checks reuse existing fixtures; nothing new is built:

- **C1 Load:** load time, GTT used, MemAvailable.
- **C2 Parallel:** `u34/pool_test.py` at the planned session count.
- **C3 Refusals:** the U26 probes (benign_sysadmin, adult_fiction, explicit_adult) comply 3/3.
- **C4 Tools:** the U6 three-step tool chain 3/3 with tool-call IDs intact (gufo #780), plus 2 requests with `tool_choice: "none"` (gufo #1232 is open: "returns the call as text 8/8 times").
- **C5 Coding:** the Pi part of `deepu105/quant-bench` (11 Aider polyglot tasks; the community benchmark Derrick shared). Record pass count and wall time.
- **C6 Vision (information only):** the bake-off vision card.

### Phase 0: snapshot and test on the X3 (no production change)

| ID | Step | Pass | Stop |
|---|---|---|---|
| P0.0 | Ask Max what the in-flight loop fix already changed. Snapshot live llama-swap.yaml, pi settings, herdr scripts and AGENTS.md files to Gitea. Pause the tagger during tests (`systemctl --user stop u42-pixlstash-tagger`; it resumes where it stopped). | Snapshot committed; tagger stopped. | — |
| P0.1 **Y** | gufo 0.35.0 with `NeosQ/Qwen3.8-Flash-Next-Uncensored-UD-Q4_K_XL`: Unsloth's type table, its own MTP head and vision projector, and a card that says it was tested on gufo and Halogen. Flags from gufo's Flash-Next page (`--speculative mtp --mtp-model ...`) plus `--sessions 2 --context 131072 --preserve-thinking on`, as in the archived gufo slot. | C1-C5 pass. | Load fails, or C3 or C4 fail. |
| P0.2 **Y** | Halogen 0.20.7 with the existing uncensored slot (huihui HGN; passed U26 on 0.20.5). 0.20.6 fixed replies computed from another conversation's context. | C1-C5. | — |
| P0.3 **Y**, optional (OD1) | Uncensored Swift on the X3: Halogen 0.20.7 with `johnlockejrr/Swift-1.5-Flash-Next-Heretic-ReverseEngineer-HGN`, the only Swift HGN with a load report (no refusal or quality data; 119 GB). | C1-C5. | Skipped unless Derrick wants it. |
| P0.4 **Y** | Memory: the leading candidate plus embed-small, JoyCaption and ref2va-27b loaded, one request each. | At least 8 GiB MemAvailable; no OOM. | Under 8 GiB: use the matrix rule in section 4. |
| G0 | Pick what `flash-next` runs. Among candidates passing C1-C4, take the most C5 tasks passed; on a tie, gufo (Derrick's preference); then speed. If P0.3 wins, Swift serves Hermes and X3 coding. | — | Nothing passes: stop and decide with Derrick. |

Delete a losing candidate's files before downloading the next one, and keep at least 100 GiB free.

**Watch:** gufo PR #1036 (per-request residual projection). Once it ships, test the gufo-proven `ethanwtodd` Swift file with a refusal projection. That is the same method Strata uses for Swift on the AlienPC.

### Phase 1: stop the loops (Nov 16 audit; coordinate with P0.0)

| ID | Step | Pass |
|---|---|---|
| P1.1 | B4: commit the X3's live trees to Gitea with `/home/evo` paths and the `agent-shared/extensions` folder. Give `evo` its own Gitea token (I12). | A fresh clone starts Forge with all skills. |
| P1.2 | B3: Ralph's GPU check uses an X3-only lock with `flock -n`. | A 2-item Ralph loop runs with no 1-hour waits. |
| P1.3 | I2: before each Ralph loop, clear stale `fix_plan.md` items. Each pass runs a skill-load smoke test and a file-count cap from `git diff --stat`, and may not edit skills or AGENTS.md. One worktree per loop. | A planted stale item and a planted 30-file rewrite are both refused. |
| P1.4 | I3: mark the 6 known failing tests xfail with reasons. | The suite is green, and a new failure fails it. |
| P1.5 | I8: short Always / Ask / Never AGENTS.md files. Replace the `.bak` rule in `community/agent-shared/AGENTS.md` (line 16) with "commit to git; etckeeper for /etc". | No contradictions left between the files. |
| P1.6 **Y** | I9: set the subagent model per pane (`flash-next-sub`; Render keeps `gemma4-heretic-sub`). Upgrade pi-subagents to 0.88.1 or later with explicit context inheritance. | A Forge subagent causes no model swap. |
| P1.7 **Y** | B1: agy runs as `evo`, in a per-job worktree, with a time limit. | A test agy job cannot sudo and stops at its limit. |
| P1.8 **Y** | B2 (OD2): Forge-X3 asks before vault reads, Gitea writes and outbound sends, using the installed pi-permission-system extension. pi itself never asks per tool call, and its `--approve` flag only trusts project settings (pi docs). Headless runs deny those tools. | A planted "read the vault" prompt asks first in Forge-X3 and is denied in Ralph. |
| P1.9 | Loop limits: load `loop-guard.ts` (stops a third identical tool call) in every pane. Run every headless job (Ralph, pi-job) under `timeout`, because pi has no turn or time limit of its own. On timeout, write a `STUCK` status note. | A planted impossible task ends `STUCK` at its limit. |

### Phase 2: names and hygiene

| ID | Step | Pass |
|---|---|---|
| P2.1 **Y** | Labels. On the X3, `herdr-panes.sh` creates each workspace with `--label "$name"`: add a label map (render → Render-X3, forge → Forge-X3, sydney → Sydney-X3) and relabel the existing workspaces. Do the same on the AlienPC in `C:\AI\director\scripts\pi_herdr_at_logon.ps1` (Forge-AlienPC, Render-AlienPC, Sydney-AlienPC). Each launcher passes one identity line ("You are Forge-X3 on evo-x3") through pi's append-system-prompt option. Don't put it in `community/agent-shared/AGENTS.md`, which both machines load. Folder names, launcher files and pi state folders stay the same. | herdr and pi-mobile show the new labels, and each chat names its host when asked. |
| P2.2 **Y** | Clean up. Write a manifest first (repo, revision and sha256 for each file), then delete only after a yes: `/srv/bakeoff` (341 GiB), unused `~/rocm` (9.9 GiB), the aborted U34 backup (5.2 GiB) and the old Q4 27B file (17 GiB). After P6 passes, also delete Flash-Next files that neither llama-swap.yaml nor its rollback file use. Copy to QNAP only what can't be downloaded again: results, logs, custom conversions. | About 370 GiB freed now; manifest in Gitea. |
| P2.3 | Layout. pi-job and Ralph logs go to `~/AI/_runs/` (gitignored). Render runs stay in `community/runs/`; fix U23 gap 11 so a relative run path can't write outside it. Agent checkouts go in `~/AI/worktrees/` and are removed once their branch merges. Delete existing `_archive/*.bak-*` files after the next verified QNAP backup. On the AlienPC, run `git config --system core.longpaths true` (Git for Windows' fix for "Filename too long"). After its backlog finishes, run the tagger from a nightly systemd timer. | No new `.bak` files for a week, and the evo-x3 snapshot clones on the AlienPC. |

### Phase 3: X3 model cutover (after G0)

| ID | Step | Pass |
|---|---|---|
| P3.1 **Y** | llama-swap.yaml: `flash-next` runs the G0 winner. Keep its ID, the `flash-next-sub` alias and `useModelName` (the maintainer's answer in llama-swap #1355). Save the old command as a rollback file, as U34 did, and archive the separate `flash-next-uncensored` slot. gufo gets `--stall-timeout-ms 120000`: per gufo's docs a hang then exits like a crash, and llama-swap restarts it on the next request. If Halogen wins, it runs 0.20.7. Apply the P0.4 matrix rule if needed, and commit with etckeeper. If the session size changed (gufo 2 x 131K), set `contextWindow` to 131072 in the X3 pi models.json, the AlienPC `evo-x3` provider and Hermes. | verify-serve gives 401 without a key and 200 with one; C2 and C3 pass; a Gemma request and back works; Forge-X3, Render-X3 and the AlienPC panes still answer. |

### Phase 4: Hermes-X3

| ID | Step | Pass |
|---|---|---|
| P4.1 **Y** | Install Hermes Agent as `evo` with the official installer. Run `hermes gateway install` (systemd user service) and `loginctl enable-linger evo` (a sudo step; Max runs it after a yes). Provider: llama-swap as an OpenAI-compatible endpoint at `http://127.0.0.1:8080/v1`, model `flash-next`, key `LLM_KEY_HERMES` (already in llama-swap's key list). Pin `context_length`, because Hermes misreads llama.cpp context sizes (issue #155853). Vision: `flash-next` if C6 passed, otherwise `auxiliary.vision` set to `gemma4-heretic` (one swap per picture). If replies come back empty, set `chat_template_kwargs.enable_thinking: false` (Hermes docs). | Hermes answers and survives a reboot. |
| P4.2 **Y** | API server: `API_SERVER_ENABLED=true`, an `API_SERVER_KEY`, bound to `127.0.0.1:8642`. In Open WebUI (Admin > Settings > Connections), add `http://127.0.0.1:8642/v1` with that key. Open WebUI uses host networking, so loopback works; its environment settings only apply on first launch, so add it in the UI. Name the model `Hermes-X3` and keep Open WebUI's own web search off for it. | The phone reaches Hermes-X3 on :8443, and port 8642 is not reachable from the tailnet. |
| P4.3 | `~/AI/bin/pi-job` (one short script) plus one Hermes skill explaining when and how to call it. It detaches at once and prints a job ID, writes `~/AI/_runs/<id>/status` and `log`, and `pi-job status <id>` reads them. Hermes's own background tool can't push results into Open WebUI (Hermes docs: API-server completions are "never autonomous new model turns"), so the status file is the check. Optional: one ntfy line when a job ends, if Derrick gives `evo` a publish token for one topic. | Hermes starts a job and reports its status when asked. |
| P4.4 | Safety. Hermes's API-server toolsets: terminal, files, memory and skills; no web or browser (OD3). Hermes runs as `evo`, which has no sudo; apart from `llm.env` (the llama-swap caller keys, readable by `evo` per U36), `/etc/evo-x3` is root-only. Set `agent.max_turns`, which is unlimited by default. Keep `unattended_mode: deny` and set a short `approvals.timeout`, because Open WebUI's streaming requests still wait for approval on flagged commands. `command_allowlist` only pre-approves flagged commands and is not a fence. | A flagged command is refused quickly, and a runaway turn stops at `max_turns`. |

### Phase 5: AlienPC Swift lane

| ID | Step | Pass |
|---|---|---|
| P5.1 **Y** | On the AlienPC, publish the GPU lock gate's `/v1` on a new tailnet-only port: `tailscale serve --bg --https=8447 --set-path=/v1 http://127.0.0.1:8085/v1` (8447 is free in the Nov 17 snapshot). Make sure the gate starts at logon. Add ComfyUI's queue path to llama-swap `upstream.ignorePaths` so the X3's status probe can never load ComfyUI; status paths already return 409 when it is unloaded (U8). Tailscale ACL: `:8446` and `:8447` reachable only from the X3 and Derrick's devices, as U8 already recommended for 8446. If the AlienPC's llama-swap uses API keys, give the X3 its own (Derrick types it). | From the X3, `/v1/models` on :8447 works, and the queue probe returns 409 while ComfyUI is unloaded. A device outside the ACL is refused. |
| P5.2 | On the X3, add an `alienpc` provider to evo's `~/.pi/agent/models.json`: `api` openai-completions, `baseUrl` `https://alienpc.tailf242b2.ts.net:8447/v1`, a key read from a 0600 file, and the `coding_swift15_iq3s_esp` entry copied from the AlienPC's models.json (`contextWindow` 131072, `samplingParams.experimental_speed_projection: true`). The Oct 25 audit found that sending `false` turns Swift's refusals back on. | `pi -p --model alienpc/coding_swift15_iq3s_esp` answers and passes C3. |
| P5.3 | pi-job uses the AlienPC first when it is free. While on the AlienPC it re-probes every 30 s. On a render or a failed request, it stops pi (SIGTERM; print mode exits cleanly) and resumes with `pi --session <file> --model x3-local/flash-next` in the same worktree. pi then uses the new model and drops the old model's thinking blocks. | AC-OP step 4 passes. |
| P5.4 **Y** (OD5) | AlienPC pane models. U34 pre-staged a change (alienpc-director `b5d964a`): at the next AlienPC logon, Forge-AlienPC moves to the X3's `flash-next`, and Render-AlienPC and Sydney-AlienPC move to the X3's Gemma. Default: revert only the Forge line, so Forge-AlienPC keeps local Swift (D8). Keep Render and Sydney on the X3's Gemma, so the AlienPC GPU stays free for ComfyUI and Swift. | After a logon, Forge-AlienPC runs local Swift. |

### Phase 6: acceptance

| ID | Step | Pass |
|---|---|---|
| P6.1 | AC-OP end to end from a phone. | All four results as described in section 1. |
| P6.2 | A deliberately impossible task on each lane (AlienPC Swift and X3 Flash-Next). | Both end `STUCK` at their limit with a status note. |
| P6.3 | Rollback drill: restore the previous llama-swap.yaml, then the new one again. | 5 minutes or less each way. |

### Phase 7: eGPU (notes only)

- **Separate backend.** The eGPU gets its own engine instance behind llama-swap, with its own model names: llama.cpp, or the `llama-halo-hybrid` fork, which marks the R9700 as production. First candidate: `gemma4-heretic`, so render prompts stop swapping out `flash-next`.
- **Pin engines to the iGPU.** gufo crashed with a second GPU present (gufo #696), so pin it to the iGPU (`HIP_VISIBLE_DEVICES` / `ROCR_VISIBLE_DEVICES`). Halogen hides extra GPUs itself (Halogen #188: an EVO-X3 with a 7900 XT over OCuLink).
- **Card notes.** If an R9700 drops off the bus at idle, turn ASPM L1 off. No reports found for the Arc Pro B70.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Uncensored model with tools: injected text meets no refusal. | Hermes has no web or browser tools. Forge asks before vault reads, Gitea writes and outbound sends; headless runs deny them. |
| Open gufo bugs: #1232 (`tool_choice: "none"`), #1198 (load refused after a cold boot), crashes on long runs. | C4 tests #1232. For #1198, use gufo's documented workaround (`--cache-ram-bytes off`, or boot with `kho=off`). llama-swap restarts gufo on the next request. |
| The uncensored files are community requants, not official. | C1-C5 on this box. The Halogen huihui slot is the proven fallback. |
| The huihui abliteration may cost quality: one source, the dymoo fork README, scored it 56% against 90% for the base model. | C5 compares all candidates on the same tasks. |
| Swift's licence: free up to US$1M revenue. | Personal use. |
| Every `flash-next` reload costs about 25 s. | One main model; batch jobs at night; the eGPU later. |
| The tagger backlog (about 1.5 days from Nov 16) keeps Gemma loaded. | Paused during tests; nightly afterwards. |
| The new AlienPC LLM port. | Tailnet-only, ACL limited to the X3 and Derrick's devices, plus a key if llama-swap uses keys. |
| Hermes approvals can stall Open WebUI for up to `approvals.timeout`. | A short timeout; Hermes's work goes through pi-job, which needs no approval. |

## 7. Open decisions

| ID | Decision | Default |
|---|---|---|
| OD1 | Try uncensored Swift on the X3 (P0.3: 119 GB download, no refusal or quality data)? | Skip. The AlienPC Swift lane covers coding. |
| OD2 | Forge-X3: one pane with approval prompts, or separate web and ops panes? | One pane. |
| OD3 | Hermes web search. Hermes has a native SearXNG plugin and the X3 already runs SearXNG. If it is turned on, use a second profile that cannot run pi-job. | Off. |
| OD4 | eGPU model and first workload. | When bought. |
| OD5 | AlienPC panes after U34's pre-staged change (P5.4). | Forge-AlienPC back to local Swift; Render and Sydney stay on the X3's Gemma. |
| OD6 | Hermes channel. The Hermes community mostly uses Telegram or Discord gateways, which also push job results. | Open WebUI (decided); a gateway is optional later. |

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
| Memory: Halogen Flash-Next 88.9 GiB; Gemma + JoyCaption about 50 GiB; ref2va-27b 19.1 GiB; qwen27b 70.2 GiB | Verified | llama-swap.yaml, U48, U24 |
| Tagger: 32,964 pictures, about 1.5 days' ETA on Nov 16, uses gemma4-heretic | Verified | U42, U44 |
| `.bak` copies come from a written rule | Verified | `community/agent-shared/AGENTS.md` line 16 |
| U34 pre-staged the AlienPC panes onto X3 models for the next logon | Verified | U34-rollout-done |
| Swift is uncensored only with ESP (`experimental_speed_projection: true`) | Verified | `agy_audit_20261025_report.md` |
| Community pattern: one strong model shared by all agents; llama-swap TTL unloading for specialists; Hermes with gufo and Flash-Next in use | Verified (Reddit, Sep-Oct 2026; gufo #715) | PullPush archive of r/StrixHalo, r/LocalLLM, r/hermesagent |

## 9. Rollback

- **llama-swap.yaml:** etckeeper history plus the rollback file. Restore and restart in 5 minutes or less.
- **Weights:** the files in use before cutover stay on disk until P6 passes.
- **Hermes:** `systemctl --user stop`; Open WebUI keeps talking to llama-swap directly.
- **AlienPC:** `tailscale serve --https=8447 off`, and revert the P5.4 line.
