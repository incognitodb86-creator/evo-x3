# 0.6 compound - self-setup learnings, index (2026-10-25, Forge/Ralph)

**Item:** fix_plan.md 0.6 "Compound the self-setup arc: write the durable learnings where the loop
reads them. One dense line per lesson in `C:\Users\derek\5slock\ralph-community\AGENTS.md` Learnings
(keep the file under its cap), full write-up in
`C:\Users\derek\5slock\ralph-community\notes\learnings\self_setup.md`. Repair 0.3's pre-reset archive
verifier, which is red because later legitimate edits/renames made the live source differ from the
archived bytes. Update fix_plan.md ... Add the check ... Commit in the same iteration."

This file is the **pointer/index** in the research repo. The write-up, the one-liners and the checker
live with the loop, because the loop reads them:

| artifact | path | what |
|---|---|---|
| full write-up (13 lessons) | `C:\Users\derek\5slock\ralph-community\notes\learnings\self_setup.md` | one `## Lesson N` per lesson: Rule / Evidence / Reproduce / Qualifies + the `AGENTS:` id it earned |
| durable one-liners | `C:\Users\derek\5slock\ralph-community\AGENTS.md` `## Learnings` | 10 lines `L1`-`L10`, 39-line file (its own first line promises "under 40 lines") |
| checker | `C:\Users\derek\5slock\ralph-community\notes\ali06_learnings_check.py` | 12 detectors; `--selftest` seeds 18 faults and requires each named detector to fire there and 0 on the real tree |
| skills cost probe | `C:\Users\derek\5slock\ralph-community\notes\ali06_skills_bytes.py` | the number behind the "33.7 KB" line: skills block 15,889 bytes over 45 `SKILL.md` files, 1,870 bytes for the 4 named CE skills |
| plan | `C:\Users\derek\5slock\ralph-community\notes\plans\0.6-compound.md` | the 8-step plan this item followed |
| AGENTS.md before this item | `C:\Users\derek\5slock\ralph-community\notes\AGENTS_before_0.6.md` | byte-exact backup (5slock is not a git repo) |
| 0.3 archive + verifier | `C:\AI\community\archive\2026-10-23-prereset\MANIFEST.json`, `C:\Users\derek\5slock\ralph-community\notes\prereset_archive_20261023.py` | 80 entries; the repaired contract is in `notes\learnings\prereset_archive_20261023.md` |

## Index of the 13 lessons

| # | lesson | AGENTS.md | item |
|---|---|---|---|
| 1 | the pre-reset archive is a snapshot contract, not a "never touch it again" contract; drift after archive is declared in a ledger, and an unledtered vanish is `SOURCE_GONE` | L1 | 0.3, 0.6 |
| 2 | `settings.json` `model` + `defaultProvider` beat ralph.ps1's `-Model` - the 0.1 drift mechanism | L2 | 0.4 |
| 3 | pi's resource surface is scoped to the working directory and to what is enabled (depth-7 cwd = 0 resources; `enabled: false` = 0 tools) | L3 | 0.4 |
| 4 | a citation you copy is a claim you own: re-verify against the installed version | L4 | 0.4, 0.6 |
| 5 | the archived guard gated on the command string, and pi RPC bash bypasses extension interception - it never enforced the GPU rule | L5 | 0.4 |
| 6 | PowerShell 5.1 `Tee-Object -Append` writes UTF-16 into a mixed-encoding log (use `Add-Content -Encoding UTF8`) | L6 | 0.5 |
| 7 | PowerShell variables are case-insensitive: `$pid` clobbers `param($PSItem)` and a param becomes an array | L7 | 0.5 |
| 8 | the tick and the commit ship together, and pinning `@fix_plan.md` is an argv contract | none - the rule lives in `AGENTS.md` Run lines and PROMPT.md | 0.5 |
| 9 | compaction deletes the plan, not the work: `notes\progress.md` + the item plan are the memory | none - PROMPT.md 2b is the live rule | 0.5 |
| 10 | fetch once, and never read a 401/403/404 stamp as evidence | L8 | 0.2 |
| 11 | verify a source by title + abstract, not by id; copy units and names exactly (download != install, one source row per deliverable) | L9 | 0.2 |
| 12 | a green check that cannot fail is worthless: probe the capability, seed the fault, never trust `...\| tail; echo rc=$?` | L10 | 0.5, 0.6 |
| 13 | skills are a per-session token bill: probe measures `system_prompt_bytes` 33.7 KB (0.4) -> 35,388 B now with 38 skills loaded; the skills block itself is 15,889 B and the 4 named CE skills cost 1,870 B | none - the cost is in the `AGENTS.md` "Installed in pi 1.4" line | 0.4 |

The research-side lessons (10, 11, 13 and 2) also apply to every future research pass in
`C:\AI\community`. `C:\AI\community\notes\self_setup_research_20261023.md` carries its own repair
header for the two 0.2 citation errors (arXiv 2607.22010 is a speech-deepfake LoRA geometry paper, not
an agent paper; the "installs" column counted downloads).

## Two repairs this item made to the record

1. **0.3's verifier** was red (`DRIFT 5slock/AGENTS.md`, `SOURCE_GONE` x2 on the guard extensions that
   0.4 disabled) because it required archived bytes to equal live bytes forever. The repair adds a
   declared `POST_RESET` ledger (`edited` / `renamed`) that checks the named keeper, and the
   unledtered case keeps failing. `--verify` = 80 entries 0 problems; `--selftest` = 8 probes fire.
2. **0.4's doc citation** `docs/balancing-custom-models-and-settings.md:75` does not exist in installed
   pi 1.4.0 (its docs directory has no such file, and no saved page in `C:\AI\community\notes\web`
   contains the quoted phrase). The finding survives; the citation does not. The real rule: pi reads
   resources from cwd and at most 5 directories above (`docs\configuration.md:3`,
   `docs\extensions.md:46`), and an MCP entry with `enabled: false` is not connected (`docs\mcp.md:69,100`).
   The dead token is kept in prose and listed in the checker's `DEAD_CITES` so it stays visible.
3. **The loop check's selftest was red** (`25 seeded faults, 2 did not fire`, rc=1) even though 0.5's tick
   note said 0 silent. Two seed bugs, same shape as the 0.6 checker's: the `agents_stale` seed `replace()`-ed
   AGENTS.md wording the file stopped using in 0.5, so the seed was a no-op; and the `plan` seed was
   dispatched to `d_plan`, whose plan-file check re-read the live `fix_plan.md` instead of judging the text
   handed to it. Repaired: the seed anchors on wording that exists, and the plan-file half is now
   `d_plan_heading(text)`. Now `25 seeded faults, 0 did not fire`, rc=0.

## Re-check (all green at ship time)

```
python C:\Users\derek\5slock\ralph-community\notes\ali06_learnings_check.py
python C:\Users\derek\5slock\ralph-community\notes\ali06_learnings_check.py --selftest
python C:\Users\derek\5slock\ralph-community\notes\prereset_archive_20261023.py --verify
python C:\Users\derek\5slock\ralph-community\notes\prereset_archive_20261023.py --selftest
python C:\Users\derek\5slock\ralph-community\notes\ali05_loop_check.py
python C:\Users\derek\5slock\ralph-community\notes\ali05_loop_check.py --selftest
python C:\Users\derek\5slock\ralph-community\notes\ali06_skills_bytes.py
C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py
```
