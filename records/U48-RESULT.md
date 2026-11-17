# U48 RESULT — 27B Ref2VA Prompt Rewriter on EVO-X3

**Status:** PASS (2026-11-16 15:05 CST)

## 1. Model Files & Verification
- Source repo: `https://huggingface.co/pytraveler/MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-GGUF`
- Directory: `/srv/models/ref2va-27b/` (`0755`, `derekboone:derekboone`)
- Files (all sizes and SHA256 verified against HF LFS hashes):
  - `MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-Q4_K_M.gguf`: `16,547,400,384` bytes (`16.547 GB` / `15.41 GiB`), SHA256 `ff75aa50230c3dc8d6fe0c0e155bba1a852fdcb032719181559f8e867b3106df`
  - `mmproj-MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-F16.gguf`: `927,607,328` bytes (`0.928 GB` / `0.86 GiB`), SHA256 `32c75dffda80d9e92c9b5008bf73a7c86415b279bf1b614ed2ff8390add5f9f6`
- Total size: `17,475,007,712` bytes (`17.475 GB` / `16.275 GiB`, within `<= 19 GB` limit).
- Recorded in `/srv/models/SHA256SUMS`.

## 2. Runtime Check & `llama-swap.yaml` Update
- Runtime image (same toolbox digest as `gemma4-heretic`): `docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6`
- `llama-server --version`: `version: 1.0.0-dev (build 12405, commit 9f26fe11c)` (`>= b10310`).
- Waited for `/home/derekboone/evo-x3/records/U47-RESULT.md` (appeared 14:58 CST) and for active Render pi chat request (`task 18407` on `gemma4-heretic` slot 1) to complete before restarting.
- Backup: `/etc/evo-x3/llama-swap.yaml.bak-20261116-u48-pre`
- Placed `ref2va-27b` in the non-exclusive `"small"` group (alongside `embed-small` and `joycaption`) on loopback port `8085` so `gemma4-heretic` stays resident on `8081`.
- Validation: `/usr/local/bin/llama-swap -config /etc/evo-x3/llama-swap.yaml -validate` -> `config is valid: 7 model(s), 0 peer(s)`.

### Exact `cmd` (no keys)
```text
podman run --rm --name llama-swap-ref2va-27b
  --network=host --device=/dev/dri --device=/dev/kfd --group-add=keep-groups
  --security-opt seccomp=unconfined
  -v /srv/models:/srv/models:ro,Z
  docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6
  llama-server --host 127.0.0.1 --port 8085
  -m /srv/models/ref2va-27b/MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-Q4_K_M.gguf
  --mmproj /srv/models/ref2va-27b/mmproj-MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-F16.gguf
  --jinja --load-mode none -fa on -ngl 999
  -np 1 -c 32768 -n 4096
  --temp 0
  --chat-template-kwargs '{"enable_thinking":false}'
  --alias ref2va-27b
```

### `llama-swap.yaml` Diff (no keys)
```diff
--- /etc/evo-x3/llama-swap.yaml.bak-20261116-u48-pre	2026-11-16 13:31:30.583991622 -0600
+++ /etc/evo-x3/llama-swap.yaml	2026-11-16 14:59:41.806465150 -0600
@@ -56,6 +56,7 @@
           members:
             - "embed-small"
             - "joycaption"
+            - "ref2va-27b"
 
 models:
   "flash-next":
@@ -246,3 +247,26 @@
     ttl: 3600
     concurrencyLimit: 1
     checkEndpoint: "/health"
+  "ref2va-27b":
+    # U48 2026-11-16 (Derrick t1989s7329): LightX2V MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA Q4_K_M + F16 mmproj
+    # from pytraveler/MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-GGUF (llama.cpp build 12405 >= b10310).
+    # Non-exclusive "small" group on loopback port 8085 so gemma4-heretic stays resident on 8081.
+    # Settings from plan / publisher validation: ctx 32768, thinking off, greedy (temp 0), output budget 4096, -ngl 999, -fa on.
+    cmd: |
+      podman run --rm --name llama-swap-ref2va-27b
+        --network=host --device=/dev/dri --device=/dev/kfd --group-add=keep-groups
+        --security-opt seccomp=unconfined
+        -v /srv/models:/srv/models:ro,Z
+        docker.io/kyuz0/amd-strix-halo-toolboxes@sha256:9a9e4d8f56e7792dffca1e2906d9399ff03ef87c9e2148983c9393fcbb8d7fb6
+        llama-server --host 127.0.0.1 --port 8085
+        -m /srv/models/ref2va-27b/MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-Q4_K_M.gguf
+        --mmproj /srv/models/ref2va-27b/mmproj-MiniMax-H3-Prompt-Rewriter-Qwen3.8-27B-Ref2VA-F16.gguf
+        --jinja --load-mode none -fa on -ngl 999
+        -np 1 -c 32768 -n 4096
+        --temp 0
+        --chat-template-kwargs '{"enable_thinking":false}'
+        --alias ref2va-27b
+    proxy: "http://127.0.0.1:8085"
+    ttl: 3600
+    concurrencyLimit: 1
+    checkEndpoint: "/health"
```

## 3. Restart & Service Verification
- Single `systemctl restart llama-swap` at: `2026-11-16 15:02:05 CST` (`active (running)`).
- Co-residency & model checks:
  - `gemma4-heretic`: responded `'ok.'` in `3.68 s`
  - `joycaption`: responded `'ok'` in `5.56 s`
  - `/running` after smoke test: `['gemma4-heretic:ready', 'joycaption:ready', 'ref2va-27b:ready']`
- PixlStash tagger counts (`/home/evo/AI/pixlstash-tagging/u42_state.db`, read-only):
  - Before restart (`15:02:02 CST`): `done=2058`, `failed=551`, `skipped=1108`
  - After restart (`15:04:48 CST`, ~2m43s later): `done=2086`, `failed=523`, `skipped=1108` (`done` resumed rising, +28)

## 4. Official Ref2VA System Prompt for Render
- Saved to `/home/evo/AI/render/rewriter/ref2va-system-prompt.md` (`23,923` bytes, `evo:evo`, `0644`).
- Built from LightX2V `REF_PREFIX` (per `pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI/minimax_h3_rewriter/qwen_prompt.py` and `lightx2v/.../post_vllm.py`) + `MiniMaxAI/MiniMax-H3` `docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` (`23,551` chars, SHA256 `ac11ebecde3e4961ccee6cf96b3f985ae4746bf2bc66109598b483add0f44d7d`).

## 5. Smoke Test (`ref2va-27b`)
- Input: synthetic PIL-generated `640x360` beach-at-sunset PNG (`u48_synthetic_beach.png`, deleted after run), ask `"a woman walks along a beach at sunset"`, `temperature=0`, `max_tokens=4096`, `chat_template_kwargs.enable_thinking=false`.
- Result: **PASS** — all 6 Ref2VA sections returned in order (`subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`), `finish_reason=stop`, `reasoning_len=0`.
- Metrics:
  - Load time: `13.79 s` (`15:03:08.2` container start -> `15:03:22` health check passed; `llama-server` `0.13.794 s` model loaded)
  - Total wall time (cold start + request): `93.761 s`
  - Prompt eval: `5,841` tokens in `30.063 s` (`194.29 tok/s`)
  - Generation: `423` tokens in `49.378 s` (`8.55 tok/s`)
  - Output word count: `322` words
  - Memory / Peak RAM delta (with `gemma4-heretic` and `joycaption` already loaded):
    - Host `MemAvailable`: `51,040,904 kB` (`48.68 GiB`) -> `28,877,032 kB` (`27.54 GiB`) (`-21.14 GiB` available; container RSS `715.3 MB`, `llama-server` `VmHWM` `738,700 kB`)
    - GPU GTT (`mem_info_gtt_used`): `53,642,776,576` B (`49.96 GiB`) -> `74,194,939,904` B (`69.10 GiB`) (`+19.14 GiB`)
    - GPU VRAM (`mem_info_vram_used`): `1,039,532,032` B -> `1,056,432,128` B (`+16.1 MiB`)
- Full smoke-test output: `/home/derekboone/evo-x3/records/U48-smoke-output.txt`
