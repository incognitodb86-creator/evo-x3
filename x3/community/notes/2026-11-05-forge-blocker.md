## 12:1x CT - lane Ralph (Forge) F6a: box has no network, record pushes to Gitea are deferred
What: F6a (the three reuse lines in the single PROMPT.md) completed and is ticked `[x]` - nothing about the item is blocked. What is deferred is the records step "push fleet-brain notes to Gitea": the box has no outbound network this pass, so both record commits are **local only**.
Evidence (all read-only, 12:18 CT): `git -C C:\AI\fleet-brain pull --rebase --autostash` = "Failed to connect to qnap.tailf242b2.ts.net port 443 after 21068 ms"; `git push origin master` (fleet-brain) rc 128 same; `git push gitea HEAD` (ralph-community, `derrick/ralph-community.git`) rc 128 same; `nslookup github.com` = "DNS request timed out" x2; `curl https://github.com/ghuntley` = 000; `curl http://192.168.0.147:8888` (SearXNG on the QNAP) = 000. So Tailscale, DNS, the QNAP and GitHub are all unreachable from this box at once - the pattern is the Tailnet/DNS, not one service.
Local commits awaiting push (recorded so the next pass pushes them, nothing is lost; SHAs are post-amend, the first set 7e0e8fd/2407dae/95f43ba no longer exists - a record SHA must be written after the final commit): **fleet-brain `19f4383`** (status mirror + the job's learning merged into the existing bulk-archive learning) = 1 commit ahead of `origin/master`; **ralph-community `cbba6aa`** (F6a tick + records) = 1 commit ahead of `gitea/master`; **`C:\AI\community` `c000de9`** (actions.log + this card) - its `git push` to `derrick/alienpc-community-pc` returned the same rc 128 connection failure.
Side effect on the item: the Pass clause asks to cite the Ralph playbook at https://github.com/ghuntley/how-to-ralph-wiggum - the live fetch was impossible, so the citation is the community cached copy `C:\AI\community\notes\web\01r_ghuntley_htrw_readme.txt` (62,071 B, saved 2026-10-23 20:13) plus the URL, with the source lines named (":87/:193/:396", ":420/:1207", ":440"). The item's checks do not need the network, so the tick stands.
Duration in-pass: first failure 12:0x (the pass-opening pull), re-attempted at 12:1x and 12:25 (all three repos) - same rc 128 connection failure each time, so the outage spans the whole pass, not one service. The counts at pass end: 2 unpushed commits in each of the three repos (fleet-brain 19f4383 + db4b759, ralph-community cbba6aa + c58dd6a, C:\AI\community c000de9 + 7da6020); the pairs are the record commit + its SHA-correction child, and the local working trees are otherwise clean (only the loop's own notes/heartbeat.txt is modified by the harness).

Ask: nothing to fix in the fleet's files. If the outage outlives this, the only thing to watch is the queue of unpushed record commits (3 here) - they push themselves on the next reachable pass with `git -C C:\AI\fleet-brain pull --rebase --autostash && git -C C:\AI\fleet-brain push origin master`, `git -C C:\Users\derek\5slock\ralph-community pull --rebase --autostash && git -C C:\Users\derek\5slock\ralph-community push gitea HEAD`, and `git -C C:\AI\community pull --rebase --autostash && git -C C:\AI\community push`. No action for you unless it is still down tomorrow.
Full record: C:\Users\derek\5slock\ralph-community\notes\2026-11-05-cleanup-F6a-DONE.md.

## 12:56 CT F2a pass: the outage is the QNAP/Tailscale path, and my push command was wrong (pi session, not a ralph run)
- What: this pass's commits cannot be pushed. All three repos push to the Tailscale host: C:\AI\community `git push gitea master` -> "Failed to connect to qnap.tailf242b2.ts.net port 443 after 21066 ms"; C:\Users\derek\5slock\ralph-community remote `gitea` = the same host; C:\AI\fleet-brain `git push origin master` -> same 443 failure. Local commits are fine (50dda24, 95de74c made).
- Self-check, stated not hidden: my first push attempts used `git push origin master` in community and ralph-community. There is no `origin` there; their remote is named `gitea` (git remote -v). So that rc 128 ("'origin' does not appear to be a git repository") was my command, not the network. The 443 failure is the real blocker, measured with the right remote at 12:56.
- Box state now: `nslookup github.com` resolves (140.82.114.3) and `https://github.com` = 200, so public DNS+internet are back (they were down at 12:30, see the 12:1x section above). `http://192.168.0.147:8888/` (SearXNG on the QNAP) = 000 and `qnap.tailf242b2.ts.net:443` = no connection: the QNAP/Tailscale path is the part that is down, which is also the Gitea remote.
- The ask: none for the fleet, no config change. When the QNAP/Tailscale path is back the commits push themselves - C:\AI\community `git push gitea master` (50dda24, 95de74c, the records commit), ralph-community `git push gitea master` (the fix_plan commit), fleet-brain `git push origin master` (19f4383 db4b759 + this job's learning/status). Note for the next pass: the remote is `gitea`, not `origin`, in the two ralph/community repos.

### F2a pass closed (2026-11-05 13:10 CT): the exact pending pushes

Community 50dda24 (code), 95de74c (docs), 30f88c4 (records), e4c5489 (actions line); ralph-community 6990bfc (fix_plan PARTIAL); fleet-brain 93877bc (learning + status mirror). All three pushes failed again at 13:09 CT: qnap.tailf242b2.ts.net:443, 21 s each. Next pass runs: git -C C:\AI\community push gitea master ; git -C C:\Users\derek\5slock\ralph-community push gitea master ; git -C C:\AI\fleet-brain push origin master. No force-push, no GitHub. Nothing new is asked of Derrick here; the open asks (GPU GO, owner for the 7 pre-existing red tests) are in notes\needs_derrick.md 13:00.


### B2-1 pass (2026-11-05 21:1x CT): Gitea answers HTTP 502 on all three repos (the tailnet answers, Gitea does not)
- What: item B2-1 is complete and ticked [x]; only the records push is deferred. `git ls-remote --heads` and `git push` both return "The requested URL returned error: 502" for https://qnap.tailf242b2.ts.net/derrick/alienpc-community-pc.git, .../derrick/ralph-community.git and .../derrick/fleet-brain.git; the pass-opening `git -C C:\AI\fleet-brain -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=5 pull --rebase --autostash` failed the same way. The request reaches the host and Gitea answers 502, so **Gitea on the QNAP is unhealthy**, not the tailnet/DNS (the 3rd, 4th and 5th 502 of the evening: 19:28, 20:4x, 21:1x CT).
- Local commits awaiting push, in the order a future pass pushes them: **C:\AI\community** = the commit that contains this card and notes\2026-11-05-b2-1-DONE.md (`git -C C:\AI\community log -1 --format=%h`; the loop-root fix_plan RESULT line names it), **C:\Users\derek\5slock\ralph-community** = the fix_plan B2-1 tick + progress line (named by the fleet-brain commit message), **C:\AI\fleet-brain** = the last commit of the chain, `git -C C:\AI\fleet-brain log -1 --format=%h` (status mirror + this job's single learning).
- Push commands at the first 200: `git -C C:\AI\community push gitea master` ; `git -C C:\Users\derek\5slock\ralph-community push gitea master` ; `git -C C:\AI\fleet-brain push origin master`. No force-push, no GitHub; remote names gitea, gitea, origin.
- The ask: nothing to change in the fleet's files. Gitea service health is the QNAP side; the queue of unpushed record commits pushes itself on the next healthy pass.

# B2-3 blocker (2026-11-05) - one Pass clause rests on a false premise; the feature itself is done

Owner of the fix: **Max** (the plan text). Forge built, tested, and proved the feature; only the
plan's own fact is wrong.

## What
Item B2-3 (`fix_plan.md` FORGE B2 block) says: "a non-empty list containing `pack disabled`
against the 20261031 capture (the u5 case)". Measured, that capture lists the class, so the
non-empty result is unreachable for it. Everything else in the item's Pass line passes
(`notes/2026-11-05-b2-3-DONE.md`).

## Evidence
- `C:\AI\community\notes\objinfo\object_info_20261031.json`: 2450 top-level keys,
  `MinimaxH3LatentUpscaler3D` present. `object_info_20261030.json`: 2338 keys, present.
  `object_info_20261105.json`: 1786 keys, present. (B2-2's records call 2338 "the 20261031
  capture"; 2338 is 20261030.)
- u5's `unknown class MinimaxH3LatentUpscaler3D` (2026-11-05 20:11, `runs\u5_reflora_smoke_20261105\status.log:3-4`)
  was against the **live** `/object_info` while `Comfyui_Minimax_h3_latent_Upscaler` was parked as
  `.disabled`; that capture was never saved, so no saved file reproduces u5.
- The live tree now: the upscaler pack present/enabled (B2-1's rename), 10 other packs parked
  `.disabled`.
- Proof that the guard fires: validator on a `lsu3` graph vs a capture that lacks the class ->
  `lsu3: unknown class MinimaxH3LatentUpscaler3D (defined by Comfyui_Minimax_h3_latent_Upscaler - pack disabled at the 20261101 capture; ... is present and enabled now)`;
  with the pack directory itself `.disabled` -> the exact text the item asks for
  (`... .disabled - pack disabled)`), asserted in `test_parody_reflora.py::OfflineClassCheck::test_u5_failure_line_is_exact`.

## The ask (pick one, Max)
1. Re-word clause (c)/the Pass clause to name the real evidence: the u5 capture was never saved;
   prove the regression with a capture that omits the class + a `.disabled` fixture pack
   (what Forge built). Then B2-3 can tick as written-minus-that-clause.
2. Re-capture `object_info` with the upscaler pack parked `.disabled` (GPU-adjacent, ~1 model
   load, needs a GO) and the 20261031-style literal clause becomes provable.
3. Keep the clause and leave B2-3 `[PARTIAL]` forever.

## Also for B2-4 (found while proving this, not a blocker)
Two-pass `build_parody_request` re-reads the frozen `DEFAULT_B2_TEMPLATE` and rebuilds whenever a
passed `--template` has no `refmods` node, so a raw-`b2`-shaped `--template` override is silently
discarded in two-pass mode (measured: `runs\_b2_3_check_20261105\` Proof 3). B2-4's new
`b2_parody_2pass.api.json` carries `refmods`/`refapply` itself (generated by
`derive_refmod_2pass_graph`), so the wiring is testable - but its `--template` proof must use
that file, not a raw-b2 file. Say the word if the override path should raise instead of rebuild.
