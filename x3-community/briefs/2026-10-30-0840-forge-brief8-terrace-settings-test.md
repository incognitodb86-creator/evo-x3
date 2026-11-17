# Forge brief8: terrace settings test (Max2, 2026-10-30 8:40 AM CT)

Derrick GO 8:31 AM CT. brief7 is DONE (notes\2026-10-30-brief7-probe-submit-DONE.md); brief8 supersedes it.

Plan: `C:\AI\community\plans\2026-10-30-0700-terrace-proper-settings-test-plan.md` (sha256 5d5fa1ac…3653b). Run it as written: 7 arms (A0, S1a, S1b, S2, S3, S6, S8), one variable per arm vs the B2 baseline request, shared seeds, one GPU job at a time via `C:\AI\locks\gpu-render.lock`, adults-only guard_ok logged on every submit (already in comm.run() and run_graph_job.py; probe_submit.py is archived).

Inputs staged by Max (copy, don't edit):
- `C:\Users\derek\_max2_brief8\imageA_768x1344_crop.png` (4d07281d…) and `imageB_768x1344_crop.png` (4c9ae12f…): copy into the same ComfyUI `input\community\` folder as TERRACE2_768x1344.png.
- `C:\Users\derek\_max2_s8chk\promptA.txt` (97ed1361…), `promptB.txt` (83efcf50…).

**Step A (no GPU):** build all arm request files + prompt files (S8 = line file + "\n" + prompt; hashes per plan). Also write a one-page diff table (each arm vs B2: the changed key only) and a contact sheet of the start frames. Write `C:\AI\community\notes\2026-10-30-brief8-arms-READY.md` listing every path + sha256. Then PAUSE.

**Step B:** when `C:\AI\community\notes\2026-10-30-brief8-arms-CHECKED.md` exists, render the 42 new clips in plan order (interleaved, randomized, order recorded). Run the plan's drift check first. Reuse the 7 v2 clips as the plan says. Failures: retry once, same graph and seed, per plan; recover on your own. When finished write `C:\AI\community\notes\2026-10-30-brief8-DONE.md` with all output paths.

Change no settings beyond each arm's variable. Stock community settings; no extra controls. No scoring in this brief.
