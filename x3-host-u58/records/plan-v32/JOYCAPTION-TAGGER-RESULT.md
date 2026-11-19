# JoyCaption Nightly Tagger Result — 2026-11-18 CST

- **Goal:** Switch the nightly `u42-pixlstash-tagger` (`04:00:00` timer) to **JoyCaption** (`joycaption` slot from U47 in `/etc/evo-x3/llama-swap.yaml`) while keeping Gufo resident (`flash-next-uncensored-v2`) and Render/Forge chats working (`MemAvailable >= 4 GiB`).

## Changes & Backups (No Deletes, No `llama-swap.yaml` Edits)
- **`/etc/evo-x3/llama-swap.yaml`:** Unchanged — already contained the U47 `"joycaption"` non-exclusive `"small"` group slot (`Llama-Joycaption-Beta-One-Hf-Llava-Q8_0.gguf` + `f16` mmproj on `127.0.0.1:8084`, `-np 1 -c 4096`, `ttl: 300`, `concurrencyLimit: 1`).
- **`/home/evo/AI/pixlstash-tagging/tag_runner.py`:**
  - Backup: `/home/evo/AI/pixlstash-tagging/_archive/tag_runner.py.bak-20261118-joycaption`
  - Change: `VLM_MODEL = "joycaption"` (was `"gemma4-heretic"`).
- **`/home/evo/.config/systemd/user/u42-pixlstash-tagger.service`:**
  - Backup: `/home/evo/AI/pixlstash-tagging/_archive/u42-pixlstash-tagger.service.bak-20261118-joycaption`
  - Change: `U44_VLM_CONCURRENCY=1` (matching `joycaption` `concurrencyLimit: 1`, `-np 1`), `Description=U42 PixlStash Unattended Tagging Sidecar (joycaption + InsightFace)`, `systemctl --user daemon-reload`.
- **Nightly timer:** `u42-pixlstash-tagger.timer` remains `enabled` (`OnCalendar=*-*-* 04:00:00`, next run `Thu 2026-11-19 04:00:00 CST`).

## Verification (Counts & Memory Only)
- **5-item real PixlStash test (`tag_runner.Runner(vlm_concurrency=1).query_vlm_for_image`):**
  - `sample_count: 5` -> **`ok=5 fail=0`** (`wall_s=29.89`, ~6.0 s/item including JoyCaption load).
- **Co-residency & memory:**
  - `/running` with JoyCaption active: `[('embed-small', 'ready'), ('flash-next-uncensored-v2', 'ready'), ('joycaption', 'ready')]` (`NRestarts=0`).
  - `MemAvailable`: `9,873,272 kB` (**`9.42 GiB`** free, well above the `4 GiB` floor) with JoyCaption loaded; `19,686,760 kB` (`18.77 GiB`) after `ttl: 300` idle unload.
  - `Forge-X3` and `Render-X3` one-shot checks: `FORGE_BESIDE_JC_OK`, `RENDER_BESIDE_JC_OK`.
