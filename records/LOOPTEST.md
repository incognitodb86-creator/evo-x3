# LOOPTEST — Steps for a 10-second clip, no queueing

1. Create one run folder under `/home/evo/AI/community/runs/<run_name>`.
2. Pick the start still — from `/home/evo/AI/render/_inputs`, a path Derrick gives, or the PixlStash API (`http://127.0.0.1:9537`, `Authorization: Bearer $PIXL_KEY`); inspect the chosen still with `read`.
3. Write `<run_dir>/still_read.json` (or omit it and let the pipeline auto-caption via `vision_model_alias: joycaption`).
4. Run the one command with `--frames 240` (24 fps × 10 s; the native single-shot cap is 243f ≈ 10.1 s, so a single 240-frame clip fits without extension) — omit `--scene`/`--continue` for this standalone 10-second clip:
   `/home/evo/AI/render/x3/.venv/bin/python3 /home/evo/AI/community/scripts/parody/render_writer_pipeline.py '<run_dir>' ... --frames 240`
5. Since nothing gets queued, run WITHOUT `--queue --yes-derrick`: the dry run stops and reports `prompt.txt`, the `READY`/`NOT_READY` status line, and the `pick.json`/`build_report.json` path.
6. Add `--actor 'Sydney Sweeney' --names 'Sydney Sweeney'` for the celebrity, or `--character 'FCSydny'` for the OC — visual-only aliases (`FCMegan`) get visual RefMods only, no voice ref.
