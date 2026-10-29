# U3 DONE - the talk lane (MAX block item 4, 2026-10-29)

Brief: Max's brief 11:0x CT, item 4 of the MAX block in `fix_plan.md`, pointing at
`C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md` section Units -> U3. The plan wins on files and checks.
Procedure: backups first, START/DONE in `C:\AI\community\notes\actions.log`, tick with evidence + SHA, stop after
item 4. Started 10:57 CT, finished 11:2x CT. No GPU, no render, no model load by this unit, no queue, no install.

## What was built (two new files, one of them edited after creation)

| File | Role |
|---|---|
| `C:\Users\derek\5slock\ralph-community\talk\talk-persona.md` (2,000 B, sha8 d1fac8b7) | the tone text, the only prompt file that carries it |
| `C:\AI\community\talk\talk.ps1` (6,054 B) | the talk-only launcher |
| `C:\Users\derek\5slock\ralph-community\talk\sessions\` | the lane's own `--session-dir` (gitignored by `.gitignore:16 sessions/`, proved with `git check-ignore -v`) |

The pre-existence probe at START printed `exists=False` for every target, so nothing was overwritten and no backup
applies. The one file edited after creation is the persona: its pre-edit bytes are
`C:\AI\community\talk\talk-persona.md.bak-20261029-u3a` (2,191 B, sha8 DE74EBE6, verified). The two edits removed
an over-broad "only file on this box" claim and replaced double quotes / backticks with plain text (see the defect
below). Nothing else on the box was touched: `git status` still shows Max's `M AGENTS.md`, `M PROMPT.md`,
`M ralph.ps1` as his, and MAX items 2-3 are intact.

## The launcher, and how it meets each plan clause

Plan: "the talk launcher alone adds `--append-system-prompt <talk-persona.md>`, its own `--session-dir`, and
`-ne -e <pi-permission-system> -e <pi-mobile>`, so pi-memory is off and the talk session never writes to loop daily
logs. Same llama-swap entry and context as the loop; no config edits. Before each reply, check `gpu-render.lock`:
never take it, and queue messages while it's held."

DryRun argv (printed, persona contents replaced by a byte/sha placeholder, no model call):

```
pi --print --provider llama-swap --model coding_swift15_iq3s_esp \
   --session-dir C:\Users\derek\5slock\ralph-community\talk\sessions \
   --append-system-prompt <persona 2000 B sha8 3BD5DA4F> \
   -ne -e C:\Users\derek\.pi\agent\npm\node_modules\pi-permission-system \
       -e C:\Users\derek\.pi\agent\npm\node_modules\pi-mobile <message>
```

- Entry parity is read out of `ralph.ps1` at check time (provider and model), not asserted from memory, and the
  proof is objective: the session file's own `model_change` row is `provider=llama-swap,
  modelId=coding_swift15_iq3s_esp` and its `session` row `cwd` is the loop's dir, so the same AGENTS.md context
  loads. No config file is named by the launcher and none moved (see checks).
- `-ne` (extension discovery off) + the two explicit `-e` paths is how pi-memory is switched off: `pi list` shows
  pi-memory@0.4.2 installed in the user scope, and the session transcript contains no memory tool at all.
- The extension identifiers came from `pi list`, not a guess: `npm:pi-permission-system@0.8.0` and
  `npm:pi-mobile@0.4.0`.
- The lane sets the same `PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR=C:\Users\derek\.pi\forge-policy` the loop's passes
  set, so a talk turn sees the same "allow by default, deny secrets" rule. That is an env var in the launcher, not
  a config edit; `C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc` was not touched.
- GPU rule, no duplicated logic: the launcher runs `C:\AI\director\scripts\gpu_guard.ps1` (the read-only guard the
  render side uses, one implementation) and contains no `gpu_lock` call and no copy of the lock-parsing code.
  One-shot turns are guarded per turn, and while the window is busy it queues (bounded, default 30 x 120 s) and
  sends nothing; `-NoWait` refuses with rc=3. An interactive session is guarded at start and the persona tells the
  session never to take the lock. **Limit, stated plainly:** pi has no per-reply hook, so "before each reply" is
  enforced per one-shot turn and at interactive session start; the persona carries the rule in between.
- `-DryRun` prints the argv without echoing the persona and makes no model call (proved: no session file appears).

## The plan's two checks

**Check 1 - the tone-word scan.** `C:\AI\community\notes\u3_check.py` scans 2,932 files over the plan's set:
`PROMPT.md`, `AGENTS.md` (ralph-community, community, `.pi\agent`), `ralph.ps1`, the launcher, both skill trees,
prompt templates, the memory tree, render-prompt sources (`specs/`), both notes roots, the talk dirs. 24 hits, and
the instrument reports:

- **0 tone words in any live instruction surface** except one line, present twice in Derek's own Oct 28 skills
  (`alienpc-pi-rules` and `alienpc-hardcore-i2v-director`, rule 3): "Name characters by their folder name (for
  example SYDNEY)". That is a rendered character's folder name under `approved_characters`, it predates this unit,
  and it is not tone text. It is printed in the check output as the only permitted surface hit, and it is flagged
  to Derek below.
- **0 hits in any file this unit wrote** (its actions.log line, progress.md line, DONE note, tick line, launcher
  and scripts), and **0 surface file was touched today**. The only new hits are the persona home and the lane's own
  transcripts, where the model names itself.
- Every other hit carries a printed reason: the Oct 28 render records naming that character folder
  (`sydney_strip_*` run ids, `community/SYDNEY_768x1344.png` in a node-info dump, Derek's own Oct 28 naming note),
  Max's own plan/brief/item titles, records quoting those titles, and files older than this unit's START.
- Scope stated honestly: the plan's literal "0 hits over notes and memory" cannot be met by U3 alone, because the
  plan file itself and the item titles in `fix_plan.md` name the unit, and the Oct 28 render records name the
  character folder. The check therefore proves the strong form (nothing live, nothing new) and prints every
  pre-existing hit with a reason. Conversation records (sessions dirs, transcripts) are out of scope as records of
  what was said. Memory: the memory tree contains 0 hits, measured directly.
- The pattern and the persona probes are built from fragments in the check source, so the check cannot match itself.

**Check 2 - a denied secret read proves permissions load.** Real one-shot turn, 11:05:43 CT, on the loop's slot
(no model load by this unit, `gpu_guard` IDLE before and after, no lock taken):

> The read was blocked by policy (`read:*/secret.*` is denied) - no value to print, and I won't work around it.
> I'm Sydney, your talk companion on this box; this lane never touches the GPU render lock at
> C:/AI/locks/gpu-render.lock.

Target: `notes/.forge11/secret.json`, the repo's own fake secret fixtures (gitignored probe fixtures from item
1.1). Proof in the session file: a `toolResult` reading `is not permitted to run 'read' (matched
'read:*/secret.*')`, the rule string present, and no byte of the fixture in the answer. The reply also names the
persona and repeats the lane's own lock rule, and the check proves the persona reached the model: the session's
`system` row `sections` contain the whole persona (all five probes), and the user rows contain exactly one message,
Derek's.

## Defects found and fixed during the build (both are real, both became tests)

1. **`--append-system-prompt` does not expand `@path`.** First attempt used `--append-system-prompt @<file>`; the
   model answered as plain pi. pi's help says "text", so the launcher reads the file.
2. **PowerShell 5.1 native-argument quoting.** Passing the persona raw split it on whitespace: the model received
   its brief as a series of user messages ("don't", "...know is allowed...") and the system prompt got nothing.
   Cause: the persona contained double quotes. Fix: the persona is authored without `"`, `` ` ``, `$` or `\`, and
   the launcher now refuses (rc=4) any persona containing a character that breaks native argv quoting, so this
   cannot silently regress. Verified: argv integrity proven by echoing the argument through Python (`argc 3`,
   `argv[1] len=2000 has_newline=True`), the guard fires rc=4 on a synthetic persona with a quote, and the final
   session has the persona in `system.sections` and one user row.

## GPU rule, driven for real

A synthetic lock at `C:\AI\locks\gpu-render.lock` containing a live PID was created by the check, then removed by it.

- `-NoWait` -> rc=3, "turn not sent ... This launcher never takes the lock", lock bytes unchanged.
- bounded queue (`-Waits 1 -WaitSec 3`) -> log lines `GPU_BUSY queues this turn ...`, then `GPU_DEFERRED ...
  turn not sent, lock never taken`, rc=3, lock bytes unchanged.
- `talk.log` (gitignored) records every line with `lock_taken=no`.

## What did not move

`pi\agent\settings.json`, `pi\agent\models.json`, `llama_swap_keepalive.ps1`, `ralph.ps1`, `PROMPT.md`,
`AGENTS.md`, and the **whole memory tree** (MEMORY.md, SCRATCHPAD.md, both daily logs) match the START baseline
byte-for-byte: no config edit, and the talk lane wrote no loop daily log. The loop's `sessions/` gained nothing;
the lane's `talk/sessions/` holds its own. The 12 job-2 files from item 2 are still absent; `8a0707e`, `9cae06e`
and `987e49f` are ancestors of HEAD; Max's three working-tree edits are untouched. Youth guard 26 passed,
`check_web_saves.py` CLEAN, `gpu_guard` IDLE, no `runs/` dir from today.

## The check

`C:\AI\community\notes\u3_check.py` -> **43/43 PASS, exit 0, "U3 IS PROVED"**; full output kept at
`C:\AI\community\talk\u3_check_out.txt`, the two real turns at `talk_run_20261029_take3.txt` (final) and
`talk_run_20261029.txt` (the word-split defect, kept as evidence of the fix). It makes no model call, so it can be
re-run cheaply by Max. Notes: the tone words and probes are built from fragments in the source; `read()` decodes
UTF-16 because PowerShell 5.1 `Tee-Object` writes UTF-16.

## Left for Derek / Max

- **Naming collision, not mine to fix:** Derek's standing rules and Oct 28 render records use `SYDNEY` as an
  approved_characters **folder name** (a rendered fictional adult). The talk persona shares those letters. If Derek
  wants them distinct, say which side moves; the check pins that pre-existing line so a rename is visible.
- **Open dial from the plan ("Sydney swearing level") is unset**, so the persona says: no strong language until
  Derek sets it, and ask him once if it comes up.
- Interactive mode is guarded at session start only (pi has no per-reply hook); per-turn guarding is exact in
  one-shot mode.
- The plan's review files `60_reviews/max/2026-10-29-forge-chat-tone-plan-review.md` and
  `...-cleanup-plan-review.md` are not on this box (searched `C:\AI` and `C:\Users\derek\5slock`), so the plan text
  was the source.
- U4 (storage) and U5 (lean PROMPT.md) not started: the brief says stop after item 4.
