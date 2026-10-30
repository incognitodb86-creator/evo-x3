# Forge brief 7: archive probe_submit.py (simplify cut #15 only)
Derrick approved 2026-10-30 8:05 AM CT: "Yes, go: archive probe_submit.py and fill the terrace plan gaps".
Plan: C:\AI\community\plans\2026-10-30-0800-forge-simplify-plan.md (box: 40_projects/max-fix-tests/plans/), cut #15. **Only cut #15 is approved; do no other simplify cut.**
No renders, no queue, no GPU, do not touch C:\AI\locks\gpu-render.lock, delete nothing.

1. Record `Get-FileHash` (sha256) of `C:\AI\community\scripts\probe_submit.py` (39 lines).
2. Move it (move, not copy, not delete) to `C:\AI\_archive\2026-10-30-forge-simplify\scripts\probe_submit.py` (create the folder if missing). Re-hash it there; the sha must match step 1.
3. Run `rg -n probe_submit C:\AI\community C:\Users\derek\forge` and list every caller or reference. Report any that would break; do not fix them.
4. Confirm that `comm.run()` in comm.py and `run_graph_job.py` still call `guard_ok` (the adults-only check); give file and line numbers.
5. Write `C:\AI\community\notes\2026-10-30-brief7-probe-submit-DONE.md` with: the archive path, both sha256 values, the rg output, and the guard_ok lines. Then stop. Max checks.
