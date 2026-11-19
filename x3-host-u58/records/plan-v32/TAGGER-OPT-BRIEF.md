# TAGGER-OPT brief (Max Architect, Thu Nov 19 2026 ~7:05 AM CT; Derrick picked "Only do changes 1 and 2", t2544)

Goal: make the PixlStash tagger (/home/evo/AI/pixlstash-tagging/tag_runner.py, user unit u42-pixlstash-tagger.service as evo) faster and stop JSON failures, using ONLY these two changes:

1. JoyCaption native mode instead of JSON. JoyCaption (Llama-Joycaption-Beta-One, llama-swap model "joycaption") is a captioner trained on its own prompt modes, not JSON; 61 of 81 failures since 04:00 are JSONDecodeError. Switch query_vlm_for_image / parse_vlm_json to JoyCaption's official/community booru-tag-list prompt (check the JoyCaption Beta One model card / repo for the exact prompt wording) and parse the comma-separated list into tags. Keep the existing person/character naming path working (people -> "person X" tags -> index_map character tags) if JoyCaption can provide it; if it truly cannot, keep a fallback so nothing that works today is lost, and say exactly what changed in RESULT. Keep tags normalized with the existing normalize_tag/normalize_person_name and MAX_NEW_TAGS_PER_PIC. Lower max_tokens only if the tag list fits.
2. Videos: send ONE middle frame per video instead of first/middle/last (extract_video_frames_ffmpeg / process_one_picture video branch).

Out of scope (Derrick said no): -np / concurrency changes, ttl or any llama-swap.yaml edit, restarting llama-swap or any model. Do not touch Render, Forge, Gufo/flash-next, ComfyUI, pi, or the 7878 hub.

Rules:
- Take the X3 lease first: one line in /home/derekboone/AI/locks/x3-lease.txt (bot, what, start); clear it when done.
- Back up tag_runner.py (and any other file you edit) to /home/evo/AI/pixlstash-tagging/_archive/<name>.bak-20261119-tagopt before editing.
- PRIVACY: never open, view, print or quote library pictures, captions, tags, person or character names, or unmatched-person-names.txt. Verify by counts, status codes, parse success and timings only. Never print tokens/passwords/keys.
- Test: run existing unit tests if any, then a small live test of ~5 pictures + ~2 videos (counts only: ok/failed, parse failures, seconds per item, calls per item). Then restart u42-pixlstash-tagger.service as evo (it resumes from u42_state.db) and confirm it runs ~10 minutes: count done/failed/JSON errors in u42_state.db for that window vs. the 04:00-07:00 baseline (about 30 done per 10 min, ~2.5 JoyCaption calls per picture, ~6 s per call).
- Git: update the snapshot copy in ~/evo-x3/hosts/x3/pixlstash-tagging/ (no logs, no u42_state.db, no unmatched-person-names.txt), commit with explicit paths only (no git add -A), push to gitea only. No GitHub.
- Write /home/derekboone/evo-x3/records/plan-v32/TAGGER-OPT-RESULT.md: what changed (functions, prompt wording used and its source link), backups, test counts, before/after per-picture speed and failure counts, service restart time and status, lease cleared, commit hash.
