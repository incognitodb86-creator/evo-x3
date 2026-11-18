# EVO-X3 + AlienPC agent setup plan: Hermes, pi, uncensored models, mixed engines (v2)

- **Status:** Active (v2 — audited & updated with chat naming and filesystem hygiene; execution not started)
- **Written:** 2026-11-18 by Copilot (planning only; no machine was touched)
- **Owner:** Derrick (every live change needs Derrick's yes at the time)
- **Executor:** Max (GrokBot) via agy or Forge on the X3; Copilot only drafted this
- **Tracking issue:** https://github.com/incognitodb86-creator/evo-x3/issues/1 (checklist mirrors section 5)
- **Source of truth for machine state:** Gitea `derrick/evo-x3`; this GitHub repo is a snapshot

## 1. Goal and operator acceptance

**Goal.** Derrick talks to one local assistant, **Hermes** (`Hermes-X3` / `Hermes-Ops-X3`), from a browser
over Tailscale. Every chat, pane, and Open WebUI entry is explicitly named with its machine (`-X3` or
`-AlienPC`), and both machines follow a clean, uncluttered directory layout without inline `.bak-*` sprawl.
Hermes answers everyday requests on an uncensored default Flash-Next model (`flash-next-default`), invokes
pipeline-backed tools for specialized models (Gemma, Ref2VA, JoyCaption, 27B), and sends coding to **pi**:
running **Swift** on `Forge-AlienPC` when AlienPC's GPU is free of render work, otherwise running the winning
uncensored Flash-Next (Swift if one passes Phase 0, else uncensored stock Flash-Next) on `Forge-Ops-X3`.
Agents stop looping. GrokBot (Max and the other bots) keeps running and is used when Derrick chooses.

**Operator acceptance (AC-OP).** From a phone browser over Tailscale (`https://evo-x3-1.tailf242b2.ts.net:8443`),
Derrick sends four requests:

1. In `Hermes-X3`: a general question.
2. In `Hermes-X3`: a request that a stock model would refuse (adult or explicit creative text).
3. In `Hermes-Ops-X3`: a coding task while AlienPC render is idle (and checks progress via `pi-status`).
4. In `Hermes-Ops-X3`: a coding task while AlienPC render is busy — and separately triggers a render while
   task 3 is actively running on AlienPC.

He sees:

- Chat/model names everywhere clearly show `-X3` vs `-AlienPC` (no ambiguous bare `forge` or `render`).
- 1 and 2 are answered with no refusal and no model swap while `flash-next-default` is active.
- 3 dispatches to `Forge-AlienPC` (Swift + Strata) in an isolated worktree.
- 4 dispatches to `Forge-Ops-X3` (`flash-next-default`) in an isolated worktree.
- When a render is requested during task 3, the render gate signals the AlienPC job wrapper **before**
  touching `/upstream/comfyui_auto` (so `llama-swap` does not kill Strata mid-step); the wrapper finishes
  the bounded step, commits and pushes WIP to its git branch, returns the handoff state to the X3, and the X3
  resumes and finishes the branch while ComfyUI starts the render.
- Hermes stays responsive throughout, background `tag_runner` does not swap-thrash `flash-next-default`, and
  nothing loops past the configured limits.

**Cheapest falsifying check.** Phase 0 load, refusal, concurrency, and `tool_choice: "none"` tests (after
archiving `/srv/bakeoff` to QNAP so `/` keeps `>= 100 GiB` free). If no uncensored Flash-Next variant passes
on the X3, stop and return to Derrick before any cutover.

## 2. Ratified decisions (Derrick, 2026-11-18)

| ID | Decision |
|---|---|
| D1 | **pi** is the only coding harness on both machines. OpenCode is out. |
| D2 | **Hermes Agent** runs always on, on the X3, as Derrick's local assistant. It hands coding to pi. |
| D3 | **GrokBot** (Max etc.) keeps running in parallel. Escalation to GrokBot is manual (Derrick asks). |
| D4 | **Uncensored by default** for every user-facing/chat/coding/review model. Stock censored `qwen27b` is either replaced with an uncensored 27B UD quant or excluded from adult/parody-adjacent reviews; `ref2va-27b` is scoped strictly to camera/motion Ref2VA structured rewrites. |
| D5 | **X3 engines:** Halogen, gufo and llama.cpp behind llama-swap. Each model runs on the engine where it passes the load, refusal, concurrency, and tool-call tests. Halogen (closed source) is acceptable. Community gufo forks are acceptable if they pass. |
| D6 | **One default Flash-Next (`flash-next-default`) on the X3** serves both Hermes and X3 coding, so chat and X3 coding never swap against each other. It lives in the exclusive `main` group with a 24 h TTL (`86400`): calling Gemma or 27B swaps cleanly without OOMing the 120 GiB GTT ceiling, and `flash-next-default` reloads in ~22–25 s afterward. Phase 0 chooses an uncensored Swift if one passes, otherwise the best uncensored stock Flash-Next (`gufo` NeosQ/SenseiHans or `Halogen` 0.20.7 abliterated). |
| D7 | **Models per job:** `flash-next-default` = daily driver + X3 coding; AlienPC Swift (`coding_swift15_iq3s_esp`) = primary coding/review when render is idle; `gemma4-heretic` = prompt writing (`render_writer_pipeline.py`) and vision; `ref2va-27b` = H3 Ref2VA prompt rewriting; `joycaption` = captions and tags; `embed-small` = embeddings; `qwen27b` = dense second opinion (subject to D4). |
| D8 | **AlienPC keeps its current live `C:\AI\director` Strata setup**: Swift IQ3_S with the ESP steering vector (`coding_swift15_iq3s_esp`) and Gemma on PolyStrata behind `llama-swap`. Render always comes first. |
| D9 | **Render priority (preempt before swap):** before X3 `queue-remote.sh` or AlienPC `comfy-guarded.ps1` / `gpu_lock_gate.py` touches `/upstream/comfyui_auto`, it calls the AlienPC job runner's `preempt` endpoint. The job wrapper lets the current turn finish (bounded grace window), commits and pushes WIP on the job branch, returns `{branch, sha, summary}` to the X3 to continue, and then releases the GPU to ComfyUI. |
| D10 | **Small group & background tagger:** `embed-small` stays resident (`<1 GiB`); `joycaption` (`~9 GiB`) and `ref2va-27b` (`~19.1 GiB`) use short idle TTLs (`300–600 s`, or `ref2va-27b` joins `main` if `flash-next-default` runs on gufo at `~110 GiB`). Background PixlStash `tag_runner` either moves to `joycaption` (if U47 passes) or runs only in idle batch windows so it never swap-thrashes `flash-next-default`. |
| D11 | **Access & live Tailscale Serve port map:** X3 `:443` stays `llama-swap` (`127.0.0.1:8080`, `apiKeys`) so remote `pi`/box callers keep working; X3 `:8443` stays `Open WebUI` (`127.0.0.1:3000`, `ENABLE_SIGNUP=false`) connected to Hermes API (`127.0.0.1:8642`) plus direct `llama-swap` fallback; X3 `:8444` stays `pi-mobile` hub. No Funnel anywhere. |
| D12 | **Large downloads are allowed**, each with a yes at the time and gated on `df -BG /srv >= 100 GiB` free (stage one candidate at a time; archive cold weights to QNAP). |
| D13 | **Every live change needs Derrick's yes at that moment:** llama-swap edits, restarts, installs, QNAP moves/deletes, API keys, Tailscale ACLs, AlienPC changes. |
| D14 | **eGPU:** not purchased or installed in this plan, but coming soon. Nothing in the design may block adding it as another llama-swap backend. |
| D15 | **Explicit `<Role>-<Host>` naming everywhere:** every Open WebUI entry, `herdr` pane, `pi-mobile` session, `PI_CODING_AGENT_DIR`, and system-prompt identity line carries `-X3` or `-AlienPC` (and `-Web` / `-Ops` where tool-split applies). Standby duplicate panes on AlienPC (`Render-AlienPC`, `Sydney-AlienPC`) do not auto-start once X3 equivalents are live. |
| D16 | **Filesystem & git hygiene (archive-first, zero inline `.bak-*`):** one canonical workspace root per machine (`/home/evo/AI` on X3, `C:\AI` on AlienPC), isolated ephemeral `worktrees/<job-id>` and gitignored `_runs/` folders, cold bake-off/retired weights archived to `/mnt/qnap/ai-archive/` (SHA256-verified before local removal), no inline `*.bak-*` files beside live configs/code, and `<200`-char repo paths with raw scraped dumps gitignored. |

**Superseded by these decisions** (kept for history, not deleted):

- U9/R5 "AlienPC render-only" and the Nov 16 Forge audit item I10 "archive the AlienPC Forge/LLM slots".
  Replaced by D8/D9/D15 (`Forge-AlienPC` stays active for Swift coding/review when render is idle; only
  duplicate interactive `Render-AlienPC`/`Sydney-AlienPC` auto-launch panes move to `_standby`).
- U34 (Nov 16) "Flash-Next on Halogen stock, gufo slot archived". Replaced by D5/D6; the outcome is decided
  by Phase 0.
- The Oct 10 local-agent plan's model choice (Huihui-27B on the AlienPC as the whole agent). Replaced by
  D2/D6/D8. Its safety ideas (owned fail-closed approvals, memory byte budget) are reused.

## 3. Target architecture, naming, and filesystem layout

```
Phone / laptop browser ──Tailscale Serve (tailnet only)
   ├─ :8443 ──► X3 Open WebUI (127.0.0.1:3000, ENABLE_SIGNUP=false)
   │               ├─► Hermes-X3       (127.0.0.1:8642, chat + web/research, NO shell/code)
   │               ├─► Hermes-Ops-X3   (127.0.0.1:8643, pi-code + pi-status, NO untrusted web)
   │               └─► Direct fallback (127.0.0.1:8080: Raw-FlashNext-X3, Raw-Gemma-X3, Raw-Qwen27B-X3)
   ├─ :8444 ──► X3 pi-mobile hub (panes: Forge-Web-X3, Forge-Ops-X3, Render-X3, Sydney-X3)
   └─ :443  ──► X3 llama-swap (127.0.0.1:8080, per-caller apiKeys for Forge-AlienPC / box / laptop)

X3 llama-swap (loopback 127.0.0.1:8080; unique internal port per model: 8081..8086)
  main group (swap: true, exclusive: true):
    flash-next-default :8081  [ttl 86400; Phase 0 winner: uncensored Swift OR uncensored Flash-Next]
    gemma4-heretic     :8082  [ttl 1800; gufo 0.35 + extension if P0.5 passes, else llama.cpp; Q8 vs Q4 per B4]
    qwen27b            :8084  [ttl 1800; gufo 0.35 + DFlash2; uncensored 27B UD or non-adult review per D4]
  small group (swap: false, persistent: true, exclusive: false):
    embed-small        :8083  [ttl 86400; <1 GiB, llama.cpp]
    joycaption         :8086  [ttl 300;   ~9 GiB, llama.cpp]
    ref2va-27b         :8085  [ttl 300;  ~19 GiB, llama.cpp — moves to main if G0 picks ~110 GiB gufo FN]
  rollback (archived yaml, not deleted): flash-next-halogen-stock, flash-next-gufo-stock

Hermes-Ops-X3 "pi-code" wrapper ──► check P4.1 (AlienPC C:\AI\director job gate)
   ├─ AlienPC GPU idle & lease free ──► Forge-AlienPC (pi -p on coding_swift15_iq3s_esp, C:\AI\worktrees\<job>)
   │       ▲ render requested (X3 queue-remote.sh OR AlienPC comfy-guarded.ps1 / gpu_lock_gate.py)
   │       └─ calls preempt BEFORE /upstream/comfyui_auto -> finish step -> git commit/push -> HTTP handoff
   └─ AlienPC busy (or preempted)   ──► Forge-Ops-X3  (pi -p in Podman/worktree sandbox on flash-next-default)
```

### 3.1 Chat, Pane, and Model Naming Standard (D15)

Today both machines use bare names (`forge`, `render`, `sydney`), making `herdr`, `pi-mobile`, and handoff
logs ambiguous. Every interactive surface is renamed to `<Role>-<Host>` (or `<Role>-<Mode>-<Host>`):

| Surface | New Name | Machine & Runtime Dir | Model & Role |
|---|---|---|---|
| Open WebUI (`:8443`) | `Hermes-X3` | X3 `~/.hermes-chat` (`:8642`) | `flash-next-default` — daily uncensored chat, memory, cron, web/deep research; **no** `pi-code` or arbitrary shell |
| Open WebUI (`:8443`) | `Hermes-Ops-X3` | X3 `~/.hermes-ops` (`:8643`) | `flash-next-default` — coding dispatch (`pi-code`, `pi-status`), pipeline skills (`render-write`, `ref2va-rewrite`, `caption-image`), Grok handoff; **no** untrusted web search/fetch |
| Open WebUI (`:8443`) | `Raw-FlashNext-X3`, `Raw-Gemma-X3`, `Raw-Qwen27B-X3` | X3 `llama-swap` (`:8080`) | Direct model chat fallback (still works if Hermes is stopped) |
| X3 `herdr` / `pi-mobile` (`:8444`) | `Forge-Web-X3` | X3 `~/.pi/panes/forge-web-x3` | `flash-next-default` — interactive pi with browser/SearXNG/fetch; **no** Vaultwarden/Gitea write tokens |
| X3 `herdr` / `pi-mobile` (`:8444`) | `Forge-Ops-X3` | X3 `~/.pi/panes/forge-ops-x3` | `flash-next-default` — interactive pi for repo/Gitea/ops; **no** untrusted web tools |
| X3 `herdr` / `pi-mobile` (`:8444`) | `Render-X3` | X3 `~/.pi/panes/render-x3` | `gemma4-heretic` — primary H3 prompt writer (`render_writer_pipeline.py`), queues remotely to AlienPC `:8446` |
| X3 `herdr` / `pi-mobile` (`:8444`) | `Sydney-X3` | X3 `~/.pi/panes/sydney-x3` | `gemma4-heretic` — started only after Derrick copies Sydney's private persona/memory files |
| AlienPC `herdr` / `pi-mobile` (`:8443`) | `Forge-AlienPC` | AlienPC `~\.pi\panes\forge-alienpc` | `coding_swift15_iq3s_esp` (Strata) — interactive/worker Swift coder & diff reviewer when render is idle |
| AlienPC `_standby` (not auto-started) | `Render-AlienPC`, `Sydney-AlienPC` | AlienPC `_standby\` | Disabled in `pi_herdr_at_logon.ps1` once `Render-X3` / `Sydney-X3` are live so prompts aren't written on two hosts |

Each pane's system prompt opens with a one-line identity banner (`Identity: <Name> on <hostname> (<cwd>)`) so
both Derrick and the model always know which machine they are on.

### 3.2 Filesystem & Repository Hygiene Standard (D16)

Current clutter comes from four root causes: (1) split X3 trees across `/home/derekboone` and `/home/evo`,
(2) `~475 GiB` of old bake-off/superseded weights and aborted backups left on `/`, (3) `AGENTS.md` telling
agents to create inline `.bak-*` files next to every edited file, and (4) run outputs, scraped HTML benchmark
pages (>260-char paths that break Windows git checkout), and orphan branches piled into one repo.

| Path | Canonical Purpose | Hygiene Rule |
|---|---|---|
| **X3 `/etc/evo-x3/`** | Root-owned `*.env` (`0600`) + `llama-swap.yaml` | Tracked by `etckeeper` git. **Zero inline `.bak-*` files**; pre-cutover snapshots go only in `/var/backups/evo-x3/<YYYYMMDD-unit>/`. |
| **X3 `/srv/models/<slot>/`** | Active production weights + 1 designated rollback slot + `SHA256SUMS` | Keep `>= 100 GiB` free on `/`. Stage at most one Phase 0 test candidate in `/srv/staging/` at a time. |
| **QNAP `/mnt/qnap/ai-archive/`** | Cold storage for `/srv/bakeoff` (`341 GiB`), retired weights, `~/rocm` (`9.9 GiB`), old raw bench dumps, 30+ day runs | Every move verifies `sha256sum -c` on QNAP before any local `rm`, gated on Derrick's **Y**. |
| **X3 `/home/evo/AI/`** | **Sole agent workspace root:** `forge/`, `render/`, `community/`, `sydney/`, `hermes/`, `fleet-brain/`, `locks/` | Retire duplicate launchers/configs under `/home/derekboone/evo-x3` (archive to QNAP; keep `~derekboone` strictly for human/Max sudo admin). |
| **X3 `/home/evo/AI/worktrees/<job-id>/`** | Ephemeral git worktrees for `pi-code`, `agy`, and Ralph loops | Removed automatically after branch push + merge/closeout; never left dirty across jobs. |
| **X3 `/home/evo/AI/_runs/`** | Gitignored render runs, Ralph pass logs, and `pi-code` job logs | Fix `render_writer_pipeline.py` relative-path bug (`U23` gap #11) so runs cannot land inside code repos; auto-archive >30 days to QNAP. |
| **AlienPC `C:\AI\director\`** | **Sole live AlienPC orchestration root:** `llama-swap.yaml`, `gpu_guard.ps1`, `gpu_lock_gate.py`, P4.0 job gate | Mark old `switchyard` (`D:\AI\vlm` `director.live.yaml`) `ARCHIVED-READONLY.md` so no agent edits the stale Oct config. |
| **AlienPC `C:\AI\worktrees\<job-id>\`** | Clean git worktrees for `Forge-AlienPC` worker/reviewer jobs | Isolated from `C:\Users\derek\forge`'s 61.5 GB `5slock`/PixlStash media folders. |
| **AlienPC `C:\AI\backups\<YYYYMMDD-unit>\`** | Out-of-band config backups | Sweep inline `AGENTS.md.bak-*` / `GEMINI.md.bak-*` / `*.bak-*` out of repo roots. |
| **Gitea & GitHub repos** | Restorable code, configs, and concise benchmark summaries | `.gitignore` `_archive/`, `_runs/`, `*.jsonl`, and raw scraped page dumps (`runs/*/pages/`); enforce `<200`-char relative paths so Windows clones succeed cleanly. Split `derrick/evo-x3` orphan branches into dedicated repos once Derrick creates them. |

**Rules that hold everywhere:**

- One writer per git branch/worktree. Work moves between machines only as a pushed git branch plus the P4.0
  structured HTTP handoff record (mirrored to `fleet-brain` handoff status when needed), never an unshared local folder.
- Hermes never edits code directly; `Hermes-Ops-X3` starts `pi -p` inside a bounded worktree/Podman sandbox
  with a wall-clock timeout and iteration cap, and reads back `pi-status` / final test output.
- Hermes has no built-in content classifier. Routing uses `Hermes-X3` / `Hermes-Ops-X3` profiles, deterministic
  pipeline skills (`pi-code`, `render-write`, `ref2va-rewrite`, `caption-image`), `auxiliary.vision`, and `/review`.
- Open WebUI sessions run in Hermes's *unattended* mode (`unattended_mode: deny`, warning-only loop detector)
  and request/response HTTP (no async push). Hard loop stops live in `agent.max_turns`, `command_allowlist`,
  and the `pi-code` wrapper (`P1.9`, `P3.4`, `P3.5`), with `pi-status` (plus optional `ntfy`) for long jobs.
- Every model is addressed by a `llama-swap` model name. An eGPU later becomes one more backend with its own
  names (D14).

## 4. Memory & disk budget (X3: 120 GiB GTT, ~685 GiB free disk before cleanup) — confirmed by P0.0b & P0.7

| Slot | Engine | Measured / Approx. GTT | Source | Group & Residency |
|---|---|---|---|---|
| Halogen abliterated Flash-Next (262K KV pool, 4 slots) | Halogen 0.20.7 | `88.9 GiB` engine total (`+47.7 GiB` mmap n-gram file) | `llama-swap.yaml` U26 | `main` (exclusive, `ttl: 86400`) |
| gufo Flash-Next UD-Q4_K_XL layout (stock, NeosQ, or Swift requant) | gufo 0.35.0 | `~108–113 GiB` (at `1 × 262K` or `4 × 64K` / `2 × 131K`) | archived gufo yaml | `main` (exclusive, `ttl: 86400`) |
| `gemma4-heretic` Q8_0 (live) vs Q4_K_M (+ BF16 mmproj) | gufo ext or llama.cpp | **`39.9 GiB`** (Q8_0 live) / `~20–26 GiB` (Q4_K_M, gated on B4) | red-team / RESULTS | `main` (exclusive, `ttl: 1800`) |
| `qwen27b` UD-Q8_K_XL + DFlash2 (`2 × 262K`) | gufo 0.35.0 | **`70.2 GiB`** | U24 tuning record | `main` (exclusive, `ttl: 1800`) |
| `ref2va-27b` Q4_K_M + F16 mmproj (`32K`) | llama.cpp | **`19.14 GiB`** | U48 RESULT | `small` (`ttl: 300`), or `main` if G0 picks `~110 GiB` gufo FN |
| `joycaption` 8B Q8_0 + F16 mmproj (`4K`) | llama.cpp | `~9 GiB` | U47 brief | `small` (`ttl: 300`) |
| `embed-small` nomic Q8_0 (`8K`) | llama.cpp | `<1 GiB` | `llama-swap.yaml` | `small` (`ttl: 86400`, resident) |

Consequences:

- **Why `main` stays `swap: true, exclusive: true`:** `qwen27b` (`70.2 GiB`) and live `gemma4-heretic` Q8_0
  (`39.9 GiB`) cannot fit alongside either gufo Flash-Next (`~110 GiB`) or Halogen (`88.9 GiB`) inside
  `120 GiB` GTT. Keeping `main` exclusive avoids OOMs while `flash-next-default` stays warm during normal
  chat/coding and reloads in ~22–25 s after a Gemma or 27B job. (Optional later optimization: if `B4`
  approves Heretic Q4_K_M and `G0` picks Halogen, a separate coexistence test can evaluate keeping both warm.)
- **gufo 0.35.0 reserves memory per session** (`--sessions` × `--context`); pooled sessions (`#1258`) are only
  on gufo `main` post-0.35.0. Size gufo candidates as `2 × 131K` or `4 × 64K` (`>= 2` slots so Hermes side
  tasks do not evict the active conversation's prompt cache per Hermes `#155717`, and disable title/compression
  on the main model).
- **Disk budget:** Phase 0 candidates total >500 GB if pulled together. `P0.0b` archives `/srv/bakeoff`
  (`341 GiB`) and dead artifacts to QNAP first, and every Phase 0 download checks `df -BG /srv >= 100 GiB` free.
- `P0.7` measures the exact `G0` winner + `small` group loaded together before Phase 2 cutover.

## 5. Phases and packets

Each packet lists its scope, its check, and its stop trigger. **Y** marks a step that needs Derrick's yes at
the time (D13).

### Phase 0 — Snapshot, free staging space, and measure (decides D6). Read-only for live llama-swap; uses bake-off ports.

Every model candidate runs the **same check set** ("the P0 checks"):

- Disk preflight passes (`df -BG /srv` shows `>= 100 GiB` free after download).
- Loads cleanly, with cold and cached load time + GTT footprint + parallel slot count (`>= 2`, target `4`) recorded.
- U26 refusal probes (`benign_sysadmin`, `adult_fiction`, `explicit_adult`): comply 3/3.
- 22-call tool test: Gate 0's 20 calls (simple, parallel, after a long tool result, thinking on) **plus 2 calls
  with `tool_choice: "none"` after tool output** (catches `gufo #1232` raw `<tool_call>` leaks): `<= 2` leaks total, `0` on `tool_choice: "none"`.
- Tool-call IDs intact (catches `gufo #780` broken-quant ID corruption).
- 3 frozen Forge tasks pass.
- U6 18K fixture prefill/decode speed recorded.

| ID | Packet | Pass | Stop trigger |
|---|---|---|---|
| P0.0 | Confirm with Max what the in-flight looping fix already changed. Record current live `llama-swap.yaml`, pi settings, `herdr-panes.sh`, and `AGENTS.md` hashes, plus whether `B4` blind writer scores (Heretic Q8_0 vs Q4_K_M) are in. | State recorded; diff vs this repo's snapshot listed. | Live state cannot be committed (`B4` blocker unresolved) → run `P1.1` first. |
| P0.0b **Y** | **Staging disk cleanup to QNAP (D16):** copy `/srv/bakeoff` (`341 GiB`), unused `~/rocm` (`9.9 GiB`), and `/var/backups/evo-x3/_aborted-u34-final-20261116-0732` (`5.2 GiB`) to `/mnt/qnap/ai-archive/evo-x3-20261118/`, verify `sha256sum -c` on QNAP, then remove the local copies after Derrick's yes. Create `/srv/staging/`. | QNAP checksums OK; `/` free space rises by `~355 GiB` (`>1,000 GiB` free). | QNAP mount unavailable or checksum mismatch → stop; delete nothing. |
| P0.1 **Y** | **Uncensored Swift on Halogen 0.20.7:** test published Swift abliterated/heretic `.hgn` conversions (`Quat3rnion/halogen-swift1.5-qwen3.8-flash-next-v2-abliterated`, `johnlockejrr` Swift heretic HGN) and, if neither `.hgn` loads, test `Swift-1.5 IQ4_XS` GGUF while explicitly checking slot concurrency (Halogen 0.20.7 drops default concurrency mode on GGUF). Archive losing stage files to QNAP before next pull. | P0 checks (including multi-slot check). | None loads, all refuse, or GGUF is single-slot only (record and continue to P0.2). |
| P0.2 **Y** | **Uncensored stock Flash-Next on stock gufo 0.35.0:** `NeosQ/Qwen3.8-Flash-Next-Uncensored-UD-Q4_K_XL` (feeds both gufo and Halogen) or `SenseiHans/...-Uncensored-Q4_K_XL-Gufo`, sized at `2 × 131K` / `4 × 64K`. | P0 checks. | Load fails, `tool_choice: "none"` leaks (`#1232`), or tool-call IDs corrupt (`#780`). |
| P0.3 **Y** | **Swift on stock gufo 0.35.0 (censored speed baseline):** `ethanwtodd/Swift-1.5-Qwen3.8-Flash-Next-Q4_K_XL-GGUF` (111.3 GB). | P0 checks; refusal result recorded (expected to refuse). | — (informs G0 and the PR `#1036` watch item) |
| P0.4 **Y** *(optional)* | **Uncensored Swift on gufo via `dymoo/gufo-flash-next` fork:** Orca adapter on the `ethanwtodd` Swift file (1-commit/0-star fork; needs OD6 yes + HF token + gated BF16 weights staged via QNAP if needed). | P0 checks. | Adapter will not build, or does not remove refusals on Swift. |
| P0.5 **Y** | **Gemma 4 Heretic on gufo 0.35.0:** build `franzmoca/gemma4-gufo-extension` (API `>= 0.3.20`; source already on X3) and test Heretic (Q4_K_M if `B4` scores approve, else Q8_0) + BF16 mmproj. Also check whether an uncensored Qwen3.8-27B UD quant loads cleanly on gufo + DFlash2 for D4. | Gemma: write1/write2, vision 4/4, refusal 3/3, tools; 27B refusal status recorded. | Gemma extension fails → Gemma stays on kyuz0 llama.cpp; not a plan stop. |
| P0.6 | **Baseline:** Halogen 0.20.7 + existing abliterated Flash-Next (`/srv/models/flash-next-uncensored-hgn`) on the exact same 3 Forge tasks and 22-call tool test. | Results recorded with identical harness and samplers. | — |
| P0.7 **Y** | **Co-residency memory test (audit I7):** leading `G0` candidate at target sessions/context + `small` group (`embed-small`, `joycaption`, and `ref2va-27b`) loaded simultaneously + one request each. | Record peak GTT, `MemAvailable`, any OOM/503. Must keep `>= 8 GiB` headroom (if `ref2va-27b` pushes gufo FN under `8 GiB`, move `ref2va-27b` into `main` swap group and re-verify). | OOM or `<8 GiB` even with `ref2va-27b` moved → lower session/context count and re-test. |
| **G0** | **Gate:** choose `flash-next-default` (OD1). Must pass all P0 checks. | Preference order: (1) uncensored Swift (`P0.1` or `P0.4`) with `>= 2` concurrent slots; (2) faster of `P0.2` (gufo) and `P0.6` (Halogen 0.20.7) on Forge wall time, then tool errors. | No candidate passes → stop; Derrick decides. |

**Watch item:** gufo PR `#1036` (`--projection-vector`, llama.cpp control-vector format). Once merged, test
`ethanwtodd` Swift (`P0.3`) on stock gufo with a refusal projection vector (matching AlienPC Strata's ESP method).

Shared fixtures (reuse, do not invent): U6 18K fixture, U26 refusal probes, write1/write2, vision card, and
Gate 0's tool test from `coding-harness-research-20261115.md` (+ 2 `tool_choice: "none"` calls). Forge tasks run
on frozen copies at a pinned commit, never the live tree.

### Phase 1 — Filesystem hygiene, `<Role>-<Host>` chat naming, and loop fixes. Coordinate with P0.0 first.

| ID | Packet (audit / decision ref) | Check | Stop trigger |
|---|---|---|---|
| P1.0 **Y** | **D16 filesystem cleanup on X3:** consolidate runtime workspaces under `/home/evo/AI/`; create `/home/evo/AI/worktrees/` and gitignored `/home/evo/AI/_runs/`; fix `render_writer_pipeline.py` relative-path bug (`U23` gap #11); sweep inline `*.bak-*` files into `/var/backups/evo-x3/` and archive duplicate `/home/derekboone/evo-x3` scripts to QNAP once verified. | `find /home/evo/AI /etc/evo-x3 -name '*.bak*'` returns 0; relative render path writes only under `_runs/` (or refuses); `<200`-char paths + `.gitignore` rules verified on a Windows test clone. | Uncommitted unique edits found in `~derekboone/evo-x3` → merge into `/home/evo/AI` before archiving. |
| P1.1 | **B4 + git transport:** commit `/home/evo/AI` live trees (`forge`, `render`, `community` `x3-linux`, `agent-shared/extensions`) to Gitea with `/home/evo` paths. Resolve audit `I12` so both X3 (`evo` scoped repo deploy token or `derekboone` git helper) and AlienPC can `git push`/`git fetch` coding branches without exposing admin tokens. | Fresh clone dry-starts `Forge-Ops-X3` with all skills; test branch pushed from X3 is fetched on AlienPC and vice versa. | Secrets detected by `gitleaks` → stop; rotate per existing rule. |
| P1.2 | **B3:** Ralph GPU gate in `ralph.sh` uses an X3-only lock (`/home/evo/AI/locks/x3-ralph.lock`) with `flock -n` instead of stalling on 0-byte `gpu-render.lock`. | 2-item smoke loop completes with 0 lock stalls after a `queue-remote.sh` dry-run. | — |
| P1.3 | **I2:** Ralph backpressure. Clear stale `fix_plan.md` items before each loop; run every loop in `/home/evo/AI/worktrees/<loop-id>` with output logs in `_runs/`; enforce per-pass skill-load smoke test, `git diff --stat` file-count cap, and hard deny on `skills/**` and `AGENTS.md`. | Seeded stale item is refused; planted 30-file rewrite aborts the pass cleanly. | — |
| P1.4 | **I3:** mark the 6 known failing tests `xfail` with explicit reasons and re-enable blocking lint. | Baseline test suite exits `0`; a seeded failure exits non-zero. | — |
| P1.5 | **I8 + D16:** rewrite Forge, Render, and community `AGENTS.md` into short Always / Ask / Never files (<150 lines). Remove contradictions and **delete the "back up every file" `.bak` rule** (Git/`etckeeper` own file history). | Contradiction scan finds 0 conflicts; token count of startup instructions drops. | — |
| P1.6 **Y** | **I9:** set pi subagent defaults per pane (`~/.pi/panes/*`) to the active slot's sub-alias (`flash-next-sub` during Phase 1, updated in `P2.2`; never `gemma4-heretic` outside `Render-X3`). Upgrade `pi-subagents` to `>= 0.88.1` with explicit context inheritance. | Spawning a subagent in Forge causes 0 model swaps in `llama-swap` logs. | — |
| P1.7 **Y** | **B1:** `agy` runs only as `evo` (no sudo) inside `/home/evo/AI/worktrees/<unit>` with `--print-timeout` set (`<= 1800 s`). Max runs any `sudo` step separately after Derrick's yes. | Test `agy` run fails `sudo -n true` and terminates cleanly at timeout. | — |
| P1.8 **Y** | **B2 + D15:** cut the lethal trifecta and apply `<Role>-<Host>` pane names on both machines. Split X3 Forge into `Forge-Web-X3` (browser/SearXNG/fetch, no Vaultwarden/Gitea tokens) and `Forge-Ops-X3` (repo/Gitea/ops, no web tools); rename `Render-X3` and `Sydney-X3`; rename AlienPC coding pane to `Forge-AlienPC` and move `Render-AlienPC` / `Sydney-AlienPC` out of logon auto-start into `_standby/`. | `pi-mobile` and `herdr` show exact `-X3` / `-AlienPC` names; each session's identity banner matches; `Forge-Web-X3` has 0 vault/Gitea tools; `Forge-Ops-X3` has 0 web tools. | Derrick selects single-pane approval prompts (OD2) → configure `Forge-X3` with mandatory `ask` rules on vault/outbound calls. |
| P1.9 | **Loop limits** across `Forge-*-X3`, `Render-X3`, `Forge-AlienPC`, Ralph, and the `pi-code` wrapper: verify `loop-guard.ts` (`<= 3` identical tool calls), per-job turn/iteration cap, wall-clock timeout, and deterministic `STUCK` exit writing a short handoff summary under `_runs/`. | Seeded impossible task terminates in `STUCK` within limits and writes summary. | — |

### Phase 2 — X3 model serving cutover (after G0)

| ID | Packet | Check | Stop trigger |
|---|---|---|---|
| P2.1 **Y** | **`/etc/evo-x3/llama-swap.yaml`:**<br>• Assign a **unique loopback port** (`8081`..`8086`) and unique Podman `--name` (`MF-08`) to every model slot.<br>• `main` group (`swap: true, exclusive: true`): `flash-next-default` (`ttl: 86400`), `gemma4-heretic` (`ttl: 1800`), `qwen27b` (`ttl: 1800`), plus `ref2va-27b` if `P0.7` required it.<br>• `small` group (`swap: false, persistent: true, exclusive: false`): `embed-small` (`ttl: 86400`), `joycaption` (`ttl: 300`), and `ref2va-27b` (`ttl: 300`, if `P0.7` passed).<br>• Subagent aliases use `useModelName` + `setParamsByID` on sampling/thinking only — never overriding protected `model` (`llama-swap #1355`).<br>• gufo 0.35.0 slots use `checkEndpoint: "/ready"`, `--stall-timeout-ms 120000`, and raised `healthCheckTimeout` (`gufo #957`).<br>• Halogen slots (if selected or rollback) use `0.20.7`.<br>• Archive old slots in `/var/backups/evo-x3/` (no inline `.bak` in `/etc/evo-x3/`); commit in `etckeeper`. | `llama-swap -validate` passes; 4/4 pool test passes on `flash-next-default`; refusal probes 3/3; Gemma vision 4/4; calling Gemma swaps cleanly on its own port without port conflict or OOM, and calling `flash-next-default` reloads within ~25 s. | Any check fails → `etckeeper` / `/var/backups/evo-x3/` restore + restart. |
| P2.2 **Y** | **Callers & keys:** update `~/.pi/panes/*/models.json` + AlienPC `evo-x3` provider to `flash-next-default` / `flash-next-default-sub` / `gemma4-heretic`. Verify `LLM_KEY_HERMES` (typed by Derrick in `/etc/evo-x3/llm.env`) and `captureBuffer: 0`. Switch Open WebUI RAG embeddings to `embed-small`. | `verify-serve.sh` passes (`no key: 401`, caller keys `200`); `captureBuffer: 0` verified; subagents cause 0 swaps. | — |
| P2.3 | **Engine supervision & cold-boot guard:** verify container/systemd restart recovery on `gufo` exit `75` (`device_lost` / stall timeout); if Fedora 44 exhibits `gufo #1198` post-reboot CMA load refusal, apply `--cache-ram-bytes off` or `kho=off` (with Derrick's **Y** for kernel cmdline). | `kill -9` on active engine container recovers automatically on next request within 30 s. | — |
| P2.4 **Y** | **Background `tag_runner` governance:** if `U47` JoyCaption quality check passes, point PixlStash `tag_runner` at `joycaption` (`small` group, no swap with `flash-next-default`); otherwise restrict `tag_runner` to manual/overnight batch windows so it never evicts `flash-next-default` during active hours. | 30-minute active watch shows 0 unscheduled `gemma4-heretic` swaps while `flash-next-default` is loaded. | — |

### Phase 3 — Hermes on the X3 (`Hermes-X3` & `Hermes-Ops-X3`)

| ID | Packet | Check | Stop trigger |
|---|---|---|---|
| P3.1 **Y** | **Install Hermes Agent** as user `evo`:<br>• Two isolated homes/profiles under `/home/evo/AI/hermes/`: `Hermes-X3` (`127.0.0.1:8642`) and `Hermes-Ops-X3` (`127.0.0.1:8643`), managed by systemd user units + `loginctl enable-linger evo` (Max runs `linger` with sudo after **Y**).<br>• Provider = `llama-swap` (`127.0.0.1:8080/v1`) using `LLM_KEY_HERMES`; pin `context_length` (`>= 64000`, `Hermes #155853`).<br>• Disable title/compression side tasks on the main slot (or route to a fast local helper) so they don't evict prompt cache (`Hermes #155717`). | Both gateways answer on loopback through `flash-next-default` and survive reboot. | Hermes rejects context `< 64K` → adjust session layout or stop. |
| P3.2 **Y** | **Open WebUI & Tailscale Serve wiring (preserves `:443` and `:8444`):**<br>• Set distinct `API_SERVER_KEY`s on `:8642` and `:8643` (mandatory; API server grants tool execution).<br>• Keep Tailscale Serve `:443` -> `llama-swap` (`:8080`) and `:8444` -> `pi-mobile` (`:7878`) untouched.<br>• Connect existing Open WebUI (`:8443`, `127.0.0.1:3000`, `ENABLE_SIGNUP=false`) to `:8642` (`Hermes-X3`), `:8643` (`Hermes-Ops-X3`), and `:8080` (`Raw-*-X3` fallbacks).<br>• Keep Hermes dashboard (`:9119`) loopback-only unless OD3 explicitly enables dashboard auth. | Phone browser on tailnet opens `:8443` and sees `Hermes-X3`, `Hermes-Ops-X3`, and `Raw-*-X3`; AlienPC `pi` still reaches `:443`; `:8642`/`:8643` are unreachable directly from tailnet; non-tailnet devices are blocked. | Tailscale ACL preview not approved → stop. |
| P3.3 | **Pipeline-backed model routing:**<br>• `Hermes-X3`: main = `flash-next-default`, `auxiliary.vision` = `gemma4-heretic`, SearXNG/local-deep-research enabled.<br>• `Hermes-Ops-X3`: deterministic wrapper skills so existing pipelines/lints are respected instead of raw freehand subagents:<br>  - `render-write` -> runs `render_writer_pipeline.py` **dry-run only** (`77/77` lint, never `--queue` without Derrick's explicit command)<br>  - `ref2va-rewrite` -> calls `ref2va-27b` with image + `ref2va-system-prompt.md` (`temp=0`, `enable_thinking=false`)<br>  - `caption-image` -> calls `joycaption`<br>  - `/review` -> `Forge-AlienPC` Swift when idle, else X3 uncensored reviewer per D4. | 10 test prompts hit the right pipeline/model; `render-write` produces dry-run artifacts in `_runs/` and refuses to queue without approval. | — |
| P3.4 | **`pi-code` & `pi-status` async job skills (`Hermes-Ops-X3`):**<br>• Because Open WebUI is HTTP request/response (no server push after turn completion) and coding jobs can exceed Hermes's 600 s foreground terminal cap, `pi-code(repo, task)` launches a background job runner (`job_id`), creates an isolated branch/worktree, dispatches to `Forge-AlienPC` (if `P4.1` says free) or local `Forge-Ops-X3` (inside `evo-sandbox-run.sh` / Podman worktree sandbox), and immediately returns `job_id` + target host.<br>• `pi-status(job_id)` returns live state (`RUNNING`, `PREEMPTED_TO_X3`, `DONE`, `STUCK`), diff stat, and test output; optional `ntfy` ping notifies Derrick's phone when a background job finishes or hits `STUCK`.<br>• Set `child_timeout_seconds > 0` and `max_spawn_depth: 1`. | Both AlienPC and X3 paths complete end-to-end and report via `pi-status`; a forced timeout marks `STUCK` and writes `_runs/<job_id>/summary.md`. | — |
| P3.5 | **Hermes safety & loop guards:**<br>• `Hermes-X3` has web tools but `terminal` disabled (or read-only), `no` `pi-code`, `no` vault/Gitea.<br>• `Hermes-Ops-X3` has `unattended_mode: deny`, `command_allowlist` restricted strictly to `pi-code`, `pi-status`, `render-write` (dry-run), `ref2va-rewrite`, `caption-image`, and `ask-grok`, **no** web search/fetch, `HERMES_WRITE_SAFE_ROOT=/home/evo/AI/_runs:/home/evo/AI/worktrees`, `redact_secrets: true`, and hard `agent.max_turns` cap (since Hermes's repetition detector only warns on `api_server` runs). | Planted injection fixture (`u9b`) in `Hermes-X3` cannot invoke `pi-code` or outbound curl; disallowed shell command in `Hermes-Ops-X3` is denied immediately; runaway mock tool loop stops at `max_turns`. | — |
| P3.6 | **Manual GrokBot handoff (`ask-grok`):** Derrick-triggered command in `Hermes-Ops-X3` writes a <=10-line brief to the `fleet-brain` handoff inbox for Max. Never called automatically (D3). | Brief appears only when explicitly invoked. | — |

### Phase 4 — AlienPC Swift worker, reviewer, and render-preemption gate (`C:\AI\director`)

| ID | Packet | Check | Stop trigger |
|---|---|---|---|
| P4.0 **Y** | **Authenticated job gate inside live `C:\AI\director`** (not the archived Oct `switchyard` snapshot) + AlienPC hygiene (D16):<br>• Mark old `switchyard` (`D:\AI\vlm` `director.live.yaml`) `ARCHIVED-READONLY.md` and sweep inline `.bak-*` files into `C:\AI\backups\`.<br>• Create clean `C:\AI\worktrees\` root separate from `C:\Users\derek\forge`'s 61.5 GB `5slock` folder.<br>• Expose a minimal bearer-authenticated HTTP service on a dedicated Tailscale Serve port, restricted in Tailscale ACLs (`tag:evo-x3` only, plus tighten `:8446` ComfyUI ACL to `tag:evo-x3` + Derrick's devices), supporting fixed verbs only: `GET /status`, `POST /jobs/start`, `POST /jobs/preempt`, `GET /jobs/<id>`. | Only X3 (`tag:evo-x3`) can reach the job port; unauthenticated requests get `401`; arbitrary shell args are rejected. | Tailscale ACL preview not approved → stop. |
| P4.1 **Y** | **Availability check (`GET /status`):** wraps `C:\AI\director\scripts\gpu_guard.ps1 -Gpu`, `gpu-render.lock`, active lease check, and `llama-swap` `/running` without waking `comfyui_auto`. | Returns accurate `IDLE` / `RENDER_BUSY` / `LEASE_HELD` / `CODING_ACTIVE` across all four states. | — |
| P4.2 **Y** | **Pre-swap render preemption & X3 resume (D9):**<br>• Update **both** X3 `queue-remote.sh` (before it POSTs to `alienpc:8446`) and AlienPC `comfy-guarded.ps1` / `gpu_lock_gate.py` (before anything hits `/upstream/comfyui_auto` and triggers `llama-swap`'s `taskkill /F` on Strata!) to call `POST /jobs/preempt` when `CODING_ACTIVE` is true.<br>• The AlienPC **job wrapper** (not `pi -p` itself) waits up to a bounded grace window (`90 s`) for the in-flight turn to finish, stops `pi`, runs `git add -A && git commit -m "wip: preempted for render (<job_id>)" && git push` in `C:\AI\worktrees\<job_id>`, releases the GPU so ComfyUI can load immediately, and returns `{branch, commit_sha, last_log}`.<br>• `pi-code` on the X3 automatically fetches `branch` at `commit_sha` into `/home/evo/AI/worktrees/<job_id>` and resumes `pi -p` on `flash-next-default`. | Live test: trigger `queue-remote.sh --dry-run` (preempt hook) mid-coding job → Strata is NOT killed mid-commit; WIP commit lands on Gitea within 90 s; X3 checks out the exact SHA and finishes tests; ComfyUI receives the GPU cleanly. | Preempt hook bypassed by direct unguarded browser tab → document rule: always open ComfyUI via `comfy-guarded.ps1` (already standard per `ALI-150`). |
| P4.3 | **Independent diff reviewer mode (`Forge-AlienPC`):** read-only verb `POST /jobs/review` fetches a branch into `C:\AI\worktrees\<job_id>` and runs Swift (`coding_swift15_iq3s_esp`) read-only to review X3 diffs when render is idle. | Seeded bug in an X3 branch is flagged with file/line findings and 0 file mutations. | — |

### Phase 5 — End-to-end acceptance

| ID | Packet | Check |
|---|---|---|
| P5.1 | Run `AC-OP` (section 1) end-to-end from a phone browser at `:8443`, including `pi-status` and mid-job render preemption. | All four scenarios pass; all visible names carry `-X3` / `-AlienPC`; 0 unplanned swaps during chat. |
| P5.2 | Loop & injection test: run a seeded impossible coding task + `u9b` prompt-injection fixture through Open WebUI. | Impossible task exits `STUCK` within turn/time caps on both hosts; injection fixture cannot reach `pi-code`, vault, or external hosts. |
| P5.3 | Cleanliness & rollback drill: verify 0 inline `.bak-*` files, `>= 100 GiB` free on `/`, fresh-clone Forge dry start from Gitea, and 5-minute `llama-swap` rollback + restore. | All checks pass within 5 minutes. |

### Phase 6 — eGPU via OCuLink (future, out of scope; design notes only)

- **Separate backend.** When the eGPU arrives, it runs its own engine instance behind `llama-swap` with its
  own model names and loopback port. Neither gufo nor Halogen uses a second GPU. Use `llama.cpp`, or the
  `sixvolts/llama-halo-hybrid` fork (Radeon AI PRO R9700 marked production).
- **First candidates.** Move `gemma4-heretic` or `qwen27b` to the eGPU first so prompt writing / vision /
  review no longer swap against `flash-next-default` in `main` at all. No Hermes skill or `pi` pane changes
  beyond a model mapping in `llama-swap.yaml`.
- **Memory pools.** `llama-swap`'s `capacity` router can model `gpu0` (iGPU) and `gpu1` (eGPU) pools independently.
- **Pin engines to the iGPU.** Halogen hides extra GPUs automatically (verified on an EVO-X3 + 7900 XT over
  OCuLink, `Halogen #188`). `gufo` crashed at load with a second GPU active (`gufo #696`): explicitly pin all
  `gufo` containers with `HIP_VISIBLE_DEVICES` / `ROCR_VISIBLE_DEVICES` to the iGPU and smoke-test on arrival.
- **Card support.** R9700 is documented working (if it drops off PCIe/OCuLink at idle, disable `ASPM L1` on
  its PCIe links). Intel Arc Pro B70 has no coverage in these projects yet.

## 6. Acceptance trace

| AC | Requirement | Surface | Check | Evidence goes to |
|---|---|---|---|---|
| AC-OP | Four-message phone browser acceptance + preemption + `pi-status` | Open WebUI `:8443`, `Hermes-X3`, `Hermes-Ops-X3`, `pi-code`, P4.2 gate | P5.1 | Issue `#1` comment + Gitea record |
| AC-1 | Uncensored default model, fast swap recovery, 0 GTT OOMs, 0 port collisions | `llama-swap.yaml` (`main` + `small`, unique ports `8081..8086`) | P0.1–P0.7, G0, P2.1, P2.4 | Phase 0 results + P2.1 log |
| AC-2 | Coding on AlienPC Swift when idle, X3 `flash-next-default` when busy | `pi-code`, `pi-status`, P4.0, P4.1 | P3.4, P4.1 | Issue `#1` comment |
| AC-3 | Pre-swap render preemption commits/pushes WIP before ComfyUI kills Strata | `queue-remote.sh`, `comfy-guarded.ps1`, AlienPC job wrapper, X3 resume | P4.2 | Issue `#1` comment |
| AC-4 | No loops past limits & lethal trifecta severed | `Hermes-X3` vs `Hermes-Ops-X3`, `Forge-Web-X3` vs `Forge-Ops-X3`, `loop-guard`, `max_turns` | P1.2–P1.9, P3.5, P5.2 | Issue `#1` comment |
| AC-5 | `<Role>-<Host>` naming + clean, restorable filesystems & git repos (0 `.bak-*`, `>=100 GiB` free) | Panes, Open WebUI, `/home/evo/AI`, `C:\AI\director`, `/mnt/qnap/ai-archive`, Gitea | P0.0b, P1.0, P1.1, P1.8, P4.0, P5.3 | Fresh-clone & hygiene log |
| AC-6 | Browser access over Tailscale `:8443` while preserving `:443` (`llama-swap`) and `:8444` (`pi-mobile`) | Tailscale Serve + ACLs | P3.2, P4.0 | ACL preview + curl matrix |
| AC-7 | Pipeline-backed model per job (`render-write` 77-rule dry-run, `ref2va-rewrite`, `caption-image`, `/review`) | `Hermes-Ops-X3` skills & `Hermes-X3` vision slot | P3.3 | Routing test log |
| AC-8 | eGPU ready without agent rewrites | `llama-swap` names + unique ports | Design review at P2.1 | This plan (Phase 6) |

## 7. Risks

| Risk | Mitigation |
|---|---|
| Uncensored models + unattended Open WebUI + auto-approving `pi -p` recreate the B2 lethal trifecta. | Two-profile split (`Hermes-X3` web/chat vs `Hermes-Ops-X3` code/ops), two-pane Forge split (`P1.8`), and Podman/worktree sandbox (`P3.4`, `P3.5`). |
| Calling `/upstream/comfyui_auto` (`:8446` or browser) triggers `llama-swap` `taskkill /F` on Strata before `pi` can save. | `queue-remote.sh` and `comfy-guarded.ps1` / `gpu_lock_gate.py` call `POST /jobs/preempt` **before** touching ComfyUI, and the wrapper script performs deterministic `git commit && git push` (`P4.2`). |
| Co-loading `gemma4-heretic` (`39.9 GiB`) or `qwen27b` (`70.2 GiB`) beside resident Flash-Next (`89–113 GiB`) OOMs `120 GiB` GTT or collides on `:8081`. | Keep `main` exclusive (`swap: true`) with `flash-next-default` at `ttl: 86400`, assign unique ports `8081..8086`, and govern `tag_runner` (`P2.1`, `P2.4`, `P0.7`). |
| Phase 0 model downloads (`>500 GB` total) fill `/` (`~685 GiB` free before cleanup). | `P0.0b` archives `~355 GiB` of `/srv/bakeoff` + dead files to QNAP first; stage one candidate at a time with a hard `>= 100 GiB` free check. |
| Background PixlStash `tag_runner` keeps loading `gemma4-heretic` and evicting `flash-next-default`. | Move `tag_runner` to `joycaption` (`small` group) if U47 passes, or batch-window it (`P2.4`). |
| Open WebUI HTTP turns close before a 20-minute coding job finishes. | Background job wrapper + `pi-status(job_id)` skill + optional `ntfy` completion/STUCK alert (`P3.4`). |
| Stock `qwen27b` refuses reviews on adult/parody repo content. | Test an uncensored 27B UD quant in `P0.5` or route adult/parody-adjacent reviews to `Forge-AlienPC` (Swift+ESP) / `gemma4-heretic` (`D4`, `P3.3`). |
| `gufo` 0.35.0 `#1232` (`tool_choice: "none"` leaks `<tool_call>`), `#1198` (cold-boot CMA load refusal), or `device_lost` exit `75`. | Explicit `tool_choice: "none"` calls in P0 checks; `--stall-timeout-ms 120000` + restart supervision + `kho=off` / `--cache-ram-bytes off` fallback (`P2.3`). |
| Community uncensored quants break tool-call IDs (`gufo #780`), or community forks/extensions go stale. | Tool-call ID assertion in every P0 run; pin container digests and git commits; keep Halogen 0.20.7 abliterated as ready rollback. |
| Unauthenticated AlienPC `:8446` ComfyUI port or new `P4.0` job port reached by other tailnet nodes. | Bear-token auth on `P4.0` fixed verbs + Tailscale ACL lock to `tag:evo-x3` and Derrick's devices (`P4.0`). |
| Swift Enterprise License threshold (free up to US$1M gross revenue). | Personal use is inside the free tier; re-verify before any commercial deployment. |

## 8. Open decisions (Derrick)

| ID | Decision | When |
|---|---|---|
| OD1 | `flash-next-default` pick (`G0` Phase 0 winner) + `B4` blind score pick for `gemma4-heretic` (Q8_0 vs Q4_K_M) | After Phase 0 |
| OD2 | `B2` two-pane split (`Forge-Web-X3` + `Forge-Ops-X3`, default) vs single `Forge-X3` with approval prompts | P1.8 |
| OD3 | Keep Open WebUI (`:8443`) as sole phone UI (default) vs also enabling Hermes dashboard (`:9119`) with login | P3.2 |
| OD4 | Which eGPU (e.g., R9700), and whether `gemma4-heretic` or `qwen27b` moves to it first | When purchased |
| OD5 | AlienPC remote-job gate: HTTP endpoint inside `C:\AI\director` (default) vs Windows OpenSSH forced-command | P4.0 |
| OD6 | Run optional `dymoo/gufo-flash-next` fork test (`P0.4`)? Requires HF token + ~250 GB gated BF16 staging | Before P0.4 |
| OD7 | Create separate Gitea repos so `derrick/evo-x3` orphan branches (`x3-forge`, `x3-render`, `x3-pi-config`) can split cleanly | Anytime (non-blocking) |

## 9. Research findings used by this plan (Copilot, 2026-11-18; all fetched that day)

**R1 — Swift and uncensored variants**

- **Swift-1.5 GGUFs** (`ukisai/Swift-1.5-Qwen3.8-Flash-Next-GGUF`): Q8_0 is 188.3 GB, IQ4_XS 97.7 GB, built in
  bartowski's layout. The imatrix is in UkisAI's GSQ-RCO repo.
- **A ready-made Swift requant in gufo's layout** exists: `ethanwtodd/Swift-1.5-Qwen3.8-Flash-Next-Q4_K_XL-GGUF`
  (111.3 GB, requantize script included, tested on gufo). It is censored.
- **Uncensored Swift on stock gufo:** none found. `empyrealworks/Swift-1.5-Flash-Next-Abliterated-Gufo-GGUF`
  stores some expert weights as Q4_1, and gufo closed Q4_1 support as "not planned" (`#906`).
- **Why your Nov 15 test failed:** stock gufo refuses IQ-quantized Flash-Next experts since PR `#1041` ("No text
  provider found"). `storm1er/flash-next-iq-gufo-extension` adds UD-IQ4_XS.
- **Uncensored stock Flash-Next in gufo's layout:** `NeosQ/Qwen3.8-Flash-Next-Uncensored-UD-Q4_K_XL` ("one set of
  files feeds both Halogen and Gufo") and `SenseiHans/Qwen3.8-Flash-Next-Uncensored-Q4_K_XL-Gufo`.
- **Halogen 0.20.7** loads bartowski-layout IQ4_XS and refuses Q4_1, **but drops out of default 4-slot concurrency
  mode when loading a GGUF instead of a native `.hgn`**. It will not build refusal removal into the engine (`#239`),
  but abliterated models are allowed. Swift abliterated/heretic `.hgn` repos exist (Quat3rnion, johnlockejrr) with
  load tests marked TODO (`P0.1` tests them).
- **`dymoo/gufo-flash-next`:** 1 commit, 0 stars, MIT. Its Orca adapter projects out the refusal direction,
  qualified on base Flash-Next only. Building it needs orcarouter's gated BF16 weights (~250 GB).
- **gufo PR `#1036`** (`--projection-vector`, control-vector format) is open; the maintainer wants it.
- **Swift license:** free up to US$1M revenue.

**R2 — Hermes Agent** (docs `llms-full.txt` and GitHub issues)

- **API server:** default `127.0.0.1:8642` (per-profile `API_SERVER_PORT` in `.env` for second profile `:8643`).
  `API_SERVER_KEY` is required and grants terminal/tool access.
- **Open WebUI** connects to the API server over HTTP request/response (no background push after a turn ends).
  The dashboard (`:9119`) needs an auth provider for any non-loopback bind, including Tailscale Serve.
- **Model routing:** no content-based router. Use separate profiles (`Hermes-X3`, `Hermes-Ops-X3`), pipeline
  skills, side-task slots (`auxiliary.vision`, `/review`), or delegation `model_map`.
- **Coding:** no bundled `pi` skill exists; `claude-code` shows the terminal wrapper pattern (`workdir`,
  `timeout`, background + notify; foreground terminal calls cap at `600 s`).
- **Unattended mode:** API-server sessions are unattended (`unattended_mode: deny` refuses non-allowlisted
  dangerous commands; `command_allowlist` runs without prompting; repetition guard only warns, so `agent.max_turns`
  is mandatory).
- **Install:** `hermes gateway install` + `loginctl enable-linger`. Memory caps: `MEMORY.md` 2,200 chars, `USER.md` 1,375.
- **Open local-model issues:** loops `#151401`, `#142677`, `#151373`; context misdetection `#155853`; side tasks
  evicting single-slot prompt cache `#155717`.

**R3 — Engines and eGPU**

- **gufo 0.35.0** (2026-11-17): `#1232` (`tool_choice: "none"` leak) and `#1198` (cold-boot CMA load refusal)
  remain open; `#1157` was fixed in 0.34.0. Each session reserves a full context in 0.35.0; pooled sessions are on
  `main` (`#1258`). `franzmoca/gemma4-gufo-extension` requires `0.35.0` (extension API `>= 0.3.20`).
- **Fine-tunes on gufo** load only in Unsloth's tensor layout (PR `#293`). `ref2va-27b` ships plain Q4_K_M/Q5_K_M,
  so it stays on `llama.cpp`.
- **llama-swap:** `#1355` confirmed `setParamsByID` cannot override `model` — use `useModelName`. `gufo` health
  check is `/ready` (`GET /` 404s per `#957`). Live X3 `llama-swap.yaml` uses global `apiKeys` + `captureBuffer: 0`.
- **Halogen 0.20.4–0.20.7:** fixed `tool_choice` leak (0.20.4) and a multi-agent cross-conversation context leak (0.20.6).
- **eGPU:** see Phase 6.

## 10. Evidence used (retrieved before planning & v2 audit)

| Source | What it gave | Disposition |
|---|---|---|
| `x3-bakeoffs/host-evo-x3/bakeoff/RESULTS.md` & `U21-benchmarks-20261115.md` | Engine speeds, load times, pending B4 writer scores | Applied (§4, P0 fixtures) |
| `x3-pi-config/config/llama-swap.yaml` & `U24-model-tuning-20261115.md` | Halogen `88.9 GiB`, Heretic Q8 `39.9 GiB`, `qwen27b` `70.2 GiB`, shared `:8081` port, global `apiKeys` | Applied (§3, §4, P2.1, P2.2) |
| `x3-pi-config/serve/U8-serve-and-cross-wiring.md` & `U22`/`U30`/`U31` records | Live Tailscale Serve ports: X3 `:443` (`llama-swap`), `:8443` (`Open WebUI`), `:8444` (`pi-mobile`); AlienPC `:8446` (`ComfyUI` -> `llama-swap`) | Applied (D11, §3, P3.2, P4.2) |
| `records/U34-rollout-done-20261116.md` & `gufo-downloads-20261116.md` | Disk state (`341 GiB` `/srv/bakeoff`, `9.9 GiB` `~/rocm`, `5.2 GiB` aborted backup, `.bak` sprawl, orphan Gitea branches) | Applied (D16, §3.2, P0.0b, P1.0) |
| `records/U36-gap-tables-20261116.md` & `U23-render-pi-chats-20261115.md` | Live `herdr` panes (`render`, `forge`, `sydney`), `U23` relative-path bug, missing AlienPC SSH | Applied (D15, §3.1, P1.0, P1.8, P4.0) |
| `records/U47-*`, `U48-RESULT.md` | `joycaption` (`~9 GiB`), `ref2va-27b` (`19.14 GiB` GTT, 23.9 KB prompt), active PixlStash `tag_runner` | Applied (§4, P2.4, P3.3) |
| `alienpc-comfyui-config/launchers/comfy-guarded.ps1` & `llama-swap-pre-RENDER-TIMEOUT-20261026.yaml` | `comfyui_auto` and Swift share AlienPC exclusive swap group (`taskkill /T /F` on Strata); live root is `C:\AI\director` | Applied (D8, D9, P4.0–P4.2) |
| `bakeoff/results/u6-uncens-fn-gufo.engine.log` (Nov 15) | Upstream gufo refuses IQ-quantized Flash-Next ("No text provider") | Applied (P0.1–P0.4) |
| `records/2026-11-16-forge-audit.md` | Looping/safety findings B1–B4, I2, I3, I7, I8, I9, I12 | Applied (Phase 1) |
| `records/coding-harness-research-20261115.md` | `pi` #1; 20-call Gate 0 tool check; container isolation | Applied (P0 checks, P3.4) |
| `alienpc-community/briefs/agy_audit_20261025_report.md` | Swift is uncensored only with Strata ESP steering vector (0/15 vs 15/15 refusals) | Applied (D4, P0.1, P0.4, Watch item) |
| `fleet-brain-staging/ce/plans/2026-10-10-1130-feat-hermes-local-agent-plan.md` | Owned fail-closed approvals & memory byte budget | Safety ideas reused (P3.5) |
| Reddit r/StrixHalo, r/LocalLLaMA, r/LocalLLM & `deepu105` Swift benchmark | Mixed engines behind `llama-swap`; `gufo` + Swift requant fastest on Pi coding | Applied (D5, D6, P0.3) |
| Copilot research agents, 2026-11-18 (section 9) | Published Swift/uncensored quants; `gufo` 0.35.0 & Halogen 0.20.7 caveats; Hermes unattended/API behavior; eGPU rules | Applied (Phases 0, 2, 3, 4, 6) |

## 11. Rollback

- `/etc/evo-x3/` is tracked by `etckeeper` git and each cutover writes one clean snapshot folder under
  `/var/backups/evo-x3/<YYYYMMDD-unit>/` (zero inline `.bak-*` clutter). Restore = copy back + `systemctl restart llama-swap`.
- Cold weights archived in `P0.0b` stay intact with `SHA256SUMS` on `/mnt/qnap/ai-archive/` and active rollback
  slots remain configured.
- `Hermes-X3` and `Hermes-Ops-X3` stop cleanly via `systemctl --user stop`; Open WebUI (`:8443`) keeps
  `Raw-*-X3` direct `llama-swap` connections working if Hermes is down, and `:443` / `:8444` are never interrupted.
- Live AlienPC Strata (`C:\AI\director`) model profiles are untouched (`D8`); standby pane launchers stay in
  `_standby/` and the `P4.0` job service can be stopped independently.
