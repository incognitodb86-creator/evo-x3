# Forge handoff: FLUX.2 Klein edit test code (Max Architect, 2026-10-29)
Staged only. Nothing here is run, wired into live scripts, or approved to render.
Derek 2026-10-29 (verbatim): "Send it to forge for implementation and double checking or whatever."
Derek earlier: "Don't start yet" (no render/GPU/queue without his go). Cards for the quiet window, C8-P, C-POSE etc are still open.

Source of truth: GitHub private repo fleet-brain-staging, 40_projects/flux2-overnight/code/flux-edit (HEAD 6e6384e). Plan: plans/flux-edit-ce-plan-2026-10-28.md (same repo).
Tests (82) pass on Max's box with stdlib unittest and a mock ComfyUI; NOTHING is verified on AlienPc.

Your job (read-only/test-only until Derek approves a window):
1. Review the code against the plan (U2-U5, U7, U11). Report bugs; do not widen scope.
2. Run the tests in the director venv: cd <this folder>\scripts ; python -m unittest discover -s tests  (no pytest install without a card). Report real counts.
3. Verify the unverified items and report them (no guessing): ResizeImageMaskNode input key names vs loop1017 workflow_headswap_api.json; full sha256 of UNET/VAE/CLIP; llama-swap /running shape and version string; capture /object_info baseline ONLY in a quiet window (it wakes ComfyUI).
4. Picks: Forge picks its own 30 bodies + 1 canary from the approved folder (not E10, not the 10-17 run); never ask Derek for head refs. Never any image of a minor.
5. Do NOT: render, queue, load models, restart Strata/llama-swap/ComfyUI, download, install, delete, or copy into live scripts\ without a card.
Needs Derek (NEEDS_DEREK): head-crop min and B1 misalignment thresholds, quiet window.
