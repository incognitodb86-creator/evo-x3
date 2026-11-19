# Build spec for Antigravity (agy): flux Phase 1 build + stage (plan b073bc4)

Derrick said yes at 2:52 PM CT on Oct 30 2026. Plan: 40_projects/flux2-overnight/plans/2026-10-30-flux-full-replan.md (commit b073bc4). Read its Phase 1 and build-steps sections first.

## 1. Build (follow the plan's build steps exactly)
- Add one `still` job_type branch to C:\AI\community\scripts\run_queue.py. It checks only for a PNG output and its size, and reads the prompt from the Klein edit/text node. It skips the frames, audio and contact-sheet checks. Leave --detach, --dry-run, the lock and STOP as they are, and add no new gates.
- Build C:\AI\community\templates\bfs_klein9b.api.json from the shipped BFS values. Models are in C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models: Klein 9B fp8, BFS rank64 LoRA, flux2-vae, qwen_3_8b_fp8mixed.
- Write a small request patcher modelled on make_b2_request.py.
- The static banned-node check allows only face_sim and T2 MediaPipe.
- Make one ComfyUI object_info call to confirm the BFS nodes exist.
- Run the existing run_queue tests.

## 2. Stage
Stage the 61 Phase 1 jobs as the plan sets out: 30 approved stills x 2 seeds, plus 1 canary, with the aspect-ratio and multi-character mix the plan gives. Use plain hand crops with no background removal (RMBG stays off). Then run `run_queue --dry-run`.

## 3. Stop
Do not render anything. The Phase 1 GO is Derrick's call. Report to Max in 5 lines:
1. Files changed and the commit.
2. Test result.
3. object_info result.
4. Dry-run summary.
5. Anything blocked.

## Rules
- face_sim (C-ID) and T2 MediaPipe face boxes may be used only to compare an output with its own approved_characters starting still.
- PuLID, InsightFace, ReActor, InstantID, FaceDetailer and AutoCropFaces stay banned. models\pulid\pulid_flux2_klein_v2.safetensors stays on disk, and no graph may load it.
- Fictional adults only. approved_characters is add-only.
- No repo-wide greps, no one-off check scripts, and no DONE notes beyond one commit message.
- Never run run_graph_job.py directly.
