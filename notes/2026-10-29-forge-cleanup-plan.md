pending upload
# Forge cleanup: quick fixes, prompt skill, Sydney talk session, storage, lean PROMPT.md — 1 page
Created: 2026-10-29 (deepened 8:5x AM CT from 1729e5a + audit 60_reviews/max/2026-10-29-pi-instructions-audit.md)

Derrick decision(s): 8:26 keep loop + talk session; 8:29 Sydney, chat only; 8:33/8:35 audit, "simple, modular, community-based"; 8:47 plan the cleanup (all AM CT).

**Goal:** a lean, community-shaped Forge setup in five small units, without new controls.
**Done when:** each unit's check below passes and Derrick says GO for the next one.
**Writer inputs:** none new. **Pictures:** n/a (no unit renders).
**Who builds:** Forge, on its own files. Max briefs from this plan only (pack: max, brief-only-from-the-plan.md).
**Community baseline:** pi docs `cli.md` (`--append-system-prompt`, `-ne`/`-e`, `--session-dir`) and `configuration.md` (context files load from the agent dir, cwd and parents); Ralph (ghuntley.com/ralph): lean PROMPT.md, fix_plan = to-do, AGENTS.md = learnings; plain files + rg, no RAG.
**Every unit:** backup the touched files first · one start and one done line in `C:\AI\community\notes\actions.log` · run the check · revert from backup on fail · youth guard unchanged.

## Units (order approved by Derrick 8:49 AM CT: U1 → U1b → U2–U5 on the new versions)
- **U1 Quick fixes.** (a) Make the loop run on `coding_swift15_iq3s_esp`: either Forge confirms the launcher passes `-Model coding_swift15_iq3s_esp`, or it changes the `ralph.ps1` default and PROMPT.md 1b. (b) Rewrite PROMPT.md 0a: only `@PROMPT.md` is in argv. (c) Mark the director skill's L25 beta6 KEEP line retired. *Check:* the next iteration log shows the `_esp` model, and `rg beta6_int8` in skills finds only lines marked retired or superseded.
- **U1b Upgrades (Derrick 8:49 AM CT).** Upgrade Strata, llama-swap and pi to their latest releases. The pending update from the other bot (Strata 0.2.7.1 / llama-swap v268) needs the AlienPc lease handed over first. Forge does the installs after backing up its configs and models.json. *Check:* re-measure the context ceiling and tok/s on the `_esp` slot and set pi `contextWindow` to the measured value. Re-read the new pi `cli.md`/`configuration.md`; `--append-system-prompt`, skills and AGENTS loading must still behave as U3 assumes.
- **U2 Prompt-skill merge.** `C:\AI\community\skills\h3-prompting\SKILL.md` becomes the single home for prompt rules: numbered rules, "output only the prompt", 3–6 examples from `notes\p15_writer_skill.md`, adults only (18+). Plain wording and a detail checklist go in only if `p15_writer_skill.md` or Wan `prompt_extend.py` already has them (review T-6). `ref2va-prompt`, `h3-ref2va-prompt-chain` and the director's prompt section become pointers. Repoint the dead PROMPT.md L16 scripts. Audio (Derrick 9:00 AM CT; TenStrip, [HF #77](https://huggingface.co/TenStrip/10Eros-Max/discussions/77)): no structured `overall_soundscape` block; plain audio cues in the main prompt or at its end. *Check:* each rule string appears in exactly one skill.
- **U3 Sydney talk session.** The talk launcher alone adds `--append-system-prompt <talk-persona.md>`, its own `--session-dir`, and `-ne -e <pi-permission-system> -e <pi-mobile>`, so pi-memory is off and the talk session never writes to loop daily logs. Same llama-swap entry and context as the loop; no config edits. Before each reply, check `gpu-render.lock`: never take it, and queue messages while it's held. *Check:* `rg -i "sydney|daddy"` over PROMPT/AGENTS/skills/notes/memory/new prompts = 0 hits, and a denied secret read in the talk session proves permissions still load.
- **U4 Storage.** Use one notes root (`C:\AI\community\notes`), one `progress.md` and one `notes\INDEX.md` (≤60 lines, folder → purpose). pi-memory stays as is. hermes memory stays dormant (out of scope). No RAG. Any move is archive-only and needs Derrick's yes per batch, and nothing is deleted. *Check:* every path PROMPT/AGENTS names exists.
- **U5 Lean PROMPT.md.** Keep only the loop protocol (Ralph). The render recipe and GPU essay move to h3-hc-render or AGENTS.md. The COMPLETE gate is removed, because ralph.ps1 has no check behind it. No new metrics or drift scripts (PROMPT rule 9999999). *Check:* PROMPT.md ≤2 KB, and the next CPU-only MAX pass completes.

## Open questions (Derrick)
- U1: launcher or default edit? · Sydney swearing level · U4 archive batch yes · Forge's proposed metrics and drift script: yes or no (default no).

**Acceptance before GPU:** no unit uses the GPU.
**Stop:** tone text outside talk, a second model load, chat during the lock, a duplicated rule, or a missing backup = fail; revert that unit.

Reviews: 60_reviews/max/2026-10-29-forge-chat-tone-plan-review.md (T-1..T-6 applied) · 60_reviews/max/2026-10-29-forge-cleanup-plan-review.md (F1, F2, F4 applied)
