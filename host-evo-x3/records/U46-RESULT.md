# U46 Result (2026-11-16)

## Gate Summary

| Gate | Status | Notes |
| --- | --- | --- |
| `py_compile` OK for all edited/new files | **PASS** | `index_map.py`, `index_backfill.py`, `tag_runner.py` all compiled with exit code 0 via `/home/evo/.venvs/pixlstash/bin/python -m py_compile`. |
| Tagger running after single restart (`skipped > 0`, `failed` not rising over 3 min) | **PASS (with note)** | Restarted `u42-pixlstash-tagger.service` once at `13:07:59 CST`. Verified at `13:11:43 CST` (3m44s): `status=running`, `done=1721`, `skipped=93` (`face_matched`), `failed=0`. Later at `13:19` and `13:21-13:28`, rapid skip bursts + concurrent backfill triggered `HTTP_429` rate limits (`failed=602` total in `u42_state.db`, all `HTTP_429`, retried on resume). At `13:28:24 CST`, service remains `active`/`running` (`done=2004`, `skipped=1103`, `eta=6:58:36`). |
| Backfill real run (`failures == 0`) | **PASS** | Run 1 (`13:08-13:20 CST`): `person_tags_seen=9`, `matched=7`, `unmatched=2`, `oc_skipped=0`, `pictures_checked=14529`, `already_present=14513`, `character_tags_added=12707`, `failures=0`. Run 2 (throttled + 429 backoff after PixlStash background tag sync completed, `13:21-13:28 CST`): `person_tags_seen=13`, `matched=10`, `unmatched=3`, `oc_skipped=0`, `pictures_checked=19250`, `already_present=31947`, `character_tags_added=4713`, `failures=0`. Post-run `--dry-run` confirmed idempotency (`character_tags_would_add=0`, `already_present=36660`, `failures=0`). |
| No change to `MAX_IMAGE_EDGE` / concurrency (`grep` before/after) | **PASS** | Identical before and after edit (`MAX_IMAGE_EDGE = 1280`, `DEFAULT_VLM_CONCURRENCY = 3`, `VLM_CONCURRENCY_ENV = "U44_VLM_CONCURRENCY"`, `VLM_MODEL = "gemma4-heretic"`, `Environment=U44_VLM_CONCURRENCY=3`). |

## Files Changed & Backups

- Edited: `/home/evo/AI/pixlstash-tagging/tag_runner.py`
  - Backup: `/home/evo/AI/pixlstash-tagging/_archive/u46-20261116/tag_runner.py.bak` (42,705 bytes, `0750`)
- Added: `/home/evo/AI/pixlstash-tagging/index_map.py` (`0640`)
- Added: `/home/evo/AI/pixlstash-tagging/index_backfill.py` (`0750`)
- Generated for Derrick: `/home/evo/AI/pixlstash-tagging/unmatched-person-names.txt` (`0600`, 69 bytes)
- Note on community files: `/home/derekboone` is `0700`, so `index_map.py` selects `/home/derekboone/AI/...` when readable or falls back read-only to the synced `/home/evo/AI/community` and `/home/evo/AI/comfy-alienpc/models/refmods` mirrors when running as `evo`. No community files were modified.

## `grep` Before / After (`MAX_IMAGE_EDGE`, `CONCURRENCY`, `VLM_MODEL`)

Before:
```text
/home/evo/AI/pixlstash-tagging/tag_runner.py:36:VLM_MODEL = "gemma4-heretic"
/home/evo/AI/pixlstash-tagging/tag_runner.py:63:MAX_IMAGE_EDGE = 1280
/home/evo/AI/pixlstash-tagging/tag_runner.py:66:DEFAULT_VLM_CONCURRENCY = 3
/home/evo/AI/pixlstash-tagging/tag_runner.py:67:VLM_CONCURRENCY_ENV = "U44_VLM_CONCURRENCY"
/home/evo/AI/pixlstash-tagging/tag_runner.py:102:        raw_env = os.environ.get(VLM_CONCURRENCY_ENV, "").strip()
/home/evo/AI/pixlstash-tagging/tag_runner.py:103:        val = int(raw_env) if raw_env else DEFAULT_VLM_CONCURRENCY
/home/evo/AI/pixlstash-tagging/tag_runner.py:293:        if max(w, h) > MAX_IMAGE_EDGE:
/home/evo/AI/pixlstash-tagging/tag_runner.py:294:            rgb.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
/home/evo/AI/pixlstash-tagging/tag_runner.py:779:            "model": VLM_MODEL,
/home/evo/AI/pixlstash-tagging/tag_runner.py:1024:        help=f"Number of concurrent VLM requests (env {VLM_CONCURRENCY_ENV}, default {DEFAULT_VLM_CONCURRENCY})",
/home/evo/.config/systemd/user/u42-pixlstash-tagger.service:8:Environment=U44_VLM_CONCURRENCY=3
```

After:
```text
/home/evo/AI/pixlstash-tagging/tag_runner.py:41:VLM_MODEL = "gemma4-heretic"
/home/evo/AI/pixlstash-tagging/tag_runner.py:68:MAX_IMAGE_EDGE = 1280
/home/evo/AI/pixlstash-tagging/tag_runner.py:71:DEFAULT_VLM_CONCURRENCY = 3
/home/evo/AI/pixlstash-tagging/tag_runner.py:72:VLM_CONCURRENCY_ENV = "U44_VLM_CONCURRENCY"
/home/evo/AI/pixlstash-tagging/tag_runner.py:107:        raw_env = os.environ.get(VLM_CONCURRENCY_ENV, "").strip()
/home/evo/AI/pixlstash-tagging/tag_runner.py:108:        val = int(raw_env) if raw_env else DEFAULT_VLM_CONCURRENCY
/home/evo/AI/pixlstash-tagging/tag_runner.py:298:        if max(w, h) > MAX_IMAGE_EDGE:
/home/evo/AI/pixlstash-tagging/tag_runner.py:299:            rgb.thumbnail((MAX_IMAGE_EDGE, MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
/home/evo/AI/pixlstash-tagging/tag_runner.py:804:            "model": VLM_MODEL,
/home/evo/AI/pixlstash-tagging/tag_runner.py:1065:        help=f"Number of concurrent VLM requests (env {VLM_CONCURRENCY_ENV}, default {DEFAULT_VLM_CONCURRENCY})",
/home/evo/.config/systemd/user/u42-pixlstash-tagger.service:8:Environment=U44_VLM_CONCURRENCY=3
```

## Latest Tagger Progress Numbers

- At 3m44s post-restart (`2026-11-16 13:11:43 CST`):
  - `status=running`, `done=1721/32964`, `skipped=93` (`face_matched`), `failed=0`, `sec_per_img=3.36`, `rate_per_min=17.84`, `remaining_non_skipped=12930`, `eta=12:04:04`
- At completion check (`2026-11-16 13:28:24 CST`, `/var/tmp/u42-progress/U42-tagging-progress.json`):
  - `status=running`, `pid=139203`, `total_pictures=32964`
  - `done=2004`, `skipped=1103`, `failed=602` (`HTTP_429` only)
  - `tags_added=29550`, `faces_assigned_insightface=15459`, `faces_processed=17048`, `characters_named=81`
  - `seconds_per_image=3.5`, `rate_per_min=17.12`, `remaining_non_skipped=7176`, `eta=6:58:36`
  - Latest log line (`2026-11-16 13:28:23 CST`):
    `[2026-11-16 13:28:23 CST] status=running done=2003/32964 skipped=1101 failed=602 tags_added=29534 faces_assigned_insightface=15459 faces_processed=17047 characters_named=81 sec_per_img=3.51 eta=6:59:30 vlm_conc=3 vlm_sec_per_img=3.51 vlm_pic_per_min=17.08 vlm_eta=6:59:30 phase_a=completed phase_a_fpm=0.0`

## Backfill Counts

1. Initial `--dry-run`: `person_tags_seen=9`, `matched=7`, `unmatched=2`, `oc_skipped=0`, `pictures_checked=14384`, `already_present=14368`, `character_tags_would_add=12562`, `failures=0`.
2. Real run 1 (`13:08-13:20 CST`): `person_tags_seen=9`, `matched=7`, `unmatched=2`, `oc_skipped=0`, `pictures_checked=14529`, `already_present=14513`, `character_tags_added=12707`, `failures=0`.
3. Real run 2 (throttled with 429 retry/backoff, `13:21-13:28 CST`): `person_tags_seen=13`, `matched=10`, `unmatched=3`, `oc_skipped=0`, `pictures_checked=19250`, `already_present=31947`, `character_tags_added=4713`, `failures=0`.
   - Total character tags added across both real runs: `17420`, `failures=0`.
4. Final `--dry-run` (`13:28 CST`): `person_tags_seen=15`, `matched=10`, `unmatched=5`, `oc_skipped=0`, `pictures_checked=19250`, `already_present=36660`, `character_tags_would_add=0`, `failures=0`.

## Rollback Steps

```bash
sudo -n -u evo cp -a /home/evo/AI/pixlstash-tagging/_archive/u46-20261116/tag_runner.py.bak /home/evo/AI/pixlstash-tagging/tag_runner.py
sudo -n -u evo mv /home/evo/AI/pixlstash-tagging/index_map.py /home/evo/AI/pixlstash-tagging/_archive/u46-20261116/
sudo -n -u evo mv /home/evo/AI/pixlstash-tagging/index_backfill.py /home/evo/AI/pixlstash-tagging/_archive/u46-20261116/
sudo -n -u evo XDG_RUNTIME_DIR=/run/user/$(id -u evo) systemctl --user restart u42-pixlstash-tagger.service
```
