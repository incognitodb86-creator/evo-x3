# X3 Forge: make chats readable and stop the context thrash (rev 2)

**Goal:** On the X3, `pi --continue` and `/resume` in the Forge pane open the real chat history again, and long Forge sessions stop losing their thread.

**Rev 2 changes** (from Max's loop diagnosis + gbrain `40_projects/compute-expansion/records/2026-11-18-alienpc-x3-current-setup-and-problems.md`, verified where I can from AlienPc):
- **Every config phase now ends in a pane restart.** `sessionDir` and `compaction.*` are resolved at process start. rev 1's checks read files back — that proves nothing about the running panes, which started before my writes.
- **Ordering is coordinated with Max's T1 steps** (extensions, thinking budgets, sampler, restart). They touch the same files; doing both first means two restarts and two edits per file.
- **The launcher carries the thinking default.** The launchers pass `--thinking medium` on the command line, which overrides `defaultThinkingLevel` in settings. Phase 4 now owns that value, not just file placement.
- **KV-pool eviction is an acceptance check**, not just "compaction fires once".
- Two rev 1 facts corrected below (session counts; the "runaway" AlienPc pane).

## Current state

**Verified by me, read-only, 2026-11-18:**
- Pi **1.5.2**, user-local install `~/.local/lib/node_modules/@earendil-works/pi-coding-agent`.
- Session trees: `--home-evo-AI-forge--` 16 files / 3.99 MB, `--home-evo-AI-render--` 25 / 9.76 MB, `--home-derekboone-AI-forge--` 2 / 0.14 MB. No corruption; every header parses.
- **The whole X3 chat history starts 2026-11-15 17:54 CT.** Pre-X3 AlienPc Forge sessions are not there (AlienPc has `--C-Users-derek-forge--` 45 files / 60.7 MB). The `~/.pi/panes/{forge,render}/sessions -> ~/.pi/agent/sessions` symlinks (2026-11-16 16:30) hid any earlier pane-local tree.
- Launchers set `PI_CODING_AGENT_DIR=$HOME/.pi/panes/<pane>` and `cd` into the repo, with **no** `--session-dir`; pi resolves sessions from `$PI_CODING_AGENT_DIR/sessions`.
- **Context thrash:** `~/AI/forge/.pi/settings.json` sets `compaction.reserveTokens: 131072` on a 262144-token model → threshold at 131,072. Measured: the uncensored chat crossed 131k **78 times**, peaked at **236k**, with **zero** compaction entries in any session file. It runs far past its own threshold and loses context at provider overflow instead of a clean summary.
- `~/.pi/agent/settings.json` has no `compaction` block; `~/AI/render/.pi/settings.json` uses 24576/16384 (that one is sane).
- **Phase 2 is written** (this morning): `"sessionDir": "/home/evo/.pi/agent/sessions"` in both pane settings, backups in `~/.pi/panes/_archive/*-settings.20261118-073851.pre-u58`. Both parse; the picker logic resolves 18 Forge / 22 Render sessions against those cwds. **Not effective in the live panes** — they started before the write.
- **The "runaway forge-janc w2V:p2" is not running.** `herdr pane list` on AlienPc, 07:47 CT: w2V:p1 idle, w2V:p2 done (its session file stopped growing 21:41 CT Nov 17), w2V:p3 done, w2V:p4 working = this session. No `C:\AI\locks\gpu-render.lock`. Nothing to stop on AlienPc.

**From Max / Fleet Reviewer (not independently verified by me — treat as their evidence):**
- X3 runs Halogen 0.20.5, only `flash-next-uncensored` resident; `flash-next`, `flash-next-sub`, `gemma4-heretic*` all pinned to it. KV pool at 98% (143k–150k prompt-cache evictions) at 21:23 CT Nov 17.
- `auto-continue.ts` v2 installed in both X3 panes; Render also has `loop-guard.ts`, **Forge does not**.
- Launchers pass `--thinking medium`; I confirmed this shape in `forge-pi.sh` (`--thinking "${FORGE_THINKING:-medium}"`), so the flag beats settings.json.
- `x3-local-coding` uses `temperature: 0.6, presence_penalty: 0` on abliterated weights (audit M2), off the Qwen card preset.
- Max's 20:40 CT instruction fixes (OPERATOR.md quote-error-and-stop, h3-parody-identity `--wait` removal, Render skills stripped from Forge settings) explicitly waited for a restart; the panes' last writes are 02:30 CT today, so **the current sessions do carry them** — rev 1's claim that they did not is superseded.

## 1. Scope
**In scope**
- One session root for all X3 pi chats; every entry point sees the same history.
- Compaction thresholds that match the models Forge and Render actually use, sized so Forge stops filling Halogen's shared KV pool.
- One launcher per pane, one home, carrying the agreed thinking default, verified end to end after a restart.
- Back up the pre-X3 AlienPc chat history read-only into the X3 tree.
- A short operator note: how to open a past chat (pane, phone, CLI).

**Out of scope**
- No pi upgrade — 1.5.2 is current.
- No model swaps, no llama-swap.yaml edits, no Gufo/OpenCode work (that is the compute-expansion plan, its own owner).
- **Extensions (`auto-continue.ts`, `loop-guard.ts`), thinking budgets and sampler values are Max's T1 steps.** I do not write them; I read the final state and align Phase 4 to it.
- No deletions; anything removed moves to `_archive`. Nothing runs while a render is live.

## 2. Community check (external)
- pi docs `docs/sessions.md`: sessions live under `<agent-dir>/sessions` grouped by cwd; `--continue` uses the current directory, `/resume`/`--resume` use the session's own cwd; `--session-dir`, `PI_CODING_AGENT_SESSION_DIR`, and the `sessionDir` setting redirect storage, CLI flag highest.
- pi docs `docs/compaction.md`: auto-compaction triggers at `contextTokens > contextWindow - reserveTokens`; `modelOverrides` are exact `provider/modelId` keys with per-field fallback; provider overflow can trigger one compact-and-retry.
- pi docs `docs/configuration.md`, `docs/security.md`: project `sessionDir` is read before project trust resolves — it must live in the pane dir (`$PI_CODING_AGENT_DIR/settings.json`) to apply on every launch, including headless `pi --print`.
- Installed 1.5.2 source confirms both: `dist/main.js` resolves flag → env → settings once at startup; `SessionManager.list/continueRecent` filter by header cwd when `sessionDir` is custom. **No hot reload** — this is why a restart is part of every check below.
- Loop control (Max's lane, community-sourced): thinking budget 2048–4096 for Flash-Next coding, an identical-tool-call circuit breaker, and no auto-nudge extension firing into an unchanged context.

## 3. Key design decisions
1. **One shared session root** `~/.pi/agent/sessions`, with `sessionDir` pinned in each pane's settings so the launcher, a bare `pi`, a new herdr pane, and the phone path all read one tree. Chats stay keyed by cwd, so Forge (`~/AI/forge`) and Render (`~/AI/render`) remain separated by design — that is not a bug.
2. **Compaction sized per model** in the user-level file so it covers every project: reserve 32768 (fires at 229,376 of 262,144) / keep 20000 for the 262k models; reserve 16384 / keep 20000 for 131,072-token aliases. A 131,072 window with a 131,072 reserve is a zero threshold — that pairing is forbidden in any future slot (the Gufo plan's U8 must state an explicit number).
3. **One launcher per pane** = `~/evo-x3/pi-chats/<pane>-pi.sh`, because that is what `herdr-panes.sh` runs. The forge repo copy moves to `launcher/_archive/` with a pointer. The launcher is also where the thinking default lives (command line beats settings.json), so Phase 4 sets it to Max's agreed value rather than leaving `medium` hardcoded.
4. **History import is read-only, not a move.** Copy AlienPc's old-Forge-cwd tree into the X3 tree; originals untouched.
5. **One restart per pane for this whole job**, taken after Max's T1 steps and my writes land together.

## 4. How it works (flow)
Derrick opens the forge pane (herdr → `forge-pi.sh` → `cd ~/AI/forge`, `PI_CODING_AGENT_DIR=~/.pi/panes/forge`) → pi reads `sessionDir` from that pane's settings at startup → picker and `--continue` list `~/.pi/agent/sessions/--home-evo-AI-forge--/*.jsonl` → he picks a chat, it resumes in its own cwd. Same tree from the phone (pi-mobile) and from a plain shell. Mid-chat, context passes 229k → pi compacts to a summary + recent 20k → the chat continues with its thread intact, and Forge's prompt cache stops thrashing Halogen's shared pool.

## 5. Phases
**Phase 1 — evidence lock (read-only).** DONE. `~/AI/forge/records/U58/AUDIT.md` + `evidence.txt`, counts re-derivable by the saved commands.

**Phase 2 — session root.** DONE (write): `sessionDir` in both pane settings, backups taken, both parse. **Open:** validation needs a restarted pane — see Phase GATE.

**Phase 3 — compaction.** Set the per-model block in `~/.pi/agent/settings.json` (backup first), covering `x3-local/*`, `x3-local-coding/*` and both `-sub` aliases. *Validation:* config parses; a synthetic session driven past 229k produces exactly one `compaction` entry and the chat continues; no second compaction in the following 10 turns.

**Phase 4 — launcher convergence + thinking default.** Move `~/AI/forge/launcher/forge-pi.sh` to `launcher/_archive/forge-pi.sh.moved-<date>`, leave a pointer in `launcher/README.md`; commit the live `pi-chats` launcher as the single tracked copy. Set the pane's agreed thinking value at the command-line default (Forge: 2048/4096 tier, i.e. `low`, not `medium`; Render: `off`). If Max has already changed it, record his value and do not overwrite. *Validation:* `herdr-panes.sh` dry run starts both panes; `git -C ~/AI/forge status` clean for that path; the started pane's process shows the intended thinking level.

**Phase 5 — history import.** Copy AlienPc `--C-Users-derek-forge--` (45 files, 60.7 MB) into `~/.pi/agent/sessions/alienpc-import-20261118/--C-Users-derek-forge--/` via the x3put base64 route (batched; no direct SSH key use). *Validation:* file count and total bytes match a source manifest; every imported JSONL's first line parses.

**Phase 6 — docs + records.** Update `~/evo-x3/pi-chats/README.md` (one session root, how to resume: pane `/resume`, phone, `pi --continue`), write `~/AI/forge/records/U58/BRIEF.md` + `RESULT.md`, append actions.log lines. *Validation:* a fresh shell with no env vars opens the newest Forge chat with `pi --continue`.

**GATE — the one restart (after Max's T1 steps and Phases 3–4 are written).** Restart w4:p1 (Forge) through the normal launcher route, then verify in the running pane:
- `/resume` lists ≥16 pre-existing Forge sessions with dates back to 2026-11-15; `pi --continue` from a plain shell at `~/AI/forge` opens the newest real chat.
- The pane's loaded state shows Max's extension/thinking/sampler changes, and the picker is not empty.
- One long synthetic session crosses 229k, compacts once, continues; X3 journal shows no repeat of the 143k–150k prompt-cache eviction pattern on that run.
Render (w3:p1) gets the same `sessionDir` check with ≥22 Render sessions; its chat is otherwise untouched.

## 6. Risks and mitigations
- **A setting written but never loaded** → every phase's check runs against a restarted pane, not a file read-back. This is what rev 1 got wrong.
- **Two agents editing one file** → extensions/thinking/sampler are Max's; session root/compaction/launcher placement are mine; Phase 4 defers to his thinking value if already set. One restart per pane.
- **Higher compaction threshold = heavier single requests** (the measured 236k calls) → keep `keepRecentTokens` at 20k so each compact frees ~200k, and cap the `-sub` aliases per model.
- **User-level settings touch every pane** → backup + record the diff; only the `compaction` block changes.
- **Import bloats the picker** → imported tree is a sibling directory, not listed by the normal picker; note how to read it.
- **Restarting a live pane mid-task** → check for an in-flight turn first (`herdr pane list` status) and take the gate only when Forge is idle.

## 7. Verification (end of work)
- In a **restarted** Forge pane: `/resume` lists the real history back to 2026-11-15; `pi --continue` in a plain shell at `~/AI/forge` opens the newest chat; the imported pre-X3 set is reachable.
- One long synthetic session crosses 229k and continues after a single compaction, no provider overflow, and no KV-pool eviction storm on that run.
- The restarted pane runs with Max's thinking/extension/sampler settings; Forge has a loop circuit breaker.
- `pi --version` still 1.5.2; llama-swap untouched; no GPU lock held; Render chat unaffected.
- All edited files have timestamped backups; `git status` clean in touched repos; records + actions.log written.

**Stop condition:** if a setting change does not move the picker or the compaction threshold as predicted **in a restarted pane**, revert that file from its backup, record the exact probe output, and report — do not widen scope into pi internals.

## 8. Source use
- **Adopted (community):** pi's own session/`sessionDir` model and `compaction.modelOverrides` (pi docs + installed 1.5.2 source); Max's loop-control lane (thinking budget caps, loop-guard) as the owner of those files.
- **Modified:** compaction values are ours, from the measured 131k–236k usage and the models' windows; pi ships 16384/20000.
- **Rejected:** upgrade pi (current); per-pane session dirs (that caused the split view); moving history (keep originals).

## 9. Work tracking
todo #1 Phase 2 (write done, gated on restart) · #2 Phase 3 · #3 Phase 4 · #4 Phase 5 · #6 Phase 6 · GATE = one restart + in-pane verification. One at a time; each ticked only after its own check passes, and no phase is "done" before the GATE.

## 10. Lessons capture
One learning per job into `C:\AI\fleet-brain\20_learnings` (ce-compound format, tag unreviewed): the `PI_CODING_AGENT_DIR` + `sessionDir` interaction, why a per-pane agent dir silently splits chat history, and **why a startup-resolved setting cannot be verified by reading the file back**.

## 11. Deferred ideas
- Import the pre-X3 **Render** history (same method as Phase 5).
- Set `projectTrust` for headless Ralph passes.
- Update pi-subagents (0.83.1 → newer) — needs Derrick's yes.
- Name sessions (`/name`) so the picker is readable on a phone.
- Gufo 0.35.0 / OpenCode / Hermes trial: not this plan; its U2 should test **0.35.0** (0.34 has the Flash-Next compacted-MTP norm-buffer corruption), and U8 must state an explicit `reserveTokens` for any 131k/65k window.
