VERDICT: CHANGES

Delta re-review of `records/uplan/PLAN.md` and `records/hermes-direct-render/PLAN.md`, `e0c446f..mono` (`4c4d4a6`), commits `69d7af6` + `66ea7b5`. Reviewer: Claude Opus 5.5, VS Code on Derrick's PC, read-only `git --git-dir=C:\tmp\evo-work\mono.git`, 2026-11-19 ~11:45 AM CT. Packet: `20261119-1145-evo-plan-reviewer-delta.md`. Derrick's decisions (GitHub `mono` first, Max mirrors to Gitea; `opus/<group>` in VS Code; Card 2 = yes) are taken as given. Nothing checked on a host.

Short version: 13 of 15 findings and all of M1-M9 are fixed. One new MAJOR: the plan never says how a `mono` commit under `x3/*` or `alienpc/*` reaches a live checkout that is still on its old part branch before `MONO-S5`/`S6`. That is a 2-line fix. The rest is small text.

## Findings 1-15 and M1-M9

| # | Status | Where (mono) | Note / one-line fix |
|---|---|---|---|
| 1 | FIXED | AlienPc Forge row; `INV1b`; Install table | Gate is clear. Optional: give the `INV1b` approval its own card number (it is only named inside Card 2's file-work list). |
| 2 | FIXED | AlienPc Forge row; Card 29 | Test what `:8447` reports with Swift loaded, then pick (a)/(b). Recommendation stated. |
| 3 | PARTIAL | "Leases" section; A25; Card 28 | The structure is right. Two text errors: (1) the lease README says nothing about `records/status/`, so "mirrored to `records/status/` per README" is a plan rule, not the README's. Say so. (2) The `*-alienpc-lease-*.md` file name is made up. The README says the AlienPc lease convention is in brain `10_packs/max/max-briefing.md`. Cite that file and use its name pattern. |
| 4 | PARTIAL | Install table | The table is good, and the canonical copies are named. Gaps: `L3` (nightly worktree timer) and `L7` (pi syntax-check extension) have no Install line. The `H2, H3, H4` row gives `/home/evo/.hermes/` as the only destination, but H3 units go to `/home/evo/.config/systemd/user/` and need `systemctl --user daemon-reload`. Add both. Also, the snapshot does not cover `hosts/alienpc/live/` (INV3 is still open), so "re-run snapshot" does nothing for INV1/INV1b. Say "re-copy by hand until INV3". |
| 5 | FIXED | Import-and-apply 1-2; C15; Card 27 | Using a merge on the box when Gitea has moved, never a force push, is clear. Small add: delete the `opus/<group>` branch after import. |
| 6 | FIXED | ST3 (a) | `systemd-run` only. Unit name works as the lock. Survives-exit test added. |
| 7 | FIXED | Stills intro; ST2; ST5; Card 30 | Image gate runs before any AlienPc job. Mocked fixture only. |
| 8 | PARTIAL | ST4 Gate | Build/test vs runtime split is done. But the runtime rule went from "yes per still" to "one-time yes for the feature" with no Derrick id. Make that choice a card (per still / once), as the first review's fix asked. |
| 9 | FIXED | C17; monorepo S5/S6 @ mono | Monorepo plan line 124 says "Max, or AlienPc Forge over SSH — NOT X3 Forge". Line 125 says S6 stops AlienPc Forge panes and re-tests skill links. Checked. |
| 10 | FIXED | Hermes R1-R18; Hermes Scope; C16 | 0 "Owner: Max" left (`Select-String` count). The C16 note and the R6 wait are present. |
| 11 | FIXED | ST3 (c); Card 23 | Current and proposed values match (`8G/10G/2G` → `12G/14G/2G`); headroom test added; cites t2584. |
| 12 | PARTIAL | C14, A23, inventory, R5 fixed; Card 2 list; L1-L8 Lease column | Card 2's groups still leave out `INV3`. `L1-L8` still say "Lease: X3 when verifying", but apply writes `/usr/local/bin/pi-job` with sudo, so it needs the X3 lease for apply too (same fix as R5). `65fa220` exists (checked). |
| 13 | FIXED | "PLAN ONLY" paragraph | Prefix rule plus the line saying "item tables stand in for S#". |
| 14 | FIXED | Cross-machine access | Per-brief command list, no `-AsDerek`/sudo unless named, log in RESULT. |
| 15 | FIXED | A7; folder table | "never `x3-linux`" is stated in both places. |
| M1 | FIXED | Card 27 (resolved) | Matches Derrick's decision. |
| M2 | FIXED | Card 28 | Open card with a default. |
| M3 | FIXED | Card 29 | Open card with a default. |
| M4 | FIXED | Card 30 | Open card; ST2/ST5 wait on it. |
| M5 | FIXED | Card 31 | Default: support ID and path. |
| M6 | FIXED | Card 32; Card 2 holds LX | LX waits for the path. |
| M7 | FIXED | Card 33 | First AlienPc brief checks `git status -- templates/`. |
| M8 | FIXED | Card 34; ST2 | Default auto-import, can be overridden. |
| M9 | FIXED | Card 35 | Points to Cards 22/14. |

## New issues

1. **MAJOR — `mono` to live checkout has no bridge before `MONO-S5`/`S6`.** Import step 3 says to `git pull --ff-only` from Gitea for "live git checkouts (`x3/render/`, `x3/community/`, `x3/forge/`, `alienpc/render/`, `alienpc/community/`)". `mono` was built with `filter-repo --to-subdirectory-filter` plus unrelated-history merges (monorepo KTD1). The live checkouts stay on `x3-render`/`x3-community`/`alienpc-*` until S5/S6 adopt them, so a `mono` commit under `x3/render/x3/still_candidate_sheet.py` (it exists on `mono`) can't be pulled into `/home/evo/AI/render`. Meanwhile the worker commits (`ST1`, `S2`, `H2`-`H3`, `M4`, `ST4`, `ST5`) are already on `mono`. Fix: add one rule. Until S5/S6, either (a) hold every `x3/*`/`alienpc/*` apply until cutover, or (b) on the box run `git format-patch --relative=<prefix> <range>` and `git am` it onto the part branch under the lease (no force), then push the part branch to Gitea. Root-copy items (`config/`, `hosts/`) are unaffected, because they use the Install table.
2. **MINOR — "until `mono` is live" is never defined.** It appears in the delivery line, C2, C15, import step 1 and the folder table. `copilot-instructions.md` already calls the part branches frozen. Fix: define "live" as "after `MONO-S5` (X3) / `MONO-S6` (AlienPc) pass smoke", and say Opus always commits to `mono` (never the frozen part branches). Item 1 covers the apply side.
3. **MINOR — ST1/ST5 rows still name part-branch paths only.** ST1 says "`x3-render` `x3/still_candidate_sheet.py`" (on `mono` it is `x3/render/x3/still_candidate_sheet.py`). ST5 says `templates/...` with no part folder. Fix: give the `mono` path in each Opus-file cell, as R5 now does.
4. **MINOR — the Install table's backup paths are relative.** `_archive/<date>/…` doesn't say which root (`/home/evo/AI/_archive`? the repo's `_archive`?). On AlienPc, `_archive\<date>\pi-agent\` has no base. Fix: give absolute backup roots per host.

(Findings 3, 4, 8 and 12 above also carry small new text fixes.)

## Ready for Max

**Partly yes.** Max can import `mono`, run gitleaks, sync Gitea and apply **root-copy** items (`config/bin/*`, `hosts/x3/pixlstash-tagging/`, `hosts/x3/hermes/`, `hosts/x3/systemd/user/`) with the Install table under the X3 lease. **Not yet** for any `x3/*` or `alienpc/*` apply (`ST1`, `R5`, `W3a`, `G2`, `S2`, `M4`, `ST4`, `ST5`, `RV*`). Max would have to guess how a `mono` commit reaches a part-branch checkout (new issue 1). Fix new issue 1 (and, ideally, the PARTIAL rows 3/4/8/12). Then this is APPROVE with no further review needed for text-only fixes.

## Verified (read-only git on `C:\tmp\evo-work\mono.git`)

- `mono` = `4c4d4a6`; `e0c446f`, `69d7af6` and `66ea7b5` exist; `66ea7b5` touches `records/G4/AUDIT-20261119.md` and the unified plan only.
- `scripts/snapshot-live-setup.sh` line 6 does `rm -rf "$R"` and then writes `hermes/` under it. It never writes `hosts/x3/hermes/`, `hosts/x3/systemd/` or `hosts/alienpc/`, so the `66ea7b5` reasoning is correct.
- Paths exist on `mono`: `config/bin/pi-job`, `config/bin/sync-renders`, `hosts/x3/pixlstash-tagging/import_inbox.py`, `hosts/x3/hermes/config.yaml`, `hosts/alienpc/live/pi-agent/AGENTS.md`, `hosts/x3/systemd/user/pixlstash.service.d/10-memcap.conf`, `x3/render/x3/queue-remote.sh`, `x3/render/x3/still_candidate_sheet.py` (+ test).
- Hermes plan: 0 `Owner: Max` lines; R6 and Scope carry C16.
- Lease README lines 8-30: X3 brain path only, AlienPc convention in `10_packs/max/max-briefing.md`, no `records/status/`.
- Monorepo plan lines 89, 124-125: filter-repo plus unrelated-history merge; S5/S6 owner and quiesce rules match C17.

## Could not verify here

- Live owner/mode/sudo values in the Install table (`root:root 0755` for `/usr/local/bin/*`, `evo:evo 0755` for `import_inbox.py`).
- Whether `run_queue` actually takes `gpu-render.lock` for an ST4 still (A13 is a live fact).
- The A23 live checkout SHA.
