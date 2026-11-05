# FLUX stills workflow S2 (frozen 2026-10-31 1:2x AM CT)
Adopted by Derrick 1:16 AM CT Oct 31 (card): "Adopt S2 as the FLUX stills workflow now". Scores (Fleet Reviewer audit 60_reviews/fleet/2026-10-31-max-flux-render-audit.md): S2 33/54 PASS (61%), median 0.522, 0 COPY; best arm, below the plan's 80% bar.
Copied from the requests that actually rendered (pos 1 of each run; all 54 jobs per arm share these settings):
- Pass 1 = `flux_stills_s2_kv.api.json` from `runs\flux_redo_20261030_A3\fr_A3_c01_seated_front34_apartment_s101\request.api.json`
- Pass 2 = `flux_stills_s2_bfs.api.json` from `runs\flux_redo_20261030_S2\fr_S2_c01_seated_front34_apartment_s101\request.api.json`
Only image paths, seed (0), filename_prefix (TAG) and the pass-1 prompt (placeholder POSE/LIGHT) were replaced.

| | Pass 1 (A3) | Pass 2 (S2 BFS face-restore) |
|---|---|---|
| UNET | flux-2-klein-9b-kv-fp8.safetensors (+ core FluxKVCache node 26 after the LoRA) | FLUX-KLEIN-9B-FP8-NSFW.safetensors (no KV node) |
| LoRA | bfs_head_v1_flux-klein_9b_step3750_rank64 at **0.0** (node kept, off) | bfs_head_v1_flux-klein_9b_step3750_rank64 at **0.5** |
| Text encoder / VAE | qwen_3_8b_fp8mixed (flux2) / flux2-vae | same |
| Refs | image 1 = the approved still (1 ReferenceLatent) | Picture 1 = pass-1 PNG (`... [output]`), Picture 2 = head (redo used Phase 1 head crops; make_render uses the approved still) |
| Prompt | per job: "Show the woman from image 1 <pose/angle/scene>. Keep the same face, hairstyle and hair color. <light>, photoreal." | BFS template head_swap prompt, verbatim |
| Negative | bad quality, noise, blurry, worst quality, low resolution, blur, distortion, unnatural blending, cartoon, illustration, painting | same |
| Steps / CFG / sampler / scheduler | 4 / 1.0 / lcm / Flux2Scheduler | 4 / 1.0 / lcm / Flux2Scheduler |
| Size | body resized to 1.0 MP (lanczos), latent = that size: 752x1360 in the redo | pass-1 output resized to 1.0 MP: 752x1376 in the redo |
Default user: `scripts\make_render.py still ...` (two batches: pass 1, then pass 2). Video candidate stills use `flux_stills_s2_bfs.api.json`.

## Component check vs cards (2026-10-31 ~1:30 AM CT; no settings changed)
- KV model + FluxKVCache: BFL card "step-distilled to 4 inference steps"; Comfy KV template feeds the loaded model into FluxKVCache, then the guider. Ours: UNET -> BFS LoRA at 0.0 (no-op) -> FluxKVCache -> guider, 4 steps. MATCH.
- Text encoder qwen_3_8b_fp8mixed + flux2-vae: listed in Comfy-Org/Flux-2-Klein-9B. MATCH.
- CFG 1.0 at 4 steps (distilled): nomadoor/official template "CFG: 1.0, steps: 4". MATCH. The negative text is ignored at CFG 1 (BFL: no negative prompts); the KV template zeroes it instead. Harmless; left as run.
- Sampler lcm: official sampler for the edit template NOT VERIFIED (redo plan kept the template's). Judgment call, unchanged.
- Jib Mix (pass 2): card samples use Euler, CFG 1, 10 steps; the Klein explicit plan quotes the author "8-12 steps of Euler/Simple". We run lcm 4 steps. MISMATCH vs card, but this is how S2 was scored; listed for Derrick, unchanged.
- BFS LoRA file bfs_head_v1_flux-klein_9b_step3750_rank64: listed for Klein 9B; body = Picture 1, head = Picture 2. MATCH. Card starts at strength 1.0; we use 0.5 (redo plan). Judgment, unchanged.
- BFS prompt: the card's current prompt adds "Keep the body, clothing, pose, framing, and background intact." and drops "high quality, sharp details, 4k" and the expression line. Ours is the older wording S2 was scored with. Listed for Derrick, unchanged.
- Head image: card says Picture 2 = "reference face/head"; the redo used head crops, make_render uses the full approved still (no crops exist). Listed for Derrick.
- Sizes 1 MP, multiples of 16: MATCH (nomadoor: max 4 MP, multiples of 16).
