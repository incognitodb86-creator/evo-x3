# U34 rollout progress (Derrick t1837u/t1838u; plan U33). Updated by Max Architect.

Resume rule: read this file, then continue at the first step not marked DONE.

| Step | Status | Notes |
|---|---|---|
| 1 Git + Gitea | DONE 21:05 CT | Repos init/commit: ~/evo-x3 ae970d8, ~/AI/forge e9730b3, ~/AI/render f4a4802, ~/AI/community d1505a5 (14 items by explicit path). gitleaks clean. Token (evo-x3, scope write:repository) cannot create repos -> pushed as branches of derrick/evo-x3: x3-pi-config, x3-forge, x3-render. community x3-linux pushed to derrick/alienpc-community via box relay (/workspace/maxops/x3/relay). Branch protection: no admin rights. etckeeper /etc stays local (tracks shadow, host keys, wifi PSK); sanitized host copies in config/host via scripts/sync-config-copies.sh. |
| 2 U21/U32 | DONE 06:45 CT | U21 record (no reruns needed) + U32 record written. U32 pick: local-deep-research default, GPT-Researcher alternate. Stale Antigravity lease released 06:30; Max lease held. |
| 3 Plan steps 1-8 | DONE except reboot (07:00 CT) | Step2 Halogen kept, Gufo slot archived (u34/flash-next-gufo-slot-archived-20261116.yaml). Step3 thinking: gemma4-heretic-sub forced off (setParamsByID enable_thinking false; verified 0 reasoning even when request asks on), flash-next-sub effort low (verified). Step4 pool test 2x150K+2x24K concurrent 4/4 pass, pool 67% -> keep limit 4. Step5 Qwen card sampling (thinking set, presence 0) in pi. Step6 pi: +flash-next-uncensored, Forge thinking medium; render-pi.sh and forge-pi.sh one-shot PONG. Step7 Open WebUI sees all 7 ids; RAG embeddings not changed (optional). Step8 host hygiene done 06:26; gttsize removed, reboot pending. SearXNG permanent: user quadlet searxng 127.0.0.1:8888, pi web-search.json -> 127.0.0.1. SearXNG secret_key was committed in 5c77777 by mistake -> rotated + untracked (d4254a6). |
| 4 Phase 6 cutover | TODO | only when AlienPc extend-test render not mid-run |
| 5 Cleanup + QNAP backup | TODO | |
| 6 Commit/push + U34-rollout-done record | TODO | |

## Half-applied changes
None.
