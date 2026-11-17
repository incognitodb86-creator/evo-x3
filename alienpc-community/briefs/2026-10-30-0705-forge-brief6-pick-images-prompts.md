CANCELLED 2026-10-30 07:05 CT by Derrick's direction: Max picks images and writes prompts.

# Forge brief 6: pick 2 start images and write 2 prompts (Step 1 only)
Plan: C:\AI\community\plans\2026-10-30-0700-terrace-proper-settings-test-plan.md (read "Pictures" and "Steps").
**Build only. Do not render, do not queue anything, and do not touch gpu-render.lock.**

1. Pick 2 images from the approved adults-only fictional pool: `C:\Users\derek\5slock\approved_characters`.
   - Image A is typical: medium shot, moderate motion, one hand-contact point.
   - Image B is a stress test: tighter framing, fast motion, and a different hard element (overlapping arms or loose clothing).
   - Each must show two adults fully in frame, with faces and hands visible and a clean first frame.
   - Each must differ from Terrace on at least 3 of: indoor/outdoor, lighting, framing, camera height, palette.
   - Run the adults-only check on each image.
2. Crop or pad each image to exactly 768x1344 (never stretch). Copy them to `ComfyUI\input\community\` as `V3A_768x1344.png` and `V3B_768x1344.png`.
3. Caption each image with your own vision model.
4. Write each prompt with the same process you used for `notes\2026-10-30-terrace-b2v2-prompt.txt`, in the same Ref2VA/H3 structure: person1, person2 as in the image, scene, one 5 s shot with motion beats, camera, and a short sound.
   - Each prompt is within ±15% of Terrace's word count.
   - The action is consensual and the prompt says the adults are 18+.
   - Describe only what is in the image, plus motion. Make hands and contact explicit.
5. Save the following in `C:\AI\community\notes\`:
   - `2026-10-30-v3A-prompt.txt` and `2026-10-30-v3B-prompt.txt`
   - `2026-10-30-v3-captions.md`
   - `2026-10-30-v3-sha256.txt`, with hashes of both images and both prompts
   - `2026-10-30-v3-step1-DONE.md`, listing: the source path of each image; the two 768x1344 files `ComfyUI\input\community\V3A_768x1344.png` and `V3B_768x1344.png` (crop or pad used); the prompt files with sha256 and word counts vs Terrace; the caption file; the 3+ ways each differs from Terrace; and the adults-only check result per image
6. Stop there. Max checks the work, then Derrick checks it.
