# Render pipeline overengineering review

Read-only pass, 16 Nov 2026 (CT). Scope: EVO-X3 `/home/evo/AI/render` + `/home/evo/AI/community/scripts/parody` (and `run_queue.py`, `remote_comfy.py`, `queue-remote.sh`), plus the box copies of `h3-prompting` and `h3-parody-identity`. Worked example: `/home/evo/AI/community/runs/cassie_party_parody/guide`. No edits, no queueing, no PixlStash library reads, no secret files.

Already queued (not re-proposed here): named asks go through the parody identity step (spoof is only a tone); the ask beats the still for setting, clothes and lines; PixlStash picture search is `character_id`, not `tag=`.

Keep, no matter what is cut: the 18+ hard stop (`youth_hint` / `scale_adult` / `_MINOR_RE`); every test runs guide and ref from one prompt and seed; the locked 1-pass beta7_int8HQ INDEX + RefMod graph.

## Findings (best first)

### 1. Three prose candidates plus a judge cost ~80s and barely change the text

**What.** `config.yaml` sets `n_candidates: 3`, `tie_points: 3`, and a `judge_sampler` (`writer_pipeline/config.yaml:14-16,33-36`). `render_writer_pipeline.py` writes `cand_1..3.txt`, `lint_1..3.json`, then calls an LLM judge on a lint-score tie (`render_writer_pipeline.py:1611-1640`, `934-963`). `min_ready_score` is "reported only; never blocks READY" (`config.yaml:15`, `render_writer_pipeline.py:1611-1612,1665-1667`).

**Why it hurts.** The Cassie guide run made five LLM calls and took 151s (`pick.json`): beat card 66s, prose_1 24s, prose_2 20s, prose_3 32s, judge 9s. All three candidates scored 73, all passed, no hard fails. Word overlap was 0.92–0.97 (near-copies). The judge's scores were 18 / 17 / 15 and it picked `cand_1`. Two extra drafts and a judge added ~80s and six files for no meaningful choice.

**Cut or merge.** Default `n_candidates: 1` and drop the judge. Keep `--n-candidates` (or a bakeoff flag) for A/B tests.

**Keep.** One prose call, 18+ lint, the `pick.json` status line.

**Risk.** Low.

### 2. Talk clips still pay for a beat-card LLM call the code already has a fallback for

**What.** Every run first asks the writer for a JSON beat card (`render_writer_pipeline.py:1486-1501`, schemas in `MODES` at 331-391). The card is dumped into the prose prompt (`prose_messages`, L658-660) and can adjust `clip_seconds`. For talk, a failed card is replaced by a hand-written minimal card, and the comment says "BTS/talk: never skip the beat card" (`1544-1559`).

**Why it hurts.** Cassie is a talk clip. The beat-card call was the slowest step (66s, 8,514 prompt tokens). The three later drafts were almost the same, and the pipeline already contains a valid talk card template at L1546-1557. Talk also clamps length itself (`1506-1507`, 5.2–8.7s). Planning did not catch the two dropped lines.

**Cut or merge.** For talk (and any run that already has `--frames`), use the in-code minimal card and skip the LLM planning call. Keep the LLM beat card for sex / continued / multi-shot clips where duration and phase really need a plan.

**Keep.** The four-phase idea in the prose prompt; frame snap (`snap_h3_frames`); continued-clip end_state.

**Risk.** Med (talk timing and phase notes get a bit less tailored).

### 3. `wp_lint.py` still runs ~85 checks that cannot block a ship

**What.** After U52, only `youth_hint` and `scale_adult` are hard (`wp_lint.py:258-259`, `_fix` at 515-518). The rest of `lint()` (521-795) and `mode_checks` (127-252) still score and write `lint_*.json`. `config.yaml:47` still lists a long `block_ready` array (oral_silence, blacklist, talk-related codes, etc.). Nothing in the Python tree reads `block_ready` — it is dead config. `--fix-once` rewrite is off by default (`render_writer_pipeline.py:1595-1810`).

**Why it hurts.** Cassie was READY with six soft issues on every candidate, including `talk_lines` (too few lines) and `blacklist`. None of those warnings changed the text or stopped the queue, so the dropped lines shipped anyway. Operators see a score of 73 and a pile of lint files that look like a gate.

**Cut or merge.** Shrink the live linter to the 18+ hard stops, plus a short optional report (empty output, missing headers). Delete or archive the advisory rules and the unused `block_ready` list. Do not use lint scores to pick among drafts if item 1 lands.

**Keep.** `youth_hint`, `scale_adult`, empty/refused output, missing still / RefMod / graph files.

**Risk.** Low (behavior already matches "advisory only").

### 4. Two current writer commands, plus a leftover classic parody CLI

**What.** AGENTS.md:18 and RUN_ME.md:12,34-51 tell Render it may run `render_writer_pipeline.py` or `submit_parody_run.py writer-run`. The pipeline already calls `writer-run` itself after it writes `writer_output.txt`. `submit_parody_run.py` still has a second, older CLI in `main()` (`1669-1728`): required `--name`, `--character`, `--actor`, `--description`, `--scene`, `--tone` (default `parody`). That is the INDEX identity path. The `h3-parody-identity` skill (X3 `community/skills/h3-parody-identity/SKILL.md:36-44`, also on the box) still documents that classic command with Windows `C:\AI\...` PowerShell, and it is loaded in Render's pi session (`render/x3/render-pi.sh:31-32`).

**Why it hurts.** A named "parody" ask can legally go through the general writer (`writer-run` / pipeline + spoof overlay) and never hit `--name/--character/--actor`. Cassie did exactly that: `route.json` is `mode=talk`, `overlays=["spoof"]`; `build_report.json` refmods are `source=character`, `index_status=none`, stems = `oc_poolclub`. The identity recipe was sitting in a loaded skill and a live CLI the whole time. Two "one command" stories in one session.

**Cut or merge.** One command for Render: the pipeline (or a single wrapper) writes the prompt and always calls `writer-run`, with `--names` / `--character` / `--actor` on that same path. Point the parody skill at that command, not the Windows classic CLI. Keep the classic `main()` only behind tests or an archive alias until those tests move.

**Keep.** `submit_writer_run`, `resolve_writer_refmods`, INDEX + RefMod attach, `--queue --yes-derrick`.

**Risk.** Med (classic CLI is still referenced by `test_parody_*.py`).

### 5. Each Render chat loads nine skills on top of AGENTS.md and `writer_prompt.md`

**What.** `render-pi.sh:23-35` starts pi with `--no-skills` and then loads nine skills: `video-render`, `image-render`, `comfy-render`, `h3-parody-identity`, `h3-prompting`, `h3-max-ref2va-prompt`, `h3-hc-render`, `alienpc-hardcore-i2v-director`, `alienpc-stills-pose-edit-prompting` (~910 lines of SKILL.md plus ~684 lines of references), and appends all of `AGENTS.md` (~43 KB in 188 long lines). The pipeline then sends a compiled copy of the same craft (`writer_prompt.md`, 153 lines, from `wp_compile_prompt.py`). AGENTS.md:80-81 (SPOOF AND STORY) and `OVERLAY_NOTES["spoof"]` (`render_writer_pipeline.py:411`) say spoof/parody means original characters and no real names. `h3-parody-identity` says the opposite: pair the INDEX character and actor.

**Why it hurts.** The writer pane is stuffed with overlapping, partly AlienPc-era, partly contradictory instructions. "Parody" in the ask hits the spoof overlay ("no real names") while the identity skill is also loaded. Cassie got H3 layout right and identity wrong.

**Cut or merge.** Load `h3-prompting` and `h3-parody-identity` only (add `h3-max-ref2va-prompt` when the ask is actually a Ref2VA / long chain). Drop `alienpc-*`, `h3-hc-render`, and the generic `video/image/comfy-render` skills from the writer launcher unless a later operator path needs them. Keep one craft source: edit AGENTS, compile `writer_prompt.md`. Rewrite the spoof overlay to "tone only" as already queued.

**Keep.** Locked-graph notes, 18+, INDEX/RefMod identity rules (one wording, in the parody skill + writer-run flags).

**Risk.** Med (long-clip / hardcore / stills-edit asks must still be able to pull the extra skill when needed).

### 6. The builder still contains a second linter, a repair loop, and a still-noun rewriter

**What.** `build_request.py` is 6,610 lines / 171 functions and hosts both the classic parody builder (`format_parody_prompt`, `build_parody_request`) and the writer builder. On the writer path it still has `finalize_writer_prompt` (~600 lines from 2927), `lint_writer_prompt` (3536), `repair_writer_output` (2-round LLM repair, 3639-3682), and `apply_still_facts` (2132-2183), which "swap[s] wrong setting / garment nouns for the still's own nouns". Default `writer-run` is `--strict` off / passthrough (`submit_parody_run.py:1284,1600-1601`). Cassie `build_report.json` shows `passthrough: True`, `stripped: []` — the swap did not rewrite that prompt, but `still_facts` still recorded the still's place and wardrobe, and AGENTS.md:7 plus the parody skill (SKILL.md:31) still tell the writer never to contradict the still. Pipeline header comment L5 still describes "one targeted rewrite".

**Why it hurts.** U52 said the writer text ships verbatim, but a second, large rewrite stack is still in the builder and will fight the already-queued "ask beats still" fix if `--strict` or `apply_still_facts` is left on. Two linters (`wp_lint` and `lint_writer_prompt`) describe the same craft.

**Cut or merge.** Leave default passthrough. Stop calling `apply_still_facts` on the ship path (still_read stays input, not a post-editor). Archive or gate `repair_writer_output` / sentence-stripping behind `--strict`, then delete `--strict` once tests move. Split or later archive the classic `build_parody_request` path with item 4.

**Keep.** `_check_writer_18plus`, graph wiring (`prepare_writer_base_graph`, locked template), frame snap, continuation/seam helpers that `run_queue` still needs.

**Risk.** Med (strict-path and classic-builder tests).

### 7. Docs and config still describe Windows, a still pool, and an X3 with no vault

**What.** `RUN_ME.md` is half X3 (section 0) and half AlienPc: `/home/derekboone/AI/render`, PowerShell, `C:\Users\derek\.pi`, `templates\b2_refmod.api.json`, `approved_characters/POOL` (L4,16,18-32,52,57-60,76). AGENTS.md:14 still tells Render to pick from `_inputs` or `stills/approved_characters/POOL`, and L53/160 say PixlStash `vault.db` is not on the X3. The file `/home/evo/AI/5slock/libraries/vault.db` is present (I did not open it). `config.yaml:57-59` still has `still_pool` pointing at that POOL, and `auto_still()` will pick a random still from it (`render_writer_pipeline.py:1110-1117`, `--still auto` at 1795). AGENTS.md:173 says `/home/evo/AI/locks/gpu-render.lock` is unused on the X3; `queue-remote.sh:27-33` and RUN_ME.md:16 use it as the X3 submitter lock.

**Why it hurts.** Stale paths and "vault is not here" / "use the POOL" instructions send Render hunting in the wrong place (the PixlStash `tag=` loop is the already-queued example). A Windows launch section in the X3 guide is dead weight. The lock sentence contradicts the script the queue path actually runs. `default_character: FCSydny` (`config.yaml:10`, applied at `render_writer_pipeline.py:1281`) silently attaches the OC poolclub RefMods when no identity is resolved — Cassie’s `build_report.json` stems.

**Cut or merge.** One X3-only RUN_ME (move AlienPc launch notes to an archive). Docs: any still path or `_inputs/`, 18+ only; no pool; no `auto` still. Drop `still_pool` / `auto_still`. Do not default `--character` to FCSydny; require `--character` / `--names` or a resolved still. Fix the lock sentence to match `queue-remote.sh` (the Forge batch is already touching this lock). Mention that `vault.db` is on the X3, but still never browse library contents; picture lookup stays on the API with `character_id`.

**Keep.** `_inputs` + any named path; `$PIXL_KEY` in env (never printed); queue-remote + AlienPc Comfy as the render target; the submitter lock as implemented.

**Risk.** Low.

### 8. Each run writes a pile of files almost nobody consumes after queue

**What.** Cassie `guide/` wrote, among others: `beat_card.json`, `cand_1..3.txt`, `lint_1..3.json`, `pick.json`, `slots.json`, `route.json`, `still_read.json`, `writer_output.txt`, `prompt.txt`, `cast.json`, `build_report.json`, `_prompt_ids.json`, `_render_order.json`, plus logs. Continue-clips read `pick.json` (scene_id / parent status / still) and `still_read` (`render_writer_pipeline.py:1307-1318,1328-1334`). Queue needs `prompt.txt`, `clip/request.api.json`, `_render_order.json`.

**Why it hurts.** Six candidate/lint files per clip are only useful if item 1 stays. `slots.json` / `route.json` / a full judge blob are debug. The folder is hard to read when checking "what actually shipped."

**Cut or merge.** Always keep `still_read.json`, `writer_output.txt`, `prompt.txt`, `clip/request.api.json`, compact `pick.json` / `build_report.json`, and `_render_order.json`. Write `cand_*`, `lint_*`, beat-card invalid dumps, and the judge record only with a `--debug` flag.

**Keep.** The files listed above; logs for queue (`_render_queue.log`).

**Risk.** Low.

### 9. Acts, modes, and overlays are three overlapping taxonomies

**What.** `--position` / `acts.yaml` choose the act. `config.yaml:51-56` `position_kinds` and `render_writer_pipeline.MODES` (331-391) choose a writing mode. `wp_router.py` adds overlays (`OVERLAY_RE` at 18-27, `route_mode` at 92-128). The pipeline has a second spoof/parody regex (`render_writer_pipeline.py:58`). `wp_lint.MODE_RULES` (54-70) repeats the same split. AGENTS.md:112-120 has yet another MODES list. Cassie's `route.json` had `mode_blocks: []`. The word "parody" matches the spoof overlay, whose note forbids real names (item 5).

**Why it hurts.** One ask is classified three times, and "parody" is overloaded (tone vs identity). This is the machinery behind the already-queued routing bug, not a new product decision.

**Cut or merge.** One router: act from `--position` or the ask; spoof/cinematic/gonzo as tone flags only; named character/celebrity always takes the identity attach. Delete the duplicate spoof regex in the pipeline. Drop unused `mode_blocks` if it stays empty.

**Keep.** Useful overlays that change craft (continued, threesome, toy, restraints, scale, consent_setup). Talk as a clip type, not a separate pipeline.

**Risk.** Low, once the queued routing fix lands.

### 10. A 77-rule compile gate is a third copy of the craft

**What.** `wp_compile_prompt.py` copies craft sections from AGENTS.md into `writer_prompt.md`, then runs `check_writer_prompt_rules.py` against `render-master-rules-20261113.json` (target "77/77 PASS", RUN_ME.md:63-70). `wp_compile_prompt.py:1-5,75-82`. The compiler still hard-codes `/home/derekboone/...` in its docstring.

**Why it hurts.** Every craft edit is "change AGENTS, recompile, pass 77 rules, never touch the json." It did not prevent spoof/identity or still-vs-ask contradictions, because those lines compiled through as written.

**Cut or merge.** Keep a simple compile (AGENTS craft → `writer_prompt.md`, no agent/command leakage). Drop the 77-rule json gate, or shrink it to a handful of required headings and the 18+ line.

**Keep.** The compile step so the model prompt stays free of `--queue` / tool rules (`wp_compile_prompt.py:64-65`).

**Risk.** Low.

### 11. Frozen A/B sampler and persona arms are leftover setup flags

**What.** `config.yaml:13,17-28` still carries persona `current|option1|option2`, `sampler_arm: A`, and a full unused sampler B. CLI: `--sampler-arm`, `--persona` ("setup only", `render_writer_pipeline.py:1811-1812,1822`). `--fix-once` rewrite plus `rewrite_messages` (`925-932,1595-1658`) is the same kind of leftover.

**Why it hurts.** Extra flags and config for a finished A/B. Easy to turn back on by accident.

**Cut or merge.** Pin sampler A and persona `current` in config; remove B, persona arms, and the two CLI flags. Leave `--fix-once` off; delete it with item 3/6 if unused in tests.

**Keep.** The frozen A sampler values (temp 1.0, top_p 0.95, top_k 64, min_p 0.10).

**Risk.** Low.

## Estimated line count

If the cuts above land, about **1,800–2,500 lines of Python** can go or move to archive: ~650 from shrinking `wp_lint.py`, ~200 from the 3-candidate/judge path, ~400 from the classic `submit_parody_run` CLI once tests move, and ~800–1,000 from archiving `finalize` sentence-stripping / `repair_writer_output` / the second writer linter (not graph wiring or 18+). `build_request.py` as a whole (6,610) should not be deleted; splitting classic vs writer is a later job.

On the writer pane, unloading the extra seven skills drops about **600–1,000 lines** from what Render loads every chat (skills + references), without deleting those files. RUN_ME / AGENTS cleanup is small (~50–80 lines) but high value. `render-master-rules-20261113.json` is ~62 KB of paperwork, not runtime code.

Runtime on a Cassie-like talk clip: dropping the two extra drafts, the judge, and the beat-card call is on the order of **2 to 2.5 minutes** off a 2.5-minute writer pass (Cassie was 151s).

## Not checked

- PixlStash library contents, tags, or character rows (only confirmed `vault.db` exists at the documented path; did not open it).
- Sydney chats, persona, or memory; any `.env` / key file.
- A line-by-line dead-function audit of all 6,610 lines of `build_request.py` (classic vs writer split is item 6, later).
- Whether every `test_parody_*.py` still requires the classic CLI (assumed yes; that is why item 4 is med risk).
- Live AlienPc copies of these files; the pytest gate in `run_queue.py` (it only runs `test_p6_review.py` and `test_guard_scope.py` — keep that, it is already lean).
- `scene_addenda.py` (500 lines) is still called for briefs / look lines / off-screen voice — leave it.

Nothing was changed on the X3.
