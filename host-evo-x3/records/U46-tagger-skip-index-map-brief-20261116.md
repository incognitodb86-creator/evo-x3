# U46 brief: tagger skips face-matched pictures + celebrity INDEX mapping (Derrick t1974u/t1975u/t1977u/t1978u, Nov 16 2026)

Host: EVO-X3. You run as derekboone; tagger files belong to user `evo` (use `sudo -n -u evo ...`; user units need `XDG_RUNTIME_DIR=/run/user/$(id -u evo)`).

## HARD RULES
- NEVER open, view, describe or download any picture. Never print or write tag names, person names or character names into logs, RESULT or stdout. Counts and ids only. (A name list file for Derrick is allowed, see Part B; do not cat it.)
- Do NOT change image size (MAX_IMAGE_EDGE), VLM concurrency (U44_VLM_CONCURRENCY=3), the model, llama-swap.yaml, or PixlStash server-config.json. Derrick refused smaller images.
- Back up every file you edit to /home/evo/AI/pixlstash-tagging/_archive/u46-20261116/ first. Never delete; move to _archive.
- No secrets on command lines; read tokens from /home/evo/.config/pixlstash/tagger-write.token inside Python.
- Never create PixlStash characters. Only ADD tags via POST /api/v1/pictures/{id}/tags.
- Do not touch the git repos, the Windows partitions, or anything on AlienPc.

## Part A: tagger skips pictures already fully matched by faces
File: /home/evo/AI/pixlstash-tagging/tag_runner.py (service u42-pixlstash-tagger.service, user evo; progress /var/tmp/u42-progress/U42-tagging-progress.{json,log}; state DB /home/evo/AI/pixlstash-tagging/u42_state.db).
- Before sending a picture to the VLM, if the picture has >=1 face AND zero unassigned faces (every face has a character_id), record it as status "skipped" (reason face_matched) and do not call the VLM. Pictures with no faces, or with any unassigned face, are tagged as today.
- Keep ETA/progress math correct with skips (count skips separately; ETA based on remaining non-skipped work if feasible).
- Keep Phase A (InsightFace) behaviour unchanged.
- py_compile, then restart: `systemctl --user restart u42-pixlstash-tagger.service` (as evo). It resumes from its state DB.
- Verify for 3+ minutes: status=running, done+skipped increasing, failed not climbing, skipped>0.

## Part B: map celebrity `person <Name>` tags to the INDEX
INDEX + aliases: /home/derekboone/AI/community/scripts/parody/resolve.py has load_index_files(INDEX_DIR) and load_aliases(ALIASES_PATH); INDEX_DIR=/home/derekboone/AI/community/index/h3-known-characters, ALIASES_PATH=/home/derekboone/AI/community/scripts/parody/aliases.json. Rows have "actor" and "character" (and "status"). Import these read-only; do not edit community files.
1. New module /home/evo/AI/pixlstash-tagging/index_map.py: given a person name, normalize (lowercase, alnum) and match INDEX rows by actor (and aliases). Return the list of linked character names. Skip names that match installed OC keys (submit_parody_run.installed_oc_refmod_keys / trained_oc_subject_keys) so OCs never get celebrity characters.
2. Backfill script /home/evo/AI/pixlstash-tagging/index_backfill.py: list all tags starting with "person " (GET /api/v1/tags), for each matched name find its pictures and add `character <Character>` tags (skip if already present). Idempotent. Support --dry-run (counts only). Write unmatched person names (one per line, with picture counts) to /home/evo/AI/pixlstash-tagging/unmatched-person-names.txt (0600) for Derrick; do NOT print its contents.
3. Hook into tag_runner.py: right after a `person <Name>` tag is added (around the char_named block), also add the mapped `character ...` tags. Do this as part of the same edit + single restart as Part A (one restart total).
4. Run index_backfill.py --dry-run, then for real. Report counts only: person tags seen, matched, unmatched, character tags added, failures.
Note: FCSydny/FCMegan pictures already carry manual tags (person Sydney Sweeney/character Cassie Howard, person Megan Fox/character Jennifer Check); backfill must not duplicate them.

## Gates
- py_compile OK for all edited/new files.
- Tagger running after restart with skipped>0 and failed not rising over 3 min.
- Backfill real run: failures == 0 (or explained).
- No change to MAX_IMAGE_EDGE / concurrency (show grep before/after).

## STOP CONDITION
Write /home/derekboone/evo-x3/records/U46-RESULT.md: PASS/FAIL per gate, files changed + backup paths, new progress line numbers (done/skipped/failed/rate/ETA), backfill counts, rollback steps (restore backups + restart). No names. Then stop.
