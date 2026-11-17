# RESET BRIEF for Forge (Oct 23, 2026, CT)

You (Forge) own and edit every file in this reset yourself: ralph.ps1, PROMPT.md, AGENTS.md, TASKS.md / fix_plan.md, the guard extensions in C:\AI\director\.pi\extensions\, and comm.py. Nobody else edits them for you.

## Derrick's words (CT, Oct 23)
- 7:21 PM: "I want community fucking settings stop adding your own shit"
- 7:22 PM: "I want community settings. Not him to inject anything. We test community stuff first, then once confirm working we can add stuff back."
- 7:28 PM (relayed by Alfred): "Yes, and Forge can edit comm.py but the adults-only check stays on."
- 7:19 PM, said directly: "forge should be able to edit the comm.py"

## Changes from the audit text below (these override it)
- **Youth guard (replaces audit items #9/#27 and the "edit-locked" wording).** Forge may edit comm.py. The adults-only/minors check must stay on and run before every render. test_p6_review.py (C:\AI\community\scripts\tests\test_p6_review.py) stays unchanged and must pass before every render, and comm.py (C:\AI\community\scripts\comm.py) must still be called in the render path. If an edit to comm.py makes that test fail, revert it.
- **Pre-reset archive.** Archive old copies to C:\AI\community\archive\2026-10-23-prereset\. Never delete anything (move or copy into the archive instead).
- **Secrets.** Keep the secrets deny. Keep git commits and pi's session JSONL.
- **Removals.** All other removals from the audit apply. That includes the git-push, finance/port-3100, llama-swap-busy, /upstream-/unload and comfy-restart-busy guards, "The GPU is off-limits", "Only edit files named in your task", the download card and the RL1 LoRA hold.
- **Add-backs.** Do no add-backs until the baseline test passes and Derrick okays each one, in the audit's order.
- **Content limits.** Two hard lines stay in PROMPT.md: "No secrets." and "Adults only, fictional, no real people."

## Audit section 4 (verbatim except the [CHANGED] lines)

## 4. Stock baseline, and the add-back order

**Baseline (Forge builds this, then tests it):**
1. **Loop.** A PowerShell port of snarktank ralph.sh, about 15 lines: `for ($i=1; $i -le $Max; $i++) { $o = Get-Content PROMPT.md -Raw | pi --print --provider llama-swap --model <model> --session-dir <dir>; if ($o -match '\bCOMPLETE\b') { break } }`. Nothing else.
2. **Agent.** Stock pi tools, with no `--exclude-tools` and no `--no-mcp`.
3. **Secrets.** pi-permission-system with `defaultPolicy: allow` and secrets-only deny rules (the current forge-policy file already is this).
4. **Youth guard.** [CHANGED per Derrick 7:19/7:28 PM CT: replaces #9/#27 and the "edit-locked" wording] Forge may edit comm.py. The adults-only/minors check must stay on and run before every render. test_p6_review.py stays unchanged and must pass before every render, and comm.py must still be called in the render path. If an edit to comm.py makes that test fail, Forge reverts it.
5. **PROMPT.md.** Huntley's shape: study specs/ and fix_plan.md, pick the single most important item, do it, run its test, update fix_plan.md, commit, and add learnings to AGENTS.md briefly. Plus two lines: no secrets; adults only, fictional, no real people.
6. **AGENTS.md.** Forge-owned: how to build, run and render, plus learnings. No Max rules.
7. **Plan.** Forge regenerates `fix_plan.md` from Derrick's current goals (the ALI-163/173/180–184 outcomes), replacing the 131 KB TASKS.md. The old file is archived, not deleted.
8. **Record.** pi's own session JSONL (`--session-dir`), plus Forge's own commits.

**Baseline test (it must pass before any add-back):**
- 3 consecutive clean passes on real plan items.
- 1 render end to end, with Forge driving ComfyUI itself.
- A secrets probe on a dummy test file is denied.
- [CHANGED] test_p6_review.py passes and its SHA256 is unchanged (C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213), and comm.py is still invoked before renders.

**Add-back order (one at a time, each after a passing re-test, using the community version first):**
1. **Action log.** First check whether the pi session JSONL already covers it. If Derrick still wants `forge_actions.log`, add the smallest post-pass extract from the JSONL.
2. **GPU lock.** First llama-swap's own `ttl`/`groups` and ComfyUI `/free` or `--disable-smart-memory` (documented). The custom gpu_guard and restart-busy checks come back only if a collision is actually seen.
3. **Per-pass timeout.** Only if a hung pass is observed (frankbria-style setting).
4. **Circuit breaker.** Only if the loop repeats the same failure (frankbria).
5. **GPU-minute and job caps.** Only if Derrick asks for a spend cap.
6. **Max event webhook.** Optional, for Max's status.

Nothing else comes back without an observed failure and Derrick's yes.


## Audit section 5 (verbatim except the [CHANGED] wording)

## 5. Removal list Max would hand Forge (short)

> Forge: reset to stock. You own every file below; change them yourself, commit after each step, and archive old copies under `C:\AI\community\archive\2026-10-23-prereset\`.
> 1. Replace ralph.ps1 with a ~15-line snarktank-style loop (iteration cap + COMPLETE exit, stock pi flags). Drop GuardWait, timeout, harness commits, py_compile/json/pytest checks, scope/workflow/prot snapshots (including the comm.py restore; see the youth-guard change), JOB_REQUEST runner, GPU/job caps, breaker, CUTOFF, no-progress, STOP_RALPH, GUARD_REQUEST, Send-MaxEvent, PassLog.
> 2. Guard: keep only secrets + the youth-guard piece [CHANGED: comm.py is editable by Forge; only test_p6_review.py stays unchanged, and the adults-only check stays on before every render]. Remove git-push, finance/port-3100, comfy-restart-busy, llama-swap-busy, /upstream-/unload, the K4 allowlist fallback, protected-paths.ts from your load.
> 3. Rewrite PROMPT.md in Huntley's shape; keep two hard lines (no secrets; adults only, fictional, no real people).
> 4. Rewrite AGENTS.md: delete "GPU is off-limits", "Scope", harness-restore and budget sections; keep your commands + Learnings, under 40 lines.
> 5. Archive TASKS.md; generate a lean fix_plan.md from the open goals.
> 6. Run the baseline test (3 clean passes, 1 render you drive yourself, secrets probe denied, test_p6_review.py passes with hash unchanged, comm.py still invoked before renders). Report results; no add-backs yet.

## How to run this session (practical notes)
- The old loop (ralph.ps1 PID 11380) was stopped with STOP_RALPH between passes before this session started. Archive STOP_RALPH with the rest.
- Your provider/model, as the old loop called you: `--provider llama-swap --model coding_swift15_iq3s` (llama-swap on 127.0.0.1:8080). Keep `--session-dir C:\Users\derek\5slock\ralph-community\sessions`. Drop `--exclude-tools` and `--no-mcp`.
- Commit after each step in both repos you touch (C:\Users\derek\5slock\ralph-community and C:\AI\community, plus C:\AI\director if you change the extensions). Local commits only.
- Secrets probe: create a dummy file that matches your secrets deny rule (for example a `.env` with a fake value), try to read it through your tools, and record that it was denied.
- Render: drive one render end to end yourself through ComfyUI, with comm.py run first and test_p6_review.py passing first.
- For the 3 clean passes: after the reset is committed, launch the new stock loop yourself detached (for example `Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\Users\derek\5slock\ralph-community\ralph.ps1','-Max','3' -WindowStyle Hidden`), write its PID to `C:\Users\derek\5slock\ralph-community\logs\stock_loop.pid`, and end this session. Do not wait inside this session for the loop.
- Write your results to `C:\Users\derek\5slock\ralph-community\BASELINE_TEST_20261023.md`: what you changed (commit hashes), line counts of ralph.ps1 / PROMPT.md / AGENTS.md, the archive listing, the secrets-probe result, the render result with output paths, the test_p6_review.py result and SHA256, where comm.py is called in the render path, and the stock loop PID. Leave the 3-pass result as "pending" if the loop is still running.
