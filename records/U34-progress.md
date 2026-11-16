# U34 rollout progress (Derrick t1837u/t1838u; plan U33). Updated by Max Architect.

Resume rule: read this file, then continue at the first step not marked DONE.

| Step | Status | Notes |
|---|---|---|
| 1 Git + Gitea | DONE 21:05 CT | Repos init/commit: ~/evo-x3 ae970d8, ~/AI/forge e9730b3, ~/AI/render f4a4802, ~/AI/community d1505a5 (14 items by explicit path). gitleaks clean. Token (evo-x3, scope write:repository) cannot create repos -> pushed as branches of derrick/evo-x3: x3-pi-config, x3-forge, x3-render. community x3-linux pushed to derrick/alienpc-community via box relay (/workspace/maxops/x3/relay). Branch protection: no admin rights. etckeeper /etc stays local (tracks shadow, host keys, wifi PSK); sanitized host copies in config/host via scripts/sync-config-copies.sh. |
| 2 Wait U21 (agy 125527) | WAITING | Box waiter /workspace/maxops/x3/wait-u21.sh. At 05:00 CT proceed with non-model steps only. |
| 3 Plan steps 1-8 | TODO | backups *.bak-<ts>-u34 |
| 4 Phase 6 cutover | TODO | only when AlienPc extend-test render not mid-run |
| 5 Cleanup + QNAP backup | TODO | |
| 6 Commit/push + U34-rollout-done record | TODO | |

## Half-applied changes
None.
