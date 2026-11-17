# Rollback list - Forge over-engineering fixes, 2026-10-26 (Max Architect 2)

Reason: Derrick 1:31 PM CT Oct 26: "when the render is done, you make these fixes and then audit them" (audit /workspace/cos/audits/2026-10-26-forge-overengineering-audit.md, 53286ef). Archive only; nothing was deleted.
Undo one fix with `git -C <repo> revert --no-edit <commit>` (newest first if undoing several in one repo).

| Fix | Repo | Commit | Undo |
|---|---|---|---|
| 0 track gpu_guard/gpu_lock | C:\AI\director | e6f6e41 | git revert e6f6e41 (files stay on disk) |
| 1 caption battery archived | C:\AI\community | 73ecdd3 | git revert 73ecdd3 |
| 2 per-pass checks (ralph) | ralph-community | c9881e7 | git revert c9881e7 |
| 2 per-pass checks (community) | C:\AI\community | 2a1fa28 | git revert 2a1fa28 |
| 3 card / fact layer | C:\AI\community | 7dea268 | git revert 7dea268 |
| 4 per-test builders | C:\AI\community | e9fb5a2 | git revert e9fb5a2 |
| 5a PROMPT.md stock path | ralph-community | 91ea456 | git revert 91ea456 |
| 5b fix_plan.md shrink | ralph-community | a88f931 | git revert a88f931 (full plan also at _archive/2026-10-26-overeng/fix_plan_full_20261026.md) |
| 5c AGENTS.md learnings out | ralph-community | 7c1941a | git revert 7c1941a |
| 6 Switchyard-era scripts | C:\AI\community | d7d96aa | git revert d7d96aa |
| 7 ralph.ps1 circuit breaker | ralph-community | 92f53f2 | git revert 92f53f2 |
| 8 run_graph_job budget counter | C:\AI\community | 17e932f | git revert 17e932f, then move archive/2026-10-26-overeng/p7_budget.json back to ralph-community\logs\ |
| 9 face crop | C:\AI\community | 076c3d9 | git revert 076c3d9 |
| 10 probes / one-offs | ralph-community | 70f0644 | git revert 70f0644 (4 gitignored .log files were moved by hand: move them back from _archive/2026-10-26-overeng/notes/) |
| 11 skillspector package | ralph-community (record) + C:\Users\derek\.pi\agent\settings.json | 41dcee5 | copy settings.json.bak-20261026-overeng over settings.json |

Untracked files moved by hand into the archive (now committed there): notes/tr5s_caption.py, card_vl2_build.py, card_vl2_author.py, card_vl2_patch_base.py, tr5s_card_build.py, tr5s_facts/, tr5s_graph_build.py.

Left alone on purpose: the 10+ Disabled scheduled tasks (agy-harness-gates-2026-10-10, agy-ui-settings-2026-10-10, ForgeAgyMonitor, ForgeHarnessGates-2026-10-10-v2, ForgeRalphLoop, ForgeRunAllAfter-2026-10-11, ForgeTeachRound-2026-10-10, ForgeTeachRound-2026-10-10-r2, SY_AgyFix, SY_AgyFix2, SY_Capa2, SY_Night, SY_Phone, SY_Runner) and the disabled director pi extensions (C:\AI\director\.pi\extensions\*.disabled-2026-10-25 + .bak files).

Protected-file sha256: protected_sha256_before.txt / protected_sha256_after.txt in this folder (all match except run_graph_job.py: 17 budget lines removed).