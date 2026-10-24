# CA2 Community Usage Audit (0.2 / CA2)
Date: 2026-10-24
Last Updated: 2026-10-24

## Summary
Audit of AlienPc's operational USAGE and execution patterns against primary community sources (mostlygeek/llama-swap documentation, ComfyUI documentation, TenStrip / MiniMax-H3 model guides, pi documentation, ffmpeg documentation, and AcademiaSD/LoRAlab-TrainerStudio). While the earlier CF1 audit (`notes/cf1_setup_audit_20261024.md`) verified static configuration parameters, CA2 audits how the system actually executes across 7 functional areas:
1. Ralph loop + pi execution
2. llama-swap model and ComfyUI swapping
3. ComfyUI render queueing and life-cycle management
4. H3 / TenStrip video generation workflow
5. Review, verification, and stitching
6. LoRA training
7. Audio generation and decoding

All identified mismatches have been addressed in this pass.

## Usage Audit Table

| Area | Component / Flow | What We Do Now | Community Published Practice | Source URL | Match? |
|---|---|---|---|---|---|
| **1. Loop & pi** | Loop runner & argv | `ralph.ps1` runs `pi --print --provider llama-swap --model coding_swift15_iq3s "@PROMPT.md" "@fix_plan.md"` | Pinned argv with fixed context files and system prompt | https://pi.dev/docs/latest/cli-integration | match |
| **1. Loop & pi** | Exit gate protocol | Two-key exit: `<promise>COMPLETE</promise>` standalone token AND 0 open items in `fix_plan.md` outside `## Optional` | Minimum 2-signal / two-key exit to prevent premature loop exit | https://github.com/frankbria/ralph-claude-code | match |
| **1. Loop & pi** | Process status capture | `$piRc = $LASTEXITCODE`; logs `PI_NONZERO` on error, abort, or length cutoff | Process exit status inspect, distinguishing clean completion from truncated/aborted runs | https://pi.dev/docs/latest/cli-integration | match |
| **1. Loop & pi** | Stalled loop guard | `-Stuck 3`: 3 consecutive iterations without commits aborts loop with exit code 2 | Iteration boundary commit enforcement to prevent silent loops | https://github.com/ghuntley/how-to-ralph-wiggum | match |
| **1. Loop & pi** | Request timeouts | `httpIdleTimeoutMs: 1950000`, `retry.provider.timeoutMs: 1200000` (20 min) in `settings.json` | High provider timeouts configured to absorb upstream model cold swaps | https://pi.dev/docs/latest/settings | match |
| **1. Loop & pi** | Compound Engineering | Installed CE plugin; names only 4 needed skills (`/skill:ce-plan`, `ce-work`, `ce-code-review`, `ce-compound`) | Specific skill invocation to maintain compact context budget | https://github.com/EveryInc/compound-engineering-plugin | match |
| **2. llama-swap** | Routing mode | `routing.router.use: group` with `swap: true, exclusive: true` on group `main` | Exclusive group swap ensuring single GPU workload resident at one time | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/routing/groups-and-matrix.md | match |
| **2. llama-swap** | ComfyUI model ID | Reserved model ID `comfyui_auto` registered under `models:` | Dedicated ID `comfyui_auto` mapped to `/comfyui/` passthrough route | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **2. llama-swap** | Upstream ignore paths | `upstream.ignorePaths`: static assets, `^/api/jobs$`, and `^/ws(/\|$)` | Complete three-pattern set to prevent browser UI polling from triggering reloads | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match (switched from static-only) |
| **2. llama-swap** | ComfyUI TTL | `ttl: 0` on `comfyui_auto` and `comfyui_longvideo` | `ttl: 0` or long TTL to prevent websocket inactivity from unswapping during render | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **2. llama-swap** | Graceful stop handler | `comfy_graceful_stop.ps1` with `unloadTimeout: 1900` on both ComfyUI instances | Queue-aware graceful drain script with unloadTimeout exceeding stop budget | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match (switched comfyui_longvideo) |
| **2. llama-swap** | On-demand unload | `POST /api/models/unload/<model>` with 120-300s timeout | REST API POST endpoint for explicit model unloading | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/model-runtime/ttl-and-unloading.md | match |
| **2. llama-swap** | Readiness timeout | `healthCheckTimeout: 1200`, `timeouts.responseHeader: 1200` | Generous healthcheck timeouts for heavy weight initialization | https://github.com/mostlygeek/llama-swap/blob/main/docs/reference/configuration-overview.md | match |
| **3. Queueing** | Target endpoint route | `run_graph_job.py` and `comm.py` point to `http://127.0.0.1:8080/comfyui` | Port-agnostic `/comfyui/` endpoint for `comfyui_auto` rather than hardcoded port | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match (switched from :10004 & /upstream) |
| **3. Queueing** | Cold start wake | Polls `/comfyui/system_stats` to trigger startup; waits for ComfyUI ready | Starting path polling (root GET `/comfyui/` is ignored and returns 404 while unloaded) | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match (switched from root GET) |
| **3. Queueing** | Post-job cleanup | `run_graph_job.py` calls `POST /api/models/unload/comfyui_auto` on finish | Explicit unload frees VRAM immediately for subsequent LLM requests | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/model-runtime/ttl-and-unloading.md | match |
| **4. H3 Workflow** | Frame length math | 362 frames (15.083 s at 24 fps) using grid formula `17k + 5` (`17*21 + 5 = 362`) | Legal frame lengths must satisfy `(frames - 5) % 17 == 0` | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **4. H3 Workflow** | Multi-chunk continuation | 3-chunk chain: 124 initial + 2x(overlap 22 + extension 119) = 362 frames via published nodes | `ComfyUI-Minimax-H3-Continuation` v0.6.3 (`MiniMaxH3GuidedContinuationWindow`, `TailGuide`, `Append`) | https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation | match |
| **4. H3 Workflow** | Dual VAE configuration | int8 video VAE (`minimax_h3_video_vae_int8_convrot`) + fp32 audio VAE (`minimax_h3_audio_vae_fp32`) | Standard published VAE pairing for MiniMax-H3 | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **4. H3 Workflow** | Sampling parameters | `res_multistep` + `simple`, 10 steps, euler, shift 10.0 video / 3.0 audio, `BasicGuider` (CFG 1.0) | Recommended 8-12 step turbo setup with basic guider | https://huggingface.co/TenStrip/10Eros-Max/discussions/61 | match |
| **4. H3 Workflow** | Anti-Burn LoRA | `h3_antiburn_universal_v1.safetensors` @ 0.5 on chunk 2+ only | Anti-Burn applied strictly on continuation chunks to avoid degradation | https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA | match |
| **5. Review/Stitch** | Content safety guard | `comm.guard_ok` scans all prompt-bearing text nodes before submission; tests pass | Strict programmatic filter for fictional adult content | Local rule & safety baseline | match |
| **5. Review/Stitch** | Objective validation | ffprobe stream verification (video 1344x768, packet count, audio stream, duration) | ffprobe JSON parsing by field name | https://ffmpeg.org/ | match |
| **5. Review/Stitch** | Artifact detection | `blackdetect` (d=1.0, pix_th=0.10) and `freezedetect` (n=-60dB, d=2) via ffmpeg | Automated objective artifact detection without subjective vision models | https://ffmpeg.org/ffmpeg-filters.html | match |
| **5. Review/Stitch** | Contact sheet | Tile filter contact sheet generation for visual inspection | ffmpeg select & tile filter | https://ffmpeg.org/ffmpeg-filters.html | match |
| **5. Review/Stitch** | Video concatenation | Concat demuxer with re-encode fallback | ffmpeg concat demuxer documentation | https://trac.ffmpeg.org/wiki/Concatenation | match |
| **6. LoRA Training** | Trainer package | `AcademiaSD_LoRAlab-TrainerStudio` on disk | MiniMax-H3 video LoRA trainer from images/clips/audio (8 GB VRAM min) | https://github.com/AcademiaSD/LoRAlab-TrainerStudio | match |
| **7. Audio** | Audio latent & decode | Pipeline generates audio latent decoded by `VAEDecodeAudio` into 32000 Hz stereo AAC | Native MiniMax-H3 audio latent generation and decoding | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |

## Key Findings
1. **Endpoint Alignment (Switch C)**: `scripts/run_graph_job.py` and `scripts/comm.py` previously referenced hardcoded ports (e.g. `http://127.0.0.1:10004`) or `/upstream/comfyui_auto`. Both have been aligned to the documented `/comfyui/` route (`http://127.0.0.1:8080/comfyui`), which connects to the reserved `comfyui_auto` model in llama-swap and handles port allocation dynamically.
2. **Cold Start Wake Logic**: Waking ComfyUI by issuing a GET to `/comfyui/` was ineffective because the exact root route is in the ignore list and returns 404 when the model is unloaded. The wake routine now polls `/comfyui/system_stats`, a starting path that triggers model loading and waits for readiness up to `healthCheckTimeout` (1200s).
3. **Upstream Ignore Paths (Switch A)**: `upstream.ignorePaths` in `llama-swap.yaml` includes the full three patterns (`.*\.(js|json|css|png|gif|jpg|jpeg|ico|txt)$`, `^/api/jobs$`, `^/ws(/|$)`), preventing browser tabs polling `/api/jobs` or reconnecting websockets from keeping the model indefinitely resident or triggering spurious swaps.
4. **Graceful Stop (Switch B)**: Both `comfyui_auto` and `comfyui_longvideo` utilize `comfy_graceful_stop.ps1` with an `unloadTimeout` of 1900s, ensuring active render jobs finish cleanly rather than being terminated abruptly by taskkill.
5. **GPU Sharing Protocol**: Forge's loop can safely trigger renders through `run_graph_job.py`. The LLM's subsequent request waits for the model to swap back, supported by pi's 1200s provider timeout (`retry.provider.timeoutMs`).

## Action Items
- Completed: Switched `comm.py` line 6 to `BASE = LS + "/comfyui"`.
- Completed: Updated `comfy_ctl.py` to use `LS + "/comfyui"` for status and queue checks.
- Completed: Verified `run_graph_job.py` uses `/comfyui` and `/comfyui/system_stats` for readiness polling.
- Verified: `test_p6_review.py` (21 passed) and full test suite (38 passed) passing with zero failures.
- Ready: Proceed to render all 6 staged HC15 clips end to end.
