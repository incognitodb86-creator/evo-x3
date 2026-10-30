# judge/ - p15 clip pre-gate + per-check VLM judge (2026-10-29)

Flags only. **No auto-KEEP: Derrick gives the only KEEP.** Technical defects only, fictional adults only.
Built on Derrick's approval (2026-10-29 1:28 PM CT) to catch what the old Qwen3-VL checklist judge passed:
scene swaps, start-image abandoned, partner identity swap, target pose never reached.

## Files
- `prechecks.py`: CPU only. PySceneDetect cut counts plus VBench-style DINOv2/CLIP consistency vs the start image and the previous frame. Writes `out\<tag>.json` and `out\prechecks.csv`.
- `vlm_judge.py`: calls the existing `qwen3vl_judge` through llama-swap (`http://127.0.0.1:8080/v1/chat/completions`). It sends the start image, the intended prompt and target pose, a 2x4 storyboard of 8 frames, and the full-size last frame. It asks 5 absolute yes/no checks (same_scene, same_people, start_kept, target_reached, anatomy_defect), each with a short reason. Output is forced by `response_format: json_schema` (reason maxLength 200, max_tokens 2048), so it can't truncate. Writes `out\vlm\<tag>.json` plus a storyboard jpg.
- `.venv\`: a separate venv (ComfyUI's env is untouched). The installs are logged in `notes\installs_downloads.md`.

## Run
```
cd C:\AI\community\judge
.venv\Scripts\python.exe prechecks.py --match p15v2_      # CPU, ~100 s for 36 clips
.venv\Scripts\python.exe vlm_judge.py --match p15v2_      # GPU, ~3 min for 36 clips
```
`vlm_judge.py` waits until `gpu_guard.ps1` reports IDLE and `gpu_lock.ps1 -Acquire` succeeds (it polls every 60 s while a render holds the lock). When done it unloads `qwen3vl_judge` (`/api/models/unload/qwen3vl_judge`, with `/unload` as the fallback) and releases the lock. Inputs come from `C:\Users\derek\5slock\ralph-community\notes\p15v2_manifest.json`: the start image is `guides[0].image` under ComfyUI `input\`, and the prompt is `notes\p15_prompts\<prompt_file>`.

## Thresholds (tuned once on the 36 p15v2 clips against Max's 10-29 scoring)
A clip is flagged when ANY of these fires:
- precheck `jump`: DINOv2-small min frame-to-previous cosine < **0.82** (16 evenly spaced frames). Catches an abrupt change: start abandoned, scene swap or identity swap.
- precheck `static_no_transition`: only for transition clips (one ref, i.e. the start image is the OG still). DINOv2 last-frame-to-start cosine > **0.76**. The clip never left the start pose.
- VLM: any check answered as a defect.

Cuts (AdaptiveDetector/ContentDetector, stock defaults) are reported as info only. On p15v2 they fired on 3 good clips and 0 bad ones. Both thresholds sit on a plateau: 0.80-0.82 / 0.74-0.76 give the same result.

p15v2 result (14 bad / 22 good): prechecks 11/14 caught with 6 false flags; VLM 8/14 with 3; combined 12/14 (10 of the 12 old-judge misses) with 8 false flags. The old judge caught 2/14. See `/workspace/audits/2026-10-29-judge-upgrade-results.md` (Grok box). Same data for tuning and testing, so expect lower recall on new clips.

## Sources
- VBench subject/background consistency (DINO / CLIP vs first and previous frame): https://arxiv.org/abs/2311.17982, https://github.com/Vchitect/VBench/blob/master/vbench/utils.py
- PySceneDetect detectors and defaults: https://www.scenedetect.com/docs/latest/api/detectors.html, https://github.com/Breakthrough/PySceneDetect/issues/559
- llama.cpp server json_schema / response_format: https://github.com/ggml-org/llama.cpp/blob/HEAD/tools/server/README.md
- Absolute rather than pairwise judging: https://arxiv.org/pdf/2504.14716
- Models: facebook/dinov2-small, openai/clip-vit-base-patch32 (Hugging Face)
