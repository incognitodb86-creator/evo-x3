# Gufo Phase 1 RESULT — 2026-11-17 (Max Architect, executed directly; no agy)
Plan: fleet-brain 40_projects/compute-expansion/plans/2026-11-16-x3-halogen-to-gufo-plan.md rev 6 (t294s1023).
Authorized: Derrick 6:58-6:59 AM CT. Evidence dir: ~/evo-x3/records/gufo-phase1-20261117/ (owner-only).

## Bottom line
Gufo flash-next works and is fast (passes the speed bar, tools, verify-serve, 4-caller test), but U2's all-loaded memory
gate FAILED at both approved configs, so per the plan the live yaml was REVERTED to the fresh backup at 07:33 CST.
flash-next is on Halogen again (rollback drill passed). Decision needed from Derrick (see Questions).

## Units
- U0 PASS: U54 RESULT exists (records/U54-RESULT.md, 17:19 Nov 16). Lease: records/LEASE-x3-gufo-phase1-20261117.md (not pushed; Gitea read-only).
- U1 PASS: re-stat bytes match the plan (flash-next-halogen 119,434,404,084; uncensored-hgn 118,812,268,388; halogen-models symlink 30;
  flash-next 114,121,223,122; fn-uncens-iq4xs 102,516,594,412). U34 archive opened as reference only. Free disk now 565 GB (Huihui download in progress).
  Fresh backup: gufo-phase1-20261117/backup-20261117-070651-pre-gufo/ + /etc/evo-x3/llama-swap.yaml.bak-20261117-070651-pre-gufo
  (sha fd930cb7...). Secrets not copied; pane sessions/ and memory* excluded (Sydney rule).
- U1a PASS: no staged leftovers. llama-swap started 15:02:04 Nov 16, after the yaml's last write (14:59:41); no -watch-config;
  /running gemma cmd = yaml (-np 4 -c 524288); joycaption + ref2va-27b in /v1/models. np4: tagger ran 7,567 done / 20 HTTP_500
  (last 19:00 Nov 16) on np4 since 15:02 -> kept. Halogen all-loaded baseline: U1a-all-loaded-halogen.txt
  (FN+embed+JoyCaption+Ref2VA: GTT 55.6 GiB, MemAvailable 49.8 GiB; deltas embed 0.13, JoyCaption 9.36, Ref2VA 19.42 GiB).
- U2 FUNCTIONAL PASS / GATE FAIL -> REVERTED.
  * cmd `gufo serve llm` (gufo-runtime 0.34.0 @49b1fce4), no halogen image; /ready 200 via llama-swap; verify-serve no-key 401, LLM_KEY_BOX 200 (tailnet + loopback): U2-verify.txt
  * Tool chain 3/3 on 3 separate runs: U2-toolchain.txt, U2-tool-{1,2,3}.json
  * check_fn_cutover.py: YAML_OUTSIDE_FN_OK, context 262144, 0 MISMATCH, RESULT PASS (RULE8 display names recorded)
  * All-loaded gate: 2x262144 -> FN+embed MemAvailable 7.96 GiB, swap full (U2-all-loaded-2x262k.txt); JoyCaption (9.4) / Ref2VA (19.4) cannot fit.
    1x131072 fallback -> FN+embed 18.5 GiB, +JoyCaption 9.24 GiB (real load), Ref2VA would go below 0 (not loaded: OOM risk) (U2-all-loaded-1x131k.txt). FAIL both.
  * Found and fixed a Gufo blocker: every other slot mounts /srv/models with SELinux `:Z`, so any small-group container start relabels
    the tree and Gufo loses read access (AVC denied) -> "n-gram table read failed" on every request. Fix in the FN block only:
    `--security-opt label=disable`, mount `:ro` without Z. Verified: PONG before and after embed-small start, 0 new AVCs (U2-selinux-fix-test.txt).
    Ready-to-use candidates (fix included): gufo-phase1-20261117/llama-swap.yaml.gufo-candidate (2x262144) and .gufo-fallback-1x131k.
  * Revert + Halogen rollback drill 07:33: yaml sha back to fd930cb7, verify-serve 401/200, tools 3/3, halogen image running (U2-revert-and-rollback-drill.txt).
- U3 PARTIAL: Huihui v2 UD-Q4_K_XL-V2 @cbc7fba13f downloading to /srv/models/flash-next-uncensored-huihui-v2 (log u3-huihui/download.log,
  auto sha256 check at end; ~73/111 GB at 07:34). Load + n=3 probes NOT run (FN reverted; a standalone 100+ GiB load would compete with live Render/Sydney Gemma). Uncensored slot left on Halogen .hgn, unwired on Gufo.
- U4 PASS (on Gufo 2x262144, cap 6, max-pending 16): Forge parent (~16.7K prompt) + 3 flash-next-sub tool callers, n=3: zero 429, zero 503,
  all 12 calls OK; waiters' queue ~3.0-5.3 s (median ~4.6 s): U4-four-caller.txt. Tagger stopped for the window; Render swapped in between runs (Derrick active).
- U5 PARTIAL: pi 1.5.2 with Forge's agent dir -> flash-next and flash-next-sub answered PONG in 2.0 s on Gufo (pi-forge-agentdir-test.txt).
  Forge pane NOT relaunched (engine reverted; alias unchanged, nothing to reload). No soak.
- U5b HELD: renaming Halogen display names to Gufo would be wrong while Halogen serves. Pending the decision.
- U5a HELD (AlienPc copy), U6 HELD (no deletes; all .hgn trees present). Phase 2 not started.

## Speed (Gufo, measured 07:15-07:18 CST, U2-speed.txt, U2-bake.json)
- 32K prompt via llama-swap (pi path), n=3: prefill 1,563-1,596 tok/s, decode 51.4-52.6 tok/s, TTFT ~20.8 s.
- 32K direct :8081, n=2: prefill 1,592 tok/s, decode 51.6-52.6 tok/s. llama-swap adds nothing measurable.
- 18,253-tok bake-off fixture: TTFT 11.32 s (bake-off 11.26 s), long pass; prose decode 50.1 tok/s (bake-off 50.1). Bar (>=800 / >=35): PASS.
- Load 25-27 s.

## Speed root cause (Forge's 6-8 tok/s) — not the engine
Exclusive-group swap thrash: llama-swap main group is exclusive, and gemma4-heretic (u42 PixlStash tagger loop + Render) and flash-next (Forge)
alternated. Since 18:00 Nov 16: 31 flash-next loads + 30 gemma4-heretic loads, ~1 swap/minute 06:50-07:01. Each swap = engine reload
(~24 s Halogen) + full re-prefill of Forge's 77K context (~40 s) because the prompt cache dies with the process. Gufo would thrash the same way.

## Rollback (current state IS the rollback)
Restore /etc/evo-x3/llama-swap.yaml.bak-20261117-070651-pre-gufo, `sudo systemctl restart llama-swap`, verify-serve.sh. Done and verified 07:33.
To go to Gufo: install llama-swap.yaml.gufo-candidate (or -fallback-1x131k) the same way. Halogen image + both .hgn trees present.

## Questions for Derrick
1. All-loaded gate fails because Gufo holds all 106 GiB of FN weights in memory (Halogen pages 47.7 GiB from disk). Options:
   (a) go Gufo anyway and move joycaption + ref2va-27b out of the persistent "small" group into the exclusive main group (they swap FN out when used);
   (b) go Gufo at 1x131072 and accept JoyCaption-only co-residence (Ref2VA must swap);
   (c) stay on Halogen for now. (a)/(b) touch non-FN yaml blocks -> needs his yes.
2. Render on flash-next (Derrick t37u) works on either engine and removes the Forge/Render thrash; the tagger would still swap Gemma in for Sydney/tagging.
3. Apply `:z` (shared) instead of `:Z` on the other slots too? (Only FN fixed in the candidates.)

## Housekeeping
u42-pixlstash-tagger stopped 07:05-07:34 for the quiet window, restarted. Render/Sydney panes untouched. No renders, no git commits, no deletes.

## Addendum 07:38 CST — Render moved to flash-next (Derrick t37u), on Halogen
- Pre-checks 07:36: Render w3:p1 idle, gpu-render.lock free, no pipeline/queue processes.
- Backup: /home/evo/evo-x3/_archive/render-flashnext-20261117-073605/ (render-pi.sh, panes/render settings.json, models.json copy, 0700).
- Edits: ~/evo-x3/pi-chats/render-pi.sh default --model x3-local/gemma4-heretic -> x3-local/flash-next;
  /home/evo/.pi/panes/render/settings.json defaultModel gemma4-heretic -> flash-next, subagents.defaultModel -> x3-local/flash-next-sub.
  models.json unchanged (shared file already has flash-next). Sydney and Forge untouched.
- Render pane restarted 07:36 (Escape, /quit, Enter, herdr-panes.sh relaunched only render); footer shows "flash-next • medium";
  PONG answered in ~24 s (first call included the swap from Gemma).
- Not done: repo copy config/pi-evo/pi-chats/render-pi.sh still says gemma4-heretic (no commit made).

## Addendum 07:53 CST — Render + Forge on flash-next-uncensored (Derrick t41s2); Halogen vision tried and reverted (t45u)
- Backup: /home/evo/evo-x3/_archive/uncensored-move-20261117-074540/. render-pi.sh / forge-pi.sh default --model -> x3-local/flash-next-uncensored;
  panes/render + panes/forge settings.json defaultModel -> flash-next-uncensored, subagents -> x3-local/flash-next-uncensored
  (models.json has NO flash-next-uncensored-sub entry). Panes restarted 07:46 after idle/lock checks; both footers "flash-next-uncensored • medium".
  Forge answered PONG (24 s); Render answered (166 s incl. load) but its reply ran a bash tool and rambled, ending with PONG reasoning, not a clean PONG.
  llama-swap running after both pings: only flash-next-uncensored. Caveat: that slot has concurrencyLimit 1 in the yaml (not edited), so concurrent Render/Forge/subagent calls can get 429.
- Halogen vision (HALOGEN_VISION_TOWER=1 on the uncensored slot) was installed 07:51 and REVERTED 07:53 on Derrick's "not halogen... Gufo" before any image test;
  yaml restored from /etc/evo-x3/llama-swap.yaml.bak-20261117-075106-pre-uncens-vision, verify-serve 401/200. models.json not edited.
- Huihui v2 download finished 07:45:48, sha256 OK (4 shards). No mmproj on disk; the Huihui repo has mmproj-Qwen3.8-Flash-Next-BF16.gguf (907,543,008 B, not downloaded).

## Addendum 08:35 CST: Halogen uncensored slot fix (Derrick t48u) + official shared-host recipe (parent steer)
- 07:55 vision + concurrencyLimit 1->4 applied. Image alone OK (15 s); 3 parallel 200, 0 x 429. Then embed+joycaption+ref2va loaded and a 2nd image wedged the engine (compaction, then no PING for 180 s); the watchdog killed it at 08:01 (502).
- 08:02 removed vision and kept cL4. The restart hung at "reserving the KV pool" (fragmented host memory). Recovered with no reboot at 08:17: stopped the small group, drop_caches + compact_memory; GTT went back to 0.03 GiB and uncensored loaded in 26 s.
- 08:22 wedge #2 with NO vision as soon as ref2va-27b loaded beside Halogen. So the root cause is ref2va co-residence, not vision. Recovered the same way (stopped ref2va; a stale --rm ref2va container was podman rm'd).
- Pane PONG 08:24 (Render w3:p1, Forge w4:p1): both footers read flash-next-uncensored and requests flowed (200s in the log). Neither gave a clean "PONG": both ran bash despite "no tools" and finished with reasoning text. That is model behaviour, not transport, so the panes were not restarted.
- Read-only checks: image 0.20.5 (>= 0.13.2), MEC fw 0x24 (fixed level).
- 08:28 recipe applied (backup llama-swap.yaml.bak-20261117-082636-pre-weightslock):
  - HALOGEN_WEIGHTS_LOCK=1 on flash-next + flash-next-uncensored (--ulimit memlock=-1:-1 was already there)
  - systemd drop-in llama-swap.service.d/90-memlock.conf LimitMEMLOCK=infinity
  - /etc/sysctl.d/90-halogen-compaction.conf vm.compact_unevictable_allowed=0 (sysctl --system)
  - load order: small group stopped before the Halogen restart, Halogen loaded first
  - HALOGEN_VISION_TOWER=1 re-enabled on uncensored
  - compaction_proactiveness (20), hugepage and amdgpu flags untouched
- Startup lines: "checkpoint: locked 62.11 GiB ... MemAvailable 107.3 -> 45.2"; vision tower locked 0.84 GiB; "host memory left for everything else: 4872 contiguous 2 MiB blocks (17.3 GiB total)". MemAvailable is now truthful (Mlocked 62.9 GiB).
- Retest 08:29 (vision on):
  - image #1 alone 200 (17 s cold)
  - embed 200, joycaption 200: MemAvailable 15.5 -> 6.1 GiB
  - image #2 200 in 2.0 s (the case that wedged)
  - 3 parallel 200 (1.4-1.7 s); 0 x 429, 0 PING warnings, 0 OOM, evicted 18 ms
  - MemAvailable 5.76 GiB >= 4
  - ref2va-27b deliberately NOT loaded: it needs ~19.4 GiB vs 6.1 available. Under WEIGHTS_LOCK the docs say an overcommitting co-tenant gets Halogen OOM-killed, and an unclean kill risks the issue #79 GTT leak (reboot). => OPEN for Derrick: ref2va cannot be co-resident with Halogen at the default pool (524288 / MAX_TOK 32768). Options: HALOGEN_KV_POOL_POSITIONS=262144 (~7 GiB), HALOGEN_KV8=1 (~6 GiB), HALOGEN_MAX_TOK=16384 (~4.4 GiB, -9% prefill), or keep ref2va off while uncensored is up. Hazard until decided: any ref2va request while uncensored is loaded will knock Halogen over.
- models.json (backup /home/evo/evo-x3/_archive/models-json-20261117-082959/, 0600): flash-next-uncensored input ["text","image"], name "... 4 slots, vision". Render agent-dir pi -p with an image @file described it correctly. In both panes, /reload + /model opened (the docs say /model reloads models.json); no pane restart.
- Huihui v2 GGUF left in place. No deletes (except the stale exited --rm container). No commits.

## Addendum 08:49 CST — JoyCaption off the resident group; Halogen 3 slots / 262K pool; Ref2VA co-residence (Derrick t61u / t62u)
- Backup: `/etc/evo-x3/llama-swap.yaml.bak-20261117-084352-pre-ref2va-fit` (pre-change). Later safety copy `llama-swap.yaml.bak-20261117-084715-pre-ondemand-group`.
- Halogen `flash-next-uncensored`: `HALOGEN_KV_POOL_POSITIONS=262144`, `HALOGEN_KV_SLOTS=3`, `concurrencyLimit: 3`, `HALOGEN_CTX=262144` kept, `HALOGEN_MAX_TOK` and KV8 unchanged, vision still on, WEIGHTS_LOCK=1. Start order: Halogen first, then side models.
- Startup line: "3 slots over ONE 262144-position KV pool, each request up to 262144". Pool 7.2 GiB (was 14.4). Engine total 82.5 GiB (was 89.7). Host memory left after Halogen: **24.8 GiB** (was 17.3). Per-request context is still the full 262K; three at once share the 262144-position pool (~87K each if split evenly).
- Memory: after Halogen+embed, MemAvailable ~23 GiB. After ref2va-27b loaded, MemAvailable **4.1 GiB**, then **3.4 GiB** after the uncensored image/parallel tests. No kernel OOM, no Halogen PING/wedge, 0 x 429.
- Tests (all HTTP 200, ref2va stayed `ready` alongside uncensored+embed):
  - ref2va text 200 in 7.7 s; ref2va image 200 in 11.7 s
  - uncensored image #1 200 in 1.7 s; 3 parallel text 200 in 0.51–0.58 s (empty `content` because max_tokens 8 with thinking on, "closed at 1 by answer room"); uncensored image #2 200 in 1.44 s
  - verify-serve.sh: no key 401, LLM_KEY_BOX 200
- Grouping lessons (first attempts were false fails, then fixed and retested):
  1. Removing ref2va from every group made llama-swap treat it as exclusive and **swap Halogen out** at 08:45:51 (`stop requested`, GTT 0.3 GiB after exit, recovered). Fix: keep joycaption/ref2va in a non-exclusive, swap=false group.
  2. A non-persistent on-demand group still **evicted ref2va** at 08:47:57 when the first uncensored image request arrived (embed, being persistent, stayed). Fix: ref2va is now a member of persistent `small` with embed-small. JoyCaption stays in `ondemand-small` (not auto-started).
- JoyCaption callers (not edited): the only live caller is `/home/evo/AI/pixlstash-tagging/joycaption_compare.py` (model `joycaption`). On-demand still works, but with Halogen+Ref2VA resident only ~3.4 GiB is free (JoyCaption needs ~9 GiB), so it will not fit until Ref2VA is unloaded. No hits in `/home/evo/AI/community/scripts`, `/home/evo/AI/render`, live `models.json`, or evo-x3 scripts. PixlStash has a built-in JoyCaption engine option; no X3 endpoint was found in AlienPc Roaming configs.
- Left running at 08:49 CST: `flash-next-uncensored` (3 slots, pool 262144, vision on) + `embed-small` + `ref2va-27b`. JoyCaption off. Margin is tight (~3.4 GiB). Render w3:p1 idle, Forge w4:p1 done. Evidence: `records/gufo-phase1-20261117/ref2va-fit-test.txt` and `ref2va-fit-phase*.sh`.

## 2026-11-17 09:43-09:50 CT: keep uncensored resident (Derrick t76 approval, executed by Grok Bot)
Cause: callers kept asking for gemma4-heretic / flash-next (main exclusive group), evicting flash-next-uncensored; its cold start then failed ("refusing to pin", floor 16 GiB) with ref2va resident. PixlStash held ~12.7 GiB (5.9 RSS + 6.8 zram).
Changes:
- /etc/evo-x3/llama-swap.yaml: appended hooks.on_startup.preload [flash-next-uncensored] + profile halogen-only (profile active on startup) pinning gemma4-heretic, gemma4-heretic-sub, flash-next, flash-next-sub -> flash-next-uncensored. qwen27b untouched. Backup: /etc/evo-x3/llama-swap.yaml.bak-20261117-094500-pre-preload-pins. llama-swap restarted 09:46:17.
- /home/evo/AI/render/.pi/settings.json (defaultModel, subagents.defaultModel), /home/evo/AI/forge/.pi/settings.json (same), /home/evo/AI/render/writer_pipeline/config.yaml (model_alias) -> flash-next-uncensored (x3-local/ prefix kept for subagents; no -sub variant exists for uncensored). Backups: <file>.bak-20261117-094400-pre-uncensored-pin next to each. Not committed.
- evo user units: u42-pixlstash-tagger disabled+stopped (crash loop, missing submit_parody_run); pixlstash.service drop-in ~/.config/systemd/user/pixlstash.service.d/10-memcap.conf (MemoryHigh=5G MemoryMax=8G MemorySwapMax=2G), pixlstash restarted 09:45:11.
Results: MemAvailable 2.86 -> 14.8 GiB with all three models loaded; zram 6.84 -> 0.26 GiB; pixlstash RSS 5.86 -> 1.0 GiB; preload loaded uncensored first with no client request (log shows a harmless "failed to preload ... status 404" after Health check passed); embed-small, ref2va-27b, uncensored all 200; a gemma4-heretic request is served by uncensored (same container, no gemma start).
Rollback: restore the .bak files above; rm the pixlstash drop-in; systemctl --user enable --now u42-pixlstash-tagger.
