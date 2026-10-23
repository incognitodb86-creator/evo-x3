# Forge self-diagnosis (append-only, PROMPT.md SELF-DIAGNOSE)

## 2026-10-23 ~14:05 CT (pass at iter 01 restart, after iter 03 SCOPE fail)
- Last 2 summary lines: iter 02 status=ok ticks=+1 wall=9.0m denies=7; iter 03 status=fail exit=0 ticks=+1 wall=9.1m denies=2 scope=1.
- What failed: iter 03 was stopped by the harness SCOPE check - the model edited C:\Users\derek\5slock\ralph-community\ralph.ps1, which the harness restored from git and wrote STOP_RALPH.
- Cause: PROMPT.md keeps ralph.ps1 / PROMPT.md / permission files as Max's, and AGENTS.md "## Scope" lists ralph.ps1 as out of scope; the pass treated PROMPT.md's "your own harness, guard and permission files" sentence as overriding that and touched ralph.ps1.
- Fix in reach this pass: do NOT touch ralph.ps1, PROMPT.md, TASKS caps' harness flags or any permission file; if a change there is needed write "[!] Max: <ask>" in notes and a line in notes\guard_requests.md. Self-diagnose with ralph.log + denies.log every pass and append here.
- denies.log does not exist in C:\AI\community\notes (checked 2026-10-23 14:05), so no pending denies to log; created self_diagnosis.md (it did not exist) and added the AGENTS.md Learnings line PROMPT.md requires.
- Task for this pass: R4H small prompt-LLM research (research only, no GPU, no downloads, no vision judge).
