---
title: Forge and coding pipeline audit, Nov 16 2026
reviewer: Fleet Reviewer (bc9b71d5), report-only
ask: Derrick t270u (4:00 PM CT) "audit forge and our coding pipeline? is it setup and optimized? any community tips"; t271u "check with max and see if we have any issues with forge"; scope narrowed by t273u (4:01 PM CT) "no dont audit render just forge"
subject: Forge (pi on the EVO-X3), its subagents and Ralph loop, and Antigravity (agy) coding runs; owner Max Architect (d9fbd06c)
sources: brain config snapshot dae0aaa (40_projects/evo-x3/config-snapshot-20261116, read-only, redacted); Gitea derrick/evo-x3 read-only clone (branches x3-forge, x3-community, x3-pi-config, alienpc-community); box /workspace/maxops/x3 briefs and agy launchers; Max transcript (Forge items only, Nov 9-16); 60_reviews 1068be3, b62eb3f, f439150; Max's own issue list (tr 7639). No X3 or AlienPc shell. No images, videos or .jsonl opened. Render pipeline out of scope.
verdict: NEEDS FIXES (4 blockers)
---

# Forge and coding pipeline audit, Nov 16

**Verdict: NEEDS FIXES. Forge is set up, but it isn't safe to leave running unattended.** The model, the subagent slot and the CE skills are all in place. But almost all real coding now runs through Antigravity (agy) with every safety check turned off and admin rights. Forge itself has picked up a browser, a password vault and web tools with no approval step. Its multi-step loop has a lock bug that will probably stop it from ever running on the X3. And the X3's live instructions aren't backed up in Gitea.

## Blockers

| ID | What | Evidence | Fix | Owner |
|---|---|---|---|---|
| B1 | **The busiest coding agent can do anything as admin.** All 6 agy runs today (U40–U45) launched with `--dangerously-skip-permissions`, `--mode auto` and `--print-timeout 0`, as `derekboone`, which has password-free sudo. That machine holds `/etc/evo-x3` keys. A bad line in a brief, repo file or fetched page could run root commands, and nothing would stop or time out the run. | `/workspace/maxops/x3/U4[0-5]-agy-launch.sh` (L23–28); day audit 1068be3 F6; Gitea `x3-pi-config:records/U35-redteam-fixes-20261116.md` "Not moved: agy" | Run agy as `evo` (no sudo) inside a per-job git worktree. Give it a wall-clock timeout. Max does sudo steps separately after Derrick's yes. See decision D1. | Max |
| B2 | **Forge has all three "lethal trifecta" legs and auto-approves.** Since U38 this morning, Forge on the X3 has a Playwright browser, web search and fetch (untrusted input). It also has Vaultwarden signed in with 10 items, Gitea and the HA key (private data), and shell plus HTTP (a way to send data out). It starts with `pi --approve`, and the permission policy defaults to allow for bash and MCP, with no rules for the vault tools. The only guard is a prompt line in `~/.pi/agent/AGENTS.md`. | x3-forge `launcher/forge-pi.sh` L10; snapshot `x3/pi/pi-permissions.jsonc.md` L12, L239; tr 6982, 6990, 7023; `/workspace/maxops/x3/U38-forge-parity-brief-20261116.md` | Split the web tools and the vault/Gitea tools into separate sessions, or require approval for vault reads and outbound sends. Add deny or ask rules for the vault MCP tools. See decision D2. | Max (Derrick decides) |
| B3 | **The Ralph loop probably can't run on the X3.** `ralph.sh` treats any `gpu-render.lock` file without a PID as "GPU busy". It waits 30×120 s (1 h) and then skips the pass. `queue-remote.sh` uses `flock` on that same path, which leaves a permanent 0-byte file. Once one render has been queued from the X3, every Ralph pass stalls for an hour and does nothing, so a 10-pass loop is about 10 h of no work. The gate was ported from AlienPc, where the LLM and ComfyUI shared one GPU. On the X3 the renders run on AlienPc, so the gate isn't needed. No Ralph run on the X3 is on record. | x3-forge `ralph-community/ralph.sh` L11, L57, L85; snapshot `x3/render/queue-remote.sh.md` L34–38; Render AGENTS L179 "local lock is unused on the X3" | Either point Ralph at an X3-only lock or use `flock -n` the same way `queue-remote.sh` does. Then run a 2-item smoke loop. | Max / Forge |
| B4 | **The X3 is the source of truth, but Gitea can't restore it.** Max reports that the X3 `x3-linux` branch is 4 commits ahead of Gitea, with a large dirty tree: AGENTS.md, prompts, skills and notes. `4f7dee1` isn't in Gitea, which fits that. Gitea's Forge files still use the `/home/derekboone` paths from before U35 (`.pi/settings.json` L38–42, `PROMPT.md` L1, and the AGENTS.md diff on 18 lines). The `agent-shared/extensions` folder that Forge loads isn't in Gitea at all. Restoring Forge from Gitea would leave it with no skills. | Gitea read-only clone; snapshot `x3/agents/community-agent-shared-AGENTS.md.md` vs `x3-community:agent-shared/AGENTS.md`; tr 7590, 7639 | Commit by path and relay-push the X3 tree. Linuxize the `x3-forge` files to `/home/evo`. Add the extensions folder. Confirm with a fresh-clone dry start. | Max |

## Improvements

| ID | What | Evidence | Fix | Owner |
|---|---|---|---|---|
| I1 | **Forge is mostly idle. Code goes to agy, a cloud model.** Every build and fix job on Nov 16 (U36–U49) ran in agy on Gemini 4 Hydrogen High. No real Forge job on the X3 is on record since the cutover. The files still disagree on who does the code work. | Alfred audit f439150 P2-5; open-work L7–11 | Derrick picks the split (D5). One matching line goes in the briefing, the profile and Forge AGENTS.md. | Max |
| I2 | **The Nov 13 overnight Ralph run damaged files.** A stale cleanup item sat at the top of `fix_plan.md`. Forge worked it first and rewrote 23 skill and rule files to point at a folder that doesn't exist. It left 19 skills only as `.bak-f6b` files and stopped after 7 of 10 passes. Per-item checks didn't catch any of this because skill files have no tests. | tr 5771, 5815, Argon findings (tr ~5809) | Clear stale items before each loop. Run a whole-repo backpressure check on every pass: a skill-load smoke test, a `git diff --stat` file cap, and deny skills/AGENTS.md edits in loop runs. Use one worktree per loop. | Max / Forge |
| I3 | **The test gate is never green.** "686 pass, with the same 6 old failures", and "555 tests pass" left out the 6 failing tests. Lint is now warn-only. | tr 7488, 7067; open-work L18 | Mark the 6 known failures `xfail` with a reason, so a new failure fails the run. | Max |
| I4 | **The coding model has never been measured on our own tasks.** The coding bake-off was never approved. Forge's Halogen pick rests on single runs at 32K, with no repeats (protocol item 4). The benchmark figures quoted to Derrick were vendor numbers. | tr 6973; X3 audit b62eb3f L112–122; `/workspace/maxops/coding-harness-research-20261115.md` | Run the planned Harbor / Terminal-Bench plus 3 Forge-task bake-off, n≥3, scored blind (D4). | Max |
| I5 | **Forge and Render evict each other.** flash-next and gemma4-heretic are both in the exclusive `main` group, so every switch between those chats reloads a model (Halogen load about 25 s, measured at U26). | snapshot `x3/llama-swap.yaml.md` routing; b62eb3f rec 5 | Decision D3 (keep swapping, or shrink the KV pools so both stay loaded). | Max (Derrick decides) |
| I6 | **Forge concurrency isn't proven at worst case.** flash-next allows 4 requests, but the KV pool is 524,288 positions, enough for two full 262K contexts. The test covered 2×150K + 2×24K. A parent at 262K plus 3 subagents at 128K would need 655K. | yaml flash-next L90–93; tr 6654, 6823 | Test the worst case, or cap long requests, and record what Halogen does when the pool is full. | Max |
| I7 | **No test with everything loaded together.** The persistent `small` group (joycaption 8B, ref2va-27b, embed) can stay loaded beside flash-next's 88.9 GiB engine total. No recorded test has Forge at full context with the small group loaded. | yaml `small` group, U47/U48 slots | Run one co-residency memory test, or set short TTLs on the small slots. | Max |
| I8 | **Forge's rules contradict each other and are too long.** AGENTS.md L50 says no lease for restarts, while the X3 lease README L12 says restarts take the lease. L39 says "back up every file", while PROMPT.md L4 says "no backups beyond git". L29 says "No MCP servers… on the X3" after U38 added them. The launcher L6 still says "NOT production: AlienPc Forge stays live". The file is 43 dense lines (about 8 KB) under a "STOP GIVING IT RULES" decision (briefing L22). | snapshot and Gitea, lines as cited | Run a same-day restated-rule sweep (standing rule 8). Cut it to commands first, then Always / Ask / Never. | Max |
| I9 | **Subagent defaults can still cause swaps.** The user-level pi default for subagents is `gemma4-heretic` (snapshot `x3/pi/settings.json.md` L17, L34). Any pi session outside `~/AI/forge` that spawns subagents evicts Forge's model. pi-subagents is at 0.83.1, while 0.88.1 added context-inheritance flags. Whether subagents see the untrusted-content rule isn't verified. | snapshot; harness research L17, L42, L205 | Set the user-level subagent model per pane. Consider updating pi-subagents after Derrick's yes, and set inheritance explicitly. | Max |
| I10 | **AlienPc still has the Windows Forge stack.** It still has pi 1.4.0, the `coding_swift15_iq3s_esp` default, the coding/judge/gemma llama-swap slots and `loop-guard.ts`. Its skills and `resolve.py` are stale (Max). There's no live Forge AGENTS.md at `C:\Users\derek\forge`. The plan says AlienPc should be render-only (U9/R5). | snapshot `alienpc/` README L77, `llama-swap.yaml.md`, `pi/settings.json.md` L101 | After Derrick's yes, archive the AlienPc Forge and LLM slots (move, not delete). | Max |
| I11 | **agy ran parallel jobs with no lease.** Three agy runs overlapped on the morning of Nov 16, while memory says "one run at a time". The X3 work after 7:40 AM has no lease. | tr 6961, 6994; day audit F1 | One worktree per run, plus a lease line per run. | Max |
| I12 | **Max and the day audit disagree on evo's Gitea credentials.** Max says evo has no Gitea push credentials. Day audit F5a found an existing Gitea token copied to evo today (tr 7159–7170). One of these is wrong. | tr 7639 vs 1068be3 F5 | Max checks and records which is true. If the token is there, it moves into the one locked key file (rule 5). | Max |

## Nits
- N1. Gitea `x3-forge:AGENTS.md` is a one-line symlink to a target that still has old paths.
- N2. `thinkingBudgets.medium = 2048` in the Forge settings may cap reasoning if pi applies it to Halogen. Unverified.
- N3. ripgrep isn't installed on the X3, and AGENTS.md works around it. A one-line install needs a yes.
- N4. The Oct 31 open gaps are still open: Linear sign-in and the Google OAuth client for Forge (open-work L28).

## Pipeline map
Derrick → Max (Grok Bot) → brief (`/workspace/maxops/x3`, X3 `~/evo-x3/records`) → agy on the X3 (Gemini 4 Hydrogen High, cloud, `derekboone` + sudo, skip-permissions) → repos (community `x3-linux`, render, evo-x3) → relay push → Gitea.
Derrick → Forge pi chat (herdr pane / phone) → llama-swap :8080 → flash-next (Halogen, 262K, effort medium) → subagents on the same-slot alias `flash-next-sub` (128K/8K, effort low) → tools: bash, MCP browser/search/fetch/Gitea/Vaultwarden, `pi_qnap.py`, fleet-brain.
Multi-step jobs: Forge → `ralph-loop` skill → `ralph.sh` (`pi --approve --print`, one fix_plan item per pass) → commits.

## Models per role
| Role | Model | Notes |
|---|---|---|
| Forge chat | flash-next (Qwen3.8 Flash-Next HGN v2, Halogen 0.20.5) | 262K, effort medium, concurrency 4, ttl 24 h |
| Forge subagents | flash-next-sub alias | 128K / 8K output, effort low, same process (U34) |
| Forge alternate | flash-next-uncensored | Not production, 1 slot |
| Backup coder | qwen27b Q8 + DFlash2 (Gufo) | about 22–27 tok/s, `--cache-ram-bytes` 2 GiB |
| Build/fix runs | agy Gemini 4 Hydrogen High | Cloud, Gemini quota |
| Ralph loop | flash-next | `pi --approve --print --no-session` |

## Setup checklist (status as of Nov 16, 4 PM CT)
| Item | Status |
|---|---|
| pi 1.5.2, flash-next on Halogen at 262K | DONE |
| Forge thinking medium (330dd23) | DONE |
| Same-slot subagent alias (U29/U34) | DONE in Gitea; live UNVERIFIED |
| CE pinned @34492307, unused ce-* excluded | DONE |
| Forge Linux AGENTS.md (82aabc4/98c0bc4) | DRIFTED (live evo paths not committed) |
| ralph.sh Linux port | DONE as code; GPU gate DRIFTED; never run on X3 (UNVERIFIED) |
| PI_MEMORY_DIR per Ralph pass (Oct 31 GAP1) | DONE |
| Agents run as evo (U35) | DONE for pi; MISSING for agy |
| Untrusted-content rule (Nov 15 F5) | DONE, prompt-level only |
| Forge MCP tools (U38) | DONE; permissions and AGENTS not updated (DRIFTED) |
| X3 work backed up to Gitea | DRIFTED (B4) |
| gitleaks hook on Forge repos (Oct 31 GAP3) | UNVERIFIED (`.gitleaks.toml` present; hook unknown) |
| Lease for X3 Forge/agy work | MISSING after 7:40 AM |
| Forge health check today | MISSING (Max says so) |
| Coding bake-off | MISSING (not approved) |
| AlienPc Forge retired (U9/R5) | MISSING |
| loop-guard on the X3 | UNVERIFIED |

Not every plan item from the X3 build plan was re-checked here. Only Forge and coding rows were, so this isn't a "nothing dropped" claim.

## Community tips tied to gaps
1. **Cut one leg of the lethal trifecta.** Applies to B2. Willison, 2025-06-16: https://simonwillison.net/2025/jun/16/the-lethal-trifecta/. Meta "Agents Rule of Two", 2025-10-31: https://ai.meta.com/blog/practical-ai-agent-security/. An agent that has untrusted input, private data and a way to send data out shouldn't run on its own. Split the sessions or add a human approval. Owner: Max.
2. **Prompt-level guards aren't enough.** Applies to B1 and B2. Willison talk, 2025-08-09: https://simonwillison.net/2025/Aug/9/bay-area-ai/ ("prompt begging … doomed to failure"). Design patterns, 2025-06-13: https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/. Back the AGENTS.md rule with real limits: no sudo, a container or worktree, and deny rules. Owner: Max.
3. **Use backpressure on every Ralph pass.** Applies to I2 and I3. Huntley: https://ghuntley.com/loop/ (undated, read Nov 16, 2026). Every pass runs fast tests and checks that reject bad changes before the next pass. Owner: Max/Forge.
4. **Orchestrator and workers with explicit, non-overlapping task briefs.** Applies to I1 and I9. Anthropic, June 2025: https://www.anthropic.com/research/multi-agent-research-system. Each subagent gets an objective, an output format, tool guidance and task boundaries, and doesn't inherit the lead's context. Owner: Max.
5. **One git worktree per agent or task.** Applies to B4 and I11. Augment Code guide: https://www.augmentcode.com/guides/git-worktrees-parallel-ai-agent-execution (2026, read Nov 16). Owner: Max.
6. **Keep AGENTS.md short and command-first, with Always / Ask / Never.** Applies to I8. AAIF: https://aaif.io/blog/writing-an-effective-agents-md (read Nov 16, 2026). Owner: Max.
7. **llama-swap groups: persistent groups can't be evicted, and TTL is set per model.** Applies to I5 and I7. https://llama-swap.ai/docs/guides/routing/groups-and-matrix (docs, read Nov 16, 2026). Owner: Max.
8. **Checked and already aligned (no change):** kyuz0 Vulkan RADV is the recommended stable Strix Halo backend (https://github.com/kyuz0/amd-strix-halo-toolboxes). llama.cpp host prompt cache `--cache-ram` (PR #16391, merged 2025-10-09) applies only to the llama.cpp slots, not to Halogen's Forge, so the 2 GiB cap on qwen27b is fine.

## Decisions for Derrick
- **D1 Antigravity rights.** (a) Keep as is. You give up containment: an injected line can act as root on the X3. (b) Run agy as `evo` in a per-job worktree, with no sudo and a timeout. You give up agy doing installs itself; Max runs sudo steps after your yes. (c) Run agy in a podman container with only the repo mounted. You give up setup time, and systemctl/dnf aren't available to it.
- **D2 Forge's tools.** (a) Keep everything with auto-approve. You give up protection against data theft through a web page. (b) Use two Forge panes: web (browser/search/fetch, no vault or Gitea writes) and ops (vault/Gitea/HA, no web). You give up doing both in one chat. (c) Keep one pane but ask before vault reads and outbound sends. You give up some convenience: you'll tap an approval for those calls only.
- **D3 Forge/Render swap.** (a) Keep swapping. You give up about 25 s or more on each switch. (b) Shrink the Halogen KV pool to one 262K context and trim Gemma so both stay loaded (needs a memory test). You give up Forge's second long context and some tagger parallelism. (c) Move Forge to qwen27b. You give up speed (about 22 vs 50+ tok/s) and coding quality.
- **D4 Coding bake-off.** (a) Approve the planned bake-off. You give up a few hours of X3 time with Render paused. (b) Skip it. You give up any measured proof that Forge works on our tasks.
- **D5 Forge vs agy.** (a) agy for code, Forge for staging, installs and captions. You give up local, private coding and spend Gemini quota. (b) Forge first, agy only for hard jobs. You give up speed and quality on hard jobs, and it needs B3 fixed first.

## UNVERIFIED (needs a live X3/AlienPc look)
1. Whether the live Forge `.pi/settings.json` uses `/home/evo` or the old `/home/derekboone` paths, and whether community skills and research-core actually load.
2. Whether X3 `~/AI/locks/gpu-render.lock` exists for evo (the B3 stall), and whether `ralph.sh` has ever run on the X3.
3. What's in the 4 unpushed commits and the dirty tree (Max's claim; consistent with Gitea).
4. evo's Gitea credential state (I12).
5. The Vaultwarden MCP tool list, whether it can reveal passwords, and the `mcp.json` entries.
6. pi-subagents context inheritance, loop-guard on the X3, and what's in `agent-shared/extensions`.
7. What Halogen does when the KV pool is full, and memory use with the small group loaded.
8. gitleaks hooks on the X3 repos.
9. Whether agy's sudo is still password-free today.
10. Whether AlienPc's PixlStash (Serve :8445) and its LLM slots are actually running, as opposed to only configured.
11. The ComfyUI :8446 exposure Max raised is render-side and out of scope here. BL2 in 325e7de covers it.

Nothing was changed. Each fix goes to its owner only after Derrick says yes.
