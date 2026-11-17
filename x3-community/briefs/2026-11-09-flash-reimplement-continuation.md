# Flash High reimplement: native continuation (no render, no commit)

Repo: C:\AI\community, branch docs/parody-identity-docs-20261106, HEAD cc26413. Uncommitted 3c801f1 restore of scripts/parody/build_request.py, submit_parody_run.py, and test_parody_dynamic.py. Backup and diffs: C:\AI\_archive\2026-11-09-pre-restore\. Read notes/2026-11-09-restore-3c801f1.md KEEP/DROP first. Port from the archive where it helps.

Do only these five:

1. `--ambience` option (default "quiet room ambience, soft natural room tone").
2. Refuse `--seconds` over 243 frames (~10.1s) unless there are 2+ `--beat` scenes.
3. Native continuation with only MiniMaxH3GuidedContinuationWindow → MiniMaxH3LatentTailGuide → sample → MiniMaxH3AppendContinuation. Beat 2 previous_av_latent = ["s0_samp",0]; later beats = [c{n-1}_append,0]. RefMod every beat. AddGuide/start photo on beat 1 only. 22-frame overlap. Each window ≤243 frames. One window per requested beat.
4. Airlock wording: continuation beats open holding the previous beat's closing framing, with micro-motion.
5. In submit_parody_run.py, 2+ `--beat` builds one native continuation graph, not stitched cells.

Do not restore plan_beat_windows, _split_frames, F1 repeat logic, or test_parody_continuation.py.

Keep single-shot graphs byte-identical. Lock: 768x1344, beta7_int8HQ, INDEX + RefMod, 8 steps, euler/simple, RTX 2x default.

Edit only those 3 files plus focused new tests under scripts/parody. No new flags besides `--ambience`, no new nodes, no other files, no docs, no commits, no render, no ComfyUI queue. Do not touch run_queue.py, AGENTS.md, skills, or any sydney folder.

Back up first. Run `C:\AI\director\.venv\Scripts\python.exe -m pytest C:\AI\community\scripts\parody -q --tb=short`. The 2 known beat-sheet doc failures may remain. Save a 2-beat dry-run node list and frame math to briefs/2026-11-09-flash-reimplement-continuation-dryrun.md.

Report changed functions, test counts, and dry-run evidence. Stop when it works. If this small approach fails, report it; do not redesign.
