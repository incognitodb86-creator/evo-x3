# U34: U33 plan rollout finished (2026-11-16 07:40 CT)
Owner approval: Derrick t1837u (8:59 PM CT 11/15), "implement the plan with your recommendations"; t1844u "You do it".
Done by: Max Architect. Rollback for each step: records/U34-rollback-notes.txt, plus a `.bak-*-u34` file beside each edited file.

## Steps
| Step | Result |
|---|---|
| Gitea + git | PASS. Pushed as branches of derrick/evo-x3 (x3-pi-config, x3-forge, x3-render) because the tokens can't create repos. Community is on alienpc-community branch x3-linux. Branch protection needs Derrick. |
| U21 benchmarks | PASS (record U21-benchmarks-20261115.md). B4 blind scores from Prompt maker are still pending. |
| U32 deep-research bake-off | PASS (record U32-…). Pick: local-deep-research is the default, GPT-Researcher the alternate. |
| llama-swap | PASS. The Gufo flash-next slot is archived (u34/flash-next-gufo-slot-archived-20261116.yaml; weights left in /srv/models/flash-next). flash-next-sub and gemma4-heretic-sub use setParamsByID. Thinking probe verified. Pool test 4/4 at a parallel limit of 4. |
| pi config | PASS. Qwen card sampling, flash-next-uncensored added, Forge thinking medium. |
| Host hygiene | PASS. Cockpit is off; sshd has X11Forwarding no and MaxAuthTries 3; unused VM, iSCSI, multipath and modem services are disabled; amdgpu.gttsize is removed (GTT is still 120 GiB). |
| SearXNG | PASS. Permanent user quadlet on 127.0.0.1:8888; pi web-search points at it. |
| Reboot | PASS after a detour. The 06:53 reboot landed in Windows because BootOrder had been reset. Derrick set BootOrder 0003,0000,0001 and added fedora-first-boot.service/.timer (copied into config/). Post-reboot checks all pass. |
| Phase 6 chat cutover | DONE in config, NOT live. AlienPc models.json evo-x3 provider uses the X3 ids. pi_herdr_at_logon.ps1 sends Sydney/Render to evo-x3/gemma4-heretic and Forge to evo-x3/flash-next with thinking medium (alienpc-director b5d964a). One-shot pings PONG: 16 s, 2 s, 34 s. The live herdr panes were not restarted: that would end live chats, and the herdr server started 11/11 doesn't have EVO_X3_LLM_KEY in its environment. The change takes effect at the next logon or herdr restart. The phone stays on AlienPc herdr. |
| Cleanup | PASS. Files archived, nothing deleted: ~/evo-x3/_archive/u33 (24 MB, includes scratch/u31-render-sub with hdr at 0600), /etc/evo-x3/_archive (20 old yaml baks), ~/.pi/agent/_archive (11 baks). stage-src kept (the bench uses its U12 fixture). |
| Final QNAP backup | PASS. /mnt/qnap/pi-drop/evo-x3-rollback/u34-final-20261116-0733 is 7.6 GiB: rootfs.tar.zst (15.7 GiB uncompressed, 462k entries, ACLs and xattrs kept), the open-webui volume, rpm/lsblk/findmnt manifests, and SHA256SUMS. Checked on QNAP with sha256sum -c: all OK. Not included: /srv (weights and bakeoff), container layers, caches, rocm, and secrets (/etc/evo-x3 env/cred files, shadow, SSH host keys, Wi-Fi). A local copy is in /var/backups/evo-x3. |

## Weights left in place for Derrick to decide
- /srv/models/flash-next: Gufo Q4, 107 GiB, slot archived.
- /srv/models/qwen27b/Qwen3.8-27B-UD-Q4_K_XL.gguf: 17 GiB.
- /srv/models/gemma4-heretic/…mmproj-Q8_0.gguf: 770 MiB.
- /srv/bakeoff: 341 GiB.
- ~/rocm: TheRock 7.14.1, 9.9 GiB; nothing references it.

## Incidents
- The SearXNG secret_key was pushed in 5c77777. The key was rotated and the file is now ignored. The old, dead key is still in Gitea history.
- Reboot landed in Windows; see the Reboot row above.
- The first backup run (07:32) was aborted because its unanchored tar excludes would have skipped dirs such as drivers/media. It was rerun anchored. The partial file is in /var/backups/evo-x3/_aborted-u34-final-20261116-0732 (8 GB, root-only) and can be archived or removed on Derrick's OK.

## Open items for Derrick
- Restart the herdr panes (or log off and on) to make the Phase 6 cutover live.
- B4 blind scores, then the Heretic Q8 vs Q4_K_M decision.
- Open WebUI RAG embeddings are not switched.
- Repo creation and branch protection in Gitea.
- Stale tailnet devices.
- Uninstalling Windows on the X3: his idea, not acted on. It needs his explicit decision. The BootOrder and first-boot guard are in place.
