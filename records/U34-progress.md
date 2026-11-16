# U34 rollout progress (Derrick t1837u/t1838u; plan U33). Updated by Max Architect.

Resume rule: read this file, then continue at the first step not marked DONE.

| Step | Status | Notes |
|---|---|---|
| 1 Git + Gitea | DONE 21:05 CT | Repos init/commit: ~/evo-x3 ae970d8, ~/AI/forge e9730b3, ~/AI/render f4a4802, ~/AI/community d1505a5 (14 items by explicit path). gitleaks clean. Token (evo-x3, scope write:repository) cannot create repos -> pushed as branches of derrick/evo-x3: x3-pi-config, x3-forge, x3-render. community x3-linux pushed to derrick/alienpc-community via box relay (/workspace/maxops/x3/relay). Branch protection: no admin rights. etckeeper /etc stays local (tracks shadow, host keys, wifi PSK); sanitized host copies in config/host via scripts/sync-config-copies.sh. |
| 2 U21/U32 | DONE 06:45 CT | U21 record (no reruns needed) + U32 record written. U32 pick: local-deep-research default, GPT-Researcher alternate. Stale Antigravity lease released 06:30; Max lease held. |
| 3 Plan steps 1-8 | DONE except reboot (07:00 CT) | Step2 Halogen kept, Gufo slot archived (u34/flash-next-gufo-slot-archived-20261116.yaml). Step3 thinking: gemma4-heretic-sub forced off (setParamsByID enable_thinking false; verified 0 reasoning even when request asks on), flash-next-sub effort low (verified). Step4 pool test 2x150K+2x24K concurrent 4/4 pass, pool 67% -> keep limit 4. Step5 Qwen card sampling (thinking set, presence 0) in pi. Step6 pi: +flash-next-uncensored, Forge thinking medium; render-pi.sh and forge-pi.sh one-shot PONG. Step7 Open WebUI sees all 7 ids; RAG embeddings not changed (optional). Step8 host hygiene done 06:26; gttsize removed, reboot pending. SearXNG permanent: user quadlet searxng 127.0.0.1:8888, pi web-search.json -> 127.0.0.1. SearXNG secret_key was committed in 5c77777 by mistake -> rotated + untracked (d4254a6). |
| 3b Reboot | DONE 07:25 CT | 06:53 reboot landed in Windows (BootOrder reset); Derrick picked Fedora, set BootOrder 0003,0000,0001 and added fedora-first-boot.service/.timer. Post-reboot: gttsize gone, GTT 120 GiB, llama-swap/Open WebUI/SearXNG/tailscaled/timers active, no failed units, sshd X11 no/MaxAuthTries 3, render-pi + forge-pi PONG. |
| 4 Phase 6 cutover | TODO | only when AlienPc extend-test render not mid-run |
| 5 Cleanup + QNAP backup | TODO | |
| 6 Commit/push + U34-rollout-done record | TODO | |

## Half-applied changes
None.

## 07:30–07:35 CT — Phase 6, cleanup, backup started
- Phase 6 (AlienPc): models.json evo-x3 provider → X3 ids (bak models.json.bak-20261116-072818-u34). One-shot pings PONG: Render gemma4-heretic 16 s, Sydney model 2 s, Forge flash-next/medium 34 s.
- C:\AI\director\scripts\pi_herdr_at_logon.ps1: Sydney/Render → evo-x3/gemma4-heretic, Forge → evo-x3/flash-next --thinking medium. Parse check 0 errors. Bak .bak-20261116-073004-u34. Committed b5d964a, pushed (alienpc-director, branch selfheal-2026-10-14).
- Live herdr panes NOT restarted (would cut live chats; herdr server started 11/11 lacks EVO_X3_LLM_KEY env). Takes effect on next logon / herdr restart.
- Cleanup → ~/evo-x3/_archive/u33 (24 MB) + /etc/evo-x3/_archive (20 old yaml baks) + ~/.pi/agent/_archive (11 baks). stage-src kept (bench uses U12 fixture). Commit bcc6f42. Forge launcher synced, x3-forge 330dd23.
- Final backup: first run aborted at 07:33 (unanchored tar excludes would have skipped dirs like drivers/media); relaunched 07:33 with anchored excludes.
- 07:37 Final backup PASS: QNAP u34-final-20261116-0733, 7.6 GiB, sha256 verified.
- 07:40 U34-rollout-done record written; lease released.
