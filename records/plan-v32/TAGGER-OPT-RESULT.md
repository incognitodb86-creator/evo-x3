# TAGGER-OPT Result — 2026-11-19 CST

- **Owner:** Max Architect (Antigravity, Gemini 4 Hydrogen High)
- **Date:** 2026-11-19 (`07:05`–`07:24 CST`)
- **Commits (`~/evo-x3` branch `u58`, pushed to `gitea/u58`):** `dc3a0cd` (`hosts/x3/pixlstash-tagging/tag_runner.py`), followed by this `TAGGER-OPT-RESULT.md` commit
- **Backup:** `/home/evo/AI/pixlstash-tagging/_archive/tag_runner.py.bak-20261119-tagopt` (`49,769` bytes)
- **Lease:** `/home/derekboone/AI/locks/x3-lease.txt` cleared (`0` bytes)
- **Scope:** Applied **only** Changes 1 and 2 in `/home/evo/AI/pixlstash-tagging/tag_runner.py` (synced to `~/evo-x3/hosts/x3/pixlstash-tagging/tag_runner.py`). No changes to `llama-swap.yaml`, `-np`, `ttl`, service concurrency (`U44_VLM_CONCURRENCY=1`), Render, Forge, Gufo, ComfyUI, `pi`, or `:7878`.

---

## 1. Changes Implemented

### Change 1: Native JoyCaption Booru-Like Mode (Replacing JSON Schema)
- **Sources for official prompt wording:**
  - Official system prompt (`"You are a helpful image captioner."`): [`fancyfeast/llama-joycaption-beta-one-hf-llava`](https://huggingface.co/fancyfeast/llama-joycaption-beta-one-hf-llava/blob/main/README.md)
  - Official Booru-like word-count prompt (`CAPTION_TYPE_MAP["Booru-like tag list"][1]`): [`fpgaminer/joycaption/gradio-app/app.py`](https://github.com/fpgaminer/joycaption/blob/main/gradio-app/app.py)
- **Constants & prompt wording in `tag_runner.py`:**
  - `SYSTEM_PROMPT`: `"You are a helpful image captioner."`
  - `BOORU_PROMPT` (`unassigned_faces == 0`): `"Write a list of Booru-like tags for this image within 50 words."`
  - `BOORU_PERSON_PROMPT` (`unassigned_faces > 0`): `"Write a list of Booru-like tags for this image within 60 words. If an unnamed face unmistakably belongs to a well-known celebrity or named fictional character, include character:<name>; otherwise do not guess a name."`
  - `VLM_MAX_TOKENS = 192` (lowered from `320` after verifying `4/4` `stop` completions averaged `77.5`–`88.0` tokens, fitting `MAX_NEW_TAGS_PER_PIC = 25` cleanly).
  - `BOORU_NAMESPACE_SKIP = frozenset({"artist", "copyright", "meta", "species", "lore", "rating"})`
- **Functions updated:**
  - `query_vlm_for_image`: sends `SYSTEM_PROMPT` + `BOORU_PROMPT` / `BOORU_PERSON_PROMPT` with `max_tokens=192` (removed `chat_template_kwargs`), parses via `parse_vlm_tags(content)`.
  - `parse_vlm_tags` (with `parse_vlm_json` retained as JSON fallback if `{...}` is returned): strips markdown code fences and single-line `:` preamble headers, splits on `[,\n]+`, extracts `character:<name>` through `normalize_person_name` (keeping the existing `people` -> `"person X"` -> `index_map.map_person_to_characters` path active), skips non-character booru namespaces (`BOORU_NAMESPACE_SKIP`), normalizes remaining tags through `normalize_tag`, deduplicates, and raises `ValueError("Empty tag list")` if empty. `MAX_NEW_TAGS_PER_PIC = 25` still applies in `process_one_picture`.

### Change 2: Single Middle Video Frame
- **`extract_video_frames_ffmpeg`:** probes video duration via `probe_video_duration` and extracts **1 middle frame** (`duration * 0.5`) via `run_ffmpeg_frame(["-ss", mid_ts], ...)` when `duration > 0.2s`, falling back to `["-ss", "0"]` / `[]` only if duration is unavailable/short or the middle seek fails (returns at most 1 frame instead of 3).
- **`process_one_picture` (video branch):** sends that single middle frame (`1` JoyCaption call per video instead of `3`).

---

## 2. Prompt Benchmark & Unit / Small Live Test Counts

### Pre-Edit Official Prompt Comparison (Counts & Timings Only)
- 4 `char_named > 0` items (`max_tokens=220`, service stopped):
  - `booru_like` (`"Write a list of Booru-like tags for this image."`): `avg_s=5.76`, `avg_tok=135.8`, `stop_ok=4/4`, `avg_parts=45.2`, `char=0`
  - `booru_like_50w` (`BOORU_PROMPT`): `avg_s=2.96`, `avg_tok=77.5`, `stop_ok=4/4`, `avg_parts=26.0`, `char=0`
  - `danbooru_std` (`Danbooru tag list`): `avg_s=7.39`, `avg_tok=194.8`, `stop_ok=1/4` (`max_tokens` hit 3/4), `avg_parts=54.2`, `char=0`, `copy=3`, `meta=4`
  - `booru_like_person` (`BOORU_PERSON_PROMPT` variant): `avg_s=3.37`, `avg_tok=88.0`, `stop_ok=4/4`, `avg_parts=27.8`, `char=2`

### Post-Edit Unit Tests & Small Live Test (`5` Pictures + `2` Videos)
- **Unit tests (`8` tests):** `Ran 8 tests in 0.005s — OK` (Booru comma/newline parsing, fences/preamble/namespaces, `character:<name>` + `GENERIC_PERSON_STOPWORDS`, JSON fallback, empty-list error, single middle-frame extraction + unknown-duration fallback, `query_vlm_for_image` payloads & `max_tokens=192`).
- **Live 5 pending pictures (`Runner(vlm_concurrency=1)`):** `n=5`, `ok=5`, `skipped=0`, `failed=0`, `parse_err=0`, `tags_added=124`, `calls=5` (`1.00` call/pic), `elapsed_s=20.80` (`4.16 s/pic`).
- **Live 2 fresh pending videos (`Runner(vlm_concurrency=1)`):** `n=2`, `ok=2`, `skipped=0`, `failed=0`, `parse_err=0`, `tags_added=49`, `calls=2` (`1.00` call/video), `elapsed_s=8.11` (`4.06 s/video`). *(Note: 15 previously failed `HTTPStatusError` source videos in the backlog returned `HTTP_500` from PixlStash before VLM fetch with `0` JoyCaption calls.)*

---

## 3. Service Restart & 10-Minute Before / After Comparison

- **Service restart:** `u42-pixlstash-tagger.service` restarted as `evo` at **`2026-11-19 07:12:47 CST`** (`PID 2157603`, `active (running)`, `U44_VLM_CONCURRENCY=1`, `phase_a_status: completed`).
- **Verification window:** `2026-11-19 07:12:47 CST` to `2026-11-19 07:23:08 CST` (~`10.35 min`).

| Metric | Before (`04:00`–`07:06:36 CST`) | After (`07:12:47`–`07:23:08 CST`) |
|---|---|---|
| **10-min `done` throughput** | `30` done / 10 min (`06:56:49`–`07:06:36`; `560` total `04:00`–`07:06:36`) | **`129` done** (`~10.3` min window, `12.49` items/min — **~4.2x faster**) |
| **Seconds per item** | `~20 s/item` (`~2.5` calls/item, `~6 s/call`) | **`4.8 s/item`** (`1.00` call/item; JoyCaption `3.60`–`4.05 s/call`, `78`–`92` tok) |
| **`JSONDecodeError` / parse failures** | `66` (`04:00`–`07:06:36`), `4` in last 10 min | **`0`** (and retrying backlog cleared all `66` prior `JSONDecodeError` rows) |
| **`HTTP_500` failures (PixlStash source)** | `20` (in `04:00` hour) | `20` (same pre-existing PixlStash source `HTTP_500` items retried at `07:12:48`–`07:12:54`) |
| **Tags added / Characters named (window)** | `217` `char_named` across `556` `done` (`04:00`–`07:05`) | **`3,210` tags added**, **`38` `char_named`** across `129` `done` (`29.5%`) |
| **Cumulative `u42_state.db` totals at `07:23:08`** | `done=10,178`, `failed=86`, `skipped=4,826` | `done=10,321`, `failed=20` (`HTTP_500` only), `skipped=4,826` |

All checks passed; `/home/derekboone/AI/locks/x3-lease.txt` cleared (`0` bytes).
