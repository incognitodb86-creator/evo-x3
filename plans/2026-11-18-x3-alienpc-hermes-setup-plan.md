# EVO-X3 + AlienPC agent setup plan: Hermes, pi, uncensored models, mixed engines

- **Status:** Active (planning complete; execution not started)
- **Written:** 2026-11-18 by Copilot (planning only; no machine was touched)
- **Owner:** Derrick (every live change needs Derrick's yes at the time)
- **Executor:** Max (GrokBot) via agy or Forge on the X3; Copilot only drafted this
- **Tracking issue:** https://github.com/incognitodb86-creator/evo-x3/issues/1 (checklist mirrors section 5)
- **Source of truth for machine state:** Gitea `derrick/evo-x3`; this GitHub repo is a snapshot

## 1. Goal and operator acceptance

**Goal.** Derrick talks to one local assistant, **Hermes**, from a browser over Tailscale. Hermes answers
everyday requests on an uncensored model that stays loaded, picks the right model for each job, and sends
coding to **pi** running **Swift**: on the AlienPC when its GPU is free of render work, otherwise on the X3.
Agents stop looping. GrokBot (Max and the other bots) keeps running and is used when Derrick chooses.

**Operator acceptance (AC-OP).** From a phone browser over Tailscale, Derrick sends Hermes four messages:

1. A general question.
2. A request that a stock model would refuse (adult or explicit creative text).
3. A coding task while AlienPC render is idle.
4. A coding task while AlienPC render is busy, and then start a render while task 3 is still running.

He sees:

- 1 and 2 answered with no refusal and no model swap.
- 3 runs on Swift on the AlienPC.
- 4 runs on the X3's resident Flash-Next.
- When the render starts, the AlienPC job saves its work at a stopping point and the X3 continues it from
  that point.
- Hermes stays responsive throughout, and nothing loops past the configured limits.

**Cheapest falsifying check.** Phase 0 load tests (one evening of X3 model time). If no uncensored
Flash-Next variant passes on the X3, stop and return to Derrick before any cutover.

## 2. Ratified decisions (Derrick, 2026-11-18)

| ID | Decision |
|---|---|
| D1 | **pi** is the only coding harness on both machines. OpenCode is out. |
| D2 | **Hermes Agent** runs always on, on the X3, as Derrick's local assistant. It hands coding to pi. |
| D3 | **GrokBot** (Max etc.) keeps running in parallel. Escalation to GrokBot is manual (Derrick asks). |
| D4 | **Uncensored by default** for every model, including coding. |
| D5 | **X3 engines:** Halogen, gufo and llama.cpp behind llama-swap. Each model runs on the engine where it passes the load, refusal and tool-call tests. Halogen (closed source) is acceptable. Community gufo forks are acceptable if they pass. |
| D6 | **One Flash-Next stays loaded on the X3** and serves both Hermes and X3 coding, so the daily driver and the coder never swap. It is an uncensored Swift if one passes on the X3. Otherwise it is the best uncensored stock Flash-Next that passes: on gufo (NeosQ/SenseiHans files) or the Halogen abliterated slot. Phase 0 decides. |
| D7 | **Models per job:** Flash-Next = daily driver; Swift = coding; Gemma 4 Heretic = prompt writing and vision; ref2va-27b = H3 Ref2VA prompt rewriting; JoyCaption = captions and tags; nomic = embeddings; Qwen3.8-27B = dense second opinion. |
| D8 | **AlienPC keeps its current Strata setup**: Swift IQ3_S with the steering vector (pi default `coding_swift15_iq3s_esp`) and Gemma on PolyStrata. Render always comes first. |
| D9 | **Render priority:** before a render starts, the AlienPC coding job is told to reach a stopping point and save its work, then it hands off to the X3, which continues. |
| D10 | **Small group** (JoyCaption, ref2va-27b, embeddings) unloads when idle instead of staying loaded. |
| D11 | **Access:** browser over Tailscale. Open WebUI (already on the X3) talks to Hermes's API server on loopback. The Hermes dashboard is optional and needs its own login if published. There is no native Android app (only a Termux install). |
| D12 | **Large downloads are allowed**, each with a yes at the time. |
| D13 | **Every live change needs Derrick's yes at that moment:** llama-swap edits, restarts, installs, API keys, AlienPC changes. |
| D14 | **eGPU:** not purchased or installed in this plan, but coming soon. Nothing in the design may block adding it as another llama-swap backend. |

**Superseded by these decisions** (kept for history, not deleted):

- U9/R5 "AlienPC render-only" and the Nov 16 Forge audit item I10 "archive the AlienPC Forge/LLM slots".
  Replaced by D8/D9.
- U34 (Nov 16) "Flash-Next on Halogen stock, gufo slot archived". Replaced by D5/D6; the outcome is decided
  by Phase 0.
- The Oct 10 local-agent plan's model choice (Huihui-27B on the AlienPC as the whole agent). Replaced by
  D2/D6/D8. Its safety ideas (owned fail-closed approvals, memory byte budget) are reused.

## 3. Target architecture

```
Phone / laptop browser ──Tailscale Serve (tailnet only)──► X3: Open WebUI
                                                              │ OpenAI API, key-protected
                                                              ▼
                                    Hermes gateway, API server on 127.0.0.1:8642
                                    (user evo, systemd user service + linger)
                                    main model = flash-next-resident
                                    vision slot = gemma4-heretic · review slot = qwen27b
                                    subagents pick per task from a named model map
                                    skill "pi-code" = coding route (below)
                                           │
                                           ▼
X3 llama-swap (loopback; one API key per caller)
  resident (persistent, ttl 0): flash-next-resident  [Phase 0 decides engine + file]
  on demand (swap group):      gemma4-heretic        [gufo + extension if it passes, else llama.cpp]
                               qwen27b               [gufo, DFlash2]
  small group (idle unload):   joycaption, ref2va-27b, embed-small   [llama.cpp]
  rollback (archived):         flash-next-halogen-stock, flash-next-gufo-stock
                                           │
       Hermes "code" route ────────────────┤
                                           ▼
       AlienPC render lock free and lease free? ──yes──► pi + Swift (Strata) on AlienPC
                                           │ no                 │ render requested → save at a
                                           ▼                    │ stopping point, push branch,
                                pi + resident Flash-Next on X3 ◄┘ hand off (D9)
```

**Rules that hold everywhere:**

- One writer per git branch/worktree. Work moves between machines only as a pushed branch plus a handoff
  note (inbox/outbox), never as a shared folder.
- Hermes never runs a coding job itself; it starts pi with a task brief, a wall-clock timeout and an
  iteration cap, and reads back the result.
- Hermes has no built-in router that chooses a model from the request text. "Auto-routing" here means the
  resident main model decides, and hands work to the vision slot, the review slot, named subagent models, or
  the `pi-code` skill.
- Requests that arrive through Open WebUI run in Hermes's *unattended* mode: dangerous commands are denied
  without a prompt, and Hermes's own loop guard only warns. Hard limits therefore live in `agent.max_turns`,
  the command allowlist, and the pi job wrapper (P1.9, P3.5).
- Every model is addressed by a llama-swap model name. An eGPU later becomes one more backend with its own
  names (D14).

## 4. Memory budget (X3, 120 GiB GTT) — to be confirmed by P0.5

| Item | Approx. GiB | Source |
|---|---|---|
| Halogen abliterated Flash-Next (engine total, 262K pool) | 88.9 | llama-swap.yaml U26 comment |
| gufo Flash-Next UD-Q4_K_XL layout (stock or Swift requant) at 262K, 1 session | ~108–113 | archived gufo slot comment |
| Gemma 4 Heretic Q4_K_M (+ mmproj) | ~20–26 | bake-off RESULTS |
| ref2va-27b Q4_K_M + mmproj (32K) | ~19 | U48 RESULT |
| JoyCaption 8B Q8 + mmproj | ~9 | U47 brief |
| embed-small | <1 | llama-swap.yaml |

Consequences:

- A gufo-hosted resident Flash-Next leaves almost no room. The small group must unload on idle (D10), and
  Gemma or the 27B swap with each other.
- Halogen leaves about 30 GiB. That may fit the small group, but it has never been tested together
  (audit I7).
- **gufo 0.35.0 reserves memory for a full context per session** (`--sessions` × `--context`). Pooled
  sessions exist only on gufo's main branch (PR #1258, after 0.35.0). So on 0.35.0, size it as, e.g.,
  4 × 64K or 2 × 131K. Halogen pools its KV across slots (default: two 262K or four 131K conversations).
- Hermes side tasks (title, compression) can evict a single-slot server's prompt cache (Hermes issue
  #155717). The resident model needs ≥2 slots, or those side tasks are turned off or routed elsewhere.
- P0.7 measures the chosen combination before cutover.

## 5. Phases and packets

Each packet lists its scope, its check, and its stop trigger. **Y** marks a step that needs Derrick's yes at
the time (D13).

### Phase 0 — Measure (decides D6). Read-only for production; uses bake-off ports and keys.

| ID | Packet | Check (pass = all) | Stop trigger |
|---|---|---|---|
Every candidate runs the **same check set** ("the P0 checks"):

- Loads, with load time recorded.
- U26 refusal probes: comply 3/3.
- 20-call tool test (simple, parallel, after a long tool result, thinking on): ≤2 leaks.
- Tool-call IDs intact (gufo issue #780 was a community uncensored quant that broke them).
- 3 frozen Forge tasks pass.
- U6 18K fixture speed recorded.

| ID | Packet | Pass | Stop trigger |
|---|---|---|---|
| P0.0 | Confirm with Max what the in-flight looping fix already changed. Record the current live llama-swap.yaml, pi settings and AGENTS.md hashes in Gitea. | Snapshot committed; diff vs this repo's snapshot listed. | Live state cannot be committed (B4 unresolved) → do P1.1 first. |
| P0.1 **Y** | **Uncensored Swift on Halogen.** Upgrade a bake-off Halogen to 0.20.7. Test the published Swift abliterated/heretic `.hgn` conversions (`Quat3rnion/halogen-swift1.5-qwen3.8-flash-next-v2-abliterated`, then `johnlockejrr` Swift heretic HGN). Both say "load test TODO". | P0 checks. | Neither loads or both refuse. |
| P0.2 **Y** | **Uncensored stock Flash-Next on stock gufo 0.35.0.** `NeosQ/Qwen3.8-Flash-Next-Uncensored-UD-Q4_K_XL` (also loads on Halogen) or `SenseiHans/...-Uncensored-Q4_K_XL-Gufo`. | P0 checks. | Load fails, or tool-call IDs change (#780). |
| P0.3 **Y** | **Swift on stock gufo 0.35.0 (censored speed baseline).** `ethanwtodd/Swift-1.5-Qwen3.8-Flash-Next-Q4_K_XL-GGUF` (111.3 GB, tested on gufo). | P0 checks; refusal result recorded (expected to refuse). | — (informs G0 and the PR #1036 watch item) |
| P0.4 **Y** *(optional)* | **Uncensored Swift on gufo via the `dymoo/gufo-flash-next` fork:** Orca adapter on the ethanwtodd Swift file. The fork has 1 commit and 0 stars, and the adapter was qualified only on base Flash-Next. Building it needs orcarouter's gated BF16 weights and an HF token. | P0 checks. | Adapter will not build, or does not change refusals on Swift. |
| P0.5 **Y** | **Gemma 4 Heretic on gufo 0.35.0:** build `franzmoca/gemma4-gufo-extension` (needs extension API ≥0.3.20 = gufo 0.35.0; source already on the X3) and load Heretic Q4_K_M + mmproj. | Loads; write1/write2 pass; vision 4/4; refusal probes comply; tools 3/3. | Fails → Gemma stays on llama.cpp; not a plan stop. |
| P0.6 | **Baseline:** Halogen abliterated Flash-Next (the existing `flash-next-uncensored` slot) on the 3 Forge tasks and the 20-call tool test. | Results recorded with the same harness and samplers. | — |
| P0.7 **Y** | **Everything-loaded memory test** (audit I7): the leading candidate at its target sessions and context, plus the small group, plus one request each. | GTT used, MemAvailable, and any OOM or 503 recorded; ≥8 GiB headroom. | OOM or <8 GiB → fewer sessions or less context, or small-group TTL; re-test. |
| **G0** | **Gate:** choose `flash-next-resident`. Must pass the P0 checks. | Order of preference: (1) uncensored Swift (P0.1 or P0.4); (2) the faster of P0.2 and P0.6 on Forge wall time, then on tool errors. | No candidate passes → stop; Derrick decides. |

**Watch item:** gufo PR #1036 (`--projection-vector`, in llama.cpp control-vector format) is open, and the
maintainer has said he wants it. Once it merges, re-test Swift (P0.3 file) on stock gufo with a refusal
projection vector. That is the same mechanism Strata uses for Swift on the AlienPC.

Shared fixtures (reuse, do not invent): the U6 18K fixture, the U26 refusal probes (benign_sysadmin,
adult_fiction, explicit_adult), write1/write2, the vision card, and Gate 0's 20-call tool test from
`coding-harness-research-20261115.md`. Forge tasks are frozen copies at a pinned commit, never the live tree.

### Phase 1 — Stop the loops and make the X3 restorable. Coordinate with the in-flight fix first (P0.0).

| ID | Packet (audit ref) | Check | Stop trigger |
|---|---|---|---|
| P1.1 | **B4:** commit the X3 live tree to Gitea by path. Convert paths to `/home/evo`. Add `agent-shared/extensions`. | A fresh clone dry-starts Forge with all skills. | Secrets in the diff → stop; rotate per existing rule. |
| P1.2 | **B3:** Ralph GPU gate uses an X3-only lock with `flock -n` (as `queue-remote.sh` does). | 2-item smoke loop completes; no 1-hour waits. | — |
| P1.3 | **I2:** Ralph backpressure. Clear stale `fix_plan.md` items before each loop. Every pass runs a skill-load smoke test and a `git diff --stat` file cap, and denies edits to skills/AGENTS.md. One worktree per loop. | Seeded stale item is refused. A planted 30-file rewrite is rejected by the cap. | — |
| P1.4 | **I3:** mark the 6 known failing tests `xfail` with reasons. | Suite is green; a new failure fails the run. | — |
| P1.5 | **I8:** rewrite Forge, Render and community AGENTS.md as short Always / Ask / Never files. Remove contradictions (lease vs restart, "back up every file"). | One rule per topic. A contradiction scan across the files finds none. | — |
| P1.6 **Y** | **I9:** set subagent model defaults per pane to the resident alias (no Gemma default outside Render). Upgrade pi-subagents to ≥0.88.1 with explicit context inheritance. | A subagent spawned from Forge does not change the loaded model. | — |
| P1.7 **Y** | **B1:** agy runs as `evo` (no sudo) in a per-job worktree with a wall-clock timeout. Max does sudo steps after a yes. | A test agy job cannot sudo and times out as configured. | — |
| P1.8 **Y** | **B2:** cut one leg of the "lethal trifecta" (untrusted input + private data + a way to send data out). Default: split web tools and vault/Gitea tools into separate pi sessions. Uncensored models remove the model's own refusal backstop, so this is required, not optional. | The web session cannot reach vault tools. The ops session has no web tools. | Derrick prefers approval prompts instead → record the decision and implement ask rules. |
| P1.9 | **Loop limits** on every X3 agent (Forge, Render, Ralph, Hermes-started pi): identical-tool-call guard (≤3), per-job iteration cap, wall-clock timeout, and an explicit `STUCK` exit that writes a handoff note. Verify the existing `loop-guard` on the X3. | A seeded impossible task ends in `STUCK` within the limits and leaves a note. | — |

### Phase 2 — X3 model serving cutover (after G0)

| ID | Packet | Check | Stop trigger |
|---|---|---|---|
| P2.1 **Y** | **llama-swap.yaml:**<br>• `flash-next-resident` in a group with `persistent: true`, `swap: false`, `exclusive: false`, `ttl: 0`.<br>• Gemma and qwen27b in the swap group; small group with idle TTLs.<br>• Old Flash-Next slots archived as rollback.<br>• A unique podman `--name` per slot (MF-08 lesson).<br>• Aliases use `useModelName` or extra `--served-model-name`, never `setParamsByID` on `model` (llama-swap #1355; the maintainer confirmed this).<br>• gufo slots: health check `/ready`, a raised `healthCheckTimeout` (gufo #957: `GET /` returns 404).<br>• If Halogen stays: upgrade to 0.20.7 (0.20.6 fixed replies computed from another conversation's context).<br>• Back up and commit (etckeeper) before restart. | `llama-swap -validate` passes. Pool test 4/4. Refusal probes comply. Gemma vision 4/4. A Gemma request does not evict the resident model. | Any check fails → restore the backup yaml and restart. |
| P2.2 **Y** | **Callers:** pi `models.json` and settings for Forge, Render and Ralph point at the new names. One API key per caller. Hermes gets its own key (typed by Derrick). | Each caller reaches only its models. The rate proxy logs show no prompt text. | — |
| P2.3 | **Supervision:**<br>• Engines restart on crash (`Restart=on-failure`).<br>• gufo exits with status 75 on `device_lost`; `--stall-timeout-ms 120000` turns hangs into the same exit.<br>• If gufo refuses to load after a cold boot (gufo #1198, still open in 0.35.0), use `--cache-ram-bytes off`, or boot with `kho=off`. | A killed engine is back within 30 s and llama-swap recovers. | — |

### Phase 3 — Hermes on the X3

| ID | Packet | Check | Stop trigger |
|---|---|---|---|
| P3.1 **Y** | **Install Hermes Agent** as user `evo`:<br>• `hermes gateway install` (systemd user service), plus `loginctl enable-linger evo`. Linger is a sudo step; Max runs it after a yes.<br>• Provider: `llamacpp`/custom `base_url` = llama-swap, with Hermes's own key.<br>• Pin `context_length`, ≥64K (Hermes #155853 misdetects llama.cpp contexts).<br>• `reasoning_effort` per request; thinking via `chat_template_kwargs`. | Hermes answers through the resident model. Survives a reboot. | Hermes will not start under 64K → raise the resident context or stop. |
| P3.2 **Y** | **Access:**<br>• API server on `127.0.0.1:8642` with `API_SERVER_KEY` (it grants terminal access, so the key is mandatory).<br>• Open WebUI connects via Admin → Connections (container: host network or `host-gateway`).<br>• Only Open WebUI is published tailnet-only with Tailscale Serve, under the existing ACL gate. No Funnel.<br>• The dashboard stays loopback unless a dashboard auth provider is set; Tailscale Serve counts as non-loopback. | A phone browser on the tailnet reaches Open WebUI → Hermes. A device off the tailnet cannot. Port 8642 is not reachable from the tailnet. | ACL preview not approved → stop (existing ACL gate). |
| P3.3 | **Model routing** (no built-in content router; see section 3):<br>• main = resident; `auxiliary.vision` = Gemma; review slot = qwen27b.<br>• Subagents use a model map (`delegation.backend: model_map`; prompt writing → Gemma, review → 27B, captions → JoyCaption, ref2va → ref2va-27b).<br>• Title/compression side tasks off, or on a non-resident model, so they don't evict the resident prompt cache (#155717).<br>• Optional: per-model Hermes profiles show up as separate models in Open WebUI for manual choice. | 10 sample prompts route to the expected model. No unexpected swaps of the resident model. | — |
| P3.4 | **`pi-code` skill**, modeled on Hermes's bundled `claude-code` skill:<br>• The terminal tool runs a wrapper script (background + notify for long jobs).<br>• The wrapper writes a task brief, checks AlienPC availability (P4.1), creates a worktree branch, runs `pi -p` with a wall-clock timeout and iteration cap on the chosen machine, and returns the diff summary and test result.<br>• Hermes `child_timeout_seconds` > 0, `max_spawn_depth` 1. | Both machine paths exercised. A timeout returns `STUCK` with a note. | — |
| P3.5 | **Safety:**<br>• `unattended_mode: deny` stays on (this covers Open WebUI sessions).<br>• `command_allowlist` contains only the `pi-code` wrapper and read-only status commands.<br>• `approvals.deny` patterns for sudo, ssh-keygen, and curl to non-tailnet hosts.<br>• `HERMES_WRITE_SAFE_ROOT` = Hermes home + worktrees root; `redact_secrets` on; no vault access.<br>• `agent.max_turns` set: Hermes's loop guard only warns in api_server runs (Hermes issues #151401, #142677 show tool-call loops on local models).<br>• Untrusted web content only in sessions without secrets (same rule as P1.8). | The planted prompt-injection fixture (`u9b`) does not trigger an outbound send. A disallowed command is denied. A runaway session stops at `max_turns`. | — |
| P3.6 | **GrokBot:** a manual "ask Grok" path (Derrick-triggered) that hands a brief to Max through the existing handoff inbox. No automatic escalation (D3). | A brief appears in the inbox only when Derrick asks. | — |

### Phase 4 — AlienPC coding worker and reviewer (render first)

| ID | Packet | Check | Stop trigger |
|---|---|---|---|
| P4.0 **Y** | **Remote-job path to the AlienPC.** None exists today: U47 found no SSH, share or Taildrop path, and Hermes's SSH backend expects bash. Default: a small authenticated job endpoint on the AlienPC (preferably inside Switchyard, which already owns the GPU state, leases and queue) published tailnet-only to the X3's tag. Alternative: OpenSSH Server on Windows with a forced-command wrapper. Decision OD5. | Only the X3 can reach it. It accepts only "status", "start pi job on branch X", "request stop" and "fetch result". | ACL preview not approved → stop. |
| P4.1 **Y** | **Availability check** the X3 can call: render lock free, no lease held, Swift slot loadable. Read-only, through P4.0. | Correct answer for idle, rendering and leased states. | — |
| P4.2 **Y** | **Render-priority handoff (D9):** before a render takes the GPU, the render launcher signals the running pi job. pi finishes its current step, commits work in progress to its branch, pushes, writes a handoff note, and exits. Hermes resumes the job on the X3 from that branch. | During a test job, a render request produces a pushed branch plus a note within one step. The X3 continues and finishes. The render starts without waiting for the whole job. | Strata or ComfyUI cannot be gated → render waits at most one step; record it. |
| P4.3 | **Reviewer mode:** Swift on the AlienPC reviews X3 diffs read-only (different fine-tune = independent review) when render is idle. | A review of a seeded bug catches it. | — |
| P4.4 | **Config drift note:** Switchyard `director.live.yaml` says `coding_huihui27b`; pi says Swift. Record which is live; do not change the Strata setup (D8). | The note is in Gitea. | — |

### Phase 5 — Acceptance

| ID | Packet | Check |
|---|---|---|
| P5.1 | Run AC-OP (section 1) end to end from a phone browser. | All four results as described. |
| P5.2 | Loop test: a seeded impossible coding task through Hermes. | Ends in `STUCK` within the limits on both machines. |
| P5.3 | Rollback drill: restore the previous llama-swap.yaml and resident model, then restore again. | Both directions work within 5 minutes. |

### Phase 6 — eGPU (future, out of scope; design notes only)

- **Separate backend.** When the eGPU arrives, it runs its own engine instance behind llama-swap with its
  own model names. Neither gufo nor Halogen uses a second GPU. Use llama.cpp, or the
  `sixvolts/llama-halo-hybrid` fork (R9700 marked production).
- **First candidates.** Gemma (render prompts and vision) or the 27B reviewer, so they stop swapping with
  each other on the X3. No agent or Hermes route changes beyond a model name.
- **Memory pools.** llama-swap's `capacity` router can model gpu0/gpu1 memory pools.
- **Pin engines to the iGPU.** Halogen hides extra GPUs automatically (reported on an EVO-X3 with a
  7900 XT over OCuLink). gufo crashed at load with a second GPU present (gufo #696). Pin gufo with
  `HIP_VISIBLE_DEVICES` / `ROCR_VISIBLE_DEVICES` and re-test it.
- **Card support.** The R9700 is documented working; if the card drops off the bus at idle, turn ASPM L1
  off on its links. The Arc Pro B70 has no coverage in these projects.

## 6. Acceptance trace

| AC | Requirement | Surface | Check | Evidence goes to |
|---|---|---|---|---|
| AC-OP | Four-message operator test | Hermes, llama-swap, pi, AlienPC gate | P5.1 | Issue comment + Gitea record |
| AC-1 | Uncensored daily driver, no swap for chat | flash-next-resident | P0.1–P0.7, G0, P2.1 | Phase 0 results file |
| AC-2 | Coding on Swift; AlienPC first when free | `pi-code` skill, P4.0, P4.1 | P3.4, P4.1 | Issue comment |
| AC-3 | Render priority: save, then hand off | Render launcher + pi + Hermes | P4.2 | Issue comment |
| AC-4 | No loops past limits | Loop limits on all agents | P1.2, P1.3, P1.9, P5.2 | Issue comment |
| AC-5 | X3 restorable from Gitea | Gitea branches | P1.1 | Fresh-clone record |
| AC-6 | Browser access over Tailscale only | Tailscale Serve, ACL | P3.2 | ACL preview + test |
| AC-7 | Model per job | Hermes routing | P3.3 | Routing test log |
| AC-8 | eGPU not blocked | llama-swap names only | Design review at P2.1 | This plan |

## 7. Risks

| Risk | Mitigation |
|---|---|
| Uncensored models plus agent tools remove the model's refusal backstop against injected instructions. | P1.8 and P3.5 are required, not optional. |
| gufo crashes on long jobs or OOM-kills subagent sessions (community reports, issues #1157/#1198). | P2.3 supervision; P0.5 headroom; §9 R3 version check. |
| A community fork (dymoo) or extension (franzmoca) stops being maintained. | Pin by digest or commit. Halogen abliterated stays as rollback. |
| Halogen is closed source (EULA). | Accepted (D5). gufo slots stay available as rollback. |
| Swapping two ~110 GB Flash-Next files is slow (both cannot stay in the file cache). | D6: exactly one resident Flash-Next; never route chat and coding to different Flash-Next variants on the X3. |
| Swift scored lower on hard math in the community benchmark. | Hermes can route math-heavy requests to the resident model with higher thinking effort; if Swift is resident, accept it or use GrokBot (manual). |
| The in-flight looping fix and this plan edit the same files. | P0.0 first; one writer per file; Max sequences. |
| Community uncensored quants can break tool-call IDs (gufo #780). | Tool-call ID check in every P0 run. |
| gufo #1232 (raw `<tool_call>` text when `tool_choice: "none"`) is still open in 0.35.0. | The P0 tool test covers it. Halogen fixed the same leak in 0.20.4. |
| Hermes loops on local models (open issues #151401, #142677, #151373); its loop guard only warns in API-server runs. | `agent.max_turns`, pi wrapper limits, `STUCK` exit (P1.9, P3.4, P3.5). |
| Swift's license: free up to US$1M gross revenue; commercial use above that needs a Swift Enterprise License. | Personal use is within the free tier; re-check if the use changes. |
| The new AlienPC job endpoint is a new remote-execution surface. | Fixed verbs only, tailnet-only to the X3 tag, under the ACL gate (P4.0). |

## 8. Open decisions (Derrick)

| ID | Decision | When |
|---|---|---|
| OD1 | Resident Flash-Next (G0 result) | After Phase 0 |
| OD2 | B2 tool split vs approval prompts (default: split) | P1.8 |
| OD3 | Open WebUI or the Hermes dashboard as the main phone UI (both are planned) | P3.2 |
| OD4 | Which eGPU, and what moves to it first | When purchased |
| OD5 | AlienPC remote-job path: Switchyard job endpoint (default) or OpenSSH with a forced command | P4.0 |
| OD6 | Run the optional dymoo-fork test (P0.4)? Needs an HF token for orcarouter's gated BF16 weights and a large download | Before P0.4 |

## 9. Research findings used by this plan (Copilot, 2026-11-18; all fetched that day)

**R1 — Swift and uncensored variants**

- **Swift-1.5 GGUFs** (`ukisai/Swift-1.5-Qwen3.8-Flash-Next-GGUF`): Q8_0 is 188.3 GB, IQ4_XS 97.7 GB, built in
  bartowski's layout. The imatrix is in UkisAI's GSQ-RCO repo.
- **A ready-made Swift requant in gufo's layout** exists: `ethanwtodd/Swift-1.5-Qwen3.8-Flash-Next-Q4_K_XL-GGUF`
  (111.3 GB, requantize script included, tested on gufo). It is censored.
- **Uncensored Swift on stock gufo:** none found. `empyrealworks/Swift-1.5-Flash-Next-Abliterated-Gufo-GGUF`
  stores some expert weights as Q4_1, and gufo closed Q4_1 support as "not planned" (#906).
- **Why your Nov 15 test failed:** stock gufo refuses IQ-quantized Flash-Next experts since PR #1041 ("No text
  provider found"). `storm1er/flash-next-iq-gufo-extension` adds UD-IQ4_XS.
- **Uncensored stock Flash-Next in gufo's layout:** `NeosQ/Qwen3.8-Flash-Next-Uncensored-UD-Q4_K_XL` ("one set of
  files feeds both Halogen and Gufo") and `SenseiHans/Qwen3.8-Flash-Next-Uncensored-Q4_K_XL-Gufo`.
- **Halogen 0.20.7** loads bartowski-layout IQ4_XS and refuses Q4_1. It will not build refusal removal into the
  engine (#239), but abliterated models are allowed. Swift abliterated/heretic `.hgn` repos exist
  (Quat3rnion, johnlockejrr) but none has been load-tested.
- **`dymoo/gufo-flash-next`:** 1 commit, 0 stars, MIT. Its Orca adapter projects out the refusal direction,
  qualified on base Flash-Next only. Building it needs orcarouter's gated BF16 weights.
- **gufo PR #1036** (`--projection-vector`, control-vector format) is open; the maintainer wants it.
- **Swift license:** free up to US$1M revenue.

**R2 — Hermes Agent** (docs `llms-full.txt` and GitHub issues)

- **API server:** default `127.0.0.1:8642`. `API_SERVER_KEY` is required and grants terminal access.
- **Open WebUI** connects to the API server. The dashboard (port 9119) needs an auth provider for any
  non-loopback bind, including Tailscale Serve.
- **Model routing:** no content-based router. Use the main model, side-task slots (vision, review,
  compression, title), the delegation model map, or per-model profiles. The API server ignores a requested
  model unless `direct_model_requests: true`.
- **Coding:** no `pi` skill exists. The bundled `claude-code` skill shows the pattern: terminal tool with
  workdir and timeout, background + notify.
- **Unattended mode:** API-server sessions are unattended. `unattended_mode: deny` refuses dangerous commands
  without a prompt, and `command_allowlist` applies everywhere. Hard loop stops do not apply to API-server
  runs; set `agent.max_turns`.
- **Install:** `hermes gateway install` + linger. Memory caps: MEMORY.md 2,200 characters, USER.md 1,375.
- **Open local-model issues:** loops #151401, #142677, #151373; context misdetection #155853; side tasks
  evicting the prompt cache #155717.

**R3 — Engines and eGPU**

- **gufo 0.35.0** (2026-11-17): #1232 and #1198 are still open; #1157 was fixed in 0.34.0. Each session still
  reserves a full context; pooled sessions are only on main (#1258). The Gemma extension needs 0.35.0.
- **Fine-tunes on gufo** load only in Unsloth's tensor layout (PR #293). The Ref2VA rewriter ships plain
  Q4_K_M/Q5_K_M, so it stays on llama.cpp. Whether DFlash2 speeds up fine-tunes: not found.
- **llama-swap #1355:** use `useModelName` (maintainer, 11-18). Resident model:
  `persistent: true` + `ttl: 0`. gufo health check: `/ready`.
- **Halogen 0.20.4–0.20.7:** the `tool_choice` leak is fixed (0.20.4); a cross-conversation context bug is
  fixed (0.20.6); concurrency mode is the default except for GGUF files.
- **eGPU:** see Phase 6.

## 10. Evidence used (retrieved before planning)

| Source | What it gave | Disposition |
|---|---|---|
| `x3-bakeoffs/host-evo-x3/bakeoff/RESULTS.md` (Nov 15) | Engine speeds, load times, memory | Applied (§4, P0 fixtures) |
| `x3-pi-config/config/llama-swap.yaml` (U26 comment) | Halogen abliterated Flash-Next passes refusal, tools, Forge task; 25 s load; 88.9 GiB | Applied (G0 fallback) |
| `bakeoff/results/u6-uncens-fn-gufo.engine.log` (Nov 15) | Upstream gufo refuses a non-UD layout ("No text provider") | Applied (P0.1–P0.3 design) |
| `records/2026-11-16-forge-audit.md` | Looping causes B1–B4, I2, I3, I7, I8, I9 | Applied (Phase 1) |
| `records/U47-*`, `U48-RESULT.md` | JoyCaption and ref2va-27b slots, memory, speeds | Applied (§4) |
| `records/coding-harness-research-20261115.md` | pi first; 20-call Gate 0 tool test | Applied (P0 checks) |
| `alienpc-community/briefs/agy_audit_20261025_report.md` | Swift is uncensored only with the Strata steering vector (0/15 vs 15/15 refusals) | Applied (D4 → P0.2/P0.3) |
| `fleet-brain-staging/ce/plans/2026-10-10-1130-feat-hermes-local-agent-plan.md` | Hermes dropped on the AlienPC for prompt cost; owned approvals and memory budget | Superseded model choice; safety ideas reused (P3.5) |
| Reddit r/StrixHalo, r/LocalLLaMA, r/LocalLLM (Sep–Oct 2026, PullPush archive) | Mixed engines behind llama-swap; Hermes on gufo; one shared Flash-Next for many agents | Applied (D5, D6) |
| Reddit benchmark by deepu105 (Swift 1.5 vs Qwen on Halogen, gufo, llama.cpp) | gufo + Swift requant fastest for Pi coding (24 min, 56k tokens); upstream gufo cannot load Swift's own 4-bit files | Applied (P0.3) |
| Copilot research agents, 2026-11-18 (section 9) | Published Swift and uncensored files; gufo 0.35.0 and Halogen 0.20.7 status; Hermes access, routing and safety; eGPU support | Applied (Phases 0, 2, 3, 4, 6) |

## 11. Rollback

- Every llama-swap edit keeps a timestamped backup and an etckeeper commit. Restore = copy back + restart.
- Old Flash-Next slots stay archived, not deleted. Weights are never deleted in this plan.
- Hermes can be stopped with `systemctl --user stop`. Open WebUI keeps working against llama-swap directly.
- The AlienPC Strata setup is not changed (D8). Only the availability check and the handoff signal are added.
