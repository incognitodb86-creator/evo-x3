---
name: pixlstash-image-library
description: "Use when finding stills in the local PixlStash library."
---

# PixlStash image library

Use when the user asks to find/pick reference images of their characters (`FCSydny`, `FCMegan`, etc.) or styles from the local PixlStash service — e.g. "find me 5 images of FCSydny in office attire".

## Rules (strict)
- **Use PixlStash HTTP API (`127.0.0.1:9537`) with `curl` and `jq`.**
- **NEVER write scratch `.py` files (`write_file`), NEVER query `vault.db` directly, NEVER run `python3 -c`, and NEVER use heredocs (`<<EOF`).** Both `python3 -c` and heredocs trigger approval prompts; `curl` + `jq` runs cleanly with no approval prompt.
- **Auth:** Read the read-only Bearer token inside the `curl` command from `/home/evo/.config/pixlstash/render-read.token`. Never print, echo, log, or embed the token anywhere.
- **Image paths (`MEDIA:`):** `file_path` returned by PixlStash is relative to `/home/evo/AI/5slock/libraries/`, and many paths contain spaces (which break `MEDIA:` token parsing). Always expose selected stills via space-free symlinks `/home/evo/.hermes/image_cache/pixl_<id>.<ext>` (unless `file_path` already has no whitespace) and return each selected image on its own `MEDIA:` line:
  `MEDIA:/home/evo/.hermes/image_cache/pixl_<id>.<ext>`
  (Do not place `MEDIA:` lines inside code fences.)

## Workflow (1–2 `curl | jq` calls)

1. **Resolve character ID (if needed):**
   ```bash
   curl -sS -H "Authorization: Bearer $(cat /home/evo/.config/pixlstash/render-read.token)" \
     "http://127.0.0.1:9537/api/v1/characters" | jq -r '.[] | "\(.id)\t\(.name)"'
   ```
   (`FCSydny` is `character_id=1`.)

2. **Query tagged stills via `GET /api/v1/pictures` and emit `MEDIA:` lines:**
   Use `character_id=`, repeatable `tag=` / `rejected_tag=`, `format=JPEG&format=PNG` (to exclude `.mp4` videos when stills are requested), `fields=id,file_path,format,score,smart_score`, `sort=SCORE` (or `SMART_SCORE`), and `limit=`:
   ```bash
   curl -sS -H "Authorization: Bearer $(cat /home/evo/.config/pixlstash/render-read.token)" \
     "http://127.0.0.1:9537/api/v1/pictures?character_id=1&tag=office&format=JPEG&format=PNG&fields=id,file_path,format,score,smart_score&sort=SMART_SCORE&limit=5" \
     | jq -r '.[] | "\(.id)\t\(.file_path)"' \
     | while IFS=$'\t' read -r id fp; do ext="${fp##*.}"; ln -sf "/home/evo/AI/5slock/libraries/$fp" "/home/evo/.hermes/image_cache/pixl_${id}.${ext}"; echo "MEDIA:/home/evo/.hermes/image_cache/pixl_${id}.${ext}"; done
   ```
   - Multiple `tag=` params filter by all listed tags; `rejected_tag=` excludes unwanted tags.
   - To discover exact tag names before filtering:
     ```bash
     curl -sS -H "Authorization: Bearer $(cat /home/evo/.config/pixlstash/render-read.token)" \
       "http://127.0.0.1:9537/api/v1/tags" | jq -r '.[] | select(.tag | test("office|work|suit|blazer|skirt"; "i")) | "\(.count)\t\(.tag)"' | head -n 40
     ```

3. **Semantic / text search via `GET /api/v1/pictures/search`:**
   Use `query=` (URL-encoded via `--data-urlencode` with `curl -sSG`) when searching by free-text description or attire style:
   ```bash
   curl -sSG -H "Authorization: Bearer $(cat /home/evo/.config/pixlstash/render-read.token)" \
     --data-urlencode "query=office attire" \
     "http://127.0.0.1:9537/api/v1/pictures/search?limit=5" \
     | jq -r '.[] | select(.format != "MP4") | "\(.id)\t\(.file_path)"' \
     | while IFS=$'\t' read -r id fp; do ext="${fp##*.}"; ln -sf "/home/evo/AI/5slock/libraries/$fp" "/home/evo/.hermes/image_cache/pixl_${id}.${ext}"; echo "MEDIA:/home/evo/.hermes/image_cache/pixl_${id}.${ext}"; done
   ```
   Note: do not pass `character_id=` to `/api/v1/pictures/search` for large character sets (>32k images hits SQLite bind-variable limit); use `GET /api/v1/pictures` with `character_id=` + `tag=` for character-scoped queries.

## Delivery
- Honor setting/attire constraints strictly; pick the top matching stills and deliver the exact requested count as `MEDIA:/home/evo/.hermes/image_cache/pixl_<id>.<ext>` lines (one per line) cleanly and promptly.
