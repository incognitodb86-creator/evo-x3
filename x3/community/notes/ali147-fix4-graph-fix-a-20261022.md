# ALI-147 FIX4_GRAPH option (A) - the two changes, old -> new (Forge, 2026-10-22, CPU only)

File edited in place: `C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json`
Backup (untouched, byte-identical to the pre-edit file, `cmp` silent): `request.api.json.bak-20261022-fix4graph` (41906 B vs 41921 B after the edit).
Readable evidence: `graph_diff.txt` (git diff --no-index .bak -> request.api.json, exit 1): one hunk, exactly 1 removed and 1 added line = the single `ext.inputs.clips_json` string line (the file is JSON with `indent=1`, so the whole clip list is one line). The builder self-check `notes/ali147_fix4_graph_fix_a.py` (ALL CHECKS PASS) is the semantic proof: every other node and every other `ext` input is byte-identical, and no clip key other than `validated` / `duration` changed.

| clip | name | prompt sha256 (unchanged) | len | duration old -> new | frames old -> new | validated old -> new |
|---|---|---|---|---|---|---|
| clip_1 | seg1_c0 | `7b4b22bb170fbcb8` | 3295 | 10.125 -> 10.125 | 243 -> 243 | True -> False |
| clip_2 | seg1_c1 | `49c94ba7759859e2` | 2569 | 9.916667 -> 10.833333 | 238 -> 260 | True -> False |
| clip_3 | seg2_c0 | `1f37321ff13763cd` | 3545 | 10.125 -> 10.833333 | 243 -> 260 | True -> False |
| clip_4 | seg2_c1 | `dcf5579f6cd2a04b` | 2602 | 9.916667 -> 10.833333 | 238 -> 260 | True -> False |
| clip_5 | seg3_c0 | `8ed332629e80a870` | 3354 | 10.125 -> 10.833333 | 243 -> 260 | True -> False |
| clip_6 | seg3_c1 | `d7d29ad985a7a432` | 2579 | 9.916667 -> 10.833333 | 238 -> 260 | True -> False |

Frame budget: raw 1543 (243 + 5x260, all on the 5+17k grid at 24 fps) - 5 Motion Context seams x22 = **1433 kept frames = 59.708 s**, |1433 - 1443| = 10 <= frames_tol 24.

Why (from the failed run, status.log 17:36:56-17:37:07 CT, 3/3 attempts, 5.1 s each): `Ref2VA clip 1 is marked Validated but its disk cache is missing. Refusing to rerender a validated clip. Uncheck Validated explicitly if you want this clip rendered again.` `validated: true` is the UI clip-card checkbox; a cold headless full_batch cannot satisfy it, so every clip is set to `validated: false`. The 243/238 mirror of the base run put clip_2..6 off the length grid (238 frames), which the Extender snaps; the grid-aligned 243 + 5x260 is the fair mapping (notes/ali147-fix4-graph-20261022.md finding 2).

Old failed job outputs were moved aside, never deleted: `p7/jobs/ali147_pool_fix4_s51080000.{result.json,out,err.out}` -> `*.failed-20261022`, and the run folder's `ali147_pool_fix4_s51080000*.api.json`, `objective.json`, `status.log` -> `runs/ali147_pool_fix4_s51080000/failed-20261022/`. `request.api.json` stays as the input for the re-request (FIX4_REQ).

METHOD_ONLY. No render, no GPU, no ComfyUI/llama-swap call by Forge; the job is only requested by the next task (FIX4_REQ). KEEP is Derrick's only.
