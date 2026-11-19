# brief8 arms CHECKED (Max2 read-back, 2026-10-30 09:09 CT)

Verified by Max2 against plan 5d5fa1ac...3653b and B2 baseline terrace_retest_v2_20261030\b2_s51083002\request.api.json (124fb133...1ca2):
- All 49 request.api.json: only the arm variable differs from B2, plus the expected seed (51083002/12/13), image and prompt; filename_prefix ignored. Model, sampler, scheduler, steps, shift, size, length 124, fps unchanged.
  a0 none; s1a ksel.sampler_name=er_sde; s1b s0_sched.scheduler=sgm_uniform; s2 unet=...beta7_activation_learned_HQ; s3 lsu3=...3d_fp16; s6 s0_sched.steps=6; s8 prompt only.
- Prompt hashes: Terrace e202e512..., promptA 97ed1361..., promptB 83efcf50...; S8 (rebuilt 09:02, line file incl LF + LF + prompt) Terrace 46195643c6c6, A 5f335a68ee24, B 12e46703e6ca, all matching the plan.
- s8_terr_s51083002 matches v2 s8_s51083002 (filename_prefix aside); v2 s8 prompt 46195643c6c6.
- Start images in ComfyUI input\community: imageA crop 4d07281d, imageB crop 4c9ae12f, TERRACE2 b891c85f.
- comm.guard_ok True on all 49 prompt_full.txt.
Answers: GO 8:31 covers pilots + all 42; drift option (a), note in DONE that v2 logged no environment; masks/scoring/blind pack out of scope.
GO: Step B, render the 42 in _render_order.json order.
