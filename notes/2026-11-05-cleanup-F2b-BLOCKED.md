# 2026-11-05 F2b (FORGE phase 2b) = BLOCKED (18:4x CT, Forge, pi session in C:\AI\render)

Item: `fix_plan.md` FORGE F2b - retire the per-face copies. "Depends on F2a's two OBJECTIVE oks (quote them in this item's
RESULT when it runs)." **F2a is `[PARTIAL]` and has no OBJECTIVE line** (its two GPU cells await Derrick's GO, asked in
`notes\needs_derrick.md` 13:00 CT, Ask 1, unanswered), so F2b's stated dependency is unmet and F2a's own rule binds:
"do NOT archive any old template in this item - F2b does that only after these two OBJECTIVE oks." Measured, nothing moved.

## Why blocked, one line
The item's dependency (two `OBJECTIVE ok` lines from F2a's GPU test cells) does not exist, its GO ask is unanswered, and its
Do is narrowed by the plan of record: v2 (`notes\2026-11-05-forge-cleanup-v2.md`:22-23,28, Max's 11:12 audit) says
**"F2b must not move b2_fc_sydney_lora*"** and "Every FC_SYDNEY **and b2_fc_sydney_lora\* file stays**", while this F2b
text says to move them. A v1-vs-v2 conflict in the Do is Derrick's keep/drop call (already asked: 12:0x CT block-retirement
card), not mine.

## Measured state of phase 2 (all read-only, no GPU, no lock, no HTTP, no write)

| clause | state | evidence |
| --- | --- | --- |
| 1 "the 24+3 files exist in the archive and not in the templates folders" | **partly built by the agy lane, not by this item; location differs** | `git show --name-status 25e403c` (agy U7, 12:00:59) = `D templates/faces/FC_*.api.json` x**23**; those 23 files are on disk at `C:\AI\_archive\2026-11-05-cleanup\7\faces\` (`ls ... \| wc -l` = 23), **not** in the phase-2 archive (`ls C:\AI\_archive\2026-11-05-cleanup\2` = `ralph-community`, `scripts` only). The 3 `templates\b2_fc_sydney_lora*.api.json` (20098 / 20112 / 20112 B) and `templates\b2_fc_sydney_lora.README.md` (4110 B) are **still in templates** - v2 forbids moving them, so this clause is not executable as written. |
| 2 "`ls .../faces/FC_SYDNEY.api.json` exists untouched (same size/mtime, record both)" | **met** | `stat -c '%s %y' templates/faces/FC_SYDNEY.api.json` = **21171 B, mtime 2026-11-03 19:01:34** - predates the whole 2026-11-05 cleanup, so no cleanup phase touched it. It is gitignored (`.gitignore` `*sydney*`, documented in `templates\faces\README.md`), so there is no git history to compare; the mtime is the proof. |
| 3 "`rg -l 'FC_[A-Z]+\.api\.json\|b2_fc_sydney_lora'` over C:\AI\community, .pi\agent\skills, C:\AI\render finds no live script, skill or README that references an archived file" | **met in substance, 0 real violations; counts stated** | the command returns **7 files**: 4 are records/history (`notes\2026-11-05-cleanup-F2a-PARTIAL.md`, `notes\needs_derrick.md`, `notes\progress.md`, `notes\_filescan_2026-11-01\added-7d.tsv`), 2 are the F2a proof fixtures that name the **archive path on purpose** (`scripts\tests\test_b2_lora_param.py:13-14` `FC_DIR = C:\AI\_archive\2026-11-05-cleanup\7\faces`; `notes\_f2a\make_evidence.py:14` same) - the retired artifact is the reference the node-set test compares against, so pointing it at `templates\` would be the bug; 1 is `scripts\make_b2_lora_template.py` whose `DST` = `templates\b2_fc_sydney_lora.api.json`, a file that **still exists**, so it references no archived file today - it becomes a conflict only if F2b's v1 move is executed. 0 hits in `.pi\agent\skills` and `C:\AI\render`. |
| 4 "one commit in C:\AI\community pushed to gitea" | **not met by this item** | phase 2's only template commit is agy's `25e403c`, already on `gitea/master` (`git branch -a --contains 25e403c` → `remotes/gitea/master`). F2b's own commit would be the b2.README section + the 3 files; not written (gated). |
| "Add a short section to `templates\b2.README.md` with the one command shape" | **not built** | `rg -n -- '--lora\|--strength' templates\b2.README.md` = 0 hits; `git log --oneline -1 -- templates\b2.README.md` = `bb1290f` (2026-10-30). Awaiting the same GO so it documents a recipe with a proved OBJECTIVE, not an unrendered one. |

## Numbers in the item that are stale (stated, not hidden)
- **"the 24 non-Sydney copies" is 23.** `git ls-tree --name-only 25e403c^ templates/faces/ | grep -c 'FC_.*\.api\.json$'`
  = **23**, and the deleted list is 23 names (FC_ACE..FC_ZOEY). `templates\faces\README.md` states why: "**24 templates on
  disk, 23 in git**: `.gitignore` line 75 (`*sydney*`) keeps that one path out of the repo." So 24 = 23 non-Sydney + FC_SYDNEY;
  the item, its F2a facts and v2 U7 all carry the on-disk count. Count **tracked** and **untracked** separately next time.
- The item's `faces\README.md` "if it is a per-face index" move: that file is the per-face **builder doc** (generator,
  trigger-word map location, the 0.7 strength measurement, the FIT record, the regenerate command). Moving it would strand the
  generator `make_b2_lora_template.py`. Left in place, flagged for Max/Derrick, not moved.

## Commands run (all read-only)
```
ls C:/AI/community/templates ; ls C:/AI/community/templates/faces
git -C C:\AI\community show --stat --name-status 25e403c
git -C C:\AI\community ls-tree --name-only 25e403c^ templates/faces/ | grep -c 'FC_.*\.api\.json$'   # 23
stat -c '%s %y %n' templates/faces/FC_SYDNEY.api.json                                                # 21171 2026-11-03 19:01:34
rg -l 'FC_[A-Z]+\.api\.json|b2_fc_sydney_lora' C:/AI/community C:/Users/derek/.pi/agent/skills C:/AI/render   # 7 files
rg -n -- '--lora|--strength' C:/AI/community/templates/b2.README.md                                    # 0
ls C:/AI/locks ; python C:/AI/community/scripts/comfy_ctl.py status   # no lock; guard (0, ['IDLE']) 18:37:16 CT
python -m pytest tests/test_b2_lora_param.py -q    # 5 passed, 0 skipped (the archive fixture resolves)
git -C C:\AI\community push gitea master            # rc 128, HTTP 502
```

## Gate state for the items behind this one
GPU gate is **open** right now: no `C:\AI\locks\gpu-render.lock` (locks dir = `_removed`, `gpu-render.collected`) and
`comfy_ctl.py status` 18:37:16 CT `guard=(0, ['IDLE'])`. F2a's two cells are the only thing standing between F2b and its
OBJECTIVE proof, and they need one word from Derrick.

## Network, measured per target (the 12:56 CT finding is now narrower)
`git push gitea master` in `C:\AI\community` and `git push origin master` in `C:\AI\fleet-brain` both return **HTTP 502 from
`qnap.tailf242b2.ts.net`** - DNS, TLS and the reverse proxy answer (an HTTP status is an answer), so the tailnet path is up and
**Gitea itself is unhealthy on the QNAP**. Not a network outage and not a firewall: report the 502, restart/health-check of the
QNAP Gitea container is Household's. Commits stay local and push themselves when Gitea answers 200: `C:\AI\community` is
**17 ahead** of `gitea/master`, `C:\AI\fleet-brain` **3 ahead** (this item's records included).

## Safety
No GPU, no render, no lock, no model load, no successful HTTP, no process touched (the main loop pid 36992 untouched), no
config write, no download, no install, nothing deleted, no `.bak`, no dated copy, no `git add -A`, no force-push, no GitHub,
no file under `C:\Users\derek\sydney\` opened/listed/read, no prompt text read. Files touched by this pass: this record,
`notes\needs_derrick.md` (addendum under the 13:00 F2a card, no new ask), `notes\actions.log`, `fix_plan.md` (checkbox),
`notes\progress.md`, the brain status mirror and the job's one existing learning file (merged, not new).
