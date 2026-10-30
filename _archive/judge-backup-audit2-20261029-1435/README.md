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

## Modes and thresholds (refined 2026-10-29 PM, see /workspace/audits/2026-10-29-judge-refine-results.md on the Grok box)
**Default = two tiers.** Neither tier ever KEEPs.
- **FLAG**: any `vlm_judge.py` check answered as a defect (same_scene=no, same_people=no, start_kept=no, target_reached=no, anatomy_defect=yes). There is no threshold to fit. On p15v2 it flagged 8/14 bad clips and 3/22 good. Caveat: the v3 prompt wording was chosen on these same clips. The untuned v1 prompt flagged 5/14 bad and 2/22 good.
- **REVIEW hint**: `prechecks.py` flags.
  - `jump`: DINOv2 min frame-to-previous cosine < 0.82.
  - `static_no_transition`: one-ref transition clips only, DINOv2 last-frame-to-start cosine > 0.76.
  - These were fitted on the 36 clips. Under leave-one-writer-out CV they caught 10/14 bad clips but also 13/22 good ones, so treat them as "look here first", not as fails.
- Cuts (PySceneDetect, stock defaults) are info only.
- `p_defect` in each VLM JSON is the logprob probability of the defect answer. It is stored for future calibration and **not** used for flags: thresholding it under CV gave 11/14 bad but 12/22 good.

Tried and dropped (no held-out gain on p15v2):
- a second zoomed anatomy call (mid and last frame at full size): it still missed the anatomy blob;
- CLIP similarity on a background-only ring;
- Farneback optical-flow motion stall.

## Sources
- VBench subject/background consistency (DINO / CLIP vs first and previous frame): https://arxiv.org/abs/2311.17982, https://github.com/Vchitect/VBench/blob/master/vbench/utils.py
- PySceneDetect detectors and defaults: https://www.scenedetect.com/docs/latest/api/detectors.html, https://github.com/Breakthrough/PySceneDetect/issues/559
- llama.cpp server json_schema / response_format: https://github.com/ggml-org/llama.cpp/blob/HEAD/tools/server/README.md
- Absolute rather than pairwise judging: https://arxiv.org/pdf/2504.14716
- Models: facebook/dinov2-small, openai/clip-vit-base-patch32 (Hugging Face)
- VBench-2.0 Human_Anatomy (YOLO-World + ViT anomaly classifiers), considered but not adopted: https://arxiv.org/html/2503.21755v2, https://github.com/Vchitect/VBench/tree/master/VBench-2.0/vbench2/third_party/ViTDetector
- Per-body-part yes/no distortion prompts for MLLMs (Human-AGVQA): https://arxiv.org/html/2411.16619v3
- llama.cpp OAI-compatible logprobs (pre-sampling): https://github.com/ggml-org/llama.cpp/pull/10783
