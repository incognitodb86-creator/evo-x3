# U49 Result — PixlStash Video Import + Tagging

**Status:** PASS

## Files Changed
- `/home/evo/AI/pixlstash-tagging/import_inbox.py`: Added `.mp4`, `.webm`, `.mov` to `EXT` after verifying PixlStash `POST /api/v1/pictures/import` (`STAGING_ALLOWED_MEDIA_EXTS` / `VIDEO_EXTENSIONS`) natively supports those video formats.
- `/home/evo/AI/pixlstash-tagging/tag_runner.py`: Added `probe_video_duration`, `run_ffmpeg_frame`, `extract_video_frames_ffmpeg`, and `Runner.query_vlm_for_image`. For `fmt in VIDEO_FORMATS`, `Runner.process_one_picture` fetches `/api/v1/pictures/{pid}.{fmt}`, extracts first, middle, and last frames via `ffmpeg` into a `tempfile.TemporaryDirectory`, runs the existing VLM tagging path on each frame, merges tags/people by union under existing thresholds/caps (`parse_vlm_json`, `MAX_NEW_TAGS_PER_PIC`), posts them onto the video item, and cleans up the temporary directory/frames automatically. Image handling is unchanged.

## Backups
- `/home/evo/AI/pixlstash-tagging/_archive/import_inbox.py.bak-20261116-u49`
- `/home/evo/AI/pixlstash-tagging/_archive/tag_runner.py.bak-20261116-u49`

## Test Results (Counts Only)
- `py_compile`: Passed on both `/home/evo/AI/pixlstash-tagging/import_inbox.py` and `/home/evo/AI/pixlstash-tagging/tag_runner.py`.
- Synthetic 5 s `ffmpeg testsrc` `.mp4` import via `import_inbox.py`: `{"files": 1, "imported": 1, "duplicate": 0, "failed": 0}` (landed in PixlStash as `id=33569`, `format=MP4`).
- Video tagging via `tag_runner.Runner.process_one_picture(33569, "mp4", set())`: returned `(33569, 'done', 24, 0, 0, None)`; PixlStash tag count on item: `27`; leftover temp dirs: `0`.
- Cleanup: soft-deleted and purged test item `33569` from PixlStash scrapheap (library count before `33564` -> after `33564`), and removed the imported test file from `/home/evo/AI/pixl-inbox/_imported/`.

## Tagger Service
- `u42-pixlstash-tagger.service` restarted once (`XDG_RUNTIME_DIR=/run/user/$(id -u evo)`): confirmed `active (running)` (PID `178941`).
- `u42_state.db` `done` count: `2059` before restart -> `2076` after (~77 s post-restart).
