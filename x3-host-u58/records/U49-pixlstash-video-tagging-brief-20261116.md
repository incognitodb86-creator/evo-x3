# U49 brief: PixlStash video import + tagging (Derrick approved, Nov 16 2026)
Work as user evo via `sudo -n -u evo` for files under /home/evo. Smallest change that works; follow PixlStash's own docs/community practice.
GOAL
1. /home/evo/AI/pixlstash-tagging/import_inbox.py: add .mp4 .webm .mov to the accepted extensions so Grok Downloader videos import into PixlStash (check PixlStash supports video upload via its API first; if it does not, stop BLOCKED and say so).
2. /home/evo/AI/pixlstash-tagging/tag_runner.py: for a video item, extract first, middle and last frames with ffmpeg to a temp dir, run the existing tagging path on those 3 frames, merge the tags (union, existing threshold) onto the video item, delete the temp frames. Images unchanged.
HARD RULES
- Back up each file to the sibling _archive/ as <name>.bak-20261116-u49 before editing.
- Never open, view, describe or print library images, frames, character names or tags. Counts only. Never cat unmatched-person-names.txt.
- Never print tokens/passwords; never put secrets on command lines.
- The tagger service u42-pixlstash-tagger (evo user unit) is RUNNING. Do not stop it until your edit is ready; then `systemctl --user restart u42-pixlstash-tagger.service` once (XDG_RUNTIME_DIR=/run/user/$(id -u evo)) and confirm it is active and the done count in u42_state.db rises within 5 min.
- Do not touch llama-swap, ComfyUI, Render, render-pi, or any other service. No git push.
TEST: py_compile both files; import ONE test video you generate yourself with ffmpeg testsrc (5 s) via import_inbox.py, confirm it lands in PixlStash and gets tags (count only), then delete that test item.
STOP CONDITION: write /home/derekboone/evo-x3/records/U49-RESULT.md with PASS/BLOCKED, files changed, backups, test result (counts only), tagger active + count before/after. Then stop.
